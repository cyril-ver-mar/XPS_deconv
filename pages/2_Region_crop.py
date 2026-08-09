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
from src.ui.components.plots import spectrum_figure
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(page_title="Region — XPS-Deconv", layout="wide")
ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_region", lang))
full = st.session_state.get("full_spectrum")
if full is None:
    st.warning(t("need_spectrum", lang))
    st.stop()

data_min = float(full.binding_energy.min())
data_max = float(full.binding_energy.max())
cur = st.session_state.get("region") or (data_min, data_max)

# Pending-key pattern for widgets
if st.session_state.get("pending_region_min") is not None:
    st.session_state["region_min"] = st.session_state.pop("pending_region_min")
if st.session_state.get("pending_region_max") is not None:
    st.session_state["region_max"] = st.session_state.pop("pending_region_max")
if "region_min" not in st.session_state:
    st.session_state["region_min"] = float(cur[0])
if "region_max" not in st.session_state:
    st.session_state["region_max"] = float(cur[1])

st.markdown(
    "Set the active binding-energy window. One region at a time."
    if lang == "en"
    else "Задайте активное окно по энергии связи. Одна область за раз."
)

preset = st.selectbox("Preset", ["—"] + list(REGION_PRESETS.keys()))
if preset != "—" and st.button("Apply preset"):
    lo, hi = REGION_PRESETS[preset]
    lo, hi = clamp_window(lo, hi, data_min, data_max)
    st.session_state["pending_region_min"] = lo
    st.session_state["pending_region_max"] = hi
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.slider("BE min (eV)", data_min, data_max, key="region_min")
with c2:
    st.slider("BE max (eV)", data_min, data_max, key="region_max")

n1, n2 = st.columns(2)
with n1:
    num_min = st.number_input("Numeric BE min", value=float(st.session_state["region_min"]), format="%.3f")
with n2:
    num_max = st.number_input("Numeric BE max", value=float(st.session_state["region_max"]), format="%.3f")
if st.button("Apply numeric range"):
    lo, hi = clamp_window(float(num_min), float(num_max), data_min, data_max)
    st.session_state["pending_region_min"] = lo
    st.session_state["pending_region_max"] = hi
    st.rerun()

be_min = float(min(st.session_state["region_min"], st.session_state["region_max"]))
be_max = float(max(st.session_state["region_min"], st.session_state["region_max"]))

fig = spectrum_figure(
    full.binding_energy,
    full.intensity,
    title="Select region (brush: use box select on x-axis)",
    region=(be_min, be_max),
)
fig.update_layout(dragmode="zoom")
event = st.plotly_chart(fig, use_container_width=True, key="region_plot", on_select="rerun", selection_mode="box")

# Brush via plotly selection (Streamlit ≥1.35 style)
try:
    sel = event.selection if hasattr(event, "selection") else None
    if sel and getattr(sel, "box", None):
        boxes = sel.box
        if boxes:
            xs = boxes[0].get("x") if isinstance(boxes[0], dict) else getattr(boxes[0], "x", None)
            if xs and len(xs) >= 2:
                lo, hi = clamp_window(float(min(xs)), float(max(xs)), data_min, data_max)
                st.session_state["pending_region_min"] = lo
                st.session_state["pending_region_max"] = hi
                st.rerun()
except Exception:
    pass

st.caption(
    "Tip: zoom/box-select on the plot when supported; otherwise use sliders or numeric fields."
    if lang == "en"
    else "Подсказка: box-select на графике (если поддерживается) или слайдеры / числа."
)

if st.button("Apply region (set active spectrum)", type="primary"):
    try:
        active = crop_spectrum(full, be_min, be_max)
        st.session_state["active_spectrum"] = active
        st.session_state["region"] = (be_min, be_max)
        st.session_state["corrected"] = None
        st.session_state["baseline"] = None
        st.session_state["best_fit"] = None
        st.success(f"Active region {be_min:.2f}–{be_max:.2f} eV ({len(active.binding_energy)} pts)")
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)

active = st.session_state.get("active_spectrum")
if active is not None and st.session_state.get("region"):
    st.plotly_chart(
        spectrum_figure(active.binding_energy, active.intensity, title="Active region"),
        use_container_width=True,
    )
