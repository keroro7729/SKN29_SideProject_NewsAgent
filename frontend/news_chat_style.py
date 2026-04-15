import streamlit as st

def apply_style():

    # ── 전역 스타일 ─────────────────────────────────────────
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500&display=swap');

    /* 전체 폰트 */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* 배경 */
    .stApp {
        background-color: #f8f7f4;
    }

    /* 상단 흰 바 → 배경색 통일 */
    header[data-testid="stHeader"] {
        background-color: #f8f7f4;
    }

    /* 메인 컨테이너 */
    .block-container {
        max-width: 1100px;
        padding: 2rem 2rem 4rem;
    }

    /* 헤더 */
    .site-header {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 2rem;
        border-bottom: 2px solid #1a1a1a;
        padding-bottom: 1rem;
    }

    .site-logo {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #1a1a1a;
        letter-spacing: -0.5px;
    }

    .site-date {
        font-size: 12px;
        color: #888;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* 검색창 */
    div[data-testid="stTextInput"] input {
        background: white !important;
        border: 1.5px solid #1a1a1a !important;
        border-radius: 0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 15px !important;
        padding: 10px 14px !important;
        color: #1a1a1a !important;
    }

    div[data-testid="stTextInput"] input:focus {
        box-shadow: none !important;
        border-color: #1a1a1a !important;
    }

    /* 버튼 */
    div[data-testid="stButton"] > button {
        background: #1a1a1a !important;
        color: white !important;
        border: none !important;
        border-radius: 0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        padding: 10px 20px !important;
        transition: background 0.2s !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: #333 !important;
    }

    /* secondary 버튼 스타일 (채팅 전송) */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: white !important;
        color: #1a1a1a !important;
        border: 1.5px solid #1a1a1a !important;
    }

    /* 탭 */
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 0;
        border-bottom: 1.5px solid #1a1a1a;
        background: transparent;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        color: #888 !important;
        border-radius: 0 !important;
        padding: 8px 20px !important;
        border-bottom: 2px solid transparent !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #1a1a1a !important;
        border-bottom: 2px solid #1a1a1a !important;
        background: transparent !important;
    }

    /* 뉴스 카드 */
    .news-card {
        background: white;
        border: 1px solid #e8e5e0;
        padding: 20px 24px;
        margin-bottom: 12px;
        transition: border-color 0.2s, transform 0.1s;
        cursor: pointer;
        position: relative;
    }

    .news-card:hover {
        border-color: #1a1a1a;
    }

    .news-card-number {
        font-family: 'DM Serif Display', serif;
        font-size: 11px;
        color: #bbb;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }

    .news-card-title {
        font-family: 'DM Serif Display', serif;
        font-size: 17px;
        color: #1a1a1a;
        line-height: 1.4;
        margin-bottom: 8px;
    }

    .news-card-desc {
        font-size: 13px;
        color: #666;
        line-height: 1.6;
        margin-bottom: 10px;
    }

    .news-card-meta {
        font-size: 11px;
        color: #aaa;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: flex;
        gap: 12px;
    }

    .news-card-badge {
        display: inline-block;
        background: #f0ede8;
        color: #666;
        font-size: 10px;
        padding: 2px 8px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* 요약 카드 */
    .summary-card {
        background: #1a1a1a;
        padding: 0;
        margin-bottom: 28px;
        overflow: hidden;
        position: relative;
        display: flex;
        min-height: 90px;
        border: 3px solid #f0c040;
    }

    .summary-card-accent {
        width: 6px;
        background: #f0c040;        
        flex-shrink: 0;
    }

    .summary-card-body {
        flex: 1;
        padding: 16px 28px;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .summary-card-keyword {
        flex-shrink: 0;
    }

    .summary-keyword-label {
        font-size: 12px;            
        color: #f0c040;              
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .summary-keyword-text {
        font-family: 'DM Serif Display', serif;
        font-size: 30px;          
        color: white;
        line-height: 1.1;
        white-space: nowrap;
    }

    .summary-card-vline {
        width: 1px;
        height: 44px;
        background: #333;
        flex-shrink: 0;
    }

    .summary-card-info {
        flex: 1;
    }

    .summary-count-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin-bottom: 8px;
    }

    .summary-count-num {
        font-family: 'DM Serif Display', serif;
        font-size: 26px;            
        color: #f0c040;
        line-height: 1;
    }

    .summary-count-unit {
        font-size: 14px;           
        color: #bbb;                 
        letter-spacing: 0.5px;
    }

    .summary-title {
        font-size: 15px;            
        color: #ddd;               
        line-height: 1.6;
    }

    .summary-text {
        display: none;
    }

    /* 채팅 말풍선 */
    .chat-bubble-user {
        background: #1a1a1a;
        color: white;
        padding: 12px 16px;
        margin: 6px 0;
        margin-left: 20%;
        font-size: 14px;
        line-height: 1.6;
    }

    .chat-bubble-assistant {
        background: white;
        border: 1px solid #e8e5e0;
        color: #1a1a1a;
        padding: 12px 16px;
        margin: 6px 0;
        margin-right: 20%;
        font-size: 14px;
        line-height: 1.6;
    }

    .chat-time {
        font-size: 10px;
        color: #aaa;
        letter-spacing: 0.5px;
        margin-top: 4px;
        text-align: right;
    }

    /* 컨텍스트 배너 */
    .context-banner {
        background: #fffbf0;
        border: 1px solid #f0c040;
        border-left: 4px solid #f0c040;
        padding: 10px 16px;
        font-size: 13px;
        color: #666;
        margin-bottom: 16px;
    }

    .context-banner strong {
        color: #1a1a1a;
    }

    /* 분리선 */
    .section-divider {
        height: 1px;
        background: #e8e5e0;
        margin: 24px 0;
    }

    /* 플로팅 뱃지 */
    .trend-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #eef4ff;
        color: #2563eb;
        border: 1px solid #bfdbfe;
        font-size: 12px;
        padding: 4px 10px;
        margin: 4px;
    }

    /* 빈 상태 */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
        color: #bbb;
    }

    .empty-state-icon {
        font-family: 'DM Serif Display', serif;
        font-size: 48px;
        margin-bottom: 12px;
        opacity: 0.3;
    }

    .empty-state-text {
        font-size: 14px;
        letter-spacing: 0.5px;
    }

    /* divider */
    hr {
        border: none;
        border-top: 1px solid #e8e5e0;
        margin: 1.5rem 0;
    }

    /* metric */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e8e5e0;
        padding: 16px 20px;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        color: #888 !important;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'DM Serif Display', serif !important;
        font-size: 28px !important;
        color: #1a1a1a !important;
    }
    </style>
    """, unsafe_allow_html=True)
