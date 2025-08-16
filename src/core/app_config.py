"""
应用配置管理模块
"""
import os
import json
from typing import Dict, List, Any


class AppConfig:
    """应用配置管理类"""
    
    # 海王对战模式
    SEAKING_MODES = ["🌊对战海王", "🍵反茶艺大师", "🌈决战通讯录之巅"]
    
    # 记忆存储配置
    MEMORY_STORAGE_TYPE = os.getenv("MEMORY_STORAGE_TYPE", "memory")
    ENABLE_IP_ISOLATION = os.getenv("ENABLE_IP_ISOLATION", "true").lower() == "true"
    
    # 环境检测
    IS_DEVELOPMENT = os.getenv("RAILWAY_ENVIRONMENT") is None and os.getenv("PORT") is None
    
    # LangSmith 配置
    LANGCHAIN_TRACING_V2 = "true"
    LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
    LANGCHAIN_PROJECT = "anti-love-test"
    
    @classmethod
    def setup_langsmith(cls):
        """设置 LangSmith 追踪"""
        os.environ["LANGCHAIN_TRACING_V2"] = cls.LANGCHAIN_TRACING_V2
        os.environ["LANGCHAIN_ENDPOINT"] = cls.LANGCHAIN_ENDPOINT
        os.environ["LANGCHAIN_PROJECT"] = cls.LANGCHAIN_PROJECT
    
    @classmethod
    def load_personas(cls) -> Dict[str, Any]:
        """加载海王人设配置"""
        try:
            personas_file = os.path.join("static", "personas.json")
            with open(personas_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to load personas: {e}")
            return {}
    
    @classmethod
    def is_seaking_mode(cls, button_type: str) -> bool:
        """检查是否为海王对战模式"""
        return button_type in cls.SEAKING_MODES
    
    @classmethod
    def print_startup_info(cls):
        """打印启动信息"""
        print(f"[CONFIG] IP Isolation: {cls.ENABLE_IP_ISOLATION}")
        print(f"[CONFIG] Memory Storage: {cls.MEMORY_STORAGE_TYPE}")
        print(f"[CONFIG] Development Mode: {cls.IS_DEVELOPMENT}")
