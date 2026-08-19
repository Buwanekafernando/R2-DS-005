"""
loss_framing_agent.py
-------------------------------------------------------------------
FAITHFUL port of your friend's Loss Framing Agent (his app.py run_agent).
Same inputs, same six outputs, same VADER + FOMO + tone logic.

Inputs : product_name, category, gain_message
Outputs: loss_message, gain_sentiment, loss_sentiment,
         fomo_score, sentiment_change, tone_label

The only change vs his file: the Groq call is routed through your
existing generate_with_groq (one API key, one code path). His prompt
text is kept exactly.

Requires: vaderSentiment   ->   python -m pip install vaderSentiment
Place in utils/, beside emotion_agent.py.
-------------------------------------------------------------------
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.emotion_agent import generate_with_groq, EMOTION_SIGNALS

analyzer = SentimentIntensityAnalyzer()

# Exactly your friend's keyword list from his app.py
LOSS_KEYWORDS = [
    "missing", "losing", "without", "don't miss", "never have",
    "left behind", "falling behind", "can't afford", "risk",
    "too late", "regret", "wasting", "miss out", "lose out",
    "no longer", "won't have", "disadvantage", "lack", "overlook",
]


def get_sentiment(text):
    return round(analyzer.polarity_scores(str(text))["compound"], 3)


def get_fomo_score(text):
    return sum(1 for kw in LOSS_KEYWORDS if kw in str(text).lower())


def get_tone_label(score):
    if score >= 0.05:
        return "Positive — Safe to use"
    elif score <= -0.5:
        return "Too Negative — Needs adjustment"
    else:
        return "Acceptable — Within safe range"


def build_loss_prompt(product_name, category, gain_message, target_emotion):
    signals = EMOTION_SIGNALS.get(target_emotion, EMOTION_SIGNALS["neutral"])
    return f"""You are a marketing expert specializing in loss aversion psychology.

Product: {product_name}
Category: {category}
Original message: "{gain_message}"

Rewrite as a SHORT loss-framed message (2-3 sentences):
- Emphasize what the customer LOSES or MISSES without the product (FOMO)
- BUT keep the overall feeling of {target_emotion}: convey {signals['convey']}
- Frame the loss as losing that {target_emotion}, not as fear or doom
- Stay factual, not scary

Return ONLY the rewritten message."""


def run_loss_agent(product_name, category, gain_message, target_emotion):
    """
    Faithful equivalent of your friend's run_agent().
    Returns all six outputs as a dict (instead of a tuple) so React/JSON
    can read them cleanly.
    """
    prompt = build_loss_prompt(product_name, category, gain_message, target_emotion)
    loss_message = generate_with_groq(prompt)

    gain_sent = get_sentiment(gain_message)
    loss_sent = get_sentiment(loss_message)
    fomo = get_fomo_score(loss_message)
    tone = get_tone_label(loss_sent)
    change = round(loss_sent - gain_sent, 3)

    return {
        "loss_message": loss_message,
        "gain_sentiment": gain_sent,
        "loss_sentiment": loss_sent,
        "fomo_score": fomo,
        "sentiment_change": change,
        "tone_label": tone,
    }
