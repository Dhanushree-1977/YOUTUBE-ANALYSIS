"""
Unit tests for modules/data_cleaning.py
"""

import unittest
import pandas as pd
from modules.data_cleaning import clean_channel_data, calculate_engagement_rate


class TestDataCleaning(unittest.TestCase):

    def test_missing_values_and_types(self):
        raw_data = {
            "video_id": ["v1", "v2"],
            "title": [None, "Clean Title"],
            "views": ["1000", -50],  # Negative should be coerced to 0
            "likes": [None, "50"],
            "comments": [10, None],
            "published_at": ["2024-05-10T12:00:00Z", "invalid_date"]
        }
        df_raw = pd.DataFrame(raw_data)
        cleaned = clean_channel_data(df_raw)

        # Check title handling
        self.assertEqual(cleaned.iloc[0]["title"], "Untitled")
        self.assertEqual(cleaned.iloc[1]["title"], "Clean Title")

        # Check views and negative coercion
        self.assertEqual(cleaned.iloc[0]["views"], 1000)
        self.assertEqual(cleaned.iloc[1]["views"], 0)

        # Check engagement rate column derivation
        self.assertIn("engagement_rate", cleaned.columns)
        self.assertIn("publish_year", cleaned.columns)
        self.assertIn("publish_month", cleaned.columns)
        self.assertIn("publish_day", cleaned.columns)

    def test_empty_dataframe(self):
        empty_df = pd.DataFrame()
        cleaned = clean_channel_data(empty_df)
        self.assertTrue(cleaned.empty)


if __name__ == "__main__":
    unittest.main()
