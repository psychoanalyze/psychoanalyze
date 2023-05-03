import pandas as pd
import dash
import base64
import io

import psychoanalyze as pa


def contents(contents, filename):
    if contents:
        contents = contents[0]
        filename = filename[0]
        _, contents = contents.split(",")
        data = pd.read_csv(io.StringIO(base64.b64decode(contents).decode("utf-8")))
        if "trials" in filename:
            data = data.set_index(
                pa.sessions.index_levels
                + pa.blocks.index_levels
                + pa.points.index_levels
                + [
                    "Trial ID",
                ]
            )
            blocks = pa.blocks.from_trials(data)
        elif filename == "blocks.csv":
            blocks = data
        subjects = pa.blocks.monkey_counts(blocks)
        output_data = subjects.to_frame().reset_index()
        return [dash.dash_table.DataTable(output_data.to_dict("records"))]
