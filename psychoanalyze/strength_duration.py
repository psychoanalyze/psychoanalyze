import pandas as pd

import psychoanalyze as pa


def xlabel():
    pass


def data(df, dim=None):
    if dim == "amp":
        df["Threshold Amplitude (μA)"] = df["Threshold"]
        df["Fixed Pulse Width (μs)"] = df["Fixed Magnitude"]
        df = df.drop(columns=["Threshold", "Fixed Magnitude"])

    elif dim == "pw":
        df["Fixed Amplitude (μA)"] = df["Threshold"]
        df["Threshold Pulse Width (μs)"] = df["Fixed Magnitude"]
        df = df.drop(columns=["Threshold", "Fixed Magnitude"])
    return df


def plot(plot_type, dim=None):
    return pa.plot.strength_duration(dim=dim, plot_type=plot_type)
