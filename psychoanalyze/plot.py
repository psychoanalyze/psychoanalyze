import plotly.express as px


def thresholds(data):
    return px.scatter(
        data.reset_index(),
        x="Day",
        y="Threshold",
        color="Subject",
        template="plotly_white",
    )


def curve(points):
    return px.scatter(points, y="Hit Rate", template="plotly_white")
