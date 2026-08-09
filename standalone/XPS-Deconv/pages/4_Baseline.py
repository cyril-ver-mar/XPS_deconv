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
from src.core.noise import DENOISE_HELP, DENOISE_METHODS, remove_noise
from src.ui.components.baseline_demos import BASELINE_METHOD_BLURBS, baseline_demo_figure
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

with st.expander("Graphical examples of baseline methods (demo spectrum)", expanded=False):
    st.plotly_chart(baseline_demo_figure(), use_container_width=True)

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

st.subheader("Denoise")
labeled_help("Denoise method", "denoise_method", lang)
noise_method = st.selectbox(
    "Denoise method",
    list(DENOISE_METHODS),
    key="bl_noise_method",
    format_func=lambda m: f"{m} — {DENOISE_HELP.get(m, '')[:60]}",
)
d1, d2 = st.columns(2)
with d1:
    labeled_help("Window", "denoise_window", lang)
    noise_window = st.slider("Window size", 3, 51, step=2, key="bl_noise_window")
with d2:
    labeled_help("Savitzky–Golay poly", "denoise_savgol_poly", lang)
    savgol_poly = st.number_input("Savgol poly order", 1, 5, key="bl_savgol_poly")

labeled_help("Baseline method", "baseline_method", lang)
method = st.selectbox(
    "Baseline method",
    options=list(BASELINE_METHODS),
    key="bl_method",
    format_func=lambda m: f"{m} — {BASELINE_METHOD_BLURBS.get(m, '')[:70]}",
)
st.caption(BASELINE_METHOD_BLURBS.get(method, ""))
if method == "shirley":
    help_mark("shirley", lang)
if method == "tougaard":
    help_mark("tougaard", lang)

c1, c2, c3 = st.columns(3)
with c1:
    labeled_help("Auto edge fraction", "edge_fraction", lang)
    edge_fraction = st.slider("Auto edge fraction", 0.02, 0.25, key="bl_edge")
with c2:
    labeled_help("Poly degree", "poly_degree", lang)
    poly_degree = st.number_input("Poly degree", 1, 5, key="bl_poly")
with c3:
    labeled_help("Rolling window", "rolling_window", lang)
    rolling_window = st.number_input("Rolling window", 5, 101, step=2, key="bl_roll")

if method == "tougaard":
    bcol, ccol = st.columns(2)
    with bcol:
        tougaard_B = st.number_input("Tougaard B", key="bl_tB")
    with ccol:
        tougaard_C = st.number_input("Tougaard C", key="bl_tC")
else:
    tougaard_B = float(st.session_state["bl_tB"])
    tougaard_C = float(st.session_state["bl_tC"])

labeled_help("Manual background windows", "manual_bg", lang)
n_win = st.number_input("Number of manual windows", 0, 6, key="bl_nwin")
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
        w0 = st.number_input(f"Window {i+1} min", key=f"bwmin{i}")
    with cols[1]:
        w1 = st.number_input(f"Window {i+1} max", key=f"bwmax{i}")
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
    do_preview = st.button("Preview", type="secondary")
with b2:
    do_apply = st.button("Apply to session", type="primary")
with b3:
    clear_preview = st.button("Clear preview")

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

if has_preview:
    st.caption(f"Showing **preview** (`{st.session_state.preview_settings.method}`) — not locked until Apply")
elif st.session_state.get("baseline") is not None:
    st.caption(f"Showing **applied** (`{st.session_state.baseline_settings.method}`)")
else:
    st.caption("No preview/applied baseline yet — click **Preview**")

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
    title="Baseline / denoise",
    lang=lang,
    baseline=show_bl,
    corrected=show_corr,
    denoised=show_sm,
    bg_windows=windows if str(method).startswith("median") else None,
)
