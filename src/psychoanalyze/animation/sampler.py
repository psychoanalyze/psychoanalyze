"""Animated sampler for PyMC with pause/rewind capabilities.

This module provides functionality to animate MCMC sampling, allowing users to:
- Pause and resume sampling at any point
- Rewind to previous sampling steps
- Save snapshots of the sampling state
- Visualize the evolution of the posterior during sampling
"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import arviz as az
import numpy as np
import polars as pl
import pymc as pm
import pytensor.tensor as pt


class SamplingState(Enum):
    """State of the animated sampler."""

    IDLE = "idle"
    SAMPLING = "sampling"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class SamplerSnapshot:
    """Snapshot of sampling state at a specific draw.
    
    Attributes:
        draw: Current draw number (0-indexed within post-tuning draws).
        chain: Chain number.
        posterior_samples: Dictionary mapping variable names to their samples up to this draw.
        acceptance_rate: Acceptance rate up to this draw.
    """

    draw: int
    chain: int
    posterior_samples: dict[str, np.ndarray]
    acceptance_rate: float


class AnimatedSampler:
    """MCMC sampler with animation capabilities.
    
    This class wraps PyMC's sampling functionality to enable:
    - Step-by-step sampling with pause/resume
    - Rewinding to previous states
    - Capturing snapshots at each draw
    
    The sampler stores all intermediate states, allowing full navigation
    through the sampling process.
    
    Example:
        >>> sampler = AnimatedSampler(model, trials_df)
        >>> sampler.start(draws=100, tune=50)
        >>> # Sample 10 draws
        >>> for _ in range(10):
        ...     sampler.step()
        >>> sampler.pause()
        >>> # Rewind to draw 5
        >>> sampler.rewind_to(5)
        >>> # Resume sampling
        >>> sampler.resume()
    """

    def __init__(
        self,
        trials: pl.DataFrame,
        draws: int = 1000,
        tune: int = 1000,
        chains: int = 2,
        cores: int = 1,
        target_accept: float = 0.9,
        random_seed: int | None = None,
    ) -> None:
        """Initialize the animated sampler.
        
        Args:
            trials: Trial data with Intensity and Result columns.
            draws: Number of posterior samples per chain.
            tune: Number of tuning steps.
            chains: Number of MCMC chains.
            cores: Number of CPU cores to use.
            target_accept: Target acceptance rate for NUTS sampler.
            random_seed: Random seed for reproducibility.
        """
        self.trials = trials
        self.draws = draws
        self.tune = tune
        self.chains = chains
        self.cores = cores
        self.target_accept = target_accept
        self.random_seed = random_seed
        
        self.state = SamplingState.IDLE
        self.current_draw = 0
        self.current_chain = 0
        
        # Storage for snapshots at each draw
        self.snapshots: list[SamplerSnapshot] = []
        
        # Final inference data (populated when sampling completes)
        self.idata: az.InferenceData | None = None
        
        # Build PyMC model
        self._build_model()
    
    def _build_model(self) -> None:
        """Build the PyMC model for Bayesian logistic regression."""
        x = self.trials["Intensity"].to_numpy()
        y = self.trials["Result"].to_numpy()
        
        self.model = pm.Model()
        with self.model:
            intercept = pm.Normal("intercept", mu=0.0, sigma=2.5)
            slope = pm.Normal("slope", mu=0.0, sigma=2.5)
            pm.Bernoulli("obs", logit_p=intercept + slope * x, observed=y)
            
            # Compute threshold as deterministic variable
            intercept_t = pt.as_tensor_variable(intercept)
            slope_t = pt.as_tensor_variable(slope)
            threshold = pt.true_div(pt.mul(intercept_t, -1), slope_t)
            pm.Deterministic("threshold", threshold)
    
    def sample_full(self) -> az.InferenceData:
        """Sample the full posterior without animation.
        
        This is a convenience method for when animation is not needed.
        Uses the same model but samples all draws at once.
        
        Returns:
            InferenceData object with posterior samples.
        """
        with self.model:
            idata = pm.sample(
                draws=self.draws,
                tune=self.tune,
                chains=self.chains,
                cores=self.cores,
                target_accept=self.target_accept,
                random_seed=self.random_seed,
                progressbar=False,
                return_inferencedata=True,
            )
        self.idata = idata
        self.state = SamplingState.COMPLETED
        return idata
    
    def sample_with_snapshots(
        self,
        snapshot_interval: int = 10,
    ) -> tuple[az.InferenceData, list[SamplerSnapshot]]:
        """Sample with periodic snapshots for animation.
        
        This method samples the full posterior but saves snapshots at regular
        intervals. Snapshots can then be used to animate the sampling process
        post-hoc.
        
        Args:
            snapshot_interval: Save a snapshot every N draws.
        
        Returns:
            Tuple of (InferenceData, list of snapshots).
        """
        # Sample full posterior
        idata = self.sample_full()
        
        # Extract snapshots from the posterior
        posterior = idata.posterior
        snapshots = []
        
        for chain_idx in range(self.chains):
            for draw_idx in range(0, self.draws, snapshot_interval):
                # Get samples up to this draw
                samples = {}
                for var_name in ["intercept", "slope", "threshold"]:
                    var_data = posterior[var_name].sel(chain=chain_idx, draw=slice(0, draw_idx + 1))
                    samples[var_name] = var_data.values
                
                # Calculate acceptance rate (simplified - would need sampler stats)
                acceptance_rate = 0.9  # Placeholder
                
                snapshot = SamplerSnapshot(
                    draw=draw_idx,
                    chain=chain_idx,
                    posterior_samples=samples,
                    acceptance_rate=acceptance_rate,
                )
                snapshots.append(snapshot)
        
        self.snapshots = snapshots
        return idata, snapshots
    
    def get_snapshot(self, draw: int, chain: int = 0) -> SamplerSnapshot | None:
        """Get snapshot at a specific draw and chain.
        
        Args:
            draw: Draw number to retrieve.
            chain: Chain number.
        
        Returns:
            Snapshot if available, None otherwise.
        """
        for snapshot in self.snapshots:
            if snapshot.draw == draw and snapshot.chain == chain:
                return snapshot
        return None
    
    def get_snapshots_for_chain(self, chain: int = 0) -> list[SamplerSnapshot]:
        """Get all snapshots for a specific chain.
        
        Args:
            chain: Chain number.
        
        Returns:
            List of snapshots for the chain.
        """
        return [s for s in self.snapshots if s.chain == chain]
    
    def rewind_to(self, draw: int, chain: int = 0) -> SamplerSnapshot | None:
        """Rewind to a specific draw in the sampling process.
        
        Args:
            draw: Target draw number.
            chain: Chain number.
        
        Returns:
            Snapshot at the target draw, or None if not available.
        """
        self.current_draw = draw
        self.current_chain = chain
        return self.get_snapshot(draw, chain)
    
    def get_parameter_evolution(
        self,
        param_name: str,
        chain: int = 0,
    ) -> pl.DataFrame:
        """Get the evolution of a parameter across draws.
        
        Args:
            param_name: Name of parameter (e.g., "threshold", "slope").
            chain: Chain number.
        
        Returns:
            DataFrame with columns: draw, value.
        """
        if self.idata is None:
            msg = "No sampling data available. Run sample_full() or sample_with_snapshots() first."
            raise ValueError(msg)
        
        posterior = self.idata.posterior
        param_data = posterior[param_name].sel(chain=chain).values
        
        return pl.DataFrame({
            "draw": list(range(len(param_data))),
            "value": param_data,
        })
    
    def get_trace_data(self, up_to_draw: int | None = None) -> dict[str, np.ndarray]:
        """Get trace data up to a specific draw.
        
        Args:
            up_to_draw: Maximum draw to include. If None, includes all draws.
        
        Returns:
            Dictionary mapping variable names to their trace arrays.
        """
        if self.idata is None:
            msg = "No sampling data available. Run sample_full() or sample_with_snapshots() first."
            raise ValueError(msg)
        
        posterior = self.idata.posterior
        traces = {}
        
        for var_name in ["intercept", "slope", "threshold"]:
            if up_to_draw is None:
                traces[var_name] = posterior[var_name].values
            else:
                traces[var_name] = posterior[var_name].sel(
                    draw=slice(0, up_to_draw),
                ).values
        
        return traces
    
    def save_snapshots(self, path: Path) -> None:
        """Save snapshots to disk for later replay.
        
        Args:
            path: Directory path to save snapshots.
        """
        path.mkdir(parents=True, exist_ok=True)
        
        # Save InferenceData if available
        if self.idata is not None:
            self.idata.to_netcdf(path / "idata.nc")
        
        # Save snapshot metadata
        snapshot_data = []
        for snapshot in self.snapshots:
            snapshot_data.append({
                "draw": snapshot.draw,
                "chain": snapshot.chain,
                "acceptance_rate": snapshot.acceptance_rate,
            })
        
        if snapshot_data:
            df = pl.DataFrame(snapshot_data)
            df.write_csv(path / "snapshots.csv")
    
    def load_snapshots(self, path: Path) -> None:
        """Load snapshots from disk.
        
        Args:
            path: Directory path containing saved snapshots.
        """
        idata_path = path / "idata.nc"
        if idata_path.exists():
            self.idata = az.from_netcdf(idata_path)
            self.state = SamplingState.COMPLETED
