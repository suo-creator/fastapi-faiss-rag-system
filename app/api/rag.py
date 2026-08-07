from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.services.file_service import read_file
from app.services.splitter_service import split_text
from app.services.embedding_service import get_embedding
from app.services.vector_store import vector_store
import asyncio
router = APIRouter(prefix="/rag", tags=["RAG知识库"])

class AskRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    # 读取文件
    content = await read_file(file)
    # 文本切分
    chunks = split_text(content)
    # 生成向量存入faiss
    for chunk in chunks:
        emb = await asyncio.to_thread(get_embedding, chunk)
        vector_store.add_text(chunk, emb)
    return {"filename": file.filename, "chunk_count": len(chunks), "msg": "文档上传并入库成功"}


@router.post("/ask")
async def only_ask(req: AskRequest):
    emb_q = await asyncio.to_thread(get_embedding, req.question)
    results = vector_store.search(emb_q, top_k=3)
    return {"question": req.question, "related_docs": results}


@router.post("/answer")
async def rag_answer(req: AskRequest):
    emb_q = await asyncio.to_thread(get_embedding, req.question)
    results = vector_store.search(emb_q, top_k=3)
    context_text = "\n".join([item["text"] for item in results])

    prompt = f"""参考下面的上下文回答用户问题，如果上下文中没有相关信息，直接回复：参考资料中未提及相关内容。
上下文：
{context_text}
用户问题：{req.question}
"""
    from app.services.llm_service import call_llm
    answer = await asyncio.to_thread(call_llm,prompt)
    return {
        "question": req.question,
        "answer": answer,
        "related_docs": results
    }