from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.infra.db import get_db
from app.service.message_service import handle_user_message, get_all_messages

router = APIRouter(
    prefix="/message",
    tags=["message"]
)


class ChatContext(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    summary: Optional[str] = None


class SendRequest(BaseModel):
    text: str
    # 선택된 기사/검색 컨텍스트. 없으면 일반 대화.
    context: Optional[ChatContext] = None


@router.post("/send")
def send(req: SendRequest, db: Session = Depends(get_db)):
    ctx = req.context.model_dump() if req.context else None
    return handle_user_message(db, req.text, context=ctx)


@router.get("/view_all")
def view_all(db: Session = Depends(get_db)):
    return get_all_messages(db)
