import json
import os
from typing import List, Dict, Optional
import logging
import requests

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
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("xAI API key is required. Set XAI_API_KEY in .env or environment variable.")
        
        # For now, store the API key for later use
        # xAI SDK will handle the client initialization
        logger.info("ScarcityAgent initialized with Grok AI API")
        self.strategies = [
            "Quantity-Based Scarcity (Stock limits)",
            "Time-Based Scarcity (Deadlines/Countdowns)",
            "Exclusivity-Based Scarcity (Member-only/Early access)",
            "Social-Proof Scarcity (Others are buying now)"
        ]

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
        Uses Grok AI to choose the best scarcity intensity for the product.
        """
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
                "model": "grok-1",
                "temperature": 0.3,
                "max_tokens": 20
            }
            response = requests.post(
                "https://api.x.ai/openai/v1/chat/completions",
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

        try:
            pain_points_str = ", ".join(pain_points) if pain_points else "none"
            
            prompt = f"""
            You are a psychological marketing expert specializing in the Scarcity Principle from Cialdini's Influence.
            
            Product: {product_name}
            Base Description: {base_copy}
            Scarcity Intensity: {intensity} (low: subtle hints, medium: clear urgency, high: strong pressure)
            Customer Pain Points: {pain_points_str}
            
            Generate optimized marketing copy that incorporates scarcity elements while maintaining trust and authenticity.
            Focus on one primary scarcity type: quantity, time, exclusivity, or social proof.
            Ensure the copy feels natural and not manipulative.
            
            Output only the optimized copy text, no explanations.
            """
            
            # Call Grok API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that specializes in marketing psychology."},
                    {"role": "user", "content": prompt}
                ],
                "model": "grok-1",
                "temperature": 0.7,
                "max_tokens": 150
            }
            
            response = requests.post(
                "https://api.x.ai/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_copy = result['choices'][0]['message']['content'].strip()
                logger.info(f"Generated scarcity copy for {product_name} using Grok AI")
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
        Fallback heuristic method for generating scarcity copy.
        """
        # Scenario 1: Targeted triggers based on customer pain points (Sentiment-Aware)
        targeted_trigger = ""
        if pain_points:
            if "Shipping Delays" in pain_points:
                targeted_trigger = "Order within the next 45 minutes for Priority Processing to skip the backlog."
            elif "Stock Instability" in pain_points:
                targeted_trigger = "Recent restock confirmed, but inventory is moving 3x faster than average."
            elif "Price Sensitivity" in pain_points:
                targeted_trigger = "Current price guaranteed only for the next 24 hours before seasonal adjustment."

        if targeted_trigger:
            return f"{targeted_trigger} {base_copy}"

        # Scenario 2: Default heuristic triggers
        if intensity == "high":
            return f"FINAL CALL: Only a few units left of {product_name}. {base_copy} Grab yours before the stock is gone!"
        elif intensity == "medium":
            return f"Strategic Stock Alert: {product_name} is now available in limited quantities. {base_copy}"
        else:
            return f"Popular Choice: {product_name} is seeing high demand today. {base_copy}"

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
                "model": "grok-1",
                "temperature": 0.3,
                "max_tokens": 100
            }
            response = requests.post(
                "https://api.x.ai/openai/v1/chat/completions",
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
