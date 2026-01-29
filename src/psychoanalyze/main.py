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

"""PsychoAnalyze command line interface."""

import importlib.metadata
import subprocess
import sys

import typer
from rich.console import Console

app = typer.Typer()


@app.command()
def main(command: str) -> None:
    """Main commands."""
    if command == "version":
        Console().print(importlib.metadata.version("psychoanalyze"))
    if command == "marimo":
        subprocess.run(
            [sys.executable, "-m", "marimo", "edit", "app.py"],
        )
