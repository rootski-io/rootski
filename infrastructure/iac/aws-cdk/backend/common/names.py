def cfn_format_name(name: str) -> str:
    """
    Remove occurrences of ``-`` or ``_`` from the string and title case around those.

    Example::

        >>> cfn_format_name("rootski-iam_user_id")
        'RootskiIamUserId'

    :returns: string that CFN will not modify if used as an identifier
    """
    parts = name.split("-")
    name = "".join([part.title() for part in parts])
    parts = name.split("_")
    name = "".join([part.title() for part in parts])
    return name
