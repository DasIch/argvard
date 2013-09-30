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
from argvard.utils import is_python_identifier
from argvard.exceptions import InvalidSignature, ArgumentMissing


class Signature(object):
    @classmethod
    def from_string(cls, string, allow_repetitions=False):
        def parse_word(word):
            if word.endswith('...') and is_python_identifier(word[:-3]):
                if allow_repetitions:
                    return Repetition(Argument(word[:-3]))
                raise InvalidSignature('repetitions are not allowed: %s' % word)
            elif is_python_identifier(word):
                return Argument(word)
            raise InvalidSignature('not a valid python identifier: %r' % word)
        patterns = []
        for word in string.split(' ') if string else []:
            patterns.append(parse_word(word))
        return cls(patterns)

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
