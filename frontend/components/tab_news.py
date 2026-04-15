import streamlit as st


# ── 감성 뱃지 HTML ──────────────────────────────────────────────────────────
_BADGE_CLASS = {
    "긍정": "ni-badge ni-badge-pos",
    "부정": "ni-badge ni-badge-neg",
    "중립": "ni-badge ni-badge-neu",
}


def _sentiment_badge(sentiment: str) -> str:
    cls = _BADGE_CLASS.get(sentiment, "ni-badge ni-badge-neu")
    return f'<span class="{cls}">{sentiment}</span>'


def _category_badge(category: str) -> str:
    return f'<span class="ni-badge ni-badge-cat">{category}</span>'


# ── 기사 카드 렌더링 ────────────────────────────────────────────────────────
def _render_card(article: dict, idx: int) -> None:
    """단일 기사 카드 + AI 요약 expander를 렌더링합니다."""
    sentiment = article.get("sentiment", "중립")
    category  = article.get("category", "전체")
    source    = article.get("source", "")
    date      = article.get("date", "")
    views     = article.get("views", 0)

    # ── 카드 본문 ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ni-card">
        <div class="ni-card-num">No.{idx+1:02d}</div>
        <div class="ni-card-title">{article['title']}</div>
        <div class="ni-card-desc">{article['desc']}</div>
        <div class="ni-card-footer">
            {_category_badge(category)}
            {_sentiment_badge(sentiment)}
            <span class="ni-source">{source}</span>
            <span class="ni-date">{date} &nbsp;·&nbsp; {views:,}회</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI 요약 expander ─────────────────────────────────────────────────────
    with st.expander("AI 요약 펼치기"):
        st.markdown(f"""
        <div class="ni-summary">
            <div class="ni-summary-label">📌 AI 3줄 요약</div>
            <div class="ni-summary-text">{article['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

        col_link, col_btn = st.columns([3, 1])
        with col_link:
            if article.get("link") and article["link"] != "#":
                st.markdown(f"[원문 보기 →]({article['link']})")
        with col_btn:
            if st.button("💬 채팅 분석", key=f"chatbtn_{idx}_{article.get('idx', idx)}"):
                st.session_state.selected_article = article
                st.success("AI 채팅 탭에서 이 기사에 대해 질문해보세요!")


# ── 필터 사이드바 ────────────────────────────────────────────────────────────
def _render_filters(articles: list[dict]) -> list[dict]:
    """
    감성·언론사 필터 UI를 렌더링하고 필터링된 기사 리스트를 반환합니다.

    Parameters
    ----------
    articles : 전체 기사 리스트

    Returns
    -------
    list[dict]  필터 적용 후 기사 리스트
    """
    with st.expander("🔧 필터 & 정렬", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<span class="filter-label">감성</span>', unsafe_allow_html=True)
            sentiment_filter = st.radio(
                label="감성 필터",
                options=["전체", "긍정", "부정", "중립"],
                horizontal=True,
                key="filter_sentiment",
                label_visibility="collapsed",
            )

        with col2:
            sources = sorted({a.get("source", "") for a in articles if a.get("source")})
            st.markdown('<span class="filter-label">언론사</span>', unsafe_allow_html=True)
            source_filter = st.selectbox(
                label="언론사",
                options=["전체"] + sources,
                key="filter_source",
                label_visibility="collapsed",
            )

        with col3:
            st.markdown('<span class="filter-label">정렬</span>', unsafe_allow_html=True)
            sort_by = st.selectbox(
                label="정렬",
                options=["최신순", "조회수순"],
                key="filter_sort",
                label_visibility="collapsed",
            )

    # ── 필터 적용 ────────────────────────────────────────────────────────────
    filtered = articles[:]

    if sentiment_filter != "전체":
        filtered = [a for a in filtered if a.get("sentiment") == sentiment_filter]

    if source_filter != "전체":
        filtered = [a for a in filtered if a.get("source") == source_filter]

    if sort_by == "조회수순":
        filtered.sort(key=lambda x: x.get("views", 0), reverse=True)

    return filtered


# ── 메인 렌더 함수 ───────────────────────────────────────────────────────────
def render(articles: list[dict]) -> None:
    if not articles:
        st.markdown("""
        <div class="ni-empty">
            <div class="ni-empty-icon">◈</div>
            <div class="ni-empty-text">
                검색 결과가 없습니다.<br>
                다른 검색어를 시도하거나 카테고리를 변경해보세요.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── 필터 ──────────────────────────────────────────────────────────────────
    filtered = _render_filters(articles)

    if not filtered:
        st.info("필터 조건에 맞는 기사가 없습니다.")
        return

    # ── 카드 목록 ─────────────────────────────────────────────────────────────
    for i, article in enumerate(filtered):
        _render_card(article, i)