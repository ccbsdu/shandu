import os
import json
from pathlib import Path
from typing import Dict, List

CONFIG_FILE = Path.home() / ".shandu" / "config.json"

DEFAULT_PROVIDERS = {
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "",
        "models": [
            "google/gemini-2.0-flash-thinking-exp:free",
            "google/gemini-2.0-flash-thinking-exp-1219:free",
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "google/gemini-2.0-pro-exp-02-05:free",
            "deepseek/deepseek-r1-distill-llama-70b:free",
            "deepseek/deepseek-chat:free",
            "deepseek/deepseek-r1:free"
        ]
    }
}

def get_default_config():
    return {
        "providers": DEFAULT_PROVIDERS,
        "active_provider": "OpenRouter",
        "custom_providers": {}
    }

def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        default_config = get_default_config()
        save_config(default_config)
        return default_config
    
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return get_default_config()

def save_config(config):
    """保存配置到文件"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)