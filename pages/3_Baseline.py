"""Baseline correction page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.core.baseline import auto_edge_windows, compute_baseline, merge_windows
from src.core.models import BASELINE_METHODS, BaselineSettings
from src.core.noise import remove_noise
from src.ui.components.plots import spectrum_figure
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(page_title="Baseline — XPS-Deconv", layout="wide")
ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_baseline", lang))
sp = st.session_state.get("active_spectrum") or st.session_state.get("full_spectrum")
if sp is None:
    st.warning(t("need_spectrum", lang))
    st.stop()

st.info(t("baseline_help_median", lang))
st.caption(t("shirley_help", lang))
st.caption(t("tougaard_help", lang))

method = st.selectbox(
    "Baseline method",
    options=list(BASELINE_METHODS),
    index=list(BASELINE_METHODS).index(
        st.session_state.baseline_settings.method
        if st.session_state.baseline_settings.method in BASELINE_METHODS
        else "median_linear"
    ),
)

c1, c2, c3 = st.columns(3)
with c1:
    edge_fraction = st.slider("Auto edge fraction", 0.02, 0.25, float(st.session_state.baseline_settings.edge_fraction))
with c2:
    poly_degree = st.number_input("Poly degree", 1, 5, int(st.session_state.baseline_settings.poly_degree))
with c3:
    rolling_window = st.number_input("Rolling / SNIP window", 5, 101, int(st.session_state.baseline_settings.rolling_window), step=2)

if method == "tougaard":
    bcol, ccol = st.columns(2)
    with bcol:
        tougaard_B = st.number_input("Tougaard B", value=float(st.session_state.baseline_settings.tougaard_B))
    with ccol:
        tougaard_C = st.number_input("Tougaard C", value=float(st.session_state.baseline_settings.tougaard_C))
else:
    tougaard_B = st.session_state.baseline_settings.tougaard_B
    tougaard_C = st.session_state.baseline_settings.tougaard_C

st.subheader("Manual background windows (optional)")
st.caption("Add BE intervals that contain only noise/background — used for median methods.")
n_win = st.number_input("Number of manual windows", 0, 6, len(st.session_state.baseline_settings.manual_windows))
manual = []
be_lo, be_hi = float(sp.binding_energy.min()), float(sp.binding_energy.max())
existing = list(st.session_state.baseline_settings.manual_windows)
for i in range(int(n_win)):
    default = existing[i] if i < len(existing) else (be_lo, be_lo + (be_hi - be_lo) * 0.05)
    cols = st.columns(2)
    with cols[0]:
        w0 = st.number_input(f"Window {i+1} min", value=float(default[0]), key=f"bwmin{i}")
    with cols[1]:
        w1 = st.number_input(f"Window {i+1} max", value=float(default[1]), key=f"bwmax{i}")
    manual.append((min(w0, w1), max(w0, w1)))

noise_method = st.selectbox(
    "Pre-smoothing (optional, separate from baseline)",
    ["none", "median", "moving_average", "savgol"],
    index=["none", "median", "moving_average", "savgol"].index(st.session_state.get("noise_method", "none")),
)
noise_window = st.slider("Smoothing window", 3, 21, int(st.session_state.get("noise_window", 5)), step=2)

settings = BaselineSettings(
    method=method,
    edge_fraction=float(edge_fraction),
    manual_windows=manual,
    poly_degree=int(poly_degree),
    rolling_window=int(rolling_window),
    tougaard_B=float(tougaard_B),
    tougaard_C=float(tougaard_C),
    shirley_max_iter=int(st.session_state.baseline_settings.shirley_max_iter),
)

if st.button("Preview / apply baseline", type="primary"):
    y = remove_noise(sp.intensity, method=noise_method, window_size=int(noise_window))
    corrected, baseline = compute_baseline(sp.binding_energy, y, settings)
    st.session_state["baseline_settings"] = settings
    st.session_state["noise_method"] = noise_method
    st.session_state["noise_window"] = int(noise_window)
    st.session_state["corrected"] = corrected
    st.session_state["baseline"] = baseline
    st.session_state["smoothed"] = y
    st.success("Baseline applied to session state")

auto = auto_edge_windows(sp.binding_energy, settings.edge_fraction) if method.startswith("median") else []
windows = merge_windows(auto, manual)
bl = st.session_state.get("baseline")
corr = st.session_state.get("corrected")
st.plotly_chart(
    spectrum_figure(
        sp.binding_energy,
        sp.intensity,
        title="Baseline preview",
        baseline=bl,
        corrected=corr,
        bg_windows=windows if method.startswith("median") else None,
    ),
    use_container_width=True,
)
