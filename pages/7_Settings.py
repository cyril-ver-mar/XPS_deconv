"""Settings page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import DATA_DIR, EXPORTS_DIR, ROOT as PROJECT_ROOT, ensure_runtime_dirs

st.set_page_config(page_title="Settings — XPS-Deconv", layout="wide")
ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_settings", lang))
st.write(f"Project root: `{PROJECT_ROOT}`")
st.write(f"Data dir: `{DATA_DIR}`")
st.write(f"Exports dir: `{EXPORTS_DIR}`")
st.write(f"Language: **{lang}**")
st.markdown(
    "See [docs/DECISIONS.md](../docs/DECISIONS.md) and [docs/AI-deployment/](../docs/AI-deployment/) for architecture."
)
