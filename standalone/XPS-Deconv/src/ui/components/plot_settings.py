"""Plot appearance controls (Layer 5) — live preview via session_state keys."""

from __future__ import annotations

import streamlit as st

from src.core.models import ELEMENT_BE_BANDS, ElementBeBand
from src.ui.components.help import labeled_help
from src.ui.components.plots import DEFAULT_COMPONENT_COLORS, PlotStyle, PlotViewState
from src.utils.i18n import DEFAULT_LANG, t

FONT_CHOICES = [
    "Arial",
    "Helvetica",
    "Times New Roman",
    "Times",
    "Georgia",
    "Courier New",
    "DejaVu Sans",
    "STIXGeneral",
]

_STYLE_DEFAULTS: dict[str, object] = {
    "ptitle": "",
    "font": "Arial",
    "fsize": 14,
    "tsize": 16,
    "ticksize": 12,
    "legsize": 11,
    "axis_c": "#111111",
    "grid": False,
    "grid_c": "#cccccc",
    "paper": "#ffffff",
    "plotbg": "#ffffff",
    "legend": True,
    "compact_y": False,
    "ebands": False,
    "raw_c": "#1f77b4",
    "raw_w": 2.0,
    "den_c": "#17becf",
    "den_w": 1.5,
    "bl_c": "#d62728",
    "bl_w": 2.0,
    "cor_c": "#2ca02c",
    "cor_w": 2.0,
    "fit_c": "#111111",
    "fit_w": 2.5,
    "prev_c": "#888888",
    "prev_w": 2.0,
    "comp_w": 1.5,
}


def _sk(viewer_key: str, suffix: str) -> str:
    return f"{viewer_key}_{suffix}"


def _lang() -> str:
    return str(st.session_state.get("lang", DEFAULT_LANG))


def _sync_axis_title_defaults(viewer_key: str, lang: str) -> None:
    """Keep factory axis names in the current language; leave custom names alone."""
    known_x = {t("plot_default_x", "en"), t("plot_default_x", "ru")}
    known_y = {t("plot_default_y", "en"), t("plot_default_y", "ru")}
    x_key = _sk(viewer_key, "xtitle")
    y_key = _sk(viewer_key, "ytitle")
    x_val = str(st.session_state.get(x_key, "")).strip()
    y_val = str(st.session_state.get(y_key, "")).strip()
    if not x_val or x_val in known_x:
        st.session_state[x_key] = t("plot_default_x", lang)
    if not y_val or y_val in known_y:
        st.session_state[y_key] = t("plot_default_y", lang)


def seed_plot_style_state(viewer_key: str, lang: str | None = None) -> None:
    """Fill missing style keys only — never overwrite user choices."""
    lang = lang or _lang()
    for suffix, value in _STYLE_DEFAULTS.items():
        key = _sk(viewer_key, suffix)
        if key not in st.session_state:
            st.session_state[key] = value
    for i, color in enumerate(DEFAULT_COMPONENT_COLORS):
        key = _sk(viewer_key, f"cc{i}")
        if key not in st.session_state:
            st.session_state[key] = color
    for band in ELEMENT_BE_BANDS:
        on_key = _sk(viewer_key, f"eb_{band.band_id}")
        c_key = _sk(viewer_key, f"ebc_{band.band_id}")
        if on_key not in st.session_state:
            st.session_state[on_key] = False
        if c_key not in st.session_state:
            st.session_state[c_key] = band.default_color
    _sync_axis_title_defaults(viewer_key, lang)


def reset_plot_style_state(viewer_key: str, lang: str | None = None) -> None:
    lang = lang or _lang()
    for suffix, value in _STYLE_DEFAULTS.items():
        st.session_state[_sk(viewer_key, suffix)] = value
    for i, color in enumerate(DEFAULT_COMPONENT_COLORS):
        st.session_state[_sk(viewer_key, f"cc{i}")] = color
    for band in ELEMENT_BE_BANDS:
        st.session_state[_sk(viewer_key, f"eb_{band.band_id}")] = False
        st.session_state[_sk(viewer_key, f"ebc_{band.band_id}")] = band.default_color
    st.session_state[_sk(viewer_key, "xtitle")] = t("plot_default_x", lang)
    st.session_state[_sk(viewer_key, "ytitle")] = t("plot_default_y", lang)


def read_plot_style(viewer_key: str, lang: str | None = None) -> tuple[PlotStyle, list[str]]:
    seed_plot_style_state(viewer_key, lang)
    colors = [
        str(st.session_state.get(_sk(viewer_key, f"cc{i}"), DEFAULT_COMPONENT_COLORS[i]))
        for i in range(len(DEFAULT_COMPONENT_COLORS))
    ]
    return PlotStyle(
        title=str(st.session_state.get(_sk(viewer_key, "ptitle"), "")),
        x_title=str(st.session_state.get(_sk(viewer_key, "xtitle"), t("plot_default_x", _lang()))),
        y_title=str(st.session_state.get(_sk(viewer_key, "ytitle"), t("plot_default_y", _lang()))),
        font_family=str(st.session_state.get(_sk(viewer_key, "font"), "Arial")),
        font_size=int(st.session_state.get(_sk(viewer_key, "fsize"), 14)),
        title_size=int(st.session_state.get(_sk(viewer_key, "tsize"), 16)),
        tick_size=int(st.session_state.get(_sk(viewer_key, "ticksize"), 12)),
        legend_size=int(st.session_state.get(_sk(viewer_key, "legsize"), 11)),
        axis_color=str(st.session_state.get(_sk(viewer_key, "axis_c"), "#111111")),
        grid_on=bool(st.session_state.get(_sk(viewer_key, "grid"), False)),
        grid_color=str(st.session_state.get(_sk(viewer_key, "grid_c"), "#cccccc")),
        paper_bg=str(st.session_state.get(_sk(viewer_key, "paper"), "#ffffff")),
        plot_bg=str(st.session_state.get(_sk(viewer_key, "plotbg"), "#ffffff")),
        show_legend=bool(st.session_state.get(_sk(viewer_key, "legend"), True)),
        compact_y_ticks=bool(st.session_state.get(_sk(viewer_key, "compact_y"), False)),
        raw_color=str(st.session_state.get(_sk(viewer_key, "raw_c"), "#1f77b4")),
        raw_width=float(st.session_state.get(_sk(viewer_key, "raw_w"), 2.0)),
        denoised_color=str(st.session_state.get(_sk(viewer_key, "den_c"), "#17becf")),
        denoised_width=float(st.session_state.get(_sk(viewer_key, "den_w"), 1.5)),
        baseline_color=str(st.session_state.get(_sk(viewer_key, "bl_c"), "#d62728")),
        baseline_width=float(st.session_state.get(_sk(viewer_key, "bl_w"), 2.0)),
        corrected_color=str(st.session_state.get(_sk(viewer_key, "cor_c"), "#2ca02c")),
        corrected_width=float(st.session_state.get(_sk(viewer_key, "cor_w"), 2.0)),
        best_fit_color=str(st.session_state.get(_sk(viewer_key, "fit_c"), "#111111")),
        best_fit_width=float(st.session_state.get(_sk(viewer_key, "fit_w"), 2.5)),
        previous_fit_color=str(st.session_state.get(_sk(viewer_key, "prev_c"), "#888888")),
        previous_fit_width=float(st.session_state.get(_sk(viewer_key, "prev_w"), 2.0)),
        component_width=float(st.session_state.get(_sk(viewer_key, "comp_w"), 1.5)),
    ), colors


def apply_style_to_view(view: PlotViewState, viewer_key: str, lang: str | None = None) -> PlotViewState:
    style, colors = read_plot_style(viewer_key, lang)
    view.style = style
    view.component_colors = colors
    bands: list[ElementBeBand] = []
    if st.session_state.get(_sk(viewer_key, "ebands"), False):
        for band in ELEMENT_BE_BANDS:
            if not st.session_state.get(_sk(viewer_key, f"eb_{band.band_id}"), False):
                continue
            color = str(st.session_state.get(_sk(viewer_key, f"ebc_{band.band_id}"), band.default_color))
            bands.append(
                ElementBeBand(
                    band_id=band.band_id,
                    label=band.label,
                    x0=band.x0,
                    x1=band.x1,
                    default_color=color,
                )
            )
    view.element_bands = bands
    return view


def render_plot_style_controls(viewer_key: str, lang: str) -> None:
    """Widgets live below the plot; changing them reruns → the figure updates (preview)."""
    seed_plot_style_state(viewer_key, lang)
    st.caption(t("plot_style_preview_hint", lang))
    labeled_help(t("plot_appearance", lang), "plot_style", lang)

    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t("plot_title", lang), key=_sk(viewer_key, "ptitle"))
        st.text_input(t("plot_x_title", lang), key=_sk(viewer_key, "xtitle"))
        st.text_input(t("plot_y_title", lang), key=_sk(viewer_key, "ytitle"))
        st.selectbox(t("plot_font", lang), FONT_CHOICES, key=_sk(viewer_key, "font"))
    with c2:
        st.number_input(t("plot_font_size", lang), min_value=8, max_value=28, step=1, key=_sk(viewer_key, "fsize"))
        st.number_input(t("plot_title_size", lang), min_value=8, max_value=36, step=1, key=_sk(viewer_key, "tsize"))
        st.number_input(t("plot_tick_size", lang), min_value=6, max_value=24, step=1, key=_sk(viewer_key, "ticksize"))
        st.number_input(t("plot_legend_size", lang), min_value=6, max_value=24, step=1, key=_sk(viewer_key, "legsize"))

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.color_picker(t("plot_axis_color", lang), key=_sk(viewer_key, "axis_c"))
    with a2:
        st.color_picker(t("plot_paper_bg", lang), key=_sk(viewer_key, "paper"))
    with a3:
        st.color_picker(t("plot_plot_bg", lang), key=_sk(viewer_key, "plotbg"))
    with a4:
        st.color_picker(t("plot_grid_color", lang), key=_sk(viewer_key, "grid_c"))
    g1, g2, g3 = st.columns(3)
    with g1:
        st.checkbox(t("plot_grid", lang), key=_sk(viewer_key, "grid"))
    with g2:
        st.checkbox(t("plot_show_legend", lang), key=_sk(viewer_key, "legend"))
    with g3:
        st.checkbox(t("plot_compact_y", lang), key=_sk(viewer_key, "compact_y"))

    st.markdown(f"**{t('plot_line_styles', lang)}**")
    rows = [
        ("raw", "trace_raw"),
        ("den", "trace_denoised"),
        ("bl", "trace_baseline"),
        ("cor", "trace_corrected"),
        ("fit", "trace_total_fit"),
        ("prev", "trace_previous"),
    ]
    for suffix, label_key in rows:
        rc, rw = st.columns([1, 1])
        with rc:
            st.color_picker(t(label_key, lang), key=_sk(viewer_key, f"{suffix}_c"))
        with rw:
            st.number_input(
                t("plot_line_width", lang) + f" ({t(label_key, lang)})",
                min_value=0.2,
                max_value=8.0,
                step=0.1,
                key=_sk(viewer_key, f"{suffix}_w"),
            )
    st.number_input(
        t("plot_component_width", lang),
        min_value=0.2,
        max_value=8.0,
        step=0.1,
        key=_sk(viewer_key, "comp_w"),
    )
    st.markdown(f"**{t('plot_component_colors', lang)}**")
    cols = st.columns(4)
    for i in range(len(DEFAULT_COMPONENT_COLORS)):
        with cols[i % 4]:
            st.color_picker(f"{i + 1}", key=_sk(viewer_key, f"cc{i}"))

    st.markdown(f"**{t('plot_element_bands', lang)}**")
    labeled_help(t("plot_element_bands", lang), "element_bands", lang)
    st.checkbox(t("plot_element_bands_show", lang), key=_sk(viewer_key, "ebands"))
    if st.session_state.get(_sk(viewer_key, "ebands"), False):
        for band in ELEMENT_BE_BANDS:
            c_on, c_col = st.columns([1.6, 1])
            with c_on:
                st.checkbox(
                    t(
                        "plot_band_range",
                        lang,
                        label=band.label,
                        x0=f"{band.x0:.0f}",
                        x1=f"{band.x1:.0f}",
                        unit=t("unit_ev", lang),
                    ),
                    key=_sk(viewer_key, f"eb_{band.band_id}"),
                )
            with c_col:
                st.color_picker(
                    t("plot_band_color", lang) + f" ({band.label})",
                    key=_sk(viewer_key, f"ebc_{band.band_id}"),
                )

    if st.button(t("plot_reset_style", lang), key=_sk(viewer_key, "style_reset")):
        reset_plot_style_state(viewer_key, lang)
        st.rerun()
