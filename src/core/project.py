"""Analysis project domain model (Layer 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.core.models import (
    BaselineSettings,
    FitConstraints,
    PeakConfig,
    SpectrumData,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class FitSnapshot:
    """One saved / historical deconvolution result."""

    id: str = field(default_factory=lambda: uuid4().hex[:10])
    label: str = ""
    created_at: str = field(default_factory=_now)
    peak_model: str = "pseudovoigt"
    peak_configs: List[PeakConfig] = field(default_factory=list)
    baseline_settings: BaselineSettings = field(default_factory=BaselineSettings)
    noise_method: str = "none"
    noise_window: int = 5
    savgol_poly: int = 2
    fit_constraints: FitConstraints = field(default_factory=FitConstraints)
    metrics: Optional[Dict[str, Any]] = None
    peaks_table: Optional[Any] = None  # list[dict] preferred (human-readable)
    corrected: Optional[List[float]] = None
    baseline: Optional[List[float]] = None
    smoothed: Optional[List[float]] = None
    best_fit: Optional[List[float]] = None
    components: Optional[List[List[float]]] = None
    binding_energy: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "created_at": self.created_at,
            "peak_model": self.peak_model,
            "peak_configs": [p.to_dict() for p in self.peak_configs],
            "baseline_settings": self.baseline_settings.to_dict(),
            "noise_method": self.noise_method,
            "noise_window": self.noise_window,
            "savgol_poly": self.savgol_poly,
            "fit_constraints": {
                "enable_fix_fwhm": self.fit_constraints.enable_fix_fwhm,
                "enable_doublet_links": self.fit_constraints.enable_doublet_links,
                "shared_sigma": self.fit_constraints.shared_sigma,
            },
            "metrics": self.metrics,
            "peaks_table": self.peaks_table,
            "corrected": self.corrected,
            "baseline": self.baseline,
            "smoothed": self.smoothed,
            "best_fit": self.best_fit,
            "components": self.components,
            "binding_energy": self.binding_energy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FitSnapshot":
        fc = data.get("fit_constraints") or {}
        return cls(
            id=str(data.get("id") or uuid4().hex[:10]),
            label=str(data.get("label", "")),
            created_at=str(data.get("created_at") or _now()),
            peak_model=str(data.get("peak_model", "pseudovoigt")),
            peak_configs=[PeakConfig.from_dict(p) for p in data.get("peak_configs") or []],
            baseline_settings=BaselineSettings.from_dict(data.get("baseline_settings") or {}),
            noise_method=str(data.get("noise_method", "none")),
            noise_window=int(data.get("noise_window", 5)),
            savgol_poly=int(data.get("savgol_poly", 2)),
            fit_constraints=FitConstraints(
                enable_fix_fwhm=bool(fc.get("enable_fix_fwhm", False)),
                enable_doublet_links=bool(fc.get("enable_doublet_links", False)),
                shared_sigma=bool(fc.get("shared_sigma", False)),
            ),
            metrics=data.get("metrics"),
            peaks_table=data.get("peaks_table"),
            corrected=data.get("corrected"),
            baseline=data.get("baseline"),
            smoothed=data.get("smoothed"),
            best_fit=data.get("best_fit"),
            components=data.get("components"),
            binding_energy=data.get("binding_energy"),
        )


@dataclass
class SpectrumEntry:
    id: str = field(default_factory=lambda: uuid4().hex[:10])
    label: str = ""
    spectrum: Optional[SpectrumData] = None
    notes: str = ""
    region: Optional[list] = None
    baseline_settings: BaselineSettings = field(default_factory=BaselineSettings)
    noise_method: str = "none"
    noise_window: int = 5
    savgol_poly: int = 2
    peak_model: str = "pseudovoigt"
    peak_configs: List[PeakConfig] = field(default_factory=list)
    fit_constraints: FitConstraints = field(default_factory=FitConstraints)
    fit_history: List[FitSnapshot] = field(default_factory=list)
    saved_fits: Dict[str, FitSnapshot] = field(default_factory=dict)
    last_fit_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.spectrum is None:
            raise ValueError("SpectrumEntry.spectrum is required to serialize")
        return {
            "id": self.id,
            "label": self.label,
            "spectrum": self.spectrum.to_serializable(),
            "notes": self.notes,
            "region": self.region,
            "baseline_settings": self.baseline_settings.to_dict(),
            "noise_method": self.noise_method,
            "noise_window": self.noise_window,
            "savgol_poly": self.savgol_poly,
            "peak_model": self.peak_model,
            "peak_configs": [p.to_dict() for p in self.peak_configs],
            "fit_constraints": {
                "enable_fix_fwhm": self.fit_constraints.enable_fix_fwhm,
                "enable_doublet_links": self.fit_constraints.enable_doublet_links,
                "shared_sigma": self.fit_constraints.shared_sigma,
            },
            "fit_history": [f.to_dict() for f in self.fit_history],
            "saved_fits": {k: v.to_dict() for k, v in self.saved_fits.items()},
            "last_fit_id": self.last_fit_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpectrumEntry":
        fc = data.get("fit_constraints") or {}
        saved_raw = data.get("saved_fits") or {}
        return cls(
            id=str(data.get("id") or uuid4().hex[:10]),
            label=str(data.get("label", "")),
            spectrum=SpectrumData.from_serializable(data["spectrum"]),
            notes=str(data.get("notes", "")),
            region=data.get("region"),
            baseline_settings=BaselineSettings.from_dict(data.get("baseline_settings") or {}),
            noise_method=str(data.get("noise_method", "none")),
            noise_window=int(data.get("noise_window", 5)),
            savgol_poly=int(data.get("savgol_poly", 2)),
            peak_model=str(data.get("peak_model", "pseudovoigt")),
            peak_configs=[PeakConfig.from_dict(p) for p in data.get("peak_configs") or []],
            fit_constraints=FitConstraints(
                enable_fix_fwhm=bool(fc.get("enable_fix_fwhm", False)),
                enable_doublet_links=bool(fc.get("enable_doublet_links", False)),
                shared_sigma=bool(fc.get("shared_sigma", False)),
            ),
            fit_history=[FitSnapshot.from_dict(f) for f in data.get("fit_history") or []],
            saved_fits={k: FitSnapshot.from_dict(v) for k, v in saved_raw.items()},
            last_fit_id=data.get("last_fit_id"),
        )


@dataclass
class AnalysisProject:
    id: str = field(default_factory=lambda: uuid4().hex[:10])
    name: str = "Untitled project"
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    notes: str = ""
    spectra: List[SpectrumEntry] = field(default_factory=list)
    active_spectrum_id: Optional[str] = None

    def touch(self) -> None:
        self.updated_at = _now()

    def get_active(self) -> Optional[SpectrumEntry]:
        if not self.active_spectrum_id:
            return None
        for s in self.spectra:
            if s.id == self.active_spectrum_id:
                return s
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
            "spectra": [s.to_dict() for s in self.spectra],
            "active_spectrum_id": self.active_spectrum_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisProject":
        return cls(
            id=str(data.get("id") or uuid4().hex[:10]),
            name=str(data.get("name", "Untitled project")),
            created_at=str(data.get("created_at") or _now()),
            updated_at=str(data.get("updated_at") or _now()),
            notes=str(data.get("notes", "")),
            spectra=[SpectrumEntry.from_dict(s) for s in data.get("spectra") or []],
            active_spectrum_id=data.get("active_spectrum_id"),
        )
