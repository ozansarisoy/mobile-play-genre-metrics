"""
Wikipedia Pageviews Fetcher — MPGM
=====================================
Third independent live signal (after Google Play watchlist and Apple App
Store real chart rank): daily page-view counts for each genre's Wikipedia
article, as a public-interest / "buzz" proxy.

Endpoint: Wikimedia's official, free, keyless REST API.
    https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/
        {wiki}/{access}/{agent}/{article}/{granularity}/{start}/{end}

No API key, no auth, no rate-limit tier to worry about for this volume of
requests (16 articles/day). Wikimedia's usage policy just asks for an
identifying User-Agent header, which is set below.

Why pageviews as a genre signal? A genre's Wikipedia article traffic is a
crude but real, free, and independent proxy for public interest — it moves
for different reasons than app-store rank (news coverage, a viral trend, a
Wikipedia link from a popular article) and is not affected by app-store
algorithm changes, making it a useful cross-check against the Google Play
and Apple signals rather than a duplicate of either.

Same defensive philosophy as live_fetch.py and live_fetch_apple.py: a
failure for one genre's article is logged and skipped, never aborts the run.

IMPORTANT — verify on first real run: built and logic-tested with a mocked
response; the sandbox this was built in cannot reach wikimedia.org. Check the
Actions log after the first run for "HATA:" lines.
"""

import csv
import os
import time
import json
import urllib.request
from datetime import datetime, timedelta, timezone

SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "data", "wiki_pageviews.csv")

# Genre -> representative English Wikipedia article title (spaces as underscores,
# matching Wikipedia's URL convention). Chosen as each genre's general/overview
# article rather than any single game, so the signal reflects interest in the
# genre itself, not one product's popularity.
GENRE_ARTICLES = {
    "Action": "Action_game",
    "Adventure": "Adventure_game",
    "Arcade": "Arcade_game",
    "Board": "Board_game",
    "Card": "Card_game",
    "Casino": "Casino_game",
    "Casual": "Casual_game",
    "Music": "Music_video_game",
    "Puzzle": "Puzzle_video_game",
    "Racing": "Racing_video_game",
    "Role Playing": "Role-playing_video_game",
    "Simulation": "Simulation_video_game",
    "Sports": "Sports_game",
    "Strategy": "Strategy_video_game",
    "Trivia": "Quiz",
    "Word": "Word_game",
}

WIKI = "en.wikipedia.org"
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0.5  # Wikimedia's rate limits are generous; still be polite
USER_AGENT = "MPGM/1.2 (data-science project; contact: see GitHub repo)"


def _target_date() -> str:
    """Pageview stats for 'today' aren't finalized yet; use 2 days ago for
    reliability (Wikimedia's own tooling recommends not relying on same-day
    or even yesterday's data being fully processed)."""
    d = datetime.now(timezone.utc) - timedelta(days=2)
    return d.strftime("%Y%m%d")


def _fetch_article_views(genre_name: str, article: str, date_str: str, fetched_at: str) -> dict | None:
    url = (
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
        f"{WIKI}/all-access/all-agents/{article}/daily/{date_str}/{date_str}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "accept": "application/json"})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = data.get("items", [])
        if not items:
            print(f"UYARI: {genre_name} ({article}) için {date_str} tarihinde veri yok.")
            return None
        views = sum(item.get("views", 0) for item in items)
        return {
            "fetched_at": fetched_at,
            "genre": genre_name,
            "article": article,
            "date": date_str,
            "views": views,
        }
    except Exception as e:
        print(f"HATA: {genre_name} ({article}) Wikipedia pageviews çekilemedi: {e}")
        return None


def fetch_wiki_snapshot() -> list:
    fetched_at = datetime.now(timezone.utc).isoformat()
    date_str = _target_date()
    rows = []
    for genre_name, article in GENRE_ARTICLES.items():
        row = _fetch_article_views(genre_name, article, date_str, fetched_at)
        if row is not None:
            rows.append(row)
        time.sleep(REQUEST_DELAY)
    return rows


def append_to_csv(rows: list):
    file_exists = os.path.exists(SNAPSHOT_PATH)
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    fieldnames = ["fetched_at", "genre", "article", "date", "views"]
    with open(SNAPSHOT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = fetch_wiki_snapshot()
    print(f"{len(data)} satır çekildi (Wikipedia pageviews, {len(GENRE_ARTICLES)} tür).")
    if len(data) == 0:
        print("UYARI: hiç satır çekilemedi — Wikimedia endpoint'i şu an erişilemez olabilir. "
              "Bir sonraki günlük çalıştırmada tekrar denenecek.")
    append_to_csv(data)
    print(f"wiki_pageviews.csv güncellendi -> {SNAPSHOT_PATH}")
