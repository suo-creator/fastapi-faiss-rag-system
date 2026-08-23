import faiss
import json
import os
import numpy as np
from app.core.config import settings
VECTOR_STORE_PATH = "./data/vector_store"
INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "faiss.index")
DOCS_FILE = os.path.join(VECTOR_STORE_PATH, "documents.json")

class FaissVectorStore:
    def __init__(self, dim: int = 1024):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.documents = []
        # 安全创建目录
        if not os.path.exists(VECTOR_STORE_PATH):
            os.makedirs(VECTOR_STORE_PATH)
        # 加载本地已有数据
        self._load()

    def add_text(self, text: str, embedding, metadata: dict = None) -> int:
        """存入一条向量，返回全局自增 chunk_id（供 BM25 路对齐）"""
        arr = np.array([embedding], dtype=np.float32)
        self.index.add(arr)
        chunk_id = len(self.documents)
        metadata = dict(metadata or {})
        metadata.setdefault("chunk_id", chunk_id)
        self.documents.append({
            "text": text,
            "metadata": metadata
        })
        self._save()
        return chunk_id

    def reset(self):
        self.index = faiss.IndexFlatL2(self.dim)
        self.documents = []
        for file_path in (INDEX_FILE, DOCS_FILE):
            if os.path.exists(file_path):
                os.remove(file_path)

    def search(self, query_emb, top_k: int = None):
        if top_k is None:
            top_k = settings.TOP_K
        print(f'top_k: {top_k}')
        # 关键：查询向量也要转 np.float32 的二维数组
        arr = np.array([query_emb], dtype=np.float32)
        distances, indexes = self.index.search(arr, top_k)

        res = []
        for idx in indexes[0]:
            if 0 <= idx < len(self.documents):
                res.append(self.documents[idx])
        return res

    def search_with_scores(self, query_emb, top_k: int = None):
        """
        与 search 相同的召回逻辑，额外返回每条结果的 L2 距离，
        供混合检索做分数归一化：[(document, distance), ...]
        """
        if top_k is None:
            top_k = settings.TOP_K
        arr = np.array([query_emb], dtype=np.float32)
        distances, indexes = self.index.search(arr, top_k)

        res = []
        for idx, dist in zip(indexes[0], distances[0]):
            if 0 <= idx < len(self.documents):
                res.append((self.documents[idx], float(dist)))
        return res

    def _save(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(DOCS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False)

    def _load(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(DOCS_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(DOCS_FILE, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
            # 兼容旧数据：补齐 chunk_id（按文档顺序自增，与 BM25 语料对齐）
            changed = False
            for i, doc in enumerate(self.documents):
                metadata = dict(doc.get("metadata") or {})
                if "chunk_id" not in metadata:
                    metadata["chunk_id"] = i
                    doc["metadata"] = metadata
                    changed = True
            if changed:
                self._save()

# 全局单例，其他文件直接导入使用
vector_store = FaissVectorStore(dim=1024)