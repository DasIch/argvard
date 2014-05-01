Changelog
=========

Version 0.3.1
-------------

*In development*

- Added Python 3.4 support. It should have worked previously but from now on
  it's tested.
- Fix an issue that caused docstrings to not be properly dedented when used
  as descriptions, producing among other things badly formatted help text.
- Added ability to raise :py:exc:`argvard.UsageError` inside functions to get
  help output.
- Added :doc:`annotations </user/arguments>` as a way of validating user input.

Version 0.3.0
-------------

- Execution is now delegated to ``--help``, if no main function has been
  defined.


Version 0.2.1
-------------

- Fixed typos in the documentation.


Version 0.2.0
-------------

- Added :class:`argvard.Argvard.from_main` and
  :class:`argvard.Command.from_main` to reduce overhead when creating simple
  applications or commands.


Version 0.1.0
-------------

Initial release.
