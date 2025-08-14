#!/usr/bin/env python3
"""
主集成文件 - 为app.py提供增强的意图路由功能
"""

import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.intent.agent_adapter import IntentAwareAgent


class EnhancedAntiLoveBrainService:
    """增强的反恋爱脑服务 - 集成意图路由"""
    
    def __init__(self):
        """初始化服务"""
        self.agent = None
        self.is_initialized = False
        
    def initialize(self):
        """延迟初始化 - 避免导入时的初始化开销"""
        if not self.is_initialized:
            try:
                print("🚀 正在初始化增强反恋爱脑服务...")
                self.agent = IntentAwareAgent()
                self.agent.configure(debug_mode=False)  # 生产环境关闭调试
                self.is_initialized = True
                print("✅ 增强服务初始化成功")
                return True
            except Exception as e:
                print(f"❌ 增强服务初始化失败: {e}")
                return False
        return True
    
    def process_message(self, user_message: str) -> str:
        """
        处理用户消息的主入口
        Args:
            user_message: 用户输入的消息
        Returns:
            处理后的回复消息
        """
        # 确保已初始化
        if not self.initialize():
            return "服务初始化失败，请稍后重试"
        
        try:
            # 使用意图感知Agent处理消息
            result = self.agent.process_input(user_message)
            
            # 提取回复消息
            message = result.get("message", "处理完成")
            
            # 如果有额外信息，可以添加到回复中
            if result.get("tool") and result.get("pipeline"):
                # 生产环境可以隐藏这些技术细节
                pass
            
            return message
            
        except Exception as e:
            print(f"[Error] Message processing failed: {e}")
            return "处理出错，请重试"
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        if not self.is_initialized or not self.agent:
            return {"status": "not_initialized"}
        
        return self.agent.get_stats()


# 全局服务实例
enhanced_service = EnhancedAntiLoveBrainService()


def process_with_enhanced_routing(user_message: str) -> str:
    """
    使用增强路由处理用户消息
    这是为app.py提供的主要接口
    
    Args:
        user_message: 用户输入的消息
    Returns:
        处理后的回复
    """
    return enhanced_service.process_message(user_message)


def get_routing_stats() -> Dict[str, Any]:
    """获取路由统计信息"""
    return enhanced_service.get_service_stats()


def demo_comparison():
    """演示新旧系统的对比"""
    print("🆚 新旧系统对比演示")
    print("=" * 60)
    
    test_cases = [
        "给我一套海王话术练习",
        "他总是威胁我，我该怎么办？", 
        "今天心情不好，想找人聊天",
        "我男朋友可能出轨了，我该怎么办？",
        "朋友被PUA了，我该如何帮助她？"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {user_input}")
        print("-" * 40)
        
        # 使用增强路由处理
        result = process_with_enhanced_routing(user_input)
        print(f"增强回复: {result}")
    
    # 显示统计
    print("\n📊 路由统计:")
    stats = get_routing_stats()
    if "intent_routing" in stats:
        routing_stats = stats["intent_routing"]
        print(f"总请求: {routing_stats['total']}")
        print(f"直接路由: {routing_stats['routed']} ({routing_stats['routed_rate']})")
        print(f"兜底处理: {routing_stats['fallback']} ({routing_stats['fallback_rate']})")


if __name__ == "__main__":
    demo_comparison()
