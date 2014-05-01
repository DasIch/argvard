# coding: utf-8
# Copyright 2014 Daniel Neuhäuser
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
    tests.test_annotations
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""

from __future__ import print_function

import pytest
from functools import wraps

from argvard import Argvard, Command, annotations, UsageError


@pytest.mark.parametrize('input', ['3.0', '3'])
def test_floats(input):
    @annotations(number=float)
    def foo(context, number):
        return number

    rv = foo(None, number=input)
    assert isinstance(rv, float)
    assert rv == 3.0

    with pytest.raises(UsageError) as exception:
        foo(None, number='haha')

    assert str(exception.value).startswith(
        '\'haha\' is not a valid floating-point number')


def test_ints():
    @annotations(number=int)
    def foo(context, number):
        return number

    rv = foo(None, number='3')
    assert isinstance(rv, int)
    assert rv == 3

    with pytest.raises(UsageError) as exception:
        foo(None, number='haha')

    assert str(exception.value).startswith(
        '\'haha\' is not a valid integer')


@pytest.mark.parametrize('input,output', [
    ('true', True),
    ('yes', True),
    ('y', True),
    ('false', False),
    ('no', False),
    ('n', False),
    ('n', False)
])
def test_bool(input, output):
    @annotations(flag=bool)
    def foo(context, flag):
        return flag

    rv = foo(None, flag=input)
    assert isinstance(rv, bool)
    assert rv == output

    with pytest.raises(UsageError) as exception:
        foo(None, flag='haha')

    assert input in str(exception.value)


def test_infer_from_defaults():
    @annotations()
    def foo(context, bar, flag=True):
        assert bar == 42
        return flag

    assert not foo(None, bar=42, flag='false')
    assert foo(None, bar=42, flag='true')


def test_in_application(capsys):
    argvard = Argvard()

    @argvard.main('number')
    @annotations(number=float)
    def main(context, number):
        assert isinstance(number, float)
        print(number)

    @argvard.option('--option flag')
    @annotations(flag=bool)
    def option(context, flag):
        assert isinstance(flag, bool)
        print(flag)

    argvard(['application', '3'])

    stdout, stderr = capsys.readouterr()
    assert stdout == u'3.0\n'
    assert stderr == u''

    with pytest.raises(SystemExit):
        argvard(['application', 'haha'])

    stdout, stderr = capsys.readouterr()
    assert stderr.startswith(
        u'error: \'haha\' is not a valid floating-point number.\n'
        u'usage: application '
    )
    assert stdout == u''

    argvard(['application', '--option=yes', '3.0'])

    stdout, stderr = capsys.readouterr()
    assert stdout == u'True\n3.0\n'
    assert stderr == u''

    with pytest.raises(SystemExit):
        argvard(['application', '--option=maybe', '3.0'])

    stdout, stderr = capsys.readouterr()
    assert stderr.startswith(
        u'error: \'maybe\' is not a valid boolean. '
        u'The following values are allowed:'
    )
    assert stdout == u''


def test_in_command(capsys):
    command = Command()

    @command.main('number')
    @annotations(number=float)
    def command_main(context, number):
        assert isinstance(number, float)
        print(number)

    @command.option('--option flag')
    @annotations(flag=bool)
    def option(context, flag):
        assert isinstance(flag, bool)
        print(flag)

    argvard = Argvard()
    argvard.register_command('command', command)

    argvard(['application', 'command', '3'])

    stdout, stderr = capsys.readouterr()
    assert stdout == u'3.0\n'
    assert stderr == u''

    with pytest.raises(SystemExit):
        argvard(['application', 'command', 'haha'])

    stdout, stderr = capsys.readouterr()
    assert stderr.startswith(
        u'error: \'haha\' is not a valid floating-point number.\n'
        u'usage: application '
    )
    assert stdout == u''

    argvard(['application', 'command', '--option=yes', '3.0'])

    stdout, stderr = capsys.readouterr()
    assert stdout == u'True\n3.0\n'
    assert stderr == u''

    with pytest.raises(SystemExit):
        argvard(['application', 'command', '--option=maybe', '3.0'])

    stdout, stderr = capsys.readouterr()
    assert stderr.startswith(
        u'error: \'maybe\' is not a valid boolean. '
        u'The following values are allowed:'
    )
    assert stdout == u''


def test_interaction_with_other_decorators():
    @annotations()
    def foo(context, bar=42):
        return bar

    assert foo(None, bar='42') == 42

    with pytest.raises(RuntimeError) as exception:
        foo = annotations()(foo)

    assert 'decorator already applied' in str(exception.value).lower()

    def intermediate_decorator(func):
        @wraps(func)
        def wrapper(*a, **kw):
            return func(*a, **kw)
        return wrapper

    foo = intermediate_decorator(foo)

    with pytest.raises(RuntimeError):
        foo = annotations()(foo)

    assert foo(None, bar='42') == 42


def test_context_has_annotations():
    def foo(context=True, bar=42):
        pass

    with pytest.raises(RuntimeError):
        annotations()(foo)
