import os
import time
import json
import requests

KAGGLE_USERNAME = os.environ.get('KAGGLE_USERNAME', 'yijiey')
KAGGLE_KEY = os.environ.get('KAGGLE_KEY', '')
PROFILE_URL = f'https://www.kaggle.com/api/i/users.ProfileService/GetProfile?userName={KAGGLE_USERNAME}'
COMPETITIONS_URL = 'https://www.kaggle.com/api/v1/competitions/list'
BASE_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(BASE_OUTPUT_DIR, "kaggle.json")


def _fetch_active_competitions():
    """Fetch active competitions user has entered (requires API key)."""
    if not KAGGLE_KEY:
        return []
    auth = (KAGGLE_USERNAME, KAGGLE_KEY)
    entered = []
    for page in range(1, 20):
        resp = requests.get(f'{COMPETITIONS_URL}?page={page}&sortBy=latestDeadline',
                            auth=auth, timeout=15)
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        for c in data:
            if isinstance(c, dict) and c.get('userHasEntered'):
                entered.append({
                    "title": c.get("title", ""),
                    "url": c.get("ref", ""),
                    "rank": c.get("userRank", 0),
                    "teams": c.get("teamCount", 0),
                    "deadline": c.get("deadline", "")[:10],
                    "category": c.get("category", ""),
                    "reward": c.get("reward", ""),
                })
    return entered


def run():
    print("   [Kaggle] Fetching Kaggle profile data...")
    try:
        resp = requests.get(PROFILE_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        resp.raise_for_status()
        raw = resp.json()

        # Extract summaries by type
        summaries = {}
        for s in raw.get('achievementSummaries', []):
            key = s.get('summaryType', '').replace('USER_ACHIEVEMENT_TYPE_', '').lower()
            summaries[key] = s

        comp = summaries.get('competitions', {})
        datasets = summaries.get('datasets', {})
        notebooks = summaries.get('notebooks', {})

        data = {
            "username": raw.get("userName", ""),
            "display_name": raw.get("displayName", ""),
            "join_date": raw.get("userJoinDate", ""),
            "last_active": raw.get("userLastActive", ""),
            "avatar_url": raw.get("userAvatarUrl", ""),
            "bio": raw.get("bio", ""),
            "occupation": raw.get("occupation", ""),
            "organization": raw.get("organization", ""),
            "country": raw.get("country", ""),
            "overall_tier": raw.get("performanceTier", ""),
            "competitions": {
                "tier": comp.get("tier", ""),
                "rank_current": comp.get("rankCurrent", 0),
                "rank_highest": comp.get("rankHighest", 0),
                "rank_out_of": comp.get("rankOutOf", 0),
                "rank_percentage": round(comp.get("rankPercentage", 0) * 100, 2),
                "gold_medals": comp.get("totalGoldMedals", 0),
                "silver_medals": comp.get("totalSilverMedals", 0),
                "bronze_medals": comp.get("totalBronzeMedals", 0),
                "total_entered": raw.get("totalCompetitions", 0),
            },
            "datasets": {
                "tier": datasets.get("tier", ""),
                "rank_out_of": datasets.get("rankOutOf", 0),
            },
            "notebooks": {
                "tier": notebooks.get("tier", ""),
                "rank_out_of": notebooks.get("rankOutOf", 0),
            },
            "total_discussions": raw.get("totalDiscussions", 0),
            "followers": raw.get("totalUsersFollowingMe", 0),
            "following": raw.get("totalUsersIFollow", 0),
            "badges": [b["badge"]["name"] for b in raw.get("badges", [])],
            "active_competitions": _fetch_active_competitions(),
            "last_updated": time.strftime('%Y-%m-%d %H:%M:%S')
        }

        from utils import archive_and_save, download_avatar
        changed = archive_and_save(OUTPUT_FILE, data)

        # Download the profile avatar locally (archives previous on change)
        avatar_dest = os.path.join(BASE_OUTPUT_DIR, "kaggle-avatar.png")
        if download_avatar(data["avatar_url"], avatar_dest):
            print(f"   [Avatar] Updated {avatar_dest}")

        c = data['competitions']
        status = "updated" if changed else "unchanged"
        print(f"   [Kaggle] Success ({status}). Rank {c['rank_current']}/{c['rank_out_of']}, "
              f"{c['gold_medals']}G/{c['silver_medals']}S/{c['bronze_medals']}B, "
              f"{len(data['active_competitions'])} active")

    except Exception as e:
        print(f"   [Kaggle] Error: {e}")


if __name__ == "__main__":
    run()
