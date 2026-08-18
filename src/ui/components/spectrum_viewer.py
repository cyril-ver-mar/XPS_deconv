"""Reusable spectrum viewer with invert-X, axis ranges, reset, trace toggles.

Plot first; invert is a compact control that does not reset axis/trace settings.
Other plot settings live in a collapsed accordion below.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np
import streamlit as st

from src.core.models import BeWindow
from src.ui.components.help import help_mark, labeled_help
from src.ui.components.plot_export import render_plot_export_controls
from src.ui.components.plot_settings import apply_style_to_view, render_plot_style_controls, seed_plot_style_state
from src.ui.components.plots import PlotViewState, spectrum_figure
from src.utils.i18n import DEFAULT_LANG, t


def _ensure_view(key: str) -> PlotViewState:
    store_key = f"plot_view_{key}"
    if store_key not in st.session_state:
        st.session_state[store_key] = PlotViewState()
    return st.session_state[store_key]


def _series_y_bounds(*arrays: Optional[np.ndarray]) -> tuple[float, float]:
    vals: List[float] = []
    for arr in arrays:
        if arr is None:
            continue
        a = np.asarray(arr, dtype=float)
        if a.size:
            vals.append(float(np.nanmin(a)))
            vals.append(float(np.nanmax(a)))
    if not vals:
        return 0.0, 1.0
    ymin, ymax = min(vals), max(vals)
    pad = (ymax - ymin) * 0.05 + 1e-9
    return ymin - pad, ymax + pad


def _seed_plot_state(
    viewer_key: str,
    view: PlotViewState,
    data_xmin: float,
    data_xmax: float,
    data_ymin: float,
    data_ymax: float,
) -> None:
    """Seed plot widget keys.

    - If not yet initialized (or flag was cleared for refit): write ranges from data.
    - If initialized: only fill **missing** keys (repair stale sessions) without
      overwriting user xmin/xmax/invert/traces.
    """
    init_flag = f"{viewer_key}_ranges_initialized"
    defaults = {
        f"{viewer_key}_xmin": data_xmin,
        f"{viewer_key}_xmax": data_xmax,
        f"{viewer_key}_ymin": data_ymin,
        f"{viewer_key}_ymax": data_ymax,
        f"{viewer_key}_invx": True,
        f"{viewer_key}_alpha": float(view.fill_alpha),
        f"{viewer_key}_pbe": False,
        f"{viewer_key}_pbe_d": 2,
    }
    if not st.session_state.get(init_flag):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.session_state[init_flag] = True
        return
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_spectrum_viewer(
    be: np.ndarray,
    intensity: np.ndarray,
    *,
    viewer_key: str,
    title: str = "",
    lang: str = DEFAULT_LANG,
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
    show_trace_toggles: bool = True,
) -> PlotViewState:
    """Draw spectrum first, then optional collapsed plot settings."""
    view = _ensure_view(viewer_key)
    be = np.asarray(be, dtype=float)
    intensity = np.asarray(intensity, dtype=float)
    if be.size == 0:
        st.warning(t("empty_spectrum", lang))
        return view

    data_xmin, data_xmax = float(be.min()), float(be.max())
    data_ymin, data_ymax = _series_y_bounds(
        intensity,
        baseline,
        corrected,
        denoised,
        best_fit,
        previous_fit,
        *(list(components) if components else []),
    )

    _seed_plot_state(viewer_key, view, data_xmin, data_xmax, data_ymin, data_ymax)
    seed_plot_style_state(viewer_key, lang)

    vis_keys = {
        "raw": f"{viewer_key}_tr",
        "denoised": f"{viewer_key}_td",
        "baseline": f"{viewer_key}_tb",
        "corrected": f"{viewer_key}_tc",
        "best_fit": f"{viewer_key}_tf",
        "previous_fit": f"{viewer_key}_tp",
        "components": f"{viewer_key}_tcomp",
        "fills": f"{viewer_key}_tfill",
    }
    for attr, key in vis_keys.items():
        if key not in st.session_state:
            st.session_state[key] = getattr(view.visibility, attr)

    # Compact invert control — does not touch axis ranges or trace flags
    if f"{viewer_key}_invx" not in st.session_state:
        st.session_state[f"{viewer_key}_invx"] = True
    if f"{viewer_key}_pbe" not in st.session_state:
        st.session_state[f"{viewer_key}_pbe"] = False
    if f"{viewer_key}_pbe_d" not in st.session_state:
        st.session_state[f"{viewer_key}_pbe_d"] = 2
    inv_col, help_col = st.columns([1, 0.15])
    with inv_col:
        st.checkbox(t("invert_x", lang), key=f"{viewer_key}_invx", help=t("invert_x_help", lang))
    with help_col:
        help_mark("invert_x", lang)

    if components:
        lb, dg, hp = st.columns([1.4, 0.8, 0.2])
        with lb:
            st.checkbox(t("plot_peak_be_labels", lang), key=f"{viewer_key}_pbe")
        with dg:
            st.number_input(
                t("plot_peak_be_digits", lang),
                min_value=0,
                max_value=6,
                step=1,
                key=f"{viewer_key}_pbe_d",
            )
        with hp:
            help_mark("peak_be_labels", lang)

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    # Load retained settings (safe gets — never KeyError)
    view.invert_x = bool(st.session_state.get(f"{viewer_key}_invx", True))
    view.x_min = float(st.session_state.get(f"{viewer_key}_xmin", data_xmin))
    view.x_max = float(st.session_state.get(f"{viewer_key}_xmax", data_xmax))
    view.y_min = float(st.session_state.get(f"{viewer_key}_ymin", data_ymin))
    view.y_max = float(st.session_state.get(f"{viewer_key}_ymax", data_ymax))
    view.fill_alpha = float(st.session_state.get(f"{viewer_key}_alpha", view.fill_alpha))
    view.show_peak_be_labels = bool(st.session_state.get(f"{viewer_key}_pbe", False))
    view.peak_be_digits = int(st.session_state.get(f"{viewer_key}_pbe_d", 2))
    for attr, key in vis_keys.items():
        setattr(view.visibility, attr, bool(st.session_state.get(key, True)))
    view = apply_style_to_view(view, viewer_key, lang)

    st.session_state[f"plot_view_{viewer_key}"] = view
    if title:
        st.markdown(f"**{title}**")
        st.markdown('<div style="height: 0.35rem;"></div>', unsafe_allow_html=True)
    fig = spectrum_figure(
        be,
        intensity,
        title="",  # Streamlit owns the title — avoids colliding with Plotly legend
        region=region,
        baseline=baseline,
        corrected=corrected,
        denoised=denoised,
        best_fit=best_fit,
        components=components,
        component_names=component_names,
        bg_windows=bg_windows,
        highlight_full=highlight_full,
        previous_fit=previous_fit,
        view=view,
        lang=lang,
    )
    # Constant uirevision — invert must not remount ranges
    fig.update_layout(uirevision=f"{viewer_key}-stable")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(t("plot_settings", lang), expanded=False):
        tab_view, tab_style, tab_export = st.tabs(
            [
                t("plot_tab_view", lang),
                t("plot_tab_style", lang),
                t("plot_tab_export", lang),
            ]
        )
        with tab_view:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(t("fit_all_view", lang), key=f"{viewer_key}_fitdata"):
                    st.session_state[f"{viewer_key}_xmin"] = data_xmin
                    st.session_state[f"{viewer_key}_xmax"] = data_xmax
                    st.session_state[f"{viewer_key}_ymin"] = data_ymin
                    st.session_state[f"{viewer_key}_ymax"] = data_ymax
                    st.rerun()
                if st.button(t("reset_view", lang), key=f"{viewer_key}_reset"):
                    st.session_state[f"{viewer_key}_xmin"] = data_xmin
                    st.session_state[f"{viewer_key}_xmax"] = data_xmax
                    st.session_state[f"{viewer_key}_ymin"] = data_ymin
                    st.session_state[f"{viewer_key}_ymax"] = data_ymax
                    st.rerun()
            with c2:
                labeled_help(t("fill_alpha", lang), "fill_alpha", lang)
                st.slider(t("fill_alpha", lang), 0.0, 1.0, key=f"{viewer_key}_alpha")

            ax1, ax2 = st.columns(2)
            with ax1:
                labeled_help(t("x_range_label", lang), "axis_x", lang)
                st.number_input(t("x_min", lang), key=f"{viewer_key}_xmin", format="%.4f")
                st.number_input(t("x_max", lang), key=f"{viewer_key}_xmax", format="%.4f")
            with ax2:
                labeled_help(t("y_range_label", lang), "axis_y", lang)
                st.number_input(t("y_min", lang), key=f"{viewer_key}_ymin", format="%.4f")
                st.number_input(t("y_max", lang), key=f"{viewer_key}_ymax", format="%.4f")

            if show_trace_toggles:
                labeled_help(t("show_traces", lang), "show_traces", lang)
                t1, t2, t3, t4 = st.columns(4)
                with t1:
                    st.checkbox(t("trace_raw", lang), key=vis_keys["raw"])
                    st.checkbox(t("trace_denoised", lang), key=vis_keys["denoised"])
                with t2:
                    st.checkbox(t("trace_baseline", lang), key=vis_keys["baseline"])
                    st.checkbox(t("trace_corrected", lang), key=vis_keys["corrected"])
                with t3:
                    st.checkbox(t("trace_total_fit", lang), key=vis_keys["best_fit"])
                    st.checkbox(t("trace_previous", lang), key=vis_keys["previous_fit"])
                with t4:
                    st.checkbox(t("trace_components", lang), key=vis_keys["components"])
                    st.checkbox(t("trace_fills", lang), key=vis_keys["fills"])

        with tab_style:
            render_plot_style_controls(viewer_key, lang)

        with tab_export:
            stem = title.strip() if title else viewer_key
            render_plot_export_controls(fig, key=viewer_key, lang=lang, default_stem=stem or "spectrum")

    return view
