import streamlit as st
from components.article_card import render_card


def render(articles: list[dict], category: str) -> None:
    if not articles:
        st.markdown(f"""
        <div class="ni-empty">
            <div class="ni-empty-text">{category} 카테고리 기사가 없습니다.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, article in enumerate(articles):
        render_card(article, i, category=category, key_prefix=category)
