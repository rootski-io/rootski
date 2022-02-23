import torch
from torch import nn


class SelfAttention(nn.Module):
    def __init__(self, embed_size, heads):
        """A single "head" layer for Multi-Head Attention

        This head attends to 1 :heads:'th of the values in a "word" vector.
        So if the "word" vectors are of :embed_size: 256, and the number of :heads: is 8,
        then this head only addends to an 8th of the "word" vector.

        In this example, the i'th head, attends to the i'th segment of 256 (d_model) // 8 (h) = 32
        entries in the "word" vector:

                               |-------------- 32 entries --------------|
        [ word_0, word_1, ..., word_(i*heads), ..., word_(i*[heads+1]-1), ..., word_255]

        Args:
            embed_size (int): dimension of the "word" embedding vectors (d_model)
            heads      (int): number of attention heads (h)

        TODO Issues:
        - he uses sqrt(d_model) instead of sqrt(d_key)
        - his fc_out layer is d_model x d_model instead of d_model x d_key
        """
        super(SelfAttention, self).__init__()
        self.embed_size = embed_size  # d_model
        self.heads = heads  # h
        assert self.embed_size % self.heads == 0, "embed_size (d_model) must be divisible by heads (h)"
        self.head_dim = self.embed_size // self.heads

        # Q, K, and V
        self.values = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.keys = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.queries = nn.Linear(self.head_dim, self.head_dim, bias=False)

        # fully connected layer: brings the head_dim length vector to length d_model
        self.fc_out = nn.Linear(self.heads * self.head_dim, self.embed_size)

    def forward(self, queries, keys, values, mask=None):
        """
        (1) Compute the attention for the given queries, keys, and values
            Attention(Q, K, V) = softmax( (Q @ K.T)/sqrt(d_k) ) @ V
        (2) fully connected layer

        Args:
            query  (torch.Tensor): Q [batch_size, d_query, d_model]
            keys   (torch.Tensor): K [batch_size, d_key,   d_model]
            values (torch.Tensor): V [batch_size, d_value, d_model]
            mask   (torch.Tensor): [batch_size, sentence_len, sentence_len]
                       Lower triangular matrix that hides words in the output
                       sentence that haven't been translated yet, so the attention
                       can't cheat and base the generated translation on the label translation.
        """
        batch_size = queries.shape[0]  # number of "sentences" in batch

        d_value = values.shape[1]
        d_key = keys.shape[1]
        d_query = queries.shape[1]

        if d_key * self.heads != self.embed_size:
            raise ValueError(
                f"Invalid input shape for values: {values.shape}."
                " d_key = values.size(1) must be equal to (d_model) / (num heads)"
            )

        # reshape the input tensors so we can multiply them against the K, Q, and V weights
        values = values.reshape(batch_size, d_value, self.heads, self.head_dim)
        keys = keys.reshape(batch_size, d_key, self.heads, self.head_dim)
        queries = queries.reshape(batch_size, d_query, self.heads, self.head_dim)

        # send the values, keys, queries through the linear layers
        values = self.values(values)
        keys = self.keys(keys)
        queries = self.queries(queries)

        # batch multiply the input queries with the input keys so that we have
        # one query_len x key_len matrix per head (for each sentence)
        # n - batch_size
        # q - d_query, k - d_key
        # h - number of heads
        # d - head dimension (d_model // h)
        energy = torch.einsum(
            "nqhd,nkhd->nhqk", [queries, keys]
        )  # [batch_size, num heads, d_query, d_key] adding this to trigger darker

        if mask is not None:
            # wherever mask is 0, fill energy with a very negative number
            energy = energy.masked_fill(mask=mask == 0, value=float("-1e20"))

        # attention step 1 -- compute the softmax along the key dimension (the last dimension)
        attention = torch.softmax(energy / (d_key ** 0.5), dim=3)

        # attention step 2 -- batch multiply
        # attention: [batch_size, num heads, d_query, d_key]
        # values:    [batch_size, d_value, num heads, heads dim]
        attention = torch.einsum(
            "nhqk,nkhd->nqhd", [attention, values]
        )  # [batch_size, d_query, num heads, heads dim]

        # now concatenate each of the attention matrices for each word
        attention = attention.reshape(batch_size, d_query, self.heads * self.head_dim)

        out = self.fc_out(attention)
        return out


class TransformerBlock(nn.Module):
    def __init__(self, embed_size, heads, dropout, forward_expansion):
        """[summary]

        Args:
            embed_size        (int): [description]
            heads             (int): [description]
            dropout           (int): [description]
            forward_expansion (int): [description]

        TODO Issues:
        - he just uses one head for his attention in his Transformer block
        """
        super(TransformerBlock, self).__init__()
        self.attention = SelfAttention(embed_size, heads)

        # Note, LayerNorm normalizes for each individual sentence, rather than accross a batch
        self.norm1 = nn.LayerNorm(embed_size)
        self.norm2 = nn.LayerNorm(embed_size)
        self.feed_forward = nn.Sequential(
            nn.Linear(embed_size, forward_expansion * embed_size),
            nn.ReLU(),
            nn.Linear(forward_expansion * embed_size, embed_size),
        )
        self.dropout = nn.Dropout(dropout)

    def forward(self, queries, keys, values, mask=None):
        """

        Args:
            value (): [description]
            key   (): [description]
            query (): [description]
            mask  (): [description]
        """

        # Multi-Head Attention TODO this is just single headed attention...
        attention = self.attention(queries, keys, values, mask)
        # Add & Norm
        x = self.norm1(attention + queries)
        x = self.dropout(x)

        # Feed Forward
        forward = self.feed_forward(x)
        # Add & Norm
        x = self.norm1(forward + x)
        x = self.dropout(x)

        return x


class Encoder(nn.Module):
    def __init__(
        self, src_vocab_size, embed_size, num_layers, heads, device, forward_expansion, dropout, max_length
    ):
        """

        Args:
            src_vocab_size    (): [description]
            embed_size        (): [description]
            num_layers        (): [description]
            heads             (): [description]
            device            (): [description]
            forward_expansion (): [description]
            dropout           (): [description]
            max_length        (): [description]

        TODO Issues:
        - his positional encoder doesn't use sin!
        """
        super(Encoder, self).__init__()

        self.src_vocab_size = src_vocab_size
        self.embed_size = embed_size
        self.num_layers = num_layers
        self.heads = heads
        self.device = device
        self.forward_expansion = forward_expansion
        self.dropout = dropout
        self.max_length = max_length

        self.word_embedding = nn.Embedding(src_vocab_size, embed_size)
        self.position_embedding = nn.Embedding(max_length, embed_size)

        self.layers = nn.ModuleList(
            [
                TransformerBlock(
                    embed_size=embed_size, heads=heads, dropout=dropout, forward_expansion=forward_expansion
                )
                for _ in range(num_layers)
            ]
        )
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x, mask):
        """[summary]

        Args:
            x    ([type]): [description]
            mask ([type]): [description]
        """
        batch_size, sentence_len = x.shape
        positions = (
            # index the words from 0 to sentence_length - 1
            torch.arange(0, sentence_len)
            # duplicate that index array once per sentence
            .expand(batch_size, sentence_len)
            # send the index matrix to cpu or gpu
            .to(self.device)
        )

        x = self.word_embedding(x) + self.position_embedding(x)
        x = self.dropout(x)
        for layer in self.layers:
            # in the Encoder, all of Q, K, and V are the positionally encoded sentence
            x = layer(queries=x, keys=x, values=x, mask=mask)

        return x


class DecoderBlock(nn.Module):
    def __init__(self, embed_size, heads, forward_expansion, dropout, device):
        """[summary]

        Args:
            embed_size        ([type]): [description]
            heads             ([type]): [description]
            forward_expansion ([type]): [description]
            dropout           ([type]): [description]
            device            ([type]): [description]
        """
        super(DecoderBlock, self).__init__()
        self.attention = SelfAttention(embed_size, heads)
        self.norm = nn.LayerNorm(embed_size)
        self.transformer_block = TransformerBlock(embed_size, heads, dropout, forward_expansion)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, value, key, src_mask, trg_mask):

        # Masked Multi-Head Attention
        attention = self.attention(queries=x, keys=x, values=x, mask=trg_mask)
        # Add & Norm
        query = self.norm(attention + x)
        query = self.dropout(query)

        # Multi-Head Attention + Add & Norm + Feed Forward + Add & Norm
        out = self.transformer_block(queries=query, keys=key, values=value, mask=src_mask)

        return out


class Decoder(nn.Module):
    def __init__(
        self, trg_vocab_size, embed_size, num_layers, heads, forward_expansion, dropout, device, max_length
    ):
        """[summary]

        Args:
            trg_vocab_size    (): [description]
            embed_size        (): [description]
            num_layers        (): [description]
            heads             (): [description]
            forward_expansion (): [description]
            dropout           (): [description]
            device            (): [description]
            max_length        (): [description]

        TODO Issues
        - do we need to also Softmax after fc_out so that we have pseudo-probabilities
          of words in the target language?
        """
        super(Decoder, self).__init__()
        self.device = device
        self.word_embedding = nn.Embedding(num_embeddings=trg_vocab_size, embedding_dim=embed_size)
        self.position_embedding = nn.Embedding(num_embeddings=max_length, embedding_dim=embed_size)
        self.layers = nn.ModuleList(
            [DecoderBlock(embed_size, heads, forward_expansion, dropout, device) for _ in range(num_layers)]
        )
        self.fc_out = nn.Linear(embed_size, trg_vocab_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, encoder_out, src_mask, trg_mask):
        """[summary]

        Args:
            x           (torch.Tensor): a batch of target sentences
            encoder_out (torch.Tensor): output from the encoder for a corresponding batch of source sentences
            src_mask    (torch.Tensor): ?
            trg_mask    (torch.Tensor): a batch of lower triangular matrices of ones (one for each sentence)
        """
        batch_size, sentence_length = x.shape
        positions = (
            # index the words from 0 to sentence_length - 1
            torch.arange(0, sentence_length)
            # duplicate that index array once per sentence
            .expand(batch_size, sentence_length)
            # send the index matrix to cpu or gpu
            .to(self.device)
        )

        # send the words to embedding space, and add the positional encoding
        x = self.word_embedding(x) + self.position_embedding(x)
        x = self.dropout(x)

        # run the batch through each of the
        for layer in self.layers:
            x = layer(x=x, value=encoder_out, key=encoder_out, src_mask=src_mask, trg_mask=trg_mask)

        out = self.fc_out(x)

        # do we need a softmax here?

        return out


class Transformer(nn.Module):
    def __init__(
        self,
        src_vocab_size,
        trg_vocab_size,
        src_pad_idx,
        trg_pad_idx,
        embed_size=256,
        num_layers=6,
        forward_expansion=4,
        heads=8,
        dropout=0,
        device="cpu",
        max_length=188,
    ):
        """[summary]
        Args:
            src_vocab_size           ([type]): [description]
            trg_vocab_size           ([type]): [description]
            src_pad_idx              ([type]): [description]
            trg_pad_idx              ([type]): [description]
            embed_size        (int, optional): [description]. Defaults to 256.
            num_layers        (int, optional): [description]. Defaults to 6.
            forward_expansion (int, optional): [description]. Defaults to 4.
            heads             (int, optional): [description]. Defaults to 8.
            device            (str, optional): [description]. Defaults to "cpu".
            max_length        (int, optional): [description]. Defaults to 188.
        """
        super(Transformer, self).__init__()
        self.src_pad_idx = src_pad_idx
        self.trg_pad_idx = trg_pad_idx
        self.device = device

        self.encoder = Encoder(
            src_vocab_size,
            embed_size,
            num_layers,
            heads,
            device,
            forward_expansion,
            dropout,
            max_length,
        )

        self.decoder = Decoder(
            trg_vocab_size, embed_size, num_layers, heads, forward_expansion, dropout, device, max_length
        )

    def make_src_mask(self, src):
        """[summary]

        Args:
            src ([type]): [description]
        """
        src_mask = (src != self.src_pad_idx).unsqueeze(1).unsqueeze(2)  # [batch_size, 1, 1, src_len]
        return src_mask.to(self.device)

    def make_trg_mask(self, trg):
        """For the target sentences, we need each sentence to be masked
        by a lower triangular matrix of ones. This will prevent the self-attention mechanism
        in the decoder from basing its word choices off of words it hasn't generated yet.

        Args:
            trg (torch.tensor): a tensor of shape [batch_size, max sentence length]

        Returns:
            torch.tensor: [batch_size, 1, max sentence length, max sentence length]
                          A 4 dimensional tensor representing one 2-d lower triangular matrix of ones
                          for every sentence in :trg:
        """
        batch_size, trg_len = trg.shape
        # make a 2-d lower triangular matrix of ones of shape [trg_len, trg_len]
        trg_mask = torch.tril(torch.ones((trg_len, trg_len)))
        # duplicate the matrix batch_size times, and add an empty dimension
        trg_mask = trg_mask.expand(batch_size, 1, trg_len, trg_len)

        return trg_mask

    def forward(self, src, trg):
        src_mask = self.make_src_mask(src)
        trg_mask = self.make_trg_mask(trg)

        # pass the source sentence batch into the encoder
        enc_src = self.encoder(src, src_mask)

        # pass the encoded source sentences into the decoder
        out = self.decoder(trg, enc_src, src_mask, trg_mask)

        return out

    # adding to trigger darker
    def backward(self, src, trg):
        src_mask = self.make_src_mask(src)
        trg_mask = self.make_trg_mask(trg)

        # pass the source sentence batch into the encoder
        enc_src = self.encoder(src, src_mask)

        # pass the encoded source sentences into the decoder
        out = self.decoder(trg, enc_src, src_mask, trg_mask)

        return out


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    x = torch.tensor(
        [[1, 5, 6, 4, 3, 9, 5, 2, 0], [1, 8, 7, 3, 4, 5, 6, 7, 2]]  # src sentence 1  # src sentence 2
    ).to(device)

    trg = torch.tensor(
        [[1, 7, 4, 3, 5, 9, 2, 0], [1, 5, 6, 2, 4, 7, 6, 2]]  # trg sentence 1  # trg sentence 2
    ).to(device)

    # src_pad_idx = 0
    # trg_pad_idx = 0
    # src_vocab_size = 10
    # trg_vocab_size = 10
    # model = Transformer(src_vocab_size, trg_vocab_size, src_pad_idx, trg_pad_idx).to(device)
    # out = model(x, trg[:, :-1])
    # print(out.shape)

    # adding this to trigger darker
    def function_with_missing_argument(arg1: str):
        """Do something cool."""

    def sphinx_formatted_function(arg1: str):
        """
        Do something cool.

        :param arg1: explanation
        """

    def google_formatted_function(arg1: str):
        """
        Do something cool.

        Args:
            arg1: explanation
        """
