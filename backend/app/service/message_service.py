from sqlalchemy.orm import Session
from app.service.chatbot_service import ChatBotService

from app.infra.crud import (
    get_agent_session,
    create_agent_session,
    create_message,
    get_messages_by_session,
)


SESSION_ID = 1


def handle_user_message(db: Session, user_input: str):
    # 세션 확인 (없으면 생성)
    session = get_agent_session(db, SESSION_ID)
    if not session:
        session = create_agent_session(db, title="default session")

    create_message(db, SESSION_ID, "user", user_input)

    # chatbot = ChatBotService()
    # response = chatbot.response(user_input)
    response = '임시 응답'
    create_message(db, SESSION_ID, "assistant", response)

    return {
        "response": response
    }


def get_all_messages(db: Session):
    messages = get_messages_by_session(db, SESSION_ID)

    return [
        {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in messages
    ]