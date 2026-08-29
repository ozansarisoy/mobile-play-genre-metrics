"""
Smoke / regression tests for MPG — Mobile Play Genre Metrics.
Run with: pytest -q   (or: make test)

These are not exhaustive statistical tests — they exist to catch the class of
bugs found during the packaging review (broken paths, missing i18n keys,
mismatched columns) automatically, before they reach a deployed app.
"""
import os
import sys

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
