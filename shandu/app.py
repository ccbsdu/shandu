import streamlit as st
from shandu.components import research, search, history
from shandu.utils.config import load_config, save_config, DEFAULT_PROVIDERS
from shandu.research.ollama_test import test_ollama_connection  # Changed from relative to absolute import

def init_session():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = load_config().get("api_key", "")

def render_provider_config():
    config = load_config()
    providers = {**config.get("providers", {}), **config.get("custom_providers", {})}
    selected_model = None
    
    with st.sidebar:
        st.title("⚙️ AI提供商配置")
        
        # 选择提供商
        active_provider = config.get("active_provider", "OpenRouter")
        if active_provider not in DEFAULT_PROVIDERS:
            active_provider = "OpenRouter"
            
        provider = st.selectbox(
            "选择AI提供商",
            list(DEFAULT_PROVIDERS.keys()) + ["添加新提供商"],
            index=list(DEFAULT_PROVIDERS.keys()).index(active_provider)
        )
        
        if provider == "添加新提供商":
            with st.form("new_provider"):
                new_name = st.text_input("提供商名称")
                new_url = st.text_input("API基础URL")
                new_key = st.text_input("API密钥", type="password")
                new_models = st.text_area("模型列表(每行一个)")
                
                if st.form_submit_button("添加"):
                    if new_name and new_url and new_key:
                        config.setdefault("custom_providers", {})
                        config["custom_providers"][new_name] = {
                            "base_url": new_url,
                            "api_key": new_key,
                            "models": [m.strip() for m in new_models.split("\n") if m.strip()]
                        }
                        save_config(config)
                        st.rerun()
                return provider, ""
        else:
            # 获取默认配置
            default_config = DEFAULT_PROVIDERS[provider]
            current_config = providers.get(provider, default_config)
            
            # API密钥配置
            new_key = st.text_input(
                f"{provider} API密钥",
                value=current_config.get("api_key", ""),
                type="password",
                help="OpenRouter API密钥格式为: sk-or-v1-xxxxx，请从 https://openrouter.ai/keys 获取"
            )
            
            # 验证API密钥格式
            if provider == "OpenRouter" and new_key and not new_key.startswith("sk-or-v1-"):
                st.error("OpenRouter API密钥格式不正确，应以 sk-or-v1- 开头")
                return provider, ""
                
            # 基础URL配置
            new_url = st.text_input(
                "API基础URL",
                value=current_config.get("base_url", default_config["base_url"]),
                help="OpenRouter默认API地址为: https://openrouter.ai/api/v1"
            )
            
            # 模型选择
            # 移除第一个模型选择部分
            if provider == "OpenRouter":
                groups = {
                    "Gemini": [m for m in default_config["models"] if "gemini" in m.lower()],
                    "Deepseek": [m for m in default_config["models"] if "deepseek" in m.lower()]
                }
                
                st.markdown("### 可用模型")
                for group_name, models in groups.items():
                    with st.expander(group_name, expanded=True):
                        for model in models:
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"- {model}")
                            with col2:
                                if st.button("选择", key=f"select_{model}"):
                                    selected_model = model
                                    config["selected_model"] = model
                                    st.session_state.current_model = model
                                    save_config(config)
                                    st.rerun()
            
            # 保存配置
            if new_key != current_config.get("api_key") or new_url != current_config.get("base_url"):
                config.setdefault("providers", {})
                config["providers"][provider] = {
                    "base_url": new_url,
                    "api_key": new_key,
                    "models": default_config["models"]
                }
                config["active_provider"] = provider
                save_config(config)
            
            return provider, selected_model or config.get("selected_model") or default_config["models"][0]
        
        # 分组显示提供商
        provider_groups = {
            "主流服务": ["OpenRouter"],
            "自定义服务": []  # 这里会自动填充用户添加的自定义提供商
        }
        
        # 选择提供商组
        selected_group = st.selectbox(
            "模型分类",
            list(provider_groups.keys())
        )
        
        # 显示分组下的提供商
        for provider_name in provider_groups[selected_group]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {provider_name}")
            with col2:
                enabled = provider_name in providers
                if st.toggle("启用", value=enabled, key=f"toggle_{provider_name}"):
                    if not enabled:
                        # 添加新提供商
                        config.setdefault("providers", {})
                        config["providers"][provider_name] = {
                            "base_url": "",
                            "api_key": "",
                            "models": []
                        }
                        save_config(config)
                        st.rerun()
                else:
                    if enabled:
                        # 移除提供商
                        if provider_name in config["providers"]:
                            del config["providers"][provider_name]
                        if provider_name in config.get("custom_providers", {}):
                            del config["custom_providers"][provider_name]
                        save_config(config)
                        st.rerun()
        
        st.divider()
        
        # 选择当前使用的提供商
        active_providers = [p for p in providers.keys() if providers[p].get("api_key")]
        if not active_providers:
            st.warning("请先配置至少一个AI提供商")
            return "", ""
            
        provider = st.selectbox(
            "当前使用",
            active_providers,
            index=active_providers.index(config.get("active_provider")) if config.get("active_provider") in active_providers else 0
        )
        
        provider_config = providers[provider]
        
        # API密钥配置
        new_key = st.text_input(
            "API密钥",
            value=provider_config.get("api_key", ""),
            type="password",
            help="点击查看获取API密钥的方法"
        )
        
        # 基础URL配置
        new_url = st.text_input(
            "API基础URL",
            value=provider_config.get("base_url", ""),
            help="可选，留空使用默认地址"
        )
        
        # 模型分组显示
        if provider_config.get("models"):
            st.markdown("### 可用模型")
            
            # 根据提供商调整模型分组
            if provider == "OpenRouter":
                groups = ["Gemma", "Llama3", "Mistral", "Phi"]
            elif provider == "Ollama":
                groups = ["LLaMA", "Mistral", "Gemma", "CodeLLaMA", "Phi"]
            elif provider == "OpenAI":
                groups = ["GPT-3.5", "GPT-4"]
            else:
                groups = ["全部模型"]
            
            for group in groups:
                with st.expander(group, expanded=True):
                    models = [m for m in provider_config["models"] if group.lower() in m.lower()]
                    if not models and group == "全部模型":
                        models = provider_config["models"]
                        
                    for model in models:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"- {model}")
                        with col2:
                            is_free = provider == "Ollama" or "free" in model.lower()
                            st.button("免费" if is_free else "付费", 
                                    key=f"free_{model}", 
                                    disabled=True,
                                    type="secondary" if is_free else "primary")
                        with col3:
                            if st.button("选择", key=f"select_{model}"):
                                st.session_state.selected_model = model
                                return provider, model
        
        if new_key != provider_config.get("api_key") or new_url != provider_config.get("base_url"):
            if provider in config.get("custom_providers", {}):
                config["custom_providers"][provider]["api_key"] = new_key
                config["custom_providers"][provider]["base_url"] = new_url
            else:
                config["providers"][provider]["api_key"] = new_key
                config["providers"][provider]["base_url"] = new_url
            config["active_provider"] = provider
            save_config(config)
        
        return provider, model

def main():
    init_session()
    
    st.set_page_config(
        page_title="Shandu AI 研究助手",
        page_icon="🔍",
        layout="wide"
    )
    
    # 配置提供商
    provider, selected_model = render_provider_config()
    config = load_config()
    provider_config = {**config.get("providers", {}), **config.get("custom_providers", {})}.get(provider, {})
    api_key = provider_config.get("api_key", "")
    
    # 确保选择的模型被正确保存和使用
    if "current_model" not in st.session_state or selected_model != st.session_state.current_model:
        st.session_state.current_model = selected_model
    
    # 设置研究深度和广度的默认值
    depth = "medium"
    breadth = "medium"
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["深度研究", "智能搜索", "历史记录", "研究工具"])
    
    # 使用保存的模型调用研究组件
    with tab1:
        research.render_research_tab(api_key, st.session_state.current_model, depth, breadth)
    
    with tab2:
        search.render_search_tab(api_key, st.session_state.current_model)
        
    with tab3:
        history.render_history_tab()
        
    with tab4:
        from shandu.research import show_ollama_test
        show_ollama_test()

if __name__ == "__main__":
    main()