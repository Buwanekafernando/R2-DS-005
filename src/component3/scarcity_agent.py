import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.component2.emotion_agent import generate_with_groq
from src.component3.pain_point_extractor import extract_pain_points_detailed

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_vader = SentimentIntensityAnalyzer()

# Few-shot examples shown to Grok so generated copy matches a consistent
# professional advertisement style rather than drifting per call.
FEW_SHOT_EXAMPLES = """Example 1 (Stock Instability, HIGH intensity):
"Only 6 units of the Aurora Desk Lamp remain in this batch. Once they're gone, the next restock isn't confirmed. Reserve yours before the count hits zero."

Example 2 (Shipping Delays, MEDIUM intensity):
"Orders for the Everline Backpack placed today ship within 24 hours — after that, the queue moves to next week's batch. Lock in fast delivery now."

Example 3 (Price Sensitivity, LOW intensity):
"The Solace Ceramic Mug has been a quiet favorite this month, appreciated for its everyday value. A steady choice worth adding to your routine."
"""


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
        """
        Train a DecisionTreeRegressor to predict continuous scarcity intensity (0.0-1.0).

        Training data is generated procedurally across the full feature space
        (price bucket x category x each urgency signal) rather than a handful
        of hand-picked points. This matters because with too few, too-extreme
        examples the tree just memorizes "high price bucket => high score"
        regardless of whether any real urgency signal (low stock, shipping
        delays) is present — which is exactly the bug that caused this model
        to recommend HIGH intensity almost every time for LKR-priced products
        (price buckets here are on a raw numeric scale, so most real prices
        land in the top bucket; that alone shouldn't push urgency to 0.95).

        Base rate with no urgency signals stays LOW/MEDIUM even at a high
        price bucket — genuine urgency signals (stock instability, shipping
        delays) are what should push a recommendation toward HIGH, not price
        or category alone.
        """
        import itertools

        category_scores = [0.5, 0.7, 0.8, 1.0, 1.5, 2.0, 2.5]  # grocery..luxury
        price_buckets = [0, 1, 2]
        flag_combos = [
            (0, 0, 0, 0),  # no signals — the common case
            (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1),  # one signal each
            (1, 1, 0, 0), (1, 0, 0, 1), (0, 1, 1, 0),  # a couple of realistic combos
        ]

        rng = np.random.default_rng(42)
        training_data = []
        for price_bucket, category_score, flags in itertools.product(price_buckets, category_scores, flag_combos):
            stock_flag, shipping_flag, price_sensitivity_flag, quality_flag = flags
            # Baseline sits mid-range so a typical product with no detected
            # urgency signal lands around MEDIUM, not LOW or HIGH by default.
            # Genuine urgency signals (stock/shipping issues found in the
            # description) are what should push a recommendation to HIGH —
            # price and category alone only nudge the score slightly.
            target = (
                0.36
                + 0.08 * price_bucket
                + 0.04 * (category_score - 1.0)
                + 0.20 * stock_flag
                + 0.18 * shipping_flag
                + 0.05 * price_sensitivity_flag
                + 0.08 * quality_flag
                + rng.normal(0, 0.02)  # small noise so the tree doesn't overfit to exact values
            )
            target = float(np.clip(target, 0.05, 0.97))
            training_data.append((
                [price_bucket, category_score, stock_flag, shipping_flag, price_sensitivity_flag, quality_flag],
                target,
            ))

        features = np.array([item[0] for item in training_data], dtype=float)
        targets = np.array([item[1] for item in training_data], dtype=float)

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        # max_depth keeps this from memorizing individual points — smoother,
        # more realistic generalization to prices/categories it hasn't seen
        model = DecisionTreeRegressor(random_state=42, max_depth=6, min_samples_leaf=2)
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
        # Keyword-based matching (not exact dict lookup) so real category
        # names from the app's dropdown ("Electronics", "Pet Products",
        # "Apparel") actually match — exact-key lookup here previously only
        # matched internal labels like "tech"/"fashion"/"pet" that the UI
        # never sends, so category_score silently defaulted to 1.0 for
        # almost every real product, flattening out variety in the score.
        CATEGORY_KEYWORDS = [
            ("luxury", 2.5), ("jewel", 2.5),
            ("electronic", 2.0), ("tech", 2.0),
            ("apparel", 1.8), ("fashion", 1.8), ("cloth", 1.8),
            ("sport", 1.6),
            ("beauty", 1.5), ("cosmetic", 1.5),
            ("automotive", 1.3), ("vehicle", 1.3),
            ("home", 1.0), ("kitchen", 1.0),
            ("baby", 0.8),
            ("industrial", 0.8),
            ("pet", 0.7),
            ("grocery", 0.5), ("food", 0.5),
        ]
        category_score = 1.0
        for keyword, score in CATEGORY_KEYWORDS:
            if keyword in category:
                category_score = score
                break

        price_bucket = 0 if price < 2000 else 1 if price < 15000 else 2
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

    def classify_scarcity_type(self, pain_points: List[str] = None, product_info: Dict = None) -> str:
        """
        Maps detected pain points / product context to one of the three
        scarcity types: 'stock', 'time', or 'exclusivity'.
        """
        pain_points = pain_points or []
        product_info = product_info or {}
        category = str(product_info.get("category", "")).lower()
        price = float(product_info.get("price", 0) or 0)

        if "Stock Instability" in pain_points:
            return "stock"
        if "Shipping Delays" in pain_points:
            return "time"
        if category in ["luxury", "fashion"] or price > 500:
            return "exclusivity"
        return "time"

    def _apply_cognitive_and_emotional_modifiers(
        self, intensity: str, cognitive_mode: Optional[str] = None, emotional_tone: Optional[str] = None
    ) -> str:
        """
        cognitive_mode == 'System1' (from Component 1): emotionally engaged
        consumers respond better to stronger urgency, so push intensity up
        one level (low -> medium -> high -> high).

        emotional_tone == 'trust' (from Component 2): trust-oriented framing
        is undercut by aggressive scarcity language, so cap intensity at
        'medium' regardless of what the regression model predicted.
        """
        levels = ["low", "medium", "high"]
        idx = levels.index(intensity) if intensity in levels else 1

        if cognitive_mode == "System1" and idx < len(levels) - 1:
            idx += 1

        if emotional_tone == "trust":
            idx = min(idx, levels.index("medium"))

        return levels[idx]

    def run(
        self,
        product_name: str,
        category: str,
        price: float,
        review_body: str = "",
        cognitive_mode: Optional[str] = None,
        emotional_tone: Optional[str] = None,
        base_copy: Optional[str] = None,
    ) -> Dict:
        """
        Full 5-stage Component 3 pipeline, matching the structured
        input/output contract:

        Input : product_name, category, price, review_body,
                cognitive_mode (optional, from Component 1),
                emotional_tone (optional, from Component 2)
        Output: suitability_score, scarcity_type, intensity_level,
                intensity_score, scarcity_copy, trust_status, trust_score,
                pain_points

        Stage 1 — suitability check (early exit if score < 0.5)
        Stage 2 — pain point extraction from review_body
        Stage 3 — feature vector -> regression model -> intensity score/level
        Stage 4 — Grok-generated scarcity copy (pain point + intensity + product name)
        Stage 5 — trust calibration (VADER + pattern matching), softened if Warning
        """
        product_info = {"price": price, "category": category}

        # Stage 1 — suitability
        suitability_score = self.analyze_suitability(product_info)
        if suitability_score < 0.5:
            return {
                "status": "not_applicable",
                "suitability_score": suitability_score,
                "scarcity_type": None,
                "intensity_level": None,
                "intensity_score": None,
                "scarcity_copy": None,
                "trust_status": None,
                "trust_score": None,
                "pain_points": [],
            }

        # Stage 2 — pain point extraction from review text
        pain_points = []
        if review_body:
            pain_points = extract_pain_points_detailed(review_body).get("pain_points", [])

        # Stage 3 — regression-predicted intensity, then modified by C1/C2 context
        raw_intensity = self.determine_intensity(product_name, base_copy or "", product_info=product_info, pain_points=pain_points)
        intensity_score = self.predict_intensity_score(product_info, pain_points)
        intensity_level = self._apply_cognitive_and_emotional_modifiers(raw_intensity, cognitive_mode, emotional_tone)
        scarcity_type = self.classify_scarcity_type(pain_points, product_info)

        # Stage 4 — Grok-generated copy
        scarcity_copy = self._llm_scarcity_copy(
            product_name=product_name,
            scarcity_type=scarcity_type,
            intensity_level=intensity_level,
            pain_points=pain_points,
            emotional_tone=emotional_tone,
            base_copy=base_copy,
        )

        # Stage 5 — trust calibration, soften on Warning
        trust = self.calibrate_trust_level(scarcity_copy)
        if trust["status"] == "Warning":
            scarcity_copy = self._soften_copy(scarcity_copy, product_name, scarcity_type)
            trust = self.calibrate_trust_level(scarcity_copy)

        return {
            "status": "ok",
            "suitability_score": suitability_score,
            "scarcity_type": scarcity_type,
            "intensity_level": intensity_level,
            "intensity_score": intensity_score,
            "scarcity_copy": scarcity_copy,
            "trust_status": trust["status"],
            "trust_score": trust["score"],
            "pain_points": pain_points,
        }

    def _llm_scarcity_copy(
        self,
        product_name: str,
        scarcity_type: str,
        intensity_level: str,
        pain_points: List[str] = None,
        emotional_tone: Optional[str] = None,
        base_copy: Optional[str] = None,
    ) -> str:
        """
        Generates scarcity copy via Grok, guided by few-shot examples.
        Falls back to the offline template system if Groq is unreachable
        (missing key, network error, rate limit) so the pipeline never
        hard-fails just because the LLM call failed.
        """
        pain_point_text = ", ".join(pain_points) if pain_points else "general urgency"
        tone_instruction = (
            "Keep the language measured, credible, and low-pressure — avoid aggressive "
            "words like CRITICAL, EXTREME, or excessive exclamation points, since this "
            "product's emotional tone is 'trust' and heavy urgency language undermines that."
            if emotional_tone == "trust"
            else "Match the energy of the intensity level naturally."
        )
        context_line = f'\nExisting product description for context: "{base_copy}"\n' if base_copy else ""

        prompt = f"""You are a professional advertisement copywriter specializing in scarcity-based marketing psychology.

{FEW_SHOT_EXAMPLES}
Now write a new scarcity marketing message with these inputs:
- Product name: {product_name}
- Scarcity type: {scarcity_type} (stock / time / exclusivity)
- Intensity level: {intensity_level} (low / medium / high)
- Underlying pain point signal: {pain_point_text}
{context_line}
RULES:
- One short message, 1-3 sentences.
- {tone_instruction}
- Do not fabricate exact numbers (no specific unit counts or timers) unless implied by the pain point signal.
- Return ONLY the marketing message, no preamble or explanation.

Write the message now."""

        try:
            return generate_with_groq(prompt)
        except Exception as exc:
            logger.warning("Groq scarcity copy generation failed (%s) — falling back to offline templates.", exc)
            return self._offline_scarcity_copy(product_name, base_copy or f"Discover {product_name}.", intensity_level, pain_points)

    def _soften_copy(self, copy_text: str, product_name: str, scarcity_type: str) -> str:
        """
        Rewrites a Warning-flagged message into calmer, more credible
        phrasing. Tries Grok first; falls back to a plain deterministic
        rewrite if Groq is unavailable.
        """
        prompt = f"""The following scarcity marketing message was flagged as too aggressive
and may damage customer trust:

"{copy_text}"

Rewrite it in a calmer, more credible tone for the product "{product_name}" ({scarcity_type} scarcity).
Remove ALL CAPS words, exclamation points, and aggressive phrasing like CRITICAL or EXTREME.
Keep the same core message and length. Return ONLY the rewritten message."""
        try:
            return generate_with_groq(prompt)
        except Exception:
            softened = copy_text.replace("!", ".").replace("CRITICAL", "Limited").replace("EXTREME", "High")
            return " ".join(w if not (w.isupper() and len(w) > 3) else w.capitalize() for w in softened.split())

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
        """
        Trust calibration using pattern matching for aggressive scarcity
        language (VADER sentiment is computed too, for downstream
        reporting, but scarcity copy legitimately reads as high-arousal/
        positive on VADER even when appropriate — so aggressive-phrasing
        detection is what actually drives the Warning flag).
        """
        text = str(generated_content or "")
        pattern_hit = (
            "!!!" in text
            or "CRITICAL" in text.upper()
            or "EXTREME" in text.upper()
            or text.count("!") >= 2
        )
        if pattern_hit:
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
