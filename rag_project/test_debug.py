from app.services.file_service import read_local_text
from app.services.splitter_service import split_text
from app.services.embedding_service import get_embedding

# 改成你的test.txt实际路径
content = read_local_text("./test.txt")
print("读取文件成功：", content[:100])

chunks = split_text(content)
print("切分后块：", chunks)

emb = get_embedding(chunks[0])
print("向量维度：", len(emb))