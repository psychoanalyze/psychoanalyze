"""PsychoAnalyze dashboard as a marimo notebook.

Interactive data simulation & analysis for psychophysics.
Replaces the former Dash dashboard (removed).
"""

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full", app_title="PsychoAnalyze")


@app.cell
def main_layout(
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
    return


@app.cell
def imports():
    import hashlib
    import io
    import json
    from pathlib import Path

    import altair as alt
    import arviz as az
    import marimo as mo
    import numpy as np
    import polars as pl
    from scipy.special import expit, logit
    from wigglystuff import HTMLRefreshWidget
    from wigglystuff.utils import altair2svg, refresh_altair

    from psychoanalyze.data import export as pa_export
    from psychoanalyze.data import hierarchical as pa_hierarchical
    from psychoanalyze.data import io as pa_io
    from psychoanalyze.data import points as pa_points
    from psychoanalyze.data import subject as subject_utils
    from psychoanalyze.data import trials as pa_trials
    from psychoanalyze.data.logistic import to_intercept, to_slope
    from psychoanalyze.data.trials import BOEDSampler, psi as psi_func
    from psychoanalyze.features import is_adaptive_sampling_enabled
    return (
        BOEDSampler,
        HTMLRefreshWidget,
        Path,
        alt,
        altair2svg,
        az,
        expit,
        hashlib,
        io,
        is_adaptive_sampling_enabled,
        json,
        logit,
        mo,
        np,
        pa_export,
        pa_hierarchical,
        pa_io,
        pa_points,
        pa_trials,
        pl,
        psi_func,
        refresh_altair,
        subject_utils,
    )


@app.cell
def cached_fit_cell(az, mo, np, pa_hierarchical, pl):
    @mo.persistent_cache
    def cached_hierarchical_fit(
        trials_df: pl.DataFrame,
        fit_params: dict[str, float | int | None],
    ) -> tuple[dict[str, float | np.ndarray], az.InferenceData]:
        idata = pa_hierarchical.fit(trials_df, **fit_params)
        summary = pa_hierarchical.summarize_fit(idata)
        return summary, idata
    return (cached_hierarchical_fit,)


@app.cell
def data_helpers(pa_io, pa_points, pa_trials, pl, subject_utils):
    # Import functions from refactored modules
    generate_index = pa_points.generate_index
    generate_trials = pa_trials.generate_multi_subject
    process_upload_bytes = pa_io.read_from_bytes


    def from_trials(trials_df: pl.DataFrame) -> pl.DataFrame:
        trials_df = subject_utils.ensure_subject_column(trials_df)
        return pa_points.from_trials(trials_df)
    return from_trials, generate_index, generate_trials, process_upload_bytes


@app.cell
def header(mo):
    # Header
    mo.md(r"""
    # PsychoAnalyze
    *Interactive data simulation & analysis for psychophysics.*

    [Notebooks](https://nb.psychoanalyze.io) · [GitHub](https://github.com/psychoanalyze/psychoanalyze) · [Docs](https://docs.psychoanalyze.io)
    """)
    return


@app.cell
def file_upload_ui(mo):
    # File upload
    file_upload = mo.ui.file(
        filetypes=[".csv", ".zip", ".parquet", ".pq"],
        kind="area",
        label="Upload CSV/parquet with columns: **Block, Intensity, Result** (optional: **Subject**). Data stays on this machine.",
    )
    return (file_upload,)


@app.cell
def load_sample_button(mo):
    load_sample_button = mo.ui.run_button(label="Load Sample Data")
    return (load_sample_button,)


@app.cell
def preset_and_link_ui(mo):
    preset_dropdown = mo.ui.dropdown(
        options={
            "Standard": "standard",
            "Non Standard": "non-standard",
            "2AFC": "2AFC",
        },
        value="Standard",
        label="Preset",
    )
    link_function = mo.ui.dropdown(
        options={
            "Logistic": "expit",
        },
        value="Logistic",
        label="Link function",
    )
    show_equation = mo.ui.checkbox(label="Show F(x)", value=False)
    return link_function, preset_dropdown, show_equation


@app.cell
def fit_settings_ui(mo):
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
def sampling_method_ui(is_adaptive_sampling_enabled, mo):
    # Build options dict, only including BOED if the feature flag is enabled
    options = {"Method of Constant Stimuli": "constant_stimuli"}
    if is_adaptive_sampling_enabled():
        options["Bayesian Optimal Design"] = "boed"
    
    sampling_method_dropdown = mo.ui.dropdown(
        options=options,
        value="Method of Constant Stimuli",
        label="Sampling Method",
    )
    return (sampling_method_dropdown,)


@app.cell
def step_mode_toggle(mo):
    # Step-by-step visualization controls
    step_mode_toggle = mo.ui.checkbox(label="Step-by-step mode", value=False)
    return (step_mode_toggle,)


@app.cell
def step_block_selection(mo, n_blocks, n_subjects):
    """Subject and block selection for step-by-step view (fixed to one subject+block).
    
    Uses simulation parameters to generate subject/block options to avoid circular deps.
    """
    # Generate subject options from n_subjects parameter
    # Match the format used by generate_multi_subject: A, B, C, ... Z, S26, S27, ...
    _n_subj = n_subjects.value if hasattr(n_subjects, "value") else 2
    subjects = [
        chr(ord("A") + i) if i < 26 else f"S{i}"
        for i in range(_n_subj)
    ]
    subject_options = {s: s for s in subjects}
    step_subject_dropdown = mo.ui.dropdown(
        options=subject_options,
        value=subjects[0] if subjects else None,
        label="Subject",
    )

    # Generate block options from n_blocks parameter
    _n_blk = n_blocks.value if hasattr(n_blocks, "value") else 2
    blocks = list(range(_n_blk))
    block_options = {f"Block {b}": str(b) for b in blocks}
    step_block_dropdown = mo.ui.dropdown(
        options=block_options,
        value=f"Block {blocks[0]}" if blocks else None,
        label="Block",
    )

    return step_block_dropdown, step_subject_dropdown


@app.cell
def trial_step_controls(mo, n_trials):
    # Trial step slider - only active when step mode is enabled
    _max_trials = n_trials.value if hasattr(n_trials, "value") else 100

    # Create slider for stepping through trials
    trial_step_slider = mo.ui.slider(
        value=1,
        start=1,
        stop=max(_max_trials, 1),
        step=1,
        label=f"Trial (of {_max_trials})",
    )
    # Auto-play button for animation
    auto_play_button = mo.ui.run_button(label="▶ Play", kind="neutral")
    return auto_play_button, trial_step_slider


@app.cell
def step_chart(
    BOEDSampler,
    HTMLRefreshWidget,
    alt,
    altair2svg,
    expit,
    generate_index,
    ground_truth_params,
    max_x,
    min_x,
    mo,
    n_levels,
    np,
    pl,
    psi_func,
    sampling_method_dropdown,
    step_block_dropdown,
    step_mode_toggle,
    step_subject_dropdown,
    trial_step_slider,
    trials_df,
):
    """Create step-by-step BOED visualization showing posterior updates after each trial.
    
    For BOED mode: Runs the sampler sequentially and shows the evolving posterior.
    For constant stimuli: Shows trials accumulating with hit rates.
    """

    # Only compute if step mode is enabled and we're in simulation mode
    if not step_mode_toggle.value or "Trial" not in trials_df.columns:
        step_chart = None
        step_info = mo.md("")
    else:
        current_step = trial_step_slider.value
        _sampling_method = sampling_method_dropdown.value or "constant_stimuli"

        # Use selected subject and block from dropdowns
        selected_subject = step_subject_dropdown.value
        selected_block = int(step_block_dropdown.value) if step_block_dropdown.value else 0
        
        block_trials = trials_df.filter(
            (pl.col("Subject") == selected_subject) & (pl.col("Block") == selected_block)
        ).sort("Trial")

        # Get all intensity options
        all_options = generate_index(n_levels.value, [min_x, max_x])
        options_arr = np.array(all_options)

        # Get ground truth parameters for this block
        _gt_params = ground_truth_params.get((selected_subject, selected_block))

        # Filter to trials up to current step
        trials_up_to_step = block_trials.filter(pl.col("Trial") < current_step)
        current_trial = block_trials.filter(pl.col("Trial") == current_step - 1)

        # === BOED MODE: Run sequential posterior updates ===
        if _sampling_method == "boed":
            # Initialize BOED sampler
            boed = BOEDSampler(options=options_arr, n_threshold_bins=40, n_slope_bins=15)
            
            # Replay trials up to current step to build posterior
            for _row in trials_up_to_step.iter_rows(named=True):
                intensity = float(_row["Intensity"])
                result = int(_row["Result"])
                # Find closest option index
                stim_idx = int(np.argmin(np.abs(options_arr - intensity)))
                boed.update(stim_idx, result)
            
            # Get posterior estimates
            estimates = boed.get_estimates()
            threshold_grid, threshold_marginal = boed.get_marginal_threshold()
            slope_grid, slope_marginal = boed.get_marginal_slope()
            
            # Get expected curve with credible band
            x_fine, mean_curve, lower_ci, upper_ci = boed.get_expected_curve()

        # Create x values for curves
        _x_curve = np.linspace(min_x, max_x, 100)

        # === BUILD VISUALIZATION ===
        _chart_layers = []

        # Ground truth curve (dashed gray)
        if _gt_params is not None:
            _gt_intercept = -_gt_params["x_0"] * _gt_params["k"]
            _gt_slope = _gt_params["k"]
            _y_gt = expit(_gt_slope * _x_curve + _gt_intercept)
            _gt_df = pl.DataFrame({
                "Intensity": _x_curve,
                "Hit Rate": _y_gt,
                "Type": ["Ground Truth"] * len(_x_curve),
            }).to_pandas()
            _gt_line = (
                alt.Chart(_gt_df)
                .mark_line(strokeDash=[5, 5], color="gray", strokeWidth=2)
                .encode(
                    x=alt.X("Intensity:Q", title="Intensity"),
                    y=alt.Y("Hit Rate:Q", title="Hit Rate", scale=alt.Scale(domain=[0, 1])),
                )
            )
            _chart_layers.append(_gt_line)

        # BOED: Expected curve with credible band
        if _sampling_method == "boed" and current_step > 0:
            # Credible band
            _band_df = pl.DataFrame({
                "Intensity": x_fine,
                "lower": lower_ci,
                "upper": upper_ci,
            }).to_pandas()
            _band = (
                alt.Chart(_band_df)
                .mark_area(opacity=0.3, color="steelblue")
                .encode(
                    x=alt.X("Intensity:Q"),
                    y=alt.Y("lower:Q", scale=alt.Scale(domain=[0, 1])),
                    y2="upper:Q",
                )
            )
            _chart_layers.append(_band)
            
            # Expected curve
            _expected_df = pl.DataFrame({
                "Intensity": x_fine,
                "Hit Rate": mean_curve,
            }).to_pandas()
            _expected_line = (
                alt.Chart(_expected_df)
                .mark_line(color="steelblue", strokeWidth=2)
                .encode(
                    x=alt.X("Intensity:Q"),
                    y=alt.Y("Hit Rate:Q"),
                )
            )
            _chart_layers.append(_expected_line)

        # Cumulative points (hit rate at each intensity)
        if len(trials_up_to_step) > 0:
            points_cumulative = (
                trials_up_to_step.group_by("Intensity")
                .agg([
                    pl.mean("Result").alias("Hit Rate"),
                    pl.len().alias("n_trials"),
                ])
                .sort("Intensity")
            )
            _points_pd = points_cumulative.to_pandas()
            _points_scatter = (
                alt.Chart(_points_pd)
                .mark_point(filled=True, color="darkorange")
                .encode(
                    x=alt.X("Intensity:Q"),
                    y=alt.Y("Hit Rate:Q"),
                    size=alt.Size("n_trials:Q", scale=alt.Scale(range=[50, 300]), title="Trials"),
                    tooltip=["Intensity:Q", "Hit Rate:Q", "n_trials:Q"],
                )
            )
            _chart_layers.append(_points_scatter)

        # Current trial highlight
        if len(current_trial) > 0:
            _current_intensity = float(current_trial["Intensity"][0])
            _current_result = int(current_trial["Result"][0])
            _current_pd = pl.DataFrame({
                "Intensity": [_current_intensity],
                "Result": [_current_result],
                "label": [f"Trial {current_step}: {'Hit' if _current_result else 'Miss'}"],
            }).to_pandas()

            # Vertical line at current intensity
            _vline = (
                alt.Chart(_current_pd)
                .mark_rule(color="red", strokeWidth=2, strokeDash=[4, 4])
                .encode(x=alt.X("Intensity:Q"))
            )
            _chart_layers.append(_vline)

            # Current trial marker
            _current_marker = (
                alt.Chart(_current_pd)
                .mark_point(filled=True, size=200, color="red", shape="diamond")
                .encode(
                    x=alt.X("Intensity:Q"),
                    y=alt.Y("Result:Q", scale=alt.Scale(domain=[0, 1])),
                    tooltip=["label:N", "Intensity:Q"],
                )
            )
            _chart_layers.append(_current_marker)

        # === POSTERIOR DISTRIBUTION (BOED mode) ===
        if _sampling_method == "boed":
            # Threshold posterior
            _threshold_df = pl.DataFrame({
                "Threshold": threshold_grid,
                "Probability": threshold_marginal,
            }).to_pandas()
            
            _threshold_chart = (
                alt.Chart(_threshold_df)
                .mark_area(opacity=0.6, color="steelblue")
                .encode(
                    x=alt.X("Threshold:Q", title="Threshold (x₀)", 
                           scale=alt.Scale(domain=[min_x, max_x])),
                    y=alt.Y("Probability:Q", title="Posterior Density"),
                )
                .properties(width=250, height=100, title="Threshold Posterior")
            )
            
            # Add ground truth line to threshold posterior if available
            if _gt_params is not None:
                _gt_thresh_df = pl.DataFrame({
                    "x0": [_gt_params["x_0"]],
                }).to_pandas()
                _gt_thresh_line = (
                    alt.Chart(_gt_thresh_df)
                    .mark_rule(color="red", strokeDash=[4, 4], strokeWidth=2)
                    .encode(x="x0:Q")
                )
                _threshold_chart = _threshold_chart + _gt_thresh_line
            
            # Slope posterior
            _slope_df = pl.DataFrame({
                "Slope": slope_grid,
                "Probability": slope_marginal,
            }).to_pandas()
            
            _slope_chart = (
                alt.Chart(_slope_df)
                .mark_area(opacity=0.6, color="green")
                .encode(
                    x=alt.X("Slope:Q", title="Slope (k)"),
                    y=alt.Y("Probability:Q", title="Posterior Density"),
                )
                .properties(width=250, height=100, title="Slope Posterior")
            )
            
            # Add ground truth line to slope posterior if available
            if _gt_params is not None:
                _gt_slope_df = pl.DataFrame({
                    "k": [_gt_params["k"]],
                }).to_pandas()
                _gt_slope_line = (
                    alt.Chart(_gt_slope_df)
                    .mark_rule(color="red", strokeDash=[4, 4], strokeWidth=2)
                    .encode(x="k:Q")
                )
                _slope_chart = _slope_chart + _gt_slope_line

        # === SAMPLING DISTRIBUTION HISTOGRAM ===
        if len(trials_up_to_step) > 0:
            sampling_counts = trials_up_to_step.group_by("Intensity").len()
            all_options_df = pl.DataFrame({"Intensity": all_options})
            sampling_dist = (
                all_options_df.join(sampling_counts, on="Intensity", how="left")
                .with_columns(pl.col("len").fill_null(0).alias("Count"))
                .select(["Intensity", "Count"])
                .sort("Intensity")
            )
        else:
            sampling_dist = pl.DataFrame({
                "Intensity": all_options,
                "Count": [0] * len(all_options),
            })

        _sampling_pd = sampling_dist.to_pandas()
        if len(current_trial) > 0:
            _current_intensity = float(current_trial["Intensity"][0])
            _sampling_pd["is_current"] = _sampling_pd["Intensity"].apply(
                lambda x: abs(x - _current_intensity) < 0.01
            )
        else:
            _sampling_pd["is_current"] = False

        _histogram = (
            alt.Chart(_sampling_pd)
            .mark_bar()
            .encode(
                x=alt.X("Intensity:Q", title="Intensity", scale=alt.Scale(domain=[min_x, max_x])),
                y=alt.Y("Count:Q", title="Samples"),
                color=alt.condition(alt.datum.is_current, alt.value("red"), alt.value("steelblue")),
                tooltip=["Intensity:Q", "Count:Q"],
            )
            .properties(width=500, height=80, title="Sampling Distribution")
        )

        # === ASSEMBLE FINAL VISUALIZATION ===
        _max_trials = len(block_trials)
        
        if _chart_layers:
            _main_chart = alt.layer(*_chart_layers).properties(
                width=500,
                height=250,
                title=f"Trial {current_step} of {_max_trials}",
            )
            
            if _sampling_method == "boed":
                # BOED mode: Show main chart, posteriors, and histogram
                _posterior_row = alt.hconcat(_threshold_chart, _slope_chart)
                html_content = (
                    f"<div>{altair2svg(_main_chart)}</div>"
                    f"<div>{altair2svg(_posterior_row)}</div>"
                    f"<div>{altair2svg(_histogram)}</div>"
                )
            else:
                # Constant stimuli mode
                html_content = (
                    f"<div>{altair2svg(_main_chart)}</div>"
                    f"<div>{altair2svg(_histogram)}</div>"
                )
            step_chart = HTMLRefreshWidget(html=html_content)
        else:
            step_chart = HTMLRefreshWidget(html=altair2svg(_histogram))

        # Info about current trial and estimates
        if len(current_trial) > 0:
            _info_intensity = float(current_trial["Intensity"][0])
            _info_result = "Hit ✓" if int(current_trial["Result"][0]) else "Miss ✗"
            
            if _sampling_method == "boed":
                thresh_mean, thresh_std = estimates["threshold"]
                slope_mean, slope_std = estimates["slope"]
                step_info = mo.callout(
                    mo.md(
                        f"**Trial {current_step}**: Intensity = {_info_intensity:.2f} → {_info_result}\n\n"
                        f"**Posterior estimates**: x₀ = {thresh_mean:.2f} ± {thresh_std:.2f}, "
                        f"k = {slope_mean:.2f} ± {slope_std:.2f}"
                    ),
                    kind="success" if "Hit" in _info_result else "warn",
                )
            else:
                step_info = mo.callout(
                    mo.md(f"**Trial {current_step}**: Intensity = {_info_intensity:.2f} → {_info_result}"),
                    kind="success" if "Hit" in _info_result else "warn",
                )
        else:
            step_info = mo.md("")
    return step_chart, step_info


@app.cell
def simulation_params_ui(mo, preset_dropdown):
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
    return input_form, n_blocks, n_levels, n_subjects, n_trials


@app.cell
def fit_params(
    fit_chains,
    fit_draws,
    fit_random_seed,
    fit_target_accept,
    fit_tune,
):
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
def stimulus_range(logit):
    # Default stimulus range for random parameter generation
    # Using reasonable defaults: x_0=0, k=1 as baseline
    min_x = logit(0.01)
    max_x = logit(0.99)
    return max_x, min_x


@app.cell
def stimulus_info(max_x, min_x, mo):
    # Stimulus range info for display in left column
    stimulus_info = mo.md(f"**Stimulus range:** {min_x:.2f} to {max_x:.2f}")
    return


@app.cell
def plot_equation_cell(mo, show_equation):
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
def load_sample_trials_ref(pa_trials):
    # Use refactored sample data loader from trials module
    load_sample_trials = pa_trials.load_sample
    return (load_sample_trials,)


@app.cell
def trials_data(
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
            random_seed=int(fit_random_seed.value) if fit_random_seed.value > 0 else None,
            sampling_method=sampling_method,
        )
    else:
        trials_df = load_sample_trials()
    trials_df = subject_utils.ensure_subject_column(trials_df)
    trials_df = trials_df.with_columns(pl.col("Intensity").cast(pl.Float64))
    # Ensure ID columns are integers for consistent sorting/filtering
    if "Trial" in trials_df.columns:
        trials_df = trials_df.with_columns(pl.col("Trial").cast(pl.Int64))
    if "Block" in trials_df.columns:
        trials_df = trials_df.with_columns(pl.col("Block").cast(pl.Int64))
    return ground_truth_params, trials_df


@app.cell
def fit_button(mo):
    fit_button = mo.ui.run_button(
        label="Fit Model",
        kind="success",
    )
    return (fit_button,)




@app.cell
def should_fit(fit_button, input_tabs):
    should_fit = fit_button.value or input_tabs.value == "Simulation"
    return (should_fit,)


@app.cell
def hierarchical_fit_and_blocks(
    cached_hierarchical_fit,
    fit_params: dict[str, float | int | None],
    from_trials,
    ground_truth_params,
    pl,
    should_fit,
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
        fit_summary, fit_idata = cached_hierarchical_fit(
            fit_trials_df,
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
                _gt_intercept = (
                    -_gt_params["x_0"] / _gt_params["k"] if _gt_params["k"] != 0 else 0.0
                )
                _gt_slope = _gt_params["k"]
                _block_dict.update(
                    {
                        "x_0 (actual)": _gt_params["x_0"],
                        "k (actual)": _gt_params["k"],
                        "gamma (actual)": _gt_params["gamma"],
                        "lambda (actual)": _gt_params["lambda"],
                        "intercept (actual)": _gt_intercept,
                        "slope (actual)": _gt_slope,
                    }
                )

            blocks_list.append(_block_dict)
        blocks_df = pl.from_dicts(blocks_list)
    else:
        fit_idata = None
        block_idx_by_subject_block = {}
        blocks_df = pl.DataFrame()
    return block_idx_by_subject_block, blocks_df, fit_idata, points_df


@app.cell
def selection_to_pl_helper(pl):
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
def block_rows_for_plot(
    block_idx_by_subject_block: dict[tuple[str, int], int],
    blocks_chart,
    blocks_df,
    ground_truth_params,
    pl,
    selection_to_pl,
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
                _gt_intercept = (
                    -_gt_params["x_0"] / _gt_params["k"] if _gt_params["k"] != 0 else 0.0
                )
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
                _gt_intercept = (
                    -_gt_params["x_0"] / _gt_params["k"] if _gt_params["k"] != 0 else 0.0
                )
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
    return (block_rows,)


@app.cell
def points_filtered(blocks_chart, pl, points_df, selection_to_pl):
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
def link_fn(expit, link_function):
    link_fn = expit if link_function.value == "expit" else expit
    return (link_fn,)


@app.cell
def blocks_chart_cell(
    HTMLRefreshWidget,
    alt,
    blocks_df,
    mo,
    pl,
    refresh_altair,
):
    # Blocks chart: Actual vs Estimated overlaid, x = blocks grouped by subject
    # Use wigglystuff HTMLRefreshWidget + @refresh_altair for refreshable static SVG
    @refresh_altair
    def _blocks_chart_svg(chart_pd, block_order):
        selection = alt.selection_point(fields=["Subject", "Block"], toggle=True)
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
        return (
            (error_bars + points)
            .properties(
                height=220,
                width=max(400, len(block_order) * 28),
            )
            .resolve_scale(color="shared")
        )


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
            chart_df = chart_df.with_columns(
                (
                    pl.col("Subject").cast(pl.Utf8)
                    + " · Block "
                    + pl.col("Block").cast(pl.Utf8)
                ).alias("BlockLabel"),
            )
            block_order = (
                chart_df.unique(["Subject", "Block"])
                .sort(["Subject", "Block"])
                .with_columns(
                    (
                        pl.col("Subject").cast(pl.Utf8)
                        + " · Block "
                        + pl.col("Block").cast(pl.Utf8)
                    ).alias("BlockLabel"),
                )["BlockLabel"]
                .to_list()
            )
            chart_pd = chart_df.to_pandas()
            blocks_chart = HTMLRefreshWidget(html=_blocks_chart_svg(chart_pd, block_order))
        else:
            blocks_chart = mo.md("No block data to display.")
    else:
        blocks_chart = mo.md("No block fits available yet.")
    return (blocks_chart,)


@app.cell
def main_psychometric_plot(
    HTMLRefreshWidget,
    alt,
    block_rows,
    fit_idata,
    link_fn,
    max_x,
    min_x,
    np,
    pa_hierarchical,
    pl,
    points_filtered_df,
    refresh_altair,
):
    # Plot: scatter points + logistic curves (wigglystuff HTMLRefreshWidget + @refresh_altair)
    @refresh_altair
    def _psychometric_chart(bands_pd, fitted_pd, ground_truth_pd, points_pd):
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
        return alt.layer(*plot_layers).resolve_scale(color="shared")


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
                    "Type": [
                        "Ground Truth" if blk.get("is_ground_truth", False) else "Fitted"
                    ]
                    * len(x),
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
    fits_df = fits_df.with_columns(
        pl.col("Series").str.replace(r" \(GT\)$", "").alias("BlockGroup"),
    )
    ground_truth_df = fits_df.filter(pl.col("Type") == "Ground Truth")
    fitted_df = fits_df.filter(pl.col("Type") == "Fitted")
    fitted_pd = fitted_df.to_pandas()
    ground_truth_pd = ground_truth_df.to_pandas()
    bands_pd = bands_df.to_pandas()
    points_pd = points_plot_df.to_pandas()
    plot_ui = HTMLRefreshWidget(
        html=_psychometric_chart(bands_pd, fitted_pd, ground_truth_pd, points_pd),
    )
    return (plot_ui,)


@app.cell
def format_dropdown(mo):
    format_dropdown = mo.ui.dropdown(
        options={
            "CSV (zip)": "csv_zip",
            "JSON": "json",
            "Parquet": "parquet",
            "DuckDB": "duckdb",
        },
        value="CSV (zip)",
        label="Format",
    )
    return (format_dropdown,)


@app.cell
def data_downloads_cell(
    blocks_df,
    format_dropdown,
    mo,
    pa_export,
    points_filtered_df,
    trials_df,
):
    from datetime import datetime

    # Use refactored export functions from pa_export module
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M")
    csv_zip = pa_export.to_csv_zip(trials_df, points_filtered_df, blocks_df)
    json_bytes = pa_export.to_json(points_filtered_df)
    parquet_bytes = pa_export.to_parquet(points_filtered_df)
    duckdb_bytes = pa_export.to_duckdb(trials_df, points_filtered_df, blocks_df)

    format_to_content: dict[str, tuple[bytes, str]] = {
        "csv_zip": (csv_zip, f"{timestamp}_psychoanalyze.zip"),
        "json": (json_bytes, "data.json"),
        "parquet": (parquet_bytes, "data.parquet"),
        "duckdb": (duckdb_bytes, "psychoanalyze.duckdb"),
    }
    _selected_key = format_dropdown.value or "csv_zip"
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
def input_tabs(
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
    step_block_dropdown,
    step_mode_toggle,
    step_subject_dropdown,
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

    # Step-by-step controls with subject/block selection
    step_controls = mo.vstack(
        [
            mo.md("### Step-by-Step Visualization"),
            step_mode_toggle,
            mo.hstack([step_subject_dropdown, step_block_dropdown], gap=1)
            if step_mode_toggle.value
            else mo.md(""),
            mo.hstack([trial_step_slider, auto_play_button], gap=1)
            if step_mode_toggle.value
            else mo.md(""),
        ],
        gap=1,
    )

    simulation_content = mo.vstack(
        [
            mo.md("### Simulation Mode"),
            mo.md("### Sampling Method"),
            sampling_method_dropdown,
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
