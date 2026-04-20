import html
import re

import requests
from bs4 import BeautifulSoup


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


def parse_naver_news(html_text: str) -> dict[str, str]:
    soup = BeautifulSoup(html_text, "lxml")

    article_tag = soup.find("article", id="dic_area") or soup.find(id="newsct_article")

    full_content = ""
    if article_tag:
        for tag in article_tag.select(".img_desc, script, style"):
            tag.decompose()
        full_content = clean_text(article_tag.get_text(separator="\n", strip=True)).replace('<b>','').replace('</b>','')
        
    date_tag = soup.select_one("span.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
    
    published_at = ""
    if date_tag:
        published_at = date_tag.get_text(strip=True)

    # 이미지: id=img1 우선, 없으면 og:image
    img_tag = soup.find("img", id="img1")
    if img_tag:
        image_url = (
            img_tag.get("data-src")
            or img_tag.get("src")
            or img_tag.get("data-lazy-src")
            or ""
        )
    else:
        og = soup.find("meta", property="og:image")
        image_url = og["content"] if og and og.get("content") else ""

    return {"full_content": full_content, "image_url": image_url, "published_at": published_at}


def crawl_article(article_url: str) -> dict[str, str]:
    if "news.naver.com" not in article_url and "n.news.naver.com" not in article_url:
        return {
            "full_content": "",
            "image_url": "",
            "crawl_status": "failed",
            "error_message": "네이버 뉴스 URL이 아닙니다.",
        }
    try:
        parsed = parse_naver_news(fetch_html(article_url))
        full_content = parsed["full_content"]
        published_at = parsed["published_at"]
        return {
            "full_content": full_content,
            "image_url": parsed["image_url"],
            "crawl_status": "success" if full_content else "failed",
            "error_message": "" if full_content else "본문 추출 실패",
            "published_at": published_at
        }
    except Exception as e:
        return {
            "full_content": "",
            "image_url": "",
            "crawl_status": "failed",
            "error_message": str(e),
            "published_at": ""
        }

