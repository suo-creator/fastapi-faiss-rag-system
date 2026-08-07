from app.services.embedding_service import get_embedding

vec = get_embedding("你好，这是千问Embedding测试")
print(f"向量维度：{len(vec)}")
print(f"前5个数值：{vec[:5]}")