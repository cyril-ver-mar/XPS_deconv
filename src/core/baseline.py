"""Baseline correction suite for XPS (Layer 2).

Preferred workflow: estimate noise floor in peak-free windows via median,
then build a horizontal / linear / smooth baseline. Shirley and Tougaard
are also available for classic XPS backgrounds.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
from scipy.signal import medfilt

from src.core.models import BaselineSettings, BeWindow

BeWindowList = Sequence[BeWindow]


def _odd_window(n: int, size: int) -> int:
    w = max(3, min(size, n if n % 2 else n - 1))
    return w if w % 2 else w - 1


def auto_edge_windows(
    be: np.ndarray,
    edge_fraction: float = 0.08,
) -> List[BeWindow]:
    be = np.asarray(be, dtype=float)
    if be.size < 4:
        return [(float(be.min()), float(be.max()))]
    lo, hi = float(be.min()), float(be.max())
    span = hi - lo
    width = max(span * edge_fraction, abs(be[1] - be[0]) * 3)
    return [(lo, lo + width), (hi - width, hi)]


def merge_windows(
    auto: BeWindowList,
    manual: BeWindowList,
) -> List[BeWindow]:
    return [tuple(w) for w in list(auto) + list(manual)]  # type: ignore[misc]


def mask_from_windows(be: np.ndarray, windows: BeWindowList) -> np.ndarray:
    be = np.asarray(be, dtype=float)
    mask = np.zeros(be.shape, dtype=bool)
    for lo, hi in windows:
        a, b = (lo, hi) if lo <= hi else (hi, lo)
        mask |= (be >= a) & (be <= b)
    return mask


def median_in_windows(
    be: np.ndarray,
    intensity: np.ndarray,
    windows: BeWindowList,
) -> float:
    mask = mask_from_windows(be, windows)
    if not np.any(mask):
        return float(np.median(intensity))
    return float(np.median(intensity[mask]))


def side_medians(
    be: np.ndarray,
    intensity: np.ndarray,
    windows: BeWindowList,
) -> Tuple[float, float, float, float]:
    """Return (be_left, med_left, be_right, med_right)."""
    be = np.asarray(be, dtype=float)
    intensity = np.asarray(intensity, dtype=float)
    if len(windows) >= 2:
        left_w, right_w = windows[0], windows[-1]
    elif len(windows) == 1:
        left_w = right_w = windows[0]
    else:
        left_w = right_w = (float(be.min()), float(be.max()))

    left_mask = mask_from_windows(be, [left_w])
    right_mask = mask_from_windows(be, [right_w])
    if not np.any(left_mask):
        left_mask = np.arange(len(be)) < max(1, len(be) // 10)
    if not np.any(right_mask):
        right_mask = np.arange(len(be)) >= len(be) - max(1, len(be) // 10)

    be_l = float(np.median(be[left_mask]))
    med_l = float(np.median(intensity[left_mask]))
    be_r = float(np.median(be[right_mask]))
    med_r = float(np.median(intensity[right_mask]))
    return be_l, med_l, be_r, med_r


def baseline_median_horizontal(
    be: np.ndarray,
    intensity: np.ndarray,
    windows: BeWindowList,
) -> np.ndarray:
    med = median_in_windows(be, intensity, windows)
    return np.full_like(intensity, med, dtype=float)


def baseline_median_linear(
    be: np.ndarray,
    intensity: np.ndarray,
    windows: BeWindowList,
) -> np.ndarray:
    be_l, med_l, be_r, med_r = side_medians(be, intensity, windows)
    if abs(be_r - be_l) < 1e-12:
        return np.full_like(intensity, med_l, dtype=float)
    slope = (med_r - med_l) / (be_r - be_l)
    return med_l + slope * (be - be_l)


def baseline_rolling_median(
    intensity: np.ndarray,
    window: int = 21,
) -> np.ndarray:
    w = _odd_window(len(intensity), window)
    return medfilt(np.asarray(intensity, dtype=float), kernel_size=w)


def baseline_asls(
    intensity: np.ndarray,
    lam: float = 1e5,
    p: float = 0.001,
    niter: int = 10,
) -> np.ndarray:
    """Asymmetric least squares baseline (Eilers & Boelens)."""
    y = np.asarray(intensity, dtype=float)
    L = len(y)
    if L < 3:
        return y.copy()
    D = np.diff(np.eye(L), 2)
    w = np.ones(L)
    for _ in range(niter):
        W = np.diag(w)
        Z = W + lam * D.T @ D
        z = np.linalg.solve(Z, w * y)
        w = p * (y > z) + (1 - p) * (y < z)
    return z


def baseline_snip(
    intensity: np.ndarray,
    iterations: Optional[int] = None,
) -> np.ndarray:
    """Sensitive Nonlinear Iterative Peak clipping (SNIP)."""
    y = np.asarray(intensity, dtype=float).copy()
    n = len(y)
    if n < 5:
        return y
    iters = iterations or max(1, n // 4)
    # work in log space for positivity-ish behaviour
    working = np.log(np.clip(y, 1e-12, None))
    for p in range(1, iters + 1):
        for i in range(p, n - p):
            a = working[i]
            b = (working[i - p] + working[i + p]) / 2.0
            if b < a:
                working[i] = b
    return np.exp(working)


def baseline_linear_endpoints(intensity: np.ndarray) -> np.ndarray:
    y = np.asarray(intensity, dtype=float)
    return np.linspace(y[0], y[-1], len(y))


def baseline_polynomial_edges(
    be: np.ndarray,
    intensity: np.ndarray,
    degree: int = 2,
    edge_points: int = 10,
) -> np.ndarray:
    be = np.asarray(be, dtype=float)
    y = np.asarray(intensity, dtype=float)
    n = len(y)
    ep = max(2, min(edge_points, n // 4))
    idx = np.concatenate([np.arange(ep), np.arange(n - ep, n)])
    deg = max(1, min(degree, len(idx) - 1))
    coeffs = np.polyfit(be[idx], y[idx], deg)
    return np.polyval(coeffs, be)


def baseline_shirley(
    intensity: np.ndarray,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> np.ndarray:
    """Iterative Shirley background (constant endpoints)."""
    y = np.asarray(intensity, dtype=float)
    n = len(y)
    if n < 3:
        return y.copy()
    bg = np.zeros(n, dtype=float)
    y0, yn = y[0], y[-1]
    for _ in range(max_iter):
        total = float(np.trapezoid(y - bg))
        if abs(total) < 1e-18:
            break
        cum = np.cumsum((y - bg)[::-1])[::-1]
        # integrate from i to end
        new_bg = yn + (y0 - yn) * (cum / cum[0] if cum[0] != 0 else 0)
        if np.max(np.abs(new_bg - bg)) < tol * (np.max(y) - np.min(y) + 1e-12):
            bg = new_bg
            break
        bg = new_bg
    return bg


def baseline_tougaard(
    be: np.ndarray,
    intensity: np.ndarray,
    B: float = 2866.0,
    C: float = 1643.0,
) -> np.ndarray:
    """Discrete Tougaard-like background (universal cross-section form)."""
    be = np.asarray(be, dtype=float)
    y = np.asarray(intensity, dtype=float)
    n = len(y)
    bg = np.zeros(n, dtype=float)
    # XPS BE often decreasing; use absolute energy loss along the axis
    for i in range(n):
        acc = 0.0
        for j in range(i + 1, n):
            de = abs(be[i] - be[j])
            if de < 1e-9:
                continue
            k = B * de / ((C + de**2) ** 2)
            # approximate dx
            dx = abs(be[j] - be[j - 1]) if j > 0 else abs(be[1] - be[0])
            acc += k * y[j] * dx
        bg[i] = acc
    # scale so endpoints roughly match data ends (practical XPS tweak)
    if bg.max() > 0:
        scale = (y[0] - y[-1]) / (bg[0] - bg[-1] + 1e-12) if abs(bg[0] - bg[-1]) > 1e-12 else 1.0
        if not np.isfinite(scale) or scale <= 0:
            scale = (y.mean() / (bg.mean() + 1e-12))
        bg = bg * abs(scale)
        # shift to sit under the spectrum endpoints
        bg = bg - bg[-1] + y[-1]
    return bg


def compute_baseline(
    be: np.ndarray,
    intensity: np.ndarray,
    settings: BaselineSettings,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return (corrected_intensity, baseline)."""
    be = np.asarray(be, dtype=float)
    y = np.asarray(intensity, dtype=float)
    method = settings.method

    auto = auto_edge_windows(be, settings.edge_fraction) if method.startswith("median") else []
    windows = merge_windows(auto, settings.manual_windows)

    if method == "none":
        baseline = np.zeros_like(y)
    elif method == "median_horizontal":
        baseline = baseline_median_horizontal(be, y, windows)
    elif method == "median_linear":
        baseline = baseline_median_linear(be, y, windows)
    elif method == "rolling_median":
        baseline = baseline_rolling_median(y, settings.rolling_window)
    elif method == "asls":
        baseline = baseline_asls(y)
    elif method == "snip":
        baseline = baseline_snip(y)
    elif method == "linear_endpoints":
        baseline = baseline_linear_endpoints(y)
    elif method == "polynomial_edges":
        baseline = baseline_polynomial_edges(be, y, settings.poly_degree)
    elif method == "shirley":
        baseline = baseline_shirley(y, settings.shirley_max_iter)
    elif method == "tougaard":
        baseline = baseline_tougaard(be, y, settings.tougaard_B, settings.tougaard_C)
    else:
        raise ValueError(f"Unknown baseline method: {method}")

    corrected = y - baseline if settings.subtract else y.copy()
    return corrected, baseline
