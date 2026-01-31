"""PsychoAnalyze dashboard as a marimo notebook.

Interactive data simulation & analysis for psychophysics.
Replaces the former Dash dashboard (removed).
"""

import marimo

__generated_with = "0.19.2"
app = marimo.App(width="full", app_title="PsychoAnalyze")


@app.cell
def _():
    import io
    import zipfile

    import marimo as mo
    import numpy as np
    import plotly.express as px
    import polars as pl
    from scipy.special import expit, logit

    from psychoanalyze.data import blocks as pa_blocks


    def to_intercept(location: float, scale: float) -> float:
        return -location / scale


    def to_slope(scale: float) -> float:
        return 1 / scale


    def psi(intensity: float, params: dict) -> float:
        gamma = params.get("gamma", 0.0)
        lambda_ = params.get("lambda", 0.0)
        k = params["k"]
        x_0 = params["x_0"]
        return gamma + (1 - gamma - lambda_) * (1 / (1 + np.exp(-k * (intensity - x_0))))

    def generate_index(n_levels: int, x_range: list[float]) -> list[float]:
        return list(np.linspace(x_range[0], x_range[1], n_levels))


    def generate_trials(
        n_trials: int,
        options: list[float],
        params: dict,
        n_blocks: int,
    ) -> pl.DataFrame:
        rng = np.random.default_rng()
        out = []
        for i in range(n_blocks):
            intensities = rng.choice(options, size=n_trials)
            results = np.array([int(rng.random() <= psi(x, params)) for x in intensities])
            df = pl.DataFrame({"Intensity": intensities, "Result": results})
            df = df.with_columns(pl.lit(i).alias("Block"))
            out.append(df)
        return pl.concat(out).select(["Block", "Intensity", "Result"])

    def from_trials(trials_df: pl.DataFrame) -> pl.DataFrame:
        points = trials_df.group_by(["Block", "Intensity"]).agg(
            pl.len().alias("n trials"),
            pl.sum("Result").alias("Hits"),
        )
        points = points.with_columns(
            (pl.col("Hits") / pl.col("n trials")).alias("Hit Rate"),
        )
        return points.sort(["Block", "Intensity"])

    def block_fit(trials_df: pl.DataFrame) -> dict[str, float]:
        idata = pa_blocks.fit(
            trials_df,
            draws=300,
            tune=300,
            chains=1,
            target_accept=0.9,
        )
        summary = pa_blocks.summarize_fit(idata)
        return {
            "intercept": summary["intercept"],
            "slope": summary["slope"],
        }

    def process_upload_bytes(contents: bytes, filename: str) -> pl.DataFrame:
        if "zip" in filename:
            with zipfile.ZipFile(io.BytesIO(contents)) as z:
                return pl.read_csv(z.open("trials.csv"))
        return pl.read_csv(io.BytesIO(contents))
    return (
        block_fit,
        expit,
        from_trials,
        generate_index,
        generate_trials,
        logit,
        mo,
        np,
        pl,
        process_upload_bytes,
        px,
        to_intercept,
        to_slope,
    )


@app.cell
def _(mo):
    # Header
    mo.md(r"""
    # PsychoAnalyze
    *Interactive data simulation & analysis for psychophysics.*

    [Notebooks](https://nb.psychoanalyze.io) · [GitHub](https://github.com/psychoanalyze/psychoanalyze) · [Docs](https://docs.psychoanalyze.io)
    """)


@app.cell
def _(mo):
    # File upload
    file_upload = mo.ui.file(
        filetypes=[".csv", ".zip"],
        kind="area",
        label="Upload CSV/parquet with columns: **Block, Intensity, Result.** Your data stays in the browser.",
    )
    return (file_upload,)


@app.cell
def _(mo):
    load_sample_button = mo.ui.run_button(label="Load Sample Data")
    return (load_sample_button,)


@app.cell
def _(mo):
    # Input form using mo.ui.batch
    input_form = (
        mo.md(r"""
    ## Simulation Parameters

    **Link function:** $\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$

    **Model** {x_0} {k} {preset}

    **Stimulus** {n_levels}

    **Simulation** {n_trials} {n_blocks}
    """)
        .batch(
            x_0=mo.ui.number(value=0.0, step=0.1, label="x₀"),
            k=mo.ui.number(value=1.0, step=0.1, label="k"),
            preset=mo.ui.dropdown(
                options={
                    "standard": "Standard",
                    "non-standard": "Non Standard",
                    "2AFC": "2AFC",
                },
                value="standard",
                label="Preset",
            ),
            n_levels=mo.ui.number(value=7, start=2, stop=50, step=1, label="n levels"),
            n_trials=mo.ui.number(
                value=100, start=1, stop=10000, step=1, label="trials/block",
            ),
            n_blocks=mo.ui.number(value=5, start=1, stop=100, step=1, label="blocks"),
        )
        .form(submit_button_label="Generate")
    )
    return (input_form,)


@app.cell
def _(input_form):
    # Extract values from form (with defaults before submission)
    form_values = input_form.value if input_form.value is not None else {}
    x_0 = float(form_values.get("x_0") if form_values.get("x_0") is not None else 0.0)
    k = float(form_values.get("k") if form_values.get("k") is not None else 1.0)
    n_levels = int(
        form_values.get("n_levels") if form_values.get("n_levels") is not None else 7,
    )
    n_trials = int(
        form_values.get("n_trials") if form_values.get("n_trials") is not None else 100,
    )
    n_blocks = int(
        form_values.get("n_blocks") if form_values.get("n_blocks") is not None else 5,
    )
    return k, n_blocks, n_levels, n_trials, x_0


@app.cell
def _(k, logit, to_intercept, to_slope, x_0):
    # Compute stimulus range from model parameters
    intercept = to_intercept(x_0, k)
    slope = to_slope(k)
    min_x = (logit(0.01) - intercept) / slope
    max_x = (logit(0.99) - intercept) / slope
    return max_x, min_x


@app.cell
def _(max_x, min_x, mo):
    # Stimulus range info for display in left column
    stimulus_info = mo.md(f"**Stimulus range:** {min_x:.2f} to {max_x:.2f}")
    return (stimulus_info,)


@app.cell
def _(pl):
    from pathlib import Path as _Path

    def load_sample_trials() -> pl.DataFrame:
        """Load sample experimental data from data/trials.csv."""
        sample_path = _Path(__file__).parent / "data" / "trials.csv"
        df = pl.read_csv(sample_path)
        # Transform to expected format: Block, Intensity, Result
        df = df.with_columns(
            (pl.col("Date").cast(pl.Utf8) + "_" + pl.col("Amp2").cast(pl.Utf8)).alias(
                "block_key",
            ),
        )
        df = df.with_columns(
            pl.col("block_key").rank("dense").cast(pl.Int64).alias("Block") - 1,
        )
        df = df.with_columns(pl.col("Amp1").alias("Intensity"))
        df = df.with_columns((pl.col("Result") == 1).cast(pl.Int64).alias("Result"))
        return df.select(["Block", "Intensity", "Result"])

    return (load_sample_trials,)


@app.cell
def _(
    file_upload,
    generate_index,
    generate_trials,
    k,
    load_sample_button,
    load_sample_trials,
    max_x,
    min_x,
    n_blocks,
    n_levels,
    n_trials,
    process_upload_bytes,
    x_0,
):
    # Trials: from sample button, upload, or generate
    if load_sample_button.value:
        trials_df = load_sample_trials()
    elif file_upload.value and len(file_upload.value) > 0:
        raw = file_upload.contents(0)
        fname = file_upload.name(0) or ""
        if raw is not None:
            trials_df = process_upload_bytes(raw, fname)
        else:
            trials_df = generate_trials(
                n_trials=n_trials,
                options=generate_index(n_levels, [min_x, max_x]),
                params={"x_0": x_0, "k": k, "gamma": 0.0, "lambda": 0.0},
                n_blocks=n_blocks,
            )
    else:
        trials_df = generate_trials(
            n_trials=n_trials,
            options=generate_index(n_levels, [min_x, max_x]),
            params={"x_0": x_0, "k": k, "gamma": 0.0, "lambda": 0.0},
            n_blocks=n_blocks,
        )
    trials_df = trials_df.with_columns(pl.col("Intensity").cast(pl.Float64))
    return (trials_df,)


@app.cell
def _(mo, trials_df):
    # Slider to crop dataset at a specific trial number
    total_trials = len(trials_df)
    trial_crop_slider = mo.ui.slider(
        start=1,
        stop=total_trials,
        value=total_trials,
        step=1,
        label="Crop at trial",
        show_value=True,
    )
    return (trial_crop_slider,)


@app.cell
def _(trial_crop_slider, trials_df):
    # Apply trial crop
    crop_at = trial_crop_slider.value
    trials_cropped_df = trials_df.head(crop_at)
    return (trials_cropped_df,)


@app.cell
def _(block_fit, from_trials, pl, trials_cropped_df):
    # Points and blocks from cropped trials
    points_df = from_trials(trials_cropped_df)
    blocks_list = []
    for block_id in trials_cropped_df["Block"].unique().to_list():
        block_trials = trials_cropped_df.filter(pl.col("Block") == block_id)
        fit_result = block_fit(block_trials)
        fit_result["Block"] = block_id
        fit_result["gamma"] = 0.0
        fit_result["lambda"] = 0.0
        blocks_list.append(fit_result)
    blocks_df = pl.from_dicts(blocks_list)
    return blocks_df, points_df


@app.cell
def _(blocks_df, blocks_table, k, pl, x_0):
    # Selected block rows for plot (include Model)
    if blocks_table.value is not None and hasattr(blocks_table.value, "__len__"):
        try:
            selected_blocks_df = (
                blocks_table.value
                if isinstance(blocks_table.value, pl.DataFrame)
                else pl.from_dicts(blocks_table.value)
                if blocks_table.value
                else blocks_df
            )
        except Exception:
            selected_blocks_df = blocks_df
    else:
        selected_blocks_df = blocks_df
    # Build list of block dicts for curves: selected blocks + Model
    model_intercept = -x_0 / k
    model_slope = 1 / k
    block_rows = []
    if isinstance(selected_blocks_df, pl.DataFrame) and len(selected_blocks_df) > 0:
        for row in selected_blocks_df.iter_rows(named=True):
            block_rows.append(
                {
                    "Block": str(row.get("Block", "")),
                    "intercept": row.get("intercept", 0),
                    "slope": row.get("slope", 1),
                },
            )
    else:
        for row in blocks_df.iter_rows(named=True):
            block_rows.append(
                {
                    "Block": str(row["Block"]),
                    "intercept": row["intercept"],
                    "slope": row["slope"],
                },
            )
    block_rows.append(
        {"Block": "Model", "intercept": model_intercept, "slope": model_slope},
    )
    return (block_rows,)


@app.cell
def _(blocks_table, pl, points_df):
    # Filter points by selected blocks
    if blocks_table.value is not None:
        try:
            sel = (
                blocks_table.value
                if isinstance(blocks_table.value, pl.DataFrame)
                else pl.from_dicts(blocks_table.value)
                if blocks_table.value
                else None
            )
            if sel is not None and len(sel) > 0 and "Block" in sel.columns:
                block_ids = sel["Block"].to_list()
                points_filtered_df = points_df.filter(pl.col("Block").is_in(block_ids))
            else:
                points_filtered_df = points_df
        except Exception:
            points_filtered_df = points_df
    else:
        points_filtered_df = points_df
    return (points_filtered_df,)


@app.cell
def _(mo, points_filtered_df):
    # Points table
    points_table = mo.ui.table(
        points_filtered_df.to_pandas(),
        pagination=True,
        page_size=10,
        label="Points",
        format_mapping={
            "Intensity": "{:.2f}".format,
            "Hit Rate": "{:.2f}".format,
        },
    )
    return (points_table,)


@app.cell
def _(blocks_df, mo):
    # Blocks table with multi-selection
    blocks_table = mo.ui.table(
        blocks_df.to_pandas(),
        selection="multi",
        initial_selection=[0, 2] if len(blocks_df) > 2 else list(range(len(blocks_df))),
        label="Blocks",
        format_mapping={
            "intercept": "{:.2f}".format,
            "slope": "{:.2f}".format,
        },
    )
    return (blocks_table,)


@app.cell
def _(block_rows, expit, max_x, min_x, mo, np, pl, points_filtered_df, px):
    # Plot: scatter points + logistic curves
    x = np.linspace(min_x, max_x, 100)
    fits_list = []
    for blk in block_rows:
        y = expit(x * blk["slope"] + blk["intercept"])
        fits_list.append(
            pl.DataFrame(
                {
                    "Intensity": x,
                    "Hit Rate": y,
                    "Block": [blk["Block"]] * len(x),
                },
            ),
        )
    fits_df = pl.concat(fits_list)
    points_plot_df = points_filtered_df.with_columns(pl.col("Block").cast(pl.Utf8))
    fits_df = fits_df.with_columns(pl.col("Block").cast(pl.Utf8))
    fig = px.line(
        fits_df.to_pandas(),
        x="Intensity",
        y="Hit Rate",
        color="Block",
    )
    results_fig = px.scatter(
        points_plot_df.to_pandas(),
        x="Intensity",
        y="Hit Rate",
        size="n trials",
        color="Block",
        template="plotly_white",
    )
    for trace in results_fig.data:
        fig.add_trace(trace)
    plot_ui = mo.ui.plotly(fig)
    return (plot_ui,)


@app.cell
def _(file_upload, input_form, load_sample_button, mo, stimulus_info):
    # Build tab content based on selected mode
    batch_content = mo.vstack(
        [
            mo.md("### Batch Mode"),
            mo.md("Upload your experimental data or load sample data."),
            file_upload,
            mo.md("**Or try with sample experimental data:**"),
            load_sample_button,
        ],
        gap=1,
    )

    simulation_content = mo.vstack(
        [
            mo.md("### Simulation Mode"),
            input_form,
            stimulus_info,
        ],
        gap=1,
    )

    online_content = mo.vstack(
        [
            mo.md("### Online Mode"),
            mo.md(
                "*Coming soon:* Connect to live data streams "
                "for real-time psychophysics experiments.",
            ),
            mo.md("""
    **Planned features:**
    - WebSocket connection to experiment hardware
    - Real-time threshold estimation
    - Adaptive staircase procedures
            """),
        ],
        gap=1,
    )

    input_tabs = mo.ui.tabs(
        {
            "Batch": batch_content,
            "Simulation": simulation_content,
            "Online": online_content,
        },
    )
    return (input_tabs,)


@app.cell
def _(blocks_table, input_tabs, mo, plot_ui, points_table, trial_crop_slider):
    # 3-column layout: Input | Visualization | Output
    left_column = mo.vstack(
        [
            input_tabs,
        ],
        gap=1,
    )

    # Center content varies by selected mode
    selected_mode = input_tabs.value

    if selected_mode == "Batch":
        center_column = mo.vstack(
            [
                mo.md("## Batch Analysis"),
                mo.md(
                    r"$\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$",
                ),
                trial_crop_slider,
                plot_ui,
            ],
            gap=1,
        )
    elif selected_mode == "Online":
        center_column = mo.vstack(
            [
                mo.md("## Online Mode"),
                mo.md(
                    "Real-time visualization will appear here "
                    "when connected to an experiment.",
                ),
                mo.md(
                    "*Select Batch or Simulation mode to view data.*",
                ),
            ],
            gap=1,
        )
    else:  # Simulation (default)
        center_column = mo.vstack(
            [
                mo.md("## Simulation Results"),
                mo.md(
                    r"$\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$",
                ),
                trial_crop_slider,
                plot_ui,
            ],
            gap=1,
        )

    right_column = mo.vstack(
        [
            mo.md("## Blocks"),
            blocks_table,
            mo.md("## Points"),
            points_table,
        ],
        gap=1,
    )

    mo.hstack(
        [left_column, center_column, right_column],
        widths=[1, 2, 1],
        gap=2,
    )


if __name__ == "__main__":
    app.run()
