"""Compare a sequence of deconvolution runs on the active spectrum."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ui.components.plots import SAFE_PLOT_LEGEND, SAFE_PLOT_MARGIN
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("fit_sequence_title", lang))
st.caption(t("fit_sequence_caption", lang))

sp = st.session_state.get("active_spectrum") or st.session_state.get("full_spectrum")
history = list(st.session_state.get("fit_history") or [])
if sp is None:
    st.warning(t("load_spectrum_first", lang))
    st.stop()
if not history:
    st.info(t("no_fits_yet", lang))
    st.stop()

rows = []
for snap in history:
    m = snap.metrics or {}
    rows.append(
        {
            "id": snap.id,
            "label": snap.label,
            "created_at": snap.created_at,
            "model": snap.peak_model,
            "R": m.get("R"),
            "R_squared": m.get("R_squared", m.get("r_squared")),
            "RMSE": m.get("rmse"),
            "chi2": m.get("chi_square"),
            "n_peaks": len(snap.peak_configs),
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True)

ids = [s.id for s in history]
label_map = {s.id: f"{s.label} ({s.id})" for s in history}
picked = st.multiselect(
    t("show_fits_on_plot", lang),
    options=ids,
    default=ids[-min(3, len(ids)) :],
    format_func=lambda i: label_map[i],
)

fig = go.Figure()
fig.add_trace(go.Scatter(x=sp.binding_energy, y=sp.intensity, name=t("trace_spectrum", lang), line=dict(color="#1f77b4")))
colors = ["#111", "#e41a1c", "#4daf4a", "#984ea3", "#ff7f00", "#a65628"]
for i, sid in enumerate(picked):
    snap = next(s for s in history if s.id == sid)
    if snap.best_fit is None:
        continue
    fig.add_trace(
        go.Scatter(
            x=np.asarray(snap.binding_energy or sp.binding_energy),
            y=np.asarray(snap.best_fit),
            name=snap.label or sid,
            line=dict(color=colors[i % len(colors)], width=2),
        )
    )
fig.update_layout(
    template="plotly_white",
    height=560,
    title=None,
    legend=SAFE_PLOT_LEGEND,
    margin=SAFE_PLOT_MARGIN,
    xaxis_title=t("plot_default_x", lang),
    yaxis_title=t("plot_default_y", lang),
)
fig.update_xaxes(autorange="reversed")
st.markdown(f"**{t('selected_fits_overlay', lang)}**")
st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

detail_id = st.selectbox(t("peak_table_for", lang), options=ids, format_func=lambda i: label_map[i], index=len(ids) - 1)
snap = next(s for s in history if s.id == detail_id)
if snap.peaks_table:
    st.dataframe(pd.DataFrame(snap.peaks_table), use_container_width=True)
if snap.metrics:
    m = snap.metrics
    a, b, c, d = st.columns(4)
    a.metric("R", f"{m.get('R', float('nan')):.4f}")
    b.metric("R²", f"{m.get('R_squared', m.get('r_squared', float('nan'))):.4f}")
    c.metric("RMSE", f"{m.get('rmse', float('nan')):.3f}")
    d.metric("χ²_red", f"{m.get('chi_square', float('nan'))}")

if st.button(t("load_fit_workspace", lang)):
    st.session_state["peak_configs"] = list(snap.peak_configs)
    st.session_state["peak_model"] = snap.peak_model
    st.session_state["baseline_settings"] = snap.baseline_settings
    st.session_state["noise_method"] = snap.noise_method
    st.session_state["noise_window"] = snap.noise_window
    st.session_state["savgol_poly"] = snap.savgol_poly
    st.session_state["fit_constraints"] = snap.fit_constraints
    st.session_state["metrics"] = snap.metrics
    st.session_state["corrected"] = None if snap.corrected is None else np.asarray(snap.corrected)
    st.session_state["baseline"] = None if snap.baseline is None else np.asarray(snap.baseline)
    st.session_state["smoothed"] = None if snap.smoothed is None else np.asarray(snap.smoothed)
    st.session_state["best_fit"] = None if snap.best_fit is None else np.asarray(snap.best_fit)
    st.session_state["fit_components"] = (
        None if not snap.components else [np.asarray(c) for c in snap.components]
    )
    if snap.peaks_table:
        st.session_state["peaks_df"] = pd.DataFrame(snap.peaks_table)
    st.session_state["last_fit_id"] = snap.id
    st.success(t("loaded_into_session", lang))
