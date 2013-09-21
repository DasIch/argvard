# coding: utf-8
# Copyright 2013 Daniel Neuhäuser
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
    tests.test_utils
    ~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
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
