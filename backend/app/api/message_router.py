from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.infra.db import get_db
from app.service.message_service import handle_user_message, get_all_messages

router = APIRouter(
    prefix="/message",
    tags=["message"]
)


class SendRequest(BaseModel):
    text: str


@router.post("/send")
def send(req: SendRequest, db: Session = Depends(get_db)):
    return handle_user_message(db, req.text)


@router.get("/view_all")
def view_all(db: Session = Depends(get_db)):
    return get_all_messages(db)