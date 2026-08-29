<p align="center"><img src="assets/logo_icon_square.png" width="120" alt="MPGM logo"></p>
<h1 align="center">MPGM — Mobile Play Genre Metrics</h1>
<p align="center"><i>Which mobile game genre is winning right now — and which one is next?</i></p>

---

### What problem does this solve?

Anyone deciding where to invest time or money in the mobile games market —
which genre to build for, which genre is oversaturated, which one is quietly
climbing — usually answers that question by gut feeling or by skimming Top
Charts. MPGM answers it with data: a cleaned, statistically-tested dataset of
Google Play games, a free live-updating pipeline layered on top of it, and a
dashboard that speaks both English and Turkish.

### A five-minute tour

**Open the app and you land on Overview** — genre counts, total installs per
genre on a log scale, and a rating box-plot that shows not just averages but
the spread and outliers within each genre.

**Genre Comparison** turns that into a leaderboard: a full descriptive stats
table per genre, a composite popularity score (installs + reviews + rating,
weighted and z-scored), and a Spearman correlation heatmap so you can see —
for instance — that review volume and installs move almost in lockstep,
while price and installs move in opposite directions.

**Statistical Tests** is where MPGM stops being "just a chart tool." A
Shapiro-Wilk test confirms ratings aren't normally distributed, which is why
the app uses Kruskal-Wallis instead of ANOVA to test whether genres actually
differ in rating — and if they do, Mann-Whitney U tests with Bonferroni
correction tell you exactly *which* genre pairs differ.

**Clustering** groups the 16 genres into behavioral segments using K-Means,
picking the number of clusters with a Silhouette score instead of eyeballing
an elbow chart.

**Raw Data & Outliers** lets you find IQR-flagged outliers, filter the
cleaned dataset by genre, and export it as CSV.

**Live Monitoring** is the newest and most different tab: a genre momentum
proxy built from real update-recency data, plus a Linear Regression forecast
that projects each genre's trend forward once enough daily snapshots have
accumulated — fed by a GitHub Actions job that runs for free, every day,
with no server to maintain.

### Why these specific methods?

| Question | Method used | Why not the obvious alternative |
|---|---|---|
| Is the rating data normal? | Shapiro-Wilk | Needed to know which test family is valid at all |
| Do genres differ in rating? | Kruskal-Wallis H | ANOVA assumes normality; this data doesn't have it |
| Which genre pairs differ? | Mann-Whitney U + Bonferroni | Raw pairwise p-values inflate false positives without correction |
| How do variables relate? | Spearman correlation | Pearson assumes linearity; installs/reviews are heavily skewed |
| How do genres segment? | K-Means + Silhouette | Picks cluster count from data, not from a subjective elbow bend |
| What's next for a genre? | Linear Regression (OLS) | Stays honest with few data points; ARIMA/Prophet would overfit early on and pretend to know more than the data supports |

### The live data layer, in one paragraph

Google Play has no free, public, real-time API. So instead of pretending
otherwise, MPGM tracks a representative watchlist of well-known apps per
genre — the same logic a stock index uses to track a market without pricing
every single company — and a GitHub Actions cron job fetches their current
rating, review count, and install range once a day, appending it to a
growing time series. Genres with fewer than 5 collected data points are
explicitly labeled "insufficient data" in the forecast rather than shown a
confident-looking number that isn't earned yet.

### Try it locally

```bash
git clone <your-repo-url>
cd mobile_game_genres
./setup.sh && ./run.sh      # Windows: setup.bat && run.bat
```
Or, if you prefer `make`:
```bash
make install && make run
```
Or Docker:
```bash
make docker-build && make docker-run
```
The app opens at `http://localhost:8501`.

### Repository map

```
app.py                    the Streamlit UI — 6 tabs, English/Turkish
analysis.py                 every statistic, cluster, and forecast function
data_pipeline.py              raw CSV -> cleaned DataFrame
i18n.py                         EN/TR text + value translation layer
live_fetch.py                  daily live-data collector (run by GitHub Actions)
.github/workflows/                 daily_snapshot.yml — the free cron job
data/                                raw dataset + live snapshot time series
assets/                                logo, favicon
tests/test_smoke.py                     18 automated regression checks
pyproject.toml, requirements.txt          dependencies
setup.sh / .bat, run.sh / .bat              one-command install & launch
Makefile, Dockerfile                          packaging shortcuts
CHANGELOG.md, VERSION, LICENSE                  project history, MIT license
```

### Data provenance

Base dataset: **Google Play Store Apps Dataset**, originally published on
Kaggle by `lava18`, fetched from a GitHub mirror
(`sumitgirwal/google-play-store-data-analysis`) — ~10,841 scraped records
from around 2018, filtered down to ~913 cleaned GAME-category rows. This is
a snapshot, not a live feed: use it for *relative* genre comparison, not
today's absolute market size. The live layer (`data/snapshots.csv`) is what
brings the picture current, day by day.

### Before you trust a change

```bash
pytest -q
```
18 tests check the data pipeline's shape, every statistical function in both
languages, i18n key parity between English and Turkish, forecast behavior on
edge cases (empty or insufficient data), and a full end-to-end app run with
zero exceptions. This suite is what caught every bug listed in
`CHANGELOG.md` — run it after any change, before it reaches production.

### License

MIT — see `LICENSE`.
