"""Generate PyMC sampling artifacts for CI/CD.

This test module generates netCDF files and ArviZ visualizations
that are uploaded as GitHub Actions artifacts.
"""

from pathlib import Path
from typing import Callable

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


@pytest.fixture
def netcdf_saver() -> Callable[[az.InferenceData, Path, str], None]:
    """Fixture that returns a function to save InferenceData to netCDF file.
    
    Returns:
        A callable that saves InferenceData to netCDF file
    """
    def _save_netcdf(idata: az.InferenceData, path: Path, name: str) -> None:
        nc_path = path / f"{name}.nc"
        idata.to_netcdf(nc_path)
        print(f"Saved {name} netCDF to {nc_path}")
        assert nc_path.exists()
    
    return _save_netcdf


@pytest.fixture
def plot_saver() -> Callable[[Path, str], None]:
    """Fixture that returns a function to save matplotlib figure to PNG file.
    
    Returns:
        A callable that saves current matplotlib figure to PNG
    """
    def _save_plot(path: Path, name: str) -> None:
        plot_path = path / f"{name}.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close("all")
        assert plot_path.exists()
    
    return _save_plot


@pytest.fixture
def arviz_plot_generator(
    plot_saver: Callable[[Path, str], None],
) -> Callable[[az.InferenceData, Path, str, list[str] | None, bool], None]:
    """Fixture that returns a function to generate standard ArviZ diagnostic plots.
    
    Args:
        plot_saver: Fixture for saving plots
        
    Returns:
        A callable that generates ArviZ diagnostic plots
    """
    def _generate_arviz_plots(
        idata: az.InferenceData,
        plots_dir: Path,
        prefix: str,
        var_names: list[str] | None = None,
        include_pair: bool = False,
    ) -> None:
        print(f"Generating ArviZ plots for {prefix}...")
        
        # Trace plot
        az.plot_trace(idata, var_names=var_names)
        plot_saver(plots_dir, f"{prefix}_trace")
        
        # Posterior plot
        az.plot_posterior(idata, var_names=var_names)
        plot_saver(plots_dir, f"{prefix}_posterior")
        
        # Forest plot
        az.plot_forest(idata, var_names=var_names)
        plot_saver(plots_dir, f"{prefix}_forest")
        
        # Pair plot (optional)
        if include_pair and var_names and len(var_names) >= 2:
            # Only use first two variables for pair plot
            pair_vars = var_names[:2]
            az.plot_pair(idata, var_names=pair_vars, divergences=True)
            plot_saver(plots_dir, f"{prefix}_pair")
    
    return _generate_arviz_plots


def test_blocks_fit_artifacts(
    sample_trials_data: pl.DataFrame,
    output_dirs: dict[str, Path],
    netcdf_saver: Callable[[az.InferenceData, Path, str], None],
    arviz_plot_generator: Callable[[az.InferenceData, Path, str, list[str] | None, bool], None],
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
    netcdf_saver(idata, netcdf_dir, "blocks_fit")

    # Generate ArviZ plots
    arviz_plot_generator(
        idata,
        plots_dir,
        prefix="blocks",
        var_names=["intercept", "slope", "threshold"],
        include_pair=True,
    )


def test_trials_fit_artifacts(
    sample_trials_data: pl.DataFrame,
    output_dirs: dict[str, Path],
    netcdf_saver: Callable[[az.InferenceData, Path, str], None],
    arviz_plot_generator: Callable[[az.InferenceData, Path, str, list[str] | None, bool], None],
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
    netcdf_saver(idata, netcdf_dir, "trials_fit")

    # Generate ArviZ plots
    arviz_plot_generator(
        idata,
        plots_dir,
        prefix="trials",
        include_pair=False,
    )

    print("All outputs generated successfully!")
