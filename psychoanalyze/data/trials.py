# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""Functions for data manipulations at the trial level."""
import json
import random
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd
from pandera import SeriesSchema, check_output
from sklearn.linear_model import LogisticRegression

from psychoanalyze.data import types

schema = SeriesSchema(bool, name="Test Trials")

data_path = Path("data/trials.csv")

codes = {0: "Miss", 1: "Hit"}


Trial = TypedDict("Trial", {"Result": bool, "Stimulus Magnitude": float})


def generate_trial_index(n_trials: int, options: pd.Index) -> pd.Series:
    """Generate n trials (no outcomes)."""
    return pd.Series(
        [random.choice(options) for _ in range(n_trials)],
        name="Intensity",
    )


@check_output(types.trials)
def generate(
    n_trials: int,
    options: pd.Index,
    params: dict[str, float],
) -> pd.DataFrame:
    """Generate n trials with outcomes."""
    x = generate_trial_index(n_trials, options)
    p = {option: psi(option, params) for option in options}
    return pd.DataFrame(
        {
            "Result": [int(random.random() <= p[x_val]) for x_val in x],
            "Intensity": x,
        },
    )


def load(data_path: Path = Path("data")) -> pd.DataFrame:
    """Load trials data from csv."""
    return types.trials.validate(
        pd.read_csv(
            data_path / "trials.csv",
            index_col=types.points_index_levels,
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
    return types.trials.validate(trials)


def to_store(trials: pd.DataFrame) -> str:
    """Convert data to a JSON-formatted string for dcc.Store."""
    data_dict = trials.to_dict(orient="split")
    data_dict["index_names"] = types.points_index_levels
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


def psi(intensity: float, params: dict[str, float]) -> float:
    """Calculate the value of the psychometric function for a given intensity."""
    gamma = params["Guess Rate"]
    lambda_ = params["Lapse Rate"]
    k = params["Slope"]
    x_0 = params["Threshold"]
    return gamma + (1 - gamma - lambda_) * (1 / (1 + np.exp(-k * (intensity - x_0))))


def moc_sample(n_trials: int, model_params: dict[str, float]) -> pd.DataFrame:
    """Sample results from a method-of-constant-stimuli experiment."""
    x_0 = model_params["x_0"]
    k = model_params["k"]
    intensity_choices = np.linspace(x_0 - 4 / k, x_0 + 4 / k, 7)
    intensities = [float(random.choice(intensity_choices)) for _ in range(n_trials)]
    intensity_index = pd.Index(intensities, name="Intensity")
    results = [
        int(random.random() <= psi(intensity, model_params))
        for intensity in intensities
    ]
    return pd.DataFrame(
        {"Result": pd.Series(results, dtype=int)},
        index=intensity_index,
    )


def fit(trials: pd.DataFrame) -> dict[str, float]:
    """Fit trial data using logistic regression."""
    fits = LogisticRegression().fit(trials[["Intensity"]], trials["Result"])
    return {"Threshold": -fits.intercept_[0], "Slope": fits.coef_[0][0]}
