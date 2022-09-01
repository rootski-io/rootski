"""Read markdown files for creating tasks."""

from pathlib import Path
from typing import Dict, Generator, List


def parse_markdown_title(markdown: str):
    """Parse title from md file."""
    return markdown.strip().splitlines()[0].strip("#").strip()


def parse_markdown_to_dict(markdown_fpath: Path):
    """Parse contents of markdown file to dict."""
    markdown = markdown_fpath.read_text()
    return {"title": parse_markdown_title(markdown), "markdown": markdown}


def read_markdown_files(markdown_dir: Path) -> List[Dict[str, str]]:
    """Read in the markdown templates.

    Return a list of dictionaries of the following form:

    .. code-block:: json

        {
            "title": "Task Title",
            "markdown": "# Markdown Contents!",
        }

    Args:
        markdown_dir: directory of the markdown files
    """
    markdown_fpaths: Generator[Path, None, None] = markdown_dir.glob("*.md")
    return [parse_markdown_to_dict(path) for path in markdown_fpaths]
