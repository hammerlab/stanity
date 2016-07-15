.. image:: https://travis-ci.org/hammerlab/stanity.svg?branch=setup-travis
   :height: 100px
   :width: 200 px
   :scale: 50 %
   :alt: build status
   :align: right
   :target: https://travis-ci.org/hammerlab/stanity


stanity
=========
python convenience functions for working with Stan models (via pystan)

Functionality:

stanity.fit
    thin wrapper around ``pystan.stan`` that caches compiled models
stanity.psisloo
    thin wrapper around ``psisloo`` (implemented in https://github.com/avehtari/PSIS/blob/master/py/psis.py)
stanity.loo_compare
    compare model fit using PSIS-LOO, similar to methods implemented in the R package loo

Installation
-------------
From a git checkout, run:

::

    pip install .

To run the tests:

::

    nosetests

