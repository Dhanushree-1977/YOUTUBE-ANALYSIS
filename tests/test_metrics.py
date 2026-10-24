"""
Unit tests for modules/metrics.py
"""

import unittest
import pandas as pd
from modules.metrics import (
    calculate_engagement_rate, calculate_kpis, get_top_videos,
    generate_plain_english_insights, calculate_channel_score, compare_two_videos,
    generate_smart_recommendations
)


class TestMetrics(unittest.TestCase):

    def test_engagement_rate_formula(self):
        # 100,000 views, 5,000 likes, 500 comments -> ((5000 + 500) / 100000) * 100 = 5.5%
        res = calculate_engagement_rate(likes=5000, comments=500, views=100000)
        self.assertAlmostEqual(res, 5.5, places=2)

    def test_engagement_rate_zero_views(self):
        # Edge case: zero views should safely return 0.0 without ZeroDivisionError
        res = calculate_engagement_rate(likes=10, comments=5, views=0)
        self.assertEqual(res, 0.0)

    def test_kpis_calculation(self):
        data = {
            "views": [1000, 2000, 3000],
            "likes": [50, 100, 150],
            "comments": [5, 10, 15],
            "engagement_rate": [5.5, 5.5, 5.5]
        }
        df = pd.DataFrame(data)
        kpis = calculate_kpis(df)

        self.assertEqual(kpis["total_videos"], 3)
        self.assertEqual(kpis["total_views"], 6000)
        self.assertEqual(kpis["total_likes"], 300)
        self.assertEqual(kpis["total_comments"], 30)
        self.assertEqual(kpis["avg_views"], 2000)
        self.assertEqual(kpis["median_views"], 2000)
        self.assertAlmostEqual(kpis["avg_engagement_rate"], 5.5, places=1)

    def test_top_videos_sorting(self):
        data = {
            "title": ["Video A", "Video B", "Video C"],
            "views": [100, 500, 300],
            "likes": [10, 50, 30],
            "comments": [1, 5, 3],
            "engagement_rate": [11.0, 11.0, 11.0]
        }
        df = pd.DataFrame(data)
        top = get_top_videos(df, metric="views", n=2)

        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]["title"], "Video B")
        self.assertEqual(top[1]["title"], "Video C")

    def test_plain_english_insights_generation(self):
        data = {
            "title": ["Intro to Python", "Advanced ML Guide"],
            "views": [10000, 50000],
            "likes": [500, 3000],
            "comments": [50, 300],
            "engagement_rate": [5.5, 6.6],
            "publish_day": ["Monday", "Friday"]
        }
        df = pd.DataFrame(data)
        insights = generate_plain_english_insights(df, {"title": "Test Channel"})

        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        self.assertTrue(any("Advanced ML Guide" in msg for msg in insights))

    def test_channel_score_calculation(self):
        data = {
            "views": [50000, 100000, 200000],
            "likes": [2500, 5000, 10000],
            "comments": [250, 500, 1000],
            "engagement_rate": [5.5, 5.5, 5.5],
            "publish_month": ["Jan", "Feb", "Mar"]
        }
        df = pd.DataFrame(data)
        res = calculate_channel_score(df)
        self.assertIn("overall_score", res)
        self.assertGreaterEqual(res["overall_score"], 0.0)
        self.assertLessEqual(res["overall_score"], 100.0)
        self.assertIn("tier", res)

    def test_video_comparison(self):
        v1 = {"title": "Vid A", "views": 100000, "likes": 5000, "engagement_rate": 5.0, "views_per_day": 1000}
        v2 = {"title": "Vid B", "views": 50000, "likes": 4000, "engagement_rate": 8.0, "views_per_day": 2000}
        cmp_res = compare_two_videos(v1, v2)
        self.assertEqual(cmp_res["views_winner"], "Video 1")
        self.assertEqual(cmp_res["engagement_winner"], "Video 2")
        self.assertEqual(cmp_res["views_per_day_winner"], "Video 2")

    def test_smart_recommendations(self):
        data = {
            "title": ["Intro to Python", "Advanced ML Guide"],
            "title_length": [15, 17],
            "views": [10000, 50000],
            "likes": [500, 3000],
            "comments": [50, 300],
            "engagement_rate": [5.5, 6.6],
            "publish_hour": [18, 18]
        }
        df = pd.DataFrame(data)
        recs = generate_smart_recommendations(df, {"title": "Test Channel"})
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)


if __name__ == "__main__":
    unittest.main()
