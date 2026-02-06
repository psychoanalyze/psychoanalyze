import numpy as np
import pymc as pm
import xarray as xr


def fit(
) -> xr.DataTree:
    with pm.Model():
        intercept = pm.Normal("intercept")
        slope = pm.HalfNormal("slope")

        logit_p = intercept + slope * np.linspace(-4, 4, 7)

        pm.Bernoulli("result", logit_p=logit_p)

        idata = pm.sample_prior_predictive()

    return idata.to_datatree()
