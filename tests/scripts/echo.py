# coding: utf-8
from __future__ import print_function
from argvard import Argvard


application = Argvard()


@application.main('[arguments...]')
def main(context, arguments):
    for argument in arguments:
        print(argument)


if __name__ == '__main__':
    application()
