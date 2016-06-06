
import psis
import pandas
import math
import numpy
import seaborn
import matplotlib as pyplot

class Psisloo(object):
    def __init__(self, log_lik):
        self.log_lik = log_lik
        self.result = psis.psisloo(log_lik=log_lik)
        self.looic = -2*self.result[0]
        self.looic = self.result[0]
        self.pointwise = pandas.DataFrame({'pointwise_elpd' : self.result[1], 'pareto_k': self.result[2]})
        self._summarize_pointwise()

    def _summarize_pointwise(self):
        self.summary = self.pointwise.copy()
        self.summary['greater than 0.5'] = self.summary.pareto_k > 0.5
        self.summary['greater than 1'] = self.summary.pareto_k > 1

    def print_summary(self):
        return self.summary.apply(numpy.mean)[2:]

    def plot(self):
        seaborn.pointplot(y = self.pointwise.pareto_k, x = self.pointwise.index, join = False)
        #pyplot.axhline(0.5)

def psisloo(log_lik, *args, **kwargs):
    """
    Summarize the model fit using Pareto-smoothed importance sampling (PSIS) 
    and approximate Leave-One-Out cross-validation (LOO).
    
    Takes as input a matrix of log_likelihood evaluations, per observation * iter:
        e.x.
        loosummary = loo(stan_fit.extract()['log_lik'])

    Returns a Psisloo object 

    References
    ----------
    
    Aki Vehtari, Andrew Gelman and Jonah Gabry (2015). Efficient implementation
    of leave-one-out cross-validation and WAIC for evaluating fitted Bayesian
    models. arXiv preprint arXiv:1507.04544.

    Aki Vehtari and Andrew Gelman (2015). Pareto smoothed importance sampling.
    arXiv preprint arXiv:1507.02646.
    """
    return Psisloo(log_lik)


def loo_compare(psisloo1, psisloo2):
    """
    Compares two models using pointwise approximate leave-one-out cross validation.
    
    For the method to be valid, the two models should have been fit on the same input data. 

    Parameters
    -------------------
    psisloo1 : Psisloo object for model1
    psisloo2 : Psisloo object for model2

    Returns
    -------------------
    Dict summarizing difference between two models, where a positive value indicates
        that model2 is a better fit than model1.

    """
    ## TODO: confirm that dimensions for psisloo1 & psisloo2 are the same
    loores = psisloo1.pointwise.join(psisloo2.pointwise, lsuffix = '_m1', rsuffix = '_m2')
    loores['pw_diff'] = loores.pointwise_elpd_m2 - loores.pointwise_elpd_m1
    sum_elpd_diff = loores.apply(numpy.sum).pw_diff
    sd_elpd_diff = loores.apply(numpy.std).pw_diff
    elpd_diff = {'diff' : sum_elpd_diff, 'se_diff' : math.sqrt(len(loores.pw_diff)) * sd_elpd_diff}
    return elpd_diff

