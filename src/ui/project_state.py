"""Bridge AnalysisProject ↔ Streamlit session_state."""

from __future__ import annotations

from typing import Optional

import numpy as np
import streamlit as st

from src.core.project import AnalysisProject, FitSnapshot
from src.core.region import crop_spectrum
from src.services import project_service


WORKING_CURVE_KEYS = (
    "corrected",
    "baseline",
    "smoothed",
    "best_fit",
    "previous_fit",
    "peaks_df",
    "metrics",
    "fit_components",
)

PREVIEW_KEYS = (
    "preview_smoothed",
    "preview_corrected",
    "preview_baseline",
    "preview_settings",
    "preview_noise_method",
    "preview_noise_window",
    "preview_savgol_poly",
)


def clear_transient_analysis_curves() -> None:
    """Drop overlay curves that must not follow a newly selected spectrum."""
    for key in WORKING_CURVE_KEYS:
        st.session_state[key] = None
    for key in PREVIEW_KEYS:
        st.session_state.pop(key, None)


def reset_plot_range_flags() -> None:
    """Let spectrum viewers re-fit axis ranges to the new active data."""
    for key in list(st.session_state.keys()):
        if str(key).endswith("_ranges_initialized"):
            st.session_state.pop(key, None)


def _array_matches(values: object, n: int) -> Optional[np.ndarray]:
    if values is None:
        return None
    arr = np.asarray(values, dtype=float)
    if arr.size != n:
        return None
    return arr


def get_project() -> Optional[AnalysisProject]:
    return st.session_state.get("project")


def set_project(project: AnalysisProject) -> None:
    st.session_state["project"] = project
    sync_active_to_session()


def sync_active_to_session() -> None:
    """Push active SpectrumEntry fields into the working session keys."""
    project = get_project()
    if project is None:
        return
    entry = project.get_active()
    if entry is None or entry.spectrum is None:
        st.session_state["full_spectrum"] = None
        st.session_state["active_spectrum"] = None
        return

    st.session_state["full_spectrum"] = entry.spectrum.copy()
    region = entry.region
    if region and len(region) == 2:
        try:
            st.session_state["active_spectrum"] = crop_spectrum(
                entry.spectrum, float(region[0]), float(region[1])
            )
            st.session_state["region"] = (float(region[0]), float(region[1]))
        except Exception:  # noqa: BLE001
            st.session_state["active_spectrum"] = entry.spectrum.copy()
            st.session_state["region"] = (
                float(entry.spectrum.binding_energy.min()),
                float(entry.spectrum.binding_energy.max()),
            )
    else:
        st.session_state["active_spectrum"] = entry.spectrum.copy()
        st.session_state["region"] = (
            float(entry.spectrum.binding_energy.min()),
            float(entry.spectrum.binding_energy.max()),
        )

    st.session_state["baseline_settings"] = entry.baseline_settings
    st.session_state["noise_method"] = entry.noise_method
    st.session_state["noise_window"] = entry.noise_window
    st.session_state["savgol_poly"] = entry.savgol_poly
    st.session_state["peak_model"] = entry.peak_model
    st.session_state["peak_configs"] = list(entry.peak_configs)
    st.session_state["fit_constraints"] = entry.fit_constraints
    st.session_state["fit_history"] = list(entry.fit_history)
    st.session_state["saved_fits"] = dict(entry.saved_fits)
    st.session_state["last_fit_id"] = entry.last_fit_id
    st.session_state["active_entry_id"] = entry.id

    clear_transient_analysis_curves()
    reset_plot_range_flags()

    last = None
    if entry.last_fit_id:
        last = next((f for f in entry.fit_history if f.id == entry.last_fit_id), None)
        if last is None:
            last = entry.saved_fits.get(entry.last_fit_id)
    if last is None:
        return

    n = int(np.asarray(st.session_state["active_spectrum"].binding_energy).size)
    st.session_state["corrected"] = _array_matches(last.corrected, n)
    st.session_state["baseline"] = _array_matches(last.baseline, n)
    st.session_state["smoothed"] = _array_matches(last.smoothed, n)
    st.session_state["best_fit"] = _array_matches(last.best_fit, n)
    st.session_state["metrics"] = last.metrics
    if last.peaks_table:
        import pandas as pd

        st.session_state["peaks_df"] = pd.DataFrame(last.peaks_table)
    if last.components:
        comps = [_array_matches(c, n) for c in last.components]
        if any(c is not None for c in comps):
            st.session_state["fit_components"] = comps


def persist_session_to_active(*, save_disk: bool = True) -> None:
    """Write current session analysis fields back into the active SpectrumEntry."""
    project = get_project()
    if project is None:
        return
    entry = project.get_active()
    if entry is None:
        return

    entry.region = list(st.session_state["region"]) if st.session_state.get("region") else None
    entry.baseline_settings = st.session_state.get("baseline_settings") or entry.baseline_settings
    entry.noise_method = st.session_state.get("noise_method", "none")
    entry.noise_window = int(st.session_state.get("noise_window", 5))
    entry.savgol_poly = int(st.session_state.get("savgol_poly", 2))
    entry.peak_model = st.session_state.get("peak_model", "pseudovoigt")
    entry.peak_configs = list(st.session_state.get("peak_configs") or [])
    entry.fit_constraints = st.session_state.get("fit_constraints") or entry.fit_constraints
    entry.fit_history = list(st.session_state.get("fit_history") or [])
    entry.saved_fits = dict(st.session_state.get("saved_fits") or {})
    entry.last_fit_id = st.session_state.get("last_fit_id")
    if save_disk:
        project_service.save_project(project)


def append_fit_snapshot(snap: FitSnapshot, *, also_save_named: Optional[str] = None) -> None:
    history = list(st.session_state.get("fit_history") or [])
    # keep grey previous = previous best_fit
    prev = st.session_state.get("best_fit")
    if prev is not None:
        st.session_state["previous_fit"] = np.asarray(prev).copy()
    history.append(snap)
    st.session_state["fit_history"] = history
    st.session_state["last_fit_id"] = snap.id
    if also_save_named:
        saved = dict(st.session_state.get("saved_fits") or {})
        snap.label = also_save_named
        saved[snap.id] = snap
        st.session_state["saved_fits"] = saved
    persist_session_to_active(save_disk=True)
