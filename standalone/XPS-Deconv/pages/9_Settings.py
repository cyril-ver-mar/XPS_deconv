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
from src.utils.version import get_version, version_label

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_settings", lang))
st.subheader(t("settings_paths", lang))
st.write(f"{t('app_version', lang)}: **{get_version()}** (`{version_label()}`)")
st.write(f"{t('project_root', lang)}: `{PROJECT_ROOT}`")
st.write(f"{t('data_dir', lang)}: `{DATA_DIR}`")
st.write(f"{t('exports_dir', lang)}: `{EXPORTS_DIR}`")
st.write(f"{t('language_label', lang)}: **{'Русский' if lang == 'ru' else 'English'}**")
if lang == "ru":
    st.caption("Пути вычисляются относительно папки приложения (без жёстко прошитых абсолютных адресов).")
else:
    st.caption("Paths are resolved relative to the app folder (no hardcoded machine paths).")
