from dash import Dash, dcc, Input, Output, State  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import psychoanalyze as pa
from psychoanalyze.layout import simulation_tab, experiment_tab
from scipy.special import expit
import plotly.express as px
from statsmodels.stats import anova

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

experiment_points = pa.points.load()
experiment_points = experiment_points.xs(("Z", "2017-01-10"))

stim_levels = list(range(-3, 4))
p = expit(stim_levels)

trials = pa.trials.generate(100, stim_levels)
points = pa.points.from_trials(trials)

df = pa.weber.load("data/weber_curves.csv")
df = df[df["Reference Charge (nC)"] != 260]
df = df[df["Date"] != "3/26/2018"]
df = df[df["Date"] != "4/30/2018"]
df["err+"] = (df["location_CI_5"] * df["Fixed_Param_Value"] / 1000) - df[
    "Threshold_Charge_nC"
]
df["err-"] = (
    df["Threshold_Charge_nC"] - (df["location_CI_95"]) * df["Fixed_Param_Value"] / 1000
)
weber_blocks = df
weber_blocks["Difference Threshold (nC)"] = weber_blocks[
    "Difference Threshold (nC)"
].abs()
weber_blocks["err+"] = weber_blocks["err+"].abs()
weber_blocks["err-"] = weber_blocks["err-"].abs()

app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                experiment_tab(experiment_points),
                simulation_tab(points),
            ]
        ),
        dcc.Graph(
            figure=px.scatter(
                pa.weber.aggregate(weber_blocks).reset_index(),
                x="Reference Charge (nC)",
                y="Difference Threshold (nC)",
                color="Monkey",
                color_discrete_map=pa.plot.colormap,
                symbol="Dimension",
                symbol_map={"Amp": "diamond", "Width": "diamond-open"},
                size="count",
                error_y="std",
                template=pa.plot.template,
                trendline="ols",
            ).update_layout(xaxis_range=(0, 250))
            # .write_image("figures/fig6A.svg", width=600)
        ),
        dcc.Store(data=pa.trials.to_store(trials), id="trials"),
    ]
)


@app.callback(
    Output("weber", "figure"),
    [
        Input("trendline", "value"),
        Input("group-x", "value"),
        Input("log-scale", "value"),
        Input("marginal", "value"),
        Input("error", "value"),
        Input("stable", "value"),
    ],
)
def format_weber_plot(
    trendline, group_x, log_scale, marginal, error_y, stable_sessions
):
    fig = pa.weber.plot(
        weber_blocks, trendline, group_x, log_scale, marginal, error_y, stable_sessions
    )
    results = px.get_trendline_results(fig)
    anova.anova_lm(*list(results["px_fit_results"].values)).to_csv("data/anova_all.csv")
    results_U = results[results["Monkey"] == "U"]
    anova.anova_lm(*list(results_U["px_fit_results"].values)).to_csv("data/anova_U.csv")

    results_Y = results[results["Monkey"] == "Y"]
    anova.anova_lm(*list(results_Y["px_fit_results"].values)).to_csv("data/anova_Y.csv")

    return fig


@app.callback(
    Output("points", "figure"), Input("fit", "n_clicks"), State("trials", "data")
)
def fit_curves(n_clicks, trials):
    points = pa.points.from_store(trials)
    if n_clicks:
        fits = pa.blocks.fit(points)
        fit_plot = pa.blocks.plot_fits(fits)
        return pa.points.combine_plots(pa.points.plot(experiment_points), fit_plot)
    else:
        return pa.points.plot(experiment_points)


@app.callback(Output("weber-width", "width"), Input("weber-width-input", "value"))
def adjust_figure_width(width):
    return width


@app.callback(Output("weber-time", "figure"), Input("weber-width-input", "value"))
def plot_weber_v_time_plot(dummy):
    return px.scatter(
        weber_blocks, x="Date", y="Threshold", color="Monkey", template="plotly_white"
    )


# @app.callback(
#     Output("trials", "data"), Input("n-trials", "value"), State("trials", "data")
# )
# def add_or_remove_trials(n_trials, trials):
#     trials = pd.read_json(trials, orient="split")
#     trials.index.name = "x"
#     if n_trials > len(trials):
#         n_new_trials = n_trials - len(trials)
#         trials = pd.concat([trials, pa.trials.generate(n_new_trials)])
#     return trials.to_json(orient="split")


# @app.callback(
#     [Output("psych-plot", "figure"), Output("psych-table", "data")],
#     Input("trials", "data"),
# )
# def plot_from_data(trials):
#     trials_df = pd.read_json(trials, orient="split")
#     trials_df.index.name = "x"
#     points = pa.points.from_trials(trials_df)
#     points["Hit Rate"] = points["Hits"] / points["n"]
#     points_list = points.reset_index().to_dict("records")
#     return pa.points.plot(points), points_list


if __name__ == "__main__":
    app.run_server(debug=True)
