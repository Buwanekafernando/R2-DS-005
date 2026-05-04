# src/emotion_recognition/train_model2_bert.py
# ============================================================
# MODEL 2: BERT (bert-base-uncased)
# ============================================================
# PURPOSE:
#   Fine-tune BERT for 6-class emotion classification.
#   This is the TRANSFORMER BASELINE model.
#
# WHAT IS BERT:
#   Bidirectional Encoder Representations from Transformers.
#   Published by Google in 2018.
#   Unlike Logistic Regression which looks at words
#   individually, BERT reads the ENTIRE sentence at once
#   in both directions and understands full context.
#
#   Example of why context matters:
#   "I am feeling blue today"
#   → "blue" normally means a color
#   → BERT understands "blue" = sad here because it
#     reads the full sentence context
#   → TF-IDF cannot do this
#
# WHAT IS FINE-TUNING:
#   BERT is already pre-trained on Wikipedia and BookCorpus.
#   It already understands English language patterns.
#   Fine-tuning = training it a little more on OUR emotion
#   dataset so it learns emotion-specific patterns on top
#   of its existing language knowledge.
#   Much faster and more accurate than training from scratch.
#
# HOW TO RUN:
#   python src/emotion_recognition/train_model2_bert.py
#
# EXPECTED TIME:
#   CPU: 60-120 minutes
#   GPU: 15-20 minutes
#
# OUTPUT:
#   models/bert/
#   outputs/model_comparison.csv (row added)
# ============================================================

import os
import sys
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup
)
from sklearn.metrics import (
    f1_score, accuracy_score, classification_report
)
from datetime import datetime

# Go up 3 levels to reach emotion_agent root
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

from src.emotion_recognition.model_utils import (
    load_splits, print_results, save_results
)
from config import EMOTION_LABELS, RANDOM_SEED

# ── Training settings ─────────────────────────────────────────────────
MODEL_NAME      = "bert-base-uncased"
MODEL_SAVE_PATH = "models/bert"
BATCH_SIZE      = 32
MAX_LEN         = 128
EPOCHS          = 3
LEARNING_RATE   = 2e-5

os.makedirs(MODEL_SAVE_PATH, exist_ok=True)


# ════════════════════════════════════════════════════════════
# DATASET CLASS
# ════════════════════════════════════════════════════════════

class EmotionDataset(Dataset):
    """
    Custom PyTorch Dataset for emotion classification.

    Converts raw text into BERT input format:
      input_ids      — token IDs (integers)
      attention_mask — 1 for real tokens, 0 for padding
      label          — integer emotion class

    WHY MAX_LEN = 128:
    BERT can handle up to 512 tokens but this is slow.
    Most of our texts are under 128 tokens.
    Using 128 gives a good balance of speed and accuracy.
    """
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts     = texts
        self.labels    = labels
        self.tokenizer = tokenizer
        self.max_len   = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids"     : encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "label"         : torch.tensor(
                self.labels[idx], dtype=torch.long
            )
        }


# ════════════════════════════════════════════════════════════
# TRAINING AND EVALUATION FUNCTIONS
# ════════════════════════════════════════════════════════════

def train_one_epoch(model, loader, optimizer,
                    scheduler, device):
    """
    Run one complete pass over the training data.
    Updates model weights based on prediction errors.
    """
    model.train()
    total_loss  = 0
    total_steps = len(loader)

    for batch_idx, batch in enumerate(loader):
        input_ids      = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels         = batch["label"].to(device)

        # Clear gradients from previous step
        optimizer.zero_grad()

        # Forward pass — get predictions and loss
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss
        total_loss += loss.item()

        # Backward pass — calculate gradients
        loss.backward()

        # Clip gradients to prevent exploding gradient problem
        # This is standard practice for transformer fine-tuning
        torch.nn.utils.clip_grad_norm_(
            model.parameters(), 1.0
        )

        # Update weights
        optimizer.step()
        scheduler.step()

        # Print progress every 100 batches
        if (batch_idx + 1) % 100 == 0:
            avg_loss = total_loss / (batch_idx + 1)
            pct_done = (batch_idx + 1) / total_steps * 100
            print(f"    Batch {batch_idx+1:>4}/{total_steps} "
                  f"({pct_done:.0f}%) | "
                  f"Avg Loss: {avg_loss:.4f}")

    return total_loss / len(loader)


def evaluate_model(model, loader, device):
    """
    Evaluate model on a dataset without updating weights.
    Returns lists of predictions and true labels.
    """
    model.eval()
    all_preds  = []
    all_labels = []

    # No gradient calculation needed during evaluation
    with torch.no_grad():
        for batch in loader:
            outputs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )
            # Get the class with highest probability
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(batch["label"].cpu().numpy())

    return all_preds, all_labels


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

def main():
    start = datetime.now()

    print("=" * 55)
    print("MODEL 2: BERT (bert-base-uncased)")
    print("=" * 55)
    print(f"  Epochs        : {EPOCHS}")
    print(f"  Batch size    : {BATCH_SIZE}")
    print(f"  Learning rate : {LEARNING_RATE}")
    print(f"  Max length    : {MAX_LEN} tokens")

    # ── Check device ──────────────────────────────────────────
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"\n  Device: {device}")
    if device.type == "cuda":
        print(f"  GPU   : {torch.cuda.get_device_name(0)}")
    else:
        print("  NOTE  : Training on CPU is slow (60-120 min)")
        print("          Use Google Colab GPU for faster training")

    # ── Load data ─────────────────────────────────────────────
    print("\n[Step 1] Loading data...")
    train, val, test, label2id, id2label = load_splits()

    # ── Load BERT ─────────────────────────────────────────────
    print(f"\n[Step 2] Loading {MODEL_NAME}...")
    print("  First run downloads ~440MB then cached locally")

    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    model     = BertForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(EMOTION_LABELS),
        id2label=id2label,
        label2id=label2id
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Parameters: {total_params:,}")
    print(f"  Loaded successfully")

    # ── Create data loaders ───────────────────────────────────
    print("\n[Step 3] Creating data loaders...")

    train_loader = DataLoader(
        EmotionDataset(
            train["text"].tolist(),
            train["label"].tolist(),
            tokenizer, MAX_LEN
        ),
        batch_size=BATCH_SIZE,
        shuffle=True
    )
    val_loader = DataLoader(
        EmotionDataset(
            val["text"].tolist(),
            val["label"].tolist(),
            tokenizer, MAX_LEN
        ),
        batch_size=BATCH_SIZE
    )
    test_loader = DataLoader(
        EmotionDataset(
            test["text"].tolist(),
            test["label"].tolist(),
            tokenizer, MAX_LEN
        ),
        batch_size=BATCH_SIZE
    )

    print(f"  Train batches : {len(train_loader)}")
    print(f"  Val batches   : {len(val_loader)}")
    print(f"  Test batches  : {len(test_loader)}")

    # ── Optimizer and scheduler ───────────────────────────────
    total_steps = len(train_loader) * EPOCHS
    optimizer   = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        eps=1e-8
    )

    # Linear warmup then linear decay of learning rate
    # Warmup helps model settle before full learning rate
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=total_steps // 10,
        num_training_steps=total_steps
    )

    # ── Training loop ─────────────────────────────────────────
    print(f"\n[Step 4] Training for {EPOCHS} epochs...")

    best_val_f1 = 0.0

    for epoch in range(EPOCHS):
        epoch_start = datetime.now()
        print(f"\n  {'─'*45}")
        print(f"  Epoch {epoch+1} of {EPOCHS}")
        print(f"  {'─'*45}")

        # Train for one epoch
        avg_loss = train_one_epoch(
            model, train_loader,
            optimizer, scheduler, device
        )

        # Evaluate on validation set
        val_preds, val_labels = evaluate_model(
            model, val_loader, device
        )
        val_f1  = f1_score(
            val_labels, val_preds, average="macro"
        )
        val_acc = accuracy_score(val_labels, val_preds)

        epoch_mins = (datetime.now() - epoch_start).seconds // 60
        epoch_secs = (datetime.now() - epoch_start).seconds % 60

        print(f"\n  Epoch {epoch+1} Summary:")
        print(f"    Train Loss  : {avg_loss:.4f}")
        print(f"    Val Macro F1: {val_f1:.4f}")
        print(f"    Val Accuracy: {val_acc:.4f}")
        print(f"    Time        : {epoch_mins}m {epoch_secs}s")

        # Save best model based on validation F1
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            model.save_pretrained(MODEL_SAVE_PATH)
            tokenizer.save_pretrained(MODEL_SAVE_PATH)
            print(f"    ✓ Best model saved "
                  f"(Val F1: {val_f1:.4f})")

    # ── Final evaluation on test set ──────────────────────────
    print("\n[Step 5] Final evaluation on test set...")
    print("  Loading best saved model...")

    best_model = BertForSequenceClassification.from_pretrained(
        MODEL_SAVE_PATH
    ).to(device)

    test_preds, test_labels = evaluate_model(
        best_model, test_loader, device
    )

    test_acc      = accuracy_score(test_labels, test_preds)
    test_macro_f1 = f1_score(
        test_labels, test_preds, average="macro"
    )
    test_f1_per   = f1_score(
        test_labels, test_preds,
        average=None,
        labels=list(range(len(EMOTION_LABELS)))
    )

    # Print results
    print_results(
        "BERT",
        test_acc, test_macro_f1,
        test_f1_per, label2id
    )

    # Full classification report
    target_names = [
        id2label[i] for i in range(len(EMOTION_LABELS))
    ]
    print(f"\n  Full Classification Report:")
    print(classification_report(
        test_labels, test_preds,
        target_names=target_names
    ))

    # ── Save results ──────────────────────────────────────────
    train_time_mins = round(
        (datetime.now() - start).seconds / 60, 1
    )
    save_results(
        "BERT (bert-base-uncased)",
        test_acc, test_macro_f1,
        test_f1_per, label2id,
        train_time_mins
    )

    # ── Done ──────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("MODEL 2 COMPLETE")
    print(f"  Time taken  : {train_time_mins} minutes")
    print(f"  Macro F1    : {test_macro_f1:.4f}")
    print(f"  Accuracy    : {test_acc:.4f}")
    print(f"  Model saved : {MODEL_SAVE_PATH}/")
    print("=" * 55)
    print("\nNext: python src/emotion_recognition/train_model3_roberta.py")


if __name__ == "__main__":
    main()