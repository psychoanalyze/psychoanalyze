import pandas as pd
import psychoanalyze as pa
import string

def load(data_path):
    return pd.read_csv(
        data_path / "subjects.csv",
        index_col="Monkey",
        parse_dates=["Surgery Date"],
    )


def generate_letter_names(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
    n_subjects: int,
) -> pd.Series:
    return pd.concat(
        {
            subj: pa.sessions.generate_trials(n_trials, model_params, n_days)
            for subj in string.ascii_uppercase[:n_subjects]
        },
        names=["Subject"],
    )
