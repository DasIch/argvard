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
    tests.conftest
    ~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""
import os

import pytest


@pytest.fixture
def tests_dir():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def test_scripts_dir(tests_dir):
    return os.path.join(tests_dir, 'scripts')
