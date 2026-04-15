import copy
import html
import re
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from app.config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from app.infra.naver_client import NaverNewsClient

_naver: NaverNewsClient | None = None


def _get_naver_client() -> NaverNewsClient:
    global _naver
    if _naver is None:
        _naver = NaverNewsClient(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
    return _naver


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", text)
    text = re.sub(r"무단 전재 및 재배포 금지", "", text)
    text = re.sub(r"저작권자\(c\).*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Copyright.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def clean_title(title: str) -> str:
    if not title:
        return ""
    title = html.unescape(title)
    title = re.sub(r"<[^>]+>", "", title)
    return clean_text(title)


def clean_description(description: str) -> str:
    if not description:
        return ""
    description = html.unescape(description)
    description = re.sub(r"<[^>]+>", "", description)
    return clean_text(description)


def build_summary_input(title: str, content: str) -> str:
    title = clean_text(title)
    content = clean_text(content)
    if not content:
        return f"제목: {title}\n본문:"
    return f"제목: {title}\n본문:\n{content}"


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text


def is_naver_news_url(url: str) -> bool:
    return "news.naver.com" in url or "n.news.naver.com" in url


def filter_naver_news_items(items: list[dict]) -> list[dict]:
    return [item for item in items if is_naver_news_url(item.get("link", ""))]


def pick_best_url(item: Dict[str, Any]) -> str:
    return item.get("link", "")


def parse_naver_news(html_text: str) -> Dict[str, str]:
    soup = BeautifulSoup(html_text, "lxml")
    full_content = ""
    image_url = ""

    article_tag = soup.find("article", id="dic_area")
    if article_tag is None:
        article_tag = soup.find(id="newsct_article")

    if article_tag:
        for tag in article_tag.select(".img_desc"):
            tag.decompose()
        for tag in article_tag.select("script, style"):
            tag.decompose()
        full_content = article_tag.get_text(separator="\n", strip=True)

    full_content = clean_text(full_content)

    img_tag = soup.find("img", id="img1")
    if img_tag:
        image_url = (
            img_tag.get("data-src")
            or img_tag.get("src")
            or img_tag.get("data-lazy-src")
            or ""
        )
    if not image_url:
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = og_image["content"]

    return {"full_content": full_content, "image_url": image_url}


def crawl_article(url: str) -> Dict[str, str]:
    try:
        if not is_naver_news_url(url):
            return {
                "full_content": "",
                "image_url": "",
                "crawl_status": "failed",
                "error_message": "네이버 뉴스 URL이 아닙니다.",
            }
        html_text = fetch_html(url)
        parsed = parse_naver_news(html_text)
        return {
            "full_content": parsed.get("full_content", ""),
            "image_url": parsed.get("image_url", ""),
            "crawl_status": "success",
            "error_message": "",
        }
    except Exception as e:
        return {
            "full_content": "",
            "image_url": "",
            "crawl_status": "failed",
            "error_message": str(e),
        }


def enrich_item_for_summary_agent(item: dict) -> dict:
    result = copy.deepcopy(item)
    result["title"] = clean_title(result.get("title", ""))
    result["description"] = clean_description(result.get("description", ""))

    crawl_url = pick_best_url(result)
    result["crawl_url"] = crawl_url

    crawled = crawl_article(crawl_url)
    result["full_content"] = clean_text(crawled.get("full_content", ""))
    result["image_url"] = crawled.get("image_url", "")
    result["content_length"] = len(result["full_content"])
    result["crawl_status"] = crawled.get("crawl_status", "failed")
    result["error_message"] = crawled.get("error_message", "")

    result["summary_input"] = build_summary_input(
        title=result.get("title", ""),
        content=result["full_content"],
    )
    result.pop("originallink", None)
    return result


def filter_valid_articles_for_summary(
    news_response: Dict[str, Any], min_length: int = 100
) -> List[Dict[str, Any]]:
    valid_items = []
    for item in news_response.get("items", []):
        if item.get("crawl_status") != "success":
            continue
        if item.get("content_length", 0) < min_length:
            continue
        valid_items.append(item)
    return valid_items


def search_and_prepare_news_for_agent(query: str, target_count: int = 10) -> Dict[str, Any]:
    """
    네이버 뉴스 검색 후 크롤링·요약 입력까지 가공해 반환.
    최대 target_count개까지 수집한다.
    """
    client = _get_naver_client()
    start = 1
    chunk_size = 10
    collected_items: list[dict] = []
    seen_links: set[str] = set()

    while len(collected_items) < target_count and start <= 1000:
        news_response = client.get_news(
            query=query,
            display=chunk_size,
            start=start,
            sort="date",
        )
        items = news_response.get("items", [])
        if not items:
            break

        naver_items = filter_naver_news_items(items)
        for item in naver_items:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                collected_items.append(item)
                if len(collected_items) >= target_count:
                    break
        start += chunk_size

    collected_items = collected_items[:target_count]
    enriched_items = [enrich_item_for_summary_agent(item) for item in collected_items]

    return {
        "query": query,
        "display": len(enriched_items),
        "items": enriched_items,
    }
