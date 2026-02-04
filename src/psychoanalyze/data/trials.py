
"""Functions for data manipulations at the trial level."""
import json
import random
from pathlib import Path
from typing import TypedDict

import arviz as az
import numpy as np
import polars as pl

from psychoanalyze.data import subject as subject_utils
from psychoanalyze.features import is_adaptive_sampling_enabled


class AdaptiveSamplingDisabledError(Exception):
    """Raised when using adaptive sampling without enabling the feature flag."""

    def __init__(self, method: str = "boed") -> None:
        """Initialize with the method name that was attempted."""
        super().__init__(
            f"Adaptive sampling method '{method}' is disabled. "
            "Set PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING=1 to enable.",
        )

data_path = Path("data/trials.csv")

codes = {0: "Miss", 1: "Hit"}
Trial = TypedDict("Trial", {"Result": bool, "Stimulus Magnitude": float})


def generate_trial_index(n_trials: int, options: list[float]) -> list[float]:
    """Generate n trials (no outcomes)."""
    return [random.choice(options) for _ in range(n_trials)]


def sample_trials(trials_ix: list[float], params: dict[str, float]) -> pl.DataFrame:
    """Sample trials from a given index."""
    results = [int(random.random() <= psi(x, params)) for x in trials_ix]
    return pl.DataFrame({
        "Trial": list(range(len(trials_ix))),
        "Intensity": trials_ix,
        "Result": results,
    })


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
            - "boed": Bayesian Optimal Experimental Design (requires feature flag)
        random_seed: Random seed for reproducibility
        
    Returns:
        DataFrame with Trial, Block, Intensity, and Result columns.
        Trial column preserves the order in which samples were taken within each block.
        
    Raises:
        AdaptiveSamplingDisabledError: If sampling_method is "boed" but the
            PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING feature flag is not set.
    """
    # Check feature flag for adaptive sampling methods
    if sampling_method == "boed" and not is_adaptive_sampling_enabled():
        raise AdaptiveSamplingDisabledError(sampling_method)

    frames = []
    for i in range(n_blocks):
        block_seed = None if random_seed is None else (random_seed + i * 1000)

        if sampling_method == "boed":
            # Bayesian Optimal Experimental Design
            df, _ = boed_sample(
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
    return pl.concat(frames).select(["Trial", "Block", "Intensity", "Result"])


def generate_multi_subject(
    n_trials: int,
    options: list[float],
    params: dict[str, float],
    n_blocks: int,
    n_subjects: int = 1,
    use_random_params: bool = False,
    random_seed: int | None = None,
    sampling_method: str = "constant_stimuli",
) -> tuple[pl.DataFrame, dict[tuple[str, int], dict[str, float]]]:
    """Generate trials for multiple subjects and return both data and ground truth parameters.

    This function extends `generate()` to support multiple subjects, each with
    multiple blocks. It can either use fixed parameters or sample random parameters
    from the hierarchical model priors for each block.

    Args:
        n_trials: Number of trials per block
        options: Available intensity levels to sample from
        params: Psychometric function parameters (used if use_random_params=False)
        n_blocks: Number of blocks per subject
        n_subjects: Number of subjects to simulate
        use_random_params: If True, sample parameters from hierarchical priors
            for each block. If False, use provided params with small random variation.
        random_seed: Random seed for reproducibility
        sampling_method: Sampling method passed to generate():
            - "constant_stimuli": Random sampling from fixed levels
            - "boed": Bayesian Optimal Experimental Design (requires feature flag)

    Returns:
        Tuple of (trials_df, ground_truth_params_map) where:
            - trials_df: DataFrame with Subject, Block, Trial, Intensity, Result columns
            - ground_truth_params_map: Dict mapping (subject_id, block_id) tuples to
              the parameters used to generate that block's data

    Raises:
        AdaptiveSamplingDisabledError: If sampling_method is "boed" but the
            PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING feature flag is not set.

    Example:
        >>> from psychoanalyze.data.points import generate_index
        >>> options = generate_index(7, [-4.0, 4.0])
        >>> trials_df, params_map = generate_multi_subject(
        ...     n_trials=50,
        ...     options=options,
        ...     params={},
        ...     n_blocks=2,
        ...     n_subjects=3,
        ...     use_random_params=True,
        ...     random_seed=42,
        ... )
        >>> trials_df.columns
        ['Subject', 'Block', 'Trial', 'Intensity', 'Result']
        >>> len(params_map)  # 3 subjects * 2 blocks
        6
    """
    from psychoanalyze.data.hierarchical import sample_params_from_priors

    frames = []
    ground_truth_params_map: dict[tuple[str, int], dict[str, float]] = {}
    rng = np.random.default_rng(random_seed)

    for subject_idx in range(n_subjects):
        # Generate subject ID: A, B, C, ... Z, S26, S27, ...
        subject_id = (
            chr(ord("A") + subject_idx) if subject_idx < 26 else f"S{subject_idx}"
        )

        for block_id in range(n_blocks):
            # Generate parameters for this block
            if use_random_params:
                block_seed = (
                    None
                    if random_seed is None
                    else (random_seed + subject_idx * 1000 + block_id)
                )
                block_params = sample_params_from_priors(block_seed)
            else:
                # Use provided params with random variation per block
                block_params = params.copy()
                block_params["x_0"] = params["x_0"] + rng.normal(0, 0.5)

            ground_truth_params_map[(subject_id, block_id)] = block_params

            # Generate trials for this block using specified sampling method
            trial_seed = (
                None
                if random_seed is None
                else (random_seed + subject_idx * 10000 + block_id * 100)
            )
            block_trials = generate(
                n_trials=n_trials,
                options=options,
                params=block_params,
                n_blocks=1,
                sampling_method=sampling_method,
                random_seed=trial_seed,
            )
            block_trials = block_trials.with_columns(
                pl.lit(subject_id).alias("Subject"),
                pl.lit(block_id).alias("Block"),
            )
            frames.append(block_trials)

    trials_df = pl.concat(frames) if frames else pl.DataFrame()
    return trials_df, ground_truth_params_map


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


def load_sample(data_dir: Path | None = None) -> pl.DataFrame:
    """Load sample experimental data for demos and testing.

    Loads the bundled sample dataset and transforms it to the standard format
    with columns: Subject, Block, Intensity, Result.

    The sample data is from psychophysics experiments and includes multiple
    subjects and blocks with varying parameters.

    Args:
        data_dir: Optional path to data directory. If None, uses the default
            location relative to the package installation.

    Returns:
        DataFrame with columns: Subject, Block, Intensity, Result

    Example:
        >>> trials_df = load_sample()
        >>> trials_df.columns
        ['Subject', 'Block', 'Intensity', 'Result']
        >>> trials_df["Subject"].n_unique()  # Number of subjects
        3
    """
    if data_dir is None:
        # Default to package's data directory
        data_dir = Path(__file__).parent.parent.parent.parent / "data"

    sample_path = data_dir / "trials.csv"

    if not sample_path.exists():
        msg = f"Sample data not found at {sample_path}"
        raise FileNotFoundError(msg)

    df = pl.read_csv(sample_path)

    # Transform to expected format: Subject, Block, Intensity, Result
    # Create unique block key from Date and Amp2 (reference amplitude)
    df = df.with_columns(
        (pl.col("Date").cast(pl.Utf8) + "_" + pl.col("Amp2").cast(pl.Utf8)).alias(
            "block_key",
        ),
    )
    # Convert block_key to sequential block numbers
    df = df.with_columns(
        pl.col("block_key").rank("dense").cast(pl.Int64).alias("Block") - 1,
    )
    # Amp1 is the test stimulus intensity
    df = df.with_columns(pl.col("Amp1").alias("Intensity"))
    # Ensure Result is binary integer
    df = df.with_columns((pl.col("Result") == 1).cast(pl.Int64).alias("Result"))
    # Select standard columns
    df = df.select(["Subject", "Block", "Intensity", "Result"])

    return df


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


class BOEDSampler:
    """Bayesian Optimal Experimental Design sampler for psychometric functions.
    
    Maintains a full Bayesian posterior over all model parameters (threshold, slope,
    gamma, lambda) and selects stimuli that maximize expected information gain.
    
    Unlike QUEST which only estimates threshold with a fixed slope, BOED jointly
    estimates all parameters, providing a more complete picture of uncertainty.
    
    Uses a grid-based approximation for computational efficiency while capturing
    the full joint posterior structure.
    """

    def __init__(
        self,
        options: np.ndarray,
        n_threshold_bins: int = 50,
        n_slope_bins: int = 20,
        n_gamma_bins: int = 10,
        n_lambda_bins: int = 10,
    ):
        """Initialize BOED sampler.
        
        Args:
            options: Available stimulus intensity levels
            n_threshold_bins: Number of bins for threshold parameter
            n_slope_bins: Number of bins for slope parameter
            n_gamma_bins: Number of bins for gamma (guess rate)
            n_lambda_bins: Number of bins for lambda (lapse rate)
        """
        from scipy.special import expit

        self.options = options
        self.n_threshold = n_threshold_bins
        self.n_slope = n_slope_bins
        self.n_gamma = n_gamma_bins
        self.n_lambda = n_lambda_bins

        # Create parameter grids
        x_min, x_max = options.min(), options.max()
        margin = (x_max - x_min) * 0.3
        self.threshold_grid = np.linspace(x_min - margin, x_max + margin, n_threshold_bins)
        self.slope_grid = np.linspace(0.1, 5.0, n_slope_bins)  # Positive slopes
        self.gamma_grid = np.linspace(0.0, 0.2, n_gamma_bins)  # Guess rate 0-20%
        self.lambda_grid = np.linspace(0.0, 0.2, n_lambda_bins)  # Lapse rate 0-20%

        # Total number of parameter combinations
        self.n_params = n_threshold_bins * n_slope_bins * n_gamma_bins * n_lambda_bins

        # Initialize log prior (uniform, but could be informed by hierarchical model)
        self.log_prior = np.zeros(self.n_params) - np.log(self.n_params)

        # Store trial history for posterior extraction
        self.trial_history: list[tuple[float, int]] = []

        # Precompute psi for all parameter combinations and stimuli
        self._precompute_psi(expit)

    def _param_idx(self, t: int, s: int, g: int, l: int) -> int:
        """Convert multi-dimensional indices to flat index."""
        return (
            t * (self.n_slope * self.n_gamma * self.n_lambda)
            + s * (self.n_gamma * self.n_lambda)
            + g * self.n_lambda
            + l
        )

    def _precompute_psi(self, expit):
        """Precompute p(correct | params, stimulus) for all combinations."""
        n_stimuli = len(self.options)

        # Create meshgrid for all parameters
        T, S, G, L = np.meshgrid(
            self.threshold_grid, self.slope_grid,
            self.gamma_grid, self.lambda_grid,
            indexing="ij",
        )

        # Reshape to (n_params, 1) for broadcasting with options
        T_flat = T.ravel()[:, np.newaxis]  # (n_params, 1)
        S_flat = S.ravel()[:, np.newaxis]
        G_flat = G.ravel()[:, np.newaxis]
        L_flat = L.ravel()[:, np.newaxis]

        # options has shape (n_stimuli,), broadcast to (n_params, n_stimuli)
        logits = S_flat * (self.options[np.newaxis, :] - T_flat)
        f_x = expit(logits)

        # Psychometric function: gamma + (1 - gamma - lambda) * sigmoid
        self.psi = G_flat + (1 - G_flat - L_flat) * f_x
        self.psi = np.clip(self.psi, 1e-10, 1 - 1e-10)

    def update(self, stimulus_idx: int, response: int):
        """Update posterior after observing a response.
        
        Args:
            stimulus_idx: Index of stimulus in options array
            response: 1 for hit/correct, 0 for miss/incorrect
        """
        intensity = float(self.options[stimulus_idx])
        self.trial_history.append((intensity, response))

        # Likelihood: p(response | params)
        if response == 1:
            log_likelihood = np.log(self.psi[:, stimulus_idx])
        else:
            log_likelihood = np.log(1 - self.psi[:, stimulus_idx])

        # Bayes update in log space
        self.log_prior = self.log_prior + log_likelihood

        # Normalize (log-sum-exp trick)
        max_log = np.max(self.log_prior)
        self.log_prior = self.log_prior - max_log - np.log(
            np.sum(np.exp(self.log_prior - max_log)),
        )

    def get_posterior(self) -> np.ndarray:
        """Get the current posterior distribution (normalized probabilities)."""
        return np.exp(self.log_prior)

    def get_marginal_threshold(self) -> tuple[np.ndarray, np.ndarray]:
        """Get marginal posterior over threshold parameter.
        
        Returns:
            (threshold_grid, marginal_probs)
        """
        # Reshape posterior to 4D and sum over slope, gamma, lambda dimensions
        posterior_4d = self.get_posterior().reshape(
            self.n_threshold, self.n_slope, self.n_gamma, self.n_lambda,
        )
        marginal = posterior_4d.sum(axis=(1, 2, 3))
        return self.threshold_grid, marginal

    def get_marginal_slope(self) -> tuple[np.ndarray, np.ndarray]:
        """Get marginal posterior over slope parameter."""
        # Reshape posterior to 4D and sum over threshold, gamma, lambda dimensions
        posterior_4d = self.get_posterior().reshape(
            self.n_threshold, self.n_slope, self.n_gamma, self.n_lambda,
        )
        marginal = posterior_4d.sum(axis=(0, 2, 3))
        return self.slope_grid, marginal

    def get_estimates(self) -> dict[str, tuple[float, float]]:
        """Get posterior mean and std for all parameters.
        
        Returns:
            Dictionary with keys 'threshold', 'slope', 'gamma', 'lambda',
            each containing (mean, std) tuple.
        """
        # Reshape posterior to 4D for efficient marginalization
        posterior_4d = self.get_posterior().reshape(
            self.n_threshold, self.n_slope, self.n_gamma, self.n_lambda,
        )

        results = {}

        # Threshold (dim 0)
        marginal_t = posterior_4d.sum(axis=(1, 2, 3))
        mean_t = np.sum(marginal_t * self.threshold_grid)
        var_t = np.sum(marginal_t * (self.threshold_grid - mean_t) ** 2)
        results["threshold"] = (mean_t, np.sqrt(max(var_t, 1e-10)))

        # Slope (dim 1)
        marginal_s = posterior_4d.sum(axis=(0, 2, 3))
        mean_s = np.sum(marginal_s * self.slope_grid)
        var_s = np.sum(marginal_s * (self.slope_grid - mean_s) ** 2)
        results["slope"] = (mean_s, np.sqrt(max(var_s, 1e-10)))

        # Gamma (dim 2)
        marginal_g = posterior_4d.sum(axis=(0, 1, 3))
        mean_g = np.sum(marginal_g * self.gamma_grid)
        var_g = np.sum(marginal_g * (self.gamma_grid - mean_g) ** 2)
        results["gamma"] = (mean_g, np.sqrt(max(var_g, 1e-10)))

        # Lambda (dim 3)
        marginal_l = posterior_4d.sum(axis=(0, 1, 2))
        mean_l = np.sum(marginal_l * self.lambda_grid)
        var_l = np.sum(marginal_l * (self.lambda_grid - mean_l) ** 2)
        results["lambda"] = (mean_l, np.sqrt(max(var_l, 1e-10)))

        return results

    def select_stimulus(self, rng: np.random.Generator) -> int:
        """Select next stimulus that maximizes expected information gain.
        
        Computes the expected reduction in posterior entropy for each possible
        stimulus choice and selects the one that maximizes information gain.
        
        Args:
            rng: Random number generator for tie-breaking
            
        Returns:
            Index of selected stimulus in options array
        """
        posterior = self.get_posterior()
        n_stimuli = len(self.options)

        # Current entropy
        current_entropy = -np.sum(posterior * self.log_prior)

        expected_entropy = np.zeros(n_stimuli)

        for j in range(n_stimuli):
            # Probability of hit given current posterior
            p_hit = np.sum(self.psi[:, j] * posterior)
            p_miss = 1 - p_hit

            # Expected entropy after observing response at this stimulus
            entropy_if_hit = 0.0
            entropy_if_miss = 0.0

            if p_hit > 1e-10:
                # Posterior if hit: p(params|hit) ∝ p(hit|params) * p(params)
                log_post_hit = self.log_prior + np.log(self.psi[:, j])
                max_log = np.max(log_post_hit)
                log_post_hit_norm = log_post_hit - max_log - np.log(
                    np.sum(np.exp(log_post_hit - max_log)),
                )
                post_hit = np.exp(log_post_hit_norm)
                entropy_if_hit = -np.sum(post_hit * log_post_hit_norm)

            if p_miss > 1e-10:
                # Posterior if miss
                log_post_miss = self.log_prior + np.log(1 - self.psi[:, j])
                max_log = np.max(log_post_miss)
                log_post_miss_norm = log_post_miss - max_log - np.log(
                    np.sum(np.exp(log_post_miss - max_log)),
                )
                post_miss = np.exp(log_post_miss_norm)
                entropy_if_miss = -np.sum(post_miss * log_post_miss_norm)

            # Expected entropy = p(hit) * H(post|hit) + p(miss) * H(post|miss)
            expected_entropy[j] = p_hit * entropy_if_hit + p_miss * entropy_if_miss

        # Select stimulus with minimum expected entropy (maximum info gain)
        # Add small noise to break ties
        expected_entropy = expected_entropy + rng.uniform(0, 1e-10, n_stimuli)
        return int(np.argmin(expected_entropy))

    def get_expected_curve(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Get the expected psychometric curve with credible intervals.
        
        Returns:
            (x_values, mean_curve, lower_95, upper_95)
        """
        from scipy.special import expit

        posterior = self.get_posterior()
        x_fine = np.linspace(self.options.min(), self.options.max(), 100)
        n_x = len(x_fine)

        # Vectorized computation of all curves
        # Create meshgrid for all parameters
        T, S, G, L = np.meshgrid(
            self.threshold_grid, self.slope_grid,
            self.gamma_grid, self.lambda_grid,
            indexing="ij",
        )

        # Reshape to (n_params, 1) for broadcasting
        T_flat = T.ravel()[:, np.newaxis]  # (n_params, 1)
        S_flat = S.ravel()[:, np.newaxis]
        G_flat = G.ravel()[:, np.newaxis]
        L_flat = L.ravel()[:, np.newaxis]

        # Compute curves for all parameter combinations at once
        # x_fine has shape (n_x,), broadcast to (n_params, n_x)
        logits = S_flat * (x_fine[np.newaxis, :] - T_flat)
        f_x = expit(logits)
        curves = G_flat + (1 - G_flat - L_flat) * f_x  # (n_params, n_x)

        # Weighted mean curve
        mean_curve = np.sum(posterior[:, np.newaxis] * curves, axis=0)

        # For credible intervals, use weighted percentiles
        # Sort curves at each x position and find weighted quantiles
        sorted_indices = np.argsort(curves, axis=0)

        lower = np.zeros(n_x)
        upper = np.zeros(n_x)

        for i in range(n_x):
            sorted_probs = posterior[sorted_indices[:, i]]
            sorted_vals = curves[sorted_indices[:, i], i]
            cumsum = np.cumsum(sorted_probs)

            # Find 2.5% and 97.5% quantiles
            lower_idx = np.searchsorted(cumsum, 0.025)
            upper_idx = np.searchsorted(cumsum, 0.975)

            lower[i] = sorted_vals[min(lower_idx, len(sorted_vals) - 1)]
            upper[i] = sorted_vals[min(upper_idx, len(sorted_vals) - 1)]

        return x_fine, mean_curve, lower, upper


def boed_sample(
    n_trials: int,
    options: list[float],
    params: dict[str, float],
    random_seed: int | None = None,
) -> tuple[pl.DataFrame, BOEDSampler]:
    """Sample trials using Bayesian Optimal Experimental Design.
    
    BOED maintains a full Bayesian posterior over all psychometric function
    parameters (threshold, slope, gamma, lambda) and selects each stimulus
    to maximize expected information gain.
    
    Unlike QUEST which only estimates threshold, BOED jointly estimates all
    parameters, providing a more complete picture of uncertainty.
    
    Note:
        This function requires the PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING
        environment variable to be set to "1" or "true".
    
    Args:
        n_trials: Number of trials to generate
        options: Available intensity levels to sample from
        params: True psychometric function parameters (for generating outcomes)
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuple of (DataFrame with trials, BOEDSampler with final posterior)
        
    Raises:
        AdaptiveSamplingDisabledError: If the PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING
            feature flag is not set.
    """
    if not is_adaptive_sampling_enabled():
        raise AdaptiveSamplingDisabledError("boed")

    rng = np.random.default_rng(random_seed)
    options_arr = np.array(options)

    # Initialize BOED sampler
    boed = BOEDSampler(options=options_arr)

    intensities: list[float] = []
    results: list[int] = []

    for _ in range(n_trials):
        # Select stimulus using BOED criterion (max expected info gain)
        stim_idx = boed.select_stimulus(rng)
        intensity = float(options_arr[stim_idx])

        # Generate outcome from true psychometric function
        result = int(rng.random() <= psi(intensity, params))

        # Update BOED posterior
        boed.update(stim_idx, result)

        intensities.append(intensity)
        results.append(result)

    df = pl.DataFrame({
        "Trial": list(range(len(intensities))),
        "Intensity": intensities,
        "Result": results,
    })

    return df, boed


def boed_sample_sequential(
    options: list[float],
    params: dict[str, float],
    random_seed: int | None = None,
) -> BOEDSampler:
    """Create a BOED sampler for sequential trial-by-trial sampling.
    
    This function returns a sampler that can be stepped through one trial
    at a time, useful for visualizing the posterior evolution.
    
    Note:
        This function requires the PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING
        environment variable to be set to "1" or "true".
    
    Args:
        options: Available intensity levels to sample from
        params: True psychometric function parameters (for generating outcomes)
        random_seed: Random seed for reproducibility
        
    Returns:
        BOEDSampler instance ready for sequential sampling
        
    Raises:
        AdaptiveSamplingDisabledError: If the PSYCHOANALYZE_ENABLE_ADAPTIVE_SAMPLING
            feature flag is not set.
    """
    if not is_adaptive_sampling_enabled():
        raise AdaptiveSamplingDisabledError("boed")

    options_arr = np.array(options)
    return BOEDSampler(options=options_arr)




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
    # Should not happen with current implementation, but handle gracefully  # noqa: RET503
    return {
        "Threshold": float(hier_summary["threshold"]),
        "Slope": float(hier_summary["slope"]),
    }
