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
    def from_string(cls, string):
        arguments = []
        for name in string.split(' ') if string else []:
            if not is_python_identifier(name):
                raise InvalidSignature(
                    'not a valid python identifier: %r' % name
                )
            arguments.append(name)
        return cls(arguments)

    def __init__(self, arguments):
        self.arguments = arguments

    @property
    def usage(self):
        return u' '.join(u'<%s>' % name for name in self.arguments)

    def parse(self, argv):
        rv = {}
        for name in self.arguments:
            try:
                rv[name] = next(argv)
            except StopIteration:
                raise ArgumentMissing('%s is missing' % name)
        return rv

    def call_with_arguments(self, callable, argv):
        return callable(**self.parse(argv))
