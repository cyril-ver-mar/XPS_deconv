"""Plotly spectrum helpers with display options (Layer 5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np
import plotly.graph_objects as go

from src.core.models import BeWindow

DEFAULT_COMPONENT_COLORS = [
    "#e41a1c",
    "#377eb8",
    "#4daf4a",
    "#984ea3",
    "#ff7f00",
    "#a65628",
    "#f781bf",
    "#999999",
]

# Legend below the axes so it never overlaps Streamlit page headers / captions.
SAFE_PLOT_LEGEND = dict(
    orientation="h",
    yanchor="top",
    y=-0.22,
    x=0.0,
    xanchor="left",
    bgcolor="rgba(255,255,255,0.85)",
    borderwidth=0,
    font=dict(size=11),
)
SAFE_PLOT_MARGIN = dict(l=56, r=28, t=56, b=120)


@dataclass
class TraceVisibility:
    raw: bool = True
    denoised: bool = True
    baseline: bool = True
    corrected: bool = True
    best_fit: bool = True
    components: bool = True
    fills: bool = True
    previous_fit: bool = True
    region: bool = True
    bg_windows: bool = True


@dataclass
class PlotViewState:
    invert_x: bool = True  # XPS default: high BE on the left
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    fill_alpha: float = 0.35
    component_colors: List[str] = field(default_factory=lambda: list(DEFAULT_COMPONENT_COLORS))
    visibility: TraceVisibility = field(default_factory=TraceVisibility)


def spectrum_figure(
    be: np.ndarray,
    intensity: np.ndarray,
    *,
    title: str = "",
    region: Optional[BeWindow] = None,
    baseline: Optional[np.ndarray] = None,
    corrected: Optional[np.ndarray] = None,
    denoised: Optional[np.ndarray] = None,
    best_fit: Optional[np.ndarray] = None,
    components: Optional[Sequence[np.ndarray]] = None,
    component_names: Optional[Sequence[str]] = None,
    bg_windows: Optional[Sequence[BeWindow]] = None,
    highlight_full: Optional[tuple[np.ndarray, np.ndarray]] = None,
    previous_fit: Optional[np.ndarray] = None,
    view: Optional[PlotViewState] = None,
) -> go.Figure:
    view = view or PlotViewState()
    vis = view.visibility
    fig = go.Figure()

    if highlight_full is not None:
        fbe, fint = highlight_full
        fig.add_trace(
            go.Scatter(
                x=fbe,
                y=fint,
                mode="lines",
                name="Full spectrum",
                line=dict(color="#bbbbbb", width=1),
            )
        )

    if vis.raw:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=intensity,
                mode="lines",
                name="Raw",
                line=dict(color="#1f77b4", width=2),
            )
        )
    if vis.denoised and denoised is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=denoised,
                mode="lines",
                name="Denoised",
                line=dict(color="#17becf", width=1.5, dash="dot"),
            )
        )
    if vis.baseline and baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=baseline,
                mode="lines",
                name="Baseline",
                line=dict(color="#d62728", width=2, dash="dash"),
            )
        )
    if vis.corrected and corrected is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=corrected,
                mode="lines",
                name="After baseline",
                line=dict(color="#2ca02c", width=2),
            )
        )
    if vis.previous_fit and previous_fit is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=previous_fit,
                mode="lines",
                name="Previous fit",
                line=dict(color="#888888", width=2),
                opacity=0.45,
            )
        )
    if vis.best_fit and best_fit is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=best_fit,
                mode="lines",
                name="Total fit",
                line=dict(color="#111111", width=2.5),
            )
        )

    if components and (vis.components or vis.fills):
        for i, comp in enumerate(components):
            if comp is None:
                continue
            color = view.component_colors[i % len(view.component_colors)]
            name = (
                component_names[i]
                if component_names and i < len(component_names)
                else f"Component {i + 1}"
            )
            if vis.fills:
                fig.add_trace(
                    go.Scatter(
                        x=be,
                        y=comp,
                        mode="lines",
                        name=f"{name} fill",
                        line=dict(width=0),
                        fill="tozeroy",
                        fillcolor=_hex_alpha(color, view.fill_alpha),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )
            if vis.components:
                fig.add_trace(
                    go.Scatter(
                        x=be,
                        y=comp,
                        mode="lines",
                        name=name,
                        line=dict(color=color, width=1.5),
                    )
                )

    if vis.region and region is not None:
        lo, hi = region
        fig.add_vrect(x0=lo, x1=hi, fillcolor="blue", opacity=0.08, line_width=0)
    if vis.bg_windows and bg_windows:
        for lo, hi in bg_windows:
            fig.add_vrect(x0=lo, x1=hi, fillcolor="orange", opacity=0.15, line_width=0)

    fig.update_layout(
        title=dict(text=title or "", y=0.98, pad=dict(t=4, b=8)) if title else None,
        xaxis_title="Binding energy (eV)",
        yaxis_title="Intensity",
        template="plotly_white",
        legend=SAFE_PLOT_LEGEND,
        margin=SAFE_PLOT_MARGIN,
        height=560,
        uirevision="xps-spectrum",
    )

    # Axis ranges
    be_arr = np.asarray(be, dtype=float)
    data_xmin = float(np.min(be_arr)) if be_arr.size else 0.0
    data_xmax = float(np.max(be_arr)) if be_arr.size else 1.0
    xmin = view.x_min if view.x_min is not None else data_xmin
    xmax = view.x_max if view.x_max is not None else data_xmax
    if view.invert_x:
        fig.update_xaxes(range=[max(xmin, xmax), min(xmin, xmax)])
    else:
        fig.update_xaxes(range=[min(xmin, xmax), max(xmin, xmax)])

    if view.y_min is not None or view.y_max is not None:
        ymin = view.y_min if view.y_min is not None else 0
        ymax = view.y_max if view.y_max is not None else None
        fig.update_yaxes(range=[ymin, ymax] if ymax is not None else None)
    return fig


def _hex_alpha(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return f"rgba(100,100,100,{alpha})"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
