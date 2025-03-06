import requests
import streamlit as st
import urllib3
from pathlib import Path

def test_ollama_connection():
    """测试 Ollama 服务连接"""
    # ... 代码与原文件相同 ...

def test_model_generation(model_name: str, prompt: str):
    """测试模型生成能力"""
    # ... 代码与原文件相同 ...

def show_ollama_test():
    """显示 Ollama 测试工具"""
    st.title("Ollama 测试工具")
    
    # 测试连接
    with st.expander("服务状态", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 服务连接状态")
        with col2:
            if st.button("测试连接", type="primary"):
                with st.spinner("正在连接..."):
                    success, result = test_ollama_connection()
                    if success:
                        st.success("Ollama 服务运行正常")
                        st.json(result)
                    else:
                        st.error(result)
                        st.info("调试建议：\n1. 确认 Ollama 服务是否运行\n2. 检查端口 11434 是否被占用\n3. 尝试重启 Ollama 服务")
    
    # 模型测试
    with st.expander("模型测试", expanded=True):
        success, result = test_ollama_connection()
        if success:
            models = [m['name'] for m in result.get('models', [])]
            model = st.selectbox("选择模型", models)
            prompt = st.text_area("输入提示词", value="你好，请做个自我介绍。")
            
            if st.button("测试生成"):
                with st.spinner("正在生成..."):
                    success, response = test_model_generation(model, prompt)
                    if success:
                        st.markdown("### 生成结果")
                        st.write(response)
                    else:
                        st.error(response)
        else:
            st.warning("请先确保 Ollama 服务正常运行")