from nose.tools import eq_
import numpy

import stanity

def test_psisloo():
    # Test psisloo calculation using a toy linear regression.

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
        generated quantities {
            real y_rep[num_points];
            real log_lik[num_points];
            
            for (i in 1:num_points) {
                y_rep[i] <- normal_rng(a * x[i] + b, 2);
                log_lik[i] <- normal_log(y[i], a * x[i] + b, 2);
            }
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
    
    loo = stanity.psisloo(extracted['log_lik'])
    loo_summ = loo.summary.apply(numpy.mean)[2:]
    
    numpy.testing.assert_almost_equal(loo_summ['greater than 0.5'], 0, decimal=3)
    numpy.testing.assert_almost_equal(loo_summ['greater than 1'], 0, decimal=3)

def test_loo_compare():
    # Test loo_compare using a toy linear regression.

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
        generated quantities {
            real y_rep[num_points];
            real log_lik[num_points];
            
            for (i in 1:num_points) {
                y_rep[i] <- normal_rng(a * x[i] + b, 2);
                log_lik[i] <- normal_log(y[i], a * x[i] + b, 2);
            }
        }
    """
    noise = numpy.random.normal(scale=0.1, size=num_points)
    x = numpy.random.uniform(-10, 10, size=num_points)
    
    ## first fit (correct fit)
    data1 = {
        'num_points': num_points,
        'x': x,
        'y': true_a * x + true_b + noise,
    }
    fit1 = stanity.fit(model_code, data=data1, iter=10000, chains=2)
    ext1 = fit1.extract()
    loo1 = stanity.psisloo(ext1['log_lik'])
    
    ## second fit (should be worse)
    data2 = {
        'num_points': num_points,
        'x': numpy.exp(x),
        'y': true_a * x + true_b + noise,
    }
    fit2 = stanity.fit(model_code, data=data2, iter=10000, chains=2)
    ext2 = fit2.extract()
    loo2 = stanity.psisloo(ext2['log_lik'])

    ## compare loo1 & loo2
    comparison = stanity.loo_compare(loo1, loo2)
    
    assert comparison['diff'] < 0
    assert comparison['diff'] < -1000

