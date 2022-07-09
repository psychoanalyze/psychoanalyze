import plotly.express as px  # type: ignore


def plot(data):
    return px.scatter(
        data.reset_index(),
        x="Reference Charge (nC)",
        y="Difference Threshold (nC)",
        color="Monkey",
        symbol="Dimension",
        error_y="err_y",
    )


def aggregate(data):
    return data.groupby("Reference Charge (nC)").mean().reset_index()


def from_curves(curves):
    curves["Reference Charge (nC)"] = curves["Reference PW"] * curves["Reference Amp"]
    curves["Difference Threshold (nC)"] = curves["Threshold"]
    return curves
