"""Plotly spectrum helpers with display options (Layer 5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import numpy as np
import plotly.graph_objects as go

from src.core.models import BeWindow, ElementBeBand
from src.utils.i18n import DEFAULT_LANG, t

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
class PlotStyle:
    """Publication-oriented appearance (live-previewed in Plot settings)."""

    title: str = ""
    x_title: str = ""
    y_title: str = ""
    font_family: str = "Arial"
    font_size: int = 14
    title_size: int = 16
    tick_size: int = 12
    legend_size: int = 11
    axis_color: str = "#111111"
    grid_on: bool = False
    grid_color: str = "#cccccc"
    compact_y_ticks: bool = False
    paper_bg: str = "#ffffff"
    plot_bg: str = "#ffffff"
    show_legend: bool = True
    raw_color: str = "#1f77b4"
    raw_width: float = 2.0
    denoised_color: str = "#17becf"
    denoised_width: float = 1.5
    baseline_color: str = "#d62728"
    baseline_width: float = 2.0
    corrected_color: str = "#2ca02c"
    corrected_width: float = 2.0
    best_fit_color: str = "#111111"
    best_fit_width: float = 2.5
    previous_fit_color: str = "#888888"
    previous_fit_width: float = 2.0
    component_width: float = 1.5
    full_spectrum_color: str = "#bbbbbb"
    full_spectrum_width: float = 1.0


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
    style: PlotStyle = field(default_factory=PlotStyle)
    element_bands: List[ElementBeBand] = field(default_factory=list)
    show_peak_be_labels: bool = False
    peak_be_digits: int = 2


def _localized_axis_title(value: str, key: str, lang: str) -> str:
    """Use the language default unless the user typed a custom axis name."""
    text = (value or "").strip()
    known = {t(key, "en"), t(key, "ru")}
    if not text or text in known:
        return t(key, lang)
    return text


def _aligned(y: Optional[np.ndarray], n: int) -> Optional[np.ndarray]:
    """Drop overlay series that belong to a different spectrum (wrong length)."""
    if y is None:
        return None
    arr = np.asarray(y, dtype=float)
    if arr.size != n:
        return None
    return arr


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
    lang: Optional[str] = None,
) -> go.Figure:
    view = view or PlotViewState()
    vis = view.visibility
    style = view.style
    lang = lang or DEFAULT_LANG
    if title and not style.title:
        style = PlotStyle(**{**style.__dict__, "title": title})
    fig = go.Figure()
    be = np.asarray(be, dtype=float)
    intensity = np.asarray(intensity, dtype=float)
    n = int(be.size)
    baseline = _aligned(baseline, n)
    corrected = _aligned(corrected, n)
    denoised = _aligned(denoised, n)
    best_fit = _aligned(best_fit, n)
    previous_fit = _aligned(previous_fit, n)
    if components:
        aligned_comps: list[Optional[np.ndarray]] = []
        for comp in components:
            aligned_comps.append(_aligned(None if comp is None else np.asarray(comp), n))
        components = aligned_comps

    if highlight_full is not None:
        fbe, fint = highlight_full
        fig.add_trace(
            go.Scatter(
                x=fbe,
                y=fint,
                mode="lines",
                name=t("trace_full_spectrum", lang),
                line=dict(color=style.full_spectrum_color, width=style.full_spectrum_width),
            )
        )

    if vis.raw:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=intensity,
                mode="lines",
                name=t("trace_raw", lang),
                line=dict(color=style.raw_color, width=style.raw_width),
            )
        )
    if vis.denoised and denoised is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=denoised,
                mode="lines",
                name=t("trace_denoised", lang),
                line=dict(color=style.denoised_color, width=style.denoised_width, dash="dot"),
            )
        )
    if vis.baseline and baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=baseline,
                mode="lines",
                name=t("trace_baseline", lang),
                line=dict(color=style.baseline_color, width=style.baseline_width, dash="dash"),
            )
        )
    if vis.corrected and corrected is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=corrected,
                mode="lines",
                name=t("trace_corrected", lang),
                line=dict(color=style.corrected_color, width=style.corrected_width),
            )
        )
    if vis.previous_fit and previous_fit is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=previous_fit,
                mode="lines",
                name=t("trace_previous", lang),
                line=dict(color=style.previous_fit_color, width=style.previous_fit_width),
                opacity=0.45,
            )
        )
    if vis.best_fit and best_fit is not None:
        fig.add_trace(
            go.Scatter(
                x=be,
                y=best_fit,
                mode="lines",
                name=t("trace_total_fit", lang),
                line=dict(color=style.best_fit_color, width=style.best_fit_width),
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
                else t("trace_component_n", lang, n=i + 1)
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
                        line=dict(color=color, width=style.component_width),
                    )
                )

    if view.show_peak_be_labels and components:
        digits = max(0, min(8, int(view.peak_be_digits)))
        for i, comp in enumerate(components):
            if comp is None or not np.any(np.isfinite(comp)):
                continue
            idx = int(np.nanargmax(comp))
            x_at = float(be[idx])
            y_at = float(comp[idx])
            color = view.component_colors[i % len(view.component_colors)]
            fig.add_annotation(
                x=x_at,
                y=y_at,
                xref="x",
                yref="y",
                text=f"{x_at:.{digits}f}",
                showarrow=False,
                yshift=10,
                font=dict(
                    family=style.font_family,
                    size=max(9, style.tick_size),
                    color=color,
                ),
            )

    if vis.region and region is not None:
        lo, hi = region
        fig.add_vrect(x0=lo, x1=hi, fillcolor="blue", opacity=0.08, line_width=0, layer="below")
    if vis.bg_windows and bg_windows:
        for lo, hi in bg_windows:
            fig.add_vrect(x0=lo, x1=hi, fillcolor="orange", opacity=0.15, line_width=0, layer="below")
    for band in view.element_bands:
        fig.add_vrect(
            x0=band.x0,
            x1=band.x1,
            fillcolor=band.default_color,
            opacity=0.16,
            line_width=0,
            layer="below",
        )
        fig.add_annotation(
            x=(band.x0 + band.x1) / 2.0,
            y=1.0,
            xref="x",
            yref="paper",
            text=band.label,
            showarrow=False,
            yshift=12,
            font=dict(
                family=style.font_family,
                size=max(9, style.tick_size),
                color=style.axis_color,
            ),
        )

    axis_font = dict(family=style.font_family, size=style.font_size, color=style.axis_color)
    tick_font = dict(family=style.font_family, size=style.tick_size, color=style.axis_color)
    legend = dict(SAFE_PLOT_LEGEND)
    legend["font"] = dict(family=style.font_family, size=style.legend_size, color=style.axis_color)
    legend["bgcolor"] = "rgba(255,255,255,0.85)" if style.plot_bg.lower() in ("#ffffff", "white") else style.plot_bg

    fig.update_layout(
        title=(
            dict(
                text=style.title,
                y=0.98,
                pad=dict(t=4, b=8),
                font=dict(family=style.font_family, size=style.title_size, color=style.axis_color),
            )
            if style.title
            else None
        ),
        font=dict(family=style.font_family, size=style.font_size, color=style.axis_color),
        xaxis_title=_localized_axis_title(style.x_title, "plot_default_x", lang),
        yaxis_title=_localized_axis_title(style.y_title, "plot_default_y", lang),
        template="plotly_white",
        legend=legend,
        showlegend=style.show_legend,
        margin={**SAFE_PLOT_MARGIN, "t": 80 if view.element_bands else SAFE_PLOT_MARGIN["t"]},
        height=560,
        uirevision="xps-spectrum",
        paper_bgcolor=style.paper_bg,
        plot_bgcolor=style.plot_bg,
    )
    minor = dict(
        showgrid=bool(style.grid_on),
        gridcolor=style.grid_color,
        griddash="dot",
        nticks=5,
        ticklen=3,
    )
    fig.update_xaxes(
        title_font=axis_font,
        tickfont=tick_font,
        linecolor=style.axis_color,
        tickcolor=style.axis_color,
        zerolinecolor=style.axis_color,
        gridcolor=style.grid_color,
        showgrid=style.grid_on,
        minor=minor,
        zeroline=False,
        mirror=True,
        ticks="outside",
        showline=True,
    )
    y_extra: dict = {}
    if style.compact_y_ticks:
        y_extra = {"exponentformat": "SI", "minexponent": 3}
    else:
        y_extra = {"exponentformat": "none"}
    fig.update_yaxes(
        title_font=axis_font,
        tickfont=tick_font,
        linecolor=style.axis_color,
        tickcolor=style.axis_color,
        zerolinecolor=style.axis_color,
        gridcolor=style.grid_color,
        showgrid=style.grid_on,
        minor=minor,
        zeroline=False,
        mirror=True,
        ticks="outside",
        showline=True,
        **y_extra,
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
        if ymax is not None and view.show_peak_be_labels:
            span = float(ymax) - float(ymin)
            ymax = float(ymax) + max(span * 0.08, 1e-9)
        fig.update_yaxes(range=[ymin, ymax] if ymax is not None else None)
    return fig


def _hex_alpha(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return f"rgba(100,100,100,{alpha})"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
