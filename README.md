# 📌 프로젝트명

> AI Agent를 활용한 네이버 뉴스 요약 서비스
 * 정보 과부하 시대, 인공지능 에이전트로 최신 뉴스를 효율적으로 소비하는 방법

---

## 🎯 목적

* 바쁜 현대인을 위해 핵심만 소비하는 뉴스 서비스 제공

## 📌 배경(As is)

* 하루 수천건의 뉴스가 있지만, 필요 정보는 찾기 어려움
* 불필요 정보와 사용성을 저해하는 광고 등장
* 뉴스의 핵심 내용을 얻기 위해 많은 시간 소요

## 📌 목표 (To be)
* 핵심 정보만 빠르게 제공
* 불필요 정보 제거
* 짧은 시간 안에 정보 파악 가능


---

## 🛠 Tech Stack

<img width="1536" height="1024" alt="기술스택1" src="https://github.com/user-attachments/assets/7f985d89-8721-46f1-903f-5a30a08a49a4" />


---

## 🚀 주요 기능

* 키워드 기반 네이버 뉴스 수집
* 네이버 뉴스 분류
* OpenAI LLM 기반 뉴스 요약
* 뉴스 기반 AI 질의응답

---

## 🧠 주요 구현 내용

* Streamlit을 활용한 뉴스 요약 UI/UX 구성
* Naver API 기반 뉴스 URL 수집 로직 구현
* 뉴스 크롤링 및 데이터 전처리
* LLM 기반 뉴스 요약 및 분석 정보 제공
* LangChain 활용 AI 질의응답


---

## 🖥 실행 방법

```
# .env.sample, backend/sql/ddl.sql 참고
# .env, DB 준비

# conda env 생성, 활성화
conda env create -f environment.yml
conda activate news-agent

# fastapi 실행
cd backend
uvicorn app.main:app

# streamlit 실행
streamlit run frontend/app.py
```


---

## 📂 프로젝트 구조

```
SKN29_SideProject_NewsAgent-main/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI 라우터 (엔드포인트)
│   │   ├── infra/        # 외부 API, DB, 클라이언트 관련 로직
│   │   ├── model/        # DB 모델 (ORM)
│   │   ├── service/      # 비즈니스 로직 (뉴스 처리, LLM 연동 등)
│   │   └── main.py       # FastAPI 실행 진입점
│   │
│   ├── sql/              # DB 초기 스키마 및 쿼리
│   ├── test/             # 테스트 코드
├── frontend/
│   ├── assets/
│   │   └── css/          # 스타일 파일
│   │
│   ├── components/       # UI 컴포넌트
│   ├── data/             # 프론트 데이터 처리
│   ├── styles/           # 추가 스타일 정의
│   └── utils/            # 공통 유틸 함수
├── .env
├── environment.yml
├── .gitignore
└── README.md
```

---

## 📸 서비스 화면

<img width="1104" height="432" alt="서비스_메인1" src="https://github.com/user-attachments/assets/c2c397f4-e8f0-486e-8e60-cd8181693887" />
<br>
<img width="1065" height="841" alt="서비스_요약1" src="https://github.com/user-attachments/assets/9f0e890b-51d2-4518-97c7-0f08dd228caa" />
<br>
<img width="1075" height="836" alt="서비스_채팅1" src="https://github.com/user-attachments/assets/aab4f15b-8d13-4e20-aeae-6f044ad5813f" />


## 서비스 흐름도

<img width="1774" height="887" alt="서비스흐름도1" src="https://github.com/user-attachments/assets/a745d067-b553-433c-8941-f701b0ce9973" />



---

## 🧾 API 명세

* GET /news : 뉴스 조회
* POST /news/search : 뉴스 검색

---

## 시스템 아키텍처

<img width="1536" height="1024" alt="시스템 아키텍쳐1" src="https://github.com/user-attachments/assets/ffb93105-ee85-460f-bff5-59ac6a026cae" />


## 🗄 ERD

<img width="1536" height="1024" alt="DB테이블_최종1" src="https://github.com/user-attachments/assets/0e978731-3dc9-4b67-af87-359881912ff3" />


---

## ⚠️ 한계점

* Naver API 호출 제한
* LLM 요약 품질 편차 존재

---

## 🔧 개선 방향

* 사용자 맞춤 뉴스 추천 기능 추가
* 요약 품질 개선 및 모델 최적화

---

## 👥 역할 분담

* Backend: 김진욱, 김재홍, 윤승혁, 한경찬
* Frontend: 양정현, 이지현
* AI: 윤승혁
* 공통관리: 김재홍

## 👥 한줄평

- 김재홍 : 전반적인 프로젝트 관리, API 클라이언트를 담당. 전체적인 관리 포인트를 잡지 않고 진행해서 아쉬움이 남은 프로젝트였다. API 클라이언트 개발 과정도 어렵긴 했지만, 전체적인 구조를 파악하고 설계하는 과정에 있어서 능력적인 부분이 더 절실하게 느껴진 과정이었다. End-to-End 서비스 구현 과정에서 많은 소통을 중재하지 못한 점에서 다음엔 반드시 개선해야할 부분이 생겼다. 함께 해준 팀원들에게 고마우면서도 미안한 감정이 든다.
- 김진욱 : 대부분을 팀원들에게 맡기고 백엔드 설계, 최종 코드 퀄리티 검토 정도만 수행했는데, 중간에 정처기 시험 일정 때문에 팀원들을 많이 챙겨드리지 못한거 같아서 아쉽습니다. 인적으로 자주 모여서 의견 나누고 하는 시간이 더 필요했던거 같습니다. 쉬는시간만으로는 너무 부족한 느낌도 많이 받았습니다. 다음 스프린트에는
- 양정현 : frontend를 많이 해왔지만, 이번 시간을 통해 Streamlit의 다양한 기능을 새롭게 익힐 수 있었다. 또한 LLM과 크롤링 에 대해서도 간단히 공부해보며 활용 가능성을 탐색해보는 계기가 되었다. backend 경험이 부족해 아쉬움은 있지만, 대신 LLM 활용과 프롬포트 엔지니어링 등 backend와 연관된 다양한 시도를 해볼 수 있었다. 유익한 시간이었다.
- 윤승혁 : LangChain을 활용해서 뉴스를 자동으로 요약해주는 에이전트를 만들어봤다. 다만 아직 기초적인 부분밖에 건드리지 못한 것 같아서 아쉽다.
- 이지현 : frontend를 처음으로 다루어볼 기회가 생겨 유익했다. backend 이해가 부족해서 전체적인 프로젝트 흐름을 잘 잡지 못해 부족한 것 같아 아쉽지만 이번 사이드프로젝트 fornt 경험을 통해서 다음 활동을 통해 역량을 더 키워 나가고 싶다.
- 한경찬 : ai news agent 요약 서비스를 개발하면서 백엔드 파트와 DB 구축 파트의 일부를 담당했다. 백엔드는 client 엔드 포인트 서비스와 뉴스 데이터 크롤링 서비스 개발을 배울 수 있었다. 디테일한 설계 구조까지 파악하지는 못했지만, 전반적인 개발 과정의 흐름을 경험해 볼 수 있는 기회였다. 본 프로젝트 혹은 다른 프로젝트를 하게 된다면, 더 많은 기여를 할 수 있을 것이다.

---

## 🔗 References

* API 문서 
* 관련 기술 문서



