# Naver News API params
import requests
import re
import html
from datetime import datetime
import time

# ========================================
# 네이버 뉴스 API 클라이언트 호출 클래스 정의
# ========================================
class NaverNewsClient:
    def __init__(self, client_id, client_secret):
        if not client_id or not isinstance(client_id, str):
            raise ValueError(f"client_id가 올바르지 않습니다")

        if not client_secret or not isinstance(client_secret, str):
            raise ValueError(f"client_secret이 올바르지 않습니다")

        self.client_id = client_id
        self.client_secret = client_secret

    # ========================================
    # 뉴스 API 호출 함수
    # ========================================
    def get_news(self, query, display=1,start=1,sort="date"):             
        if not query or not isinstance(query, str):
            raise ValueError(f"에러:query는 비어있지 않은 문자열이어야 합니다")
        url = "https://openapi.naver.com/v1/search/news.json"

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        # 네이버 제한
        display = max(1, min(display,100))
        start = max(1, min(start,1000))
        
        params = {
            "query": query,             # 한 번에 표시할 검색 결과 개수(기본값: 10, 최댓값: 100)
            "display": display,         # 검색 시작 위치(기본값: 1, 최댓값: 100)
            "start": start,             # 검색 시작 위치(기본값: 1, 최댓값: 1000)
            "sort": sort              # 검색 결과 정렬 방법, sim(정확도기준 내림차순 정렬(기본값)), date(날짜기준 내림차순 정렬)
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)

            # 인증 관련 체크
            if response.status_code == 401:
                raise Exception(f"인증 실패: client_id 또는 client_secret 확인 필요")
            elif response.status_code == 403:
                raise Exception(f"접근 거부: API 권한 또는 호출 제한 확인")

            # 그 다음 일반 에러 처리
            response.raise_for_status()

        except requests.exceptions.Timeout as e:
            raise Exception(f"API 요청 시간 초과: {e}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"API 요청 실패: {e}")

        try:
            data = response.json()
            if "errorCode" in data:
                raise Exception(f"API 오류: {data.get('errorMessage')}")
            return data
        except ValueError as e:
            raise Exception(f"JSON 파싱 실패:{e}")
    
    # ========================================
    # 텍스트 정제
    # ========================================
    def clean_text(self, text):
        if not isinstance(text, str):
            return ""
        text = re.sub('<.*?>','',text) # HTML 태그 제거
        text = html.unescape(text)  # HTML 엔티티 일반문자로 변환 변환
        text = re.sub('\s+', ' ', text).strip()     # 공백 통일, 양쪽 공백 제거(strip)
        return text 
    # ========================================
    # 날짜 변환
    # ========================================
    def format_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except Exception:
            return None
    # ========================================
    # 뉴스 데이터 파싱
    # ========================================
    def parse_news(self, data):
        # 1. data 자체 검증
        if not isinstance(data, dict):
            raise ValueError(f"data는 dict형태여야 합니다.")
        items = data.get("items")

        # 2. items 구조 검증
        if not isinstance(items,list):
            return [] 
        results = []
        for item in items:
            # 3. item 검증        
            if not isinstance(item,dict):
                continue # 이상한 데이터는 버림
            try:
                title = self.clean_text(item.get("title"))
                content = self.clean_text(item.get("description"))
                pub_date = self.format_date(item.get("pubDate"))

                results.append({
                    "title": title,
                    "content": content,
                    "url": item.get("link", "") or "",
                    "originallink": item.get("originallink", "") or "",
                    "date": pub_date
                })
            # 4. 개별 데이터 오류 무시 (전체 서비스 보호)
            except Exception as e:
                print(f"데이터 파싱 실패: {e}")
                continue
        return results  

    # ========================================
    # 전체 실행(API-파싱까지)
    # ========================================        
    def get_clean_news(self, query, display=1, start=1):
        try:
            raw_data = self.get_news(query, display, start)
            return self.parse_news(raw_data)

        except Exception as e:
            print(f"뉴스 조회 실패: {e}")
            return []