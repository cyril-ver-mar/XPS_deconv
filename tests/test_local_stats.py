"""Tests for local mean / uncertainty band."""

from __future__ import annotations

import numpy as np

from src.core.local_stats import (
    fraction_residual_within_local_sigma,
    fraction_within_band,
    local_mean_and_uncertainty,
)


def test_local_mean_flat():
    y = np.ones(50) * 10.0
    mean, lo, hi = local_mean_and_uncertainty(y, window=5, n_sigma=1.0)
    assert np.allclose(mean, 10.0)
    assert np.allclose(lo, 10.0)
    assert np.allclose(hi, 10.0)


def test_local_std_widens_with_noise():
    rng = np.random.default_rng(0)
    y = np.ones(80) * 5.0
    y[30:50] += rng.normal(0, 3.0, 20)
    mean, lo, hi = local_mean_and_uncertainty(y, window=7, n_sigma=1.0)
    width = hi - lo
    assert width[40] > width[10]


def test_fraction_within_band_all_inside_flat():
    y = np.ones(40) * 3.0
    _, lo, hi = local_mean_and_uncertainty(y, window=5, n_sigma=1.0)
    pct, n_in, n_tot = fraction_within_band(y, lo, hi)
    assert n_tot == 40
    assert n_in == 40
    assert pct == 100.0


def test_fraction_within_band_counts_outliers():
    y = np.ones(50) * 10.0
    y[0] = 100.0
    y[1] = -50.0
    mean = np.full(50, 10.0)
    lo = mean - 1.0
    hi = mean + 1.0
    pct, n_in, n_tot = fraction_within_band(y, lo, hi)
    assert n_tot == 50
    assert n_in == 48
    assert abs(pct - 96.0) < 1e-9


def test_residual_fraction_depends_on_model():
    rng = np.random.default_rng(1)
    y = 20.0 + rng.normal(0, 0.5, 100)
    good = y.copy()  # perfect model → all residuals ~0
    bad = np.zeros_like(y)
    pct_good, n_good, n_tot = fraction_residual_within_local_sigma(y, good, window=7, n_sigma=1.0)
    pct_bad, n_bad, _ = fraction_residual_within_local_sigma(y, bad, window=7, n_sigma=1.0)
    assert n_tot == 100
    assert pct_good > pct_bad
    assert n_good > n_bad
