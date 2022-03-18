"""SQLAlchemy models, each of which represents a table in the rootski database."""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import expression, func
from sqlalchemy.types import Boolean, Integer

# Base object which will contain all proto table declarations
Base = declarative_base()


class GenericToString:
    """Mixin for adding default magic methods to SQLAlchemy models."""

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return self.__repr__()


# re-used types
POS_ENUM = Enum(
    "preposition",
    "interjection",
    "participle",
    "particle",
    "adjective",
    "pronoun",
    "verb",
    "noun",
    "conjunction",
    "adverb",
    name="parts_of_speech",
)
MORPHEME_TYPE_ENUM = Enum("prefix", "suffix", "root", "link", name="morpheme_types")


def print_ddl(table_class, connection_or_engine):
    """Print the CREATE TABLE DDL for the given table class

    Args:
        table_class: class inheriting from Base
        connection_or_engine: connection/engine
    """
    print(CreateTable(table_class.__table__).compile(connection_or_engine))


#################
# --- Users --- #
#################


class User(Base, GenericToString):
    """Table to represent users."""

    __tablename__ = "users"

    # WARNING! We are using the user email as the primary key.
    # This is considered to be bad practice. We may change this
    # in the future, but for now I'm more concerned about protecting
    # users from losing their data if we delete/lose the existing
    # cognito user pool for any reason. By using the email, if the
    # cognito user pool gets deleted, users don't lose their data
    # as long as they re-register with the same email as before.
    email = Column(String(512), primary_key=True, nullable=True)
    is_admin = Column(Boolean, nullable=False, server_default=expression.false())

    # one-to-many
    submitted_breakdowns = relationship(
        "Breakdown",
        uselist=True,
        primaryjoin="User.email==Breakdown.submitted_by_user_email",
        back_populates="submitted_by_user",
    )
    verified_breakdowns = relationship(
        "Breakdown",
        uselist=True,
        primaryjoin="User.email==Breakdown.verified_by_user_email",
        back_populates="verified_by_user",
    )


################
# --- Word --- #
################


class Word(Base, GenericToString):
    """Contains a row for each russian word searchable by rootski."""

    __tablename__ = "words"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    word = Column(String(256), nullable=False, comment="russian word in cyrillic characters")
    accent = Column(
        String(256),
        nullable=False,
        comment="russian word in cyrillic characters, which may include a ''' or 'ё' on the stressed syllable",
    )
    pos = Column(POS_ENUM, nullable=False, comment="part of speech (noun, adjective, etc.")
    frequency = Column(Integer, nullable=True, comment="frequency rank of the word")

    # one-to-many
    breakdowns = relationship(
        "Breakdown",
        uselist=True,
        # foreign_keys=["word_to_breakdowns.breakdown_id"],
        # foreign_keys=[ForeignKey("word_to_breakdowns.breakdown_id")],
        back_populates="word_",
    )


######################
# --- Breakdowns --- #
######################


class MorphemeFamily(Base, GenericToString):
    """This table is necessary because some families have multiple meanings"""

    __tablename__ = "morpheme_families"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # TODO make 'family' a @property calculated by SQLAlchemy, rather than an actual field in the database
    family = Column(
        String(256),
        nullable=True,
        comment="comma separated list of morphemes in the morpheme family (cyrillic)",
    )
    level = Column(
        Integer,
        nullable=True,
        comment="difficulty level of the morpheme--level 1 should be learned first",
    )

    # one-to-many
    morphemes = relationship("Morpheme", uselist=True, back_populates="family")
    meanings = relationship("MorphemeFamilyMeaning", uselist=True, back_populates="family")


class MorphemeFamilyMeaning(Base, GenericToString):
    """Definition of a family of morphemes."""

    __tablename__ = "morpheme_family_meanings"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    family_id = Column(Integer, ForeignKey("morpheme_families.id"), nullable=False)
    meaning = Column(String(256), nullable=True, comment="meaning of the morpheme family if any")

    # many-to-one
    family = relationship("MorphemeFamily", uselist=False, back_populates="meanings")


class Morpheme(Base, GenericToString):
    """Roots, prefixes, and suffixes that comprise Russian words."""

    __tablename__ = "morphemes"

    morpheme_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    morpheme = Column(
        String(256),
        nullable=False,
        comment="one morpheme variant in a morpheme family (cyrillic)",
    )
    type = Column(MORPHEME_TYPE_ENUM, nullable=False)
    word_pos = Column(
        Enum("any", "adjective", "noun", "verb", name="morpheme_word_pos"),
        nullable=False,
        comment="some morphemes only appear in certain types (part of speech) of words",
    )  # formerly word_type
    family_id = Column(Integer, ForeignKey("morpheme_families.id"), nullable=False)

    # many-to-one
    family: MorphemeFamily = relationship("MorphemeFamily", uselist=False, back_populates="morphemes")


class Breakdown(Base, GenericToString):
    """
    An ordered collection of roots, prefixes, suffixes, or "null-morphemes".

    The ordered collection must sum to the word.
    """

    __tablename__ = "word_to_breakdowns"

    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    breakdown_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    word = Column(String(256), nullable=True, comment="Optional: word associated with the word_id")
    submitted_by_user_email = Column(
        String(512),
        ForeignKey("users.email"),
        nullable=True,
        comment="id of the user who submitted the breakdown--if null, the submission is anonymous",
    )
    verified_by_user_email = Column(
        String(512),
        ForeignKey("users.email"),
        nullable=True,
        comment="id of the admin user who verified the breakdown--should be null exactly when the breakdown is unverified",
    )
    is_verified = Column(
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="if True, the frontent should use this record--only one breakdown should be allowed to have True for this value",
    )
    is_inference = Column(
        Boolean,
        nullable=False,
        server_default=expression.false(),
        comment="Whether the breakdown came from a model. If True, submitted_by_user_email is null.",
    )
    date_submitted = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    date_verified = Column(DateTime, nullable=True, onupdate=func.current_timestamp())

    # one-to-many
    breakdown_items = relationship("BreakdownItem", uselist=True, back_populates="breakdown")

    # many-to-one
    word_ = relationship("Word", uselist=False, foreign_keys=[word_id], back_populates="breakdowns")
    verified_by_user = relationship(
        "User",
        uselist=False,
        foreign_keys=[verified_by_user_email],
        back_populates="verified_breakdowns",
    )
    submitted_by_user = relationship(
        "User",
        uselist=False,
        foreign_keys=[submitted_by_user_email],
        back_populates="submitted_breakdowns",
    )


class BreakdownItem(Base, GenericToString):
    """A reference to a root, prefix, or suffix as part of a word breakdown."""

    __tablename__ = "breakdowns"
    # __table_args__ = (
    #     # a morpheme should never be used twice in the same word (unless it is the NULL morpheme)
    #     # so we set these columns up as the unique primary keys of this table
    #     PrimaryKeyConstraint("breakdown_id", "morpheme_id"),
    # )

    # this id column is required by sqlalchemy
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="This id is not used in rootski logic, SQLAlchemy requires a primary key",
    )
    morpheme_id = Column(
        Integer,
        ForeignKey("morphemes.morpheme_id"),
        nullable=True,
        comment="if not null, this word substring is an identified morpheme",
    )
    breakdown_id = Column(Integer, ForeignKey("word_to_breakdowns.breakdown_id"), nullable=True)
    morpheme = Column(
        String(256),
        nullable=False,
        comment="a substring of a word--if the morpheme_id is not null, this substring is an identified morpheme",
    )
    type = Column(
        MORPHEME_TYPE_ENUM,
        nullable=True,
        comment="matches `type` in the morpheme table if the morpheme is identified, else null",
    )
    position = Column(
        Integer,
        nullable=False,
        comment="where this word substring belongs in the order of all the word substrings that make up the word",
    )

    # many-to-one
    morpheme_ = relationship("Morpheme", uselist=False)
    breakdown = relationship(
        "Breakdown",
        uselist=False,
        primaryjoin=breakdown_id == Breakdown.breakdown_id,
        back_populates="breakdown_items",
    )


###########################
# --- Parts of Speech --- #
###########################


class Noun(Base, GenericToString):
    """Grammatical information about nouns."""

    __tablename__ = "nouns"

    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, primary_key=True)
    word = Column(String(256), nullable=False, comment="the original word in cyrillic characters")
    gender = Column(
        Enum("m", "f", "n", name="noun_genders"),
        nullable=True,
        comment="word gender -- masculine, femenine, or neuter",
    )
    animate = Column(
        Boolean,
        nullable=True,
        comment="true if the noun is animate, false if inanimate",
    )
    indeclinable = Column(
        Boolean,
        nullable=True,
        comment="true if the noun is indeclinable, false if declinable",
    )

    # singular cases
    nom = Column(String(256), nullable=True, comment="nominative case")
    acc = Column(String(256), nullable=True, comment="accusative case")
    prep = Column(String(256), nullable=True, comment="prepositional case")
    gen = Column(String(256), nullable=True, comment="genetive case")
    dat = Column(String(256), nullable=True, comment="dative case")
    inst = Column(String(256), nullable=True, comment="instrumental case")

    # plural cases
    nom_pl = Column(String(256), nullable=True, comment="nominative plural case")
    acc_pl = Column(String(256), nullable=True, comment="accusative plural case")
    prep_pl = Column(String(256), nullable=True, comment="prepositional plural case")
    gen_pl = Column(String(256), nullable=True, comment="genetive plural case")
    dat_pl = Column(String(256), nullable=True, comment="dative plural case")
    inst_pl = Column(String(256), nullable=True, comment="instrumental plural case")

    # one-to-one
    _word = relationship("Word", uselist=False)


class Adjective(Base, GenericToString):
    """Grammatical information about adjectives."""

    __tablename__ = "adjectives"

    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, primary_key=True)
    comp = Column(String(256), nullable=True, comment="comparative form")
    fem_short = Column(String(256), nullable=True, comment="femenine short form with accent")
    masc_short = Column(String(256), nullable=True, comment="masculine short form with accent")
    neut_short = Column(String(256), nullable=True, comment="neuter short form with accent")
    plural_short = Column(String(256), nullable=True, comment="plural short form with accent")

    # one-to-one
    word = relationship("Word", uselist=False)


class Conjugation(Base, GenericToString):
    """Grammatical information about verbs."""

    __tablename__ = "verbs"

    word_id = Column(Integer, ForeignKey("words.id"), nullable=False, primary_key=True)
    aspect = Column(
        Enum("perf", "impf", name="verb_aspects"),
        nullable=False,
        comment="verb aspect -- imperfective or perfective",
    )

    # present/future tense
    _1st_per_sing = Column("1st_per_sing", String(256), comment="I")
    _2nd_per_sing = Column("2nd_per_sing", String(256), comment="you (informal)")
    _3rd_per_sing = Column("3rd_per_sing", String(256), comment="he/she/it")
    _1st_per_pl = Column("1st_per_pl", String(256), comment="we")
    _2nd_per_pl = Column("2nd_per_pl", String(256), comment="you all (you formal)")
    _3rd_per_pl = Column("3rd_per_pl", String(256), comment="they")

    # past tense
    past_m = Column(String(256), comment="past masculine")
    past_f = Column(String(256), comment="past femenine")
    past_n = Column(String(256), comment="past neuter")
    past_pl = Column(String(256), comment="past plural")

    # participle forms
    actv_part = Column(String(256), comment="active particible")
    pass_part = Column(String(256), comment="passive participle")
    actv_past_part = Column(String(256), comment="active past participle")
    pass_past_part = Column(String(256), comment="passive past participle")

    gerund = Column(String(256), comment="gerund")
    impr = Column(String(256), comment="imperative")
    impr_pl = Column(String(256), comment="imperative plural")

    # one-to-one
    word = relationship("Word", uselist=False)


class VerbPair(Base, GenericToString):
    """Aspectual pairs of Russian verbs, one is imperfective the other is perfective."""

    # TODO, redo this so that the columns are "verb_id", "other_verb_id", so there will be
    # AT LEAST 2 * n rows in this table where n is the number of verbs
    __tablename__ = "verb_pairs"
    # __table_args__ = (
    #     # since this is an "Association" table, we set both of the foreign keys
    #     # as the the compound-primary-key of this table
    #     PrimaryKeyConstraint("imp_word_id", "pfv_word_id"),
    # )

    _id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="Ignore this, it's just for SQLAlchemy",
    )
    imp_word_id = Column(Integer, ForeignKey("words.id"))
    pfv_word_id = Column(Integer, ForeignKey("words.id"))


#############################
# --- Example Sentences --- #
#############################


class Sentence(Base, GenericToString):
    """A sentence in the Russian language."""

    __tablename__ = "sentences"

    sentence_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    sentence = Column(String(2048), nullable=False, comment="Russian example sentence (cyrillic)")

    # one-to-one
    translation = relationship("SentenceTranslation", uselist=False, back_populates="sentence")


class SentenceTranslation(Base, GenericToString):
    """An English translation for the sentence in the Russian language."""

    __tablename__ = "sentence_translations"

    translation_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    sentence_id = Column(Integer, ForeignKey("sentences.sentence_id"))
    translation = Column(
        String(2048),
        nullable=False,
        comment="English translation of one of the russian example sentences",
    )

    # one-to-one
    sentence = relationship("Sentence", uselist=False, back_populates="translation")


class WordToSentence(Base, GenericToString):
    """Association table between words and sentences."""

    __tablename__ = "word_to_sentence"
    __table_args__ = (
        # since this is an "Association" table, we set both of the foreign keys
        # as the the compound-primary-key of this table
        PrimaryKeyConstraint("word_id", "sentence_id"),
    )

    word_id = Column(Integer, ForeignKey("words.id"))
    sentence_id = Column(Integer, ForeignKey("sentences.sentence_id"), nullable=False)
    exact_match = Column(
        Boolean,
        nullable=False,
        comment="whether the example sentence contains exactly the word",
    )


######################################
# --- Definitions / Translations --- #
######################################


class Definition(Base, GenericToString):
    """
    Definitions of Russian words.

    There are 2 types of definition in this table: parent and child.
    Parent definitions have a null "definition" field. Parent definitions
    can be joined with the "definition_contents" table to access the child/sub definitions
    of those rows.
    """

    __tablename__ = "definitions"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    pos = Column(POS_ENUM, nullable=True)  # formerly called "word_type"
    definition = Column(String(512), nullable=True, comment="null if this is a parent definition")
    notes = Column(String(256), nullable=True)

    # one-to-many
    # contents = relationship("DefinitionItem", uselist=True, back_populates="definition")

    # we would need this if we used DefinitionExample since we'd have 2 tables pointing to
    # the Definition.id foreign key (that's polymorphism since there can be 2 types of child)
    # __mapper_args__ = {
    #     "polymorphic_on": id,
    #     "polymorphic_identity":"definitions",
    #     "with_polymorphic":"*"
    # }


# currently unused
# class DefinitionExample(Base, GenericToString):
#     __tablename__ = "definition_examples"
#     __mapper_args__ = {"polymorphic_identity":"definition_examples"}

#     definition_id = Column(Integer, ForeignKey("definitions.id"))
#     id   = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     russ = Column(String(2048), nullable=False, comment="russian translation of example specific to this definition")
#     eng  = Column(String(2048), nullable=False, comment="english translation of example specific to this definition")


class DefinitionItem(Base, GenericToString):
    """
    Association table between definitions and definition items.

    Each row in this table represents either
    a sub-definition or an example. The join to get a list of sub-definitions from
    a word looks like this:

    word -> word_defs -> definition_contents -> definitions or examples
    """

    __tablename__ = "definition_contents"
    # __mapper_args__ = {"polymorphic_identity":"definition_contents"}
    __table_args__ = (PrimaryKeyConstraint("definition_id", "child_id"),)

    definition_id = Column(Integer, ForeignKey("definitions.id"))
    child_type = Column(Enum("definition", "example", name="definition_child_types"), nullable=False)
    # technically this ForeignKey can be to both definitions and definition_examples, but
    # the definition_examples table isn't currently being used.
    child_id = Column(Integer, ForeignKey("definitions.id"), nullable=False)
    position = Column(
        Integer,
        nullable=False,
        comment="position in the order of sub-definitions or examples belonging to a definition",
    )

    # many-to-one
    definition = relationship("Definition", uselist=False, foreign_keys=[definition_id])
    child = relationship("Definition", uselist=False, foreign_keys=[child_id])
