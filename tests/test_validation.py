"""
Unit tests for modules/validation.py
"""

import unittest
import pandas as pd
from modules.validation import generate_data_quality_report


class TestValidation(unittest.TestCase):

    def test_quality_report_keys_and_metrics(self):
        df = pd.DataFrame({
            "video_id": ["v1", "v2", "v2"],  # 1 duplicate video ID
            "title": ["Video 1", "Video 2", "Video 2 Duplicate"],
            "views": [1000, 2000, 3000],
            "likes": [50, 100, 150],
            "comments": [5, 10, 15],
            "published_at": ["2024-01-01T00:00:00Z", "2024-02-01T00:00:00Z", "2024-03-01T00:00:00Z"],
            "category_name": ["Education", "Education", "Tech"]
        })

        report = generate_data_quality_report(df, data_source="Test Source")

        self.assertEqual(report["status"], "success")
        self.assertEqual(report["total_records"], 3)
        self.assertEqual(report["duplicate_video_ids"], 1)
        self.assertEqual(report["unique_video_ids"], 2)
        self.assertEqual(report["missing_titles"], 0)
        self.assertEqual(report["missing_views"], 0)
        self.assertIn("Education", report["available_categories"])
        self.assertEqual(report["data_source"], "Test Source")
        self.assertGreaterEqual(report["quality_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
