import time
from sqlalchemy import text

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from app.services.file_service import read_file
from app.services.splitter_service import split_text
from app.services.embedding_service import get_embedding
from app.services import vector_store as vector_store_service
from app.services.bm25_store import bm25_store
from app.services.retrieval_service import hybrid_search
from app.services import memory_service
from app.services.llm_service import call_llm_messages
import asyncio
from sqlalchemy.orm import Session
from fastapi import Depends
from app.core.database_models import get_db
from app.models.database_models import Document
from app.models.database_models import Conversation, Message
from app.core.logger import logger
router = APIRouter(prefix="/rag", tags=["RAG知识库"])

class AskRequest(BaseModel):
    question: str
    conversation_id: int = None  # 可选会话ID，不传则新建会话

@router.post("/upload")
async def upload_doc(file: UploadFile = File(...),
                     db: Session = Depends(get_db) # 注入数据库会话
                     ):
    start_time = time.time()
    logger.info(f"开始上传文档：{file.filename}")
    try:
        if vector_store_service.vector_store is None:
            from app.services.vector_store import FaissVectorStore
            vector_store_service.vector_store = FaissVectorStore()
        store = vector_store_service.vector_store
        # 读取文件
        content = await read_file(file)
        # 文本切分
        chunks = split_text(content, filename=file.filename)
        for item in chunks:
            logger.debug(f'正在存入chunk: {item}')
            emb = await asyncio.to_thread(get_embedding, item["text"])
            # FAISS 向量路：add_text 返回全局 chunk_id
            chunk_id = store.add_text(item["text"], emb, item["metadata"])
            # BM25 关键词路：同一 chunk_id 同步入库，保证两路可对齐融合
            item["metadata"]["chunk_id"] = chunk_id
            bm25_store.add_text(item["text"], item["metadata"])
            # 保存文档记录到数据库
        doc_record = Document(
            filename=file.filename,
            chunk_count=len(chunks),
            file_size=file.size,
            status="success"
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        cost = round(time.time() - start_time, 3)
        logger.info(f'文档上传成功:{file.filename},分块数:{len(chunks)},耗时:{cost}s')
        return {
            "doc_id": doc_record.id,
            "filename": file.filename,
            "chunk_count": len(chunks),
            "msg": "文档上传并入库成功"
                }
    except Exception as e:
        cost = round(time.time() - start_time, 3)
        logger.error(f"文档上传失败：{file.filename}，耗时：{cost}s，错误：{str(e)}", exc_info=True)
        raise e


@router.post("/ask")
async def only_ask(req: AskRequest):
    store = vector_store_service.vector_store
    if store is None or len(store.documents) == 0:
        return {'answer':'知识库为空，请先上传文档'}
    results = await asyncio.to_thread(hybrid_search, req.question)
    return {"question": req.question, "related_docs": results}


@router.post("/answer")
async def rag_answer(req: AskRequest,
                     db: Session = Depends(get_db)  # 新增数据库依赖
):
    # 1. 处理会话：没传ID就自动新建一个
    if req.conversation_id is None:
        conv = Conversation(user_id=1, title=req.question[:20])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    else:
        conversation_id = req.conversation_id

    # 2. 保存用户提问到数据库
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=req.question
    )
    db.add(user_msg)

    store = vector_store_service.vector_store
    if store is None or len(store.documents) == 0:
        return {'question': req.question, 'answer': '知识库为空，请先上传文档', 'related_docs': [], 'sources': []}

    # 3. 混合检索（向量 + BM25 加权融合），替换原纯向量检索
    results = await asyncio.to_thread(hybrid_search, req.question)
    # 拼接带来源的上下文
    context_parts = []
    for item in results:
        meta = item["metadata"]
        source_tag = f"[来源：{meta['filename']}-第{meta['paragraph']}段]"
        context_parts.append(f"{source_tag}\n{item['text']}")
    context_text = "\n\n".join(context_parts)

    # 4. 分级记忆
    # 短期记忆：当前会话最近 N 轮（含刚保存的当前问题，最后一条需排除）
    recent = await asyncio.to_thread(memory_service.build_recent_history, db, conversation_id)
    # 长期记忆：语义检索相关历史问答
    long_term_texts = await asyncio.to_thread(memory_service.recall_long_term, req.question)

    # 5. 组装多轮 messages（system + 历史对话 + 当前问题）
    system_prompt = (
        "你是文档问答助手。必须严格基于提供的上下文作答，"
        "上下文没有的信息直接回复：未检索到相关资料。"
        "回答结尾标注信息来源，格式：来源：文件名-第x段。"
    )
    long_term_block = ""
    if long_term_texts:
        long_term_block = "\n\n".join(f"[历史参考]\n{t}" for t in long_term_texts)

    messages = [{"role": "system", "content": system_prompt}]
    # 短期历史对话（排除最后一条，即当前问题）
    for m in recent[:-1]:
        messages.append({"role": m["role"], "content": m["content"]})
    user_content = f"上下文：\n{context_text}\n\n{long_term_block}\n\n用户问题：{req.question}"
    messages.append({"role": "user", "content": user_content})

    answer = await asyncio.to_thread(call_llm_messages, messages)

    # 6. 保存助手回复 + 写入长期记忆
    db.add(Message(conversation_id=conversation_id, role="assistant", content=answer))
    db.commit()
    await asyncio.to_thread(memory_service.save_turn_to_memory, req.question, answer, conversation_id)

    sources = [item["metadata"] for item in results]
    return {
        "question": req.question,
        "answer": answer,
        "related_docs": results,
        "sources": sources
    }

@router.post("/clear")
def clear_vector(db: Session = Depends(get_db)):
    store = vector_store_service.vector_store
    if store is not None:
        store.reset()
    bm25_store.reset()

    db.query(Document).delete(synchronize_session=False)
    db.commit()

    sequence_exists = db.execute(
        text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sqlite_sequence'")
    ).scalar()
    if sequence_exists:
        db.execute(text("DELETE FROM sqlite_sequence WHERE name = 'documents'"))
        db.commit()

    return {'msg': '向量库和文档记录已经清空，下次上传将从 doc_id=1 开始'}


@router.post("/conversation/create")
def create_conversation(db: Session = Depends(get_db)):
    """创建新的对话会话"""
    conv = Conversation(user_id=1, title="新对话")  # 先默认用户ID=1，后续可扩展用户系统
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"conversation_id": conv.id, "title": conv.title}