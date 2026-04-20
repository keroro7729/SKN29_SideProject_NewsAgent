import streamlit as st
from constants import ARTICLES_PER_PAGE
from components.article_card import render_card
from components.filters import render_filters


def render(articles: list[dict], category: str) -> None:
    if not articles:
        st.markdown(f"""
        <div class="ni-empty">
            <div class="ni-empty-text">{category} 카테고리 기사가 없습니다.</div>
        </div>
        """, unsafe_allow_html=True)
        return
 
    # ── 필터 적용 ────────────────────────────────────────────────────────────
    filtered = render_filters(articles, key_prefix=category)

    if not filtered:
        st.info("필터 조건에 맞는 기사가 없습니다.")
        return

    # ── 페이지네이션: 현재 보여줄 개수만 슬라이싱 ─────────────────────────────
    count_key = f"visible_count_{category}"
    visible_count = st.session_state.get(count_key, ARTICLES_PER_PAGE)
    visible_count = min(visible_count, len(filtered))

    visible_articles = filtered[:visible_count]

    # ── 카드 목록 ─────────────────────────────────────────────────────────────
    for i, article in enumerate(visible_articles):
        render_card(article, i, category=category, key_prefix=category)

    # ── 더보기 버튼 ──────────────────────────────────────────────────────────
    remaining = len(filtered) - visible_count
    if remaining > 0:
        st.markdown('<div class="ni-load-more">', unsafe_allow_html=True)
        if st.button(
            f"기사 더보기  ({remaining}개 남음)  ∨",
            key=f"load_more_{category}",
            use_container_width=True,
        ):
            st.session_state[count_key] = visible_count + ARTICLES_PER_PAGE
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
