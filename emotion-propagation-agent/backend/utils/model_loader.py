import json
import os
from dataclasses import dataclass

import numpy as np

try:
    import torch
    from torch.nn.functional import softmax
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    IMPORT_WARNING = None
except Exception as exc:  # pragma: no cover - depends on local environment
    torch = None
    softmax = None
    AutoModelForSequenceClassification = None
    AutoTokenizer = None
    IMPORT_WARNING = f"Transformers dependencies are not available: {exc}"


MODEL_LOADED = False
MODEL_WARNING = None
MODEL_DIRNAME = "roberta_emotion_model"


@dataclass(frozen=True)
class EmotionModelBundle:
    tokenizer: object | None
    model: object | None
    labels: list[str]
    loaded: bool
    warning: str | None = None


_BUNDLE: EmotionModelBundle | None = None


def _normalize_label_mapping(raw_mapping, config) -> list[str]:
    if isinstance(raw_mapping, list):
        return [str(item) for item in raw_mapping]

    if isinstance(raw_mapping, dict):
        if all(str(k).isdigit() for k in raw_mapping.keys()):
            return [str(label) for _, label in sorted(raw_mapping.items(), key=lambda item: int(item[0]))]
        if all(isinstance(value, int) for value in raw_mapping.values()):
            return [str(label) for label, _ in sorted(raw_mapping.items(), key=lambda item: int(item[1]))]

    id2label = getattr(config, "id2label", None)
    if isinstance(id2label, dict) and id2label:
        if all(str(k).isdigit() for k in id2label.keys()):
            return [str(label) for _, label in sorted(id2label.items(), key=lambda item: int(item[0]))]
        return [str(label) for _, label in sorted(id2label.items(), key=lambda item: int(item[0]))]

    num_labels = getattr(config, "num_labels", 0) or 0
    return [f"label_{index}" for index in range(int(num_labels))]


def load_emotion_model(models_dir: str | None = None) -> EmotionModelBundle:
    global _BUNDLE, MODEL_LOADED, MODEL_WARNING

    if models_dir is None:
        models_dir = os.path.join(os.path.dirname(__file__), "..", "models", MODEL_DIRNAME)
    model_dir = os.path.abspath(models_dir)

    if IMPORT_WARNING:
        MODEL_LOADED = False
        MODEL_WARNING = IMPORT_WARNING
        _BUNDLE = EmotionModelBundle(tokenizer=None, model=None, labels=[], loaded=False, warning=MODEL_WARNING)
        return _BUNDLE

    if not os.path.isdir(model_dir):
        MODEL_LOADED = False
        MODEL_WARNING = "RoBERTa model folder not found in backend/models/roberta_emotion_model"
        _BUNDLE = EmotionModelBundle(tokenizer=None, model=None, labels=[], loaded=False, warning=MODEL_WARNING)
        return _BUNDLE

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
        model.eval()

        label_mapping_path = os.path.join(model_dir, "label_mapping.json")
        raw_mapping = None
        if os.path.exists(label_mapping_path):
            with open(label_mapping_path, "r", encoding="utf-8") as file:
                raw_mapping = json.load(file)

        labels = _normalize_label_mapping(raw_mapping, model.config)
        MODEL_LOADED = True
        MODEL_WARNING = None
        _BUNDLE = EmotionModelBundle(tokenizer=tokenizer, model=model, labels=labels, loaded=True, warning=None)
        return _BUNDLE
    except Exception as exc:
        MODEL_LOADED = False
        MODEL_WARNING = f"Failed to load RoBERTa emotion model: {exc}"
        _BUNDLE = EmotionModelBundle(tokenizer=None, model=None, labels=[], loaded=False, warning=MODEL_WARNING)
        return _BUNDLE


def predict_emotions(text: str, top_k: int = 5) -> dict:
    bundle = _BUNDLE
    if bundle is None or not bundle.loaded or bundle.model is None or bundle.tokenizer is None:
        return {"predictions": [], "top_emotion": None, "warning": MODEL_WARNING}

    try:
        encoded = bundle.tokenizer(
            text or "",
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=256,
        )

        with torch.no_grad():
            outputs = bundle.model(**encoded)
            probabilities = softmax(outputs.logits, dim=-1)[0].detach().cpu().numpy()

        scores = np.asarray(probabilities).reshape(-1)
        labels = bundle.labels or [f"label_{index}" for index in range(len(scores))]
        k = max(1, min(int(top_k), len(scores), len(labels)))
        top_indexes = np.argsort(-scores)[:k]

        predictions = []
        for index in top_indexes:
            predictions.append(
                {
                    "emotion": str(labels[int(index)]),
                    "score": round(float(scores[int(index)]), 4),
                }
            )

        top_emotion = predictions[0]["emotion"] if predictions else None
        return {"predictions": predictions, "top_emotion": top_emotion, "warning": MODEL_WARNING}
    except Exception as exc:
        return {"predictions": [], "top_emotion": None, "warning": f"RoBERTa inference failed: {exc}"}
