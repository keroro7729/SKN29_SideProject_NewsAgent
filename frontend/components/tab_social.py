import streamlit as st


_BADGE_CLASS = {
    "긍정": "ni-badge ni-badge-pos",
    "부정": "ni-badge ni-badge-neg",
    "중립": "ni-badge ni-badge-neu",
}


def render(articles: list[dict]) -> None:
    if not articles:
        st.markdown("""
        <div class="ni-empty">
            <div class="ni-empty-text">사회 카테고리 기사가 없습니다.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, article in enumerate(articles):
        sentiment = article.get("sentiment", "중립")
        badge_cls = _BADGE_CLASS.get(sentiment, "ni-badge ni-badge-neu")

        st.markdown(f"""
        <div class="ni-card">
            <div class="ni-card-num">No.{i+1:02d}</div>
            <div class="ni-card-title">{article['title']}</div>
            <div class="ni-card-desc">{article['desc']}</div>
            <div class="ni-card-footer">
                <span class="ni-badge ni-badge-cat">사회</span>
                <span class="{badge_cls}">{sentiment}</span>
                <span class="ni-source">{article.get('source','')}</span>
                <span class="ni-date">{article.get('date','')} · {article.get('views',0):,}회</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("AI 요약 펼치기"):
            st.markdown(f"""
            <div class="ni-summary">
                <div class="ni-summary-label">📌 AI 3줄 요약</div>
                <div class="ni-summary-text">{article.get('summary','')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💬 채팅 분석", key=f"soc_chat_{i}"):
                st.session_state.selected_article = article
                st.success("AI 채팅 탭에서 이 기사에 대해 질문해보세요!")