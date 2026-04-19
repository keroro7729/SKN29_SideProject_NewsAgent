# 테스트 용도로 작성한 코드
# 일단 dummy_news를 사용하였지만, 추후에 db 연동할 계획

from chatbot_service import ChatBotService
from dummy_news import get_dummy_news, get_trending_keywords
from dotenv import load_dotenv
load_dotenv()

service = ChatBotService()
dummy_news = get_dummy_news()

for news in dummy_news:
    resp = service.response([news['desc']])
    # 내용이 한 문장이라 아이러니하게도 내용보다 요약이 더 긺
    print('내용:', news['desc'])
    print('카테고리:', resp.category)
    print('요약:', resp.summary)
    print('키워드:', resp.tags)
    print()