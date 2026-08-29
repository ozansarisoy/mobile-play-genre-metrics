"""
Apple App Store Live Chart Fetcher — MPGM
============================================
Adds a SECOND, independent live signal alongside the Google Play watchlist
(live_fetch.py): Apple's real, ranked Top Free Games chart, per genre.

Why this matters more than the Google Play watchlist: the Google Play side
tracks a small, hand-picked list of representative apps because Google Play
has no free official charts API. Apple, by contrast, publishes an official,
free, keyless RSS/JSON feed of its ACTUAL top-charts — real rank, not a
proxy. This gives a much stronger "which genre is rising/falling" signal:
instead of watching a handful of apps' rating drift, we get the real market
rank of the top games in each genre, every day.

Endpoint used (Apple's classic RSS generator, JSON output):
    https://itunes.apple.com/{country}/rss/topfreeapplications/limit={limit}/genre={genre_id}/json

This endpoint requires no API key and has been publicly documented and used
by third parties for years. Its availability has occasionally been reported
as flaky in developer forums (Apple has also introduced a newer
rss.applemarketingtools.com/api/v2 endpoint for the ALL-apps chart, but that
newer endpoint does not support genre filtering, which is the whole point
here) — so every request is wrapped defensively: a failure for one genre is
logged and skipped, it never aborts the whole run, exactly like the
Google Play fetcher in live_fetch.py.

IMPORTANT — verify on first real run: this was implemented and syntax/logic
-tested without live network access to Apple's servers (the sandbox this was
built in cannot reach itunes.apple.com). It WILL be exercised for real the
first time your GitHub Actions workflow runs it. If Apple's endpoint has
changed shape, check the "HATA" lines in the Actions log — the script will
tell you plainly rather than fail silently.
"""

import csv
import os
import time
import urllib.request
import json
from datetime import datetime, timezone

SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "data", "apple_snapshots.csv")

# Apple's documented, stable affiliate/genre IDs for iOS Games sub-genres.
# Reference: Apple's iTunes affiliate genre taxonomy (unchanged for years).
# "Casual" has no dedicated Apple chart genre ID, so it's intentionally
# omitted here — that genre still gets live coverage from the Google Play
# side (live_fetch.py).
GENRE_IDS = {
    "Action": 7001,
    "Adventure": 7002,
    "Arcade": 7003,
    "Board": 7004,
    "Card": 7005,
    "Casino": 7006,
    "Music": 7011,
    "Puzzle": 7012,
    "Racing": 7013,
    "Role Playing": 7014,
    "Simulation": 7015,
    "Sports": 7016,
    "Strategy": 7017,
    "Trivia": 7018,
    "Word": 7019,
}

COUNTRY = "us"       # Apple storefront country code
CHART_LIMIT = 25      # top-N games fetched per genre
REQUEST_TIMEOUT = 15  # seconds
REQUEST_DELAY = 1.5   # seconds between requests, polite to Apple's servers


def _fetch_genre_chart(genre_name: str, genre_id: int, fetched_at: str) -> list:
    url = (
        f"https://itunes.apple.com/{COUNTRY}/rss/topfreeapplications/"
        f"limit={CHART_LIMIT}/genre={genre_id}/json"
    )
    rows = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MPGM/1.1 (+data-science-project)"})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        entries = data.get("feed", {}).get("entry", [])
        for rank, entry in enumerate(entries, start=1):
            try:
                app_name = entry.get("im:name", {}).get("label", "")
                artist = entry.get("im:artist", {}).get("label", "")
                app_id = entry.get("id", {}).get("attributes", {}).get("im:id", "")
                rows.append({
                    "fetched_at": fetched_at,
                    "genre": genre_name,
                    "country": COUNTRY,
                    "rank": rank,
                    "app_name": app_name,
                    "developer": artist,
                    "apple_app_id": app_id,
                })
            except Exception as e:
                print(f"HATA: {genre_name} rank {rank} parse edilemedi: {e}")
    except Exception as e:
        print(f"HATA: {genre_name} (genre_id={genre_id}) Apple chart çekilemedi: {e}")
    return rows


def fetch_apple_snapshot() -> list:
    fetched_at = datetime.now(timezone.utc).isoformat()
    all_rows = []
    for genre_name, genre_id in GENRE_IDS.items():
        rows = _fetch_genre_chart(genre_name, genre_id, fetched_at)
        all_rows.extend(rows)
        time.sleep(REQUEST_DELAY)
    return all_rows


def append_to_csv(rows: list):
    file_exists = os.path.exists(SNAPSHOT_PATH)
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    fieldnames = ["fetched_at", "genre", "country", "rank", "app_name", "developer", "apple_app_id"]
    with open(SNAPSHOT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = fetch_apple_snapshot()
    print(f"{len(data)} satır çekildi (Apple App Store, {len(GENRE_IDS)} tür).")
    if len(data) == 0:
        print("UYARI: hiç satır çekilemedi — Apple endpoint'i şu an erişilemez olabilir. "
              "Bir sonraki günlük çalıştırmada tekrar denenecek.")
    append_to_csv(data)
    print(f"apple_snapshots.csv güncellendi -> {SNAPSHOT_PATH}")
