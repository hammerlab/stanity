import time

import pystan

FIT_CACHE = {}
def fit(model_code, *args, **kwargs):
    """
    Fit a Stan model. Caches the compiled model.

    *args and **kwargs are passed to the pystan.stan function.

    Arguments you most likely want to pass: data, init, iter, chains.        

    Unlike pystan.stan, if the n_jobs kwarg is not specified, it defaults to
    -1.

    Parameters
    -------------------
    model_code : string
        Stan model


    Returns
    -------------------
    pystan StanFit4Model instance : the fit model
    """
    kwargs = dict(kwargs)
    kwargs['model_code'] = model_code
    if 'n_jobs' not in kwargs:
        kwargs['n_jobs'] = -1
    if model_code in FIT_CACHE:
        print("Reusing model.")
        kwargs['fit'] = FIT_CACHE[model_code]
    else:
        print("NOT reusing model.")
    start = time.time()
    FIT_CACHE[model_code] = pystan.stan(*args, **kwargs)
    print("Ran in %0.3f sec." % (time.time() - start))
    return FIT_CACHE[model_code]

