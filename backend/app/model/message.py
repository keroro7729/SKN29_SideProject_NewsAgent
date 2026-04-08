from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.infra.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    agent_session_id = Column(Integer, ForeignKey("agent_sessions.id"))
    role = Column(String(50))  # user / assistant
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    #agent_session = relationship("AgentSession", back_populates='message')