"""Deconvolution / peak fitting page."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.core.models import PEAK_MODELS, FitConstraints, PeakConfig
from src.services.analysis_service import run_fit
from src.services.peak_library_service import load_library
from src.ui.components.plots import spectrum_figure
from src.ui.components.sidebar import render_sidebar
from src.ui.session_keys import init_session_state
from src.utils.cancel import CancelToken
from src.utils.i18n import t
from src.utils.paths import ensure_runtime_dirs

st.set_page_config(page_title="Deconvolution — XPS-Deconv", layout="wide")
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
    # Prefer live widget values when present; otherwise keep stored config.
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


st.markdown(
    """
**Peak models**
- **gaussian** — pure Gaussian line shape  
- **lorentzian** — pure Lorentzian  
- **voigt** — convolution of Gaussian and Lorentzian  
- **pseudovoigt** — weighted mix (GL(m)-like) via `fraction`  
"""
    if lang == "en"
    else """
**Модели пиков**
- **gaussian** — чистая гауссиана  
- **lorentzian** — чистая лоренциана  
- **voigt** — свёртка гауссианы и лоренцианы  
- **pseudovoigt** — смесь (аналог GL(m)) через `fraction`  
"""
)

peak_model = st.selectbox(
    "Peak model",
    list(PEAK_MODELS),
    index=list(PEAK_MODELS).index(st.session_state.get("peak_model", "pseudovoigt")),
)

st.subheader("Constraints (on/off)")
c1, c2, c3 = st.columns(3)
with c1:
    fix_fwhm = st.toggle("Fix FWHM (all peaks)", value=st.session_state.fit_constraints.enable_fix_fwhm)
with c2:
    shared_sigma = st.toggle("Shared sigma", value=st.session_state.fit_constraints.shared_sigma)
with c3:
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

st.subheader("Peaks")
st.caption(
    f"Active peaks in this session: **{len(st.session_state['peak_configs'])}**. "
    "Use Delete / Clear all — the list is kept when you change pages."
)

# Pending clear for library multiselect (widget pending-key pattern)
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
    st.caption("No library entries for this core level — add a blank peak or edit the Peak library.")

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
    added = 0
    skipped = 0
    for item in pick:
        name, rest = item.split(" @ ")
        center = float(rest)
        if any(_same_peak(p, name.strip(), center) for p in configs):
            skipped += 1
            continue
        configs.append(PeakConfig(name=name.strip(), center=center))
        added += 1
    st.session_state["peak_configs"] = configs
    st.session_state["pending_clear_lib_pick"] = True
    if added:
        st.success(f"Added {added} peak(s)" + (f"; skipped {skipped} duplicate(s)" if skipped else ""))
    elif skipped:
        st.info("All selected peaks were already in the list.")
    st.rerun()

if add_blank:
    configs = _sync_peaks_from_widgets()
    configs.append(
        PeakConfig(
            name=f"Peak{len(configs) + 1}",
            center=float(sp.binding_energy.mean()),
        )
    )
    st.session_state["peak_configs"] = configs
    st.rerun()

if save_edits:
    _sync_peaks_from_widgets()
    st.success("Peak edits saved")

if clear_all:
    for p in list(st.session_state["peak_configs"]):
        _clear_peak_widget_keys(p.uid)
    st.session_state["peak_configs"] = []
    st.session_state["pending_clear_lib_pick"] = True
    st.rerun()

# Handle pending delete before rendering widgets
pending_delete = st.session_state.pop("pending_delete_peak_uid", None)
if pending_delete:
    configs = _sync_peaks_from_widgets()
    configs = [p for p in configs if p.uid != pending_delete]
    _clear_peak_widget_keys(pending_delete)
    st.session_state["peak_configs"] = configs
    st.rerun()

existing: list[PeakConfig] = list(st.session_state["peak_configs"])
if not existing:
    st.info("No peaks yet. Add from the library or use **Add blank peak**.")

for i, base in enumerate(existing):
    keys = _peak_widget_keys(base.uid)
    # Initialize widget values once (pending-key safe: set before instantiate)
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

    with st.expander(f"Peak {i + 1}: {st.session_state[keys['name']]}", expanded=i < 3):
        head_l, head_r = st.columns([4, 1])
        with head_l:
            st.text_input("Name", key=keys["name"])
        with head_r:
            if st.button("Delete", key=f"del_{base.uid}", type="primary"):
                st.session_state["pending_delete_peak_uid"] = base.uid
                st.rerun()
        st.number_input("Center (eV)", format="%.3f", key=keys["center"])
        st.number_input("Tolerance ±eV (0 = fix center)", key=keys["tol"])
        st.number_input("Sigma guess", key=keys["sigma"])
        st.slider("GL fraction (pseudovoigt)", 0.0, 1.0, key=keys["frac"])
        st.checkbox("Fix center", key=keys["fix_c"])
        st.checkbox("Fix FWHM (this peak)", key=keys["fix_w"])
        st.text_input("Link group id (optional)", key=keys["link_g"])
        st.number_input("Link ΔBE (eV)", key=keys["link_d"])

if st.button("Run deconvolution", type="primary", disabled=not st.session_state["peak_configs"]):
    configs = _sync_peaks_from_widgets()
    if not configs:
        st.error("Add at least one peak before fitting.")
        st.stop()
    st.session_state["peak_model"] = peak_model
    st.session_state["fit_constraints"] = FitConstraints(
        enable_fix_fwhm=fix_fwhm,
        enable_doublet_links=doublet,
        shared_sigma=shared_sigma,
    )
    token: CancelToken = st.session_state["cancel_token"]
    token.reset()
    progress = st.progress(0, text="Starting…")

    def on_prog(v: int, desc: str) -> None:
        progress.progress(min(100, max(0, v)) / 100.0, text=desc)

    baseline = st.session_state.get("baseline_settings")
    out = run_fit(
        sp,
        configs,
        peak_model=peak_model,
        baseline=baseline,
        noise_method=st.session_state.get("noise_method", "none"),
        noise_window=int(st.session_state.get("noise_window", 5)),
        constraints=st.session_state["fit_constraints"],
        cancel=token,
        progress=on_prog,
    )
    if out["error"]:
        st.error(out["error"])
    else:
        st.session_state["corrected"] = out["corrected"]
        st.session_state["baseline"] = out["baseline"]
        st.session_state["best_fit"] = out["best_fit"]
        st.session_state["peaks_df"] = out["peaks_df"]
        st.session_state["metrics"] = out["metrics"]
        comps = []
        result = out["result"]
        if result is not None:
            for i in range(len(configs)):
                comps.append(result.eval_components(x=sp.binding_energy).get(f"p{i}_"))
        st.session_state["fit_components"] = comps
        st.success("Fit complete")

if st.session_state.get("metrics"):
    st.json(st.session_state["metrics"])
if st.session_state.get("peaks_df") is not None:
    st.dataframe(st.session_state["peaks_df"], use_container_width=True)

st.plotly_chart(
    spectrum_figure(
        sp.binding_energy,
        sp.intensity,
        title="Fit",
        baseline=st.session_state.get("baseline"),
        corrected=st.session_state.get("corrected"),
        best_fit=st.session_state.get("best_fit"),
        components=[c for c in (st.session_state.get("fit_components") or []) if c is not None],
    ),
    use_container_width=True,
)
