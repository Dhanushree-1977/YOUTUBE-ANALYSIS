"""
modules package for YouTube Analytics & Trends Platform
=======================================================
Modular architecture for data cleaning, metrics, data validation,
sentiment analysis, machine learning model evaluation, historical growth tracking,
and automated PDF analytics reporting.
"""

from .data_cleaning import clean_channel_data, clean_trending_data, calculate_engagement_rate
from .metrics import (
    calculate_kpis, get_top_videos, calculate_publishing_time_patterns,
    generate_plain_english_insights, calculate_channel_score, compare_two_videos,
    generate_smart_recommendations, detect_anomalies, analyze_title_patterns
)
from .validation import generate_data_quality_report
from .sentiment import analyze_comment_sentiments, get_sample_comment_dataset, classify_comment_text
from .ml_evaluation import train_and_evaluate_rf_model, prepare_features, FEATURE_COLUMNS
from .pdf_report import generate_pdf_report
from .historical_tracker import record_snapshot, load_all_snapshots, calculate_growth_velocity
