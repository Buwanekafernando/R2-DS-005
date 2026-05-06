# src/load_datasets.py
# ============================================================
# PURPOSE: Load your 3 specific downloaded datasets
#
# Files expected:
#   data/raw/goemotions/train-00000-of-00001.parquet
#   data/raw/goemotions/validation-00000-of-00001.parquet
#   data/raw/goemotions/test-00000-of-00001.parquet
#   data/raw/isear/eng_dataset.csv
#   data/raw/amazon/amazon_reviews_us_*.tsv (7 files)
# ============================================================

import pandas as pd
import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)
from config import RAW_DIR, GOEMOTIONS_LABEL_NAMES


# ════════════════════════════════════════════════════════════
# LOADER 1 — GoEmotions
# ════════════════════════════════════════════════════════════
def load_goemotions() -> pd.DataFrame:
    """
    Load GoEmotions from 3 parquet files.

    GoEmotions 'labels' column contains a LIST of integers.
    Each integer maps to an emotion name.
    Example: [3] means emotion at index 3 in GOEMOTIONS_LABEL_NAMES
    Example: [3, 14] means two emotions — we take only the first.

    WHY TAKE FIRST LABEL ONLY:
    Multi-label samples are complex to handle.
    Taking the primary (first) label is acceptable
    for our 6-class classification task.
    This is documented in our preprocessing decisions.
    """
    print("\n--- Loading GoEmotions ---")
    path = os.path.join(RAW_DIR, "goemotions")

    files = {
        "train"     : "train-00000-of-00001.parquet",
        "validation": "validation-00000-of-00001.parquet",
        "test"      : "test-00000-of-00001.parquet",
    }

    dfs = []
    for split_name, filename in files.items():
        filepath = os.path.join(path, filename)

        if not os.path.exists(filepath):
            print(f"  ERROR: File not found: {filepath}")
            print(f"  Please check your goemotions folder")
            continue

        df = pd.read_parquet(filepath)
        print(f"  Loaded {split_name:12}: {len(df):>6} rows")
        print(f"  Columns: {df.columns.tolist()}")
        dfs.append(df)

    if not dfs:
        raise FileNotFoundError(
            "No GoEmotions parquet files found in "
            "data/raw/goemotions/"
        )

    combined = pd.concat(dfs, ignore_index=True)

    # ── Convert label integers to label names ─────────────────
    # The 'labels' column looks like: [14] or [3, 27]
    # We need the name at that index from GOEMOTIONS_LABEL_NAMES

    def labels_to_name(label_list):
        """Convert list of label integers to first emotion name"""
        # Handle different possible formats
        if label_list is None:
            return None

        # If it is already a list
        if isinstance(label_list, list):
            if len(label_list) == 0:
                return None
            first_idx = label_list[0]

        # If it is a numpy array
        elif hasattr(label_list, '__iter__'):
            label_list = list(label_list)
            if len(label_list) == 0:
                return None
            first_idx = label_list[0]

        else:
            # Single integer
            first_idx = int(label_list)

        # Safety check
        if first_idx >= len(GOEMOTIONS_LABEL_NAMES):
            return None

        return GOEMOTIONS_LABEL_NAMES[int(first_idx)]

    combined["raw_label"] = combined["labels"].apply(labels_to_name)
    combined["source"]    = "goemotions"

    # Keep only needed columns
    result = combined[["text", "raw_label", "source"]].copy()
    result = result.dropna(subset=["raw_label"])

    print(f"\n  GoEmotions total    : {len(result):>6} rows")
    print(f"  Unique labels found : "
          f"{sorted(result['raw_label'].unique().tolist())}")

    return result


# ════════════════════════════════════════════════════════════
# LOADER 2 — ISEAR (your eng_dataset.csv from Kaggle)
# ════════════════════════════════════════════════════════════
def load_isear() -> pd.DataFrame:
    """
    Load ISEAR dataset from eng_dataset.csv

    Your file columns: id, sentiment, content
      - text  is in 'content' column
      - label is in 'sentiment' column

    ISEAR contains personal emotional experience descriptions.
    Sentences are more formal and structured than social media.
    This helps bridge the gap between casual Reddit text
    (GoEmotions) and formal marketing language.

    Source: Kaggle — ISEAR dataset (eng_dataset.csv)
    """
    print("\n--- Loading ISEAR ---")
    path = os.path.join(RAW_DIR, "isear", "eng_dataset.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"ISEAR file not found at: {path}\n"
            "Expected: data/raw/isear/eng_dataset.csv"
        )

    df = pd.read_csv(path, encoding="utf-8", encoding_errors="ignore")
    print(f"  Loaded: {len(df)} rows")
    print(f"  Columns: {df.columns.tolist()}")

    # Your columns are: id, sentiment, content
    # Rename to our standard format
    df = df.rename(columns={
        "content"  : "text",
        "sentiment": "raw_label"
    })

    # Normalize labels to lowercase
    df["raw_label"] = df["raw_label"].str.lower().str.strip()
    df["source"]    = "isear"

    # Keep only needed columns
    result = df[["text", "raw_label", "source"]].copy()
    result = result.dropna(subset=["text", "raw_label"])

    print(f"  ISEAR total         : {len(result):>6} rows")
    print(f"  Unique labels found : "
          f"{sorted(result['raw_label'].unique().tolist())}")

    return result


# ════════════════════════════════════════════════════════════
# LOADER 3 — Amazon Reviews (your 7 TSV files)
# ════════════════════════════════════════════════════════════
def load_amazon() -> pd.DataFrame:
    """
    Load Amazon Reviews from your 7 TSV files.

    Your file columns include:
      review_body    → this is the text we use
      star_rating    → we filter to 5-star only
      product_category → the product type

    Your 7 files:
      amazon_reviews_us_Apparel_v1_00.tsv
      amazon_reviews_us_Baby_v1_00.tsv
      amazon_reviews_us_Beauty_v1_00.tsv
      amazon_reviews_us_Electronics_v1_00.tsv
      amazon_reviews_us_Grocery_v1_00.tsv
      amazon_reviews_us_Pet_Products_v1_00.tsv
      amazon_reviews_us_Sports_v1_00.tsv

    WHY 5-STAR ONLY:
    5-star reviews express strong positive consumer emotions.
    These are joy, trust, and excitement — exactly the emotions
    we want to embed in marketing content.
    Negative reviews would contaminate our training data.

    WHY 2000 PER CATEGORY:
    We cap at 2000 per file to keep the dataset manageable
    and prevent any one category from dominating.
    Total: 7 × 2000 = 14,000 marketing-domain samples.

    NOTE: Amazon labels here are product categories, NOT emotions.
    Emotion labels are assigned later by our trained classifier.
    This is called 'automatic labeling' or 'silver labeling'.
    """
    print("\n--- Loading Amazon Reviews ---")
    path = os.path.join(RAW_DIR, "amazon")

    # ── Map your filenames to short category labels ───────────
    FILE_CATEGORY_MAP = {
        "amazon_reviews_us_Apparel_v1_00.tsv"      : "Apparel",
        "amazon_reviews_us_Baby_v1_00.tsv"          : "Baby",
        "amazon_reviews_us_Beauty_v1_00.tsv"        : "Beauty",
        "amazon_reviews_us_Electronics_v1_00.tsv"   : "Electronics",
        "amazon_reviews_us_Grocery_v1_00.tsv"       : "Grocery",
        "amazon_reviews_us_Pet_Products_v1_00.tsv"  : "Pet",
        "amazon_reviews_us_Sports_v1_00.tsv"        : "Sports",
    }

    SAMPLES_PER_FILE = 2000   # cap per category
    MIN_TEXT_LENGTH  = 30     # skip very short reviews

    all_rows = []

    for filename, category_label in FILE_CATEGORY_MAP.items():
        filepath = os.path.join(path, filename)

        if not os.path.exists(filepath):
            print(f"  WARNING: File not found — {filename}")
            print(f"           Skipping {category_label}")
            continue

        print(f"\n  Loading: {category_label} ({filename})")

        try:
            # Read TSV in chunks to handle large files efficiently
            # TSV = Tab Separated Values, so sep="\t"
            # on_bad_lines="skip" = ignore corrupted rows
            # encoding_errors="ignore" = ignore encoding issues
            collected_rows = []

            chunk_reader = pd.read_csv(
                filepath,
                sep="\t",
                chunksize=10000,        # read 10000 rows at a time
                on_bad_lines="skip",
                encoding="utf-8",
                encoding_errors="ignore",
                usecols=[               # only load columns we need
                    "star_rating",
                    "review_body",
                    "product_category"
                ],
                dtype={"star_rating": str}  # read as string first
            )

            for chunk in chunk_reader:
                # Clean star_rating — convert to numeric safely
                chunk["star_rating"] = pd.to_numeric(
                    chunk["star_rating"],
                    errors="coerce"
                )

                # Filter: 5-star reviews only
                five_star = chunk[chunk["star_rating"] == 5.0]

                # Filter: minimum text length
                five_star = five_star[
                    five_star["review_body"].notna() &
                    (five_star["review_body"].str.len() >= MIN_TEXT_LENGTH)
                ]

                # Add to our collection
                for _, row in five_star.iterrows():
                    collected_rows.append({
                        "text"    : str(row["review_body"]).strip(),
                        "raw_label": category_label,
                        "source"  : "amazon"
                    })

                    if len(collected_rows) >= SAMPLES_PER_FILE:
                        break

                if len(collected_rows) >= SAMPLES_PER_FILE:
                    break

            print(f"    Collected: {len(collected_rows):>5} reviews")
            all_rows.extend(collected_rows)

        except Exception as e:
            print(f"    ERROR loading {filename}: {e}")
            print(f"    Skipping this file...")
            continue

    if not all_rows:
        print("  WARNING: No Amazon data loaded")
        return pd.DataFrame(columns=["text", "raw_label", "source"])

    result = pd.DataFrame(all_rows)

    print(f"\n  Amazon total collected: {len(result)} reviews")
    print(f"  Category breakdown:")
    counts = result["raw_label"].value_counts()
    for cat, count in counts.items():
        bar = "█" * (count // 100)
        print(f"    {cat:15} {bar} {count}")

    return result


# ════════════════════════════════════════════════════════════
# TEST — Run this file directly to test all loaders
# Command: python src/load_datasets.py
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("TESTING DATASET LOADERS")
    print("=" * 60)

    # Test GoEmotions
    try:
        go = load_goemotions()
        print(f"\n  GoEmotions: OK — {len(go)} rows")
    except Exception as e:
        print(f"\n  GoEmotions: FAILED — {e}")

    # Test ISEAR
    try:
        isear = load_isear()
        print(f"\n  ISEAR: OK — {len(isear)} rows")
    except Exception as e:
        print(f"\n  ISEAR: FAILED — {e}")

    # Test Amazon
    try:
        amazon = load_amazon()
        print(f"\n  Amazon: OK — {len(amazon)} rows")
    except Exception as e:
        print(f"\n  Amazon: FAILED — {e}")

    print("\n" + "=" * 60)
    print("LOADER TEST COMPLETE")
    print("=" * 60)