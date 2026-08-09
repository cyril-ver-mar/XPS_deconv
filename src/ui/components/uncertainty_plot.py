"""Deconv diagnostic plot: local mean/uncertainty + selectable PseudoVoigt sum."""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np
import plotly.graph_objects as go
from lmfit.models import PseudoVoigtModel

from src.core.local_stats import (
    fraction_residual_within_local_sigma,
    local_mean_and_uncertainty,
)
from src.core.models import PeakConfig
from src.ui.components.plots import DEFAULT_COMPONENT_COLORS


def _guess_height(be: np.ndarray, y: np.ndarray, center: float, half_width: float = 1.5) -> float:
    """Amplitude guess from local max near peak center (avoids invisible tiny peaks)."""
    be = np.asarray(be, dtype=float)
    y = np.asarray(y, dtype=float)
    if be.size == 0 or y.size == 0:
        return 1.0
    mask = (be >= center - half_width) & (be <= center + half_width)
    if not np.any(mask):
        return float(max(np.nanmax(y) * 0.3, 1.0))
    return float(max(np.nanmax(y[mask]) * 0.8, 1.0))


def evaluate_pseudovoigt_components(
    be: np.ndarray,
    peaks: Sequence[PeakConfig],
    components: Optional[Sequence[Optional[np.ndarray]]] = None,
    intensity_for_guess: Optional[np.ndarray] = None,
) -> list[np.ndarray]:
    """Use fitted component curves when available; else evaluate PseudoVoigt guesses."""
    be = np.asarray(be, dtype=float)
    y_ref = np.asarray(intensity_for_guess if intensity_for_guess is not None else np.ones_like(be), dtype=float)
    out: list[np.ndarray] = []
    for i, peak in enumerate(peaks):
        if components is not None and i < len(components) and components[i] is not None:
            out.append(np.asarray(components[i], dtype=float))
            continue
        model = PseudoVoigtModel(prefix=f"p{i}_")
        params = model.make_params()
        params[f"p{i}_center"].set(value=float(peak.center))
        params[f"p{i}_sigma"].set(value=max(0.05, float(peak.sigma)))
        if f"p{i}_fraction" in params:
            params[f"p{i}_fraction"].set(value=float(np.clip(peak.fraction, 0.0, 1.0)))
        amp = peak.amplitude
        if amp is None:
            amp = _guess_height(be, y_ref, float(peak.center), half_width=max(1.0, 2.0 * float(peak.sigma)))
        if f"p{i}_height" in params:
            params[f"p{i}_height"].set(value=float(amp), min=0)
        elif f"p{i}_amplitude" in params:
            params[f"p{i}_amplitude"].set(value=float(amp), min=0)
        out.append(np.asarray(model.eval(params, x=be), dtype=float))
    return out


def mean_uncertainty_peaks_figure(
    be: np.ndarray,
    intensity: np.ndarray,
    peaks: Sequence[PeakConfig],
    *,
    selected_indices: Optional[Sequence[int]] = None,
    fit_components: Optional[Sequence[Optional[np.ndarray]]] = None,
    best_fit: Optional[np.ndarray] = None,
    window: int = 7,
    n_sigma: float = 1.0,
    invert_x: bool = True,
    title: str = "Local mean / uncertainty + PseudoVoigt selection",
) -> Tuple[go.Figure, float, int, int]:
    """Black=original, red=local mean, green=±uncertainty, peaks + selected sum.

    Returns ``(figure, percent_residual_in_±nσ, n_inside, n_total)`` where the
    percent is ``|y − sum(selected peaks)| ≤ n·σ_local`` (depends on peak selection).
    """
    be = np.asarray(be, dtype=float)
    y = np.asarray(intensity, dtype=float)
    mean, lower, upper = local_mean_and_uncertainty(y, window=window, n_sigma=n_sigma)
    comps = evaluate_pseudovoigt_components(be, peaks, fit_components, intensity_for_guess=y)

    if selected_indices is None:
        selected_indices = list(range(len(peaks)))
    selected = [int(i) for i in selected_indices if 0 <= int(i) < len(comps)]

    peak_sum = np.zeros_like(y, dtype=float)
    if selected:
        for i in selected:
            peak_sum = peak_sum + comps[i]
    pct, n_in, n_tot = fraction_residual_within_local_sigma(
        y, peak_sum, window=window, n_sigma=n_sigma
    )

    fig = go.Figure()
    # Uncertainty band (green envelope as two lines + faint fill)
    fig.add_trace(
        go.Scatter(
            x=be,
            y=upper,
            mode="lines",
            name=f"Upper (+{n_sigma:g}σ local)",
            line=dict(color="#2ca02c", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=be,
            y=lower,
            mode="lines",
            name=f"Lower (−{n_sigma:g}σ local)",
            line=dict(color="#2ca02c", width=1.5),
            fill="tonexty",
            fillcolor="rgba(44, 160, 44, 0.12)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=be,
            y=y,
            mode="lines",
            name="Original",
            line=dict(color="#111111", width=1.2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=be,
            y=mean,
            mode="lines",
            name="Local mean",
            line=dict(color="#d62728", width=2.5),
        )
    )

    for i, peak in enumerate(peaks):
        color = DEFAULT_COMPONENT_COLORS[i % len(DEFAULT_COMPONENT_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=be,
                y=comps[i],
                mode="lines",
                name=f"PV: {peak.name}",
                line=dict(color=color, width=1.5, dash="dot"),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=be,
            y=peak_sum,
            mode="lines",
            name="Sum of selected peaks",
            line=dict(color="#9467bd", width=3),
        )
    )

    # Full deconvolution total fit (when a fit has been run)
    if best_fit is not None:
        bf = np.asarray(best_fit, dtype=float)
        if bf.size == y.size:
            fig.add_trace(
                go.Scatter(
                    x=be,
                    y=bf,
                    mode="lines",
                    name="Total fit (deconv)",
                    line=dict(color="#000000", width=2.5, dash="dash"),
                )
            )

    fig.update_layout(
        title=title,
        xaxis_title="Binding energy (eV)",
        yaxis_title="Intensity",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=20, t=60, b=40),
        height=520,
        uirevision="mean-uncert-peaks",
    )
    if invert_x and be.size:
        fig.update_xaxes(range=[float(be.max()), float(be.min())])
    return fig, pct, n_in, n_tot


def render_mean_uncertainty_panel(
    be: np.ndarray,
    intensity: np.ndarray,
    peaks: Sequence[PeakConfig],
    *,
    widget_prefix: str,
    invert_x: bool = True,
    fit_components: Optional[Sequence[Optional[np.ndarray]]] = None,
    best_fit: Optional[np.ndarray] = None,
    lang: str = "ru",
) -> None:
    """Streamlit UI for local mean / uncertainty + selectable PseudoVoigt sum."""
    import streamlit as st

    from src.utils.i18n import t

    st.subheader(t("uncert_title", lang))
    st.caption(t("uncert_caption", lang))

    peak_list = list(peaks or [])
    sel_key = f"{widget_prefix}_uncert_peak_sel"
    win_key = f"{widget_prefix}_uncert_win"
    ns_key = f"{widget_prefix}_uncert_ns"

    if peak_list:
        peak_labels = [f"{i}: {p.name} @ {p.center:.2f} eV" for i, p in enumerate(peak_list)]
        prev = st.session_state.get(sel_key)
        if prev is None or any(lab not in peak_labels for lab in (prev or [])):
            st.session_state[sel_key] = peak_labels
        selected_labels = st.multiselect(
            t("uncert_peaks_sum", lang),
            options=peak_labels,
            key=sel_key,
        )
        selected_idx = [peak_labels.index(lab) for lab in selected_labels if lab in peak_labels]
        if not selected_idx:
            st.caption(t("uncert_no_sel", lang))
    else:
        selected_idx = []
        st.info(t("uncert_add_peaks", lang))

    u1, u2 = st.columns(2)
    with u1:
        uncert_window = st.slider(t("uncert_window", lang), 3, 31, 7, step=2, key=win_key)
    with u2:
        uncert_nsigma = st.slider(t("uncert_nsigma", lang), 0.5, 3.0, 1.0, step=0.1, key=ns_key)

    fig_uncert, pct_in, n_in, n_tot = mean_uncertainty_peaks_figure(
        be,
        intensity,
        peak_list,
        selected_indices=selected_idx,
        fit_components=fit_components,
        best_fit=best_fit,
        window=int(uncert_window),
        n_sigma=float(uncert_nsigma),
        invert_x=bool(invert_x),
        title=t("uncert_title", lang),
    )
    m1, m2 = st.columns(2)
    m1.metric(
        t("uncert_metric", lang, n=f"{float(uncert_nsigma):g}"),
        f"{pct_in:.1f}%",
    )
    m2.metric(t("uncert_count", lang), f"{n_in} / {n_tot}")
    st.plotly_chart(fig_uncert, use_container_width=True)
