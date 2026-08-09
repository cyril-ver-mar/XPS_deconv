"""Peak fitting / deconvolution with lmfit (Layer 2)."""

from __future__ import annotations

import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from lmfit.models import (
    GaussianModel,
    LorentzianModel,
    PseudoVoigtModel,
    VoigtModel,
)

from src.core.models import FitConstraints, PeakConfig
from src.utils.cancel import CancelToken

ProgressCb = Optional[Callable[[int, str], None]]

_MODEL_MAP = {
    "gaussian": GaussianModel,
    "lorentzian": LorentzianModel,
    "voigt": VoigtModel,
    "pseudovoigt": PseudoVoigtModel,
}


def perform_deconvolution(
    be: np.ndarray,
    intensity: np.ndarray,
    peak_configs: List[PeakConfig],
    peak_model: str = "pseudovoigt",
    constraints: Optional[FitConstraints] = None,
    cancel: Optional[CancelToken] = None,
    progress: ProgressCb = None,
) -> Tuple[Optional[Any], Optional[pd.DataFrame], Optional[Dict[str, Any]], Optional[str]]:
    """Fit peaks to an already baseline-corrected intensity.

    Returns (lmfit result, peaks dataframe, metrics dict, error_message).
    """
    constraints = constraints or FitConstraints()

    def set_progress(value: int, desc: str) -> None:
        if progress is not None:
            progress(value, desc)

    try:
        set_progress(10, "Validating inputs…")
        if not peak_configs:
            return None, None, None, "No peaks selected"
        if cancel and cancel.is_cancelled:
            return None, None, None, "Cancelled"

        ModelClass = _MODEL_MAP.get(peak_model)
        if ModelClass is None:
            return None, None, None, f"Unknown peak model: {peak_model}"

        set_progress(40, "Building model…")
        model = None
        for i, _ in enumerate(peak_configs):
            peak_model_i = ModelClass(prefix=f"p{i}_")
            model = peak_model_i if model is None else model + peak_model_i

        assert model is not None
        params = model.make_params()
        y = np.asarray(intensity, dtype=float)
        height_guess = float(np.max(y) * 0.5) if y.size else 1.0

        for i, config in enumerate(peak_configs):
            prefix = f"p{i}_"
            center_guess = float(config.center)
            tolerance = float(config.tolerance)

            if config.fix_center or tolerance <= 0:
                params[f"{prefix}center"].set(value=center_guess, vary=False)
            else:
                params[f"{prefix}center"].set(
                    value=center_guess,
                    min=center_guess - tolerance,
                    max=center_guess + tolerance,
                    vary=True,
                )

            if f"{prefix}height" in params:
                amp0 = config.amplitude if config.amplitude is not None else height_guess
                params[f"{prefix}height"].set(value=float(amp0), min=0)
            elif f"{prefix}amplitude" in params:
                amp0 = config.amplitude if config.amplitude is not None else height_guess * 2.5
                params[f"{prefix}amplitude"].set(value=float(amp0), min=0)

            sigma0 = max(0.1, float(config.sigma))
            params[f"{prefix}sigma"].set(
                value=sigma0,
                min=0.05,
                max=8.0,
                vary=not constraints.enable_fix_fwhm and not config.fix_fwhm,
            )
            if f"{prefix}fraction" in params:
                params[f"{prefix}fraction"].set(
                    value=float(np.clip(config.fraction, 0.0, 1.0)),
                    min=0.0,
                    max=1.0,
                )
            if f"{prefix}gamma" in params:
                params[f"{prefix}gamma"].set(value=sigma0, min=0.05, max=8.0)

        if constraints.shared_sigma and len(peak_configs) > 1:
            for i in range(1, len(peak_configs)):
                params[f"p{i}_sigma"].set(expr="p0_sigma")

        if constraints.enable_doublet_links:
            groups: Dict[str, List[int]] = {}
            for i, cfg in enumerate(peak_configs):
                if cfg.link_group:
                    groups.setdefault(cfg.link_group, []).append(i)
            for _gid, idxs in groups.items():
                if len(idxs) < 2:
                    continue
                i0, i1 = idxs[0], idxs[1]
                delta = peak_configs[i1].link_delta_be
                if delta is None:
                    delta = peak_configs[i1].center - peak_configs[i0].center
                params[f"p{i1}_center"].set(expr=f"p{i0}_center + ({float(delta)})")

        if cancel and cancel.is_cancelled:
            return None, None, None, "Cancelled"

        set_progress(70, "Running lmfit…")
        t0 = time.time()
        result = model.fit(y, params, x=np.asarray(be, dtype=float))
        fit_time = time.time() - t0

        if cancel and cancel.is_cancelled:
            return None, None, None, "Cancelled"

        set_progress(90, "Extracting peak table…")
        peak_rows = []
        total_area = 0.0
        for i, config in enumerate(peak_configs):
            prefix = f"p{i}_"
            p = result.params
            center = p[f"{prefix}center"].value
            center_err = p[f"{prefix}center"].stderr or 0.0
            sigma = p[f"{prefix}sigma"].value
            sigma_err = p[f"{prefix}sigma"].stderr or 0.0
            fwhm = p[f"{prefix}fwhm"].value if f"{prefix}fwhm" in p else 2.355 * sigma

            if f"{prefix}height" in p:
                height = p[f"{prefix}height"].value
                height_err = p[f"{prefix}height"].stderr or 0.0
            else:
                amplitude = p[f"{prefix}amplitude"].value
                height = amplitude / (sigma * np.sqrt(2 * np.pi) + 1e-18)
                height_err = 0.0

            if f"{prefix}amplitude" in p:
                area = p[f"{prefix}amplitude"].value
                area_err = p[f"{prefix}amplitude"].stderr or 0.0
            else:
                area = height * sigma * np.sqrt(2 * np.pi)
                area_err = 0.0

            total_area += area
            peak_rows.append(
                {
                    "Peak": config.name,
                    "Position_eV": round(center, 4),
                    "Position_err": round(center_err, 5),
                    "Height": round(height, 4),
                    "Height_err": round(height_err, 5),
                    "Sigma_eV": round(sigma, 4),
                    "Sigma_err": round(sigma_err, 5),
                    "FWHM_eV": round(fwhm, 4),
                    "Area": round(area, 4),
                    "Area_err": round(area_err, 5),
                }
            )

        df = pd.DataFrame(peak_rows)
        if total_area > 0:
            df["Area_percent"] = (df["Area"] / total_area * 100).round(2)
        else:
            df["Area_percent"] = 0.0

        residuals = result.residual
        rmse = float(np.sqrt(np.mean(residuals**2)))
        ss_res = float(np.sum(residuals**2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        metrics = {
            "chi_square": float(result.redchi) if result.redchi is not None else None,
            "rmse": rmse,
            "r_squared": r_squared,
            "total_area": float(total_area),
            "n_iterations": int(result.nfev),
            "fit_time_s": fit_time,
            "success": bool(result.success),
            "message": str(result.message),
            "peak_model": peak_model,
        }
        set_progress(100, "Done")
        return result, df, metrics, None
    except Exception as exc:  # noqa: BLE001 — surface to UI
        return None, None, None, f"{exc}\n{traceback.format_exc()}"
