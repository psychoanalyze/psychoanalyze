import pandas as pd
import numpy as np
from scipy.stats import logistic
from psychoanalyze import data


def add_posterior(data, posterior):
    return pd.concat(
        [data, posterior],
        keys=["Observed", "Posterior"],
        names=["Type"],
    ).reset_index()


def params(points: pd.DataFrame, x: pd.Index, var: str):
    fit = data.fit_curve(points)
    df = fit.loc[f"{var}[1]":f"{var}[{len(x)}]", "5%":"95%"]
    df.index = x
    return df


def generate(n_trials_per_level=100):
    index = pd.Index(range(-3, 4), name="x")
    n = [n_trials_per_level] * len(index)
    p = logistic.cdf(index)
    return pd.DataFrame({"n": n, "Hits": np.random.binomial(n, p)}, index=index)
