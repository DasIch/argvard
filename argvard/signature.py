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
    ('identifier', r'[a-zA-Z_][a-zA-Z_0-9]*'),
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
    state = _parse_words(state, patterns)
    assert state[0] == len(state[1])
    return patterns


def _parse_words(state, patterns):
    position, tokens = state
    while position < len(tokens):
        if tokens[position][0] == ']':
            break
        position, tokens = _parse_word((position, tokens), patterns)
        if position < len(tokens) and tokens[position][0] == ']':
            break
    return position, tokens


def _parse_word(state, patterns):
    position, tokens = _either(state, patterns, [
        _parse_optional, _parse_repetition, _parse_argument
    ])
    if position < len(tokens):
        if tokens[position][0] == 'space':
            position += 1
        elif tokens[position][0] != ']':
            raise InvalidSignature()
    return position, tokens


def _parse_optional(state, patterns):
    position, tokens = state
    if tokens[position][0] != '[':
        raise InvalidSignature('expected [, got %r' % (tokens[position], ))
    position += 1
    rv = []
    position, tokens = _parse_word((position, tokens), rv)
    position, tokens = _parse_words((position, tokens), rv)
    if tokens[position][0] != ']':
        raise InvalidSignature('expected ], got %r' % (tokens[position], ))
    position += 1
    patterns.append(Optional(rv))
    return position, tokens


def _parse_repetition(state, patterns):
    position, tokens = state
    if position + 1 >= len(tokens):
        raise InvalidSignature('expected at least one more token')
    if tokens[position + 1][0] != 'repetition':
        raise InvalidSignature(
            'expected repetition as next token, got %r' % (tokens[position + 1], )
        )
    if tokens[position][0] != 'identifier':
        raise InvalidSignature(
            'expected identifier, got %r' % (tokens[position], )
        )
    patterns.append(Repetition(Argument(tokens[position][1])))
    return position + 2, tokens


def _parse_argument(state, patterns):
    position, tokens = state
    type, lexeme = tokens[position]
    if type == 'identifier':
        patterns.append(Argument(lexeme))
        return position + 1, tokens
    raise InvalidSignature('expected identifier, got: %r' % ((type, lexeme), ))


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
    """
    Represents a signature using patterns.
    """
    @classmethod
    def from_string(cls, string, option=True):
        """
        Returns a :class:`Signature` object based on the given `string`. If
        `option` is `True`, repetitions or optional patterns will not be
        allowed.

        If the `string` cannot be parsed, :exc:`InvalidSignature` is raised.
        """
        return cls(_parse_signature(string, option=option))

    def __init__(self, patterns):
        self.patterns = patterns

    @property
    def usage(self):
        """
        A usage string that describes the signature.
        """
        return u' '.join(u'<%s>' % pattern.usage for pattern in self.patterns)

    def parse(self, argv):
        """
        Parses the given `argv` and returns a dictionary mapping argument names
        to the values found in `argv`.
        """
        rv = {}
        for pattern in self.patterns:
            pattern.apply(rv, argv)
        return rv

    def call_with_arguments(self, callable, argv):
        """
        Parses `argv` and calls `callable` with the result.
        """
        return callable(**self.parse(argv))


class Argument(object):
    """
    Represents a positional argument with the given `name`.
    """
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
    """
    Represents one or more occurences of the given `pattern`.
    """
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


class Optional(object):
    """
    Represents an optional occurence of the given `patterns`.
    """
    def __init__(self, patterns):
        self.patterns = patterns

    @property
    def usage(self):
        return u'[%s]' % u' '.join(pattern.usage for pattern in self.patterns)

    def apply(self, result, argv):
        transaction = {}
        position = argv.position
        try:
            for pattern in self.patterns:
                pattern.apply(transaction, argv)
        except ArgumentMissing:
            argv.position = position
        else:
            result.update(transaction)
