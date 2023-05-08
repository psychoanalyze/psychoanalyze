import pandas as pd
import psychoanalyze as pa


def load(data_path):
    return pd.read_csv(
        data_path / "subjects.csv",
        index_col="Monkey",
        parse_dates=["Surgery Date"],
    )


def generate_letter_names(n_subjects):
    return list("ABCDEFG"[:n_subjects])


def generate_trials(n_trials, model_params, n_levels, fixed_range, n_days, n_subjects):
    return pd.concat(
        {
            subj: pa.sessions.generate_trials(
                n_trials, model_params, n_levels, fixed_range, n_days
            )
            for subj in range(n_subjects)
        },
        names=["Subject"],
    )
