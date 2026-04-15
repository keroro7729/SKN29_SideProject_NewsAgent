from typing import TypedDict
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.infra.db import Base

# ORM 모델
class News(Base):
    __tablename__ = "news"

    id            = Column(Integer, primary_key=True, index=True)
    title         = Column(String(500), nullable=False)
    description   = Column(Text, nullable=True)
    full_content  = Column(Text, nullable=True)
    link          = Column(Text, nullable=True)
    original_link = Column(Text, nullable=True)
    image_url     = Column(Text, nullable=True)
    summary       = Column(Text, nullable=True)
    crawl_status  = Column(String(20), default="pending")
    error_message = Column(Text, nullable=True)
    pub_date      = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# 1개 뉴스 구조 정의
class NewsItem(TypedDict, total=False):
    title: str
    description: str
    link: str
    originallink: str
    pubDate: str
    crawl_url: str
    full_content: str           # 본문 전체 텍스트
    image_url: str
    content_length: int
    crawl_status: str
    error_message: str
    summary_input: str          # 요약 모델에 입력할 텍스트
    summary: str                # LLM 요약 결과


# 뉴스 검색 결과 전체 구조 반환시 형태
class NewsSearchResponse(TypedDict, total=False):
    query: str                  # 사용자 검색 키워드
    display: int                # 검색 결과 수 ( 10개 )
    items: list[NewsItem]       # 기사 리스트



