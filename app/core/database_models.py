import os
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker,declarative_base

# SQLite 数据库，文件存项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL =f"sqlite:///{os.path.join(BASE_DIR, 'rag.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 专属配置
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库会话依赖，接口里直接注入使用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()