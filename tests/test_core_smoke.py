"""Smoke tests for XPS-Deconv core algorithms."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.baseline import compute_baseline, median_in_windows, auto_edge_windows
from src.core.fitting import perform_deconvolution
from src.core.models import BaselineSettings, PeakConfig, SpectrumData
from src.core.region import crop_spectrum


def _synthetic_peak(be: np.ndarray, center: float, amp: float = 100.0, sigma: float = 0.8) -> np.ndarray:
    return amp * np.exp(-0.5 * ((be - center) / sigma) ** 2)


def test_crop_spectrum():
    be = np.linspace(290, 280, 101)
    y = np.ones_like(be)
    sp = SpectrumData(binding_energy=be, intensity=y, core_level="C1s")
    frag = crop_spectrum(sp, 284.0, 286.0)
    assert frag.binding_energy.min() >= 284.0
    assert frag.binding_energy.max() <= 286.0
    assert frag.binding_energy.size >= 3


def test_median_baseline_noise_floor():
    be = np.linspace(295, 280, 301)
    y = np.full_like(be, 10.0)  # flat noise floor
    y += _synthetic_peak(be, 284.8, amp=200.0)
    settings = BaselineSettings(method="median_linear", edge_fraction=0.1, manual_windows=[])
    corrected, baseline = compute_baseline(be, y, settings)
    # baseline near noise floor
    assert abs(float(np.median(baseline[:20])) - 10.0) < 2.0
    assert float(np.max(corrected)) > 100.0


def test_median_in_windows():
    be = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([10.0, 100.0, 11.0, 12.0, 200.0])
    med = median_in_windows(be, y, [(1.0, 1.5), (3.0, 4.0)])
    assert med == pytest.approx(11.0) or med == pytest.approx(10.0) or med == pytest.approx(12.0)


def test_auto_edge_windows():
    be = np.linspace(0, 100, 101)
    wins = auto_edge_windows(be, 0.1)
    assert len(wins) == 2
    assert wins[0][0] <= wins[0][1]


def test_fit_gaussian_synthetic():
    be = np.linspace(290, 280, 201)
    y = 5.0 + _synthetic_peak(be, 284.8, amp=150.0, sigma=0.7)
    settings = BaselineSettings(method="median_horizontal", edge_fraction=0.15)
    corrected, _ = compute_baseline(be, y, settings)
    result, df, metrics, err = perform_deconvolution(
        be,
        corrected,
        [PeakConfig(name="C-C", center=284.8, tolerance=0.5, sigma=0.7)],
        peak_model="gaussian",
    )
    assert err is None
    assert result is not None
    assert df is not None and len(df) == 1
    assert metrics is not None and metrics["r_squared"] > 0.9
