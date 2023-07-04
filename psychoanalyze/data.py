"""Generic data tools for psychophysics data."""
from itertools import accumulate
from pathlib import Path

import pandas as pd
from numpy import linspace
from numpy.random import default_rng
from scipy.stats import logistic as scipy_logistic

from psychoanalyze import blocks, points, sessions, subjects


def generate_outcomes(
    n_trials_per_stim_level: int,
    index: pd.Index,
    threshold: float,
    scale: float,
) -> pd.Series:
    """Generate outcomes."""
    random_number_generator = default_rng()
    return pd.Series(
        random_number_generator.binomial(
            n_trials_per_stim_level,
            scipy_logistic.cdf(index.get_level_values("x"), threshold, scale),
            len(index),
        ),
    )


def logistic(
    threshold: float = 0.0,
    scale: float = 1.0,
    gamma: float = 0.0,
    lambda_: float = 0.0,
) -> pd.Series:
    """Generate logistic curves from parameters."""
    x = linspace(scipy_logistic.ppf(0.01), scipy_logistic.ppf(0.99), 100)
    index = pd.Index(x, name="x")
    return pd.Series(
        gamma + (1 - gamma - lambda_) * scipy_logistic.cdf(x, threshold, scale),
        index=index,
        name="Hit Rate",
    )


def transform_errors(fit: pd.DataFrame) -> pd.DataFrame:
    """Transform errors from absolute to relative."""
    fit["err+"] = fit["95%"] - fit["50%"]
    fit["err-"] = fit["50%"] - fit["5%"]
    return fit.drop(columns=["95%", "5%"])


def reshape_fit_results(fits: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
    """Reshape fit params for plotting."""
    rows = [f"{y}[{i}]" for i in range(1, len(x) + 1)]
    param_fits = fits.loc[
        rows,  # row eg 'p[1]:p[8]'
        ["5%", "50%", "95%"],  # col
    ]
    param_fits = transform_errors(param_fits)
    param_fits = param_fits.rename(columns={"50%": y})
    param_fits.index = x
    return param_fits


def generate_animation_curves() -> pd.DataFrame:
    """Generate animation data for curves."""
    n_blocks = 10
    n_trials_per_level_per_block = 10
    all_data = pd.concat(
        list(
            accumulate(
                [
                    blocks.generate(n_trials_per_level_per_block)
                    for _ in range(n_blocks)
                ],
            ),
        ),
    )
    all_data["Hit Rate"] = blocks.hit_rate
    return all_data


def dimension_filter(blocks: pd.DataFrame, dim: str) -> pd.DataFrame:
    """Filter block data by dimension."""
    return blocks[blocks["Dimension"] == dim]


def load(
    data_dir: Path = Path("data"),
) -> dict[str, pd.DataFrame]:
    """Load all tables into dict."""
    return {
        "Sessions": sessions.load(data_dir),
        "Subjects": subjects.load(data_dir),
        "Blocks": blocks.load(data_dir),
        "Points": points.load(data_dir).to_frame(),
    }


def generate() -> pd.DataFrame:
    """Generate data."""
    return pd.DataFrame(
        {
            "Intensity": [0.0],
            "Hit Rate": [0.5],
        },
    )
