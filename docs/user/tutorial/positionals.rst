.. _positionals:

Dealing with positional arguments
=================================

Now that we have managed to greet the world, let us be more specific about whom
we greet or at least let users be able to do that::

    @application.main('name')
    def main(context, name):
        print(u'Hello, %s!' % name)

Replace the main function defined in `hello.py` with the code above. This
defines a signature for the main function. A signature defines which positional
arguments something takes, in this case a main function.

This signature defines one required positional argument called `name`.
Positional arguments are passed to the function under the names defined in the
signature.

Now in order to run `hello.py` you have to call it like this::

    $ python hello.py Daniel
    Hello, Daniel!

Obviously you can replace "Daniel" with your own name.


Default arguments
-----------------

This does introduce a problem though because if we call run `hello.py` as we
did previously, we get this::

    $ python hello.py
    error: name is missing
    usage: hello.py [-h|--help] <name>

If we want to have backwards compatibility, we need to make the name an
optional positional argument::

    @application.main('[name]')
    def main(context, name=u'World'):
        print(u'Hello, %s!' % name)

Now we can run the application with a name::

    $ python hello.py Daniel
    Hello, Daniel!

or without it::

    $ python hello.py
    Hello, World!


Repetitions
-----------

Now that we have managed to greet one person or well everyone. Let us try to
greet multiple people::

    @application.main('[name...]')
    def main(context, name=None):
        if name is None:
            name = [u'World']
        if len(name) == 1:
            print(u'Hello, %s!' % name[0])
        elif len(name) == 2:
            print(u'Hello %s and %s!' % (name[0], name[1]))
        else:
            print(u'Hello %s and %s!' % (u', '.join(name[:-1]), name[-1]))

The function does quite a bit more than the previous ones, to achieve a nice
formatting. Apart from that what has really changed is that we have added `...`
to the end of the argument in the signature.

Now we can greet any number of people::

    $ python hello.py
    Hello, World!
    $ python hello.py Daniel
    Hello, Daniel!
    $ python hello.py Daniel Horst
    Hello, Daniel and Horst!
    $ python hello.py Daniel Horst Peter
    Hello, Daniel, Horst and Peter!
