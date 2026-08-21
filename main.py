from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.database_models import engine, Base
from app.models.database_models import *  # 导入所有表模型，必须导入才会自动建表
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BusinessException
from app.core.logger import logger
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
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BusinessException
from app.core.logger import logger

# 捕获自定义业务异常
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.warning(f"业务异常：{exc.msg}")
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "msg": exc.msg,
            "data": None
        }
    )

# 捕获系统全局异常
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"系统异常：{str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "系统内部错误，请稍后重试",
            "data": None
        }
    )

