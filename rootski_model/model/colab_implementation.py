import math
import time

import torch
import torch.nn as nn
import torch.optim as optim


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        self.scale = nn.Parameter(torch.ones(1))

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer("pe", pe)

    def forward(self, x):
        x = x + self.scale * self.pe[: x.size(0), :]
        return self.dropout(x)


class TransformerModel(nn.Module):
    def __init__(self, intoken, outtoken, hidden, enc_layers=3, dec_layers=1, dropout=0.1):
        super(TransformerModel, self).__init__()
        nhead = hidden // 64

        self.encoder = nn.Embedding(intoken, hidden)
        self.pos_encoder = PositionalEncoding(hidden, dropout)

        self.decoder = nn.Embedding(outtoken, hidden)
        self.pos_decoder = PositionalEncoding(hidden, dropout)

        self.transformer = nn.Transformer(
            d_model=hidden,
            nhead=nhead,
            num_encoder_layers=enc_layers,
            num_decoder_layers=dec_layers,
            dim_feedforward=hidden * 4,
            dropout=dropout,
            activation="relu",
        )
        self.fc_out = nn.Linear(hidden, outtoken)

        self.src_mask = None
        self.trg_mask = None
        self.memory_mask = None

    def generate_square_subsequent_mask(self, sz):
        mask = torch.triu(torch.ones(sz, sz), 1)
        mask = mask.masked_fill(mask == 1, float("-inf"))
        return mask

    def make_len_mask(self, inp):
        return (inp == 0).transpose(0, 1)

    def forward(self, src, trg):
        if self.trg_mask is None or self.trg_mask.size(0) != len(trg):
            self.trg_mask = self.generate_square_subsequent_mask(len(trg)).to(trg.device)

        # print("src", src.size())
        # print("trg", trg.size())

        src_pad_mask = self.make_len_mask(src)
        trg_pad_mask = self.make_len_mask(trg)

        # print("src_pad_mask", src_pad_mask.size())
        # print("trg_pad_mask", trg_pad_mask.size())

        src = self.encoder(src)
        # print("encoded src", src.size())
        src = self.pos_encoder(src)
        # print("pos envoded src", src.size())

        trg = self.decoder(trg)
        # print("encoded trg", trg.size())
        trg = self.pos_decoder(trg)
        # print("pos encoded trg", trg.size())

        output = self.transformer(
            src,
            trg,
            src_mask=self.src_mask,
            tgt_mask=self.trg_mask,
            memory_mask=self.memory_mask,
            src_key_padding_mask=src_pad_mask,
            tgt_key_padding_mask=trg_pad_mask,
            memory_key_padding_mask=src_pad_mask,
        )
        # print("transformer output", output.size())
        output = self.fc_out(output)
        # print("model output", output.size())

        return output


def train(model, optimizer, criterion, iterator, num_batches=1, device="cpu"):
    model.train()
    epoch_loss = 0
    total_train_examples = 0
    for i in range(num_batches):
        batch = next(iterator)
        src, trg = batch
        total_train_examples += src.size(0)
        # src, trg = src.transpose(0, 1).to(device), trg.transpose(0, 1).to(device)
        src, trg = src.to(device), trg.to(device)
        # # print("Batch transposed, src", src.size(), "trg", trg.size())
        optimizer.zero_grad()
        # output = model(src, trg[:-1,:])
        output = model(src, trg[:, :-1])

        output_dim = output.shape[-1]

        # loss = criterion(output.reshape(-1, output_dim), trg[1:,:].reshape(-1))
        loss = criterion(output.reshape(-1, output_dim), trg[:, 1:].reshape(-1))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        epoch_loss += loss.item()
    return epoch_loss  # / total_train_examples


def evaluate(model, criterion, iterator, num_batches=1, device="cpu"):
    model.eval()
    epoch_loss = 0
    total_evaluated_examples = 0
    with torch.no_grad():
        for i in range(num_batches):
            batch = next(iterator)
            src, trg = batch
            total_evaluated_examples += src.size(0)
            # src, trg = src.transpose(0, 1).to(device), trg.transpose(0, 1).to(device)
            src, trg = src.to(device), trg.to(device)

            output = model(src, trg[:, :-1])
            # output = model(src, trg[:-1,:])

            # print("SRC BATCH SIZE", src.size(), "TRG BATCH SIZE", trg.size(), "TRG INPUT SIZE", trg[:-1,:].size(), "OUTPUT SIZE", output.size())

            output_dim = output.shape[-1]

            loss = criterion(output.reshape(-1, output_dim), trg[:, 1:].reshape(-1))
            # loss = criterion(output.reshape(-1, output_dim), trg[1:,:].reshape(-1))

            epoch_loss += loss.item()

        # for i in [0, 5, -1]:
        #     # print('word:', ''.join(seq2g(src[:,i].tolist())).replace('PAD', '').replace('SOS', '').replace('EOS', ''))
        #     # print('real p:    ', seq2p(trg[1:,i].tolist()))
        #     # print('predict p: ', seq2p(output[:,i].argmax(-1).tolist()))

    return epoch_loss  # / total_evaluated_examples


def validate(model, dataloader, show=10, device="cpu"):
    model.eval()
    show_count = 0
    error_w = 0
    error_p = 0
    with torch.no_grad():
        for batch in tqdm(dataloader):
            src, trg = batch
            src, trg = src.tra.transpose(0, 1).to(device), trg.transpose(0, 1).to(device)
            real_p = seq2p(trg.squeeze(1).tolist())
            real_g = seq2g(src.squeeze(1).tolist()[1:-1])

            memory = model.transformer.encoder(model.pos_encoder(model.encoder(src)))

            out_indexes = [
                p2idx["SOS"],
            ]

            for i in range(max_len):
                trg_tensor = torch.LongTensor(out_indexes).unsqueeze(1).to(device)

                output = model.fc_out(
                    model.transformer.decoder(model.pos_decoder(model.decoder(trg_tensor)), memory)
                )
                out_token = output.argmax(2)[-1].item()
                out_indexes.append(out_token)
                if out_token == p2idx["EOS"]:
                    break

            out_p = seq2p(out_indexes)
            error_w += int(real_p != out_p)
            error_p += phoneme_error_rate(real_p, out_p)
            if show > show_count:
                show_count += 1
                # print('Real g', ''.join(real_g))
                # print('Real p', real_p)
                # print('Pred p', out_p)
    return error_p / len(dataloader) * 100, error_w / len(dataloader) * 100


# model.load_state_dict(torch.load('g2p_model.pt'))
# # print(validate(model, val_loader, show=10))


if __name__ == "__main__":

    import torch
    from data import TESTING_DATA_PATH, TRAINING_DATA_PATH, MorphemeDataset
    from inference import preprocess
    from model import *
    from torch import nn
    from torch.utils.data import DataLoader

    device = "cpu"

    # initialize the train/val datasets
    train_data = MorphemeDataset(data_file_path=TRAINING_DATA_PATH)
    val_data = MorphemeDataset(
        data_file_path=TESTING_DATA_PATH,
        src_vocab_override=train_data.src_vocab,
        trg_vocab_override=train_data.trg_vocab,
    )

    max_batch_size = 2048 // 2

    train_loader = DataLoader(
        train_data,
        # sample trg sequences in each batch s.t. they are of equal length
        batch_sampler=train_data.make_sampler(max_batch_size, shuffle=True),
        collate_fn=MorphemeDataset.make_collate_batch_fn(
            src_vocab=train_data.src_vocab,
            trg_vocab=train_data.trg_vocab,
            src_pad_tkn=train_data.pad_tkn,
            trg_pad_tkn=train_data.pad_tkn,
            human_readable=False,
        ),
    )

    val_loader = DataLoader(
        val_data,
        # sample trg sequences in each batch s.t. they are of equal length
        batch_sampler=val_data.make_sampler(max_batch_size, shuffle=True),
        collate_fn=MorphemeDataset.make_collate_batch_fn(
            src_vocab=val_data.src_vocab,
            trg_vocab=val_data.trg_vocab,
            src_pad_tkn=val_data.pad_tkn,
            trg_pad_tkn=val_data.pad_tkn,
            human_readable=False,
        ),
    )

    # initialize the model
    SRC_VOCAB_SIZE = len(train_data.src_vocab.vocab)
    TRG_VOCAB_SIZE = len(train_data.trg_vocab.vocab)
    SRC_PAD_TOKEN = train_data.src_vocab.pad_token
    SRC_PAD_INDEX = train_data.src_vocab.vocab.stoi[SRC_PAD_TOKEN]
    TRG_PAD_TOKEN = train_data.trg_vocab.pad_token
    TRG_PAD_INDEX = train_data.trg_vocab.vocab.stoi[TRG_PAD_TOKEN]

    print("SRC_VOCAB_SIZE", SRC_VOCAB_SIZE)
    print("TRG_VOCAB_SIZE", TRG_VOCAB_SIZE)
    print("SRC_PAD_TOKEN", SRC_PAD_TOKEN)
    print("SRC_PAD_INDEX", SRC_PAD_INDEX)
    print("TRG_PAD_TOKEN", TRG_PAD_TOKEN)
    print("TRG_PAD_INDEX", TRG_PAD_INDEX)
    print("SRC VOCAB", ",".join(train_data.src_vocab.vocab.stoi.keys()))
    print("TRG VOCAB", ",".join(train_data.trg_vocab.vocab.stoi.keys()))

    # model = TransformerModel(
    #     intoken=SRC_VOCAB_SIZE,
    #     outtoken=TRG_VOCAB_SIZE,
    #     hidden=128,
    #     enc_layers=3,
    #     dec_layers=1).to(device)

    model = Transformer(
        src_pad_idx=SRC_PAD_INDEX,
        trg_pad_idx=TRG_PAD_INDEX,
        src_vocab_size=SRC_VOCAB_SIZE,
        trg_vocab_size=TRG_VOCAB_SIZE,
    ).to(device)

    def count_parameters(model):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)

    # print(f'The model has {count_parameters(model):,} trainable parameters')
    # # print(model)

    optimizer = optim.AdamW(model.parameters())
    criterion = nn.CrossEntropyLoss(ignore_index=TRG_PAD_INDEX)

    def epoch_time(start_time, end_time):
        elapsed_time = end_time - start_time
        elapsed_mins = int(elapsed_time / 60)
        elapsed_secs = int(elapsed_time - (elapsed_mins * 60))
        return elapsed_mins, elapsed_secs

    N_EPOCHS = 100

    best_valid_loss = float("inf")

    train_loader_iter = iter(train_loader)
    val_loader_iter = iter(val_loader)

    train_losses = []
    val_losses = []

    print("loading previous model...")
    model.load_state_dict(torch.load("g2p_model.pt"))
    print(f"Starting Training Epochs ({N_EPOCHS} total)")
    for epoch in range(N_EPOCHS):
        print(f"Epoch: {epoch+1:02}")

        start_time = time.time()

        train_loss = train(model, optimizer, criterion, train_loader_iter)
        valid_loss = evaluate(model, criterion, val_loader_iter)

        train_losses.append(train_loss)
        val_losses.append(valid_loss)

        epoch_mins, epoch_secs = epoch_time(start_time, time.time())

        if epoch == 0:
            best_valid_loss = valid_loss

        torch.save(model.state_dict(), "g2p_model.pt")
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss

        print(f"Time: {epoch_mins}m {epoch_secs}s")
        print(f"Train Loss: {train_loss:.3f}")
        print(f"Val   Loss: {valid_loss:.3f}")

        import inference

        breakdown = inference.breakdown_russian_word(
            "приказать", model, train_data.src_vocab, train_data.trg_vocab
        )
        print("приказать -> {}".format(",".join(breakdown)))

    import matplotlib.pyplot as plt

    plt.plot(train_losses, label="Train")
    plt.title("Loss")
    # plt.show()
    plt.xlabel("epoch")
    plt.ylabel("loss")

    plt.plot(val_losses, label="Validation")
    plt.savefig("losses.png")

    print(f"Best Valid Loss: {best_valid_loss}")

    from tqdm.notebook import tqdm

    max_len = 40
    # print(validate(model, val_loader, show=10))

    src = preprocess("приказать", train_data.src_vocab).transpose(0, 1).to(device)
    print("src tensor", src)

    memory = model.transformer.encoder(model.pos_encoder(model.encoder(src)))

    trg_sos_tkn_idx = train_data.trg_vocab.vocab.stoi[train_data.trg_vocab.init_token]
    out_indexes = [
        trg_sos_tkn_idx,
    ]

    for i in range(max_len):
        trg_tensor = torch.LongTensor(out_indexes).unsqueeze(1).to(device)

        output = model.fc_out(model.transformer.decoder(model.pos_decoder(model.decoder(trg_tensor)), memory))
        out_token = output.argmax(2)[-1].item()
        out_indexes.append(out_token)
        if out_token == train_data.trg_vocab.eos_token:
            break

    import inference

    print("Decoded:", inference.decode(out_indexes, vocab=train_data.trg_vocab, remove_meta_tokens=False))
