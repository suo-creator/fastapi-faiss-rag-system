def split_text(text: str, chunk_size: int = 200, overlap: int = 30) -> list[str]:
    """简单文本切分"""
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = start + chunk_size - overlap
    return chunks