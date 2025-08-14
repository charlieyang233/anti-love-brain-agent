"""
记忆管理器工厂 - 支持内存模式和Redis模式
"""
import os
from typing import Optional
from .memory_manager import SmartMemoryManager
from .redis_memory_manager import RedisMemoryManager

class MemoryManagerFactory:
    """记忆管理器工厂类"""
    
    @staticmethod
    def create_memory_manager(
        storage_type: str = "memory",  # "memory" 或 "redis"
        user_id: Optional[str] = None,
        max_conversation_window: int = 15,
        **kwargs
    ):
        """
        创建记忆管理器实例
        
        Args:
            storage_type: 存储类型 ("memory" 或 "redis")
            user_id: 用户ID（Redis模式必需）
            max_conversation_window: 对话窗口大小
            **kwargs: 其他配置参数
        
        Returns:
            记忆管理器实例
        """
        
        if storage_type.lower() == "redis":
            # Redis模式配置
            redis_config = {
                "redis_host": os.getenv("REDIS_HOST", "localhost"),
                "redis_port": int(os.getenv("REDIS_PORT", "6379")),
                "redis_db": int(os.getenv("REDIS_DB", "0")),
                "redis_password": os.getenv("REDIS_PASSWORD"),
                "user_id": user_id,
                "max_conversation_window": max_conversation_window,
                "memory_ttl": int(os.getenv("MEMORY_TTL", str(7 * 24 * 3600)))  # 7天
            }
            redis_config.update(kwargs)
            
            try:
                return RedisMemoryManager(**redis_config)
            except Exception as e:
                print(f"Redis连接失败，回退到内存模式: {e}")
                # 回退到内存模式
                return SmartMemoryManager(max_conversation_window=max_conversation_window)
        
        else:
            # 内存模式（默认）
            return SmartMemoryManager(max_conversation_window=max_conversation_window)

# 全局配置
MEMORY_STORAGE_TYPE = os.getenv("MEMORY_STORAGE_TYPE", "memory")  # "memory" 或 "redis"
ENABLE_MULTI_USER = os.getenv("ENABLE_MULTI_USER", "false").lower() == "true"
