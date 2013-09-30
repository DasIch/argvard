Argvard
=======

Argvard is a framework for command line applications inspired by Flask_ and
docopt_, available under the `Apache License, Version 2.0`_. It is designed to
be simple and intuitive to use without being constraining.

.. _Flask: http://flask.pocoo.org
.. _docopt: http://docopt.org
.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.html

::

    import sys
    from argvard import Argvard


    application = Argvard()
    @application.main('name')
    def main(context, name):
        print(u'Hello, %s!' % name)

    if __name__ == '__main__':
        application(sys.argv)
