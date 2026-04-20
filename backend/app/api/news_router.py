from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infra.db import get_db
from app.infra.crud import create_news, get_news_by_article_url, get_news_list_by_category
from app.service.news_service import search_and_prepare_news_for_agent, to_news_entity
from app.model.news_model import NewsSearchResponse
from app.service.news_refine_service import NewsRefineService

router = APIRouter(
    prefix="/news",
    tags=["news"],
)

@router.post("/search", response_model=None)
def search_and_save_news(query: str, count: int = 10, db: Session = Depends(get_db)):
    """
    뉴스 검색 + 크롤링 + 요약, 카테고리, 태그 추가 + DB 저장
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="query를 입력해주세요.")

    result: NewsSearchResponse = search_and_prepare_news_for_agent(query=query, target_count=count)
    items = result.get("items", [])

    news_models = []
    refiner = NewsRefineService()
    for item in items:
        input = item.get('title') + '\n' + item.get('full_content')
        news_summary = refiner.get_summary_category(input)
        item['summary'] = news_summary.summary
        item['category'] = news_summary.category
        item['tags'] = news_summary.tags
        news_models.append(to_news_entity(item, db=db))

    saved_models = create_news(db=db, news_list=news_models)
    return [
        {
            "title": news.title,
            "category": news.category,
            "full_content": news.full_content,
            "summary": news.summary,
            "tags": news.tags,
            "article_url": news.article_url,
            "image_url": news.image_url,
        }
        for news in saved_models
    ]

@router.get("")
def get_news(category: str, db: Session = Depends(get_db)):
    return get_news_list_by_category(db, category)

@router.get("/{article_url:path}")
def get_news(article_url: str, db: Session = Depends(get_db)):
    """
    article_url로 저장된 뉴스 단건 조회
    """
    news = get_news_by_article_url(db=db, article_url=article_url)
    if not news:
        raise HTTPException(status_code=404, detail="해당 뉴스를 찾을 수 없습니다.")
    return news

