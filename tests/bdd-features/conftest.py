"""Shared fixtures for BDD simulation tests."""

import time
from dataclasses import dataclass

import numpy as np
import polars as pl
import pytest
from scipy.stats import logistic


@dataclass
class PsychometricParams:
    """Parameters defining a psychometric function."""

    threshold: float
    slope: float
    guess_rate: float = 0.0
    lapse_rate: float = 0.0

    @property
    def logistic_cdf(self):
        """Return the logistic CDF function with these parameters."""
        return lambda x: logistic.cdf(x, loc=self.threshold, scale=1 / self.slope)

    def psi(self, x: np.ndarray) -> np.ndarray:
        """Calculate psychometric function values."""
        p = self.logistic_cdf(x)
        return self.guess_rate + (1 - self.guess_rate - self.lapse_rate) * p


@pytest.fixture
def psychometric_function():
    """Standard psychometric function with threshold 50 and slope 0.1."""
    return PsychometricParams(threshold=50, slope=0.1)


@pytest.fixture
def stimulus_range():
    """Stimulus intensity range from 0 to 100."""
    return (0, 100)


@pytest.fixture
def empty_trials():
    """Empty trial dataset."""
    return pl.DataFrame(
        {
            "Intensity": pl.Series([], dtype=pl.Float64),
            "Result": pl.Series([], dtype=pl.UInt8),
            "Trial": pl.Series([], dtype=pl.UInt32),
        }
    )


@pytest.fixture
def online_simulation_session(psychometric_function, stimulus_range):
    """Fixture for managing an online simulation session."""

    class OnlineSimulation:
        def __init__(self, params: PsychometricParams, stim_range: tuple):
            self.params = params
            self.stim_range = stim_range
            self.trials = pl.DataFrame(
                {
                    "Intensity": pl.Series([], dtype=pl.Float64),
                    "Result": pl.Series([], dtype=pl.UInt8),
                    "Trial": pl.Series([], dtype=pl.UInt32),
                }
            )
            self.threshold_estimates = []
            self.render_times = []
            self.started = False

        def start(self):
            """Start the online simulation session."""
            self.started = True
            self.trials = pl.DataFrame(
                {
                    "Intensity": pl.Series([], dtype=pl.Float64),
                    "Result": pl.Series([], dtype=pl.UInt8),
                    "Trial": pl.Series([], dtype=pl.UInt32),
                }
            )
            self.threshold_estimates = []
            self.render_times = []

        def get_adaptive_intensity(self) -> float:
            """Get next stimulus intensity based on current threshold estimate."""
            if len(self.trials) == 0:
                return np.mean(self.stim_range)

            current_threshold = self.estimate_threshold()
            noise = np.random.normal(0, 2)
            adaptive_intensity = np.clip(
                current_threshold + noise, self.stim_range[0], self.stim_range[1]
            )
            return adaptive_intensity

        def present_stimulus(self, intensity: float) -> int:
            """Present stimulus and collect result."""
            p = self.params.psi(np.array([intensity]))[0]
            result = int(np.random.binomial(1, p))
            return result

        def add_trial(self, intensity: float, result: int):
            """Add trial to dataset and update estimates."""
            trial_num = len(self.trials) + 1
            new_row = pl.DataFrame(
                {
                    "Intensity": [intensity],
                    "Result": [result],
                    "Trial": [trial_num],
                }
            )
            self.trials = pl.concat([self.trials, new_row])
            self.threshold_estimates.append(self.estimate_threshold())

        def render_curve(self) -> float:
            """Render psychometric curve and measure time."""
            start = time.perf_counter()
            if len(self.trials) > 0:
                threshold_estimate = self.estimate_threshold()
            end = time.perf_counter()
            render_time = (end - start) * 1000  # Convert to ms
            self.render_times.append(render_time)
            return render_time

        def estimate_threshold(self) -> float:
            """Estimate threshold from current trials using logit transform."""
            if len(self.trials) < 2:
                return np.mean(self.stim_range)

            points = self.trials.group_by("Intensity").agg(
                pl.len().alias("n_trials"),
                pl.sum("Result").alias("Hits"),
            )
            hit_rates = (points["Hits"] / points["n_trials"]).to_numpy()
            intensities = points["Intensity"].to_numpy()

            from scipy.special import logit

            valid_mask = (hit_rates > 0.0) & (hit_rates < 1.0)
            if not valid_mask.any():
                return np.mean(intensities)

            logit_rates = np.full_like(hit_rates, np.nan, dtype=float)
            logit_rates[valid_mask] = logit(hit_rates[valid_mask])

            valid_intensities = intensities[valid_mask]
            valid_logits = logit_rates[valid_mask]

            if len(valid_logits) > 1:
                coeffs = np.polyfit(valid_intensities, valid_logits, 1)
                threshold = -coeffs[1] / coeffs[0] if coeffs[0] != 0 else np.nanmean(
                    valid_intensities
                )
            else:
                threshold = np.mean(intensities)

            return float(np.clip(threshold, self.stim_range[0], self.stim_range[1]))

        def calculate_confidence_interval(self, confidence: float = 0.95) -> tuple:
            """Calculate confidence interval for threshold estimate."""
            if len(self.threshold_estimates) < 2:
                est = self.estimate_threshold()
                return (est, est)

            estimates = np.array(self.threshold_estimates)
            margin = np.std(estimates) * 1.96
            return (
                float(np.mean(estimates) - margin),
                float(np.mean(estimates) + margin),
            )

    return OnlineSimulation(psychometric_function, stimulus_range)
