"""
Two-language (EN default / TR) translation dictionary for the Streamlit app.
Usage in app.py: `t("key")` returns the string in the currently selected
language (st.session_state["lang"], default "en").
"""

TRANSLATIONS = {
    "en": {
        "app_title": "Mobile Play Genre Metrics (MPGM)",
        "app_caption": "Data source: Google Play Store Apps Dataset (Kaggle — lava18/google-play-store-apps). "
                        "This analysis examines {n} cleaned GAME-category apps across {g} genre groups.",
        "methodology_expander": "About the data source and methodology (why / how)",
        "methodology_md": """
**Data source:** The Google Play Store Apps dataset, originally published on Kaggle
(user: lava18, `google-play-store-apps`), contains ~10,841 scraped app records.
This app fetches it programmatically from a current GitHub mirror
(`sumitgirwal/google-play-store-data-analysis`) via `raw.githubusercontent.com`.

**Why this dataset?** Play Store classifies the mobile game market via
Category=GAME and Genres sub-tags — it holds genre, install count, rating,
size and price in one place. Since there is no free public real-time Play
Store API, this broad static snapshot was chosen instead.

**Limitations (stated honestly):** The data is from a scrape around 2018; it
does not reflect current 2026 absolute market sizes. "Installs" is a range
(e.g. "10,000,000+") in the Play Store, so it should be read as a lower
bound, not an exact count. The analysis is therefore reliable for
**relative** genre comparisons, not absolute current market share.

**How was it cleaned?**
- `Installs` "10,000+" → 10000 (comma and + stripped)
- `Size` "19M"/"512k" → numeric MB, "Varies with device" → missing
- `Genres` split on ';', first tag kept as "primary genre"
- Genres with n<10 samples grouped into "Other (n<10)" (for test reliability)
- Rows with missing/invalid critical fields (rating, installs, reviews) dropped
- Duplicate app names dropped
        """,
        "tab_overview": "Overview",
        "tab_genre_compare": "Genre Comparison",
        "tab_stats": "Statistical Tests",
        "tab_cluster": "Clustering",
        "tab_raw": "Raw Data & Outliers",
        "tab_live": "Live Monitoring (Trend)",
        "metric_total_games": "Total games (clean)",
        "metric_n_genres": "Number of genres",
        "metric_avg_rating": "Average rating",
        "metric_median_installs": "Median installs",
        "chart_games_per_genre": "Games per genre (market saturation indicator)",
        "chart_installs_per_genre": "Total installs per genre (log scale)",
        "x_total_installs_log": "Total installs (log)",
        "chart_rating_boxplot": "User rating distribution by genre",
        "boxplot_note": """
**Why a box plot?** The mean alone can be misleading because it's sensitive to
extreme values. A box plot shows the median, interquartile range (IQR) and
outliers at once — letting us tell apart "generally good with a few bad
outliers" from "generally mediocre".
        """,
        "genre_stats_header": "### Genre-level summary statistics",
        "genre_stats_note": """
**How was this computed?** For each genre group, `pandas.groupby().agg()`
computed mean/median rating, total and average installs, average review
count, average size (MB) and paid-app share. Median is a more robust
central-tendency measure than mean for heavily skewed distributions (like
install counts) because it isn't dragged by extreme values.
        """,
        "popularity_header": "### Popularity score — top-performing games",
        "popularity_caption": "Popularity Score = 0.5×z(log installs) + 0.3×z(log reviews) + 0.2×z(rating). "
                               "Weights prioritize install volume (market reach), review volume "
                               "represents engagement/interest, and rating represents quality.",
        "slider_top_n": "Number of games to show",
        "corr_header": "### Correlation between variables (Spearman)",
        "corr_title": "Spearman correlation matrix",
        "corr_note": """
**Why Spearman, not Pearson?** Pearson correlation assumes a linear
relationship and normal distribution. Variables like installs and reviews
are heavily right-skewed (a few mega-hits, most apps low install counts), so
Spearman's rank-based approach is more reliable. The strong positive
correlation between reviews and installs is expected (both reflect user
volume); the negative correlation between price and installs confirms the
free-to-play model dominates the mobile game market.
        """,
        "normality_header": "### 1. Normality test (Shapiro-Wilk)",
        "normality_warning": "p < 0.05 → the Rating distribution is NOT normal. This is why "
                              "non-parametric tests are used below.",
        "normality_success": "p >= 0.05 → the normal distribution assumption could not be rejected.",
        "kw_header": "### 2. Kruskal-Wallis H test — is there a rating difference across genres?",
        "kw_caption": "H0: All genres have the same rating distribution. H1: At least one genre differs.",
        "kw_h_stat": "H statistic",
        "kw_p_value": "p-value",
        "posthoc_header": "### 3. Post-hoc pairwise comparisons (Mann-Whitney U + Bonferroni correction)",
        "posthoc_caption": """
Kruskal-Wallis tells us there is an overall difference, but not WHICH genre
pairs differ. So each genre pair gets its own Mann-Whitney U test. Since
multiple comparisons are made, p-values are Bonferroni-corrected
(p × number of comparisons) to reduce false-positive risk.
        """,
        "posthoc_checkbox": "Show only significant differences (p_bonferroni < 0.05)",
        "price_header": "### 4. Price ↔ Rating relationship (Mann-Whitney U)",
        "price_summary": "Paid game average rating: **{p:.2f}** (n={pn}) | Free game average rating: **{f:.2f}** (n={fn})",
        "price_sig": "A statistically significant rating difference was found between paid and free games (p<0.05).",
        "price_nosig": "No statistically significant rating difference was found between paid and free games (p>=0.05).",
        "cluster_header": "### K-Means genre segmentation",
        "cluster_intro": """
**Why clustering?** Instead of manually classifying 16 genres, the goal is to
group them by shared behavioral features (average rating, install volume,
review volume, size, paid share) using data-driven segments. This gives an
objective answer to "which genre segment should I target" via Streamlit.

**How?**
1. Features were standardized (z-score) per genre — otherwise large-scale
   variables like install count would dominate the clustering alone.
2. K-Means was tried for K=2..7; for each k, the **Silhouette score**
   (how well-separated clusters are) was computed — the elbow method alone
   wasn't trusted since the elbow point can be subjective.
3. The k with the highest Silhouette score was selected.
        """,
        "silhouette_title": "Silhouette score vs k (selected k={k})",
        "elbow_title": "Elbow chart (inertia)",
        "cluster_result_header": "### Result: {k} clusters found",
        "cluster_scatter_title": "Genre clusters: install volume vs average rating",
        "cluster_x": "Average installs (log10)",
        "cluster_y": "Average rating",
        "cluster_color": "Cluster",
        "outlier_header": "### Outlier detection — IQR method",
        "outlier_caption": "IQR method: values below Q1 - 1.5×IQR or above Q3 + 1.5×IQR are considered "
                            "outliers. This is a robust method independent of distribution shape.",
        "outlier_select": "Column to search for outliers",
        "outlier_found": "**{n}** outliers found ({pct:.1f}% of data).",
        "raw_header": "### Filterable raw data",
        "raw_filter": "Filter by genre",
        "download_button": "Download cleaned data as CSV",
        "footer": "This project is prepared for publishing on Streamlit. Statistical methods: "
                  "scipy.stats (Shapiro-Wilk, Kruskal-Wallis, Mann-Whitney U), scikit-learn "
                  "(K-Means, StandardScaler, Silhouette).",
        "live_header": "### Live data monitoring",
        "live_intro": """
**Architecture — why built this way?**
Play Store has no free, public, real-time API. So "live" data is provided by
a **GitHub Actions** cron job running daily (`live_fetch.py`): every day at
06:00 UTC, current rating, review count and install data is fetched from the
Play Store for a curated watchlist of representative apps per genre, and
appended as new rows to `data/snapshots.csv` (an append-only time series).
This file is auto-committed back to GitHub.

**Streamlit Community Cloud was chosen as the dashboard** (free, already set
up for this project, auto-updates when connected to the GitHub repo) — no
need to open a separate Grafana/Supabase account. The Streamlit app re-reads
the current `snapshots.csv` on every load and recomputes the charts below live.
        """,
        "live_no_data": """
No live snapshot yet. Once the GitHub Actions workflow
(`.github/workflows/daily_snapshot.yml`) is pushed to the repo, the first
snapshot will be created automatically (06:00 UTC) or can be triggered
manually via **"Run workflow"** in the Actions tab. After a few days of
accumulated data this tab will show daily/weekly/monthly/yearly trends.
        """,
        "live_metric_days": "Snapshot days collected",
        "live_metric_apps": "Apps tracked",
        "live_metric_last": "Last updated",
        "live_period": "Period",
        "live_period_daily": "Daily",
        "live_period_weekly": "Weekly",
        "live_period_monthly": "Monthly",
        "live_period_yearly": "Yearly",
        "live_metric_select": "Metric",
        "live_metric_score": "Average rating",
        "live_metric_reviews": "Review count",
        "live_metric_installs": "Installs (lower bound)",
        "live_trend_title": "{period} genre-level {metric} change",
        "live_not_enough": "Not enough data accumulated yet for the selected period.",
        "live_app_history_header": "#### Per-app raw snapshot history",
        "live_app_select": "Select app",
        "lang_label": "Language / Dil",
        "forecast_header": "### Genre momentum & trend forecast — which genres may rise or fall?",
        "forecast_static_sub": "#### A. Static-data momentum proxy (available now)",
        "forecast_static_note": """
**Algorithm:** For each genre, the share of apps updated in the last 12
months (relative to the dataset's most recent update date) is computed.
This is **not** a statistical forecast — it's an indirect proxy: a high
recent-update share suggests developers are still actively investing in
that genre (a "live/rising" signal), while a low share suggests reduced
maintenance (a "stagnant/declining" signal). Genres are bucketed into
rising/stable/declining proxy tiers by this ratio.
        """,
        "forecast_live_sub": "#### B. Live time-series forecast (Linear Regression / OLS)",
        "forecast_live_note": """
**Algorithm:** Once daily live snapshots accumulate (`data/snapshots.csv`,
collected by the GitHub Actions cron job), a **Linear Regression (OLS,
scikit-learn)** model is fit per genre: time (days) → metric (rating /
reviews / installs). The fitted slope gives the trend direction (rising,
declining, stable) and a point forecast N days ahead.

**Why Linear Regression and not ARIMA/Prophet?** With few data points
(especially in the first weeks), complex models overfit and produce
unreliable forecasts. A simple linear trend stays interpretable and stable
even with limited data. Genres with fewer than 5 collected data points are
explicitly marked "insufficient data" rather than shown a forecast — this
is a deliberate choice to avoid presenting an unreliable number as if it
were reliable. As more weeks of data accumulate, this can be upgraded to a
model that captures seasonality (e.g. Holt-Winters exponential smoothing).
        """,
        "forecast_live_no_data": "Not enough live snapshot history yet to fit a trend model. "
                                  "This section activates once several days of data have accumulated.",
        "forecast_horizon_label": "Forecast horizon (days)",
        "forecast_metric_label": "Metric to forecast",
        "apple_header": "### Apple App Store live rank (second live signal)",
        "apple_intro": """
**Why a second live source?** The Google Play watchlist above tracks a
handful of representative apps because Google Play has no free official
charts API. Apple, by contrast, publishes an official, free, keyless feed of
its **real, ranked** Top Free Games chart per genre — not a proxy, the
actual market position. This section tracks that daily, independently of
the Google Play signal above.
        """,
        "apple_no_data": "No Apple chart snapshots yet. This populates once the GitHub Actions "
                          "workflow has run `live_fetch_apple.py` at least once.",
        "apple_metric_avg_rank": "Average rank (lower = more popular)",
        "apple_trend_title": "Average Apple Top Free Games rank by genre over time",
        "apple_leaderboard_header": "#### Latest day — best average rank per genre",
        "apple_note": "Rank 1 is the most popular app in that genre on the US App Store that day. "
                      "A falling line means the genre's presence in the charts is strengthening.",
    },
    "tr": {
        "app_title": "Mobile Play Genre Metrics (MPGM)",
        "app_caption": "Veri kaynağı: Google Play Store Apps Dataset (Kaggle — lava18/google-play-store-apps). "
                        "Bu analizde {n:,} temizlenmiş GAME kategorisi uygulaması, {g} tür grubu altında incelenmiştir.",
        "methodology_expander": "Veri kaynağı ve metodoloji hakkında (neden / nasıl)",
        "methodology_md": """
**Veri kaynağı:** Google Play Store Apps veri seti, orijinal olarak Kaggle'da
(kullanıcı: lava18, `google-play-store-apps`) yayınlanmıştır ve Play Store'dan
scrape edilen ~10.841 uygulama kaydı içerir. Uygulama bu veriyi güncel bir
GitHub aynasından (`sumitgirwal/google-play-store-data-analysis`) `raw.githubusercontent.com`
üzerinden programatik olarak çekmiştir.

**Neden bu veri seti?** Play Store, mobil oyun pazarını Category=GAME ve alt
Genres etiketleriyle sınıflandırır — bu proje için gerekli olan tür (genre),
kurulum sayısı, puan, boyut ve fiyat bilgilerini tek bir kaynakta barındırır.
Gerçek zamanlı bir Play Store API'si genel kullanıma açık ve ücretsiz
olmadığından, bu statik-ama-geniş kapsamlı veri seti tercih edilmiştir.

**Sınırlamalar (dürüstçe belirtilmelidir):** Veri 2018 civarı bir scrape
anına aittir; güncel 2026 pazar büyüklüklerini yansıtmaz. "Installs" alanı
Play Store'da aralık (ör. "10.000.000+") olarak sunulur, bu nedenle kesin
kurulum sayısı değil, alt sınır olarak yorumlanmalıdır. Analiz bu nedenle
**göreli** tür karşılaştırmaları için güvenilirdir, mutlak günümüz pazar
payı tahmini için değildir.

**Nasıl temizlendi?**
- `Installs` "10,000+" → 10000 (virgül ve + işareti temizlendi)
- `Size` "19M"/"512k" → MB cinsinden sayısal değer, "Varies with device" → eksik
- `Genres` alanı ';' ile bölünüp ilk etiket "ana tür" (primary genre) olarak alındı
- n<10 örnekli türler "Diğer" grubuna toplandı (istatistiksel test güvenilirliği için)
- Kritik alanlarda (puan, kurulum, yorum) eksik veya bozuk (rating>5) satırlar elendi
- Tekrarlanan uygulama adları elendi
        """,
        "tab_overview": "Genel Bakış",
        "tab_genre_compare": "Tür Karşılaştırması",
        "tab_stats": "İstatistiksel Testler",
        "tab_cluster": "Kümeleme Analizi",
        "tab_raw": "Ham Veri & Aykırı Değerler",
        "tab_live": "Canlı İzleme (Trend)",
        "metric_total_games": "Toplam oyun (temiz)",
        "metric_n_genres": "Tür sayısı",
        "metric_avg_rating": "Ortalama puan",
        "metric_median_installs": "Medyan kurulum",
        "chart_games_per_genre": "Tür başına oyun sayısı (pazar doygunluğu göstergesi)",
        "chart_installs_per_genre": "Tür başına toplam kurulum (log ölçek)",
        "x_total_installs_log": "Toplam kurulum (log)",
        "chart_rating_boxplot": "Türlere göre kullanıcı puanı dağılımı",
        "boxplot_note": """
**Neden kutu grafiği (box plot)?** Ortalama tek başına yanıltıcı olabilir
çünkü aşırı değerlerden (outlier) etkilenir. Kutu grafiği medyanı, çeyrekler
arası açıklığı (IQR) ve aykırı noktaları aynı anda gösterir — böylece bir
türün "genelde iyi puanlı ama birkaç kötü örnek var mı" yoksa "genel
olarak vasat mı" olduğunu ayırt edebiliriz.
        """,
        "genre_stats_header": "### Tür bazlı özet istatistik tablosu",
        "genre_stats_note": """
**Nasıl hesaplandı?** Her tür grubu için `pandas.groupby().agg()` ile
ortalama/medyan puan, toplam ve ortalama kurulum, ortalama yorum sayısı,
ortalama boyut (MB) ve ücretli uygulama oranı hesaplandı. Medyan, aşırı
çarpık dağılımlarda (kurulum sayısı gibi) ortalamadan daha güvenilir bir
merkezi eğilim ölçüsüdür çünkü uç değerlerden etkilenmez.
        """,
        "popularity_header": "### Popülerlik skoru — en yüksek performanslı oyunlar",
        "popularity_caption": "Popülerlik Skoru = 0.5×z(log kurulum) + 0.3×z(log yorum) + 0.2×z(puan). "
                               "Ağırlıklar kurulum hacmine öncelik verir (pazar ulaşımı), yorum hacmi "
                               "etkileşim/ilgiyi, puan ise kaliteyi temsil eder.",
        "slider_top_n": "Gösterilecek oyun sayısı",
        "corr_header": "### Değişkenler arası korelasyon (Spearman)",
        "corr_title": "Spearman korelasyon matrisi",
        "corr_note": """
**Neden Spearman, Pearson değil?** Pearson korelasyonu doğrusal ilişkiyi
ve normal dağılımı varsayar. Kurulum ve yorum sayısı gibi değişkenler
aşırı sağa çarpık olduğundan (birkaç mega-hit, çoğu düşük kurulum),
Spearman'ın sıra-tabanlı (rank-based) yaklaşımı daha güvenilir sonuç verir.
Yorum sayısı ile kurulum arasındaki güçlü pozitif korelasyon beklenir
(her ikisi de kullanıcı hacmini yansıtır); fiyat ile kurulum arasındaki
negatif korelasyon ise ücretsiz modelin mobil oyun pazarında baskın
olduğunu doğrular.
        """,
        "normality_header": "### 1. Normallik testi (Shapiro-Wilk)",
        "normality_warning": "p < 0.05 → Puan (Rating) dağılımı normal DEĞİL. Bu yüzden "
                              "aşağıda parametrik olmayan (non-parametrik) testler kullanılmıştır.",
        "normality_success": "p >= 0.05 → Normal dağılım varsayımı reddedilemedi.",
        "kw_header": "### 2. Kruskal-Wallis H testi — türler arası puan farkı var mı?",
        "kw_caption": "H0: Tüm türlerin puan dağılımları aynıdır. H1: En az bir tür farklıdır.",
        "kw_h_stat": "H istatistiği",
        "kw_p_value": "p-değeri",
        "posthoc_header": "### 3. Post-hoc ikili karşılaştırmalar (Mann-Whitney U + Bonferroni düzeltmesi)",
        "posthoc_caption": """
Kruskal-Wallis testi genel bir fark olduğunu söyler ama HANGİ tür
çiftlerinin farklı olduğunu söylemez. Bu yüzden her tür çifti için
ayrı ayrı Mann-Whitney U testi uygulanır. Çoklu karşılaştırma yapıldığı
için yanlış-pozitif riskini azaltmak amacıyla p-değerleri Bonferroni
yöntemiyle düzeltilir (p × karşılaştırma sayısı).
        """,
        "posthoc_checkbox": "Sadece anlamlı farkları göster (p_bonferroni < 0.05)",
        "price_header": "### 4. Fiyat ↔ Puan ilişkisi (Mann-Whitney U)",
        "price_summary": "Ücretli oyun ortalama puanı: **{p:.2f}** (n={pn}) | Ücretsiz oyun ortalama puanı: **{f:.2f}** (n={fn})",
        "price_sig": "Ücretli ve ücretsiz oyunlar arasında puan açısından istatistiksel olarak "
                     "anlamlı fark bulunmuştur (p<0.05).",
        "price_nosig": "Ücretli ve ücretsiz oyunlar arasında puan açısından anlamlı fark bulunamamıştır (p>=0.05).",
        "cluster_header": "### K-Means ile tür segmentasyonu",
        "cluster_intro": """
**Neden kümeleme?** Amaç, 16 farklı türü elle sınıflandırmak yerine, ortak
davranışsal özelliklerine (ortalama puan, kurulum hacmi, yorum hacmi,
boyut, ücretli oran) göre veri-odaklı segmentlere ayırmaktır. Bu,
Streamlit üzerinden "hangi tür grubuna girmeliyim" sorusuna nesnel bir
yanıt sunar.

**Nasıl?**
1. Her tür için özellikler standardize edildi (z-skor) — aksi halde
   kurulum sayısı gibi büyük ölçekli değişkenler kümelemeye tek başına
   hakim olurdu.
2. K=2..7 için K-Means denendi; her k için **Silhouette skoru**
   (kümeler ne kadar iyi ayrışmış) hesaplandı — sadece dirsek (elbow)
   yöntemine güvenilmedi çünkü elbow noktası sübjektif yorumlanabilir.
3. En yüksek Silhouette skoruna sahip k seçildi.
        """,
        "silhouette_title": "Silhouette skoru vs k (seçilen k={k})",
        "elbow_title": "Elbow grafiği (inertia)",
        "cluster_result_header": "### Sonuç: {k} küme bulundu",
        "cluster_scatter_title": "Tür kümeleri: kurulum hacmi vs ortalama puan",
        "cluster_x": "Ortalama kurulum (log10)",
        "cluster_y": "Ortalama puan",
        "cluster_color": "Küme",
        "outlier_header": "### Aykırı değer (outlier) tespiti — IQR yöntemi",
        "outlier_caption": "IQR yöntemi: Q1 - 1.5×IQR altında veya Q3 + 1.5×IQR üstünde kalan "
                            "değerler aykırı sayılır. Bu, dağılım şekline bağlı olmayan, sağlam "
                            "(robust) bir yöntemdir.",
        "outlier_select": "Aykırı değer aranacak sütun",
        "outlier_found": "**{n}** aykırı değer bulundu (verinin %{pct:.1f}'i).",
        "raw_header": "### Filtrelenebilir ham veri",
        "raw_filter": "Tür filtrele",
        "download_button": "Temizlenmiş veriyi CSV olarak indir",
        "footer": "Bu proje Streamlit üzerinde yayınlanmak üzere hazırlanmıştır. "
                  "İstatistiksel yöntemler: scipy.stats (Shapiro-Wilk, Kruskal-Wallis, "
                  "Mann-Whitney U), scikit-learn (K-Means, StandardScaler, Silhouette).",
        "live_header": "### Canlı veri izleme",
        "live_intro": """
**Mimari — neden bu şekilde kuruldu?**
Play Store'un genel kullanıma açık, ücretsiz ve gerçek-zamanlı bir API'si
yoktur. Bu yüzden "canlı" veri, **GitHub Actions** üzerinde günlük çalışan
bir cron job (`live_fetch.py`) ile sağlanır: her gün 06:00 UTC'de, tür
başına seçilmiş temsilci uygulamaların (`WATCHLIST`) güncel puan, yorum
sayısı ve kurulum verisi Play Store'dan çekilir ve `data/snapshots.csv`
dosyasına yeni bir satır seti olarak eklenir (append-only zaman serisi).
Bu dosya GitHub'a otomatik commit edilir.

**Dashboard olarak Streamlit Community Cloud seçildi** (ücretsiz, zaten bu
proje için kurulu, GitHub reposuna bağlanınca otomatik güncellenir) —
ayrı bir Grafana/Supabase hesabı açmaya gerek bırakmaz. Streamlit uygulaması
her yüklendiğinde güncel `snapshots.csv`'yi okur ve aşağıdaki grafikleri
canlı olarak yeniden hesaplar.
        """,
        "live_no_data": """
Henüz canlı veri snapshot'ı yok. GitHub Actions workflow'u
(`.github/workflows/daily_snapshot.yml`) repoya push edildikten
sonra ilk kez otomatik (06:00 UTC) veya Actions sekmesinden
**"Run workflow"** ile manuel tetiklendiğinde ilk snapshot
oluşur. Birkaç gün veri biriktikten sonra bu sekme günlük/haftalık/
aylık/yıllık trendleri gösterecektir.
        """,
        "live_metric_days": "Toplanan snapshot günü",
        "live_metric_apps": "Takip edilen uygulama",
        "live_metric_last": "Son güncelleme",
        "live_period": "Periyot",
        "live_period_daily": "Günlük",
        "live_period_weekly": "Haftalık",
        "live_period_monthly": "Aylık",
        "live_period_yearly": "Yıllık",
        "live_metric_select": "Metrik",
        "live_metric_score": "Ortalama puan",
        "live_metric_reviews": "Yorum sayısı",
        "live_metric_installs": "Kurulum (alt sınır)",
        "live_trend_title": "{period} tür bazlı {metric} değişimi",
        "live_not_enough": "Seçilen periyot için henüz yeterli veri birikmedi.",
        "live_app_history_header": "#### Uygulama bazlı ham snapshot geçmişi",
        "live_app_select": "Uygulama seç",
        "lang_label": "Language / Dil",
        "forecast_header": "### Tür momentumu ve trend tahmini — hangi türler yükselebilir veya düşebilir?",
        "forecast_static_sub": "#### A. Statik veriden momentum proxy'si (şu an mevcut)",
        "forecast_static_note": """
**Algoritma:** Her tür için son 12 ayda güncellenen uygulama oranı
(veri setindeki en güncel güncelleme tarihine göre) hesaplanır. Bu **istatistiksel
bir tahmin DEĞİLDİR** — dolaylı bir göstergedir: yüksek güncel-güncelleme
oranı geliştiricilerin o türe hâlâ aktif yatırım yaptığını ("canlı/yükselen"
sinyali), düşük oran ise azalan bakımı ("durgun/düşüşte" sinyali) gösterir.
Türler bu orana göre yükselen/sabit/düşüşte proxy katmanlarına ayrılır.
        """,
        "forecast_live_sub": "#### B. Canlı zaman serisi tahmini (Doğrusal Regresyon / OLS)",
        "forecast_live_note": """
**Algoritma:** Günlük canlı snapshot'lar birikince (`data/snapshots.csv`,
GitHub Actions cron job'u ile toplanır), her tür için **Doğrusal Regresyon
(OLS, scikit-learn)** modeli fit edilir: zaman (gün) → metrik (puan/yorum/
kurulum). Fit edilen eğim (slope) trend yönünü (yükseliyor, düşüyor, sabit)
ve N gün sonrası için nokta tahminini verir.

**Neden ARIMA/Prophet değil de Doğrusal Regresyon?** Az veri noktasıyla
(özellikle ilk haftalarda) karmaşık modeller aşırı öğrenir (overfit) ve
güvenilmez tahmin üretir. Basit bir doğrusal trend, sınırlı veriyle bile
yorumlanabilir ve stabil kalır. 5'ten az veri noktası olan türler için
tahmin göstermek yerine açıkça "yetersiz veri" etiketi kullanılır — bu,
güvenilmez bir sayıyı güvenilirmiş gibi sunmamak için bilinçli bir tasarım
kararıdır. Haftalar boyunca veri biriktikçe, mevsimsellik yakalayan bir
modele (ör. Holt-Winters üstel düzeltme) geçilebilir.
        """,
        "forecast_live_no_data": "Trend modeli fit etmek için henüz yeterli canlı snapshot geçmişi yok. "
                                  "Bu bölüm birkaç günlük veri biriktikten sonra aktifleşir.",
        "forecast_horizon_label": "Tahmin ufku (gün)",
        "forecast_metric_label": "Tahmin edilecek metrik",
        "apple_header": "### Apple App Store canlı sıralaması (ikinci canlı sinyal)",
        "apple_intro": """
**Neden ikinci bir canlı kaynak?** Yukarıdaki Google Play izleme listesi
birkaç temsilci uygulamayı takip ediyor çünkü Google Play'de ücretsiz resmi
bir chart API'si yok. Apple ise tür başına **gerçek, sıralanmış** Top Free
Games chart'ını resmi, ücretsiz, anahtarsız bir feed ile yayınlıyor — bu bir
tahmin değil, gerçek pazar konumu. Bu bölüm bunu yukarıdaki Google Play
sinyalinden bağımsız olarak günlük takip eder.
        """,
        "apple_no_data": "Henüz Apple chart snapshot'ı yok. GitHub Actions workflow'u "
                          "`live_fetch_apple.py`'yi en az bir kez çalıştırınca dolar.",
        "apple_metric_avg_rank": "Ortalama sıra (düşük = daha popüler)",
        "apple_trend_title": "Zaman içinde tür bazlı ortalama Apple Top Free Games sırası",
        "apple_leaderboard_header": "#### Son gün — tür başına en iyi ortalama sıra",
        "apple_note": "1. sıra, o gün ABD App Store'da o türdeki en popüler uygulama demektir. "
                      "Düşen bir çizgi, türün chart'lardaki varlığının güçlendiği anlamına gelir.",
    },
}

# Column-header translations for dataframes shown to the user
COLUMN_LABELS = {
    "en": {
        "n": "n", "avg_rating": "Avg rating", "median_rating": "Median rating",
        "rating_std": "Rating std", "total_installs": "Total installs",
        "avg_installs": "Avg installs", "median_installs": "Median installs",
        "avg_reviews": "Avg reviews", "avg_size_mb": "Avg size (MB)",
        "paid_share": "Paid share", "avg_price": "Avg price",
        "App": "App", "Genre_Group": "Genre", "Rating_num": "Rating",
        "Installs_num": "Installs", "Reviews_num": "Reviews",
        "Popularity_Score": "Popularity score", "Size_MB": "Size (MB)",
        "Price_num": "Price", "Last_Updated_dt": "Last updated",
        "genre_1": "Genre 1", "genre_2": "Genre 2", "u_statistic": "U statistic",
        "p_raw": "p (raw)", "p_bonferroni": "p (Bonferroni)", "significant": "Significant",
        "avg_log_installs": "Avg log installs", "avg_log_reviews": "Avg log reviews",
        "avg_size": "Avg size", "cluster": "Cluster",
        "fetched_at": "Fetched at", "score": "Rating", "reviews": "Reviews",
        "installs": "Installs", "min_installs": "Installs (min)",
        "recent_update_share": "Recent update share", "momentum_label": "Momentum label",
        "genre": "Genre", "t_days": "Days", "slope_per_day": "Slope/day",
        "direction": "Direction", "forecast_value": "Forecast value",
        "r_squared": "R-squared", "n_points": "Data points",
        "rank": "Rank", "app_name": "App", "developer": "Developer",
        "avg_rank": "Avg rank", "country": "Country",
    },
    "tr": {
        "n": "n", "avg_rating": "Ortalama puan", "median_rating": "Medyan puan",
        "rating_std": "Puan std", "total_installs": "Toplam kurulum",
        "avg_installs": "Ortalama kurulum", "median_installs": "Medyan kurulum",
        "avg_reviews": "Ortalama yorum", "avg_size_mb": "Ortalama boyut (MB)",
        "paid_share": "Ücretli oran", "avg_price": "Ortalama fiyat",
        "App": "Uygulama", "Genre_Group": "Tür", "Rating_num": "Puan",
        "Installs_num": "Kurulum", "Reviews_num": "Yorum",
        "Popularity_Score": "Popülerlik skoru", "Size_MB": "Boyut (MB)",
        "Price_num": "Fiyat", "Last_Updated_dt": "Son güncelleme",
        "genre_1": "Tür 1", "genre_2": "Tür 2", "u_statistic": "U istatistiği",
        "p_raw": "p (ham)", "p_bonferroni": "p (Bonferroni)", "significant": "Anlamlı mı",
        "avg_log_installs": "Ort. log kurulum", "avg_log_reviews": "Ort. log yorum",
        "avg_size": "Ortalama boyut", "cluster": "Küme",
        "fetched_at": "Çekilme zamanı", "score": "Puan", "reviews": "Yorum",
        "installs": "Kurulum", "min_installs": "Kurulum (min)",
        "recent_update_share": "Güncel güncelleme oranı", "momentum_label": "Momentum etiketi",
        "genre": "Tür", "t_days": "Gün", "slope_per_day": "Eğim/gün",
        "direction": "Yön", "forecast_value": "Tahmin değeri",
        "r_squared": "R-kare", "n_points": "Veri noktası",
        "rank": "Sıra", "app_name": "Uygulama", "developer": "Geliştirici",
        "avg_rank": "Ort. sıra", "country": "Ülke",
    },
}


def get_translator(lang: str):
    def t(key: str, **kwargs) -> str:
        s = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
        return s.format(**kwargs) if kwargs else s
    return t


def translate_columns(df, lang: str):
    labels = COLUMN_LABELS.get(lang, COLUMN_LABELS["en"])
    return df.rename(columns=labels)


VALUE_LABELS = {
    "en": {
        "Other (n<10)": "Other (n<10)",
        "rising_proxy": "rising (proxy)", "stable_proxy": "stable (proxy)", "declining_proxy": "declining (proxy)",
        "rising": "rising", "declining": "declining", "stable": "stable", "insufficient_data": "insufficient data",
    },
    "tr": {
        "Other (n<10)": "Diğer (n<10)",
        "rising_proxy": "yükselen (proxy)", "stable_proxy": "sabit (proxy)", "declining_proxy": "düşüşte (proxy)",
        "rising": "yükseliyor", "declining": "düşüyor", "stable": "sabit", "insufficient_data": "yetersiz veri",
    },
}


def translate_values(df, lang: str, columns=None):
    """Translate cell VALUES (not column headers) for known categorical columns
    (genre labels, momentum/direction tags) so non-English UIs never leak raw
    English/Turkish-only strings. Unknown values pass through unchanged."""
    labels = VALUE_LABELS.get(lang, VALUE_LABELS["en"])
    df = df.copy()
    cols = columns or [c for c in df.columns if c in ("Genre_Group", "genre", "momentum_label", "direction")]
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(object).apply(lambda v: labels.get(str(v), v))
    return df
