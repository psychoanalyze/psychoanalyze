
"""Data transformation functions for subject-level data."""
import string
from pathlib import Path

import polars as pl

from psychoanalyze.data import sessions


def load(data_path: Path) -> pl.DataFrame:
    """Load subject data from csv."""
    df = pl.read_csv(data_path / "subjects.csv")
    df = df.with_columns(pl.col("Surgery Date").str.to_datetime())
    return df


def generate_letter_names(n_subjects: int) -> list[str]:
    """Generate a list of dummy subjects using capital letters in alph. order."""
    return list("ABCDEFG"[:n_subjects])


def generate_trials(
    n_trials: int,
    model_params: dict[str, float],
    n_days: int,
    n_subjects: int,
) -> pl.DataFrame:
    """Generate trial-level data, including subject-level info."""
    frames = []
    for subj in string.ascii_uppercase[:n_subjects]:
        df = sessions.generate_trials(n_trials, model_params, n_days)
        df = df.with_columns(pl.lit(subj).alias("Subject"))
        frames.append(df)
    return pl.concat(frames)

def generate_multi_subject(
    n_trials: int,
    options: list[float],
    params: dict[str, float],
    n_blocks: int,
    n_subjects: int = 1,
    use_random_params: bool = False,
) -> tuple[pl.DataFrame, dict[tuple[str, int], dict[str, float]]]:
    frames = []
    ground_truth_params_map: dict[tuple[str, int], dict[str, float]] = {}
    rng = np.random.default_rng()

    for subject_idx in range(n_subjects):
        subject_id = (
            chr(ord("A") + subject_idx) if subject_idx < 26 else f"S{subject_idx}"
        )

        for block_id in range(n_blocks):
            block_params = params.copy()
            block_params["x_0"] = params["x_0"] + rng.normal(0, 0.5)

            ground_truth_params_map[(subject_id, block_id)] = block_params

            block_trials = generate(
                n_trials=n_trials,
                options=options,
                params=block_params,
                n_blocks=1,
            )
            block_trials = block_trials.with_columns(
                pl.lit(subject_id).alias("Subject"),
                pl.lit(block_id).alias("Block"),
            )
            frames.append(block_trials)

    trials_df = pl.concat(frames) if frames else pl.DataFrame()
    return trials_df, ground_truth_params_map