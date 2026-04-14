import streamlit as st
import requests
from datetime import datetime

# ── 설정 ──────────────────────────────────────────────────
API_BASE = "http://localhost:8000/message"

st.set_page_config(page_title="Messenger", page_icon="💬", layout="centered")

# ── 헬퍼 함수 ─────────────────────────────────────────────
def send_message(text: str):
    try:
        res = requests.post(f"{API_BASE}/send", json={"text": text}, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except requests.exceptions.ConnectionError:
        return None, "서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요."
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP 오류: {e.response.status_code}"
    except Exception as e:
        return None, str(e)


def fetch_all_messages():
    try:
        res = requests.get(f"{API_BASE}/view_all", timeout=10)
        res.raise_for_status()
        return res.json(), None
    except requests.exceptions.ConnectionError:
        return None, "서버에 연결할 수 없습니다."
    except Exception as e:
        return None, str(e)


def format_time(ts):
    if not ts:
        return datetime.now().strftime("%H:%M")
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except Exception:
        return str(ts)[:5]


# ── 세션 상태 초기화 ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ── 헤더 ─────────────────────────────────────────────────
st.title("💬 Messenger")
st.divider()

# ── 메시지 목록 렌더링 ────────────────────────────────────
if not st.session_state.messages:
    st.caption("첫 메시지를 보내보세요")
else:
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        text = msg.get("text", "")
        time = msg.get("time", "")
        with st.chat_message(role):
            st.write(text)
            st.caption(time)

# ── 에러 표시 ─────────────────────────────────────────────
if "last_error" in st.session_state and st.session_state.last_error:
    st.error(st.session_state.last_error)
    st.session_state.last_error = None

st.divider()

# ── 입력 영역 ─────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_text = st.text_input(
        label="",
        placeholder="메시지를 입력하세요…",
        key=f"msg_input_{st.session_state.input_key}",
        label_visibility="collapsed",
    )

with col_btn:
    send_clicked = st.button("전송", use_container_width=True)

# ── 전송 처리 ─────────────────────────────────────────────
if send_clicked and user_text.strip():
    now = datetime.now().strftime("%H:%M")

    st.session_state.messages.append({
        "role": "user",
        "text": user_text.strip(),
        "time": now,
    })

    result, err = send_message(user_text.strip())

    if err:
        st.session_state.last_error = err
    elif result:
        reply_text = (
            result.get("reply") or
            result.get("response") or
            result.get("message") or
            result.get("text") or
            str(result)
        )
        st.session_state.messages.append({
            "role": "assistant",
            "text": reply_text,
            "time": datetime.now().strftime("%H:%M"),
        })

    st.session_state.input_key += 1
    st.rerun()

# ── 하단 버튼 ─────────────────────────────────────────────
col_refresh, col_clear, _ = st.columns([2, 2, 3])

with col_refresh:
    if st.button("🔄 전체 불러오기", use_container_width=True):
        data, err = fetch_all_messages()
        if err:
            st.session_state.last_error = err
        elif data:
            loaded = []
            msgs = data if isinstance(data, list) else data.get("messages", [])
            for m in msgs:
                role = m.get("role", "user") if isinstance(m, dict) else "user"
                text = (m.get("text") or m.get("content") or str(m)) if isinstance(m, dict) else str(m)
                time = format_time(m.get("created_at") or m.get("timestamp")) if isinstance(m, dict) else ""
                loaded.append({"role": role, "text": text, "time": time})
            st.session_state.messages = loaded
            st.rerun()

with col_clear:
    if st.button("🗑️ 대화 지우기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
