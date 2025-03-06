import requests
import streamlit as st

def test_ollama_connection():
    """测试 Ollama 服务连接"""
    try:
        # 尝试直接使用 socket 测试端口
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 11434))  # 使用 127.0.0.1 替代 localhost
        sock.close()
        
        if result != 0:
            return False, "端口 11434 未开放，请确认 Ollama 服务是否启动"
            
        # 使用更低级别的连接参数
        import urllib3
        urllib3.disable_warnings()
        
        session = requests.Session()
        response = session.get(
            "http://127.0.0.1:11434/api/tags",  # 使用 127.0.0.1
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
        
        # 打印详细的调试信息
        st.write(f"连接信息:")
        st.write(f"- 状态码: {response.status_code}")
        st.write(f"- 响应头: {dict(response.headers)}")
        st.write(f"- 请求URL: {response.url}")
        st.write(f"- 请求头: {dict(response.request.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                st.write("- JSON解析成功")
                return True, data
            except Exception as e:
                st.write(f"- 原始响应: {response.text[:200]}")
                return False, f"数据解析失败: {str(e)}"
                
        error_msg = "服务异常:\n"
        error_msg += f"- 状态码: {response.status_code}\n"
        error_msg += f"- 响应头: {dict(response.headers)}\n"
        error_msg += f"- 响应内容: {response.text[:200] if response.text else '无'}\n"
        error_msg += f"- 请求头: {dict(response.request.headers)}"
        return False, error_msg
        
    except requests.exceptions.Timeout:
        return False, "连接超时 (30秒)"
    except requests.exceptions.ConnectionError as e:
        return False, f"连接被拒绝: {str(e)}"
    except Exception as e:
        return False, f"未知错误: {str(e)}\n类型: {type(e).__name__}"

def test_model_generation(model_name: str, prompt: str):
    """测试模型生成能力"""
    try:
        session = requests.Session()
        response = session.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": model_name,
                "prompt": "请直接回答，不要返回JSON格式：" + prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            },
            timeout=(5, 60),
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
                
                # 尝试解析JSON响应
                try:
                    import json
                    json_data = json.loads(response_text)
                    if isinstance(json_data, dict):
                        # 如果是JSON格式，提取有用信息
                        if 'solution' in json_data:
                            solution = json_data['solution'][0]
                            response_text = '\n'.join(f"{k}: {v}" for k, v in solution.items())
                except:
                    # 如果不是JSON格式，直接使用原文本
                    pass
                
                return True, response_text.strip()
            except Exception as e:
                st.write(f"- 原始响应: {response.text[:200]}")
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
        return False, f"未知错误: {str(e)}\n类型: {type(e).__name__}"

def main():
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

if __name__ == "__main__":
    main()