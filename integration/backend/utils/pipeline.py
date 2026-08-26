"""
pipeline.py  (two-stage: emotion generates -> friend's full loss agent)
-------------------------------------------------------------------
STAGE 1 — Your Emotion Propagation Agent generates the emotionally
          targeted marketing copy (generate-verify-refine, top-1).
          This copy is the "gain-framed message".

STAGE 2 — Your friend's Loss Framing Agent (full, faithful) converts
          that copy into a loss-framed message and returns ALL SIX of
          his outputs: loss_message, gain_sentiment, loss_sentiment,
          fomo_score, sentiment_change, tone_label.

STAGE 3 — Your RoBERTa re-checks whether the target emotion survived
          the loss reframing.

Place in utils/, beside emotion_agent.py, model_loader.py, loss_framing_agent.py.
-------------------------------------------------------------------
"""

import os
from dotenv import load_dotenv

# .env lives in backend/, the parent of utils/
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from utils.emotion_agent import (
    build_marketing_prompt,
    generate_with_groq,
    select_emotion_for_category,
    get_visual_suggestions,
    PROJECT_EMOTIONS,
)
from utils.model_loader import load_emotion_model, predict_emotions
from utils.loss_framing_agent import run_loss_agent

EMOTION_ATTEMPTS = 3   # retry budget for the emotion-generation stage


def score_for_emotion(text, target_emotion):
    """Return (top1_label, top1_score, target_emotion_score)."""
    result = predict_emotions(text, top_k=len(PROJECT_EMOTIONS))
    preds = result.get("predictions") or []
    if not preds:
        return None, 0.0, 0.0
    top1 = preds[0]
    target_score = next(
        (p["score"] for p in preds if p["emotion"] == target_emotion), 0.0
    )
    return top1["emotion"], top1["score"], target_score


def generate_emotional_copy(product_name, category, target_audience, features, target_emotion):
    """Stage 1: your generate-verify-refine loop. Keeps the best attempt."""
    best = {"text": "", "detected": None, "target_score": -1.0}
    previous_failure = None
    attempts = 0

    for attempt in range(1, EMOTION_ATTEMPTS + 1):
        attempts = attempt
        prompt = build_marketing_prompt(
            product_name, category, target_audience, features,
            target_emotion, previous_failure=previous_failure,
        )
        text = generate_with_groq(prompt)
        top1, top1_score, target_score = score_for_emotion(text, target_emotion)

        if top1 == target_emotion:
            return {"text": text, "detected": top1, "target_score": target_score,
                    "attempts": attempt, "matched": True}

        if target_score > best["target_score"]:
            best = {"text": text, "detected": top1, "target_score": target_score}
        previous_failure = top1

    best["attempts"] = attempts
    best["matched"] = False
    return best


def run_pipeline(product_name, category, target_audience="", features="", target_emotion=None):
    if not target_emotion:
        target_emotion = select_emotion_for_category(category)

    # STAGE 1 — Emotion agent generates the (gain-framed) emotional copy
    emo = generate_emotional_copy(
        product_name, category, target_audience, features, target_emotion
    )
    gain_message = emo["text"]

    # STAGE 2 — Friend's full Loss Framing Agent (all six outputs)
    loss = run_loss_agent(product_name, category, gain_message, target_emotion)

    # STAGE 3 — RoBERTa re-check: did the target emotion survive?
    post_top1, _, post_target_score = score_for_emotion(loss["loss_message"], target_emotion)

    return {
        "product_name": product_name,
        "category": category,
        "target_emotion": target_emotion,

        # --- Stage 1: emotion agent ---
        "emotion_copy": gain_message,          # this is the gain-framed message
        "emotion_detected": emo["detected"],
        "emotion_matched": emo["matched"],
        "attempts_used": emo["attempts"],

        # --- Stage 2: friend's loss agent (his exact six outputs) ---
        "loss_message": loss["loss_message"],
        "gain_sentiment": loss["gain_sentiment"],
        "loss_sentiment": loss["loss_sentiment"],
        "fomo_score": loss["fomo_score"],
        "sentiment_change": loss["sentiment_change"],
        "tone_label": loss["tone_label"],

        # --- Stage 3: emotion survival re-check ---
        "emotion_after_loss": post_top1,
        "emotion_after_score": round(post_target_score, 4),
        "emotion_survived": (post_top1 == target_emotion),

        # visuals
        "visual_suggestions": get_visual_suggestions(target_emotion),
    }


if __name__ == "__main__":
    load_emotion_model()
    out = run_pipeline(
        product_name="Sony WH-1000XM5",
        category="Electronics",
        target_audience="commuters and remote workers",
        features="active noise cancellation, 30h battery, comfortable fit",
        target_emotion="excitement",
    )
    print("\n===== PIPELINE OUTPUT =====")
    for k, v in out.items():
        print(f"{k:20}: {v}")
