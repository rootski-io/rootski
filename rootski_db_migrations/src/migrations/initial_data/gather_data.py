"""
Gather the russian data csv files and load them into database tables.

This script relies on a few environment variables variables:

.. code-block:: yaml

    DATA_DIR: absolute path to the data dir (useful if running in docker)
    POSTGRES_USER: the postgres user
    POSTGRES_PASSWORD: the postgres password
    POSTGRES_DB: the postgres database
    POSTGRES_HOST: the postgres host
    POSTGRES_PORT: the postgres port

.. note::

    Hi there, Eric here. I am *so* sorry about the code quality in this file.
    I wrote most of it years ago when

    a. I hadn't learned about good practices
    b. I was moving fast trying to get the data just organized enough to start building the application

    A few glaring problems here are:

    - this file is long so it's hard to digest
    - the pandas operations are hard to understand (this is usually the case)
    - the docstrings use a format inconsistent with the rest of rootski (we've moved from Google format to Sphinx)
    - magic numbers
    - the comments and docstrings are vague
    - there are very few type annotations

    We'll incrementally refactor this file as it makes sense.
"""

import os
import sys
import time
from os.path import join
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from migrations.initial_data.initial_models import (
    Base,
    Breakdown,
    BreakdownItem,
    Definition,
    DefinitionItem,
    Morpheme,
    MorphemeFamily,
    MorphemeFamilyMeaning,
    Sentence,
    SentenceTranslation,
    VerbPair,
    Word,
)
from migrations.utils.alembic_x_args import get_db_connection_string_from_env_vars
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# get the location of the csv files
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = join(THIS_DIR, "data") if not os.environ.get("DATA_DIR") else os.environ.get("DATA_DIR")


def get_group_data(
    group_df: pd.DataFrame,
    *group_cols,
) -> Dict[str, pd.DataFrame]:
    """
    Convert a dataframe resulting from a ``df.groupby()`` call to a dict.

    The keys of the dict is the value defining the group.
    """
    first_row = group_df.iloc[0]
    return {col: first_row[col] for col in group_cols}


def get_group_children(group_df, *child_cols, sort_col=None, ascending=True) -> Dict[str, pd.DataFrame]:
    """Turn a dataframe resulting from ``df.groupby()`` into a dict."""
    child_df: pd.DataFrame = group_df[list(child_cols)]
    if sort_col is not None:
        child_df.sort_values(sort_col, ascending=ascending, inplace=True)
    child_rows = child_df.to_dict(orient="records")
    return child_rows


# pylint: disable=too-many-arguments, invalid-name, too-many-locals
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
    collapsed_rows = []

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


# pylint: disable=invalid-name
def collapse_deconstructions_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Separate the deconstructions dataframe into 2.

    The joins will look like this:

    word -> deconstructions (and then some python logic to get them in the right form)
    to
    word -> word_to_breakdown -> breakdowns

    Args:
        df: the deconstructions dataframe

    Returns:
        word_to_breakdown_df, breakdowns_df
    """
    # collapse the breakdowns df on the breakdown_id
    collapsed_rows = collapse_df(
        df,
        groupby_col="breakdown_id",
        group_cols=["breakdown_id", "word", "word_id"],
        child_cols=["breakdown_id", "morpheme", "type", "morpheme_id", "position"],
        child_name="breakdown",
        grp_sort_col=None,
        grp_ascending=True,
        ch_sort_col="position",
        ch_ascending=True,
    )

    collapsed_df = pd.DataFrame(collapsed_rows)

    # separate out words_to_breakdown from breakdowns (deconstructions)
    word_to_breakdown_df = collapsed_df[["word_id", "breakdown_id", "word"]]
    breakdown_rows = []
    for _, row in collapsed_df.iterrows():
        breakdown_rows += row["breakdown"]
    breakdowns_df = pd.DataFrame(breakdown_rows)

    return word_to_breakdown_df, breakdowns_df


def collapse_family_meanings_df(family_meanings: pd.DataFrame):
    """Break the family meanings df into two dfs that can be joined.

    The same morpheme family can have multiple meanings.

    However, we only have one csv: family_meanings, where the "primary_key" (family_id)
    is not unique: it repeats when there is more than one meaning.

    As a result of this function, the join to get a morpheme meaning looks like this:
    morpheme -> morpheme_families -> morpheme_family_meanings
    """
    collapsed_rows = collapse_df(
        family_meanings,
        groupby_col="family_id",
        group_cols=["family_id", "family", "level"],
        child_name="meanings",
        child_cols=["meaning", "family_id"],
    )
    collapsed_df = pd.DataFrame(collapsed_rows)

    # separate out morpheme families from family meanings
    morpheme_families = collapsed_df[["family_id", "family", "level"]].rename(columns={"family_id": "id"})

    family_meaning_rows = []
    for _, row in collapsed_df.iterrows():
        family_meaning_rows += row["meanings"]
    family_meanings = pd.DataFrame(family_meaning_rows)

    return family_meanings, morpheme_families


# pylint: disable=too-many-statements, too-many-locals
def load_base_tables(db_conn_url: str = None, seeding_db: bool = True, connection=None, verbose=False):
    """
    Load CSV files into the SQL database pointed to by ``db_conn_url``.

    Args:
        db: connection string to a database
        seeding_db: if True, drop/create tables before loading the database.
            if False, assume the tables are already created.
        connection: a sqlalchemy connection to the database, used if :db_conn_url:
            not provided
    """
    chunksize = 2**11

    #################
    # --- Words --- #
    #################

    words = pd.read_csv(join(DATA_DIR, "words.csv")).rename(columns={"type": "pos"})
    pd.read_csv(join(DATA_DIR, "declensions.csv"))
    adjectives = pd.read_csv(join(DATA_DIR, "adjectives.csv")).reset_index(drop=True)
    nouns = pd.read_csv(join(DATA_DIR, "nouns.csv")).astype({"animate": bool, "indeclinable": bool})
    # drop the nouns that don't have an associated word in the words table
    columns = list(set(nouns.columns))
    nouns = pd.merge(words, nouns, left_on="id", right_on="word_id", indicator=True, how="inner").rename(
        columns={"word_x": "word"}
    )[columns]
    conjugations = pd.read_csv(join(DATA_DIR, "conjugations.csv"))

    ######################
    # --- Breakdowns --- #
    ######################

    breakdowns = pd.read_csv(join(DATA_DIR, "breakdown-items.csv"))
    word_to_breakdown = pd.read_csv(join(DATA_DIR, "word-to-breakdown.csv"))
    # remove breakdowns that aren't in word_to_breakdown
    breakdowns = breakdowns[breakdowns["breakdown_id"].isin(word_to_breakdown["breakdown_id"])]
    # word_to_breakdown["submitted_by"] = None
    # word_to_breakdown["verified_by"] = None
    word_to_breakdown["is_verified"] = False
    word_to_breakdown["is_inference"] = False
    # don't set "date_submitted" so that it can default to current_timestamp
    # word_to_breakdown["date_submitted"] = None
    word_to_breakdown["date_verified"] = None

    #####################
    # --- Morphemes --- #
    #####################

    morphemes = pd.read_csv(join(DATA_DIR, "morphemes_v3.csv")).rename(columns={"word_type": "word_pos"})
    # one of the morphemes has an invalid type:
    morphemes = morphemes[morphemes.word_pos != "suffix"]
    family_meanings = pd.read_csv(join(DATA_DIR, "family_meanings_v1.csv"))
    morpheme_family_meanings, morpheme_families = collapse_family_meanings_df(family_meanings)
    # not all morphemes have meanings, so their families were not in family-meanings.csv; nevertheless they *do* have family_id's
    # so this join will add families for those morphemes
    merge = pd.merge(
        morphemes,
        morpheme_families,
        left_on="family_id",
        right_on="id",
        how="outer",
    )
    merge["id"] = merge["family_id"]
    merge = merge[merge.id.notnull()].drop_duplicates(["id", "family"])  # drop na on "id" column
    morpheme_families = merge[morpheme_families.columns]

    # At this point, the following SQL query:

    # select (sort of *)
    # from morphemes
    # inner join morpheme_families on morphemes.family_id = morpheme_families.id
    # where morpheme_families.family is null or morpheme_families.level is null

    # returns this

    # morpheme_id morpheme    type    pos         family_id family level
    # 2266	    ионный	    suffix	adjective	1425      NULL	 NULL
    # 2496	    о	        link	any	        1426	  NULL	 NULL
    # 2497	    е	        link	any	        1427	  NULL	 NULL

    # basically, for these 3 rows, the family and level are null. This causes
    # Errors in the API. We need to fix this:

    morpheme_families.family = morpheme_families.family.fillna(merge.morpheme)
    morpheme_families.level = morpheme_families.level.fillna(value=6.0)

    # get rid of the duplicate "вать" that we removed from the morphemes dataframe earlier
    morpheme_family_meanings = morpheme_family_meanings[morpheme_family_meanings.family_id != 1303]

    verb_pairs = pd.read_csv(join(DATA_DIR, "verb_pairs.csv"))[["imp_word_id", "pfv_word_id"]]

    #####################
    # --- Sentences --- #
    #####################

    sentences = pd.read_csv(join(DATA_DIR, "sentences.csv"))
    translations = pd.read_csv(join(DATA_DIR, "translations.csv"))
    word_to_sentence = pd.read_csv(join(DATA_DIR, "word_to_sentence.csv")).astype({"exact_match": bool})

    #######################
    # --- Definitions --- #
    #######################

    word_defs = pd.read_csv(join(DATA_DIR, "word_defs.csv"))
    # exclude 'cases' column from definitions
    definitions = pd.read_csv(join(DATA_DIR, "definitions.csv"))[
        ["id", "word_type", "definition", "notes"]
    ].rename(columns={"word_type": "pos"})
    definition_contents = pd.read_csv(join(DATA_DIR, "definition_contents.csv"))
    # we're not using the definition examples because they are sparse
    # definition_examples = pd.read_csv(join(DATA_DIR, 'definition_examples.csv'))

    # Create the tables from SQLAlchemy definitions
    engine: Engine = None
    if db_conn_url:
        engine = create_engine(db_conn_url, echo=verbose)
    else:
        if not connection:
            raise ValueError("You must provide one of :db: or :connection: as an argument")

    if seeding_db:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    # Populate the created SQL tables from the dataframes
    to_sql_args = {
        "if_exists": "append",
        "con": engine,
        "index": False,
        "chunksize": chunksize,
    }

    words.to_sql(name="words", **to_sql_args)
    adjectives.to_sql(name="adjectives", **to_sql_args)
    nouns.to_sql(name="nouns", **to_sql_args)
    conjugations.to_sql(name="conjugations", **to_sql_args)

    word_to_breakdown.to_sql(name="word_to_breakdowns", **to_sql_args)
    morpheme_families.to_sql(name="morpheme_families", **to_sql_args)
    morpheme_family_meanings.to_sql(name="morpheme_family_meanings", **to_sql_args)
    morphemes.to_sql(name="morphemes", **to_sql_args)
    breakdowns.to_sql(name="breakdowns", **to_sql_args)
    verb_pairs.to_sql(name="verb_pairs", **to_sql_args)
    sentences.to_sql(name="sentences", **to_sql_args)
    translations.to_sql(name="sentence_translations", **to_sql_args)
    word_to_sentence.to_sql(name="word_to_sentence", **to_sql_args)

    word_defs.to_sql(name="word_defs", **to_sql_args)
    definitions.to_sql(name="definitions", **to_sql_args)
    definition_contents.to_sql(name="definition_contents", **to_sql_args)
    # we aren't using the definition_examples because the data was very sparse
    # definition_examples.to_sql(name='definition_examples', **to_sql_args)

    # create indexes for faster querying (this way gets faster results than setting the
    # pd.DataFrame index and setting index=True in pd.to_sql(if_exists="replace", )
    con = engine.connect()
    con.execute(
        """CREATE UNIQUE INDEX "idx_definition_id" ON "definitions" (
        "id"	ASC
    );"""
    )
    # again, we're not using the definition examples
    # con.execute("""CREATE UNIQUE INDEX "idx_example_id" ON "definition_examples" (
    #     "id"	ASC
    # );""")
    con.execute(
        """CREATE UNIQUE INDEX "idx_word_id" ON "words" (
        "id"	ASC
    );"""
    )
    con.execute(
        """CREATE UNIQUE INDEX "idx_sentence_id" ON "sentences" (
        "sentence_id"	ASC
    );"""
    )
    con.close()


# def load_definitions_examples_materialized_view(db_type):

#     # execute query to create definitions/examples materialized view
#     engine = create_engine(postgres, echo=True)
#     sql = SQL_STATEMENTS.LOAD_DEFINITIONS_AND_EXAMPLES_MATERIALIZED_VIEW

#     if db_type == "postgres":
#         sql = to_postgres(sql)

#     with engine.connect() as conn:
#         conn.execute(sql)


#############################################
# --- Fix for autoincrement in postgres --- #
#############################################

# Inserts into the database were failing. I searched for hours and finally found this SO answer:
# https://stackoverflow.com/questions/4448340/postgresql-duplicate-key-violates-unique-constraint
#
# Apparently, since gather_data.py is doing a bulk load of rows into postgres tables, postgres
# doesn't know which value to start incrementing the primary key in each table. Postgres is dumb
# about "autoincrementing" primary keys. It doesn't discover the MAX_VALUE of a given primary key
# column and set the next inserted id to (MAX_VALUE + 1). Instead, it just starts at 1 (or some
# other number in my case) and adds one to that each time... even if there are already 200,000 rows
# taking up IDs 1-200,000... not good.
#
# To fix this, we need to call the SETVAL() postgres function on all of our primary key columns
# in all of our tables after doing a bulk load.
#

SET_VAL_QUERY = """
select setval(
    pg_get_serial_sequence('{table_name}', '{pk_column}'),
    (select max({pk_column}) from {table_name}) + 1
)
"""

PRIMARY_KEY_TABLES_AND_COLUMNS = [
    (Word, "id"),
    (MorphemeFamily, "id"),
    (MorphemeFamilyMeaning, "id"),
    (Morpheme, "morpheme_id"),
    (Breakdown, "breakdown_id"),
    (BreakdownItem, "id"),
    (VerbPair, "_id"),
    (Sentence, "sentence_id"),
    (SentenceTranslation, "translation_id"),
    (Definition, "id"),
    (DefinitionItem, "definition_id"),
    (DefinitionItem, "child_id"),
]


def fix_pkey_for_table(table_name, pk_column, engine: Engine):
    """Set the autoincrement value to the correct number in a primary key column.

    This fixes a problem where data loaded from a CSV into the postgres database
    doesn't correctly update the autoincrementing primary key value. Result:
    if we load primary keys 1, 2, and 3 and then insert a new row in the table,
    postgres will try to insert 1 again. We need it to insert 4 in this scenario.

    :param table_name: SQL table to fix the primary key column in
    :param pk_column: Autoincrementing column in the table to fix
    :param _engine: SQLAlchemy object to connect to the database
    """
    print(f"Setting sequence for {table_name}")
    query = SET_VAL_QUERY.format(table_name=table_name, pk_column=pk_column)
    engine.execute(query)


def fix_all_tables(
    engine: Engine,
    table_pk_pairs: Optional[List[Tuple[Any, str]]] = None,
):
    """Fix the autoincrement problem on all tables in ``table_pk_pairs``.

    :param engine: for connecting to the database
    :param table_pk_pairs: List of tuples where the first argument is a SQLAlchemy model class and the
        second is a primary key column name whose autoincrement should be fixed.
    """
    table_pk_pairs: List[Tuple[Any, str]] = table_pk_pairs or PRIMARY_KEY_TABLES_AND_COLUMNS
    for table, pk_column in table_pk_pairs:
        fix_pkey_for_table(table.__tablename__, pk_column, engine)


def seed_database(connection_string: str):
    """Load several data from CSV files into a SQL database.

    :param connection_string: URL for the database with credentials
    """
    try:
        load_base_tables(connection_string, seeding_db=True, verbose=True)
        engine: Engine = create_engine(connection_string, echo=True)
        fix_all_tables(engine=engine)
    except Exception as err:
        with open("error.log", "w", encoding="utf-8") as file:
            file.write(str(err))
        raise err

    split_deconstructions_table_into_breakdown_and_word_to_breakdown_tables = False
    if split_deconstructions_table_into_breakdown_and_word_to_breakdown_tables:
        deconstructions_df = pd.read_csv(join(DATA_DIR, "breakdowns-raw.csv"))
        word_to_breakdown, breakdowns = collapse_deconstructions_df(deconstructions_df)
        word_to_breakdown.to_csv(join(DATA_DIR, "word-to-breakdown.csv"), index=False)
        breakdowns.to_csv(join(DATA_DIR, "breakdown-items.csv"), index=False)


def is_database_seeded(connection_string: str, retries=10, retry_delay_seconds=3) -> bool:
    """Return ``True`` if the data in this script has already been loaded into a database."""
    for i in range(retries):
        try:
            engine: Engine = create_engine(connection_string)
            with Session(bind=engine) as session:
                words: List[Word] = session.query(Word).limit(5).all()
                print(f"Got words from the database: {words}")

                if len(words) == 5:
                    print("success")
                    return True
        # pylint: disable=broad-except
        except Exception as err:
            print(err)
            print(f"Retry {i}/{retries} failed to connect see if the database is seeded. Trying again.")
        time.sleep(retry_delay_seconds)
    return False


def main():
    """Consume the CLI arguments and perform an operation against against a running database."""
    # read CLI arguments
    args = sys.argv
    arg = args[1]

    # get the db conenction string
    conn_str = get_db_connection_string_from_env_vars(confirm_url_with_user=False)

    # run the specified subcommand
    command = {
        "seed-db": lambda: seed_database(conn_str),
        "is-db-seeded": lambda: is_database_seeded(conn_str),
    }[arg]
    command()


if __name__ == "__main__":
    main()
