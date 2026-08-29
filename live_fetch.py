"""
Canlı Veri Toplayıcı — Mobil Oyun Türleri
===========================================
Bu script GitHub Actions cron job'u ile GÜNLÜK olarak çalıştırılır (bkz.
.github/workflows/daily_snapshot.yml). Her çalıştırmada, önceden tanımlanmış
tür başına takip listesindeki (WATCHLIST) uygulamaların GÜNCEL Play Store
verisini (google_play_scraper ile) çeker ve data/snapshots.csv dosyasına
YENİ satırlar olarak EKLER (append). Zamanla biriken bu satırlar,
app.py'deki "Canlı İzleme" sekmesinde günlük/haftalık/aylık/yıllık trend
analizine dönüştürülür.

Neden sabit bir takip listesi (tüm GAME kategorisini taramak yerine)?
Play Store'da tür başına binlerce uygulama var; hepsini günlük taramak
hem çok yavaş hem de IP engellemesi riski taşır. Bunun yerine her tür
için en çok bilinen/temsilci ~8-12 uygulama seçilip zaman içindeki
değişimleri (puan, yorum sayısı, kurulum aralığı) izlenir — bu, borsa
endeksi mantığıyla aynıdır (tüm hisseleri değil, temsilci bir sepeti izle).
"""

import csv
import os
import time
from datetime import datetime, timezone

from google_play_scraper import app as gp_app

SNAPSHOT_PATH = os.path.join(os.path.dirname(__file__), "data", "snapshots.csv")

# Tür -> temsilci uygulama package id'leri (Google Play "app id")
WATCHLIST = {
    "Action": ["com.pubg.imobile", "com.miHoYo.GenshinImpact", "com.dts.freefireth",
               "com.activision.callofduty.shooter", "com.epicgames.fortnite"],
    "Arcade": ["com.king.candycrushsaga", "com.rovio.angrybirds", "air.com.hypah.io.slither",
               "com.halfbrick.fruitninjafree", "com.ketchapp.stack"],
    "Racing": ["com.ea.gp.needforspeedmostwanted", "com.gameloft.android.ANMP.GloftA9HM",
               "com.miniclip.eightballpool", "com.hutchgames.hillclimb"],
    "Adventure": ["com.mojang.minecraftpe", "com.roblox.client", "com.innersloth.spacemafia"],
    "Puzzle": ["com.king.candycrushsodasaga", "com.easybrain.sudoku.android", "com.gramgames.mergedragons"],
    "Casual": ["com.supercell.hayday", "com.zynga.toonblast", "com.playrix.homescapes"],
    "Strategy": ["com.supercell.clashofclans", "com.supercell.clashroyale", "com.nexonm.dominations"],
    "Card": ["com.mobilityware.solitaire", "com.zynga.poker"],
    "Casino": ["com.productmadness.hoc", "com.slotomania.slots"],
    "Role Playing": ["com.garena.game.codm", "net.wooga.june"],
    "Simulation": ["com.ea.games.simsfreeplay_row", "com.tastypill.idlefactory"],
    "Sports": ["com.ea.gp.fifamobile", "com.dreamgames.trainstation2"],
    "Board": ["com.king.farmheroessaga", "com.electronicarts.monopoly"],
    "Trivia": ["com.scopely.wheeloffortune", "com.smgmobile.trivia"],
    "Word": ["com.zynga.words", "com.pyxelperfect.wordconnect"],
    "Music": ["com.miniclip.crazykart", "com.beatstar.game"],
}


def fetch_snapshot():
    rows = []
    fetched_at = datetime.now(timezone.utc).isoformat()
    for genre, app_ids in WATCHLIST.items():
        for app_id in app_ids:
            try:
                d = gp_app(app_id, lang="en", country="us")
                rows.append({
                    "fetched_at": fetched_at,
                    "genre": genre,
                    "app_id": app_id,
                    "title": d.get("title"),
                    "score": d.get("score"),
                    "ratings": d.get("ratings"),
                    "reviews": d.get("reviews"),
                    "installs": d.get("installs"),
                    "real_installs": d.get("realInstalls"),
                    "min_installs": d.get("minInstalls"),
                    "price": d.get("price"),
                    "free": d.get("free"),
                    "updated": d.get("updated"),
                    "version": d.get("version"),
                })
            except Exception as e:
                print(f"HATA: {app_id} ({genre}) çekilemedi: {e}")
            time.sleep(1.5)  # Play Store'u aşırı yüklememek / bloklanmamak için nazik gecikme
    return rows


def append_to_csv(rows):
    file_exists = os.path.exists(SNAPSHOT_PATH)
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    fieldnames = ["fetched_at", "genre", "app_id", "title", "score", "ratings", "reviews",
                  "installs", "real_installs", "min_installs", "price", "free", "updated", "version"]
    with open(SNAPSHOT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data = fetch_snapshot()
    print(f"{len(data)} satır çekildi.")
    append_to_csv(data)
    print(f"snapshots.csv güncellendi -> {SNAPSHOT_PATH}")
