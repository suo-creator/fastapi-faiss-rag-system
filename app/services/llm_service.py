import requests
from app.core.config import settings
def call_llm(question: str) -> str:
    """非流式调用大模型，返回完整回答"""
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.LLM_MODEL_NAME,
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    resp = requests.post(f"{settings.LLM_BASE_URL}/chat/completions", headers=headers, json=payload)
    result = resp.json()
    return result["choices"][0]["message"]["content"]

# 流式生成器
def stream_llm(question: str):
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.LLM_MODEL_NAME,
        "messages": [{"role": "user", "content": question}],
        "stream": True   # 开启流式！关键参数
    }
    # stream=True 必须加上
    response = requests.post(
        url=f"{settings.LLM_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        stream=True
    )

    # 逐行读取返回流
    for line in response.iter_lines():
        if line:
            line_text = line.decode("utf-8")
            # 流式返回前缀 data: ，过滤无关内容
            if line_text.startswith("data:"):
                data_str = line_text[5:].strip()
                # 结束标志
                if data_str == "[DONE]":
                    break
                import json
                chunk = json.loads(data_str)
                # 取出增量文本
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta
