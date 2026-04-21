"""
백엔드(FastAPI) API 호출 헬퍼

- 프론트엔드(Streamlit)에서 백엔드와 통신할 때 공용으로 쓰는 함수 모음입니다.
- BASE_URL은 환경변수 `NEWS_API_BASE_URL` 로 덮어쓸 수 있고,
  기본값은 로컬 개발 환경(`http://127.0.0.1:8000`)입니다.
- 네트워크 에러/타임아웃/HTTP 에러를 모두 잡아 빈 결과 혹은 예외 메시지를
  안전하게 반환하도록 작성했습니다. (UI가 죽지 않도록)
"""
from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import requests

log = logging.getLogger(__name__)

# 기본 백엔드 주소 (uvicorn 기본 포트 8000)
BASE_URL = os.getenv("NEWS_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# 외부 API(네이버 검색 + OpenAI 요약)를 태우는 엔드포인트는 응답이 느릴 수 있으므로
# 타임아웃을 넉넉하게 둡니다.
DEFAULT_TIMEOUT = 10      # 일반 조회용
LONG_TIMEOUT = 60         # /news/search 같이 오래 걸리는 작업용


# ─────────────────────────────── 공용 헬퍼 ───────────────────────────────
def _handle(resp: requests.Response) -> Any:
    """공통 응답 처리: 2xx면 JSON 반환, 아니면 예외."""
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        log.error("API 오류 %s %s: %s", resp.status_code, resp.url, resp.text[:500])
        raise
    if not resp.content:
        return None
    return resp.json()


# ─────────────────────────────── health ────────────────────────────────
def ping() -> bool:
    """백엔드 서버가 살아있는지 확인."""
    try:
        r = requests.get(f"{BASE_URL}/health/ping", timeout=DEFAULT_TIMEOUT)
        return r.ok and r.json().get("message") == "pong"
    except requests.RequestException:
        return False


# ─────────────────────────────── news ──────────────────────────────────
def search_news(query: str, count: int = 10) -> list[dict]:
    """
    검색어로 뉴스 검색 + 크롤링 + 요약/카테고리/태그 생성 + DB 저장까지 수행.
    반환값: [{title, category, summary, full_content, tags, article_url, image_url}, ...]
    """
    r = requests.post(
        f"{BASE_URL}/news/search",
        params={"query": query, "count": count},
        timeout=LONG_TIMEOUT,
    )
    print("뉴스 검색 request: ", r)
    return _handle(r) or []


def get_news_by_category(category: str) -> list[dict]:
    """카테고리별 저장된 뉴스 목록 조회."""
    r = requests.get(
        f"{BASE_URL}/news",
        params={"category": category},
        timeout=DEFAULT_TIMEOUT,
    )
    print(" 뉴스 카테고리 조회 request: ", r)
    return _handle(r) or []


def get_news_detail(article_url: str) -> dict | None:
    """article_url 로 뉴스 단건 조회."""
    # 경로에 URL 전체를 붙이므로 인코딩 처리 없이 그대로 전달
    r = requests.get(f"{BASE_URL}/news/{article_url}", timeout=DEFAULT_TIMEOUT)
    if r.status_code == 404:
        return None
    return _handle(r)


# ─────────────────────────────── message (AI 채팅) ──────────────────────
def send_message(text: str, context: dict | None = None) -> dict:
    """
    사용자 메시지를 백엔드로 보내고 AI 응답을 받음.
    context: {"title": "...", "body": "..."} 형태 (선택)
    반환: {"response": "..."}
    """
    payload: dict = {"text": text}
    if context:
        payload["context"] = {
            "title": context.get("title"),
            "body": context.get("body") or context.get("summary"),
            "summary": context.get("summary"),
        }
    r = requests.post(
        f"{BASE_URL}/message/send",
        json=payload,
        timeout=LONG_TIMEOUT,
    )
    return _handle(r) or {}


def list_messages() -> list[dict]:
    """지금까지 저장된 전체 메시지 조회."""
    r = requests.get(f"{BASE_URL}/message/view_all", timeout=DEFAULT_TIMEOUT)
    return _handle(r) or []


# ─────────────────────────────── 어댑터 ──────────────────────────────────
# 백엔드 응답 필드와 프론트(article_card/filters) 에서 쓰는 필드가 다르므로
# 변환 함수로 맞춰 줍니다. 백엔드 API 가 확장되면 이 함수만 수정하면 됩니다.

_PRESS_MAP = {
    "news.naver.com": "네이버뉴스",
    "n.news.naver.com": "네이버뉴스",
    "yna.co.kr": "연합뉴스",
    "ytn.co.kr": "YTN",
    "kbs.co.kr": "KBS",
    "mbc.co.kr": "MBC",
    "sbs.co.kr": "SBS",
    "jtbc.co.kr": "JTBC",
    "hani.co.kr": "한겨레",
    "khan.co.kr": "경향신문",
    "mk.co.kr": "매일경제",
    "hankyung.com": "한국경제",
    "sedaily.com": "서울경제",
    "mt.co.kr": "머니투데이",
    "asiae.co.kr": "아시아경제",
    "etnews.com": "전자신문",
    "zdnet.co.kr": "ZDNet Korea",
    "it.chosun.com": "IT조선",
    "dt.co.kr": "디지털타임스",
}


def _press_from_url(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""
    # 정확 매칭 → 부분 매칭
    if host in _PRESS_MAP:
        return _PRESS_MAP[host]
    for k, v in _PRESS_MAP.items():
        if k in host:
            return v
    return host  # 못 찾으면 호스트 그대로


def adapt_article(n: dict) -> dict:
    """
    백엔드 뉴스 dict → 프론트 카드에서 기대하는 dict 로 변환.
    누락된 필드는 안전한 기본값으로 채웁니다.
    """
    title = n.get("title", "")
    summary = n.get("summary", "") or ""
    article_url = n.get("article_url", "") or ""
    full_content = n.get("full_content", "") or ""

    # 짧은 설명(desc): summary 첫 줄 또는 full_content 앞 120자
    first_line = summary.split("\n", 1)[0].lstrip("• ").strip()
    desc = first_line or full_content[:120]

    return {
        "title": title,
        "desc": desc,
        "summary": summary,
        "category": n.get("category", "전체"),
        "sentiment": n.get("sentiment", "중립"),   # 백엔드 확장 시 사용
        "source": _press_from_url(article_url),
        "date": datetime.now().strftime("%Y.%m.%d %H:%M"),
        "views": 0,
        "link": article_url,
        "image_url": n.get("image_url", ""),
        "tags": n.get("tags", []),
    }


def adapt_articles(items: list[dict]) -> list[dict]:
    return [adapt_article(n) for n in items]

