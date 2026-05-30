import os
import torch
import time
import joblib          
import numpy as np     
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from src.generator import (
    build_emotional_prompt,
    build_rational_prompt,
    build_hybrid_prompt,
    generate_copy
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))


class DualSystemAgent:
    """
    Component 1 — Dual System Reasoning Agent
    Classifies a product as System 1 or System 2 and
    generates psychologically aligned marketing copy.

    Usage (product only — original behaviour unchanged):
        agent = DualSystemAgent()
        result = agent.run("Sony Headphones", "Electronics")
        print(result['agent_output'])

    Usage (with demographic profile — new behaviour):
        result = agent.run(
            "Sony Headphones", "Electronics",
            demographics={
                "gender": "Male",
                "age_range": "25 – 34",
                "district": "Colombo",
                ...
            }
        )
    """

    def __init__(self, model_path="models/roberta_checkpoint"):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # ── Load your trained classifier from Step 1 ─────
        # (unchanged from your original code)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model     = AutoModelForSequenceClassification.from_pretrained(
            model_path
        )
        self.model     = self.model.to(self.device)
        self.model.eval()

        self.sia = SentimentIntensityAnalyzer()

        self.demo_model   = self._load_pkl("models/demographic_classifier.pkl")
        self.meta_model   = self._load_pkl("models/fusion_meta_model.pkl")
        self.feature_cols = self._load_pkl("models/demographic_feature_cols.pkl")

        print(f"DualSystemAgent ready")
        print(f"  Model  : {model_path}")
        print(f"  Device : {self.device}")
        if self.demo_model:
            print(f"  Demographic model : loaded ✓")
        else:
            print(f"  Demographic model : not found (run notebooks 13 & 14)")


    def _load_pkl(self, relative_path):
        """Load a joblib pkl file. Returns None if file not found."""
        full_path = os.path.join(BASE_DIR, relative_path)
        if os.path.exists(full_path):
            return joblib.load(full_path)
        return None

    def _encode_demographics(self,
        gender,               
        age_range,           
        district,            
        occupation,           
        monthly_spending,     
        culture_influence,    
        avg_emotional_appeal,    
        emotional_reason_count,  # int 0–7
        rational_reason_count,   # int 0–7
        rational_check_total,    # int 0–21
        emotional_check_total    # int 0–7
    ):
        """
        Encodes all 11 features to match FEATURE_COLS:
        ['gender_enc', 'age_enc', 'environment_enc', 'occupation_enc',
         'spending_enc', 'culture_enc', 'avg_appeal_norm',
         'emotional_reason_count', 'rational_reason_count',
         'rational_check_total', 'emotional_check_total']
        """

        # gender_enc
        v = str(gender).strip().lower()
        gender_enc = 1.0 if 'female' in v else 0.0

        # age_enc
        age_map = {
            'under 18': 0, '18 – 24': 1, '25 – 34': 2,
            '35 – 44': 3, '45 – 54': 4, '55 and above': 5
        }
        age_enc = float(age_map.get(str(age_range).strip(), 2))

        # environment_enc — urban vs rural from district
        urban_districts = {
            'colombo', 'gampaha', 'kandy', 'galle', 'kalutara',
            'kurunegala', 'ratnapura', 'matara', 'jaffna'
        }
        environment_enc = 1.0 if str(district).strip().lower() in urban_districts else 0.0

        # occupation_enc
        occ_map = {
            'student':                       0.7,
            'homemaker':                     0.5,
            'private sector employee':       0.4,
            'government employee':           0.3,
            'self-employed / business owner':0.3,
            'other':                         0.5,
        }
        occupation_enc = occ_map.get(str(occupation).strip().lower(), 0.5)

        # spending_enc
        spend_map = {
            'less than rs. 5,000':    0.0,
            'rs. 5,000 – rs. 15,000': 0.25,
            'rs. 15,001 – rs. 30,000':0.5,
            'rs. 30,001 – rs. 50,000':0.75,
            'more than rs. 50,000':   1.0,
        }
        spending_enc = spend_map.get(str(monthly_spending).strip().lower(), 0.5)

        # culture_enc
        cv = str(culture_influence).strip().lower()
        culture_enc = (1.0 if 'strongly' in cv else
                       0.0 if 'no' in cv else 0.5)

        return np.array([
            gender_enc,
            age_enc,
            environment_enc,
            occupation_enc,
            spending_enc,
            culture_enc,
            float(avg_emotional_appeal)   if avg_emotional_appeal   is not None else 0.0,
            float(emotional_reason_count) if emotional_reason_count is not None else 0.0,
            float(rational_reason_count)  if rational_reason_count  is not None else 0.0,
            float(rational_check_total)   if rational_check_total   is not None else 0.0,
            float(emotional_check_total)  if emotional_check_total  is not None else 0.0,
        ]).reshape(1, -1)

#classification 
    def classify(self, product_text, category="unknown",
                 demographics=None, max_length=256):
        """
        Classify product into System 1 or System 2.

        Args:
            product_text : str
            category     : str
            demographics : dict | None  ← NEW optional parameter
            max_length   : int

        Returns:
            dict with cognitive_mode, confidence, probabilities, reasoning
        """

        input_text = f"PRODUCT: {product_text}. REVIEW: {category}"

        encoding = self.tokenizer(
            input_text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        # ── Your original RoBERTa inference (unchanged) ───
        with torch.no_grad():
            outputs = self.model(**encoding)
            probs   = torch.softmax(outputs.logits, dim=1)
            pred    = torch.argmax(probs, dim=1).item()

        s2_prob    = round(probs[0][0].item(), 4)
        s1_prob    = round(probs[0][1].item(), 4)

        
        classification_method = "product text only (RoBERTa)"

        if (demographics is not None and
                self.demo_model is not None and
                self.meta_model is not None):
            try:
                demo_feats = self._encode_demographics(
                    gender                = demographics.get('gender', 'Male'),
                    age_range             = demographics.get('age_range', '25 – 34'),
                    district              = demographics.get('district', 'Colombo'),
                    occupation            = demographics.get('occupation', 'Other'),
                    monthly_spending      = demographics.get('monthly_spending',
                                                             'Rs. 15,001 – Rs. 30,000'),
                    culture_influence     = demographics.get('culture_influence', 'Somewhat'),
                    avg_emotional_appeal  = demographics.get('avg_emotional_appeal', 0.0),
                    emotional_reason_count= demographics.get('emotional_reason_count', 0),
                    rational_reason_count = demographics.get('rational_reason_count', 0),
                    rational_check_total  = demographics.get('rational_check_total', 0),
                    emotional_check_total = demographics.get('emotional_check_total', 0),
                )

                roberta_probs_arr = np.array([s2_prob, s1_prob])
                demo_probs_arr    = self.demo_model.predict_proba(demo_feats)[0]

                combined = np.hstack([
                    roberta_probs_arr.reshape(1, -1),
                    demo_probs_arr.reshape(1, -1)
                ])
                fused   = self.meta_model.predict_proba(combined)[0]
                s2_prob = round(float(fused[0]), 4)
                s1_prob = round(float(fused[1]), 4)
                pred    = 1 if s1_prob > s2_prob else 0

                classification_method = "product + demographic fusion"

            except Exception as e:
                print(f"  Demographic fusion error: {e}. Using RoBERTa only.")
                # Fall back to original RoBERTa values (already set above)

        confidence = max(s1_prob, s2_prob)
        mode       = "System1" if pred == 1 else "System2"

        # Reasoning
        if pred == 1:
            reason = (
                "Strong emotional/impulsive purchase signal detected."
                if confidence > 0.85
                else "Moderate emotional purchase signal detected."
            )
        else:
            reason = (
                "Strong rational/deliberate purchase signal detected."
                if confidence > 0.85
                else "Moderate rational purchase signal detected."
            )

        # ── NEW: append demographic context to reasoning ──
        if demographics is not None and classification_method != "product text only (RoBERTa)":
            age      = demographics.get('age_range', '')
            district = demographics.get('district', '')
            if age and district:
                reason += f" Profile: {age} from {district}."

        return {
            "cognitive_mode":          mode,
            "label":                   pred,
            "confidence":              round(confidence, 4),
            "s1_probability":          s1_prob,
            "s2_probability":          s2_prob,
            "reasoning":               reason,
            "classification_method":   classification_method,   # ← NEW field
        }

    def _evaluate_copy(self, text, expected_mode):
        """Score how well generated copy matches the intended mode"""

        words      = text.lower().split()
        sentiment  = self.sia.polarity_scores(text)

        s1_markers = ['feel', 'love', 'amazing', 'perfect', 'beautiful',
                      'enjoy', 'experience', 'dream', 'wonderful', '!']
        s2_markers = ['features', 'performance', 'quality', 'reliable',
                      'efficient', 'proven', 'compare', 'specifications',
                      'battery', 'compatible', 'warranty', 'technology']

        s1_hits = sum(1 for w in s1_markers if w in words)
        s2_hits = sum(1 for w in s2_markers if w in words)

        if expected_mode == "emotional":
            alignment = min(
                s1_hits / max(s1_hits + s2_hits, 1), 1.0
            )
        else:
            alignment = min(
                s2_hits / max(s1_hits + s2_hits, 1), 1.0
            )

        return {
            "sentiment_compound": round(sentiment["compound"], 4),
            "sentiment_positive": round(sentiment["pos"], 4),
            "word_count":         len(words),
            "mode_alignment":     round(alignment, 4),
        }

  
    def run(self, product_text, category="unknown", demographics=None):
        """
        Main entry point — runs the full pipeline.
        Returns complete JSON-ready dictionary.
        Called by api/main.py and ui/app.py

        Args:
            product_text : str
            category     : str
            demographics : dict | None  ← NEW optional parameter
        """

        # Stage 1 — Classify (now passes demographics through)
        classification = self.classify(product_text, category, demographics)
        mode           = classification["cognitive_mode"]
        confidence     = classification["confidence"]
        s1_prob        = classification["s1_probability"]
        s2_prob        = classification["s2_probability"]

        # Stage 2 — Build prompts (unchanged)
        if confidence < 0.65:
            emo_prompt = build_hybrid_prompt(
                product_text, category, s1_prob, s2_prob
            )
            copy_type  = "hybrid"
        else:
            emo_prompt = build_emotional_prompt(
                product_text, category, confidence
            )
            copy_type  = "standard"

        rat_prompt = build_rational_prompt(
            product_text, category, confidence
        )

        # Stage 3 — Generate copies (unchanged)
        emotional_copy = generate_copy(emo_prompt)
        time.sleep(1)
        rational_copy  = generate_copy(rat_prompt)

        if not emotional_copy or not rational_copy:
            return {"error": "Generation failed. Check LLM connection."}

        # Stage 4 — Evaluate copy quality (unchanged)
        emo_quality = self._evaluate_copy(emotional_copy, "emotional")
        rat_quality = self._evaluate_copy(rational_copy,  "rational")

        # Stage 5 — Select recommended strategy (unchanged)
        if confidence >= 0.65:
            strategy         = "emotional" if mode == "System1" else "rational"
            recommended_copy = (
                emotional_copy if mode == "System1" else rational_copy
            )
        else:
            if emo_quality["mode_alignment"] >= rat_quality["mode_alignment"]:
                strategy, recommended_copy = "emotional", emotional_copy
            else:
                strategy, recommended_copy = "rational",  rational_copy

        return {
            "input": {
                "product_text": product_text,
                "category":     category,
                "demographics": demographics or {},   # ← NEW field
            },
            "classification": {
                "cognitive_mode":          mode,
                "label":                   classification["label"],
                "confidence":              confidence,
                "s1_probability":          s1_prob,
                "s2_probability":          s2_prob,
                "copy_type":               copy_type,
                "reasoning":               classification["reasoning"],
                "classification_method":   classification["classification_method"],  # ← NEW
            },
            "generated_copy": {
                "emotional": {
                    "text":    emotional_copy,
                    "quality": emo_quality
                },
                "rational": {
                    "text":    rational_copy,
                    "quality": rat_quality
                }
            },
            "recommendation": {
                "strategy":      strategy,
                "selected_copy": recommended_copy,
                "explanation": (
                    f"Product classified as {mode} with "
                    f"{confidence:.0%} confidence. "
                    f"{strategy.capitalize()} strategy selected."
                )
            },
            # ── This is what Components 2, 3, 4 receive ──
            "agent_output": {
                "cognitive_mode":   mode,
                "confidence":       confidence,
                "strategy":         strategy,
                "emotional_copy":   emotional_copy,
                "rational_copy":    rational_copy,
                "recommended_copy": recommended_copy
            }
        }

    def run_batch(self, products_list):
        """
        Run agent on a list of products.

        Original usage (unchanged):
            products = [("Sony Headphones", "Electronics"), ...]
            results  = agent.run_batch(products)

        New usage with demographics:
            products = [
                {
                    "product_text": "Sony Headphones",
                    "category":     "Electronics",
                    "demographics": {"gender": "Male", ...}
                },
                ...
            ]
            results = agent.run_batch(products)
        """
        results = []
        total   = len(products_list)

        for i, item in enumerate(products_list):

            # ── Support both original tuple format and new dict format ──
            if isinstance(item, (list, tuple)):
                # Original format: (product_text, category)
                product      = item[0]
                category     = item[1] if len(item) > 1 else "unknown"
                demographics = None
            else:
                # New dict format
                product      = item.get("product_text", "")
                category     = item.get("category", "unknown")
                demographics = item.get("demographics", None)

            print(f"[{i+1}/{total}] {product[:50]}...")
            result = self.run(product, category, demographics)

            if result and "error" not in result:
                results.append(result)
            time.sleep(1)

        print(f"\nCompleted: {len(results)}/{total} products processed")
        return results