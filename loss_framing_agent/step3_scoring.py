#VADER  + FOMO 

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

df_results = pd.read_csv("outputs/gain_vs_loss_results.csv")
print(f"Loaded {len(df_results)} rows")

analyzer = SentimentIntensityAnalyzer()

loss_keywords = [
    "missing", "losing", "without", "don't miss", "never have",
    "left behind", "falling behind", "can't afford", "risk",
    "costly mistake", "too late", "regret", "wasting", "stuck",
    "miss out", "lose out", "no longer", "won't have", "deprive",
    "disadvantage", "suffer", "lack", "neglect", "overlook"
]

def get_sentiment(text):
    return round(analyzer.polarity_scores(str(text))['compound'], 3)

def get_fomo_score(text):
    return sum(1 for kw in loss_keywords if kw in str(text).lower())

def tone_label(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.5:
        return "Too Negative"
    else:
        return "Acceptable"

df_results['gain_sentiment'] = df_results['review_body'].apply(get_sentiment)
df_results['loss_sentiment'] = df_results['loss_framed_message'].apply(get_sentiment)
df_results['fomo_score']     = df_results['loss_framed_message'].apply(get_fomo_score)
df_results['tone_label']     = df_results['loss_sentiment'].apply(tone_label)
df_results['tone_ok']        = df_results['tone_label'] != "Too Negative"

print("\n===== SCORING SUMMARY =====")
print(f"Average GAIN sentiment : {df_results['gain_sentiment'].mean():.3f}")
print(f"Average LOSS sentiment : {df_results['loss_sentiment'].mean():.3f}")
print(f"Average FOMO score     : {df_results['fomo_score'].mean():.2f}")
print(f"\nTone distribution:")
print(df_results['tone_label'].value_counts())
print(f"\nAcceptable tone: {df_results['tone_ok'].sum()} / {len(df_results)}")

df_results.to_csv("outputs/gain_vs_loss_results.csv", index=False)
print("\nSaved to outputs/gain_vs_loss_results.csv")