#!/usr/bin/env python3
"""
主应用集成模块 - 将增强意图路由系统集成到app.py中
"""

import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.memory_manager import SmartMemoryManager
from src.intent.core.dual_router_memory import DualRouterMemoryIntegration


class IntentEnabledChatHandler:
    """支持增强意图的聊天处理器"""
    
    def __init__(self, memory_manager: SmartMemoryManager, enable_enhanced_routing: bool = True):
        self.memory_manager = memory_manager
        self.enhanced_routing_enabled = enable_enhanced_routing
        
        if self.enhanced_routing_enabled:
            self.enhanced_integration = DualRouterMemoryIntegration(memory_manager)
            print("✅ 双层路由记忆集成系统已启用")
        else:
            # 回退到原始Agent
            from src.agent import build_agent
            self.original_agent = build_agent(memory_manager)
            print("⚠️  使用原始Agent系统")
    
    def process_chat(self, user_input: str, user_ip: str = None) -> Dict[str, Any]:
        """处理聊天请求的主入口"""
        
        # 构造上下文
        memory_stats = self.memory_manager.get_memory_stats()
        context = {
            "user_ip": user_ip,
            "conversation_history": self._get_conversation_history(),
            "user_patterns": memory_stats.get("user_patterns", {})
        }
        
        if self.enhanced_routing_enabled:
            return self._process_with_enhanced_routing(user_input, context)
        else:
            return self._process_with_original_agent(user_input, context)
    
    def _process_with_enhanced_routing(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """使用双层路由处理"""
        try:
            result = self.enhanced_integration.process_with_memory_update(user_input, context)
            
            # 添加调试信息
            result["debug_info"] = result.get("debug_info", {})
            result["debug_info"].update({
                "dual_layer_routing": True,
                "memory_window_size": len(context.get("conversation_history", [])),
                "user_patterns_count": len(context.get("user_patterns", {}))
            })
            
            return result
            
        except Exception as e:
            print(f"[Error] Dual layer routing failed, falling back to original: {e}")
            return self._process_with_original_agent(user_input, context)
    
    def _get_conversation_history(self) -> list:
        """获取对话历史的安全方法"""
        try:
            # 从memory中提取消息历史
            if hasattr(self.memory_manager.memory, 'chat_memory'):
                messages = self.memory_manager.memory.chat_memory.messages
                return [{"type": msg.__class__.__name__, "content": str(msg.content)} for msg in messages[-10:]]
            return []
        except Exception as e:
            print(f"[Warning] Failed to get conversation history: {e}")
            return []
    
    def _process_with_original_agent(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """使用原始Agent处理"""
        try:
            # 获取原始Agent（如果还没有）
            if not hasattr(self, 'original_agent'):
                from src.agent import build_agent
                self.original_agent = build_agent(self.memory_manager)
            
            # 调用原始Agent
            agent_result = self.original_agent.invoke({"input": user_input})
            
            # 标准化返回格式
            return {
                "response": agent_result.get("output", "抱歉，我遇到了一些问题。"),
                "routing_info": {
                    "path": "original_agent",
                    "tools_called": ["langchain_agent"],
                    "success": True
                },
                "performance": {"token_saved": False},
                "memory_stats": self.memory_manager.get_memory_stats(),
                "debug_info": {
                    "enhanced_routing": False,
                    "fallback_reason": "原始Agent处理",
                    "memory_window_size": len(context.get("conversation_history", []))
                },
                "raw": {"langchain_agent": agent_result}
            }
            
        except Exception as e:
            print(f"[Error] Original agent also failed: {e}")
            return self._emergency_response(user_input, str(e))
    
    def _emergency_response(self, user_input: str, error_msg: str) -> Dict[str, Any]:
        """紧急响应机制"""
        emergency_response = "🚨 系统暂时遇到了一些问题，请稍后再试。如果问题持续，请联系管理员。"
        
        return {
            "response": emergency_response,
            "routing_info": {
                "path": "emergency",
                "tools_called": [],
                "success": False
            },
            "performance": {"token_saved": False},
            "memory_stats": self.memory_manager.get_memory_stats(),
            "debug_info": {
                "enhanced_routing": False,
                "error": error_msg,
                "emergency_mode": True
            },
            "raw": {"error": error_msg}
        }
    
    def reset_session(self) -> Dict[str, Any]:
        """重置会话"""
        try:
            # 清除短期记忆，保留长期记忆
            self.memory_manager.clear_session()
            
            return {
                "success": True,
                "message": "会话已重置，长期记忆保留",
                "memory_stats": self.memory_manager.get_memory_stats()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"重置失败: {str(e)}",
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        status = {
            "enhanced_routing_enabled": self.enhanced_routing_enabled,
            "memory_stats": self.memory_manager.get_memory_stats(),
            "system_health": "healthy"
        }
        
        if self.enhanced_routing_enabled:
            try:
                enhanced_stats = self.enhanced_integration.get_enhanced_stats()
                status.update(enhanced_stats)
            except Exception as e:
                status["enhanced_routing_error"] = str(e)
                status["system_health"] = "degraded"
        
        return status


def create_app_integration_patch():
    """生成app.py的集成补丁代码"""
    
    patch_code = '''
# 在app.py顶部添加导入
from src.intent.app_integration import IntentEnabledChatHandler

# 修改用户内存管理器字典的初始化
user_memory_managers: Dict[str, IntentEnabledChatHandler] = {}

# 修改get_memory_manager函数
def get_memory_manager(user_ip: str) -> IntentEnabledChatHandler:
    """获取用户的记忆管理器和聊天处理器"""
    if user_ip not in user_memory_managers:
        memory_manager = SmartMemoryManager(max_conversation_window=15)
        # 创建增强聊天处理器（可以通过环境变量控制是否启用）
        enable_enhanced = os.getenv("ENABLE_ENHANCED_ROUTING", "true").lower() == "true"
        user_memory_managers[user_ip] = IntentEnabledChatHandler(
            memory_manager=memory_manager,
            enable_enhanced_routing=enable_enhanced
        )
    return user_memory_managers[user_ip]

# 修改聊天端点
@app.post("/chat")
async def chat(request: ChatRequest, req: Request):
    user_ip = req.client.host
    
    try:
        chat_handler = get_memory_manager(user_ip)
        result = chat_handler.process_chat(request.input, user_ip)
        
        return {
            "response": result["response"],
            "debug_info": result.get("debug_info", {}),
            "routing_info": result.get("routing_info", {}),
            "performance": result.get("performance", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 修改重置端点
@app.post("/reset")
async def reset_chat(req: Request):
    user_ip = req.client.host
    
    try:
        chat_handler = get_memory_manager(user_ip)
        result = chat_handler.reset_session()
        
        if result["success"]:
            return {"message": result["message"], "memory_stats": result.get("memory_stats", {})}
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 添加新的系统状态端点
@app.get("/system/status")
async def get_system_status(req: Request):
    user_ip = req.client.host
    
    try:
        chat_handler = get_memory_manager(user_ip)
        return chat_handler.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
    
    return patch_code


def test_app_integration():
    """测试应用集成"""
    print("🔧 应用集成测试")
    print("=" * 60)
    
    # 测试增强路由模式
    print("\n1. 测试增强路由模式")
    memory_manager = SmartMemoryManager(max_conversation_window=15)
    enhanced_handler = IntentEnabledChatHandler(memory_manager, enable_enhanced_routing=True)
    
    test_input = "我想要一些撩妹技巧"
    result = enhanced_handler.process_chat(test_input, "127.0.0.1")
    
    print(f"输入: {test_input}")
    print(f"路由: {result['routing_info']['path']}")
    print(f"回复: {result['response']}")
    print(f"Token节省: {result['performance']['token_saved']}")
    
    # 测试原始模式
    print("\n2. 测试原始Agent模式")
    original_handler = IntentEnabledChatHandler(memory_manager, enable_enhanced_routing=False)
    
    result2 = original_handler.process_chat(test_input, "127.0.0.1")
    print(f"路由: {result2['routing_info']['path']}")
    print(f"回复: {result2['response']}")
    
    # 测试重置功能
    print("\n3. 测试重置功能")
    reset_result = enhanced_handler.reset_session()
    print(f"重置成功: {reset_result['success']}")
    print(f"消息: {reset_result['message']}")
    
    # 测试系统状态
    print("\n4. 测试系统状态")
    status = enhanced_handler.get_system_status()
    print(f"增强路由启用: {status['enhanced_routing_enabled']}")
    print(f"系统健康: {status['system_health']}")
    if 'routing_performance' in status:
        routing_perf = status['routing_performance']
        print(f"直接路由率: {routing_perf.get('direct_rate', 0):.1%}")
        print(f"Token节省率: {routing_perf.get('token_savings_rate', 0):.1%}")
    
    print("\n✅ 集成测试完成！")
    
    # 生成集成补丁
    print("\n📋 app.py集成补丁代码已生成，可以查看patch输出")


if __name__ == "__main__":
    test_app_integration()
    
    print("\n" + "="*60)
    print("📋 APP.PY 集成补丁代码")
    print("="*60)
    print(create_app_integration_patch())
