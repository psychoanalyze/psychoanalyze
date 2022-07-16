import psychoanalyze as pa


def test_generate_sessions():
    assert pa.sessions.generate(3) == [0, 1, 2]
