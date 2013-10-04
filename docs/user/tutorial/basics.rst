Creating a basic "Hello World!"-Application
==========================================

The first step on our journey will be to create a simple "Hello World!"
application. The first part of that application consists of importing what we
need::

    from argvard import Argvard

The :class:`~argvard.Argvard` object is central to every Argvard application
and -- for now -- the only thing we are going to need. The next part of the
application is creating such an object::

    application = Argvard()

As you can see this is trivial as we do not have to pass it any arguments. As
you can see from the name I gave it, for all intents and purposes it is the
application. The next step is making that the application do something::

    @application.main()
    def main(context):
        print(u'Hello, World!')

The `application.main` decorator is used to register what in Argvard terms is
called the `main` function. If you are familiar with other programming
languages, you may be aware that a `main` function of some form can be found in
many languages. In languages in which it exists it acts as an entry point and
is automatically called when your application is started.

This case is similiar, `main` is a function that will always be called by the
`application` after any options have been parsed. The `main` function is
supposed to do, whatever your application is supposed to do.

The last step is calling the application::

    if __name__ == '__main__':
       application()

If you are not already familiar with the pattern, `__name__` is a special
variable the interpreter sets to the name of the current module. If the module
is being executed directly (and is not just imported), `__name__` will be set
to ``'__main__'``. This ensures that `application` is not called, unless the
module is executed directly, which makes it possible to import the module
without any side effects.

Once you have typed that into your editor, save it as `hello.py` and execute
it with ``python hello.py``. It should print "Hello, World!" and exit.
