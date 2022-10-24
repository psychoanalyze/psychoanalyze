from pathlib import Path
from dash import Dash, Output, Input
import dash_bootstrap_components as dbc
import psychoanalyze as pa
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app.layout = pa.dash.layout


@app.callback(
    Output("day-select", "marks"),
    Output("day-select", "value"),
    Input("monkey-select", "value"),
)
def day_marks(monkey):
    sessions = pa.sessions.load_cached(Path("data"), monkey=monkey)
    session_max_n_index = sessions["n Trials"].idxmax()
    day_value = sessions.loc[session_max_n_index, "Day"]
    day_marks = {
        float(sessions.loc[i, "Day"]): str(sessions.loc[i, "Day"])
        for i in sessions.index.values
    }
    if len(day_marks):
        return day_marks, day_value


@app.callback(Output("day-display", "children"), Input("day-select", "value"))
def display_day(day):
    return f"Day {day}"


@app.callback(
    Output("ref-stimulus-table", "data"),
    Input("monkey-select", "value"),
    Input("day-select", "value"),
    Input("dim-select", "value"),
)
def display_ref_stimulus_table(monkey, day, dim):
    blocks = pa.blocks.load(monkey=monkey, day=day, dim=dim)
    session_cols = ["Monkey", "Date"]
    ref_stim_cols = ["Amp2", "Width2", "Freq2", "Dur2"]
    return (
        blocks.reset_index()
        .drop(
            columns=session_cols
            + [
                "Dimension",
                "n Levels",
                "Day",
            ]
            + ref_stim_cols
        )
        .to_dict("records")
    )


@app.callback(
    Output("psychometric-fig", "figure"),
    Output("Threshold-value", "children"),
    Output("width-value", "children"),
    Output("gamma-value", "children"),
    Output("lambda-value", "children"),
    Output("Threshold-err+", "children"),
    Output("Threshold-err-", "children"),
    Input("monkey-select", "value"),
    Input("day-select", "value"),
    Input("ref-stimulus-table", "selected_rows"),
    Input("fit-button", "n_clicks"),
)
def plot_selected_block(monkey, day, row_numbers, n_clicks):
    if row_numbers is None:
        points = pd.DataFrame({"x": [], "Hit Rate": []})
    else:
        if len(row_numbers):
            blocks = pa.blocks.load(monkey=monkey, day=day)
            blocks = blocks.iloc[row_numbers]
            points = pa.points.load()
            points = blocks.join(points)
            x_range = (points["x"].min(), points["x"].max())
            if os.path.exists("data/fit.csv"):
                fit = pa.blocks.read_fit("data/fit.csv", blocks.index[0])
                if len(fit):
                    fig = go.Figure(
                        data=pa.points.plot(points).data
                        + pa.plot.psychometric(
                            fit,
                            x_range=x_range,
                        ).data,
                        layout_template=pa.plot.template,
                    )
                    return (
                        fig,
                        f'{fit["Threshold"]: .2f}',
                        f'{fit["width"]: .2f}',
                        f'{fit["gamma"]: .2f}',
                        f'{fit["lambda"]: .2f}',
                        None,
                        None,
                    )
                else:
                    return pa.points.plot(points), None, None, None, None, None, None
            if n_clicks:
                fit = pa.points.fit(
                    points, save_to="data/fit.csv", block=blocks.index[0]
                )
                return (
                    go.Figure(
                        data=pa.points.plot(points).data
                        + pa.plot.psychometric(
                            fit=fit,
                            x_range=x_range,
                        ).data,
                        layout_template=pa.plot.template,
                    ),
                    *fit,
                )
        else:
            points = pd.DataFrame({"x": [], "Hit Rate": []})
    base_plot = pa.points.plot(points)
    return (
        base_plot,
        *(None, None, None, None),
        None,
        None,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
