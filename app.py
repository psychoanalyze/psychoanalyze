# Copyright 2023 Tyler Schlichenmeyer
# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""PsychoAnalyze dashboard as a marimo notebook.

Interactive data simulation & analysis for psychophysics.
Replaces the former Dash dashboard (removed).
"""

import marimo

__generated_with = "0.19.2"
app = marimo.App(width="columns")


@app.cell
def __():
    import io
    import zipfile

    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from scipy.special import expit, logit
    from sklearn.linear_model import LogisticRegression

    def to_intercept(location: float, scale: float) -> float:
        return -location / scale

    def to_slope(scale: float) -> float:
        return 1 / scale

    def psi(intensity: float, params: dict) -> float:
        gamma = params.get("gamma", 0.0)
        lambda_ = params.get("lambda", 0.0)
        k = params["k"]
        x_0 = params["x_0"]
        return gamma + (1 - gamma - lambda_) * (
            1 / (1 + np.exp(-k * (intensity - x_0)))
        )

    def generate_index(n_levels: int, x_range: list[float]) -> pd.Index:
        return pd.Index(
            np.linspace(x_range[0], x_range[1], n_levels), name="Intensity"
        )

    def generate_trials(
        n_trials: int,
        options: pd.Index,
        params: dict,
        n_blocks: int,
    ) -> pd.DataFrame:
        rng = np.random.default_rng()
        out = []
        for i in range(n_blocks):
            intensities = rng.choice(options.to_numpy(), size=n_trials)
            results = np.array(
                [int(rng.random() <= psi(x, params)) for x in intensities]
            )
            df = pd.DataFrame({"Intensity": intensities, "Result": results})
            df["Block"] = i
            out.append(df)
        return pd.concat(out, ignore_index=True)[["Block", "Intensity", "Result"]]

    def from_trials(trials_df: pd.DataFrame) -> pd.DataFrame:
        points = trials_df.groupby(["Block", "Intensity"])["Result"].agg(
            ["count", "sum"]
        )
        points = points.rename(columns={"count": "n trials", "sum": "Hits"})
        points["Hit Rate"] = points["Hits"] / points["n trials"]
        return points.reset_index()

    def block_fit(trials_df: pd.DataFrame) -> pd.Series:
        fit = LogisticRegression().fit(
            trials_df[["Intensity"]], trials_df["Result"]
        )
        return pd.Series({
            "intercept": float(fit.intercept_[0]),
            "slope": float(fit.coef_[0][0]),
        })

    def process_upload_bytes(contents: bytes, filename: str) -> pd.DataFrame:
        if "zip" in filename:
            with zipfile.ZipFile(io.BytesIO(contents)) as z:
                return pd.read_csv(z.open("trials.csv"))
        return pd.read_csv(io.BytesIO(contents.decode("utf-8")))

    return (
        mo,
        np,
        pd,
        px,
        go,
        expit,
        logit,
        process_upload_bytes,
        block_fit,
        from_trials,
        generate_index,
        generate_trials,
        to_intercept,
        to_slope,
    )


@app.cell
def _(mo):
    # Header
    mo.md(
        r"""
        # PsychoAnalyze
        *Interactive data simulation & analysis for psychophysics.*

        [Notebooks](https://nb.psychoanalyze.io) · [GitHub](https://github.com/psychoanalyze/psychoanalyze) · [Docs](https://docs.psychoanalyze.io)
        """
    )
    return


@app.cell
def _(mo):
    # File upload
    file_upload = mo.ui.file(
        filetypes=[".csv", ".zip"],
        kind="area",
        label="Upload CSV/parquet with columns: **Block, Intensity, Result.** Your data stays in the browser.",
    )
    file_upload
    return (file_upload,)


@app.cell
def _(mo):
    # Link function (display only in marimo)
    mo.md(r"## Link function: $\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$")
    return


@app.cell
def _(mo):
    # Model parameters: x_0, k; preset dropdown
    x_0_num = mo.ui.number(value=0.0, step=0.1, label="$x_0$")
    k_num = mo.ui.number(value=1.0, step=0.1, label="$k$")
    preset_dropdown = mo.ui.dropdown(
        options={
            "standard": "Standard",
            "non-standard": "Non Standard",
            "2AFC": "2AFC",
        },
        value="standard",
        label="Presets",
    )
    mo.hstack(
        [
            mo.md("**Model parameters** "),
            x_0_num,
            k_num,
            preset_dropdown,
        ],
        gap=2,
    )
    return (k_num, preset_dropdown, x_0_num)


# Preset dropdown is for reference; edit x₀ and k in the number inputs above.


@app.cell
def _(k_num, x_0_num):
    # Single source of truth for x_0, k (avoids MultipleDefinitionError)
    x_0 = x_0_num.value if x_0_num.value is not None else 0.0
    k = k_num.value if k_num.value is not None else 1.0
    return (k, x_0)


@app.cell
def _(k, logit, mo, to_intercept, to_slope, x_0):
    # Stimulus: min_x, max_x (computed), n_levels
    intercept = to_intercept(x_0, k)
    slope = to_slope(k)
    min_x = (logit(0.01) - intercept) / slope
    max_x = (logit(0.99) - intercept) / slope
    n_levels_num = mo.ui.number(value=7, start=2, stop=50, step=1, label="n levels")
    mo.hstack(
        [
            mo.md("**Stimulus** min / n levels / max: "),
            mo.md(f"*{min_x:.2f}*"),
            n_levels_num,
            mo.md(f"*{max_x:.2f}*"),
        ],
        gap=2,
    )
    return (intercept, max_x, min_x, n_levels_num, slope)


@app.cell
def _(mo, n_levels_num):
    # Simulate: n_trials, n_blocks
    n_trials_num = mo.ui.number(
        value=100, start=1, stop=10000, step=1, label="trials per block"
    )
    n_blocks_num = mo.ui.number(
        value=5, start=1, stop=100, step=1, label="blocks"
    )
    mo.hstack(
        [
            mo.md("**Simulate** "),
            n_trials_num,
            n_blocks_num,
        ],
        gap=2,
    )
    return (n_blocks_num, n_trials_num)


@app.cell
def _(
    file_upload,
    generate_index,
    generate_trials,
    k,
    max_x,
    min_x,
    n_blocks_num,
    n_levels_num,
    n_trials_num,
    process_upload_bytes,
    x_0,
):
    # Trials: from upload or generate
    if file_upload.value and len(file_upload.value) > 0:
        raw = file_upload.contents(0)
        fname = file_upload.name(0) or ""
        if raw is not None:
            trials_df = process_upload_bytes(raw, fname)
        else:
            trials_df = generate_trials(
                n_trials=n_trials_num.value or 100,
                options=generate_index(
                    n_levels_num.value or 7, [min_x, max_x]
                ),
                params={"x_0": x_0, "k": k, "gamma": 0.0, "lambda": 0.0},
                n_blocks=n_blocks_num.value or 5,
            )
    else:
        trials_df = generate_trials(
            n_trials=n_trials_num.value or 100,
            options=generate_index(
                n_levels_num.value or 7, [min_x, max_x]
            ),
            params={"x_0": x_0, "k": k, "gamma": 0.0, "lambda": 0.0},
            n_blocks=n_blocks_num.value or 5,
        )
    trials_df["Intensity"] = trials_df["Intensity"].astype(float)
    return (trials_df,)


@app.cell
def _(block_fit, from_trials, trials_df):
    # Points and blocks from trials
    points_df = from_trials(trials_df)
    blocks_df = (
        trials_df.groupby("Block")
        .apply(block_fit)
        .reset_index()
    )
    blocks_df["gamma"] = 0.0
    blocks_df["lambda"] = 0.0
    return (blocks_df, points_df)


@app.cell
def _(blocks_df, mo):
    # Blocks table with multi-selection
    blocks_table = mo.ui.table(
        blocks_df,
        selection="multi",
        initial_selection=[0, 2] if len(blocks_df) > 2 else list(range(len(blocks_df))),
        label="Blocks",
        format_mapping={
            "intercept": "{:.2f}".format,
            "slope": "{:.2f}".format,
        },
    )
    mo.md("## Blocks")
    blocks_table
    return (blocks_table,)


@app.cell
def _(blocks_table, blocks_df, k, x_0):
    # Selected block rows for plot (include Model)
    if blocks_table.value is not None and hasattr(blocks_table.value, "__len__"):
        try:
            selected_blocks_df = (
                blocks_table.value
                if isinstance(blocks_table.value, pd.DataFrame)
                else pd.DataFrame(blocks_table.value)
            )
        except Exception:
            selected_blocks_df = blocks_df
    else:
        selected_blocks_df = blocks_df
    # Build list of block dicts for curves: selected blocks + Model
    model_intercept = -x_0 / k
    model_slope = 1 / k
    block_rows = []
    if isinstance(selected_blocks_df, pd.DataFrame) and len(selected_blocks_df) > 0:
        for _, row in selected_blocks_df.iterrows():
            block_rows.append(
                {
                    "Block": str(row.get("Block", row.name)),
                    "intercept": row.get("intercept", 0),
                    "slope": row.get("slope", 1),
                }
            )
    else:
        for _, row in blocks_df.iterrows():
            block_rows.append(
                {
                    "Block": str(row["Block"]),
                    "intercept": row["intercept"],
                    "slope": row["slope"],
                }
            )
    block_rows.append(
        {"Block": "Model", "intercept": model_intercept, "slope": model_slope}
    )
    return (block_rows, model_intercept, model_slope, selected_blocks_df)


@app.cell
def _(blocks_table, points_df):
    # Filter points by selected blocks
    if blocks_table.value is not None:
        try:
            sel = (
                blocks_table.value
                if isinstance(blocks_table.value, pd.DataFrame)
                else pd.DataFrame(blocks_table.value)
            )
            if len(sel) > 0 and "Block" in sel.columns:
                block_ids = sel["Block"].tolist()
                points_filtered_df = points_df[
                    points_df["Block"].isin(block_ids)
                ]
            else:
                points_filtered_df = points_df
        except Exception:
            points_filtered_df = points_df
    else:
        points_filtered_df = points_df
    return (points_filtered_df,)


@app.cell
def _(block_rows, expit, go, max_x, min_x, mo, np, pd, points_filtered_df, px):
    # Plot: scatter points + logistic curves
    x = np.linspace(min_x, max_x, 100)
    fits_list = []
    for blk in block_rows:
        y = expit(
            x * blk["slope"] + blk["intercept"]
        )
        fits_list.append(
            pd.DataFrame(
                {
                    "Intensity": x,
                    "Hit Rate": y,
                    "Block": blk["Block"],
                }
            )
    )
    fits_df = pd.concat(fits_list, ignore_index=True)
    points_plot_df = points_filtered_df.copy()
    points_plot_df["Block"] = points_plot_df["Block"].astype(str)
    fits_df["Block"] = fits_df["Block"].astype(str)
    fig = px.line(
        fits_df,
        x="Intensity",
        y="Hit Rate",
        color="Block",
    )
    results_fig = px.scatter(
        points_plot_df,
        x="Intensity",
        y="Hit Rate",
        size="n trials",
        color="Block",
        template="plotly_white",
    )
    for trace in results_fig.data:
        fig.add_trace(trace)
    plot_ui = mo.ui.plotly(fig)
    mo.md(r"## Psychometric function: $\psi(x) = \gamma + (1 - \gamma - \lambda)F(x)$")
    plot_ui
    return (fig, fits_df, plot_ui, points_plot_df, results_fig)


@app.cell
def _(mo, points_filtered_df):
    # Points table
    mo.md("## Points")
    points_table = mo.ui.table(
        points_filtered_df,
        pagination=True,
        page_size=10,
        label="Points",
        format_mapping={
            "Intensity": "{:.2f}".format,
            "Hit Rate": "{:.2f}".format,
        },
    )
    points_table
    return (points_table,)


@app.cell
def _(mo):
    # Export note: tables have built-in download; plot can be saved via browser
    mo.md(
        "**Export:** Use each table's download button for data. "
        "Right-click the plot → Save image as for the figure."
    )
    return ()


if __name__ == "__main__":
    app.run()
