from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
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





#######################################################################################
# crawling
#######################################################################################

def get_news_by_article_url(db: Session, article_url: str) -> News | None:
    if not article_url:
        return None
    return db.query(News).filter(News.article_url == article_url).first()

def create_news_articles(db: Session, items: list[NewsItem]) -> list[News]:
    """
    뉴스 여러 건 저장
    - article_url 기준 중복 스킵
    - 빈 article_url 스킵
    """
    if not items:
        return []

    saved: list[News] = []

    # 입력 데이터에서 유효한 URL만 추출
    article_urls = {
        item.get("article_url", "").strip()
        for item in items
        if item.get("article_url")
    }

    # 기존 URL 한 번에 조회
    existing_urls = {
        row[0]
        for row in db.query(News.article_url)
        .filter(News.article_url.in_(article_urls))
        .all()
    }

    try:
        for item in items:
            article_url = item.get("article_url", "").strip()
            if not article_url:
                continue

            if article_url in existing_urls:
                continue

            news = News(
                title=item.get("title", ""),
                full_content=item.get("full_content"),
                article_url=article_url,
                image_url=item.get("image_url"),
                summary=item.get("summary"),
                #crawl_status=item.get("crawl_status", "pending"),
                #summary_status=item.get("summary_status", "pending"),
                #error_message=item.get("error_message"),
                published_at=item.get("published_at"),
            )
            db.add(news)
            saved.append(news)
            existing_urls.add(article_url)

        db.commit()

        for news in saved:
            db.refresh(news)

        return saved

    except SQLAlchemyError:
        db.rollback()
        raise


def save_summary_result(db: Session, article_id: int, summary: str) -> News | None:
    """
    요약 결과 저장
    """
    news = db.query(News).filter(News.id == article_id).first()
    if not news:
        return None

    try:
        news.summary = summary
        # news.summary_status = "success"
        db.commit()
        db.refresh(news)
        return news

    except SQLAlchemyError:
        db.rollback()
        raise

