import plotly.express as px
import pandas as pd


def p3_1(data: pd.Series):
    return px.scatter(data, y="p(yes)")
