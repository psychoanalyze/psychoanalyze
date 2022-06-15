import pandas as pd
import numpy as np
from scipy.stats import logistic
from scipy.special import logit
import psychoanalyze as pa


def add_posterior(data, posterior):
    return pd.concat(
        [data, posterior],
        keys=["Observed", "Posterior"],
        names=["Type"],
    ).reset_index()


def params(points: pd.DataFrame, x: pd.Index, var: str):
    fit = pa.data.fit_curve(points)
    df = fit.loc[f"{var}[1]":f"{var}[{len(x)}]", "5%":"95%"]
    df.index = x
    return df


def generate(n_trials_per_level=100):
    index = pd.Index(range(-3, 4), name="x")
    n = [n_trials_per_level] * len(index)
    p = logistic.cdf(index)
    return pd.DataFrame({"n": n, "Hits": np.random.binomial(n, p)}, index=index)


def hit_rate(df: pd.DataFrame) -> pd.Series:
    return df["Hits"] / df["n"]


def xrange_index(x_min, x_max):
    return pd.Index(list(range(x_min, x_max + 1)), name="x")


def prep_psych_curve(curves_data, x_min, x_max, x, y):
    pa.curve.xrange_index(x_min, x_max)
    curves_data["Hit Rate"] = pa.curve.hit_rate()
    transform = {"alpha": logit(curves_data["Hit Rate"]), "p": curves_data["Hit Rate"]}
    curves_data[y] = transform[y]
    posterior = pa.data.params(curves_data, x, y)
    return pa.curve.add_posterior(curves_data, posterior)
