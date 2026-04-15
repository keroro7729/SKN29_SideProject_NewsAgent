import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 연결 죽었는지 체크
    connect_args={"charset": "utf8mb4"}, # 한글 설정
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# FastAPI DI용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def init_db():
    """앱 시작 시 테이블 생성"""
    Base.metadata.create_all(bind=engine)