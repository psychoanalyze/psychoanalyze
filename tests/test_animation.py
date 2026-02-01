"""Tests for psychoanalyze.animation module."""
import tempfile
from pathlib import Path

import polars as pl
import pytest

from psychoanalyze.animation import AnimatedSampler, SamplingState


@pytest.fixture
def trials_df() -> pl.DataFrame:
    """Create sample trial data for testing."""
    return pl.DataFrame({
        "Intensity": [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
        "Result": [0, 0, 0, 1, 1, 1, 1, 1],
    })


def test_animated_sampler_initialization(trials_df: pl.DataFrame) -> None:
    """Test that AnimatedSampler initializes correctly."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    assert sampler.state == SamplingState.IDLE
    assert sampler.draws == 50
    assert sampler.tune == 50
    assert sampler.chains == 1
    assert sampler.current_draw == 0
    assert sampler.idata is None


def test_sample_full(trials_df: pl.DataFrame) -> None:
    """Test full sampling without animation."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    idata = sampler.sample_full()
    
    assert idata is not None
    assert sampler.state == SamplingState.COMPLETED
    assert "intercept" in idata.posterior
    assert "slope" in idata.posterior
    assert "threshold" in idata.posterior
    assert idata.posterior["intercept"].shape == (1, 50)


def test_sample_with_snapshots(trials_df: pl.DataFrame) -> None:
    """Test sampling with periodic snapshots."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    idata, snapshots = sampler.sample_with_snapshots(snapshot_interval=10)
    
    assert idata is not None
    assert len(snapshots) > 0
    assert all(isinstance(s.draw, int) for s in snapshots)
    assert all(s.chain == 0 for s in snapshots)
    
    # Check that snapshots contain expected variables
    first_snapshot = snapshots[0]
    assert "intercept" in first_snapshot.posterior_samples
    assert "slope" in first_snapshot.posterior_samples
    assert "threshold" in first_snapshot.posterior_samples


def test_get_snapshot(trials_df: pl.DataFrame) -> None:
    """Test retrieving specific snapshots."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    sampler.sample_with_snapshots(snapshot_interval=10)
    
    # Get a snapshot that should exist
    snapshot = sampler.get_snapshot(draw=10, chain=0)
    assert snapshot is not None
    assert snapshot.draw == 10
    assert snapshot.chain == 0
    
    # Get a snapshot that doesn't exist
    snapshot_missing = sampler.get_snapshot(draw=5, chain=0)
    assert snapshot_missing is None


def test_rewind_to(trials_df: pl.DataFrame) -> None:
    """Test rewinding to a specific draw."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    sampler.sample_with_snapshots(snapshot_interval=10)
    
    snapshot = sampler.rewind_to(draw=20, chain=0)
    
    assert sampler.current_draw == 20
    assert sampler.current_chain == 0
    assert snapshot is not None
    assert snapshot.draw == 20


def test_get_parameter_evolution(trials_df: pl.DataFrame) -> None:
    """Test getting parameter evolution over draws."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    sampler.sample_full()
    
    threshold_df = sampler.get_parameter_evolution("threshold", chain=0)
    
    assert len(threshold_df) == 50
    assert "draw" in threshold_df.columns
    assert "value" in threshold_df.columns
    assert threshold_df["draw"].to_list() == list(range(50))


def test_get_trace_data(trials_df: pl.DataFrame) -> None:
    """Test getting trace data up to a specific draw."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    sampler.sample_full()
    
    # Get all traces
    traces = sampler.get_trace_data()
    assert "intercept" in traces
    assert "slope" in traces
    assert "threshold" in traces
    assert traces["intercept"].shape == (1, 50)
    
    # Get traces up to draw 25
    traces_partial = sampler.get_trace_data(up_to_draw=25)
    assert traces_partial["intercept"].shape == (1, 25)


def test_get_snapshots_for_chain(trials_df: pl.DataFrame) -> None:
    """Test getting all snapshots for a specific chain."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=2,
        random_seed=42,
    )
    
    sampler.sample_with_snapshots(snapshot_interval=10)
    
    chain_0_snapshots = sampler.get_snapshots_for_chain(chain=0)
    chain_1_snapshots = sampler.get_snapshots_for_chain(chain=1)
    
    assert len(chain_0_snapshots) > 0
    assert len(chain_1_snapshots) > 0
    assert all(s.chain == 0 for s in chain_0_snapshots)
    assert all(s.chain == 1 for s in chain_1_snapshots)


def test_save_and_load_snapshots(trials_df: pl.DataFrame) -> None:
    """Test saving and loading snapshots to/from disk."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    sampler.sample_with_snapshots(snapshot_interval=10)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "snapshots"
        
        # Save snapshots
        sampler.save_snapshots(save_path)
        
        assert (save_path / "idata.nc").exists()
        assert (save_path / "snapshots.csv").exists()
        
        # Load snapshots
        new_sampler = AnimatedSampler(
            trials=trials_df,
            draws=50,
            tune=50,
            chains=1,
            random_seed=42,
        )
        new_sampler.load_snapshots(save_path)
        
        assert new_sampler.idata is not None
        assert new_sampler.state == SamplingState.COMPLETED


def test_error_on_missing_idata(trials_df: pl.DataFrame) -> None:
    """Test that accessing traces before sampling raises an error."""
    sampler = AnimatedSampler(
        trials=trials_df,
        draws=50,
        tune=50,
        chains=1,
        random_seed=42,
    )
    
    with pytest.raises(ValueError, match="No sampling data available"):
        sampler.get_parameter_evolution("threshold")
    
    with pytest.raises(ValueError, match="No sampling data available"):
        sampler.get_trace_data()
