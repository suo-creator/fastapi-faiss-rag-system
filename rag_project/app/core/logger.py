import logging
import os
from datetime import datetime

# 日志存放目录
LOG_DIR = "./logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件名按天生成
log_file = os.path.join(LOG_DIR, f"rag_{datetime.now().strftime('%Y%m%d')}.log")

# 日志格式
log_format = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

# 配置日志：同时输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 全局日志实例，其他文件直接导入使用
logger = logging.getLogger("rag_project")