import pandas as pd
import psychoanalyze as pa
import pytest
import plotly.express as px


@pytest.fixture
def trials():
    return pa.trials.fake(100, set(range(8)))


def test_thresholds():
    data = pd.DataFrame(
        {
            "Subject": ["A", "B"],
            "5%": [1, 2],
            "50%": [1, 2],
            "95%": [1, 2],
            "Day": [1, 2],
        }
    )
    fig = pa.plot.thresholds(data)
    subjects = {trace["legendgroup"] for trace in fig.data}
    assert subjects == {"A", "B"}
    assert fig.layout.xaxis.title.text == "Day"
    assert fig.layout.yaxis.title.text == "50%"


def test_standard_logistic():
    s = pa.data.logistic()
    df = s.to_frame()
    df["Type"] = "Generated"
    fig = pa.plot.logistic(df)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"


def test_combine_logistics():
    s1 = pa.data.logistic(threshold=0)
    s2 = pa.data.logistic(threshold=1)
    df = pd.concat([s1, s2], keys=["0", "1"], names=["Type"])
    assert len(pa.plot.logistic(df.reset_index()).data) == 2


def test_bayes():
    simulated = pd.DataFrame(
        {
            "x": [-4, -2, 0, 2, 4],
            "Hit Rate": [0.01, 0.19, 0.55, 0.81, 0.99],
        }
    )
    index = pd.Index([-4, -2, 0, 2, 4], name="Hit Rate")
    estimated = pd.Series([0.011, 0.2, 0.56, 0.80, 0.98], index=index)
    fig = pa.plot.bayes(simulated, estimated)
    assert fig.layout.xaxis.title.text == "x"
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert len(fig.data) == 2


def test_curves():
    curves_data = {
        "y": "p",
        "curves_df": pd.DataFrame(
            {"p": [], "err+": [], "err-": []}, index=pd.Index([], name="x")
        ),
    }
    assert pa.plot.curves(curves_data)


def test_strength_duration():
    fig = pa.plot.strength_duration(dim="Amp", plot_type="inverse")
    assert fig.layout.xaxis.title.text == "Fixed Pulse Width (μs)"
    assert fig.layout.yaxis.title.text == "Threshold Amplitude (μA)"


def test_strength_duration_pw():
    fig = pa.plot.strength_duration(dim="Width", plot_type="inverse")
    assert fig.layout.xaxis.title.text == "Fixed Amplitude (μA)"
    assert fig.layout.yaxis.title.text == "Threshold Pulse Width (μs)"


def test_strength_duration_linear_amp():
    fig = pa.plot.strength_duration(dim="Amp", plot_type="linear")
    assert fig.layout.xaxis.title.text == "Fixed Pulse Width (μs)"
    assert fig.layout.yaxis.title.text == "Threshold Charge (nC)"


def test_strength_duration_linear_width():
    fig = pa.plot.strength_duration(dim="Width", plot_type="linear")
    assert fig.layout.xaxis.title.text == "Fixed Amplitude (μA)"
    assert fig.layout.yaxis.title.text == "Threshold Charge (nC)"


def test_strength_duration_with_data():
    x_data = [1]
    y_data = [1]
    fig = pa.plot.strength_duration(
        dim="Width", plot_type="linear", x_data=x_data, y_data=y_data
    )
    assert len(fig.data) == 1


def test_strength_duration_data_filters_dimension():
    df = pd.DataFrame(
        {
            "Fixed Pulse Width (μs)": [1],
            "Threshold Charge (nC)": [1],
            "Dimension": ["Width"],
        }
    )
    fig = pa.plot.strength_duration(dim="Amp", plot_type="linear", data=df)
    assert len(fig.data) == 1


def test_plot_counts():
    sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Day": [1, 2], "Dimension": ["Amp", "Amp"]}
    )
    fig = pa.plot.counts(sessions, dim="Width")
    assert fig.layout.yaxis.title.text == "# of Sessions"


def test_plot_counts_dim_facet():
    sessions = pd.DataFrame(
        {"Monkey": ["U", "U"], "Day": [1, 2], "Dimension": ["Amp", "Width"]}
    )
    figs = pa.plot.counts(sessions, dim="Amp")
    assert len(figs.data)


def test_psychometric():
    psychometric_plot = pa.plot.psychometric(
        {"Threshold": 0, "width": 1, "gamma": 0, "lambda": 0}
    )
    assert len(psychometric_plot.data) == 1


def test_ecdf_location_no_data():
    blocks = pd.DataFrame({"location": []})
    ecdf_fig = pa.plot.ecdf(blocks, "location")
    assert ecdf_fig.layout.xaxis.title.text == "location"


def test_ecdf_width_no_data():
    blocks = pd.DataFrame({"width": []})
    ecdf_fig = pa.plot.ecdf(blocks, "width")
    assert ecdf_fig.layout.xaxis.title.text == "width"


def test_combine_line_and_scatter():
    fig1 = px.scatter(
        pd.DataFrame(
            {"Stimulus Magnitude": [0], "Hit Rate": [0.5]},
        ),
        x="Stimulus Magnitude",
        y="Hit Rate",
    )
    fig2 = px.line(
        pd.DataFrame({"Stimulus Magnitude": [0], "Hit Rate": [0.5]}),
        x="Stimulus Magnitude",
        y="Hit Rate",
    )
    fig = pa.plot.combine_figs(fig1, fig2)
    assert fig.layout.xaxis.title.text == "Stimulus Magnitude"
    assert fig.layout.yaxis.title.text == "Hit Rate"
    assert len(fig.data) == 2
