"""Generate the code reference pages."""

from pathlib import Path
import mkdocs_gen_files

with mkdocs_gen_files.open(Path("API.md"), "w") as fd:
    print("::: psychoanalyze", file=fd)
