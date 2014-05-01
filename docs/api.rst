API
===

.. module:: argvard


.. data:: __version__

   The version as a string.


.. data:: __version_info__

   The version as a tuple, containing the major, minor, and bugfix version. You
   should use this, if you need to implement any version checks.


Application Object
------------------

.. autoclass:: Argvard
   :members:
   :inherited-members:


Command Object
--------------

.. autoclass:: Command
   :members:
   :inherited-members:


Context Object
--------------

.. autoclass:: Context
   :members:

Annotations
-----------

.. autofunction:: annotations

Exceptions
----------

.. autoclass:: UsageError
