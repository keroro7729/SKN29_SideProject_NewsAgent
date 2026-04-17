import streamlit as st


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── 리셋 & 전역 ──────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Streamlit 기본 상단 바 제거 ───────────────────── */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    color: #111;
}

.stApp {
    background: #f5f3ef;
    min-height: 100vh;
}

.block-container {
    max-width: 1100px !important;
    padding: 0 2rem 5rem !important;
}

/* ── 헤더 ──────────────────────────────────────────────── */
.ni-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 1.4rem 0 1rem;
    border-bottom: 3px solid #111;
    margin-bottom: 1.5rem;
}

.ni-logo {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -1px;
    color: #111;
    line-height: 1;
}


.ni-meta {
    font-size: 11px;
    color: #888;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    text-align: right;
    line-height: 1.6;
}

/* ── 카테고리 탭 ──────────────────────────────────────── */
div[data-testid="stTabs"] [role="tablist"] {
    gap: 0 !important;
    border-bottom: 2px solid #111 !important;
    background: transparent !important;
    padding: 0 !important;
}

div[data-testid="stTabs"] button[role="tab"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #999 !important;
    border-radius: 0 !important;
    padding: 10px 22px !important;
    border-bottom: 3px solid transparent !important;
    margin-bottom: -2px !important;
    transition: color .15s !important;
}

div[data-testid="stTabs"] button[role="tab"]:hover {
    color: #111 !important;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #111 !important;
    border-bottom: 3px solid #e8a020 !important;
    background: transparent !important;
}

/* ── 검색창 ──────────────────────────────────────────── */
div[data-testid="stTextInput"] input {
    background: white !important;
    border: 2px solid #111 !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 11px 16px !important;
    color: #111 !important;
    transition: border-color .15s !important;
}

div[data-testid="stTextInput"] input:focus {
    box-shadow: 4px 4px 0 #e8a020 !important;
    border-color: #111 !important;
    outline: none !important;
}

/* ── 버튼 ──────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    background: #111 !important;
    color: #fff !important;
    border: 2px solid #111 !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 11px 20px !important;
    transition: background .15s, color .15s, transform .1s !important;
}

div[data-testid="stButton"] > button:hover {
    background: #e8a020 !important;
    border-color: #e8a020 !important;
    color: #111 !important;
    transform: translate(-1px,-1px) !important;
}

div[data-testid="stButton"] > button:active {
    transform: translate(0,0) !important;
}

/* ── 뉴스 카드 ────────────────────────────────────────── */
.ni-card {
    background: white;
    border: 1.5px solid #ddd9d2;
    padding: 20px 24px 18px;
    margin-bottom: 10px;
    position: relative;
    transition: border-color .15s, box-shadow .15s;
    overflow: hidden;
}

.ni-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: transparent;
    transition: background .15s;
}

.ni-card:hover { border-color: #111; box-shadow: 4px 4px 0 #111; }
.ni-card:hover::before { background: #e8a020; }

.ni-card-num {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #bbb;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.ni-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 700;
    color: #111;
    line-height: 1.4;
    margin-bottom: 8px;
}

.ni-card-desc {
    font-size: 13px;
    color: #666;
    line-height: 1.65;
    margin-bottom: 12px;
}

.ni-card-footer {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.ni-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 8px;
}

.ni-badge-cat  { background: #111; color: #fff; }
.ni-badge-pos  { background: #d4edda; color: #1a6e36; }
.ni-badge-neg  { background: #fde8e8; color: #b91c1c; }
.ni-badge-neu  { background: #e8e5df; color: #555; }

.ni-source { font-size: 11px; color: #999; letter-spacing: .5px; }
.ni-date   { font-size: 11px; color: #bbb; margin-left: auto; }

/* ── 요약 패널 ────────────────────────────────────────── */
.ni-summary {
    background: #111;
    color: white;
    padding: 18px 22px;
    border-left: 4px solid #e8a020;
    margin-bottom: 20px;
}

.ni-summary-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #e8a020;
    margin-bottom: 8px;
}

.ni-summary-text {
    font-size: 13.5px;
    color: #ccc;
    line-height: 1.75;
    white-space: pre-line;
}

/* ── 채팅 ───────────────────────────────────────────── */
.ni-chat-user {
    background: #111;
    color: white;
    padding: 12px 16px;
    margin: 8px 0;
    margin-left: 15%;
    font-size: 14px;
    line-height: 1.6;
    position: relative;
}

.ni-chat-bot {
    background: white;
    border: 1.5px solid #ddd9d2;
    border-left: 4px solid #e8a020;
    color: #111;
    padding: 12px 16px;
    margin: 8px 0;
    margin-right: 15%;
    font-size: 14px;
    line-height: 1.6;
}

.ni-chat-time {
    font-size: 10px;
    color: #888;
    text-align: right;
    margin-top: 4px;
    letter-spacing: .5px;
}

/* ── 컨텍스트 배너 ────────────────────────────────────── */
.ni-context {
    background: #fffbf0;
    border: 1.5px solid #e8a020;
    border-left: 4px solid #e8a020;
    padding: 10px 16px;
    font-size: 13px;
    color: #555;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── 트렌드 키워드 ───────────────────────────────────── */
.ni-kw {
    display: inline-block;
    background: white;
    border: 1.5px solid #ddd9d2;
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    margin: 4px;
    transition: border-color .15s, background .15s;
    cursor: pointer;
}

.ni-kw:hover { border-color: #111; background: #111; color: white; }

/* ── 통계 카드 (metric) ──────────────────────────────── */
div[data-testid="stMetric"] {
    background: white !important;
    border: 1.5px solid #ddd9d2 !important;
    padding: 16px 20px !important;
}

div[data-testid="stMetricLabel"] p {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #999 !important;
}

div[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 26px !important;
    color: #111 !important;
}

/* ── 빈 상태 ─────────────────────────────────────────── */
.ni-empty {
    text-align: center;
    padding: 80px 20px;
}

.ni-empty-icon {
    font-family: 'Playfair Display', serif;
    font-size: 52px;
    color: #ccc;
    margin-bottom: 12px;
}

.ni-empty-text {
    font-size: 14px;
    color: #aaa;
    letter-spacing: .5px;
    line-height: 1.8;
}

/* ── 구분선 ─────────────────────────────────────────── */
.ni-rule {
    height: 1px;
    background: #ddd9d2;
    margin: 1.5rem 0;
}

/* ── 사이드 필터 레이블 ──────────────────────────────── */
.filter-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 6px;
    display: block;
}

/* ── expander 커스텀 ──────────────────────────────────── */
details summary {
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: .5px !important;
    color: #555 !important;
    cursor: pointer;
}

/* ── selectbox ──────────────────────────────────────── */
div[data-testid="stSelectbox"] > div > div {
    border: 1.5px solid #111 !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 13px !important;
}

/* ── radio (감성 필터) ──────────────────────────────── */
div[data-testid="stRadio"] label {
    font-size: 13px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ── scrollbar ────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f5f3ef; }
::-webkit-scrollbar-thumb { background: #ccc; }
::-webkit-scrollbar-thumb:hover { background: #999; }

/* ── 인기 검색어 트렌딩 영역 ────────────────────────────── */
.ni-trending-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 0 6px;
    flex-wrap: wrap;
}

.ni-trending-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #888;
    white-space: nowrap;
    flex-shrink: 0;
}

.ni-trending-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.ni-hot-pill {
    display: inline-block;
    background: white;
    border: 1.5px solid #ddd9d2;
    color: #444;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    padding: 5px 14px;
    border-radius: 999px;
    cursor: pointer;
    transition: all .15s;
    user-select: none;
}

.ni-hot-pill:hover {
    border-color: #e8a020;
    color: #111;
    background: #fffbf0;
}

/* 인기 검색어 아래의 Streamlit 버튼 행 완전히 숨기기 */
.ni-trending-wrap ~ div[data-testid="stHorizontalBlock"] {
    display: none !important;
}

/* 착지 힌트 문구 */
.ni-landing-hint {
    font-size: 12.5px;
    color: #aaa;
    letter-spacing: .3px;
    padding: 18px 0 0;
}
"""

def inject_css():
    """전역 CSS를 Streamlit 페이지에 주입합니다."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)