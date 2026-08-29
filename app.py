import streamlit as st
import pandas as pd
import plotly.express as px
import os

from data_pipeline import load_and_clean
from analysis import (
    normality_check, genre_descriptive_stats, kruskal_wallis_by_genre,
    dunn_posthoc, correlation_matrix, cluster_genres, iqr_outliers, popularity_score,
    genre_momentum_static, forecast_live_trend,
)
from i18n import get_translator, translate_columns, translate_values

APP_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="Mobile Play Genre Metrics (MPGM)", layout="wide",
                    page_icon=os.path.join(APP_DIR, "assets", "favicon.png"))

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

lang_col, _ = st.columns([1, 5])
with lang_col:
    choice = st.selectbox(
        "Language / Dil", options=["English", "Türkçe"],
        index=0 if st.session_state["lang"] == "en" else 1,
        label_visibility="collapsed",
    )
st.session_state["lang"] = "en" if choice == "English" else "tr"
lang = st.session_state["lang"]
t = get_translator(lang)

logo_col, title_col = st.columns([1, 8])
with logo_col:
    st.image(os.path.join(APP_DIR, "assets", "logo_icon_square.png"), width=88)

@st.cache_data
def get_data():
    df = load_and_clean()
    df["Popularity_Score"] = popularity_score(df)
    return df

df = get_data()

with title_col:
    st.title(t("app_title"))
    st.caption(t("app_caption", n=len(df), g=df["Genre_Group"].nunique()))

with st.expander(t("methodology_expander"), expanded=False):
    st.markdown(t("methodology_md"))

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    t("tab_overview"), t("tab_genre_compare"), t("tab_stats"),
    t("tab_cluster"), t("tab_raw"), t("tab_live"),
])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("metric_total_games"), f"{len(df):,}")
    c2.metric(t("metric_n_genres"), df["Genre_Group"].nunique())
    c3.metric(t("metric_avg_rating"), f"{df['Rating_num'].mean():.2f} / 5")
    c4.metric(t("metric_median_installs"), f"{df['Installs_num'].median():,.0f}")

    colA, colB = st.columns(2)
    with colA:
        genre_counts = df["Genre_Group"].value_counts().reset_index()
        genre_counts.columns = ["Genre_Group", "count"]
        genre_counts = translate_values(genre_counts, lang, columns=["Genre_Group"])
        fig = px.bar(genre_counts, x="count", y="Genre_Group", orientation="h",
                      title=t("chart_games_per_genre"))
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, yaxis_title="", xaxis_title="")
        st.plotly_chart(fig, width='stretch')

    with colB:
        installs_by_genre = df.groupby("Genre_Group")["Installs_num"].sum().sort_values(ascending=False).reset_index()
        installs_by_genre = translate_values(installs_by_genre, lang, columns=["Genre_Group"])
        fig2 = px.bar(installs_by_genre, x="Installs_num", y="Genre_Group", orientation="h",
                       title=t("chart_installs_per_genre"), log_x=True)
        fig2.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title=t("x_total_installs_log"), yaxis_title="")
        st.plotly_chart(fig2, width='stretch')

    st.markdown(f"#### {t('chart_rating_boxplot')}")
    box_df = translate_values(df[["Genre_Group", "Rating_num"]], lang, columns=["Genre_Group"])
    fig3 = px.box(box_df, x="Genre_Group", y="Rating_num", points="outliers", title=t("chart_rating_boxplot"))
    fig3.update_layout(xaxis_tickangle=-40, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig3, width='stretch')
    st.markdown(t("boxplot_note"))

with tab2:
    st.markdown(t("genre_stats_header"))
    stats_df = genre_descriptive_stats(df)
    st.dataframe(translate_columns(translate_values(stats_df.reset_index(), lang), lang), width='stretch')
    st.markdown(t("genre_stats_note"))

    st.markdown(t("popularity_header"))
    st.caption(t("popularity_caption"))
    top_n = st.slider(t("slider_top_n"), 5, 30, 15)
    top_games = df.nlargest(top_n, "Popularity_Score")[
        ["App", "Genre_Group", "Rating_num", "Installs_num", "Reviews_num", "Popularity_Score"]
    ].round(2)
    st.dataframe(translate_columns(translate_values(top_games, lang), lang), width='stretch')

    st.markdown(t("corr_header"))
    corr = correlation_matrix(df, lang=lang)
    fig4 = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, title=t("corr_title"))
    st.plotly_chart(fig4, width='stretch')
    st.markdown(t("corr_note"))

with tab3:
    st.markdown(t("normality_header"))
    norm_result = normality_check(df, "Rating_num")
    st.write(f"{'İstatistik' if lang=='tr' else 'Statistic'} = {norm_result['statistic']:.4f}, "
             f"{'p-değeri' if lang=='tr' else 'p-value'} = {norm_result['p_value']:.2e}")
    if not norm_result["normal_mi"]:
        st.warning(t("normality_warning"))
    else:
        st.success(t("normality_success"))

    st.markdown(t("kw_header"))
    st.caption(t("kw_caption"))
    kw = kruskal_wallis_by_genre(df, lang=lang)
    colk1, colk2 = st.columns(2)
    colk1.metric(t("kw_h_stat"), f"{kw['H_stat']:.2f}")
    colk2.metric(t("kw_p_value"), f"{kw['p_value']:.2e}")
    st.info(kw["interpretation"])

    if kw["significant_0.05"]:
        st.markdown(t("posthoc_header"))
        st.caption(t("posthoc_caption"))
        posthoc = dunn_posthoc(df)
        sig_only = st.checkbox(t("posthoc_checkbox"), value=True)
        display_df = posthoc[posthoc["significant"]] if sig_only else posthoc
        st.dataframe(translate_columns(display_df.round(4), lang), width='stretch', height=350)

    st.markdown(t("price_header"))
    ucretli = df.loc[df["Price_num"] > 0, "Rating_num"].dropna()
    ucretsiz = df.loc[df["Price_num"] == 0, "Rating_num"].dropna()
    from scipy import stats as sstats
    u_stat, p_val = sstats.mannwhitneyu(ucretli, ucretsiz, alternative="two-sided")
    st.write(t("price_summary", p=ucretli.mean(), pn=len(ucretli), f=ucretsiz.mean(), fn=len(ucretsiz)))
    st.write(f"Mann-Whitney U = {u_stat:.1f}, p = {p_val:.4f}")
    st.info(t("price_sig") if p_val < 0.05 else t("price_nosig"))

with tab4:
    st.markdown(t("cluster_header"))
    st.markdown(t("cluster_intro"))

    agg, diag, best_k = cluster_genres(df)

    colc1, colc2 = st.columns([1, 1])
    with colc1:
        fig5 = px.line(diag, x="k", y="silhouette", markers=True, title=t("silhouette_title", k=best_k))
        fig5.add_vline(x=best_k, line_dash="dash", line_color="red")
        st.plotly_chart(fig5, width='stretch')
    with colc2:
        fig6 = px.line(diag, x="k", y="inertia", markers=True, title=t("elbow_title"))
        st.plotly_chart(fig6, width='stretch')

    st.markdown(t("cluster_result_header", k=best_k))
    st.dataframe(translate_columns(translate_values(agg.reset_index(), lang), lang), width='stretch')

    cluster_scatter_df = translate_values(agg.reset_index(), lang)
    fig7 = px.scatter(
        cluster_scatter_df, x="avg_log_installs", y="avg_rating",
        color=agg["cluster"].astype(str), size="avg_size",
        hover_name="Genre_Group", title=t("cluster_scatter_title"),
        labels={"avg_log_installs": t("cluster_x"), "avg_rating": t("cluster_y"), "color": t("cluster_color")},
    )
    st.plotly_chart(fig7, width='stretch')

with tab5:
    st.markdown(t("outlier_header"))
    st.caption(t("outlier_caption"))
    outlier_col = st.selectbox(t("outlier_select"), ["Installs_num", "Reviews_num", "Size_MB", "Rating_num"])
    outliers = iqr_outliers(df, outlier_col)
    st.write(t("outlier_found", n=len(outliers), pct=len(outliers) / len(df) * 100))
    st.dataframe(
        translate_columns(translate_values(
            outliers[["App", "Genre_Group", outlier_col]].sort_values(outlier_col, ascending=False), lang), lang),
        width='stretch', height=300,
    )

    st.markdown(t("raw_header"))
    from i18n import VALUE_LABELS
    _genre_opts = sorted(df["Genre_Group"].unique())
    genre_filter = st.multiselect(
        t("raw_filter"), _genre_opts,
        format_func=lambda v: VALUE_LABELS.get(lang, VALUE_LABELS["en"]).get(v, v),
    )
    filtered = df[df["Genre_Group"].isin(genre_filter)] if genre_filter else df
    st.dataframe(
        translate_columns(translate_values(filtered[["App", "Genre_Group", "Rating_num", "Installs_num", "Reviews_num",
                                     "Size_MB", "Price_num", "Last_Updated_dt"]], lang), lang),
        width='stretch', height=400,
    )
    st.download_button(t("download_button"), filtered.to_csv(index=False).encode("utf-8"),
                        "mobile_games_clean_data.csv", "text/csv")

with tab6:
    st.markdown(t("live_header"))
    st.markdown(t("live_intro"))

    st.markdown(t("forecast_header"))
    st.markdown(t("forecast_static_sub"))
    st.markdown(t("forecast_static_note"))
    momentum = genre_momentum_static(df)
    st.dataframe(translate_columns(translate_values(momentum.reset_index(), lang), lang), width='stretch')

    st.markdown(t("forecast_live_sub"))
    st.markdown(t("forecast_live_note"))

    snap_path = os.path.join(APP_DIR, "data", "snapshots.csv")
    try:
        snaps = pd.read_csv(snap_path, parse_dates=["fetched_at"])
    except Exception:
        snaps = pd.DataFrame()

    if snaps.empty or len(snaps) < 1 or snaps["fetched_at"].isna().all():
        st.warning(t("live_no_data"))
        st.info(t("forecast_live_no_data"))
    else:
        snaps["fetched_date"] = snaps["fetched_at"].dt.date
        n_days = snaps["fetched_date"].nunique()
        c1, c2, c3 = st.columns(3)
        c1.metric(t("live_metric_days"), n_days)
        c2.metric(t("live_metric_apps"), snaps["app_id"].nunique())
        c3.metric(t("live_metric_last"), str(snaps["fetched_at"].max()))

        period_options = [t("live_period_daily"), t("live_period_weekly"), t("live_period_monthly"), t("live_period_yearly")]
        period = st.radio(t("live_period"), period_options, horizontal=True)
        freq_map = {
            t("live_period_daily"): "D", t("live_period_weekly"): "W",
            t("live_period_monthly"): "M", t("live_period_yearly"): "Y",
        }
        metric_options = {
            t("live_metric_score"): "score", t("live_metric_reviews"): "reviews",
            t("live_metric_installs"): "min_installs",
        }
        metric_label = st.selectbox(t("live_metric_select"), list(metric_options.keys()))
        metric = metric_options[metric_label]

        trend = (
            snaps.set_index("fetched_at")
            .groupby("genre")[metric]
            .resample(freq_map[period])
            .mean()
            .reset_index()
        )
        trend = translate_values(trend, lang, columns=["genre"])
        if trend[metric].notna().sum() > 0:
            fig8 = px.line(trend, x="fetched_at", y=metric, color="genre", markers=True,
                            title=t("live_trend_title", period=period, metric=metric_label))
            st.plotly_chart(fig8, width='stretch')
        else:
            st.info(t("live_not_enough"))

        st.markdown(t("live_app_history_header"))
        app_choice = st.selectbox(t("live_app_select"), sorted(snaps["title"].dropna().unique()))
        app_hist = snaps[snaps["title"] == app_choice].sort_values("fetched_at")
        st.dataframe(translate_columns(app_hist[["fetched_at", "score", "reviews", "installs", "min_installs"]], lang),
                     width='stretch')

        horizon = st.slider(t("forecast_horizon_label"), 7, 180, 30)
        forecast_metric_label = st.selectbox(
            t("forecast_metric_label"), list(metric_options.keys()), key="forecast_metric"
        )
        forecast_df = forecast_live_trend(snaps, metric=metric_options[forecast_metric_label], horizon_days=horizon)
        forecast_df = translate_values(forecast_df, lang, columns=["genre", "direction"])
        st.dataframe(translate_columns(forecast_df.round(4), lang), width='stretch')

st.markdown("---")
st.caption(t("footer"))
