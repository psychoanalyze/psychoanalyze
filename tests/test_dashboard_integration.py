import psychoanalyze as pa


def test_integrate_data():
    n_trials_per_level = 10
    x_min = -3
    x_max = 3
    y = "p"
    curves_data = pa.curve.generate(n_trials_per_level)

    x = pa.curve.xrange_index(x_min, x_max)
    curves_data_w_posterior = pa.curve.prep_psych_curve(
        curves_data=curves_data, x=x, y=y
    )
