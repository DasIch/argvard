Signatures
==========

Signatures are used to define positional arguments of an option, command or the
application. A signature consists of zero or more *words* separated by spaces.

A *word* can be a *name*, -- and if the signature does not describe the
positional arguments of an option -- a *repetition* or an *optional*.

A *name* is a python identifier, that an argument will be bound to.

A *repetition* is a name followed by `...`, it matches one or more arguments,
all of which will be bound to the name.

An *optional* is a name or repetition followed by zero or more words enclosed
in brackets.

For a short overview this is the grammar in EBNF_::

    signature = [ word { " " word } ]
    word = name | repetition | optional ;
    name = (* Any valid Python identifier *) ;
    repetition = name "..." ;
    optional = "[" (name | repetition) { word } "]" ;


.. _EBNF: http://en.wikipedia.org/wiki/Extended_Backus-Naur_Form
