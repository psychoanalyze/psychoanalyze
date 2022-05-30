import psychoanalyze as pa


def test_generate():
    assert len(pa.trial.generate(100)) == 100
