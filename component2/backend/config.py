# config.py
# ============================================================
# CENTRAL CONFIGURATION FILE
# ============================================================

import os

# ── Folder Paths ─────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
RAW_DIR       = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MERGED_DIR    = os.path.join(BASE_DIR, "data", "merged")
SPLITS_DIR    = os.path.join(BASE_DIR, "data", "splits")
OUTPUTS_DIR   = os.path.join(BASE_DIR, "outputs")
LOGS_DIR      = os.path.join(BASE_DIR, "logs")

# ── Your 6 Target Emotion Labels ─────────────────────────────
# Based on Plutchik Wheel of Emotions (1980)
# These 6 cover all emotions relevant to marketing persuasion
EMOTION_LABELS = [
    "joy",
    "trust",
    "excitement",
    "sadness",
    "anger",
    "fear"
]

# ── GoEmotions Label List ─────────────────────────────────────
# ORDER IS CRITICAL — index number in labels column maps here
# Example: array([25]) → index 25 → "neutral"
# Example: array([17]) → index 17 → "joy"
# Source: https://huggingface.co/datasets/google-research-datasets/go_emotions
GOEMOTIONS_LABEL_NAMES = [
    "admiration",    # 0
    "amusement",     # 1
    "anger",         # 2
    "annoyance",     # 3
    "approval",      # 4
    "caring",        # 5
    "confusion",     # 6
    "curiosity",     # 7
    "desire",        # 8
    "disappointment",# 9
    "disapproval",   # 10
    "disgust",       # 11
    "embarrassment", # 12
    "excitement",    # 13
    "fear",          # 14
    "gratitude",     # 15
    "grief",         # 16
    "joy",           # 17
    "love",          # 18
    "nervousness",   # 19
    "optimism",      # 20
    "pride",         # 21
    "realization",   # 22
    "relief",        # 23
    "remorse",       # 24
    "sadness",       # 25
    "surprise",      # 26
    "neutral"        # 27
]

# ── GoEmotions → Your 6 Labels Mapping ───────────────────────
# None means REMOVE that label — not useful for marketing
#
# WHY THESE MAPPINGS:
# admiration → trust  (admiring a product = trusting it)
# amusement  → joy    (amusement is a form of joy)
# curiosity  → excitement (curiosity drives excitement)
# desire     → excitement (wanting something = excitement)
# gratitude  → joy    (feeling grateful = joyful)
# grief      → sadness
# love       → joy    (love is a strong form of joy)
# nervousness→ fear
# optimism   → joy    (positive outlook = joyful)
# pride      → joy    (pride is a positive emotion)
# relief     → trust  (relief comes from trusting outcome)
# surprise   → excitement (surprise = excited reaction)
# neutral    → None   (no emotion = remove)
# confusion  → None   (not marketing relevant)
# disgust    → None   (we never generate disgust in marketing)
# embarrassment → None
# realization   → None
# remorse       → None
# disapproval   → None
# disappointment→ sadness (weak signal, keep as sadness)

GOEMOTIONS_MAP = {
    "admiration"    : "trust",
    "amusement"     : "joy",
    "anger"         : "anger",
    "annoyance"     : "anger",
    "approval"      : "trust",
    "caring"        : "trust",
    "confusion"     : None,
    "curiosity"     : "excitement",
    "desire"        : "excitement",
    "disappointment": "sadness",
    "disapproval"   : None,
    "disgust"       : None,
    "embarrassment" : None,
    "excitement"    : "excitement",
    "fear"          : "fear",
    "gratitude"     : "joy",
    "grief"         : "sadness",
    "joy"           : "joy",
    "love"          : "joy",
    "nervousness"   : "fear",
    "optimism"      : "joy",
    "pride"         : "joy",
    "realization"   : None,
    "relief"        : "trust",
    "remorse"       : "sadness",
    "sadness"       : "sadness",
    "surprise"      : "excitement",
    "neutral"       : None,
}

# ── ISEAR → Your 6 Labels Mapping ────────────────────────────
# Your ISEAR file (eng_dataset.csv) sentiment column values:
# joy, fear, anger, sadness, disgust, shame, guilt
ISEAR_MAP = {
    "joy"    : "joy",
    "fear"   : "fear",
    "anger"  : "anger",
    "sadness": "sadness",

}

# ── Amazon Category → Expected Dominant Emotion ──────────────
# Used in Step 1 (Emotion Identifier) rule-based mapping
# Based on consumer psychology research:
# Apparel   → joy      (fashion makes people happy)
# Baby      → trust    (parents prioritise safety/reliability)
# Beauty    → joy      (beauty products make people feel good)
# Electronics → excitement (new tech is thrilling)
# Grocery   → trust    (food safety is critical)
# Pet       → joy      (pets bring happiness)
# Sports    → excitement (sports energy and performance)
CATEGORY_EMOTION_MAP = {
    "Apparel"    : "joy",
    "Baby"       : "trust",
    "Beauty"     : "joy",
    "Electronics": "excitement",
    "Grocery"    : "trust",
    "Pet"        : "joy",
    "Sports"     : "excitement",
}

# ── Preprocessing Settings ────────────────────────────────────
MIN_CHARS = 10    # remove texts shorter than 10 characters
MAX_CHARS = 512   # remove texts longer than 512 characters
MIN_WORDS = 3     # remove texts with fewer than 3 words

# ── Balancing Settings ────────────────────────────────────────
# Each class will have this many samples after balancing
# 6000 × 6 emotions = 36,000 total training samples
SAMPLES_PER_CLASS = 6000

# ── Amazon Settings ───────────────────────────────────────────
SAMPLES_PER_AMAZON_FILE = 2000  # per TSV file
AMAZON_MIN_TEXT_LENGTH  = 30    # skip very short reviews

# ── Train / Val / Test Split ──────────────────────────────────
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
TEST_RATIO  = 0.15

# ── Random Seed ───────────────────────────────────────────────
# Same seed every run = same results every run
# This makes your research reproducible
RANDOM_SEED = 42