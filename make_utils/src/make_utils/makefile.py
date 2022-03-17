import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Callable, Dict, List, Optional

from rich import print
from rich.panel import Panel

FILE_WARNING_HEADER = dedent(
    """\
# WARNING! DO NOT MODIFY THIS FILE! It was generated automatically
# from the {script_name} file.
"""
)

############################
# --- Helper Functions --- #
############################


def comment_string(string: str):
    result = dedent("\n".join(["# " + line.strip() for line in string.splitlines()]))
    return result


def get_make_target_name(target: "Target"):
    """Derive a string for the makefile target from a function name."""
    return target.function.__name__.replace("_", "-")


def make_help_entry_from_function(target: "Target"):
    """
    Generate a string row for a function.

    :param target: The docstring will be taken from this function and
        used as the description in the help message
    :param alias: If set, the alias will be used for the function display name
        in the help message entry; otherwise, a name will be
        derived from the function name.
    """
    trg_name = target.alias or get_make_target_name(target)
    return f"\t  [yellow]{trg_name}[/yellow] -- {target.function.__doc__}"


def generate_help_message_tag_section(tag: str, targets: List["Target"]):
    """
    Create a group of target entries for the help section... with a header.

    \t<tag text>
    \t\thelp command 1 ...
    \t\thelp command 2 ...
    """
    # create a row in the help message for each target
    target_help_entries: str = "\n\n".join([make_help_entry_from_function(trg) for trg in targets])

    return dedent(
        f"""
    \t[bold cyan]{tag.upper()}[/bold cyan]

    {target_help_entries}
    """
    )


####################
# --- Makefile --- #
####################


@dataclass(frozen=True)
class Target:
    function: Callable
    alias: Optional[str] = None


class Makefile:
    """
    Decorator for registering python functions as makefile-like targets.

    A "target" is really just a function. "Target" is the term used
    to describe subcommands/functions in a Makefile.

    This class allows you to register python functions, generate
    a makefile from them, and print a nicely formatted help message.
    """

    def __init__(
        self,
        makefile_script_fname: str,
        makefile_header: str = "",
        help_message_extra: str = "",
        makefile_fpath: Path = Path("Makefile"),
    ):
        """
        :param makefile_script_fname: filename to use in the help message
            and refer to in the generated makefile targets. It could be a ``.py``
            or a ``.xsh`` script.
        :param help_message_extra: extra text to print in the header of the help message
            besides printing out all of the targets and their docstrings
        :param makefile_header: additional header text to use for a makefile
        :param makefile_fpath: location to create a makefile on 'make' or 'generate_makefile'
        """
        self.script_name: str = makefile_script_fname  # probably make.xsh or make.py
        self.makefile_header: str = makefile_header
        self.help_message_extra: str = help_message_extra
        self.makefile_fpath: Path = makefile_fpath  # path/to/Makefile

        # a list of functions that take no arguments; the keys are a tag
        # that can be used to group targets by category
        self._targets: Dict[str, List[Target]] = defaultdict(list)

        # register some default targets
        self.target(tag="makefile", alias="help")(self.print_help_msg)
        self.target(tag="makefile", alias="make")(self.generate_makefile)

    @property
    def targets(self) -> Dict[str, Target]:
        """
        Return a dict mapping makefile target names to python callables.

        The callables must not require any arguments.
        """
        # concatenate each of the grouped lists of targets in to a single list
        targets: List[Target] = []
        for _, trgs in self._targets.items():
            targets += trgs

        # map "func-name" -> func_name
        targets = {trg.alias or get_make_target_name(trg): trg for trg in targets}

        return targets

    ########################
    # --- Help Message --- #
    ########################

    def __generate_help_message(self):
        """Generate the help message for all targets."""
        # prepare to build the header of the help message
        number_of_pound_signs = len(self.script_name) + 12
        run_command = (
            f"python {self.script_name}"
            if self.script_name.endswith(".py")
            else f"python -m xonsh {self.script_name}"
        )

        # create the header for the help message
        help_message_header = dedent(
            f"""\
        [green]
        {'#' * number_of_pound_signs}
        # --- {self.script_name} --- #
        {'#' * number_of_pound_signs}[/green]

        {self.help_message_extra}

        [bold]USAGE[/bold]
        \t{run_command} [yellow]<command>[/yellow]

        [bold]COMMANDS[/bold]
        """
        )

        help_entries_grouped_by_tag: str = "".join(
            [generate_help_message_tag_section(tag, targets) for tag, targets in self._targets.items()]
        )

        # concatenate the help message parts
        return Panel(
            help_message_header + help_entries_grouped_by_tag,
            title="Help Documentation",
            expand=False,
            border_style="cyan",
            highlight=True,
        )

    def print_help_msg(self):
        """
        Show a list of available Makefile targets AKA commands.

        Run this! The output is nice and colorful ✨ 🎨 ✨
        """
        print(self.__generate_help_message())

    ####################
    # --- Makefile --- #
    ####################

    def target(self, tag: str = "", alias: Optional[str] = None):
        """
        Decorator that registers python functions as a target.

        :param tag: Allows targets to be grouped by "tag" in the help message.
        :param alias: If set, uses the alias as the makefile target name instead
            of deriving it from the function name.
        """

        def target_factory(command):
            # register the command as a makefile target
            self._targets[tag].append(Target(alias=alias, function=command))

            # make it so the command ends in the same directory it starts in
            cwd = Path.cwd()

            def command_that_ends_in_cwd():
                try:
                    command()
                finally:
                    os.chdir(cwd)

            return command_that_ends_in_cwd

        return target_factory

    def __generate_makefile_target_text(self, target: Target) -> str:
        """
        From a function like this:

        def example_target:
            "An example target."
            ...

        Return

        # An example target
        example-target:
            python -m xonsh <script_name> example-target # if .xsh
            OR
            python <script_name> example-target # if .py
        """
        # create a comment from the docstring
        docstring = target.function.__doc__
        comment = comment_string(docstring.strip()) if docstring is not None else ""

        # derive the target name from the command
        target_name: str = target.alias or get_make_target_name(target)

        # derive the python/xonsh command needed to run the command
        logic: str = (
            f"python {self.script_name} {target_name}"
            if self.script_name.endswith(".py")
            else f"python -m xonsh {self.script_name} {target_name}"
        )

        return dedent(comment) + dedent(
            f"""
        {target_name}:
        \t{logic}
        """
        )

    def __generate_makefile_tag_section(self, tag: str, targets: List[Target]) -> str:
        """Generate the text for an entire group of Makefile targets."""
        number_of_pounds = len(tag) + 12
        section_heading = dedent(
            f"""

        {'#' * number_of_pounds}
        # --- {tag.upper()} --- #
        {'#' * number_of_pounds}

        """
        )

        targets: str = "\n\n".join(self.__generate_makefile_target_text(trg) for trg in targets)

        return section_heading + targets

    def generate_makefile(self):
        """
        Generate a makefile from the targets registered with this instance of
        the Makefile decorator.
        """

        """
        .. note:: this docstring is split in half because we don't want the
            arguments to show up in the "make" target when running "make help".

        :param custom_text: Text that goes between the makefile header and
            the auto-generated makefile targets.
        :param makefile_fpath: Location to write the Makefile on disk.
        """
        do_not_modify_warning: str = FILE_WARNING_HEADER.format(script_name=self.script_name)

        target_grouped_by_tag: str = "".join(
            [self.__generate_makefile_tag_section(tag, targets) for tag, targets in self._targets.items()]
        )

        makefile_contents = "\n\n".join([do_not_modify_warning, self.makefile_header, target_grouped_by_tag])

        print(f'Creating makefile at path: "{self.makefile_fpath}"')
        with open(self.makefile_fpath, "w") as file:
            file.write(makefile_contents)

    ######################################
    # --- Executing Makefile Targets --- #
    ######################################

    def run(self):
        """Read the first argument to the script and execute the corresponding target."""
        args = sys.argv[1:]
        if len(args) == 0 or args[0] not in self.targets.keys():
            self.print_help_msg()
            sys.exit(1)
        else:
            command = self.targets[args[0]]
            command.function()


if __name__ == "__main__":

    # make us a decorator
    makefile = Makefile(
        makefile_script_fname="make.xsh",
        makefile_header="Text from the makefile header argument.",
        help_message_extra="HELP MESSAGE EXTRA",
        makefile_fpath=Path(__file__).parent / "Makefile",
    )

    # register a coupl'a makefile targets
    @makefile.target(tag="basic")
    def some_other_target():
        """
        This is a target with a multi-line docstring.

        Very cool explanation. Oh yeah!
        """
        ...

    @makefile.target(tag="basic")
    def target_three():
        """A third target"""
        ...

    @makefile.target(tag="basic")
    def some_target():
        """This is a target."""
        ...

    # generate the makefile in the same folder as this file
    THIS_DIR = Path(__file__).parent
    makefile.generate_makefile()

    makefile.print_help_msg()
