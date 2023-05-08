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
        trials = pd.Series(
            data[data.columns[-1]],
            index=pd.MultiIndex.from_frame(data[data.columns[0:-1]]),
        )
        blocks = pa.blocks.from_trials(trials)
        subjects = pa.blocks.monkey_counts(blocks)
        output_data = subjects.to_frame().reset_index()
        return [dash.dash_table.DataTable(output_data.to_dict("records"))]
