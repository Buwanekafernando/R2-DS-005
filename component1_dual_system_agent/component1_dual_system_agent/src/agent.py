

import os
import torch
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from src.generator import (
    build_emotional_prompt,
    build_rational_prompt,
    build_hybrid_prompt,
    generate_copy
)

# ── Fix: absolute path ────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, "config", ".env"))


class DualSystemAgent:
    """
    Component 1 — Dual System Reasoning Agent
    Classifies a product as System 1 or System 2 and
    generates psychologically aligned marketing copy.

    Usage:
        agent = DualSystemAgent()
        result = agent.run("Sony Headphones", "Electronics")
        print(result['agent_output'])
    """

    def __init__(self,
                 model_path="models/roberta_checkpoint"):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        # Load your trained classifier from Step 1
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model     = AutoModelForSequenceClassification.from_pretrained(
            model_path
        )
        self.model     = self.model.to(self.device)
        self.model.eval()

        self.sia = SentimentIntensityAnalyzer()

        print(f"DualSystemAgent ready")
        print(f"  Model  : {model_path}")
        print(f"  Device : {self.device}")

   
    def classify(self, product_text, category="unknown", max_length=256):
        """Classify product into System 1 or System 2"""

        input_text = f"PRODUCT: {product_text}. REVIEW: {category}"

        encoding = self.tokenizer(
            input_text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**encoding)
            probs   = torch.softmax(outputs.logits, dim=1)
            pred    = torch.argmax(probs, dim=1).item()

        s2_prob    = round(probs[0][0].item(), 4)
        s1_prob    = round(probs[0][1].item(), 4)
        confidence = max(s1_prob, s2_prob)
        mode       = "System1" if pred == 1 else "System2"

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

        return {
            "cognitive_mode": mode,
            "label":          pred,
            "confidence":     round(confidence, 4),
            "s1_probability": s1_prob,
            "s2_probability": s2_prob,
            "reasoning":      reason
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

   
    def run(self, product_text, category="unknown"):
        """
        Main entry point — runs the full pipeline.
        Returns complete JSON-ready dictionary.
        Called by api/main.py and ui/app.py
        """

        # Stage 1 — Classify
        classification = self.classify(product_text, category)
        mode           = classification["cognitive_mode"]
        confidence     = classification["confidence"]
        s1_prob        = classification["s1_probability"]
        s2_prob        = classification["s2_probability"]

        # Stage 2 — Build prompts
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

        # Stage 3 — Generate copies
        emotional_copy = generate_copy(emo_prompt)
        time.sleep(1)
        rational_copy  = generate_copy(rat_prompt)

        if not emotional_copy or not rational_copy:
            return {"error": "Generation failed. Check LLM connection."}

        # Stage 4 — Evaluate copy quality
        emo_quality = self._evaluate_copy(emotional_copy, "emotional")
        rat_quality = self._evaluate_copy(rational_copy,  "rational")

        # Stage 5 — Select recommended strategy
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

        # Stage 6 — Return full output
        return {
            "input": {
                "product_text": product_text,
                "category":     category
            },
            "classification": {
                "cognitive_mode": mode,
                "label":          classification["label"],
                "confidence":     confidence,
                "s1_probability": s1_prob,
                "s2_probability": s2_prob,
                "copy_type":      copy_type,
                "reasoning":      classification["reasoning"]
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
        Run agent on a list of (product_text, category) tuples.
        Used for bulk evaluation in the notebook.

        Example:
            products = [("Sony Headphones", "Electronics"), ...]
            results  = agent.run_batch(products)
        """
        results = []
        total   = len(products_list)

        for i, (product, category) in enumerate(products_list):
            print(f"[{i+1}/{total}] {product[:50]}...")
            result = self.run(product, category)
            if result and "error" not in result:
                results.append(result)
            time.sleep(1)

        print(f"\nCompleted: {len(results)}/{total} products processed")
        return results