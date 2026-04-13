from typing import TypedDict


class NewsItem(TypedDict, total=False):
    title: str
    description: str
    link: str
    originallink: str
    pubDate: str
    crawl_url: str
    full_content: str
    image_url: str
    content_length: int
    crawl_status: str
    error_message: str
    summary_input: str


class NewsSearchResponse(TypedDict, total=False):
    query: str
    display: int
    items: list[NewsItem]


def summarize_text(summary_input: str) -> str:
    """
    나중에 OpenAI 등 요약 모델 붙일 자리
    """
    return ""