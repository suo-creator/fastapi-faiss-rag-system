from fastapi import UploadFile

async def read_file(file: UploadFile) -> str:
    """读取上传的txt/md文件，返回文本字符串"""
    content_bytes = await file.read()
    # 使用utf‑8解码
    text = content_bytes.decode("utf‑8")
    await file.seek(0)
    return text

# 新增：读取磁盘上本地文件路径，用于调试
def read_local_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf‑8") as f:
        return f.read()