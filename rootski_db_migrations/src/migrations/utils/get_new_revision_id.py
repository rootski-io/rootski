"""
Helper script to get new database revision ID.

The idea is that we want all of the revision scripts to be in ascending order.
This will make our alembic revision scripts easier to reason about.

We will use a file naming convention of "{revision_number}_{revision_name}.py".

This script finds the script with the latest revision number and prints
the version number after that to the stdout. So if we have the following
versions,

.. code-block:: text

    versions/
    ├── 1_start.py
    ├── 2_create_tables.py
    └── 3_seed_database.py

we would expect this script to print ``4``.
"""

from pathlib import Path
from typing import List

THIS_DIR = Path(__file__).parent
MIGRATION_VERSIONS_DIR = THIS_DIR / "../rootski_db/versions/"


def get_new_revision_id() -> str:
    """Return ``N + 1`` where ``N`` is the highest existing database revision ID."""
    latest_rev_id: str = get_latest_revision_id()
    new_rev_id = str(int(latest_rev_id) + 1)
    return new_rev_id


def get_latest_revision_id() -> str:
    """Return the ID of the most recent database revision file."""
    revision_fnames = get_revision_fnames()
    revision_ids: List[str] = [get_revision_id_from_revision_fname(rev_fname) for rev_fname in revision_fnames]
    revision_ids_as_ints: List[int] = [int(rev_id) for rev_id in revision_ids]
    latest_rev_id: str = str(max(revision_ids_as_ints))
    return latest_rev_id


def get_revision_fnames() -> List[str]:
    """Return a list of all of the database revision ``.py`` file names."""
    migration_fpaths: List[Path] = MIGRATION_VERSIONS_DIR.glob("*.py")
    migration_fnames: List[str] = [f.name for f in migration_fpaths]
    return migration_fnames


def get_revision_id_from_revision_fname(revision_fname: str) -> str:
    """Parse the ID of an alembic revision ``.py`` file.

    :param revision_fname: name the file (not the full file path)
    """
    revision_id: str = revision_fname.split("_")[0]
    return revision_id


def main():
    """Print the new highest version ID."""
    new_revision_id = get_new_revision_id()
    print(new_revision_id)


if __name__ == "__main__":
    main()
