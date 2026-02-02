
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
    sampling_method: str = "constant_stimuli",
    random_seed: int | None = None,
) -> pl.DataFrame:
    """Generate n trials with outcomes.
    
    Args:
        n_trials: Number of trials per block
        options: Available intensity levels
        params: Psychometric function parameters
        n_blocks: Number of blocks to generate
        sampling_method: One of:
            - "constant_stimuli": Random sampling from fixed levels (classic MoCS)
            - "adaptive": Fisher Information-based adaptive sampling
            - "quest": QUEST/Psi Bayesian adaptive method
        random_seed: Random seed for reproducibility
        
    Returns:
        DataFrame with Block, Intensity, and Result columns
    """
    frames = []
    for i in range(n_blocks):
        block_seed = None if random_seed is None else (random_seed + i * 1000)
        
        if sampling_method == "adaptive":
            # Fisher Information-based adaptive sampling
            df = adaptive_sample(
                n_trials=n_trials,
                options=options,
                params=params,
                n_initial=max(5, min(n_trials // 5, len(options))),
                random_seed=block_seed,
            )
        elif sampling_method == "quest":
            # QUEST/Psi Bayesian adaptive sampling
            df = quest_sample(
                n_trials=n_trials,
                options=options,
                params=params,
                random_seed=block_seed,
            )
        else:
            # Default: Method of constant stimuli (random sampling)
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


def _fit_sigmoid_mle(
    x_obs: np.ndarray,
    hits: np.ndarray,
    n_trials: np.ndarray,
    x_range: tuple[float, float],
) -> tuple[float, float, float, float]:
    """Fit sigmoid parameters using maximum likelihood estimation.
    
    Fits a 2-parameter logistic function (threshold and slope) with fixed
    guess rate (gamma=0) and lapse rate (lambda=0) for speed.
    
    Args:
        x_obs: Observed intensity levels
        hits: Number of hits at each level
        n_trials: Number of trials at each level
        x_range: (min, max) of intensity range for prior bounds
        
    Returns:
        Tuple of (threshold_estimate, threshold_std, slope_estimate, slope_std)
    """
    from scipy.optimize import minimize
    from scipy.special import expit
    
    if len(x_obs) == 0:
        # No data - return prior centered in range
        mid = (x_range[0] + x_range[1]) / 2
        width = x_range[1] - x_range[0]
        return mid, width / 2, 1.0, 1.0
    
    # Negative log-likelihood for logistic regression
    def neg_log_likelihood(params: np.ndarray) -> float:
        threshold, slope = params
        # Ensure slope is positive
        slope = max(slope, 0.1)
        p = expit(slope * (x_obs - threshold))
        p = np.clip(p, 1e-10, 1 - 1e-10)
        # Binomial log-likelihood
        ll = np.sum(hits * np.log(p) + (n_trials - hits) * np.log(1 - p))
        return -ll
    
    # Initial guess: threshold at midpoint, slope = 1
    x0 = np.array([(x_range[0] + x_range[1]) / 2, 1.0])
    
    # Bounds
    bounds = [(x_range[0], x_range[1]), (0.1, 10.0)]
    
    try:
        result = minimize(neg_log_likelihood, x0, method='L-BFGS-B', bounds=bounds)
        threshold_est = result.x[0]
        slope_est = max(result.x[1], 0.1)
        
        # Estimate uncertainty from Hessian (Fisher Information)
        # For simplicity, use a rough approximation based on data
        n_total = np.sum(n_trials)
        threshold_std = max(1.0 / (slope_est * np.sqrt(n_total + 1)), 0.1)
        slope_std = max(slope_est / np.sqrt(n_total + 1), 0.1)
    except Exception:
        # Fallback to simple estimates
        threshold_est = (x_range[0] + x_range[1]) / 2
        threshold_std = (x_range[1] - x_range[0]) / 4
        slope_est = 1.0
        slope_std = 1.0
    
    return threshold_est, threshold_std, slope_est, slope_std


def _sigmoid_fisher_information(
    x: np.ndarray,
    threshold: float,
    slope: float,
) -> np.ndarray:
    """Calculate Fisher Information about threshold at each intensity.
    
    For a sigmoid, the Fisher Information about the threshold parameter
    is proportional to p(x) * (1 - p(x)) * slope^2, which is maximized
    at the threshold where p = 0.5.
    
    Args:
        x: Candidate intensities
        threshold: Current threshold estimate
        slope: Current slope estimate
        
    Returns:
        Fisher Information values at each intensity
    """
    from scipy.special import expit
    
    p = expit(slope * (x - threshold))
    # Fisher Information for threshold in logistic model
    fisher_info = slope**2 * p * (1 - p)
    return fisher_info


class QuestSampler:
    """QUEST/Psi adaptive sampling algorithm for threshold estimation.
    
    Maintains a Bayesian posterior distribution over threshold values and
    selects stimuli that maximize expected information gain (minimize
    expected posterior entropy).
    
    Based on Watson & Pelli (1983) QUEST and Kontsevich & Tyler (1999) Psi.
    """
    
    def __init__(
        self,
        options: np.ndarray,
        slope: float = 1.0,
        gamma: float = 0.0,
        lapse: float = 0.02,
        n_threshold_bins: int = 100,
    ):
        """Initialize QUEST sampler.
        
        Args:
            options: Available stimulus intensity levels
            slope: Assumed slope of psychometric function
            gamma: Guess rate (lower asymptote)
            lapse: Lapse rate (1 - upper asymptote)
            n_threshold_bins: Number of bins for threshold prior/posterior
        """
        from scipy.special import expit
        
        self.options = options
        self.slope = slope
        self.gamma = gamma
        self.lapse = lapse
        
        # Create threshold grid spanning the stimulus range
        x_min, x_max = options.min(), options.max()
        margin = (x_max - x_min) * 0.2
        self.threshold_grid = np.linspace(
            x_min - margin, x_max + margin, n_threshold_bins
        )
        
        # Initialize uniform prior over threshold
        self.log_prior = np.zeros(n_threshold_bins)
        self.log_prior -= np.log(n_threshold_bins)  # Normalize
        
        # Precompute psychometric function values for all (threshold, stimulus) pairs
        # Shape: (n_thresholds, n_stimuli)
        self._precompute_psi(expit)
    
    def _precompute_psi(self, expit):
        """Precompute p(correct | threshold, stimulus) for efficiency."""
        # Outer subtraction: options[j] - threshold_grid[i]
        diff = self.options[np.newaxis, :] - self.threshold_grid[:, np.newaxis]
        # Psychometric function: gamma + (1 - gamma - lapse) * sigmoid
        p_core = expit(self.slope * diff)
        self.psi = self.gamma + (1 - self.gamma - self.lapse) * p_core
        # Clip to avoid log(0)
        self.psi = np.clip(self.psi, 1e-10, 1 - 1e-10)
    
    def update(self, stimulus_idx: int, response: int):
        """Update posterior after observing a response.
        
        Args:
            stimulus_idx: Index of stimulus in options array
            response: 1 for hit/correct, 0 for miss/incorrect
        """
        # Likelihood: p(response | threshold)
        if response == 1:
            log_likelihood = np.log(self.psi[:, stimulus_idx])
        else:
            log_likelihood = np.log(1 - self.psi[:, stimulus_idx])
        
        # Bayes update in log space
        self.log_prior = self.log_prior + log_likelihood
        
        # Normalize (log-sum-exp trick for numerical stability)
        max_log = np.max(self.log_prior)
        self.log_prior = self.log_prior - max_log - np.log(
            np.sum(np.exp(self.log_prior - max_log))
        )
    
    def get_threshold_estimate(self) -> tuple[float, float]:
        """Get current threshold estimate and uncertainty.
        
        Returns:
            (mean_threshold, std_threshold)
        """
        posterior = np.exp(self.log_prior)
        mean = np.sum(posterior * self.threshold_grid)
        var = np.sum(posterior * (self.threshold_grid - mean) ** 2)
        return mean, np.sqrt(max(var, 1e-10))
    
    def select_stimulus(self, rng: np.random.Generator) -> int:
        """Select next stimulus that maximizes expected information gain.
        
        Uses the Psi method: selects stimulus that minimizes expected
        posterior entropy, which is equivalent to maximizing expected
        information gain about the threshold.
        
        Args:
            rng: Random number generator for tie-breaking
            
        Returns:
            Index of selected stimulus in options array
        """
        posterior = np.exp(self.log_prior)
        n_stimuli = len(self.options)
        
        expected_entropy = np.zeros(n_stimuli)
        
        for j in range(n_stimuli):
            # Probability of each response given current posterior
            # p(response=1) = sum_theta p(response=1|theta) * p(theta)
            p_hit = np.sum(self.psi[:, j] * posterior)
            p_miss = 1 - p_hit
            
            # Expected entropy after observing response at this stimulus
            entropy_if_hit = 0.0
            entropy_if_miss = 0.0
            
            if p_hit > 1e-10:
                # Posterior if hit: p(theta|hit) ∝ p(hit|theta) * p(theta)
                log_post_hit = self.log_prior + np.log(self.psi[:, j])
                max_log = np.max(log_post_hit)
                log_post_hit = log_post_hit - max_log - np.log(
                    np.sum(np.exp(log_post_hit - max_log))
                )
                post_hit = np.exp(log_post_hit)
                # Entropy: -sum p log p
                entropy_if_hit = -np.sum(post_hit * log_post_hit)
            
            if p_miss > 1e-10:
                # Posterior if miss
                log_post_miss = self.log_prior + np.log(1 - self.psi[:, j])
                max_log = np.max(log_post_miss)
                log_post_miss = log_post_miss - max_log - np.log(
                    np.sum(np.exp(log_post_miss - max_log))
                )
                post_miss = np.exp(log_post_miss)
                entropy_if_miss = -np.sum(post_miss * log_post_miss)
            
            # Expected entropy = p(hit) * H(post|hit) + p(miss) * H(post|miss)
            expected_entropy[j] = p_hit * entropy_if_hit + p_miss * entropy_if_miss
        
        # Select stimulus with minimum expected entropy (maximum info gain)
        # Add small noise to break ties
        expected_entropy = expected_entropy + rng.uniform(0, 1e-10, n_stimuli)
        return int(np.argmin(expected_entropy))


def quest_sample(
    n_trials: int,
    options: list[float],
    params: dict[str, float],
    random_seed: int | None = None,
) -> pl.DataFrame:
    """Sample trials using the QUEST/Psi adaptive algorithm.
    
    QUEST (Quick Estimation by Sequential Testing) maintains a Bayesian
    posterior over threshold values and selects each stimulus to maximize
    expected information gain about the threshold.
    
    This is a classic algorithm from Watson & Pelli (1983), extended by
    Kontsevich & Tyler (1999) as the Psi method.
    
    Args:
        n_trials: Number of trials to generate
        options: Available intensity levels to sample from
        params: True psychometric function parameters (for generating outcomes)
        random_seed: Random seed for reproducibility
        
    Returns:
        DataFrame with 'Intensity' and 'Result' columns
    """
    rng = np.random.default_rng(random_seed)
    options_arr = np.array(options)
    
    # Initialize QUEST with assumed slope (can be estimated from data if needed)
    # Use a reasonable default slope, or could be parameterized
    assumed_slope = params.get("k", 1.0)
    assumed_gamma = params.get("gamma", 0.0)
    assumed_lapse = params.get("lambda", 0.02)
    
    quest = QuestSampler(
        options=options_arr,
        slope=assumed_slope,
        gamma=assumed_gamma,
        lapse=assumed_lapse,
    )
    
    intensities: list[float] = []
    results: list[int] = []
    
    for _ in range(n_trials):
        # Select stimulus using Psi criterion
        stim_idx = quest.select_stimulus(rng)
        intensity = float(options_arr[stim_idx])
        
        # Generate outcome from true psychometric function
        result = int(rng.random() <= psi(intensity, params))
        
        # Update QUEST posterior
        quest.update(stim_idx, result)
        
        intensities.append(intensity)
        results.append(result)
    
    return pl.DataFrame({"Intensity": intensities, "Result": results})


def adaptive_sample(
    n_trials: int,
    options: list[float],
    params: dict[str, float],
    n_initial: int = 5,
    random_seed: int | None = None,
) -> pl.DataFrame:
    """Sample trials using Fisher Information-based adaptive sampling.
    
    This algorithm exploits knowledge that the psychometric function is a
    sigmoid. It adaptively selects stimulus intensities to efficiently
    estimate the threshold by:
    
    1. Starting with a few samples spread across the intensity range
    2. Fitting a sigmoid (logistic) model to estimate threshold
    3. Sampling where Fisher Information about threshold is highest
       (which is near the estimated threshold for sigmoids)
    4. Adding exploration to avoid getting stuck
    
    This is more efficient than GP-based methods because it uses the
    known parametric form of the psychometric function.
    
    Args:
        n_trials: Total number of trials to generate
        options: Available intensity levels to sample from
        params: True psychometric function parameters (for generating outcomes)
        n_initial: Number of initial exploratory trials
        random_seed: Random seed for reproducibility
        
    Returns:
        DataFrame with 'Intensity' and 'Result' columns
    """
    rng = np.random.default_rng(random_seed)
    options_arr = np.array(options)
    x_range = (float(options_arr.min()), float(options_arr.max()))
    
    intensities: list[float] = []
    results: list[int] = []
    
    # Phase 1: Initial sampling - spread across the range
    n_init = min(n_initial, n_trials, len(options))
    if n_init > 0:
        # Select evenly spaced initial points
        init_indices = np.linspace(0, len(options) - 1, n_init, dtype=int)
        init_intensities = options_arr[init_indices].tolist()
        
        for intensity in init_intensities:
            result = int(rng.random() <= psi(intensity, params))
            intensities.append(float(intensity))
            results.append(result)
    
    # Phase 2: Adaptive sampling using Fisher Information
    remaining_trials = n_trials - len(intensities)
    
    for trial_idx in range(remaining_trials):
        # Aggregate observed data
        obs_df = pl.DataFrame({"Intensity": intensities, "Result": results})
        agg = obs_df.group_by("Intensity").agg([
            pl.sum("Result").alias("hits"),
            pl.len().alias("n"),
        ])
        x_obs = agg["Intensity"].to_numpy()
        hits = agg["hits"].to_numpy()
        n_obs = agg["n"].to_numpy()
        
        # Fit sigmoid to current data
        threshold_est, threshold_std, slope_est, _ = _fit_sigmoid_mle(
            x_obs, hits, n_obs, x_range
        )
        
        # Calculate Fisher Information at each candidate intensity
        fisher_info = _sigmoid_fisher_information(options_arr, threshold_est, slope_est)
        
        # Penalize already-sampled locations (diminishing returns)
        sampling_value = fisher_info.copy()
        for i, x_cand in enumerate(options_arr):
            match_idx = np.where(np.abs(x_obs - x_cand) < 1e-10)[0]
            if len(match_idx) > 0:
                n_at_loc = n_obs[match_idx[0]]
                # Diminishing returns: sqrt scaling
                sampling_value[i] = sampling_value[i] / np.sqrt(1 + n_at_loc)
        
        # Add exploration bonus based on threshold uncertainty
        # Sample more broadly when uncertain about threshold location
        exploration_weight = min(threshold_std / (x_range[1] - x_range[0]), 0.5)
        
        # Distance from estimated threshold (normalized)
        dist_from_threshold = np.abs(options_arr - threshold_est)
        max_dist = max(dist_from_threshold.max(), 1e-10)
        
        # Exploration term: prefer points we haven't sampled much
        # that are within reasonable range of threshold uncertainty
        within_uncertainty = dist_from_threshold < 2 * threshold_std
        exploration_bonus = np.zeros_like(sampling_value)
        for i, x_cand in enumerate(options_arr):
            match_idx = np.where(np.abs(x_obs - x_cand) < 1e-10)[0]
            if len(match_idx) == 0:
                # Unsampled point - bonus if within uncertainty range
                if within_uncertainty[i]:
                    exploration_bonus[i] = 0.3
                else:
                    exploration_bonus[i] = 0.1 * (1 - dist_from_threshold[i] / max_dist)
        
        # Combine exploitation (Fisher Info) and exploration
        acquisition = (1 - exploration_weight) * sampling_value + exploration_weight * exploration_bonus
        
        # Add small noise to break ties
        acquisition = acquisition + rng.uniform(0, 1e-6, len(acquisition))
        
        # Select intensity with maximum acquisition value
        best_idx = np.argmax(acquisition)
        next_intensity = float(options_arr[best_idx])
        
        # Generate outcome
        next_result = int(rng.random() <= psi(next_intensity, params))
        
        intensities.append(next_intensity)
        results.append(next_result)
    
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
