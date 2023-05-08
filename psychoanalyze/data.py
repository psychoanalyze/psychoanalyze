from pathlib import Path
import pandas as pd
from numpy.random import default_rng
from numpy import linspace
from scipy.stats import logistic as scipy_logistic
import psychoanalyze as pa
from itertools import accumulate


def generate_outcomes(n_trials_per_stim_level, index, threshold, scale):
    random_number_generator = default_rng()
    return random_number_generator.binomial(
        n_trials_per_stim_level,
        scipy_logistic.cdf(index.get_level_values("x"), threshold, scale),
        len(index),
    )


def logistic(threshold=0, scale=1, gamma=0, lambda_=0):
    x = linspace(scipy_logistic.ppf(0.01), scipy_logistic.ppf(0.99), 100)
    index = pd.Index(x, name="x")
    return pd.Series(
        gamma + (1 - gamma - lambda_) * scipy_logistic.cdf(x, threshold, scale),
        index=index,
        name="Hit Rate",
    )


def mu(fit):
    df = fit.loc["mu", ["5%", "50%", "95%"]]
    return df.T


def transform_errors(df):
    df["err+"] = df["95%"] - df["50%"]
    df["err-"] = df["50%"] - df["5%"]
    return df.drop(columns=["95%", "5%"])


def reshape_fit_results(fit: pd.DataFrame, x: pd.Index, y: str) -> pd.DataFrame:
    rows = [f"{y}[{i}]" for i in range(1, len(x) + 1)]
    df = fit.loc[
        rows,  # row eg 'p[1]:p[8]'
        ["5%", "50%", "95%"],  # col
    ]
    df = transform_errors(df)
    df = df.rename(columns={"50%": y})
    df.index = x
    return df


def generate_animation_curves():
    n_blocks = 10
    n_trials_per_level_per_block = 10
    df = pd.concat(
        list(
            accumulate(
                [
                    pa.blocks.generate(n_trials_per_level_per_block)
                    for _ in range(n_blocks)
                ]
            )
        )
    )
    df["Hit Rate"] = pa.blocks.hit_rate
    return df


def filter(df, dim):
    return df[df["Dimension"] == dim]


def load(data_dir=Path("data"), monkey=None, day=None):
    return {
        "Sessions": pa.sessions.load_cached(data_dir),
        "Subjects": pa.subjects.load(data_dir),
        "Blocks": pa.blocks.load(data_dir, monkey=monkey, day=day),
        "Points": pa.points.load(data_dir),
    }
