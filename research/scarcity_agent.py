import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import logging
import requests
import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# Try to load .env file but don't fail if dotenv is not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScarcityAgent:
    """
    Component 3: Scarcity Optimization Agent
    Objective: Integrate scarcity-based elements to increase urgency while maintaining trust.
    Uses Grok AI API for intelligent scarcity copy generation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.model_path = Path(__file__).with_name("trained_scarcity_model.joblib")
        self.local_model = self._load_local_model()
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key and self.local_model is None:
            raise ValueError("xAI API key is required. Set XAI_API_KEY in .env or environment variable.")
        
        # For now, store the API key for later use
        # xAI SDK will handle the client initialization
        logger.info("ScarcityAgent initialized with a local trained intensity model")
        self.strategies = [
            "Quantity-Based Scarcity (Stock limits)",
            "Time-Based Scarcity (Deadlines/Countdowns)",
            "Exclusivity-Based Scarcity (Member-only/Early access)",
            "Social-Proof Scarcity (Others are buying now)"
        ]

    def _load_local_model(self):
        """Load a saved local model if available, otherwise train a simple default one."""
        if self.model_path.exists():
            try:
                model = joblib.load(self.model_path)
                logger.info("Loaded local scarcity intensity model from %s", self.model_path)
                return model
            except Exception as exc:
                logger.warning("Could not load local model from %s: %s", self.model_path, exc)

        return self._train_and_save_default_model()

    def _train_and_save_default_model(self):
        """Train a lightweight decision-tree model for intensity selection."""
        training_data = [
            ([0, 0.5, 0, 0, 1, 0], "low"),
            ([0, 0.8, 0, 0, 0, 0], "low"),
            ([1, 1.2, 0, 1, 0, 0], "medium"),
            ([1, 1.5, 1, 0, 0, 0], "medium"),
            ([2, 2.0, 1, 1, 0, 0], "high"),
            ([2, 2.5, 1, 0, 0, 1], "high"),
            ([1, 2.0, 0, 0, 1, 0], "medium"),
            ([2, 2.2, 0, 1, 1, 0], "high"),
            ([0, 1.0, 0, 0, 0, 1], "medium"),
            ([1, 1.8, 1, 0, 1, 0], "high"),
            ([0, 0.7, 0, 0, 0, 0], "low"),
            ([1, 1.3, 0, 1, 0, 1], "medium"),
        ]

        features = np.array([item[0] for item in training_data], dtype=float)
        labels = [item[1] for item in training_data]

        model = DecisionTreeClassifier(random_state=42)
        model.fit(features, labels)
        joblib.dump(model, self.model_path)
        logger.info("Trained and saved default scarcity intensity model to %s", self.model_path)
        return model

    def _build_feature_vector(self, product_info: Dict = None, pain_points: List[str] = None) -> List[float]:
        """Convert product and pain-point metadata into numeric features for the local model."""
        product_info = product_info or {}
        pain_points = pain_points or []
        pain_text = " ".join(pain_points).lower()

        price = float(product_info.get("price", 0) or 0)
        category = str(product_info.get("category", "general") or "general").lower()
        category_score = {
            "luxury": 2.5,
            "tech": 2.0,
            "fashion": 2.0,
            "beauty": 1.5,
            "baby": 0.8,
            "pet": 0.7,
            "grocery": 0.5,
            "general": 1.0,
        }.get(category, 1.0)

        price_bucket = 0 if price < 100 else 1 if price < 500 else 2
        stock_flag = 1.0 if any(token in pain_text for token in ["stock", "inventory", "availability"]) else 0.0
        shipping_flag = 1.0 if any(token in pain_text for token in ["shipping", "delay", "delivery"]) else 0.0
        price_sensitivity_flag = 1.0 if any(token in pain_text for token in ["price", "budget", "sensitive"]) else 0.0
        quality_flag = 1.0 if any(token in pain_text for token in ["quality", "durability", "reliability"]) else 0.0

        return [price_bucket, category_score, stock_flag, shipping_flag, price_sensitivity_flag, quality_flag]

    def analyze_suitability(self, product_info: Dict) -> float:
        """
        Determines how appropriate scarcity is for this product.
        Returns a score between 0 and 1.
        """
        # In a real implementation, this would use an LLM or heuristic rules
        # For now, we simulate a logic based on price and category
        price = product_info.get("price", 0)
        category = product_info.get("category", "").lower()
        
        score = 0.5 # Default
        if category in ["luxury", "tech", "fashion"]:
            score += 0.3
        if price > 500:
            score += 0.2
            
        return min(score, 1.0)

    def determine_intensity(self, product_name: str, base_copy: str, product_info: Dict = None, pain_points: List[str] = None) -> str:
        """
        Uses the trained local model first, then falls back to Grok AI or heuristics.
        """
        if self.local_model is not None:
            try:
                features = self._build_feature_vector(product_info, pain_points)
                predicted = self.local_model.predict([features])[0]
                if predicted in ["low", "medium", "high"]:
                    logger.info("Determined intensity '%s' for %s using the local trained model", predicted, product_name)
                    return predicted
            except Exception as exc:
                logger.warning("Local model prediction failed for %s: %s", product_name, exc)

        product_info = product_info or {}
        pain_points_str = ", ".join(pain_points) if pain_points else "none"
        category = product_info.get("category", "general")
        price = product_info.get("price", "unknown")

        prompt = f"""
You are a marketing strategy specialist. Determine the most appropriate scarcity intensity for this product. Output exactly one word: low, medium, or high.

Product Name: {product_name}
Category: {category}
Price: {price}
Base Description: {base_copy}
Customer Pain Points: {pain_points_str}

Choose:
- low when urgency should be subtle and trust-preserving,
- medium when there is balanced urgency and conversion potential,
- high when strong scarcity pressure is justified.

Respond with only the intensity level.
"""

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": "You are an expert marketing strategist advising on urgency intensity."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok",
                "temperature": 0.3,
                "max_tokens": 20
            }
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                intensity = result['choices'][0]['message']['content'].strip().lower()
                if intensity in ["low", "medium", "high"]:
                    logger.info(f"Determined intensity '{intensity}' for {product_name} using Grok AI")
                    return intensity
                logger.warning(f"Unexpected intensity value from Grok AI: {intensity}")
            else:
                logger.error(f"Grok API error during intensity selection: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error determining intensity: {e}")

        # Fallback heuristic
        return self._heuristic_intensity(product_info, pain_points)

    def _heuristic_intensity(self, product_info: Dict = None, pain_points: List[str] = None) -> str:
        product_info = product_info or {}
        category = product_info.get("category", "").lower()
        price = product_info.get("price", 0) or 0
        pain_points = pain_points or []

        if "Stock Instability" in pain_points or "Shipping Delays" in pain_points:
            return "high"
        if category in ["luxury", "tech", "fashion"] or price >= 500:
            return "high"
        if "Price Sensitivity" in pain_points:
            return "medium"
        return "medium"

    def generate_scarcity_copy(self, product_name: str, base_copy: str, intensity: str = None, pain_points: List[str] = None, product_info: Dict = None) -> str:
        """
        Transforms base copy into scarcity-focused copy based on intensity and sentiment using Grok AI.
        """
        if intensity is None:
            intensity = self.determine_intensity(product_name, base_copy, product_info=product_info, pain_points=pain_points)

        if not self.api_key:
            logger.info("No API key configured; using local heuristic scarcity copy for %s", product_name)
            return self._heuristic_scarcity_copy(product_name, base_copy, intensity, pain_points)

        try:
            pain_points_str = ", ".join(pain_points) if pain_points else "none"
            category = product_info.get("category", "general") if product_info else "general"
            price = product_info.get("price", "unknown") if product_info else "unknown"

            # Create intensity-specific prompts
            intensity_prompts = {
                "low": f"""
You are a psychological marketing expert specializing in subtle scarcity techniques.

Product: {product_name}
Category: {category}
Price: {price}
Base Description: {base_copy}
Customer Pain Points: {pain_points_str}

Create LOW INTENSITY scarcity copy that:
- Uses gentle, subtle hints of limited availability
- Focuses on social proof ("others are choosing this")
- Maintains a calm, trustworthy tone
- Avoids pressure or urgency words
- Feels natural and conversational
- Preserves brand authenticity

Examples of low intensity: "This popular item is getting attention from our community" or "Many customers are adding this to their carts today"

Output only the optimized copy text, no explanations.
""",

                "medium": f"""
You are a psychological marketing expert specializing in balanced scarcity techniques.

Product: {product_name}
Category: {category}
Price: {price}
Base Description: {base_copy}
Customer Pain Points: {pain_points_str}

Create MEDIUM INTENSITY scarcity copy that:
- Uses clear but not aggressive urgency signals
- Incorporates time-based elements (limited time offers)
- Includes specific numbers (limited stock, time remaining)
- Balances urgency with trust
- Feels professional and credible
- Uses action-oriented language

Examples of medium intensity: "Only 5 left in stock - order soon" or "Available for the next 24 hours at this price"

Output only the optimized copy text, no explanations.
""",

                "high": f"""
You are a psychological marketing expert specializing in strong scarcity techniques.

Product: {product_name}
Category: {category}
Price: {price}
Base Description: {base_copy}
Customer Pain Points: {pain_points_str}

Create HIGH INTENSITY scarcity copy that:
- Uses strong urgency and pressure language
- Incorporates multiple scarcity types (quantity + time + exclusivity)
- Creates FOMO (fear of missing out)
- Uses countdown timers, final calls, last chance messaging
- Employs power words like "final", "last", "limited", "exclusive"
- Creates immediate action motivation

Examples of high intensity: "FINAL HOUR: Only 2 left - selling out fast!" or "Last chance - offer ends in 30 minutes!"

Output only the optimized copy text, no explanations.
"""
            }

            prompt = intensity_prompts.get(intensity, intensity_prompts["medium"])

            # Call Grok API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "messages": [
                    {"role": "system", "content": "You are a creative marketing copywriter specializing in psychological triggers and scarcity principles."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok",
                "temperature": 0.8,  # Higher temperature for more creativity
                "max_tokens": 200
            }

            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                generated_copy = result['choices'][0]['message']['content'].strip()
                logger.info(f"Generated {intensity} intensity scarcity copy for {product_name} using Grok AI")
                return generated_copy
            else:
                logger.error(f"Grok API error: {response.status_code} - {response.text}")
                return self._heuristic_scarcity_copy(product_name, base_copy, intensity, pain_points)

        except Exception as e:
            logger.error(f"Error generating scarcity copy: {e}")
            # Fallback to heuristic
            return self._heuristic_scarcity_copy(product_name, base_copy, intensity, pain_points)

    def _heuristic_scarcity_copy(self, product_name: str, base_copy: str, intensity: str, pain_points: List[str] = None) -> str:
        """
        Fallback heuristic method for generating scarcity copy with creative variations.
        """
        import random

        # Scenario 1: Targeted triggers based on customer pain points (Sentiment-Aware)
        targeted_trigger = ""
        if pain_points:
            if "Shipping Delays" in pain_points:
                triggers = [
                    "Order within the next 45 minutes for Priority Processing to skip the backlog.",
                    "Secure your spot in our expedited shipping queue - limited slots available.",
                    "Fast-track your delivery with our limited-time rush processing option."
                ]
                targeted_trigger = random.choice(triggers)
            elif "Stock Instability" in pain_points:
                triggers = [
                    "Recent restock confirmed, but inventory is moving 3x faster than average.",
                    "Fresh stock just arrived, but demand is exceptionally high this week.",
                    "New inventory added today - quantities are limited and moving quickly."
                ]
                targeted_trigger = random.choice(triggers)
            elif "Price Sensitivity" in pain_points:
                triggers = [
                    "Current price guaranteed only for the next 24 hours before seasonal adjustment.",
                    "This competitive pricing is time-sensitive - secure it before the next price update.",
                    "Limited-time value pricing - won't last beyond today's market conditions."
                ]
                targeted_trigger = random.choice(triggers)

        if targeted_trigger:
            return f"{targeted_trigger} {base_copy}"

        # Scenario 2: Intensity-specific creative triggers
        if intensity == "high":
            high_intensity_templates = [
                f"FINAL CALL: Only a few units left of {product_name}. {base_copy} Grab yours before the stock is gone!",
                f"CRITICAL STOCK ALERT: {product_name} is selling out fast! {base_copy} Last chance to secure yours today!",
                f"EXTREME DEMAND: {product_name} has only {random.randint(2, 5)} units remaining. {base_copy} Act now or miss out!",
                f"FINAL HOURS: {product_name} inventory critically low. {base_copy} Don't wait - limited stock won't last!",
                f"SELLING OUT: {product_name} is disappearing from shelves. {base_copy} Secure your order immediately!"
            ]
            return random.choice(high_intensity_templates)

        elif intensity == "medium":
            medium_intensity_templates = [
                f"Strategic Stock Alert: {product_name} is now available in limited quantities. {base_copy}",
                f"Time-Sensitive Offer: {product_name} at current pricing for a limited time. {base_copy}",
                f"Growing Demand: {product_name} inventory is moving quickly. {base_copy} Order soon to avoid disappointment.",
                f"Limited Availability: {product_name} quantities are restricted. {base_copy} Available while supplies last.",
                f"Smart Purchase Alert: {product_name} is seeing increased interest. {base_copy} Don't miss this opportunity."
            ]
            return random.choice(medium_intensity_templates)

        else:  # low intensity
            low_intensity_templates = [
                f"Popular Choice: {product_name} is gaining attention from our community. {base_copy}",
                f"Trending Item: {product_name} is being discovered by more customers daily. {base_copy}",
                f"Community Favorite: {product_name} is receiving positive feedback. {base_copy}",
                f"Rising Interest: {product_name} is becoming a customer favorite. {base_copy}",
                f"Well-Received: {product_name} is getting noticed for its quality. {base_copy}"
            ]
            return random.choice(low_intensity_templates)

    def generate_all_intensities(self, product_name: str, base_copy: str, pain_points: List[str] = None, product_info: Dict = None) -> Dict[str, str]:
        """
        Generates scarcity copy for all three intensity levels.
        """
        intensities = ["low", "medium", "high"]
        results = {}
        for intensity in intensities:
            results[intensity] = self.generate_scarcity_copy(
                product_name, base_copy, intensity=intensity, pain_points=pain_points, product_info=product_info
            )
        return results

    def recommend_best_intensity(self, product_name: str, base_copy: str, generated_copies: Dict[str, str], pain_points: List[str] = None, product_info: Dict = None) -> Dict:
        """
        Uses Grok AI to recommend the best intensity based on generated copies.
        """
        pain_points_str = ", ".join(pain_points) if pain_points else "none"
        category = product_info.get("category", "general") if product_info else "general"
        price = product_info.get("price", "unknown") if product_info else "unknown"

        if not self.api_key:
            logger.info("No API key configured; using local heuristic recommendation fallback")
            return {
                "recommended_intensity": "medium",
                "reason": "Balanced medium intensity recommended as a safe default when no API key is configured.",
                "full_response": "Local fallback recommendation."
            }

        copies_text = "\n".join([f"{intensity.upper()}: {copy}" for intensity, copy in generated_copies.items()])

        prompt = f"""
You are a marketing strategy expert. Review the following scarcity copy variations for a product and recommend the best one.

Product: {product_name}
Category: {category}
Price: {price}
Base Description: {base_copy}
Customer Pain Points: {pain_points_str}

Generated Copies:
{copies_text}

Choose the best intensity (low, medium, or high) and explain why in 1-2 sentences. Format your response as:
RECOMMENDATION: [intensity]
REASON: [explanation]
"""

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": "You are an expert marketing strategist evaluating scarcity copy effectiveness."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok",
                "temperature": 0.3,
                "max_tokens": 100
            }
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                result = response.json()
                recommendation_text = result['choices'][0]['message']['content'].strip()
                # Parse the response
                lines = recommendation_text.split('\n')
                recommended_intensity = "medium"  # default
                reason = "AI recommendation not parsed correctly."
                for line in lines:
                    if line.startswith("RECOMMENDATION:"):
                        rec = line.split(":", 1)[1].strip().lower()
                        if rec in ["low", "medium", "high"]:
                            recommended_intensity = rec
                    elif line.startswith("REASON:"):
                        reason = line.split(":", 1)[1].strip()
                return {
                    "recommended_intensity": recommended_intensity,
                    "reason": reason,
                    "full_response": recommendation_text
                }
            else:
                logger.error(f"Grok API error during recommendation: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")

        # Fallback
        return {
            "recommended_intensity": "medium",
            "reason": "Medium intensity recommended as a balanced approach for optimal conversion.",
            "full_response": "Unable to get AI recommendation."
        }

    def calibrate_trust_level(self, generated_content: str) -> Dict:
        """
        Evaluates if the scarcity cues feel 'authentic' or 'manipulative'.
        """
        # Simulating an authenticity check
        if "!!!" in generated_content or "HURRY" in generated_content.upper():
            return {"status": "Warning", "score": 0.4, "reason": "High pressure might reduce long-term trust."}
        return {"status": "Safe", "score": 0.9, "reason": "Subtle and organic scarcity."}

    def process_batch_from_json(self, json_path: str, output_path: str):
        """
        Loads products from JSON and generates scarcity strategy for each.
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
            
        results = []
        for p in products:
            suitability = self.analyze_suitability(p)
            # Only generate for suitable items
            if suitability > 0.5:
                all_copies = self.generate_all_intensities(p['name'], "Get yours now.", pain_points=p.get('pain_points', []), product_info=p)
                recommendation = self.recommend_best_intensity(p['name'], "Get yours now.", all_copies, pain_points=p.get('pain_points', []), product_info=p)
                results.append({
                    "product": p['name'],
                    "category": p['category'],
                    "suitability": suitability,
                    "all_copies": all_copies,
                    "recommended_intensity": recommendation['recommended_intensity'],
                    "recommendation_reason": recommendation['reason']
                })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Batch processing complete. Results saved to {output_path}")

if __name__ == "__main__":
    # Quick Test
    agent = ScarcityAgent()
    product = {"name": "Neuro-Headset 2.0", "price": 899, "category": "Tech"}
    
    suitability = agent.analyze_suitability(product)
    print(f"Suitability Score: {suitability}")
    
    print("\n--- Generating Scarcity Content ---")
    copy = agent.generate_scarcity_copy(
        product["name"], 
        "The ultimate tool for brain performance optimization.", 
        intensity="medium"
    )
    print(copy)
    
    trust = agent.calibrate_trust_level(copy)
    print(f"\nTrust Calibration: {trust}")
