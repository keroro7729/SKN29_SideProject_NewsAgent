import os
import random
import logging
import streamlit as st

# 로거 설정
log = logging.getLogger(__name__)

# ── 더미 응답 풀 ─────────────────────────────────────────────────────────────
_DUMMY_REPLIES = [
    "현재 OpenAI API 키가 설정되지 않아 더미 응답을 반환합니다.\n\n"
    "실제 AI 분석을 사용하려면 프로젝트 루트의 `.env` 파일에\n"
    "`OPENAI_API_KEY=sk-...` 를 추가해 주세요.",

    "**[더미 응답]** 해당 뉴스는 최근 가장 많이 언급된 이슈 중 하나입니다.\n\n"
    "• 긍정적 측면: 관련 산업 성장과 일자리 창출 기대\n"
    "• 부정적 측면: 단기적 시장 변동성 증가 우려\n"
    "• 향후 전망: 전문가 의견이 갈리는 상황",

    "**[더미 응답]** 요약하자면 세 가지 핵심 포인트가 있습니다.\n\n"
    "1. 이슈의 배경과 원인\n"
    "2. 현재 이해관계자들의 입장\n"
    "3. 예상 시나리오 및 대응 방향",
]

@st.cache_resource
def _get_openai_client():
    """OpenAI 클라이언트를 반환합니다. 실패 시 None."""
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or not key.startswith("sk-"):
            return None
        return OpenAI(api_key=key)
    except ImportError:
        return None


def chat_with_gpt(
    messages: list[dict],
    user_message: str,
    context_article: dict | None = None,
) -> str:
    """
    GPT 기반 뉴스 AI 어시스턴트 채팅 응답을 생성합니다.

    Parameters
    ----------
    messages        : 이전 대화 이력 [{"role": "user"|"assistant", "text": str}]
    user_message    : 현재 사용자 입력
    context_article : 채팅에 전달할 기사 컨텍스트 dict
                      (title, body, summary 키 포함)

    Returns
    -------
    str  AI 응답 텍스트 (Markdown 포함 가능)
    """
    client = _get_openai_client()
    if client is None:
        return random.choice(_DUMMY_REPLIES)

    # ── 시스템 프롬프트 구성 ──────────────────────────────────────────────────
    system = (
        "당신은 NewsInsight의 뉴스 분석 AI입니다. "
        "사용자의 질문에 명확하고 간결하게 한국어로 답변하세요. "
        "핵심만 짚어 3~5문장 이내로 답변하되, 필요시 불릿 포인트를 사용하세요."
    )

    if context_article:
        system += (
            f"\n\n[현재 분석 중인 기사]\n"
            f"제목: {context_article.get('title', '')}\n"
            f"내용: {context_article.get('body', context_article.get('summary', ''))[:1500]}\n"
            "이 기사와 관련된 질문에 우선 답변하세요."
        )

    # ── 대화 이력 구성 (최근 10턴) ───────────────────────────────────────────
    history = [{"role": "system", "content": system}]
    for m in messages[-10:]:
        history.append({
            "role": m.get("role", "user"),
            "content": m.get("text", ""),
        })
    history.append({"role": "user", "content": user_message})

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            max_tokens=600,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    
    except Exception as e:
        # 1. 에러 상세 내용은 터미널(콘솔)에 기록 (디버깅용)
        log.exception("OpenAI API 호출 중 오류 발생") 
        # 2. 사용자에게는 안전하고 깔끔한 메시지만 반환
        return "⚠️ 일시적으로 답변을 받아오지 못했어요. 잠시 후 다시 시도해주세요."


def summarize_article(title: str, body: str) -> str:
    """
    기사 제목과 본문을 받아 3~5줄 불릿 요약을 반환합니다.
    (더미 데이터 사용 시 호출되지 않으나, 실제 크롤링 연동 시 활용)

    Parameters
    ----------
    title : str  기사 제목
    body  : str  기사 본문 (최대 3000자 권장)

    Returns
    -------
    str  "• ...\n• ...\n• ..." 형식의 요약
    """
    client = _get_openai_client()
    if client is None:
        return "• API 키가 없어 요약을 생성할 수 없습니다.\n• .env 파일에 OPENAI_API_KEY를 설정해주세요."

    prompt = (
        f"다음 뉴스 기사를 3~5개의 핵심 불릿 포인트로 요약하세요. "
        f"각 줄은 '• '로 시작하고 한국어로 작성하세요.\n\n"
        f"제목: {title}\n본문: {body[:2000]}"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    
    except Exception as e:
        log.exception("요약 생성 실패")
        return "• 요약 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."