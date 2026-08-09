"""Local mean / uncertainty bands from adjacent points (Layer 2)."""

from __future__ import annotations

from typing import Tuple

import numpy as np
from scipy.ndimage import uniform_filter1d


def _odd_window(n: int, size: int) -> int:
    w = max(3, min(int(size), n if n % 2 else n - 1))
    return w if w % 2 else w - 1


def local_mean_std(
    intensity: np.ndarray,
    window: int = 7,
) -> Tuple[np.ndarray, np.ndarray]:
    """Rolling mean and local std from adjacent points (same window)."""
    y = np.asarray(intensity, dtype=float)
    n = len(y)
    if n == 0:
        empty = np.array([], dtype=float)
        return empty, empty
    if n < 3:
        return y.copy(), np.zeros_like(y)

    w = _odd_window(n, window)
    mean = uniform_filter1d(y, size=w, mode="nearest")
    mean_sq = uniform_filter1d(y * y, size=w, mode="nearest")
    var = np.maximum(mean_sq - mean * mean, 0.0)
    return mean, np.sqrt(var)


def local_mean_and_uncertainty(
    intensity: np.ndarray,
    window: int = 7,
    n_sigma: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rolling mean and ±n_sigma local-std envelope from adjacent points.

    Returns
    -------
    mean, lower, upper
        ``lower = mean - n_sigma * local_std``, ``upper = mean + n_sigma * local_std``.
    """
    mean, std = local_mean_std(intensity, window=window)
    lower = mean - float(n_sigma) * std
    upper = mean + float(n_sigma) * std
    return mean, lower, upper


def fraction_within_band(
    intensity: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> Tuple[float, int, int]:
    """Share of points with ``lower <= y <= upper``.

    Returns ``(percent_0_to_100, n_inside, n_total)``.
    """
    y = np.asarray(intensity, dtype=float)
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    n = int(y.size)
    if n == 0 or lo.size != n or hi.size != n:
        return 0.0, 0, n
    inside = (y >= lo) & (y <= hi) & np.isfinite(y) & np.isfinite(lo) & np.isfinite(hi)
    n_inside = int(np.count_nonzero(inside))
    return 100.0 * n_inside / n, n_inside, n


def fraction_residual_within_local_sigma(
    intensity: np.ndarray,
    model: np.ndarray,
    window: int = 7,
    n_sigma: float = 1.0,
) -> Tuple[float, int, int]:
    """Share of points where ``|y - model| <= n_sigma * local_std``.

    Local std comes from the same adjacent-point window as the green band.
    Changing the selected peak sum (``model``) changes this fraction.
    """
    y = np.asarray(intensity, dtype=float)
    m = np.asarray(model, dtype=float)
    n = int(y.size)
    if n == 0 or m.size != n:
        return 0.0, 0, n
    _, std = local_mean_std(y, window=window)
    tol = float(n_sigma) * std
    residual = np.abs(y - m)
    finite = np.isfinite(y) & np.isfinite(m) & np.isfinite(tol)
    inside = finite & (residual <= tol)
    n_inside = int(np.count_nonzero(inside))
    return 100.0 * n_inside / n, n_inside, n
