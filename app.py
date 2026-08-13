"""XPS-Deconv — Streamlit entrypoint with ordered, translated navigation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.deps_check import guard_app_startup

guard_app_startup()

import streamlit as st

from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.i18n import DEFAULT_LANG, t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(
    page_title="XPS-Deconv",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_runtime_dirs()
init_session_state()


def _home() -> None:
    lang = render_sidebar()
    st.title(t("app_title", lang))
    if lang == "en":
        st.markdown(
            """
**XPS-Deconv** — Thermo Scientific **VGD** XPS deconvolution with reloadable **projects**.

### Workflow
1. **Import** — create/load a project, upload VGDs, pick one spectrum  
2. **Interactive** — all-in-one live tuning  
3. **Region / Baseline / Deconvolution** — step-by-step pages  
4. **Fit sequence** — compare fits  
5. **Peak library** — edit / add / delete peak types; restore defaults  
6. **Sessions / Export** — Excel / CSV / PNG  
7. **Documentation** — how every part works  
8. **Settings**

Helpers: **❔** next to parameters. Language: sidebar.
"""
        )
    else:
        st.markdown(
            """
**XPS-Deconv** — деконволюция XPS из **VGD** с перезагружаемыми **проектами**.

### Порядок работы
1. **Импорт** — проект, загрузка VGD, выбор спектра  
2. **Интерактив** — всё в одном окне  
3. **Обрезка / Базовая линия / Деконволюция** — пошаговые страницы  
4. **Последовательность фитов** — сравнение  
5. **Библиотека пиков** — правка / добавление / удаление типов; восстановление по умолчанию  
6. **Сессии / Экспорт** — Excel / CSV / PNG  
7. **Документация** — как устроена каждая часть  
8. **Настройки**

Подсказки: **❔** у параметров. Язык — в боковой панели.
"""
        )


lang = st.session_state.get("lang", DEFAULT_LANG)

main = [
    st.Page(_home, title=t("nav_home", lang), icon="🏠", default=True),
    st.Page("pages/1_Import_VGD.py", title=t("nav_import", lang), icon="📁"),
    st.Page("pages/2_Interactive_workspace.py", title=t("nav_interactive", lang), icon="🎛️"),
]
analysis = [
    st.Page("pages/3_Region_crop.py", title=t("nav_region", lang), icon="✂️"),
    st.Page("pages/4_Baseline.py", title=t("nav_baseline", lang), icon="📉"),
    st.Page("pages/5_Deconvolution.py", title=t("nav_fit", lang), icon="🔬"),
    st.Page("pages/6_Fit_sequence.py", title=t("nav_sequence", lang), icon="📊"),
    st.Page("pages/7_Peak_library.py", title=t("nav_peaks", lang), icon="📚"),
    st.Page("pages/8_Sessions_Export.py", title=t("nav_sessions", lang), icon="💾"),
]
settings = [
    st.Page("pages/10_Documentation.py", title=t("nav_docs", lang), icon="📖"),
    st.Page("pages/9_Settings.py", title=t("nav_settings", lang), icon="⚙️"),
]

nav = st.navigation(
    {
        t("nav_group_main", lang): main,
        t("nav_group_analysis", lang): analysis,
        t("nav_group_settings", lang): settings,
    }
)
nav.run()
