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
from constants         import CATEGORIES, CATEGORY_EMOJI
from styles.global_css import inject_css
from data.dummy_news   import get_dummy_news, get_trending_keywords
import components.tab_news    as tab_news
import components.tab_generic as tab_generic
import components.tab_chat    as tab_chat


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
        "active_category":  CATEGORIES[0],   # 현재 선택된 카테고리 탭
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


# ── 검색창 (form으로 감싸 엔터키 지원) ────────────────────────────────────────
with st.form(key="search_form", clear_on_submit=False):
    col_q, col_btn = st.columns([5, 1])

    with col_q:
        query_input = st.text_input(
            label="검색",
            placeholder="검색어를 입력하세요  (예: 인공지능, 반도체, 손흥민, BTS)",
            key="search_input",
            label_visibility="collapsed",
        )

    with col_btn:
        search_clicked = st.form_submit_button("검색", use_container_width=True)

# 검색 실행: 버튼 클릭 또는 엔터키 (form_submit_button이 둘 다 처리)
if search_clicked and query_input.strip():
    st.session_state.query            = query_input.strip()
    st.session_state.news_list        = []
    st.session_state.selected_article = None

    with st.spinner("뉴스를 불러오는 중…"):
        # ─ 실제 API/DB 연동 시 이 라인만 교체 ─
        # from data.naver_api import fetch_news
        # st.session_state.news_list = fetch_news(st.session_state.query)
        st.session_state.news_list = get_dummy_news(
            category=CATEGORIES[0],
            query=st.session_state.query,
        )

st.markdown('<div class="ni-rule"></div>', unsafe_allow_html=True)


# ── 빈 상태: 검색 전 화면 ─────────────────────────────────────────────────────
if not st.session_state.query:
    hot_keywords = get_trending_keywords(CATEGORIES[0])

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
                st.session_state.news_list = get_dummy_news(category=CATEGORIES[0], query=kw)
                st.rerun()

    # 안내 문구
    st.markdown("""
    <div class="ni-landing-hint">
        검색어를 입력하거나 위 키워드를 클릭하면 AI가 뉴스를 분석해드립니다.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── 카테고리 탭 ───────────────────────────────────────────────────────────────
tab_labels = [f"{CATEGORY_EMOJI[c]} {c}" for c in CATEGORIES]
tabs = st.tabs(tab_labels)

# ── 탭별 기사 로딩 ────────────────────────────────────────────────────────────
def _load(category: str) -> list[dict]:
    if category == CATEGORIES[0]: # "전체"
        return st.session_state.news_list
    return get_dummy_news(category=category, query="")


# ══════════════════════════════════════════════════════════════════════════════
# 탭 0: 전체 뉴스
with tabs[0]:
    tab_news.render(_load(CATEGORIES[0]))

# 탭 1~5: 사회 / 경제 / 스포츠 / 엔터 / IT/과학
for i in range(1, 6):
    with tabs[i]:
        tab_generic.render(_load(CATEGORIES[i]), category=CATEGORIES[i])

# 탭 6: AI 채팅
with tabs[6]:
    tab_chat.render()


# ── 맨 위로 가기 버튼 ─────────────────────────────────────────────────────────
st.components.v1.html(
    """
    <script>
    (function() {
        let parentDoc;
        try {
            parentDoc = window.parent.document;
        } catch (e) {
            return;
        }

        // 기존 버튼 제거 (리런 대비)
        const oldBtn = parentDoc.getElementById('scrollTopBtn');
        if (oldBtn) oldBtn.remove();

        // 버튼 생성
        const btn = parentDoc.createElement('button');
        btn.id = 'scrollTopBtn';
        btn.innerHTML = '↑';
        btn.setAttribute('aria-label', '맨 위로');
        btn.style.cssText = [
            'position: fixed',
            'bottom: 30px',
            'right: 30px',
            'width: 48px',
            'height: 48px',
            'border-radius: 50%',
            'background: #111',
            'color: #fff',
            'border: 2px solid #111',
            'font-size: 20px',
            'font-weight: 700',
            'cursor: pointer',
            'opacity: 0',
            'pointer-events: none',
            'box-shadow: 4px 4px 0 #e8a020',
            'z-index: 999999',
            'transition: opacity .2s, background .15s, color .15s, transform .1s'
        ].join(';') + ';';

        btn.onmouseover = function() {
            this.style.background = '#e8a020';
            this.style.color = '#111';
            this.style.borderColor = '#e8a020';
            this.style.transform = 'translate(-1px,-1px)';
        };
        btn.onmouseout = function() {
            this.style.background = '#111';
            this.style.color = '#fff';
            this.style.borderColor = '#111';
            this.style.transform = 'translate(0,0)';
        };

        btn.onclick = function() {
            try { window.parent.scrollTo({top: 0, behavior: 'smooth'}); } catch(e) {}
            const candidates = [
                '[data-testid="stAppViewContainer"]',
                '[data-testid="stMain"]',
                'section.main',
                '.main' 
            ];
            candidates.forEach(sel => {
                const el = parentDoc.querySelector(sel);
                if (el && typeof el.scrollTo === 'function') {
                    try { el.scrollTo({top: 0, behavior: 'smooth'}); } catch(e) {}
                }
            });
            try { parentDoc.documentElement.scrollTo({top: 0, behavior: 'smooth'}); } catch(e) {}
            try { parentDoc.body.scrollTo({top: 0, behavior: 'smooth'}); } catch(e) {}
        };

        try {
            parentDoc.body.appendChild(btn);
        } catch (e) {
            return;
        }

        // 스크롤 위치 계산 (여러 컨테이너 중 최댓값)
        function getScrollY() {
            const targets = [
                window.parent,
                parentDoc.documentElement,
                parentDoc.body,
                parentDoc.querySelector('[data-testid="stAppViewContainer"]'),
                parentDoc.querySelector('[data-testid="stMain"]'),
                parentDoc.querySelector('section.main'),
                parentDoc.querySelector('.main')
            ];
            let maxY = 0;
            targets.forEach(t => {
                if (!t) return;
                const y = (t === window.parent)
                    ? (t.scrollY || t.pageYOffset || 0)
                    : (t.scrollTop || 0);
                if (y > maxY) maxY = y;
            });
            return maxY;
        }

        function toggleBtn() {
            const y = getScrollY();
            if (y > 300) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0';
                btn.style.pointerEvents = 'none';
            }
        }

        // 모든 후보 컨테이너에 scroll 리스너 등록
        const scrollTargets = [
            window.parent,
            parentDoc,
            parentDoc.querySelector('[data-testid="stAppViewContainer"]'),
            parentDoc.querySelector('[data-testid="stMain"]'),
            parentDoc.querySelector('section.main'),
            parentDoc.querySelector('.main')
        ].filter(Boolean);

        scrollTargets.forEach(t => {
            try { t.addEventListener('scroll', toggleBtn, true); } catch(e) {}
            try { t.addEventListener('scroll', toggleBtn, false); } catch(e) {}
        });

        // 초기 상태 체크
        toggleBtn();
    })();
    </script>
    """,
    height=0,
)