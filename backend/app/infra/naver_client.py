import html
import logging
import re
from datetime import datetime

import requests

logger = logging.getLogger(__name__)


class NaverNewsClient:
    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not isinstance(client_id, str):
            raise ValueError("client_id가 올바르지 않습니다")
        if not client_secret or not isinstance(client_secret, str):
            raise ValueError("client_secret이 올바르지 않습니다")

        self.client_id = client_id
        self.client_secret = client_secret

    def get_news(
        self,
        query: str,
        display: int = 10,
        start: int = 1,
        sort: str = "date",
    ) -> dict:
        if not query or not isinstance(query, str):
            raise ValueError("query는 비어 있지 않은 문자열이어야 합니다")

        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        display = max(1, min(display, 100))
        start = max(1, min(start, 1000))
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort,
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 401:
                raise RuntimeError("인증 실패: client_id 또는 client_secret 확인 필요")
            if response.status_code == 403:
                raise RuntimeError("접근 거부: API 권한 또는 호출 제한 확인")
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"API 요청 시간 초과: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API 요청 실패: {e}") from e

        try:
            data = response.json()
            if "errorCode" in data:
                raise RuntimeError(f"API 오류: {data.get('errorMessage')}")
            return data
        except ValueError as e:
            raise RuntimeError(f"JSON 파싱 실패: {e}") from e

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = re.sub("<.*?>", "", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def format_date(self, date_str: str | None):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            return None

    def parse_news(self, data: dict) -> list[dict]:
        if not isinstance(data, dict):
            raise ValueError("data는 dict 형태여야 합니다")
        items = data.get("items")
        if not isinstance(items, list):
            return []

        results = []
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                url = item.get("link", "") or ""
                if not url.startswith("https://n.news.naver.com"):
                    continue
                url = url.split("?")[0]
                title = self.clean_text(item.get("title"))
                content = self.clean_text(item.get("description"))
                pub_date = self.format_date(item.get("pubDate"))
                results.append(
                    {
                        "title": title,
                        "content": content,
                        "url": url,
                        "originallink": item.get("originallink", "") or "",
                        "date": pub_date,
                    }
                )
            except Exception as e:
                logger.warning("뉴스 항목 파싱 실패: %s", e)
                continue
        return results

    def get_clean_news(self, query: str, display: int = 1, start: int = 1) -> list[dict]:
        try:
            raw_data = self.get_news(query, display, start)
            return self.parse_news(raw_data)
        except Exception as e:
            logger.warning("뉴스 조회 실패: %s", e)
            return []
