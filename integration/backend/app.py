"""
app.py — Integrated System API
-------------------------------------------------------------------
The combined system: Emotion Propagation Agent (Component 2) +
Loss Framing Agent (Component 4), connected by pipeline.py.

Run from the integration/ folder:   python app.py
Exposes:
    GET  /health        -> quick check the server is up
    POST /api/pipeline  -> runs the full combined pipeline
-------------------------------------------------------------------
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# .env sits in this same integration/ folder
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from utils.model_loader import load_emotion_model
from utils.pipeline import run_pipeline

app = Flask(__name__)
CORS(app)

# Load the RoBERTa emotion model ONCE at startup.
# model_loader looks for ../models/roberta_emotion_model relative to utils/,
# which resolves to integration/models/roberta_emotion_model.
load_emotion_model()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/pipeline", methods=["POST"])
def api_pipeline():
    data = request.get_json(force=True) or {}
    try:
        result = run_pipeline(
            product_name=data.get("product_name", ""),
            category=data.get("category", ""),
            target_audience=data.get("target_audience", ""),
            features=data.get("features", ""),
            target_emotion=data.get("target_emotion") or None,
        )
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
