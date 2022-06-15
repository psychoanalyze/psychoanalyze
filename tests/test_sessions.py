import psychoanalyze as pa


def test_generate_sessions():
    assert pa.session.generate(3) == [0, 1, 2]
