from datetime import datetime
from html import escape
import streamlit as st
from utils.api_client import send_message as api_send_message


# ── 추천 질문 목록 ───────────────────────────────────────────────────────────
# 한 번에 화면에 표시할 추천 질문 개수
_SUGGESTIONS_TO_SHOW = 3


def _get_suggestions(query: str) -> list[str]:
    """
    검색어 기반 + 일반 분석 질문을 섞은 추천 질문 풀을 반환합니다.
    풀 순서대로 상위 N개(_SUGGESTIONS_TO_SHOW)가 화면에 노출되며,
    클릭된 질문은 used_suggestions 에 추가되어 이후 노출에서 제외됩니다.
    """
    q = query.strip() if query else ""
    return [
        # ── 검색어 기반 ──
        f"'{q}' 핵심 이슈 3줄 요약",
        f"'{q}' 관련 주요 쟁점은?",
        # ── 분석/관점 ──
        "긍정·부정 양면 비교 분석",
        "찬반 논쟁의 핵심 포인트는?",
        # ── 전망 ──
        "향후 전망과 영향은?",
        "단기 vs 장기 전망 비교",
        # ── 이해/설명 ──
        "쉬운 말로 풀어서 설명해줘",
        "관련 배경 지식이 필요해",
        # ── 비교 ──
        "과거 유사 사례와 비교",
        "해외 사례와 비교 분석",
        # ── 영향 ──
        "일반 시민에게 미치는 영향은?",
        "경제·산업에 미치는 파급효과",
    ]


# ── 컨텍스트 배너 ────────────────────────────────────────────────────────────
def _render_context_banner() -> None:
    """선택된 기사가 있으면 컨텍스트 배너를 표시합니다."""
    article = st.session_state.get("selected_article")
    if not article:
        return

    title_short = article["title"][:50] + ("…" if len(article["title"]) > 50 else "")
    st.markdown(f"""
    <div class="ni-context">
        📎 <strong>분석 중인 기사:</strong> {escape(title_short)}
    </div>
    """, unsafe_allow_html=True)

    if st.button("컨텍스트 해제", key="ctx_clear"):
        st.session_state.selected_article = None
        st.rerun()


# ── 대화 이력 렌더링 ─────────────────────────────────────────────────────────
def _render_messages() -> None:
    """저장된 대화 메시지를 말풍선 형태로 렌더링합니다."""
    messages = st.session_state.get("messages", [])

    if not messages:
        st.markdown("""
        <div class="ni-empty" style="padding: 40px 0;">
            <div class="ni-empty-text">
                뉴스에 대해 자유롭게 질문하세요.<br>
                아래 추천 질문을 클릭하거나 직접 입력할 수 있습니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    for msg in messages:
        role = msg.get("role", "user")
        text = msg.get("text", "")
        time = msg.get("time", "")

        if role == "user":
            st.markdown(f"""
            <div class="ni-chat-user">
                {escape(text)}
                <div class="ni-chat-time">{escape(time)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ni-chat-bot">
                {escape(text)}
                <div class="ni-chat-time">{escape(time)}</div>
            </div>
            """, unsafe_allow_html=True)


# ── 추천 질문 버튼 ───────────────────────────────────────────────────────────
def _render_suggestions() -> None:
    """
    추천 질문 버튼을 표시합니다.
    - 대화 시작 여부와 무관하게 query 가 있으면 항상 표시
    - 이미 클릭한 질문(used_suggestions)은 풀에서 제외
    - 풀이 완전히 고갈되면 섹션 전체 숨김
    """
    query = st.session_state.get("query", "")
    if not query:
        return

    # ① 전체 질문 풀
    all_suggestions = _get_suggestions(query)

    # ② 사용된 질문 제외
    used = st.session_state.get("used_suggestions", set())
    available = [s for s in all_suggestions if s not in used]

    # ③ 풀 고갈 시 자동 숨김
    if not available:
        return

    # ④ 상위 N개만 노출 (남은 개수가 N 미만이면 그만큼만)
    to_show = available[:_SUGGESTIONS_TO_SHOW]

    # ⑤ 버튼 렌더링
    st.caption("💡 추천 질문")
    cols = st.columns(len(to_show))
    for col, q in zip(cols, to_show):
        with col:
            # key 는 질문 텍스트 기반으로 고유화 (풀이 바뀌어도 안전)
            if st.button(q, key=f"suggest_{q}", use_container_width=True):
                # 클릭된 질문을 "사용됨" 으로 표시
                st.session_state.used_suggestions = used | {q}
                _send_message(q)


# ── 메시지 전송 처리 ─────────────────────────────────────────────────────────
def _send_message(user_text: str) -> None:
    """
    사용자 메시지를 session_state 에 추가하고
    GPT 응답을 받아 이력에 저장한 뒤 페이지를 재실행합니다.
    """
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "text": user_text, "time": now})

    # 컨텍스트: 선택 기사 > 전체 뉴스 요약 > None
    ctx = st.session_state.get("selected_article") or _build_news_context()

    with st.spinner("AI가 답변을 생성하고 있습니다…"):
        try:
            resp = api_send_message(user_text, context=ctx)
            reply = resp.get("response", "") or "⚠️ 빈 응답을 받았습니다."
        except Exception as e:
            reply = f"⚠️ 백엔드 호출 실패: {e}"

    st.session_state.messages.append({
        "role": "assistant",
        "text": reply,
        "time": datetime.now().strftime("%H:%M"),
    })
    st.session_state.input_key = st.session_state.get("input_key", 0) + 1
    st.rerun()


def _build_news_context() -> dict | None:
    """검색된 뉴스 목록 전체를 채팅 컨텍스트로 조합합니다."""
    news_list = st.session_state.get("news_list", [])
    query     = st.session_state.get("query", "")
    if not news_list:
        return None
    body = "\n\n".join(
        f"{a['title']}: {a['summary']}"
        for a in news_list
    )
    return {"title": query, "body": body}


# ── 메인 렌더 함수 ───────────────────────────────────────────────────────────
def render() -> None:
    """AI 채팅 탭 전체를 렌더링합니다."""
    st.markdown("""
    <div class="ni-summary">
        <div class="ni-summary-label">🤖 AI 뉴스 분석</div>
        <div class="ni-summary-text">
검색된 뉴스를 바탕으로 AI와 심층 대화를 나눠보세요.
기사 탭에서 특정 기사를 선택하면 해당 기사에 집중한 분석도 가능합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ① 컨텍스트 배너
    _render_context_banner()

    # ② 대화 이력
    _render_messages()

    # ③ 스크롤 앵커 및 자동 스크롤 스크립트 추가
    # 메시지가 있을 때만 작동하도록 조건부 렌더링
    if st.session_state.get("messages"):
        st.markdown('<div id="scroll-anchor"></div>', unsafe_allow_html=True)
        st.components.v1.html(
            """
            <script>
                var scrollAnchor = window.parent.document.getElementById('scroll-anchor');
                if (scrollAnchor) {
                    scrollAnchor.scrollIntoView({behavior: 'smooth'});
                }
            </script>
            """,
            height=0,
        )

    st.markdown('<div class="ni-rule"></div>', unsafe_allow_html=True)

    # ④ 추천 질문
    _render_suggestions()

    # ⑤ 입력창 + 전송 버튼 (form으로 감싸 엔터키 지원)
    input_key = st.session_state.get("input_key", 0)

    with st.form(key=f"chat_form_{input_key}", clear_on_submit=False):
        col_input, col_send = st.columns([5, 1])

        with col_input:
            user_text = st.text_input(
                label="채팅 입력",
                placeholder="메시지를 입력하세요…",
                key=f"chat_input_{input_key}",
                label_visibility="collapsed",
            )

        with col_send:
            send_clicked = st.form_submit_button("전송", use_container_width=True)

    # 엔터 또는 전송 버튼 클릭 시 동일하게 처리
    if send_clicked and user_text.strip():
        _send_message(user_text.strip())

    # ⑥ 대화 초기화
    if st.session_state.get("messages"):
        st.markdown("")
        if st.button("🗑️  대화 초기화"):
            st.session_state.messages = []
            st.session_state.used_suggestions = set()   # 추천 질문도 함께 리셋
            st.rerun()