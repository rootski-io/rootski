=========================
Make Utils
=========================

This python package enables us to easily use ``xonsh``, a python-based superset of
``bash`` to write Makefiles.

This has several benefits:

- We can generate true Makefiles which gives the benefit of CLI autocompletion.
- We can use python for our makefile targets instead of ``bash`` or worse ``sh``.
- ``make help`` provides a beautiful help page in the terminal that uses
  the ``make.xsh`` docstrings as descriptions for each of the makefile targets.


There are some drawbacks:

- Since the Makefile becomes a thin wrapper around calls like
  ``python -m xonsh make.xsh <target name>``, you must have Python installed
  to use the Makefile. And preferebly, a virtual environment created and activated.
  This adds an unfortunate step for contributors only intend to develop the frontend
  React application. However, the reward for setting this all up is several
  easy-to-use, well-documented makefile targets that make life much easier.
