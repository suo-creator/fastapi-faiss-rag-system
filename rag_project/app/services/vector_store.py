import faiss
import json
import os
import numpy as np
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

    def add_text(self, text: str, embedding, metadata: dict = None):
        arr = np.array([embedding], dtype=np.float32)
        self.index.add(arr)
        self.documents.append({
            "text": text,
            "metadata": metadata if metadata else {}
        })

    def search(self, query_emb, top_k: int = 3):
        # 关键：查询向量也要转 np.float32 的二维数组
        arr = np.array([query_emb], dtype=np.float32)
        distances, indexes = self.index.search(arr, top_k)

        res = []
        for idx in indexes[0]:
            if 0 <= idx < len(self.documents):
                res.append(self.documents[idx])
        return res

    def _save(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(DOCS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.text_list, f, ensure_ascii=False)

    def _load(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(DOCS_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(DOCS_FILE, "r", encoding="utf-8") as f:
                self.text_list = json.load(f)

# 全局单例，其他文件直接导入使用
vector_store = FaissVectorStore(dim=1024)