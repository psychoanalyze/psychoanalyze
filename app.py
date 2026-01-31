"""PsychoAnalyze dashboard as a marimo notebook.

Interactive data simulation & analysis for psychophysics.
Replaces the former Dash dashboard (removed).
"""

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full", app_title="PsychoAnalyze")


@app.cell
def _():
    import io
    import zipfile

    import altair as alt
    import arviz as az
    import marimo as mo
    import numpy as np
    import polars as pl
    from scipy.special import expit, logit

    from psychoanalyze.data import blocks as pa_blocks
    from psychoanalyze.data import points as pa_points
    from psychoanalyze.data import subject as subject_utils
    from psychoanalyze.data import trials as pa_trials
    from psychoanalyze.data.logistic import to_intercept, to_slope
    return (
        alt,
        az,
        expit,
        io,
        logit,
        mo,
        np,
        pa_blocks,
        pa_points,
        pa_trials,
        pl,
        subject_utils,
        to_intercept,
        to_slope,
        zipfile,
    )


@app.cell
def _(az, io, pa_blocks, pa_points, pa_trials, pl, subject_utils, zipfile):
    generate_index = pa_points.generate_index

    def generate_trials(
        n_trials: int,
        options: list[float],
        params: dict,
        n_blocks: int,
    ) -> pl.DataFrame:
        trials_df = pa_trials.generate(
            n_trials=n_trials,
            options=options,
            params=params,
            n_blocks=n_blocks,
        )
        return subject_utils.ensure_subject_column(trials_df)


    def from_trials(trials_df: pl.DataFrame) -> pl.DataFrame:
        trials_df = subject_utils.ensure_subject_column(trials_df)
        return pa_points.from_trials(trials_df)

    def block_fit(
        trials_df: pl.DataFrame,
    ) -> tuple[dict[str, float], az.InferenceData]:
        fit_idata = pa_blocks.fit(
            trials_df,
            draws=300,
            tune=300,
            chains=1,
            target_accept=0.9,
        )
        summary = pa_blocks.summarize_fit(fit_idata)
        return (
            {
                "intercept": summary["intercept"],
                "slope": summary["slope"],
            },
            fit_idata,
        )


    def process_upload_bytes(contents: bytes, filename: str) -> pl.DataFrame:
        if "zip" in filename:
            with zipfile.ZipFile(io.BytesIO(contents)) as z:
                return pl.read_csv(z.open("trials.csv"))
        if "parquet" in filename or filename.endswith(".pq"):
            return pl.read_parquet(io.BytesIO(contents))
        return pl.read_csv(io.BytesIO(contents))
    return (
        block_fit,
        from_trials,
        generate_index,
        generate_trials,
        process_upload_bytes,
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
        filetypes=[".csv", ".zip", ".parquet", ".pq"],
        kind="area",
        label="Upload CSV/parquet with columns: **Block, Intensity, Result** (optional: **Subject**). Your data stays in the browser.",
    )
    return (file_upload,)


@app.cell
def _(mo):
    load_sample_button = mo.ui.run_button(label="Load Sample Data")
    return (load_sample_button,)


@app.cell
def _(mo):
    preset_dropdown = mo.ui.dropdown(
        options={
            "standard": "Standard",
            "non-standard": "Non Standard",
            "2AFC": "2AFC",
        },
        value="standard",
        label="Preset",
    )
    link_function = mo.ui.dropdown(
        options={
            "expit": "Logistic",
        },
        value="expit",
        label="Link function",
    )
    show_equation = mo.ui.checkbox(label="Show F(x)", value=False)
    return link_function, preset_dropdown, show_equation


@app.cell
def _(mo, preset_dropdown):
    _presets = {
        "standard": [0.0, 1.0, 0.0, 0.0],
        "non-standard": [10.0, 2.0, 0.2, 0.1],
        "2AFC": [0.0, 1.0, 0.5, 0.0],
    }
    _preset_free = {
        "standard": [True, True, True, True],
        "non-standard": [True, True, True, True],
        "2AFC": [True, True, False, True],
    }
    _preset_key = preset_dropdown.value or "standard"
    _preset_values = _presets.get(_preset_key, _presets["standard"])
    _preset_free_values = _preset_free.get(_preset_key, _preset_free["standard"])

    x_0_free = mo.ui.checkbox(value=_preset_free_values[0], label="x₀ free")
    x_0 = mo.ui.number(value=_preset_values[0], step=0.1, label="x₀")
    k_free = mo.ui.checkbox(value=_preset_free_values[1], label="k free")
    k = mo.ui.number(value=_preset_values[1], step=0.1, label="k")
    gamma_free = mo.ui.checkbox(value=_preset_free_values[2], label="γ free")
    gamma = mo.ui.number(value=_preset_values[2], step=0.01, label="γ")
    lambda_free = mo.ui.checkbox(value=_preset_free_values[3], label="λ free")
    lambda_ = mo.ui.number(value=_preset_values[3], step=0.01, label="λ")
    n_levels = mo.ui.number(value=7, start=2, stop=50, step=1, label="n levels")
    n_trials = mo.ui.number(
        value=100,
        start=1,
        stop=10000,
        step=1,
        label="trials/block",
    )
    n_blocks = mo.ui.number(value=5, start=1, stop=100, step=1, label="blocks")

    input_form = (
        mo.md(r"""
    ## Simulation Parameters

    **Link function:** $\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$

    **Model** {x_0_free} {x_0} {k_free} {k} {gamma_free} {gamma} {lambda_free} {lambda_}

    **Stimulus** {n_levels}

    **Simulation** {n_trials} {n_blocks}
    """)
        .batch(
            x_0_free=x_0_free,
            x_0=x_0,
            k_free=k_free,
            k=k,
            gamma_free=gamma_free,
            gamma=gamma,
            lambda_free=lambda_free,
            lambda_=lambda_,
            n_levels=n_levels,
            n_trials=n_trials,
            n_blocks=n_blocks,
        )
        .form(submit_button_label="Generate")
    )
    return gamma, input_form, k, lambda_, n_blocks, n_levels, n_trials, x_0


@app.cell
def _(k, logit, to_intercept, to_slope, x_0):
    # Compute stimulus range from model parameters
    intercept = to_intercept(x_0.value, k.value)
    slope = to_slope(k.value)
    min_x = (logit(0.01) - intercept) / slope
    max_x = (logit(0.99) - intercept) / slope
    return max_x, min_x


@app.cell
def _(max_x, min_x, mo):
    # Stimulus range info for display in left column
    stimulus_info = mo.md(f"**Stimulus range:** {min_x:.2f} to {max_x:.2f}")
    return (stimulus_info,)


@app.cell
def _(mo, show_equation):
    equation_abstracted = r"""
    $$
    \psi(x) = \gamma + (1 - \gamma - \lambda)F(x)
    $$
    """
    equation_expanded = r"""
    $$
    \psi(x) = \frac{\gamma + (1 - \gamma - \lambda)}{1 + e^{-k(x - x_0)}}
    $$
    """
    plot_equation = mo.md(
        equation_expanded if show_equation.value else equation_abstracted,
    )
    return (plot_equation,)


@app.cell
def _(pl, subject_utils):
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
        df = df.select(["Block", "Intensity", "Result"])
        return subject_utils.ensure_subject_column(df)
    return (load_sample_trials,)


@app.cell
def _(
    file_upload,
    gamma,
    generate_index,
    generate_trials,
    k,
    lambda_,
    load_sample_button,
    load_sample_trials,
    max_x,
    min_x,
    n_blocks,
    n_levels,
    n_trials,
    pl,
    process_upload_bytes,
    subject_utils,
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
                n_trials=n_trials.value,
                options=generate_index(n_levels.value, [min_x, max_x]),
                params={
                    "x_0": x_0.value,
                    "k": k.value,
                    "gamma": gamma.value,
                    "lambda": lambda_.value,
                },
                n_blocks=n_blocks.value,
            )
    else:
        trials_df = generate_trials(
            n_trials=n_trials.value,
            options=generate_index(n_levels.value, [min_x, max_x]),
            params={
                "x_0": x_0.value,
                "k": k.value,
                "gamma": gamma.value,
                "lambda": lambda_.value,
            },
            n_blocks=n_blocks.value,
        )
    trials_df = subject_utils.ensure_subject_column(trials_df)
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
    block_fit_map: dict[tuple[str, int], object] = {}
    block_keys = trials_cropped_df.select(["Subject", "Block"]).unique()
    for block_key_row in block_keys.iter_rows(named=True):
        block_id = block_key_row["Block"]
        subject_id = block_key_row["Subject"]
        block_trials = trials_cropped_df.filter(
            (pl.col("Block") == block_id) & (pl.col("Subject") == subject_id),
        )
        fit_summary, _block_idata = block_fit(block_trials)
        fit_summary["Block"] = block_id
        fit_summary["Subject"] = subject_id
        fit_summary["gamma"] = 0.0
        fit_summary["lambda"] = 0.0
        block_fit_map[(str(subject_id), int(block_id))] = _block_idata
        blocks_list.append(fit_summary)
    blocks_df = pl.from_dicts(blocks_list)
    return block_fit_map, blocks_df, points_df


@app.cell
def _(
    block_fit_map: dict[tuple[str, int], object],
    blocks_df,
    blocks_table,
    k,
    pl,
    x_0,
):
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
    model_intercept = -x_0.value / k.value
    model_slope = 1 / k.value
    def block_label(row: dict) -> str:
        subject = row.get("Subject")
        block = row.get("Block")
        if subject is None or subject == "":
            return str(block)
        return f"{subject}-{block}"

    block_rows = []
    if isinstance(selected_blocks_df, pl.DataFrame) and len(selected_blocks_df) > 0:
        for block_row in selected_blocks_df.iter_rows(named=True):
            subject = str(block_row.get("Subject", ""))
            block = int(block_row.get("Block", 0))
            block_rows.append(
                {
                    "Block": block_label(block_row),
                    "intercept": block_row.get("intercept", 0),
                    "slope": block_row.get("slope", 1),
                    "idata": block_fit_map.get((subject, block)),
                },
            )
    else:
        for block_row in blocks_df.iter_rows(named=True):
            subject = str(block_row.get("Subject", ""))
            block = int(block_row.get("Block", 0))
            block_rows.append(
                {
                    "Block": block_label(block_row),
                    "intercept": block_row["intercept"],
                    "slope": block_row["slope"],
                    "idata": block_fit_map.get((subject, block)),
                },
            )
    block_rows.append(
        {
            "Block": "Model",
            "intercept": model_intercept,
            "slope": model_slope,
            "idata": None,
        },
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
                if "Subject" in sel.columns:
                    selected_pairs = sel.select(["Subject", "Block"]).to_dicts()
                    points_filtered_df = points_df.filter(
                        pl.struct(["Subject", "Block"]).is_in(selected_pairs),
                    )
                else:
                    block_ids = sel["Block"].to_list()
                    points_filtered_df = points_df.filter(
                        pl.col("Block").is_in(block_ids),
                    )
            else:
                points_filtered_df = points_df
        except Exception:
            points_filtered_df = points_df
    else:
        points_filtered_df = points_df
    return (points_filtered_df,)


@app.cell
def _(expit, link_function):
    link_fn = expit if link_function.value == "expit" else expit
    return (link_fn,)


@app.cell
def _(mo, n_levels, points_filtered_df):
    # Points table
    points_table = mo.ui.table(
        points_filtered_df.to_pandas(),
        pagination=True,
        page_size=n_levels.value,
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
def _(
    alt,
    block_rows,
    link_fn,
    max_x,
    min_x,
    mo,
    np,
    pa_blocks,
    pl,
    points_filtered_df,
):
    # Plot: scatter points + logistic curves
    x = np.linspace(min_x, max_x, 100)
    fits_list = []
    bands_list = []
    for blk in block_rows:
        y = link_fn(x * blk["slope"] + blk["intercept"])
        fits_list.append(
            pl.DataFrame(
                {
                    "Intensity": x,
                    "Hit Rate": y,
                    "Series": [blk["Block"]] * len(x),
                },
            ),
        )
        _block_idata = blk.get("idata")
        if _block_idata is not None and blk["Block"] != "Model":
            band_df = pa_blocks.curve_credible_band(_block_idata, x, hdi_prob=0.9)
            band_df = band_df.with_columns(pl.lit(blk["Block"]).alias("Series"))
            bands_list.append(band_df)
    fits_df = pl.concat(fits_list)
    bands_df = (
        pl.concat(bands_list)
        if len(bands_list) > 0
        else pl.DataFrame({"Intensity": [], "lower": [], "upper": [], "Series": []})
    )
    points_plot_df = points_filtered_df.with_columns(
        (
            pl.col("Subject").cast(pl.Utf8)
            + "-"
            + pl.col("Block").cast(pl.Utf8)
        ).alias("Series"),
    )
    fits_df = fits_df.with_columns(pl.col("Series").cast(pl.Utf8))
    fits_pd = fits_df.to_pandas()
    bands_pd = bands_df.to_pandas()
    points_pd = points_plot_df.to_pandas()
    band_chart = (
        alt.Chart(bands_pd)
        .mark_area(opacity=0.2)
        .encode(
            x=alt.X("Intensity:Q"),
            y=alt.Y("lower:Q"),
            y2=alt.Y2("upper:Q"),
            color=alt.Color("Series:N"),
        )
    )
    line_chart = (
        alt.Chart(fits_pd)
        .mark_line()
        .encode(
            x=alt.X("Intensity:Q"),
            y=alt.Y("Hit Rate:Q"),
            color=alt.Color("Series:N"),
        )
    )
    points_chart = (
        alt.Chart(points_pd)
        .mark_point(filled=True)
        .encode(
            x=alt.X("Intensity:Q"),
            y=alt.Y("Hit Rate:Q"),
            size=alt.Size("n trials:Q"),
            color=alt.Color("Series:N"),
            tooltip=["Series:N", "Intensity:Q", "Hit Rate:Q", "n trials:Q"],
        )
    )
    plot_layers = [line_chart, points_chart]
    if len(bands_pd) > 0:
        plot_layers.insert(0, band_chart)
    plot_chart = alt.layer(*plot_layers).resolve_scale(color="shared").interactive()
    plot_ui = mo.ui.altair_chart(plot_chart)
    return (plot_ui,)


@app.cell
def _(blocks_df, mo, pl, points_filtered_df, trials_cropped_df):
    import io as _io
    import tempfile
    import zipfile as _zipfile
    from datetime import datetime
    from pathlib import Path

    import duckdb


    def build_csv_zip(
        points_df: pl.DataFrame,
        blocks_df: pl.DataFrame,
        trials_df: pl.DataFrame,
    ) -> bytes:
        zip_buffer = _io.BytesIO()
        with _zipfile.ZipFile(
            zip_buffer,
            mode="a",
            compression=_zipfile.ZIP_DEFLATED,
            allowZip64=False,
        ) as zip_file:
            for level, level_df in {
                "points": points_df,
                "blocks": blocks_df,
                "trials": trials_df,
            }.items():
                csv_buffer = _io.StringIO()
                level_df.write_csv(csv_buffer)
                zip_file.writestr(f"{level}.csv", csv_buffer.getvalue())
        zip_buffer.seek(0)
        return zip_buffer.read()


    def build_json(points_df: pl.DataFrame) -> bytes:
        return points_df.to_pandas().to_json().encode("utf-8")


    def build_parquet(points_df: pl.DataFrame) -> bytes:
        buffer = _io.BytesIO()
        points_df.write_parquet(buffer)
        buffer.seek(0)
        return buffer.read()


    def build_duckdb(points_df: pl.DataFrame) -> bytes:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "psychoanalyze.duckdb"
            connection = duckdb.connect(str(db_path))
            connection.register("points_df", points_df.to_pandas())
            connection.execute("CREATE TABLE points AS SELECT * FROM points_df")
            connection.close()
            return db_path.read_bytes()


    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M")
    csv_zip = build_csv_zip(points_filtered_df, blocks_df, trials_cropped_df)
    json_bytes = build_json(points_filtered_df)
    parquet_bytes = build_parquet(points_filtered_df)
    duckdb_bytes = build_duckdb(points_filtered_df)

    data_downloads = mo.vstack(
        [
            mo.download(
                csv_zip,
                filename=f"{timestamp}_psychoanalyze.zip",
                label="Download CSV (zip)",
            ),
            mo.download(json_bytes, filename="data.json", label="Download JSON"),
            mo.download(
                parquet_bytes,
                filename="data.parquet",
                label="Download Parquet",
            ),
            mo.download(
                duckdb_bytes,
                filename="psychoanalyze.duckdb",
                label="Download DuckDB",
            ),
        ],
        gap=1,
    )
    return (data_downloads,)


@app.cell
def _(
    file_upload,
    input_form,
    link_function,
    load_sample_button,
    mo,
    preset_dropdown,
    show_equation,
    stimulus_info,
):
    # Build tab content based on selected mode
    batch_content = mo.vstack(
        [
            mo.md("### Batch Mode"),
            mo.md("Upload your experimental data or load sample data."),
            file_upload,
            mo.md("**Or try with sample experimental data:**"),
            load_sample_button,
            mo.md("### Link Function"),
            link_function,
            show_equation,
            mo.md("### Model Parameters"),
            preset_dropdown,
            input_form,
            stimulus_info,
        ],
        gap=1,
    )

    simulation_content = mo.vstack(
        [
            mo.md("### Simulation Mode"),
            mo.md("### Link Function"),
            link_function,
            show_equation,
            mo.md("### Model Parameters"),
            preset_dropdown,
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
def _(
    blocks_table,
    data_downloads,
    input_tabs,
    mo,
    plot_equation,
    plot_ui,
    points_table,
    trial_crop_slider,
):
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
                plot_equation,
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
                plot_equation,
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
            mo.md("## Download Data"),
            data_downloads,
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
