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
import pytest

from argvard import (
    Argvard, Command, InvalidSignature, ArgumentMissing, UnexpectedArgument
)


class TestArgvard(object):
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

    def test_option_without_name(self):
        argvard = Argvard()
        with pytest.raises(InvalidSignature):
            @argvard.option('')
            def foo():
                pass

    @pytest.mark.parametrize('name', [
        '--',
        '-',
        '-foo'
    ])
    def test_option_with_bad_name(self, name):
        argvard = Argvard()
        with pytest.raises(InvalidSignature):
            @argvard.option(name)
            def option():
                pass

    def test_define_option_twice(self):
        argvard = Argvard()
        @argvard.option('--option')
        def foo():
            pass

        with pytest.raises(RuntimeError):
            @argvard.option('--option')
            def bar():
                pass

    def test_option_overrideable(self):
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

    def test_option(self):
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

    def test_option_with_signature(self):
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

    def test_option_short_with_concatenated_argument(self):
        called = []
        argvard = Argvard()
        @argvard.option('-o argument')
        def option(context, argument):
            called.append(argument)
        argvard.main()(lambda context: None)
        argvard(['application', '-ofoo'])
        assert called == ['foo']

    def test_option_multiple_shorts(self):
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

    def test_short_option_lookalike(self):
        called = []
        argvard = Argvard()
        @argvard.main('argument')
        def main(context, argument):
            called.append(argument)
        argvard(['application', '-foobar'])
        assert called == ['-foobar']

    def test_short_option_prefix(self):
        called = []
        argvard = Argvard()
        @argvard.main('argument')
        def main(context, argument):
            called.append(argument)
        argvard(['application', '-'])
        assert called == ['-']

    def test_long_option_with_concatenated_argument(self):
        called = []
        argvard = Argvard()
        @argvard.option('--option argument')
        def option(context, argument):
            called.append(argument)
        argvard.main()(lambda context: None)
        argvard(['application', '--option=foobar'])
        assert called == ['foobar']

    def test_option_ordering(self):
        argvard = Argvard()
        @argvard.option('-a')
        def foo():
            pass
        @argvard.option('-b')
        def bar():
            pass
        assert list(argvard.options.keys()) == ['-a', '-b']

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

    def test_main(self):
        called = []
        argvard = Argvard()
        @argvard.main()
        def main(context):
            called.append(True)
        argvard(['application'])
        assert called == [True]
        with pytest.raises(UnexpectedArgument):
            argvard(['application', 'unexpected'])

    def test_main_with_signature(self):
        called = []
        argvard = Argvard()
        @argvard.main('name')
        def main(context, name):
            called.append(name)
        argvard(['application', 'name'])
        assert called == ['name']

    def test_defaults(self):
        argvard = Argvard(defaults={'a': 1})
        @argvard.option('-a')
        def option(context):
            assert 'a' in context
            assert context['a'] == 1
        argvard.main()(lambda context: None)
        argvard(['application', '-a'])

    def test_context_inherited_by_commands(self):
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
