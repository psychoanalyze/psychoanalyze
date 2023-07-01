import random

import arviz as az
import bambi as bmb
import pandas as pd


def model(dbt, session):
    trials = dbt.ref("trials")

    trials = pd.DataFrame(
        {
            "Result": [random.choice([0, 1]) for _ in range(100)],
            "Intensity": [random.choice([0, 1, 2, 3, 4]) for _ in range(100)],
        }
    )

    model = bmb.Model("Result ~ Intensity", trials, family="bernoulli")
    fitted = model.fit()

    return az.summary(fitted, round_to=2)
