from datetime import datetime
import streamlit as st
from utils.llm_api import chat_with_gpt


# ── 추천 질문 목록 ───────────────────────────────────────────────────────────
def _get_suggestions(query: str) -> list[str]:
    return [
        f"'{query}' 핵심 이슈 3줄 요약",
        "긍정·부정 양면 비교 분석",
        "향후 전망과 영향은?",
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
        📎 <strong>분석 중인 기사:</strong> {title_short}
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
                {text}
                <div class="ni-chat-time">{time}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ni-chat-bot">
                {text}
                <div class="ni-chat-time">{time}</div>
            </div>
            """, unsafe_allow_html=True)


# ── 추천 질문 버튼 ───────────────────────────────────────────────────────────
def _render_suggestions() -> None:
    """
    뉴스가 검색되어 있고 대화가 아직 없을 때 추천 질문 버튼을 표시합니다.
    버튼 클릭 시 해당 질문으로 즉시 채팅을 시작합니다.
    """
    news_list = st.session_state.get("news_list", [])
    messages  = st.session_state.get("messages", [])
    query     = st.session_state.get("query", "")

    if not news_list or messages:
        return

    st.caption("💡 추천 질문")
    suggestions = _get_suggestions(query)
    cols = st.columns(len(suggestions))

    for i, (col, q) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(q, key=f"suggest_{i}", use_container_width=True):
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
        reply = chat_with_gpt(
            st.session_state.messages[:-1],
            user_text,
            ctx,
        )

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

    st.markdown('<div class="ni-rule"></div>', unsafe_allow_html=True)

    # ③ 추천 질문
    _render_suggestions()

    # ④ 입력창 + 전송 버튼
    input_key = st.session_state.get("input_key", 0)
    col_input, col_send = st.columns([5, 1])

    with col_input:
        user_text = st.text_input(
            label="채팅 입력",
            placeholder="메시지를 입력하세요…",
            key=f"chat_input_{input_key}",
            label_visibility="collapsed",
        )

    with col_send:
        send_clicked = st.button("전송", key="send_btn", use_container_width=True)

    if send_clicked and user_text.strip():
        _send_message(user_text.strip())

    # ⑤ 대화 초기화
    if st.session_state.get("messages"):
        st.markdown("")
        if st.button("🗑️  대화 초기화"):
            st.session_state.messages = []
            st.rerun()