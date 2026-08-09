"""Session-state keys used across pages."""

from __future__ import annotations

from typing import Any, Dict

from src.core.models import BaselineSettings, FitConstraints
from src.utils.cancel import CancelToken

DEFAULTS: Dict[str, Any] = {
    "lang": "en",
    "full_spectrum": None,
    "active_spectrum": None,
    "vgd_labels": [],
    "vgd_path": None,
    "spectrum_index": 0,
    "region": None,  # (be_min, be_max)
    "baseline_settings": BaselineSettings(),
    "noise_method": "none",
    "noise_window": 5,
    "peak_model": "pseudovoigt",
    "peak_configs": [],
    "fit_constraints": FitConstraints(),
    "corrected": None,
    "baseline": None,
    "smoothed": None,
    "best_fit": None,
    "peaks_df": None,
    "metrics": None,
    "fit_components": None,
    "cancel_token": CancelToken(),
    "pending_region_min": None,
    "pending_region_max": None,
}


def init_session_state() -> None:
    import streamlit as st

    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            # Fresh instances for mutable defaults
            if key == "baseline_settings":
                st.session_state[key] = BaselineSettings()
            elif key == "fit_constraints":
                st.session_state[key] = FitConstraints()
            elif key == "cancel_token":
                st.session_state[key] = CancelToken()
            elif key == "peak_configs":
                st.session_state[key] = []
            else:
                st.session_state[key] = value
