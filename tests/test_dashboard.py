# Copyright 2023 Tyler Schlichenmeyer

# This file is part of PsychoAnalyze.
# PsychoAnalyze is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# PsychoAnalyze is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# PsychoAnalyze. If not, see <https://www.gnu.org/licenses/>.

"""Test dashboard callbacks."""


from contextvars import copy_context

from dash._callback_context import context_value  # type: ignore[import]
from dash._utils import AttributeDict  # type: ignore[import]
from hypothesis import given
from hypothesis.strategies import integers

from psychoanalyze.dashboard.app import update_trials


@given(integers(), integers(), integers())
def test_update_trials(n_levels: int, trials_per_block: int, n_blocks: int):
    contents = None
    filename = None
    n_levels = 7
    trials_per_block = 100
    n_blocks = 5
    n_params = [n_levels, trials_per_block, n_blocks]
    location = 0
    scale = 1
    params = [location, scale]

    def input_trigger():  # noqa: ANN202
        context_value.set(
            AttributeDict(triggered_inputs=[{"prop_id": '{"type": "n-param"}'}]),
        )
        return update_trials(contents, filename, n_params, params)

    ctx = copy_context()
    output = ctx.run(input_trigger)

    trials = output[0]

    assert len(trials) == trials_per_block * n_blocks
