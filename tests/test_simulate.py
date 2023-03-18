from psychoanalyze import simulate


def test_simulation():
    sim = simulate.run(0)
    assert len(sim) == 0
