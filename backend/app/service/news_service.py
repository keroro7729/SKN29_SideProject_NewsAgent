from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List

from app.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from app.infra.naver_client import NaverNewsClient
from app.service.crawl_service import clean_text, crawl_article
from app.model.news_model import NewsItem, News, Tag

_naver: NaverNewsClient | None = None


def _get_naver_client() -> NaverNewsClient:
    global _naver
    if _naver is None:
        _naver = NaverNewsClient(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
    return _naver


def to_news_entity(item: NewsItem, db) -> News:
    news = News(
        title=item["title"],
        full_content=item["full_content"],
        article_url=item["article_url"],
        image_url=item["image_url"],
        summary=item.get("summary"),
        category=item.get("category"),
    )

    news.tags = get_or_create_tags(db, item.get("tags", []))
    return news

def get_or_create_tags(db, tag_names: list[str]) -> list[Tag]:
    if not tag_names:
        return []
    
    # 1. 이미 존재하는 태그 조회
    existing_tags = db.query(Tag).filter(Tag.name.in_(tag_names)).all()
    existing_map = {tag.name: tag for tag in existing_tags}

    result = []
    new_tags_added = False
    
    for name in set(tag_names):
        if name in existing_map:
            result.append(existing_map[name])
        else:
            tag = Tag(name=name)
            db.add(tag)
            result.append(tag)
            new_tags_added = True

    # 2. 새로 추가된 태그가 있다면 flush해서 DB 세션에 상태를 동기화
    if new_tags_added:
        db.flush() 

    return result

def parse_pub_date(pub_date: str | None) -> datetime | None:
    if not pub_date:
        return None
    try:
        return parsedate_to_datetime(pub_date)
    except Exception:
        return None


def enrich_news_item(raw_item: dict) -> dict:
    article_url = raw_item.get("link", "").strip()
    crawled = crawl_article(article_url)
    full_content = crawled["full_content"]

    result = {
        "title": clean_text(raw_item.get("title", "")),
        "article_url": article_url,
        "published_at": parse_pub_date(raw_item.get("pubDate")),
        "full_content": full_content,
        "image_url": crawled["image_url"],
        "summary": None,
        "crawl_status": crawled["crawl_status"],
        "error_message": crawled["error_message"],
        "content_length": len(full_content),
    }
    print('크롤링 결과: ', result)
    return result


def filter_valid_articles_for_summary(
    news_response: Dict[str, Any], min_length: int = 100
) -> List[Dict[str, Any]]:
    return [
        item for item in news_response.get("items", [])
        if item.get("crawl_status") == "success"
        and item.get("content_length", 0) >= min_length
    ]


def search_and_prepare_news_for_agent(
    query: str,
    target_count: int = 10,
) -> Dict[str, Any]:
    client = _get_naver_client()
    collected_items: list[dict] = []
    seen_urls: set[str] = set()
    start = 1
    chunk_size = 10

    while len(collected_items) < target_count and start <= 1000:
        items = client.get_news(
            query=query, display=chunk_size, start=start, sort="date"
        ).get("items", [])

        if not items:
            break

        for item in items:
            url = item.get("link", "").strip()
            if not url or url in seen_urls:
                continue
            if "news.naver.com" not in url and "n.news.naver.com" not in url:
                continue

            seen_urls.add(url)
            collected_items.append(item)

            if len(collected_items) >= target_count:
                break

        start += chunk_size

    enriched_items = [enrich_news_item(item) for item in collected_items[:target_count]]

    return {
        "query": query,
        "display": len(enriched_items),
        "items": enriched_items,
    }
