"""Analysis orchestration: noise, baseline, fit (Layer 4)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.core.baseline import compute_baseline
from src.core.fitting import perform_deconvolution
from src.core.models import BaselineSettings, FitConstraints, PeakConfig, SpectrumData
from src.core.noise import remove_noise
from src.core.project import FitSnapshot
from src.core.region import crop_spectrum
from src.utils.cancel import CancelToken


def apply_region(spectrum: SpectrumData, be_min: float, be_max: float) -> SpectrumData:
    return crop_spectrum(spectrum, be_min, be_max)


def prepare_intensity(
    spectrum: SpectrumData,
    noise_method: str = "none",
    noise_window: int = 5,
    savgol_poly: int = 2,
    baseline: Optional[BaselineSettings] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray], np.ndarray]:
    """Return (working_intensity, baseline_array_or_None, noise_smoothed)."""
    y = remove_noise(
        spectrum.intensity,
        method=noise_method,
        window_size=noise_window,
        savgol_poly=savgol_poly,
    )
    if baseline is None or baseline.method == "none":
        return y.copy(), None, y
    corrected, bl = compute_baseline(spectrum.binding_energy, y, baseline)
    return corrected, bl, y


def run_fit(
    spectrum: SpectrumData,
    peaks: List[PeakConfig],
    peak_model: str,
    baseline: BaselineSettings,
    noise_method: str = "none",
    noise_window: int = 5,
    savgol_poly: int = 2,
    constraints: Optional[FitConstraints] = None,
    cancel: Optional[CancelToken] = None,
    progress: Optional[Callable[[int, str], None]] = None,
) -> Dict[str, Any]:
    corrected, bl, smoothed = prepare_intensity(
        spectrum,
        noise_method=noise_method,
        noise_window=noise_window,
        savgol_poly=savgol_poly,
        baseline=baseline,
    )
    result, df, metrics, err = perform_deconvolution(
        spectrum.binding_energy,
        corrected,
        peaks,
        peak_model=peak_model,
        constraints=constraints,
        cancel=cancel,
        progress=progress,
    )
    components = None
    if result is not None:
        comps = result.eval_components(x=spectrum.binding_energy)
        components = [comps.get(f"p{i}_") for i in range(len(peaks))]
    return {
        "error": err,
        "result": result,
        "peaks_df": df,
        "metrics": metrics,
        "corrected": corrected,
        "baseline": bl,
        "smoothed": smoothed,
        "best_fit": None if result is None else np.asarray(result.best_fit, dtype=float),
        "components": components,
    }


def snapshot_from_fit_result(
    spectrum: SpectrumData,
    out: Dict[str, Any],
    *,
    label: str,
    peaks: List[PeakConfig],
    peak_model: str,
    baseline: BaselineSettings,
    noise_method: str,
    noise_window: int,
    savgol_poly: int,
    constraints: FitConstraints,
) -> FitSnapshot:
    comps = out.get("components") or []
    return FitSnapshot(
        label=label,
        peak_model=peak_model,
        peak_configs=list(peaks),
        baseline_settings=baseline,
        noise_method=noise_method,
        noise_window=noise_window,
        savgol_poly=savgol_poly,
        fit_constraints=constraints,
        metrics=out.get("metrics"),
        peaks_table=None if out.get("peaks_df") is None else out["peaks_df"].to_dict(orient="records"),
        corrected=None if out.get("corrected") is None else np.asarray(out["corrected"]).tolist(),
        baseline=None if out.get("baseline") is None else np.asarray(out["baseline"]).tolist(),
        smoothed=None if out.get("smoothed") is None else np.asarray(out["smoothed"]).tolist(),
        best_fit=None if out.get("best_fit") is None else np.asarray(out["best_fit"]).tolist(),
        components=[np.asarray(c).tolist() for c in comps if c is not None],
        binding_energy=np.asarray(spectrum.binding_energy, dtype=float).tolist(),
    )
