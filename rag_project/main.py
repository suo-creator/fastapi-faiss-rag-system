import uvicorn
from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router

app = FastAPI(title="RAG对话服务")

# 挂载路由
app.include_router(chat_router)
app.include_router(rag_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)