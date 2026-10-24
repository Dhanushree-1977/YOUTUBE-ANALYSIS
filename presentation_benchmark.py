"""
presentation_benchmark.py
==========================
Reconstructs and analyzes the exact 10-video cross-category benchmark dataset
from 'YouTube_Analysis_Project_Presentation.pptx' (Slides 4, 6, 7, 8, 9).

Covers 7 categories:
Music, Entertainment, Education, Sports, Food, Technology, Travel.

Generates the 4 presentation charts:
1. Top 5 Most Viewed Videos
2. Average Views by Category
3. Views vs. Likes Scatter Plot
4. Views Trend Over Time (by Month)
"""

import os
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11
})

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")


def create_presentation_benchmark_data():
    """
    Exact 10-video dataset derived from the PPTX charts and metrics.
    """
    records = [
        {
            "video_id": "PPT_01",
            "title": "Top 10 Songs",
            "category": "Music",
            "views": 5000000,
            "likes": 250000,
            "comments": 22000,
            "publish_month": 1,
            "publish_date": "2024-01-15"
        },
        {
            "video_id": "PPT_02",
            "title": "Funny Cats",
            "category": "Entertainment",
            "views": 3200000,
            "likes": 180000,
            "comments": 14500,
            "publish_month": 2,
            "publish_date": "2024-02-10"
        },
        {
            "video_id": "PPT_03",
            "title": "Cooking Recipe",
            "category": "Food",
            "views": 1500000,
            "likes": 75000,
            "comments": 6800,
            "publish_month": 3,
            "publish_date": "2024-03-22"
        },
        {
            "video_id": "PPT_04",
            "title": "Tech Gadgets Review",
            "category": "Technology",
            "views": 2100000,
            "likes": 110000,
            "comments": 9200,
            "publish_month": 4,
            "publish_date": "2024-04-05"
        },
        {
            "video_id": "PPT_05",
            "title": "Football Highlights",
            "category": "Sports",
            "views": 4500000,
            "likes": 210000,
            "comments": 19000,
            "publish_month": 5,
            "publish_date": "2024-05-18"
        },
        {
            "video_id": "PPT_06",
            "title": "Python Tutorial",
            "category": "Education",
            "views": 1200000,
            "likes": 60000,
            "comments": 5400,
            "publish_month": 6,
            "publish_date": "2024-06-12"
        },
        {
            "video_id": "PPT_07",
            "title": "Movie Trailer",
            "category": "Entertainment",
            "views": 3800000,
            "likes": 190000,
            "comments": 17200,
            "publish_month": 7,
            "publish_date": "2024-07-28"
        },
        {
            "video_id": "PPT_08",
            "title": "Study Tips & Focus",
            "category": "Education",
            "views": 900000,
            "likes": 40000,
            "comments": 3800,
            "publish_month": 8,
            "publish_date": "2024-08-14"
        },
        {
            "video_id": "PPT_09",
            "title": "World Tour Vlog",
            "category": "Travel",
            "views": 1600000,
            "likes": 70000,
            "comments": 8100,
            "publish_month": 9,
            "publish_date": "2024-09-03"
        },
        {
            "video_id": "PPT_10",
            "title": "Dance Performance",
            "category": "Music",
            "views": 2700000,
            "likes": 130000,
            "comments": 11500,
            "publish_month": 10,
            "publish_date": "2024-10-20"
        }
    ]

    df = pd.DataFrame(records)
    df["like_ratio"] = (df["likes"] / df["views"]) * 100
    df["comment_ratio"] = (df["comments"] / df["views"]) * 100

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUTPUT_DIR, "presentation_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"[+] Presentation benchmark dataset saved to: {csv_path}")
    return df


def generate_presentation_charts(df):
    """Generate all 4 charts matching the PowerPoint slides."""
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # 1. Slide 6: Top 5 Most Viewed Videos
    top5 = df.sort_values(by="views", ascending=False).head(5)
    plt.figure(figsize=(9, 5))
    bars = plt.bar(top5["title"], top5["views"] / 1e6, color="#1f77b4", width=0.55)
    plt.title("Top 5 Most Viewed Videos", fontsize=14, pad=12)
    plt.xlabel("Video Title", labelpad=10)
    plt.ylabel("Views (Millions)", labelpad=10)
    plt.xticks(rotation=90)
    plt.ylim(0, 5.5)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    chart1_path = os.path.join(CHARTS_DIR, "slide6_top5_most_viewed.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"[+] Saved Slide 6 chart: {chart1_path}")

    # 2. Slide 7: Average Views by Category
    cat_order = ["Education", "Entertainment", "Food", "Music", "Sports", "Technology", "Travel"]
    cat_avg = df.groupby("category")["views"].mean().reindex(cat_order) / 1e6
    plt.figure(figsize=(9, 5))
    plt.bar(cat_avg.index, cat_avg.values, color="#1f77b4", width=0.55)
    plt.title("Average Views by Category", fontsize=14, pad=12)
    plt.xlabel("Category", labelpad=10)
    plt.ylabel("Views (Millions)", labelpad=10)
    plt.xticks(rotation=90)
    plt.ylim(0, 5.0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    chart2_path = os.path.join(CHARTS_DIR, "slide7_avg_views_by_category.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"[+] Saved Slide 7 chart: {chart2_path}")

    # 3. Slide 8: Views vs Likes Scatter Plot
    plt.figure(figsize=(9, 5))
    plt.scatter(df["views"], df["likes"], color="#6366f1", marker="x", s=65, linewidths=2)
    plt.title("Views vs Likes", fontsize=14, pad=12)
    plt.xlabel("Views", labelpad=10)
    plt.ylabel("Likes", labelpad=10)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart3_path = os.path.join(CHARTS_DIR, "slide8_views_vs_likes.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"[+] Saved Slide 8 chart: {chart3_path}")

    # 4. Slide 9: Views Trend Over Time (by Month)
    monthly_trend = df.sort_values(by="publish_month")
    plt.figure(figsize=(9, 5))
    plt.plot(monthly_trend["publish_month"], monthly_trend["views"] / 1e6, marker="o", color="#1f77b4", linewidth=2)
    plt.title("Views Trend Over Time (by Month)", fontsize=14, pad=12)
    plt.xlabel("Month", labelpad=10)
    plt.ylabel("Total Views (Millions)", labelpad=10)
    plt.xticks(range(1, 11))
    plt.ylim(0.7, 5.3)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    chart4_path = os.path.join(CHARTS_DIR, "slide9_views_trend_over_time.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"[+] Saved Slide 9 chart: {chart4_path}")


def main():
    print("=" * 70)
    print("      REPRODUCING PPTX BENCHMARK DATASET & VISUALIZATIONS")
    print("=" * 70)
    df = create_presentation_benchmark_data()
    generate_presentation_charts(df)
    print("\nSummary of Presentation Benchmark:")
    print(f"  Total Benchmark Videos: {len(df)}")
    print(f"  Top Video: {df.sort_values(by='views', ascending=False).iloc[0]['title']} ({df['views'].max():,} views)")
    print(f"  Top Category by Avg Views: {df.groupby('category')['views'].mean().idxmax()} ({int(df.groupby('category')['views'].mean().max()):,} avg views)")
    print("=" * 70)


if __name__ == "__main__":
    main()
