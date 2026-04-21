"""
백엔드-프론트엔드 최소 연동 데모 (Streamlit)

실행 순서:
  1) 백엔드 실행
     (새 터미널)  cd backend && uvicorn app.main:app --reload
  2) 프론트엔드 실행
     (새 터미널)  cd frontend && streamlit run example_integration.py

동작:
  - "검색" 버튼 → 백엔드 /news/search 호출 → 결과를 화면에 카드로 표시
  - 각 카드 "요약 보기" → 제목/요약/원문 링크 노출
  - 아래쪽에 백엔드 health 체크(ping) 표시
"""
import streamlit as st

from utils.api_client import ping, search_news

st.set_page_config(page_title="연동 데모", page_icon="🔗", layout="wide")
st.title("🔗 백엔드 ↔ 프론트 최소 연동 데모")

# ── 1) 백엔드 상태 확인 ────────────────────────────────────────────────
with st.sidebar:
    st.subheader("백엔드 상태")
    if ping():
        st.success("백엔드 연결 OK ✅")
    else:
        st.error("백엔드에 연결할 수 없어요. uvicorn 이 떠있는지 확인하세요.")

# ── 2) 검색 폼 ────────────────────────────────────────────────────────
with st.form("search"):
    query = st.text_input("검색어", value="인공지능")
    count = st.slider("가져올 기사 수", 1, 10, 3)
    submitted = st.form_submit_button("검색 실행")

# ── 3) 결과 출력 ──────────────────────────────────────────────────────
if submitted and query.strip():
    with st.spinner("백엔드에서 뉴스 수집/요약 중... (최대 1분 정도 걸릴 수 있어요)"):
        try:
            items = search_news(query.strip(), count=count)
        except Exception as e:
            st.error(f"API 호출 실패: {e}")
            items = []

    st.caption(f"총 {len(items)}건")
    for n in items:
        with st.container(border=True):
            st.markdown(f"### {n.get('title', '(제목 없음)')}")
            st.caption(f"카테고리: {n.get('category', '-')}")
            if n.get("image_url"):
                st.image(n["image_url"], width=240)
            st.write(n.get("summary", ""))
            if n.get("article_url"):
                st.markdown(f"[원문 보기]({n['article_url']})")
