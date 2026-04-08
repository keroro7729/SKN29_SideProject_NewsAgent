from fastapi import FastAPI
from app.api.health_router import router as health_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="News Agent FastAPI App",
        version="1.0.0"
    )

    app.include_router(health_router)

    return app


app = create_app()