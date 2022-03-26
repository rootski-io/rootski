"""Description of the source language and target language."""

import os
import pandas as pd
from random import sample

import torch
from torchtext import vocab
from torchtext.vocab import Vocab
from colorama import Fore
from torch.utils.data import Dataset, Sampler

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
        return [
            beginning[tag]] + [middle[tag]] * (len(morpheme) - 2) + [ending[tag]
        ]

    translation = []
    for morpheme, tag in morpheme_pairs:
        translation += translate_morpheme(morpheme, tag)

    return translation


def add_eos_sos_tokens(sequence: list, start_tkn=START_OF_WORD_TOKEN, 
    end_tkn=END_OF_WORD_TOKEN):
    """Wrap the sequence in the <start> and <end> tokens."""
    return [start_tkn] + sequence + [end_tkn]


def pad_sequence(sequence: list, max_seq_len: int, pad_tkn: str=PADDING_TOKEN):
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


def sequence_stoi(seq: list, vocab: Vocab):
    """Convert string to int given a Vocab object"""
    return vocab(seq)


def sequence_itos(seq: list, vocab: Vocab):
    """Convert string to int given a Vocab object"""
    return [vocab.get_itos()[item] for item in seq]


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


def tokenize_trg(raw_breakdown):
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


class MorphemeDataset(Dataset):
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
        trg_vocab_override=None,
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
            trg_vocab_override (torchtext.data.field.Field, optional): complete
                vocabulary constructed from another data file.
                If None, this is generated when the dataset is initialized.
        """
        self.pad_tkn = pad_tkn
        self.unk_tkn = unk_tkn
        self.start_tkn = start_tkn
        self.end_tkn = end_tkn
        self.src_vocab = src_vocab_override  # cyrillic vocab
        self.trg_vocab = trg_vocab_override  # morpheme-position vocab

        self.load_process_data(file_path, file_sep, file_header)
        self.src_vocab = vocab.build_vocab_from_iterator(
            self.data.source.values.flatten(),
            # specials=["<pad>","<start>","<end>","<?>"]
        )
        self.trg_vocab = vocab.build_vocab_from_iterator(
            self.data.target.values.flatten(),
            # specials=["<pad>","<start>","<end>","<?>"]
        )

    def load_process_data(self, file_path, file_sep, file_header):
        """Load and process the data from the given file."""
        # initializes self.data as a dataframe
        data = pd.read_csv(file_path, sep=file_sep, header=file_header)

        src = data.iloc[:, 0].apply(tokenize_src)
        trg = data.iloc[:, 0].apply(tokenize_trg)

        src = src.apply(add_eos_sos_tokens, args=(self.start_tkn, self.end_tkn))
        trg = trg.apply(add_eos_sos_tokens, args=(self.start_tkn, self.end_tkn))

        max_seq_len = 0
        for src_seq in src:
            if len(src_seq) > max_seq_len:
                max_seq_len = len(src_seq)

        src = src.apply(pad_sequence, args=(max_seq_len, self.pad_tkn))
        trg = trg.apply(pad_sequence, args=(max_seq_len, self.pad_tkn))

        self.data = pd.DataFrame(data={"source": src, "target": trg})

    def __getitem__(self, idx: int):
        """Retreive one item from the data set."""
        return self.data.loc[idx, "source"], self.data.loc[idx, "target"]

    def __len__(self):
        """Get number of items in data set."""
        return self.data.shape[0]

    def src_stoi(self, seq):
        """Get int repr of a sequence."""
        return self.src_vocab(seq)

    def trg_stoi(self, seq):
        """Get int repr of a sequence."""
        return self.trg_vocab(seq)
    
    def make_sampler(self, max_batch_size, shuffle=True):
        """Returns an iterator that iterates over the dataset to
        produce (src, trg) batches where the trg sequences are all
        of equal length. The batches may be of any length between
        1 and :max_batch_size:"""
        return MorphemeSamplerIterator(self.data, max_batch_size, shuffle)
    
    @staticmethod
    def make_collate_batch_fn(src_vocab, trg_vocab, src_pad_tkn, trg_pad_tkn,
        human_readable=False):
        """Prepare a batch collating function that can take a list of sequences
        returned by MorphemeDataset.__getitem__ and shape them into tensors for
        training.

        Args:
            src_vocab (torchtext.data.field.Field): the src_vocab attribute of
                a MorphemeDataset
            trg_vocab (torchtext.data.field.Field): the src_vocab attribute of
                a MorphemeDataset
            src_pad_tkn  (str): the <padding> token used for the source language
            trg_pad_tkn  (str): the <padding> token used for the target language
            human_readable (bool): if True, return the batch as a dataframe of
                string tokenized sequences

        Returns:
            func(list) -> pd.DataFrame: if human_readable, the batch will be a
                dataframe of padded, string tokenized sequences with columns
                "source" and "target"
            func(list) -> Tensor, Tensor: if !human_readable, the batch will be
                two tensors:
                src sequences: shape [N, s] where N is the number of sequences
                    to train on and s is the longest source sequence length for
                    this particular batch
                trg sequences: shape [N, t] where N is the number of sequences
                    to train on and t is the longest target sequence length for
                    this particular batch
        """

        def collate_sequence_batch_fn(sequences: list):
            """Handle a batch of sequences taken from the data loader. Assume
            that the dataloader was instantiated with batch_size=N.
            This function prepares the batch of (src, trg) sequence tuples in
            the following way:

            1. discovers the "max sequence length" of all the expanded sequences
                from this batch
            2. pads each sequence up to the "max sequence length" for the batch
            3. converts the tokenized sequences to indices
            4. creates a src and trg

            Args:
                sequences list: A list containing N (batch size) items which are
                    the return type of MorphemeDataset.__getitem__. Since that
                    function returns tuples of the form
                    (src_sequence, trg_sequence), we will deal with them here.
            """

            sequences_df = pd.DataFrame(sequences, columns=["source", "target"])

            # convert the string token sequences to index sequences
            sequences_df["source"] = sequences_df["source"].apply(
                src_vocab
            )
            sequences_df["target"] = sequences_df["target"].apply(
                trg_vocab
            )

            # convert the dataframes to tensors
            src = torch.Tensor(sequences_df.source.to_list()).long()  # (N, s)
            trg = torch.Tensor(sequences_df.target.to_list()).long()  # (N, t)

            return src, trg

        return collate_sequence_batch_fn


class MorphemeSamplerIterator(Sampler):
    def __init__(self, data: pd.DataFrame, max_batch_size: int, shuffle=True):
        """Manages iteration through a MorphemeDataset. A DataLoader
        will get an iterator from this class that will return batches of indices
        from which to create batches from the MorphemeDataset.

        Args:
            data (pd.DataFrame): the internal dataframe of a MorphemeDataset.
                It must have a "target_len" column--which is the length of the
                target sequence for the given row. The indices generated by this
                class are indices of this dataframe. The batches of indices
                returned by the iterator will ALWAYS correspond to (src, trg)
                pairs where the trg's have the same length.
            max_batch_size (int): The sampler will *try* to return lists of
                length :max_batch_size: of indices corresponding to training
                examples in a MorphemeDataset.
                If there are only S samples left of
        """
        self.data = data
        target_len = data.target.apply(len)
        self.data['target_len'] = target_len
        self.max_batch_size = max_batch_size
        self.shuffle = shuffle

    @staticmethod
    def subsample(_set, num_samples: int, shuffle: bool):
        """Helper function for retrieving subsamples of a :_set:
        Args:
            _set         (set): population of elements to draw a sample from
            num_samples  (int): returned set will have
                min(len(_set), num_samples) elements
            shuffle     (bool): whether or not batches should be randomly or 
                sequentially drawn
        Returns:
            set: sample taken from :_set:
        """
        num_samples = min(len(_set), num_samples)
        samples = {}
        if shuffle:
            samples = sample(_set, num_samples)
        else:
            # take the first num_samples elements of :_set:
            samples = list(_set)[:num_samples]
        return set(samples)

    def reset(self):
        target_lengths = list(set(self.data.target_len.to_list()))

        # get a dict of the form 
        # { target_seq_length : indices of trg examples of that length }
        tgt_len_to_indices = {
            tgt_len: set(
                self.data[self.data.target_len == tgt_len].index.to_list()
            )
            for tgt_len in target_lengths
        }
        self.tgt_len_to_indices = tgt_len_to_indices

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        self.reset()
        return self

    def __next__(self):
        "Return a list of integers representing a batch of indices"
        # if there are no target lengths left, 
        # reset iterator (meaning the dictionary)
        if len(self.tgt_len_to_indices) == 0:
            self.reset()

        tgt_len = -1
        if self.shuffle:
            # randomly choose one of the remaining target lengths
            tgt_len = sample(self.tgt_len_to_indices.keys(), 1)[0]
        else:
            # choose the lowest of the remaining target lengths
            tgt_len = min(self.tgt_len_to_indices.keys())

        # get a batch of indices of size ≤ self.max_batch_size
        batch: set = MorphemeSamplerIterator.subsample(
            self.tgt_len_to_indices[tgt_len], self.max_batch_size, self.shuffle
        )

        # remove that batch from the dictionary
        self.tgt_len_to_indices[tgt_len] -= batch

        # if the target length has no indices left, 
        # remove it from the dictionary
        if len(self.tgt_len_to_indices[tgt_len]) == 0:
            self.tgt_len_to_indices.pop(tgt_len)

        # return the batch of indices as a list
        return list(batch)


if __name__ == "__main__":

    data_set = MorphemeDataset(DATA_DIR + TRAINING_DATA_FILENAME)
    print(len(data_set.src_vocab))
