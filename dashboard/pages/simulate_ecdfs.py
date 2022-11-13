from dash import dcc, Output, Input, callback
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import random

import psychoanalyze as pa


dash.register_page(__name__, path="/")

layout = dbc.Container(
    [
        dbc.Col(
            [
                dbc.Label("Number of Blocks"),
                dbc.Input(type="number", value=50, id="n"),
            ],
            width="auto",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="ecdf-amp")),
                dbc.Col(dcc.Graph(id="ecdf-width")),
                dbc.Col(dcc.Graph(id="ecdf-nuisance")),
            ]
        ),
    ]
)


def draw(n: int, param: str) -> pd.Series:
    """
    Draw n random numbers from a normal distribution.
    """
    return pd.Series([random.gauss(0, 1) for _ in range(n)], name=param)


def plot_ecdf(param_values: pd.DataFrame, condition: str) -> px.line:
    """
    Plot ECDF of a parameter.
    """
    return px.ecdf(
        param_values, color="Monkey", line_dash="param", template=pa.plot.template
    ).update_layout(xaxis_title=condition)


def plot_nuisance_ecdf(param_values: pd.DataFrame) -> px.line:
    """
    Plot ECDF of a parameter.
    """
    return px.ecdf(
        param_values,
        x="value",
        color="Monkey",
        template=pa.plot.template,
        line_dash="param",
    )


def monkey_blocks(n: int, monkey: str) -> pd.DataFrame:
    blocks = pd.DataFrame(
        {param: draw(n, param) for param in ["location", "width", "gamma", "lambda"]}
    )
    blocks["Monkey"] = monkey
    return blocks


def condition_blocks(n: int, condition: str) -> pd.DataFrame:
    U_blocks = monkey_blocks(n, "U")
    Y_blocks = monkey_blocks(n, "Y")
    blocks = pd.concat([U_blocks, Y_blocks])
    blocks["condition"] = condition
    return blocks


@callback(
    Output("ecdf-amp", "figure"),
    Output("ecdf-width", "figure"),
    Output("ecdf-nuisance", "figure"),
    Input("n", "value"),
)
def plot_ecdfs(n):
    amp_blocks = condition_blocks(n, "Amp")
    width_blocks = condition_blocks(n, "Width")
    blocks = pd.concat([amp_blocks, width_blocks])
    nuisance_df = blocks[["gamma", "lambda", "Monkey"]].melt(
        id_vars=["Monkey"], var_name="param"
    )

    def melt_blocks(blocks: pd.DataFrame):
        return blocks[["location", "width", "Monkey"]].melt(
            id_vars=["Monkey"], var_name="param"
        )

    return (
        plot_ecdf(melt_blocks(amp_blocks), "Amplitude"),
        plot_ecdf(melt_blocks(width_blocks), "Pulse Width"),
        plot_nuisance_ecdf(nuisance_df),
    )
