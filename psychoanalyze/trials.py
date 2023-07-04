"""Functions for data manipulations at the trial level."""
import json
import random
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd
from pandera import DataFrameModel, SeriesSchema
from pandera.typing import Index
from sklearn.linear_model import LogisticRegression

from psychoanalyze import schemas

schema = SeriesSchema(bool, name="Test Trials")


class Trials(DataFrameModel):

    """Trials data type for pandera + mypy type checking."""

    result: int
    intensity: Index[float]


data_path = Path("data/trials.csv")

codes = {0: "Miss", 1: "Hit"}


Trial = TypedDict("Trial", {"Result": bool, "Stimulus Magnitude": float})


def generate_hits(n: int, p: float) -> int:
    """Sample n hits from n trials and probability p from binomial dist."""
    return np.random.default_rng().binomial(n, p)


def generate_block(dim: str = "x") -> pd.DataFrame:
    """Generate a block of trial data."""
    hits = pd.Series(
        [generate_hits(100, p) for p in [0.1, 0.2, 0.5, 0.8, 0.9]],
        name="Hits",
    )
    x = [0, 1, 2, 3, 4]
    return pd.DataFrame({"Hits": hits, "n": [100] * 5}, index=pd.Index(x, name=dim))


def generate(n: int, options: list[float], outcomes: list[float]) -> pd.DataFrame:
    """Generate n trials with outcomes."""
    return pd.DataFrame(
        {
            "result": pd.Series(
                [random.choice(outcomes) for _ in range(n)],
                dtype=int,
            ),
        },
        index=pd.Index(
            [random.choice(options) for _ in range(n)],
            name="intensity",
            dtype=float,
        ),
    )


def load(data_path: Path = Path("data")) -> pd.DataFrame:
    """Load trials data from csv."""
    return schemas.trials.validate(
        pd.read_csv(
            data_path / "trials.csv",
            index_col=schemas.points_index_levels,
            parse_dates=["Date"],
        ),
    )


def from_store(store_data: str) -> pd.DataFrame:
    """Convert JSON-formatted string to DataFrame."""
    df_dict = json.loads(store_data)
    index_names = df_dict.pop("index_names")
    index = pd.MultiIndex.from_tuples(df_dict["index"])
    trials = pd.DataFrame({"Result": df_dict["data"][0]}, index=index)
    trials.index.names = index_names
    return schemas.trials.validate(trials)


def to_store(trials: pd.DataFrame) -> str:
    """Convert data to a JSON-formatted string for dcc.Store."""
    data_dict = trials.to_dict(orient="split")
    data_dict["index_names"] = schemas.points_index_levels
    return json.dumps(data_dict)


def normalize(trials: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Normalize denormalized trial data."""
    return {
        "Session": trials[["Monkey", "Block"]].drop_duplicates(),
        "Reference Stimulus": trials[["Amp2", "Width2", "Freq2", "Dur2"]],
        "Channel Config": trials[["Active Channels", "Return Channels"]],
        "Test Stimulus": trials[["Amp1", "Width1", "Freq1", "Dur1"]],
    }


def result(p: float) -> bool:
    """Return a trial result given a probability p."""
    return random.random() < p


def results(n: int, p_x: pd.Series) -> list[Trial]:
    """Return a list of trial results in dict format."""
    results = []
    for _ in range(n):
        stimulus_magnitude = random.choice(p_x.index.to_list())
        _result = result(p_x[stimulus_magnitude])
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


def psi(gamma: float, lambda_: float, k: float, intensity: float, x_0: float) -> float:
    """Calculate the value of the psychometric function for a given intensity."""
    return gamma + (1 - gamma - lambda_) * (1 / (1 + np.exp(-k * (intensity - x_0))))


def moc_sample(n_trials: int, model_params: dict[str, float]) -> pd.DataFrame:
    """Sample results from a method-of-constant-stimuli experiment."""
    x_0 = model_params["x_0"]
    k = model_params["k"]
    gamma = model_params["gamma"]
    lambda_ = model_params["lambda"]
    intensity_choices = np.linspace(x_0 - 4 / k, x_0 + 4 / k, 7)
    intensities = [float(random.choice(intensity_choices)) for _ in range(n_trials)]
    intensity_index = pd.Index(intensities, name="Intensity")
    results = [
        int(random.random() <= psi(gamma, lambda_, k, intensity, x_0))
        for intensity in intensities
    ]
    return pd.DataFrame(
        {"Result": pd.Series(results, dtype=int)},
        index=intensity_index,
    )


def fit(trials: pd.DataFrame) -> pd.DataFrame:
    """Fit trial data using logistic regression."""
    return LogisticRegression().fit(trials[["Intensity"]], trials["Result"])
