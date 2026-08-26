

import pandas as pd
import glob
import os

folder_path = "data/"
all_files = glob.glob(folder_path + "*.tsv")

print(f"Found {len(all_files)} files:")
for f in all_files:
    print(" -", os.path.basename(f))

df_list = []
for file in all_files:
    print(f"\nLoading: {os.path.basename(file)} ...")
    temp = pd.read_csv(
        file, sep='\t',
        on_bad_lines='skip',
        low_memory=False,
        nrows=2000
        #df = pd.read_csv(file, sep='\t').sample(2000, random_state=42)
    )
    print(f"  Rows loaded: {len(temp)}")
    df_list.append(temp)

df = pd.concat(df_list, ignore_index=True)

# Clean
df_clean = df[['product_title', 'product_category',
               'star_rating', 'review_headline', 'review_body']].copy()
df_clean.dropna(subset=['review_body', 'review_headline'], inplace=True)
df_clean = df_clean[df_clean['star_rating'] == 5].copy()
df_clean['body_len'] = df_clean['review_body'].str.len()
df_clean = df_clean[
    (df_clean['body_len'] >= 80) &
    (df_clean['body_len'] <= 500)
].copy()

# Sample 143 per category = ~1001 rows total
df_list_sampled = []
for cat in df_clean['product_category'].unique():
    cat_df = df_clean[df_clean['product_category'] == cat]
    sampled = cat_df.sample(min(len(cat_df), 143), random_state=42)
    df_list_sampled.append(sampled)

df_sample = pd.concat(df_list_sampled, ignore_index=True)

print("\n===== CLEANED DATA =====")
print(f"Total rows : {len(df_sample)}")
print(df_sample['product_category'].value_counts())

# Save
df_sample.to_csv("outputs/cleaned_sample.csv", index=False)
print("\nSaved to outputs/cleaned_sample.csv")