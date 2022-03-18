#!/bin/bash

# this variable must be manually set to point at the rootski master data folder
DATA_MASTER_DIR="/Users/eric/Desktop/rootski/data/russian/master"

# directory containing this script
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRG_DATA_DIR="$THIS_DIR/data"
DEFINITIONS_DIR="../Definitions"
EXAMPLE_SENTENCES_DIR="../Example Sentences"

DATA_FILES=(
    "adjectives.csv"
    "breakdowns.csv"
    "../clean_frequencies.csv"
    "conjugations.csv"
    "declensions.csv"
    "$DEFINITIONS_DIR/definition_contents.csv"
    "$DEFINITIONS_DIR/definition_examples.csv"
    "$DEFINITIONS_DIR/definitions.csv"
    "../family_meanings_v1.csv"
    "morphemes_v3.csv"
    "nouns.csv"
    "$EXAMPLE_SENTENCES_DIR/sentences.csv"
    "$EXAMPLE_SENTENCES_DIR/translations.csv"
    "verb_pairs.csv"
    "$DEFINITIONS_DIR/word_defs.csv"
    "$EXAMPLE_SENTENCES_DIR/word_to_sentence.csv"
    "../pystardict/Eric/word_types.csv"
    "words.csv"
)

for ((i = 0; i < ${#DATA_FILES[@]}; i++))
do
    DATA_FILE="$DATA_MASTER_DIR/${DATA_FILES[$i]}"
    cp "$DATA_FILE" "$TRG_DATA_DIR/initial_data" \
        || echo "[rootski] Error: could not find file at path $DATA_FILE"
done

# rename breakdowns.csv to be processed by gather_data.py
mv "$DATA_MASTER_DIR/breakdowns.csv" "$DATA_MASTER_DIR/breakdowns-raw.csv"
