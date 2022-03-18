"""
Utility functions for makefiles written in pure python.

Some of the uses include:

- logging
- rendering templates where values are formatted ${LIKE_THIS}
- raising Errors
"""

import sys
from textwrap import dedent

# pylint: disable=redefined-builtin
from rich import print

from make_utils.utils_without_dependencies import safe_format


class MakeXshError(Exception):
    """
    Custom exception that can halt program execution on init.

    This is useful when running bash-like commands in .xsh scripts
    which should halt the script execution if the command fails. For example,

    .. code-block:: text

        # should cause the .xsh program to exit with a useful message
        cat non_existant_file.txt || @(MakeXshError("File does not exist!"))
    """

    def __init__(self, msg, _exit=True):
        super().__init__(msg)
        log(f"Error: {msg}", mode="error")
        if _exit:
            sys.exit(1)


def log(msg, mode="info"):
    """
    Write a colorized message to the console with a ``[rootski]`` prefix for utility scripts.

    :param mode: determines the color of the log message
    """
    color = {
        "info": "cyan",
        "error": "red",
    }[mode]
    # pylint: disable=anomalous-backslash-in-string
    print(f"[green]\[rootski][/green] [{color}]{msg}[/{color}]")


def render_template(template_fpath, values, outfile_path=None):
    """
    Render a template file where the file has placeholders in the form of ``${variable_name}``.

    Args:
        template_fpath (Path): file path to a text file name *.template.*;
        values Dict[str, str]: dictionary where keys appear in the template as {key}
            and are replaced wit the value
        outfile_path (Path | None): location to write the rendered template to,
            if None, render it in the same location. If outfile_path is a directory,
            the rendered template will be placed inside it.

    Raises:
        MakeXshError: if ".template" is not present in the file name
    """
    filename = template_fpath.name
    if ".template" not in filename:
        MakeXshError("File name must contain '.template'")

    file_warning_header = dedent(
        f"""
        # WARNING! DO NOT MODIFY THIS FILE! It was generated automatically by make.xsh
        # by populating the {filename} template.\n\n
    """
    )

    if not outfile_path:
        outfile_path = template_fpath.parent / filename.replace(".template", "")
    elif outfile_path.is_dir():
        outfile_path = outfile_path / filename.replace(".template", "")

    rendered_template_contents = safe_format(template_fpath.read_text(), **values)

    outfile_path.write_text(file_warning_header + rendered_template_contents)
