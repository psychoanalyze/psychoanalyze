import pandas as pd
import plotly.express as px


def p3_1(data: pd.Series):
    data.index.name = "φ"
    return px.line(data.rename("P"), y="P")
