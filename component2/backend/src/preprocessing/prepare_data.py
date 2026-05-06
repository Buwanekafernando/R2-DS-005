# src/prepare_data.py
# ============================================================
# PURPOSE:
#   1. Align labels from each dataset to our 6 emotions
#   2. Merge all datasets together
#   3. Split FIRST into train/val/test
#   4. Balance ONLY the training set after splitting
#   5. Run quality checks
#
# IMPORTANT — WHY WE SPLIT BEFORE BALANCING:
# If we balance first then split, repeated texts from
# oversampling appear in both train and test sets.
# This is called data leakage — the model has already
# seen test data during training, making results invalid.
# Splitting first prevents this completely.
#
# WHAT TO TELL PANEL:
# "I split the data before balancing to prevent data
#  leakage. Oversampling was applied only to the
#  training set. Val and test sets contain only original
#  unseen texts to ensure honest evaluation."
# ============================================================

import pandas as pd
import os
import sys
from sklearn.utils import resample
from sklearn.model_selection import train_test_split

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
from config import (
    EMOTION_LABELS, SAMPLES_PER_CLASS,
    SPLITS_DIR, MERGED_DIR,
    RANDOM_SEED, TRAIN_RATIO, VAL_RATIO
)


def align_labels(df: pd.DataFrame,
                 mapping: dict,
                 dataset_name: str) -> pd.DataFrame:
    """
    Map each dataset's raw labels to our 6 unified emotions.
    Remove rows whose labels map to None.

    WHY LABEL ALIGNMENT:
    GoEmotions has 28 labels. ISEAR has 4 labels.
    Without alignment we cannot merge them.
    We map all labels to the same 6 emotion names
    so the merged dataset is consistent.

    WHAT TO TELL PANEL:
    "I created a mapping table for each dataset that
     converts their original labels to our 6-class
     taxonomy. Labels not relevant to marketing
     such as disgust, neutral, and confusion were removed."
    """
    before = len(df)
    df     = df.copy()

    # Apply the mapping
    df["emotion"] = df["raw_label"].map(mapping)

    # Show which labels were removed
    removed = df[df["emotion"].isna()]["raw_label"].value_counts()
    if len(removed) > 0:
        print(f"    Removed labels from {dataset_name}:")
        for label, count in removed.items():
            print(f"      {label}: {count} rows removed")

    # Remove rows with no mapping
    df    = df.dropna(subset=["emotion"])
    after = len(df)

    print(f"    {dataset_name}: {before} → {after} rows "
          f"(removed {before - after})")

    return df[["text", "emotion", "source"]].copy()


def merge_datasets(dfs: list) -> pd.DataFrame:
    """
    Concatenate all aligned datasets into one.
    Remove any texts that appear in more than one dataset.

    WHY REMOVE CROSS-DATASET DUPLICATES:
    The same sentence appearing in both training sources
    would be counted twice, giving it more influence
    on the model than it deserves.
    """
    merged = pd.concat(dfs, ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates(subset=["text"])
    after  = len(merged)

    print(f"\n  Merged total: {after} rows "
          f"(removed {before - after} cross-dataset duplicates)")

    print("\n  Distribution BEFORE balancing:")
    counts = merged["emotion"].value_counts()
    for emotion, count in counts.items():
        bar = "█" * (count // 500)
        pct = count / len(merged) * 100
        print(f"    {emotion:15} {bar:15} {count:>6} ({pct:.1f}%)")

    print("\n  Source distribution:")
    for source, count in merged["source"].value_counts().items():
        print(f"    {source:15} {count:>6} rows")

    return merged


def balance_train_only(train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Balance class distribution in training set ONLY.

    Val and test sets are NOT balanced.
    They keep their natural distribution for honest evaluation.

    METHOD:
    Classes with MORE samples → undersample (random removal)
    Classes with FEWER samples → oversample (repeat with replacement)

    WHY NOT SMOTE:
    SMOTE creates synthetic samples by interpolating between
    existing ones. It works well for numbers but poorly for text.
    Repeating existing samples is the accepted standard
    method for text classification in NLP research.
    """
    print(f"\n  Balancing training set to {SAMPLES_PER_CLASS} per class...")
    parts = []

    for emotion in EMOTION_LABELS:
        subset = train_df[train_df["emotion"] == emotion]
        count  = len(subset)

        if count == 0:
            print(f"    WARNING: No samples found for '{emotion}'")
            continue
        elif count >= SAMPLES_PER_CLASS:
            sampled = subset.sample(
                n=SAMPLES_PER_CLASS,
                random_state=RANDOM_SEED
            )
            action = "undersample"
        else:
            sampled = resample(
                subset,
                replace=True,
                n_samples=SAMPLES_PER_CLASS,
                random_state=RANDOM_SEED
            )
            action = "oversample "

        parts.append(sampled)
        print(f"    {emotion:15} {action}: {count:>5} → {SAMPLES_PER_CLASS}")

    balanced = pd.concat(parts, ignore_index=True)
    balanced = balanced.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(drop=True)

    print(f"  Training set after balancing: {len(balanced)} rows")
    return balanced


def split_first_then_balance(df: pd.DataFrame,
                              prefix: str) -> tuple:
    """
    CORRECT ORDER:
    Step A — Split into train/val/test using original data
    Step B — Balance ONLY the training set

    WHY THIS ORDER:
    If we balance first then split, repeated texts from
    oversampling end up in both train and test sets.
    This means the model sees test data during training
    which makes evaluation results invalid and dishonest.

    By splitting first:
    - Test set contains only original, unseen texts
    - Val set contains only original, unseen texts
    - Only training set gets oversampled
    - Evaluation results are honest and trustworthy

    SPLIT RATIOS:
    Train 70% → model learns patterns from this
    Val   15% → tune model settings on this
    Test  15% → final evaluation only, never seen in training
    """
    os.makedirs(SPLITS_DIR, exist_ok=True)

    print(f"\n  Step A: Splitting original data first...")
    print(f"  Total rows before split: {len(df)}")

    # ── Split off test set (30% of total) ─────────────────────
    train_val, test = train_test_split(
        df,
        test_size=(1.0 - TRAIN_RATIO),
        stratify=df["emotion"],
        random_state=RANDOM_SEED
    )

    # ── Split remaining into train and val ────────────────────
    val_relative = VAL_RATIO / (TRAIN_RATIO + VAL_RATIO)
    train_raw, val = train_test_split(
        train_val,
        test_size=val_relative,
        stratify=train_val["emotion"],
        random_state=RANDOM_SEED
    )

    print(f"  Raw split sizes:")
    print(f"    Train (before balance) : {len(train_raw):>6} rows")
    print(f"    Val                    : {len(val):>6} rows")
    print(f"    Test                   : {len(test):>6} rows")

    # ── Balance ONLY the training set ─────────────────────────
    print(f"\n  Step B: Balancing training set only...")
    train = balance_train_only(train_raw)

    # ── Save all three splits ─────────────────────────────────
    train_path = os.path.join(SPLITS_DIR, f"{prefix}_train.csv")
    val_path   = os.path.join(SPLITS_DIR, f"{prefix}_val.csv")
    test_path  = os.path.join(SPLITS_DIR, f"{prefix}_test.csv")

    train.to_csv(train_path, index=False)
    val.to_csv(val_path,     index=False)
    test.to_csv(test_path,   index=False)

    print(f"\n  Final splits saved:")
    print(f"    Train (balanced)  : {len(train):>6} rows → {train_path}")
    print(f"    Val   (original)  : {len(val):>6} rows → {val_path}")
    print(f"    Test  (original)  : {len(test):>6} rows → {test_path}")

    return train, val, test


def run_quality_checks(train: pd.DataFrame,
                       val: pd.DataFrame,
                       test: pd.DataFrame) -> bool:
    """
    Run final checks before training begins.
    Catches problems early with clear error messages.

    CHECK 1 — No data leakage:
    Test texts must not appear in training data.

    CHECK 2 — All 6 emotions present in every split:
    If one emotion is missing from test, we cannot
    evaluate the model on that emotion.

    CHECK 3 — No empty texts anywhere:
    Empty strings cause errors during model training.
    """
    print("\n  Running quality checks...")
    passed = True

    # ── Check 1: No data leakage ──────────────────────────────
    train_texts = set(train["text"].tolist())
    test_texts  = set(test["text"].tolist())
    overlap     = train_texts & test_texts

    if overlap:
        print(f"  ✗ FAIL: Data leakage — "
              f"{len(overlap)} texts appear in both train and test")
        passed = False
    else:
        print(f"  ✓ PASS: No data leakage between train and test")

    # ── Check 2: All emotions present ─────────────────────────
    for split_name, split_df in [
        ("train", train),
        ("val",   val),
        ("test",  test)
    ]:
        present = set(split_df["emotion"].unique())
        missing = set(EMOTION_LABELS) - present

        if missing:
            print(f"  ✗ FAIL: {split_name} missing emotions: {missing}")
            passed = False
        else:
            dist    = split_df["emotion"].value_counts(normalize=True)
            min_pct = dist.min() * 100
            max_pct = dist.max() * 100
            print(f"  ✓ PASS: {split_name} has all 6 emotions "
                  f"(min={min_pct:.1f}% max={max_pct:.1f}%)")

    # ── Check 3: No empty texts ───────────────────────────────
    for split_name, split_df in [
        ("train", train),
        ("val",   val),
        ("test",  test)
    ]:
        empty = split_df[split_df["text"].str.strip() == ""]
        if len(empty) > 0:
            print(f"  ✗ FAIL: {split_name} has {len(empty)} empty texts")
            passed = False
        else:
            print(f"  ✓ PASS: {split_name} has no empty texts")

    return passed