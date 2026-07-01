from __future__ import annotations

from typing import Any


PRODUCT_CATEGORY_EMOTION_MAP: dict[str, list[str]] = {
    "fashion": ["confidence", "excitement", "admiration"],
    "beauty": ["confidence", "joy", "admiration"],
    "education": ["optimism", "confidence", "curiosity"],
    "technology": ["excitement", "trust", "curiosity"],
    "healthcare": ["trust", "relief", "confidence"],
    "fitness": ["excitement", "confidence", "optimism"],
    "food": ["joy", "relief", "trust"],
    "travel": ["excitement", "joy", "curiosity"],
    "finance": ["trust", "confidence", "relief"],
    "insurance": ["trust", "relief", "confidence"],
    "general": ["joy", "trust", "excitement"],
}


EMOTION_STYLE_GUIDES: dict[str, dict[str, Any]] = {
    "joy": {"tone": "positive, warm, cheerful", "colors": ["yellow", "orange", "white"], "cta": "Enjoy it today"},
    "excitement": {
        "tone": "energetic, bold, enthusiastic",
        "colors": ["red", "orange", "purple"],
        "cta": "Discover it now",
    },
    "trust": {"tone": "reliable, calm, professional", "colors": ["blue", "white", "navy"], "cta": "Choose with confidence"},
    "confidence": {
        "tone": "empowering, clear, motivating",
        "colors": ["blue", "purple", "white"],
        "cta": "Start with confidence today",
    },
    "curiosity": {
        "tone": "intriguing, thoughtful, exploratory",
        "colors": ["purple", "teal", "dark blue"],
        "cta": "Explore what is possible",
    },
    "optimism": {"tone": "hopeful, future-focused, encouraging", "colors": ["green", "sky blue", "white"], "cta": "Build a better future"},
    "relief": {"tone": "calming, reassuring, supportive", "colors": ["soft green", "beige", "white"], "cta": "Make life easier today"},
    "admiration": {"tone": "premium, elegant, impressive", "colors": ["black", "gold", "white"], "cta": "Experience premium quality"},
    "neutral": {"tone": "clear, simple, informative", "colors": ["gray", "blue", "white"], "cta": "Learn more"},
}


MESSAGE_TEMPLATES: dict[str, str] = {
    "joy": "Enjoy every moment with {product_name}, designed to bring happy experiences through {features}. Perfect for {target_audience} who want something simple, useful, and delightful.",
    "excitement": "Discover the next level with {product_name}. Built with {features}, it gives {target_audience} a powerful way to move faster, do more, and feel excited about every step.",
    "trust": "Choose {product_name} with confidence. With {features}, it is designed to give {target_audience} reliable quality, trusted performance, and a smoother experience every day.",
    "confidence": "Step forward with {product_name}. Created for {target_audience}, it helps you feel ready, focused, and in control with features such as {features}.",
    "curiosity": "Unlock a smarter experience with {product_name}. From {features}, it gives {target_audience} a fresh reason to explore what is possible.",
    "optimism": "Build a better tomorrow with {product_name}. Designed for {target_audience}, it supports progress, growth, and new possibilities through {features}.",
    "relief": "Make life easier with {product_name}. With {features}, it helps {target_audience} enjoy a smoother, simpler, and more stress-free experience.",
    "admiration": "Stand out with {product_name}. Crafted with {features}, it gives {target_audience} a premium experience designed to feel impressive and refined.",
    "neutral": "{product_name} is designed for {target_audience}. It includes {features} to provide a practical and useful experience.",
}


VALID_PRODUCT_CATEGORIES = [
    "general",
    "fashion",
    "beauty",
    "education",
    "technology",
    "healthcare",
    "fitness",
    "food",
    "travel",
    "finance",
    "insurance",
]

VALID_TARGET_EMOTIONS = ["joy", "excitement", "trust", "confidence", "curiosity", "optimism", "relief", "admiration", "neutral"]


def select_target_emotion(product_category: str | None, preferred_emotion: str | None) -> str:
    if preferred_emotion:
        preferred_emotion = preferred_emotion.strip().lower()
        if preferred_emotion in EMOTION_STYLE_GUIDES:
            return preferred_emotion

    category = (product_category or "general").strip().lower()
    if category not in PRODUCT_CATEGORY_EMOTION_MAP:
        category = "general"

    for candidate in PRODUCT_CATEGORY_EMOTION_MAP.get(category, []):
        if candidate in EMOTION_STYLE_GUIDES:
            return candidate

    return "neutral"


def generate_cta(target_emotion: str) -> str:
    emotion = (target_emotion or "neutral").strip().lower()
    guide = EMOTION_STYLE_GUIDES.get(emotion, EMOTION_STYLE_GUIDES["neutral"])
    return str(guide.get("cta", "Learn more"))


def _normalize_features(key_features: Any) -> str:
    if key_features is None:
        return "useful features"
    if isinstance(key_features, str):
        features = [f.strip() for f in key_features.split(",") if f.strip()]
    elif isinstance(key_features, (list, tuple)):
        features = [str(f).strip() for f in key_features if str(f).strip()]
    else:
        features = [str(key_features).strip()] if str(key_features).strip() else []
    return ", ".join(features) if features else "useful features"


def generate_marketing_message(
    product_name: str,
    product_category: str,
    target_audience: str,
    key_features: Any,
    target_emotion: str,
) -> str:
    emotion = (target_emotion or "neutral").strip().lower()
    template = MESSAGE_TEMPLATES.get(emotion, MESSAGE_TEMPLATES["neutral"])
    return template.format(
        product_name=(product_name or "This product").strip(),
        target_audience=(target_audience or "customers").strip(),
        features=_normalize_features(key_features),
    )


def generate_visual_suggestions(product_category: str, target_emotion: str) -> dict[str, Any]:
    emotion = (target_emotion or "neutral").strip().lower()
    category = (product_category or "general").strip().lower()
    guide = EMOTION_STYLE_GUIDES.get(emotion, EMOTION_STYLE_GUIDES["neutral"])

    category_image_style = {
        "fashion": "confident models in clean studio lighting",
        "beauty": "close-up skincare routines with soft lighting",
        "education": "focused learners studying with modern tools",
        "technology": "sleek product shots with futuristic UI overlays",
        "healthcare": "calm clinical environments with caring professionals",
        "fitness": "active people training with high energy and motion",
        "food": "bright, appetizing food photography with natural light",
        "travel": "wide scenic landscapes with adventurous perspective",
        "finance": "professional office scenes with trustworthy visuals",
        "insurance": "family-focused scenes conveying safety and reassurance",
        "general": "minimal product lifestyle scenes with clean backgrounds",
    }

    mood_by_emotion = {
        "joy": "bright and friendly",
        "excitement": "bold and high-energy",
        "trust": "clean and reassuring",
        "confidence": "empowering and modern",
        "curiosity": "mysterious and exploratory",
        "optimism": "fresh and future-focused",
        "relief": "calm and soothing",
        "admiration": "premium and elegant",
        "neutral": "clear and informative",
    }

    return {
        "color_palette": list(guide.get("colors", ["gray", "blue", "white"])),
        "image_style": category_image_style.get(category, category_image_style["general"]),
        "layout_mood": mood_by_emotion.get(emotion, mood_by_emotion["neutral"]),
    }


def generate_full_strategy(input_data: dict[str, Any]) -> dict[str, Any]:
    product_name = str(input_data.get("product_name", "")).strip()
    product_category = str(input_data.get("product_category", "general")).strip().lower()
    target_audience = str(input_data.get("target_audience", "")).strip()
    key_features = input_data.get("key_features", [])
    preferred_emotion = input_data.get("target_emotion", None)

    target_emotion = select_target_emotion(product_category, preferred_emotion)
    style = EMOTION_STYLE_GUIDES.get(target_emotion, EMOTION_STYLE_GUIDES["neutral"])

    generated_message = generate_marketing_message(
        product_name=product_name,
        product_category=product_category,
        target_audience=target_audience,
        key_features=key_features,
        target_emotion=target_emotion,
    )

    return {
        "product_name": product_name,
        "product_category": product_category,
        "target_audience": target_audience,
        "target_emotion": target_emotion,
        "tone": style.get("tone", EMOTION_STYLE_GUIDES["neutral"]["tone"]),
        "generated_message": generated_message,
        "cta": generate_cta(target_emotion),
        "visual_suggestions": generate_visual_suggestions(product_category, target_emotion),
    }
