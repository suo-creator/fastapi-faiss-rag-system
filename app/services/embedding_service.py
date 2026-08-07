import requests
from app.core.config import settings

def get_embedding(text: str) -> list[float]:
    """调用通义千问Embedding接口，返回单条文本的向量"""
    headers = {
        "Authorization": f"Bearer {settings.EMBEDDING_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.EMBEDDING_MODEL,
        "input": text
    }
    resp = requests.post(
        f"{settings.EMBEDDING_BASE_URL}/embeddings",
        headers=headers,
        json=payload
    )
    data = resp.json()
    return data["data"][0]["embedding"]

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """批量获取文本向量列表"""
    return [get_embedding(text) for text in texts]

