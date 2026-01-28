
import pandas as pd

from psychoanalyze.analysis import ecdf
def test_ecdf_location_no_data():
    blocks = pd.DataFrame({"location": []})
    ecdf_fig = ecdf.plot(blocks, "location")

    assert ecdf_fig.layout.xaxis.title.text == "location"
def test_ecdf_width_no_data():
    blocks = pd.DataFrame({"width": []})
    ecdf_fig = ecdf.plot(blocks, "width")

    assert ecdf_fig.layout.xaxis.title.text == "width"
