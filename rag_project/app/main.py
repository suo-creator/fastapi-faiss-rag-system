import uvicorn
from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG对话服务")


# 新增：允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，开发用
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂载路由
app.include_router(chat_router)
app.include_router(rag_router)

