# app/model/news.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.infra.db import Base


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