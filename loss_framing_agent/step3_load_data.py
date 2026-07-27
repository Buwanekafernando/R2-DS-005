import pandas as pd
import glob
import os

# Path to your data folder
folder_path = "data/"

# Find all TSV files
all_files = glob.glob(folder_path + "*.tsv")

print(f"Found {len(all_files)} files:")
for f in all_files:
    print(" -", os.path.basename(f))

# Load all files one by one
df_list = []
for file in all_files:
    print(f"\nLoading: {os.path.basename(file)} ...")
    temp = pd.read_csv(
        file,
        sep='\t',
        on_bad_lines='skip',
        low_memory=False
    )
    print(f"  Rows loaded: {len(temp)}")
    df_list.append(temp)

# Combine all into one dataframe
df = pd.concat(df_list, ignore_index=True)

print("\n=== COMBINED DATASET ===")
print(f"Total rows     : {len(df)}")
print(f"Total columns  : {len(df.columns)}")
print(f"\nColumn names:\n{df.columns.tolist()}")
print(f"\nCategories found:\n{df['product_category'].value_counts()}")
print(f"\nSample data:")
print(df[['product_category','star_rating','review_headline','review_body']].head(3))