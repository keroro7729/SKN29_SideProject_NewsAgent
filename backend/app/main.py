from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health_router import router as health_router
from app.api.message_router import router as message_router
from app.api.news_router import router as news_router
from app.infra.db import init_db

# 프론트엔드에서 브라우저로 직접 API를 호출하는 경우를 대비해
# 개발 환경의 주요 오리진(Streamlit 8501, React/Vite 5173, 3000 등)을 허용합니다.
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8501",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8501",
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="News Agent FastAPI App",
        version="1.0.0"
    )

    # CORS: 브라우저에서 다른 포트/도메인의 API를 호출할 때 필요
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(message_router)
    app.include_router(news_router)

    return app

app = create_app()

@app.on_event("startup")
def startup():
    # model import가 여기서 이루어져야 순환 참조 없음
    from app.infra.db import Base, engine
    from app.model import agent_session, message, news_model  # noqa: F401
    init_db()

