from langchain_text_splitters import CharacterTextSplitter
def split_text(text: str, filename: str, chunk_size: int = 800):
    # ========== 保留你原有切分逻辑 ==========
    # 把你之前的切分代码放在这里，最终输出纯文本列表 chunk_list
    # 示例：如果用的是字符切分，替换成自己的实现即可

    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
    chunk_list = splitter.split_text(text)


    # 封装元数据，统一返回结构
    result = []
    for idx, chunk_text in enumerate(chunk_list):
        result.append({
            "text": chunk_text,
            "metadata": {
                "filename": filename,
                "paragraph": idx + 1,  # 段落号从1开始计数
                "page": None  # txt文档无页码，预留字段，后续支持PDF可补充
            }
        })
    return result