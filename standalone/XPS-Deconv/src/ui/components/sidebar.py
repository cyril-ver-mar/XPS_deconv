"""Shared Streamlit sidebar chrome (Layer 5)."""

from __future__ import annotations

import os
import signal

import streamlit as st

from src.utils.i18n import DEFAULT_LANG, t
from src.utils.version import get_version


def render_sidebar() -> str:
    lang = st.session_state.get("lang", DEFAULT_LANG)
    st.sidebar.title(t("app_title", lang))
    st.sidebar.caption(f"v{get_version()}")
    # Keep radio index in sync with session lang (Russian default)
    choice = st.sidebar.radio(
        t("lang", lang),
        options=["ru", "en"],
        format_func=lambda x: "Русский" if x == "ru" else "English",
        index=0 if lang == "ru" else 1,
        key="lang_radio",
    )
    st.session_state["lang"] = choice

    if st.sidebar.button(t("cancel", choice)):
        token = st.session_state.get("cancel_token")
        if token is not None:
            token.cancel()
            st.sidebar.warning(t("cancel_requested", choice))

    if st.sidebar.button(t("exit_app", choice)):
        st.sidebar.write(t("stopping", choice))
        os.kill(os.getpid(), signal.SIGTERM)

    return choice
