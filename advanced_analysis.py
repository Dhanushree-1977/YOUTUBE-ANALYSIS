"""
advanced_analysis.py - Machine Learning & Comment Sentiment Analysis
====================================================================
Implements the advanced analytics scope:
1. Machine Learning View Prediction (Random Forest vs Baseline Median Predictor):
   - Strictly pre-publication features to prevent data leakage
   - Evaluates MAE, RMSE, and R^2 score against a baseline predictor
   - Computes feature importances and exports model to 'output/rf_model.joblib'
2. Audience Comment Sentiment Analysis:
   - Sentiment classification (Positive, Neutral, Negative)
   - Comment explorer dataset exported to 'output/comments_sample.json'
   - Generates visual distribution charts in 'output/charts/'
"""

import os
import sys
import json
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from modules.ml_evaluation import train_and_evaluate_rf_model, prepare_features
from modules.sentiment import analyze_comment_sentiments, get_sample_comment_dataset

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")
CLEANED_CSV_PATH = os.path.join(OUTPUT_DIR, "youtube_videos_cleaned.csv")
MODEL_PATH = os.path.join(OUTPUT_DIR, "rf_model.joblib")
COMMENTS_PATH = os.path.join(OUTPUT_DIR, "comments_sample.json")


def load_dataset():
    if not os.path.exists(CLEANED_CSV_PATH):
        raw_csv = os.path.join(OUTPUT_DIR, "youtube_videos_raw.csv")
        if not os.path.exists(raw_csv):
            import subprocess
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "fetch_data.py")], check=True)
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "analyze_data.py")], check=True)

    return pd.read_csv(CLEANED_CSV_PATH)


def train_ml_predictor(df):
    print("\n" + "=" * 70)
    print("      MACHINE LEARNING: VIDEO PERFORMANCE PREDICTION & BASELINE BENCHMARK")
    print("=" * 70)

    eval_result = train_and_evaluate_rf_model(df, model_save_path=MODEL_PATH)
    metrics = eval_result.get("metrics", {})

    print(f"[+] Random Forest Model Evaluation:")
    print(f"    - MAE (Mean Absolute Error):     {metrics.get('rf_mae', 0):,} views")
    print(f"    - RMSE (Root Mean Squared Error): {metrics.get('rf_rmse', 0):,} views")
    print(f"    - R^2 Score (Log Views):         {metrics.get('rf_r2', 0):.3f}")
    print(f"    - Baseline Median MAE:           {metrics.get('baseline_mae', 0):,} views")
    print(f"    - Baseline Median RMSE:          {metrics.get('baseline_rmse', 0):,} views")
    print(f"    - MAE Improvement over Baseline: {metrics.get('mae_improvement_pct', 0.0):.1f}%")
    print(f"    - Data Leakage Guard:            {eval_result.get('leakage_check', 'PASS')}")
    print(f"[+] Exported trained ML model to: {MODEL_PATH}")

    # Feature Importance Plot
    importances = pd.Series(eval_result.get("feature_importances", {})).sort_values(ascending=True)

    plt.figure(figsize=(9, 5))
    importances.plot(kind="barh", color="#2563eb", edgecolor="none")
    plt.title("ML Feature Importance: Predicting Pre-Publication Views", weight="bold", pad=12)
    plt.xlabel("Relative Importance Score")
    plt.tight_layout()
    chart5_path = os.path.join(CHARTS_DIR, "chart5_ml_feature_importance.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f"[+] Saved Feature Importance chart: {chart5_path}")

    # Actual vs Predicted Plot
    X, y = prepare_features(df)
    import joblib
    model = joblib.load(MODEL_PATH)
    y_pred_log = model.predict(X)
    y_pred = np.expm1(y_pred_log)

    plt.figure(figsize=(7, 6))
    plt.scatter(y, y_pred, alpha=0.6, color="#059669", edgecolors="none")
    max_val = max(y.max(), y_pred.max())
    plt.plot([0, max_val], [0, max_val], "--", color="red", label="Ideal Fit (y=x)")
    plt.title("Actual vs. Predicted Video Views (Pre-Publication)", weight="bold")
    plt.xlabel("Actual Views")
    plt.ylabel("Predicted Views")
    plt.legend()
    plt.tight_layout()
    chart6_path = os.path.join(CHARTS_DIR, "chart6_actual_vs_predicted.png")
    plt.savefig(chart6_path, dpi=300)
    plt.close()
    print(f"[+] Saved Actual vs Predicted chart: {chart6_path}")

    return eval_result


def analyze_comment_sentiment():
    print("\n" + "=" * 70)
    print("      AUDIENCE COMMENT SENTIMENT ANALYSIS")
    print("=" * 70)

    comments_data = get_sample_comment_dataset()
    sentiment_result = analyze_comment_sentiments(comments_data)

    with open(COMMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(sentiment_result, f, indent=4)
    print(f"[+] Exported Comment Explorer dataset to: {COMMENTS_PATH}")

    # Sentiment Distribution Chart
    counts = pd.Series({
        "Positive": sentiment_result["positive_count"],
        "Neutral": sentiment_result["neutral_count"],
        "Negative": sentiment_result["negative_count"]
    })

    plt.figure(figsize=(8, 5))
    colors = {"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"}
    sns.barplot(x=counts.index, y=counts.values, palette=colors, hue=counts.index, legend=False)
    plt.title("Audience Comment Sentiment Distribution", weight="bold", pad=12)
    plt.xlabel("Sentiment Classification")
    plt.ylabel("Number of Comments")
    plt.ylim(0, max(1, counts.max()) * 1.25)

    total = sentiment_result["total_comments"]
    for idx, (sent, cnt) in enumerate(counts.items()):
        pct = (cnt / total) * 100 if total > 0 else 0
        plt.text(idx, cnt + 0.3, f"{cnt} ({pct:.1f}%)", ha="center", weight="bold")

    plt.tight_layout()
    chart7_path = os.path.join(CHARTS_DIR, "chart7_comment_sentiment_distribution.png")
    plt.savefig(chart7_path, dpi=300)
    plt.close()
    print(f"[+] Saved Comment Sentiment chart: {chart7_path}")

    return sentiment_result


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    df = load_dataset()
    train_ml_predictor(df)
    analyze_comment_sentiment()
    print("\n[+] Advanced analysis (ML + Sentiment) completed successfully!")


if __name__ == "__main__":
    main()
