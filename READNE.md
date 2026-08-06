# RAG 对话服务
## 项目简介
基于FastAPI构建的大模型对话后端服务 ,目前已实现基础对话接口与流式打字机输出能力,为后续 RAG（检索增强生成）知识库功能提供工程化基础骨架。项目采用分层架构设计,职责分离清晰,便于后续功能扩展与维护。
## 技术栈
* Web 框架:FastAPI + Uvicorn（ASGI 高性能服务）
* 配置管理:python-dotenv + 环境变量（密钥硬编码零侵入）
* 模型对接:兼容 OpenAI 协议的大模型 API（DeepSeek、通义千问等主流厂商均可适配）
* 响应模式:同步一次性返回 + SSE 流式输出双模式支持
## 项目目录结构
```markdown
rag_project/
├── .env                    # 环境变量配置（密钥、模型地址等,不提交 Git）
├── .gitignore              # Git 忽略文件规则
├── README.md               # 项目说明文档
└── app/
    ├── main.py             # 程序入口,统一注册路由
    ├── api/                # 接口路由层:仅处理请求接收与响应封装
    │   ├── __init__.py
    │   └── chat.py         # 对话相关接口集合
    ├── services/           # 业务逻辑层:封装大模型调用核心逻辑
    │   ├── __init__.py
    │   └── llm_service.py  # 大模型同步/流式调用函数
    └── core/               # 核心配置层:全局配置与环境变量读取
        ├── __init__.py
        └── config.py       # 统一配置管理实例
   ```
## 环境准备与安装
### 1. 环境要求
Python 3.9 及以上版本
### 2. 创建并激活虚拟环境
```bash
#在项目根目录新建虚拟环境
python -m venv venv
#Windows 系统激活虚拟环境
venv\Scripts\activate
#Mac / Linux 系统激活虚拟环境
source venv/bin/activate
```
### 3. 安装项目依赖
```bash
pip install fastapi uvicorn python-dotenv requests
```

### 4. 配置环境变量
在项目根目录新建 .env 文件,填入你的大模型配置信息:
```env
LLM_API_KEY=你的大模型API密钥
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
```

## 启动项目
1. 终端进入项目根目录 rag_project
2. 确认虚拟环境处于激活状态
3. 执行启动命令:
```bash
uvicorn app.main:app --reload
```
4. 服务启动成功后可访问:
在线接口文档(Swagger UI):`http://127.0.0.1:8000/docs`
健康检查地址:`http://127.0.0.1:8000/health`
## 接口说明
1. 健康检查接口

* 请求方式:GET
* 接口路径:/health
* 功能描述:检测服务是否正常运行,可用于服务监控
* 返回示例:

```json
{
  "status": "ok",
  "msg": "服务正常运行"
}
 ```

2. 普通对话接口(非流式)

* 请求方式:POST
* 接口路径:/chat
* 功能描述:等待大模型生成完整回答后一次性返回
* 请求体:
```json
{
  "question": "你好,请简单介绍一下Python"
}
```
返回示例:
```json
{
  "answer": "Python是一种解释型、面向对象的高级编程语言,语法简洁易懂..."
}
```
3. 流式对话接口(打字机效果)

* 请求方式:POST
* 接口路径:/chat/stream
* 功能描述:遵循 SSE 协议逐段推送文本,实现打字机式输出效果,降低用户等待感知
* 请求体:

```json
{
  "question": "你好,请简单介绍一下Python"
}
```
响应格式:文本流,持续推送回答片段,生成结束后自动断开连接
## 接口测试方式
### 方式 1:Swagger 在线调试
浏览器打开`http://127.0.0.1:8000/docs` ,找到对应接口点击 Try it out,填写参数后即可直接调试。
### 方式 2:流式接口本地测试脚本
在项目根目录新建 test_stream.py 文件:
```python
import requests
url = "http://127.0.0.1:8000/chat/stream"
json_data = {"question": "简单介绍一下FastAPI框架"}
with requests.post(url, json=json_data, stream=True) as resp:
    for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
        print(chunk, end="")
```
运行脚本即可在控制台看到逐字输出的效果:
```
python test_stream.py
```
## 后续迭代规划
*  接入向量数据库,实现 RAG 知识库检索与增强回答
*  支持多轮对话上下文记忆能力
*  新增文档上传、解析与向量化接口
*  增加接口鉴权、访问限流与调用日志
*  对接前端页面,实现完整可视化对话交互
## 注意事项
1. .env 文件包含敏感密钥信息,请勿提交到 Git 仓库,已在 .gitignore 中配置自动忽略
2. 启动服务时请确保终端位于项目根目录,避免出现环境变量读取失败、模块导入报错
3. Swagger 文档页面无法直观展示流式打字机效果,流式接口建议使用脚本或前端页面测试














