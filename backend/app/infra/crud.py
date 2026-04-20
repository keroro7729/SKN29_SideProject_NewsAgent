from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from app.model.agent_session import AgentSession
from app.model.message import Message
from datetime import datetime
from app.model.news_model import News 
from app.model.news_model import NewsItem

# ------------------------
# AgentSession
# ------------------------

def create_agent_session(db: Session, title: str | None = None) -> AgentSession:
    session = AgentSession(title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_agent_session(db: Session, session_id: int) -> AgentSession | None:
    return db.query(AgentSession).filter(AgentSession.id == session_id).first()

# agent session list 조회 (사용자별?)

# ------------------------
# Message
# ------------------------

def create_message(
    db: Session,
    session_id: int,
    role: str,
    content: str
) -> Message:
    message = Message(
        agent_session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_by_session(
    db: Session,
    session_id: int
) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.agent_session_id == session_id)
        .order_by(Message.created_at.asc())
        .all() # pagenation 고려
    )

# ------------------------
# News
# ------------------------


def get_news_by_article_url(db: Session, article_url: str) -> News | None:
    if not article_url:
        return None
    return db.query(News).filter(News.article_url == article_url).first()

def get_news_by_id(db: Session, id: int) -> News | None:
    return db.query(News).filter(News.id == id).first()

def create_news(db: Session, news_list: list[News]) -> int:
    if not news_list:
        return 0

    urls = [n.article_url for n in news_list]

    existing_urls = set(
        db.execute(
            select(News.article_url).where(News.article_url.in_(urls))
        ).scalars().all()
    )

    filtered = [n for n in news_list if n.article_url not in existing_urls]

    if not filtered:
        return 0

    db.add_all(filtered)
    db.commit()

    return len(filtered)
