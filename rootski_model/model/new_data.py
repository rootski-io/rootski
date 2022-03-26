"""Description of the source language and target language."""

import os

import pandas as pd

# import torchtext
from colorama import Fore
from torch.utils.data import Dataset

#####################
# --- Constants --- #
#####################

PADDING_TOKEN = "<pad>"
START_OF_WORD_TOKEN = "<start>"
END_OF_WORD_TOKEN = "<end>"
UNKNOWN_TOKEN = "<?>"

DATA_DIR = "../data/"
TRAINING_DATA_FILENAME = "test_clean.csv"
TESTING_DATA_FILENAME = "test_clean.csv"
TRAINING_DATA_PATH = os.path.join(DATA_DIR, TRAINING_DATA_FILENAME)
TESTING_DATA_PATH = os.path.join(DATA_DIR, TESTING_DATA_FILENAME)
DATA_FILE_FORMAT = "csv"


#########################################################
# --- Helper Functions for Data Preprocessing Utils --- #
#########################################################


def breakdown_from_raw(breakdown):
    """Parse raw breakdown strings in the train/test data to lists of
        "morpheme pairs".

    Raw breakdowns in the training set have the following format:
        "morpheme0:tag0/morpheme1:tag1/.../morphemeN:tagN"

    This function parses the :breakdown: from that form into a list of tuples:
        [("morpheme0", "tag0"), ..., ("morphemeN", "tagN")]

    Example:
        "при:prefix/каз:root/ать:suffix" -> [
            ("при", "prefix"), ("каз", "root"), ("ать", "suffix")
        ]

    Args:
        breakdown (str): raw breakdown string from training/test data
            files as described above

    Returns:
        list[str]: a "morpheme_pairs" list as described above
    """
    return [tuple(pair.split(":")) for pair in breakdown.split("/")]


def print_word(morpheme_pairs: list):
    """
    Color code a list of :morpheme_pairs: by the morpheme tag and print
    as a single "|" separated string
    """
    color_map = {
        "prefix": Fore.GREEN,
        "root": Fore.MAGENTA,
        "suffix": Fore.BLUE,
        "link": Fore.YELLOW,
        "<unknown>": Fore.BLACK,
    }

    result = ""
    for morpheme, tag in morpheme_pairs:
        result += color_map[tag] + morpheme + Fore.BLACK + "|"
    result = result.rstrip("|")

    print(result)


def to_target(morpheme_pairs):
    """Translate source language (russian characters) into
    target language (morpheme tags).

    @param
        morpheme_pairs (list): word represented as a list of morphemes
            ex: [("при", "prefix"), ("каз", "root"), ("ать", "suffix")]

    @return
        target language representation
        ex: [
            "<BP>", "<MP>", "<EP>", "<BR>",
            "<MR>", "<ER>", "<BS>", "<MS>", "<ES>"
        ]
    """

    # target vocabulary
    beginning = {
        "root": "<BR>",  # begin root
        "prefix": "<BP>",  # begin prefix
        "suffix": "<BS>",  # begin suffix
    }

    middle = {
        "root": "<MR>",  # middle root
        "prefix": "<MP>",  # middle prefix
        "suffix": "<MS>",  # middle suffix
    }

    # end root  # end prefix  # end suffix
    ending = {"root": "<ER>", "prefix": "<EP>", "suffix": "<ES>"}

    single = {
        "root": "<SR>",  # singleton root
        "prefix": "<SP>",  # singleton prefix
        "suffix": "<SS>",  # singleton suffix
        "link": "<L>",  # link (link is always singleton)
    }

    def translate_morpheme(morpheme, tag):
        """Given a :morpheme: and :tag: return a list of words in the morpheme
        target language from the morpheme.

        Examples:
            ("каз", "root")       -> ["<BR>", "<MR>", "<ER>"]
            ("blah", "<unknown>") -> ["<?>", "<?>", "<?>", "<?>"]

        Args:
            morpheme (str): should be a morpheme, but can be any string
            tag      (str): one of [
                "root", "prefix", "suffix", "link", "<unknown>"
            ]

        Returns:
            list[str]: see examples
        """
        if tag == "<unknown>":
            return [UNKNOWN_TOKEN] * len(morpheme)

        if len(morpheme) == 1:
            return [single[tag]]

        morpheme[0]
        morpheme[-1]
        return [beginning[tag]] + [middle[tag]] * (len(morpheme) - 2) + [ending[tag]]

    translation = []
    for morpheme, tag in morpheme_pairs:
        translation += translate_morpheme(morpheme, tag)

    return translation


def add_eos_sos_tokens(sequence: list, start_tkn, end_tkn):
    """Wrap the sequence in the <start> and <end> tokens."""
    return [start_tkn] + sequence + [end_tkn]


def pad_sequence(sequence: list, max_seq_len: int, pad_tkn: str):
    """Wrap the input :sequence: with <start> and <end> tokens and pads it to
    max length.

    Example:
        Input:  ["<start>", "a", "b", "c", "<end>"]
        Output: [
            "<start>", "a", "b", "c", "<end>", "<pad>", "<pad>", "<pad>",
             ..., up to max sequence length
            ]
    """
    # pad the sequence with <padding> tokens until it is the standard
    # fixed sequence length
    padding_length = max_seq_len - len(sequence)
    padded_sequence = sequence + [pad_tkn] * padding_length
    return padded_sequence


####################################
# --- Data Preprocessing Utils --- #
####################################


def tokenize_src(raw_breakdown):
    """
    This function concatenates the morphemes in the :raw_breakdown: and
    returns a list of cyrillic characters (tokens of the source language)

    Example:
        "при:prefix/каз:root/ать:suffix" -> [
            "п","р","и","к","а","з","а","т","ь"
        ]
    """
    # parse line into [(morpheme, tag), ...] list
    morpheme_pairs = breakdown_from_raw(raw_breakdown)

    # extract the word
    word = "".join([morpheme for morpheme, _ in morpheme_pairs])

    # return the word as a list of characters
    return list(word)


def tokenize_tgt(raw_breakdown):
    """
    This function concatenates the morpheme tags in the :raw_breakdown: and
    returns a list of part-of-morpheme tags (tokens of the target language)

    Example:
        "при:prefix/каз:root/ать:suffix" -> [
            "<BP>","<MP>","<EP>","<BR>","<MR>","<ER>","<BS>","<MS>","<ES>"
        ]
    """
    # parse line into [(morpheme, tag), ...] list
    morpheme_pairs = breakdown_from_raw(raw_breakdown)

    return to_target(morpheme_pairs)


class MorphemeDatset(Dataset):
    """Create dataset for tokeninzing and managind language data."""

    def __init__(
        self,
        file_path,
        file_sep=",",
        file_header=None,
        file_format=DATA_FILE_FORMAT,
        pad_tkn=PADDING_TOKEN,
        unk_tkn=UNKNOWN_TOKEN,
        start_tkn=START_OF_WORD_TOKEN,
        end_tkn=END_OF_WORD_TOKEN,
        src_vocab_override=None,
        tgt_vocab_override=None,
    ):
        """This dataset class is used for parsing and loading the russian
        morpheme data csv files. Rows from the data :data_file_path: are
        parsed the following way.

        "при:prefix/каз:root/ать:suffix" ->
            source: [
                "<start>","п","р","и","к","а","з","а","т","ь","<end>","<pad>",
                "<pad>","<pad>", ... up to :max_seq_len:
                ]
            target: [
                "<start>","<BP>","<MP>","<EP>","<BR>","<MR>","<ER>","<BS>",
                "<MS>","<ES>","<end>","<pad>","<pad>","<pad>",
                ... up to :max_seq_len:
            ]

        Args:
            data_file_path (str): path to a russian morpheme sequence
                data file for training, testing, or validation
            file_sep    (str, optional): separator for the data file format.
            Defaults to "\t".
            pad_tkn     (str, optional): token in cyrillic and morphem-pos
                languages for padding. Defaults to PADDING_TOKEN.
            unk_tkn     (str, optional): token in cyrillic and morphem-pos
                languages for unknown. Defaults to UNKNOWN_TOKEN.
            start_tkn   (str, optional): token in cyrillic and morphem-pos
                languages for start of sequence. Default: START_OF_WORD_TOKEN.
            end_tkn     (str, optional): token in cyrillic and morphem-pos
                languages for end of sequence. Defaults to END_OF_WORD_TOKEN.
            src_vocab_override     (torchtext.data.field.Field, optional):
                complete vocabulary constructed from another data file.
                If None, this is generated when the dataset is initialized.
            tgt_vocab_override (torchtext.data.field.Field, optional): complete
                vocabulary constructed from another data file.
                If None, this is generated when the dataset is initialized.
        """
        self.pad_tkn = pad_tkn
        self.unk_tkn = unk_tkn
        self.start_tkn = start_tkn
        self.end_tkn = end_tkn
        self.src_vocab = src_vocab_override  # cyrillic vocab
        self.tgt_vocab = tgt_vocab_override  # morpheme-position vocab

        self.load_process_data(file_path, file_sep, file_header)

    def load_process_data(self, file_path, file_sep, file_header):
        """Load and process the data from the given file."""
        # initializes self.data as a dataframe
        data = pd.read_csv(file_path, sep=file_sep, header=file_header)

        src = data.iloc[:, 0].apply(tokenize_src)
        tgt = data.iloc[:, 0].apply(tokenize_tgt)

        src = src.apply(add_eos_sos_tokens, args=(self.start_tkn, self.end_tkn))
        tgt = tgt.apply(add_eos_sos_tokens, args=(self.start_tkn, self.end_tkn))

        max_seq_len = 0
        for src_seq in src:
            if len(src_seq) > max_seq_len:
                max_seq_len = len(src_seq)

        src = src.apply(pad_sequence, args=(max_seq_len, self.pad_tkn))
        tgt = tgt.apply(pad_sequence, args=(max_seq_len, self.pad_tkn))

        self.data = pd.DataFrame(data={"source": src, "target": tgt})

    def __getitem__(self, idx: int):
        """Retreive one item from the data set."""
        return self.data.loc[idx, "source"], self.data.loc[idx, "target"]

    def __len__(self):
        """Get number of items in data set."""
        return self.data.shape[0]


if __name__ == "__main__":

    data_set = MorphemeDatset(DATA_DIR + TRAINING_DATA_FILENAME)
    print(data_set.data.sample(10))
