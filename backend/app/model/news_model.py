from typing import TypedDict
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship
from app.infra.db import Base

news_tags = Table(
    "news_tags",
    Base.metadata,
    Column("news_id", ForeignKey("news.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

# ORM 모델
class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    full_content = Column(Text, nullable=True)
    article_url = Column(String(1000), nullable=False, unique=True)
    image_url = Column(Text, nullable=True)

    summary = Column(Text, nullable=True)
    category = Column(String(10), nullable=True)
    tags = relationship("Tag", secondary=news_tags, backref="news")

    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    crawl_status = Column(String(20), default="pending")
    summary_status = Column(String(20), default="pending")
    error_message = Column(Text, nullable=True)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)

class NewsItem(TypedDict, total=False):
    title: str
    article_url: str
    published_at: datetime | None

    full_content: str           # 기사 전문
    image_url: str
    content_length: int

    crawl_status: str
    summary_status: str
    error_message: str

    summary: str                # LLM 요약 결과
    category: str
    tags: list[str]


class NewsSearchResponse(TypedDict, total=False):
    query: str                  # 사용자 검색 키워드
    display: int                # 반환 기사 수
    items: list[NewsItem]       # 기사 리스트





