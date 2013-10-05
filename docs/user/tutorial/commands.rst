Defining Commands
=================

If you develop larger command line applications, like pip_ which you probably
used to install Argvard, your application often does not perform a specific
action like greeting someone but instead allows the user to perform multiple
distinct actions.

.. _pip: http://www.pip-installer.org/

In the case of pip such an action is installing or uninstalling something.
These are fundamentally different actions, not just in what they operate on,
how they operate but in what they do. We do not want to choose between these
actions based on positional arguments or options, we need a different way
to express these: commands.

A :class:`~argvard.Command` is very much like an argvard object. A command
requires a main function that performs something and we can register options
on a command.

Let us create a simple calculator as an example::

    from argvard import Argvard, Command

    application = Argvard()

    @application.main()
    def main(context):
        context.argvard(context.command_path + ['--help'])

The calculator, unless called with a command, has nothing useful to do. So
within the main function we recursively call the application with the `--help`
option, to provide the user with a help message that explains how the
application should be used.

Now comes there interesting part, defining the commands::

    add = Command()
    @add.main('a b')
    def add_main(context, a, b):
        print(int(a) + int(b))

    sub = Command()
    @sub.main('a b')
    def sub_main(context, a, b):
        print(int(a) - int(b))

As you can see and as mentioned above, command objects are very similar to
argvard objects in how they are used. We are not doing this in the tutorial but
you could also add options to the `add` or `sub` commands. Now that the commands
have been defined you have to register them with the application::

    application.register_command('add', add)
    application.register_command('sub', sub)

The string passed to :meth:`~argvard.Argvard.register_command` is the name, which
is used on the command line to call the command we are registering. In case you
were wondering, you can also register commands with other commands.

Finally we call the application, just as we did in our previous "Hello World"
application::

    if __name__ == '__main__':
        application()

If you run the application the commands can be invoked as expected::

    $ python calc.py add 1 1
    2
    $ python calc.py sub 1 1
    0

Congratulations! You have now learned everything you need to know about
Argvard, to create command line applications.
