"""Functions relating to strength-duration analysis."""
import pandas as pd


def from_blocks(blocks: pd.DataFrame, dim: str) -> pd.DataFrame:
    """Calculate strength-duration measures from block data."""
    if dim == "Amp":
        ylabel = "Threshold Amplitude (μA)"
        xlabel = "Fixed Pulse Width (μs)"
    elif dim == "Width":
        ylabel = "Fixed Amplitude (μA)"
        xlabel = "Threshold Pulse Width (μs)"

    blocks[ylabel] = blocks["Threshold"]
    blocks[xlabel] = blocks["Fixed Magnitude"]
    return blocks.drop(columns=["Threshold", "Fixed Magnitude"])
