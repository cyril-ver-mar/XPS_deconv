"""Baseline + denoise page — separate Preview vs Apply."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.core.baseline import auto_edge_windows, compute_baseline, merge_windows
from src.core.models import BASELINE_METHODS, BaselineSettings
from src.core.noise import DENOISE_METHODS, remove_noise
from src.ui.components.baseline_demos import baseline_blurb, baseline_demo_figure
from src.ui.components.help import help_mark, labeled_help
from src.ui.components.sidebar import render_sidebar
from src.ui.components.spectrum_viewer import render_spectrum_viewer
from src.ui.project_state import persist_session_to_active
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_baseline", lang))
st.info(t("baseline_help_median", lang))

with st.expander(t("baseline_demo_expander", lang), expanded=False):
    st.plotly_chart(baseline_demo_figure(lang=lang), use_container_width=True)

sp = st.session_state.get("active_spectrum") or st.session_state.get("full_spectrum")
if sp is None:
    st.warning(t("need_spectrum", lang))
    st.stop()

bs = st.session_state.baseline_settings

# Seed widget keys once (before widgets)
if "bl_noise_method" not in st.session_state:
    st.session_state["bl_noise_method"] = st.session_state.get("noise_method", "none")
if "bl_noise_window" not in st.session_state:
    st.session_state["bl_noise_window"] = int(st.session_state.get("noise_window", 5))
if "bl_savgol_poly" not in st.session_state:
    st.session_state["bl_savgol_poly"] = int(st.session_state.get("savgol_poly", 2))
if "bl_method" not in st.session_state:
    st.session_state["bl_method"] = bs.method if bs.method in BASELINE_METHODS else "median_linear"
if "bl_edge" not in st.session_state:
    st.session_state["bl_edge"] = float(bs.edge_fraction)
if "bl_poly" not in st.session_state:
    st.session_state["bl_poly"] = int(bs.poly_degree)
if "bl_roll" not in st.session_state:
    st.session_state["bl_roll"] = int(bs.rolling_window)
if "bl_tB" not in st.session_state:
    st.session_state["bl_tB"] = float(bs.tougaard_B)
if "bl_tC" not in st.session_state:
    st.session_state["bl_tC"] = float(bs.tougaard_C)
if "bl_nwin" not in st.session_state:
    st.session_state["bl_nwin"] = len(bs.manual_windows)

st.subheader(t("denoise", lang))
labeled_help(t("denoise_method", lang), "denoise_method", lang)
noise_method = st.selectbox(
    t("denoise_method", lang),
    list(DENOISE_METHODS),
    key="bl_noise_method",
    format_func=lambda m: f"{m} — {t(f'denoise_help_{m}', lang)[:60]}",
)
d1, d2 = st.columns(2)
with d1:
    labeled_help(t("window", lang), "denoise_window", lang)
    noise_window = st.slider(t("window_size", lang), 3, 51, step=2, key="bl_noise_window")
with d2:
    labeled_help(t("savgol_poly", lang), "denoise_savgol_poly", lang)
    savgol_poly = st.number_input(t("savgol_poly", lang), 1, 5, key="bl_savgol_poly")

labeled_help(t("baseline_method", lang), "baseline_method", lang)
method = st.selectbox(
    t("baseline_method", lang),
    options=list(BASELINE_METHODS),
    key="bl_method",
    format_func=lambda m: f"{m} — {baseline_blurb(m, lang)[:70]}",
)
st.caption(baseline_blurb(method, lang))
if method == "shirley":
    help_mark("shirley", lang)
if method == "tougaard":
    help_mark("tougaard", lang)

c1, c2, c3 = st.columns(3)
with c1:
    labeled_help(t("auto_edge_fraction", lang), "edge_fraction", lang)
    edge_fraction = st.slider(t("auto_edge_fraction", lang), 0.02, 0.25, key="bl_edge")
with c2:
    labeled_help(t("poly_degree", lang), "poly_degree", lang)
    poly_degree = st.number_input(t("poly_degree", lang), 1, 5, key="bl_poly")
with c3:
    labeled_help(t("rolling_window", lang), "rolling_window", lang)
    rolling_window = st.number_input(t("rolling_window", lang), 5, 101, step=2, key="bl_roll")

if method == "tougaard":
    bcol, ccol = st.columns(2)
    with bcol:
        tougaard_B = st.number_input(t("tougaard_b", lang), key="bl_tB")
    with ccol:
        tougaard_C = st.number_input(t("tougaard_c", lang), key="bl_tC")
else:
    tougaard_B = float(st.session_state["bl_tB"])
    tougaard_C = float(st.session_state["bl_tC"])

labeled_help(t("manual_bg_windows", lang), "manual_bg", lang)
n_win = st.number_input(t("n_manual_windows", lang), 0, 6, key="bl_nwin")
manual = []
be_lo, be_hi = float(sp.binding_energy.min()), float(sp.binding_energy.max())
existing = list(bs.manual_windows)
for i in range(int(n_win)):
    default = existing[i] if i < len(existing) else (be_lo, be_lo + (be_hi - be_lo) * 0.05)
    if f"bwmin{i}" not in st.session_state:
        st.session_state[f"bwmin{i}"] = float(default[0])
    if f"bwmax{i}" not in st.session_state:
        st.session_state[f"bwmax{i}"] = float(default[1])
    cols = st.columns(2)
    with cols[0]:
        w0 = st.number_input(t("window_n_min", lang, n=i + 1), key=f"bwmin{i}")
    with cols[1]:
        w1 = st.number_input(t("window_n_max", lang, n=i + 1), key=f"bwmax{i}")
    manual.append((min(float(w0), float(w1)), max(float(w0), float(w1))))

settings = BaselineSettings(
    method=str(method),
    edge_fraction=float(edge_fraction),
    manual_windows=manual,
    poly_degree=int(poly_degree),
    rolling_window=int(rolling_window),
    tougaard_B=float(tougaard_B),
    tougaard_C=float(tougaard_C),
    shirley_max_iter=int(bs.shirley_max_iter),
)


def _compute_preview():
    y = remove_noise(
        sp.intensity,
        method=str(noise_method),
        window_size=int(noise_window),
        savgol_poly=int(savgol_poly),
    )
    corrected, baseline = compute_baseline(sp.binding_energy, y, settings)
    return y, corrected, baseline


b1, b2, b3 = st.columns(3)
with b1:
    do_preview = st.button(t("preview", lang), type="secondary")
with b2:
    do_apply = st.button(t("apply_to_session", lang), type="primary")
with b3:
    clear_preview = st.button(t("clear_preview", lang))

if clear_preview:
    for k in (
        "preview_smoothed",
        "preview_corrected",
        "preview_baseline",
        "preview_settings",
        "preview_noise_method",
        "preview_noise_window",
        "preview_savgol_poly",
    ):
        st.session_state.pop(k, None)
    st.rerun()

if do_preview:
    y, corrected, baseline = _compute_preview()
    st.session_state["preview_smoothed"] = y
    st.session_state["preview_corrected"] = corrected
    st.session_state["preview_baseline"] = baseline
    st.session_state["preview_settings"] = settings
    st.session_state["preview_noise_method"] = str(noise_method)
    st.session_state["preview_noise_window"] = int(noise_window)
    st.session_state["preview_savgol_poly"] = int(savgol_poly)
    st.session_state.pop("baseline_page_ranges_initialized", None)
    st.rerun()

if do_apply:
    y, corrected, baseline = _compute_preview()
    st.session_state["baseline_settings"] = settings
    st.session_state["noise_method"] = str(noise_method)
    st.session_state["noise_window"] = int(noise_window)
    st.session_state["savgol_poly"] = int(savgol_poly)
    st.session_state["smoothed"] = y
    st.session_state["corrected"] = corrected
    st.session_state["baseline"] = baseline
    st.session_state["preview_smoothed"] = y
    st.session_state["preview_corrected"] = corrected
    st.session_state["preview_baseline"] = baseline
    st.session_state["preview_settings"] = settings
    st.session_state.pop("baseline_page_ranges_initialized", None)
    persist_session_to_active(save_disk=True)
    st.rerun()

has_preview = st.session_state.get("preview_baseline") is not None
show_bl = st.session_state.get("preview_baseline") if has_preview else st.session_state.get("baseline")
show_corr = st.session_state.get("preview_corrected") if has_preview else st.session_state.get("corrected")
show_sm = st.session_state.get("preview_smoothed") if has_preview else st.session_state.get("smoothed")
n_pts = len(sp.intensity)

def _match(arr):
    if arr is None:
        return None
    try:
        size = len(arr)
    except TypeError:
        return None
    return arr if size == n_pts else None

show_bl, show_corr, show_sm = _match(show_bl), _match(show_corr), _match(show_sm)
if has_preview and show_bl is None:
    has_preview = False

if has_preview:
    st.caption(t("showing_preview", lang, method=st.session_state.preview_settings.method))
elif show_bl is not None:
    st.caption(t("showing_applied", lang, method=st.session_state.baseline_settings.method))
else:
    st.caption(t("no_preview_yet", lang))

auto = (
    auto_edge_windows(sp.binding_energy, settings.edge_fraction)
    if str(method).startswith("median")
    else []
)
windows = merge_windows(auto, manual)
render_spectrum_viewer(
    sp.binding_energy,
    sp.intensity,
    viewer_key="baseline_page",
    title=t("baseline_denoise_title", lang),
    lang=lang,
    baseline=show_bl,
    corrected=show_corr,
    denoised=show_sm,
    bg_windows=windows if str(method).startswith("median") else None,
)
