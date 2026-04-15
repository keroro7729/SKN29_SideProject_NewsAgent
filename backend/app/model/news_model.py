# 네이밍 news_models.py 복수형도 괜찮을거 같네요

from typing import TypedDict
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.infra.db import Base

# ORM 모델
class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    full_content = Column(Text, nullable=True)
    article_url = Column(String(1000), nullable=False, unique=True)
    image_url = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    # 카테고리 태그(list)도 추가 + list 속성은 orm에서 어떻게 처리돼서 db에는 어떻게 될까?
    # crawl_status = Column(String(20), default="pending")
    # error_message = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NewsItem(TypedDict, total=False):
    title: str
    article_url: str
    published_at: datetime | None

    full_content: str           # 기사 전문
    image_url: str
    content_length: int

    #crawl_status: str
    #summary_status: str
    #error_message: str

    summary_input: str          # 요약 모델 입력용 텍스트
    summary: str                # LLM 요약 결과


class NewsSearchResponse(TypedDict, total=False):
    query: str                  # 사용자 검색 키워드
    display: int                # 반환 기사 수
    items: list[NewsItem]       # 기사 리스트





