from html import escape
import streamlit as st
from constants import CATEGORIES
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

    # ── 카드 목록 ─────────────────────────────────────────────────────────────
    for i, article in enumerate(filtered):
        category = article.get("category", _ALL)
        # 카드 렌더링 시에도 키 충돌 방지를 위해 tab_name 활용
        render_card(article, i, category=category, key_prefix=tab_name)