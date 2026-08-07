from starlette.responses import StreamingResponse

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from app.services.llm_service import call_llm,stream_llm
# 创建路由组
router = APIRouter()


# 请求数据模型
class ChatRequest(BaseModel):
    question: str

# 用同步函数def.异步函数async def 会阻塞整个服务主循环，让性能变差
# 健康检查接口
@router.get("/health")
def health_check():
    return {"status": "ok",'msg':'服务正常运行'}


@router.post("/chat")
def chat(req: ChatRequest):
    answer = call_llm(req.question)
    return {"answer":f"模拟回答：收到你的问题{answer}，等待接入大模型"}


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    generator = stream_llm(req.question)
    # media_type 设置文本流
    return StreamingResponse(generator, media_type="text/event-stream")









