from fastapi import FastAPI
from app.api.health_router import router as health_router
from app.api.message_router import router as message_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="News Agent FastAPI App",
        version="1.0.0"
    )

    app.include_router(health_router)
    app.include_router(message_router)

    return app


app = create_app()



########################################################################################
# 뉴스 크롤링 출력 (임시)
########################################################################################

from pprint import pprint
from app.service.news_service import search_and_prepare_news_for_agent

if __name__ == "__main__":
    query = input("검색어를 입력하세요: ").strip()

    if not query:
        print("검색어가 비어 있습니다.")
        raise SystemExit(1)

    result = search_and_prepare_news_for_agent(query=query, target_count=10)
    pprint(result, sort_dicts=False)