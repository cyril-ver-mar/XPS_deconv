"""Editable peak library page — add / edit / delete types + restore defaults."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.services.peak_library_service import default_library, load_library, save_library
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_peaks", lang))
st.caption(t("peak_lib_caption", lang))

lib = load_library()
defaults = default_library()
NEW = "__new__"

core_options = sorted(lib.keys()) + [NEW]
core = st.selectbox(
    t("core_level", lang),
    options=core_options,
    format_func=lambda c: t("add_option_new", lang) if c == NEW else c,
    key="peak_lib_core_sel",
)

if core == NEW:
    new_core = st.text_input(t("new_core_level", lang), value="C1s", key="peak_lib_new_core")
    if st.button(t("create_core", lang), type="primary") and new_core.strip():
        name = new_core.strip()
        if name not in lib:
            lib[name] = list(defaults.get(name, []))
            save_library(lib)
            st.session_state["peak_lib_core_sel"] = name
            st.rerun()
        else:
            st.warning(name)
    st.stop()

rows = lib.get(core, [])
df = pd.DataFrame([{"name": n, "be_ev": float(e)} for n, e in rows])
if df.empty:
    df = pd.DataFrame({"name": pd.Series(dtype=str), "be_ev": pd.Series(dtype=float)})

edited = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "name": st.column_config.TextColumn(t("peak_name", lang), required=True),
        "be_ev": st.column_config.NumberColumn(t("be_ev", lang), format="%.3f", required=True),
    },
    key=f"peak_lib_editor_{core}",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button(t("save_core", lang), type="primary", key="peak_lib_save"):
        cleaned = []
        for _, row in edited.iterrows():
            name = str(row.get("name", "")).strip()
            if not name or pd.isna(row.get("be_ev")):
                continue
            cleaned.append((name, float(row["be_ev"])))
        lib[core] = cleaned
        save_library(lib)
        st.success(t("core_saved", lang, n=len(cleaned), core=core))
with c2:
    if st.button(t("reset_core_defaults", lang), key="peak_lib_reset_core"):
        if core in defaults:
            lib[core] = list(defaults[core])
        else:
            lib[core] = []
        save_library(lib)
        st.rerun()
with c3:
    confirm_del = st.checkbox(t("confirm_delete_core", lang), key="peak_lib_confirm_del")
    if st.button(t("delete_core", lang), type="secondary", disabled=not confirm_del, key="peak_lib_del"):
        lib.pop(core, None)
        save_library(lib)
        st.session_state["peak_lib_core_sel"] = NEW if not lib else sorted(lib.keys())[0]
        st.success(t("core_deleted", lang, core=core))
        st.rerun()
with c4:
    confirm_all = st.checkbox(t("confirm_restore_lib", lang), key="peak_lib_confirm_restore")
    if st.button(
        t("reset_lib_defaults", lang),
        type="secondary",
        disabled=not confirm_all,
        key="peak_lib_restore_all",
    ):
        save_library(default_library())
        st.success(t("lib_restored", lang))
        st.rerun()

st.subheader(t("lib_levels_list", lang))
st.dataframe(
    pd.DataFrame(
        [{t("core_level", lang): k, t("n_peaks_col", lang): len(v)} for k, v in sorted(lib.items())]
    ),
    use_container_width=True,
    hide_index=True,
)
