"""Generate PyMC sampling artifacts for CI/CD.

This test module generates netCDF files and ArviZ visualizations
that are uploaded as GitHub Actions artifacts.
"""

from pathlib import Path

import arviz as az
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from psychoanalyze.data import blocks, trials


@pytest.fixture
def output_dirs(tmp_path: Path) -> dict[str, Path]:
    """Create output directories for artifacts."""
    netcdf_dir = tmp_path / "netcdf"
    plots_dir = tmp_path / "plots"
    netcdf_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
    return {"netcdf": netcdf_dir, "plots": plots_dir}


@pytest.fixture
def sample_trials_data() -> pl.DataFrame:
    """Sample trial data for testing."""
    return pl.DataFrame({
        "Intensity": [0.0, 1.0, 2.0, 3.0, 4.0] * 4,
        "Result": [0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1],
    })


def test_blocks_fit_artifacts(
    sample_trials_data: pl.DataFrame,
    output_dirs: dict[str, Path],
) -> None:
    """Generate artifacts from blocks.fit()."""
    netcdf_dir = output_dirs["netcdf"]
    plots_dir = output_dirs["plots"]

    print("Running blocks.fit()...")
    idata = blocks.fit(
        sample_trials_data,
        draws=500,
        tune=500,
        chains=2,
        random_seed=42,
    )

    # Save netCDF
    nc_path = netcdf_dir / "blocks_fit.nc"
    idata.to_netcdf(nc_path)
    print(f"Saved blocks netCDF to {nc_path}")
    assert nc_path.exists()

    # Generate ArviZ plots
    print("Generating ArviZ plots for blocks...")

    # Trace plot
    az.plot_trace(idata, var_names=["intercept", "slope", "threshold"])
    plt.savefig(plots_dir / "blocks_trace.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Posterior plot
    az.plot_posterior(idata, var_names=["intercept", "slope", "threshold"])
    plt.savefig(plots_dir / "blocks_posterior.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Pair plot
    az.plot_pair(idata, var_names=["intercept", "slope"], divergences=True)
    plt.savefig(plots_dir / "blocks_pair.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Forest plot
    az.plot_forest(idata, var_names=["intercept", "slope", "threshold"])
    plt.savefig(plots_dir / "blocks_forest.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Verify plots were created
    assert (plots_dir / "blocks_trace.png").exists()
    assert (plots_dir / "blocks_posterior.png").exists()
    assert (plots_dir / "blocks_pair.png").exists()
    assert (plots_dir / "blocks_forest.png").exists()


def test_trials_fit_artifacts(
    sample_trials_data: pl.DataFrame,
    output_dirs: dict[str, Path],
) -> None:
    """Generate artifacts from trials.fit()."""
    netcdf_dir = output_dirs["netcdf"]
    plots_dir = output_dirs["plots"]

    print("Running trials.fit()...")
    idata = trials.fit(
        sample_trials_data,
        draws=500,
        tune=500,
        chains=2,
        random_seed=42,
    )

    # Save netCDF
    nc_path = netcdf_dir / "trials_fit.nc"
    idata.to_netcdf(nc_path)
    print(f"Saved trials netCDF to {nc_path}")
    assert nc_path.exists()

    # Generate ArviZ plots
    print("Generating ArviZ plots for trials...")

    # Trace plot
    az.plot_trace(idata)
    plt.savefig(plots_dir / "trials_trace.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Posterior plot
    az.plot_posterior(idata)
    plt.savefig(plots_dir / "trials_posterior.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Forest plot
    az.plot_forest(idata)
    plt.savefig(plots_dir / "trials_forest.png", dpi=150, bbox_inches="tight")
    plt.close("all")

    # Verify plots were created
    assert (plots_dir / "trials_trace.png").exists()
    assert (plots_dir / "trials_posterior.png").exists()
    assert (plots_dir / "trials_forest.png").exists()

    print("All outputs generated successfully!")
