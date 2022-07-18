import pandas as pd
import numpy as np
import psychoanalyze as pa
from pathlib import Path
import random
import pandera as pr
from datetime import datetime
import json

dims = ["Amp1", "Width1", "Freq1", "Dur1"]

data_path = Path("data/trials.csv")

schema = pr.DataFrameSchema(
    {"Result": pr.Column(int, checks=pr.Check.isin([0, 1, 2, 3]), coerce=True)},
    index=pr.MultiIndex(
        [
            pr.Index(str, name="Monkey", checks=pr.Check.isin(["U", "Y", "Z"])),
            pr.Index("datetime64", name="Date", coerce=True),
        ]
        + [pr.Index(float, name=dim) for dim in pa.blocks.stim_dims]
        + [pr.Index(int, name=dim) for dim in pa.blocks.channel_dims]
        + [pr.Index(float, name=dim) for dim in dims]
    ),
    coerce=True,
)


def generate(n, stim_levels=[float(i) for i in range(-3, 4)]):
    return schema.validate(
        pd.DataFrame(
            {"Result": np.random.binomial(1, 0.5, n)},
            index=pd.MultiIndex.from_frame(
                pd.DataFrame(
                    {
                        "Monkey": ["Z"] * n,
                        "Date": [datetime.now()] * n,
                        "Amp2": [0.0] * n,
                        "Width2": [0.0] * n,
                        "Freq2": [0.0] * n,
                        "Dur2": [0.0] * n,
                        "Active Channels": [1] * n,
                        "Return Channels": [1] * n,
                        "Amp1": random.choices(stim_levels, k=n),
                        "Width1": [0.0] * n,
                        "Freq1": [0.0] * n,
                        "Dur1": [0.0] * n,
                    }
                )
            ),
        )
    )


def load(filepath: Path = data_path):
    return schema.validate(
        pd.read_csv(
            filepath,
            index_col=pa.sessions.dims + pa.blocks.dims + pa.trials.dims,
            parse_dates=["Date"],
        )
    )


def from_store(store_data):
    df_dict = json.loads(store_data)
    index_names = df_dict.pop("index_names")
    print(f"store_data: {df_dict}")
    print(index_names)
    index = pd.MultiIndex.from_tuples(df_dict["index"])
    df = pd.DataFrame({"Result": df_dict["data"][0]}, index=index)
    df.index.names = [
        "Monkey",
        "Date",
        "Amp2",
        "Width2",
        "Freq2",
        "Dur2",
        "Active Channels",
        "Return Channels",
        "Amp1",
        "Width1",
        "Freq1",
        "Dur1",
    ]
    print(df)
    return schema.validate(df)
