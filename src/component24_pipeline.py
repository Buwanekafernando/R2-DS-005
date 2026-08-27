"""
component24_pipeline.py  (two-stage: emotion generates -> loss agent reframes)
-------------------------------------------------------------------
STAGE 1 — Component 2 (Emotion Propagation Agent) generates the
          emotionally targeted marketing copy (generate-verify-refine,
          top-1). This copy is the "gain-framed message".

STAGE 2 — Component 4 (Loss Framing Agent) converts that copy into a
          loss-framed message and returns all six of its outputs:
          loss_message, gain_sentiment, loss_sentiment, fomo_score,
          sentiment_change, tone_label.

STAGE 3 — Component 2's RoBERTa re-checks whether the target emotion
          survived the loss reframing.

This is a faithful port of the original pipeline.py — only the import
paths were updated for the unified project structure.
-------------------------------------------------------------------
"""

from src.component2.emotion_agent import (
    build_marketing_prompt,
    generate_with_groq,
    select_emotion_for_category,
    get_visual_suggestions,
    PROJECT_EMOTIONS,
)
from src.component2.model_loader import load_emotion_model, predict_emotions
from src.component4.loss_framing_agent import run_loss_agent

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


def generate_emotional_copy(product_name, category, target_audience, features, target_emotion, base_copy=None):
    """Stage 1: generate-verify-refine loop. Keeps the best attempt.

    If base_copy is provided (Component 1's recommended_copy), each attempt
    infuses the target emotion into that existing copy rather than writing
    unrelated copy from scratch — this is the C1 -> C2 connection.
    """
    best = {"text": "", "detected": None, "target_score": -1.0}
    previous_failure = None
    attempts = 0

    for attempt in range(1, EMOTION_ATTEMPTS + 1):
        attempts = attempt
        prompt = build_marketing_prompt(
            product_name, category, target_audience, features,
            target_emotion, previous_failure=previous_failure,
            base_copy=base_copy,
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


def run_component24_pipeline(product_name, category, target_audience="", features="",
                              target_emotion=None, base_copy=None):
    """
    Runs Component 2 (emotion generation) -> Component 4 (loss reframing)
    -> Component 2 re-check, and returns the combined result.

    base_copy: optional. When provided (typically Component 1's
    recommended_copy), Component 2 infuses emotion into that existing copy
    instead of generating unrelated copy from scratch. Component 4 then
    reframes whatever Component 2 produces, so base_copy flows through to
    Component 4 automatically as well.
    """
    if not target_emotion:
        target_emotion = select_emotion_for_category(category)

    # STAGE 1 — Emotion agent generates the (gain-framed) emotional copy,
    # built on top of base_copy when one is supplied
    emo = generate_emotional_copy(
        product_name, category, target_audience, features, target_emotion, base_copy=base_copy
    )
    gain_message = emo["text"]

    # STAGE 2 — Loss Framing Agent (all six outputs)
    loss = run_loss_agent(product_name, category, gain_message, target_emotion)

    # STAGE 3 — RoBERTa re-check: did the target emotion survive?
    post_top1, _, post_target_score = score_for_emotion(loss["loss_message"], target_emotion)

    return {
        "product_name": product_name,
        "category": category,
        "target_emotion": target_emotion,
        "base_copy_used": base_copy,

        # --- Stage 1: emotion agent ---
        "emotion_copy": gain_message,          # this is the gain-framed message
        "emotion_detected": emo["detected"],
        "emotion_matched": emo["matched"],
        "attempts_used": emo["attempts"],

        # --- Stage 2: loss agent (six outputs) ---
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
