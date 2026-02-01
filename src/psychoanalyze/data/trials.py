
"""Functions for data manipulations at the trial level."""
import json
import random
from pathlib import Path
from typing import TypedDict, cast

import arviz as az
import numpy as np
import pandas as pd
import polars as pl
import pymc as pm
import pytensor.tensor as pt

from psychoanalyze.data import subject as subject_utils

data_path = Path("data/trials.csv")

codes = {0: "Miss", 1: "Hit"}
Trial = TypedDict("Trial", {"Result": bool, "Stimulus Magnitude": float})


def generate_trial_index(n_trials: int, options: list[float]) -> list[float]:
    """Generate n trials (no outcomes)."""
    return [random.choice(options) for _ in range(n_trials)]


def sample_trials(trials_ix: list[float], params: dict[str, float]) -> pl.DataFrame:
    """Sample trials from a given index."""
    results = [int(random.random() <= psi(x, params)) for x in trials_ix]
    return pl.DataFrame({"Intensity": trials_ix, "Result": results})


def generate(
    n_trials: int,
    options: list[float],
    params: dict[str, float],
    n_blocks: int,
) -> pl.DataFrame:
    """Generate n trials with outcomes."""
    frames = []
    for i in range(n_blocks):
        trials_ix = generate_trial_index(n_trials, options)
        df = sample_trials(trials_ix, params)
        df = df.with_columns(pl.lit(i).alias("Block"))
        frames.append(df)
    return pl.concat(frames).select(["Block", "Intensity", "Result"])


def load(data_path: Path) -> pl.DataFrame:
    """Load trials data from csv."""
    return pl.read_csv(
        data_path,
        schema_overrides={
            "Result": pl.Int64,
            "Intensity": pl.Float64,
            "Block": pl.Int64,
        },
    )


def from_store(store_data: str) -> pl.DataFrame:
    """Convert JSON-formatted string to DataFrame."""
    df_dict = json.loads(store_data)
    return pl.DataFrame(df_dict["data"])


def to_store(trials: pl.DataFrame) -> str:
    """Convert data to a JSON-formatted string for dcc.Store."""
    return json.dumps({"data": trials.to_dicts()})


def normalize(trials: pl.DataFrame) -> dict[str, pl.DataFrame]:
    """Normalize denormalized trial data."""
    trials = subject_utils.ensure_subject_column(trials)
    return {
        "Session": trials.select(["Subject", "Block"]).unique(),
        "Reference Stimulus": trials.select(["Amp2", "Width2", "Freq2", "Dur2"]),
        "Channel Config": trials.select(["Active Channels", "Return Channels"]),
        "Test Stimulus": trials.select(["Amp1", "Width1", "Freq1", "Dur1"]),
    }


def result(p: float) -> bool:
    """Return a trial result given a probability p."""
    return random.random() < p


def results(n: int, p_x: pl.DataFrame) -> list[Trial]:
    """Return a list of trial results in dict format."""
    intensities = p_x["Intensity"].to_list()
    probs = p_x["p"].to_list()
    prob_map = dict(zip(intensities, probs))

    results = []
    for _ in range(n):
        stimulus_magnitude = random.choice(intensities)
        _result = result(prob_map[stimulus_magnitude])
        results.append(
            Trial(
                {
                    "Stimulus Magnitude": stimulus_magnitude,
                    "Result": _result,
                },
            ),
        )
    return results


def labels(results: list[int]) -> list[str]:
    """Convert a list of outcome codes to their labels."""
    return [codes[result] for result in results]


def psi(intensity: float, params: dict[str, float]) -> float:
    """Calculate the value of the psychometric function for a given intensity."""
    gamma = params["gamma"]
    lambda_ = params["lambda"]
    k = params["k"]
    x_0 = params["x_0"]
    return gamma + (1 - gamma - lambda_) * (1 / (1 + np.exp(-k * (intensity - x_0))))


def moc_sample(n_trials: int, model_params: dict[str, float]) -> pl.DataFrame:
    """Sample results from a method-of-constant-stimuli experiment."""
    x_0 = model_params["x_0"]
    k = model_params["k"]
    intensity_choices = np.linspace(x_0 - 4 / k, x_0 + 4 / k, 7)
    intensities = [float(random.choice(intensity_choices)) for _ in range(n_trials)]
    results = [
        int(random.random() <= psi(intensity, model_params))
        for intensity in intensities
    ]
    return pl.DataFrame({"Intensity": intensities, "Result": results})


def fit(
    trials: pl.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int | None = None,
) -> az.InferenceData:
    """Fit trial data using hierarchical Bayesian logistic regression.
    
    This function now uses the hierarchical model by default, which provides
    better estimates especially for sparse data. For backward compatibility,
    if no 'Block' column is present, a default block is created.
    
    Args:
        trials: DataFrame with 'Intensity' and 'Result' columns.
                Optionally includes 'Block' for multi-block hierarchical fitting.
        draws: Number of posterior samples per chain
        tune: Number of tuning samples
        chains: Number of MCMC chains
        target_accept: Target acceptance probability for NUTS sampler
        random_seed: Random seed for reproducibility
        
    Returns:
        InferenceData object with posterior samples.
    """
    from psychoanalyze.data import hierarchical
    
    # Ensure Block column exists for hierarchical model
    if "Block" not in trials.columns:
        trials = trials.with_columns(pl.lit(0).alias("Block"))
    
    # Use hierarchical model
    return hierarchical.fit(
        trials=trials,
        draws=draws,
        tune=tune,
        chains=chains,
        target_accept=target_accept,
        random_seed=random_seed,
    )


def summarize_fit(idata: az.InferenceData) -> dict[str, float]:
    """Summarize posterior draws for trial-level fits.
    
    For hierarchical models (multi-block), returns the first block's parameters
    for backward compatibility. Uses different key names ('Threshold', 'Slope')
    than blocks.summarize_fit for historical reasons.
    
    Args:
        idata: InferenceData from fit()
        
    Returns:
        Dictionary with 'Threshold' and 'Slope' for the first block.
    """
    from psychoanalyze.data import hierarchical
    
    # Get hierarchical summary
    hier_summary = hierarchical.summarize_fit(idata)
    
    # Check if this is a multi-block fit
    if isinstance(hier_summary.get("threshold"), np.ndarray):
        # Multi-block: return first block for backward compatibility
        return {
            "Threshold": float(hier_summary["threshold"][0]),
            "Slope": float(hier_summary["slope"][0]),
        }
    else:
        # Should not happen with current implementation, but handle gracefully
        return {
            "Threshold": float(hier_summary["threshold"]),
            "Slope": float(hier_summary["slope"]),
        }
