import streamlit as st
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import wikipedia
from googlesearch import search
import pandas as pd

def search_google(query: str, max_results: int) -> List[Dict]:
    try:
        results = []
        for url in search(query, num_results=max_results, lang="zh"):
            try:
                response = requests.get(url, timeout=5)
                response.encoding = response.apparent_encoding  # 自动检测编码
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 获取标题
                title = soup.title.string if soup.title else url
                title = title.strip()
                
                # 获取描述
                snippet = None
                # 尝试不同的 meta 描述标签
                for meta in soup.find_all('meta'):
                    if meta.get('name', '').lower() in ['description', 'og:description']:
                        snippet = meta.get('content', '')
                        break
                
                if not snippet:
                    # 如果没有描述，提取正文前200个字符
                    text = soup.get_text()
                    snippet = ' '.join(text.split())[:200]
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet + "..." if snippet else "暂无描述"
                })
            except Exception as e:
                continue
        return results
    except Exception as e:
        st.warning(f"Google搜索出错: {str(e)}")
        return []

def search_wikipedia(query: str, max_results: int) -> List[Dict]:
    try:
        wikipedia.set_lang("zh")
        search_results = wikipedia.search(query, results=max_results)
        results = []
        for title in search_results:
            try:
                page = wikipedia.page(title)
                results.append({
                    'title': page.title,
                    'url': page.url,
                    'snippet': page.summary[:200] + "..."
                })
            except:
                continue
        return results
    except Exception as e:
        st.warning(f"维基百科搜索出错: {str(e)}")
        return []

def search_arxiv(query: str, max_results: int) -> List[Dict]:
    try:
        response = requests.get(
            'http://export.arxiv.org/api/query',
            params={
                'search_query': query,
                'max_results': max_results,
                'sortBy': 'relevance'
            }
        )
        soup = BeautifulSoup(response.text, 'xml')
        entries = soup.find_all('entry')
        
        results = []
        for entry in entries:
            results.append({
                'title': entry.title.text,
                'url': entry.id.text,
                'snippet': entry.summary.text[:200] + "..."
            })
        return results
    except Exception as e:
        st.warning(f"ArXiv搜索出错: {str(e)}")
        return []

def get_ollama_models() -> List[Dict]:
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            # 对模型进行分类
            categorized_models = {
                "通用模型": [],
                "代码模型": [],
                "特殊模型": []
            }
            
            for model in models:
                name = model['name']
                if 'coder' in name.lower():
                    categorized_models["代码模型"].append(model)
                elif any(x in name.lower() for x in ['llama', 'mixtral', 'glm']):
                    categorized_models["通用模型"].append(model)
                else:
                    categorized_models["特殊模型"].append(model)
            
            return categorized_models
    except Exception as e:
        st.warning(f"获取Ollama模型列表失败: {str(e)}")
        return {}

def render_search_tab(api_key, model):
    st.header("智能搜索")
    
    # 添加模型选择
    selected_model = None
    if model == "ollama":
        with st.sidebar:
            st.subheader("Ollama 模型选择")
            
            # 获取并显示模型列表
            model_categories = get_ollama_models()
            
            if model_categories:
                # 检查是否已经选择了模型
                if 'current_model' not in st.session_state:
                    st.session_state.current_model = None
                
                # 选择模型类别
                category = st.selectbox(
                    "选择模型类别",
                    list(model_categories.keys()),
                    key="model_category"
                )
                
                if category and model_categories[category]:
                    # 选择具体模型
                    model_names = [m['name'] for m in model_categories[category]]
                    selected_model = st.selectbox(
                        "选择模型",
                        model_names,
                        key="model_name"
                    )
                    
                    # 测试模型是否可用
                    if selected_model and st.button("测试模型"):
                        with st.spinner(f"正在测试模型 {selected_model} ..."):
                            try:
                                response = requests.post(
                                    "http://localhost:11434/api/generate",
                                    json={
                                        "model": selected_model,
                                        "prompt": "你好",
                                        "stream": False
                                    }
                                )
                                if response.status_code == 200:
                                    st.session_state.current_model = selected_model
                                    st.success(f"模型 {selected_model} 加载成功！")
                                else:
                                    st.error("模型加载失败，请重试")
                            except Exception as e:
                                st.error(f"模型测试失败: {str(e)}")
                    
                    # 显示当前选择的模型
                    if st.session_state.current_model:
                        st.info(f"当前使用模型: {st.session_state.current_model}")
            else:
                st.warning("未找到可用的 Ollama 模型")
    
    query = st.text_input("搜索关键词")
    
    col1, col2 = st.columns(2)
    with col1:
        engines = st.multiselect(
            "搜索引擎",
            ["Google", "维基百科", "ArXiv", "GitHub"],
            default=["Google", "维基百科"]
        )
    
    with col2:
        max_results = st.slider("最大结果数", 5, 30, 15)
    
    if st.button("搜索", type="primary"):
        if not query:
            st.error("请输入搜索关键词")
            return
            
        with st.spinner("正在搜索..."):
            try:
                results = []
                
                for engine in engines:
                    if engine == "Google":
                        results.extend(search_google(query, max_results))
                    elif engine == "维基百科":
                        results.extend(search_wikipedia(query, max_results))
                    elif engine == "ArXiv":
                        results.extend(search_arxiv(query, max_results))
                
                if results:
                    st.success(f"找到 {len(results)} 个结果")
                    
                    # 使用选定的模型处理结果
                    if model == "ollama" and selected_model:
                        with st.spinner(f"使用 {selected_model} 处理搜索结果..."):
                            # 调用 Ollama API 处理结果
                            for result in results:
                                response = requests.post(
                                    "http://localhost:11434/api/generate",
                                    json={
                                        "model": selected_model,
                                        "prompt": f"请总结以下内容：{result['snippet']}"
                                    }
                                )
                                if response.status_code == 200:
                                    result['ai_summary'] = response.json().get('response', '')
                    
                    # 显示结果
                    for result in results:
                        with st.container():
                            st.markdown(f"### {result['title']}")
                            if 'ai_summary' in result:
                                st.markdown("AI 总结：")
                                st.markdown(result['ai_summary'])
                            st.markdown(result['snippet'])
                            st.markdown(f"[查看原文]({result['url']})")
                            st.divider()
                else:
                    st.info("未找到相关结果")
                
                st.session_state.history.append({
                    "type": "search",
                    "query": query,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                st.error(f"搜索过程中发生错误: {str(e)}")