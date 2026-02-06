import marimo

__generated_with = "0.19.7"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    import altair as alt
    import numpy as np
    import pymc as pm
    import xarray as xr
    from datetime import date
    import polars as pl
    import marimo as mo

    import arviz_stats as azs
    import arviz_plots as azp
    from scipy.special import expit
    return alt, azp, azs, date, expit, mo, np, pl, pm, xr


@app.cell
def _(test_trials, xr, z_test_stim):
    ds = xr.Dataset(
        {"result": xr.DataArray(test_trials["Result"], dims="trial")},
        coords={
            "amplitude": z_test_stim["z_Amp1"],
            "date": test_trials["Date"],
        },
    )
    ds
    return (ds,)


@app.cell
def _(ds, np):
    date_labels, date_idx = np.unique(ds.date.values, return_inverse=True)
    # subj_labels, subj_idx = np.unique(ds.subject.values, return_inverse=True)
    return date_idx, date_labels


@app.cell
def _(date_labels, ds):
    coords = {
        "trial": ds.trial,
        "date": date_labels,
        # "subj": subj_labels,
    }
    return (coords,)


@app.cell
def _(catch_trials, coords, date_idx, ds, pm):
    with pm.Model(coords=coords) as model:
        x = pm.Data(name="amplitude", value=ds.amplitude, dims="trial")

        date_idx_data = pm.Data("date", value=date_idx, dims="trial")

        mu_intercept = pm.Normal("mu_intercept")
        sigma_intercept = pm.HalfNormal("sigma_intercept")

        mu_slope = pm.HalfNormal("mu_slope")
        sigma_slope = pm.HalfNormal("sigma_slope")

        mu_guess_logit = pm.Normal("mu_guess_logit", -2.0, 1.5)
        sigma_guess_logit = pm.HalfNormal("sigma_guess_logit")

        z_intercept = pm.Normal("z_intercept", dims="date")
        intercept_date = pm.Deterministic(
            "intercept_date",
            mu_intercept + z_intercept * sigma_intercept,
            dims="date",
        )

        z_slope = pm.Normal("z_slope", dims="date")
        slope_date = pm.Deterministic(
            "slope_date",
            pm.math.log1pexp(mu_slope + z_slope * sigma_slope),
            dims="date",
        )

        z_guess = pm.Normal("z_guess", dims="date")
        guess_rate_date = pm.Deterministic(
            "guess_rate_date",
            pm.math.sigmoid(mu_guess_logit + z_guess * sigma_guess_logit),
            dims="date",
        )
        guess_trial = guess_rate_date[date_idx_data]

        eta = intercept_date[date_idx_data] + slope_date[date_idx_data] * x

        p = (1.0 - guess_trial) * pm.math.sigmoid(eta) + guess_trial

        pm.Binomial(
            "k",
            n=catch_trials["n"].to_numpy(),
            p=guess_rate_date,
            observed=catch_trials["false_alarms"].to_numpy(),
            dims="date",
        )
        y = pm.Bernoulli("result", p=p, dims="trial", observed=ds.result)
        threshold = pm.Deterministic(
            "threshold_date", -intercept_date / slope_date, dims="date"
        )

        prior_predictive_samples = pm.sample_prior_predictive()
    prior_predictive_samples
    return (model,)


@app.cell
def _(mo):
    run_button = mo.ui.run_button()
    run_button
    return (run_button,)


@app.cell
def _(mo, model, pm, run_button):
    mo.stop(not run_button.value)
    with model:
        samples = pm.sample()
    return (samples,)


@app.cell
def _(azp, samples):
    azp.plot_dist(
        samples,
        var_names=["mu_intercept", "mu_slope", "mu_guess_logit"],
        kind="ecdf",
    ).show()
    return


@app.cell
def _(azs, samples, test_stimulus):
    z_threshold_hdi = azs.hdi(samples, var_names=["threshold_date"])
    threshold_hdi = (
        z_threshold_hdi * test_stimulus["Amp1"].std() + test_stimulus["Amp1"].mean()
    )
    return (threshold_hdi,)


@app.cell
def _(azs, samples, test_stimulus):
    threshold_means = (
        azs.mean(samples).threshold_date * test_stimulus["Amp1"].std()
        + test_stimulus["Amp1"].mean()
    )
    return (threshold_means,)


@app.cell
def _(alt, threshold_hdi):
    threshold_err = (
        alt.Chart(
            threshold_hdi.to_dataframe().unstack("ci_bound")["threshold_date"].reset_index()
        )
        .mark_errorbar()
        .encode(
            x="date",
            y="upper",
            y2="lower",
        )
    )
    return (threshold_err,)


@app.cell
def _(expit, np, samples, xr):
    z_amp = xr.DataArray(np.linspace(-3, 3), dims="x")

    _logit_p = z_amp * samples.posterior.slope_date + samples.posterior.intercept_date

    p_dates = (1 - samples.posterior["guess_rate_date"]) * expit(
        _logit_p
    ) + samples.posterior["guess_rate_date"]
    return p_dates, z_amp


@app.cell
def _(p_dates, test_stimulus, xr, z_amp):
    amp = z_amp * test_stimulus["Amp1"].std() + test_stimulus["Amp1"].mean()
    p_raw = xr.Dataset({"p(yes)": p_dates}, coords={"amp": amp})
    p_raw
    return (p_raw,)


@app.cell(column=1)
def _(date, pl):
    reference_stimulus_fields = [
        "Width2",
        "Amp2",
        "Freq2",
        "Dur2",
    ]

    test_stimulus_fields = [
        "Width1",
        "Amp1",
        "Freq1",
        "Dur1",
    ]

    trials = (
        pl.read_csv(
            "data/trials.csv",
            try_parse_dates=True,
            schema_overrides={
                # "Result": pl.Categorical,
                "Subject": pl.Enum(["U", "Y", "Z"])
            },
        )
        # .select(
        #     "Subject",
        #     "Date",
        #     pl.struct(reference_stimulus_fields).alias("reference_stimulus"),
        #     pl.struct(test_stimulus_fields).alias("test_stimulus"),
        #     # pl.struct("Active Channels", "Return Channels").alias("electrode_config"),
        #     # "Result",
        # )
        .filter(pl.col("Subject") == "Y")
        .filter(pl.col("Date") >= date(2017, 5, 7))
        .filter(
            ~pl.col("Date").is_in(
                [
                    date(2017, 8, 4),
                    date(2017, 8, 14),
                    date(2017, 8, 2),
                    date(2017, 7, 6),
                    date(2017, 6, 28),
                    date(2017, 5, 11),
                ]
            )
        )
    )
    return (trials,)


@app.cell
def _(trials, xr):
    channel_config = xr.DataArray(
        trials.select("Active Channels", "Return Channels"),
        dims=["trial", "electrode_group"],
    )
    return


@app.cell
def _(trials, xr):
    xr.DataArray(
        trials.select("Amp1", "Width1", "Freq1", "Dur1"),
        dims=["trial", "stimulus_dimension"],
        coords={"stimulus_dimension": ["amp", "pw", "freq", "dur"]},
    )
    return


@app.cell
def _(pl, trials):
    detection_block = (
        trials.filter(
            pl.any_horizontal(pl.col("reference_stimulus").struct.field("Amp2") == 0)
        )
        .drop("reference_stimulus")
        .with_columns(
            electrode_config_str=pl.concat_str(
                [
                    pl.col("electrode_config").struct.field("Active Channels"),
                    pl.col("electrode_config").struct.field("Return Channels"),
                ],
                separator="|",
            )
        )
    )
    return (detection_block,)


@app.cell
def _(detection_block, pl):
    test_trials = detection_block.filter(pl.col("Result").is_in([1, 0]))
    return (test_trials,)


@app.cell
def _(detection_block, pl):
    catch_trials = detection_block.group_by(
        # "Subject",
        "Date",
        # "electrode_config",
        # "test_stimulus",
    ).agg(
        [
            (pl.col("Result") == 2).sum().alias("false_alarms"),
            (pl.col("Result").is_in([2, 3]).len().alias("n")),
        ]
    )
    return (catch_trials,)


@app.cell
def _(test_trials):
    test_stimulus = test_trials["test_stimulus"].struct.unnest()
    return (test_stimulus,)


@app.cell
def _(pl, test_stimulus):
    z_test_stim = test_stimulus.select(
        ((pl.all() - pl.all().mean()) / pl.all().std()).name.prefix("z_")
    )
    z_test_stim
    return (z_test_stim,)


@app.cell
def _(alt, pl, test_trials):
    data_trace = (
        test_trials.group_by(
            "Date",
            "electrode_config_str",
            pl.col("test_stimulus").struct.field("Amp1"),
        )
        .agg([pl.col("Result").mean().alias("p(yes)"), pl.len().alias("n")])
        .rename({"Amp1": "amp", "Date": "date"})
        .sort("amp")
    ).plot.scatter(
        x=alt.X("amp"),
        y="p(yes)",
        size="n",
        color="date",
        shape="electrode_config_str",
    )
    return


@app.cell
def _(alt, threshold_err, threshold_means):
    threshold_mean_plot = (
        alt.Chart(threshold_means.to_dataframe().reset_index())
        .mark_point()
        .encode(
            x="date",
            y="threshold_date",
            # color="electrode_config",
        )
    )
    # threshold_mean_plot
    threshold_mean_plot + threshold_err
    return


@app.cell
def _(p_raw, pl):
    fit_trace = pl.DataFrame(p_raw.to_dataframe().reset_index()).plot.line(
        x="amp",
        y="p(yes)",
        color="date",
    )
    return


if __name__ == "__main__":
    app.run()
