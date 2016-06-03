from nose.tools import eq_
import numpy

import stanity

def test_fit():
    # Test a toy linear regression.

    true_a = 52.3
    true_b = -30
    num_points = 100

    model_code = """
        data {
            int<lower=0> num_points;
            vector[num_points] x;
            vector[num_points] y;
        }
        parameters {
            real a;
            real b;
        }
        model {
            y ~ normal(a * x + b, 2);
            a ~ normal(0, 100);
            b ~ normal(0, 100);
        }
    """
    noise = numpy.random.normal(scale=0.1, size=num_points)
    x = numpy.random.uniform(-1000, 1000, size=num_points)
    data = {
        'num_points': num_points,
        'x': x,
        'y': true_a * x + true_b + noise,
    }
    fit = stanity.fit(model_code, data=data, iter=10000, chains=2)
    extracted = fit.extract()
    numpy.testing.assert_almost_equal(extracted['a'].mean(), true_a, decimal=1)
    numpy.testing.assert_almost_equal(extracted['b'].mean(), true_b, decimal=1)

