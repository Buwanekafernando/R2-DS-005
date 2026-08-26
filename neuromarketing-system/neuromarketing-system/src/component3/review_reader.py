"""
Review Reader & Pain Point Training Module
Reads product reviews from TSV files and extracts pain points for training
"""

import pandas as pd
import os
from typing import List, Dict, Tuple
from collections import Counter
from .pain_point_extractor import extract_pain_points_detailed

class ReviewReader:
    """Reads and processes product reviews to extract pain points"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.review_cache = {}
        self.pain_point_stats = {}
    
    def read_reviews_for_product(self, product_name: str, category: str = None, limit: int = 50) -> List[Dict]:
        """
        Read reviews for a specific product from TSV files
        
        Args:
            product_name: Name of the product
            category: Category filter (optional)
            limit: Max number of reviews to read
        
        Returns:
            List of reviews with extracted pain points
        """
        reviews_found = []
        
        # Search in all category TSV files
        tsv_files = [f for f in os.listdir(self.base_dir) 
                     if f.startswith("amazon_reviews_us_") and f.endswith(".tsv")]
        
        for tsv_file in tsv_files:
            file_category = tsv_file.replace("amazon_reviews_us_", "").replace("_v1_00.tsv", "")
            
            # Skip if category filter applied and doesn't match
            if category and category.lower() not in file_category.lower():
                continue
            
            try:
                # Read the TSV file
                df = pd.read_csv(
                    os.path.join(self.base_dir, tsv_file),
                    sep='\t',
                    usecols=['product_title', 'review_body', 'star_rating'],
                    on_bad_lines='skip',
                    nrows=5000  # Limit read for performance
                )
                
                # Filter for the product
                product_reviews = df[df['product_title'].str.contains(product_name, case=False, na=False)]
                
                for _, row in product_reviews.iterrows():
                    if len(reviews_found) >= limit:
                        break
                    
                    review_text = str(row['review_body'])
                    pain_analysis = extract_pain_points_detailed(review_text)
                    
                    reviews_found.append({
                        'product': product_name,
                        'category': file_category,
                        'review_text': review_text,
                        'rating': float(row['star_rating']),
                        'pain_points': pain_analysis['pain_points'],
                        'matched_keywords': pain_analysis['matched_keywords'],
                        'total_pain_points': pain_analysis['total_pain_points']
                    })
                
                if len(reviews_found) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error reading {tsv_file}: {e}")
                continue
        
        return reviews_found
    
    def extract_pain_points_from_reviews(self, reviews: List[Dict]) -> Dict:
        """
        Aggregate pain points from multiple reviews and calculate statistics
        
        Args:
            reviews: List of review objects with pain points
        
        Returns:
            Dict with aggregated pain point statistics and frequency
        """
        pain_point_frequency = Counter()
        keyword_frequency = Counter()
        priority_count = {"HIGH": 0, "MEDIUM": 0}
        total_reviews = len(reviews)
        
        for review in reviews:
            for pain_point in review['pain_points']:
                pain_point_frequency[pain_point] += 1
            
            for pain_point, details in review['matched_keywords'].items():
                keyword = details['keyword']
                keyword_frequency[keyword] += 1
                priority = details['priority']
                priority_count[priority] += 1
        
        # Calculate percentage occurrence
        pain_point_percentages = {
            pain_point: (count / total_reviews * 100)
            for pain_point, count in pain_point_frequency.items()
        }
        
        return {
            'total_reviews': total_reviews,
            'pain_point_frequency': dict(pain_point_frequency),
            'pain_point_percentages': pain_point_percentages,
            'top_pain_points': pain_point_frequency.most_common(5),
            'top_keywords': keyword_frequency.most_common(10),
            'priority_distribution': priority_count,
            'avg_pain_points_per_review': sum(r['total_pain_points'] for r in reviews) / total_reviews if total_reviews > 0 else 0
        }
    
    def get_product_pain_profile(self, product_name: str, category: str = None, review_limit: int = 100) -> Dict:
        """
        Get comprehensive pain point profile for a product based on reviews
        
        Args:
            product_name: Name of the product
            category: Category filter (optional)
            review_limit: Number of reviews to analyze
        
        Returns:
            Comprehensive pain profile with statistics
        """
        # Read reviews
        reviews = self.read_reviews_for_product(product_name, category, review_limit)
        
        if not reviews:
            return {
                'product': product_name,
                'reviews_found': 0,
                'pain_points': [],
                'status': 'No reviews found'
            }
        
        # Extract and analyze pain points
        pain_analysis = self.extract_pain_points_from_reviews(reviews)
        
        # Calculate average rating
        avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
        
        return {
            'product': product_name,
            'category': reviews[0]['category'] if reviews else 'Unknown',
            'reviews_found': len(reviews),
            'avg_rating': avg_rating,
            'pain_analysis': pain_analysis,
            'top_pain_points': [point for point, _ in pain_analysis['top_pain_points']],
            'review_sample': reviews[:3]  # First 3 reviews as sample
        }
    
    def get_category_statistics(self, category: str, limit_per_product: int = 30) -> Dict:
        """
        Get pain point statistics for an entire category
        
        Args:
            category: Product category
            limit_per_product: Max reviews per product
        
        Returns:
            Category-wide pain point statistics
        """
        try:
            tsv_file = f"amazon_reviews_us_{category}_v1_00.tsv"
            tsv_path = os.path.join(self.base_dir, tsv_file)
            
            if not os.path.exists(tsv_path):
                return {'status': f'File not found: {tsv_file}'}
            
            df = pd.read_csv(
                tsv_path,
                sep='\t',
                usecols=['product_title', 'review_body', 'star_rating'],
                on_bad_lines='skip',
                nrows=3000
            )
            
            all_pain_points = []
            all_keywords = []
            rating_distribution = {}
            
            for _, row in df.iterrows():
                review_text = str(row['review_body'])
                rating = float(row['star_rating'])
                
                pain_analysis = extract_pain_points_detailed(review_text)
                all_pain_points.extend(pain_analysis['pain_points'])
                all_keywords.extend(pain_analysis['matched_keywords'].keys())
                
                rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
            
            pain_frequency = Counter(all_pain_points)
            
            return {
                'category': category,
                'total_reviews': len(df),
                'pain_point_frequency': dict(pain_frequency),
                'top_pain_points': pain_frequency.most_common(10),
                'unique_pain_points': len(pain_frequency),
                'rating_distribution': rating_distribution,
                'avg_rating': df['star_rating'].mean()
            }
            
        except Exception as e:
            return {'status': f'Error processing category: {e}'}

# Global instance
_reader = None

def get_reader() -> ReviewReader:
    """Get or create global reader instance"""
    global _reader
    if _reader is None:
        _reader = ReviewReader(".")
    return _reader

def read_reviews_for_product(product_name: str, category: str = None, limit: int = 50) -> List[Dict]:
    """Convenience function"""
    return get_reader().read_reviews_for_product(product_name, category, limit)

def get_product_pain_profile(product_name: str, category: str = None, review_limit: int = 100) -> Dict:
    """Convenience function"""
    return get_reader().get_product_pain_profile(product_name, category, review_limit)

def get_category_statistics(category: str) -> Dict:
    """Convenience function"""
    return get_reader().get_category_statistics(category)
