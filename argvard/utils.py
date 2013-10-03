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
    argvard.utils
    ~~~~~~~~~~~~~

    :copyright: 2013
    :license: Apache License 2.0, see LICENSE for more details
"""
import re
import unicodedata
from keyword import iskeyword

from argvard._compat import PY2


_python2_identifier_re = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*$')


def is_python_identifier(possible_identifier):
    """
    Returns `True` if the given `possible_identifier` can be used as an
    identifier in the Python version used by the executing interpreter.
    """
    if PY2:
        return is_python2_identifier(possible_identifier)
    else:
        return is_python3_identifier(possible_identifier)


def is_python2_identifier(possible_identifier):
    """
    Returns `True` if the given `possible_identifier` can be used as an
    identifier in Python 2.
    """
    match = _python2_identifier_re.match(possible_identifier)
    return bool(match) and not iskeyword(possible_identifier)


def is_python3_identifier(possible_identifier):
    """
    Returns `True` if the given `possible_identifier` can be used as an
    identifier in Python 3.
    """
    possible_identifier = unicodedata.normalize('NFKC', possible_identifier)
    return (
        bool(possible_identifier) and
        _is_in_id_start(possible_identifier[0]) and
        all(map(_is_in_id_continue, possible_identifier[1:]))
    ) and not iskeyword(possible_identifier)


def _is_in_id_start(character):
    category = unicodedata.category(character)
    return category in set([
        'Lu', # uppercase letters
        'Ll', # lowercase letters
        'Lt', # titlecase letters
        'Lm', # modifier letters
        'Lo', # other letters
        'NI', # letter numbers
    ]) or character == u'_'


def _is_in_id_continue(character):
    category = unicodedata.category(character)
    return _is_in_id_start(character) or category in set([
        'Mn', # nonspacing marks
        'Mc', # spacing combining marks
        'Nd', # decimal numbers
        'Pc' # connector punctuations
    ]) or character == u'\u00B7'


def unique(iterable):
    """
    Returns an iterator that yields the first occurence of a hashable item in
    `iterable`.
    """
    seen = set()
    for obj in iterable:
        if obj not in seen:
            yield obj
            seen.add(obj)
