"""In-app documentation — how every part of XPS-Deconv works."""

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
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_docs", lang))
st.caption(t("docs_caption", lang))

guide_path = ROOT / "docs" / ("USER_GUIDE_ru.md" if lang == "ru" else "USER_GUIDE.md")
if not guide_path.exists():
    guide_path = ROOT / "docs" / "USER_GUIDE.md"

try:
    body = guide_path.read_text(encoding="utf-8")
except OSError as exc:
    st.error(f"{guide_path}: {exc}")
    st.stop()

# Split on ## headings for a table-of-contents experience
sections: list[tuple[str, str]] = []
current_title = t("docs_full", lang)
current_lines: list[str] = []
for line in body.splitlines():
    if line.startswith("## "):
        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))
        current_title = line[3:].strip()
        current_lines = [line]
    else:
        current_lines.append(line)
if current_lines:
    sections.append((current_title, "\n".join(current_lines).strip()))

titles = [s[0] for s in sections]
tab_labels = titles if len(titles) <= 8 else titles[:7] + [t("docs_more", lang)]

if len(titles) <= 8:
    tabs = st.tabs(titles)
    for tab, (_title, md) in zip(tabs, sections):
        with tab:
            st.markdown(md)
else:
    tabs = st.tabs(tab_labels)
    for i, tab in enumerate(tabs[:-1]):
        with tab:
            st.markdown(sections[i][1])
    with tabs[-1]:
        for title, md in sections[7:]:
            with st.expander(title, expanded=False):
                st.markdown(md)

st.divider()
st.markdown(t("docs_footer", lang))
