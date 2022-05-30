import pandas as pd
import numpy as np
from scipy.stats import logistic


def generate():
    index = pd.Index(range(-4, 5), name="x")
    n = [100] * 9
    p = logistic.cdf(index)
    return pd.DataFrame({"n": n, "p": p, "Hits": np.random.binomial(n, p)}, index=index)
