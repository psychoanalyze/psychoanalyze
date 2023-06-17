from typing import TypedDict
import pandas as pd
import numpy as np
import psychoanalyze as pa
from pathlib import Path
import json
import pandera as pr
import random

schema = pr.SeriesSchema(bool, name="Test Trials")


class Trials(pr.DataFrameModel):
    result: int


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


def generate(n: int) -> pd.Series:
    return pd.Series(np.random.binomial(1, 0.5, n),dtype=int, name="Result")


def load(data_path: Path = Path("data")):
    return pa.schemas.trials.validate(
        pd.read_csv(
            data_path / "trials.csv",
            index_col=pa.schemas.points_index_levels,
            parse_dates=["Date"],
        )
    )


def from_store(store_data):
    df_dict = json.loads(store_data)
    index_names = df_dict.pop("index_names")
    index = pd.MultiIndex.from_tuples(df_dict["index"])
    df = pd.DataFrame({"Result": df_dict["data"][0]}, index=index)
    df.index.names = index_names
    return pa.schemas.trials.validate(df)


def to_store(df):
    df.index = df.index.set_levels(df.index.levels[1].astype(str), level=1)
    data_dict = df.to_dict(orient="split")
    data_dict["index_names"] = pa.schemas.points_index_levels
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
    return [pa.trials.codes[result] for result in results]


def psi(gamma, lambda_, k, intensity, x_0):
    return gamma + (1 - gamma - lambda_) * (1 / (1 + np.exp(-k * (intensity - x_0))))


def moc_sample(n_trials: int, model_params: dict[str, float]) -> pd.Series:
    x_0 = model_params["x_0"]
    k = model_params["k"]
    gamma = model_params["gamma"]
    lambda_ = model_params["lambda"]
    intensity_choices = np.linspace(x_0 - 4 / k, x_0 + 4 / k, 7)
    intensities = [float(random.choice(intensity_choices)) for _ in range(n_trials)]
    intensity_index = pd.Index(intensities, name="Intensity")
    results = [
        random.random() <= psi(gamma, lambda_, k, intensity, x_0)
        for intensity in intensities
    ]
    return pd.Series(results, name="Result", index=intensity_index)
