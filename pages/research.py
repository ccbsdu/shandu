import streamlit as st
from ..research import show_ollama_test

def show():
    st.title("研究功能")
    
    # 添加功能选择
    tool = st.selectbox(
        "选择工具",
        ["Ollama 测试工具"]
    )
    
    # 显示选中的工具
    if tool == "Ollama 测试工具":
        show_ollama_test()

if __name__ == "__main__":
    show()