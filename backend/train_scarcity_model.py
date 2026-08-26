import sys
import os
import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
import argparse

backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from utils.scarcity_agent import ScarcityAgent
from utils.pain_point_extractor import extract_pain_points_detailed


def compute_pseudo_target(product_info: dict, pain_points: list, review_text: str = "") -> float:
    """Heuristic function to compute a pseudo-continuous target between 0 and 1 when labels are absent."""
    base = 0.2
    # increase for high priority pain points
    if pain_points:
        high_priority = [p for p in pain_points if p in ("Shipping Delays", "Stock Instability", "Quality Issues")]
        base += 0.25 * len(high_priority)
        # presence of any pain points bumps score
        base += 0.05 * max(0, len(pain_points) - len(high_priority))

    # price-driven urgency
    price = float(product_info.get("price", 0) or 0)
    if price >= 500:
        base += 0.15
    elif price >= 100:
        base += 0.07

    # explicit keywords indicating scarcity
    text = (review_text or "").lower()
    if any(k in text for k in ["sold out", "out of stock", "limited supply", "back order", "restock"]):
        base += 0.25
    if any(k in text for k in ["fast selling", "selling out"]):
        base += 0.15

    return float(max(0.0, min(1.0, base)))


def load_sample_products(json_path: Path) -> dict:
    if not json_path or not json_path.exists():
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        # build lookup by name (lowercase) -> product dict
        return {str(p.get("name", "")).lower(): p for p in items}
    except Exception:
        return {}


def train_from_tsvs(tsv_paths, sample_json=None, max_samples=20000, chunk_size=50000):
    """Stream TSV(s), extract features using ScarcityAgent helper, generate pseudo-targets, and train model."""
    models_dir = backend_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    regressor_path = models_dir / "scarcity_intensity_regressor.pkl"
    scaler_path = models_dir / "scarcity_scaler.pkl"

    agent = ScarcityAgent(model_dir=str(models_dir))
    product_lookup = load_sample_products(Path(sample_json) if sample_json else None)

    X = []
    y = []
    processed = 0

    for tsv in tsv_paths:
        if processed >= max_samples:
            break
        if not Path(tsv).exists():
            print(f"[WARN] TSV path not found: {tsv}")
            continue

        print(f"Processing TSV: {tsv} (chunksize={chunk_size})")
        try:
            for chunk in pd.read_csv(tsv, sep="\t", chunksize=chunk_size, iterator=True, dtype=str, encoding='utf-8', error_bad_lines=False, warn_bad_lines=False):
                # try common column names
                col_review = None
                col_title = None
                col_category = None

                for c in ("review_body", "reviewText", "review_body_text", "reviewBody"):
                    if c in chunk.columns:
                        col_review = c
                        break
                for c in ("product_title", "productTitle", "title"):
                    if c in chunk.columns:
                        col_title = c
                        break
                for c in ("product_category", "category", "product_category_tree"):
                    if c in chunk.columns:
                        col_category = c
                        break

                for _, row in chunk.iterrows():
                    if processed >= max_samples:
                        break
                    review_text = str(row.get(col_review, "")) if col_review else ""
                    title = str(row.get(col_title, "")) if col_title else ""
                    category = str(row.get(col_category, "")) if col_category else ""

                    product_info = {"name": title, "category": category or "general", "price": 0}
                    # try lookup price/category from sample products
                    if title and title.lower() in product_lookup:
                        p = product_lookup[title.lower()]
                        product_info["price"] = p.get("price", 0)
                        product_info["category"] = p.get("category", product_info["category"])

                    pp_details = extract_pain_points_detailed(review_text) if review_text else {"pain_points": []}
                    pain_points = pp_details.get("pain_points", [])

                    feat = agent._build_feature_vector(product_info=product_info, pain_points=pain_points)
                    target = compute_pseudo_target(product_info, pain_points, review_text)

                    X.append(feat)
                    y.append(target)
                    processed += 1

                if processed >= max_samples:
                    break
        except Exception as exc:
            print(f"[ERROR] Failed processing {tsv}: {exc}")

    if len(X) < 10:
        print("Not enough samples gathered for training. Aborting.")
        return

    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    reg = DecisionTreeRegressor(random_state=42)
    reg.fit(X_scaled, y)

    with open(regressor_path, "wb") as f:
        pickle.dump(reg, f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    print("[SUCCESS] Trained Regression model from TSV(s) and saved artifacts:")
    print(f"   - Regressor Model: {regressor_path}")
    print(f"   - Feature Scaler: {scaler_path}")


def train_and_save_regression_pkl_model():
    # keep the original small-sample trainer for quick runs
    print("=== Manual Scarcity Regression Model Training Pipeline (default small sample) ===")
    models_dir = backend_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    regressor_path = models_dir / "scarcity_intensity_regressor.pkl"
    scaler_path = models_dir / "scarcity_scaler.pkl"

    # Feature Vector: [price_bucket, category_score, stock_flag, shipping_flag, price_sensitivity_flag, quality_flag]
    # Continuous Regression Target: Urgency Intensity Score (0.0 to 1.0)
    training_data = [
        ([0, 0.5, 0, 0, 1, 0], 0.20),
        ([0, 0.8, 0, 0, 0, 0], 0.15),
        ([1, 1.2, 0, 1, 0, 0], 0.50),
        ([1, 1.5, 1, 0, 0, 0], 0.55),
        ([2, 2.0, 1, 1, 0, 0], 0.85),
        ([2, 2.5, 1, 0, 0, 1], 0.95),
        ([1, 2.0, 0, 0, 1, 0], 0.50),
        ([2, 2.2, 0, 1, 1, 0], 0.90),
        ([0, 1.0, 0, 0, 0, 1], 0.45),
        ([1, 1.8, 1, 0, 1, 0], 0.80),
        ([0, 0.7, 0, 0, 0, 0], 0.10),
        ([1, 1.3, 0, 1, 0, 1], 0.52),
    ]

    features = np.array([item[0] for item in training_data], dtype=float)
    targets = np.array([item[1] for item in training_data], dtype=float)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    reg = DecisionTreeRegressor(random_state=42)
    reg.fit(scaled_features, targets)

    with open(regressor_path, "wb") as f:
        pickle.dump(reg, f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    print("[SUCCESS] Successfully trained Regression model and exported .pkl artifacts:")
    print(f"   - Regressor Model: {regressor_path}")
    print(f"   - Feature Scaler: {scaler_path}")

    # Verification test
    agent = ScarcityAgent(model_dir=str(models_dir))
    sample_score = agent.predict_intensity_score(
        product_info={"price": 899, "category": "tech"},
        pain_points=["Stock Instability", "Shipping Delays"]
    )
    sample_intensity = agent.determine_intensity(
        "Luxury Smartwatch",
        "Premium wearable technology",
        product_info={"price": 899, "category": "tech"},
        pain_points=["Stock Instability", "Shipping Delays"]
    )
    print(f"[VERIFIED] Regression Score: {sample_score:.2f} -> Category: '{sample_intensity}'")


def _cli():
    parser = argparse.ArgumentParser(description="Train scarcity intensity regressor")
    parser.add_argument("--tsv-files", type=str, help="Comma-separated paths to TSV files to ingest for training")
    parser.add_argument("--sample-json", type=str, help="Optional sample_products.json to lookup prices/categories")
    parser.add_argument("--max-samples", type=int, default=20000, help="Maximum number of rows to sample from TSVs")
    args = parser.parse_args()

    if args.tsv_files:
        paths = [p.strip() for p in args.tsv_files.split(",") if p.strip()]
        train_from_tsvs(paths, sample_json=args.sample_json, max_samples=args.max_samples)
    else:
        train_and_save_regression_pkl_model()


if __name__ == "__main__":
    _cli()
