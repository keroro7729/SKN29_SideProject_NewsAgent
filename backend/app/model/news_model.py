from typing import TypedDict                # 각 키, 타입이 무엇인지 딕셔너리 구조 설명


# 1개 뉴스 구조 정의
class NewsItem(TypedDict, total=False):
    title: str
    description: str
    link: str
    originallink: str
    pubDate: str
    crawl_url: str
    full_content: str           # 본문 전체 텍스트
    image_url: str
    content_length: int
    crawl_status: str
    error_message: str
    summary_input: str          # 요약 모델에 입력할 텍스트


# 뉴스 검색 결과 전체 구조 반환시 형태
class NewsSearchResponse(TypedDict, total=False):
    query: str                  # 사용자 검색 키워드
    display: int                # 검색 결과 수 ( 10개 )
    items: list[NewsItem]       # 기사 리스트



def summarize_text(summary_input: str) -> str:
    """
    나중에 OpenAI 등 요약 모델 붙일 자리
    """
    return ""