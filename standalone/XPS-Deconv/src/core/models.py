"""Spectrum domain models (Layer 2)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple
from uuid import uuid4

import numpy as np

BeWindow = Tuple[float, float]


@dataclass
class SpectrumData:
    """Working spectrum used across the pipeline."""

    binding_energy: np.ndarray
    intensity: np.ndarray
    core_level: str = "Unknown"
    source_path: str = ""
    spectrum_index: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "SpectrumData":
        return SpectrumData(
            binding_energy=np.asarray(self.binding_energy, dtype=float).copy(),
            intensity=np.asarray(self.intensity, dtype=float).copy(),
            core_level=self.core_level,
            source_path=self.source_path,
            spectrum_index=self.spectrum_index,
            metadata=dict(self.metadata),
        )

    def to_serializable(self) -> Dict[str, Any]:
        return {
            "binding_energy": np.asarray(self.binding_energy, dtype=float).tolist(),
            "intensity": np.asarray(self.intensity, dtype=float).tolist(),
            "core_level": self.core_level,
            "source_path": self.source_path,
            "spectrum_index": self.spectrum_index,
            "metadata": self.metadata,
        }

    @classmethod
    def from_serializable(cls, payload: Dict[str, Any]) -> "SpectrumData":
        return cls(
            binding_energy=np.asarray(payload["binding_energy"], dtype=float),
            intensity=np.asarray(payload["intensity"], dtype=float),
            core_level=str(payload.get("core_level", "Unknown")),
            source_path=str(payload.get("source_path", "")),
            spectrum_index=int(payload.get("spectrum_index", 0)),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass
class PeakConfig:
    name: str
    center: float
    tolerance: float = 0.0
    sigma: float = 1.0
    amplitude: Optional[float] = None
    fraction: float = 0.5  # PseudoVoigt / GL mix
    fix_center: bool = False
    fix_fwhm: bool = False
    link_group: Optional[str] = None  # doublet linkage id
    link_delta_be: Optional[float] = None  # e.g. Ag3d 6.0 eV
    uid: str = field(default_factory=lambda: uuid4().hex[:8])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PeakConfig":
        payload = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        if not payload.get("uid"):
            payload["uid"] = uuid4().hex[:8]
        return cls(**payload)


@dataclass
class FitConstraints:
    enable_fix_fwhm: bool = False
    enable_doublet_links: bool = False
    shared_sigma: bool = False


@dataclass
class BaselineSettings:
    method: str = "median_linear"
    edge_fraction: float = 0.08
    manual_windows: List[BeWindow] = field(default_factory=list)
    poly_degree: int = 2
    rolling_window: int = 21
    shirley_max_iter: int = 50
    tougaard_B: float = 2866.0
    tougaard_C: float = 1643.0
    subtract: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "edge_fraction": self.edge_fraction,
            "manual_windows": [list(w) for w in self.manual_windows],
            "poly_degree": self.poly_degree,
            "rolling_window": self.rolling_window,
            "shirley_max_iter": self.shirley_max_iter,
            "tougaard_B": self.tougaard_B,
            "tougaard_C": self.tougaard_C,
            "subtract": self.subtract,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaselineSettings":
        windows = [tuple(w) for w in data.get("manual_windows") or []]
        return cls(
            method=str(data.get("method", "median_linear")),
            edge_fraction=float(data.get("edge_fraction", 0.08)),
            manual_windows=windows,  # type: ignore[arg-type]
            poly_degree=int(data.get("poly_degree", 2)),
            rolling_window=int(data.get("rolling_window", 21)),
            shirley_max_iter=int(data.get("shirley_max_iter", 50)),
            tougaard_B=float(data.get("tougaard_B", 2866.0)),
            tougaard_C=float(data.get("tougaard_C", 1643.0)),
            subtract=bool(data.get("subtract", True)),
        )


BASELINE_METHODS: Sequence[str] = (
    "none",
    "median_horizontal",
    "median_linear",
    "rolling_median",
    "asls",
    "snip",
    "linear_endpoints",
    "polynomial_edges",
    "shirley",
    "tougaard",
)

PEAK_MODELS: Sequence[str] = (
    "gaussian",
    "lorentzian",
    "voigt",
    "pseudovoigt",  # GL(m)-like via fraction
)

REGION_PRESETS: Dict[str, BeWindow] = {
    "O1s (525-540 eV)": (525.0, 540.0),
    "C1s (280-295 eV)": (280.0, 295.0),
    "N1s (395-405 eV)": (395.0, 405.0),
    "Ag3d (365-378 eV)": (365.0, 378.0),
    "Sr3d (130-140 eV)": (130.0, 140.0),
    "Ti2p (450-465 eV)": (450.0, 465.0),
    "Fe2p (700-730 eV)": (700.0, 730.0),
    "Si2p (95-110 eV)": (95.0, 110.0),
    "Ca2p (340-355 eV)": (340.0, 355.0),
}
