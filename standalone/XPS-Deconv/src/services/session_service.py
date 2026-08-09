"""Session save/load and export (Layer 4)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from src.core.models import BaselineSettings, FitConstraints, PeakConfig, SpectrumData
from src.db import sessions_repo
from src.utils.paths import EXPORTS_DIR, SESSIONS_DIR, ensure_runtime_dirs


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    raise TypeError(f"Not serializable: {type(obj)}")


def build_session_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    full: Optional[SpectrumData] = state.get("full_spectrum")
    active: Optional[SpectrumData] = state.get("active_spectrum")
    peaks = state.get("peak_configs") or []
    baseline: Optional[BaselineSettings] = state.get("baseline_settings")
    constraints: Optional[FitConstraints] = state.get("fit_constraints")
    peaks_df: Optional[pd.DataFrame] = state.get("peaks_df")
    peaks_records = None
    if peaks_df is not None:
        peaks_records = peaks_df.to_dict(orient="records")
    metrics = state.get("metrics")
    return {
        "version": 2,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "full_spectrum": None if full is None else full.to_serializable(),
        "active_spectrum": None if active is None else active.to_serializable(),
        "region": state.get("region"),
        "baseline_settings": None if baseline is None else baseline.to_dict(),
        "noise_method": state.get("noise_method", "none"),
        "noise_window": state.get("noise_window", 5),
        "peak_model": state.get("peak_model", "pseudovoigt"),
        "peak_configs": [p.to_dict() if isinstance(p, PeakConfig) else p for p in peaks],
        "fit_constraints": None
        if constraints is None
        else {
            "enable_fix_fwhm": constraints.enable_fix_fwhm,
            "enable_doublet_links": constraints.enable_doublet_links,
            "shared_sigma": constraints.shared_sigma,
        },
        "metrics": metrics,
        "peaks": peaks_records,  # human-readable list of objects
        "peaks_table": peaks_records,  # alias for older loaders
        "corrected": None
        if state.get("corrected") is None
        else np.asarray(state["corrected"]).tolist(),
        "baseline": None
        if state.get("baseline") is None
        else np.asarray(state["baseline"]).tolist(),
        "best_fit": None
        if state.get("best_fit") is None
        else np.asarray(state["best_fit"]).tolist(),
    }


def save_session(name: str, state: Dict[str, Any], notes: str = "") -> Path:
    ensure_runtime_dirs()
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name).strip("_") or "session"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = SESSIONS_DIR / f"{safe}_{stamp}.json"
    payload = build_session_payload(state)
    path.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")
    active: Optional[SpectrumData] = state.get("active_spectrum") or state.get("full_spectrum")
    sessions_repo.upsert_session(
        name=name,
        json_path=path,
        core_level="" if active is None else active.core_level,
        source_path="" if active is None else active.source_path,
        notes=notes,
    )
    return path


def load_session(path: str | Path) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    out: Dict[str, Any] = {"raw": payload}
    if payload.get("full_spectrum"):
        out["full_spectrum"] = SpectrumData.from_serializable(payload["full_spectrum"])
    if payload.get("active_spectrum"):
        out["active_spectrum"] = SpectrumData.from_serializable(payload["active_spectrum"])
    out["region"] = payload.get("region")
    if payload.get("baseline_settings"):
        out["baseline_settings"] = BaselineSettings.from_dict(payload["baseline_settings"])
    out["noise_method"] = payload.get("noise_method", "none")
    out["noise_window"] = payload.get("noise_window", 5)
    out["peak_model"] = payload.get("peak_model", "pseudovoigt")
    out["peak_configs"] = [PeakConfig.from_dict(p) for p in payload.get("peak_configs") or []]
    fc = payload.get("fit_constraints") or {}
    out["fit_constraints"] = FitConstraints(
        enable_fix_fwhm=bool(fc.get("enable_fix_fwhm", False)),
        enable_doublet_links=bool(fc.get("enable_doublet_links", False)),
        shared_sigma=bool(fc.get("shared_sigma", False)),
    )
    out["metrics"] = payload.get("metrics")
    peaks_payload = payload.get("peaks") or payload.get("peaks_table")
    if peaks_payload:
        out["peaks_df"] = pd.DataFrame(peaks_payload)
    for key in ("corrected", "baseline", "best_fit"):
        if payload.get(key) is not None:
            out[key] = np.asarray(payload[key], dtype=float)
    return out


def export_excel(state: Dict[str, Any], filename: str) -> Path:
    ensure_runtime_dirs()
    path = EXPORTS_DIR / filename
    if not path.suffix:
        path = path.with_suffix(".xlsx")
    active: SpectrumData = state.get("active_spectrum") or state.get("full_spectrum")
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        if active is not None:
            pd.DataFrame(
                {
                    "Binding_Energy_eV": active.binding_energy,
                    "Intensity": active.intensity,
                }
            ).to_excel(writer, sheet_name="Spectrum", index=False)
        if state.get("baseline") is not None and state.get("corrected") is not None:
            pd.DataFrame(
                {
                    "Binding_Energy_eV": active.binding_energy,
                    "Baseline": state["baseline"],
                    "After_Baseline": state["corrected"],
                }
            ).to_excel(writer, sheet_name="Baseline", index=False)
        if state.get("best_fit") is not None:
            pd.DataFrame(
                {
                    "Binding_Energy_eV": active.binding_energy,
                    "Best_Fit": state["best_fit"],
                    "Corrected": state.get("corrected"),
                }
            ).to_excel(writer, sheet_name="FitCurve", index=False)
        if state.get("peaks_df") is not None:
            state["peaks_df"].to_excel(writer, sheet_name="Peaks", index=False)
        if state.get("metrics"):
            pd.DataFrame([state["metrics"]]).to_excel(writer, sheet_name="Metrics", index=False)
    return path


def export_peaks_csv(peaks_df: pd.DataFrame, filename: str) -> Path:
    ensure_runtime_dirs()
    path = EXPORTS_DIR / filename
    if not path.suffix:
        path = path.with_suffix(".csv")
    peaks_df.to_csv(path, index=False)
    return path
