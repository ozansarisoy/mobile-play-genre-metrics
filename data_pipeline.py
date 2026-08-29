"""
Mobil Oyun Türleri Veri Bilimi Projesi — Veri Hazırlama Modülü
================================================================
Kaynak veri: Google Play Store Apps Dataset (Kaggle - lava18/google-play-store-apps,
GitHub aynası: sumitgirwal/google-play-store-data-analysis, googleplaystore.csv)
~10.841 uygulama kaydı, 2018 itibarıyla Play Store'dan scrape edilmiştir.
Bu modül GAME kategorisindeki ~1.144 kaydı ayıklayıp analiz için temizler.
"""

import pandas as pd
import numpy as np
import re
import os

RAW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "googleplaystore_raw.csv")


def _parse_installs(x):
    """'10,000+' -> 10000 (int). Kurulum sayısı aralık üst sınırı olarak yorumlanır."""
    if pd.isna(x):
        return np.nan
    x = str(x).replace(",", "").replace("+", "").strip()
    if x in ("Free", "0", ""):
        return 0 if x == "0" else np.nan
    try:
        return int(x)
    except ValueError:
        return np.nan


def _parse_size(x):
    """'19M' -> 19.0 (MB), '512k' -> 0.5 (MB), 'Varies with device' -> NaN."""
    if pd.isna(x):
        return np.nan
    x = str(x).strip()
    if "Varies" in x:
        return np.nan
    m = re.match(r"^([\d.]+)([MkK])$", x)
    if not m:
        return np.nan
    val, unit = float(m.group(1)), m.group(2).upper()
    return val if unit == "M" else val / 1024.0


def _parse_price(x):
    if pd.isna(x):
        return np.nan
    x = str(x).replace("$", "").strip()
    try:
        return float(x)
    except ValueError:
        return np.nan


def load_and_clean(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Kaynak veride bir satırda kolon kayması (malformed) hatası bilinir; Rating>5 olanları ele
    df = df[pd.to_numeric(df["Rating"], errors="coerce").le(5) | df["Rating"].isna()]

    games = df[df["Category"] == "GAME"].copy()

    games["Installs_num"] = games["Installs"].apply(_parse_installs)
    games["Size_MB"] = games["Size"].apply(_parse_size)
    games["Price_num"] = games["Price"].apply(_parse_price)
    games["Reviews_num"] = pd.to_numeric(games["Reviews"], errors="coerce")
    games["Rating_num"] = pd.to_numeric(games["Rating"], errors="coerce")
    games["Type"] = games["Type"].fillna("Free")
    games["Last_Updated_dt"] = pd.to_datetime(games["Last Updated"], errors="coerce")

    # Ana tür (primary genre): ';' ile ayrılan ilk etiket
    games["Primary_Genre"] = games["Genres"].apply(lambda g: str(g).split(";")[0].strip())

    # Az örnekli türleri (n<10) "Diğer" altında topla — istatistiksel testlerin güvenilirliği için
    genre_counts = games["Primary_Genre"].value_counts()
    small_genres = genre_counts[genre_counts < 10].index
    games["Genre_Group"] = games["Primary_Genre"].where(
        ~games["Primary_Genre"].isin(small_genres), "Other (n<10)"
    )

    # Tekrarlanan uygulama isimlerini (farklı scrape zamanlarından kaynaklı) ele
    games = games.drop_duplicates(subset=["App"], keep="first")

    # Analiz için kritik alanlarda eksik olan satırları at
    games = games.dropna(subset=["Rating_num", "Installs_num", "Reviews_num"])

    # Log dönüşümler: Installs ve Reviews aşırı sağa çarpık (birkaç mertebe farkı) —
    # görselleştirme ve korelasyon analizinde log ölçek kullanılacak
    games["Installs_log"] = np.log10(games["Installs_num"].replace(0, 1))
    games["Reviews_log"] = np.log10(games["Reviews_num"].replace(0, 1))

    return games.reset_index(drop=True)


if __name__ == "__main__":
    g = load_and_clean()
    print(g.shape)
    print(g["Genre_Group"].value_counts())
    print(g[["Rating_num", "Installs_num", "Reviews_num", "Size_MB", "Price_num"]].describe())
