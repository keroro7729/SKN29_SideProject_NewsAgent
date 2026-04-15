from fastapi import FastAPI
from app.api.health_router import router as health_router
from app.api.message_router import router as message_router
from app.api.news_router import router as news_router
from app.infra.db import init_db

def create_app() -> FastAPI:
    app = FastAPI(
        title="News Agent FastAPI App",
        version="1.0.0"
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
    # Base.metadata.create_all(bind=engine) # db에 기능 있음
    # 테이블 자동 생성기능. 편리하지만 주의해야할 점이 많은 기능임


