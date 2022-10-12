import pandas as pd


def xlabel():
    pass


def data(df=None, dim=None):
    df = pd.DataFrame({"Monkey": [], "Day": []})
    if dim == "amp":
        df["Threshold Amplitude (μA)"] = []
        df["Fixed Pulse Width (μs)"] = []
    elif dim == "pw":
        df["Fixed Amplitude (μA)"] = []
        df["Threshold Pulse Width (μs)"] = []
    return df
