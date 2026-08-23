import requests
from app.core.config import settings
from app.core.exceptions import BusinessException

REQUEST_TIMEOUT = 60


def _parse_response(response: requests.Response) -> dict:
    try:
        result = response.json()
    except ValueError as exc:
        raise BusinessException(code=502, msg="大模型接口返回了无法解析的响应") from exc

    if not response.ok:
        error = result.get("error", result)
        if isinstance(error, dict):
            error = error.get("message", error.get("code", "未知错误"))
        if isinstance(error, str) and "insufficient balance" in error.lower():
            error = "大模型账户余额不足，请充值或更换可用的 API Key"
        raise BusinessException(code=502, msg=f"大模型接口调用失败：{error}")

    if not isinstance(result.get("choices"), list) or not result["choices"]:
        raise BusinessException(code=502, msg="大模型接口返回格式异常：缺少 choices")
    return result


def call_llm(question: str) -> str:
    """非流式调用大模型，返回完整回答（单轮）"""
    return call_llm_messages([{"role": "user", "content": question}])


def call_llm_messages(messages: list[dict]) -> str:
    """非流式调用大模型，支持多轮对话，返回完整回答

    messages: [{"role": "system"/"user"/"assistant", "content": str}, ...]
    """
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.LLM_MODEL_NAME,
        "messages": messages
    }
    try:
        resp = requests.post(
            f"{settings.LLM_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise BusinessException(code=502, msg=f"无法连接大模型接口：{exc}") from exc

    result = _parse_response(resp)
    message = result["choices"][0].get("message", {})
    content = message.get("content")
    if not content:
        raise BusinessException(code=502, msg="大模型接口返回格式异常：缺少回答内容")
    return content

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
    try:
        response = requests.post(
            url=f"{settings.LLM_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise BusinessException(code=502, msg=f"无法连接大模型接口：{exc}") from exc

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
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {}).get("content", "")
                if delta:
                    yield delta
