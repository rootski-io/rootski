import torch
from data import PADDING_TOKEN, MorphemeDataset
from inference import breakdown_russian_word
from model import Transformer
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

# Training hyperparameters
NUM_EPOCHS = 100
BATCHES_PER_TRAINING_EPOCH = 4
BATCHES_PER_VALIDATION_EPOCH = 2
MAX_BATCH_SIZE = 32
LEARNING_RATE = 3e-4


def train(
    model: Transformer,
    train_dataset: MorphemeDataset,
    val_dataset: MorphemeDataset,
    num_epochs: int = NUM_EPOCHS,
    batches_per_train_epoch: int = BATCHES_PER_TRAINING_EPOCH,
    batches_per_val_epoch: int = BATCHES_PER_TRAINING_EPOCH,
    max_batch_size: int = MAX_BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    device="cpu",
):
    """
    TODO since the train and val datasets are of different lengths, they
    will finish iteration at different times, so will simply stop returning
    batches...

    Args:
        model             (Transformer):
        train_dataset (MorphemeDataset):
        val_dataset   (MorphemeDataset):
        num_epochs              (int, optional): Defaults to NUM_EPOCHS.
        batches_per_train_epoch (int, optional): Defaults to BATCHES_PER_TRAINING_EPOCH.
        batches_per_val_epoch   (int, optional): Defaults to BATCHES_PER_VALIDATION_EPOCH.
        max_batch_size    (int, optional): Defaults to BATCH_SIZE.
        learning_rate             (float): Defaults to LEARNING_RATE
        device            (str, optional): Defaults to "cpu".
    """

    model.to(device)  # perform training operations with GPU if available

    train_loader = DataLoader(
        train_dataset,
        # sample trg sequences in each batch s.t. they are of equal length
        batch_sampler=train_dataset.make_sampler(max_batch_size, shuffle=True),
        collate_fn=MorphemeDataset.make_collate_batch_fn(
            src_vocab=train_dataset.src_vocab,
            trg_vocab=train_dataset.trg_vocab,
            src_pad_tkn=train_dataset.pad_tkn,
            trg_pad_tkn=train_dataset.pad_tkn,
            human_readable=False,
        ),
    )

    val_loader = DataLoader(
        val_dataset,
        # sample trg sequences in each batch s.t. they are of equal length
        batch_sampler=val_dataset.make_sampler(max_batch_size, shuffle=True),
        collate_fn=MorphemeDataset.make_collate_batch_fn(
            src_vocab=val_dataset.src_vocab,
            trg_vocab=val_dataset.trg_vocab,
            src_pad_tkn=val_dataset.pad_tkn,
            trg_pad_tkn=val_dataset.pad_tkn,
            human_readable=False,
        ),
    )

    # get iterators from the dataloaders
    train_iterator = iter(train_loader)
    val_iterator = iter(val_loader)

    # prepare the optimizer for gradient descent on the model weights
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # prepare the loss function
    pad_idx = train_dataset.trg_vocab.vocab.stoi[PADDING_TOKEN]
    criterion = nn.CrossEntropyLoss(ignore_index=pad_idx)

    # prepare to log training/validation metrics
    writer = SummaryWriter(log_dir="runs")

    train_losses = []
    val_losses = []

    for epoch in range(num_epochs):
        avg_train_loss = do_training_epoch(
            model, optimizer, criterion, train_iterator, device=device, num_batches=batches_per_train_epoch
        )
        avg_val_loss = do_validation_epoch(
            model, criterion, val_iterator, device=device, num_batches=batches_per_val_epoch
        )

        model.save_model_checkpoint(
            train_dataset.src_vocab, train_dataset.trg_vocab, path="model_checkpoint.pt"
        )

        train_losses.append(avg_train_loss)
        val_losses.append(avg_val_loss)

        print(
            f"=> Epoch: {epoch + 1} -- Avg. Training Loss {avg_train_loss:.3f}"
            f" Avg. Validation Loss {avg_val_loss:.3f}"
        )
        writer.add_scalar("Loss/train", avg_train_loss, epoch)
        writer.add_scalar("Loss/validation", avg_val_loss, epoch)

        word = "приказать"
        breakdown = breakdown_russian_word(word, model, train_dataset.src_vocab, train_dataset.trg_vocab)
        print(",".join(breakdown))

        writer.add_text("word", " ".join(breakdown), global_step=epoch)
        writer.add_text("breakdown", " ".join(breakdown), global_step=epoch)

    import matplotlib.pyplot as plt

    plt.plot(train_losses, label="Train")
    plt.title("Loss")
    # plt.show()
    plt.xlabel("epoch")
    plt.ylabel("loss")

    plt.plot(val_losses, label="Validation")
    plt.savefig("my-losses.png")


def do_training_epoch(model, optimizer, criterion, train_dataloader_iterator, num_batches, device="cpu"):
    """Perform a single training epoch--in this case, inputting the entire training dataset
    into the model one time. Gradient descent is performed on the weights during this epoch.

    Args:
        model (Transformer): Wrapper around nn.Transformer with sine/cosine positional encoding
        optimizer (torch.optim.Optimizer): Some optimizer initialized with access to all of the
            model parameters that we want to iterate on with gradient descent
        criterion (function): A loss function for multi-class classification.
            KL divergence for label smoothing and Cross Entropy Loss are standard.
        train_dataloader (torch.data.DataLoader): A DataLoader with the batch_sampler parameter
            overriden so that all the target sequences in the batches are of equal length
        device (str, optional): "cpu" or "cuda" (used for running computations on a GPU).
            Defaults to "cpu".

    Returns:
        float: Average loss per training example for the epoch
    """
    model.train()  # set to train mode: turn on features like dropout
    epoch_loss = 0  # keep track the total loss
    total_samples = 0  # count the number of samples evaluated in this epoch

    for _ in range(num_batches):
        batch = next(train_dataloader_iterator)
        src, trg = batch  # (N, s), (N, t) s ≤ S, t ≤ T
        N, s = src.shape
        # N, t = trg.shape
        src.to(device), trg.to(device)  # send the batch tensors to GPU if desired

        optimizer.zero_grad()  # clean up any gradients from previous training steps
        # input_trg           = trg[:, :-1]  # <start> h e l l o
        # expected_output_trg = trg[:, 1:]   # h e l l o <end>
        # output_trg = model(src, input_trg) # (N, t - 1, Target Vocab Size)
        output_trg = model(src, trg[:, :-1])  # (N, t - 1, Target Vocab Size)

        # reshape the output to be 2-d and the expected ouput to be 1-d
        # trg_vocab_size = output_trg.size(2)
        trg_vocab_size = output_trg.size(-1)
        # output          = output_trg.reshape(N * (t - 1), trg_vocab_size)
        # output          = output_trg.reshape(-1, trg_vocab_size)
        # expected_output = expected_output_trg.reshape(-1)
        # expected_output = expected_output_trg.reshape(N * (t - 1))

        loss = criterion(output_trg.reshape(-1, trg_vocab_size), trg[:, 1:].reshape(-1))
        # loss = criterion(output, expected_output)
        loss.backward()  # compute the gradient for all weights using back prop

        # update epoch metrics
        epoch_loss += loss.item()
        total_samples += N
        # total_samples += N

        # keep the gradients within from exploding
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()  # iterate the weights with gradient descent

    return epoch_loss  # / total_samples


def do_validation_epoch(model, criterion, val_dataloader_iterator, num_batches, device="cpu"):
    """Perform a single training epoch--in this case, inputting the entire training dataset
    into the model one time. Gradient descent is NOT performed on the model weights
    during this epoch.

    Args:
        model (Transformer): Wrapper around nn.Transformer with sine/cosine positional encoding
        criterion (function): A loss function for multi-class classification.
            KL divergence for label smoothing and Cross Entropy Loss are standard.
        val_dataloader (MorphemeSampler): A DataLoader with the batch_sampler parameter
            overriden so that all the target sequences in the batches are of equal length
        device (str, optional): "cpu" or "cuda" (used for running computations on a GPU).
            Defaults to "cpu".

    Returns:
        float: Average loss per validation example for the epoch
    """
    model.eval()  # set to evaluation mode: turn off features like dropout
    epoch_loss = 0
    total_samples = 0  # count the number of samples evaluated in this epoch

    with torch.no_grad():  # disable autograd/backprop
        for _ in range(num_batches):
            batch = next(val_dataloader_iterator)
            src, trg = batch  # (N, s), (N, t) s ≤ S, t ≤ T
            N, s = src.shape
            N, t = trg.shape
            src.to(device), trg.to(device)  # send the batch tensors to GPU if desired

            # input_trg           = trg[:, :-1]  # <start> h e l l o
            # expected_output_trg = trg[:, 1:]   # h e l l o <end>
            # output_trg = model(src, input_trg) # output: (N, t - 1, Target Vocab Size)
            output_trg = model(src, trg[:, :-1])  # output: (N, t - 1, Target Vocab Size)

            # reshape the output to be 2-d and the expected ouput to be 1-d
            # trg_vocab_size = output_trg.size(2)
            trg_vocab_size = output_trg.size(-1)
            # output          = output_trg.reshape(N * (t - 1), trg_vocab_size)
            # expected_output = expected_output_trg.reshape(N * (t - 1))

            # loss = criterion(output, expected_output)
            loss = criterion(output_trg.reshape(-1, trg_vocab_size), trg[:, 1:].reshape(-1))

            # update epoch metrics
            epoch_loss += loss.item()
            total_samples += N
            # total_samples += N

    return epoch_loss  # / total_samples


if __name__ == "__main__":

    import torch
    from data import TESTING_DATA_PATH, TRAINING_DATA_PATH, MorphemeDataset
    from torch import nn
    from torch.utils.data import DataLoader
    from train import train

    # initialize the train/val datasets
    train_data = MorphemeDataset(data_file_path=TRAINING_DATA_PATH)
    val_data = MorphemeDataset(
        data_file_path=TESTING_DATA_PATH,
        src_vocab_override=train_data.src_vocab,
        trg_vocab_override=train_data.trg_vocab,
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

    model = Transformer(
        src_pad_idx=SRC_PAD_INDEX,
        trg_pad_idx=TRG_PAD_INDEX,
        src_vocab_size=SRC_VOCAB_SIZE,
        trg_vocab_size=TRG_VOCAB_SIZE,
    )
    # model, src_vocab, trg_vocab = Transformer.load_model_checkpoint()

    # model, src_vocab, trg_vocab = Transformer.load_model_checkpoint("./model_checkpoint.pt")
    train(
        model,
        train_data,
        val_data,
        num_epochs=100,
        batches_per_train_epoch=1,
        batches_per_val_epoch=1,
        max_batch_size=2048 // 2,
    )
