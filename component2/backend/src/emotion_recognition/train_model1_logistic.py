# src/emotion_recognition/train_model1_logistic.py
# ============================================================
# MODEL 1: Logistic Regression with TF-IDF (Baseline)
# ============================================================
# PURPOSE:
#   Train a simple Logistic Regression classifier.
#   This is the BASELINE model — no deep learning involved.
#
# WHY START WITH LOGISTIC REGRESSION:
#   Every ML research paper must have a simple baseline.
#   If complex models like BERT and RoBERTa cannot
#   significantly beat this, the added complexity is
#   not justified. If they DO beat it significantly,
#   we have proven deep learning adds real value.
#
# WHAT IS TF-IDF:
#   Term Frequency - Inverse Document Frequency.
#   Converts text into numerical vectors.
#   Words appearing often in one text but rarely across
#   all texts get high scores — they are distinctive.
#   Example: "joyful" in a happy review gets high score
#   because it strongly signals that emotion.
#
# HOW TO RUN:
#   python src/emotion_recognition/train_model1_logistic.py
#
# EXPECTED TIME: 2-3 minutes
#
# OUTPUT:
#   models/logistic_regression/model.pkl
#   models/logistic_regression/vectorizer.pkl
#   outputs/model_comparison.csv (row added)
# ============================================================

import os
import sys
import joblib
from datetime import datetime

# Go up 3 levels to reach emotion_agent root
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    f1_score, accuracy_score, classification_report
)

from src.emotion_recognition.model_utils import (
    load_splits, print_results, save_results
)
from config import RANDOM_SEED, EMOTION_LABELS

# ── Save path ─────────────────────────────────────────────────────────
MODEL_SAVE_PATH = "models/logistic_regression"
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)


def main():
    start = datetime.now()

    print("=" * 55)
    print("MODEL 1: Logistic Regression (Baseline)")
    print("=" * 55)

    # ── Step 1: Load data ─────────────────────────────────────
    print("\n[Step 1] Loading data...")
    train, val, test, label2id, id2label = load_splits()

    # ── Step 2: Build TF-IDF features ────────────────────────
    print("\n[Step 2] Building TF-IDF features...")
    print("  Settings:")
    print("    max_features = 50,000")
    print("    ngram_range  = (1,2) — single words + word pairs")
    print("    sublinear_tf = True  — log scaling on frequency")
    print("    min_df       = 2     — ignore very rare words")

    vectorizer = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        strip_accents="unicode",
        analyzer="word",
        min_df=2
    )

    # Fit ONLY on training data
    # IMPORTANT: Never fit on val or test
    # Fitting on test data = data leakage
    print("\n  Fitting on training data...")
    X_train = vectorizer.fit_transform(train["text"])
    X_val   = vectorizer.transform(val["text"])
    X_test  = vectorizer.transform(test["text"])

    y_train = train["label"].values
    y_val   = val["label"].values
    y_test  = test["label"].values

    print(f"  Feature matrix shape : {X_train.shape}")
    print(f"  Meaning              : {X_train.shape[0]} samples")
    print(f"                         × {X_train.shape[1]} TF-IDF features")

    # ── Step 3: Train model ───────────────────────────────────
    print("\n[Step 3] Training Logistic Regression...")
    print("  Parameters:")
    print("    max_iter        = 1000")
    print("    C               = 1.0 (regularization strength)")
    print("    solver          = lbfgs")
    print("    multi_class     = multinomial (6 classes)")

    model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_SEED,
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial"
    )

    model.fit(X_train, y_train)
    train_seconds = (datetime.now() - start).seconds
    print(f"\n  Training complete in {train_seconds} seconds")

    # ── Step 4: Validate ──────────────────────────────────────
    print("\n[Step 4] Validation results...")
    val_preds    = model.predict(X_val)
    val_acc      = accuracy_score(y_val, val_preds)
    val_macro_f1 = f1_score(
        y_val, val_preds, average="macro"
    )
    print(f"  Val Accuracy : {val_acc:.4f} ({val_acc*100:.1f}%)")
    print(f"  Val Macro F1 : {val_macro_f1:.4f}")

    # ── Step 5: Test ──────────────────────────────────────────
    print("\n[Step 5] Test set evaluation...")
    test_preds    = model.predict(X_test)
    test_acc      = accuracy_score(y_test, test_preds)
    test_macro_f1 = f1_score(
        y_test, test_preds, average="macro"
    )
    test_f1_per   = f1_score(
        y_test, test_preds,
        average=None,
        labels=list(range(len(EMOTION_LABELS)))
    )

    # Print results
    print_results(
        "Logistic Regression",
        test_acc, test_macro_f1,
        test_f1_per, label2id
    )

    # Full classification report
    target_names = [
        id2label[i] for i in range(len(EMOTION_LABELS))
    ]
    print(f"\n  Full Classification Report:")
    print(classification_report(
        y_test, test_preds,
        target_names=target_names
    ))

    # ── Step 6: Save model ────────────────────────────────────
    print("\n[Step 6] Saving model...")
    joblib.dump(
        model,
        os.path.join(MODEL_SAVE_PATH, "model.pkl")
    )
    joblib.dump(
        vectorizer,
        os.path.join(MODEL_SAVE_PATH, "vectorizer.pkl")
    )
    print(f"  Saved: {MODEL_SAVE_PATH}/model.pkl")
    print(f"  Saved: {MODEL_SAVE_PATH}/vectorizer.pkl")

    # ── Step 7: Save results to comparison file ───────────────
    train_time_mins = round(
        (datetime.now() - start).seconds / 60, 1
    )
    save_results(
        "Logistic Regression",
        test_acc, test_macro_f1,
        test_f1_per, label2id,
        train_time_mins
    )

    # ── Done ──────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("MODEL 1 COMPLETE")
    print(f"  Time taken : {train_time_mins} minutes")
    print(f"  Macro F1   : {test_macro_f1:.4f}")
    print(f"  Accuracy   : {test_acc:.4f}")
    print("=" * 55)
    print("\nNext: python src/emotion_recognition/train_model2_bert.py")


if __name__ == "__main__":
    main()