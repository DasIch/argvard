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
    argvard
    ~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""
from argvard.utils import is_python_identifier
from argvard._compat import implements_iterator


class Argvard(object):
    def __init__(self):
        self.main_func = None
        self.main_signature = None
        self.options = {}

    def option(self, signature):
        parts = signature.split(' ', 1)
        if not parts or not parts[0]:
            raise InvalidSignature('option name missing')
        name = parts[0]
        if name.startswith('--'):
            if len(name) == 2:
                raise InvalidSignature(
                    'option with long prefix is missing a name'
                )
        elif name.startswith('-'):
            if len(name) == 1:
                raise InvalidSignature(
                    'option with short prefix is missing a name'
                )
            elif len(name) > 2:
                raise InvalidSignature(
                    'short option with name longer than one character: %s' % name
                )
        if name in self.options:
            raise RuntimeError('%s is already defined' % name)
        if parts[1:]:
            signature = Signature.from_string(parts[1])
        else:
            signature = Signature([])
        def decorator(function):
            self.options[name] = signature, function
            return function
        return decorator

    def main(self, signature=''):
        signature = Signature.from_string(signature)
        def decorator(function):
            if self.main_func is not None:
                raise RuntimeError('main is already defined')
            self.main_func = function
            self.main_signature = signature
            return function
        return decorator

    def call_options(self, argv):
        for argument in argv:
            if argument in self.options:
                signature, function = self.options[argument]
                signature.call_with_arguments(function, argv)
            else:
                argv.position -= 1
                break

    def call_main(self, argv):
        self.main_signature.call_with_arguments(self.main_func, argv)

    def __call__(self, argv):
        if self.main_func is None:
            raise RuntimeError('main is undefined')
        argv = Argv(argv)
        self.call_options(argv)
        self.call_main(argv)


@implements_iterator
class Argv(object):
    def __init__(self, argv):
        self.argv = argv
        self.position = 1

    def __iter__(self):
        return self

    def __next__(self):
        try:
            argument = self.argv[self.position]
        except IndexError:
            raise StopIteration()
        self.position += 1
        return argument


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

    def parse(self, argv):
        rv = {}
        argv = iter(argv)
        for name in self.arguments:
            try:
                rv[name] = next(argv)
            except StopIteration:
                raise ArgumentMissing('%s is missing' % name)
        return rv

    def call_with_arguments(self, callable, argv):
        return callable(**self.parse(argv))


class InvalidSignature(Exception):
    pass


class ArgumentMissing(Exception):
    pass
