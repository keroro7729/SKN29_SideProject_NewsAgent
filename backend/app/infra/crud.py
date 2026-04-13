from sqlalchemy.orm import Session
from app.model.agent_session import AgentSession
from app.model.message import Message


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

def create_news_article(db, article_data: dict):
    """
    기사 저장
    """
    pass


def get_news_by_link(db, link: str):
    """
    링크로 기사 조회
    """
    pass


def save_summary_result(db, article_id: int, summary: str):
    """
    요약 결과 저장
    """
    pass