"""Demo spectra + baseline method gallery (Layer 2 / UI support)."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.baseline import compute_baseline
from src.core.models import BASELINE_METHODS, BaselineSettings


def make_demo_spectrum(n: int = 250) -> Tuple[np.ndarray, np.ndarray]:
    """Synthetic XPS-like region: sloping noise floor + two peaks + step."""
    be = np.linspace(292.0, 280.0, n)
    # sloping background + step under peaks
    bg = 40 + 0.8 * (be - 280) + 25 / (1 + np.exp((be - 286) * 3))
    peak1 = 180 * np.exp(-0.5 * ((be - 284.8) / 0.55) ** 2)
    peak2 = 90 * np.exp(-0.5 * ((be - 286.5) / 0.7) ** 2)
    noise = np.random.default_rng(42).normal(0, 3.0, size=n)
    return be, bg + peak1 + peak2 + noise


def baseline_demo_figure(methods: tuple[str, ...] | None = None) -> go.Figure:
    be, y = make_demo_spectrum()
    methods = methods or tuple(m for m in BASELINE_METHODS if m != "none")
    cols = 2
    rows = int(np.ceil(len(methods) / cols))
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=list(methods),
        shared_xaxes=False,
    )
    for i, method in enumerate(methods):
        r, c = divmod(i, cols)
        settings = BaselineSettings(method=method, edge_fraction=0.12, rolling_window=31)
        try:
            corrected, baseline = compute_baseline(be, y, settings)
        except Exception:  # noqa: BLE001
            corrected, baseline = y.copy(), np.zeros_like(y)
        fig.add_trace(
            go.Scatter(x=be, y=y, mode="lines", line=dict(color="#1f77b4", width=1), showlegend=False),
            row=r + 1,
            col=c + 1,
        )
        fig.add_trace(
            go.Scatter(
                x=be,
                y=baseline,
                mode="lines",
                line=dict(color="#d62728", width=1.5, dash="dash"),
                showlegend=False,
            ),
            row=r + 1,
            col=c + 1,
        )
        fig.update_xaxes(autorange="reversed", row=r + 1, col=c + 1)
    fig.update_layout(
        height=220 * rows,
        title="Baseline methods on a synthetic demo spectrum (blue=data, red=baseline)",
        template="plotly_white",
        margin=dict(l=30, r=20, t=60, b=30),
    )
    return fig


BASELINE_METHOD_BLURBS: Dict[str, str] = {
    "none": "No baseline subtraction.",
    "median_horizontal": "Median of background windows → flat line (noise floor).",
    "median_linear": "Medians of left/right (or manual) windows → straight baseline (recommended default).",
    "rolling_median": "Sliding median across the whole curve — smooth under peaks if window is large.",
    "asls": "Asymmetric least squares — flexible smooth background.",
    "snip": "SNIP clipping — iteratively peels peaks to reveal background.",
    "linear_endpoints": "Straight line from first to last point (notebook-style).",
    "polynomial_edges": "Polynomial fit using only edge points.",
    "shirley": "Classic XPS Shirley step under the peak envelope.",
    "tougaard": "Inelastic-loss style Tougaard background (tune B, C).",
}
