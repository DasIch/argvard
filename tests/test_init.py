# coding: utf-8
"""
    tests.test_init
    ~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
"""
import pytest

from argvard import Argvard, InvalidSignature, ArgumentMissing


class TestArgvard(object):
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

    def test_option(self):
        called = []
        argvard = Argvard()
        @argvard.option('--option')
        def option():
            called.append(True)
        argvard.main()(lambda: None)
        argvard(['application'])
        assert called == []
        argvard(['application', '--option'])
        assert called == [True]

    def test_option_with_signature(self):
        called = []
        argvard = Argvard()
        @argvard.option('--option argument')
        def option(argument):
            called.append(argument)
        argvard.main()(lambda: None)
        argvard(['application'])
        assert called == []
        with pytest.raises(ArgumentMissing):
            argvard(['application', '--option'])
        argvard(['application', '--option', 'foo'])
        assert called == ['foo']

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
        def main():
            called.append(True)
        argvard(['application'])
        assert called == [True]

    def test_main_with_signature(self):
        called = []
        argvard = Argvard()
        @argvard.main('name')
        def main(name):
            called.append(name)
        argvard(['application', 'name'])
        assert called == ['name']
