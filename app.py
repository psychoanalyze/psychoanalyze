"""PsychoAnalyze dashboard as a marimo notebook.

Interactive data simulation & analysis for psychophysics.
Replaces the former Dash dashboard (removed).
"""

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full", app_title="PsychoAnalyze")


@app.cell
def _(
    blocks_chart,
    data_downloads,
    input_tabs,
    mo,
    plot_equation,
    plot_ui,
    step_chart,
    step_info,
    step_mode_toggle,
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
        # Show step-by-step view or regular view based on toggle
        if step_mode_toggle.value and step_chart is not None:
            center_column = mo.vstack(
                [
                    mo.md("## Step-by-Step Simulation"),
                    step_info,
                    step_chart,
                    plot_equation,
                ],
                gap=1,
            )
        else:
            center_column = mo.vstack(
                [
                    mo.md("## Simulation Results"),
                    plot_equation,
                    plot_ui,
                ],
                gap=1,
            )

    right_column = mo.vstack(
        [
            mo.md("## Blocks"),
            blocks_chart,
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


@app.cell
def _():
    import hashlib
    import io
    import json
    import zipfile
    from pathlib import Path

    import altair as alt
    import arviz as az
    import marimo as mo
    import numpy as np
    import polars as pl
    from scipy.special import expit, logit

    from psychoanalyze.data import hierarchical as pa_hierarchical
    from psychoanalyze.data import points as pa_points
    from psychoanalyze.data import subject as subject_utils
    from psychoanalyze.data import trials as pa_trials
    from psychoanalyze.data.logistic import to_intercept, to_slope
    return (
        Path,
        alt,
        az,
        expit,
        hashlib,
        io,
        json,
        logit,
        mo,
        np,
        pa_hierarchical,
        pa_points,
        pa_trials,
        pl,
        subject_utils,
        to_intercept,
        to_slope,
        zipfile,
    )


@app.cell
def _(Path, az, cache_root, hashlib, io, json, mo, np, pa_hierarchical, pl):
    def normalize_trials_for_hash(trials_df: pl.DataFrame) -> pl.DataFrame:
        preferred_cols = [
            col
            for col in ["Subject", "Block", "Intensity", "Result"]
            if col in trials_df.columns
        ]
        cols = preferred_cols if preferred_cols else trials_df.columns
        return trials_df.select(cols).sort(cols)

    def trials_cache_key(
        trials_df: pl.DataFrame,
        fit_params: dict[str, float | int | None],
    ) -> str:
        normalized = normalize_trials_for_hash(trials_df)
        buffer = io.BytesIO()
        normalized.write_csv(buffer)
        digest = hashlib.sha256()
        digest.update(buffer.getvalue())
        digest.update(json.dumps(fit_params, sort_keys=True).encode())
        return digest.hexdigest()

    def idata_cache_path(cache_key: str) -> Path:
        return cache_root / f"idata-{cache_key}.nc"

    @mo.cache
    def cached_hierarchical_fit(
        trials_df: pl.DataFrame,
        cache_key: str,
        fit_params: dict[str, float | int | None],
    ) -> tuple[dict[str, float | np.ndarray], az.InferenceData]:
        cache_path = idata_cache_path(cache_key)
        if cache_path.exists():
            idata = az.from_netcdf(cache_path)
        else:
            idata = pa_hierarchical.fit(trials_df, **fit_params)
            idata.to_netcdf(cache_path)
        summary = pa_hierarchical.summarize_fit(idata)
        return summary, idata
    return cached_hierarchical_fit, trials_cache_key


@app.cell
def _(io, np, pa_points, pa_trials, pl, subject_utils, zipfile):
    generate_index = pa_points.generate_index

    def sample_params_from_priors(random_seed: int | None = None) -> dict[str, float]:
        """Sample parameters from hierarchical model priors.

        Returns a dict with keys: x_0, k, gamma, lambda
        """
        rng = np.random.default_rng(random_seed)

        # Sample hyperparameters
        mu_intercept = rng.normal(0.0, 2.5)
        sigma_intercept = np.abs(rng.normal(0.0, 2.5))
        mu_slope = np.abs(rng.normal(0.0, 2.5))
        sigma_slope = np.abs(rng.normal(0.0, 2.5))

        # Sample block-level params from hyperpriors
        intercept = rng.normal(mu_intercept, sigma_intercept)
        slope = np.abs(rng.normal(mu_slope, sigma_slope))

        # Sample gamma and lambda from Beta(1, 19) - mode near 0.05
        gamma = rng.beta(1.0, 19.0)
        lambda_ = rng.beta(1.0, 19.0)

        # Convert intercept/slope to x_0/k parameterization
        # threshold x_0 = -intercept / slope
        # k = slope (steepness)
        k = slope
        x_0 = -intercept / slope if slope != 0 else 0.0

        return {
            "x_0": x_0,
            "k": k,
            "gamma": gamma,
            "lambda": lambda_,
        }

    def generate_trials(
        n_trials: int,
        options: list[float],
        params: dict,
        n_blocks: int,
        n_subjects: int = 1,
        use_random_params: bool = False,
        random_seed: int | None = None,
        sampling_method: str = "constant_stimuli",
    ) -> tuple[pl.DataFrame, dict[tuple[str, int], dict]]:
        """Generate trials and return both data and block-specific parameters.

        Args:
            use_random_params: If True, ignore params and generate from priors
            random_seed: Random seed for parameter generation
            sampling_method: Either "constant_stimuli" (random from options) 
                            or "adaptive" (Expected Improvement)

        Returns:
            (trials_df, ground_truth_params_map)
            where ground_truth_params_map keys are (subject_id, block_id) tuples
        """
        frames = []
        ground_truth_params_map = {}
        rng = np.random.default_rng(random_seed)

        for subject_idx in range(n_subjects):
            subject_id = (
                chr(ord("A") + subject_idx) if subject_idx < 26 else f"S{subject_idx}"
            )

            for block_id in range(n_blocks):
                # Generate parameters for this block
                if use_random_params:
                    block_seed = None if random_seed is None else (random_seed + subject_idx * 1000 + block_id)
                    block_params = sample_params_from_priors(block_seed)
                else:
                    # Use provided params with random variation per block
                    block_params = params.copy()
                    block_params["x_0"] = params["x_0"] + rng.normal(0, 0.5)

                ground_truth_params_map[(subject_id, block_id)] = block_params

                # Generate trials for this block using specified sampling method
                trial_seed = None if random_seed is None else (random_seed + subject_idx * 10000 + block_id * 100)
                block_trials = pa_trials.generate(
                    n_trials=n_trials,
                    options=options,
                    params=block_params,
                    n_blocks=1,
                    sampling_method=sampling_method,
                    random_seed=trial_seed,
                )
                block_trials = block_trials.with_columns(
                    pl.lit(subject_id).alias("Subject"),
                    pl.lit(block_id).alias("Block"),
                )
                frames.append(block_trials)

        return (
            pl.concat(frames) if frames else pl.DataFrame(),
            ground_truth_params_map,
        )

    def from_trials(trials_df: pl.DataFrame) -> pl.DataFrame:
        trials_df = subject_utils.ensure_subject_column(trials_df)
        return pa_points.from_trials(trials_df)

    def process_upload_bytes(contents: bytes, filename: str) -> pl.DataFrame:
        if "zip" in filename:
            with zipfile.ZipFile(io.BytesIO(contents)) as z:
                return pl.read_csv(z.open("trials.csv"))
        if "parquet" in filename or filename.endswith(".pq"):
            return pl.read_parquet(io.BytesIO(contents))
        return pl.read_csv(io.BytesIO(contents))
    return from_trials, generate_index, generate_trials, process_upload_bytes


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
        label="Upload CSV/parquet with columns: **Block, Intensity, Result** (optional: **Subject**). Data stays on this machine.",
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
def _(mo):
    fit_draws = mo.ui.number(value=300, start=50, stop=5000, step=50, label="draws")
    fit_tune = mo.ui.number(value=300, start=50, stop=5000, step=50, label="tune")
    fit_chains = mo.ui.number(value=4, start=1, stop=4, step=1, label="chains")
    fit_target_accept = mo.ui.number(
        value=0.9,
        start=0.5,
        stop=0.99,
        step=0.01,
        label="target_accept",
    )
    fit_random_seed = mo.ui.number(
        value=0,
        start=0,
        stop=99999,
        step=1,
        label="random seed (0 = random)",
    )

    fit_settings = mo.vstack(
        [
            mo.md("### Advanced Fitting"),
            fit_draws,
            fit_tune,
            fit_chains,
            fit_target_accept,
            fit_random_seed,
        ],
        gap=1,
    )
    return (
        fit_chains,
        fit_draws,
        fit_random_seed,
        fit_settings,
        fit_target_accept,
        fit_tune,
    )


@app.cell
def _(mo):
    sampling_method_dropdown = mo.ui.dropdown(
        options={
            "constant_stimuli": "Method of Constant Stimuli",
            "adaptive": "Adaptive (Fisher Information)",
            "quest": "QUEST/Psi (Bayesian)",
        },
        value="constant_stimuli",
        label="Sampling Method",
    )
    return (sampling_method_dropdown,)


@app.cell
def _(mo):
    # Step-by-step visualization controls
    step_mode_toggle = mo.ui.checkbox(label="Step-by-step mode", value=False)
    return (step_mode_toggle,)


@app.cell
def _(mo, n_trials, step_mode_toggle):
    # Trial step slider - only active when step mode is enabled
    max_trials = n_trials.value if hasattr(n_trials, 'value') else 100
    trial_step_slider = mo.ui.slider(
        start=1,
        stop=max(max_trials, 1),
        step=1,
        value=max(max_trials, 1),
        label="Trial",
        show_value=True,
    )
    # Auto-play button for animation
    auto_play_button = mo.ui.run_button(label="▶ Play", kind="neutral")
    return auto_play_button, trial_step_slider


@app.cell
def _(
    alt,
    expit,
    generate_index,
    ground_truth_params,
    max_x,
    min_x,
    mo,
    n_levels,
    np,
    pl,
    step_mode_toggle,
    trial_step_slider,
    trials_df,
):
    """Create step-by-step visualization showing trials accumulating one at a time."""
    
    # Only compute if step mode is enabled and we're in simulation mode
    if not step_mode_toggle.value or "Trial" not in trials_df.columns:
        step_chart = None
        step_info = mo.md("")
    else:
        current_step = trial_step_slider.value
        
        # Get first block's data for step-by-step view
        first_subject = trials_df["Subject"].unique().to_list()[0]
        first_block = trials_df.filter(pl.col("Subject") == first_subject)["Block"].unique().to_list()[0]
        block_trials = trials_df.filter(
            (pl.col("Subject") == first_subject) & (pl.col("Block") == first_block)
        ).sort("Trial")
        
        # Filter to trials up to current step
        trials_up_to_step = block_trials.filter(pl.col("Trial") < current_step)
        current_trial = block_trials.filter(pl.col("Trial") == current_step - 1)
        
        # Get all intensity options for the histogram
        all_options = generate_index(n_levels.value, [min_x, max_x])
        
        # Compute cumulative hit rates at each intensity
        if len(trials_up_to_step) > 0:
            points_cumulative = trials_up_to_step.group_by("Intensity").agg([
                pl.mean("Result").alias("Hit Rate"),
                pl.len().alias("n_trials"),
            ]).sort("Intensity")
            
            # Create sampling distribution for histogram (include all options)
            sampling_counts = trials_up_to_step.group_by("Intensity").len()
            # Merge with all options to show zeros
            all_options_df = pl.DataFrame({"Intensity": all_options})
            sampling_dist = all_options_df.join(
                sampling_counts, on="Intensity", how="left"
            ).with_columns(
                pl.col("len").fill_null(0).alias("Count")
            ).select(["Intensity", "Count"]).sort("Intensity")
        else:
            points_cumulative = pl.DataFrame({
                "Intensity": [],
                "Hit Rate": [],
                "n_trials": [],
            })
            sampling_dist = pl.DataFrame({
                "Intensity": all_options,
                "Count": [0] * len(all_options),
            })
        
        # Get ground truth parameters for this block
        gt_params = ground_truth_params.get((first_subject, first_block))
        
        # Create x values for fitted curve
        x_curve = np.linspace(min_x, max_x, 100)
        
        # === MAIN PSYCHOMETRIC CHART ===
        chart_layers = []
        
        # Ground truth curve (dashed)
        if gt_params is not None:
            gt_intercept = -gt_params["x_0"] * gt_params["k"]
            gt_slope = gt_params["k"]
            y_gt = expit(gt_slope * x_curve + gt_intercept)
            gt_df = pl.DataFrame({
                "Intensity": x_curve,
                "Hit Rate": y_gt,
                "Type": ["Ground Truth"] * len(x_curve),
            }).to_pandas()
            gt_line = alt.Chart(gt_df).mark_line(
                strokeDash=[5, 5],
                color="gray",
                strokeWidth=2,
            ).encode(
                x=alt.X("Intensity:Q", title="Intensity"),
                y=alt.Y("Hit Rate:Q", title="Hit Rate", scale=alt.Scale(domain=[0, 1])),
            )
            chart_layers.append(gt_line)
        
        # Cumulative points (sized by n_trials)
        if len(points_cumulative) > 0:
            points_pd = points_cumulative.to_pandas()
            points_scatter = alt.Chart(points_pd).mark_point(
                filled=True,
                color="steelblue",
            ).encode(
                x=alt.X("Intensity:Q"),
                y=alt.Y("Hit Rate:Q"),
                size=alt.Size("n_trials:Q", scale=alt.Scale(range=[50, 300]), title="Trials"),
                tooltip=["Intensity:Q", "Hit Rate:Q", "n_trials:Q"],
            )
            chart_layers.append(points_scatter)
        
        # Current trial highlight (large marker with different color)
        if len(current_trial) > 0:
            current_intensity = float(current_trial["Intensity"][0])
            current_result = int(current_trial["Result"][0])
            current_pd = pl.DataFrame({
                "Intensity": [current_intensity],
                "Result": [current_result],
                "label": [f"Trial {current_step}: {'Hit' if current_result else 'Miss'}"],
            }).to_pandas()
            
            # Vertical line at current intensity
            vline = alt.Chart(current_pd).mark_rule(
                color="red",
                strokeWidth=2,
                strokeDash=[4, 4],
            ).encode(
                x=alt.X("Intensity:Q"),
            )
            chart_layers.append(vline)
            
            # Current trial marker
            current_marker = alt.Chart(current_pd).mark_point(
                filled=True,
                size=200,
                color="red",
                shape="diamond",
            ).encode(
                x=alt.X("Intensity:Q"),
                y=alt.Y("Result:Q", scale=alt.Scale(domain=[0, 1])),
                tooltip=["label:N", "Intensity:Q"],
            )
            chart_layers.append(current_marker)
        
        # === SAMPLING DISTRIBUTION HISTOGRAM ===
        sampling_pd = sampling_dist.to_pandas()
        # Highlight current intensity in histogram
        if len(current_trial) > 0:
            current_intensity = float(current_trial["Intensity"][0])
            sampling_pd["is_current"] = sampling_pd["Intensity"].apply(
                lambda x: abs(x - current_intensity) < 0.01
            )
        else:
            sampling_pd["is_current"] = False
        
        histogram = alt.Chart(sampling_pd).mark_bar().encode(
            x=alt.X("Intensity:Q", title="Intensity"),
            y=alt.Y("Count:Q", title="Samples"),
            color=alt.condition(
                alt.datum.is_current,
                alt.value("red"),
                alt.value("steelblue"),
            ),
            tooltip=["Intensity:Q", "Count:Q"],
        ).properties(
            width=500,
            height=100,
            title="Sampling Distribution",
        )
        
        # Combine all layers for main chart
        if chart_layers:
            main_chart = alt.layer(*chart_layers).properties(
                width=500,
                height=250,
                title=f"Trial {current_step} of {len(block_trials)}",
            )
            # Stack main chart and histogram vertically
            combined_chart = alt.vconcat(main_chart, histogram).resolve_scale(
                x="shared"
            )
            step_chart = mo.ui.altair_chart(combined_chart)
        else:
            step_chart = mo.ui.altair_chart(histogram)
        
        # Info about current trial
        if len(current_trial) > 0:
            current_intensity = float(current_trial["Intensity"][0])
            current_result = "Hit ✓" if int(current_trial["Result"][0]) else "Miss ✗"
            step_info = mo.callout(
                mo.md(f"**Trial {current_step}**: Intensity = {current_intensity:.2f} → {current_result}"),
                kind="success" if "Hit" in current_result else "warn",
            )
        else:
            step_info = mo.md("")
    
    return step_chart, step_info


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

    n_levels = mo.ui.number(value=7, start=2, stop=50, step=1, label="n levels")
    n_trials = mo.ui.number(
        value=100,
        start=1,
        stop=10000,
        step=1,
        label="trials/block",
    )
    n_blocks = mo.ui.number(value=2, start=1, stop=100, step=1, label="blocks")
    n_subjects = mo.ui.number(value=2, start=1, stop=50, step=1, label="subjects")

    input_form = (
        mo.md(r"""
    ## Simulation Parameters

    **Link function:** $\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$

    *Parameters (x₀, k, γ, λ) are randomly sampled from hierarchical priors*

    **Stimulus** {n_levels}

    **Simulation** {n_trials} {n_blocks} {n_subjects}
    """)
        .batch(
            n_levels=n_levels,
            n_trials=n_trials,
            n_blocks=n_blocks,
            n_subjects=n_subjects,
        )
        .form(submit_button_label="Generate")
    )
    return (
        input_form,
        n_blocks,
        n_levels,
        n_subjects,
        n_trials,
    )


@app.cell
def _(fit_chains, fit_draws, fit_random_seed, fit_target_accept, fit_tune):
    random_seed = int(fit_random_seed.value)
    fit_params: dict[str, float | int | None] = {
        "draws": int(fit_draws.value),
        "tune": int(fit_tune.value),
        "chains": int(fit_chains.value),
        "target_accept": float(fit_target_accept.value),
        "random_seed": None if random_seed <= 0 else random_seed,
    }
    return (fit_params,)


@app.cell
def _(logit):
    # Default stimulus range for random parameter generation
    # Using reasonable defaults: x_0=0, k=1 as baseline
    min_x = logit(0.01)
    max_x = logit(0.99)
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
def _(pl):
    from pathlib import Path as _Path

    def load_sample_trials() -> pl.DataFrame:
        """Load sample experimental data from data/trials.csv."""
        sample_path = _Path(__file__).parent / "data" / "trials.csv"
        df = pl.read_csv(sample_path)
        # Transform to expected format: Subject, Block, Intensity, Result
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
        df = df.select(["Subject", "Block", "Intensity", "Result"])
        return df
    return (load_sample_trials,)


@app.cell
def _(
    file_upload,
    fit_random_seed,
    generate_index,
    generate_trials,
    input_tabs,
    load_sample_trials,
    max_x,
    min_x,
    n_blocks,
    n_levels,
    n_subjects,
    n_trials,
    pl,
    process_upload_bytes,
    sampling_method_dropdown,
    subject_utils,
):
    # Trials: upload if provided, otherwise default to sample in Batch/Online
    ground_truth_params = {}
    use_random_params = input_tabs.value == "Simulation"
    sampling_method = sampling_method_dropdown.value or "constant_stimuli"

    if file_upload.value and len(file_upload.value) > 0:
        raw = file_upload.contents(0)
        fname = file_upload.name(0) or ""
        if raw is not None:
            trials_df = process_upload_bytes(raw, fname)
        else:
            trials_df, ground_truth_params = generate_trials(
                n_trials=n_trials.value,
                options=generate_index(n_levels.value, [min_x, max_x]),
                params={},
                n_blocks=n_blocks.value,
                n_subjects=n_subjects.value,
                use_random_params=use_random_params,
                random_seed=int(fit_random_seed.value)
                if fit_random_seed.value > 0
                else None,
                sampling_method=sampling_method,
            )
    elif input_tabs.value == "Simulation":
        trials_df, ground_truth_params = generate_trials(
            n_trials=n_trials.value,
            options=generate_index(n_levels.value, [min_x, max_x]),
            params={},
            n_blocks=n_blocks.value,
            n_subjects=n_subjects.value,
            use_random_params=use_random_params,
            random_seed=int(fit_random_seed.value)
            if fit_random_seed.value > 0
            else None,
            sampling_method=sampling_method,
        )
    else:
        trials_df = load_sample_trials()
    trials_df = subject_utils.ensure_subject_column(trials_df)
    trials_df = trials_df.with_columns(pl.col("Intensity").cast(pl.Float64))
    return ground_truth_params, trials_df


@app.cell
@app.cell
def _(mo):
    fit_button = mo.ui.run_button(
        label="Fit Model",
        kind="success",
    )
    return (fit_button,)


@app.cell
def _(Path):
    cache_root = Path("__marimo__") / "cache" / "psychoanalyze"
    cache_root.mkdir(parents=True, exist_ok=True)
    return (cache_root,)


@app.cell
def _(fit_button, input_tabs):
    should_fit = fit_button.value or input_tabs.value == "Simulation"
    return (should_fit,)


@app.cell
def _(
    cached_hierarchical_fit,
    fit_params: dict[str, float | int | None],
    from_trials,
    ground_truth_params,
    pl,
    should_fit,
    trials_cache_key,
    trials_df,
):
    # Points always computed from trials
    points_df = from_trials(trials_df)

    # Only run fitting if button clicked or on Simulation tab
    if should_fit:
        composite_block = (
            pl.col("Subject").cast(pl.Utf8) + "__" + pl.col("Block").cast(pl.Utf8)
        )
        fit_trials_df = trials_df.with_columns(composite_block.alias("Block"))
        cache_key = trials_cache_key(trials_df, fit_params)
        fit_summary, fit_idata = cached_hierarchical_fit(
            fit_trials_df,
            cache_key,
            fit_params,
        )
        fit_blocks = fit_trials_df["Block"].unique().sort().to_list()
        block_idx_by_key = {block: idx for idx, block in enumerate(fit_blocks)}

        blocks_list = []
        block_idx_by_subject_block: dict[tuple[str, int], int] = {}
        block_keys = trials_df.select(["Subject", "Block"]).unique()
        for block_key_row in block_keys.iter_rows(named=True):
            subject_id = str(block_key_row["Subject"])
            block_id = int(block_key_row["Block"])
            block_key = f"{subject_id}__{block_id}"
            block_idx = block_idx_by_key.get(block_key)
            if block_idx is None:
                continue
            block_idx_by_subject_block[(subject_id, block_id)] = block_idx

            # Get ground truth params for this block if available
            _gt_params = ground_truth_params.get((subject_id, block_id))

            # Estimated parameters from fit
            _est_intercept = float(fit_summary["intercept"][block_idx])
            _est_slope = float(fit_summary["slope"][block_idx])
            _est_gamma = float(fit_summary["gamma"][block_idx])
            _est_lambda = float(fit_summary["lam"][block_idx])
            _est_x_0 = -_est_intercept / _est_slope if _est_slope != 0 else 0.0
            _est_k = _est_slope

            # Calculate confidence intervals from posterior
            _x_0_ci_lower = _est_x_0
            _x_0_ci_upper = _est_x_0
            try:
                posterior = fit_idata.posterior
                threshold_samples = (
                    posterior["threshold"]
                    .isel(threshold_dim_0=block_idx)
                    .stack(sample=("chain", "draw"))
                    .values
                )
                _x_0_ci_lower = float(__import__("numpy").quantile(threshold_samples, 0.05))
                _x_0_ci_upper = float(__import__("numpy").quantile(threshold_samples, 0.95))
            except (KeyError, IndexError, ValueError, AttributeError):
                pass

            _block_dict = {
                "Block": block_id,
                "Subject": subject_id,
                "intercept": _est_intercept,
                "slope": _est_slope,
                "gamma": _est_gamma,
                "lambda": _est_lambda,
                "x_0 (est)": _est_x_0,
                "k (est)": _est_k,
                "x_0_ci_lower": _x_0_ci_lower,
                "x_0_ci_upper": _x_0_ci_upper,
            }

            # Add ground truth columns if available
            if _gt_params is not None:
                _gt_intercept = -_gt_params["x_0"] / _gt_params["k"] if _gt_params["k"] != 0 else 0.0
                _gt_slope = _gt_params["k"]
                _block_dict.update({
                    "x_0 (actual)": _gt_params["x_0"],
                    "k (actual)": _gt_params["k"],
                    "gamma (actual)": _gt_params["gamma"],
                    "lambda (actual)": _gt_params["lambda"],
                    "intercept (actual)": _gt_intercept,
                    "slope (actual)": _gt_slope,
                })

            blocks_list.append(_block_dict)
        blocks_df = pl.from_dicts(blocks_list)
    else:
        fit_idata = None
        block_idx_by_subject_block = {}
        blocks_df = pl.DataFrame()
    return block_idx_by_subject_block, blocks_df, fit_idata, points_df


@app.cell
def _(pl):
    def selection_to_pl(selection: object) -> pl.DataFrame | None:
        if selection is None:
            return None
        if isinstance(selection, pl.DataFrame):
            return selection
        if isinstance(selection, dict):
            return pl.from_dicts([selection])
        if isinstance(selection, list):
            return pl.from_dicts(selection) if selection else None
        if hasattr(selection, "to_dict"):
            try:
                return pl.from_dicts(selection.to_dict("records"))
            except Exception:
                return None
        if hasattr(selection, "to_dicts"):
            try:
                return pl.from_dicts(selection.to_dicts())
            except Exception:
                return None
        return None

    return (selection_to_pl,)


@app.cell
def _(
    block,
    block_idx_by_subject_block: dict[tuple[str, int], int],
    blocks_df,
    blocks_chart,
    ground_truth_params,
    pl,
    selection_to_pl,
    subject,
):
    # Selected block rows for plot (include ground truth per block)
    selected_blocks_df = selection_to_pl(getattr(blocks_chart, "value", None))
    if selected_blocks_df is None or len(selected_blocks_df) == 0:
        selected_blocks_df = blocks_df

    def block_label(row: dict) -> str:
        subject = row.get("Subject")
        block = row.get("Block")
        if subject is None or subject == "":
            return str(block)
        return f"{subject}-{block}"

    block_rows = []
    if isinstance(selected_blocks_df, pl.DataFrame) and len(selected_blocks_df) > 0:
        for block_row in selected_blocks_df.iter_rows(named=True):
            _subject = str(block_row.get("Subject", ""))
            _block = int(block_row.get("Block", 0))

            # Add estimated curve
            block_rows.append(
                {
                    "Block": block_label(block_row),
                    "intercept": block_row.get("intercept", 0),
                    "slope": block_row.get("slope", 1),
                    "block_idx": block_idx_by_subject_block.get((_subject, _block)),
                    "is_ground_truth": False,
                },
            )

            # Add ground truth curve if available
            _gt_params = ground_truth_params.get((_subject, _block))
            if _gt_params is not None:
                _gt_intercept = -_gt_params["x_0"] / _gt_params["k"] if _gt_params["k"] != 0 else 0.0
                _gt_slope = _gt_params["k"]
                block_rows.append(
                    {
                        "Block": f"{_subject}-{_block} (GT)",
                        "intercept": _gt_intercept,
                        "slope": _gt_slope,
                        "block_idx": None,
                        "is_ground_truth": True,
                    },
                )
    else:
        for block_row in blocks_df.iter_rows(named=True):
            _subject = str(block_row.get("Subject", ""))
            _block = int(block_row.get("Block", 0))

            # Add estimated curve
            block_rows.append(
                {
                    "Block": block_label(block_row),
                    "intercept": block_row["intercept"],
                    "slope": block_row["slope"],
                    "block_idx": block_idx_by_subject_block.get((_subject, _block)),
                    "is_ground_truth": False,
                },
            )

            # Add ground truth curve if available
            _gt_params = ground_truth_params.get((_subject, _block))
            if _gt_params is not None:
                _gt_intercept = -_gt_params["x_0"] / _gt_params["k"] if _gt_params["k"] != 0 else 0.0
                _gt_slope = _gt_params["k"]
                block_rows.append(
                    {
                        "Block": f"{_subject}-{_block} (GT)",
                        "intercept": _gt_intercept,
                        "slope": _gt_slope,
                        "block_idx": None,
                        "is_ground_truth": True,
                    },
                )
            gt_params = ground_truth_params.get((subject, block))
            if gt_params is not None:
                gt_intercept = -gt_params["x_0"] / gt_params["k"] if gt_params["k"] != 0 else 0.0
                gt_slope = gt_params["k"]
                block_rows.append(
                    {
                        "Block": f"{subject}-{block} (GT)",
                        "intercept": gt_intercept,
                        "slope": gt_slope,
                        "block_idx": None,
                        "is_ground_truth": True,
                    },
                )
    return (block_rows,)


@app.cell
def _(blocks_chart, pl, points_df, selection_to_pl):
    # Filter points by selected blocks
    sel = selection_to_pl(getattr(blocks_chart, "value", None))
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
    return (points_filtered_df,)


@app.cell
def _(expit, link_function):
    link_fn = expit if link_function.value == "expit" else expit
    return (link_fn,)


@app.cell
def _(alt, blocks_df, mo, pl):
    # Blocks chart: Actual vs Estimated overlaid, x = blocks grouped by subject
    if len(blocks_df) > 0 and "x_0 (est)" in blocks_df.columns:
        chart_rows = []

        for row in blocks_df.iter_rows(named=True):
            subject = str(row["Subject"])
            block = int(row["Block"])
            x_est = float(row["x_0 (est)"])

            conf_low = x_est
            conf_high = x_est
            if "x_0_ci_lower" in row and row["x_0_ci_lower"] is not None:
                conf_low = float(row["x_0_ci_lower"])
            if "x_0_ci_upper" in row and row["x_0_ci_upper"] is not None:
                conf_high = float(row["x_0_ci_upper"])

            chart_rows.append(
                {
                    "Subject": subject,
                    "Block": block,
                    "Type": "Estimated",
                    "Threshold": x_est,
                    "Conf_Low": conf_low,
                    "Conf_High": conf_high,
                },
            )

            if "x_0 (actual)" in row and row["x_0 (actual)"] is not None:
                x_actual = float(row["x_0 (actual)"])
                chart_rows.append(
                    {
                        "Subject": subject,
                        "Block": block,
                        "Type": "Actual",
                        "Threshold": x_actual,
                        "Conf_Low": x_actual,
                        "Conf_High": x_actual,
                    },
                )

        if chart_rows:
            chart_df = pl.from_dicts(chart_rows)
            # Block label for x-axis: blocks grouped by subject (Subject · Block N)
            chart_df = chart_df.with_columns(
                (pl.col("Subject").cast(pl.Utf8) + " · Block " + pl.col("Block").cast(pl.Utf8)).alias("BlockLabel"),
            )
            # Sort order: by subject then block so x-axis groups blocks by subject
            block_order = (
                chart_df.unique(["Subject", "Block"])
                .sort(["Subject", "Block"])
                .with_columns(
                    (pl.col("Subject").cast(pl.Utf8) + " · Block " + pl.col("Block").cast(pl.Utf8)).alias("BlockLabel"),
                )["BlockLabel"]
                .to_list()
            )
            chart_pd = chart_df.to_pandas()

            selection = alt.selection_point(fields=["Subject", "Block"], toggle=True)

            # Points: overlay Actual vs Estimated with different marker shapes
            points = (
                alt.Chart(chart_pd)
                .mark_point(filled=True, size=80)
                .encode(
                    x=alt.X(
                        "BlockLabel:N",
                        sort=block_order,
                        title="Block (by subject)",
                    ),
                    y=alt.Y("Threshold:Q", title="Threshold (x₀)"),
                    shape=alt.Shape("Type:N", title="", legend=alt.Legend(orient="top")),
                    color=alt.condition(
                        selection,
                        alt.Color("Subject:N", scale=alt.Scale(scheme="category10")),
                        alt.value("#d3d3d3"),
                    ),
                    tooltip=["Subject:N", "Block:Q", "Type:N", "Threshold:Q"],
                )
                .add_params(selection)
            )

            # Vertical error bars for estimated (confidence intervals), using rule for pre-computed bounds
            estimated_pd = chart_pd[chart_pd["Type"] == "Estimated"]
            error_bars = (
                alt.Chart(estimated_pd)
                .mark_rule()
                .encode(
                    x=alt.X("BlockLabel:N", sort=block_order),
                    y=alt.Y("Conf_Low:Q"),
                    y2=alt.Y2("Conf_High:Q"),
                    color=alt.Color("Subject:N", scale=alt.Scale(scheme="category10")),
                )
            )

            chart = (error_bars + points).properties(
                height=220,
                width=max(400, len(block_order) * 28),
            ).resolve_scale(color="shared")
            blocks_chart = mo.ui.altair_chart(chart)
        else:
            blocks_chart = mo.md("No block data to display.")
    else:
        blocks_chart = mo.md("No block fits available yet.")
    return (blocks_chart,)


@app.cell
def _(
    alt,
    block_rows,
    fit_idata,
    link_fn,
    max_x,
    min_x,
    mo,
    np,
    pa_hierarchical,
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
                    "Type": ["Ground Truth" if blk.get("is_ground_truth", False) else "Fitted"] * len(x),
                },
            ),
        )
        block_idx_val = blk.get("block_idx")
        if (
            fit_idata is not None
            and block_idx_val is not None
            and not blk.get("is_ground_truth", False)
        ):
            band_df = pa_hierarchical.curve_credible_band(
                fit_idata,
                x,
                block_idx=block_idx_val,
                hdi_prob=0.9,
            )
            band_df = band_df.with_columns(pl.lit(blk["Block"]).alias("Series"))
            bands_list.append(band_df)
    fits_df = (
        pl.concat(fits_list)
        if len(fits_list) > 0
        else pl.DataFrame({"Intensity": [], "Hit Rate": [], "Series": [], "Type": []})
    )
    bands_df = (
        pl.concat(bands_list)
        if len(bands_list) > 0
        else pl.DataFrame({"Intensity": [], "lower": [], "upper": [], "Series": []})
    )
    points_plot_df = points_filtered_df.with_columns(
        (pl.col("Subject").cast(pl.Utf8) + "-" + pl.col("Block").cast(pl.Utf8)).alias(
            "Series",
        ),
    )
    fits_df = fits_df.with_columns(pl.col("Series").cast(pl.Utf8))
    # Extract base block name (without " (GT)" suffix) for consistent coloring
    fits_df = fits_df.with_columns(
        pl.col("Series").str.replace(r" \(GT\)$", "").alias("BlockGroup"),
    )
    # Separate ground truth vs fitted curves for different styling
    ground_truth_df = fits_df.filter(pl.col("Type") == "Ground Truth")
    fitted_df = fits_df.filter(pl.col("Type") == "Fitted")
    fitted_pd = fitted_df.to_pandas()
    ground_truth_pd = ground_truth_df.to_pandas()
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
    fitted_line_chart = (
        alt.Chart(fitted_pd)
        .mark_line()
        .encode(
            x=alt.X("Intensity:Q"),
            y=alt.Y("Hit Rate:Q"),
            color=alt.Color("BlockGroup:N"),
        )
    )
    ground_truth_line_chart = (
        alt.Chart(ground_truth_pd)
        .mark_line(strokeDash=[5, 5], strokeWidth=2)
        .encode(
            x=alt.X("Intensity:Q"),
            y=alt.Y("Hit Rate:Q"),
            color=alt.Color("BlockGroup:N"),
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
    plot_layers = [fitted_line_chart, points_chart]
    if len(ground_truth_pd) > 0:
        plot_layers.insert(0, ground_truth_line_chart)
    if len(bands_pd) > 0:
        plot_layers.insert(0, band_chart)
    plot_chart = alt.layer(*plot_layers).resolve_scale(color="shared")
    plot_ui = mo.ui.altair_chart(plot_chart)
    return (plot_ui,)


@app.cell
def _(mo):
    format_dropdown = mo.ui.dropdown(
        options={
            "csv_zip": "CSV (zip)",
            "json": "JSON",
            "parquet": "Parquet",
            "duckdb": "DuckDB",
        },
        value="csv_zip",
        label="Format",
    )
    return (format_dropdown,)


@app.cell
def _(blocks_df, format_dropdown, mo, pl, points_filtered_df, trials_df: object):
    import io as _io
    import zipfile as _zipfile
    from datetime import datetime
    from pathlib import Path as _Path

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
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = _Path(temp_dir) / "psychoanalyze.duckdb"
            connection = duckdb.connect(str(db_path))
            connection.register("points_df", points_df.to_pandas())
            connection.execute("CREATE TABLE points AS SELECT * FROM points_df")
            connection.close()
            return db_path.read_bytes()

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M")
    csv_zip = build_csv_zip(points_filtered_df, blocks_df, trials_df)
    json_bytes = build_json(points_filtered_df)
    parquet_bytes = build_parquet(points_filtered_df)
    duckdb_bytes = build_duckdb(points_filtered_df)

    format_to_content: dict[str, tuple[bytes, str]] = {
        "csv_zip": (csv_zip, f"{timestamp}_psychoanalyze.zip"),
        "json": (json_bytes, "data.json"),
        "parquet": (parquet_bytes, "data.parquet"),
        "duckdb": (duckdb_bytes, "psychoanalyze.duckdb"),
    }
    _selected_key = format_dropdown.selected_key or format_dropdown.value or "csv_zip"
    _selected_bytes, _selected_filename = format_to_content.get(
        _selected_key, format_to_content["csv_zip"]
    )
    download_button = mo.download(
        _selected_bytes,
        filename=_selected_filename,
        label="Download",
    )
    data_downloads = mo.vstack(
        [format_dropdown, download_button],
        gap=1,
    )
    return (data_downloads,)


@app.cell
def _(
    auto_play_button,
    file_upload,
    fit_button,
    fit_settings,
    input_form,
    link_function,
    load_sample_button,
    mo,
    preset_dropdown,
    sampling_method_dropdown,
    show_equation,
    step_mode_toggle,
    trial_step_slider,
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
            fit_settings,
            fit_button,
        ],
        gap=1,
    )

    # Sampling method info callout
    sampling_method_info = mo.callout(
        mo.md("""
**Method of Constant Stimuli:** Randomly samples from fixed intensity levels. Classic approach used in traditional psychophysics.

**Adaptive (Fisher Information):** Fits a logistic model and samples where Fisher Information about the threshold is highest (near the estimated threshold).

**QUEST/Psi (Bayesian):** Maintains a full probability distribution over threshold values and selects stimuli that maximize expected information gain. Classic algorithm from Watson & Pelli (1983).
        """),
        kind="info",
    )

    # Step-by-step controls
    step_controls = mo.vstack(
        [
            mo.md("### Step-by-Step Visualization"),
            step_mode_toggle,
            mo.hstack([trial_step_slider, auto_play_button], gap=1) if step_mode_toggle.value else mo.md(""),
        ],
        gap=1,
    )

    simulation_content = mo.vstack(
        [
            mo.md("### Simulation Mode"),
            mo.md("### Sampling Method"),
            sampling_method_dropdown,
            sampling_method_info,
            step_controls,
            mo.md("### Link Function"),
            link_function,
            show_equation,
            input_form,
            fit_settings,
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
            "Simulation": simulation_content,
            "Batch": batch_content,
            "Online": online_content,
        },
    )
    return (input_tabs,)


if __name__ == "__main__":
    app.run()
