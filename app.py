from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
from typing import Dict

# 加载环境变量
load_dotenv()

# 配置LangSmith（必须在导入agent之前设置）
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "anti-love-test"
# LANGSMITH_API_KEY应该已经在.env文件中设置了

from src.agent import build_agent
from src.memory_factory import MemoryManagerFactory
from src.intent.core.app_integration import IntentEnabledChatHandler

app = FastAPI(title="Anti Love Brain - 拽姐 Agent")

# 记忆存储配置
MEMORY_STORAGE_TYPE = os.getenv("MEMORY_STORAGE_TYPE", "memory")  # "memory" 或 "redis"
ENABLE_IP_ISOLATION = os.getenv("ENABLE_IP_ISOLATION", "true").lower() == "true"
ENABLE_ENHANCED_ROUTING = os.getenv("ENABLE_ENHANCED_ROUTING", "true").lower() == "true"

# 用户记忆管理器 - 更新为支持增强路由
user_memory_managers: Dict[str, IntentEnabledChatHandler] = {}

class ChatRequest(BaseModel):
    input: str

def get_memory_manager(user_ip: str) -> IntentEnabledChatHandler:
    """获取用户的记忆管理器和聊天处理器"""
    if user_ip not in user_memory_managers:
        # 使用工厂创建记忆管理器
        memory_manager = MemoryManagerFactory.create_memory_manager(
            storage_type=MEMORY_STORAGE_TYPE,
            user_id=user_ip if ENABLE_IP_ISOLATION else "default_user",
            max_conversation_window=15
        )
        
        # 创建增强聊天处理器
        user_memory_managers[user_ip] = IntentEnabledChatHandler(
            memory_manager=memory_manager,
            enable_enhanced_routing=ENABLE_ENHANCED_ROUTING
        )
    return user_memory_managers[user_ip]

@app.post("/chat")
async def chat(request: ChatRequest, req: Request):
    """聊天端点 - 集成增强路由系统"""
    if not ENABLE_IP_ISOLATION:
        user_ip = "default_user"
    else:
        user_ip = req.client.host
    
    try:
        chat_handler = get_memory_manager(user_ip)
        result = chat_handler.process_chat(request.input, user_ip)
        
        return {
            "response": result["response"],
            "debug_info": result.get("debug_info", {}) if os.getenv("DEBUG", "false").lower() == "true" else {},
            "routing_info": result.get("routing_info", {}),
            "performance": result.get("performance", {})
        }
    except Exception as e:
        print(f"[Error] Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_chat(req: Request):
    """重置端点 - 清除短期记忆"""
    if not ENABLE_IP_ISOLATION:
        user_ip = "default_user"
    else:
        user_ip = req.client.host
    
    try:
        chat_handler = get_memory_manager(user_ip)
        result = chat_handler.reset_session()
        
        if result["success"]:
            return {
                "message": result["message"], 
                "memory_stats": result.get("memory_stats", {}),
                "routing_enabled": ENABLE_ENHANCED_ROUTING
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        print(f"[Error] Reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def get_system_status(req: Request):
    """系统状态端点 - 显示路由和记忆状态"""
    if not ENABLE_IP_ISOLATION:
        user_ip = "default_user"
    else:
        user_ip = req.client.host
    
    try:
        chat_handler = get_memory_manager(user_ip)
        status = chat_handler.get_system_status()
        
        # 添加系统级配置信息
        status["system_config"] = {
            "enhanced_routing_enabled": ENABLE_ENHANCED_ROUTING,
            "ip_isolation_enabled": ENABLE_IP_ISOLATION,
            "memory_storage_type": MEMORY_STORAGE_TYPE,
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
        }
        
        return status
    except Exception as e:
        print(f"[Error] Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/routing/stats")
async def get_routing_stats():
    """路由统计端点 - 显示全局路由性能"""
    try:
        total_stats = {
            "total_users": len(user_memory_managers),
            "enhanced_routing_enabled": ENABLE_ENHANCED_ROUTING,
            "per_user_stats": {}
        }
        
        for user_ip, handler in user_memory_managers.items():
            if ENABLE_ENHANCED_ROUTING and hasattr(handler, 'enhanced_integration'):
                user_stats = handler.get_system_status()
                total_stats["per_user_stats"][user_ip] = {
                    "routing_performance": user_stats.get("routing_performance", {}),
                    "memory_stats": user_stats.get("memory_status", {})
                }
        
        return total_stats
    except Exception as e:
        print(f"[Error] Routing stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/favicon.ico")
async def favicon():
    return FileResponse('static/favicon.svg')

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动 Anti Love Brain Agent")
    print(f"📊 增强路由: {'✅ 启用' if ENABLE_ENHANCED_ROUTING else '❌ 禁用'}")
    print(f"🌐 IP隔离: {'✅ 启用' if ENABLE_IP_ISOLATION else '❌ 禁用'}")
    print(f"💾 记忆存储: {MEMORY_STORAGE_TYPE}")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
