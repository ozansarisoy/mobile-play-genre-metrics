# Changelog

All notable changes to this project are documented here.

## [1.1.1] — 2026-08-29
### Fixed
- Light theme showed a broken, mismatched look: selectbox dropdowns and Plotly chart
  backgrounds stayed dark even when "Light"/"Açık" was selected, with faded/washed-out
  text. Root cause: the browser applies native dark styling to form controls based on
  the page's `color-scheme` CSS property, which Streamlit sets from the OS/browser
  preference by default — our own CSS painted the page background light but never told
  the browser to also treat native controls (dropdowns, popovers) as light. Fixed by
  explicitly setting `color-scheme: light` / `color-scheme: dark` on `<html>` per the
  selected theme, and widened CSS coverage to selectbox/dropdown internals, dataframe
  containers, and the Plotly chart wrapper background so every surface — not just the
  page shell — follows the chosen theme consistently.
- Verified across all 4 language x theme combinations with zero exceptions; 20/20 tests pass.

## [1.1.0] — 2026-08-29
### Added
- Light/Dark theme toggle (`theme.py`), placed next to the language selector. Own
  session-controlled toggle rather than relying on Streamlit's native (Python-unreadable)
  theme switch, so it can also drive the Plotly chart template — all 8 charts in the app
  now render in `plotly_white` or `plotly_dark` to match the selected theme.
- 2 new automated tests (`test_app_runs_with_dark_theme`, `test_plotly_template_mapping`);
  suite is now 20 tests, all passing across every language x theme combination.

### Known trade-off
- The custom CSS is injected at runtime from within the app, not via
  `.streamlit/config.toml` (which is static and can't offer a user-facing toggle). This
  means there can be a brief flash of the default Streamlit chrome color on first paint
  before the CSS applies; it does not recur on reruns within the same session.

## [1.0.0] — 2026-08-20
### Added
- Initial data science pipeline on the Google Play Store Apps dataset (GAME category).
- Descriptive statistics, Kruskal-Wallis + Mann-Whitney/Bonferroni post-hoc tests, Spearman correlation.
- K-Means genre clustering with Silhouette-based k selection.
- Composite popularity score and IQR-based outlier detection.
- Live daily data collection via GitHub Actions + `google-play-scraper` (`live_fetch.py`).
- Daily / weekly / monthly / yearly trend view in the "Live Monitoring" tab.
- Genre momentum proxy (static, update-recency based) and Linear Regression trend forecast (live data based).
- Full English/Turkish bilingual UI (English shown by default).
- Project branding: name "Mobile Play Genre Metrics (MPGM)" and logo.

### Fixed (packaging pass)
- `data_pipeline.py` and `app.py` used working-directory-relative paths (`data/...`) that broke when the
  app was launched from anywhere other than the project root. Now resolved relative to the file's own
  location (`os.path.dirname(__file__)`), so the app runs correctly regardless of the current working
  directory or how it's packaged/installed.
- The auto-generated "small genre" bucket was hardcoded in Turkish (`"Diğer (n<10)"`) even when the UI
  language was English. The underlying data label is now English (`"Other (n<10)"`), with a value-level
  translation layer (`i18n.translate_values`) applied everywhere it's displayed so it correctly reads
  "Other (n<10)" in English and "Diğer (n<10)" in Turkish.
- Momentum labels (`rising_proxy` / `stable_proxy` / `declining_proxy`) and forecast direction labels
  (`rising` / `declining` / `stable` / `insufficient_data`) were shown as raw internal strings regardless
  of language. Now translated via the same value-translation layer.
- Inconsistent column naming: the popularity score column was named `Populerlik_Skoru` (Turkish) inside an
  otherwise English-first codebase. Renamed to `Popularity_Score` for internal consistency; display-layer
  translation still shows the correct localized label.
- Two Streamlit widgets on the Live Monitoring tab shared the exact same "Metric" label, which was
  confusing since they controlled two different things (the trend chart vs. the forecast). The forecast
  selector now has its own distinct label ("Metric to forecast" / "Tahmin edilecek metrik").
- `live_fetch.py`'s watchlist listed `com.miHoYo.GenshinImpact` under both "Action" and "Role Playing",
  which would double-count that app's snapshots and mix its trend into two genres. Removed the duplicate.
- Replaced the deprecated Streamlit `use_container_width=True` argument (17 occurrences) with the current
  `width='stretch'` API ahead of its removal.
- Verified via `streamlit.testing.v1.AppTest` that the app runs with zero exceptions in both English and
  Turkish, from any working directory.

### Packaging
- Added `pyproject.toml`, `VERSION`, `CHANGELOG.md`, `.gitignore`, `LICENSE`.
- Added `setup.sh` / `setup.bat` (one-command virtual-env + dependency install) and `run.sh` / `run.bat`
  (launch the app).
- Added `Makefile` with `install`, `run`, `test`, `docker-build`, `docker-run` targets.
- Added `Dockerfile` + `.dockerignore` for containerized deployment.
- Added `tests/test_smoke.py` — automated regression checks for the data pipeline, statistical functions,
  and i18n key/column-label completeness (run with `pytest` or `make test`).
