import streamlit as st
from shandu.agents import ResearchGraph
from datetime import datetime

def render_research_tab(api_key: str, model: str, depth: str, breadth: str):
    st.header("深度研究")
    
    # 更新模型状态，确保使用传入的新模型
    st.session_state.current_model = model
    
    query = st.text_area("研究主题", 
                        placeholder="输入你想研究的主题...",
                        height=100)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        detail_level = st.select_slider(
            "详细程度",
            options=["low", "medium", "high"],
            value="medium"
        )
    with col2:
        # 获取当前提供商的模型列表
        from shandu.utils.config import load_config
        config = load_config()
        providers = {**config.get("providers", {}), **config.get("custom_providers", {})}
        current_provider = config.get("active_provider")
        
        if current_provider and current_provider in providers:
            provider_config = providers[current_provider]
            provider_models = provider_config.get("models", [])
            if isinstance(provider_models, list) and provider_models:
                if isinstance(provider_models[0], dict):
                    provider_models = [m['name'] for m in provider_models]
                
                selected_model = st.selectbox(
                    "选择模型",
                    options=provider_models,
                    index=provider_models.index(model) if model in provider_models else 0,
                    key="model_selector"
                )
                if selected_model != model:
                    st.session_state.current_model = selected_model
                    config["selected_model"] = selected_model
                    from shandu.utils.config import save_config
                    save_config(config)
                    st.rerun()
                    
        st.info(f"当前使用模型：{model}")
    
    if st.button("开始研究", type="primary"):
        if not api_key and st.session_state.get("active_provider") != "Ollama":
            st.error("请先配置 API Key")
            return
            
        if not query:
            st.error("请输入研究主题")
            return
            
        with st.spinner("正在进行研究分析..."):
            try:
                # 根据提供商选择不同的处理逻辑
                if st.session_state.get("active_provider") == "Ollama":
                    from shandu.research.ollama_test import test_model_generation
                    success, response = test_model_generation(model, query)
                    if success:
                        results_text = response
                        st.markdown("### 研究结果")
                        st.write(results_text)
                        
                        # 提供下载按钮
                        st.download_button(
                            label="下载研究报告",
                            data=results_text,
                            file_name=f"研究报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                        
                        # 保存到历史记录
                        st.session_state.history.append({
                            "type": "research",
                            "query": query,
                            "results": results_text,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                    else:
                        st.error(response)
                else:
                    # 原有的研究逻辑
                    researcher = ResearchGraph(api_key=api_key, model=model)
                    results = researcher.analyze_topic(topic=query)
                    results.sources.append(f"使用模型: {model}")
                    
                    with st.container():
                        st.markdown(results.to_markdown())
                    
                    st.download_button(
                        label="下载研究报告",
                        data=results.to_markdown(),
                        file_name=f"研究报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
                    
                    st.session_state.history.append({
                        "type": "research",
                        "query": query,
                        "results": results.to_markdown(),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
            except Exception as e:
                st.error(f"研究过程中发生错误: {str(e)}")