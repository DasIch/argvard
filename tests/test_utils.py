# coding: utf-8
"""
    tests.test_utils
    ~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
"""
from itertools import repeat

import pytest

from argvard.utils import is_python_identifier
from argvard._compat import PY2


@pytest.mark.parametrize(('possible_identifier', 'result'),
    list(zip([
        'a',
        'abc',
        'A',
        'ABC',
        '_',
        '_abc',
        '_ABC',
        'a1'
    ] + [] if PY2 else [
        '\xe4',
        '\u03bc',
        '\u887d2',
        'x\U000E0100'
    ], repeat(True))) +
    list(zip([
        'abc.def',
        '123',
        '€',
        ''
    ], repeat(False)))
)
def test_is_python_identifier(possible_identifier, result):
    assert is_python_identifier(possible_identifier) == result
