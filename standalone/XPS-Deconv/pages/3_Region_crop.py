"""Region crop page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.core.models import REGION_PRESETS
from src.core.region import clamp_window, crop_spectrum
from src.ui.components.help import labeled_help
from src.ui.components.sidebar import render_sidebar
from src.ui.components.spectrum_viewer import render_spectrum_viewer
from src.ui.project_state import clear_transient_analysis_curves, persist_session_to_active, reset_plot_range_flags
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_region", lang))
labeled_help(t("nav_region", lang), "region_crop", lang)

full = st.session_state.get("full_spectrum")
if full is None:
    st.warning(t("need_spectrum", lang) + t("need_spectrum_import_hint", lang))
    st.stop()

data_min = float(full.binding_energy.min())
data_max = float(full.binding_energy.max())
cur = st.session_state.get("region") or (data_min, data_max)

if st.session_state.get("pending_region_min") is not None:
    st.session_state["region_min"] = st.session_state.pop("pending_region_min")
if st.session_state.get("pending_region_max") is not None:
    st.session_state["region_max"] = st.session_state.pop("pending_region_max")
if "region_min" not in st.session_state:
    st.session_state["region_min"] = float(cur[0])
if "region_max" not in st.session_state:
    st.session_state["region_max"] = float(cur[1])

labeled_help(t("presets", lang), "region_preset", lang)
preset = st.selectbox(t("preset", lang), ["—"] + list(REGION_PRESETS.keys()))
if preset != "—" and st.button(t("apply_preset", lang)):
    lo, hi = REGION_PRESETS[preset]
    lo, hi = clamp_window(lo, hi, data_min, data_max)
    st.session_state["pending_region_min"] = lo
    st.session_state["pending_region_max"] = hi
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.slider(t("be_min", lang), data_min, data_max, key="region_min", help=t("be_min_help", lang))
with c2:
    st.slider(t("be_max", lang), data_min, data_max, key="region_max", help=t("be_max_help", lang))

n1, n2 = st.columns(2)
with n1:
    num_min = st.number_input(t("numeric_be_min", lang), value=float(st.session_state["region_min"]), format="%.3f")
with n2:
    num_max = st.number_input(t("numeric_be_max", lang), value=float(st.session_state["region_max"]), format="%.3f")
if st.button(t("apply_numeric_range", lang)):
    lo, hi = clamp_window(float(num_min), float(num_max), data_min, data_max)
    st.session_state["pending_region_min"] = lo
    st.session_state["pending_region_max"] = hi
    st.rerun()

be_min = float(min(st.session_state["region_min"], st.session_state["region_max"]))
be_max = float(max(st.session_state["region_min"], st.session_state["region_max"]))

render_spectrum_viewer(
    full.binding_energy,
    full.intensity,
    viewer_key="region_full",
    title=t("full_spectrum_roi", lang),
    lang=lang,
    region=(be_min, be_max),
    show_trace_toggles=False,
)

if st.button(t("apply_region", lang), type="primary"):
    try:
        active = crop_spectrum(full, be_min, be_max)
        st.session_state["active_spectrum"] = active
        st.session_state["region"] = (be_min, be_max)
        clear_transient_analysis_curves()
        reset_plot_range_flags()
        persist_session_to_active(save_disk=True)
        st.success(
            t("region_applied", lang, lo=be_min, hi=be_max, n=len(active.binding_energy))
        )
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)

active = st.session_state.get("active_spectrum")
if active is not None:
    render_spectrum_viewer(
        active.binding_energy,
        active.intensity,
        viewer_key="region_active",
        title=t("active_region_title", lang),
        lang=lang,
        show_trace_toggles=False,
    )
