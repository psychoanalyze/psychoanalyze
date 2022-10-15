import pandas as pd

import psychoanalyze as pa


def xlabel():
    pass


def from_blocks(blocks, dim=None):
    if dim == "Amp":
        blocks["Threshold Amplitude (μA)"] = blocks["Threshold"]
        blocks["Fixed Pulse Width (μs)"] = blocks["Fixed Magnitude"]
        blocks = blocks.drop(columns=["Threshold", "Fixed Magnitude"])

    elif dim == "Width":
        blocks["Fixed Amplitude (μA)"] = blocks["Threshold"]
        blocks["Threshold Pulse Width (μs)"] = blocks["Fixed Magnitude"]
        blocks = blocks.drop(columns=["Threshold", "Fixed Magnitude"])
    return blocks


def plot(plot_type, dim=None):
    return pa.plot.strength_duration(dim=dim, plot_type=plot_type)
