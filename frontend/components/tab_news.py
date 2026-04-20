from html import escape
import streamlit as st
from constants import CATEGORIES, ARTICLES_PER_PAGE
from components.article_card import render_card
from components.filters import render_filters

# ── 필터용 상수 ─────────────────────────────────────────────────────────────
_ALL = CATEGORIES[0]          # "전체"

# ── 메인 렌더 함수 ───────────────────────────────────────────────────────────
def render(articles: list[dict], tab_name: str = "전체") -> None:
    if not articles:
        # 현재 검색어를 직접 드러내서 사용자가 원인을 바로 파악할 수 있게 함
        query = st.session_state.get("query", "")
        if query:
            msg = ( 
                f"<strong>'{escape(query)}'</strong> 에 대한 검색 결과가 없습니다.<br>"
                "다른 키워드를 시도하거나 카테고리를 변경해보세요."
            )
        else:
            msg = (
                "검색 결과가 없습니다.<br>"
                "다른 검색어를 시도하거나 카테고리를 변경해보세요."
            )
        st.markdown(f"""
        <div class="ni-empty">
            <div class="ni-empty-icon">◈</div>
            <div class="ni-empty-text">
                {msg}
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── 필터 ──────────────────────────────────────────────────────────────────
    # 탭별로 위젯 키 충돌을 막기 위해 tab_name을 key_prefix로 넘겨줍니다.
    filtered = render_filters(articles, key_prefix=tab_name)

    if not filtered:
        st.info("필터 조건에 맞는 기사가 없습니다.")
        return

    # ── 페이지네이션: 현재 보여줄 개수만 슬라이싱 ─────────────────────────────
    count_key = f"visible_count_{tab_name}"
    visible_count = st.session_state.get(count_key, ARTICLES_PER_PAGE)
    # 전체 필터 결과 개수보다 더 크면 안 됨
    visible_count = min(visible_count, len(filtered))

    visible_articles = filtered[:visible_count]

    # ── 카드 목록 ─────────────────────────────────────────────────────────────
    for i, article in enumerate(visible_articles):
        category = article.get("category", _ALL)
        # 카드 렌더링 시에도 키 충돌 방지를 위해 tab_name 활용
        render_card(article, i, category=category, key_prefix=tab_name)

    # ── 더보기 버튼 ──────────────────────────────────────────────────────────
    remaining = len(filtered) - visible_count
    if remaining > 0:
        st.markdown('<div class="ni-load-more">', unsafe_allow_html=True)
        if st.button(
            f"기사 더보기  ({remaining}개 남음)  ∨",
            key=f"load_more_{tab_name}",
            use_container_width=True,
        ):
            st.session_state[count_key] = visible_count + ARTICLES_PER_PAGE
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
