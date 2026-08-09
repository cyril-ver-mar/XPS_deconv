"""Shared Streamlit sidebar chrome (Layer 5)."""

from __future__ import annotations

import os
import signal

import streamlit as st

from src.utils.i18n import t


def render_sidebar() -> str:
    lang = st.session_state.get("lang", "en")
    st.sidebar.title(t("app_title", lang))
    choice = st.sidebar.radio(
        t("lang", lang),
        options=["en", "ru"],
        format_func=lambda x: "English" if x == "en" else "Русский",
        index=0 if lang == "en" else 1,
        key="lang_radio",
    )
    st.session_state["lang"] = choice

    if st.sidebar.button(t("cancel", choice)):
        token = st.session_state.get("cancel_token")
        if token is not None:
            token.cancel()
            st.sidebar.warning("Cancel requested")

    if st.sidebar.button(t("exit_app", choice)):
        st.sidebar.write("Stopping…")
        os.kill(os.getpid(), signal.SIGTERM)

    return choice
