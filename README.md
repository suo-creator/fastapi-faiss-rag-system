# RAG 智能文档问答系统

基于 FastAPI、FAISS、SQLite 和 Streamlit 实现的轻量级检索增强生成（RAG）文档问答系统。系统支持 TXT 文档上传、文本切分、向量化检索、基于上下文的 LLM 问答、引用来源返回、SSE 流式输出和 Docker Compose 部署。

## 项目亮点

- 打通文档上传、文本切分、Embedding、FAISS 检索和 LLM 生成的 RAG 全流程
- 使用 FAISS 保存语义索引，使用 SQLite 持久化文档、会话和消息等业务数据
- 在 Prompt 中约束回答范围，并返回文件名和段落编号，支持答案来源追溯
- 支持普通响应和 SSE 流式响应，改善长回答的交互体验
- 使用 FastAPI 路由分层、业务异常处理、统一日志和 Docker Compose 完成工程化组织
- 默认通过 `CHUNK_SIZE`、`CHUNK_OVERLAP` 和 `TOP_K` 环境变量控制文本切分与检索参数

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | FastAPI、Uvicorn |
| 前端 | Streamlit |
| 向量检索 | FAISS `IndexFlatL2` |
| 数据持久化 | SQLite、SQLAlchemy ORM |
| 文本切分 | LangChain `RecursiveCharacterTextSplitter` |
| 模型接口 | 兼容 OpenAI 协议的 Embedding / Chat API |
| 配置与日志 | python-dotenv、Python logging |
| 部署 | Docker、Docker Compose |

## 系统流程

```mermaid
flowchart LR
    A[Streamlit 前端] --> B[FastAPI API]
    B --> C[TXT 读取与文本切分]
    C --> D[Embedding API]
    D --> E[FAISS 向量索引]
    B --> F[SQLite]
    B --> G[相似度检索]
    G --> H[Prompt 组装]
    H --> I[LLM API]
    I --> B
```

### 文档上传

用户上传 TXT 文件后，后端依次完成文件读取、递归文本切分、向量生成，并将向量和元数据保存到 FAISS；文件名、大小和分块数量保存到 SQLite。

### 问答检索

用户问题首先生成查询向量，随后从 FAISS 召回 Top-K 个文本片段。系统将片段及文件名、段落号拼接到 Prompt 中，调用 LLM 生成回答，并返回相关片段和来源信息。

## 项目结构

```text
rag_new/
├── app.py                         # Streamlit 前端入口
├── main.py                        # FastAPI 服务入口
├── requirements.txt               # Python 依赖
├── docker-compose.yml             # 前后端容器编排
├── Dockerfile.backend
├── Dockerfile.frontend
├── app/
│   ├── api/
│   │   ├── chat.py                # 健康检查、普通和流式接口
│   │   └── rag.py                 # 上传、检索、问答、会话接口
│   ├── core/
│   │   ├── config.py              # 环境变量配置
│   │   ├── database_models.py     # 数据库连接与 Base
│   │   ├── exceptions.py          # 业务异常
│   │   └── logger.py              # 日志配置
│   ├── models/
│   │   └── database_models.py     # 数据表模型
│   └── services/
│       ├── embedding_service.py   # Embedding 接口封装
│       ├── file_service.py        # 文件读取
│       ├── llm_service.py         # LLM 同步 / 流式调用
│       ├── splitter_service.py    # 文本切分
│       └── vector_store.py        # FAISS 增删查和持久化
├── data/vector_store/             # faiss.index、documents.json
└── logs/                          # 运行日志
```

## 快速开始

### 1. 安装依赖

建议使用 Python 3.10 及以上版本：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env`：

```env
LLM_API_KEY=你的大模型API密钥
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
EMBEDDING_API_KEY=你的向量模型API密钥
EMBEDDING_BASE_URL=向量模型接口地址
EMBEDDING_MODEL=text-embedding-v2
TOP_K=1
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

不要将 `.env`、API Key 或本地数据库提交到 Git。

### 3. 启动后端和前端

后端：

```bash
uvicorn main:app --reload
```

前端另开终端：

```bash
streamlit run app.py
```

- 前端地址：`http://127.0.0.1:8501`
- Swagger：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/health`

### 4. Docker Compose 启动

配置 `.env` 后执行：

```bash
docker compose up --build
```

前端访问 `http://127.0.0.1:8501`，后端访问 `http://127.0.0.1:8000/docs`。

## 核心接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/rag/upload` | 上传 TXT 并构建向量库 |
| POST | `/rag/ask` | 仅检索相关文本片段 |
| POST | `/rag/answer` | 检索增强问答并返回来源 |
| POST | `/rag/conversation/create` | 创建会话 |
| POST | `/rag/clear` | 清空向量库和文档记录 |
| POST | `/chat` | 普通响应接口 |
| POST | `/chat/stream` | SSE 流式响应接口 |

问答请求示例：

```json
{
  "question": "公司迟到扣款规则是什么",
  "conversation_id": 1
}
```

## 已知限制

- 当前仅支持 TXT 文件，暂未实现 PDF、Word 等格式解析
- 当前使用本地 FAISS 和 SQLite，适合单机或小规模知识库
- 用户身份暂使用默认 `user_id=1`，尚未接入鉴权和多租户隔离
- Embedding 维度当前固定为 1024，需要与所配置的向量模型保持一致
- 当前前端为演示型 Streamlit 页面，未提供完整的文档管理和历史会话列表

## 后续计划

- 增加 PDF、Word 等格式解析和文档管理能力
- 接入用户鉴权、访问限流和多用户数据隔离
- 增加自动化测试、RAG 评估指标和持续集成
- 根据数据规模评估迁移至 Milvus 或 PGVector
