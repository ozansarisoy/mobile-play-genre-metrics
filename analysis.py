"""
İstatistiksel Analiz Modülü
============================
Neden bu yöntemler seçildi?
- Rating, Installs, Reviews değişkenleri normal dağılıma uymuyor (aşırı çarpık,
  Shapiro-Wilk testi ile doğrulanır) -> parametrik olmayan testler tercih edilir.
- Tür (genre) sayısı ikiden fazla ve bağımsız gruplar olduğu için çoklu grup
  karşılaştırmasında ANOVA yerine Kruskal-Wallis H testi kullanılır.
- Kruskal-Wallis anlamlı çıkarsa, hangi tür çiftlerinin farklı olduğunu bulmak
  için Dunn post-hoc testi (Bonferroni düzeltmeli) uygulanır.
- Değişkenler arası ilişkilerde Pearson yerine Spearman korelasyonu kullanılır
  çünkü ilişkiler monotonik ama doğrusal olmayabilir ve veri çarpık.
- Tür bazlı kümeleme için K-Means kullanılır; küme sayısı Elbow yöntemi ve
  Silhouette skoru ile birlikte belirlenir (tek başına elbow sübjektif olduğu için).
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def normality_check(df: pd.DataFrame, col: str, sample_n: int = 500) -> dict:
    """Shapiro-Wilk normallik testi. p<0.05 -> normal dağılım reddedilir."""
    sample = df[col].dropna()
    if len(sample) > sample_n:
        sample = sample.sample(sample_n, random_state=42)
    stat, p = stats.shapiro(sample)
    return {"statistic": stat, "p_value": p, "normal_mi": p > 0.05}


def genre_descriptive_stats(df: pd.DataFrame, genre_col="Genre_Group") -> pd.DataFrame:
    agg = df.groupby(genre_col).agg(
        n=("App", "count"),
        avg_rating=("Rating_num", "mean"),
        median_rating=("Rating_num", "median"),
        rating_std=("Rating_num", "std"),
        total_installs=("Installs_num", "sum"),
        avg_installs=("Installs_num", "mean"),
        median_installs=("Installs_num", "median"),
        avg_reviews=("Reviews_num", "mean"),
        avg_size_mb=("Size_MB", "mean"),
        paid_share=("Price_num", lambda x: (x > 0).mean()),
        avg_price=("Price_num", lambda x: x[x > 0].mean()),
    ).sort_values("total_installs", ascending=False)
    return agg.round(3)


def kruskal_wallis_by_genre(df: pd.DataFrame, value_col="Rating_num", genre_col="Genre_Group", lang="en") -> dict:
    groups = [g[value_col].dropna().values for _, g in df.groupby(genre_col) if len(g) >= 5]
    h_stat, p_value = stats.kruskal(*groups)
    msg_en = (
        "There IS a statistically significant difference in rating distributions "
        "across genres (p<0.05) — genre choice may relate to user satisfaction."
        if p_value < 0.05 else
        "No statistically significant difference in rating distributions across genres (p>=0.05)."
    )
    msg_tr = (
        "Türler arasında puan dağılımlarında istatistiksel olarak anlamlı fark VAR "
        "(p<0.05) — tür seçimi kullanıcı memnuniyetiyle ilişkili olabilir."
        if p_value < 0.05 else
        "Türler arasında puan dağılımlarında istatistiksel olarak anlamlı fark yok (p>=0.05)."
    )
    return {
        "H_stat": h_stat,
        "p_value": p_value,
        "significant_0.05": p_value < 0.05,
        "n_groups": len(groups),
        "interpretation": msg_tr if lang == "tr" else msg_en,
    }


def dunn_posthoc(df: pd.DataFrame, value_col="Rating_num", genre_col="Genre_Group") -> pd.DataFrame:
    """Basit Bonferroni düzeltmeli ikili Mann-Whitney U testleri (Dunn testinin
    yerine geçen, bağımlılık gerektirmeyen bir yaklaşım)."""
    genres = [g for g, sub in df.groupby(genre_col) if len(sub) >= 5]
    results = []
    n_comparisons = len(genres) * (len(genres) - 1) // 2
    for i in range(len(genres)):
        for j in range(i + 1, len(genres)):
            g1, g2 = genres[i], genres[j]
            v1 = df.loc[df[genre_col] == g1, value_col].dropna()
            v2 = df.loc[df[genre_col] == g2, value_col].dropna()
            u_stat, p = stats.mannwhitneyu(v1, v2, alternative="two-sided")
            p_adj = min(p * n_comparisons, 1.0)  # Bonferroni düzeltmesi
            results.append({
                "genre_1": g1, "genre_2": g2, "u_statistic": u_stat,
                "p_raw": p, "p_bonferroni": p_adj, "significant": p_adj < 0.05,
            })
    return pd.DataFrame(results).sort_values("p_bonferroni")


def correlation_matrix(df: pd.DataFrame, lang="en") -> pd.DataFrame:
    cols = ["Rating_num", "Installs_log", "Reviews_log", "Size_MB", "Price_num"]
    corr = df[cols].corr(method="spearman")
    labels_en = ["Rating", "Installs(log)", "Reviews(log)", "Size(MB)", "Price"]
    labels_tr = ["Puan", "Kurulum(log)", "Yorum(log)", "Boyut(MB)", "Fiyat"]
    corr.columns = labels_tr if lang == "tr" else labels_en
    corr.index = corr.columns
    return corr.round(3)


def cluster_genres(df: pd.DataFrame, genre_col="Genre_Group", k_range=range(2, 8)):
    """Tür bazında agregatlanmış özelliklerle K-Means kümeleme.
    Amaç: türleri 'niş/az bilinen', 'kitlesel-casual', 'yüksek etkileşimli/rekabetçi'
    gibi segmentlere ayırmak.
    """
    agg = df.groupby(genre_col).agg(
        avg_rating=("Rating_num", "mean"),
        avg_log_installs=("Installs_log", "mean"),
        avg_log_reviews=("Reviews_log", "mean"),
        avg_size=("Size_MB", "mean"),
        paid_share=("Price_num", lambda x: (x > 0).mean()),
    ).dropna()

    X = StandardScaler().fit_transform(agg.values)

    inertias, sil_scores = [], []
    for k in k_range:
        if k >= len(agg):
            break
        km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X, km.labels_))

    valid_ks = list(k_range)[: len(sil_scores)]
    best_k = valid_ks[int(np.argmax(sil_scores))]

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10).fit(X)
    agg["cluster"] = km_final.labels_

    diag = pd.DataFrame({"k": valid_ks, "inertia": inertias, "silhouette": sil_scores})
    return agg.round(3), diag.round(3), best_k


def iqr_outliers(df: pd.DataFrame, col: str) -> pd.DataFrame:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return df[(df[col] < lower) | (df[col] > upper)]


def popularity_score(df: pd.DataFrame) -> pd.Series:
    """Kompozit popülerlik skoru: standardize edilmiş (z-skor) kurulum(log),
    yorum(log) ve puanın ağırlıklı ortalaması. Ağırlıklar: kurulum 0.5,
    yorum-hacmi 0.3 (etkileşim/ilgi göstergesi), puan 0.2 (kalite göstergesi)."""
    z_inst = (df["Installs_log"] - df["Installs_log"].mean()) / df["Installs_log"].std()
    z_rev = (df["Reviews_log"] - df["Reviews_log"].mean()) / df["Reviews_log"].std()
    z_rat = (df["Rating_num"] - df["Rating_num"].mean()) / df["Rating_num"].std()
    return 0.5 * z_inst + 0.3 * z_rev + 0.2 * z_rat


def genre_momentum_static(df: pd.DataFrame, genre_col="Genre_Group") -> pd.DataFrame:
    """Statik veriden 'momentum' proxy'si — GERÇEK bir tahmin değil, dolaylı bir
    göstergedir. Algoritma: her tür için son 12 ayda güncellenmiş uygulama
    oranı hesaplanır (Last_Updated_dt >= veri setindeki en güncel tarih - 365 gün).
    Yüksek oran, geliştiricilerin o türe hâlâ aktif yatırım yaptığını (canlı/
    büyüyen tür) düşük oran ise bakımın azaldığını (durgun/düşüşte tür)
    dolaylı olarak gösterir. İstatistiksel bir anlamlılık testi DEĞİLDİR."""
    ref_date = df["Last_Updated_dt"].max()
    cutoff = ref_date - pd.Timedelta(days=365)
    tmp = df.copy()
    tmp["recently_updated"] = tmp["Last_Updated_dt"] >= cutoff
    agg = tmp.groupby(genre_col).agg(
        n=("App", "count"),
        recent_update_share=("recently_updated", "mean"),
        avg_rating=("Rating_num", "mean"),
    ).sort_values("recent_update_share", ascending=False)
    agg["momentum_label"] = pd.cut(
        agg["recent_update_share"], bins=[-0.01, 0.33, 0.66, 1.01],
        labels=["declining_proxy", "stable_proxy", "rising_proxy"],
    )
    return agg.round(3)


def forecast_live_trend(snaps: pd.DataFrame, metric: str = "score", horizon_days: int = 30,
                         genre_col: str = "genre", time_col: str = "fetched_at") -> pd.DataFrame:
    """CANLI snapshot zaman serisinden (data/snapshots.csv) tür bazlı doğrusal
    trend (Linear Regression / OLS) fit eder ve horizon_days sonrası için
    nokta tahmini üretir.

    Neden Linear Regression? Genre başına biriken veri noktası azken (ilk
    haftalarda) karmaşık modeller (ARIMA, Prophet) aşırı öğrenir (overfit) ve
    güvenilmez tahmin üretir. Basit bir doğrusal trend, az veriyle bile
    yorumlanabilir bir eğim (slope) ve yön (yükseliyor/düşüyor/sabit) verir.
    Veri biriktikçe (>60 gün) daha esnek modellere (ör. mevsimsellik içeren
    Holt-Winters) geçilebilir; şu an için OLS en sağlam ve en az varsayım
    gerektiren seçimdir.

    En az MIN_POINTS gözlem olmayan türler için tahmin ATLANIR (güvenilmez
    olurdu) — bu, sonuçları olduğundan güvenilir göstermemek için bilinçli
    bir tasarım kararıdır.
    """
    from sklearn.linear_model import LinearRegression

    MIN_POINTS = 5
    results = []
    snaps = snaps.dropna(subset=[metric, time_col]).copy()
    snaps["t_days"] = (snaps[time_col] - snaps[time_col].min()).dt.total_seconds() / 86400

    for genre, g in snaps.groupby(genre_col):
        g_agg = g.groupby("t_days", as_index=False)[metric].mean()
        if len(g_agg) < MIN_POINTS:
            results.append({
                genre_col: genre, "n_points": len(g_agg), "slope_per_day": np.nan,
                "direction": "insufficient_data", "forecast_value": np.nan,
                "r_squared": np.nan,
            })
            continue
        X = g_agg[["t_days"]].values
        y = g_agg[metric].values
        model = LinearRegression().fit(X, y)
        slope = model.coef_[0]
        r2 = model.score(X, y)
        last_t = g_agg["t_days"].max()
        forecast_t = last_t + horizon_days
        forecast_value = model.predict([[forecast_t]])[0]
        direction = "rising" if slope > 0.001 else ("declining" if slope < -0.001 else "stable")
        results.append({
            genre_col: genre, "n_points": len(g_agg), "slope_per_day": slope,
            "direction": direction, "forecast_value": forecast_value, "r_squared": r2,
        })
    result_df = pd.DataFrame(results, columns=[genre_col, "n_points", "slope_per_day",
                                                 "direction", "forecast_value", "r_squared"])
    return result_df.sort_values("slope_per_day", ascending=False)
