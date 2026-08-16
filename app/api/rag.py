import time

from fastapi import APIRouter, UploadFile, File
from pip._internal.index import sources
from pydantic import BaseModel
from app.services.file_service import read_file
from app.services.splitter_service import split_text
from app.services.embedding_service import get_embedding
from app.services.vector_store import vector_store, FaissVectorStore
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
    global vector_store
    start_time = time.time()
    logger.info(f"开始上传文档：{file.filename}")
    try:
        if vector_store is None:
            vector_store = FaissVectorStore()
        # 读取文件
        content = await read_file(file)
        # 文本切分
        chunks = split_text(content, filename=file.filename)
        for item in chunks:
            logger.debug(f'正在存入chunk: {item}')
            emb = await asyncio.to_thread(get_embedding, item["text"])
            vector_store.add_text(item["text"], emb, item["metadata"])
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
    global vector_store
    if vector_store is None:
        return {'answer':'知识库为空，请先上传文档'}
    emb_q = await asyncio.to_thread(get_embedding, req.question)
    results = vector_store.search(emb_q)
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

    # 3. 原有检索、大模型调用逻辑保持不变
    emb_q = await asyncio.to_thread(get_embedding, req.question)
    results = vector_store.search(emb_q)
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


@router.post("/conversation/create")
def create_conversation(db: Session = Depends(get_db)):
    """创建新的对话会话"""
    conv = Conversation(user_id=1, title="新对话")  # 先默认用户ID=1，后续可扩展用户系统
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"conversation_id": conv.id, "title": conv.title}