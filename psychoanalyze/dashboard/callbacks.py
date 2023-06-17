from dash import Input, Output
import pandas as pd
import psychoanalyze as pa
import plotly.express as px
from .app import app


@app.callback(
    Output("plot", "figure"),
    Input("table", "derived_virtual_selected_rows"),
    Input("plot-tabs", "active_tab"),
    Input("blocks-store", "data"),
    Input("points-store", "data"),
)
def update_plot(selected_blocks, active_tab, blocks_store, points_store):
    blocks = (
        pd.DataFrame.from_records(blocks_store)
        if blocks_store
        else pd.DataFrame(
            {"slope": pd.Series(dtype=float), "threshold": pd.Series(dtype=float)},
            index=pd.MultiIndex.from_frame(
                pd.DataFrame(
                    {
                        "Subject": pd.Series(dtype=str),
                        "Block": pd.Series(dtype=int),
                    },
                ),
            ),
        )
    )
    points = (
        pd.DataFrame.from_records(points_store)
        if points_store
        else pd.DataFrame(
            {"Hit Rate": pd.Series(dtype=float)},
            index=pd.MultiIndex.from_frame(
                pd.DataFrame(
                    {
                        "Subject": pd.Series(dtype=str),
                        "Block": pd.Series(dtype=int),
                        "Intensity": pd.Series(dtype=float),
                    }
                ),
            ),
        )
    )
    if not selected_blocks:
        filtered_blocks = blocks
    else:
        filtered_blocks = blocks.loc[selected_blocks]
    filtered_points = points.join(filtered_blocks)
    if active_tab == "psi-tab":
        return (
            px.scatter(
                filtered_points.reset_index(),
                x="Intensity",
                y="Hit Rate",
                color="Subject",
                template=pa.plot.template,
            )
            # .add_trace(go.Scatter(x=x, y=y, mode="lines", name="model")),
        )
    # elif active_tab == "ecdf-tab":
    #     return (
    #         px.ecdf(
    #             params,
    #             x="Threshold",
    #             color="Subject",
    #             template=pa.plot.template,
    #         ),
    #         params.to_dict("records"),
    #     )
    # elif active_tab == "time-series-tab":
    #     return (
    #         px.scatter(
    #             params,
    #             x="Block",
    #             y="Threshold",
    #             symbol="Subject",
    #             template=pa.plot.template,
    #         ),
    #         params.to_dict("records"),
    #     )
    # elif active_tab == "sd-tab":
    #     return (
    #         px.box(
    #             params.rename(columns={
    # "Threshold": "Threshold (modulated dimension)"}),
    #             x="Fixed Intensity",
    #             y="Threshold (modulated dimension)",
    #             color="Subject",
    #             template=pa.plot.template,
    #         ),
    #         params.to_dict("records"),
    #     )
    # px.ecdf(
    #     params.reset_index(),
    #     x="slope",
    #     color="Subject",
    #     template=pa.plot.template,
    # ),


@app.callback(
    Output("points-store", "data"),
    Output("table", "data"),
    Output("blocks-store", "data"),
    [
        Input("n-trials", "value"),
        Input("model-k", "value"),
        Input("x_0", "value"),
        Input("gamma", "value"),
        Input("lambda", "value"),
        Input("n-subjects", "value"),
        Input("dataset", "value"),
    ],
)
def update_data(
    n_trials,
    k,
    x_0,
    gamma,
    lambda_,
    n_subjects,
    dataset,
):
    if dataset == "schlich2022":
        points = pd.read_csv("data/normalized/points.csv")
        blocks = pd.read_csv("data/fit.csv")

        return (
            [
                px.box(
                    points,
                    x="Charge",
                    y="Hit Rate",
                    # color="Subject",
                    template=pa.plot.template,
                )
            ]
            + [
                px.ecdf(
                    blocks,
                    x="Threshold",
                    template=pa.plot.template,
                )
            ]
            * 2
            + [px.scatter()] * 2
        )
    else:
        # n_days = 5
        # model_params = {"x_0": x_0, "k": k, "gamma": gamma, "lambda": lambda_}
        trials = pa.trials.generate(100)
        points = pa.points.from_trials(trials)
        # x = list(np.linspace(intensities.min(), intensities.max()))
        # y = [pa.trials.psi(gamma, lambda_, k, intensity, x_0) for intensity in x]

        # fits = (
        #     trials.reset_index(level="Intensity")
        #     .groupby(["Subject", "Block"])
        #     .apply(pa.blocks.get_fit)
        # )

        # params = params.reset_index().rename(columns={"intercept": "Threshold"})
        blocks = pa.blocks.from_trials(trials)
        blocks_store = blocks.to_dict("records")
        points_store = points.to_dict("records")
        fits = (
            trials.reset_index(-1)
            .groupby(["Subject", "Block"])
            .apply(pa.blocks.get_fit)
        )
        return (
            points_store,
            fits.to_dict("records"),
            blocks_store,
        )
