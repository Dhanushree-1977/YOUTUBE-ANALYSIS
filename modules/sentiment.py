"""
sentiment.py - Comment Sentiment Classification & Explorer
===========================================================
Provides sentiment scoring, distribution metrics, and an interactive comment
explorer dataset with graceful handling of disabled/restricted comments.
"""

import re
from typing import Dict, Any, List

# Lexicons for lightweight rule-based scoring (calibrated for YouTube comments)
POSITIVE_WORDS = {
    "great", "amazing", "awesome", "helpful", "love", "loved", "best", "excellent",
    "clear", "brilliant", "fantastic", "thanks", "thank", "informative", "perfect",
    "good", "super", "easy", "invaluable", "gem", "masterpiece", "recommend", "liked"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "confusing", "worst", "hate", "boring", "useless", "wrong",
    "dislike", "poor", "waste", "horrible", "difficult", "disappointed", "annoying",
    "broken", "misleading", "audio", "trash", "stupid", "slow", "error", "failed"
}


def classify_comment_text(text: str) -> Dict[str, Any]:
    """
    Classifies comment text into Positive, Neutral, or Negative.
    Returns sentiment label and normalized polarity score between -1.0 and 1.0.
    """
    if not text or not isinstance(text, str):
        return {"sentiment": "Neutral", "score": 0.0}

    clean_text = re.sub(r"[^\w\s]", " ", text.lower())
    words = clean_text.split()
    if not words:
        return {"sentiment": "Neutral", "score": 0.0}

    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

    total_matched = pos_count + neg_count
    if total_matched == 0:
        return {"sentiment": "Neutral", "score": 0.0}

    score = (pos_count - neg_count) / max(1, total_matched)

    if score > 0.15:
        sentiment = "Positive"
    elif score < -0.15:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {"sentiment": sentiment, "score": round(score, 2)}


def get_sample_comment_dataset() -> List[Dict[str, Any]]:
    """
    Returns an annotated sample dataset of typical YouTube viewer comments
    across technical tutorials and trending videos for the Comment Explorer.
    """
    comments_raw = [
        ("Alex M.", "This tutorial was extremely helpful! Finally understood how the uploads playlist pagination works.", 342),
        ("DevCoder", "The explanation at 12:40 was confusing, had to rewind 3 times.", 45),
        ("Sarah Jenkins", "The video is about 10 minutes long and covers basic concepts.", 12),
        ("TechEnthusiast99", "Awesome presentation! Clear audio, concise slides, and practical code examples.", 189),
        ("PythonGeek", "Best breakdown of Random Forest regression vs median baseline on YouTube.", 94),
        ("Viewer_404", "Terrible microphone quality during the first two minutes, but the coding part was okay.", 28),
        ("Elena Rostova", "Loved the dark navy theme and the clean data quality report table!", 77),
        ("DataDan", "Can you explain how engagement rate is calculated when a video has zero comments?", 19),
        ("Mark B.", "Waste of time honestly, you skipped all the difficult parts.", 11),
        ("Sophie Chen", "Thank you so much! This helped me pass my data science assignment.", 215),
        ("CodeWizard", "Standard tutorial, nothing special but works fine.", 8),
        ("Liam O'Connor", "Brilliant insights into publishing time patterns and why correlation doesn't mean causation.", 152),
        ("GamingFanatic", "Audio is completely broken in the second half.", 31),
        ("Maria Garcia", "Fantastic dashboard layout. Everything is so easy to navigate.", 64),
        ("CuriousMind", "Where can we download the cleaned CSV dataset?", 15)
    ]

    records = []
    for author, text, likes in comments_raw:
        res = classify_comment_text(text)
        records.append({
            "author": author,
            "text": text,
            "likes": likes,
            "sentiment": res["sentiment"],
            "score": res["score"]
        })
    return records


def analyze_comment_sentiments(comments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Aggregates sentiment distribution, counts, and percentages.
    Gracefully handles disabled comments or empty lists.
    """
    if comments is None:
        comments = get_sample_comment_dataset()

    total = len(comments)
    if total == 0:
        return {
            "status": "disabled_or_empty",
            "message": "Comments are disabled or unavailable for this channel/video.",
            "total_comments": 0,
            "positive_count": 0,
            "neutral_count": 0,
            "negative_count": 0,
            "positive_pct": 0.0,
            "neutral_pct": 0.0,
            "negative_pct": 0.0,
            "sample_comments": []
        }

    pos_count = sum(1 for c in comments if c["sentiment"] == "Positive")
    neu_count = sum(1 for c in comments if c["sentiment"] == "Neutral")
    neg_count = sum(1 for c in comments if c["sentiment"] == "Negative")

    return {
        "status": "success",
        "total_comments": total,
        "positive_count": pos_count,
        "neutral_count": neu_count,
        "negative_count": neg_count,
        "positive_pct": round((pos_count / total) * 100, 1),
        "neutral_pct": round((neu_count / total) * 100, 1),
        "negative_pct": round((neg_count / total) * 100, 1),
        "sample_comments": comments
    }
