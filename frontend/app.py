import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from datetime import datetime

# ── 페이지 설정 (반드시 첫 번째 Streamlit 호출이어야 함) ──────────────────────
st.set_page_config(
    page_title="NewsInsight",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 모듈 임포트 ───────────────────────────────────────────────────────────────
from styles.global_css import inject_css
from data.dummy_news   import get_dummy_news, get_trending_keywords
import components.tab_news        as tab_news
import components.tab_social      as tab_social
import components.tab_economy     as tab_economy
import components.tab_sports_ent  as tab_sports_ent
import components.tab_chat        as tab_chat


# ── 전역 CSS 주입 ─────────────────────────────────────────────────────────────
inject_css()


# ── 세션 상태 초기화 ──────────────────────────────────────────────────────────
def _init_state() -> None:
    """
    앱 최초 실행 또는 페이지 새로고침 시 세션 상태를 초기화합니다.
    이미 설정된 키는 덮어쓰지 않으므로 안전합니다.
    """
    defaults = {
        "query":            "",       # 현재 검색어
        "news_list":        [],       # 검색 결과 기사 리스트
        "messages":         [],       # AI 채팅 이력
        "selected_article": None,     # 채팅 컨텍스트로 넘길 기사
        "input_key":        0,        # 채팅 입력창 초기화용 카운터
        "active_category":  "전체",   # 현재 선택된 카테고리 탭
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ── 헤더 ──────────────────────────────────────────────────────────────────────
today    = datetime.now().strftime("%Y년 %m월 %d일")
weekdays = ["월", "화", "수", "목", "금", "토", "일"]
weekday  = weekdays[datetime.now().weekday()]

st.markdown(f"""
<div class="ni-header">
    <div>
        <div class="ni-logo">News<span>Insight</span></div>
    </div>
    <div class="ni-meta">
        {today} ({weekday})<br>
        AI 뉴스 분석 플랫폼
    </div>
</div>
""", unsafe_allow_html=True)


# ── 검색창 ────────────────────────────────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])

with col_q:
    query_input = st.text_input(
        label="검색",
        placeholder="검색어를 입력하세요  (예: 인공지능, 반도체, 손흥민, BTS)",
        key="search_input",
        label_visibility="collapsed",
    )

with col_btn:
    search_clicked = st.button("검색", use_container_width=True)

# 검색 실행: 버튼 클릭 또는 엔터 (input 값 변경 감지)
if search_clicked and query_input.strip():
    st.session_state.query            = query_input.strip()
    st.session_state.news_list        = []
    st.session_state.selected_article = None

    with st.spinner("뉴스를 불러오는 중…"):
        # ─ 실제 API/DB 연동 시 이 라인만 교체 ─
        # from data.naver_api import fetch_news
        # st.session_state.news_list = fetch_news(st.session_state.query)
        st.session_state.news_list = get_dummy_news(
            category="전체",
            query=st.session_state.query,
        )

st.markdown('<div class="ni-rule"></div>', unsafe_allow_html=True)


# ── 빈 상태: 검색 전 화면 ─────────────────────────────────────────────────────
if not st.session_state.query:
    hot_keywords = get_trending_keywords("전체")

    # 인기 검색어 pill 태그 (HTML 렌더링)
    pills_html = "".join(
        f'<span class="ni-hot-pill" id="pill_{i}">{kw}</span>'
        for i, kw in enumerate(hot_keywords)
    )
    st.markdown(f"""
    <div class="ni-trending-wrap">
        <span class="ni-trending-label">🔥 추천 검색어</span>
    </div>
    """, unsafe_allow_html=True)

    # 클릭 가능한 버튼 (Streamlit 상호작용) — 시각적으로는 숨기고 pill 클릭 느낌
    btn_cols = st.columns(len(hot_keywords))
    for i, (col, kw) in enumerate(zip(btn_cols, hot_keywords)):
        with col:
            if st.button(kw, key=f"hot_{i}", use_container_width=True):
                st.session_state.query     = kw
                st.session_state.news_list = get_dummy_news(category="전체", query=kw)
                st.rerun()

    # 안내 문구
    st.markdown("""
    <div class="ni-landing-hint">
        검색어를 입력하거나 위 키워드를 클릭하면 AI가 뉴스를 분석해드립니다.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── 카테고리 탭 ───────────────────────────────────────────────────────────────
# 탭 순서: 전체뉴스 / 사회 / 경제 / 스포츠 / 연예 / AI 채팅
tabs = st.tabs(["📋 전체뉴스", "🏛️ 사회", "📈 경제", "⚽ 스포츠", "🎬 연예", "🤖 AI 채팅"])

TAB_CATEGORIES = ["전체", "사회", "경제", "스포츠", "연예"]


# ── 탭별 기사 로딩 ────────────────────────────────────────────────────────────
def _load(category: str) -> list[dict]:
    """
    카테고리에 맞는 기사 리스트를 반환합니다.
    전체 탭은 session_state.news_list 를 그대로 사용하고,
    나머지 탭은 해당 카테고리만 필터링해 반환합니다.
    """
    if category == "전체":
        return st.session_state.news_list

    # 더미 데이터에서 해당 카테고리 기사를 별도로 가져옵니다.
    # 실제 API 연동 시 DB 쿼리로 교체하세요.
    return get_dummy_news(category=category, query="")


# ══════════════════════════════════════════════════════════════════════════════
# 탭 0: 전체 뉴스
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    tab_news.render(_load("전체"))

# ══════════════════════════════════════════════════════════════════════════════
# 탭 1: 사회
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    tab_social.render(_load("사회"))

# ══════════════════════════════════════════════════════════════════════════════
# 탭 2: 경제
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    tab_economy.render(_load("경제"))

# ══════════════════════════════════════════════════════════════════════════════
# 탭 3: 스포츠
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    tab_sports_ent.render(_load("스포츠"), category="스포츠")

# ══════════════════════════════════════════════════════════════════════════════
# 탭 4: 연예
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    tab_sports_ent.render(_load("연예"), category="연예")

# ══════════════════════════════════════════════════════════════════════════════
# 탭 5: AI 채팅
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    tab_chat.render()