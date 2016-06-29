from __future__ import absolute_import

from .fit import fit
from .psisloo import Psisloo, psisloo, loo_compare
from .utilities import print_dict

__all__ = [
    "fit",
    "psisloo",
    "Psisloo",
    "psis",
    "loo_compare",
    "print_dict",
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
