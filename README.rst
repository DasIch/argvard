Argvard
=======

.. image:: https://travis-ci.org/DasIch/argvard.png?branch=master
   :target: https://travis-ci.org/DasIch/argvard

.. image:: https://coveralls.io/repos/DasIch/argvard/badge.png?branch=master
   :target: https://coveralls.io/r/DasIch/argvard?branch=master

.. image:: https://badge.fury.io/py/Argvard.png
   :target: http://badge.fury.io/py/Argvard

Argvard is a framework for command line applications inspired by Flask_ and
docopt_, available under the `Apache License, Version 2.0`_. It is designed to
be simple and intuitive to use without being constraining.

.. _Flask: http://flask.pocoo.org
.. _docopt: http://docopt.org
.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.html

::

    from argvard import Argvard

    application = Argvard()

    @application.main('name')
    def main(context, name):
        print(u'Hello, %s!' % name)

    if __name__ == '__main__':
        application()

If you want to learn more take a look at the documentation_.

.. _documentation: https://argvard.readthedocs.org
