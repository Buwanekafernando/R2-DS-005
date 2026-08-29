# src/generator.py

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

# Project root = three levels up from src/component1/generator.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

# ════════════════════════════════════════════════════════
# CHANNEL-SPECIFIC COPY VARIANTS
# Takes the already-chosen winning copy and reformats it for different
# marketing channels, rather than writing something unrelated from
# scratch — keeps the core message and psychological strategy consistent
# across every format the business owner actually needs to publish.
# ════════════════════════════════════════════════════════

def build_social_media_prompt(product_text, category, winning_copy):
    return f"""You are a social media copywriter. Adapt the marketing message below into
a short, punchy social media caption (Instagram/Facebook style).

PRODUCT: {product_text}
CATEGORY: {category}
BASE MESSAGE (keep the same core idea and tone): "{winning_copy}"

Write a social media caption that:
1. Is 15-30 words, casual and scroll-stopping
2. Keeps the same core selling point and emotional tone as the base message
3. Ends with 3-5 relevant hashtags on a new line
4. Uses at most one emoji, only if it fits naturally

Write ONLY the caption. No labels, no explanations."""


def build_product_listing_prompt(product_text, category, winning_copy):
    return f"""You are an e-commerce copywriter. Adapt the marketing message below into
a product listing description (like an Amazon or Daraz listing).

PRODUCT: {product_text}
CATEGORY: {category}
BASE MESSAGE (keep the same core idea and tone): "{winning_copy}"

Write a product listing description that:
1. Opens with one compelling sentence (the hook)
2. Follows with 3 short bullet points highlighting key benefits (use "•")
3. Keeps the same core selling point as the base message
4. Total length 40-70 words including bullets

Write ONLY the listing text. No labels, no explanations."""


def build_email_prompt(product_text, category, winning_copy):
    return f"""You are an email marketing copywriter. Adapt the marketing message below into
a short promotional email.

PRODUCT: {product_text}
CATEGORY: {category}
BASE MESSAGE (keep the same core idea and tone): "{winning_copy}"

Write, in this exact format:
SUBJECT: <a short, compelling subject line, under 8 words>
BODY: <a 2-3 sentence email body that keeps the same core selling point as
the base message, ending with a clear call to action>

Write ONLY those two lines. No labels other than SUBJECT: and BODY:, no other explanations."""


def generate_channel_variants(product_text, category, winning_copy):
    """
    Generates Social Media, Product Listing, and Email variants of the
    winning copy. Three separate calls (not one combined call) so each
    format gets a properly targeted prompt and a parsing failure in one
    doesn't take down the others.
    """
    social = generate_copy(build_social_media_prompt(product_text, category, winning_copy))
    listing = generate_copy(build_product_listing_prompt(product_text, category, winning_copy))
    email_raw = generate_copy(build_email_prompt(product_text, category, winning_copy))

    email_subject, email_body = "", email_raw or ""
    if email_raw:
        for line in email_raw.splitlines():
            if line.strip().upper().startswith("SUBJECT:"):
                email_subject = line.split(":", 1)[1].strip()
            elif line.strip().upper().startswith("BODY:"):
                email_body = line.split(":", 1)[1].strip()

    return {
        "social_media": social,
        "product_listing": listing,
        "email_subject": email_subject,
        "email_body": email_body,
    }
