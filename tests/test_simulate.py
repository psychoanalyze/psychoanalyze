import pandas as pd
from psychoanalyze import simulate


def test_simulation():
    sim = simulate.run(0)
    assert len(sim) == 0


def test_hit_rate():
    trial_counts = pd.Series(
        [1],
        index=pd.Index(["Miss"], name="Outcome"),
        name="count",
    )
    assert simulate.hit_rate(trial_counts) == 0


def test_psi():
    psi_observed = pd.Series(
        [0.0], name="Hit Rate", index=pd.Index([0.0], name="Intensity")
    )
    psi_model = pd.Series(
        [],
        name="Hit Rate",
        index=pd.Index([], name="Intensity", dtype=float),
        dtype=float,
    )
    psi = simulate.psi(psi_observed, psi_model)
    pd.testing.assert_frame_equal(
        psi,
        pd.DataFrame({"Source": ["Observed"], "Intensity": [0.0], "Hit Rate": [0.0]}),
    )


def test_hit_rates():
    trials = pd.DataFrame({"Intensity": [1.0], "Outcome": [1]})
    pd.testing.assert_frame_equal(
        simulate.hit_rates(trials),
        pd.DataFrame({"Intensity": [1.0], "Hits": [1], "n": [1], "Hit Rate": [1.0]}),
    )
