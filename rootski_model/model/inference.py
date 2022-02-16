import torch
from data import MorphemeDataset
from model import Transformer
from torch import Tensor
from torchtext.data import Field


def preprocess(word: str, vocab: Field) -> Tensor:
    word = list(word)  # "hi" -> [h, i]
    word = MorphemeDataset.add_eos_sos_tokens(
        word, vocab.init_token, vocab.eos_token
    )  # [h, i] -> [<start>, h, i, <end>]
    word = MorphemeDataset.sequence_stoi(word, vocab)  # [<start>, h, i, <end>] -> [0, 92, 23, 1]
    word = torch.tensor(word).long().unsqueeze(0)  # (s) -> (1, s)
    return word


def decode(sequence: list, vocab: Field, remove_meta_tokens=True) -> list:
    sequence = MorphemeDataset.sequence_itos(sequence, vocab)
    if remove_meta_tokens:
        meta_tokens = [vocab.unk_token, vocab.pad_token, vocab.init_token, vocab.eos_token]
        for token in meta_tokens:
            # remove all occurrences of token from sequence
            sequence = list(filter((token).__ne__, sequence))
    return sequence


def breakdown_russian_word(word: str, model: Transformer, src_vocab: Field, trg_vocab: Field):
    """[summary]

    Args:
        word          (str): [description]
        model (Transformer): [description]
        src_vocab   (Field): [description]
        trg_vocab   (Field): [description]

    Returns:
        [type]: [description]
    """

    # put the model in evaluation mode; turn of features like dropout
    model.eval()

    # get the meta tokens & indices from the src/trg vocabs
    src_sos_tkn = src_vocab.init_token  # <start>
    src_eos_tkn = src_vocab.eos_token  # <end>
    trg_sos_tkn = trg_vocab.init_token  # <start>
    trg_eos_tkn = trg_vocab.eos_token  # <end>

    trg_sos_idx = trg_vocab.vocab.stoi[trg_sos_tkn]
    trg_eos_idx = trg_vocab.vocab.stoi[trg_eos_tkn]

    # prepare an initial trg sequence
    trg = [trg_sos_tkn]  # [<start>]

    # encode the initial src/trg pair as tensors of indices
    trg = MorphemeDataset.sequence_stoi(trg, trg_vocab)  # encode trg as list of trg_vocab indices
    trg = torch.tensor(trg, dtype=torch.long).unsqueeze(0)  # (1, t := len(trg))
    src = preprocess(word, src_vocab)  # (1, s := len(src))

    trg_start_index_tensor = torch.tensor([[trg_sos_idx]], dtype=torch.long)
    final_result = []

    with torch.no_grad():
        # predict one token at a time until we hit an <end> token or the max seq length
        for _ in range(model.max_trg_seq_len):

            # print("INFERENCE src", src.size())
            # print("INFERENCE trg", trg.size())

            output = model(src, trg)  # (1, 1, s), (1, 1, t) -> (1, t, trg vocab size)
            # print("INFERENCE output", output.size())

            output = torch.softmax(output, dim=2)  # (1, t, output vocab size) -> (1, t, output vocab size)
            trg = output.argmax(dim=2)  # (1, t, output vocab size) -> (1, t)
            x = trg.squeeze(0)  # (1, t) -> (t)

            trg = torch.cat([trg_start_index_tensor, trg], dim=1)  # trg = [<start>] + trg
            newest_token_idx = x[-1].item()

            # # print("output:")
            # # print(x)
            # # print("final result:")
            # # print(final_result)

            # finish translation if we
            if newest_token_idx == trg_eos_idx:
                # print("ending!")
                break

            final_result += [newest_token_idx]

    # conver the index sequence to a sequence of string tokens
    breakdown_sequence = MorphemeDataset.sequence_itos(final_result, trg_vocab)

    return breakdown_sequence


if __name__ == "__main__":
    word = "приказать"
    model, src_vocab, trg_vocab = Transformer.load_model_checkpoint("./model_checkpoint.pt")
    breakdown = breakdown_russian_word(word, model, src_vocab, trg_vocab)
    print("Word:", word)
    print("Breakdown", breakdown)
