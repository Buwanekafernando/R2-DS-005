from __future__ import annotations

import os
from typing import Any

import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# If this model ever stops working, just change this one line.
# Alternatives: "openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"

PRODUCT_CATEGORIES = [
    "Baby",
    "Beauty",
    "Apparel",
    "Electronics",
    "Sports",
    "Pet",
    "Groceries",
]

PROJECT_EMOTIONS = [
    "joy",
    "excitement",
    "trust",
    "confidence",
    "curiosity",
    "relief",
    "admiration",
    "neutral",
]

CATEGORY_EMOTION_MAP = {
    "Baby": ["trust", "relief", "joy"],
    "Beauty": ["confidence", "trust", "joy"],
    "Apparel": ["joy", "excitement"],
    "Electronics": ["excitement", "joy"],
    "Sports": ["excitement", "confidence", "trust"],
    "Pet": ["joy", "trust"],
    "Groceries": ["trust", "relief", "joy"],
}

VISUAL_SUGGESTIONS = {
    "joy": {
        "palette": "Warm yellow, soft orange, red",
        "image_style": "High-brightness painterly texture, warm golden-yellow lighting, vivid orange highlights, soft expressive focus",
        "layout_mood": "High positive affect, warm, luminous, and emotionally synesthetic",
    },
    "excitement": {
        "palette": "Red, orange, purple",
        "image_style": "High-risk extreme sports, thrill/free-motion action shots, intimate/passionate human interactions, intense high-arousal scenes",
        "layout_mood": "Thrill-seeking, high-impact, passionate, and fast-paced",
    },
    "trust": {
        "palette": "Blue, Pink, navy",
        "image_style": "High-realism human photography, authentic user-generated content (UGC), clear product feature shots",
        "layout_mood": "High media richness, transparent, predictable, and credible",
    },
    "confidence": {
        "palette": "Purple,black, gold, deep blue",
        "image_style": "Strong upright posture, neat professional clothing, modern background with sharp angles",
        "layout_mood": "Bold, strong, and modern",
    },
    "curiosity": {
        "palette": "Purple, teal, light grey",
        "image_style": "Unusual product combinations, dreamlike settings, visual puzzles, unexpected angles, creative macro close-ups",
        "layout_mood": "Playful, mystery-filled, intriguing, and mind-bending",
    },
    "relief": {
        "palette": "Soft green, light blue, white",
        "image_style": "Serene natural landscapes, soft open scenery, wholesome human interactions, relaxed users in calm settings",
        "layout_mood": "Soothing, harmonious, spacious, and reassuring",
    },
    "admiration": {
        "palette": "Gold, black, ivory",
        "image_style": "Premium product shots, elegant backgrounds, refined details",
        "layout_mood": "Elegant, premium, and aspirational",
    },
    "neutral": {
        "palette": "Grey, white, brown",
        "image_style": "Static, un-animated product photography with balanced composition, moderate color saturation, and clean, uncluttered visual backgrounds",
        "layout_mood": "Informative, visual-balance focused, structured, and emotionally neutral",
    },
}


def select_emotion_for_category(category: str | None) -> str:
    normalized = str(category or "").strip().title()
    recommendations = CATEGORY_EMOTION_MAP.get(normalized, CATEGORY_EMOTION_MAP["Beauty"])
    return recommendations[0]


def _normalize_features(features: Any) -> str:
    if isinstance(features, str):
        return features.strip()
    if isinstance(features, (list, tuple)):
        return ", ".join(str(item).strip() for item in features if str(item).strip())
    return str(features or "").strip()


def generate_with_groq(prompt: str, model_name: str = DEFAULT_GROQ_MODEL) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it to a .env file or your environment variables."
        )

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_completion_tokens": 300,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Groq LLM service is not available. Check your API key and internet connection."
        ) from exc
    except ValueError as exc:
        raise RuntimeError("Groq returned an invalid response.") from exc

    try:
        message = str(payload["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Groq returned an unexpected response format.") from exc

    if not message:
        raise RuntimeError("Groq returned an empty response.")
    return message


# Per-emotion writing guidance. "convey" tells Groq what to express;
# "avoid" pushes it away from near-twin emotions the classifier confuses it with.
EMOTION_SIGNALS = {
    "joy": {
        "convey": "happiness, warmth, delight, and feeling genuinely good in the moment",
        "avoid": "technical specs, a serious tone, or emphasis on how impressive the product is",
    },
    "excitement": {
        "convey": "high energy, anticipation, thrill, and a can't-wait sense of urgency",
        "avoid": "calm, slow, or reassuring language",
    },
    "trust": {
        "convey": "reliability, safety, dependability, and proven, honest quality",
        "avoid": "hype, exaggeration, or high-energy excitement",
    },
    "confidence": {
        "convey": "a forward-looking, self-assured belief that things will keep getting better for the reader \u2014 hopeful momentum, reaching goals, moving forward, a brighter result ahead, and the reader feeling capable of achieving it",
        "avoid": "praising how impressive, stunning, elegant, radiant, or premium the product or result is (that reads as admiration); do NOT use words like stunning, radiant, unparalleled, standout, or flawless \u2014 focus on the reader's forward progress and self-belief, not on how impressive the product looks",
    },
    "curiosity": {
        "convey": "intrigue, a sense of discovery, and an open question that makes the reader want to explore",
        "avoid": "revealing everything upfront or making flat, definitive statements",
    },
    "relief": {
        "convey": "ease, calm, stress lifting away, and things finally becoming simple",
        "avoid": "high energy, urgency, or excitement",
    },
    "admiration": {
        "convey": "being impressed by the product's craftsmanship, quality, and standout excellence",
        "avoid": "focusing on the reader's own capability or control (that reads as confidence); keep the spotlight on how remarkable the PRODUCT itself is",
    },
    "neutral": {
        "convey": "clear, factual, informative product details in a balanced tone",
        "avoid": "strong emotional language of any kind",
    },
}


def build_marketing_prompt(
    product_name: str,
    category: str,
    target_audience: str,
    features: Any,
    target_emotion: str,
    previous_failure: str | None = None,
) -> str:
    feature_text = _normalize_features(features) or "practical everyday benefits"
    signals = EMOTION_SIGNALS.get(target_emotion, EMOTION_SIGNALS["neutral"])

    correction = ""
    if previous_failure:
        correction = (
            f'The previous message was detected as "{previous_failure}" instead of "{target_emotion}". '
            f'Rewrite it with clearer "{target_emotion}" cues.\n'
        )
        failure_signals = EMOTION_SIGNALS.get(previous_failure)
        if failure_signals:
            correction += (
                f'This time, avoid language that expresses "{previous_failure}" '
                f'({failure_signals["convey"]}).\n'
            )

    return (
        "You are writing a concise product marketing message for a research prototype.\n"
        "Generate one short marketing message.\n"
        f"The message must strongly express the target emotion: {target_emotion}.\n"
        f"To express {target_emotion}, convey: {signals['convey']}.\n"
        f"Avoid: {signals['avoid']}.\n"
        "Do not mention the emotion name directly.\n"
        "Keep the message between 35 and 60 words.\n"
        "Do not use bullet points.\n"
        "Do not include hashtags.\n"
        "Do not make false claims.\n"
        "Product category must be one of Baby, Beauty, Apparel, Electronics, Sports, Pet, Groceries.\n"
        "Return only the marketing message.\n"
        f"{correction}"
        f"Product name: {product_name}\n"
        f"Product category: {category}\n"
        f"Target audience: {target_audience}\n"
        f"Key features: {feature_text}\n"
    )


def get_visual_suggestions(target_emotion: str) -> dict[str, str]:
    key = str(target_emotion or "neutral").strip().lower()
    return VISUAL_SUGGESTIONS.get(key, VISUAL_SUGGESTIONS["neutral"])