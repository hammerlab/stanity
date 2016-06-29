
from .psis import psisloo as _psisloo
import pandas
import math
import numpy
import seaborn

class Psisloo(object):
    """Approximate leave-one-out cross validation of Bayesian models using PSIS-LOO

    This class stores results from approximate leave-one-out cross validation using
    Pareto-smoothed importance sampling (PSIS-LOO). Object contains pointwise 
    expected log predictive density (elpd) and pointwise pareto-k importance 
    metrics, as well as summary metrics such as WAIC. 

    Taken in concert, these metrics can be used for model comparison and model checking.

    This function is a thin wrapper around Aki Vehtari's `psisloo` function, 
    included from https://github.com/avehtari/PSIS/blob/master/py/psis.py

    - **parameters**, **types**, **return** and **return types**::

          :param log_likelihood: a matrix of log_likelihood evaluations, per observation * iter
          :type log_likelihood: matrix

          :param result: output from psis.psisloo on given log_likelihood matrix
          :type result: list of length 3 - loo (scalar), loos (ndarray), ks (ndarray)

          :param looic: summarized ELPD of the model, multiplied by -2 (on scale of deviance)
          :type looic: scalar

          :param elpd: summarized ELPD of the model on original scale
          :type elpd: scalar

          :param pointwise: DataFrame containing pointwise metrics resulting from psisloo call
          :type pointwise: DataFrame with two columns: pointwise_elpd, & pareto_k

    """
    def __init__(self, log_likelihood):
        self.log_lik = log_likelihood
        self.result = _psisloo(log_lik=self.log_lik)
        self.looic = -2*self.result[0]
        self.elpd = self.result[0]
        self.pointwise = pandas.DataFrame(
            {'pointwise_elpd' : self.result[1],
             'pareto_k': self.result[2]})
        self._summarize_pointwise()

    def _summarize_pointwise(self):
        self.summary = self.pointwise.copy()
        self.summary['greater than 0.5'] = self.summary.pareto_k > 0.5
        self.summary['greater than 1'] = self.summary.pareto_k > 1

    def print_summary(self):
        """ Numerical summary of pointwise Pareto-k indices

        Reports on frequency of observations with tail indices > 0.5 & 1

        This is a useful metric because too extreme observations may invalidate approximations.
        It is also a sign that these observations may be more extreme than expected.

        """
        return self.summary.apply(numpy.mean)[2:]

    def plot(self):
        """ Graphical summary of pointwise pareto-k importance-sampling indices

        Pareto-k tail indices are plotted (on the y axis) for each observation unit (on the x axis)

        """
        seaborn.pointplot(
            y = self.pointwise.pareto_k,
            x = self.pointwise.index,
            join = False)
        #pyplot.axhline(0.5)

def psisloo(log_likelihood):
    """
    Summarize the model fit using Pareto-smoothed importance sampling (PSIS) 
    and approximate Leave-One-Out cross-validation (LOO).
    
    Takes as input an ndarray of posterior log likelihood terms [ p( y_i | theta^s ) ]
        per observation unit.

        e.x. if using pystan:

        loosummary = stanity.psisloo(stan_fit.extract()['log_lik'])

    Returns a Psisloo object. Useful methods such as print_summary() & plot().

    References
    ----------
    
    Aki Vehtari, Andrew Gelman and Jonah Gabry (2015). Efficient implementation
    of leave-one-out cross-validation and WAIC for evaluating fitted Bayesian
    models. arXiv preprint arXiv:1507.04544.

    Aki Vehtari and Andrew Gelman (2015). Pareto smoothed importance sampling.
    arXiv preprint arXiv:1507.02646.
    """
    return Psisloo(log_likelihood)


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
    Dict with two values:

        diff: difference in elpd (estimated log predictive density) 
                between two models, where a positive value indicates
                that model2 is a better fit than model1.

        se_diff: estimated standard error of the difference
                between model2 & model1.

    """
    ## TODO: confirm that dimensions for psisloo1 & psisloo2 are the same
    loores = psisloo1.pointwise.join(
        psisloo2.pointwise,
        lsuffix = '_m1',
        rsuffix = '_m2')

    loores['pw_diff'] = loores.pointwise_elpd_m2 - loores.pointwise_elpd_m1

    sum_elpd_diff = loores.apply(numpy.sum).pw_diff
    sd_elpd_diff = loores.apply(numpy.std).pw_diff

    elpd_diff = {
        'diff' : sum_elpd_diff,
        'se_diff' : math.sqrt(len(loores.pw_diff)) * sd_elpd_diff
        }
    
    return elpd_diff

