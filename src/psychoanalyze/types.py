
"""Patito schemas for psychoanalyze dataframes.

Contains data table schemas of the hierarchical entities described above.
Uses patito for Polars DataFrame validation.
"""

from typing import TYPE_CHECKING

import patito as pt
from pydantic import BaseModel

if TYPE_CHECKING:
    from datetime import datetime

session_dims = ["Subject", "Date"]
block_stim_dims = ["Amp2", "Width2", "Freq2", "Dur2"]
block_channel_dims = ["Active Channels", "Return Channels"]
block_dims = block_stim_dims + block_channel_dims
point_dims = ["Amp1", "Width1", "Freq1", "Dur1"]

block_index_levels = session_dims + block_dims
points_index_levels = block_index_levels + point_dims

class Stimulus(BaseModel):
    amplitude: float
    pulse_width: float
    frequency: float
    duration: float

class Block(BaseModel):
    subject: str
    date: datetime

class Trial(pt.Model):
    """Trial-level data schema."""

    reference_stimulus: Stimulus
    test_stimulus: Stimulus
    result: int
    block: Block


class FitParams(BaseModel):
    location: float
    slope: float
    guess_rate: float
    lapse_rate: float

class PyMCParams(BaseModel):
    draws: int = 1000
    tune: int = 1000
    chains: int = 2
    target_accept: float = 0.9