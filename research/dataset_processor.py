import pandas as pd
import os
import json

def process_all_categories(base_dir, output_json, limit_per_cat=50):
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and f.startswith("amazon_reviews_us_")]
    all_products = []
    
    print(f"Discovered {len(folders)} category folders.")
    
    cols = ['product_title', 'product_category', 'star_rating', 'review_body']
    
    for folder in folders:
        # The file is likely named the same as the folder
        tsv_path = os.path.join(base_dir, folder, folder)
        
        if not os.path.exists(tsv_path):
            print(f"Skipping {folder} (Not found at {tsv_path})")
            continue
            
        print(f"Processing: {folder}...")
        cat_products = []
        seen_titles = set()
        
        try:
            reader = pd.read_csv(
                tsv_path, 
                sep='\t', 
                on_bad_lines='skip', 
                chunksize=5000, 
                usecols=cols,
                encoding='utf-8'
            )
            
            for chunk in reader:
                for _, row in chunk.iterrows():
                    title = row['product_title']
                    if title not in seen_titles:
                        body = str(row['review_body']).lower()
                        pain_points = []
                        if "slow" in body or "wait" in body: pain_points.append("Shipping Delays")
                        if "sold out" in body or "waitlist" in body: pain_points.append("Stock Instability")
                        if "expensive" in body or "price" in body: pain_points.append("Price Sensitivity")
                        
                        cat_products.append({
                            "name": title,
                            "category": row['product_category'],
                            "rating": float(row['star_rating']),
                            "pain_points": list(set(pain_points))
                        })
                        seen_titles.add(title)
                    
                    if len(cat_products) >= limit_per_cat:
                        break
                if len(cat_products) >= limit_per_cat:
                    break
            
            all_products.extend(cat_products)
            print(f"  - OK: Added {len(cat_products)} items.")
            
        except Exception as e:
            print(f"  - Error: {e}")

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=4)
        
    print(f"\nTOTAL: Extracted {len(all_products)} products.")

if __name__ == "__main__":
    process_all_categories(".", "sample_products.json")
