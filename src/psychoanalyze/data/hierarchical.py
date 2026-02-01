"""Hierarchical model for fitting psychometric functions across multiple blocks.

This module provides a unified interface for fitting psychometric functions
using hierarchical Bayesian models. Unlike independent block-level fits,
hierarchical models share information across blocks through group-level
(hyperprior) parameters, which improves parameter estimation especially
for blocks with sparse data.

The hierarchical structure is:
    - Group level: μ_intercept, σ_intercept, μ_slope, σ_slope (hyperparameters)
    - Block level: intercept[b] ~ Normal(μ_intercept, σ_intercept)
                   slope[b] ~ Normal(μ_slope, σ_slope)
    - Trial level: Result ~ Bernoulli(logit_p = intercept[block] + slope[block] * Intensity)

This approach consolidates both block-level and points-level fitting into a
single coherent framework.
"""

from typing import cast

import arviz as az
import numpy as np
import pandas as pd
import polars as pl
import pymc as pm
import pytensor.tensor as pt
from scipy.special import expit


def fit(
    trials: pl.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int | None = None,
) -> az.InferenceData:
    """Fit hierarchical logistic regression to trial data across multiple blocks.
    
    This function fits a hierarchical Bayesian model where each block gets its own
    intercept and slope parameters, but these parameters are drawn from group-level
    distributions. This allows information sharing across blocks and provides better
    estimates for blocks with limited data.
    
    Args:
        trials: DataFrame with columns 'Intensity', 'Result', and 'Block'
        draws: Number of posterior samples per chain
        tune: Number of tuning samples
        chains: Number of MCMC chains
        target_accept: Target acceptance probability for NUTS sampler
        random_seed: Random seed for reproducibility
        
    Returns:
        InferenceData object containing posterior samples for:
            - mu_intercept, sigma_intercept: Group-level intercept hyperparameters
            - mu_slope, sigma_slope: Group-level slope hyperparameters
            - intercept: Block-specific intercepts (shape: [n_blocks])
            - slope: Block-specific slopes (shape: [n_blocks])
            - threshold: Block-specific thresholds (shape: [n_blocks])
    
    Example:
        >>> trials_df = pl.DataFrame({
        ...     "Intensity": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
        ...     "Result": [0, 0, 1, 0, 1, 1],
        ...     "Block": [0, 0, 0, 1, 1, 1],
        ... })
        >>> idata = fit(trials_df, draws=100, tune=100, chains=1)
        >>> summary = summarize_fit(idata)
    """
    # Prepare data
    if "Block" not in trials.columns:
        msg = "trials DataFrame must contain a 'Block' column"
        raise ValueError(msg)
    
    # Get unique blocks and create block index
    blocks = trials["Block"].unique().sort()
    n_blocks = len(blocks)
    block_idx_map = {block: idx for idx, block in enumerate(blocks.to_list())}
    
    # Create block indices for each trial
    block_idx = np.array([block_idx_map[b] for b in trials["Block"].to_list()])
    x = trials["Intensity"].to_numpy()
    y = trials["Result"].to_numpy()
    
    with pm.Model():
        # Hyperpriors (group-level parameters)
        mu_intercept = pm.Normal("mu_intercept", mu=0.0, sigma=2.5)
        sigma_intercept = pm.HalfNormal("sigma_intercept", sigma=2.5)
        
        mu_slope = pm.Normal("mu_slope", mu=0.0, sigma=2.5)
        sigma_slope = pm.HalfNormal("sigma_slope", sigma=2.5)
        
        # Block-level parameters (drawn from group distribution)
        intercept = pm.Normal(
            "intercept",
            mu=mu_intercept,
            sigma=sigma_intercept,
            shape=n_blocks,
        )
        slope = pm.Normal(
            "slope",
            mu=mu_slope,
            sigma=sigma_slope,
            shape=n_blocks,
        )
        
        # Likelihood (trial-level)
        logit_p = intercept[block_idx] + slope[block_idx] * x
        pm.Bernoulli("obs", logit_p=logit_p, observed=y)
        
        # Derived quantities
        threshold = pm.Deterministic("threshold", -intercept / slope)
        
        # Sample posterior
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=1,
            target_accept=target_accept,
            random_seed=random_seed,
            progressbar=False,
            return_inferencedata=True,
        )
        
        # Add block identifiers to inference data
        idata.posterior = idata.posterior.assign_coords(
            block=("intercept_dim_0", blocks.to_list()),
        )
    
    return idata


def summarize_fit(idata: az.InferenceData) -> dict[str, float | np.ndarray]:
    """Summarize posterior draws from hierarchical fit.
    
    Args:
        idata: InferenceData from hierarchical fit
        
    Returns:
        Dictionary with keys:
            - mu_intercept, sigma_intercept: Group-level intercept parameters
            - mu_slope, sigma_slope: Group-level slope parameters
            - intercept: Array of block-specific intercepts
            - slope: Array of block-specific slopes
            - threshold: Array of block-specific thresholds
    """
    var_names = [
        "mu_intercept",
        "sigma_intercept",
        "mu_slope",
        "sigma_slope",
        "intercept",
        "slope",
        "threshold",
    ]
    summary = cast(pd.DataFrame, az.summary(idata, var_names=var_names))
    
    result = {}
    
    # Extract scalar group-level parameters
    for param in ["mu_intercept", "sigma_intercept", "mu_slope", "sigma_slope"]:
        result[param] = float(summary.loc[param, "mean"])
    
    # Extract block-level arrays
    n_blocks = len([idx for idx in summary.index if idx.startswith("intercept[")])
    
    for param in ["intercept", "slope", "threshold"]:
        values = []
        for i in range(n_blocks):
            row_name = f"{param}[{i}]"
            values.append(float(summary.loc[row_name, "mean"]))
        result[param] = np.array(values)
    
    return result


def curve_credible_band(
    idata: az.InferenceData,
    x: np.ndarray | list[float],
    block_idx: int = 0,
    hdi_prob: float = 0.9,
) -> pl.DataFrame:
    """Compute credible band for psychometric curve of a specific block.
    
    Args:
        idata: InferenceData from hierarchical fit
        x: Array of intensity values to evaluate curve at
        block_idx: Index of the block to compute curve for
        hdi_prob: Probability mass for credible interval
        
    Returns:
        DataFrame with columns 'Intensity', 'lower', 'upper'
    """
    x_array = np.asarray(x, dtype=float)
    posterior = idata.posterior
    
    # Extract posterior samples for the specific block
    intercept = posterior["intercept"].isel(intercept_dim_0=block_idx)
    slope = posterior["slope"].isel(slope_dim_0=block_idx)
    
    # Stack chains and draws
    intercept = intercept.stack(sample=("chain", "draw")).values
    slope = slope.stack(sample=("chain", "draw")).values
    
    # Compute curve for all posterior samples
    logits = intercept[:, None] + slope[:, None] * x_array[None, :]
    probs = expit(logits)
    
    # Compute credible intervals
    alpha = (1.0 - hdi_prob) / 2.0
    lower = np.quantile(probs, alpha, axis=0)
    upper = np.quantile(probs, 1.0 - alpha, axis=0)
    
    return pl.DataFrame({"Intensity": x_array, "lower": lower, "upper": upper})


def from_points(
    points: pl.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int | None = None,
) -> az.InferenceData:
    """Fit hierarchical model using aggregated points data.
    
    This provides an alternative interface for fitting when you have points-level
    data (aggregated hit counts) rather than trial-level data. Internally converts
    to binomial likelihood.
    
    Args:
        points: DataFrame with 'Intensity', 'Hits', 'n trials', and 'Block'
        draws: Number of posterior samples per chain
        tune: Number of tuning samples
        chains: Number of MCMC chains
        target_accept: Target acceptance probability
        random_seed: Random seed
        
    Returns:
        InferenceData object with hierarchical posterior samples
    """
    # Prepare data
    if not {"Block", "Intensity", "Hits", "n trials"}.issubset(points.columns):
        msg = "points DataFrame must contain 'Block', 'Intensity', 'Hits', 'n trials'"
        raise ValueError(msg)
    
    blocks = points["Block"].unique().sort()
    n_blocks = len(blocks)
    block_idx_map = {block: idx for idx, block in enumerate(blocks.to_list())}
    
    block_idx = np.array([block_idx_map[b] for b in points["Block"].to_list()])
    x = points["Intensity"].to_numpy()
    hits = points["Hits"].to_numpy()
    n_trials = points["n trials"].to_numpy()
    
    with pm.Model():
        # Hyperpriors
        mu_intercept = pm.Normal("mu_intercept", mu=0.0, sigma=2.5)
        sigma_intercept = pm.HalfNormal("sigma_intercept", sigma=2.5)
        
        mu_slope = pm.Normal("mu_slope", mu=0.0, sigma=2.5)
        sigma_slope = pm.HalfNormal("sigma_slope", sigma=2.5)
        
        # Block-level parameters
        intercept = pm.Normal(
            "intercept",
            mu=mu_intercept,
            sigma=sigma_intercept,
            shape=n_blocks,
        )
        slope = pm.Normal(
            "slope",
            mu=mu_slope,
            sigma=sigma_slope,
            shape=n_blocks,
        )
        
        # Likelihood (binomial for aggregated data)
        logit_p = intercept[block_idx] + slope[block_idx] * x
        pm.Binomial("obs", n=n_trials, logit_p=logit_p, observed=hits)
        
        # Derived quantities
        threshold = pm.Deterministic("threshold", -intercept / slope)
        
        # Sample
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=1,
            target_accept=target_accept,
            random_seed=random_seed,
            progressbar=False,
            return_inferencedata=True,
        )
        
        idata.posterior = idata.posterior.assign_coords(
            block=("intercept_dim_0", blocks.to_list()),
        )
    
    return idata
