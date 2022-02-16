import numpy as np
import pandas as pd


def get_group_data(
    group_df: pd.DataFrame,
    *group_cols,
):
    first_row = group_df.iloc[0]
    return {col: first_row[col] for col in group_cols}


def get_group_children(group_df, *child_cols, sort_col=None, ascending=True):
    child_df: pd.DataFrame = group_df[list(child_cols)]
    if sort_col is not None:
        child_df.sort_values(sort_col, ascending=ascending, inplace=True)
    child_rows = child_df.to_dict(orient="records")
    return child_rows


def collapse_df(
    df: pd.DataFrame,
    groupby_col,
    group_cols,
    child_cols,
    child_name,
    grp_sort_col=None,
    grp_ascending=True,
    ch_sort_col=None,
    ch_ascending=True,
):
    """
    Collapses results of two joined dataframes.

    Args:
        df (pd.DataFrame): dataframe to collapse
        groupby_col (str): column name to group by and collapse
        group_cols (list[str]): list of column names to keep at the group level
        grp_sort_col (str): one of the group_cols, sort the group rows by this col
        grp_ascending (bool): sort group cols in ascending order
        child_cols (list[str]): list of columns to keep for each child in the child attribute
        child_name (str): name of the child attribute
        ch_sort_col (str): one of the child_cols, sorts children within group by this column
    """

    collapsed_rows = list()

    # solves JSON serialization problem by casting numpy types to python types
    df = df.replace({np.nan: None})
    df = df.astype(object)

    groupby = df.groupby(groupby_col)
    groups = list(groupby.groups.keys())

    for group in groups:
        group_df = groupby.get_group(group)
        group_data = get_group_data(group_df, *group_cols)
        group_children = get_group_children(group_df, *child_cols, sort_col=ch_sort_col, ascending=ch_ascending)
        group_data[child_name] = group_children
        collapsed_rows.append(group_data)

    if grp_sort_col:
        collapsed_rows = sorted(collapsed_rows, key=lambda row: row[grp_sort_col], reverse=not grp_ascending)

    return collapsed_rows
