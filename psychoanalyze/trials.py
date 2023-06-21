from typing import TypedDict
import pandas as pd
import numpy as np
from pathlib import Path
import json
from pandera import SeriesSchema, DataFrameModel
import random
from pandera.typing import Index

from psychoanalyze import schemas

schema = SeriesSchema(bool, name="Test Trials")


class Trials(DataFrameModel):
    result: int
    intensity: Index[float]


data_path = Path("data/trials.csv")

codes = {False: "Miss", True: "Hit"}


def n(trials: pd.Series) -> int:
    return len(trials)


Trial = TypedDict("Trial", {"Result": bool, "Stimulus Magnitude": float})


def generate_hits(n, p):
    return np.random.binomial(n, p)


def generate_block(dim="x"):
    hits = pd.Series(
        [generate_hits(100, p) for p in [0.1, 0.2, 0.5, 0.8, 0.9]], name="Hits"
    )
    x = [0, 1, 2, 3, 4]
    return pd.DataFrame({"Hits": hits, "n": [100] * 5}, index=pd.Index(x, name=dim))


def generate(n: int, options, outcomes={0,1}):
    return pd.DataFrame(
        {
            "Result": pd.Series([random.choice(outcomes) for _ in range(n)], dtype=int)
        },
        index=pd.Index(
            [random.choice(options) for _ in range(n)], name="Intensity", dtype=float
        ),
    )


def load(data_path: Path = Path("data")):
    return schemas.trials.validate(
        pd.read_csv(
            data_path / "trials.csv",
            index_col=schemas.points_index_levels,
            parse_dates=["Date"],
        )
    )


def from_store(store_data):
    df_dict = json.loads(store_data)
    index_names = df_dict.pop("index_names")
    index = pd.MultiIndex.from_tuples(df_dict["index"])
    df = pd.DataFrame({"Result": df_dict["data"][0]}, index=index)
    df.index.names = index_names
    return schemas.trials.validate(df)


def to_store(df):
    df.index = df.index.set_levels(df.index.levels[1].astype(str), level=1)
    data_dict = df.to_dict(orient="split")
    data_dict["index_names"] = schemas.points_index_levels
    return json.dumps(data_dict)


def normalize(trials):
    return {
        "Session": trials[["Monkey", "Block"]].drop_duplicates(),
        "Reference Stimulus": trials[["Amp2", "Width2", "Freq2", "Dur2"]],
        "Channel Config": trials[["Active Channels", "Return Channels"]],
        "Test Stimulus": trials[["Amp1", "Width1", "Freq1", "Dur1"]],
    }


def result(p: float) -> bool:
    return random.random() < p


def results(n: int, p_x: pd.Series) -> list[Trial]:
    results = []
    for _ in range(n):
        stimulus_magnitude = random.choice(p_x.index.to_list())
        _result = result(p_x[stimulus_magnitude])
        results.append(
            Trial(
                {
                    "Stimulus Magnitude": stimulus_magnitude,
                    "Result": _result,
                }
            )
        )
    return results


def labels(results: list[bool]) -> list[str]:
    return [codes[result] for result in results]


def psi(gamma, lambda_, k, intensity, x_0):
    return gamma + (1 - gamma - lambda_) * (1 / (1 + np.exp(-k * (intensity - x_0))))


def moc_sample(n_trials: int, model_params: dict[str, float]):
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
        {
            "Result": pd.Series(results, dtype=int)
        },
        index=intensity_index
    )


def fit(points):
    return {"Fit": [None, None, None, None]}
