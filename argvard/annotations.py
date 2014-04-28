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
    argvard.annotations
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""
from __future__ import print_function
import functools
import inspect

from argvard._compat import iteritems
from argvard.exceptions import UsageError


try:
    # normal getargspec doesn't work with annotations
    _getargspec = inspect.getfullargspec
except AttributeError:
    # and in Python 2 there are no annotations
    _getargspec = inspect.getargspec


IS_ANNOTATED = object()


def annotations(from_defaults=True, **kwargs):
    """
    A function decorator which coerces argument values to the annotated types.
    This decorator is implicitly applied to command and option functions.
    Explicitly wrapping your functions with it allows more fine-grained
    configuration and the usage of annotations in Python 2. Applying this
    decorator multiple times will raise a :py:exc:`RuntimeError`.

    :param from_defaults: Infer the type of arguments by their default value.
    :param kwargs: Python 2 doesn't have function annotations, so you can
        also pass types here as keyword arguments.
    """

    def decorator(func):
        func = set_annotations(**kwargs)(func)
        if from_defaults:
            func = infer_from_defaults(func)
        func = resolve_shortcuts(func)
        func = with_annotations(func)
        return func

    return decorator


def set_annotations(**kwargs):
    def decorator(func):
        if not hasattr(func, '__annotations__'):
            func.__annotations__ = {}
        func.__annotations__.update(kwargs)
        return func
    return decorator


def with_annotations(func):
    if getattr(func, '_argvard_annotations', None) == IS_ANNOTATED:
        raise RuntimeError('Decorator already applied.')
    if 'context' in func.__annotations__:
        raise RuntimeError('Setting type annotations on the context '
                           'variable is not allowed.')

    @functools.wraps(func)
    def wrapper(context, **arguments):
        for key, value in list(iteritems(arguments)):
            annotation = func.__annotations__.get(key, None)
            if annotation:
                try:
                    value = annotation(value)
                except ValueError as e:
                    raise UsageError(str(e))

            arguments[key] = value

        return func(context, **arguments)

    wrapper._argvard_annotations = IS_ANNOTATED
    return wrapper


def infer_from_defaults(func):
    spec = _getargspec(func)
    spec.args
    for key, value in zip(reversed(spec.args), reversed(spec.defaults or ())):
        cls = type(value)

        # Check if type behaves correctly, e.g. NoneType doesn't and is
        # completely meaningless for validation anyway.
        try:
            if cls(value) != value:
                raise ValueError()
        except (ValueError, TypeError):
            pass
        else:
            func.__annotations__[key] = cls

    return func


def integer_type(x):
    try:
        return int(x)
    except ValueError:
        raise ValueError('{!r} is not a valid integer.'.format(x))


def float_type(x):
    try:
        return float(x)
    except ValueError:
        raise ValueError('{!r} is not a valid floating-point number.'.format(x))


def boolean_type(x):
    values = {'y': True, 'yes': True, 'true': True, 'n': False, 'no': False,
              'false': False}
    try:
        return values[x.lower()]
    except KeyError:
        raise ValueError('{!r} is not a valid boolean. The following values '
                         'are allowed: {}'.format(x, ', '.join(values)))


_builtin_shortcuts = {
    int: integer_type,
    bool: boolean_type,
    float: float_type,
}


def resolve_shortcuts(func, shortcuts=_builtin_shortcuts):
    for key, value in list(iteritems(func.__annotations__)):
        if value in shortcuts:
            func.__annotations__[key] = shortcuts[value]

    return func
