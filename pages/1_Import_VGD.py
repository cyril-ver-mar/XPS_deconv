"""Import VGD page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.services.import_service import list_spectrum_labels, load_spectrum
from src.ui.components.plots import spectrum_figure
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(page_title="Import VGD — XPS-Deconv", layout="wide")
ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_import", lang))
st.caption(
    "Thermo Scientific VGD only. Choose one spectrum per session."
    if lang == "en"
    else "Только Thermo Scientific VGD. Один спектр на сессию."
)

uploaded = st.file_uploader("VGD file", type=["vgd", "VGD"])
path_text = st.text_input(
    "Or local path",
    value=st.session_state.get("vgd_path") or "",
)

col1, col2 = st.columns(2)
with col1:
    load_btn = st.button("Load", type="primary")

if load_btn:
    try:
        if uploaded is not None:
            tmp = Path("data") / "_upload_tmp.vgd"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_bytes(uploaded.getvalue())
            path = tmp
        elif path_text.strip():
            path = Path(path_text.strip())
        else:
            st.error("Provide a file or path")
            st.stop()
        vgd, _ = load_spectrum(path, 0)
        labels = list_spectrum_labels(vgd)
        st.session_state["vgd_path"] = str(path)
        st.session_state["vgd_labels"] = labels
        st.session_state["_vgd_cache_path"] = str(path)
        st.success(f"Loaded {path.name}: {len(labels)} spectrum(s)")
    except Exception as exc:  # noqa: BLE001
        st.exception(exc)

labels = st.session_state.get("vgd_labels") or []
if labels and st.session_state.get("vgd_path"):
    idx = st.selectbox(
        "Spectrum",
        options=list(range(len(labels))),
        format_func=lambda i: labels[i],
        index=min(st.session_state.get("spectrum_index", 0), len(labels) - 1),
    )
    if st.button("Use selected spectrum"):
        try:
            _, spectrum = load_spectrum(st.session_state["vgd_path"], idx)
            st.session_state["full_spectrum"] = spectrum
            st.session_state["active_spectrum"] = spectrum.copy()
            st.session_state["spectrum_index"] = idx
            st.session_state["region"] = (
                float(spectrum.binding_energy.min()),
                float(spectrum.binding_energy.max()),
            )
            st.session_state["corrected"] = None
            st.session_state["baseline"] = None
            st.session_state["best_fit"] = None
            st.session_state["peaks_df"] = None
            st.session_state["metrics"] = None
            st.success(f"Active: {spectrum.core_level} ({len(spectrum.binding_energy)} points)")
        except Exception as exc:  # noqa: BLE001
            st.exception(exc)

sp = st.session_state.get("full_spectrum")
if sp is not None:
    st.plotly_chart(
        spectrum_figure(sp.binding_energy, sp.intensity, title=f"{sp.core_level}"),
        use_container_width=True,
    )
else:
    st.info(t("need_spectrum", lang))
