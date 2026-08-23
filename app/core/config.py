
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

# 混合检索配置
    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT", 0.5))
    BM25_RECALL_K: int = int(os.getenv("BM25_RECALL_K", 20))

# Rerank 精排配置
    RERANK_ENABLED: bool = os.getenv("RERANK_ENABLED", "true").lower() == "true"
    RERANK_MODEL: str = os.getenv(
        "RERANK_MODEL",
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "models", "bge-reranker-base")
    )
    RERANK_RECALL_K: int = int(os.getenv("RERANK_RECALL_K", 20))

# 分级记忆配置
    MEMORY_RECENT_TURNS: int = int(os.getenv("MEMORY_RECENT_TURNS", 5))   # 短期：最近 N 轮
    MEMORY_LONG_TOP_K: int = int(os.getenv("MEMORY_LONG_TOP_K", 3))      # 长期：召回历史条数
settings = Settings()
print(f'{settings.TOP_K}')
