"""
tone_naturalizer.py
-------------------------------------------------------------------
Step 4 of the Component 2 -> 4 pipeline (Natural-Tone Version).

Rewrites the loss-framed message in a more natural, conversational
voice: varied sentence length, contractions, a warmer register. This
is a copy-quality pass only. It does not score, evaluate, or make any
claim about AI-detection tools.

The original loss_message (and its sentiment / FOMO / tone metrics) is
left untouched; the natural-tone rewrite is returned alongside it.
-------------------------------------------------------------------
"""

from src.component2.emotion_agent import generate_with_groq


def build_natural_tone_prompt(loss_message: str, category: str) -> str:
    return f"""You are a marketing copywriter for {category} products.

Rewrite the following message so it reads naturally and conversationally,
as if a person wrote it, not a brand template.

Message: "{loss_message}"

Guidelines:
- Vary sentence length (mix short and slightly longer sentences)
- Use natural contractions where they fit (you're, don't, it's)
- Keep the meaning and the sense of urgency/loss intact; do not soften it
  into a gain-framed message
- Keep it to 2-3 sentences
- Avoid stiff, overly formal, or corporate-sounding phrasing

Return ONLY the rewritten message, nothing else."""


def naturalize_tone(loss_message: str, category: str) -> str:
    """
    Returns a more naturally-voiced rewrite of the loss-framed message.
    Falls back to the original message if generation fails, so a
    transient API error never breaks the pipeline.
    """
    if not loss_message:
        return loss_message

    try:
        rewritten = generate_with_groq(build_natural_tone_prompt(loss_message, category))
        return rewritten.strip() if rewritten else loss_message
    except Exception:
        return loss_message
