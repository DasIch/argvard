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
    argvard._compat
    ~~~~~~~~~~~~~~~

    :copyright: 2013 by Daniel Neuhäuser
    :license: Apache License 2.0, see LICENSE for more details
"""
import sys


PY2 = sys.version_info[0] == 2


if PY2:
    def implements_iterator(cls):
        cls.next = cls.__next__
        del cls.__next__
        cls.next.im_func.__name__ = 'next'
        return cls

    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()
else:
    def implements_iterator(cls):
        return cls

    def itervalues(d):
        return iter(d.values())

    def iteritems(d):
        return iter(d.items())
