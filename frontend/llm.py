import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# ── 1. 네이버 뉴스 검색 ────────────────────────────
def search_naver_news(query: str, display: int = 5) -> list[dict]:
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display, "sort": "date"}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    return res.json()["items"]


# ── 2. 기사 본문 추출 ──────────────────────────────
def fetch_article_body(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        body = soup.select_one("#dic_area") or soup.select_one("#articleBodyContents")
        if body:
            return body.get_text(separator="\n").strip()

        paragraphs = soup.find_all("p")
        return "\n".join(p.get_text() for p in paragraphs if len(p.get_text()) > 50)
    except Exception as e:
        return f"[본문 추출 실패: {e}]"


# ── 3. GPT로 요약 ──────────────────────────────────
def summarize_with_gpt(title: str, body: str) -> str:
    if not body or "[본문 추출 실패" in body:
        return "본문을 가져오지 못했습니다."

    prompt = f"""다음 뉴스 기사를 3~5줄로 핵심만 요약해주세요.
- 핵심 사실 위주로 간결하게
- 불필요한 수식어 제외
- 한국어로 작성

제목: {title}

본문:
{body[:3000]}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


# ── 4. 메인 실행 ───────────────────────────────────
def run_news_summary(query: str, count: int = 5):
    print(f"\n🔍 '{query}' 뉴스 검색 중...\n" + "="*60)
    articles = search_naver_news(query, display=count)

    for i, article in enumerate(articles, 1):
        title = BeautifulSoup(article["title"], "html.parser").get_text()
        link  = article["originallink"] or article["link"]

        print(f"\n[{i}] {title}")
        print(f"🔗 {link}")

        body    = fetch_article_body(link)
        summary = summarize_with_gpt(title, body)

        print(f"📝 요약:\n{summary}")
        print("-" * 60)

        time.sleep(1)


if __name__ == "__main__":
    run_news_summary("인공지능", count=3)