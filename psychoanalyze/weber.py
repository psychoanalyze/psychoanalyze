import plotly.express as px


def plot(data):
    return px.scatter(
        data.reset_index(),
        x="Reference Charge (nC)",
        y="Difference Threshold (nC)",
        color="Monkey",
        symbol="Dimension",
        error_y="err_y",
    )
