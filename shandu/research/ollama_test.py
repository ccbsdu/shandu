import requests
import streamlit as st
import urllib3
from shandu.utils.search import search_web

def test_ollama_connection():
    """测试 Ollama 服务连接"""
    try:
        # 尝试直接使用 socket 测试端口
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()
        
        if result != 0:
            return False, "端口 11434 未开放，请确认 Ollama 服务是否启动"
            
        # 使用更低级别的连接参数
        urllib3.disable_warnings()
        
        session = requests.Session()
        response = session.get(
            "http://127.0.0.1:11434/api/tags",
            timeout=(5, 30),
            headers={
                'Host': 'localhost',
                'Connection': 'keep-alive',
                'Accept': 'application/json',
                'User-Agent': 'curl/7.79.1'
            },
            verify=False,
            allow_redirects=False
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                # 直接返回模型列表
                models = []
                for model in data.get('models', []):
                    if isinstance(model, dict) and 'name' in model:
                        models.append(model['name'])
                    elif isinstance(model, str):
                        models.append(model)
                return True, {'models': [{'name': m} for m in models]}
            except Exception as e:
                return False, f"数据解析失败: {str(e)}"
        
        error_msg = "服务异常:\n"
        error_msg += f"- 状态码: {response.status_code}\n"
        error_msg += f"- 响应头: {dict(response.headers)}\n"
        error_msg += f"- 响应内容: {response.text[:200] if response.text else '无'}"
        return False, error_msg
        
    except requests.exceptions.Timeout:
        return False, "连接超时 (30秒)"
    except requests.exceptions.ConnectionError as e:
        return False, f"连接被拒绝: {str(e)}"
    except Exception as e:
        return False, f"未知错误: {str(e)}"

def test_model_generation(model_name: str, prompt: str, context: str = None):
    """测试模型生成能力"""
    try:
        # 构建提示词
        if context:
            full_prompt = f"""基于以下搜索结果进行总结：

搜索结果：
{context}

研究主题：
{prompt}

请提供详细的分析和总结。
"""
        else:
            full_prompt = prompt

        session = requests.Session()
        response = session.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            },
            timeout=(5, 120),  # 增加超时时间
            headers={
                'Host': 'localhost',
                'Connection': 'keep-alive',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'curl/7.79.1'
            },
            verify=False,
            allow_redirects=False
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                response_text = data.get('response', '')
                return True, response_text.strip()
            except Exception as e:
                return False, f"响应解析失败: {str(e)}"
                
        error_msg = "生成失败:\n"
        error_msg += f"- 状态码: {response.status_code}\n"
        error_msg += f"- 响应头: {dict(response.headers)}\n"
        error_msg += f"- 响应内容: {response.text[:200] if response.text else '无'}"
        return False, error_msg
        
    except requests.exceptions.Timeout:
        return False, "生成超时 (60秒)"
    except requests.exceptions.ConnectionError as e:
        return False, f"连接失败: {str(e)}"
    except Exception as e:
        return False, f"未知错误: {str(e)}"

def show_ollama_test():
    """显示 Ollama 研究工具"""
    st.title("Ollama 研究工具")
    
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
    
    # 深度研究
    with st.expander("深度研究", expanded=True):
        success, result = test_ollama_connection()
        if success:
            models = [m['name'] for m in result.get('models', [])]
            model = st.selectbox("选择模型", models)
            
            research_query = st.session_state.get("research_query", "")
            prompt = st.text_area("研究主题", value=research_query)
            
            # 添加搜索结果输入
            search_results = st.text_area(
                "搜索结果（可选）",
                placeholder="如果有相关搜索结果，请粘贴在这里，模型将基于这些内容进行分析总结...",
                height=200
            )
            
            if st.button("开始研究"):
                if not prompt:
                    st.error("请输入研究主题")
                    return
                    
                # 先进行搜索
                with st.spinner("正在搜索相关信息..."):
                    search_results = search_web(prompt)
                    search_text = "\n\n".join(search_results)
                    
                # 更新搜索结果框
                st.session_state.search_results = search_text
                
                # 进行研究分析
                with st.spinner("正在研究分析..."):
                    success, response = test_model_generation(
                        model, 
                        prompt,
                        context=search_text
                    )
                    if success:
                        st.markdown("### 研究结果")
                        st.write(response)
                    else:
                        st.error(response)
        else:
            st.warning("请先确保 Ollama 服务正常运行")