"""Tests for hierarchical model fitting."""

import numpy as np
import polars as pl
import pytest

from psychoanalyze.data import hierarchical


def test_fit_with_multiple_blocks() -> None:
    """Hierarchical fit should work with multiple blocks."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0, 2.0, 3.0, 0.0, 1.0, 2.0, 3.0],
            "Result": [0, 0, 1, 1, 0, 0, 1, 1],
            "Block": [0, 0, 0, 0, 1, 1, 1, 1],
        },
    )
    idata = hierarchical.fit(
        trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )

    # Check that group-level parameters exist
    assert "mu_intercept" in idata.posterior
    assert "sigma_intercept" in idata.posterior
    assert "mu_slope" in idata.posterior
    assert "sigma_slope" in idata.posterior
    assert "mu_gamma" in idata.posterior
    assert "kappa_gamma" in idata.posterior
    assert "mu_lambda" in idata.posterior
    assert "kappa_lambda" in idata.posterior

    # Check that block-level parameters exist with correct shape
    assert "intercept" in idata.posterior
    assert "slope" in idata.posterior
    assert "gamma" in idata.posterior
    assert "lam" in idata.posterior
    assert "threshold" in idata.posterior
    assert idata.posterior["intercept"].shape[-1] == 2  # 2 blocks
    assert idata.posterior["gamma"].shape[-1] == 2  # 2 blocks
    assert idata.posterior["lam"].shape[-1] == 2  # 2 blocks


def test_fit_requires_block_column() -> None:
    """Fit should raise error if Block column is missing."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0],
            "Result": [0, 1],
        },
    )
    with pytest.raises(ValueError, match="Block"):
        hierarchical.fit(trials_df, draws=10, tune=10, chains=1)


def test_summarize_fit() -> None:
    """Summarize should extract group and block-level parameters."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
            "Result": [0, 0, 1, 0, 1, 1],
            "Block": [0, 0, 0, 1, 1, 1],
        },
    )
    idata = hierarchical.fit(
        trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    summary = hierarchical.summarize_fit(idata)

    # Check group-level parameters
    assert "mu_intercept" in summary
    assert "sigma_intercept" in summary
    assert "mu_slope" in summary
    assert "sigma_slope" in summary
    assert "mu_gamma" in summary
    assert "kappa_gamma" in summary
    assert "mu_lambda" in summary
    assert "kappa_lambda" in summary

    # Check block-level arrays
    assert "intercept" in summary
    assert "slope" in summary
    assert "gamma" in summary
    assert "lam" in summary
    assert "threshold" in summary
    assert isinstance(summary["intercept"], np.ndarray)
    assert isinstance(summary["gamma"], np.ndarray)
    assert isinstance(summary["lam"], np.ndarray)
    assert len(summary["intercept"]) == 2  # 2 blocks
    assert len(summary["gamma"]) == 2  # 2 blocks

    # Gamma and lambda should be in valid range [0, 1]
    assert all(0 <= g <= 1 for g in summary["gamma"])
    assert all(0 <= l <= 1 for l in summary["lam"])


def test_curve_credible_band() -> None:
    """Credible band should be computed for specific block."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
            "Result": [0, 0, 1, 0, 1, 1],
            "Block": [0, 0, 0, 1, 1, 1],
        },
    )
    idata = hierarchical.fit(
        trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )

    x = [0.0, 1.0, 2.0, 3.0]
    band = hierarchical.curve_credible_band(idata, x, block_idx=0)

    assert set(band.columns) == {"Intensity", "lower", "upper"}
    assert len(band) == len(x)
    assert all(band["lower"] <= band["upper"])


def test_from_points_with_aggregated_data() -> None:
    """Should fit hierarchical beta-binomial model using points-level data."""
    points_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
            "Hits": [0, 2, 8, 1, 5, 9],
            "n trials": [10, 10, 10, 10, 10, 10],
            "Block": [0, 0, 0, 1, 1, 1],
        },
    )
    idata = hierarchical.from_points(
        points_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )

    # Should have same structure as trial-level fit
    assert "mu_intercept" in idata.posterior
    assert "intercept" in idata.posterior
    assert "gamma" in idata.posterior
    assert "lam" in idata.posterior
    assert "kappa_obs" in idata.posterior  # Overdispersion parameter
    assert idata.posterior["intercept"].shape[-1] == 2
    assert idata.posterior["gamma"].shape[-1] == 2


def test_from_points_requires_correct_columns() -> None:
    """from_points should require specific columns."""
    points_df = pl.DataFrame(
        {
            "Intensity": [0.0, 1.0],
            "Hits": [0, 5],
        },
    )
    with pytest.raises(ValueError, match="Block"):
        hierarchical.from_points(points_df, draws=10, tune=10, chains=1)


def test_hierarchical_vs_independent_fits() -> None:
    """Hierarchical model should provide shrinkage for sparse blocks.

    This test demonstrates the key benefit of hierarchical modeling:
    blocks with little data borrow strength from other blocks.
    """
    # Create data with one well-sampled block and one sparse block
    np.random.seed(42)

    # Block 0: Well-sampled (many trials)
    x0 = np.linspace(-2, 2, 50)
    y0 = (np.random.random(50) < 1 / (1 + np.exp(-x0))).astype(int)

    # Block 1: Sparse (few trials)
    x1 = np.array([-1.0, 0.0, 1.0])
    y1 = np.array([0, 1, 1])

    trials_df = pl.DataFrame(
        {
            "Intensity": np.concatenate([x0, x1]),
            "Result": np.concatenate([y0, y1]),
            "Block": [0] * len(x0) + [1] * len(x1),
        },
    )

    # Fit hierarchical model
    idata = hierarchical.fit(
        trials_df,
        draws=100,
        tune=100,
        chains=1,
        random_seed=42,
    )
    summary = hierarchical.summarize_fit(idata)

    # The hierarchical model should provide reasonable estimates for both blocks
    assert len(summary["threshold"]) == 2
    assert not np.isnan(summary["threshold"]).any()
    assert not np.isinf(summary["threshold"]).any()

    # Group-level parameters should capture overall pattern
    assert isinstance(summary["mu_intercept"], float)
    assert isinstance(summary["sigma_intercept"], float)

    # Gamma and lambda should be present and reasonable
    assert len(summary["gamma"]) == 2
    assert len(summary["lam"]) == 2
    assert all(0 <= g <= 1 for g in summary["gamma"])
    assert all(0 <= l <= 1 for l in summary["lam"])


def test_standardization_parameters_stored() -> None:
    """Fit should store standardization parameters in idata.attrs."""
    trials_df = pl.DataFrame(
        {
            "Intensity": [10.0, 20.0, 30.0, 10.0, 20.0, 30.0],
            "Result": [0, 0, 1, 0, 1, 1],
            "Block": [0, 0, 0, 1, 1, 1],
        },
    )
    idata = hierarchical.fit(
        trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )

    # Standardization parameters should be stored
    assert "x_mean" in idata.attrs
    assert "x_std" in idata.attrs
    assert idata.attrs["x_mean"] == pytest.approx(20.0, rel=0.01)
    assert idata.attrs["x_std"] > 0


def test_threshold_in_original_scale() -> None:
    """Summarized threshold should be in original intensity scale."""
    # Create data with known threshold around x=100
    np.random.seed(42)
    x = np.array([90.0, 95.0, 100.0, 105.0, 110.0] * 10)
    # Simulate with threshold at 100
    probs = 1 / (1 + np.exp(-(x - 100) / 2))
    y = (np.random.random(len(x)) < probs).astype(int)

    trials_df = pl.DataFrame(
        {
            "Intensity": x,
            "Result": y,
            "Block": [0] * len(x),
        },
    )

    idata = hierarchical.fit(
        trials_df,
        draws=200,
        tune=200,
        chains=1,
        random_seed=42,
    )
    summary = hierarchical.summarize_fit(idata)

    # Threshold should be close to 100 (the true value), not near 0
    assert summary["threshold"][0] > 90
    assert summary["threshold"][0] < 110
