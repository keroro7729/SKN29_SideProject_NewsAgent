import streamlit as st
from constants import CATEGORIES, SENTIMENTS

_ALL = CATEGORIES[0]

def render_filters(articles: list[dict], key_prefix: str) -> list[dict]:
    """
    감성·언론사 필터 UI를 렌더링하고 필터링된 기사 리스트를 반환합니다.
    여러 탭에서 독립적으로 동작할 수 있도록 key_prefix를 필수로 받습니다.
    """
    with st.expander("🔧 필터 & 정렬", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<span class="filter-label">감성</span>', unsafe_allow_html=True)
            sentiment_filter = st.radio(
                label="감성 필터",
                options=[_ALL] + list(SENTIMENTS),
                horizontal=True,
                key=f"filter_sentiment_{key_prefix}",
                label_visibility="collapsed",
            )

        with col2:
            sources = sorted({a.get("source", "") for a in articles if a.get("source")})
            st.markdown('<span class="filter-label">언론사</span>', unsafe_allow_html=True)
            source_filter = st.selectbox(
                label="언론사",
                options=[_ALL] + sources,
                key=f"filter_source_{key_prefix}",
                label_visibility="collapsed",
            )

        with col3:
            st.markdown('<span class="filter-label">정렬</span>', unsafe_allow_html=True)
            sort_by = st.selectbox(
                label="정렬",
                options=["최신순", "조회수순"],
                key=f"filter_sort_{key_prefix}",
                label_visibility="collapsed",
            )

    # ── 필터 적용 ────────────────────────────────────────────────────────────
    filtered = articles[:]

    if sentiment_filter != _ALL:
        filtered = [a for a in filtered if a.get("sentiment") == sentiment_filter]

    if source_filter != _ALL:
        filtered = [a for a in filtered if a.get("source") == source_filter]

    if sort_by == "조회수순":
        filtered.sort(key=lambda x: x.get("views", 0), reverse=True)

    return filtered