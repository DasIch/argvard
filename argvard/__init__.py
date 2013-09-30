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
from __future__ import print_function
import sys
import textwrap
from functools import partial
from collections import OrderedDict

from argvard.utils import unique
from argvard.signature import Signature
from argvard.exceptions import UnexpectedArgument, UsageError, InvalidSignature
from argvard._compat import implements_iterator, iteritems, itervalues


class ExecutableBase(object):
    def __init__(self, defaults=None):
        self.defaults = {} if defaults is None else defaults

        self.main_func = None
        self.main_signature = None
        self.options = OrderedDict()
        self.commands = OrderedDict()
        self.description = None

        self.add_help_option()

    def add_help_option(self):
        @self.option('-h|--help', overrideable=True)
        def help(context):
            """
            Show this text.
            """
            print(u'usage: %s' %
                (context.command or context.argvard).get_usage(context)
            )
            if self.description:
                print()
                print(self.description)
            if self.options:
                print()
                print(u'options:')
                for option in unique(itervalues(self.options)):
                    print(u', '.join(option.names))
                    if option.description:
                        print(
                            u''.join(
                                u' ' * 4 + line
                                for line in option.description.splitlines(True)
                            )
                        )
            if self.commands:
                print()
                print(u'commands:')
                for name, command in iteritems(self.commands):
                    print(name)
                    if command.description:
                        print(u' ' * 4 + command.description.splitlines()[0])
            sys.exit(1)

    def get_usage(self, context):
        usage = u' '.join(context.command_path)
        if self.options:
            usage += u' ' + ' '.join(
                u'[%s]' % option.usage for option in unique(itervalues(self.options))
            )
        if self.main_signature and self.main_signature.usage:
            usage += u' ' + self.main_signature.usage
        return usage

    def register_command(self, name, command):
        if name in self.commands:
            raise RuntimeError('%s is already defined' % name)
        self.commands[name] = command

    def option(self, string, overrideable=False):
        def decorator(function):
            option = Option.from_string(
                string, function, overrideable=overrideable
            )
            for name in option.names:
                if name in self.options and not self.options[name].overrideable:
                    raise RuntimeError('%s is already defined' % name)
            self.options.update((name, option) for name in option.names)
            return function
        return decorator

    def main(self, signature=''):
        signature = Signature.from_string(signature, allow_repetitions=True)
        def decorator(function):
            if self.main_func is not None:
                raise RuntimeError('main is already defined')
            self.main_func = function
            self.main_signature = signature
            if function.__doc__:
                self.description = textwrap.dedent(function.__doc__).strip()
            return function
        return decorator

    def call_options(self, context, argv):
        for argument in argv:
            if argument in self.options:
                option = self.options[argument]
                option.call(context, argv)
            else:
                argv.position -= 1
                break

    def call_commands(self, context, argv):
        try:
            argument = next(argv)
        except StopIteration:
            pass
        else:
            if argument in self.commands:
                context.command_path.append(argument)
                self.commands[argument](context, argv)
                return True
            else:
                argv.position -= 1
                return False

    def call_main(self, context, argv):
        arguments = self.main_signature.parse(argv)
        remaining = list(argv)
        if remaining:
            raise UnexpectedArgument('unexpected argument "%s"' % remaining[0])
        self.main_func(context, **arguments)

    def normalize_argv(self, argv):
        rv = []
        for i, argument in enumerate(argv):
            if argument == '--':
                rv.extend(argv[i:])
                break
            elif argument.startswith('--') and '=' in argument:
                rv.extend(argument.split('=', 1))
            elif argument.startswith('-') and not argument.startswith('--'):
                if argument[1:] and '-' + argument[1] in self.options:
                    rv.append('-' + argument[1])
                    for j, character in enumerate(argument[2:], start=2):
                        if '-' + character in self.options:
                            rv.append('-' + character)
                        else:
                            rv.append(argument[j:])
                            break
                else:
                    rv.append(argument)

            else:
                rv.append(argument)
        return rv


class Argvard(ExecutableBase):
    def create_context(self, argv):
        context = Context(self, argv[0])
        context.update(self.defaults)
        return context

    def __call__(self, argv):
        if self.main_func is None:
            raise RuntimeError('main is undefined')
        argv = Argv(self.normalize_argv(argv))
        context = self.create_context(argv)
        self.call_options(context, argv)
        try:
            if not self.call_commands(context, argv):
                self.call_main(context, argv)
        except UsageError as error:
            print(u'error: %s' % error.args[0], file=sys.stderr)
            print(u'usage: %s' % (context.command or context.argvard).get_usage(context), file=sys.stderr)
            sys.exit(1)


class Command(ExecutableBase):
    def update_context(self, context):
        context.command = self
        for key, value in iteritems(self.defaults):
            context.setdefault(key, value)

    def __call__(self, context, argv):
        if self.main_func is None:
            raise RuntimeError('main is undefined')
        self.update_context(context)
        self.call_options(context, argv)
        if not self.call_commands(context, argv):
            self.call_main(context, argv)


@implements_iterator
class Argv(object):
    def __init__(self, argv):
        self.argv = argv
        self.position = 1

    def __getitem__(self, index):
        return self.argv[index]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            argument = self.argv[self.position]
        except IndexError:
            raise StopIteration()
        self.position += 1
        return argument


class Option(object):
    @classmethod
    def from_string(cls, string, function, overrideable=False):
        parts = string.split(' ', 1)
        if not parts or not parts[0]:
            raise InvalidSignature('option name missing')
        names = parts[0]
        if u'|' in names:
            names = names.split(u'|')
        else:
            names = [names]
        for name in names:
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
        if parts[1:]:
            signature = Signature.from_string(parts[1])
        else:
            signature = Signature([])
        return cls(names, function, signature, overrideable=overrideable)

    def __init__(self, names, function, signature, overrideable=False):
        self.names = names
        self.function = function
        if self.function.__doc__ is None:
            self.description = None
        else:
            self.description = textwrap.dedent(self.function.__doc__.strip())
        self.signature = signature
        self.overrideable = overrideable

    @property
    def usage(self):
        usage = u'|'.join(self.names)
        if self.signature.usage:
            usage += u' ' + self.signature.usage
        return usage

    def call(self, context, argv):
        self.signature.call_with_arguments(
            partial(self.function, context), argv
        )


class Context(dict):
    def __init__(self, argvard, application_name):
        self.argvard = argvard
        self.command_path = [application_name]

        self.command = None
