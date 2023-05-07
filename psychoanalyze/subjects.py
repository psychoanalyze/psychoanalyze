import pandas as pd

import psychoanalyze as pa


def load(data_path):
    return pd.read_csv(
        data_path / "subjects.csv",
        index_col="Monkey",
        parse_dates=["Surgery Date"],
    )


def make_predictions(fits, intensity_choices):
    return pd.concat(
        {
            block: pa.blocks.make_predictions(fits[block], intensity_choices)
            for block in fits
        },
        names=["Block"],
    )


def fit_params(fits):
    return pd.DataFrame.from_records(
        [
            {
                "slope": fit.coef_[0][0],
                "intercept": fit.intercept_[0],
            }
            for fit in fits.values()
        ],
        index=pd.Index(fits.keys(), name="Block"),
    )
