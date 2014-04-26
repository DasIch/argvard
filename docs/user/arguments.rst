Arguments
=========

Validation with annotations
---------------------------

Argvard can use `function annotations <http://python.org/dev/peps/pep-3107/>`_
to validate and convert arguments::

    from argvard import Argvard, annotations

    application = Argvard()

    @application.main('number')
    def main(number:float):
        assert isinstance(number, float)
        print('Hooray!')

Since Python 2 doesn't have function annotations, you can explicitly use the
:py:func:`argvard.annotations` function decorator::

    from argvard import Argvard, annotations

    application = Argvard()

    @application.main('number')
    @annotations(number=float)
    def main(number):
        ...

Any callable which returns the new value or raises ``ValueError`` on invalid
input can be used instead of ``float``.

Most builtin types should just work, but some of them are special-cased to be
more liberal in input, and to provide nicer error messages:

* ``bool``: Accepts ``{"y", "yes", "true"}`` for ``True`` and ``{"n", "no",
  "false"}`` for ``False``. Case-insensitive.

* ``float, int``: Same accepted values as the builtins, but nicer error
  messages.

If you want ``number`` to be an optional argument, you would have to write it like this::

    @application.main('number')
    @annotations()
    def main(number:float = 1.0):
        ...

The :py:func:`argvard.annotations` decorator also guesses the type of variables
by their default value. In the above example you wouldn't have to specify
``number`` to be a float::

    @application.main('number')
    @annotations()
    def main(number=1.0):
        ...

Simple validation
-----------------

If for some reason you don't want to or can't use annotations, you can still do
what the decorator does under the hood and raise :py:exc:`argvard.UsageError`
in your functions to show a error message and exit::

    from argvard import Argvard, UsageError

    application = Argvard()

    @application.main('number')
    def main(number):
        try:
            number = float(number)
        except ValueError:
            raise UsageError('This is not a number.')
