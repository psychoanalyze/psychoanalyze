import psychoanalyze as pa


def xlabel():
    pass


def from_blocks(blocks, dim=None):
    if dim == "Amp":
        ylabel = "Threshold Amplitude (μA)"
        xlabel = "Fixed Pulse Width (μs)"
    elif dim == "Width":
        ylabel = "Fixed Amplitude (μA)"
        xlabel = "Threshold Pulse Width (μs)"

    blocks[ylabel] = blocks["Threshold"]
    blocks[xlabel] = blocks["Fixed Magnitude"]
    return blocks.drop(columns=["Threshold", "Fixed Magnitude"])


def plot(plot_type, dim=None):
    return pa.plot.strength_duration(dim=dim, plot_type=plot_type)
