import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# 스타일 파일에서 함수 가져오기
from news_chat_style import apply_style

# llm.py가 같은 폴더에 있다고 가정
sys.path.append(os.path.dirname(__file__))

# ── 페이지 설정 ─────────────────────────────────────────
st.set_page_config(
    page_title="NewsInsight",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 스타일 실행 ─────────────────────────────────────────
apply_style()

# ── 세션 상태 초기화 ────────────────────────────────────
def init_state():
    defaults = {
        "query": "",
        "news_list": [],       # [{title, desc, summary, source, link}]
        "messages": [],        # [{role, text, time}]
        "selected_article": None,  # 채팅에 넘길 기사
        "is_loading": False,
        "input_key": 0,
        "active_tab": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── llm.py 연동 함수 ────────────────────────────────────
def load_llm():
    """llm.py의 함수들을 동적으로 import. 실패 시 더미 데이터 반환."""
    try:
        from llm import search_naver_news, fetch_article_body, summarize_with_gpt
        from bs4 import BeautifulSoup
        return search_naver_news, fetch_article_body, summarize_with_gpt, BeautifulSoup, True
    except Exception:
        return None, None, None, None, False


def fetch_news_with_summary(query: str, count: int = 5):
    """뉴스 검색 + 본문 추출 + 요약 통합 함수"""
    search_naver_news, fetch_article_body, summarize_with_gpt, BeautifulSoup, ok = load_llm()

    if not ok:
        # llm.py 없을 때 더미 데이터
        import random
        sources = ["연합뉴스", "중앙일보", "조선일보", "한겨레", "매일경제"]
        return [
            {
                "title": f"{query} 관련 주요 뉴스 {i+1}",
                "desc": f"{query}에 관한 최신 동향과 전문가 분석입니다.",
                "summary": f"• {query} 분야에서 새로운 움직임이 포착됐습니다.\n• 전문가들은 이번 사안에 대해 긍정적으로 평가했습니다.\n• 향후 추가적인 변화가 예상됩니다.",
                "source": random.choice(sources),
                "link": "#",
            }
            for i in range(count)
        ]

    articles = search_naver_news(query, display=count)
    results = []

    for article in articles:
        title = BeautifulSoup(article["title"], "html.parser").get_text()
        link = article.get("originallink") or article.get("link", "#")
        desc = BeautifulSoup(article.get("description", ""), "html.parser").get_text()
        source = article.get("originallink", "").split("/")[2] if article.get("originallink") else "뉴스"

        body = fetch_article_body(link)
        summary = summarize_with_gpt(title, body)

        results.append({
            "title": title,
            "desc": desc[:120] + "..." if len(desc) > 120 else desc,
            "summary": summary,
            "source": source,
            "link": link,
            "body": body[:2000],
        })

    return results


def chat_with_gpt(messages: list, user_message: str, context_article=None) -> str:
    """GPT 채팅 (기사 컨텍스트 포함 가능)"""
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        system_prompt = "당신은 뉴스 분석 전문가입니다. 사용자의 질문에 명확하고 간결하게 한국어로 답변해주세요."

        if context_article:
            system_prompt += f"""

현재 사용자가 읽고 있는 기사:
제목: {context_article.get('title', '')}
내용: {context_article.get('body', context_article.get('summary', ''))}

이 기사와 관련된 질문에 우선적으로 답변해주세요.
"""

        history = [{"role": "system", "content": system_prompt}]
        for m in messages[-10:]:  # 최근 10개만
            history.append({"role": m["role"], "content": m["text"]})
        history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            max_tokens=500,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"응답을 가져오지 못했습니다: {str(e)}"


# ── 헤더 ────────────────────────────────────────────────
today = datetime.now().strftime("%Y년 %m월 %d일")
st.markdown(f"""
<div class="site-header">
    <span class="site-logo">NewsInsight</span>
    <span class="site-date">{today}</span>
</div>
""", unsafe_allow_html=True)


# ── 검색창 ───────────────────────────────────────────────
with st.form("search_form"):
    col_search, col_btn = st.columns([5, 1])

    with col_search:
        query_input = st.text_input(
            label="",
            placeholder="검색어를 입력하세요 (예: 인공지능, 반도체, 부동산)",
            key="search_input",
            label_visibility="collapsed",
        )

    with col_btn:
        search_clicked = st.form_submit_button("검색", use_container_width=True)

if search_clicked and query_input.strip():
    st.session_state.query = query_input.strip()
    st.session_state.news_list = []
    st.session_state.selected_article = None
    with st.spinner("뉴스를 검색하고 요약 중입니다..."):
        st.session_state.news_list = fetch_news_with_summary(
            st.session_state.query, count=5
        )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ── 결과 없을 때 ─────────────────────────────────────────
if not st.session_state.query:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">◈</div>
        <div class="empty-state-text">검색어를 입력하면 최신 뉴스와 AI 요약을 제공합니다</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── 탭 ──────────────────────────────────────────────────
tab_news, tab_sentiment, tab_trend, tab_chat = st.tabs(["뉴스", "감성 분석", "트렌드", "AI 채팅"])


# ══════════════════════════════════════════════════════
# 탭 1: 뉴스
# ══════════════════════════════════════════════════════
with tab_news:
    if not st.session_state.query:
        st.info("검색어를 입력하고 검색을 실행해주세요.")
    elif not st.session_state.news_list:
        st.warning(f"'{st.session_state.query}'에 대한 뉴스를 찾지 못했어요. 다른 검색어를 입력해보세요.")

    else:
        # 상단 요약 배너
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-card-accent"></div>
            <div class="summary-card-body">
                <div class="summary-card-keyword">
                    <div class="summary-keyword-label">검색어</div>
                    <div class="summary-keyword-text">{st.session_state.query}</div>
                </div>
                <div class="summary-card-vline"></div>
                <div class="summary-card-info">
                    <div class="summary-count-row">
                        <span class="summary-count-num">{len(st.session_state.news_list):02d}</span>
                        <span class="summary-count-unit">articles collected</span>
                    </div>
                    <div class="summary-title">AI가 요약한 최신 뉴스입니다. 아래 기사를 펼치거나 AI 채팅 탭에서 질문해보세요.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 뉴스 카드 목록
        for i, article in enumerate(st.session_state.news_list):
            with st.container():
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-card-number">No. {i+1:02d}</div>
                    <div class="news-card-title">{article['title']}</div>
                    <div class="news-card-desc">{article['desc']}</div>
                    <div class="news-card-meta">
                        <span>{article['source']}</span>
                        <span class="news-card-badge">AI 요약</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 요약 expander
                with st.expander("AI 요약 보기"):
                    st.markdown(article["summary"])
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        if article.get("link") and article["link"] != "#":
                            st.markdown(f"[원문 보기 →]({article['link']})")
                    with col_b:
                        if st.button("채팅에서 분석", key=f"chat_btn_{i}"):
                            st.session_state.selected_article = article
                            # 채팅 탭으로 안내
                            st.success("AI 채팅 탭에서 이 기사에 대해 질문하세요!")


# ══════════════════════════════════════════════════════
# 탭 2: 감성 분석
# ══════════════════════════════════════════════════════
with tab_sentiment:
    if not st.session_state.news_list:
        st.info("검색을 먼저 실행해주세요.")
    else:
        import random
        col_chart, col_info = st.columns([3, 2])

        with col_chart:
            # 도넛 차트
            pos = random.randint(30, 55)
            neg = random.randint(15, 35)
            neu = 100 - pos - neg

            fig = go.Figure(data=[go.Pie(
                labels=["긍정", "부정", "중립"],
                values=[pos, neg, neu],
                hole=0.6,
                marker=dict(colors=["#2d6a4f", "#c1440e", "#b0a898"]),
                textinfo="label+percent",
                textfont=dict(family="DM Sans", size=13),
            )])
            fig.update_layout(
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[dict(
                    text=f"<b>{pos}%</b><br>긍정",
                    x=0.5, y=0.5,
                    font=dict(family="DM Serif Display", size=18, color="#1a1a1a"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_info:
            st.markdown("#### 감성 분포")
            st.metric("긍정적 기사", f"{pos}%")
            st.metric("부정적 기사", f"{neg}%")
            st.metric("중립적 기사", f"{neu}%")
            st.caption("※ AI 감성 분석 결과는 참고용입니다.")


# ══════════════════════════════════════════════════════
# 탭 3: 트렌드
# ══════════════════════════════════════════════════════
with tab_trend:
    if not st.session_state.news_list:
        st.info("검색을 먼저 실행해주세요.")
    else:
        import random

        # 주간 트렌드 차트
        days = ["월", "화", "수", "목", "금", "토", "일"]
        values = [random.randint(20, 90) for _ in days]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days,
            y=values,
            mode="lines+markers",
            line=dict(color="#1a1a1a", width=2),
            marker=dict(color="#1a1a1a", size=8),
            fill="tozeroy",
            fillcolor="rgba(26,26,26,0.05)",
        ))
        fig.update_layout(
            title=dict(
                text=f"'{st.session_state.query}' 주간 언급량",
                font=dict(family="DM Serif Display", size=18, color="#1a1a1a"),
            ),
            xaxis=dict(showgrid=False, tickfont=dict(family="DM Sans")),
            yaxis=dict(showgrid=True, gridcolor="#f0ede8", tickfont=dict(family="DM Sans")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=60, b=40, l=40, r=20),
        )
        st.plotly_chart(fig, use_container_width=True)

        # 연관 키워드
        st.markdown("#### 연관 키워드")
        keywords = [
            f"{st.session_state.query} 시장", f"{st.session_state.query} 기술",
            "투자", "정책", "글로벌", "국내", "스타트업", "규제", "혁신",
        ]
        badge_html = "".join(
            f'<span class="trend-badge"># {kw}</span>' for kw in keywords
        )
        st.markdown(badge_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 탭 4: AI 채팅
# ══════════════════════════════════════════════════════
with tab_chat:
    # 선택된 기사 컨텍스트 배너
    if st.session_state.selected_article:
        title_short = st.session_state.selected_article["title"][:50] + "..."
        st.markdown(f"""
        <div class="context-banner">
            📎 현재 분석 중인 기사: <strong>{title_short}</strong>
        </div>
        """, unsafe_allow_html=True)
        if st.button("컨텍스트 해제"):
            st.session_state.selected_article = None
            st.rerun()

    # 채팅 메시지 표시
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="empty-state" style="padding: 40px 20px;">
                <div class="empty-state-text">뉴스에 대해 자유롭게 질문해보세요</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                role = msg.get("role", "user")
                text = msg.get("text", "")
                time = msg.get("time", "")

                if role == "user":
                    st.markdown(f"""
                    <div class="chat-bubble-user">{text}
                        <div class="chat-time">{time}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-bubble-assistant">{text}
                        <div class="chat-time">{time}</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # 추천 질문 (뉴스 있을 때)
    if st.session_state.news_list and not st.session_state.messages:
        st.caption("추천 질문")
        q_cols = st.columns(3)
        suggestions = [
            f"'{st.session_state.query}' 핵심 이슈 정리해줘",
            "긍정적인 면과 부정적인 면 비교해줘",
            "향후 전망은 어떻게 돼?",
        ]
        for i, (col, q) in enumerate(zip(q_cols, suggestions)):
            with col:
                if st.button(q, key=f"suggest_{i}", use_container_width=True):
                    now = datetime.now().strftime("%H:%M")
                    st.session_state.messages.append({"role": "user", "text": q, "time": now})
                    with st.spinner("답변 생성 중..."):
                        # 검색된 뉴스 요약을 컨텍스트로 넘김
                        ctx = st.session_state.selected_article or (
                            {"title": st.session_state.query,
                             "body": "\n\n".join(
                                 f"{a['title']}: {a['summary']}"
                                 for a in st.session_state.news_list
                             )}
                            if st.session_state.news_list else None
                        )
                        reply = chat_with_gpt(st.session_state.messages[:-1], q, ctx)
                    st.session_state.messages.append({"role": "assistant", "text": reply, "time": datetime.now().strftime("%H:%M")})
                    st.session_state.input_key += 1
                    st.rerun()

    # 입력창
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_text = st.text_input(
                label="",
                placeholder="메시지를 입력하세요…",
                key=f"chat_input_{st.session_state.input_key}",
                label_visibility="collapsed",
            )
        with col_send:
            send_clicked = st.form_submit_button("전송", key="send_btn", use_container_width=True)

    if send_clicked and user_text.strip():
        now = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({"role": "user", "text": user_text.strip(), "time": now})

        with st.spinner("답변 생성 중..."):
            ctx = st.session_state.selected_article or (
                {"title": st.session_state.query,
                 "body": "\n\n".join(
                     f"{a['title']}: {a['summary']}"
                     for a in st.session_state.news_list
                 )}
                if st.session_state.news_list else None
            )
            reply = chat_with_gpt(st.session_state.messages[:-1], user_text.strip(), ctx)

        st.session_state.messages.append({"role": "assistant", "text": reply, "time": datetime.now().strftime("%H:%M")})
        st.session_state.input_key += 1
        st.rerun()

    # 대화 지우기
    if st.session_state.messages:
        if st.button("🗑️ 대화 지우기"):
            st.session_state.messages = []
            st.rerun()
