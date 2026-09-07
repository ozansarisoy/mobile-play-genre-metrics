"""
Smoke / regression tests for MPG — Mobile Play Genre Metrics.
Run with: pytest -q   (or: make test)

These are not exhaustive statistical tests — they exist to catch the class of
bugs found during the packaging review (broken paths, missing i18n keys,
mismatched columns) automatically, before they reach a deployed app.
"""
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pytest

from data_pipeline import load_and_clean
from analysis import (
    normality_check, genre_descriptive_stats, kruskal_wallis_by_genre,
    dunn_posthoc, correlation_matrix, cluster_genres, iqr_outliers,
    popularity_score, genre_momentum_static, forecast_live_trend,
)
import i18n


@pytest.fixture(scope="module")
def df():
    return load_and_clean()


def test_load_and_clean_shape(df):
    assert len(df) > 500
    assert df["Genre_Group"].nunique() > 5
    assert not df["Rating_num"].isna().any()
    assert (df["Rating_num"] <= 5).all()


def test_load_and_clean_is_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    df2 = load_and_clean()
    assert len(df2) > 0


def test_genre_labels_are_english_by_default(df):
    # The auto-generated bucket must be English at the data layer;
    # translation happens only at display time via i18n.translate_values.
    labels = df["Genre_Group"].unique().tolist()
    assert "Diğer (n<10)" not in labels
    if any("n<10" in str(l) for l in labels):
        assert "Other (n<10)" in labels


def test_popularity_score(df):
    scores = popularity_score(df)
    assert len(scores) == len(df)
    assert scores.notna().sum() > 0


def test_genre_descriptive_stats(df):
    stats_df = genre_descriptive_stats(df)
    assert "avg_rating" in stats_df.columns
    assert "total_installs" in stats_df.columns
    assert len(stats_df) == df["Genre_Group"].nunique()


def test_normality_check(df):
    result = normality_check(df, "Rating_num")
    assert 0 <= result["p_value"] <= 1


def test_kruskal_wallis_bilingual(df):
    for lang in ("en", "tr"):
        result = kruskal_wallis_by_genre(df, lang=lang)
        assert "interpretation" in result
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 0


def test_dunn_posthoc(df):
    posthoc = dunn_posthoc(df)
    assert {"genre_1", "genre_2", "p_bonferroni", "significant"}.issubset(posthoc.columns)
    assert (posthoc["p_bonferroni"] <= 1.0).all()


def test_correlation_matrix_bilingual(df):
    for lang in ("en", "tr"):
        corr = correlation_matrix(df, lang=lang)
        assert corr.shape == (5, 5)


def test_cluster_genres(df):
    agg, diag, best_k = cluster_genres(df)
    assert "cluster" in agg.columns
    assert best_k >= 2
    assert diag["silhouette"].max() <= 1.0


def test_iqr_outliers(df):
    outliers = iqr_outliers(df, "Installs_num")
    assert len(outliers) < len(df)


def test_genre_momentum_static(df):
    momentum = genre_momentum_static(df)
    assert "recent_update_share" in momentum.columns
    assert momentum["recent_update_share"].between(0, 1).all()


def test_forecast_live_trend_empty_snapshots():
    empty = pd.DataFrame(columns=["fetched_at", "genre", "score"])
    empty["fetched_at"] = pd.to_datetime(empty["fetched_at"])
    result = forecast_live_trend(empty)
    assert len(result) == 0


def test_forecast_live_trend_insufficient_data():
    snaps = pd.DataFrame({
        "fetched_at": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        "genre": ["Action", "Action"],
        "score": [4.1, 4.2],
    })
    result = forecast_live_trend(snaps)
    assert (result["direction"] == "insufficient_data").all()


def test_i18n_key_parity():
    en_keys = set(i18n.TRANSLATIONS["en"].keys())
    tr_keys = set(i18n.TRANSLATIONS["tr"].keys())
    assert en_keys == tr_keys, f"Mismatched i18n keys: {en_keys ^ tr_keys}"


def test_i18n_column_label_parity():
    en_cols = set(i18n.COLUMN_LABELS["en"].keys())
    tr_cols = set(i18n.COLUMN_LABELS["tr"].keys())
    assert en_cols == tr_cols, f"Mismatched column label keys: {en_cols ^ tr_cols}"


def test_i18n_translate_values_roundtrip():
    df_test = pd.DataFrame({"Genre_Group": ["Other (n<10)", "Action"]})
    tr_out = i18n.translate_values(df_test, "tr", columns=["Genre_Group"])
    assert tr_out["Genre_Group"].iloc[0] == "Diğer (n<10)"
    en_out = i18n.translate_values(df_test, "en", columns=["Genre_Group"])
    assert en_out["Genre_Group"].iloc[0] == "Other (n<10)"


def test_app_runs_without_exceptions():
    """End-to-end smoke test using Streamlit's own AppTest harness."""
    from streamlit.testing.v1 import AppTest

    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
    at = AppTest.from_file(app_path)
    at.run(timeout=90)
    assert len(at.exception) == 0, f"App raised exceptions: {list(at.exception)}"

    at.session_state["lang"] = "tr"
    at.run(timeout=90)
    assert len(at.exception) == 0, f"App raised exceptions (tr): {list(at.exception)}"


def test_app_search_bar_finds_a_game():
    from streamlit.testing.v1 import AppTest

    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
    at = AppTest.from_file(app_path)
    at.run(timeout=90)
    at.text_input(key="game_search").set_value("a").run(timeout=90)
    assert len(at.exception) == 0, f"Search bar raised exceptions: {list(at.exception)}"


def test_app_genre_comparison_mode_works():
    from streamlit.testing.v1 import AppTest

    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
    at = AppTest.from_file(app_path)
    at.run(timeout=90)
    at.selectbox(key="cmp_a").set_value("Puzzle").run(timeout=90)
    at.selectbox(key="cmp_b").set_value("Action").run(timeout=90)
    assert len(at.exception) == 0, f"Genre comparison raised exceptions: {list(at.exception)}"


def test_app_runs_with_dark_theme():
    """The dark theme toggle must not break any chart or widget."""
    from streamlit.testing.v1 import AppTest

    app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
    at = AppTest.from_file(app_path)
    at.run(timeout=90)
    at.session_state["theme"] = "dark"
    at.run(timeout=90)
    assert len(at.exception) == 0, f"App raised exceptions (dark theme): {list(at.exception)}"


def test_plotly_template_mapping():
    from theme import plotly_template
    assert plotly_template("dark") == "plotly_dark"
    assert plotly_template("light") == "plotly_white"
    assert plotly_template("unknown") == "plotly_white"  # safe fallback


def test_apple_genre_ids_are_valid():
    from live_fetch_apple import GENRE_IDS
    assert len(GENRE_IDS) > 5
    assert all(isinstance(v, int) and v > 0 for v in GENRE_IDS.values())
    assert "Action" in GENRE_IDS and "Puzzle" in GENRE_IDS


def test_apple_fetch_genre_chart_parses_mock_response():
    import unittest.mock as mock
    import json as json_mod
    from live_fetch_apple import _fetch_genre_chart

    fake_response = {
        "feed": {
            "entry": [
                {
                    "im:name": {"label": "Mock Game"},
                    "im:artist": {"label": "Mock Studio"},
                    "id": {"attributes": {"im:id": "999"}},
                },
            ]
        }
    }

    class FakeResp:
        def __init__(self, data): self._data = json_mod.dumps(data).encode("utf-8")
        def read(self): return self._data
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with mock.patch("urllib.request.urlopen", return_value=FakeResp(fake_response)):
        rows = _fetch_genre_chart("Action", 7001, "2026-01-01T00:00:00+00:00")
    assert len(rows) == 1
    assert rows[0]["rank"] == 1
    assert rows[0]["app_name"] == "Mock Game"
    assert rows[0]["apple_app_id"] == "999"


def test_apple_fetch_genre_chart_never_raises_on_network_failure():
    import unittest.mock as mock
    from live_fetch_apple import _fetch_genre_chart

    with mock.patch("urllib.request.urlopen", side_effect=Exception("network down")):
        rows = _fetch_genre_chart("Action", 7001, "2026-01-01T00:00:00+00:00")
    assert rows == []


def test_wikipedia_genre_articles_are_valid():
    from live_fetch_wikipedia import GENRE_ARTICLES
    assert len(GENRE_ARTICLES) > 5
    assert all(isinstance(v, str) and len(v) > 0 for v in GENRE_ARTICLES.values())
    assert "Puzzle" in GENRE_ARTICLES


def test_wikipedia_fetch_parses_mock_response():
    import unittest.mock as mock
    import json as json_mod
    from live_fetch_wikipedia import _fetch_article_views

    fake_response = {"items": [{"views": 555}]}

    class FakeResp:
        def __init__(self, data): self._data = json_mod.dumps(data).encode("utf-8")
        def read(self): return self._data
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with mock.patch("urllib.request.urlopen", return_value=FakeResp(fake_response)):
        row = _fetch_article_views("Puzzle", "Puzzle_video_game", "20260101", "2026-01-01T00:00:00+00:00")
    assert row is not None
    assert row["views"] == 555
    assert row["genre"] == "Puzzle"


def test_wikipedia_fetch_handles_empty_items():
    import unittest.mock as mock
    import json as json_mod
    from live_fetch_wikipedia import _fetch_article_views

    class FakeResp:
        def __init__(self, data): self._data = json_mod.dumps(data).encode("utf-8")
        def read(self): return self._data
        def __enter__(self): return self
        def __exit__(self, *a): return False

    with mock.patch("urllib.request.urlopen", return_value=FakeResp({"items": []})):
        row = _fetch_article_views("Puzzle", "Puzzle_video_game", "20260101", "2026-01-01T00:00:00+00:00")
    assert row is None


def test_wikipedia_fetch_never_raises_on_network_failure():
    import unittest.mock as mock
    from live_fetch_wikipedia import _fetch_article_views

    with mock.patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        row = _fetch_article_views("Puzzle", "Puzzle_video_game", "20260101", "2026-01-01T00:00:00+00:00")
    assert row is None


def test_resample_frequency_aliases_are_valid_for_current_pandas():
    """Regression test for the v1.3.1 bug: 'M' and 'Y' resample aliases were
    removed in modern pandas, crashing the app when a user picked Monthly or
    Yearly in the Live Monitoring tab. Confirms the app's freq_map values
    ('D', 'W', 'ME', 'YE') all resample without raising."""
    snaps = pd.DataFrame({
        "fetched_at": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-02-01", "2027-01-01"]),
        "genre": ["Action"] * 4,
        "score": [4.1, 4.2, 4.3, 4.4],
    })
    for freq in ["D", "W", "ME", "YE"]:
        trend = snaps.set_index("fetched_at").groupby("genre")["score"].resample(freq).mean().reset_index()
        assert len(trend) > 0


def test_watchlist_has_no_duplicate_app_ids():
    from live_fetch import WATCHLIST
    all_ids = [app_id for ids in WATCHLIST.values() for app_id in ids]
    assert len(all_ids) == len(set(all_ids)), "Duplicate app IDs found across genres in WATCHLIST"
    assert len(all_ids) >= 40  # expanded watchlist should have meaningfully more coverage than before


def test_compute_comparison_metrics():
    from ai_report import compute_comparison_metrics
    df_a = pd.DataFrame({
        "Rating_num": [4.0, 4.5], "Installs_num": [1000, 2000], "Reviews_num": [10, 20],
        "Size_MB": [10.0, 20.0], "Price_num": [0.0, 0.0], "Popularity_Score": [0.1, 0.2],
    })
    df_b = df_a.copy()
    result = compute_comparison_metrics(df_a, df_b)
    assert result["a"]["n"] == 2
    assert result["a"]["avg_rating"] == pytest.approx(4.25)


def test_generate_comparison_narrative_bilingual():
    from ai_report import compute_comparison_metrics, generate_comparison_narrative
    df_a = pd.DataFrame({
        "Rating_num": [4.0, 4.5], "Installs_num": [1000, 2000], "Reviews_num": [10, 20],
        "Size_MB": [10.0, 20.0], "Price_num": [0.0, 0.0], "Popularity_Score": [0.1, 0.2],
    })
    df_b = pd.DataFrame({
        "Rating_num": [3.0, 3.5], "Installs_num": [500, 800], "Reviews_num": [5, 8],
        "Size_MB": [15.0, 25.0], "Price_num": [0.0, 0.0], "Popularity_Score": [-0.1, -0.2],
    })
    metrics = compute_comparison_metrics(df_a, df_b)
    for lang in ("en", "tr"):
        narrative = generate_comparison_narrative("A", "B", "A", "B", metrics, None, lang=lang)
        assert isinstance(narrative, str) and len(narrative) > 100
        assert "simulation" in narrative.lower() or "simülasyon" in narrative.lower()


def test_build_excel_report_produces_valid_bytes():
    from ai_report import build_excel_report
    table = pd.DataFrame({"Metric": ["Rating"], "A": ["4.2"], "B": ["4.5"]})
    result = build_excel_report("A", "B", table, "## Test narrative\n- point one", lang="en")
    assert isinstance(result, bytes) and len(result) > 100
    assert result[:2] == b"PK"  # xlsx is a zip archive


def test_build_pdf_report_produces_valid_bytes():
    from ai_report import build_pdf_report
    table = pd.DataFrame({"Metric": ["Rating"], "A": ["4.2"], "B": ["4.5"]})
    result, font_ok = build_pdf_report("A", "B", table, "## Test narrative\n- point one\n*disclaimer*", lang="en")
    assert isinstance(result, bytes) and len(result) > 100
    assert result[:5] == b"%PDF-"
    assert font_ok is True, "Bundled Unicode font failed to load in this test environment"


def test_pdf_report_bundled_font_exists():
    """The PDF Turkish-character fix depends on a bundled TTF font shipping
    with the repo (Streamlit Cloud's server has no guaranteed system fonts)."""
    font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "assets", "fonts")
    assert os.path.exists(os.path.join(font_dir, "DejaVuSans.ttf"))
    assert os.path.exists(os.path.join(font_dir, "DejaVuSans-Bold.ttf"))


def test_pdf_report_renders_turkish_characters_correctly():
    """Regression test for the v1.4.1 bug: Turkish characters (ş, ı, ğ, ü,
    ö, ç, İ) rendered as '■' in the PDF export because ReportLab's default
    Helvetica font only covers Latin-1. Extracts the actual PDF text and
    checks the Turkish characters survive intact."""
    import pdfplumber
    from ai_report import build_pdf_report

    table = pd.DataFrame({"Metrik": ["Puan"], "A": ["4.2"], "B": ["4.5"]})
    narrative = "Türkçe karakter testi: şımärşĞÜÖÇİ öğüşçı — Karşılaştırma sonuçları"
    pdf_bytes, font_ok = build_pdf_report("A", "B", table, narrative, lang="tr")
    assert font_ok is True, "Bundled Unicode font failed to load — this test env lacks assets/fonts/"

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = pdf.pages[0].extract_text()

    assert "■" not in text, "PDF still contains the mojibake replacement character"
    for ch in "şığüöçİĞÜÖÇ":
        assert ch in text, f"Turkish character '{ch}' did not survive PDF export"


def test_ai_report_provides_both_languages_regardless_of_ui_language():
    """The app must always offer both EN and TR exports, not just whatever
    language the interface is currently set to."""
    from ai_report import compute_comparison_metrics, generate_comparison_narrative

    df_a = pd.DataFrame({
        "Rating_num": [4.0], "Installs_num": [1000], "Reviews_num": [10],
        "Size_MB": [10.0], "Price_num": [0.0], "Popularity_Score": [0.1],
    })
    df_b = df_a.copy()
    metrics = compute_comparison_metrics(df_a, df_b)
    en_report = generate_comparison_narrative("A", "B", "A", "B", metrics, None, lang="en")
    tr_report = generate_comparison_narrative("A", "B", "A", "B", metrics, None, lang="tr")
    assert en_report != tr_report
    assert "simulation" in en_report.lower()
    assert "simülasyon" in tr_report.lower()


def test_build_pdf_report_reports_font_failure_instead_of_failing_silently():
    """Regression test for the exact bug reported after v1.4.1: the PDF font
    fix worked locally but a user still got garbled '■' characters, with no
    way to tell why. This confirms build_pdf_report NEVER silently succeeds
    with the wrong font — if the bundled font can't be found, font_ok must
    be False so the caller (app.py) can show a visible warning instead of
    producing a mojibake PDF with no explanation."""
    import unittest.mock as mock
    from ai_report import build_pdf_report

    table = pd.DataFrame({"Metrik": ["Puan"], "A": ["4.2"], "B": ["4.5"]})
    with mock.patch("os.path.isfile", return_value=False):
        pdf_bytes, font_ok = build_pdf_report("A", "B", table, "Test", lang="tr")
    assert font_ok is False
    assert isinstance(pdf_bytes, bytes) and pdf_bytes[:5] == b"%PDF-"  # still produces *a* PDF, just flagged
