import math

import torch
from torch import Tensor, nn
from torch.autograd import Variable

MODEL_CHECKPOINT_FILE_PATH = "/Users/eric/repos/insidesales/ds/transformer/model/model_checkpoint.pt"

# Transformer Hyperparameters (defaults to those recommended in the paper)
EMBEDDING_DIM = 6  # d_model
NUMBER_OF_HEADS = 2  # h
NUM_ENCODER_LAYERS = 6  # N
NUM_DECODER_LAYERS = 6  # N
DIM_FEEDFORWARD = 2018
DROPOUT_RATIO = 0.1

# training parameters
MAX_SRC_SEQUENCE_LENGTH = 40
MAX_TRG_SEQUENCE_LENGTH = 40
BATCH_SIZE = 10  # number of sequences to train on per optimization step


class PositionalEncoder(nn.Module):
    def __init__(self, d_model, max_seq_len, dropout=0.1):
        """Encodes absolute and relative position information into each element of a sequence.

        This is done by adding a special constant matrix to the word embeddings matrix representing
        a sequence of words. In theory, this allows the network to learn approximately how close a word
        is to the beginning or end of a sentence.

        The exact matrix addition is defined here:

        let scaled_pos(embedding_pos) = embedding_pos * -log(10,000) / d_model
        ^^^ effectively a scaled f(x) = -log(x) so that the range is (0, 1]

        [(word 0, embed 0), (word 0, embed 1), ...]     [sin( 0 * scaled_pos(0) ), cos( 0 * scaled_pos(0) ), ...]
        [(word 1, embed 0), (word 1, embed 1), ...]  +  [sin( 1 * scaled_pos(1) ), cos( 1 * scaled_pos(1) ), ...]
        [(word 2, embed 0), (word 2, embed 1), ...]     [sin( 2 * scaled_pos(2) ), cos( 2 * scaled_pos(2) ), ...]
        [  ...                                    ]     [ ...                                                   ]

        Args:
            d_model     (int): length of the "word" embeddings (required)
            dropout   (float): proportion of values to dropout from the word embeddings. Defaults to 0.1.
            max_seq_len (int): maximum number of "words" any "sentence" will have. Defaults to 5000.
        """
        super(PositionalEncoder, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        self.d_model = d_model

        # prepare to construct the positional encoding matrix to add to word embeddings
        pos_encoding = torch.zeros(max_seq_len, d_model)

        # [max_seq_len, 1] float matrix counting from 0 to max_seq_len - 1
        position = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)

        # construct a position matrix entries POS[i, j] = i * scaled_pos(j) as in the docstring
        log_scale = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        log_scaled_positions = position * log_scale  # [max_seq_len, d_model]

        # apply sin to the even columns, and cos to the odd columns of POS
        pos_encoding[:, 0::2] = torch.sin(log_scaled_positions)
        pos_encoding[:, 1::2] = torch.cos(log_scaled_positions)

        # disable gradient descent for the positional encoding matrix; it is a constant
        self.register_buffer("pos_encoding", pos_encoding)

    def forward(self, x) -> Tensor:
        """Performs positional encoding on a batch of sequences whose items
        have been sent to an embedding space. This is done by adding the constant
        2-d positional encoding matrix to each of the 2-d embedded sequence matrices
        in the 3-d input :x:

        Args:
            x (Tensor): [batch size, max sequence length, d_model] the embedded sequences
        Returns:
            Tensor: [batch size, max sequence length, d_model] the positionally encoded embeddings
        """
        max_batch_seq_len = x.size(1)
        # scale up the word meaning embeddings by a positive constant so that meaning outweighs position
        x = x * math.sqrt(self.d_model)
        # left is 3-d, right is 2-d: right is added to each of the pages of left
        x = x + Variable(self.pos_encoding[:max_batch_seq_len, :], requires_grad=False)
        return x


class Transformer(nn.Module):
    def __init__(
        self,
        src_pad_idx,
        trg_pad_idx,
        src_vocab_size,
        trg_vocab_size,
        d_model=EMBEDDING_DIM,
        num_heads=NUMBER_OF_HEADS,
        num_encoder_layers=NUM_ENCODER_LAYERS,
        num_decoder_layers=NUM_DECODER_LAYERS,
        dim_feedforward=DIM_FEEDFORWARD,
        dropout=DROPOUT_RATIO,
        max_src_seq_len=MAX_SRC_SEQUENCE_LENGTH,
        max_trg_seq_len=MAX_TRG_SEQUENCE_LENGTH,
    ):
        """A wrapper class for the official PyTorch implementation of the Transformer model.

        Args:
            src_pad_idx    (int): index of the <padding> token of the source language
            trg_pad_idx    (int): index of the <padding> token of the target language
            src_vocab_size (int): total number of tokens (words) in the source language
            trg_vocab_size (int): total number of tokens (words) in the target language
            d_model            (int, optional): dimension of sequence item embeddings. Defaults to EMBEDDING_DIM.
            num_heads          (int, optional): number of heads used in the Transformer model. Defaults to NUMBER_OF_HEADS.
            num_encoder_layers (int, optional): number of num_encoder_layers used in the Transformer model. Defaults to NUM_ENCODER_LAYERS.
            num_decoder_layers (int, optional): number of num_decoder_layers used in the Transformer model. Defaults to NUM_DECODER_LAYERS.
            dim_feedforward    (int, optional): dimension of the feed forward layer in each Encoder and Decoder layer. Defaults to DIM_FEEDFORWARD.
            dropout            (float, optional): float between 0 and 1; ratio of values that are randomly set to 0
                everywhere dropout is used in the model. This includes the Positional Encoding layers as well as others.
                Defaults to DROPOUT_RATIO.
            max_src_seq_len    (int, optional): max length of a sequence in the source language.
                An upper bound to the number of items that can legally be allowed as input for source sequences.
                Note, that you can actually put shorter sequence lengths into the model without worrying about padding
                them to length :max_src_seq_len: In other words, a batch of source sequences can have shape
                (N, s) where s ≤ S. Where S is :max_src_seq_len: In that case, all of the input sequences in the batch
                must be padded to length s.
                Defaults to MAX_SRC_SEQUENCE_LENGTH.
            max_trg_seq_len    (int, optional): max length of a sequence in the target language.
                The target length is flexible as well, exactly as in :max_src_seq_len:. So if T = :max_trg_seq_len:,
                you can input any batch of target sequences of shape (N, t) where t ≤ T. In this case all target
                sequences in the batch need to be padded to length t.
                Defaults to MAX_TRG_SEQUENCE_LENGTH.
        """
        super(Transformer, self).__init__()

        self.src_pad_idx = src_pad_idx
        self.trg_pad_idx = trg_pad_idx
        self.src_vocab_size = src_vocab_size
        self.trg_vocab_size = trg_vocab_size
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_encoder_layers = num_encoder_layers
        self.num_decoder_layers = num_decoder_layers
        self.dim_feedforward = dim_feedforward
        self.dropout = dropout
        self.max_src_seq_len = max_src_seq_len
        self.max_trg_seq_len = max_trg_seq_len

        # embedding layers to encode sequence item indices from the src and trg languages
        self.src_embedding = nn.Embedding(num_embeddings=src_vocab_size, embedding_dim=d_model)
        self.trg_embedding = nn.Embedding(num_embeddings=trg_vocab_size, embedding_dim=d_model)

        # positional encoders for source and target language embeddings
        self.src_positional_encoder = PositionalEncoder(
            d_model=d_model, dropout=dropout, max_seq_len=max_src_seq_len
        )
        self.trg_positional_encoder = PositionalEncoder(
            d_model=d_model, dropout=dropout, max_seq_len=max_trg_seq_len
        )

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=num_heads,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
        )

        # returns a tensor of shape [batch size, max sequence length, trg vocab size]
        self.trg_embedding_to_trg_vocab = nn.Linear(d_model, trg_vocab_size)

    def make_padding_mask(self, sequences: Tensor, padding_idx: int) -> Tensor:
        """Construct a 2-d tensor to use as a mask over the padding indices for each
        of the input sequences.

        Example:
            Input                            Output
            [[a, b, c,     <pad>, <pad>], -> [[0, 0, 0,    -inf, -inf],  sequence 1
             [x, y, <pad>, <pad>, <pad>]]     [0, 0, -inf, -inf, -inf]]  sequence 2

        Args:
            sequences (Tensor): [batch size, max sequence length] the un-embedded sequences
                                in either the source or target language
            type (int): the index corresponding to the <padding> token in the language
                                that the :sequences: are from.
        Returns:
            Tensor: [batch size, max sequence length] see the example
        """
        # prepare to construct the padding mask
        batch_size, max_seq_len = sequences.shape
        mask = torch.zeros(batch_size, max_seq_len, dtype=torch.float)

        # set the indices in the mask correspanding to <padding> tokens to -inf
        padding_indices = sequences == padding_idx
        mask[padding_indices] = float("-inf")

        return mask

    def make_trg_mask(self, size: int) -> Tensor:
        """Create a 2-d tensor of dimension [size, size] to be used as a mask for the
        decoder layers of the Transformer model.

        The mask is an upper triangular matrix of -inf which will eventually be passed
        into the PyTorch MultiHeadAttention.forward function as :attn_mask:

        >>> Transformer.make_2d_mask(3)
            tensor([[0., -inf, -inf],      word 0 can attend to word 0
                    [0.,  0.,  -inf],      word 1 can attend to word 0 and 1
                    [0.,  0.,   0.]])      word 2 can attend to word 0, 1, and 2

        Args:
            size (int): number of rows and columns in the mask tensor

        Returns:
            Tensor: see previous description
        """
        mask = (torch.triu(torch.ones(size, size)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float("-inf")).masked_fill(mask == 1, float(0.0))
        return mask

    def forward(self, src, trg) -> Tensor:
        """

        Notation:
            N - batch size (number of sequences in a batch)
            S - max source sequence length
            T - max target sequence length
            s - max source sequence length (for this particular batch)
            t - max target sequence length (for this particular batch)
            E - embedding length (d_model)

        Args:
            src (Tensor): [N, S, E] source sequence
            trg (Tensor): [N, T, E] target sequence
        """
        Ns, S = src.shape
        Nt, T = trg.shape
        assert (
            Ns == Nt
        ), f"The number of source sequences ({Ns}) must be equal to the number of target sequences ({Nt})"

        # create padding masks from un-embedded src and trg sequences
        src_padding_mask = self.make_padding_mask(sequences=src, padding_idx=self.src_pad_idx)
        # print("src_padding_mask", src_padding_mask.size())
        trg_padding_mask = self.make_padding_mask(sequences=trg, padding_idx=self.trg_pad_idx)
        # print("trg_padding_mask", trg_padding_mask.size())
        trg_attn_mask = self.make_trg_mask(T)
        # print("trg_attn_mask", trg_attn_mask.size())

        # encode the source sequences
        src = self.src_embedding(src)  # (N, s)    -> (N, s, E)
        # print("embedded src", src.size())
        src = self.src_positional_encoder(src)  # (N, s, E) -> (N, s, E)
        # print("position embedded src", src.size())
        src = src.transpose(0, 1)  # (N, s, E) -> (s, N, E)
        # print("transposed pos emb src", src.size())

        # encode the target sequences
        trg = self.trg_embedding(trg)  # (N, t)    -> (N, t, E)
        # print("embedded trg", trg.size())
        trg = self.trg_positional_encoder(trg)  # (N, t, E) -> (N, t, E)
        # print("position embedded trg", trg.size())
        trg = trg.transpose(0, 1)  # (N, t, E) -> (t, N, E)
        # print("transposed pos emb trg", trg.size())

        # pass them into the transformer (s, N, E), (t, N, E) -> (T, N, E)
        decoded = self.transformer(
            src,
            trg,
            tgt_mask=trg_attn_mask,
            src_key_padding_mask=src_padding_mask,
            tgt_key_padding_mask=trg_padding_mask,
        )
        # print("transformer output", decoded.size())
        decoded = decoded.transpose(0, 1)  # (t, N, E) -> (N, t, E)
        # print("transformer transposed output", decoded.size())

        # transform the decoded "word" embeddings to one scalars
        out = self.trg_embedding_to_trg_vocab(decoded)  # (N, t, E) -> (N, t, Target Vocab Size)
        # print("model output", out.size())

        return out

    def save_model_checkpoint(self, src_vocab, trg_vocab, path=MODEL_CHECKPOINT_FILE_PATH):
        """Save metadata about a model to disk
        Args:
            path (str, optional): location to save a model checkpoint to.
                Defaults to MODEL_CHECKPOINT_FILE_PATH.
        """
        torch.save(
            {
                # artifacts
                "state_dict": self.state_dict(),
                "src_vocab": src_vocab,
                "trg_vocab": trg_vocab,
                # init params
                "src_pad_idx": self.src_pad_idx,
                "trg_pad_idx": self.trg_pad_idx,
                "src_vocab_size": self.src_vocab_size,
                "trg_vocab_size": self.trg_vocab_size,
                "d_model": self.d_model,
                "num_heads": self.num_heads,
                "num_encoder_layers": self.num_encoder_layers,
                "num_decoder_layers": self.num_decoder_layers,
                "dim_feedforward": self.dim_feedforward,
                "dropout": self.dropout,
                "max_src_seq_len": self.max_src_seq_len,
                "max_trg_seq_len": self.max_trg_seq_len,
            },
            path,
        )

    @staticmethod
    def load_model_checkpoint(path=MODEL_CHECKPOINT_FILE_PATH):
        """Load a dictionary with information about the saved model
        Args:
            path (str): file path to the where a model checkpoint
                dict is saved. Defaults to MODEL_CHECKPOINT_FILE_PATH.
        Returns:
            Transformer, Field, Field:
                - Loaded transformer model object
                - source vocab built from the training set the model was trained on
                - target vocab built from the training set the model was trained on
        """
        checkpoint: dict = torch.load(path)
        model = Transformer(
            src_pad_idx=checkpoint["src_pad_idx"],
            trg_pad_idx=checkpoint["trg_pad_idx"],
            src_vocab_size=checkpoint["src_vocab_size"],
            trg_vocab_size=checkpoint["trg_vocab_size"],
            d_model=checkpoint["d_model"],
            num_heads=checkpoint["num_heads"],
            num_encoder_layers=checkpoint["num_encoder_layers"],
            num_decoder_layers=checkpoint["num_decoder_layers"],
            dim_feedforward=checkpoint["dim_feedforward"],
            dropout=checkpoint["dropout"],
            max_src_seq_len=checkpoint["max_src_seq_len"],
            max_trg_seq_len=checkpoint["max_trg_seq_len"],
        )
        return model, checkpoint["src_vocab"], checkpoint["trg_vocab"]
