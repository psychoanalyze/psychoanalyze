import psychoanalyze as pa


def test_integrate_data(mocker):
    mocker.patch("psychoanalyze.points.fit")
    n_trials_per_level = 10
    x_min = -3
    x_max = 3
    y = "p"
    curves_data = pa.blocks.generate(n_trials_per_level)

    x = pa.blocks.xrange_index(x_min, x_max)
    assert pa.blocks.prep_psych_curve(curves_data=curves_data, x=x, y=y)
