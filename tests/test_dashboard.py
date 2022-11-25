import psychoanalyze as pa
import base64
import dash

from dashboard import app  # noqa: F401
from dashboard.pages.upload import show_contents


def test_integrate_data(mocker):
    mocker.patch("psychoanalyze.points.fit")
    n_trials_per_level = 10
    x_min = -3
    x_max = 3
    y = "p"
    curves_data = pa.blocks.generate(n_trials_per_level)

    x = pa.blocks.xrange_index(x_min, x_max)
    assert pa.blocks.prep_psych_curve(curves_data=curves_data, x=x, y=y)


def test_upload_csv():
    header = "data:application/vnd.ms-excel;base64"
    text = base64.b64encode(
        ",".join(
            [
                "Monkey",
                "Date",
                "Amp2",
                "Width2",
                "Freq2",
                "Dur2",
                "Active Channels",
                "Return Channels",
                "Amp1",
                "Width1",
                "Freq1",
                "Dur1",
                "Trial ID",
                "Result",
            ]
        ).encode("utf-8")
    ).decode("utf-8")
    contents = f"{header},{text}"
    filename = "trials_blank.csv"
    output = show_contents(contents, filename)
    assert output.data == dash.dash_table.DataTable([]).data
