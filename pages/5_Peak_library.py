"""Editable peak library page."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.services.peak_library_service import default_library, load_library, save_library
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(page_title="Peak library — XPS-Deconv", layout="wide")
ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_peaks", lang))
lib = load_library()

core = st.selectbox("Core level", sorted(lib.keys()) + ["__new__"])
if core == "__new__":
    new_core = st.text_input("New core level name", value="C1s")
    if st.button("Create core level") and new_core.strip():
        lib[new_core.strip()] = []
        save_library(lib)
        st.rerun()
    st.stop()

rows = lib.get(core, [])
text = st.text_area(
    "Peaks as JSON list of [name, eV]",
    value=json.dumps([[n, e] for n, e in rows], indent=2, ensure_ascii=False),
    height=360,
)
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("Save core level", type="primary"):
        try:
            parsed = json.loads(text)
            lib[core] = [(str(a), float(b)) for a, b in parsed]
            save_library(lib)
            st.success("Saved")
        except Exception as exc:  # noqa: BLE001
            st.exception(exc)
with c2:
    if st.button("Reset this core to defaults"):
        defaults = default_library()
        if core in defaults:
            lib[core] = defaults[core]
            save_library(lib)
            st.rerun()
with c3:
    if st.button("Reset entire library to defaults"):
        save_library(default_library())
        st.rerun()
