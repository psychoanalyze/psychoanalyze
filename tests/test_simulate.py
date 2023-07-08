"""Test simulation functions in psychoanalyze.simulate."""
import pandas as pd

from psychoanalyze.data import simulate


def test_simulation() -> None:
    """Test simulation of an empty dataset."""
    sim = simulate.run(0)
    assert len(sim) == 0


def test_psi() -> None:
    """Test labeling of data from model + observed inputs."""
    psi_observed = pd.Series(
        [0.0],
        name="Hit Rate",
        index=pd.Index([0.0], name="Intensity"),
    )
    psi_model = pd.Series(
        [],
        name="Hit Rate",
        index=pd.Index([], name="Intensity", dtype=float),
        dtype=float,
    )
    psi_simulated = pd.Series(
        [],
        name="Hit Rate",
        index=pd.Index([], name="Intensity", dtype=float),
        dtype=float,
    )
    psi = simulate.psi(psi_observed, psi_model, psi_simulated)
    pd.testing.assert_frame_equal(
        psi,
        pd.DataFrame({"Source": ["Observed"], "Intensity": [0.0], "Hit Rate": [0.0]}),
    )
