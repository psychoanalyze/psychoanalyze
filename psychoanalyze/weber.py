import plotly.express as px  # type: ignore


def plot(data, trendline=None):
    return px.scatter(
        data.reset_index(),
        x="Reference Charge (nC)",
        y="Difference Threshold (nC)",
        color="Monkey",
        symbol="Dimension",
        trendline=trendline,
        template="plotly_white",
    )


def aggregate(data):
    return data.groupby("Reference Charge (nC)").mean().reset_index()
