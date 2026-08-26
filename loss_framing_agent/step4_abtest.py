# A/B TEST 

import pandas as pd
import time
from groq import Groq


client = Groq(api_key=GROQ_API_KEY)

df_results = pd.read_csv("outputs/gain_vs_loss_results.csv")
print(f"Loaded {len(df_results)} rows")

def ab_test_judge(gain_msg, loss_msg, product, category):
    prompt = f"""You are a consumer psychology expert.

Product: {product}
Category: {category}

Message A: "{gain_msg[:200]}"
Message B: "{loss_msg[:200]}"

Which message makes a customer MORE likely to purchase?
Reply with ONLY one letter: A or B"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"

def parse_winner(text):
    text = str(text).strip().upper()
    # Get first character only
    first_char = text[0] if text else ''
    if first_char == 'B':
        return 'B - Loss'
    elif first_char == 'A':
        return 'A - Gain'
    else:
        return 'Unknown'

print(f"\nRunning A/B test on {len(df_results)} rows...\n")
ab_results = []

for idx, (i, row) in enumerate(df_results.iterrows()):
    result = ab_test_judge(
        row['review_body'],
        row['loss_framed_message'],
        row['product_title'],
        row['product_category']
    )
    ab_results.append(result)
    if (idx + 1) % 100 == 0:
        print(f"  Progress: {idx+1}/{len(df_results)} done ✓")
    time.sleep(0.3)

# Show sample raw responses
print("\nSample raw LLM responses:")
for r in ab_results[:5]:
    print(f"  >>> '{r}'")

df_results['ab_result'] = ab_results
df_results['ab_winner'] = df_results['ab_result'].apply(parse_winner)

total    = len(df_results[df_results['ab_winner'] != 'Unknown'])
gain_win = (df_results['ab_winner'] == 'A - Gain').sum()
loss_win = (df_results['ab_winner'] == 'B - Loss').sum()

print(f"\n===== A/B TEST RESULTS =====")
print(f"Total evaluated : {total}")
if total > 0:
    print(f"Gain framing won: {gain_win} ({gain_win/total*100:.1f}%)")
    print(f"Loss framing won: {loss_win} ({loss_win/total*100:.1f}%)")
print(f"\nBy category:")
print(df_results.groupby('product_category')['ab_winner'].value_counts().to_string())

df_results.to_csv("outputs/final_results.csv", index=False)
print("\nSaved to outputs/final_results.csv")