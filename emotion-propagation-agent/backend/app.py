import os
from datetime import datetime, timezone

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load GROQ_API_KEY (and anything else) from a .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from utils import model_loader
from utils.emotion_agent import (
    PRODUCT_CATEGORIES,
    PROJECT_EMOTIONS,
    build_marketing_prompt,
    generate_with_groq,
    get_visual_suggestions,
    select_emotion_for_category,
)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}})

model_loader.load_emotion_model()

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "outputs")
USER_STUDY_CSV = os.path.join(OUTPUTS_DIR, "user_study_responses.csv")
MAX_ATTEMPTS = 3
# A generation counts as a match if the target emotion lands within the top-K
# predictions (not only #1). Set to 1 for strict top-1 matching, 2 or 3 to relax.
MATCH_TOP_K = 1


def _json_error(message: str, status_code: int = 400):
    return jsonify({"error": message}), status_code


def _get_json():
    return request.get_json(silent=True) or {}


def _is_valid_scale(value):
    try:
        numeric_value = int(value)
        return 1 <= numeric_value <= 5
    except Exception:
        return False


def _normalize_generation_payload(payload: dict) -> dict:
    category = payload.get("category", payload.get("product_category", ""))
    features = payload.get("features", payload.get("key_features", ""))

    if isinstance(features, (list, tuple)):
        features = ", ".join(str(item).strip() for item in features if str(item).strip())

    return {
        "product_name": str(payload.get("product_name", "")).strip(),
        "category": str(category or "").strip().title(),
        "target_audience": str(payload.get("target_audience", "")).strip(),
        "features": str(features or "").strip(),
        "target_emotion": str(payload.get("target_emotion", "")).strip().lower(),
    }


def _target_score(predictions, target_emotion):
    """Return the model's score for the target emotion (0.0 if not present)."""
    for prediction in predictions:
        if prediction.get("emotion") == target_emotion:
            try:
                return float(prediction.get("score", 0.0) or 0.0)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def _build_generation_result(data: dict, target_emotion: str) -> dict:
    previous_failure = None
    attempt_history = []
    final_warning = model_loader.MODEL_WARNING

    # We keep the BEST attempt (the one where the target emotion scored highest),
    # not simply the last attempt. A full match always wins.
    best_record = None
    best_target_score = -1.0

    for attempt in range(1, MAX_ATTEMPTS + 1):
        prompt = build_marketing_prompt(
            product_name=data["product_name"],
            category=data["category"],
            target_audience=data["target_audience"],
            features=data["features"],
            target_emotion=target_emotion,
            previous_failure=previous_failure,
        )
        generated_message = generate_with_groq(prompt)
        validation = model_loader.predict_emotions(generated_message, top_k=5)

        predictions = validation.get("predictions", [])
        top_emotion = validation.get("top_emotion")
        warning = validation.get("warning")
        final_warning = warning

        # Where does the target emotion rank among predictions? (1 = top)
        target_rank = None
        for position, prediction in enumerate(predictions, start=1):
            if prediction.get("emotion") == target_emotion:
                target_rank = position
                break

        top_k_emotions = [p.get("emotion") for p in predictions[:MATCH_TOP_K]]
        matched_strict = bool(model_loader.MODEL_LOADED and top_emotion == target_emotion)
        matched = bool(model_loader.MODEL_LOADED and target_emotion in top_k_emotions)
        this_target_score = _target_score(predictions, target_emotion)

        record = {
            "attempt": attempt,
            "generated_message": generated_message,
            "top_emotion": top_emotion,
            "matched": matched,
            "matched_strict": matched_strict,
            "target_rank": target_rank,
            "target_score": round(this_target_score, 4),
            "predictions": predictions,
            "warning": warning,
        }
        attempt_history.append(record)

        # Track the best attempt so far by how strongly the target emotion scored.
        if this_target_score > best_target_score:
            best_target_score = this_target_score
            best_record = record

        if matched:
            # A match is the best possible outcome; keep it and stop.
            best_record = record
            break

        previous_failure = top_emotion
        if not model_loader.MODEL_LOADED:
            break

    # Choose the final result: the best attempt (or the last one as a fallback).
    chosen = best_record if best_record is not None else (attempt_history[-1] if attempt_history else None)

    if chosen:
        final_message = chosen["generated_message"]
        final_predictions = chosen["predictions"]
        final_top_emotion = chosen["top_emotion"]
        validation_success = bool(chosen.get("matched"))
        validation_success_strict = bool(chosen.get("matched_strict"))
        final_target_rank = chosen.get("target_rank")
    else:
        final_message = ""
        final_predictions = []
        final_top_emotion = None
        validation_success = False
        validation_success_strict = False
        final_target_rank = None

    response = {
        "product_name": data["product_name"],
        "category": data["category"],
        "target_audience": data["target_audience"],
        "features": data["features"],
        "target_emotion": target_emotion,
        "generated_message": final_message,
        "emotion_predictions": final_predictions,
        "top_emotion": final_top_emotion,
        "validation_success": validation_success,
        "validation_success_strict": validation_success_strict,
        "target_rank": final_target_rank,
        "match_top_k": MATCH_TOP_K,
        "attempts_used": len(attempt_history),
        "max_attempts": MAX_ATTEMPTS,
        "attempt_history": attempt_history,
        "visual_suggestions": get_visual_suggestions(target_emotion),
    }

    if final_warning:
        response["warning"] = final_warning

    return response


@app.get("/")
def root():
    return jsonify(
        {
            "message": "Emotion Propagation Agent API is running",
            "component": "Component 2",
            "model": "RoBERTa emotion classifier",
            "generation": "LLM-based generation with validation loop",
            "status": "active",
        }
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": model_loader.MODEL_LOADED,
            "model_warning": model_loader.MODEL_WARNING,
            "allowed_categories": PRODUCT_CATEGORIES,
            "allowed_emotions": PROJECT_EMOTIONS,
        }
    )


@app.post("/api/reload-model")
def api_reload_model():
    bundle = model_loader.load_emotion_model()
    return jsonify({"message": "Model reloaded", "model_loaded": bundle.loaded, "warning": bundle.warning})


@app.post("/api/predict-emotion")
def api_predict_emotion():
    payload = _get_json()
    text = str(payload.get("text", "")).strip()
    if not text:
        return _json_error("Missing required field: text", 400)

    result = model_loader.predict_emotions(text, top_k=5)
    return jsonify({"text": text, **result})


@app.post("/api/generate-message")
def api_generate_message():
    data = _normalize_generation_payload(_get_json())
    if not data["product_name"]:
        return _json_error("Missing required field: product_name", 400)
    if not data["category"]:
        return _json_error("Missing required field: category", 400)
    if data["category"] not in PRODUCT_CATEGORIES:
        return _json_error(f"Invalid category. Allowed: {', '.join(PRODUCT_CATEGORIES)}", 400)

    target_emotion = data["target_emotion"] or select_emotion_for_category(data["category"])
    if target_emotion not in PROJECT_EMOTIONS:
        return _json_error(f"Invalid target_emotion. Allowed: {', '.join(PROJECT_EMOTIONS)}", 400)

    try:
        result = _build_generation_result(data, target_emotion)
        return jsonify(result)
    except RuntimeError as exc:
        return _json_error(str(exc), 503)
    except Exception as exc:
        return _json_error(f"Failed to generate content: {exc}", 500)


@app.post("/api/generate-variations")
def api_generate_variations():
    data = _normalize_generation_payload(_get_json())
    if not data["product_name"]:
        return _json_error("Missing required field: product_name", 400)
    if not data["category"]:
        return _json_error("Missing required field: category", 400)
    if data["category"] not in PRODUCT_CATEGORIES:
        return _json_error(f"Invalid category. Allowed: {', '.join(PRODUCT_CATEGORIES)}", 400)

    payload = _get_json()
    target_emotions = payload.get("target_emotions") or []
    if not isinstance(target_emotions, list) or not target_emotions:
        return _json_error("target_emotions must be a non-empty list.", 400)

    normalized_emotions = []
    for emotion in target_emotions:
        emotion_key = str(emotion).strip().lower()
        if emotion_key in PROJECT_EMOTIONS and emotion_key not in normalized_emotions:
            normalized_emotions.append(emotion_key)

    if not normalized_emotions:
        return _json_error(f"No valid target_emotions provided. Allowed: {', '.join(PROJECT_EMOTIONS)}", 400)

    variations = []
    try:
        for emotion in normalized_emotions:
            result = _build_generation_result(data, emotion)
            variations.append(
                {
                    "target_emotion": emotion,
                    "generated_message": result["generated_message"],
                    "top_emotion": result["top_emotion"],
                    "validation_success": result["validation_success"],
                    "attempts_used": result["attempts_used"],
                    "max_attempts": result["max_attempts"],
                    "emotion_predictions": result["emotion_predictions"],
                    "attempt_history": result["attempt_history"],
                    "visual_suggestions": result["visual_suggestions"],
                    "warning": result.get("warning"),
                }
            )
    except RuntimeError as exc:
        return _json_error(str(exc), 503)
    except Exception as exc:
        return _json_error(f"Failed to generate variations: {exc}", 500)

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
    missing = [field for field in required if field not in payload]
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
    invalid_scales = [field for field in scale_fields if not _is_valid_scale(payload.get(field))]
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
        return jsonify(
            {
                "total_responses": 0,
                "best_emotion": None,
                "summary": [],
                "average_attempts_used": None,
                "validation_success_rate": None,
            }
        )

    df = pd.read_csv(USER_STUDY_CSV)
    if df.empty or "target_emotion" not in df.columns:
        return jsonify(
            {
                "total_responses": 0,
                "best_emotion": None,
                "summary": [],
                "average_attempts_used": None,
                "validation_success_rate": None,
            }
        )

    numeric_columns = [
        "emotion_strength",
        "persuasiveness",
        "engagement_interest",
        "trustworthiness",
        "attempts_used",
    ]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    if "validation_success" in df.columns:
        df["validation_success_numeric"] = (
            df["validation_success"]
            .astype(str)
            .str.lower()
            .map({"true": 1.0, "false": 0.0, "1": 1.0, "0": 0.0})
        )
    else:
        df["validation_success_numeric"] = pd.NA

    grouped = (
        df.groupby("target_emotion", dropna=False)
        .agg(
            average_emotion_strength=("emotion_strength", "mean"),
            average_persuasiveness=("persuasiveness", "mean"),
            average_engagement_interest=("engagement_interest", "mean"),
            average_trustworthiness=("trustworthiness", "mean"),
            average_attempts_used=("attempts_used", "mean"),
            validation_success_rate=("validation_success_numeric", "mean"),
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
                "average_attempts_used": round(float(row["average_attempts_used"]), 4) if pd.notna(row["average_attempts_used"]) else None,
                "validation_success_rate": round(float(row["validation_success_rate"]), 4) if pd.notna(row["validation_success_rate"]) else None,
            }
        )

    best_emotion = None
    if not grouped.empty and "average_engagement_interest" in grouped.columns:
        grouped_sorted = grouped.sort_values(["average_engagement_interest", "average_persuasiveness"], ascending=False)
        best_emotion = str(grouped_sorted.iloc[0]["target_emotion"])

    average_attempts_used = None
    if "attempts_used" in df.columns and df["attempts_used"].notna().any():
        average_attempts_used = round(float(df["attempts_used"].mean()), 4)

    validation_success_rate = None
    if df["validation_success_numeric"].notna().any():
        validation_success_rate = round(float(df["validation_success_numeric"].mean()), 4)

    return jsonify(
        {
            "total_responses": int(len(df)),
            "best_emotion": best_emotion,
            "summary": summary,
            "average_attempts_used": average_attempts_used,
            "validation_success_rate": validation_success_rate,
        }
    )


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