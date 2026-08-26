import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScarcityAgent:
    """
    Component 3: Scarcity Optimization Agent
    Objective: Integrate scarcity-based elements to increase urgency while maintaining trust.
    Uses locally trained Machine Learning Regression (.pkl) models to predict continuous scarcity intensity scores.
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        if model_dir:
            self.models_dir = Path(model_dir)
        else:
            # Project root = two levels up from src/component3/scarcity_agent.py
            self.models_dir = Path(__file__).parent.parent.parent / "models"
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.models_dir / "scarcity_intensity_regressor.pkl"
        self.scaler_path = self.models_dir / "scarcity_scaler.pkl"
        
        self.local_model = None
        self.scaler = None
        self._load_local_model()

        logger.info("ScarcityAgent initialized with local Regression .pkl model from %s", self.models_dir)
        self.strategies = [
            "Quantity-Based Scarcity (Stock limits)",
            "Time-Based Scarcity (Deadlines/Countdowns)",
            "Exclusivity-Based Scarcity (Member-only/Early access)",
            "Social-Proof Scarcity (Others are buying now)"
        ]

    def _load_local_model(self):
        """Load saved local regression .pkl models if available, otherwise train default model."""
        if self.model_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    self.local_model = pickle.load(f)
                if self.scaler_path.exists():
                    with open(self.scaler_path, "rb") as f:
                        self.scaler = pickle.load(f)
                
                # Test prediction to verify compatibility
                test_feat = np.array([[0, 0.5, 0, 0, 1, 0]], dtype=float)
                if self.scaler:
                    test_feat = self.scaler.transform(test_feat)
                self.local_model.predict(test_feat)
                logger.info("Successfully loaded offline regression .pkl model from %s", self.models_dir)
                return self.local_model
            except Exception as exc:
                logger.warning("Failed to load .pkl regression model from %s: %s. Retraining...", self.models_dir, exc)

        return self.train_and_save_default_model()

    def train_and_save_default_model(self):
        """Train a DecisionTreeRegressor model to predict continuous scarcity intensity scores (0.0 to 1.0)."""
        training_data = [
            ([0, 0.5, 0, 0, 1, 0], 0.20),
            ([0, 0.8, 0, 0, 0, 0], 0.15),
            ([1, 1.2, 0, 1, 0, 0], 0.50),
            ([1, 1.5, 1, 0, 0, 0], 0.55),
            ([2, 2.0, 1, 1, 0, 0], 0.85),
            ([2, 2.5, 1, 0, 0, 1], 0.95),
            ([1, 2.0, 0, 0, 1, 0], 0.50),
            ([2, 2.2, 0, 1, 1, 0], 0.90),
            ([0, 1.0, 0, 0, 0, 1], 0.45),
            ([1, 1.8, 1, 0, 1, 0], 0.80),
            ([0, 0.7, 0, 0, 0, 0], 0.10),
            ([1, 1.3, 0, 1, 0, 1], 0.52),
        ]

        features = np.array([item[0] for item in training_data], dtype=float)
        targets = np.array([item[1] for item in training_data], dtype=float)

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        model = DecisionTreeRegressor(random_state=42)
        model.fit(scaled_features, targets)

        self.models_dir.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(model, f)
        with open(self.scaler_path, "wb") as f:
            pickle.dump(scaler, f)

        self.local_model = model
        self.scaler = scaler
        logger.info("Trained and saved manual regression .pkl model to %s", self.model_path)
        return model

    def _build_feature_vector(self, product_info: Dict = None, pain_points: List[str] = None) -> List[float]:
        """Convert product metadata and pain points into numeric feature vector."""
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

    def predict_intensity_score(self, product_info: Dict = None, pain_points: List[str] = None) -> float:
        """
        Uses the regression model to predict a continuous intensity score between 0.0 and 1.0.
        """
        if self.local_model is not None:
            try:
                raw_features = np.array([self._build_feature_vector(product_info, pain_points)], dtype=float)
                if self.scaler:
                    raw_features = self.scaler.transform(raw_features)
                predicted_score = float(self.local_model.predict(raw_features)[0])
                return float(np.clip(predicted_score, 0.0, 1.0))
            except Exception as exc:
                logger.warning("Regression model prediction failed: %s", exc)

        return self._heuristic_intensity_score(product_info, pain_points)

    def _heuristic_intensity_score(self, product_info: Dict = None, pain_points: List[str] = None) -> float:
        product_info = product_info or {}
        category = str(product_info.get("category", "")).lower()
        price = product_info.get("price", 0) or 0
        pain_points = pain_points or []

        score = 0.4
        if "Stock Instability" in pain_points or "Shipping Delays" in pain_points:
            score += 0.35
        if category in ["luxury", "tech", "fashion"] or price >= 500:
            score += 0.30
        if "Price Sensitivity" in pain_points:
            score += 0.15
        return float(np.clip(score, 0.0, 1.0))

    def analyze_suitability(self, product_info: Dict) -> float:
        """
        Determines how appropriate scarcity is for this product.
        Returns a continuous regression score between 0 and 1.
        """
        price = product_info.get("price", 0)
        category = str(product_info.get("category", "")).lower()
        
        score = 0.5
        if category in ["luxury", "tech", "fashion"]:
            score += 0.3
        if price > 500:
            score += 0.2
            
        return min(score, 1.0)

    def determine_intensity(self, product_name: str, base_copy: str, product_info: Dict = None, pain_points: List[str] = None) -> str:
        """
        Predicts continuous regression score and converts it to discrete intensity level ('low', 'medium', 'high').
        - Score < 0.40 -> 'low'
        - 0.40 <= Score < 0.70 -> 'medium'
        - Score >= 0.70 -> 'high'
        """
        score = self.predict_intensity_score(product_info, pain_points)
        if score < 0.40:
            intensity = "low"
        elif score < 0.70:
            intensity = "medium"
        else:
            intensity = "high"

        logger.info("Determined intensity '%s' (Regression Score: %.2f) for %s", intensity, score, product_name)
        return intensity

    def generate_scarcity_copy(self, product_name: str, base_copy: str, intensity: str = None, pain_points: List[str] = None, product_info: Dict = None) -> str:
        """
        Transforms base copy into scarcity copy based on predicted intensity score and pain points.
        """
        if intensity is None:
            intensity = self.determine_intensity(product_name, base_copy, product_info=product_info, pain_points=pain_points)

        return self._offline_scarcity_copy(product_name, base_copy, intensity, pain_points)

    def _offline_scarcity_copy(self, product_name: str, base_copy: str, intensity: str, pain_points: List[str] = None) -> str:
        import random

        targeted_trigger = ""
        if pain_points:
            if "Shipping Delays" in pain_points:
                triggers = [
                    "Order within the next 45 minutes for Priority Processing to skip shipping backlogs.",
                    "Secure your order in our expedited fulfillment queue - limited daily slots available.",
                    "Fast-track delivery guaranteed when ordered within the current batch cutoff."
                ]
                targeted_trigger = random.choice(triggers)
            elif "Stock Instability" in pain_points:
                triggers = [
                    "Inventory restock confirmed, but stock is selling out 3x faster than average.",
                    "Fresh batch just arrived, but quantities are strictly limited.",
                    "New inventory added today - high demand means stock won't last long."
                ]
                targeted_trigger = random.choice(triggers)
            elif "Price Sensitivity" in pain_points:
                triggers = [
                    "Current promotional price guaranteed for the next 24 hours only.",
                    "Time-sensitive pricing - locked in before the upcoming cost adjustment.",
                    "Special value pricing active today - offer ends at midnight."
                ]
                targeted_trigger = random.choice(triggers)

        if targeted_trigger:
            return f"{targeted_trigger} {base_copy}"

        if intensity == "high":
            templates = [
                f"FINAL CALL: Only a few units left of {product_name}. {base_copy} Grab yours before stock runs out!",
                f"CRITICAL STOCK ALERT: {product_name} is selling out fast! {base_copy} Last chance to order today!",
                f"EXTREME DEMAND: {product_name} has limited units remaining. {base_copy} Act now to secure yours!",
                f"FINAL HOURS: {product_name} inventory is critically low. {base_copy} Don't wait - stock won't last!",
                f"SELLING OUT: {product_name} is disappearing quickly. {base_copy} Secure your order immediately!"
            ]
            return random.choice(templates)

        elif intensity == "medium":
            templates = [
                f"Strategic Stock Alert: {product_name} is available in limited quantities. {base_copy}",
                f"Time-Sensitive Offer: {product_name} at current pricing for a limited window. {base_copy}",
                f"Growing Demand: {product_name} inventory is moving quickly. {base_copy} Order soon to guarantee availability.",
                f"Limited Availability: {product_name} quantities are restricted. {base_copy} Available while supplies last.",
                f"Popular Choice: {product_name} is seeing high demand today. {base_copy} Reserve yours while available."
            ]
            return random.choice(templates)

        else:  # low intensity
            templates = [
                f"Customer Favorite: {product_name} is gaining attention from our community. {base_copy}",
                f"Trending Item: {product_name} is being discovered by more shoppers daily. {base_copy}",
                f"Community Choice: {product_name} receives top satisfaction ratings. {base_copy}",
                f"Rising Interest: {product_name} is becoming a favorite selection. {base_copy}",
                f"Well-Received: {product_name} is recognized for its quality. {base_copy}"
            ]
            return random.choice(templates)

    def generate_all_intensities(self, product_name: str, base_copy: str, pain_points: List[str] = None, product_info: Dict = None) -> Dict[str, str]:
        intensities = ["low", "medium", "high"]
        results = {}
        for intensity in intensities:
            results[intensity] = self.generate_scarcity_copy(
                product_name, base_copy, intensity=intensity, pain_points=pain_points, product_info=product_info
            )
        return results

    def recommend_best_intensity(self, product_name: str, base_copy: str, generated_copies: Dict[str, str], pain_points: List[str] = None, product_info: Dict = None) -> Dict:
        score = self.predict_intensity_score(product_info, pain_points)
        intensity = self.determine_intensity(product_name, base_copy, product_info=product_info, pain_points=pain_points)
        return {
            "recommended_intensity": intensity,
            "intensity_score": score,
            "reason": f"Regression model predicted an urgency intensity score of {score:.2f} (Category: {intensity.upper()}).",
            "full_response": f"Recommended intensity level: {intensity.upper()} (Score: {score:.2f})."
        }

    def calibrate_trust_level(self, generated_content: str) -> Dict:
        if "!!!" in generated_content or "CRITICAL" in generated_content.upper() or "EXTREME" in generated_content.upper():
            return {"status": "Warning", "score": 0.5, "reason": "High urgency detected - monitor for long-term customer trust."}
        return {"status": "Safe", "score": 0.9, "reason": "Balanced and organic scarcity messaging."}

    def process_batch_from_json(self, json_path: str, output_path: str):
        with open(json_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
            
        results = []
        for p in products:
            suitability = self.analyze_suitability(p)
            if suitability > 0.5:
                all_copies = self.generate_all_intensities(p['name'], "Get yours now.", pain_points=p.get('pain_points', []), product_info=p)
                recommendation = self.recommend_best_intensity(p['name'], "Get yours now.", all_copies, pain_points=p.get('pain_points', []), product_info=p)
                results.append({
                    "product": p['name'],
                    "category": p['category'],
                    "suitability": suitability,
                    "intensity_score": recommendation['intensity_score'],
                    "all_copies": all_copies,
                    "recommended_intensity": recommendation['recommended_intensity'],
                    "recommendation_reason": recommendation['reason']
                })
        
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        logger.info(f"Batch processing complete. Results saved to {output_path}")

if __name__ == "__main__":
    agent = ScarcityAgent()
    product = {"name": "Neuro-Headset 2.0", "price": 899, "category": "Tech"}
    
    suitability = agent.analyze_suitability(product)
    print(f"Suitability Score: {suitability}")
    
    score = agent.predict_intensity_score(product)
    print(f"Predicted Intensity Score (Regression): {score}")
    
    copy = agent.generate_scarcity_copy(
        product["name"], 
        "The ultimate tool for brain performance optimization."
    )
    print(f"Generated Copy: {copy}")
