from sqlalchemy.orm import Session
from app.model.agent_session import AgentSession
from app.model.message import Message
from datetime import datetime
from app.model.news import News
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
# 뉴스 기사 저장/조회/요약 결과 저장 관련 함수 (임시)
#######################################################################################

def parse_pub_date(pub_date_str: str | None) -> datetime | None:
    """네이버 API pubDate 문자열 → datetime 변환"""
    if not pub_date_str:
        return None
    try:
        return datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
    except ValueError:
        return None

def create_news_articles(db: Session, items: list[NewsItem]) -> list[News]:
    """뉴스 아이템 리스트 전체 저장, 중복 링크는 스킵"""
    saved = []

    for item in items:
        link = item.get("link") or item.get("crawl_url", "")

        # 중복 체크
        if db.query(News).filter(News.link == link).first():
            continue

        news = News(
            title         = item.get("title", ""),
            description   = item.get("description"),
            full_content  = item.get("full_content"),
            link          = link,
            original_link = item.get("originallink"),
            image_url     = item.get("image_url"),
            crawl_status  = item.get("crawl_status", "failed"),
            error_message = item.get("error_message"),
            pub_date      = parse_pub_date(item.get("pubDate")),
        )
        db.add(news)
        saved.append(news)

    db.commit()

    for news in saved:
        db.refresh(news)

    return saved

def get_news_by_link(db: Session, link: str) -> News | None:
    """링크로 기사 조회"""
    return db.query(News).filter(News.link == link).first()


def save_summary_result(db: Session, article_id: int, summary: str) -> News | None:
    """요약 결과 저장 (LLM 요약 완료 후 UPDATE)"""
    news = db.query(News).filter(News.id == article_id).first()
    if not news:
        return None
    news.summary = summary
    db.commit()
    db.refresh(news)
    return news