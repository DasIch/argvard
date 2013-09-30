# coding: utf-8
import os
from setuptools import setup


PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))


setup(
    name='Argvard',
    version='0.1.0-dev',
    url='https://github.com/DasIch/argvard',
    author='Daniel Neuhäuser',
    author_email='ich@danielneuhaeuser.de',
    license='Apache License, Version 2.0',
    description='Framework for command line applications',
    long_description=open(os.path.join(PROJECT_DIR, 'README.rst')).read(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    packages=['argvard']
)
