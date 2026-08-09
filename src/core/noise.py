"""Noise / denoise helpers (Layer 2) — reworked with clearer methods."""

from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import medfilt, savgol_filter, wiener

DENOISE_METHODS: Sequence[str] = (
    "none",
    "median",
    "moving_average",
    "savgol",
    "wiener",
)

DENOISE_HELP = {
    "none": "No smoothing — use raw counts/intensity.",
    "median": "Median filter: robust to spikes/outliers; good first choice for XPS noise.",
    "moving_average": "Boxcar average: strong smoothing, can broaden peaks if window is large.",
    "savgol": "Savitzky–Golay: polynomial smooth that preserves peak shape better than a plain average.",
    "wiener": "Wiener filter: adaptive smooth based on local variance (can help mixed noise).",
}


def _odd_window(n: int, size: int) -> int:
    w = max(3, min(int(size), n if n % 2 else n - 1))
    return w if w % 2 else w - 1


def remove_noise(
    intensity: np.ndarray,
    method: str = "median",
    window_size: int = 5,
    savgol_poly: int = 2,
) -> np.ndarray:
    """Denoise a 1D intensity array. Separate from baseline estimation."""
    intensity = np.asarray(intensity, dtype=float)
    if method == "none" or window_size < 3 or len(intensity) < 3:
        return intensity.copy()
    window = _odd_window(len(intensity), window_size)
    if method == "median":
        return medfilt(intensity, kernel_size=window)
    if method == "moving_average":
        return uniform_filter1d(intensity, size=window, mode="nearest")
    if method == "savgol":
        poly = max(1, min(int(savgol_poly), window - 1))
        return savgol_filter(intensity, window_length=window, polyorder=poly)
    if method == "wiener":
        # mysize must be odd-ish; wiener accepts int
        return np.asarray(wiener(intensity, mysize=window), dtype=float)
    return intensity.copy()


def denoise_preview_pair(
    intensity: np.ndarray,
    method: str,
    window_size: int = 5,
    savgol_poly: int = 2,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return (raw, denoised) for UI comparison."""
    raw = np.asarray(intensity, dtype=float)
    return raw, remove_noise(raw, method=method, window_size=window_size, savgol_poly=savgol_poly)
