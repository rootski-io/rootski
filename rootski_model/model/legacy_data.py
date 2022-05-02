"""
Description of the source language and target language
"""

import os
from random import sample

import pandas as pd
import torch
import torchtext
from colorama import Fore
from torch.utils.data import Dataset, Sampler
from torchtext.data import Field

#####################
# --- Constants --- #
#####################

PADDING_TOKEN = "_"
START_OF_WORD_TOKEN = "<start>"
END_OF_WORD_TOKEN = "<end>"
UNKNOWN_TOKEN = "<?>"

DATA_DIR = "/Users/eric/repos/insidesales/ds/transformer/data/"
TRAINING_DATA_FILENAME = "test_clean_double.tsv"
TESTING_DATA_FILENAME = "test_clean_double.tsv"
TRAINING_DATA_PATH = os.path.join(DATA_DIR, TRAINING_DATA_FILENAME)
TESTING_DATA_PATH = os.path.join(DATA_DIR, TESTING_DATA_FILENAME)
DATA_FILE_FORMAT = "tsv"

#########################################################
# --- Helper Functions for Data Preprocessing Utils --- #
#########################################################


def breakdown_from_raw(breakdown):
    """
    Parses raw breakdown strings in the train/test data to lists of "morpheme pairs"

    Raw brakdowns in the training set have the following format:
        "morpheme0:tag0/morpheme1:tag1/.../morphemeN:tagN"

    This function parses the :breakdown: from that form into a list of tuples:
        [("morpheme0", "tag0"), ..., ("morphemeN", "tagN")]

    Example:
        "при:prefix/каз:root/ать:suffix" -> [("при", "prefix"), ("каз", "root"), ("ать", "suffix")]

    Args:
        breakdown (str): raw breakdown string from training/test data files as described above

    Returns:
        list[str]: a "morpheme_pairs" list as described above
    """
    return [tuple(pair.split(":")) for pair in breakdown.split("/")]


def print_word(morpheme_pairs: list):
    """Color code a list of :morpheme_pairs: by the morpheme tag and print
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
    """
    Translate source language (russian characters) into
    target language (morpheme tags)

    @param
        morpheme_pairs (list): word represented as a list of morphemes
            ex: [("при", "prefix"), ("каз", "root"), ("ать", "suffix")]

    @return
        target language representation
        ex: ["<BP>", "<MP>", "<EP>", "<BR>", "<MR>", "<ER>", "<BS>", "<MS>", "<ES>"]
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

    ending = {"root": "<ER>", "prefix": "<EP>", "suffix": "<ES>"}  # end root  # end prefix  # end suffix

    single = {
        "root": "<SR>",  # singleton root
        "prefix": "<SP>",  # singleton prefix
        "suffix": "<SS>",  # singleton suffix
        "link": "<L>",  # link (link is always singleton)
    }

    def translate_morpheme(morpheme, tag):
        """Given a :morpheme: and :tag: return a list of words in the morpheme target language
        from the morpheme.

        Examples:
            ("каз", "root")       -> ["<BR>", "<MR>", "<ER>"]
            ("blah", "<unknown>") -> ["<?>", "<?>", "<?>", "<?>"]

        Args:
            morpheme (str): should be a morpheme, but can be any string
            tag      (str): one of ["root", "prefix", "suffix", "link", "<unknown>"]

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


####################################
# --- Data Preprocessing Utils --- #
####################################


def tokenize_src(raw_breakdown):
    """
    This function concatenates the morphemes in the :raw_breakdown: and
    returns a list of cyrillic characters (tokens of the source language)

    Example:
        "при:prefix/каз:root/ать:suffix" -> ["п","р","и","к","а","з","а","т","ь"]
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
        "при:prefix/каз:root/ать:suffix" -> ["<BP>","<MP>","<EP>","<BR>","<MR>","<ER>","<BS>","<MS>","<ES>"]
    """
    # parse line into [(morpheme, tag), ...] list
    morpheme_pairs = breakdown_from_raw(raw_breakdown)

    return to_target(morpheme_pairs)


class MorphemeDataset(Dataset):
    def __init__(
        self,
        data_file_path,
        file_sep="\t",
        file_format=DATA_FILE_FORMAT,
        pad_tkn=PADDING_TOKEN,
        unk_tkn=UNKNOWN_TOKEN,
        start_tkn=START_OF_WORD_TOKEN,
        end_tkn=END_OF_WORD_TOKEN,
        src_vocab_override=None,
        trg_vocab_override=None,
    ):
        """This dataset class is used for parsing and loading the russian morpheme
        data csv files. Rows from the data :data_file_path: are parsed the following way:

        "при:prefix/каз:root/ать:suffix" ->
            source: ["<start>","п","р","и","к","а","з","а","т","ь","<end>","<pad>","<pad>","<pad>", ... up to :max_seq_len:]
            target: ["<start>","<BP>","<MP>","<EP>","<BR>","<MR>","<ER>","<BS>","<MS>","<ES>","<end>","<pad>","<pad>","<pad>", ... up to :max_seq_len:]

        Args:
            data_file_path (str): path to a russian morpheme sequence
                data file for training, testing, or validation
            file_sep    (str, optional): separator for the data file format. Defaults to "\t".
            pad_tkn     (str, optional): token in cyrillic and morphem-pos languages for padding. Defaults to PADDING_TOKEN.
            unk_tkn     (str, optional): token in cyrillic and morphem-pos languages for unknown. Defaults to UNKNOWN_TOKEN.
            start_tkn   (str, optional): token in cyrillic and morphem-pos languages for start of sequence. Defaults to START_OF_WORD_TOKEN.
            end_tkn     (str, optional): token in cyrillic and morphem-pos languages for end of sequence. Defaults to END_OF_WORD_TOKEN.
            src_vocab_override     (torchtext.data.field.Field, optional): complete vocabulary constructed from another data file.
                If None, this is generated when the dataset is initialized.
            trg_vocab_override (torchtext.data.field.Field, optional): complete vocabulary constructed from another data file.
                If None, this is generated when the dataset is initialized.
        """
        self.pad_tkn = pad_tkn
        self.unk_tkn = unk_tkn
        self.start_tkn = start_tkn
        self.end_tkn = end_tkn
        self.src_vocab = src_vocab_override  # cyrillic vocab
        self.trg_vocab = trg_vocab_override  # morpheme-position vocab

        self.tokenize_data(data_file_path, file_format)  # initializes self.data as a dataframe
        self.data = MorphemeDataset.build_partial_target_sequences_from_df(self.data)
        self.data = self.data.sort_values("target_len").reset_index(drop=True)

    def tokenize_data(self, data_file_path, file_format):
        """Initialize three class attributes
        (1) src_vocab     - Field.vocab object constructed from the data file if not overridden
        (2) trg_vocab - Field.vocab object constructed from the data file if not overridden
        (3) data - a pandas DataFrame containing the tokenized data
        """
        # define tokenizers to parse fields in the train/test datasets
        CYRILLIC = Field(
            sequential=True,
            tokenize=tokenize_src,
            unk_token=UNKNOWN_TOKEN,
            pad_token=PADDING_TOKEN,
            init_token=START_OF_WORD_TOKEN,
            eos_token=END_OF_WORD_TOKEN,
        )
        MORPHEME_POS = Field(
            sequential=True,
            tokenize=tokenize_tgt,
            unk_token=UNKNOWN_TOKEN,
            pad_token=PADDING_TOKEN,
            init_token=START_OF_WORD_TOKEN,
            eos_token=END_OF_WORD_TOKEN,
        )

        # read and tokenize data file to sequences of the form ["a", "b", "c"]
        data = torchtext.data.TabularDataset(
            path=data_file_path,
            format=file_format,
            skip_header=True,
            fields=[("source", CYRILLIC), ("target", MORPHEME_POS)],
        )

        # build the vocabulary from the data
        CYRILLIC.build_vocab(data)
        MORPHEME_POS.build_vocab(data)
        if not self.src_vocab:
            self.src_vocab = CYRILLIC
        if not self.trg_vocab:
            self.trg_vocab = MORPHEME_POS

        # convert the dataset to a dataframe with sequence form ["<start>", "a", "b", "c", "<end>"]
        self.data = pd.DataFrame(
            [
                {
                    "source": MorphemeDataset.add_eos_sos_tokens(example.source, self.start_tkn, self.end_tkn),
                    "target": MorphemeDataset.add_eos_sos_tokens(example.target, self.start_tkn, self.end_tkn),
                }
                for example in data.examples
            ]
        )

    @staticmethod
    def expand_sequence_pair(src_seq: list, trg_seq: list):
        """Given an unpadded pair of sequences, create training examples designed
        to help the model learn to predict the full sequence one item at a time.

        Example:
            Input:
                :src_seq:                             :trg_seq:
                ["<start>", "a", "b", "c", "<end>"]   ["<start>", "x", "y", "<end>"]

            Output (a list of dicts with the following key value pairs):
                "source"                              "target"                        "target_len"
                ["<start>", "a", "b", "c", "<end>"]   ["<start>", "x"]                2             dict 0
                ["<start>", "a", "b", "c", "<end>"]   ["<start>", "x", "y"]           3             dict 1
                ["<start>", "a", "b", "c", "<end>"]   ["<start>", "x", "y", "<end>"]  4             dict 2

        Args:
            src_seq list[str]: A tokenized source sequence
            trg_seq list[str]: The corresponding tokenized target sequence
            min_trg_length (int, optional): The minimum length of an target sequence fragment.
                Defaults to 2.

        Returns:
            list[dict]: dictionaries representing the rows shows in the example
        """
        expanded_seq_pair_rows = []
        for i in range(1, len(trg_seq)):  # note, the index starts at 2
            expanded_seq_pair_rows.append(
                {  # because each trg training example must at least
                    "source": src_seq,  # have the <start> token and one other.
                    "target": trg_seq[: i + 1],
                    "target_len": i + 1,
                }
            )
        return expanded_seq_pair_rows

    @staticmethod
    def build_partial_target_sequences_from_df(src_trg_seq_df: pd.DataFrame):
        """Expand the src, trg sequence pairs for an entire dataset as described
        in the MorphemeDataset.expand_sequence_pair function

        Args:
            src_trg_seq_df (pd.DataFrame): a dataframe with columns "source" and "target"
                corresponding to tokenized sequences. The input sequences should have no
                <padding> tokens.

        Returns:
            pd.DataFrame: DataFrame of expanded sequence pairs with columns "source" and "target".
        """
        global expanded_sequence_rows
        expanded_sequence_rows = []

        def get_expanded_sequence_rows(src_trg_seq_dict):
            "Helper function to expand a row or dictionary to a list of expanded src, trg pairs"
            global expanded_sequence_rows
            expanded_sequence_rows
            src_seq, trg_seq = src_trg_seq_dict["source"], src_trg_seq_dict["target"]
            expanded_sequence_rows += MorphemeDataset.expand_sequence_pair(src_seq, trg_seq)

        # populate the expanded_sequence_rows list by applying
        # the helper function to all of the src, trg pairs
        src_trg_seq_df.apply(get_expanded_sequence_rows, axis=1)

        return pd.DataFrame(expanded_sequence_rows)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        """Retrieve padded source and target sequences from the desired :index: in the dataset

        Args:
            index (int): index of the sequence to retrieve from the dataset; this index
                should be line_number - 1 where line_number is the the line in the csv/tsv
                file that the data was originally read from

        Return:
            list: a tokenized source sequence (still string tokens)
            list: [1, max sequence length] the trg sentence encoded as a tensor of word indices
        """
        row = self.data.iloc[index]
        src = row["source"]
        trg = row["target"]
        return src, trg

    @staticmethod
    def add_eos_sos_tokens(sequence: list, start_tkn, end_tkn):
        # wrap the sequence in the <start> and <end> tokens
        return [start_tkn] + sequence + [end_tkn]

    @staticmethod
    def pad_sequence(sequence: list, max_seq_len: int, pad_tkn: str):
        """
        Wraps the input :sequence: with <start> and <end> tokens and pads it to max length

        Example:
            Input:  ["<start>", "a", "b", "c", "<end>"]
            Output: ["<start>", "a", "b", "c", "<end>", "<pad>", "<pad>", "<pad>", ..., up to max sequence length]
        """
        # pad the sequence with <padding> tokens until it is the standard fixed sequence length
        padding_length = max_seq_len - len(sequence)
        padded_sequence = sequence + [pad_tkn] * padding_length
        return padded_sequence

    @staticmethod
    def sequence_stoi(seq: list, vocab: Field):
        """Take a string tokenized sequence and convert them to indices.

        Args:
            seq (list): list of string tokens in the language defined by :vocab:
            vocab (Field): see :seq:

        Returns:
            list[int]: a sequence of token indices from :vocab:
        """
        indexed_seq = [vocab.vocab.stoi[item] for item in seq]
        return indexed_seq

    @staticmethod
    def sequence_itos(seq: list, vocab: Field):
        """Take sequence of vocabulary indices and convert it to a string
        tokenized sequence

        Args:
            seq (list): list of string tokens in the language defined by :vocab:
            vocab (Field): see :seq:
        Returns:
            list[int]: a sequence of token indices from :vocab:
        """
        string_token_sequence = [vocab.vocab.itos[item] for item in seq]
        return string_token_sequence

    @staticmethod
    def make_collate_batch_fn(src_vocab, trg_vocab, src_pad_tkn, trg_pad_tkn, human_readable=False):
        """Prepare a batch collating function that can take a list of sequences
        returned by MorphemeDataset.__getitem__ and shape them into tensors for training.

        Args:
            src_vocab (torchtext.data.field.Field): the src_vocab attribute of a MorphemeDataset
            trg_vocab (torchtext.data.field.Field): the src_vocab attribute of a MorphemeDataset
            src_pad_tkn   (str): the <padding> token used for the source language
            trg_pad_tkn   (str): the <padding> token used for the target language
            human_readable (bool): if True, return the batch as a dataframe of string tokenized sequences

        Returns:
            func(list) -> pd.DataFrame: if human_readable, the batch will be a dataframe of padded, string
                tokenized sequences with columns "source" and "target"
            func(list) -> Tensor, Tensor: if !human_readable, the batch will be two tensors:
                src sequences: shape [N, s] where N is the number of sequences to train on and s is the longest
                               source sequence length for this particular batch
                trg sequences: shape [N, t] where N is the number of sequences to train on and t is the longest
                               target sequence length for this particular batch
        """

        def collate_sequence_batch_fn(sequences: list):
            """Handle a batch of sequences taken from the data loader. Assume that the dataloader
            was instantiated with batch_size=N. This function prepares the batch of (src, trg) sequence
            tuples in the following way:

            1. discovers the "max sequence length" of all the expanded sequences from this batch
            2. pads each sequence up to the "max sequence length" for the batch
            3. converts the tokenized sequences to indices
            4. creates a src and trg

            Args:
                sequences list: A list containing N (batch size) items which are the
                    return type of MorphemeDataset.__getitem__. Since that function returns tuples of the
                    form (src_sequence, trg_sequence), we will deal with them here.
            """
            # find the max lengths of the src and trg sequences
            max_src_seq_len, max_trg_seq_len = 0, 0
            for src_seq, trg_seq in sequences:
                # update the max lengths if either of these sequences are the longest so far
                if len(src_seq) > max_src_seq_len:
                    max_src_seq_len = len(src_seq)
                if len(trg_seq) > max_trg_seq_len:
                    max_trg_seq_len = len(trg_seq)

            sequences_df = pd.DataFrame(sequences, columns=["source", "target"])

            # pad the sequences with their <padding> tokens
            sequences_df["source"] = sequences_df["source"].apply(
                lambda seq: MorphemeDataset.pad_sequence(seq, max_src_seq_len, src_pad_tkn)
            )
            sequences_df["target"] = sequences_df["target"].apply(
                lambda seq: MorphemeDataset.pad_sequence(seq, max_trg_seq_len, trg_pad_tkn)
            )

            # if desired, return the string tokenized dataframe
            if human_readable:
                return sequences_df

            # convert the string token sequences to index sequences
            sequences_df["source"] = sequences_df["source"].apply(
                lambda seq: MorphemeDataset.sequence_stoi(seq, src_vocab)
            )
            sequences_df["target"] = sequences_df["target"].apply(
                lambda seq: MorphemeDataset.sequence_stoi(seq, trg_vocab)
            )

            # convert the dataframes to tensors
            src = torch.Tensor(sequences_df.source.to_list()).long()  # (N, s)
            trg = torch.Tensor(sequences_df.target.to_list()).long()  # (N, t)

            return src, trg

        return collate_sequence_batch_fn

    def make_sampler(self, max_batch_size, shuffle=True):
        """Returns an iterator that iterates over the dataset to
        produce (src, trg) batches where the trg sequences are all
        of equal length. The batches may be of any length between
        1 and :max_batch_size:"""
        return MorphemeSamplerIterator(self.data, max_batch_size, shuffle)


class MorphemeSamplerIterator(Sampler):
    def __init__(self, data: pd.DataFrame, max_batch_size: int, shuffle=True):
        """Manages iteration through a MorphemeDataset. A DataLoader
        will get an iterator from this class that will return batches of indices
        from which to create batches from the MorphemeDataset.

        Args:
            data (pd.DataFrame): the internal dataframe of a MorphemeDataset.
                It must have a "target_len" column--which is the length of the target
                sequence for the given row. The indices generated by this class are
                indices of this dataframe. The batches of indices returned by the iterator
                will ALWAYS correspond to (src, trg) pairs where the trg's have the
                same length.
            max_batch_size (int): The sampler will *try* to return lists of length :max_batch_size:
                of indices corresponding to training examples in a MorphemeDataset. If there are
                only S samples left of
        """
        self.data = data
        self.max_batch_size = max_batch_size
        self.shuffle = shuffle

    @staticmethod
    def subsample(_set, num_samples: int, shuffle: bool):
        """Helper function for retrieving subsamples of a :_set:
        Args:
            _set         (set): population of elements to draw a sample from
            num_samples  (int): returned set will have min( len(_set), num_samples ) elements
            shuffle     (bool): whether or not batches should be randomly or sequentially drawn
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

        # get a dict of the form { target_seq_length : indices of trg examples of that length }
        tgt_len_to_indices = {
            tgt_len: set(self.data[self.data.target_len == tgt_len].index.to_list())
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
        # if there are no target lengths left, reset iterator (meaning the dictionary)
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

        # if the target length has no indices left, remove it from the dictionary
        if len(self.tgt_len_to_indices[tgt_len]) == 0:
            self.tgt_len_to_indices.pop(tgt_len)

        # return the batch of indices as a list
        return list(batch)
