import streamlit as st
from html import escape
from constants import CATEGORIES


# ── 감성 뱃지 HTML ──────────────────────────────────────────────────────────
_BADGE_CLASS = {
    "긍정": "ni-badge ni-badge-pos",
    "부정": "ni-badge ni-badge-neg",
    "중립": "ni-badge ni-badge-neu",
}


def _sentiment_badge(sentiment: str) -> str:
    cls = _BADGE_CLASS.get(sentiment, "ni-badge ni-badge-neu")
    return f'<span class="{cls}">{escape(sentiment)}</span>'


def _category_badge(category: str) -> str:
    return f'<span class="ni-badge ni-badge-cat">{escape(category)}</span>'


# ── 공용 카드 렌더 함수 ─────────────────────────────────────────────────────
def render_card(article: dict, idx: int, category: str, key_prefix: str) -> None:
    """
    단일 기사 카드 + AI 요약 expander를 렌더링합니다.

    Parameters
    ----------
    article    : 기사 dict (title, desc, summary, sentiment, source, date, views, link)
    idx        : 기사 인덱스 (번호 표시 + 위젯 key 용)
    category   : 카테고리 이름 (뱃지 표시용)
    key_prefix : Streamlit 위젯 key 충돌 방지용 접두사 (예: "전체", "사회" 등)
    """
    sentiment = article.get("sentiment", "중립")
    source    = article.get("source", "")
    date      = article.get("date", "")
    views     = article.get("views", 0)

    # ── 카드 본문 ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ni-card">
        <div class="ni-card-num">No.{idx+1:02d}</div>
        <div class="ni-card-title">{escape(article.get('title', ''))}</div>
        <div class="ni-card-desc">{escape(article.get('desc', ''))}</div>
        <div class="ni-card-footer">
            {_category_badge(category)}
            {_sentiment_badge(sentiment)}
            <span class="ni-source">{escape(source)}</span>
            <span class="ni-date">{escape(date)} &nbsp;·&nbsp; {views:,}회</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI 요약 expander ─────────────────────────────────────────────────────
    with st.expander("AI 요약 펼치기"):
        st.markdown(f"""
        <div class="ni-summary">
            <div class="ni-summary-label">📌 AI 3줄 요약</div>
            <div class="ni-summary-text">{escape(article.get('summary', ''))}</div>
        </div>
        """, unsafe_allow_html=True)

        col_link, col_btn = st.columns([3, 1])
        with col_link:
            link = article.get("link", "")
            if link and link != "#":
                st.markdown(f"[원문 보기 →]({link})")
        with col_btn:
            if st.button("💬 채팅 분석", key=f"{key_prefix}_chat_{idx}"):
                st.session_state.selected_article = article
                st.success("AI 채팅 탭에서 이 기사에 대해 질문해보세요!")
