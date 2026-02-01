"""Hierarchical model for fitting psychometric functions across multiple blocks.

This module provides a unified interface for fitting psychometric functions
using hierarchical Bayesian models. Unlike independent block-level fits,
hierarchical models share information across blocks through group-level
(hyperprior) parameters, which improves parameter estimation especially
for blocks with sparse data.

The model uses a beta-binomial likelihood to account for overdispersion and
includes guess rate (γ) and lapse rate (λ) parameters for the full
psychometric function:

    ψ(x) = γ + (1 - γ - λ) * F(x; intercept, slope)

where F is the logistic function.

The hierarchical structure is:
    - Group level: μ_intercept, σ_intercept, μ_slope, σ_slope (hyperparameters)
                   μ_gamma, κ_gamma, μ_lambda, κ_lambda (hyperparameters for rates)
    - Block level: intercept[b] ~ Normal(μ_intercept, σ_intercept)
                   slope[b] ~ HalfNormal(σ_combined) where σ_combined² = μ_slope² + σ_slope²
                   gamma[b] ~ Beta(μ_gamma * κ_gamma, (1 - μ_gamma) * κ_gamma)
                   lambda[b] ~ Beta(μ_lambda * κ_lambda, (1 - μ_lambda) * κ_lambda)
    - Trial level: p = γ + (1 - γ - λ) * logistic(intercept + slope * Intensity)
                   Result ~ BetaBinomial(n, p * κ_obs, (1 - p) * κ_obs)

This approach consolidates both block-level and points-level fitting into a
single coherent framework while properly modeling lapse/guess behavior.
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
    """Fit hierarchical beta-binomial model to trial data across multiple blocks.

    This function fits a hierarchical Bayesian model where each block gets its own
    intercept, slope, guess rate (γ), and lapse rate (λ) parameters. These parameters
    are drawn from group-level distributions, allowing information sharing across
    blocks. The beta-binomial likelihood accounts for overdispersion.

    The psychometric function is:
        ψ(x) = γ + (1 - γ - λ) * logistic(intercept + slope * x)

    Data is standardized (mean-centered and scaled by std) before fitting to improve
    MCMC sampling efficiency.

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
            - mu_slope, sigma_slope: Group-level slope hyperparameters (slope is constrained positive)
            - mu_gamma, kappa_gamma: Group-level guess rate hyperparameters
            - mu_lambda, kappa_lambda: Group-level lapse rate hyperparameters
            - intercept: Block-specific intercepts (shape: [n_blocks])
            - slope: Block-specific slopes, always positive (shape: [n_blocks])
            - gamma: Block-specific guess rates (shape: [n_blocks])
            - lam: Block-specific lapse rates (shape: [n_blocks])
            - threshold: Block-specific thresholds (shape: [n_blocks])

        Standardization parameters are stored in idata.attrs:
            - x_mean: Mean of Intensity used for standardization
            - x_std: Std of Intensity used for standardization

    Example:
        >>> trials_df = pl.DataFrame({
        ...     "Intensity": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
        ...     "Result": [0, 0, 1, 0, 1, 1],
        ...     "Block": [0, 0, 0, 1, 1, 1],
        ... })
        >>> idata = fit(trials_df, draws=100, tune=100, chains=1)
        >>> summary = summarize_fit(idata)
    """
    if "Block" not in trials.columns:
        msg = "trials DataFrame must contain a 'Block' column"
        raise ValueError(msg)

    blocks = trials["Block"].unique().sort()
    n_blocks = len(blocks)
    block_idx_map = {block: idx for idx, block in enumerate(blocks.to_list())}

    block_idx = np.array([block_idx_map[b] for b in trials["Block"].to_list()])
    x_raw = trials["Intensity"].to_numpy()
    y = trials["Result"].to_numpy()

    # Standardize intensity for better MCMC sampling
    x_mean = float(np.mean(x_raw))
    x_std = float(np.std(x_raw))
    if x_std == 0:
        x_std = 1.0
    x = (x_raw - x_mean) / x_std

    with pm.Model():
        # Intercept/slope hyperpriors
        mu_intercept = pm.Normal("mu_intercept", mu=0.0, sigma=2.5)
        sigma_intercept = pm.HalfNormal("sigma_intercept", sigma=2.5)

        mu_slope = pm.HalfNormal("mu_slope", sigma=2.5)
        sigma_slope = pm.HalfNormal("sigma_slope", sigma=2.5)

        # Guess rate (γ) hyperpriors - typically small (0-10%)
        mu_gamma = pm.Beta("mu_gamma", alpha=1.0, beta=19.0)  # Prior mode near 0.05
        kappa_gamma = pm.Gamma("kappa_gamma", alpha=2.0, beta=0.1)  # Concentration

        # Lapse rate (λ) hyperpriors - typically small (0-10%)
        mu_lambda = pm.Beta("mu_lambda", alpha=1.0, beta=19.0)  # Prior mode near 0.05
        kappa_lambda = pm.Gamma("kappa_lambda", alpha=2.0, beta=0.1)  # Concentration

        # Block-level intercept and slope
        intercept = pm.Normal(
            "intercept",
            mu=mu_intercept,
            sigma=sigma_intercept,
            shape=n_blocks,
        )
        slope = pm.HalfNormal(
            "slope",
            sigma=pt.sqrt(mu_slope**2 + sigma_slope**2),
            shape=n_blocks,
        )

        # Block-level guess and lapse rates (Beta-parameterized by mean/concentration)
        gamma = pm.Beta(
            "gamma",
            alpha=mu_gamma * kappa_gamma,
            beta=(1 - mu_gamma) * kappa_gamma,
            shape=n_blocks,
        )
        lam = pm.Beta(
            "lam",
            alpha=mu_lambda * kappa_lambda,
            beta=(1 - mu_lambda) * kappa_lambda,
            shape=n_blocks,
        )

        # Psychometric function: ψ(x) = γ + (1 - γ - λ) * logistic(intercept + slope * x)
        logit_f = intercept[block_idx] + slope[block_idx] * x
        f_x = pm.math.sigmoid(logit_f)
        p = gamma[block_idx] + (1 - gamma[block_idx] - lam[block_idx]) * f_x

        # Bernoulli likelihood for individual trials
        pm.Bernoulli("obs", p=p, observed=y)

        # Threshold: value where psychometric function = 0.5
        # Solve: 0.5 = γ + (1 - γ - λ) * logistic(intercept + slope * x)
        # => logistic(intercept + slope * x) = (0.5 - γ) / (1 - γ - λ)
        # => intercept + slope * x = logit((0.5 - γ) / (1 - γ - λ))
        # => x = (logit((0.5 - γ) / (1 - γ - λ)) - intercept) / slope
        target_p = (0.5 - gamma) / (1 - gamma - lam)
        # Clamp to valid range for logit to avoid numerical issues
        target_p_clamped = pt.clip(target_p, 0.001, 0.999)
        threshold = pm.Deterministic(
            "threshold",
            (pt.log(target_p_clamped / (1 - target_p_clamped)) - intercept) / slope,
        )

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

    # Store standardization parameters for later unstandardization
    idata.attrs["x_mean"] = x_mean
    idata.attrs["x_std"] = x_std

    return idata


def summarize_fit(idata: az.InferenceData) -> dict[str, float | np.ndarray]:
    """Summarize posterior draws from hierarchical fit.

    Parameters are unstandardized back to the original intensity scale using
    the x_mean and x_std stored in idata.attrs.

    Args:
        idata: InferenceData from hierarchical fit

    Returns:
        Dictionary with keys:
            - mu_intercept, sigma_intercept: Group-level intercept parameters
            - mu_slope, sigma_slope: Group-level slope parameters
            - mu_gamma, kappa_gamma: Group-level guess rate parameters
            - mu_lambda, kappa_lambda: Group-level lapse rate parameters
            - intercept: Array of block-specific intercepts (original scale)
            - slope: Array of block-specific slopes (original scale)
            - gamma: Array of block-specific guess rates
            - lam: Array of block-specific lapse rates
            - threshold: Array of block-specific thresholds (original scale)
    """
    var_names = [
        "mu_intercept",
        "sigma_intercept",
        "mu_slope",
        "sigma_slope",
        "mu_gamma",
        "kappa_gamma",
        "mu_lambda",
        "kappa_lambda",
        "intercept",
        "slope",
        "gamma",
        "lam",
        "threshold",
    ]
    summary = cast("pd.DataFrame", az.summary(idata, var_names=var_names))

    # Get standardization parameters
    x_mean = idata.attrs.get("x_mean", 0.0)
    x_std = idata.attrs.get("x_std", 1.0)

    result = {}

    # Extract scalar group-level parameters
    scalar_params = [
        "mu_intercept",
        "sigma_intercept",
        "mu_slope",
        "sigma_slope",
        "mu_gamma",
        "kappa_gamma",
        "mu_lambda",
        "kappa_lambda",
    ]
    for param in scalar_params:
        result[param] = float(summary.loc[param, "mean"])

    # Extract block-level arrays
    n_blocks = len([idx for idx in summary.index if idx.startswith("intercept[")])

    intercepts_std = []
    slopes_std = []
    gammas = []
    lams = []
    for i in range(n_blocks):
        intercepts_std.append(float(summary.loc[f"intercept[{i}]", "mean"]))
        slopes_std.append(float(summary.loc[f"slope[{i}]", "mean"]))
        gammas.append(float(summary.loc[f"gamma[{i}]", "mean"]))
        lams.append(float(summary.loc[f"lam[{i}]", "mean"]))

    intercepts_std = np.array(intercepts_std)
    slopes_std = np.array(slopes_std)

    # Unstandardize: slope_orig = slope_std / x_std
    #                intercept_orig = intercept_std - slope_std * x_mean / x_std
    slopes_orig = slopes_std / x_std
    intercepts_orig = intercepts_std - slopes_std * x_mean / x_std

    # Thresholds in original scale
    thresholds = []
    for i in range(n_blocks):
        thresholds.append(float(summary.loc[f"threshold[{i}]", "mean"]))
    thresholds_std = np.array(thresholds)
    thresholds_orig = thresholds_std * x_std + x_mean

    result["intercept"] = intercepts_orig
    result["slope"] = slopes_orig
    result["gamma"] = np.array(gammas)
    result["lam"] = np.array(lams)
    result["threshold"] = thresholds_orig

    return result


def curve_credible_band(
    idata: az.InferenceData,
    x: np.ndarray | list[float],
    block_idx: int = 0,
    hdi_prob: float = 0.9,
) -> pl.DataFrame:
    """Compute credible band for psychometric curve of a specific block.

    The psychometric function is:
        ψ(x) = γ + (1 - γ - λ) * logistic(intercept + slope * x)

    The intensity values (x) should be in the original scale. They are
    standardized internally using the parameters stored in idata.attrs
    before computing probabilities with the standardized model parameters.

    Args:
        idata: InferenceData from hierarchical fit
        x: Array of intensity values in original scale
        block_idx: Index of the block to compute curve for
        hdi_prob: Probability mass for credible interval

    Returns:
        DataFrame with columns 'Intensity', 'lower', 'upper'
    """
    x_array = np.asarray(x, dtype=float)
    posterior = idata.posterior

    # Get standardization parameters
    x_mean = idata.attrs.get("x_mean", 0.0)
    x_std = idata.attrs.get("x_std", 1.0)

    # Standardize input x values
    x_std_array = (x_array - x_mean) / x_std

    # Extract posterior samples for the specific block (in standardized space)
    intercept = posterior["intercept"].isel(intercept_dim_0=block_idx)
    slope = posterior["slope"].isel(slope_dim_0=block_idx)
    gamma = posterior["gamma"].isel(gamma_dim_0=block_idx)
    lam = posterior["lam"].isel(lam_dim_0=block_idx)

    # Stack chains and draws
    intercept = intercept.stack(sample=("chain", "draw")).values
    slope = slope.stack(sample=("chain", "draw")).values
    gamma = gamma.stack(sample=("chain", "draw")).values
    lam = lam.stack(sample=("chain", "draw")).values

    # Compute curve for all posterior samples: ψ(x) = γ + (1 - γ - λ) * sigmoid(logit)
    logits = intercept[:, None] + slope[:, None] * x_std_array[None, :]
    f_x = expit(logits)
    probs = gamma[:, None] + (1 - gamma[:, None] - lam[:, None]) * f_x

    # Compute credible intervals
    alpha = (1.0 - hdi_prob) / 2.0
    lower = np.quantile(probs, alpha, axis=0)
    upper = np.quantile(probs, 1.0 - alpha, axis=0)

    # Return with original x values
    return pl.DataFrame({"Intensity": x_array, "lower": lower, "upper": upper})


def from_points(
    points: pl.DataFrame,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 2,
    target_accept: float = 0.9,
    random_seed: int | None = None,
) -> az.InferenceData:
    """Fit hierarchical beta-binomial model using aggregated points data.

    This provides an alternative interface for fitting when you have points-level
    data (aggregated hit counts) rather than trial-level data. Uses beta-binomial
    likelihood to account for overdispersion and includes guess rate (γ) and
    lapse rate (λ) parameters.

    The psychometric function is:
        ψ(x) = γ + (1 - γ - λ) * logistic(intercept + slope * x)

    Data is standardized (mean-centered and scaled by std) before fitting to improve
    MCMC sampling efficiency.

    Args:
        points: DataFrame with 'Intensity', 'Hits', 'n trials', and 'Block'
        draws: Number of posterior samples per chain
        tune: Number of tuning samples
        chains: Number of MCMC chains
        target_accept: Target acceptance probability
        random_seed: Random seed

    Returns:
        InferenceData object with hierarchical posterior samples including
        gamma (guess rate) and lam (lapse rate) parameters
    """
    if not {"Block", "Intensity", "Hits", "n trials"}.issubset(points.columns):
        msg = "points DataFrame must contain 'Block', 'Intensity', 'Hits', 'n trials'"
        raise ValueError(msg)

    blocks = points["Block"].unique().sort()
    n_blocks = len(blocks)
    block_idx_map = {block: idx for idx, block in enumerate(blocks.to_list())}

    block_idx = np.array([block_idx_map[b] for b in points["Block"].to_list()])
    x_raw = points["Intensity"].to_numpy()
    hits = points["Hits"].to_numpy()
    n_trials = points["n trials"].to_numpy()

    # Standardize intensity for better MCMC sampling
    x_mean = float(np.mean(x_raw))
    x_std = float(np.std(x_raw))
    if x_std == 0:
        x_std = 1.0
    x = (x_raw - x_mean) / x_std

    with pm.Model():
        # Intercept/slope hyperpriors
        mu_intercept = pm.Normal("mu_intercept", mu=0.0, sigma=2.5)
        sigma_intercept = pm.HalfNormal("sigma_intercept", sigma=2.5)

        mu_slope = pm.HalfNormal("mu_slope", sigma=2.5)
        sigma_slope = pm.HalfNormal("sigma_slope", sigma=2.5)

        # Guess rate (γ) hyperpriors
        mu_gamma = pm.Beta("mu_gamma", alpha=1.0, beta=19.0)
        kappa_gamma = pm.Gamma("kappa_gamma", alpha=2.0, beta=0.1)

        # Lapse rate (λ) hyperpriors
        mu_lambda = pm.Beta("mu_lambda", alpha=1.0, beta=19.0)
        kappa_lambda = pm.Gamma("kappa_lambda", alpha=2.0, beta=0.1)

        # Overdispersion parameter for beta-binomial
        kappa_obs = pm.Gamma("kappa_obs", alpha=2.0, beta=0.1)

        # Block-level intercept and slope
        intercept = pm.Normal(
            "intercept",
            mu=mu_intercept,
            sigma=sigma_intercept,
            shape=n_blocks,
        )
        slope = pm.HalfNormal(
            "slope",
            sigma=pt.sqrt(mu_slope**2 + sigma_slope**2),
            shape=n_blocks,
        )

        # Block-level guess and lapse rates
        gamma = pm.Beta(
            "gamma",
            alpha=mu_gamma * kappa_gamma,
            beta=(1 - mu_gamma) * kappa_gamma,
            shape=n_blocks,
        )
        lam = pm.Beta(
            "lam",
            alpha=mu_lambda * kappa_lambda,
            beta=(1 - mu_lambda) * kappa_lambda,
            shape=n_blocks,
        )

        # Psychometric function: ψ(x) = γ + (1 - γ - λ) * logistic(intercept + slope * x)
        logit_f = intercept[block_idx] + slope[block_idx] * x
        f_x = pm.math.sigmoid(logit_f)
        p = gamma[block_idx] + (1 - gamma[block_idx] - lam[block_idx]) * f_x

        # Beta-binomial likelihood for overdispersion
        alpha_obs = p * kappa_obs
        beta_obs = (1 - p) * kappa_obs
        pm.BetaBinomial(
            "obs",
            alpha=alpha_obs,
            beta=beta_obs,
            n=n_trials,
            observed=hits,
        )

        # Threshold calculation
        target_p = (0.5 - gamma) / (1 - gamma - lam)
        target_p_clamped = pt.clip(target_p, 0.001, 0.999)
        threshold = pm.Deterministic(
            "threshold",
            (pt.log(target_p_clamped / (1 - target_p_clamped)) - intercept) / slope,
        )

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

    # Store standardization parameters for later unstandardization
    idata.attrs["x_mean"] = x_mean
    idata.attrs["x_std"] = x_std

    return idata
