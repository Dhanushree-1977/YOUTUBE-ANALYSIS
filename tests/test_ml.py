"""
Unit tests for modules/ml_evaluation.py
"""

import unittest
import numpy as np
import pandas as pd
from modules.ml_evaluation import prepare_features, train_and_evaluate_rf_model, FEATURE_COLUMNS


class TestMLEvaluation(unittest.TestCase):

    def test_no_data_leakage(self):
        # Ensure likes and comments are strictly EXCLUDED from feature columns
        self.assertNotIn("likes", FEATURE_COLUMNS)
        self.assertNotIn("comments", FEATURE_COLUMNS)
        self.assertNotIn("like_ratio", FEATURE_COLUMNS)
        self.assertNotIn("engagement_rate", FEATURE_COLUMNS)

    def test_feature_preparation_shape(self):
        df = pd.DataFrame({
            "title": ["Title One", "Second Longer Title Here"],
            "views": [10000, 25000],
            "description_length": [300, 500],
            "tag_count": [10, 15],
            "publish_day": ["Monday", "Friday"],
            "publish_hour": [14, 18]
        })
        X, y = prepare_features(df)
        self.assertEqual(len(X), 2)
        self.assertEqual(len(y), 2)
        self.assertEqual(list(X.columns), FEATURE_COLUMNS)

    def test_model_training_and_baseline_comparison(self):
        # Generate small synthetic dataset (> 15 rows)
        np.random.seed(42)
        records = []
        for i in range(25):
            records.append({
                "title": f"Video Tutorial Episode {i}",
                "views": np.random.randint(5000, 50000),
                "description_length": np.random.randint(100, 800),
                "tag_count": np.random.randint(5, 20),
                "publish_day": "Wednesday",
                "publish_hour": 15
            })
        df = pd.DataFrame(records)

        result = train_and_evaluate_rf_model(df, test_size=0.25, random_state=42)
        self.assertEqual(result["status"], "success")
        self.assertIn("rf_mae", result["metrics"])
        self.assertIn("baseline_mae", result["metrics"])
        self.assertIn("rf_rmse", result["metrics"])
        self.assertIn("rf_r2", result["metrics"])


if __name__ == "__main__":
    unittest.main()
