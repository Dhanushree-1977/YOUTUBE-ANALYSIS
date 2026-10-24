"""
validation.py - Data Quality & Dataset Validation Module
========================================================
Inspects datasets before and after processing to generate a rigorous Data Quality Report:
- Total rows and columns
- Duplicate rows vs duplicate video IDs
- Missing values by column
- Invalid or negative numerical entries
- Unique video IDs and categories
- Date ranges and data collection metadata
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any


def generate_data_quality_report(
    df: pd.DataFrame,
    raw_df: pd.DataFrame = None,
    data_source: str = "Demo Dataset",
    collected_at: str = None
) -> Dict[str, Any]:
    """
    Evaluates dataset integrity and compiles a comprehensive Data Quality Report.
    """
    if df is None or df.empty:
        return {
            "status": "empty",
            "message": "Dataset is empty. No data quality metrics available.",
            "data_source": data_source,
            "collected_at": collected_at or datetime.now().strftime("%d %B %Y, %I:%M %p")
        }

    total_rows = len(df)
    total_cols = len(df.columns)

    # 1. Duplicate checks
    # Exact duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    # Duplicate video IDs (if video_id present)
    duplicate_ids = 0
    unique_ids = total_rows
    if "video_id" in df.columns:
        unique_ids = int(df["video_id"].nunique())
        duplicate_ids = int(total_rows - unique_ids)

    # 2. Missing values by column
    missing_by_col = {}
    key_columns = ["video_id", "title", "published_at", "views", "likes", "comments", "category_name"]
    for col in key_columns:
        if col in df.columns:
            missing_by_col[col] = int(df[col].isna().sum())
        else:
            missing_by_col[col] = total_rows  # Column missing entirely

    total_missing_cells = int(df.isna().sum().sum())

    # 3. Invalid numerical values (e.g., negative counts or non-numeric)
    invalid_numerical_counts = 0
    for col in ["views", "likes", "comments"]:
        if col in df.columns:
            # Check for negative numbers
            negatives = (pd.to_numeric(df[col], errors="coerce") < 0).sum()
            invalid_numerical_counts += int(negatives)

    # 4. Date ranges
    date_min = "N/A"
    date_max = "N/A"
    if "published_at" in df.columns:
        dt_series = pd.to_datetime(df["published_at"], errors="coerce")
        valid_dts = dt_series.dropna()
        if not valid_dts.empty:
            date_min = valid_dts.min().strftime("%Y-%m-%d")
            date_max = valid_dts.max().strftime("%Y-%m-%d")

    # 5. Categories available
    categories = []
    if "category_name" in df.columns:
        categories = sorted(df["category_name"].dropna().unique().tolist())
    elif "category" in df.columns:
        categories = sorted(df["category"].dropna().unique().tolist())

    # 6. Overall Quality Score (0 to 100%)
    # Deductions for duplicates, missing required values, and invalid numbers
    total_checks = total_rows * 4
    issues = duplicate_rows + missing_by_col.get("title", 0) + missing_by_col.get("views", 0) + invalid_numerical_counts
    quality_score = max(0.0, round((1.0 - (issues / max(1, total_checks))) * 100.0, 1))

    formatted_time = collected_at or datetime.now().strftime("%d %B %Y, %I:%M %p")

    return {
        "status": "success",
        "data_source": data_source,
        "collected_at": formatted_time,
        "total_records": total_rows,
        "total_columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "duplicate_video_ids": duplicate_ids,
        "unique_video_ids": unique_ids,
        "missing_titles": missing_by_col.get("title", 0),
        "missing_views": missing_by_col.get("views", 0),
        "missing_likes": missing_by_col.get("likes", 0),
        "missing_comments": missing_by_col.get("comments", 0),
        "total_missing_cells": total_missing_cells,
        "invalid_numerical_values": invalid_numerical_counts,
        "date_range": {
            "start": date_min,
            "end": date_max
        },
        "available_categories": categories,
        "category_count": len(categories),
        "quality_score": quality_score
    }
