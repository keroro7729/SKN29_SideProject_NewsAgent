"""
채팅(메시지) 서비스.

/message/send 호출 시:
 1) 세션(없으면 생성) → 사용자 메시지 DB 저장
 2) 기존 대화 이력 로드 (최근 N턴)
 3) OpenAI 호출해서 응답 생성
 4) assistant 메시지 DB 저장 후 반환
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.infra.crud import (
    create_agent_session,
    create_message,
    get_agent_session,
    get_messages_by_session,
)
from app.infra.openai_client import OpenAIClient

log = logging.getLogger(__name__)

# 현재는 단일 세션만 사용. 추후 유저/세션 분리 시 파라미터화.
SESSION_ID = 1

# 채팅용 기본 시스템 프롬프트
_SYSTEM_PROMPT = (
    "당신은 NewsInsight의 뉴스 분석 AI입니다. "
    "사용자의 질문에 한국어로 명확하고 간결하게 답변하세요. "
    "핵심만 짚어 3~5문장 이내로 답변하되, 필요하면 불릿 포인트를 사용하세요."
)


def _ensure_session(db: Session):
    session = get_agent_session(db, SESSION_ID)
    if not session:
        session = create_agent_session(db, title="default session")
    return session


def _build_history(db: Session) -> list[dict]:
    """
    DB 의 Message 엔티티를 OpenAIClient 가 기대하는
    [{"role": "user"|"assistant", "content": "..."}] 형태로 변환.
    """
    msgs = get_messages_by_session(db, SESSION_ID)
    history: list[dict] = []
    for m in msgs:
        if m.role not in ("user", "assistant"):
            continue
        if not (m.content or "").strip():
            continue
        history.append({"role": m.role, "content": m.content})
    return history


def handle_user_message(
    db: Session,
    user_input: str,
    context: Optional[dict] = None,
) -> dict:
    """
    사용자 메시지 처리.
    context: {"title": "...", "body": "..."} 형태의 기사 컨텍스트 (선택)
    """
    _ensure_session(db)

    # 1) 사용자 메시지 저장 (이력에 포함시키기 전에)
    create_message(db, SESSION_ID, "user", user_input)

    # 2) 시스템 프롬프트 조립 (선택 기사 컨텍스트 반영)
    system_prompt = _SYSTEM_PROMPT
    if context:
        ctx_title = (context.get("title") or "").strip()
        ctx_body = (context.get("body") or context.get("summary") or "").strip()
        if ctx_title or ctx_body:
            system_prompt += (
                "\n\n[현재 분석 중인 기사]"
                f"\n제목: {ctx_title}"
                f"\n내용: {ctx_body[:1500]}"
                "\n이 기사와 관련된 질문에 우선 답변하세요."
            )

    # 3) 지금 막 저장한 user 메시지는 history 에 포함되면 안 됨(중복 방지)
    #    → 마지막 user 메시지를 제외한 나머지를 history 로 사용
    full_history = _build_history(db)
    if full_history and full_history[-1]["role"] == "user" and full_history[-1]["content"] == user_input:
        history = full_history[:-1]
    else:
        history = full_history

    # 4) OpenAI 호출 (실패 시 사용자 친화 메시지)
    try:
        client = OpenAIClient()
        result = client.send_message(
            system_prompt=system_prompt,
            user_input=user_input,
            history=history,
        )
        response_text = result.text
    except Exception as e:  # 키 누락 / 네트워크 / 모델 오류 등
        log.exception("OpenAI 호출 실패")
        response_text = "⚠️ 일시적으로 답변을 받아오지 못했어요. 잠시 후 다시 시도해주세요."

    # 5) assistant 메시지 저장
    create_message(db, SESSION_ID, "assistant", response_text)

    return {"response": response_text}


def get_all_messages(db: Session):
    messages = get_messages_by_session(db, SESSION_ID)
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at}
        for m in messages
    ]
