WORD_BY_ID = """
SELECT
    id as word_id
    ,word
    ,accent
    ,pos
    ,frequency
FROM words
WHERE words.id={word_id}
"""

SEARCH_WORDS = """
SELECT
	id
	,word
    ,type
    ,frequency
FROM words
WHERE words.word LIKE "{search_key}%"
LIMIT {limit};
"""

SEARCH_MORPHEMES = """
SELECT
	morpheme_id
	,morpheme
	,"type"
FROM morphemes
WHERE morphemes.morpheme LIKE "%{search_key}%"
LIMIT {limit}
"""

DEFINITIONS = """
-- definitions
SELECT
    word_defs.definition_id
    ,word_defs."position" as "def_position"
    ,definition_contents.child_id as "sub_def_id"
    ,definition_contents."position" as "sub_def_position"
    ,definitions.pos
    ,definitions.definition
    ,definitions.notes
FROM words
INNER JOIN word_defs
ON words.id = word_defs.word_id
INNER JOIN definition_contents
ON word_defs.definition_id = definition_contents.definition_id
INNER JOIN definitions
ON definition_contents.child_id = definitions.id
WHERE TRUE
    AND child_type != 'example'
    AND words.id = {word_id};
"""

MORPHEME_BREAKDOWN = """
-- root breakdown and meanings
SELECT
	breakdowns.morpheme_id
	,breakdowns.morpheme
	,breakdowns."position"
	,breakdowns."type"
	,family_meanings.family_id
	,family_meanings."level"
	,family_meanings.meaning
	,family_meanings.family -- do we want to maintain an up-to-date family string all the time?
FROM breakdowns
LEFT JOIN morphemes
ON breakdowns.morpheme_id = morphemes.morpheme_id
LEFT JOIN family_meanings
ON morphemes.family_id = family_meanings.family_id
WHERE word_id = {};
"""

ADJECTIVE_FORMS = """
-- adjective
SELECT
	comp
	,fem_short
	,masc_short
	,neut_short
	,plural_short
FROM adjectives
WHERE word_id = {};
"""

VERB_CONJUGATIONS = """
-- verb (conjugations + aspect)
SELECT
	"aspect"
	,"1st_per_sing"
    ,"2nd_per_sing"
	,"3rd_per_sing"
	,"1st_per_pl"
	,"2nd_per_pl"
	,"3rd_per_pl"
	,"past_m"
	,"past_f"
	,"past_n"
	,"past_pl"
	,"actv_part"
	,"pass_part"
	,"actv_past_part"
	,"pass_past_part"
	,"gerund"
	,"impr"
	,"impr_pl"
FROM conjugations
WHERE word_id = {};
"""

ASPECTUAL_PAIRS = """
-- verb (aspectual pair)
SELECT
	verb_pairs.imp_word_id
	,w1.accent "imp_accent"
	,verb_pairs.pfv_word_id
	,w2.accent "pfv_accent"
FROM words w1
LEFT JOIN verb_pairs
ON w1.id = verb_pairs.imp_word_id
LEFT JOIN words w2
ON w2.id = verb_pairs.pfv_word_id
WHERE {} IN (verb_pairs.imp_word_id, verb_pairs.pfv_word_id);
"""

NOUN_DECLENSIONS = """
-- noun (declensions)
SELECT
	gender
	,animate
	,indeclinable
	,nom
	,acc
	,prep
	,gen
	,dat
	,inst
	,nom_pl
	,acc_pl
	,prep_pl
	,gen_pl
	,dat_pl
	,inst_pl
FROM nouns
WHERE word_id = {};
"""

EXAMPLE_SENTENCES = """
-- example sentences
SELECT
	sentence "rus"
	,sentence_translations."translation" "eng"
	,word_to_sentence.exact_match
FROM words
INNER JOIN word_to_sentence
ON words.id = word_to_sentence.word_id
INNER JOIN sentences
ON word_to_sentence.sentence_id = sentences.sentence_id
INNER JOIN sentence_translations
ON sentences.sentence_id = sentence_translations.sentence_id
WHERE words.id = {}
ORDER BY exact_match DESC;
"""
