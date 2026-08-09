"""Deconvolution / peak fitting page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import numpy as np

from src.core.models import PEAK_MODELS, FitConstraints, PeakConfig
from src.services.analysis_service import run_fit, snapshot_from_fit_result
from src.services.peak_library_service import load_library
from src.ui.components.help import help_mark, labeled_help
from src.ui.components.sidebar import render_sidebar
from src.ui.components.spectrum_viewer import render_spectrum_viewer
from src.ui.components.uncertainty_plot import render_mean_uncertainty_panel
from src.ui.project_state import append_fit_snapshot, persist_session_to_active
from src.ui.session_keys import init_session_state
from src.utils.cancel import CancelToken
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

ensure_runtime_dirs()
init_session_state()
lang = render_sidebar()

st.header(t("nav_fit", lang))
sp = st.session_state.get("active_spectrum") or st.session_state.get("full_spectrum")
if sp is None:
    st.warning(t("need_spectrum", lang))
    st.stop()

if not isinstance(st.session_state.get("peak_configs"), list):
    st.session_state["peak_configs"] = []


def _peak_widget_keys(uid: str) -> dict[str, str]:
    return {
        "name": f"pn_{uid}",
        "center": f"pc_{uid}",
        "tol": f"pt_{uid}",
        "sigma": f"ps_{uid}",
        "frac": f"pf_{uid}",
        "fix_c": f"pfc_{uid}",
        "fix_w": f"pfw_{uid}",
        "link_g": f"plg_{uid}",
        "link_d": f"pld_{uid}",
    }


def _clear_peak_widget_keys(uid: str) -> None:
    for key in _peak_widget_keys(uid).values():
        st.session_state.pop(key, None)


def _read_peak_from_widgets(base: PeakConfig) -> PeakConfig:
    keys = _peak_widget_keys(base.uid)
    name = st.session_state.get(keys["name"], base.name)
    center = float(st.session_state.get(keys["center"], base.center))
    tol = float(st.session_state.get(keys["tol"], base.tolerance))
    sigma = float(st.session_state.get(keys["sigma"], base.sigma))
    frac = float(st.session_state.get(keys["frac"], base.fraction))
    fix_c = bool(st.session_state.get(keys["fix_c"], base.fix_center or tol <= 0))
    fix_w = bool(st.session_state.get(keys["fix_w"], base.fix_fwhm))
    link_g = str(st.session_state.get(keys["link_g"], base.link_group or "")).strip()
    link_d = float(st.session_state.get(keys["link_d"], base.link_delta_be or 0.0))
    return PeakConfig(
        name=str(name),
        center=center,
        tolerance=tol,
        sigma=sigma,
        fraction=frac,
        fix_center=fix_c,
        fix_fwhm=fix_w,
        link_group=link_g or None,
        link_delta_be=link_d if link_g else None,
        uid=base.uid,
        amplitude=base.amplitude,
    )


def _sync_peaks_from_widgets() -> list[PeakConfig]:
    synced = [_read_peak_from_widgets(p) for p in st.session_state["peak_configs"]]
    st.session_state["peak_configs"] = synced
    return synced


def _same_peak(a: PeakConfig, name: str, center: float) -> bool:
    return a.name.strip() == name.strip() and abs(a.center - center) < 1e-6


labeled_help("Peak model", "peak_model", lang)
peak_model = st.selectbox(
    "Peak model",
    list(PEAK_MODELS),
    index=list(PEAK_MODELS).index(st.session_state.get("peak_model", "pseudovoigt")),
)

st.subheader(t("constraints", lang))
c1, c2, c3 = st.columns(3)
with c1:
    labeled_help("Fix FWHM (all)", "fix_fwhm", lang)
    fix_fwhm = st.toggle("Fix FWHM (all peaks)", value=st.session_state.fit_constraints.enable_fix_fwhm)
with c2:
    labeled_help("Shared sigma", "shared_sigma", lang)
    shared_sigma = st.toggle("Shared sigma", value=st.session_state.fit_constraints.shared_sigma)
with c3:
    labeled_help("Doublet links", "link_group", lang)
    doublet = st.toggle("Enable doublet links", value=st.session_state.fit_constraints.enable_doublet_links)

lib = load_library()
core_options = ["—"] + list(lib.keys())
default_core = sp.core_level if sp.core_level in lib else "—"
core = st.selectbox(
    "Core level for library",
    core_options,
    index=core_options.index(default_core) if default_core in core_options else 0,
)
suggestions = lib.get(core, []) if core != "—" else []

st.subheader(t("peaks", lang))
st.caption(
    f"Active peaks: **{len(st.session_state['peak_configs'])}**. "
    "Default tolerance = 0 (fixed center). Use Delete / Clear all as needed."
)

if st.session_state.pop("pending_clear_lib_pick", False):
    st.session_state["lib_peak_pick"] = []

if suggestions:
    pick = st.multiselect(
        "Add from library",
        options=[f"{n} @ {e:.2f}" for n, e in suggestions],
        key="lib_peak_pick",
    )
else:
    pick = []

b1, b2, b3, b4 = st.columns(4)
with b1:
    add_lib = st.button("Add selected from library", disabled=not pick)
with b2:
    add_blank = st.button("Add blank peak")
with b3:
    save_edits = st.button("Save peak edits")
with b4:
    clear_all = st.button("Clear all peaks", type="secondary")

if add_lib and pick:
    configs = _sync_peaks_from_widgets()
    added = skipped = 0
    for item in pick:
        name, rest = item.split(" @ ")
        center = float(rest)
        if any(_same_peak(p, name.strip(), center) for p in configs):
            skipped += 1
            continue
        configs.append(PeakConfig(name=name.strip(), center=center, tolerance=0.0, fix_center=True))
        added += 1
    st.session_state["peak_configs"] = configs
    st.session_state["pending_clear_lib_pick"] = True
    persist_session_to_active(save_disk=True)
    st.rerun()

if add_blank:
    configs = _sync_peaks_from_widgets()
    configs.append(
        PeakConfig(
            name=f"Peak{len(configs) + 1}",
            center=float(sp.binding_energy.mean()),
            tolerance=0.0,
            fix_center=True,
        )
    )
    st.session_state["peak_configs"] = configs
    persist_session_to_active(save_disk=True)
    st.rerun()

if save_edits:
    _sync_peaks_from_widgets()
    persist_session_to_active(save_disk=True)
    st.success("Saved")

if clear_all:
    for p in list(st.session_state["peak_configs"]):
        _clear_peak_widget_keys(p.uid)
    st.session_state["peak_configs"] = []
    st.session_state["pending_clear_lib_pick"] = True
    persist_session_to_active(save_disk=True)
    st.rerun()

pending_delete = st.session_state.pop("pending_delete_peak_uid", None)
if pending_delete:
    configs = _sync_peaks_from_widgets()
    configs = [p for p in configs if p.uid != pending_delete]
    _clear_peak_widget_keys(pending_delete)
    st.session_state["peak_configs"] = configs
    persist_session_to_active(save_disk=True)
    st.rerun()

existing: list[PeakConfig] = list(st.session_state["peak_configs"])
if not existing:
    st.info("No peaks yet. Add from the library or use **Add blank peak**.")

for i, base in enumerate(existing):
    keys = _peak_widget_keys(base.uid)
    if keys["name"] not in st.session_state:
        st.session_state[keys["name"]] = base.name
    if keys["center"] not in st.session_state:
        st.session_state[keys["center"]] = float(base.center)
    if keys["tol"] not in st.session_state:
        st.session_state[keys["tol"]] = float(base.tolerance)
    if keys["sigma"] not in st.session_state:
        st.session_state[keys["sigma"]] = float(base.sigma)
    if keys["frac"] not in st.session_state:
        st.session_state[keys["frac"]] = float(base.fraction)
    if keys["fix_c"] not in st.session_state:
        st.session_state[keys["fix_c"]] = bool(base.fix_center or base.tolerance <= 0)
    if keys["fix_w"] not in st.session_state:
        st.session_state[keys["fix_w"]] = bool(base.fix_fwhm)
    if keys["link_g"] not in st.session_state:
        st.session_state[keys["link_g"]] = base.link_group or ""
    if keys["link_d"] not in st.session_state:
        st.session_state[keys["link_d"]] = float(base.link_delta_be or 0.0)

    with st.expander(f"Peak {i + 1}: {st.session_state[keys['name']]}", expanded=False):
        head_l, head_r = st.columns([4, 1])
        with head_l:
            st.text_input("Name", key=keys["name"])
        with head_r:
            if st.button("Delete", key=f"del_{base.uid}", type="primary"):
                st.session_state["pending_delete_peak_uid"] = base.uid
                st.rerun()
        st.number_input("Center (eV)", format="%.3f", key=keys["center"])
        labeled_help("Tolerance / pos_error", "tolerance", lang)
        st.number_input("Tolerance ±eV (0 = fix center)", key=keys["tol"])
        st.number_input("Sigma guess", key=keys["sigma"])
        labeled_help("GL fraction", "gl_fraction", lang)
        st.slider("GL fraction (pseudovoigt)", 0.0, 1.0, key=keys["frac"])
        labeled_help("Fix center", "fix_center", lang)
        st.checkbox("Fix center", key=keys["fix_c"])
        labeled_help("Fix FWHM", "fix_fwhm", lang)
        st.checkbox("Fix FWHM (this peak)", key=keys["fix_w"])
        labeled_help("Link group", "link_group", lang)
        st.text_input("Link group id (optional)", key=keys["link_g"])
        labeled_help("Link ΔBE", "link_delta", lang)
        st.number_input("Link ΔBE (eV)", key=keys["link_d"])

run_label = st.text_input("Label for this fit in the sequence", value="fit")
save_named = st.checkbox("Also store as named saved fit", value=False)

if st.button(t("run_fit", lang), type="primary", disabled=not st.session_state["peak_configs"]):
    configs = _sync_peaks_from_widgets()
    st.session_state["peak_model"] = peak_model
    constraints = FitConstraints(
        enable_fix_fwhm=fix_fwhm,
        enable_doublet_links=doublet,
        shared_sigma=shared_sigma,
    )
    st.session_state["fit_constraints"] = constraints
    token: CancelToken = st.session_state["cancel_token"]
    token.reset()
    progress = st.progress(0, text="Starting…")

    def on_prog(v: int, desc: str) -> None:
        progress.progress(min(100, max(0, v)) / 100.0, text=desc)

    out = run_fit(
        sp,
        configs,
        peak_model=peak_model,
        baseline=st.session_state.get("baseline_settings"),
        noise_method=st.session_state.get("noise_method", "none"),
        noise_window=int(st.session_state.get("noise_window", 5)),
        savgol_poly=int(st.session_state.get("savgol_poly", 2)),
        constraints=constraints,
        cancel=token,
        progress=on_prog,
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
            label=run_label or "fit",
            peaks=configs,
            peak_model=peak_model,
            baseline=st.session_state.get("baseline_settings"),
            noise_method=st.session_state.get("noise_method", "none"),
            noise_window=int(st.session_state.get("noise_window", 5)),
            savgol_poly=int(st.session_state.get("savgol_poly", 2)),
            constraints=constraints,
        )
        append_fit_snapshot(snap, also_save_named=(run_label if save_named else None))
        # Expand main plot Y and re-enable Total fit / components after a new fit
        y_lo, y_hi = float("inf"), float("-inf")
        for arr in (
            sp.intensity,
            out.get("baseline"),
            out.get("corrected"),
            out.get("smoothed"),
            out.get("best_fit"),
            *(out.get("components") or []),
        ):
            if arr is None:
                continue
            a = np.asarray(arr, dtype=float)
            if a.size:
                y_lo = min(y_lo, float(np.nanmin(a)))
                y_hi = max(y_hi, float(np.nanmax(a)))
        if y_lo < y_hi:
            pad = (y_hi - y_lo) * 0.05 + 1e-9
            st.session_state["deconv_main_ymin"] = y_lo - pad
            st.session_state["deconv_main_ymax"] = y_hi + pad
            st.session_state["deconv_main_tf"] = True
            st.session_state["deconv_main_tcomp"] = True
        st.success(
            f"Fit complete — R={out['metrics'].get('R', float('nan')):.4f}, "
            f"R²={out['metrics'].get('R_squared', out['metrics'].get('r_squared', float('nan'))):.4f}"
        )

if st.session_state.get("metrics"):
    m = st.session_state["metrics"]
    st.subheader(t("fit_stats", lang))
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("R", f"{m.get('R', float('nan')):.5f}")
    k2.metric("R²", f"{m.get('R_squared', m.get('r_squared', float('nan'))):.5f}")
    k3.metric("RMSE", f"{m.get('rmse', float('nan')):.4f}")
    k4.metric("χ²_red", f"{m.get('chi_square', float('nan'))}")

if st.session_state.get("peaks_df") is not None:
    st.subheader(t("peak_table", lang))
    st.dataframe(st.session_state["peaks_df"], use_container_width=True)

names = [p.name for p in st.session_state.get("peak_configs") or []]
render_spectrum_viewer(
    sp.binding_energy,
    sp.intensity,
    viewer_key="deconv_main",
    title=t("nav_fit", lang),
    lang=lang,
    baseline=st.session_state.get("baseline"),
    corrected=st.session_state.get("corrected"),
    denoised=st.session_state.get("smoothed"),
    best_fit=st.session_state.get("best_fit"),
    previous_fit=st.session_state.get("previous_fit"),
    components=st.session_state.get("fit_components"),
    component_names=names,
)

# --- Extra diagnostic: local mean / uncertainty + selectable PseudoVoigt sum ---
y_diag = st.session_state.get("corrected")
if y_diag is None:
    y_diag = sp.intensity
render_mean_uncertainty_panel(
    sp.binding_energy,
    y_diag,
    list(st.session_state.get("peak_configs") or []),
    widget_prefix="deconv",
    invert_x=bool(st.session_state.get("deconv_main_invx", True)),
    fit_components=st.session_state.get("fit_components"),
    best_fit=st.session_state.get("best_fit"),
    lang=lang,
)
