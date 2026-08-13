"""
Unit tests for PII Redaction Tool evaluation metrics and metric verifier.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluate import EvaluationMetrics, evaluate_detectors


class TestEvaluationMetrics(unittest.TestCase):
    """Test mathematical precision, recall, F1, and coverage formulas."""

    def test_perfect_metrics(self):
        """TP=30, FP=0, FN=0 -> Precision=1.0, Recall=1.0, F1=1.0."""
        m = EvaluationMetrics(tp=30, fp=0, fn=0)
        self.assertEqual(m.precision, 1.0)
        self.assertEqual(m.recall, 1.0)
        self.assertEqual(m.f1, 1.0)

    def test_baseline_metrics(self):
        """Historical baseline: TP=22, FP=0, FN=8 -> Precision=1.0, Recall=0.7333..., F1=0.84615..."""
        m = EvaluationMetrics(tp=22, fp=0, fn=8)
        self.assertEqual(m.precision, 1.0)
        self.assertAlmostEqual(m.recall, 22 / 30, places=4)
        self.assertAlmostEqual(m.f1, 44 / 52, places=4)

    def test_zero_denominator_safety(self):
        """Zero counts should return 0.0 without division by zero errors."""
        m = EvaluationMetrics(tp=0, fp=0, fn=0)
        self.assertEqual(m.precision, 0.0)
        self.assertEqual(m.recall, 0.0)
        self.assertEqual(m.f1, 0.0)

    def test_gold_standard_benchmark_evaluation(self):
        """Running evaluate_detectors against gold_standard.json must yield TP=30, FP=0, FN=0."""
        category_metrics, overall, sample_results = evaluate_detectors()
        self.assertEqual(overall.tp, 30)
        self.assertEqual(overall.fp, 0)
        self.assertEqual(overall.fn, 0)
        self.assertEqual(overall.precision, 1.0)
        self.assertEqual(overall.recall, 1.0)
        self.assertEqual(overall.f1, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
