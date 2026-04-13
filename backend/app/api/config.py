import os
from dotenv import load_dotenv


load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"


