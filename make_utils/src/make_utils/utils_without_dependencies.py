"""Common utils needed in makefile targets that written in pure python."""

import platform
from textwrap import dedent


def get_localhost():
    """
    Return the appropriate version of ``localhost`` to be used in Docker containers.

    The value of ``localhost`` is determined by the OS of the host machine running
    the docker containers.
    """
    system = platform.system().lower()

    is_linux = system == "linux"
    is_mac = system == "darwin"

    localhost = ""
    if is_mac:
        localhost = "host.docker.internal"
    elif is_linux:
        localhost = "127.0.0.1"

    return localhost


def safe_format(template, **kwargs):
    """
    Substitute occurences of ``${key}`` in the ``template`` string with its kwarg ``value``.

    The equivalent of str.format, but doesn't throw an error
    if you don't plug in a value for a {variable} section
    in a "{var1} ... {var2}" formatted string.
    """
    for key, value in kwargs.items():
        template = template.replace("${" + key + "}", value)
    return template


def print_import_error_help_message(error: ModuleNotFoundError):
    """Print a useful message teaching users how to install python dependencies for makefiles."""
    last_error_msg_line = str(error).splitlines()[-1]
    print("\n[rootski] Failure! make.xsh failed with this error:")
    print(f"\n          {last_error_msg_line}")
    print(
        dedent(
            """
        [rootski] You'll need to create and activate a python virtual environment
                  to run "make" commands. Here's how:

                  (1) install python version 3.9+, ideally using pyenv (https://github.com/pyenv/pyenv).
                      If you went with pyenv, do this:

                      (bash) pyenv install 3.9.7   # install this version
                      (bash) pyenv global 3.9.7    # set your "python" command to this version

                  (2) create a copy of that python version in the rootski/ repo directory:

                      # make sure "python" is the version you want; if it starts with a 2, you're in trouble
                      (bash) python --version

                      # create a copy of python with the "venv" module in a folder called "venv/"
                      (bash) python -m venv venv/

                  (3) "activate" your new "virtual environment" (copy of python)

                      (bash) source ./venv/bin/activate

                  (4) great job! run "python --version" again to make sure the version hasn't changed
                      you have now unlocked the "make install" command. Run it to install all the
                      python libraries you need to run the other "make" commands

                      (bash) make install
    """
        )
    )
