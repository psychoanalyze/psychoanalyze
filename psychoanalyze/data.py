import pandas as pd


def generate(n_subjects=None):
    subjects = list("ABCDEFG"[:n_subjects])
    records = [{"Day": 1, "Subject": subject, "Threshold": 1} for subject in subjects]
    return pd.DataFrame.from_records(records)
