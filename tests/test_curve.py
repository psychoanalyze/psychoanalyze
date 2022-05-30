import psychoanalyze as pa


def test_generate():
    assert len(pa.curve.generate()) == 9
