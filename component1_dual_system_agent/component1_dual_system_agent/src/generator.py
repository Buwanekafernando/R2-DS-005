# src/generator.py

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))

api_key = os.getenv("XAI_API_KEY")

if not api_key:
    raise ValueError(
        "XAI_API_KEY not found. "
        "Add XAI_API_KEY=xai-... to config/.env"
    )

_client = OpenAI(
    api_key  = api_key,
    base_url = "https://api.x.ai/v1"
)

GROK_MODEL = "grok-3"
print(f"Grok client ready | Model: {GROK_MODEL}")


# ════════════════════════════════════════════════════════
# GENERATION
# ════════════════════════════════════════════════════════

def generate_copy(prompt, retries=3):
    """Single entry point for copy generation. Called by src/agent.py"""

    for attempt in range(retries):
        try:
            response = _client.chat.completions.create(
                model    = GROK_MODEL,
                messages = [
                    {
                        "role":    "system",
                        "content": (
                            "You are a world-class marketing copywriter with deep "
                            "expertise in consumer psychology and neuro-marketing. "
                            "Write only the marketing copy — no labels, no "
                            "explanations, no preamble."
                        )
                    },
                    {
                        "role":    "user",
                        "content": prompt
                    }
                ],
                max_tokens  = 150,
                temperature = 0.75,
            )

            copy_text = response.choices[0].message.content.strip()

            if len(copy_text.split()) >= 5:
                return copy_text
            else:
                print(f"  Warning: Copy too short. Retrying...")
                continue

        except Exception as e:
            error_msg = str(e)
            print(f"  [GROK ERROR] Attempt {attempt+1}/{retries}: "
                  f"{type(e).__name__}: {error_msg[:100]}")

            if "429" in error_msg or "rate" in error_msg.lower():
                wait = 20 * (attempt + 1)
                print(f"  Rate limit. Waiting {wait}s...")
                time.sleep(wait)

            elif "401" in error_msg or "auth" in error_msg.lower():
                print("  Auth failed. Check XAI_API_KEY in config/.env")
                return None

            elif "403" in error_msg or "credits" in error_msg.lower():
                print("  No credits. Add credits at console.x.ai")
                return None

            else:
                time.sleep(3)

    print("  All retries failed.")
    return None


# ════════════════════════════════════════════════════════
# PROMPT BUILDERS
# ════════════════════════════════════════════════════════

def build_emotional_prompt(product_text, category, confidence):
    if confidence > 0.85:
        intensity   = "very strong"
        instruction = "Use vivid sensory language, excitement, and desire. Make it irresistible."
    elif confidence > 0.70:
        intensity   = "moderate"
        instruction = "Use warm, positive emotional language. Focus on how it makes the user feel."
    else:
        intensity   = "subtle"
        instruction = "Use gentle emotional appeal. Balance feeling with light product information."

    return f"""You are an expert neuro-marketing copywriter specializing in System 1 \
emotional marketing. System 1 thinking is fast, intuitive, and emotion-driven.

PRODUCT: {product_text}
CATEGORY: {category}
EMOTIONAL INTENSITY NEEDED: {intensity}

Write a SHORT marketing message (2-3 sentences, max 60 words) that:
1. Triggers immediate emotional desire using sensory or emotional language
2. Creates a feeling of pleasure, excitement, or belonging
3. Uses simple, vivid words that bypass rational thinking
4. Does NOT mention technical specifications or rational justifications
5. {instruction}

Write ONLY the marketing copy. No labels, no explanations."""


def build_rational_prompt(product_text, category, confidence):
    if confidence > 0.85:
        depth       = "highly detailed"
        instruction = "Include specific numbers, comparisons, and technical advantages."
    elif confidence > 0.70:
        depth       = "moderately detailed"
        instruction = "Highlight key features and value proposition clearly."
    else:
        depth       = "balanced"
        instruction = "Combine key facts with a light value statement."

    return f"""You are an expert neuro-marketing copywriter specializing in System 2 \
rational marketing. System 2 thinking is slow, analytical, and evidence-based.

PRODUCT: {product_text}
CATEGORY: {category}
DETAIL LEVEL NEEDED: {depth}

Write a SHORT marketing message (2-3 sentences, max 60 words) that:
1. Presents clear, logical reasons to purchase
2. Highlights specific features, benefits, or value
3. Uses precise, factual language that supports informed decision-making
4. Addresses potential objections implicitly
5. {instruction}

Write ONLY the marketing copy. No labels, no explanations."""


def build_hybrid_prompt(product_text, category, s1_prob, s2_prob):
    dominant    = "emotional" if s1_prob > s2_prob else "rational"
    blend_ratio = f"{int(s1_prob*100)}% emotional, {int(s2_prob*100)}% rational"

    return f"""You are an expert neuro-marketing copywriter.

PRODUCT: {product_text}
CATEGORY: {category}
BLEND RATIO: {blend_ratio} (dominant: {dominant})

Write a SHORT marketing message (2-3 sentences, max 60 words) that:
1. Opens with an emotional hook to capture attention
2. Follows with one clear rational reason to justify the purchase
3. Closes with a subtle call to action

Write ONLY the marketing copy. No labels, no explanations."""