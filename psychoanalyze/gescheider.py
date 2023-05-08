import plotly.express as px
import pandas as pd


def p3_1(data: pd.Series):
    data.index.name = "φ"
    return px.line(data.rename("P"), y="P")
