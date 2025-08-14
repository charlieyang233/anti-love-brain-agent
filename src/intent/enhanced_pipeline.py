#!/usr/bin/env python3
"""
增强管道 - 集成意图路由到现有Agent架构
"""

import sys
import os
from typing import Dict, Any, Optional

# 添加路径以支持模块导入
sys.path.append(os.path.join(os.path.dirname(__file__)))
from basic_router import intent_route, Route

class EnhancedPipeline:
    """增强的意图路由管道"""
    
    def __init__(self, original_agent=None):
        """
        初始化增强管道
        Args:
            original_agent: 现有的Agent执行器
        """
        self.original_agent = original_agent
        self.stats = {"total": 0, "routed": 0, "fallback": 0}
    
    def handle_user_input(self, user_text: str, debug: bool = True) -> Dict[str, Any]:
        """
        处理用户输入的主入口
        Args:
            user_text: 用户输入文本
            debug: 是否打印调试信息
        Returns:
            处理结果字典
        """
        self.stats["total"] += 1
        
        # 1. 意图路由
        route = intent_route(user_text)
        
        if debug:
            print(f"[intentRoute] tool='{route.tool}', reason='{route.reason}', confidence={route.confidence:.2f}")
        
        # 2. 根据路由结果处理
        try:
            if route.tool in ["seaking_tool", "help_tool", "roast_tool", "talk_tool"]:
                # 直接路由到工具
                self.stats["routed"] += 1
                return self._handle_direct_route(user_text, route)
            
            elif route.tool == "severity_analyzer":
                # 需要进一步分析
                self.stats["routed"] += 1
                return self._handle_severity_route(user_text, route)
            
            else:
                # 兜底：交给原Agent
                self.stats["fallback"] += 1
                return self._handle_agent_fallback(user_text, route)
                
        except Exception as e:
            print(f"[Error] Pipeline execution failed: {e}")
            return {
                "message": "处理出错，请重试",
                "error": str(e),
                "route": route.__dict__
            }
    
    def _handle_direct_route(self, user_text: str, route: Route) -> Dict[str, Any]:
        """处理直接路由的工具调用"""
        
        # 根据工具类型返回不同的模拟响应
        tool_responses = {
            "seaking_tool": {
                "message": "🎯 海王模拟模式启动！准备好接受挑战了吗？",
                "mode": "seaking",
                "next_action": "开始对战"
            },
            "help_tool": {
                "message": "🆘 高风险情况！立即寻求帮助：110/当地妇联/反家暴热线",
                "mode": "help",
                "high_risk": route.reason == "high_risk",
                "channels": "110/当地妇联/反家暴热线" if route.reason == "high_risk" else None
            },
            "roast_tool": {
                "message": "💥 哎呦，这不得好好吐槽一下？姐来给你分析分析这个情况...",
                "mode": "roast",
                "target": "other" if "other" in route.reason else "self"
            },
            "talk_tool": {
                "message": "💬 来来来，姐陪你聊聊这个话题~",
                "mode": "talk",
                "topic": "daily"
            }
        }
        
        response = tool_responses.get(route.tool, {"message": "处理中..."})
        response.update({
            "tool": route.tool,
            "route": route.__dict__,
            "pipeline": "direct"
        })
        
        return response
    
    def _handle_severity_route(self, user_text: str, route: Route) -> Dict[str, Any]:
        """处理需要恋爱脑程度分析的情况"""
        return {
            "message": "🔍 让姐先分析一下你的恋爱脑程度...",
            "tool": "severity_analyzer",
            "route": route.__dict__,
            "pipeline": "severity_analysis",
            "next_step": "二次路由到help_tool或roast_tool"
        }
    
    def _handle_agent_fallback(self, user_text: str, route: Route) -> Dict[str, Any]:
        """兜底：交给原有Agent处理"""
        if self.original_agent:
            # 这里应该调用原Agent，暂时模拟
            result = {
                "message": "交给原Agent处理: " + user_text,
                "source": "original_agent"
            }
        else:
            result = {
                "message": "No route matched, please refine input.",
                "source": "fallback"
            }
        
        result.update({
            "tool": "agent_fallback",
            "route": route.__dict__,
            "pipeline": "fallback"
        })
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        if self.stats["total"] > 0:
            routed_rate = self.stats["routed"] / self.stats["total"] * 100
            fallback_rate = self.stats["fallback"] / self.stats["total"] * 100
        else:
            routed_rate = fallback_rate = 0
        
        return {
            **self.stats,
            "routed_rate": f"{routed_rate:.1f}%",
            "fallback_rate": f"{fallback_rate:.1f}%"
        }

def test_pipeline():
    """测试管道功能"""
    pipeline = EnhancedPipeline()
    
    test_cases = [
        "给我一套海王话术练习",
        "他威胁要打我",
        "今天天气真好呢",
        "我男朋友总是冷暴力，该怎么办？",
        "朋友的男朋友出轨了，气死我了"
    ]
    
    print("🔧 测试增强管道")
    print("=" * 50)
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"测试 {i}: {user_input}")
        result = pipeline.handle_user_input(user_input, debug=False)
        print(f"回复: {result.get('message', 'No message')}")
        print(f"工具: {result.get('tool', 'No tool')}")
        print(f"管道: {result.get('pipeline', 'Unknown')}")
        print()
    
    # 显示统计
    stats = pipeline.get_stats()
    print(f"📊 路由统计: {stats}")

if __name__ == "__main__":
    test_pipeline()
