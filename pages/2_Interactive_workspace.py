"""Interactive all-in-one deconvolution workspace."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import streamlit as st

from src.core.models import BASELINE_METHODS, PEAK_MODELS, BaselineSettings, FitConstraints, PeakConfig
from src.core.noise import DENOISE_METHODS
from src.services.analysis_service import run_fit, snapshot_from_fit_result
from src.ui.components.help import labeled_help
from src.ui.components.sidebar import render_sidebar
from src.ui.components.spectrum_viewer import render_spectrum_viewer
from src.ui.components.uncertainty_plot import render_mean_uncertainty_panel
from src.ui.project_state import append_fit_snapshot, persist_session_to_active
from src.ui.session_keys import init_session_state
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("interactive_title", lang))
st.caption(t("interactive_caption", lang))

sp = st.session_state.get("active_spectrum") or st.session_state.get("full_spectrum")
if sp is None:
    st.warning(t("select_spectrum_import", lang))
    st.stop()

left, right = st.columns([1.05, 1.35])

with left:
    with st.expander(t("denoise", lang), expanded=False):
        labeled_help("Denoise", "denoise_method", lang)
        noise_method = st.selectbox("Method", list(DENOISE_METHODS), key="ws_noise_method")
        noise_window = st.slider(
            "Window", 3, 51, int(st.session_state.get("noise_window", 5)), step=2, key="ws_nw"
        )
        savgol_poly = st.number_input(
            "Savgol poly", 1, 5, int(st.session_state.get("savgol_poly", 2)), key="ws_sg"
        )

    with st.expander(t("baseline", lang), expanded=False):
        labeled_help("Baseline", "baseline_method", lang)
        method = st.selectbox(
            "Baseline method",
            list(BASELINE_METHODS),
            index=list(BASELINE_METHODS).index(
                st.session_state.baseline_settings.method
                if st.session_state.baseline_settings.method in BASELINE_METHODS
                else "median_linear"
            ),
            key="ws_bl_method",
        )
        edge_fraction = st.slider(
            "Edge fraction",
            0.02,
            0.25,
            float(st.session_state.baseline_settings.edge_fraction),
            key="ws_ef",
        )
        settings = BaselineSettings(
            method=method,
            edge_fraction=float(edge_fraction),
            manual_windows=list(st.session_state.baseline_settings.manual_windows),
            poly_degree=int(st.session_state.baseline_settings.poly_degree),
            rolling_window=int(st.session_state.baseline_settings.rolling_window),
            tougaard_B=float(st.session_state.baseline_settings.tougaard_B),
            tougaard_C=float(st.session_state.baseline_settings.tougaard_C),
        )

    with st.expander(t("constraints", lang), expanded=False):
        peak_model = st.selectbox(t("peak_model", lang), list(PEAK_MODELS), key="ws_pm")
        fix_fwhm = st.toggle(
            "Fix FWHM", value=st.session_state.fit_constraints.enable_fix_fwhm, key="ws_ff"
        )
        shared_sigma = st.toggle(
            "Shared sigma", value=st.session_state.fit_constraints.shared_sigma, key="ws_ss"
        )
        doublet = st.toggle(
            "Doublet links",
            value=st.session_state.fit_constraints.enable_doublet_links,
            key="ws_db",
        )

    with st.expander(t("peaks", lang), expanded=False):
        configs = list(st.session_state.get("peak_configs") or [])

        from src.services.peak_library_service import load_library

        lib = load_library()
        core_options = ["—"] + list(lib.keys())
        default_core = sp.core_level if sp.core_level in lib else "—"
        ws_core = st.selectbox(
            "Library core level",
            core_options,
            index=core_options.index(default_core) if default_core in core_options else 0,
            key="ws_lib_core",
        )
        suggestions = lib.get(ws_core, []) if ws_core != "—" else []
        if suggestions:
            pick = st.multiselect(
                "Add from library",
                options=[f"{n} @ {e:.2f}" for n, e in suggestions],
                key="ws_lib_pick",
            )
            if st.button(t("add_lib_peaks", lang), key="ws_add_lib") and pick:
                for item in pick:
                    name, rest = item.split(" @ ")
                    center = float(rest)
                    if any(
                        p.name.strip() == name.strip() and abs(p.center - center) < 1e-6
                        for p in configs
                    ):
                        continue
                    configs.append(
                        PeakConfig(
                            name=name.strip(), center=center, tolerance=0.0, fix_center=True
                        )
                    )
                st.session_state["peak_configs"] = configs
                st.session_state["ws_lib_pick"] = []
                st.rerun()

        if st.button(t("add_blank_peak", lang), key="ws_add"):
            configs.append(
                PeakConfig(
                    name=f"Peak{len(configs)+1}",
                    center=float(sp.binding_energy.mean()),
                    tolerance=0.0,
                    fix_center=True,
                )
            )
            st.session_state["peak_configs"] = configs
            st.rerun()

        new_configs: list[PeakConfig] = []
        for i, p in enumerate(configs):
            with st.expander(f"{p.name}", expanded=False):
                name = st.text_input("Name", value=p.name, key=f"ws_n_{p.uid}")
                center = st.number_input(
                    "Center", value=float(p.center), format="%.3f", key=f"ws_c_{p.uid}"
                )
                labeled_help("Tolerance", "tolerance", lang)
                tol = st.number_input(
                    "Tolerance / pos_error", value=float(p.tolerance), key=f"ws_t_{p.uid}"
                )
                sigma = st.number_input("Sigma", value=float(p.sigma), key=f"ws_s_{p.uid}")
                labeled_help("Fix center", "fix_center", lang)
                fix_c = st.checkbox(
                    "Fix center", value=p.fix_center or tol <= 0, key=f"ws_fc_{p.uid}"
                )
                labeled_help("Fix FWHM", "fix_fwhm", lang)
                fix_w = st.checkbox("Fix FWHM", value=p.fix_fwhm, key=f"ws_fw_{p.uid}")
                if st.button("Delete", key=f"ws_del_{p.uid}"):
                    st.session_state["peak_configs"] = [x for x in configs if x.uid != p.uid]
                    st.rerun()
                new_configs.append(
                    PeakConfig(
                        name=name,
                        center=float(center),
                        tolerance=float(tol),
                        sigma=float(sigma),
                        fix_center=bool(fix_c),
                        fix_fwhm=bool(fix_w),
                        fraction=p.fraction,
                        link_group=p.link_group,
                        link_delta_be=p.link_delta_be,
                        uid=p.uid,
                    )
                )
        if new_configs:
            st.session_state["peak_configs"] = new_configs
            configs = new_configs

    auto = st.checkbox("Auto-refit when clicking Apply", value=True)
    apply = st.button(t("apply_refit", lang), type="primary")
    save_name = st.text_input("Save current fit as", value="workspace_fit")
    do_save = st.button(t("save_named_fit", lang))

with right:
    if apply or (auto and apply):
        pass  # handled below

    # Run fit when Apply clicked
    if apply:
        constraints = FitConstraints(
            enable_fix_fwhm=fix_fwhm,
            enable_doublet_links=doublet,
            shared_sigma=shared_sigma,
        )
        st.session_state["baseline_settings"] = settings
        st.session_state["noise_method"] = noise_method
        st.session_state["noise_window"] = int(noise_window)
        st.session_state["savgol_poly"] = int(savgol_poly)
        st.session_state["peak_model"] = peak_model
        st.session_state["fit_constraints"] = constraints
        out = run_fit(
            sp,
            configs,
            peak_model=peak_model,
            baseline=settings,
            noise_method=noise_method,
            noise_window=int(noise_window),
            savgol_poly=int(savgol_poly),
            constraints=constraints,
        )
        if out["error"]:
            st.error(out["error"])
        else:
            st.session_state["corrected"] = out["corrected"]
            st.session_state["baseline"] = out["baseline"]
            st.session_state["smoothed"] = out["smoothed"]
            st.session_state["best_fit"] = out["best_fit"]
            st.session_state["peaks_df"] = out["peaks_df"]
            st.session_state["metrics"] = out["metrics"]
            st.session_state["fit_components"] = out["components"]
            snap = snapshot_from_fit_result(
                sp,
                out,
                label="workspace",
                peaks=configs,
                peak_model=peak_model,
                baseline=settings,
                noise_method=noise_method,
                noise_window=int(noise_window),
                savgol_poly=int(savgol_poly),
                constraints=constraints,
            )
            append_fit_snapshot(snap)
            persist_session_to_active(save_disk=True)

    if do_save and st.session_state.get("best_fit") is not None:
        # save last curves as named
        from src.core.project import FitSnapshot

        snap = FitSnapshot(
            label=save_name,
            peak_model=st.session_state.get("peak_model", "pseudovoigt"),
            peak_configs=list(st.session_state.get("peak_configs") or []),
            baseline_settings=st.session_state.get("baseline_settings"),
            noise_method=st.session_state.get("noise_method", "none"),
            noise_window=int(st.session_state.get("noise_window", 5)),
            savgol_poly=int(st.session_state.get("savgol_poly", 2)),
            fit_constraints=st.session_state.get("fit_constraints"),
            metrics=st.session_state.get("metrics"),
            peaks_table=None
            if st.session_state.get("peaks_df") is None
            else st.session_state["peaks_df"].to_dict(orient="records"),
            corrected=None
            if st.session_state.get("corrected") is None
            else np.asarray(st.session_state["corrected"]).tolist(),
            baseline=None
            if st.session_state.get("baseline") is None
            else np.asarray(st.session_state["baseline"]).tolist(),
            smoothed=None
            if st.session_state.get("smoothed") is None
            else np.asarray(st.session_state["smoothed"]).tolist(),
            best_fit=None
            if st.session_state.get("best_fit") is None
            else np.asarray(st.session_state["best_fit"]).tolist(),
            components=None
            if not st.session_state.get("fit_components")
            else [np.asarray(c).tolist() for c in st.session_state["fit_components"] if c is not None],
            binding_energy=np.asarray(sp.binding_energy).tolist(),
        )
        saved = dict(st.session_state.get("saved_fits") or {})
        saved[snap.id] = snap
        st.session_state["saved_fits"] = saved
        persist_session_to_active(save_disk=True)
        st.success(f"Saved fit `{save_name}`")

    saved = dict(st.session_state.get("saved_fits") or {})
    if saved:
        sid = st.selectbox(
            "Show saved fit (overlay as previous/grey via load)",
            options=["—"] + list(saved.keys()),
            format_func=lambda i: "—" if i == "—" else f"{saved[i].label} ({i})",
        )
        if sid != "—" and st.button("Overlay saved fit (grey)"):
            st.session_state["previous_fit"] = np.asarray(saved[sid].best_fit)
            st.rerun()
        if sid != "—" and st.button("Load saved fit as current"):
            snap = saved[sid]
            st.session_state["previous_fit"] = st.session_state.get("best_fit")
            st.session_state["best_fit"] = None if snap.best_fit is None else np.asarray(snap.best_fit)
            st.session_state["corrected"] = None if snap.corrected is None else np.asarray(snap.corrected)
            st.session_state["baseline"] = None if snap.baseline is None else np.asarray(snap.baseline)
            st.session_state["peak_configs"] = list(snap.peak_configs)
            st.session_state["metrics"] = snap.metrics
            if snap.peaks_table:
                st.session_state["peaks_df"] = pd.DataFrame(snap.peaks_table)
            st.rerun()

    if st.session_state.get("metrics"):
        m = st.session_state["metrics"]
        a, b, c = st.columns(3)
        a.metric("R", f"{m.get('R', float('nan')):.4f}")
        b.metric("R²", f"{m.get('R_squared', m.get('r_squared', float('nan'))):.4f}")
        c.metric("RMSE", f"{m.get('rmse', float('nan')):.3f}")

    if st.session_state.get("peaks_df") is not None:
        st.dataframe(st.session_state["peaks_df"], use_container_width=True)

    names = [p.name for p in st.session_state.get("peak_configs") or []]
    render_spectrum_viewer(
        sp.binding_energy,
        sp.intensity,
        viewer_key="workspace",
        title=t("interactive_title", lang),
        lang=lang,
        baseline=st.session_state.get("baseline"),
        corrected=st.session_state.get("corrected"),
        denoised=st.session_state.get("smoothed"),
        best_fit=st.session_state.get("best_fit"),
        previous_fit=st.session_state.get("previous_fit"),
        components=st.session_state.get("fit_components"),
        component_names=names,
    )

    y_diag = st.session_state.get("corrected")
    if y_diag is None:
        y_diag = sp.intensity
    render_mean_uncertainty_panel(
        sp.binding_energy,
        y_diag,
        list(st.session_state.get("peak_configs") or []),
        widget_prefix="workspace",
        invert_x=bool(st.session_state.get("workspace_invx", True)),
        fit_components=st.session_state.get("fit_components"),
        best_fit=st.session_state.get("best_fit"),
        lang=lang,
    )
