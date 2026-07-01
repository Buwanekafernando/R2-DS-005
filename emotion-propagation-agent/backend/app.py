import os
from datetime import datetime, timezone

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.emotion_agent import (
    VALID_PRODUCT_CATEGORIES,
    VALID_TARGET_EMOTIONS,
    generate_full_strategy,
)
from utils.model_loader import load_emotion_model, predict_emotions


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})

MODEL_BUNDLE = load_emotion_model()

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
USER_STUDY_CSV = os.path.join(OUTPUTS_DIR, "user_study_responses.csv")


def _json_error(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


def _get_json():
    return request.get_json(silent=True) or {}


def _is_valid_scale(value):
    try:
        v = int(value)
        return 1 <= v <= 5
    except Exception:
        return False


@app.get("/")
def root():
    return jsonify({"message": "Emotion Propagation Agent API is running", "component": "Component 2", "status": "active"})


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "model_loaded": bool(MODEL_BUNDLE.loaded)})


@app.post("/api/reload-model")
def api_reload_model():
    global MODEL_BUNDLE
    MODEL_BUNDLE = load_emotion_model()
    return jsonify({"message": "Model reloaded", "model_loaded": bool(MODEL_BUNDLE.loaded), "warning": MODEL_BUNDLE.warning})


@app.post("/api/predict-emotion")
def api_predict_emotion():
    payload = _get_json()
    text = payload.get("text")
    if not text or not str(text).strip():
        return _json_error("Missing required field: text", 400)

    if not MODEL_BUNDLE.loaded:
        return jsonify(
            {
                "text": str(text),
                "predictions": [],
                "warning": MODEL_BUNDLE.warning or "Model not loaded.",
            }
        )

    try:
        predictions = predict_emotions(str(text), top_k=5)
        return jsonify({"text": str(text), "predictions": predictions})
    except Exception:
        return _json_error("Prediction failed.", 500)


@app.post("/api/generate-message")
def api_generate_message():
    payload = _get_json()
    required = ["product_name", "product_category", "target_audience", "key_features", "target_emotion"]
    missing = [k for k in required if k not in payload]
    if missing:
        return _json_error(f"Missing required fields: {', '.join(missing)}", 400)

    product_category = str(payload.get("product_category", "general")).strip().lower()
    if product_category not in VALID_PRODUCT_CATEGORIES:
        return _json_error(f"Invalid product_category. Allowed: {', '.join(VALID_PRODUCT_CATEGORIES)}", 400)

    target_emotion = str(payload.get("target_emotion", "neutral")).strip().lower()
    if target_emotion not in VALID_TARGET_EMOTIONS:
        return _json_error(f"Invalid target_emotion. Allowed: {', '.join(VALID_TARGET_EMOTIONS)}", 400)

    strategy = generate_full_strategy(payload)
    generated_message = strategy.get("generated_message", "")

    if MODEL_BUNDLE.loaded:
        predictions = predict_emotions(generated_message, top_k=5)
        strategy["emotion_predictions"] = predictions
    else:
        strategy["emotion_predictions"] = []
        strategy["warning"] = MODEL_BUNDLE.warning or "Model not loaded."

    return jsonify(strategy)


@app.post("/api/generate-variations")
def api_generate_variations():
    payload = _get_json()
    required = ["product_name", "product_category", "target_audience", "key_features", "target_emotions"]
    missing = [k for k in required if k not in payload]
    if missing:
        return _json_error(f"Missing required fields: {', '.join(missing)}", 400)

    product_category = str(payload.get("product_category", "general")).strip().lower()
    if product_category not in VALID_PRODUCT_CATEGORIES:
        return _json_error(f"Invalid product_category. Allowed: {', '.join(VALID_PRODUCT_CATEGORIES)}", 400)

    target_emotions = payload.get("target_emotions") or []
    if not isinstance(target_emotions, list) or not target_emotions:
        return _json_error("target_emotions must be a non-empty list.", 400)

    normalized = []
    for e in target_emotions:
        e_norm = str(e).strip().lower()
        if e_norm in VALID_TARGET_EMOTIONS and e_norm not in normalized:
            normalized.append(e_norm)

    if not normalized:
        return _json_error(f"No valid target_emotions provided. Allowed: {', '.join(VALID_TARGET_EMOTIONS)}", 400)

    variations = []
    for emotion in normalized:
        variant_payload = dict(payload)
        variant_payload["target_emotion"] = emotion
        strategy = generate_full_strategy(variant_payload)
        generated_message = strategy.get("generated_message", "")
        item = {"target_emotion": emotion, "generated_message": generated_message, "cta": strategy.get("cta"), "tone": strategy.get("tone")}

        if MODEL_BUNDLE.loaded:
            item["emotion_predictions"] = predict_emotions(generated_message, top_k=5)
        else:
            item["emotion_predictions"] = []
            item["warning"] = MODEL_BUNDLE.warning or "Model not loaded."

        variations.append(item)

    return jsonify({"variations": variations})


@app.post("/api/user-study")
def api_user_study():
    payload = _get_json()
    required = [
        "participant_id",
        "product_name",
        "target_emotion",
        "generated_message",
        "perceived_emotion",
        "emotion_strength",
        "message_clarity",
        "persuasiveness",
        "trustworthiness",
        "engagement_interest",
        "purchase_interest",
        "comments",
    ]
    missing = [k for k in required if k not in payload]
    if missing:
        return _json_error(f"Missing required fields: {', '.join(missing)}", 400)

    scale_fields = [
        "emotion_strength",
        "message_clarity",
        "persuasiveness",
        "trustworthiness",
        "engagement_interest",
        "purchase_interest",
    ]
    invalid_scales = [f for f in scale_fields if not _is_valid_scale(payload.get(f))]
    if invalid_scales:
        return _json_error(f"Invalid rating(s). Must be 1-5: {', '.join(invalid_scales)}", 400)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    record = dict(payload)
    record["created_at"] = datetime.now(timezone.utc).isoformat()

    df_new = pd.DataFrame([record])
    if os.path.exists(USER_STUDY_CSV):
        try:
            df_existing = pd.read_csv(USER_STUDY_CSV)
            df_out = pd.concat([df_existing, df_new], ignore_index=True)
        except Exception:
            df_out = df_new
    else:
        df_out = df_new

    df_out.to_csv(USER_STUDY_CSV, index=False)
    return jsonify({"message": "User study response saved successfully"})


@app.get("/api/user-study-summary")
def api_user_study_summary():
    if not os.path.exists(USER_STUDY_CSV):
        return jsonify({"total_responses": 0, "best_emotion": None, "summary": []})

    df = pd.read_csv(USER_STUDY_CSV)
    if df.empty or "target_emotion" not in df.columns:
        return jsonify({"total_responses": 0, "best_emotion": None, "summary": []})

    for col in ["emotion_strength", "persuasiveness", "engagement_interest", "trustworthiness"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    grouped = (
        df.groupby("target_emotion", dropna=False)
        .agg(
            average_emotion_strength=("emotion_strength", "mean"),
            average_persuasiveness=("persuasiveness", "mean"),
            average_engagement_interest=("engagement_interest", "mean"),
            average_trustworthiness=("trustworthiness", "mean"),
        )
        .reset_index()
    )

    summary = []
    for _, row in grouped.iterrows():
        summary.append(
            {
                "target_emotion": str(row["target_emotion"]),
                "average_emotion_strength": round(float(row["average_emotion_strength"]), 4) if pd.notna(row["average_emotion_strength"]) else None,
                "average_persuasiveness": round(float(row["average_persuasiveness"]), 4) if pd.notna(row["average_persuasiveness"]) else None,
                "average_engagement_interest": round(float(row["average_engagement_interest"]), 4) if pd.notna(row["average_engagement_interest"]) else None,
                "average_trustworthiness": round(float(row["average_trustworthiness"]), 4) if pd.notna(row["average_trustworthiness"]) else None,
            }
        )

    best_emotion = None
    if not grouped.empty and "average_engagement_interest" in grouped.columns:
        grouped_sorted = grouped.sort_values(["average_engagement_interest", "average_persuasiveness"], ascending=False)
        best_emotion = str(grouped_sorted.iloc[0]["target_emotion"])

    return jsonify({"total_responses": int(len(df)), "best_emotion": best_emotion, "summary": summary})


@app.get("/api/user-study-responses")
def api_user_study_responses():
    if not os.path.exists(USER_STUDY_CSV):
        return jsonify({"responses": []})
    try:
        df = pd.read_csv(USER_STUDY_CSV)
        return jsonify({"responses": df.fillna("").to_dict(orient="records")})
    except Exception:
        return jsonify({"responses": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
