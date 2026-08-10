
from dotenv import load_dotenv
import os
# 加载.env文件
load_dotenv()
class Settings:
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

# 千问 Embedding 配置
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY")
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")

# RAG 通用配置
    TOP_K: int = int(os.getenv("TOP_K", 3))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))
settings = Settings()

