### conda env 생성, 활성화
```
conda env create -f environment.yml
conda activate news-agent

# 초기화 시 기존 news-agent 삭제
conda remove --name news-agent --all
```

### fastapi 실행
```
cd backend
uvicorn app.main:app
uvicorn app.main:app --reload # 리로드 옵션: 코드 변경시 자동 재실행
```

### streamlit 실행
```
cd frontend
streamlit run app.py
```

### `.vscode/settings.json` 추천 세팅
```
    // EXPLORER에 특정파일 자동 숨김처리
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/__init__.py": true
    },
```