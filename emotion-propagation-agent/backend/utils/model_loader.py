import os
from dataclasses import dataclass

import joblib
import numpy as np


@dataclass(frozen=True)
class EmotionModelBundle:
    model: object | None
    label_binarizer: object | None
    loaded: bool
    warning: str | None = None


_BUNDLE: EmotionModelBundle | None = None


def _sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -50, 50)
    return 1 / (1 + np.exp(-x))


def load_emotion_model(models_dir: str | None = None) -> EmotionModelBundle:
    global _BUNDLE
    if models_dir is None:
        models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    models_dir = os.path.abspath(models_dir)

    classifier_path = os.path.join(models_dir, "emotion_classifier_tfidf_logreg.pkl")
    lb_path = os.path.join(models_dir, "emotion_label_binarizer.pkl")

    if not os.path.exists(classifier_path) or not os.path.exists(lb_path):
        _BUNDLE = EmotionModelBundle(
            model=None,
            label_binarizer=None,
            loaded=False,
            warning="Model files not found. Please place the trained .pkl files inside backend/models.",
        )
        return _BUNDLE

    try:
        model = joblib.load(classifier_path)
        label_binarizer = joblib.load(lb_path)
        _BUNDLE = EmotionModelBundle(model=model, label_binarizer=label_binarizer, loaded=True, warning=None)
        return _BUNDLE
    except Exception as exc:
        _BUNDLE = EmotionModelBundle(
            model=None,
            label_binarizer=None,
            loaded=False,
            warning=f"Failed to load model files: {exc}",
        )
        return _BUNDLE


def predict_emotions(text: str, top_k: int = 5) -> list[dict]:
    bundle = _BUNDLE
    if bundle is None or not bundle.loaded or bundle.model is None or bundle.label_binarizer is None:
        return []

    if text is None:
        text = ""

    try:
        if hasattr(bundle.model, "predict_proba"):
            scores = bundle.model.predict_proba([text])
            scores = np.asarray(scores)
            if scores.ndim == 3:
                scores = scores[0]
            if scores.ndim == 2 and scores.shape[0] == 1:
                scores = scores[0]
            probs = scores.astype(float)
        elif hasattr(bundle.model, "decision_function"):
            raw = bundle.model.decision_function([text])
            raw = np.asarray(raw)
            if raw.ndim == 2 and raw.shape[0] == 1:
                raw = raw[0]
            probs = _sigmoid(raw.astype(float))
        else:
            predicted = bundle.model.predict([text])
            predicted = np.asarray(predicted)
            if predicted.ndim == 2 and predicted.shape[0] == 1:
                predicted = predicted[0]
            probs = predicted.astype(float)

        classes = None
        if hasattr(bundle.label_binarizer, "classes_"):
            classes = list(getattr(bundle.label_binarizer, "classes_", []))
        elif isinstance(bundle.label_binarizer, (list, tuple)):
            classes = list(bundle.label_binarizer)
        elif isinstance(bundle.label_binarizer, dict):
            if "classes_" in bundle.label_binarizer:
                classes = list(bundle.label_binarizer.get("classes_", []))
            elif "classes" in bundle.label_binarizer:
                classes = list(bundle.label_binarizer.get("classes", []))

        if not classes:
            return []

        classes = [str(c) for c in classes]
        probs = np.asarray(probs).reshape(-1)

        k = max(1, min(int(top_k), len(classes)))
        top_idx = np.argsort(-probs)[:k]

        results: list[dict] = []
        for idx in top_idx:
            emotion = classes[int(idx)]
            score = float(probs[int(idx)])
            score = max(0.0, min(1.0, score))
            results.append({"emotion": emotion, "score": round(score, 4)})

        return results
    except Exception:
        return []
