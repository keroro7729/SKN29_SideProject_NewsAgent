from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infra.db import get_db
from app.infra.crud import create_news_articles, get_news_by_article_url
from app.service.news_service import search_and_prepare_news_for_agent
from app.model.news_model import NewsSearchResponse

router = APIRouter(
    prefix="/news",
    tags=["news"],
)

# 검색 -> api 나가고 크롤링 db저장까지
@router.post("/search", response_model=None)
def search_and_save_news(query: str, count: int = 10, db: Session = Depends(get_db)):
    """
    뉴스 검색 + 크롤링 + DB 저장
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="query를 입력해주세요.")

    result: NewsSearchResponse = search_and_prepare_news_for_agent(query=query, target_count=count)
    items = result.get("items", [])

    saved = create_news_articles(db=db, items=items) # crud 라우터 레벨에서 호출, 서비스에 있으면 좋지 않을까?

    return {
        "query": result.get("query"),
        "fetched": len(items),
        "saved": len(saved),
    }


# 기사 url을 키 같이 사용하기로 했나본데? 괜찮은데? 아주 좋습니다.
# 단건 조회 미리 만들어둔것도 좋은거 같습니다.
@router.get("/{article_url:path}")
def get_news(article_url: str, db: Session = Depends(get_db)):
    """
    article_url로 저장된 뉴스 단건 조회
    """
    news = get_news_by_article_url(db=db, article_url=article_url)
    if not news:
        raise HTTPException(status_code=404, detail="해당 뉴스를 찾을 수 없습니다.")
    return news
