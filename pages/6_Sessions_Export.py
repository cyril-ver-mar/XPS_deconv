"""Sessions and export page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import streamlit as st

from src.db.sessions_repo import delete_session, list_sessions
from src.services.session_service import export_excel, export_peaks_csv, load_session, save_session
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import EXPORTS_DIR, ensure_runtime_dirs

st.set_page_config(page_title="Sessions — XPS-Deconv", layout="wide")
ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_sessions", lang))

st.subheader("Save session")
name = st.text_input("Session name", value="fit_session")
notes = st.text_input("Notes", value="")
if st.button("Save current session", type="primary"):
    path = save_session(name, dict(st.session_state), notes=notes)
    st.success(f"Saved {path}")

st.subheader("Load session")
rows = list_sessions()
if not rows:
    st.caption("No indexed sessions yet.")
else:
    labels = {r["id"]: f"{r['name']} | {r['core_level']} | {r['created_at']}" for r in rows}
    sid = st.selectbox("Indexed sessions", options=list(labels.keys()), format_func=lambda i: labels[i])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Load selected"):
            row = next(r for r in rows if r["id"] == sid)
            loaded = load_session(row["json_path"])
            for key in (
                "full_spectrum",
                "active_spectrum",
                "region",
                "baseline_settings",
                "noise_method",
                "noise_window",
                "peak_model",
                "peak_configs",
                "fit_constraints",
                "metrics",
                "peaks_df",
                "corrected",
                "baseline",
                "best_fit",
            ):
                if key in loaded:
                    st.session_state[key] = loaded[key]
            st.success("Session loaded into memory")
            st.rerun()
    with c2:
        if st.button("Delete selected"):
            delete_session(int(sid))
            st.warning("Deleted")
            st.rerun()

manual = st.text_input("Or load JSON path")
if st.button("Load JSON path") and manual.strip():
    loaded = load_session(manual.strip())
    for key, val in loaded.items():
        if key != "raw":
            st.session_state[key] = val
    st.success("Loaded")
    st.rerun()

st.subheader("Export")
base = st.text_input("Export basename", value="xps_export")
e1, e2, e3 = st.columns(3)
with e1:
    if st.button("Excel (.xlsx)"):
        path = export_excel(dict(st.session_state), base)
        st.success(str(path))
with e2:
    if st.button("Peaks CSV") and st.session_state.get("peaks_df") is not None:
        path = export_peaks_csv(st.session_state["peaks_df"], base + "_peaks")
        st.success(str(path))
with e3:
    if st.button("PNG figure"):
        sp = st.session_state.get("active_spectrum") or st.session_state.get("full_spectrum")
        if sp is None:
            st.error("No spectrum")
        else:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(sp.binding_energy, sp.intensity, label="Spectrum")
            if st.session_state.get("baseline") is not None:
                ax.plot(sp.binding_energy, st.session_state["baseline"], "--", label="Baseline")
            if st.session_state.get("corrected") is not None:
                ax.plot(sp.binding_energy, st.session_state["corrected"], label="Corrected")
            if st.session_state.get("best_fit") is not None:
                ax.plot(sp.binding_energy, st.session_state["best_fit"], label="Fit")
            ax.invert_xaxis()
            ax.set_xlabel("Binding energy (eV)")
            ax.set_ylabel("Intensity")
            ax.legend()
            ax.grid(True, alpha=0.3)
            out = EXPORTS_DIR / f"{base}.png"
            fig.tight_layout()
            fig.savefig(out, dpi=200)
            plt.close(fig)
            st.success(str(out))
            st.image(str(out))
