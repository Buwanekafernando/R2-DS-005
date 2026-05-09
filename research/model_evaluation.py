"""
Model Evaluation & Metrics Framework
Evaluates the accuracy and performance of Scarcity Agent models
"""

import json
from typing import List, Dict, Tuple

# Optional imports - don't fail if not available
try:
    import numpy as np
except ImportError:
    np = None

try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
except ImportError:
    pass

try:
    from scarcity_agent import ScarcityAgent
except ImportError:
    ScarcityAgent = None

class ModelEvaluator:
    """Evaluates model performance with standard ML metrics"""
    
    def __init__(self):
        self.agent = ScarcityAgent()
        self.results = {}
    
    # ============================================
    # 1. SUITABILITY MODEL EVALUATION
    # ============================================
    
    def evaluate_suitability_model(self, test_data: List[Dict]) -> Dict:
        """
        Evaluates suitability classification model
        
        Args:
            test_data: List of dicts with {product_info, true_label}
                      true_label: 1 if scarcity is suitable, 0 if not
        
        Returns:
            Metrics dict with accuracy, precision, recall, F1
        """
        predictions = []
        ground_truth = []
        
        for item in test_data:
            pred_score = self.agent.analyze_suitability(item['product_info'])
            # Convert continuous score to binary (threshold: 0.6)
            pred_label = 1 if pred_score > 0.6 else 0
            predictions.append(pred_label)
            ground_truth.append(item['true_label'])
        
        metrics = {
            "model": "Suitability Analysis",
            "accuracy": accuracy_score(ground_truth, predictions),
            "precision": precision_score(ground_truth, predictions, zero_division=0),
            "recall": recall_score(ground_truth, predictions, zero_division=0),
            "f1": f1_score(ground_truth, predictions, zero_division=0),
            "confusion_matrix": confusion_matrix(ground_truth, predictions).tolist()
        }
        
        self.results['suitability'] = metrics
        return metrics
    
    # ============================================
    # 2. PAIN POINT EXTRACTION EVALUATION
    # ============================================
    
    def evaluate_pain_point_extraction(self, test_reviews: List[Dict]) -> Dict:
        """
        Evaluates pain point extraction accuracy
        
        Args:
            test_reviews: List of dicts with {review_text, true_pain_points}
        
        Returns:
            Metrics dict with accuracy, precision, recall, F1
        """
        correct = 0
        precision_scores = []
        recall_scores = []
        
        for item in test_reviews:
            predicted = self._extract_pain_points(item['review_text'])
            true = set(item['true_pain_points'])
            predicted_set = set(predicted)
            
            # Exact match
            if predicted_set == true:
                correct += 1
            
            # Calculate per-sample precision and recall
            if len(predicted_set) > 0:
                precision = len(predicted_set & true) / len(predicted_set)
                precision_scores.append(precision)
            
            if len(true) > 0:
                recall = len(predicted_set & true) / len(true)
                recall_scores.append(recall)
        
        accuracy = correct / len(test_reviews)
        avg_precision = np.mean(precision_scores) if precision_scores else 0
        avg_recall = np.mean(recall_scores) if recall_scores else 0
        avg_f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
        
        metrics = {
            "model": "Pain Point Extraction",
            "accuracy": accuracy,
            "precision": avg_precision,
            "recall": avg_recall,
            "f1": avg_f1,
            "samples": len(test_reviews)
        }
        
        self.results['pain_extraction'] = metrics
        return metrics
    
    # ============================================
    # 3. TRUST CALIBRATION MODEL EVALUATION
    # ============================================
    
    def evaluate_trust_calibration(self, test_copies: List[Dict]) -> Dict:
        """
        Evaluates trust calibration model
        
        Args:
            test_copies: List of dicts with {copy_text, true_label}
                        true_label: 1 if authentic, 0 if manipulative
        
        Returns:
            Metrics dict with accuracy, precision, recall, F1
        """
        predictions = []
        ground_truth = []
        
        for item in test_copies:
            result = self.agent.calibrate_trust_level(item['copy_text'])
            # Convert to binary: Safe=1, Warning=0
            pred_label = 1 if result['status'] == 'Safe' else 0
            predictions.append(pred_label)
            ground_truth.append(item['true_label'])
        
        metrics = {
            "model": "Trust Calibration",
            "accuracy": accuracy_score(ground_truth, predictions),
            "precision": precision_score(ground_truth, predictions, zero_division=0),
            "recall": recall_score(ground_truth, predictions, zero_division=0),
            "f1": f1_score(ground_truth, predictions, zero_division=0),
            "confusion_matrix": confusion_matrix(ground_truth, predictions).tolist()
        }
        
        self.results['trust_calibration'] = metrics
        return metrics
    
    # ============================================
    # 4. HELPER METHODS
    # ============================================
    
    def _extract_pain_points(self, review_text: str) -> List[str]:
        """Extract pain points from review text (same logic as dataset_processor)"""
        body = review_text.lower()
        pain_points = []
        
        if "slow" in body or "wait" in body:
            pain_points.append("Shipping Delays")
        if "sold out" in body or "waitlist" in body:
            pain_points.append("Stock Instability")
        if "expensive" in body or "price" in body:
            pain_points.append("Price Sensitivity")
        
        return pain_points
    
    def generate_report(self) -> Dict:
        """Generate comprehensive evaluation report"""
        from datetime import datetime
        report = {
            "timestamp": str(datetime.now()),
            "models_evaluated": list(self.results.keys()),
            "detailed_results": self.results,
            "summary": self._calculate_summary()
        }
        return report
    
    def _calculate_summary(self) -> Dict:
        """Calculate summary statistics across all models"""
        if not self.results:
            return {}
        
        f1_scores = [v['f1'] for v in self.results.values()]
        accuracies = [v['accuracy'] for v in self.results.values()]
        
        if np:
            avg_f1 = np.mean(f1_scores)
            avg_accuracy = np.mean(accuracies)
        else:
            avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
            avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        return {
            "avg_f1": avg_f1,
            "avg_accuracy": avg_accuracy,
            "best_f1_model": max(self.results.items(), key=lambda x: x[1]['f1'])[0],
            "best_accuracy_model": max(self.results.items(), key=lambda x: x[1]['accuracy'])[0]
        }


# ============================================
# CURRENT MODEL PERFORMANCE ASSESSMENT
# ============================================

def assess_current_models() -> Dict:
    """
    Assess current models without ground truth data
    Provides theoretical accuracy estimates
    """
    
    assessment = {
        "Suitability Model": {
            "type": "Heuristic Decision Tree",
            "current_status": "Rule-based, no ML training",
            "estimated_accuracy": "65-75%",
            "reason": "Works for obvious cases (luxury/high-price), but may miss nuanced products",
            "limitations": [
                "Fixed thresholds ($500, luxury categories)",
                "Doesn't learn from actual customer response",
                "No personalization"
            ],
            "needs_improvement": [
                "Train on actual conversion data",
                "Add more category/price combinations",
                "Incorporate customer demographics"
            ]
        },
        
        "Pain Point Extraction": {
            "type": "Keyword Matching",
            "current_status": "Rule-based NLP",
            "estimated_accuracy": "70-80%",
            "reason": "Keyword matching is reliable but may miss synonyms",
            "limitations": [
                "Only 6 keywords total",
                "No semantic understanding",
                "Case-sensitive operations"
            ],
            "needs_improvement": [
                "Use NLP pre-trained models (BERT, RoBERTa)",
                "Expand keyword lists with synonyms",
                "Implement stemming/lemmatization"
            ]
        },
        
        "Trust Calibration": {
            "type": "Pattern Matching",
            "current_status": "Rule-based validation",
            "estimated_accuracy": "60-70%",
            "reason": "Only 2 red flags detected; may miss subtle manipulation",
            "limitations": [
                "Only detects '!!!' and 'HURRY'",
                "Binary output (Safe/Warning)",
                "No confidence scoring"
            ],
            "needs_improvement": [
                "Train on human-labeled authentic/manipulative copy",
                "Add readability metrics",
                "Implement sentiment analysis"
            ]
        },
        
        "Grok-1 LLM": {
            "type": "Large Language Model",
            "current_status": "API-based, pre-trained by xAI",
            "estimated_accuracy": "80-90%",
            "reason": "LLMs excel at creative, context-aware generation",
            "limitations": [
                "Depends on prompt quality",
                "No fine-tuning on scarcity psychology",
                "API costs scale with usage"
            ],
            "needs_improvement": [
                "Fine-tune on marketing psychology corpus",
                "A/B test generated copy against human-written",
                "Add in-context learning examples"
            ]
        }
    }
    
    return assessment


if __name__ == "__main__":
    print("=" * 60)
    print("MODEL EVALUATION FRAMEWORK INITIALIZED")
    print("=" * 60)
    
    # Show current model assessment
    assessment = assess_current_models()
    
    for model_name, details in assessment.items():
        print(f"\n📊 {model_name}")
        print(f"   Type: {details['type']}")
        print(f"   Status: {details['current_status']}")
        print(f"   Est. Accuracy: {details['estimated_accuracy']}")
        print(f"   Reason: {details['reason']}")
    
    print("\n" + "=" * 60)
    print("To run full evaluation, provide labeled test data:")
    print("  evaluator = ModelEvaluator()")
    print("  evaluator.evaluate_suitability_model(test_data)")
    print("=" * 60)
