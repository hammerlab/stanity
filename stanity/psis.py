"""Pareto smoothed importance sampling (PSIS)

This module implements Pareto smoothed importance sampling (PSIS) and PSIS
leave-one-out cross-validation for Python (Numpy).

Included functions
------------------
psisloo
    Pareto smoothed importance sampling leave-one-out log predictive densities.

psislw
    Pareto smoothed importance sampling.

gpdfitnew
    Estimate the paramaters for the Generalized Pareto Distribution (GPD).

gpinv
    Inverse Generalised Pareto distribution function.

sumlogs
    Sum of vector where numbers are represented by their logarithms.

References
----------
Aki Vehtari, Andrew Gelman and Jonah Gabry (2015). Efficient implementation
of leave-one-out cross-validation and WAIC for evaluating fitted Bayesian
models. arXiv preprint arXiv:1507.04544.

Aki Vehtari and Andrew Gelman (2015). Pareto smoothed importance sampling.
arXiv preprint arXiv:1507.02646.

"""

# Copyright (c) 2015 Aki Vehtari, Tuomas Sivula
# Original Matlab version by Aki Vehtari. Translation to Python
# by Tuomas Sivula.

# This software is distributed under the GNU General Public
# License (version 3 or later); please refer to the file
# License.txt, included with the software, for details.

from __future__ import division # For Python 2 compatibility
import numpy as np


def psisloo(log_lik, **kwargs):
    """PSIS leave-one-out log predictive densities.
    
    Computes the log predictive densities given posterior samples of the log 
    likelihood terms p(y_i|\theta^s) in input parameter `log_lik`. Returns a 
    sum of the leave-one-out log predictive densities `loo`, individual 
    leave-one-out log predictive density terms `loos` and an estimate of Pareto 
    tail indeces `ks`. If tail index k>0.5, variance of the raw estimate does 
    not exist and if tail index k>1 the mean of the raw estimate does not exist 
    and the PSIS estimate is likely to have large variation and some bias.
    
    Parameters
    ----------
    log_lik : ndarray
        Array of size n x m containing n posterior samples of the log likelihood
        terms p(y_i|\theta^s).
    
    Additional keyword arguments are passed to the psislw() function (see the
    corresponding documentation).
    
    Returns
    -------
    loo : scalar
        sum of the leave-one-out log predictive densities
    
    loos : ndarray
        individual leave-one-out log predictive density terms
    
    ks : ndarray
        estimated Pareto tail indeces
    
    """
    # ensure overwrite flag in passed arguments
    kwargs['overwrite_lw'] = True
    # log raw weights from log_lik
    lw = -log_lik
    # compute Pareto smoothed log weights given raw log weights
    lw, ks = psislw(lw, **kwargs)
    # compute
    lw += log_lik
    loos = sumlogs(lw, axis=0)
    loo = loos.sum()
    return loo, loos, ks


def psislw(lw, wcpp=20, wtrunc=3/4, overwrite_lw=False):
    """Pareto smoothed importance sampling (PSIS).
    
    Parameters
    ----------
    lw : ndarray
        Array of size n x m containing m sets of n log weights. It is also
        possible to provide one dimensional array of length n.
    
    wcpp : number
        Percentage of samples used for GPD fit estimate (default is 20).
    
    wtrunc : float
        Positive parameter for truncating very large weights to n^wtrunc.
        Providing False or 0 disables truncation. Default values is 3/4.
    
    overwrite_lw : bool, optional
        If True, the input array `lw` is smoothed in-place. By default, a new
        array is allocated.
    
    Returns
    -------
    lw_out : ndarray
        smoothed log weights
    kss : ndarray
        Pareto tail indices
    
    """
    if lw.ndim == 2:
        n, m = lw.shape
    elif lw.ndim == 1:
        n = len(lw)
        m = 1
    else:
        raise ValueError("Argument `lw` must be 1 or 2 dimensional.")
    if n <= 1:
        raise ValueError("More than one log-weight needed.")
    
    if overwrite_lw:
        # in-place operation
        lw_out = lw
    else:
        # allocate new array for output
        lw_out = np.copy(lw, order='K')
    
    # allocate output array for kss
    kss = np.empty(m)
    
    # precalculate constants
    cutoffmin = np.log(np.finfo(float).tiny)
    logn = np.log(n)
    
    # loop over sets of log weights
    for i, x in enumerate(lw_out.T if lw_out.ndim == 2 else lw_out[None,:]):
        # improve numerical accuracy
        x -= np.max(x)
        # divide log weights into body and right tail
        xcutoff = max(
            np.percentile(x, 100 - wcpp),
            cutoffmin
        )
        expxcutoff = np.exp(xcutoff)
        tailinds, = np.where(x > xcutoff)
        x2 = x[tailinds]
        n2 = len(x2)
        if n2 <= 4:
            # not enough tail samples for gpdfitnew
            k = np.inf
        else:
            # order of tail samples
            x2si = np.argsort(x2)
            # fit generalized Pareto distribution to the right tail samples
            np.exp(x2, out=x2)
            x2 -= expxcutoff
            k, sigma = gpdfitnew(x2, sort=x2si)
            # compute ordered statistic for the fit
            sti = np.arange(0.5, n2)
            sti /= n2
            qq = gpinv(sti, k, sigma)
            qq += expxcutoff
            np.log(qq, out=qq)
            # place the smoothed tail into the output array
            x[tailinds[x2si]] = qq
        if wtrunc > 0:
            # truncate too large weights
            lwtrunc = wtrunc * logn - logn + sumlogs(x)
            x[x > lwtrunc] = lwtrunc
        # renormalize weights
        x -= sumlogs(x)
        # store tail index k
        kss[i] = k
    
    # If the provided input array is one dimensional, return kss as scalar.
    if lw_out.ndim == 1:
        kss = kss[0]
    
    return lw_out, kss


def gpdfitnew(x, sort=True):
    """Estimate the paramaters for the Generalized Pareto Distribution (GPD)
    
    Returns empirical Bayes estimate for the parameters of the two-parameter
    generalized Parato distribution given the data.
    
    Parameters
    ----------
    x : ndarray
        One dimensional data array
    
    sort : {bool, ndarray, 'in-place'}, optional
        If known in advance, one can provide an array of indices that would
        sort the input array `x`. If the input array is already sorted, provide
        False. If the array is not sorted but can be sorted in-place, provide
        string 'in-place'. If True (default behaviour) the sorted array indices
        are determined internally.
    
    Returns
    -------
    k, sigma : float
        estimated parameter values
    
    Notes
    -----
    This function returns a negative of Zhang and Stephens's k, because it is
    more common parameterisation.
    
    """
    if x.ndim != 1 or len(x) <= 1:
        raise ValueError("Invalid input array.")
    
    # check if x should be sorted
    if sort is True:
        sort = np.argsort(x)
        xsorted = False
    elif sort is False:
        xsorted = True
    elif sort == 'in-place':
        x.sort()
        xsorted = True
    else:
        xsorted = False
    
    n = len(x)
    m = 80 + int(np.floor(np.sqrt(n)))
    
    bs = np.arange(1, m + 1, dtype=float)
    bs -= 0.5
    np.divide(m, bs, out=bs)
    np.sqrt(bs, out=bs)
    np.subtract(1, bs, out=bs)
    if xsorted:
        bs /= 3 * x[np.floor(n/4 + 0.5) - 1]
        bs += 1 / x[-1]
    else:
        bs /= 3 * x[sort[np.floor(n/4 + 0.5) - 1]]
        bs += 1 / x[sort[-1]]
    
    ks = np.negative(bs)
    temp = ks[:,None] * x
    np.log1p(temp, out=temp)
    np.mean(temp, axis=1, out=ks)
    
    L = bs / ks
    np.negative(L, out=L)
    np.log(L, out=L)
    L -= ks
    L -= 1
    L *= n
    
    temp = L - L[:,None]
    np.exp(temp, out=temp)
    w = np.sum(temp, axis=1)
    np.divide(1, w, out=w)
    
    # remove negligible weights
    dii = w >= 10 * np.finfo(float).eps
    if not np.all(dii):
        w = w[dii]
        bs = bs[dii]
    # normalise w
    w /= w.sum()
    
    # posterior mean for b
    b = np.sum(bs * w)
    # Estimate for k, note that we return a negative of Zhang and
    # Stephens's k, because it is more common parameterisation.
    temp = (-b) * x
    np.log1p(temp, out=temp)
    k = np.mean(temp)
    # estimate for sigma
    sigma = -k / b
    
    return k, sigma


def gpinv(p, k, sigma):
    """Inverse Generalised Pareto distribution function."""
    x = np.empty(p.shape)
    x.fill(np.nan)
    if sigma <= 0:
        return x
    ok = (p > 0) & (p < 1)
    if np.all(ok):
        if np.abs(k) < np.finfo(float).eps:
            np.negative(p, out=x)
            np.log1p(x, out=x)
            np.negative(x, out=x)
        else:
            np.negative(p, out=x)
            np.log1p(x, out=x)
            x *= -k
            np.expm1(x, out=x)
            x /= k
        x *= sigma
    else:
        if np.abs(k) < np.finfo(float).eps:
            # x[ok] = - np.log1p(-p[ok])
            temp = p[ok]
            np.negative(temp, out=temp)
            np.log1p(temp, out=temp)
            np.negative(temp, out=temp)
            x[ok] = temp
        else:
            # x[ok] = np.expm1(-k * np.log1p(-p[ok])) / k
            temp = p[ok]
            np.negative(temp, out=temp)
            np.log1p(temp, out=temp)
            temp *= -k
            np.expm1(temp, out=temp)
            temp /= k
            x[ok] = temp
        x *= sigma
        x[p == 0] = 0
        if k >= 0:
            x[p == 1] = np.inf
        else:
            x[p == 1] = -sigma / k
    return x


def sumlogs(x, axis=None, out=None):
    """Sum of vector where numbers are represented by their logarithms.
    
    Calculates np.log(np.sum(np.exp(x), axis=axis)) in such a fashion that it
    works even when elements have large magnitude.
    
    """
    maxx = x.max(axis=axis, keepdims=True)
    xnorm = x - maxx
    np.exp(xnorm, out=xnorm)
    out = np.sum(xnorm, axis=axis, out=out)
    if isinstance(out, np.ndarray):
        np.log(out, out=out)
    else:
        out = np.log(out)
    out += np.squeeze(maxx)
    return out

