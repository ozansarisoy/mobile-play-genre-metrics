# Changelog

All notable changes to this project are documented here.

## [1.4.4] — 2026-09-07
### Fixed
- **Nonsensical "closest match" in game search.** Searching a single letter like "S"
  returned "Rush" as the top result — not because it was relevant, but because it
  happened to be the *shortest* app name containing that letter. The old ranking
  sorted every substring match purely by name length, which has no real connection
  to relevance. Fixed the ranking to prioritize (1) exact match, (2) name starts with
  the query, (3) shortest length only as the final tiebreaker — so searching "clash"
  now correctly surfaces "Clash Royale" instead of an unrelated short name.
- Also added a minimum 2-character requirement before searching at all: a single
  letter matches hundreds of games by definition and can never produce a meaningful
  "closest match," so the app now asks for a more specific query instead of guessing.
- 2 new regression tests (ranking prioritizes a relevant prefix match; a 1-character
  query is rejected with a message rather than silently matched). Suite is now 41 tests.

## [1.4.3] — 2026-09-07
### Fixed
- **Confusing row numbers in every data table.** `st.dataframe()` shows pandas'
  internal row index by default, which is meaningless to a user — it's not a rank
  or an ID, just "which position this row happened to land at" after filtering or
  sorting, which is why it jumped around unpredictably (e.g. the outlier table
  showing rows numbered 1, 2, 8, 9, 55, 15, 7... instead of a clean sequence).
  Added `hide_index=True` to all 12 data tables across the app (genre stats,
  popularity leaderboard, post-hoc test results, clustering results, outliers,
  raw filtered data, momentum proxy, per-app snapshot history, forecast table,
  and both the Apple and Wikipedia leaderboards) so every table now shows only
  meaningful columns.

## [1.4.2] — 2026-09-07
### Changed
- **`build_pdf_report` no longer fails silently.** After the v1.4.1 font fix, a user
  still received a PDF with garbled Turkish characters (`■`), with no visible sign of
  why. The function was tested extensively in development (including from a different
  working directory, simulating deployment path differences) and worked correctly
  every time — meaning the most likely explanation was the fix not yet being live on
  the deployed app at the time that PDF was generated. Rather than leave this as a
  guess, `build_pdf_report` now returns `(pdf_bytes, font_ok)` instead of just bytes:
  if the bundled Unicode font can't be found or registered for any reason, `font_ok`
  is `False` and the app shows a visible warning explaining that the PDF may not
  render Turkish characters correctly — instead of silently producing the same
  confusing bug again with no explanation. New regression test mocks a missing font
  file and confirms this contract holds. Excel export is unaffected either way.

**If you still see `■` characters after updating to this version**, the warning
banner will now tell you definitively whether it's a font-loading problem — please
report back with that banner text so we can pin down the exact deployment issue
rather than guessing at fixes.

## [1.4.1] — 2026-09-07
### Fixed
- **Garbled Turkish characters in the PDF comparison report** (`■` in place of ş, ı,
  ğ, ü, ö, ç, İ, Ğ, Ş, Ö, Ç, Ü). Root cause: ReportLab's built-in fonts (Helvetica
  etc.) only cover Latin-1 and silently replace unsupported characters. Fixed by
  bundling a Unicode TTF font (DejaVu Sans, `assets/fonts/`) directly in the repo and
  registering it with ReportLab at PDF build time — bundled rather than relying on a
  system font, since Streamlit Cloud's server has no guarantee of any particular font
  being pre-installed. Verified by extracting the actual PDF text and confirming every
  Turkish character survives intact (new regression test).
- Confirmed the **Excel export was already correct** — `openpyxl` writes UTF-8
  natively, so no fix was needed there; verified with a round-trip read-back test.

### Added
- **Both-language export, regardless of current UI language.** Previously the
  Genre Comparison report only exported in whichever language the interface was
  currently set to. Since a report is often shared with someone who reads the other
  language, both Excel and PDF are now always offered in both English and Turkish —
  four download buttons total, with the current UI language shown first.
- 3 new automated tests: bundled-font presence, PDF Turkish-character round-trip via
  `pdfplumber` text extraction, and both-language narrative generation. Suite is now
  38 tests.

## [1.4.0] — 2026-09-06
### Added
- **AI Analysis Simulation** in Genre Comparison Mode — after picking two genres, the
  app now generates a multi-paragraph narrative report comparing them: per-metric
  leader and percentage gap, the precomputed Mann-Whitney U + Bonferroni significance
  test for that exact genre pair (reused from the Statistical Tests tab, not
  recalculated), and an overall verdict. Implemented as a deterministic, rule-based
  template generator (`ai_report.py`) rather than a live LLM API call — stated plainly
  in the UI as a "simulation," since a real API call would need a paid key and would
  break the project's fully-free architecture. Every number in the report is computed
  from the same cleaned dataset used everywhere else in the app.
- **Excel and PDF export** of the comparison report (same module) — one click each,
  via `openpyxl` and `reportlab`. The Excel file has a data sheet and a report-text
  sheet; the PDF renders the comparison table plus the full narrative with the app's
  brand colors.
- 6 new automated tests covering the resample-frequency fix, watchlist integrity, and
  the full AI report pipeline (metrics, bilingual narrative, Excel/PDF byte validity).
  Suite is now 35 tests.

### Fixed
- **Crash on "Monthly" or "Yearly" in Live Monitoring**: pandas removed the legacy `M`
  and `Y` resample frequency aliases in the version now installed (`pandas>=2.2`
  ships `ME`/`YE` instead), so clicking those two period options raised an unhandled
  `ValueError` and broke the tab. Fixed by updating `freq_map` to `ME`/`YE`. Verified
  with real accumulated live data across all four period options.
- **Invisible ("white-on-white") text** in the genre stats table's column menu, the
  clustering result table, and the CSV download button. Root cause: `theme.py`
  previously painted a blanket text color onto every bare `h1..h6, p, label, span,
  div, li, a` tag on the page. Several native Streamlit components — the dataframe
  column-header menu, buttons, and Plotly's fullscreen overlay — render as portals
  outside the normal app DOM subtree or already carry their own correct contrast
  internally; the blanket rule forced our color onto them too, producing invisible
  text on their own light background. Fixed by scoping all text-color rules to the
  `.stApp` container (letting normal inheritance handle real descendants) and by
  adding a proper Streamlit theme (`.streamlit/config.toml`) so dataframes, buttons,
  popovers, and the fullscreen frame render with Streamlit's own guaranteed-correct
  native contrast instead of fighting injected CSS. Stated trade-off: this config
  file is static and matches the app's default (dark) theme — switching the in-app
  toggle to Light still repaints the page shell and charts correctly, but these
  specific native components keep their dark styling underneath, since Streamlit
  doesn't support a user-facing, runtime-switchable native theme.
- **Broken layout when expanding the Spearman correlation heatmap to fullscreen** —
  same root cause as above (the blanket CSS rule reached into the fullscreen-cloned
  DOM subtree); fixed by the same theme.py rewrite.
- **Watchlist coverage**: `live_fetch.py`'s per-genre app list was thin (2–5 apps per
  genre). Expanded to 2–8 apps per genre (64 total, no duplicates) for broader,
  steadier daily coverage. New IDs are well-known public package names but were not
  live-verified from this development environment (no Google Play access here) —
  check the next Actions log for "HATA:" lines to confirm each resolves correctly.

## [1.3.0] — 2026-08-29
### Added
- **Wikipedia Pageviews integration** (`live_fetch_wikipedia.py`) — a third, independent
  live data signal: daily page-view counts for each genre's Wikipedia article, via
  Wikimedia's official, free, keyless REST API. Covers all 16 genres (each mapped to
  its general/overview Wikipedia article, not a single game, so the signal reflects
  genre-level interest). Runs daily in the same GitHub Actions job, with
  `continue-on-error: true` like the Apple fetcher — a failure here never blocks the
  Google Play or Apple snapshots from committing.
- New "Wikipedia interest" section in the Live Monitoring tab: a daily views-by-genre
  trend chart and a same-day leaderboard of most-viewed genre articles.
- **"Live data last updated" badge** under the app title — shows the newest timestamp
  across all three live sources (Google Play, Apple, Wikipedia) at a glance, or an
  honest "no live data yet" message before the first snapshot.
- **Genre Comparison Mode** (in the Genre Comparison tab) — pick any two genres and see
  a side-by-side table of rating, installs, reviews, size, and popularity score.
- **Find a Game search bar** (top of the Overview tab) — type any (partial) game name,
  see its core stats and its percentile rank within its own genre by popularity score.
- 6 new automated tests (Wikipedia genre-article validity, mocked-response parsing,
  empty-data handling, network-failure resilience, search bar exercised with a real
  query, genre comparison exercised with real selections). Suite is now 29 tests.

### Known limitation — please verify on first live run
- Same as the Apple integration: `live_fetch_wikipedia.py` was built and logic-tested
  against a **mocked** Wikimedia response; the sandbox it was built in cannot reach
  wikimedia.org. The endpoint is official, documented, and has been stable for years,
  but check the Actions log for "HATA:"/"UYARI:" lines after the first real run to
  confirm the genre article titles resolve correctly.

## [1.2.1] — 2026-08-29
### Changed
- Default language on first load is now **Turkish** (was English). Default theme on
  first load is now **Dark** (was Light). Both remain fully switchable at any time via
  the selectors — this only changes what a fresh session sees before the user picks
  anything. Verified across all 4 language x theme combinations with zero exceptions.

## [1.2.0] — 2026-08-29
### Added
- **Apple App Store live chart integration** (`live_fetch_apple.py`) — a second,
  independent live data signal alongside the existing Google Play watchlist. Fetches
  Apple's official, free, keyless Top Free Games chart per genre (real market rank,
  not a proxy) via `https://itunes.apple.com/{country}/rss/topfreeapplications/...`,
  covering 15 of the app's 16 genres (all except "Casual", which has no dedicated
  Apple chart genre ID — that genre keeps its existing Google Play coverage).
- New "Apple App Store live rank" section in the Live Monitoring tab: a genre-level
  average-rank trend chart (inverted y-axis so an upward-reading line means the genre
  is climbing) and a same-day leaderboard table of best average rank per genre.
- Runs daily in the same GitHub Actions job as the Google Play fetcher, with
  `continue-on-error: true` — if Apple's endpoint is ever unreachable on a given day,
  the Google Play snapshot still commits normally; nothing is lost.
- 4 new automated tests: genre ID table validity, JSON-parsing logic against a mocked
  Apple response, and a check that a network failure returns an empty list rather than
  raising. Suite is now 23 tests.
- Fully bilingual (EN/TR) like every other section of the app.

### Known limitation — please verify on first live run
- This integration was built and logic-tested with a **mocked** Apple response — the
  environment it was built in cannot reach `itunes.apple.com` to test the live
  endpoint. The endpoint is publicly documented and has been used by third parties for
  years, but its availability has occasionally been reported as flaky in Apple
  developer forums. The code is written defensively (a failure for one genre is
  logged and skipped, never crashes the run), so the worst case if the endpoint has
  changed shape is simply an empty `apple_snapshots.csv` — check the Actions log for
  "HATA:" lines after the first real run to confirm it's working as expected.

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
