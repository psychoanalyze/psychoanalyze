"""PsychoAnalyze dashboard as a marimo notebook.

Interactive data simulation & analysis for psychophysics.
Replaces the former Dash dashboard (removed).
"""

import marimo

__generated_with = "0.19.7"
app = marimo.App(width="full", app_title="PsychoAnalyze")


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
        mu_slope = rng.normal(0.0, 2.5)
        sigma_slope = np.abs(rng.normal(0.0, 2.5))

        # Sample block-level params from hyperpriors
        intercept = rng.normal(mu_intercept, sigma_intercept)
        slope = rng.normal(mu_slope, sigma_slope)

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
    ) -> tuple[pl.DataFrame, dict[tuple[str, int], dict]]:
        """Generate trials and return both data and block-specific parameters.

        Args:
            use_random_params: If True, ignore params and generate from priors
            random_seed: Random seed for parameter generation

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

                # Generate trials for this block
                block_trials = pa_trials.generate(
                    n_trials=n_trials,
                    options=options,
                    params=block_params,
                    n_blocks=1,
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
    n_subjects = mo.ui.number(value=2, start=1, stop=50, step=1, label="subjects")

    input_form = (
        mo.md(r"""
    ## Simulation Parameters

    **Link function:** $\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$

    **Model** {x_0_free} {x_0} {k_free} {k} {gamma_free} {gamma} {lambda_free} {lambda_}

    **Stimulus** {n_levels}

    **Simulation** {n_trials} {n_blocks} {n_subjects}
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
            n_subjects=n_subjects,
        )
        .form(submit_button_label="Generate")
    )
    return (
        gamma,
        input_form,
        k,
        lambda_,
        n_blocks,
        n_levels,
        n_subjects,
        n_trials,
        x_0,
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
    gamma,
    generate_index,
    generate_trials,
    input_tabs,
    k,
    lambda_,
    load_sample_trials,
    max_x,
    min_x,
    n_blocks,
    n_levels,
    n_subjects,
    n_trials,
    pl,
    process_upload_bytes,
    subject_utils,
    x_0,
):
    # Trials: upload if provided, otherwise default to sample in Batch/Online
    ground_truth_params = {}
    use_random_params = input_tabs.value == "Simulation"

    if file_upload.value and len(file_upload.value) > 0:
        raw = file_upload.contents(0)
        fname = file_upload.name(0) or ""
        if raw is not None:
            trials_df = process_upload_bytes(raw, fname)
        else:
            trials_df, ground_truth_params = generate_trials(
                n_trials=n_trials.value,
                options=generate_index(n_levels.value, [min_x, max_x]),
                params={
                    "x_0": x_0.value,
                    "k": k.value,
                    "gamma": gamma.value,
                    "lambda": lambda_.value,
                },
                n_blocks=n_blocks.value,
                n_subjects=n_subjects.value,
                use_random_params=use_random_params,
                random_seed=int(fit_random_seed.value) if fit_random_seed.value > 0 else None,
            )
    elif input_tabs.value == "Simulation":
        trials_df, ground_truth_params = generate_trials(
            n_trials=n_trials.value,
            options=generate_index(n_levels.value, [min_x, max_x]),
            params={
                "x_0": x_0.value,
                "k": k.value,
                "gamma": gamma.value,
                "lambda": lambda_.value,
            },
            n_blocks=n_blocks.value,
            n_subjects=n_subjects.value,
            use_random_params=use_random_params,
            random_seed=int(fit_random_seed.value) if fit_random_seed.value > 0 else None,
        )
    else:
        trials_df = load_sample_trials()
    trials_df = subject_utils.ensure_subject_column(trials_df)
    trials_df = trials_df.with_columns(pl.col("Intensity").cast(pl.Float64))
    return ground_truth_params, trials_df


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
def _(mo):
    fit_button = mo.ui.run_button(
        label="Fit Model",
        kind="success",
    )
    return (fit_button,)


@app.cell
def _(trial_crop_slider, trials_df):
    # Apply trial crop
    crop_at = trial_crop_slider.value
    trials_cropped_df = trials_df.head(crop_at)
    return (trials_cropped_df,)


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
    trials_cropped_df,
):
    # Points always computed from trials
    points_df = from_trials(trials_cropped_df)

    # Only run fitting if button clicked or on Simulation tab
    if should_fit:
        composite_block = (
            pl.col("Subject").cast(pl.Utf8) + "__" + pl.col("Block").cast(pl.Utf8)
        )
        fit_trials_df = trials_cropped_df.with_columns(composite_block.alias("Block"))
        cache_key = trials_cache_key(trials_cropped_df, fit_params)
        fit_summary, fit_idata = cached_hierarchical_fit(
            fit_trials_df,
            cache_key,
            fit_params,
        )
        fit_blocks = fit_trials_df["Block"].unique().sort().to_list()
        block_idx_by_key = {block: idx for idx, block in enumerate(fit_blocks)}

        blocks_list = []
        block_idx_by_subject_block: dict[tuple[str, int], int] = {}
        block_keys = trials_cropped_df.select(["Subject", "Block"]).unique()
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

            _block_dict = {
                "Block": block_id,
                "Subject": subject_id,
                "intercept": _est_intercept,
                "slope": _est_slope,
                "gamma": _est_gamma,
                "lambda": _est_lambda,
                "x_0 (est)": _est_x_0,
                "k (est)": _est_k,
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
def _(
    block,
    block_idx_by_subject_block: dict[tuple[str, int], int],
    blocks_df,
    blocks_table,
    ground_truth_params,
    pl,
    subject,
):
    # Selected block rows for plot (include ground truth per block)
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
    if len(blocks_df) > 0:
        # Reorder columns to show actual vs estimated side by side for display
        col_order = ["Subject", "Block"]
        param_cols = ["x_0", "k", "gamma", "lambda"]
        for param in param_cols:
            if f"{param} (actual)" in blocks_df.columns:
                col_order.append(f"{param} (actual)")
            if f"{param} (est)" in blocks_df.columns:
                col_order.append(f"{param} (est)")
        # Add remaining columns that aren't already included
        for col in blocks_df.columns:
            if col not in col_order:
                col_order.append(col)

        display_df = blocks_df.select([c for c in col_order if c in blocks_df.columns])

        format_mapping = {
            "intercept": "{:.3f}".format,
            "slope": "{:.3f}".format,
            "intercept (actual)": "{:.3f}".format,
            "slope (actual)": "{:.3f}".format,
            "x_0 (actual)": "{:.3f}".format,
            "x_0 (est)": "{:.3f}".format,
            "k (actual)": "{:.3f}".format,
            "k (est)": "{:.3f}".format,
            "gamma": "{:.3f}".format,
            "lambda": "{:.3f}".format,
            "gamma (actual)": "{:.3f}".format,
            "lambda (actual)": "{:.3f}".format,
        }

        blocks_table = mo.ui.table(
            display_df.to_pandas(),
            selection="multi",
            initial_selection=[0, 1]
            if len(display_df) > 1
            else list(range(len(display_df))),
            label="Blocks",
            format_mapping=format_mapping,
        )
    else:
        blocks_table = mo.ui.table(
            [],
            selection="multi",
            label="Blocks",
        )
    return (blocks_table,)


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
            color=alt.Color("Series:N"),
        )
    )
    ground_truth_line_chart = (
        alt.Chart(ground_truth_pd)
        .mark_line(strokeDash=[5, 5], strokeWidth=2)
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
    plot_layers = [fitted_line_chart, points_chart]
    if len(ground_truth_pd) > 0:
        plot_layers.insert(0, ground_truth_line_chart)
    if len(bands_pd) > 0:
        plot_layers.insert(0, band_chart)
    plot_chart = alt.layer(*plot_layers).resolve_scale(color="shared")
    plot_ui = mo.ui.altair_chart(plot_chart)
    return (plot_ui,)


@app.cell
def _(blocks_df, mo, pl, points_filtered_df, trials_cropped_df):
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
    fit_button,
    fit_settings,
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
            fit_settings,
            stimulus_info,
            fit_button,
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
            fit_settings,
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


if __name__ == "__main__":
    app.run()
