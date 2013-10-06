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
    tests.test_init
    ~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""
import os
import subprocess

import pytest

from argvard import Argvard, Command
from argvard.exceptions import InvalidSignature, ArgumentMissing


class TestArgvard(object):
    def test_get_usage(self):
        argvard = Argvard()

        @argvard.main()
        def main(context):
            assert (
                context.argvard.get_usage(context) ==
                u'application [-h|--help]'
            )
        argvard(['application'])

        argvard = Argvard()

        @argvard.option('--foo')
        def option(context):
            pass

        @argvard.main()
        def main2(context):
            assert (
                context.argvard.get_usage(context) ==
                u'application [-h|--help] [--foo]'
            )
        argvard(['application'])

        argvard = Argvard()

        @argvard.main('foo bar')
        def main3(context, foo, bar):
            assert (
                context.argvard.get_usage(context) ==
                u'application [-h|--help] <foo> <bar>'
            )

        argvard(['application', 'foo', 'bar'])

    def test_register_command(self):
        called = []
        argvard = Argvard()

        @argvard.main()
        def foo(context):
            called.append('application')
        command = Command()

        @command.main()
        def bar(context):
            called.append('command')
        argvard.register_command('command', command)
        argvard(['application'])
        assert called == ['application']
        del called[:]
        argvard(['application', 'command'])
        assert called == ['command']

    def test_command_ordering(self):
        argvard = Argvard()
        command = Command()
        argvard.register_command('foo', command)
        argvard.register_command('bar', command)
        assert list(argvard.commands.keys()) == ['foo', 'bar']

    def test_command_get_usage(self):
        argvard = Argvard()
        argvard.main()(lambda context: None)
        command = Command()

        @command.main()
        def main(context):
            assert (
                context.argvard.get_usage(context) ==
                'application command [-h|--help]'
            )
        argvard.register_command('command', command)
        argvard(['application', 'command'])

        argvard = Argvard()
        argvard.main()(lambda context: None)
        command = Command()

        @command.option('--foo')
        def option(context):
            pass

        @command.main()
        def main2(context):
            assert (
                context.command.get_usage(context) ==
                'application command [-h|--help] [--foo]'
            )
        argvard.register_command('command', command)
        argvard(['application', 'command'])

        argvard = Argvard()
        argvard.main()(lambda context: None)
        command = Command()

        @command.main('foo bar')
        def main3(context, foo, bar):
            assert (
                context.command.get_usage(context) ==
                'application command [-h|--help] <foo> <bar>'
            )
        argvard.register_command('command', command)
        argvard(['application', 'command', 'foo', 'bar'])

    def test_define_main_twice(self):
        argvard = Argvard()

        @argvard.main()
        def foo():
            pass

        with pytest.raises(RuntimeError):
            @argvard.main()
            def bar():
                pass

    def test_call_without_main(self):
        argvard = Argvard()
        with pytest.raises(RuntimeError):
            argvard(['application'])

    def test_main(self, capsys):
        called = []
        argvard = Argvard()

        @argvard.main()
        def main(context):
            called.append(True)
        argvard(['application'])
        assert called == [True]

        with pytest.raises(SystemExit) as exception:
            argvard(['application', 'unexpected'])
        assert exception.value.code == 1
        stdout, stderr = capsys.readouterr()
        assert stdout == u''
        assert stderr == (
            u'error: unexpected argument "unexpected"\n'
            u'usage: application [-h|--help]\n'
        )

    def test_main_with_signature(self):
        called = []
        argvard = Argvard()

        @argvard.main('name')
        def main(context, name):
            called.append(name)
        argvard(['application', 'name'])
        assert called == ['name']

        called = []
        argvard = Argvard()

        @argvard.main('arguments...')
        def main2(context, arguments):
            called.append(arguments)
        argvard(['application', 'foo', 'bar', 'baz'])
        assert called == [['foo', 'bar', 'baz']]

        called = []
        argvard = Argvard()

        @argvard.main('[foo]')
        def main3(context, foo='default'):
            called.append(foo)
        argvard(['application'])
        assert called == ['default']
        del called[:]
        argvard(['application', 'argument'])
        assert called == ['argument']

        called = []
        argvard = Argvard()

        @argvard.main('[foo [bar]]')
        def main4(context, foo='foo', bar='bar'):
            called.extend([foo, bar])
        argvard(['application'])
        assert called == ['foo', 'bar']
        del called[:]
        argvard(['application', 'spam'])
        assert called == ['spam', 'bar']
        del called[:]
        argvard(['application', 'spam', 'eggs'])
        assert called == ['spam', 'eggs']

        called = []
        argvard = Argvard()

        @argvard.main('[foo...]')
        def main5(context, foo=None):
            if foo is None:
                foo = []
            called.append(foo)
        argvard(['application'])
        assert called == [[]]
        del called[:]
        argvard(['application', 'argument'])
        assert called == [['argument']]
        del called[:]
        argvard(['application', 'spam', 'eggs'])
        assert called == [['spam', 'eggs']]

    def test_main_without_argv(self, test_scripts_dir):
        process = subprocess.Popen(
            [
                'python', os.path.join(test_scripts_dir, 'echo.py'),
                'foo', 'bar', 'baz'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        assert stdout == b'foo\nbar\nbaz\n'
        assert stderr == b''


class TestOption(object):
    @pytest.mark.parametrize('name', [
        '',
        '--',
        '-',
        '-foo'
    ])
    def test_bad_name(self, name):
        argvard = Argvard()
        with pytest.raises(InvalidSignature):
            @argvard.option(name)
            def option():
                pass

    def test_define_twice(self):
        argvard = Argvard()

        @argvard.option('--option')
        def foo():
            pass

        with pytest.raises(RuntimeError):
            @argvard.option('--option')
            def bar():
                pass

    def test_overrideable(self):
        called = []
        argvard = Argvard()

        @argvard.option('--option', overrideable=True)
        def foo(context):
            called.append('foo')

        @argvard.option('--option')
        def bar(context):
            called.append('bar')
        argvard.main()(lambda context: None)
        argvard(['application', '--option'])
        assert called == ['bar']

    def test_basic(self):
        called = []
        argvard = Argvard()

        @argvard.option('--option')
        def option(context):
            called.append(True)
        argvard.main()(lambda context: None)
        argvard(['application'])
        assert called == []
        argvard(['application', '--option'])
        assert called == [True]

    def test_with_signature(self):
        called = []
        argvard = Argvard()

        @argvard.option('--option argument')
        def option(context, argument):
            called.append(argument)
        argvard.main()(lambda context: None)
        argvard(['application'])
        assert called == []
        with pytest.raises(ArgumentMissing):
            argvard(['application', '--option'])
        argvard(['application', '--option', 'foo'])
        assert called == ['foo']

    def test_repetitions_in_signature(self):
        argvard = Argvard()
        with pytest.raises(InvalidSignature):
            @argvard.option('--foo argument...')
            def option(context):
                pass

    def test_optional_in_signature(self):
        argvard = Argvard()
        with pytest.raises(InvalidSignature):
            @argvard.option('--foo [argument]')
            def option(context):
                pass

    def test_short_with_concatenated_argument(self):
        called = []
        argvard = Argvard()

        @argvard.option('-o argument')
        def option(context, argument):
            called.append(argument)
        argvard.main()(lambda context: None)
        argvard(['application', '-ofoo'])
        assert called == ['foo']

    def test_multiple_shorts(self):
        called = []
        argvard = Argvard()

        @argvard.option('-a')
        def a(context):
            called.append('a')

        @argvard.option('-b')
        def b(context):
            called.append('b')
        argvard.main()(lambda context: None)
        argvard(['application', '-ab'])
        assert called == ['a', 'b']

    def test_option_lookalike_ignored(self):
        called = []
        argvard = Argvard()

        @argvard.main('argument')
        def main(context, argument):
            called.append(argument)
        argvard(['application', '-foobar'])
        assert called == ['-foobar']

    def test_standalone_short_prefix_is_preserved(self):
        called = []
        argvard = Argvard()

        @argvard.main('argument')
        def main(context, argument):
            called.append(argument)
        argvard(['application', '-'])
        assert called == ['-']

    def test_long_with_concatenated_argument(self):
        called = []
        argvard = Argvard()

        @argvard.option('--option argument')
        def option(context, argument):
            called.append(argument)
        argvard.main()(lambda context: None)
        argvard(['application', '--option=foobar'])
        assert called == ['foobar']

    def test_ordering(self):
        argvard = Argvard()

        @argvard.option('-a')
        def foo():
            pass

        @argvard.option('-b')
        def bar():
            pass
        assert list(argvard.options.keys()) == ['-h', '--help', '-a', '-b']

    def test_usage(self):
        argvard = Argvard()

        @argvard.option('-a foo bar')
        def option(foo, bar):
            pass
        assert argvard.options['-a'].usage == u'-a <foo> <bar>'

    def test_multiple_name_definition(self):
        called = []
        argvard = Argvard()

        @argvard.option('-a|--abc')
        def option(context):
            called.append(True)

        @argvard.main()
        def main(context):
            assert (
                context.argvard.get_usage(context) ==
                u'application [-h|--help] [-a|--abc]'
            )
        argvard(['application', '-a', '--abc'])
        assert called == [True, True]


class TestContext(object):
    def test_defaults(self):
        argvard = Argvard(defaults={'a': 1})

        @argvard.option('-a')
        def option(context):
            assert 'a' in context
            assert context['a'] == 1
        argvard.main()(lambda context: None)
        argvard(['application', '-a'])

    def test_command_defaults(self):
        argvard = Argvard()

        @argvard.option('-a')
        def option(context):
            context['a'] = 1
        argvard.main()(lambda context: None)
        command = Command(defaults={'b': 1})

        @command.main()
        def main(context):
            assert 'a' in context
            assert context['a'] == 1
            assert 'b' in context
            assert context['b'] == 1
        argvard.register_command('command', command)
        argvard(['application', '-a', 'command'])

    def test_command_defaults_dont_override_context(self):
        argvard = Argvard()

        @argvard.option('-a')
        def option(context):
            context['a'] = 1
        argvard.main()(lambda context: None)
        command = Command(defaults={'a': 2})

        @command.main()
        def main(context):
            assert 'a' in context
            assert context['a'] == 1
        argvard.register_command('command', command)
        argvard(['application', '-a', 'command'])

    def test_inherited_by_commands(self):
        argvard = Argvard()

        @argvard.option('-a')
        def option(context):
            context['a'] = 1
        argvard.main()(lambda context: None)
        command = Command()

        @command.main()
        def main(context):
            assert 'a' in context
            assert context['a'] == 1
        argvard.register_command('command', command)
        argvard(['application', '-a', 'command'])

    def test_argvard_attribute(self):
        argvard = Argvard()

        @argvard.main()
        def main(context):
            assert context.argvard is argvard
        argvard(['application'])

    def test_command_path_attribute(self):
        argvard = Argvard()

        @argvard.main()
        def main(context):
            assert context.command_path == ['application']
        argvard(['application'])

        command = Command()

        @command.main()
        def command_main(context):
            assert context.command_path == ['application', 'command']
        argvard.register_command('command', command)
        argvard(['application', 'command'])

    def test_command_attribute(self):
        argvard = Argvard()

        @argvard.main()
        def main(context):
            assert context.command is None
        argvard(['application'])

        argvard = Argvard()
        argvard.main()(lambda context: None)
        command = Command()

        @command.main()
        def main2(context):
            assert context.command is command
        argvard.register_command('command', command)
        argvard(['application', 'command'])

    def test_caller_attribute(self):
        argvard = Argvard()

        @argvard.main()
        def main(context):
            assert context.caller is argvard

        command = Command()

        @command.main()
        def main2(context):
            assert context.caller is command

        argvard.register_command('command', command)

        argvard(['application'])
        argvard(['application', 'command'])


class TestHelpOption(object):
    @pytest.fixture(params=['-h', '--help'])
    def name(self, request):
        return request.param

    def test_application(self, capsys, name):
        argvard = Argvard()
        argvard.main()(lambda context: None)
        with pytest.raises(SystemExit) as exception:
            argvard(['application', name])
        assert exception.value.code == 1
        stdout, stderr = capsys.readouterr()
        assert stderr == u''
        assert stdout == (
            u'usage: application [-h|--help]\n'
            u'\n'
            u'options:\n'
            u'-h, --help\n'
            u'    Show this text.\n'
        )

    def test_application_description(self, capsys, name):
        argvard = Argvard()

        @argvard.main()
        def main():
            """
            A description.
            """
        with pytest.raises(SystemExit) as exception:
            argvard(['application', name])
        assert exception.value.code == 1
        stdout, stderr = capsys.readouterr()
        assert stderr == u''
        assert stdout == (
            u'usage: application [-h|--help]\n'
            u'\n'
            u'A description.\n'
            u'\n'
            u'options:\n'
            u'-h, --help\n'
            u'    Show this text.\n'
        )

    def test_option_description(self, capsys, name):
        argvard = Argvard()

        @argvard.option('--foo')
        def option(context):
            """
            A description.
            """
        argvard.main()(lambda context: None)
        with pytest.raises(SystemExit) as exception:
            argvard(['application', name])
        assert exception.value.code == 1
        stdout, stderr = capsys.readouterr()
        assert stderr == u''
        assert stdout == (
            u'usage: application [-h|--help] [--foo]\n'
            u'\n'
            u'options:\n'
            u'-h, --help\n'
            u'    Show this text.\n'
            u'--foo\n'
            u'    A description.\n'
        )

    def test_command(self, capsys, name):
        argvard = Argvard()
        argvard.main()(lambda context: None)
        command = Command()

        @command.main()
        def main(context):
            pass
        argvard.register_command('command', command)
        with pytest.raises(SystemExit) as exception:
            argvard(['application', 'command', name])
        assert exception.value.code == 1
        stdout, stderr = capsys.readouterr()
        assert stderr == u''
        assert stdout == (
            u'usage: application command [-h|--help]\n'
            u'\n'
            u'options:\n'
            u'-h, --help\n'
            u'    Show this text.\n'
        )

    def test_command_description(self, capsys, name):
        argvard = Argvard()
        argvard.main()(lambda context: None)
        command = Command()

        @command.main()
        def main(context):
            """
            Command description.

            Some more information that should not always be included.
            """
        argvard.register_command('command', command)
        with pytest.raises(SystemExit) as exception:
            argvard(['application', 'command', name])
        assert exception.value.code == 1
        stdout, stderr = capsys.readouterr()
        assert stderr == u''
        assert stdout == (
            u'usage: application command [-h|--help]\n'
            u'\n'
            u'Command description.\n'
            u'\n'
            u'Some more information that should not always be included.\n'
            u'\n'
            u'options:\n'
            u'-h, --help\n'
            u'    Show this text.\n'
        )
