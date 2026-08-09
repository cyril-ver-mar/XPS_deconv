"""XPS-Deconv — Streamlit entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(
    page_title="XPS-Deconv",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.title(t("app_title", lang))
st.markdown(
    """
**XPS-Deconv** — professional Thermo Scientific **VGD** XPS deconvolution.

### Workflow
1. **Import VGD** — load file, pick one spectrum  
2. **Region crop** — sliders, presets, numeric range, brush on plot  
3. **Baseline** — median noise-floor (recommended) or Shirley / Tougaard / smooth  
4. **Deconvolution** — choose peak model, constraints, fit  
5. **Sessions / Export** — save/reload full fit session; Excel / CSV / PNG  

Use the sidebar language switch for **English / Русский**.  
Algorithm help is shown on each analysis page.
"""
    if lang == "en"
    else """
**XPS-Deconv** — профессиональная деконволюция XPS из файлов **VGD** (Thermo Scientific).

### Порядок работы
1. **Импорт VGD** — загрузка, выбор одного спектра  
2. **Обрезка области** — слайдеры, пресеты, числа, кисть на графике  
3. **Базовая линия** — медиана шума (рекомендуется) или Shirley / Tougaard / сглаживание  
4. **Деконволюция** — модель пика, ограничения, фит  
5. **Сессии / Экспорт** — сохранение сессии; Excel / CSV / PNG  

Язык переключается в боковой панели.
"""
)

st.info(
    "Open pages from the left sidebar (Streamlit multipage navigation)."
    if lang == "en"
    else "Страницы открываются в левой панели навигации Streamlit."
)
