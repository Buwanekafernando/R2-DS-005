# run_preprocessing.py
# ============================================================
# MASTER SCRIPT — runs the complete preprocessing pipeline
#
# Run from emotion_agent folder:
# Command: python run_preprocessing.py
# ============================================================

import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    PROCESSED_DIR, MERGED_DIR,
    GOEMOTIONS_MAP, ISEAR_MAP
)
from src.preprocessing.load_datasets import load_goemotions, load_isear, load_amazon
from src.preprocessing.clean_text    import clean_dataset
from src.preprocessing.prepare_data  import (
    align_labels,
    merge_datasets,
    split_first_then_balance,
    run_quality_checks
)

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MERGED_DIR,    exist_ok=True)


def main():
    start = datetime.now()
    print("=" * 60)
    print("PREPROCESSING PIPELINE — Emotion Propagation Agent")
    print(f"Started : {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── STEP 1: Load ──────────────────────────────────────────
    print("\n[STEP 1] Loading raw datasets...")
    go_raw    = load_goemotions()
    isear_raw = load_isear()
    amz_raw   = load_amazon()

    print(f"\n  Raw dataset sizes:")
    print(f"    GoEmotions : {len(go_raw):>6} rows")
    print(f"    ISEAR      : {len(isear_raw):>6} rows")
    print(f"    Amazon     : {len(amz_raw):>6} rows")
    print(f"    Total      : "
          f"{len(go_raw)+len(isear_raw)+len(amz_raw):>6} rows")

    # ── STEP 2: Clean ─────────────────────────────────────────
    print("\n[STEP 2] Cleaning datasets...")
    go_clean    = clean_dataset(go_raw,    "GoEmotions")
    isear_clean = clean_dataset(isear_raw, "ISEAR")
    amz_clean   = clean_dataset(amz_raw,   "Amazon")

    # Save cleaned individual files
    go_clean.to_csv(
        os.path.join(PROCESSED_DIR, "goemotions_clean.csv"),
        index=False
    )
    isear_clean.to_csv(
        os.path.join(PROCESSED_DIR, "isear_clean.csv"),
        index=False
    )
    amz_clean.to_csv(
        os.path.join(PROCESSED_DIR, "amazon_clean.csv"),
        index=False
    )
    print(f"\n  Cleaned files saved to data/processed/")

    # ── STEP 3: Align Labels ──────────────────────────────────
    print("\n[STEP 3] Aligning labels to 6 unified emotions...")
    go_aligned    = align_labels(
        go_clean, GOEMOTIONS_MAP, "GoEmotions"
    )
    isear_aligned = align_labels(
        isear_clean, ISEAR_MAP, "ISEAR"
    )

    print(f"\n  After alignment:")
    print(f"    GoEmotions : {len(go_aligned):>6} rows")
    print(f"    ISEAR      : {len(isear_aligned):>6} rows")
    print(f"    Amazon     : {len(amz_clean):>6} rows "
          f"(category labels — emotions assigned after training)")

    # ── STEP 4: Merge ─────────────────────────────────────────
    print("\n[STEP 4] Merging GoEmotions + ISEAR...")
    merged = merge_datasets([go_aligned, isear_aligned])

    # Save the merged corpus before balancing
    merged.to_csv(
        os.path.join(MERGED_DIR, "merged_raw.csv"),
        index=False
    )
    merged.to_csv(
        os.path.join(MERGED_DIR, "general_corpus.csv"),
        index=False
    )
    print(f"  Saved: data/merged/merged_raw.csv")
    print(f"  Saved: data/merged/general_corpus.csv")

    # ── STEP 5: Split first, then balance train only ──────────
    print("\n[STEP 5] Splitting first then balancing train only...")
    print("  Reason: prevents data leakage between train and test")
    train, val, test = split_first_then_balance(merged, "general")

    # ── STEP 6: Quality Checks ────────────────────────────────
    print("\n[STEP 6] Running quality checks...")
    all_passed = run_quality_checks(train, val, test)

    # ── DONE ──────────────────────────────────────────────────
    end      = datetime.now()
    duration = (end - start).seconds

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print(f"Time taken : {duration} seconds")
    print("=" * 60)

    print("\nFiles created:")
    print("  data/processed/goemotions_clean.csv")
    print("  data/processed/isear_clean.csv")
    print("  data/processed/amazon_clean.csv")
    print("  data/merged/merged_raw.csv")
    print("  data/merged/general_corpus.csv")
    print("  data/splits/general_train.csv")
    print("  data/splits/general_val.csv")
    print("  data/splits/general_test.csv")

    if all_passed:
        print("\n  All quality checks passed ✓")
        print("  Next step: python src/train_classifier.py")
    else:
        print("\n  Some checks failed — review errors above")

    print("=" * 60)


if __name__ == "__main__":
    main()