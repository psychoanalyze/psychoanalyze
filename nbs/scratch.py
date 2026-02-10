import marimo

__generated_with = "0.19.8"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    from datetime import date

    import altair as alt
    import polars as pl
    import xarray as xr

    return alt, date, pl, xr


@app.cell(column=1)
def _():
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
    return


@app.cell
def _(date, pl):
    trials_pl = (
        pl.read_csv(
            "../data/trials.csv",
            try_parse_dates=True,
            schema_overrides={
                # "Result": pl.Categorical,
                "Subject": pl.Enum(["U", "Y", "Z"])
            },
        )
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
    return (trials_pl,)


@app.cell
def _(trials_pl, xr):
    trials = xr.Dataset(
        {
            "result": xr.DataArray(trials_pl["Result"], dims="trial"),
        },
        coords={
            "subject": xr.DataArray(trials_pl["Subject"], dims="trial"),
            "date": xr.DataArray(trials_pl["Date"], dims="trial"),
            "test_stimulus": xr.DataArray(
                trials_pl.select("Amp1", "Width1", "Freq1", "Dur1"),
                dims=["trial", "stimulus_dimension"],
                coords={
                    "stimulus_dimension": ["amp", "pw", "freq", "dur"],
                },
            ),
            "reference_stimulus": xr.DataArray(
                trials_pl.select("Amp2", "Width2", "Freq2", "Dur2"),
                dims=["trial", "stimulus_dimension"],
                coords={
                    "stimulus_dimension": ["amp", "pw", "freq", "dur"],
                },
            ),
            "channel_config": xr.DataArray(
                trials_pl.select("Active Channels", "Return Channels"),
                dims=["trial", "electrode_group"],
            ),
        },
    )
    trials
    return (trials,)


@app.cell
def _(trials):
    detection_trials = trials.sel(
        trial=(trials.reference_stimulus.sel({"stimulus_dimension": "amp"}) == 0).values
    ).drop_vars("reference_stimulus")
    detection_trials
    return (detection_trials,)


@app.cell
def _(detection_trials):
    test_trials = detection_trials.isel(trial=detection_trials.result.isin([0, 1]))
    test_trials
    return


@app.cell
def _(detection_trials):
    catch_trials = (
        detection_trials.sel(stimulus_dimension="amp")
        .isel(trial=detection_trials.result.isin([2, 3]))
        .groupby("date")
        .count()
    )

    catch_trials["false_alarms"] = (
        detection_trials.sel(stimulus_dimension="amp")
        .isel(trial=detection_trials.result.isin([2]))
        .groupby("date")
        .count()
        .result
    )

    catch_trials = catch_trials.to_dataframe().rename(columns={"result": "n"})[
        ["n", "false_alarms"]
    ]
    return


@app.cell
def _(alt):
    threshold_mean_plot = (
        alt.Chart()
        .mark_point()
        .encode(
            x="date",
            y="threshold_date",
            # color="electrode_config",
        )
    )
    # threshold_mean_plot
    # threshold_mean_plot + threshold_err
    return


@app.cell
def _(pl):
    fit_trace = pl.DataFrame().plot.line(
        x="amp",
        y="p(yes)",
        color="date",
    )
    fit_trace
    return


if __name__ == "__main__":
    app.run()
