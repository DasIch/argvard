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
    argvard.signature
    ~~~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""
import re

from argvard.exceptions import InvalidSignature, ArgumentMissing


_TOKENS = [
    ('identifier',  r'[a-zA-Z_][a-zA-Z_0-9]*'),
    ('repetition', r'\.\.\.'),
    ('[', r'\['),
    (']', r'\]'),
    ('space', r' +')
]
_OPTION_TOKENS = [
    (name, regex) for name, regex in _TOKENS
    if name not in ['repetition', '[', ']']
]


def _build_tokenizer(tokens):
    regex = re.compile('|'.join('(%s)' % regex for name, regex in tokens))
    def _tokenize(string):
        position = 0
        while position < len(string):
            match = regex.match(string, position)
            if match:
                position = match.end()
                yield tokens[match.lastindex - 1][0], match.group()
            else:
                raise InvalidSignature(string, position)
    return _tokenize


_tokenize = _build_tokenizer(_TOKENS)
_option_tokenize = _build_tokenizer(_OPTION_TOKENS)


def _parse_signature(signature, option=True):
    if option:
        tokens = _option_tokenize(signature)
    else:
        tokens = _tokenize(signature)
    state = 0, list(tokens)
    patterns = []
    _parse_words(state, patterns)
#    assert state[0] == len(state[1])
    return patterns


def _parse_words(state, patterns):
    position, tokens = state
    while position < len(tokens):
        position, tokens = _parse_word((position, tokens), patterns)
        if position < len(tokens):
            assert tokens[position][0] == 'space'
        position += 1
    return position, tokens


def _parse_word(state, patterns):
    return _either(state, patterns, [_parse_repetition, _parse_argument])


def _parse_repetition(state, patterns):
    position, tokens = state
    if position + 1 >= len(tokens):
        raise InvalidSignature()
    if tokens[position + 1][0] != 'repetition':
        raise InvalidSignature()
    if tokens[position][0] != 'identifier':
        raise InvalidSignature()
    patterns.append(Repetition(Argument(tokens[position][1])))
    return position + 2, tokens


def _parse_argument(state, patterns):
    position, tokens = state
    type, lexeme = tokens[position]
    if type == 'identifier':
        patterns.append(Argument(lexeme))
        return position + 1, tokens
    raise InvalidSignature()


def _either(state, patterns, parsers):
    for parser in parsers:
        transaction = []
        try:
            state = parser(state, transaction)
            patterns.extend(transaction)
            return state
        except InvalidSignature:
            pass
    raise


class Signature(object):
    @classmethod
    def from_string(cls, string, option=True):
        return cls(_parse_signature(string, option=option))

    def __init__(self, patterns):
        self.patterns = patterns

    @property
    def usage(self):
        return u' '.join(u'<%s>' % pattern.usage for pattern in self.patterns)

    def parse(self, argv):
        rv = {}
        for pattern in self.patterns:
            pattern.apply(rv, argv)
        return rv

    def call_with_arguments(self, callable, argv):
        return callable(**self.parse(argv))


class Argument(object):
    def __init__(self, name):
        self.name = name

    @property
    def usage(self):
        return self.name

    def apply(self, result, argv):
        try:
            result[self.name] = next(argv)
        except StopIteration:
            raise ArgumentMissing('%s is missing' % self.usage)


class Repetition(object):
    def __init__(self, pattern):
        self.pattern = pattern

    @property
    def usage(self):
        return self.pattern.usage + u'...'

    def apply(self, result, argv):
        remaining = list(argv)
        if remaining:
            self.pattern.apply(result, iter([remaining]))
        else:
            raise ArgumentMissing('%s is missing' % self.usage)
