# TODO use regex to make sure query strings are safe from SQL injection
from typing import Any, Dict, List

import pandas as pd
from loguru import logger
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from rootski.services.database.models.models import (
    Breakdown,
    BreakdownItem,
    Morpheme,
    MorphemeFamily,
    MorphemeFamilyMeaning,
    Word,
)
from rootski.services.database.non_orm import sql_statements
from rootski.services.database.non_orm.utils import collapse_df


class RootskiDBService:
    def __init__(self, engine: Engine):
        """
        Args:
            db_type: one of ["postgres", "sqlite"]. Will format queries accordingly.
        """
        self._engine = engine

    def run_query(self, query, as_df=False, **kwargs):
        """
        Args:
            query  (str): pre-validated SQL query ready to run against db
            as_df (bool): return dataframe object if true, otherwise, rows as dictionaries
            kwargs      : parameters to be forwarded to pandas.read_sql_query

        Returns:
            list[dict]: SQL result set (if not as_df)
            OR
            pd.DataFrame: SQL result set (if as_df)
        """
        try:
            logger.debug(f"Running query: {query}")
            # run query and parse results to dataframe
            result_set = pd.read_sql_query(query, con=self._engine, **kwargs)
            # if desired, convert dataframe rows to list of dicts
            if not as_df:
                result_set = result_set.to_dict(orient="records")
            logger.debug(f"Fetched results: {str(result_set)}")
            return result_set
        except Exception as e:
            logger.warning(f"Query failed with exception: {str(e)}")
            return []

    def query_word_by_id(self, word_id):
        # TODO: decide how to handle errors for example when the given word_id does not exist
        query = sql_statements.WORD_BY_ID.format(word_id=word_id)
        result_set = self.run_query(query)
        if len(result_set) > 0:
            return result_set[0]
        return None

    def search_words(self, search_key, limit=100):
        query = sql_statements.SEARCH_WORDS.format(search_key=search_key, limit=limit)
        return self.run_query(query)

    def search_morphemes(self, search_key, limit=100):
        query = sql_statements.SEARCH_MORPHEMES.format(search_key=search_key, limit=limit)
        return self.run_query(query)

    def query_definitions(self, word_id):
        """
        Returns

        .. code:: text

            [
                {
                    "word_type": str,
                    "definitions": [
                        {
                            "definition_id": int,
                            "def_position": int,              # the definition objs are sorted by def_position asc
                            "sub_defs": [
                                {
                                    "sub_def_id": int,
                                    "sub_def_position": int,  # sub_def objs are sorted by sub_def_position asc
                                    "definition": str,
                                    "notes": str | None
                                },
                                ...
                            ]
                        },
                        ...
                    ]
                },
                ...
            ]

        """
        query = sql_statements.DEFINITIONS.format(word_id=word_id)
        result_set = self.run_query(query, as_df=True)

        if len(result_set) == 0:
            return []

        # nest the sub definitions under the definitions
        result_set = collapse_df(
            result_set,
            groupby_col="definition_id",
            group_cols=["definition_id", "def_position", "pos"],
            child_cols=["sub_def_id", "sub_def_position", "definition", "notes"],
            child_name="sub_defs",
            grp_sort_col="def_position",
            ch_sort_col="sub_def_position",
        )
        logger.debug("Result set for definitions" + str(result_set))

        # nest the definitions under the word types
        result_set = pd.DataFrame(result_set)
        result_set = collapse_df(
            result_set,
            groupby_col="pos",
            group_cols=["pos"],
            child_cols=["def_position", "definition_id", "sub_defs"],
            child_name="definitions",
        )
        logger.debug(str(result_set))

        # NOTE: this is a hack, rather than play with sql queries, we are going
        # to manually de-duplicate the subdefinitions here
        def get_deduped_sub_defs(sub_defs: List[Dict[str, Any]]):
            deduped_sub_defs = []
            for sub_def in sub_defs:
                if len(deduped_sub_defs) == 0:
                    deduped_sub_defs.append(sub_def)
                else:
                    # if the subdef is already in the list, don't add it
                    if sub_def["sub_def_id"] in [sub_def["sub_def_id"] for sub_def in deduped_sub_defs]:
                        continue
                    deduped_sub_defs.append(sub_def)
            return deduped_sub_defs

        def get_result_item_with_deduped_sub_defs(result_item: Dict[str, Any]):
            to_return = result_item.copy()
            to_return["definitions"] = [
                {
                    **definition,
                    "sub_defs": get_deduped_sub_defs(definition["sub_defs"]),
                }
                for definition in result_item["definitions"]
            ]
            return to_return

        deduped_result_set = [get_result_item_with_deduped_sub_defs(definition) for definition in result_set]

        # END HACK :)

        return deduped_result_set

    def query_morpheme_breakdown(self, word_id):
        """
        Returns a breakdown of the following form

        .. code:: text

            [
                {
                    'morpheme': 'год',
                    'morpheme_id': 294.0,
                    'level': 3.0,
                    'position': 0,                  # morphemes sorted by position asc
                    'type': 'root',
                    'family_id': 134,
                    'family': 'гож,год,гожд',
                    'meanings': [
                        {
                            'meaning': 'pleasing:1'
                        },
                        ...
                    ]
                },
                ...
            ]
        """
        # query = sql_statements.MORPHEME_BREAKDOWN.format(word_id)
        # result_set_df = self.run_query(query, as_df=True)
        # result_set = collapse_df(result_set_df,
        #     groupby_col="position",
        #     group_cols=["morpheme", "morpheme_id", "level", "position", "type", "family_id", "family"],
        #     child_cols=["meaning"],
        #     child_name="meanings", grp_sort_col="position")
        # return result_set

        # query sqlalchemy table for Breakdown where id is morpheme_id
        with Session(self._engine) as session:
            to_return = []
            breakdown: Breakdown = session.query(Breakdown).where(Breakdown.word_id == word_id).limit(1).one()
            for breakdown_item in breakdown.breakdown_items:
                breakdown_item: BreakdownItem
                breakdown_item_fields = {
                    "morpheme_id": breakdown_item.morpheme_id,
                    "breakdown_id": breakdown_item.breakdown_id,
                    "morpheme": breakdown_item.morpheme,
                    "type": breakdown_item.type,
                    "position": breakdown_item.position,
                    "family_id": None,
                    "family": None,
                    "meanings": [],
                }

                if breakdown_item.morpheme_id:
                    family: MorphemeFamily = breakdown_item.morpheme_.family
                    breakdown_item_fields.update(
                        {
                            "family_id": family.id,
                            "family": family.family,
                        }
                    )

                if breakdown_item.morpheme_ and breakdown_item.morpheme_.family:
                    family: MorphemeFamily = breakdown_item.morpheme_.family
                    meanings = [{"meaning": m.meaning} for m in family.meanings]
                    breakdown_item_fields.update({"meanings": meanings})

                to_return.append(breakdown_item_fields)

            return to_return

    def query_adjective_forms(self, word_id):
        query = sql_statements.ADJECTIVE_FORMS.format(word_id)
        return self.run_query(query)

    def query_verb_conjugations(self, word_id):
        query = sql_statements.VERB_CONJUGATIONS.format(word_id)
        return self.run_query(query)

    def query_aspectual_pairs(self, word_id):
        query = sql_statements.ASPECTUAL_PAIRS.format(word_id)
        return self.run_query(query)

    def query_noun_declensions(self, word_id):
        query = sql_statements.NOUN_DECLENSIONS.format(word_id)
        return self.run_query(query)

    def query_example_sentences(self, word_id):
        query = sql_statements.EXAMPLE_SENTENCES.format(word_id)
        return self.run_query(query)

    def fetch_word_data(self, word_id, main_word_type):
        """
        1. Breakdown
        2. Definitions
        3. Example Sentences
        4. POS specific results i.e. verb, noun, etc.
        5. The word itself

        Args:
            word_id (int): id of a word in the "words" table
            main_word_type (str): one of ["noun", "adjective", "verb", "particle", "adverb", "preposition", "pronoun"]

        Returns:
            dict: payload-like object of all data to display on word page
        """

        data = {
            "word": self.query_word_by_id(word_id),
            # "breakdown": self.query_morpheme_breakdown(word_id),
            "definitions": self.query_definitions(word_id),
            "sentences": self.query_example_sentences(word_id),
        }

        pos_specific_data = dict()
        if main_word_type == "noun":
            pos_specific_data = self.fetch_noun_data(word_id)
        elif main_word_type == "verb":
            pos_specific_data = self.fetch_verb_data(word_id)
        elif main_word_type == "adjective":
            pos_specific_data = self.fetch_adjective_data(word_id)

        data.update(pos_specific_data)

        return data

    def fetch_adjective_data(self, word_id):
        """
        1. Adjective short forms
        """
        short_forms = self.query_adjective_forms(word_id)
        if len(short_forms) > 0:
            short_forms = short_forms[0]
        else:
            short_forms = None

        return {"short_forms": short_forms}

    def fetch_noun_data(self, word_id):
        """
        1. Declensions
        """
        declensions = self.query_noun_declensions(word_id)
        if len(declensions) > 0:
            declensions = declensions[0]
        else:
            declensions = None

        return {"declensions": declensions}

    def fetch_verb_data(self, word_id):
        """
        1. Conjugations
        2. Aspectual Pairs
        """
        conjugations = self.query_verb_conjugations(word_id)
        if len(conjugations) > 0:
            conjugations = conjugations[0]
        else:
            conjugations = None

        return {
            "conjugations": conjugations,
            "aspectual_pairs": self.query_aspectual_pairs(word_id),
        }
