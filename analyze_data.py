"""
analyze_data.py - YouTube Video, Channel & Today's Trending Analysis
=====================================================================
Performs comprehensive data cleaning, statistical evaluation, and visual analytics:
1. Channel-level metrics & 4 core charts (PDF brief)
2. Today's Trending Videos analytics & 4 viral trend charts
"""

import os
import sys
import json
import re
from collections import Counter
import pandas as pd
import numpy as np

# Use thread-safe headless Agg backend for Matplotlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.titlesize": 14
})

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")
RAW_CSV_PATH = os.path.join(OUTPUT_DIR, "youtube_videos_raw.csv")
CLEANED_CSV_PATH = os.path.join(OUTPUT_DIR, "youtube_videos_cleaned.csv")
TRENDING_CSV_PATH = os.path.join(OUTPUT_DIR, "today_trending_videos.csv")
CHANNEL_JSON_PATH = os.path.join(OUTPUT_DIR, "channel_info.json")


def load_channel_data():
    if not os.path.exists(RAW_CSV_PATH):
        print(f"[*] Raw data missing, fetching fresh data...")
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "fetch_data.py")], check=True)

    df = pd.read_csv(RAW_CSV_PATH)
    channel_info = {}
    if os.path.exists(CHANNEL_JSON_PATH):
        with open(CHANNEL_JSON_PATH, "r", encoding="utf-8") as f:
            channel_info = json.load(f)
    return df, channel_info


from modules.data_cleaning import clean_channel_data, clean_trending_data
from modules.metrics import calculate_kpis, generate_plain_english_insights
from modules.validation import generate_data_quality_report


def plot_channel_charts(df):
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # 1. Top 10 Most Viewed Videos
    top10 = df.sort_values(by="views", ascending=False).head(10).copy()
    top10["display_title"] = top10["title"].apply(lambda t: t[:45] + "..." if len(t) > 45 else t)

    plt.figure(figsize=(12, 6))
    bars = sns.barplot(data=top10, x="views", y="display_title", palette="crest", hue="display_title", legend=False)
    for bar in bars.patches:
        width = bar.get_width()
        plt.text(width * 1.01, bar.get_y() + bar.get_height() / 2, f"{int(width):,}", va="center", ha="left", fontsize=9)
    plt.title("Top 10 Most Viewed Videos", weight="bold", pad=15)
    plt.xlabel("Total View Count")
    plt.ylabel("Video Title")
    plt.xlim(0, top10["views"].max() * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "chart1_top_viewed_videos.png"), dpi=200)
    plt.close("all")

    # 2. Publishing-Time Performance Analysis (Day & Hour)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2))
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_stats = df.groupby("publish_day")["views"].mean().reindex(day_order).fillna(0)
    sns.barplot(x=day_stats.index, y=day_stats.values, ax=ax1, palette="viridis", hue=day_stats.index, legend=False)
    ax1.set_title("Average Views by Day of Upload\n(Observed historical pattern; not causal)", weight="bold", fontsize=11)
    ax1.set_xlabel("Day of Week")
    ax1.set_ylabel("Average Views")
    ax1.tick_params(axis="x", rotation=35)

    hour_stats = df.groupby("publish_hour")["views"].mean().reindex(range(24)).fillna(0)
    ax2.plot(hour_stats.index, hour_stats.values, marker="o", color="#e74c3c", linewidth=2.5)
    ax2.set_title("Average Views by Upload Hour (UTC)\n(Observed historical pattern; not causal)", weight="bold", fontsize=11)
    ax2.set_xlabel("Hour of Day (0-23)")
    ax2.set_ylabel("Average Views")
    ax2.set_xticks(range(0, 24, 2))
    ax2.grid(True, linestyle="--", alpha=0.6)
    plt.suptitle("Publishing-Time Performance Analysis", weight="bold", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "chart2_best_time_to_publish.png"), dpi=200)
    plt.close("all")

    # 3. Upload Consistency Trends
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    yearly = df["publish_year"].value_counts().sort_index().reset_index()
    yearly.columns = ["Year", "Count"]
    sns.barplot(data=yearly, x="Year", y="Count", ax=ax1, palette="mako", hue="Year", legend=False)
    ax1.set_title("Upload Frequency: Videos Published per Year", weight="bold")

    df["year_month"] = df["published_at"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("year_month").size()
    ax2.plot(monthly.index, monthly.values, marker=".", color="#2ecc71", linewidth=2)
    ax2.fill_between(monthly.index, monthly.values, color="#2ecc71", alpha=0.2)
    ax2.set_title("Monthly Upload Cadence Over Time", weight="bold")
    ax2.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "chart3_upload_consistency.png"), dpi=200)
    plt.close("all")

    # 4. Engagement Trends & Correlation
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    sns.regplot(data=df, x="views", y="likes", ax=ax1, scatter_kws={"alpha": 0.6, "color": "#3498db"}, line_kws={"color": "#e74c3c", "linewidth": 2})
    ax1.set_title("Correlation: Video Views vs. Likes", weight="bold")
    corr_cols = [c for c in ["views", "likes", "comments", "engagement_rate", "like_ratio", "tag_count"] if c in df.columns]
    corr = df[corr_cols].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True, ax=ax2)
    ax2.set_title("Metrics Correlation Matrix (Incl. Engagement Rate)", weight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "chart4_engagement_correlation.png"), dpi=200)
    plt.close("all")


def analyze_today_trends():
    print("\n" + "=" * 70)
    print("           TODAY'S YOUTUBE TRENDING VIDEOS ANALYSIS")
    print("=" * 70)

    if not os.path.exists(TRENDING_CSV_PATH):
        print("[!] Trending data missing, generating today's trending feed...")
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "fetch_data.py")], check=True)

    df_trend = pd.read_csv(TRENDING_CSV_PATH)
    print(f"[+] Loaded {len(df_trend)} Trending Videos for Today.")

    # 1. Category Distribution on Today's Trending Page
    cat_counts = df_trend["category_name"].value_counts()
    plt.figure(figsize=(10, 5))
    sns.barplot(x=cat_counts.values, y=cat_counts.index, palette="flare", hue=cat_counts.index, legend=False)
    plt.title("Today's Trending Feed: Share by Category", weight="bold", pad=12)
    plt.xlabel("Number of Trending Videos")
    plt.ylabel("Category")
    for idx, count in enumerate(cat_counts.values):
        plt.text(count + 0.1, idx, f"{count} ({count/len(df_trend)*100:.0f}%)", va="center", weight="bold", fontsize=9)
    plt.tight_layout()
    trend1_path = os.path.join(CHARTS_DIR, "trend_chart1_today_categories.png")
    plt.savefig(trend1_path, dpi=200)
    plt.close("all")
    print(f"[+] Saved Trending Chart 1: {trend1_path}")

    # 2. Viral Velocity: Views per Hour
    top_velocity = df_trend.sort_values(by="views_per_hour", ascending=False).head(10).copy()
    top_velocity["short_title"] = top_velocity["title"].apply(lambda t: t[:40] + "..." if len(t) > 40 else t)

    plt.figure(figsize=(11, 6))
    bars = sns.barplot(data=top_velocity, x="views_per_hour", y="short_title", palette="rocket", hue="short_title", legend=False)
    for bar in bars.patches:
        width = bar.get_width()
        plt.text(width * 1.01, bar.get_y() + bar.get_height() / 2, f"{int(width):,}/hr", va="center", fontsize=9)
    plt.title("Viral Velocity: Fastest Growing Videos Today (Views per Hour)", weight="bold", pad=12)
    plt.xlabel("Velocity (Views / Hour since Upload)")
    plt.ylabel("Video Title")
    plt.xlim(0, top_velocity["views_per_hour"].max() * 1.22)
    plt.tight_layout()
    trend2_path = os.path.join(CHARTS_DIR, "trend_chart2_viral_velocity.png")
    plt.savefig(trend2_path, dpi=200)
    plt.close("all")
    print(f"[+] Saved Trending Chart 2: {trend2_path}")

    # 3. Trending Engagement: Views vs Like Ratio
    plt.figure(figsize=(9, 5))
    sns.scatterplot(
        data=df_trend,
        x="views",
        y="like_ratio",
        hue="category_name",
        s=120,
        alpha=0.8,
        palette="tab10"
    )
    plt.title("Today's Trending: Total Views vs. Audience Like Ratio", weight="bold", pad=12)
    plt.xlabel("Total Views")
    plt.ylabel("Like Ratio (% of Views)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.tight_layout()
    trend3_path = os.path.join(CHARTS_DIR, "trend_chart3_trending_engagement.png")
    plt.savefig(trend3_path, dpi=200)
    plt.close("all")
    print(f"[+] Saved Trending Chart 3: {trend3_path}")

    # 4. Most Frequent Words in Today's Trending Titles
    stopwords = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "by", "from", "video", "official"}
    all_words = []
    for title in df_trend["title"]:
        words = re.findall(r"\b[A-Za-z]{3,}\b", title.lower())
        all_words.extend([w for w in words if w not in stopwords])

    word_counts = pd.Series(Counter(all_words)).sort_values(ascending=False).head(10)
    plt.figure(figsize=(9, 5))
    sns.barplot(x=word_counts.values, y=word_counts.index, palette="viridis", hue=word_counts.index, legend=False)
    plt.title("Top Viral Keywords in Today's Trending Titles", weight="bold", pad=12)
    plt.xlabel("Occurrences in Trending Titles")
    plt.ylabel("Keyword")
    plt.tight_layout()
    trend4_path = os.path.join(CHARTS_DIR, "trend_chart4_trending_tags.png")
    plt.savefig(trend4_path, dpi=200)
    plt.close("all")
    print(f"[+] Saved Trending Chart 4: {trend4_path}")

    return df_trend


def main():
    df, channel_info = load_channel_data()
    df_clean = clean_channel_data(df, output_path=CLEANED_CSV_PATH)
    plot_channel_charts(df_clean)
    analyze_today_trends()
    
    kpis = calculate_kpis(df_clean)
    print("\n" + "=" * 70)
    print(f"  CHANNEL PERFORMANCE METRICS (Dataset: {channel_info.get('title', 'Unknown')})")
    print(f"  Data Source: {channel_info.get('data_source', 'Demo Dataset')}")
    print(f"  Total Videos: {kpis['total_videos']} | Total Views: {kpis['total_views']:,}")
    print(f"  Average Engagement Rate: {kpis['avg_engagement_rate']:.2f}%")
    print("=" * 70)
    print("\n[+] Channel and Today's Trending analysis complete!")


if __name__ == "__main__":
    main()
