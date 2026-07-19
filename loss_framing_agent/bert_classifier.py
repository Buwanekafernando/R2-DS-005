# BERT + MODEL COMPARISON 

import pandas as pd
import time
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

df_results = pd.read_csv("outputs/final_results.csv")
print(f"Loaded {len(df_results)} rows\n")

# ============================================================
# MODEL 1: DistilBERT (fast, lightweight transformer)
# ============================================================
print("Loading Model 1: DistilBERT...")
distilbert = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True,
    max_length=512
)

def classify_distilbert(text):
    result = distilbert(str(text)[:512])[0]
    label = result['label']
    score = round(result['score'], 3)
    framing = "Loss-framed" if label == "NEGATIVE" else "Gain-framed"
    return framing, score

# ============================================================
# MODEL 2: RoBERTa (larger, more accurate transformer)
# ============================================================
print("Loading Model 2: RoBERTa...")
roberta = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512
)

def classify_roberta(text):
    result = roberta(str(text)[:512])[0]
    label = result['label'].upper()
    score = round(result['score'], 3)
    framing = "Loss-framed" if label == "NEGATIVE" else "Gain-framed"
    return framing, score

# ============================================================
# MODEL 3: VADER (rule-based, no deep learning)
# ============================================================
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()

def classify_vader(text):
    score = vader.polarity_scores(str(text))['compound']
    if score < 0.05:
        return "Loss-framed", round(abs(score), 3)
    else:
        return "Gain-framed", round(score, 3)

# ============================================================
# TEST ALL 3 MODELS ON SAMPLE MESSAGES
# ============================================================
print("\n" + "="*65)
print("TESTING ALL 3 MODELS ON SAMPLE MESSAGES")
print("="*65)

test_cases = [
    ("These headphones are amazing! Best sound quality ever.",
     "GAIN"),
    ("Without these headphones you are missing pure audio bliss.",
     "LOSS"),
    ("This baby blanket keeps your child warm and comfortable.",
     "GAIN"),
    ("Don't let your baby miss out on the comfort they deserve.",
     "LOSS"),
    ("Great running shoes that improved my performance dramatically.",
     "GAIN"),
    ("You risk falling behind other runners without proper footwear.",
     "LOSS"),
    ("This serum works wonders. My skin looks 10 years younger.",
     "GAIN"),
    ("Missing out on this serum means missing out on younger skin.",
     "LOSS"),
]

results_test = []
for text, expected in test_cases:
    db_frame, db_score   = classify_distilbert(text)
    rob_frame, rob_score = classify_roberta(text)
    vd_frame,  vd_score  = classify_vader(text)

    db_correct  = "✓" if (expected=="LOSS") == (db_frame=="Loss-framed")  else "✗"
    rob_correct = "✓" if (expected=="LOSS") == (rob_frame=="Loss-framed") else "✗"
    vd_correct  = "✓" if (expected=="LOSS") == (vd_frame=="Loss-framed")  else "✗"

    results_test.append({
        'text': text[:60],
        'expected': expected,
        'distilbert': f"{db_frame} {db_correct}",
        'roberta':    f"{rob_frame} {rob_correct}",
        'vader':      f"{vd_frame} {vd_correct}",
    })
    print(f"\nText     : {text[:65]}")
    print(f"Expected : {expected}")
    print(f"DistilBERT : {db_frame} ({db_score}) {db_correct}")
    print(f"RoBERTa    : {rob_frame} ({rob_score}) {rob_correct}")
    print(f"VADER      : {vd_frame} ({vd_score}) {vd_correct}")
    print("-" * 65)

# Calculate accuracy on test cases
db_acc  = sum(1 for r in results_test if "✓" in r['distilbert'])  / len(results_test) * 100
rob_acc = sum(1 for r in results_test if "✓" in r['roberta'])     / len(results_test) * 100
vd_acc  = sum(1 for r in results_test if "✓" in r['vader'])       / len(results_test) * 100

print(f"\n{'='*65}")
print(f"TEST ACCURACY ON SAMPLE MESSAGES")
print(f"{'='*65}")
print(f"DistilBERT accuracy : {db_acc:.1f}%")
print(f"RoBERTa accuracy    : {rob_acc:.1f}%")
print(f"VADER accuracy      : {vd_acc:.1f}%")

# ============================================================
# RUN BEST MODEL ON ALL 1001 ROWS
# ============================================================
best_model = max(
    [("DistilBERT", db_acc, classify_distilbert),
     ("RoBERTa",    rob_acc, classify_roberta),
     ("VADER",      vd_acc,  classify_vader)],
    key=lambda x: x[1]
)

print(f"\n{'='*65}")
print(f"BEST MODEL: {best_model[0]} ({best_model[1]:.1f}% accuracy)")
print(f"Running {best_model[0]} on all {len(df_results)} rows...")
print(f"{'='*65}\n")

classify_fn = best_model[2]

gain_labels = []
loss_labels = []
gain_scores = []
loss_scores = []

for idx, row in df_results.iterrows():
    g_frame, g_score = classify_fn(row['review_body'])
    l_frame, l_score = classify_fn(row['loss_framed_message'])
    gain_labels.append(g_frame)
    loss_labels.append(l_frame)
    gain_scores.append(g_score)
    loss_scores.append(l_score)

    if (idx + 1) % 100 == 0:
        print(f"  Progress: {idx+1}/{len(df_results)} done ✓")

df_results['bert_gain_label']  = gain_labels
df_results['bert_loss_label']  = loss_labels
df_results['bert_gain_score']  = gain_scores
df_results['bert_loss_score']  = loss_scores
df_results['best_model_used']  = best_model[0]

# ============================================================
# VALIDATION RESULTS
# ============================================================
correctly_gain = sum(1 for x in gain_labels if x == "Gain-framed")
correctly_loss = sum(1 for x in loss_labels if x == "Loss-framed")
total = len(df_results)

print(f"\n{'='*65}")
print(f"VALIDATION RESULTS — {best_model[0]}")
print(f"{'='*65}")
print(f"Original reviews detected as Gain-framed : {correctly_gain}/{total} ({correctly_gain/total*100:.1f}%)")
print(f"Generated messages detected as Loss-framed: {correctly_loss}/{total} ({correctly_loss/total*100:.1f}%)")
print(f"\nThis means {correctly_loss/total*100:.1f}% of generated messages")
print(f"are independently confirmed as loss-framed by {best_model[0]}")

# ============================================================
# MODEL COMPARISON SUMMARY TABLE
# ============================================================
print(f"\n{'='*65}")
print(f"MODEL COMPARISON SUMMARY")
print(f"{'='*65}")
print(f"{'Model':<15} {'Type':<25} {'Test Accuracy':<15} {'Best For'}")
print(f"{'-'*65}")
print(f"{'DistilBERT':<15} {'Transformer (66M params)':<25} {db_acc:<15.1f} General NLP")
print(f"{'RoBERTa':<15} {'Transformer (125M params)':<25} {rob_acc:<15.1f} Sentiment detection")
print(f"{'VADER':<15} {'Rule-based lexicon':<25} {vd_acc:<15.1f} Fast sentiment")
print(f"{'-'*65}")
print(f"SELECTED: {best_model[0]} — highest accuracy for this task")

# Save final results
df_results.to_csv("outputs/final_results.csv", index=False)
print(f"\nSaved to outputs/final_results.csv")
print("\nBERT CLASSIFICATION COMPLETE!")