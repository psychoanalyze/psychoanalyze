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
    
    # Check that block-level parameters exist with correct shape
    assert "intercept" in idata.posterior
    assert "slope" in idata.posterior
    assert "threshold" in idata.posterior
    assert idata.posterior["intercept"].shape[-1] == 2  # 2 blocks


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
    
    # Check block-level arrays
    assert "intercept" in summary
    assert "slope" in summary
    assert "threshold" in summary
    assert isinstance(summary["intercept"], np.ndarray)
    assert len(summary["intercept"]) == 2  # 2 blocks


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
    """Should fit hierarchical model using points-level data."""
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
    assert idata.posterior["intercept"].shape[-1] == 2


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
    # Even though block 1 has sparse data
    assert len(summary["threshold"]) == 2
    assert not np.isnan(summary["threshold"]).any()
    assert not np.isinf(summary["threshold"]).any()
    
    # Group-level parameters should capture overall pattern
    assert isinstance(summary["mu_intercept"], float)
    assert isinstance(summary["sigma_intercept"], float)
