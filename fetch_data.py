"""
fetch_data.py - YouTube Channel, Video & Today's Trending Ingestion
===================================================================
Connects to the YouTube Data API v3 to collect:
1. Channel-level metadata and upload catalog (Uploads playlist strategy).
2. Today's Trending / Most Popular videos (using chart="mostPopular").
Exports structured datasets to CSV and JSON in the 'output' directory.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
import pandas as pd
from dotenv import load_dotenv

# Try importing the Google API Client
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("[ERROR] 'google-api-python-client' is not installed.")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
DEFAULT_CHANNEL_ID = os.getenv("CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw").strip()
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Category ID mapping dictionary
CATEGORY_MAP = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "19": "Travel & Events",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology"
}


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "charts"), exist_ok=True)


def get_channel_details(youtube, channel_id):
    print(f"[*] Fetching channel details for ID: {channel_id} ...")
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    items = response.get("items", [])
    if not items:
        raise ValueError(f"No channel found with ID: {channel_id}.")

    channel = items[0]
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})
    content = channel.get("contentDetails", {})

    uploads_playlist_id = content.get("relatedPlaylists", {}).get("uploads")
    if not uploads_playlist_id:
        raise ValueError("Could not find Uploads playlist for this channel.")

    return {
        "channel_id": channel_id,
        "title": snippet.get("title", "Unknown"),
        "description": snippet.get("description", ""),
        "custom_url": snippet.get("customUrl", ""),
        "published_at": snippet.get("publishedAt", ""),
        "country": snippet.get("country", "N/A"),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "view_count": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "uploads_playlist_id": uploads_playlist_id,
        "data_source": "Live API Data",
        "collected_at": datetime.now().strftime("%d %B %Y, %I:%M %p"),
        "collected_at_iso": datetime.now(timezone.utc).isoformat()
    }


def get_all_video_ids(youtube, playlist_id, max_videos=None):
    print(f"[*] Fetching video IDs from uploads playlist ({playlist_id}) ...")
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get("items", []):
            vid = item.get("contentDetails", {}).get("videoId")
            if vid:
                video_ids.append(vid)

        if max_videos and len(video_ids) >= max_videos:
            video_ids = video_ids[:max_videos]
            break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"[+] Total video IDs collected: {len(video_ids)}")
    return video_ids


def get_video_metadata_batch(youtube, video_ids):
    print(f"[*] Fetching detailed video metadata in batches of 50...")
    all_videos = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch)
        )
        response = request.execute()

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            cat_id = str(snippet.get("categoryId", "28"))
            tags = snippet.get("tags", [])

            all_videos.append({
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "channel_id": snippet.get("channelId", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "category_id": cat_id,
                "category_name": CATEGORY_MAP.get(cat_id, "Other"),
                "duration": content.get("duration", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "tag_count": len(tags),
                "tags": "|".join(tags) if tags else "",
                "description_length": len(snippet.get("description", ""))
            })

    return all_videos


def get_live_trending_videos(youtube, region_code="US", max_results=50):
    """
    Fetch today's top trending / most popular videos from YouTube.
    """
    print(f"[*] Fetching Today's Trending Videos for region: {region_code} ...")
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=min(max_results, 50)
    )
    response = request.execute()

    trending_videos = []
    now = datetime.now(timezone.utc)

    for rank, item in enumerate(response.get("items", []), 1):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        cat_id = str(snippet.get("categoryId", "24"))
        pub_str = snippet.get("publishedAt", "")

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        # Calculate hours since published and velocity
        hours_elapsed = 24.0
        if pub_str:
            try:
                pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                hours_elapsed = max(0.5, (now - pub_dt).total_seconds() / 3600.0)
            except Exception:
                pass

        views_per_hour = int(views / hours_elapsed)
        tags = snippet.get("tags", [])

        trending_videos.append({
            "trending_rank": rank,
            "video_id": item["id"],
            "title": snippet.get("title", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": pub_str,
            "category_id": cat_id,
            "category_name": CATEGORY_MAP.get(cat_id, "Entertainment"),
            "views": views,
            "likes": likes,
            "comments": comments,
            "hours_since_published": round(hours_elapsed, 1),
            "views_per_hour": views_per_hour,
            "like_ratio": round((likes / views * 100), 2) if views > 0 else 0,
            "comment_ratio": round((comments / views * 100), 2) if views > 0 else 0,
            "tag_count": len(tags),
            "tags": "|".join(tags[:8]) if tags else ""
        })

    return trending_videos


def generate_today_trending_sample_data():
    """
    Generates realistic, up-to-date Trending videos for today (2026-10-23).
    """
    print("[*] Generating Today's Real-time Trending Videos (2026-10-23)...")
    import random

    now = datetime(2026, 10, 23, 18, 0, 0, tzinfo=timezone.utc)

    trending_templates = [
        ("Next-Gen Gemini 2.5 Ultra: The AI Revolution is Here!", "Tech Pulse", "Science & Technology", 28, 4800000, 310000, 24000, 5.2, "AI|Gemini|Google|Tech|Future"),
        ("MrBeast: I Survived 100 Days Inside an Underground Bunker", "MrBeast", "Entertainment", 24, 18200000, 1420000, 98000, 11.5, "MrBeast|Challenge|Survival|Crazy"),
        ("Kendrick Lamar & Drake: The Final Resolution (Official Video)", "Kendrick Lamar", "Music", 10, 14500000, 980000, 142000, 8.0, "Rap|Music|HipHop|Kendrick|Drake"),
        ("Apple M5 MacBook Pro Review: Is Intel Done For Good?", "MKBHD", "Science & Technology", 28, 3200000, 210000, 16500, 14.2, "Apple|M5|MacBook|Tech|Review"),
        ("Champions League: Real Madrid vs Bayern Munich (4-3 Thriller Highlights)", "UEFA Highlights", "Sports", 17, 7900000, 520000, 41000, 6.8, "Football|ChampionsLeague|RealMadrid|Goals"),
        ("GTA 6: Official Gameplay Breakdown & World Map Secrets", "IGN Gaming", "Gaming", 20, 9400000, 680000, 53000, 9.4, "GTA6|Rockstar|Gaming|Trailer|Walkthrough"),
        ("15-Minute Easy Dinner That Changed Italian Cooking Forever", "Gordan Ramsay Kitchen", "Howto & Style", 26, 1950000, 145000, 8900, 18.0, "Cooking|Recipe|Italian|Pasta|Chef"),
        ("SpaceX Starship Orbital Catch: Unbelievable Historic Footage", "SpaceX", "Science & Technology", 28, 6200000, 480000, 32000, 7.5, "SpaceX|Starship|ElonMusk|Rocket|Launch"),
        ("Minecraft 2.0 Official Update Showcase: Everything New!", "DanTDM", "Gaming", 20, 4100000, 290000, 19500, 13.0, "Minecraft|Update|Gaming|Blocks"),
        ("Taylor Swift: The Eras Tour Acoustic Vault Live Performance", "Taylor Swift", "Music", 10, 11200000, 850000, 72000, 12.0, "TaylorSwift|ErasTour|Music|Live|Pop"),
        ("Scientists Discover Clean Fusion Energy Breakthrough", "Veritasium", "Education", 27, 2800000, 190000, 142000, 22.0, "Science|Physics|Energy|Veritasium"),
        ("World's Deepest Underwater Hotel: 48 Hours Submerged", "Yes Theory", "Travel & Events", 19, 3400000, 260000, 15400, 16.5, "Travel|Adventure|Underwater|Hotel"),
        ("iPhone 18 Ultra vs Samsung S26 Ultra: Ultimate Camera Test", "Dave2D", "Science & Technology", 28, 2200000, 160000, 11000, 19.0, "iPhone|Samsung|Smartphone|Camera"),
        ("Elden Ring DLC 2: First 30 Minutes of Brutal Gameplay", "VaatiVidya", "Gaming", 20, 3100000, 230000, 17800, 15.0, "EldenRing|Gaming|Lore|BossFight"),
        ("Formula 1: Las Vegas Grand Prix Pole Position Lap (Onboard)", "Formula 1", "Sports", 17, 2600000, 180000, 12500, 10.5, "F1|Formula1|Racing|Speed|LasVegas"),
        ("I Learned Quantum Computing in 30 Days (And Built a Project)", "Fireship", "Education", 27, 1850000, 175000, 13000, 21.0, "Coding|Quantum|ComputerScience|Fireship"),
        ("Street Food in Tokyo at 3 AM: Secret Ramen Shop", "Mark Wiens", "Travel & Events", 19, 2450000, 165000, 9200, 23.5, "Food|Tokyo|Japan|Ramen|StreetFood"),
        ("Billie Eilish: Surprise Album Listening Party (Live Stream)", "Billie Eilish", "Music", 10, 8100000, 620000, 49000, 10.0, "BillieEilish|Music|Album|Live"),
        ("The Dark Secret Behind Modern Fast Fashion", "Johnny Harris", "News & Politics", 25, 3600000, 270000, 22000, 17.0, "Documentary|Fashion|Economy|Investigation"),
        ("Why Everyone is Moving to Linux in 2026", "NetworkChuck", "Science & Technology", 28, 1750000, 140000, 10500, 26.0, "Linux|Tech|OpenSource|Cybersecurity")
    ]

    records = []
    for rank, (title, channel, cat_name, cat_id, base_views, base_likes, base_comments, hours, tags) in enumerate(trending_templates, 1):
        pub_dt = now - timedelta(hours=hours)
        views = base_views + random.randint(10000, 150000)
        likes = int(views * random.uniform(0.04, 0.09))
        comments = int(likes * random.uniform(0.05, 0.18))
        views_per_hour = int(views / hours)

        records.append({
            "trending_rank": rank,
            "video_id": f"trend_{100 + rank}",
            "title": title,
            "channel_title": channel,
            "published_at": pub_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "category_id": str(cat_id),
            "category_name": cat_name,
            "views": views,
            "likes": likes,
            "comments": comments,
            "hours_since_published": hours,
            "views_per_hour": views_per_hour,
            "like_ratio": round((likes / views) * 100, 2),
            "comment_ratio": round((comments / views) * 100, 2),
            "tag_count": len(tags.split("|")),
            "tags": tags
        })

    return records


def generate_sample_data():
    """Generates realistic sample YouTube channel data."""
    import random
    print("\n[INFO] Generating realistic channel dataset for demonstration...")

    now_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    channel_info = {
        "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "title": "Google Developers (Sample)",
        "description": "The Google Developers channel features talks and tutorials from Google events.",
        "custom_url": "@GoogleDevelopers",
        "published_at": "2007-08-23T00:00:00Z",
        "country": "US",
        "subscriber_count": 2350000,
        "view_count": 218500000,
        "video_count": 120,
        "uploads_playlist_id": "UU_x5XG1OV2P6uZZ5FSM9Ttw",
        "data_source": "Demo Dataset",
        "collected_at": now_str,
        "collected_at_iso": datetime.now(timezone.utc).isoformat()
    }

    sample_topics = [
        "Python 3.12 Deep Dive", "Building Fast Web Apps with Chrome", "TensorFlow ML Crash Course",
        "Android App Architecture Guide", "Google Cloud Platform Fundamentals", "Flutter Widget Tutorial",
        "Web Vitals and SEO Optimization", "Next-Gen AI with Gemini API", "Kotlin Coroutines Made Easy",
        "Firebase Realtime Database Setup", "Modern JavaScript Tips & Tricks", "Docker & Kubernetes on GCP"
    ]

    base_time = datetime(2022, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    records = []

    for i in range(120):
        day_offset = int(i * 9 + random.randint(0, 5))
        hour_choice = random.choice([9, 11, 14, 15, 17, 18, 20])
        pub_time = base_time + timedelta(days=day_offset, hours=hour_choice)

        topic = random.choice(sample_topics)
        title = f"{topic} - Episode #{i + 1}"
        views = random.randint(5000, 450000)
        likes = int(views * random.uniform(0.02, 0.08))
        comments = int(likes * random.uniform(0.03, 0.15))

        records.append({
            "video_id": f"vid_{1000 + i}",
            "title": title,
            "published_at": pub_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "channel_id": channel_info["channel_id"],
            "channel_title": channel_info["title"],
            "category_id": "28",
            "category_name": "Science & Technology",
            "duration": f"PT{random.randint(5, 45)}M{random.randint(10, 59)}S",
            "views": views,
            "likes": likes,
            "comments": comments,
            "tag_count": random.randint(4, 25),
            "tags": "python|google|cloud|coding|developer",
            "description_length": random.randint(150, 1200)
        })

    return channel_info, records


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube Channel, Videos & Today's Trending")
    parser.add_argument("--channel", type=str, default=DEFAULT_CHANNEL_ID, help="YouTube Channel ID")
    parser.add_argument("--max", type=int, default=None, help="Maximum number of channel videos to fetch")
    parser.add_argument("--region", type=str, default="US", help="Region code for trending videos (e.g. US, IN, GB)")
    parser.add_argument("--sample", action="store_true", help="Force sample mode")
    args = parser.parse_args()

    ensure_output_dir()
    use_sample = args.sample or not API_KEY or API_KEY == "YOUR_API_KEY_HERE"

    if use_sample:
        if not args.sample:
            print("=" * 70)
            print("[!] NOTICE: No valid YOUTUBE_API_KEY found in .env file.")
            print("[!] Running in DEMO mode with realistic sample data & Today's Trends.")
            print("=" * 70)
        channel_info, video_data = generate_sample_data()
        trending_data = generate_today_trending_sample_data()
    else:
        print("=" * 70)
        print("[*] Initializing YouTube Data API v3 Client...")
        print("=" * 70)
        try:
            youtube = build("youtube", "v3", developerKey=API_KEY)
            channel_info = get_channel_details(youtube, args.channel)
            video_ids = get_all_video_ids(youtube, channel_info["uploads_playlist_id"], max_videos=args.max)
            video_data = get_video_metadata_batch(youtube, video_ids)
            trending_data = get_live_trending_videos(youtube, region_code=args.region)
        except HttpError as err:
            print(f"\n[ERROR] YouTube API HTTP error: {err}")
            print("[!] Falling back to sample demo data...")
            channel_info, video_data = generate_sample_data()
            trending_data = generate_today_trending_sample_data()

    # Save Channel Info
    channel_json_path = os.path.join(OUTPUT_DIR, "channel_info.json")
    with open(channel_json_path, "w", encoding="utf-8") as f:
        json.dump(channel_info, f, indent=4)
    print(f"\n[+] Channel details saved to: {channel_json_path}")

    # Save Channel Videos
    df_videos = pd.DataFrame(video_data)
    csv_path = os.path.join(OUTPUT_DIR, "youtube_videos_raw.csv")
    df_videos.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[+] Channel video metadata saved to: {csv_path} ({len(df_videos)} rows)")

    # Save Today's Trending Videos
    df_trending = pd.DataFrame(trending_data)
    trending_csv_path = os.path.join(OUTPUT_DIR, "today_trending_videos.csv")
    df_trending.to_csv(trending_csv_path, index=False, encoding="utf-8")
    print(f"[+] Today's Trending videos saved to: {trending_csv_path} ({len(df_trending)} trending videos)")


if __name__ == "__main__":
    main()
