"""Noise smoothing helpers (Layer 2) — separate from baseline estimation."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import medfilt, savgol_filter


def remove_noise(
    intensity: np.ndarray,
    method: str = "median",
    window_size: int = 5,
) -> np.ndarray:
    intensity = np.asarray(intensity, dtype=float)
    if method == "none" or window_size < 3 or len(intensity) < 3:
        return intensity.copy()
    window = window_size if window_size % 2 else window_size + 1
    window = min(window, len(intensity) if len(intensity) % 2 else len(intensity) - 1)
    window = max(3, window if window % 2 else window - 1)
    if method == "median":
        return medfilt(intensity, kernel_size=window)
    if method == "moving_average":
        return uniform_filter1d(intensity, size=window, mode="nearest")
    if method == "savgol":
        poly = min(3, window - 1)
        return savgol_filter(intensity, window_length=window, polyorder=poly)
    return intensity.copy()
