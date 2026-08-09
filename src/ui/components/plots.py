"""Plotly spectrum helpers (Layer 5)."""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import plotly.graph_objects as go

from src.core.models import BeWindow


def spectrum_figure(
    be: np.ndarray,
    intensity: np.ndarray,
    *,
    title: str = "",
    region: Optional[BeWindow] = None,
    baseline: Optional[np.ndarray] = None,
    corrected: Optional[np.ndarray] = None,
    best_fit: Optional[np.ndarray] = None,
    components: Optional[Sequence[np.ndarray]] = None,
    bg_windows: Optional[Sequence[BeWindow]] = None,
    highlight_full: Optional[tuple[np.ndarray, np.ndarray]] = None,
) -> go.Figure:
    fig = go.Figure()
    if highlight_full is not None:
        fbe, fint = highlight_full
        fig.add_trace(
            go.Scatter(x=fbe, y=fint, mode="lines", name="Full spectrum", line=dict(color="#999", width=1))
        )
    fig.add_trace(
        go.Scatter(x=be, y=intensity, mode="lines", name="Spectrum", line=dict(color="#1f77b4", width=2))
    )
    if corrected is not None:
        fig.add_trace(
            go.Scatter(x=be, y=corrected, mode="lines", name="After baseline", line=dict(color="#2ca02c", width=2))
        )
    if baseline is not None:
        fig.add_trace(
            go.Scatter(x=be, y=baseline, mode="lines", name="Baseline", line=dict(color="#d62728", width=2, dash="dash"))
        )
    if best_fit is not None:
        fig.add_trace(
            go.Scatter(x=be, y=best_fit, mode="lines", name="Total fit", line=dict(color="#111", width=2))
        )
    if components:
        for i, comp in enumerate(components):
            fig.add_trace(
                go.Scatter(x=be, y=comp, mode="lines", name=f"Component {i+1}", line=dict(width=1), opacity=0.8)
            )
    if region is not None:
        lo, hi = region
        fig.add_vrect(x0=lo, x1=hi, fillcolor="blue", opacity=0.08, line_width=0)
    if bg_windows:
        for lo, hi in bg_windows:
            fig.add_vrect(x0=lo, x1=hi, fillcolor="orange", opacity=0.15, line_width=0)

    fig.update_layout(
        title=title,
        xaxis_title="Binding energy (eV)",
        yaxis_title="Intensity",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=20, t=60, b=40),
        height=480,
    )
    fig.update_xaxes(autorange="reversed")
    return fig
