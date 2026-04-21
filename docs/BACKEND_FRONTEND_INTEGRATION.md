# 백엔드 ↔ 프론트엔드 연동 가이드

비전공자도 따라 할 수 있도록, **왜 그렇게 해야 하는지**와 **구체적인 명령어**를 함께 정리했습니다. 현재 프로젝트는 백엔드(FastAPI, 포트 8000)와 프론트엔드(Streamlit, 포트 8501)가 분리돼 있고, 프론트엔드는 아직 `data/dummy_news.py` 를 쓰고 있습니다. 아래 단계대로 진행하면 실제 백엔드 데이터로 교체할 수 있습니다.

## 1. API 엔드포인트 설계 제안

백엔드와 프론트엔드 사이의 약속(계약)이 바로 API 엔드포인트입니다. 핵심 원칙은 **자원(명사) + HTTP 메서드(동사)** 조합으로 표현하고, 응답 포맷을 일관되게 유지하는 것입니다. 현재 프로젝트의 라우터는 이 원칙을 거의 잘 지키고 있으나, 프론트엔드가 바로 사용하기 쉬운 형태로 다음처럼 정리/보완하기를 제안합니다.

| 메서드 | 경로 | 용도 | 비고 |
| --- | --- | --- | --- |
| GET | `/health/ping` | 서버 헬스체크 | 이미 있음. 프론트 최초 로딩 시 호출 권장 |
| GET | `/news?category=경제&page=1&size=10` | 카테고리별 저장 뉴스 조회 | `page`, `size` 쿼리파라미터로 페이지네이션 추가 권장 |
| GET | `/news/{id}` | 단건 상세 조회 | 현재는 `article_url`을 path로 받는데, URL을 path에 넣으면 슬래시·인코딩 문제가 잦습니다. `id`(정수) 기반으로 바꾸고, 필요하면 `GET /news/by-url?u=…` 형태의 별도 엔드포인트를 두는 게 안전합니다 |
| POST | `/news/search` | 외부 검색 + 크롤링 + 요약 + 저장 | 현재 `query`, `count` 가 쿼리스트링인데 POST에는 보통 **JSON Body** 가 관례입니다 (`{"query": "...", "count": 10}`) |
| POST | `/message/send` | 채팅 메시지 전송 | 이미 JSON Body 사용 — 좋은 예시 |
| GET | `/message/view_all?session_id=…` | 메시지 이력 | 세션 단위로 묶을 수 있게 `session_id` 도입 권장 |

추가로 다음을 권장합니다.

- **응답 스키마 통일**: 리스트는 항상 `{"items": [...], "total": N}` 형태로 감싸면 프론트에서 페이지네이션·빈 상태 처리가 쉬워집니다.
- **에러 포맷 고정**: FastAPI 기본 `{"detail": "..."}` 를 그대로 쓰고, 프론트는 HTTP 상태코드로 분기합니다.
- **Pydantic `response_model` 명시**: 지금은 `response_model=None` 인데, 모델을 명시하면 자동으로 문서(`/docs`)에 스키마가 드러나고 프론트 개발이 훨씬 쉬워집니다.

## 2. CORS 및 HTTP 통신 최적화

### 2-1. CORS가 뭔가요?

브라우저는 보안을 위해 "현재 열려 있는 페이지의 출처(origin)"와 다른 곳으로 API를 호출할 때 서버가 허용했는지를 확인합니다. `http://localhost:8501`(Streamlit)에서 `http://localhost:8000`(FastAPI)을 호출하면 포트가 다르므로 **다른 출처**로 간주돼 차단됩니다. 이를 풀어주는 장치가 CORS 설정입니다.

주의할 점: **Streamlit 자체는 서버에서 `requests`로 백엔드를 호출**하므로 엄밀히는 브라우저 CORS가 걸리지 않습니다. 다만 앞으로 React/Vue로 프론트가 바뀌거나, Streamlit에서 `components.html` 로 브라우저 직접 fetch를 쓴다면 바로 문제가 되기 때문에 **지금 미리 열어두는 게 안전**합니다.

이번 작업으로 `backend/app/main.py` 에 다음이 추가되어 있습니다.

```python
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:3000",   # React
    "http://localhost:5173",   # Vite
    "http://localhost:8501",   # Streamlit
    # ... 필요한 곳 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

운영 환경에서는 `allow_origins=["*"]` 대신 **정확한 도메인만** 적는 게 보안상 권장입니다.

### 2-2. HTTP 통신 최적화 포인트

- **타임아웃 반드시 지정**: `requests.get(url, timeout=10)` 처럼 꼭 초를 적어 주세요. 지정하지 않으면 네트워크가 끊겼을 때 프론트가 영원히 멈춥니다.
- **오래 걸리는 작업 분리**: `/news/search`는 네이버 + OpenAI + DB 저장까지 하니 1분 넘게 걸릴 수 있습니다. 프론트에서 **로딩 스피너**(Streamlit의 `st.spinner`)를 보여주고, 필요하면 백엔드를 **비동기 작업(Celery/Background Tasks)**으로 빼고 `/news/jobs/{id}` 로 상태를 폴링하는 구조를 나중에 고려하세요.
- **캐싱**: 같은 카테고리를 반복 호출한다면 Streamlit의 `@st.cache_data(ttl=60)` 로 1분 정도 메모이즈하면 불필요한 네트워크가 줄어듭니다.
- **에러 처리는 UI까지 도달**: 백엔드 500이나 400이 나면 그냥 비어 보이지 않도록 `st.error("...")` 로 사용자에게 안내합니다.
- **환경변수로 주소 관리**: 하드코딩된 `http://127.0.0.1:8000` 대신 `NEWS_API_BASE_URL` 같은 환경변수를 써야 개발/운영 주소를 쉽게 바꿀 수 있습니다. (본 프로젝트 `utils/api_client.py` 가 이미 그렇게 돼 있습니다.)
- **보안**: API 키(OpenAI, 네이버)는 **백엔드에만** 둬야 합니다. 브라우저 프론트에 노출되면 누구나 훔쳐 쓸 수 있습니다.

## 3. 단계별 연결 방법

순서대로 따라 하시면 됩니다.

1. **환경 준비**
   - `.env` 파일에 DB 접속 정보, `CLIENT_ID`, `CLIENT_SECRET`, `OPENAI_API_KEY` 가 모두 채워져 있는지 확인합니다.
   - `conda env create -f environment.yml` 로 가상환경을 만들고 `conda activate news-agent`.
2. **백엔드 기동 (터미널 1)**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   브라우저에서 `http://127.0.0.1:8000/docs` 에 접속해 Swagger UI가 뜨는지 확인합니다. 여기서 `GET /health/ping` 을 눌러 `pong` 이 나오면 서버가 정상입니다.
3. **프론트엔드 기동 (터미널 2)**
   ```bash
   cd frontend
   streamlit run example_integration.py
   ```
   브라우저가 열리고 좌측 사이드바에 "백엔드 연결 OK ✅" 표시가 나타나야 합니다.
4. **검색 테스트**
   `example_integration.py` 에서 검색어를 입력하고 `검색 실행` 을 눌러 결과 카드가 뜨면 성공입니다.
5. **기존 app.py 붙이기**
   더미 데이터를 쓰는 위치를 찾습니다.
   ```python
   # frontend/app.py 내부
   from data.dummy_news import get_dummy_news      # ← 기존
   from utils.api_client import get_news_by_category, search_news  # ← 교체
   ```
   이제 각 탭이 더미 대신 백엔드에서 받아온 데이터를 쓰도록 한두 줄씩 바꿉니다. (예시는 아래 4번 참고)
6. **카테고리별 캐싱 추가 (선택)**
   ```python
   import streamlit as st
   from utils.api_client import get_news_by_category

   @st.cache_data(ttl=60)
   def load_news(category: str):
       return get_news_by_category(category)
   ```
7. **배포 시 CORS 재설정**: 배포 도메인이 생기면 `ALLOWED_ORIGINS` 에 그 도메인을 추가하거나 `NEWS_API_BASE_URL` 환경변수를 바꿉니다.

## 4. 최소 연동 코드 스니펫

### 4-1. 백엔드 (이미 반영됨 — `backend/app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health/ping")
def ping():
    return {"message": "pong"}
```

### 4-2. 프론트엔드 API 클라이언트 (`frontend/utils/api_client.py`)

```python
import os, requests

BASE_URL = os.getenv("NEWS_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

def search_news(query: str, count: int = 10) -> list[dict]:
    r = requests.post(
        f"{BASE_URL}/news/search",
        params={"query": query, "count": count},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()
```

### 4-3. Streamlit에서 받아 화면에 표시 (`frontend/example_integration.py` 핵심만)

```python
import streamlit as st
from utils.api_client import search_news

query = st.text_input("검색어", "인공지능")
if st.button("검색"):
    with st.spinner("백엔드 호출 중..."):
        items = search_news(query, count=3)
    for n in items:
        st.markdown(f"### {n['title']}")
        st.caption(n.get("category", ""))
        st.write(n.get("summary", ""))
        st.markdown(f"[원문 보기]({n['article_url']})")
```

## 5. 자주 발생하는 문제 체크리스트

- `ConnectionError` → 백엔드가 안 떠 있음. 터미널에서 `uvicorn` 이 실행 중인지 확인.
- 오래 기다려도 응답 없음 → OpenAI/네이버 API 키가 잘못됐거나 네트워크 차단. `http://127.0.0.1:8000/docs` 에서 직접 호출해 보세요.
- 브라우저 콘솔에 `CORS policy: ...` → `ALLOWED_ORIGINS` 에 현재 페이지 주소가 포함됐는지 확인.
- 한글 깨짐 → FastAPI/requests는 기본 UTF-8입니다. 파일 저장 시 인코딩을 UTF-8로 지정하세요.
- `/news/{article_url}` 이 404 → URL에 슬래시가 여러 개 있어 경로 파싱이 꼬이는 경우가 많습니다. 2번 절에서 권장한 대로 `id` 기반으로 바꾸는 걸 추천합니다.
