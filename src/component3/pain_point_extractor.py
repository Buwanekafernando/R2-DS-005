"""
Enhanced Pain Point Extraction Module
Extracts 40+ keywords across 10+ pain point categories using NLP-based keyword matching
Version: 2.0 (Research Enhanced)
"""

from typing import List, Dict, Set
import re

class PainPointExtractor:
    """Enhanced pain point extractor with comprehensive keyword mapping for research"""
    
    def __init__(self):
        """Initialize pain point categories with expanded keyword lists"""
        self.pain_point_categories = {
            # 1. LOGISTICS & DELIVERY
            "Shipping Delays": {
                "keywords": ["slow", "wait", "late", "delayed", "takes forever", "months to arrive", 
                           "shipping slow", "took weeks", "forever to ship", "stuck in transit",
                           "sluggish delivery", "snail pace", "dragging", "procrastination"],
                "weight": 1.0,
                "priority": "HIGH"
            },
            
            # 2. INVENTORY & AVAILABILITY
            "Stock Instability": {
                "keywords": ["sold out", "waitlist", "out of stock", "unavailable", "oos",
                           "back order", "discontinued", "no stock", "never in stock", "always sold",
                           "restock", "limited supply", "can't find", "impossible to get"],
                "weight": 1.0,
                "priority": "HIGH"
            },
            
            # 3. PRICING CONCERNS
            "Price Sensitivity": {
                "keywords": ["expensive", "price", "overpriced", "too much", "costly", "outrageous",
                           "highway robbery", "ripoff", "not worth", "money grab", "pricey",
                           "overcharge", "inflated", "budget busting", "charge too much"],
                "weight": 0.9,
                "priority": "MEDIUM"
            },
            
            # 4. QUALITY CONCERNS
            "Quality Issues": {
                "keywords": ["defective", "broken", "faulty", "poor quality", "cheap material",
                           "flimsy", "doesn't last", "wears out", "shoddy", "subpar",
                           "inferior", "low quality", "disappointing quality", "terrible build"],
                "weight": 1.0,
                "priority": "HIGH"
            },
            
            # 5. DURABILITY PROBLEMS
            "Durability & Longevity": {
                "keywords": ["doesn't last", "broke", "falls apart", "quit working", "failed",
                           "stopped working", "lifespan", "wears out quickly", "breaks", "deteriorates",
                           "short-lived", "not durable", "gave up", "fell apart after"],
                "weight": 0.95,
                "priority": "HIGH"
            },
            
            # 6. CUSTOMER SERVICE
            "Poor Customer Service": {
                "keywords": ["customer service", "support useless", "no response", "rude staff",
                           "unhelpful", "ignore complaints", "won't refund", "hard to reach",
                           "no help", "unresponsive", "dismissive", "terrible service"],
                "weight": 0.85,
                "priority": "MEDIUM"
            },
            
            # 7. RETURN & REFUND ISSUES
            "Return/Refund Difficulties": {
                "keywords": ["refund", "return", "no refund", "hard to return", "return policy",
                           "money back", "won't refund", "refuses to return", "restocking",
                           "refund denied", "return hassle", "return window", "can't return"],
                "weight": 0.95,
                "priority": "HIGH"
            },
            
            # 8. PACKAGING & PRESENTATION
            "Packaging Problems": {
                "keywords": ["damaged package", "arrived broken", "poor packaging", "damaged goods",
                           "shipping damage", "crushed", "shattered", "packaging failed",
                           "box damage", "delivered damaged", "came broken", "bad packaging"],
                "weight": 0.8,
                "priority": "MEDIUM"
            },
            
            # 9. AUTHENTICITY & TRUST
            "Authenticity Concerns": {
                "keywords": ["fake", "counterfeit", "not authentic", "knockoff", "replica",
                           "genuine", "real deal", "suspect", "suspicious", "too good to be true",
                           "doubt authenticity", "questions quality", "seems fake"],
                "weight": 1.0,
                "priority": "HIGH"
            },
            
            # 10. EXPECTATIONS vs REALITY
            "Expectation Misalignment": {
                "keywords": ["not as described", "misleading", "false advertising", "different from",
                           "looks nothing like", "disappointing", "expected more", "not what i wanted",
                           "mislead", "photos lie", "picture misleading", "described wrong"],
                "weight": 0.95,
                "priority": "HIGH"
            },
            
            # 11. COMPATIBILITY & FIT
            "Fit/Compatibility Issues": {
                "keywords": ["doesn't fit", "too small", "too large", "wrong size", "sizing",
                           "incompatible", "doesn't work with", "not compatible", "won't fit",
                           "size off", "runs small", "runs large", "doesn't match"],
                "weight": 0.9,
                "priority": "MEDIUM"
            },
            
            # 12. VALUE & ROI
            "Poor Value Proposition": {
                "keywords": ["not worth", "waste of money", "poor value", "bad deal", "not value",
                           "overrated", "underwhelming", "doesn't justify", "rip off", "highway robbery",
                           "not worth price", "overpriced for", "better alternatives"]
            }
        }
    
    def extract_pain_points(self, review_text: str, use_weighted: bool = True) -> List[str]:
        """
        Extract pain points from review text using keyword matching
        
        Args:
            review_text: Raw review text to analyze
            use_weighted: If True, returns all matched categories; if False, returns sorted by weight
        
        Returns:
            List of identified pain points
        """
        text_lower = review_text.lower()
        # Remove punctuation for better matching
        text_normalized = re.sub(r'[^\w\s]', ' ', text_lower)
        
        matched_categories = {}
        
        for category, config in self.pain_point_categories.items():
            keywords = config.get("keywords", [])
            weight = config.get("weight", 1.0)
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword in text_normalized:
                    matched_categories[category] = {
                        "weight": weight,
                        "priority": config.get("priority", "MEDIUM"),
                        "matched_keyword": keyword
                    }
                    break  # Move to next category after first match
        
        if not matched_categories:
            return []
        
        # Sort by weight and priority if requested
        if use_weighted:
            sorted_categories = sorted(
                matched_categories.items(),
                key=lambda x: (x[1]["weight"], x[1]["priority"] == "HIGH"),
                reverse=True
            )
            return [cat[0] for cat in sorted_categories]
        else:
            return list(matched_categories.keys())
    
    def extract_with_details(self, review_text: str) -> Dict:
        """
        Extract pain points with detailed information (category, keyword matched, weight)
        
        Args:
            review_text: Raw review text to analyze
        
        Returns:
            Dict with pain points and their metadata
        """
        text_lower = review_text.lower()
        text_normalized = re.sub(r'[^\w\s]', ' ', text_lower)
        
        results = {
            "pain_points": [],
            "matched_keywords": {},
            "total_pain_points": 0,
            "priority_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        }
        
        for category, config in self.pain_point_categories.items():
            keywords = config.get("keywords", [])
            weight = config.get("weight", 1.0)
            priority = config.get("priority", "MEDIUM")
            
            for keyword in keywords:
                if keyword in text_normalized:
                    results["pain_points"].append(category)
                    results["matched_keywords"][category] = {
                        "keyword": keyword,
                        "weight": weight,
                        "priority": priority
                    }
                    results["priority_distribution"][priority] += 1
                    break
        
        results["total_pain_points"] = len(results["pain_points"])
        return results
    
    def get_keyword_coverage(self) -> Dict:
        """
        Return comprehensive statistics on keyword coverage
        
        Returns:
            Dict with coverage metrics for research
        """
        total_keywords = 0
        category_count = 0
        keyword_by_category = {}
        
        for category, config in self.pain_point_categories.items():
            keywords = config.get("keywords", [])
            total_keywords += len(keywords)
            category_count += 1
            keyword_by_category[category] = {
                "count": len(keywords),
                "keywords": keywords,
                "weight": config.get("weight", 1.0),
                "priority": config.get("priority", "MEDIUM")
            }
        
        return {
            "total_keywords": total_keywords,
            "total_categories": category_count,
            "keywords_per_category": total_keywords / category_count if category_count > 0 else 0,
            "category_breakdown": keyword_by_category
        }

# Global extractor instance
_extractor = None

def get_extractor() -> PainPointExtractor:
    """Get or create global extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = PainPointExtractor()
    return _extractor

def extract_pain_points(review_text: str) -> List[str]:
    """Convenience function to extract pain points"""
    return get_extractor().extract_pain_points(review_text)

def extract_pain_points_detailed(review_text: str) -> Dict:
    """Convenience function to extract pain points with details"""
    return get_extractor().extract_with_details(review_text)
