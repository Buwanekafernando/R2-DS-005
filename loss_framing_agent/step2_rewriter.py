
import pandas as pd
import time
from groq import Groq


client = Groq(api_key=GROQ_API_KEY)

df_sample = pd.read_csv("outputs/cleaned_sample.csv")
print(f"Loaded {len(df_sample)} rows")

def convert_to_loss_frame(review_text, product_name, category):
    prompt = f"""You are a marketing expert specializing in loss aversion psychology.

Product: {product_name}
Category: {category}
Original gain-framed review: "{review_text}"

Rewrite this as a SHORT loss-framed marketing message (2-3 sentences only).
- Emphasize what the customer LOSES or MISSES by NOT having this product
- Create FOMO (fear of missing out)
- Stay factual, not scary
- Vary your style

Return ONLY the rewritten message. Nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


# Test 3 rows
print("\n===== TESTING ON 3 ROWS =====\n")
for i, row in df_sample.head(3).iterrows():
    print(f"PRODUCT  : {row['product_title'][:60]}")
    print(f"CATEGORY : {row['product_category']}")
    print(f"ORIGINAL : {row['review_body'][:150]}")
    loss_msg = convert_to_loss_frame(
        row['review_body'],
        row['product_title'],
        row['product_category']
    )
    print(f"LOSS MSG : {loss_msg}")
    print("-" * 60)
    time.sleep(0.5)

input("\nTest looks good? Press ENTER to run on all rows...")

# Run all rows
print(f"\nProcessing all {len(df_sample)} rows...\n")
loss_messages = []
errors = 0

for idx, (i, row) in enumerate(df_sample.iterrows()):
    loss_msg = convert_to_loss_frame(
        row['review_body'],
        row['product_title'],
        row['product_category']
    )
    if "ERROR" in str(loss_msg):
        errors += 1
        loss_messages.append("ERROR")
    else:
        loss_messages.append(loss_msg)

    if (idx + 1) % 50 == 0:
        print(f"  Progress: {idx+1}/{len(df_sample)} done ✓")

    time.sleep(0.5)

df_sample['loss_framed_message'] = loss_messages
df_results = df_sample[df_sample['loss_framed_message'] != "ERROR"].copy()

print(f"\n===== DONE =====")
print(f"Converted : {len(df_results)} rows")
print(f"Errors    : {errors} rows")

df_results.to_csv("outputs/gain_vs_loss_results.csv", index=False)
print("Saved to outputs/gain_vs_loss_results.csv")