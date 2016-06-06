stanity
=========
python convenience functions for working with Stan models (via pystan)

Functionality:

stanity.fit
    thin wrapper around ``pystan.stan`` that caches compiled models
stanity.psisloo
    thin wrapper around ``psisloo`` (implemented [here](https://github.com/avehtari/PSIS/blob/master/py/psis.py))
stanity.loo_compare
    compare model fit using PSIS-LOO, analogous to that implemented in the R package called [loo](https://github.com/stan-dev/loo)

Installation
-------------
From a git checkout, run:

::

    pip install .

To run the tests:

::

    nosetests

