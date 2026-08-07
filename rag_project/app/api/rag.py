from fastapi import APIRouter, UploadFile, File
from pip._internal.index import sources
from pydantic import BaseModel
from app.services.file_service import read_file
from app.services.splitter_service import split_text
from app.services.embedding_service import get_embedding
from app.services.vector_store import vector_store, FaissVectorStore
import asyncio
router = APIRouter(prefix="/rag", tags=["RAG知识库"])

class AskRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    global vector_store
    if vector_store is None:
        vector_store = FaissVectorStore()
    # 读取文件
    content = await read_file(file)
    # 文本切分
    chunks = split_text(content, filename=file.filename)
    for item in chunks:
        print("正在存入chunk：", item)
        emb = await (
    asyncio.to_thread(get_embedding, item["text"]))
        vector_store.add_text(item["text"], emb, item["metadata"])
    return {"filename": file.filename, "chunk_count": len(chunks), "msg": "文档上传并入库成功"}


@router.post("/ask")
async def only_ask(req: AskRequest):
    global vector_store
    if vector_store is None:
        return {'answer':'知识库为空，请先上传文档'}
    emb_q = await asyncio.to_thread(get_embedding, req.question)
    results = vector_store.search(emb_q, top_k=3)
    return {"question": req.question, "related_docs": results}


@router.post("/answer")
async def rag_answer(req: AskRequest):
    emb_q = await asyncio.to_thread(get_embedding, req.question)
    results = vector_store.search(emb_q, top_k=3)
    # 拼接带来源的上下文
    context_parts = []
    for item in results:
        meta = item["metadata"]
        source_tag = f"[来源：{meta['filename']}-第{meta['paragraph']}段]"
        context_parts.append(f"{source_tag}\n{item['text']}")
    context_text = "\n\n".join(context_parts)



    # 优化prompt，强制标注来源
    prompt = f"""参考下面的上下文回答用户问题。
    规则：
    1. 必须严格基于上下文作答，上下文没有的信息直接回复：未检索到相关资料
    2. 回答结尾标注信息来源，格式：来源：文件名-第x段

    上下文：
    {context_text}

    用户问题：{req.question}
    """
    from app.services.llm_service import call_llm
    answer = await asyncio.to_thread(call_llm,prompt)
    sources = [item["metadata"] for item in results]
    return {
        "question": req.question,
        "answer": answer,
        "related_docs": results,
        "sources": sources
    }

@router.post("/clear")
def clear_vector():
    global vector_store
    vector_store = None
    return {'msg': '向量库已经清空'}