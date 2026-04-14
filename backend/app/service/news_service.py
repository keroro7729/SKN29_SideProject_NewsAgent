import re
import copy
import html
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup

from app.api.config import (
    NAVER_CLIENT_ID,
    NAVER_CLIENT_SECRET,
    NAVER_NEWS_API_URL,
)



# --------------------------------------------------
# 1. 텍스트 정리
# --------------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""

    # HTML 엔티티 복원 
    text = html.unescape(text)

    # <br> 처리 후 남은 공백/줄바꿈 정리
    text = text.replace("\xa0", " ")

    # 이메일 제거
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", text)

    # 저작권/재배포 문구 제거
    text = re.sub(r"무단 전재 및 재배포 금지", "", text)
    text = re.sub(r"저작권자\(c\).*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Copyright.*", "", text, flags=re.IGNORECASE)

    # 공백/줄바꿈 정리
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def clean_title(title: str) -> str:
    
    # 네이버 API title에 <b> 태그가 포함 -> 제거
    if not title:
        return ""
    title = html.unescape(title)                        # html 특수문자를 원래 문자로 변환
    title = re.sub(r"<[^>]+>", "", title)               # 특수문자 제거
    return clean_text(title)


def clean_description(description: str) -> str:

    # 네이버 AP description에도 <b> 태그 포함 -> 제거
    if not description:
        return ""
    description = html.unescape(description)            # html 특수문자를 원래 문자로 변환      
    description = re.sub(r"<[^>]+>", "", description)   # 특수문자 제거
    return clean_text(description)

# --------------------------------------------------
# 2. summary_input 생성
# --------------------------------------------------
def build_summary_input(title: str, content: str) -> str:
    '''
    요약 모델에 넣기 좋은 입력 텍스트 가공
    위에서 사용한 제목, 본문 정리 함수 적용
    '''
    title = clean_text(title)
    content = clean_text(content)

    if not content:
        return f"제목: {title}\n본문:"

    return f"제목: {title}\n본문:\n{content}"


# --------------------------------------------------
# 3. 네이버 뉴스 검색 API 호출
# --------------------------------------------------
def search_news(query: str, display: int = 10, start: int = 1, sort: str = "date") -> Dict[str, Any]:
    # API id/secret은 호출
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }

    # API에 실제 검색 조건
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": sort,
    }

    # get을 통해 API 요청
    response = requests.get(
        NAVER_NEWS_API_URL,
        headers=headers,
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# 3. 크롤링 보조 (html 요청)
# --------------------------------------------------
def fetch_html(url: str) -> str:
    
    # 기사 URL -> html 요청
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }

    # 타임아웃 10초, 예외처리
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response.text

# --------------------------------------------------
# 4. URL 유형 판별
# --------------------------------------------------

# 필터를 통해 네이버 뉴스 기사만 선별
def is_naver_news_url(url: str) -> bool:
    return "news.naver.com" in url or "n.news.naver.com" in url


# 검색결과 item에서 네이버만, 기준 item['link']로 판단 
def filter_naver_news_items(items: list[dict]) -> list[dict]:
    filtered_items = []

    for item in items:
        link = item.get("link", "")
        if is_naver_news_url(link):
            filtered_items.append(item)

    return filtered_items


def pick_best_url(item: Dict[str, Any]) -> str:
    # 네이버 뉴스만 사용할 것이므로 link만 반환
    return item.get("link", "")


# --------------------------------------------------
# 5. 네이버 뉴스 파서
# --------------------------------------------------
def parse_naver_news(html_text: str) -> Dict[str, str]:
    
    # lxml 파서로 HTML 파싱
    soup = BeautifulSoup(html_text, "lxml")

    # 본문, 이미지 변수 초기화
    full_content = ""
    image_url = ""

    # ------------------------------------------
    # 5-1. 본문 영역 찾기
    # ------------------------------------------
    article_tag = soup.find("article", id="dic_area")
    if article_tag is None:
        article_tag = soup.find(id="newsct_article")

    # ------------------------------------------
    # 5-2. 본문에서 불필요한 요소 제거
    # ------------------------------------------
    if article_tag:
        for tag in article_tag.select(".img_desc"):
            tag.decompose()

        for tag in article_tag.select("script, style"):
            tag.decompose()

        full_content = article_tag.get_text(separator="\n", strip=True)

    full_content = clean_text(full_content)

    # ------------------------------------------
    # 5-3. 대표 이미지 추출
    # ------------------------------------------
    img_tag = soup.find("img", id="img1")

    # 이미지 속성이 여러가지일 경우 우선순위로 가져오기
    if img_tag:
        image_url = (
            img_tag.get("data-src")
            or img_tag.get("src")
            or img_tag.get("data-lazy-src")
            or ""
        )

    # img1이 없으면 og:image 사용
    if not image_url:
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image_url = og_image["content"]

    return {
        "full_content": full_content,
        "image_url": image_url,
    }

# --------------------------------------------------
# . 기사 1개 크롤링
# --------------------------------------------------
def crawl_article(url: str) -> Dict[str, str]:
    """
    네이버 뉴스 기사 1개 크롤링 & 예외 처리
    """
    try:
        # 네이버 뉴스 URL이 아니면 실패 반환
        if not is_naver_news_url(url):
            return {
                "full_content": "",
                "image_url": "",
                "crawl_status": "failed",
                "error_message": "네이버 뉴스 URL이 아닙니다."
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


# --------------------------------------------------
# 7. 기사 1개 요약, agent용 구조 정리
# --------------------------------------------------
def enrich_item_for_summary_agent(item: dict) -> dict:
    result = copy.deepcopy(item)

    # 정리한 제목,본문
    result["title"] = clean_title(result.get("title", ""))
    result["description"] = clean_description(result.get("description", ""))

    # 실제 가져올 URL
    crawl_url = pick_best_url(result)
    result["crawl_url"] = crawl_url

    # 크롤링 결과
    crawled = crawl_article(crawl_url)

    # 본문, 이미지 저장 후 크롤링 상태, 에러 여부 
    result["full_content"] = clean_text(crawled.get("full_content", ""))
    result["image_url"] = crawled.get("image_url", "")
    result["content_length"] = len(result["full_content"])
    result["crawl_status"] = crawled.get("crawl_status", "failed")
    result["error_message"] = crawled.get("error_message", "")
    
    # agent용 summary_input 생성
    result["summary_input"] = build_summary_input(
        title=result.get("title", ""),
        content=result["full_content"],
    )

    # 원문 링크 제거 - 혼동 방지
    result.pop("originallink", None)

    return result

# --------------------------------------------------
# 8. 요약 대상 기사만 필터링
# --------------------------------------------------

# 최소 길이 100으로, 너무 짧은 기사는 제외
# 실패한 기사 요약 제외
def filter_valid_articles_for_summary(news_response: Dict[str, Any], min_length: int = 100) -> List[Dict[str, Any]]:
    valid_items = []

    for item in news_response.get("items", []):
        if item.get("crawl_status") != "success":
            continue

        if item.get("content_length", 0) < min_length:
            continue

        valid_items.append(item)

    return valid_items


# --------------------------------------------------
# . 검색 + 크롤링 + 요약 입력 생성
# --------------------------------------------------
def search_and_prepare_news_for_agent(query: str, target_count: int = 10) -> Dict[str, Any]:
    """
    검색어를 받고, 네이버 뉴스 링크 모아서
    무조건 최대 target_count개까지 채운뒤 반환
    """
    start = 1               # 검색 시작 위치
    chunk_size = 10         # 한번에 가져올 기사 수
    collected_items = []    # 네이버 뉴스만 모을 리스트
    seen_links = set()      # 중복 제거 - 집합

    # 조건을 만족할 때까지 반복 api 호출
    while len(collected_items) < target_count and start <= 1000:
        news_response = search_news(
            query=query,
            display=chunk_size,
            start=start,
            sort="date",           # 최신순
        )

        items = news_response.get("items", [])
        if not items:
            break

        naver_items = filter_naver_news_items(items)

        for item in naver_items:
            link = item.get("link", "")

            # 중복 링크는 건너뛰고, 새로운 링크만 수집
            if link and link not in seen_links:
                seen_links.add(link)
                collected_items.append(item)

                if len(collected_items) >= target_count:
                    break

        start += chunk_size

    collected_items = collected_items[:target_count]

    # 요약 agent가 바로 사용가능한 형태 가공
    enriched_items = []
    for item in collected_items:
        enriched_items.append(enrich_item_for_summary_agent(item))

    # 최종 결과 반환
    return {
        "query": query,
        "display": len(enriched_items),
        "items": enriched_items,
    }