import streamlit as st

# 页面基础配置（必须写在最前面）
st.set_page_config(
    page_title="RAG 文档问答系统",
    page_icon="📄",
    layout="wide"
)

# 页面标题
st.title("📄 基于 RAG 的智能文档问答系统")
st.divider()

# 项目介绍
st.subheader("项目功能")
st.write("✅ 支持上传 TXT 文档，自动构建知识库")
st.write("✅ 基于文档内容智能问答，拒绝编造")
st.write("✅ 回答自带引用来源，可追溯原文段落")

st.divider()
st.caption("开发进度：第4周 Day1 首页搭建完成")

import requests

# ========== 后端接口地址，改成你自己的 ==========
BASE_URL = "http://127.0.0.1:8000/rag"

st.subheader("📤 第一步：上传文档")
uploaded_file = st.file_uploader("选择一个 TXT 文档", type=["txt"])

if uploaded_file is not None:
    if st.button("开始上传并构建知识库"):
        with st.spinner("正在上传并处理文档..."):
            try:
                # 调用后端 /upload 接口
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
                response = requests.post(f"{BASE_URL}/upload", files=files)

                if response.status_code == 200:
                    st.success(f"✅ 文档「{uploaded_file.name}」上传成功！")
                    # 把文件名存到会话里，后面用
                    st.session_state["current_file"] = uploaded_file.name
                else:
                    st.error("❌ 上传失败，请检查后端服务是否启动")
            except Exception as e:
                st.error(f"❌ 请求出错：{str(e)}")

st.divider()

st.subheader("💬 第二步：开始问答")

# 新增：右上角清空按钮
col1, col2 = st.columns([4, 1])
with col1:
    st.write("")
with col2:
    if st.button("清空聊天记录", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()
    # =====新增：清空后端知识库按钮（写在app.py里面）=====
    if st.button(label="🗑️清空知识库", use_container_width=True):
        try:
            res = requests.post(f"{BASE_URL}/clear")
            if res.status_code == 200:
                st.success("✅知识库已清空")
                st.session_state.pop("current_file", None)
                st.session_state["chat_history"] = []
                st.rerun()
            else:
                st.error("清空知识库失败")
        except Exception as e:
            st.error(f"请求后端失败，请确认FastAPI已经启动：{e}")
# 如果还没上传文档，禁用输入并提示
if "current_file" not in st.session_state:
    st.info("ℹ️ 请先在上方上传文档，再开始提问")
else:
    # 初始化聊天历史（用 session_state 保存页面刷新不丢失）
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # 渲染所有历史聊天消息
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # 如果是 AI 消息且有来源，也显示来源
            if message["role"] == "assistant" and "sources" in message:
                st.caption("📚 引用来源：")
                for idx, doc in enumerate(message["sources"]):
                    meta = doc.get("metadata", {})
                    filename = meta.get("filename", "未知文件")
                    paragraph = meta.get("paragraph", "未知段落")
                    st.caption(f"- 来源 {idx+1}：{filename} - 第 {paragraph} 段")

    # 聊天输入框
    user_input = st.chat_input("请输入你的问题...")

    if user_input:
        # 1. 把用户消息加入历史，并显示
        user_msg = {"role": "user", "content": user_input}
        st.session_state["chat_history"].append(user_msg)
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. 调用后端接口，获取真实回答
        with st.chat_message("assistant"):
            with st.spinner("正在检索文档并生成回答..."):
                try:
                    # 请求后端 /ask 接口
                    data = {"question": user_input}
                    response = requests.post(f"{BASE_URL}/answer", json=data)

                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("answer", "未获取到回答")
                        related_docs = result.get("related_docs", [])

                        # 显示回答
                        st.markdown(answer)

                        # 新增：显示引用来源
                        if related_docs:
                            st.caption("📚 引用来源：")
                            for idx, doc in enumerate(related_docs):
                                meta = doc.get("metadata", {})
                                filename = meta.get("filename", "未知文件")
                                paragraph = meta.get("paragraph", "未知段落")
                                st.caption(f"- 来源 {idx + 1}：{filename} - 第 {paragraph} 段")
                        # 只在这里存入一次最终回答，不会重复新增记录
                        st.session_state["chat_history"].append({
                            "role": "assistant",
                            "content": answer,
                            "sources": related_docs
                        })
                    else:
                        st.error("❌ 问答接口调用失败")
                except Exception as e:
                    st.error(f"❌ 请求出错: {str(e)}")


