"""
data_cleaning.py - Data Cleaning & Feature Engineering Module
============================================================
Handles rigorous data validation, timestamp standardization, metric derivation,
and schema consistency across YouTube video datasets.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone


def calculate_engagement_rate(likes, comments, views):
    """
    Computes engagement rate as: ((likes + comments) / views) * 100
    Guarantees zero-division safety and non-negative outputs.
    """
    likes = np.asarray(likes, dtype=float)
    comments = np.asarray(comments, dtype=float)
    views = np.asarray(views, dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        rate = np.where(views > 0, ((likes + comments) / views) * 100.0, 0.0)
    rate = np.nan_to_num(rate, nan=0.0, posinf=0.0, neginf=0.0)
    return np.round(np.maximum(rate, 0.0), 3)


def clean_channel_data(df: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
    """
    Cleans raw channel video metadata:
    - Coerces numerical statistics (views, likes, comments, tag_count)
    - Replaces missing titles with 'Untitled'
    - Parses UTC published_at timestamps
    - Derives calendar features (year, month, day of week, hour)
    - Computes engagement rate, like ratio, comment ratio, and video age
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # Clean textual fields
    if "title" in df.columns:
        df["title"] = df["title"].fillna("Untitled").astype(str).str.strip()
        df.loc[df["title"] == "", "title"] = "Untitled"
    else:
        df["title"] = "Untitled"

    # Numerical coercion (negative values coerced to 0)
    for col in ["views", "likes", "comments", "tag_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            df[col] = df[col].apply(lambda x: int(max(0, x)))
        else:
            df[col] = 0

    # Timestamp parsing
    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    else:
        df["published_at"] = pd.Timestamp.now(tz=timezone.utc)

    # Fallback for unparseable dates
    now_utc = pd.Timestamp.now(tz=timezone.utc)
    df["published_at"] = df["published_at"].fillna(now_utc)

    # Derived temporal components
    df["publish_year"] = df["published_at"].dt.year
    df["publish_month"] = df["published_at"].dt.strftime("%b")
    df["publish_day"] = df["published_at"].dt.day_name()
    df["publish_hour"] = df["published_at"].dt.hour

    # Derived metrics
    df["engagement_rate"] = calculate_engagement_rate(df["likes"], df["comments"], df["views"])
    
    with np.errstate(divide="ignore", invalid="ignore"):
        df["like_ratio"] = np.where(df["views"] > 0, (df["likes"] / df["views"]) * 100.0, 0.0)
        df["comment_ratio"] = np.where(df["views"] > 0, (df["comments"] / df["views"]) * 100.0, 0.0)
    df["like_ratio"] = np.round(np.nan_to_num(df["like_ratio"], nan=0.0), 3)
    df["comment_ratio"] = np.round(np.nan_to_num(df["comment_ratio"], nan=0.0), 3)

    # Video age in days (relative to current observation time)
    age_delta = (now_utc - df["published_at"]).dt.total_seconds() / 86400.0
    df["video_age_days"] = np.maximum(0, age_delta).round(1)

    # Views per day (Video Age Fairness metric)
    with np.errstate(divide="ignore", invalid="ignore"):
        df["views_per_day"] = np.where(df["video_age_days"] > 0, df["views"] / df["video_age_days"], df["views"].astype(float))
    df["views_per_day"] = np.round(np.nan_to_num(df["views_per_day"], nan=0.0), 1)

    # Tag and title length features for ML
    df["title_length"] = df["title"].str.len()
    df["title_word_count"] = df["title"].str.split().str.len()

    if "description_length" not in df.columns:
        df["description_length"] = 450

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")

    return df


def clean_trending_data(df: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
    """Cleans today's trending video dataset with viral velocity metrics."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    if "title" in df.columns:
        df["title"] = df["title"].fillna("Untitled").astype(str).str.strip()

    for col in ["views", "likes", "comments", "hours_since_published", "views_per_hour"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            df[col] = df[col].apply(lambda x: max(0, x))

    df["engagement_rate"] = calculate_engagement_rate(df.get("likes", 0), df.get("comments", 0), df.get("views", 0))

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")

    return df
