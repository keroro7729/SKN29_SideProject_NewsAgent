from app.infra.client import OpenAIClient

client = OpenAIClient()
system_prompt = "You are a helpful assistant that summarizes news articles. Please provide a concise summary of the following news articles."
"""
넌 뉴스 요약 도우미야.

# 출력 형식
{
    summary: "user_input의 뉴스 내용 요약 데이터 한문단",
    score: "뉴스 내용의 긍정 부정 점수"
}
"""

def summary(news_datas: List[str]) -> str:

    user_input = '\n'.join(news_datas)

    response = client.send_message(
        system_prompt,
        user_input
    )

    return response.text


def summarize_text(summary_input: str) -> str:
    """
    나중에 OpenAI 또는 다른 요약 모델 호출을 붙일 자리
    """
    return ""