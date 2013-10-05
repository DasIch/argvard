Defining Options
================

So far we have concerned ourselves with whom we greet and not with how, let us
change. How an application does things can usually be changed by using options,
unfortunately there is not much you can change when saying hello to someone, so
we are going to turn our application into something much more general, that is
an application that greets people::

    @application.option('--greeting greeting')
    def greeting(context, greeting):
        context['greeting'] = greeting

This is quite similar to how main functions are defined. The difference is
that the signature in case of an option, includes the name of an option.

Another thing we do is use the `context` object that we have ignored so far.
This object is basically a dictionary that is passed around to capture the
state of the application. You are supposed to use it to store information
gathered in options.

Now we can use this information in the `context` in a main function::

    @application.main('[name...]')
    def main(context, name=None):
        if name is None:
            name = [u'World']
        greeting = context.get('greeting', u'Hello')
        if len(name) == 1:
            print(u'%s, %s!' % (greeting, name[0]))
        elif len(name) == 2:
            print(u'%s %s and %s!' % (greeting, name[0], name[1]))
        else:
            print(u'%s %s and %s!' % (greeting, u', '.join(name[:-1]), name[-1]))

Now we can use the `--greeting` option to change the way our application greets
people::

    $ python hello.py --greeting Hi
    Hi, World!

Congratulations! You have now learned everything you need to know about
Argvard, to create simple command line applications.
