"""Region cropping for XPS spectra (Layer 2)."""

from __future__ import annotations

from typing import Tuple

import numpy as np

from src.core.models import SpectrumData


def crop_spectrum(
    spectrum: SpectrumData,
    be_min: float,
    be_max: float,
) -> SpectrumData:
    if be_min >= be_max:
        raise ValueError("be_min must be < be_max")
    be = np.asarray(spectrum.binding_energy, dtype=float)
    intensity = np.asarray(spectrum.intensity, dtype=float)
    mask = (be >= be_min) & (be <= be_max)
    frag_be = be[mask]
    frag_int = intensity[mask]
    if frag_be.size < 3:
        raise ValueError(f"Too few points in range ({frag_be.size}); widen the window.")
    out = spectrum.copy()
    out.binding_energy = frag_be
    out.intensity = frag_int
    out.metadata = {
        **spectrum.metadata,
        "region_be_min": float(be_min),
        "region_be_max": float(be_max),
        "parent_core_level": spectrum.core_level,
    }
    return out


def clamp_window(
    be_min: float,
    be_max: float,
    data_min: float,
    data_max: float,
) -> Tuple[float, float]:
    lo = max(be_min, data_min)
    hi = min(be_max, data_max)
    if lo >= hi:
        return data_min, data_max
    return lo, hi
