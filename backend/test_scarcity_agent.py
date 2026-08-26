import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from utils.scarcity_agent import ScarcityAgent

class TestScarcityAgentRegression(unittest.TestCase):

    def setUp(self):
        self.agent = ScarcityAgent()

    def test_analyze_suitability(self):
        score = self.agent.analyze_suitability({"price": 1000, "category": "luxury"})
        self.assertTrue(0.0 <= score <= 1.0)

    def test_predict_intensity_score_regression(self):
        score = self.agent.predict_intensity_score(
            product_info={"price": 899, "category": "tech"},
            pain_points=["Stock Instability", "Shipping Delays"]
        )
        self.assertTrue(0.0 <= score <= 1.0)
        self.assertIsInstance(score, float)

    def test_offline_scarcity_copy(self):
        copy = self.agent._offline_scarcity_copy("Test Product", "Great product", "medium")
        self.assertIn("Test Product", copy)
        self.assertIn("Great product", copy)

    def test_calibrate_trust_level(self):
        result = self.agent.calibrate_trust_level("Normal copy")
        self.assertIn("status", result)
        self.assertIn("score", result)

    def test_trained_regression_model_is_available(self):
        self.assertTrue(self.agent.model_path.exists())
        self.assertIsNotNone(self.agent.local_model)

if __name__ == "__main__":
    unittest.main()