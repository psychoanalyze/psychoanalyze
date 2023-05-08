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


def generate_trials(
    n_trials, k, x_0, n_levels, fixed_min, fixed_max, n_days, n_subjects, gamma, lambda_
):
    return pd.concat(
        {
            subj: pa.sessions.generate_trials(
                n_trials, k, x_0, n_levels, fixed_min, fixed_max, n_days, gamma, lambda_
            )
            for subj in range(n_subjects)
        },
        names=["Subject"],
    )
