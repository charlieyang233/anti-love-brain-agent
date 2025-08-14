#!/usr/bin/env python3
"""
Agent适配器 - 将意图路由集成到现有的LangChain Agent
"""

import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.intent.enhanced_pipeline import EnhancedPipeline
from src.agent import build_agent


class IntentAwareAgent:
    """带意图路由功能的增强Agent"""
    
    def __init__(self):
        """初始化增强Agent"""
        # 初始化原有Agent
        try:
            self.original_agent = build_agent()
            print("✅ 原有Agent初始化成功")
        except Exception as e:
            print(f"⚠️ 原有Agent初始化失败: {e}")
            self.original_agent = None
        
        # 初始化意图路由管道
        self.pipeline = EnhancedPipeline(original_agent=self.original_agent)
        
        # 集成配置
        self.config = {
            "enable_intent_routing": True,
            "fallback_to_agent": True,
            "debug_mode": False
        }
        
        print("🚀 意图感知Agent初始化完成")
    
    def process_input(self, user_input: str, **kwargs) -> Dict[str, Any]:
        """
        处理用户输入的主入口
        Args:
            user_input: 用户输入文本
            **kwargs: 其他参数
        Returns:
            处理结果
        """
        # 如果禁用意图路由，直接使用原Agent
        if not self.config["enable_intent_routing"]:
            return self._fallback_to_original_agent(user_input)
        
        try:
            # 使用意图路由管道处理
            result = self.pipeline.handle_user_input(
                user_input, 
                debug=self.config["debug_mode"]
            )
            
            # 如果路由到severity_analyzer，需要调用原Agent进行分析
            if result.get("tool") == "severity_analyzer":
                return self._handle_severity_analysis(user_input, result)
            
            # 如果需要fallback到原Agent
            elif result.get("pipeline") == "fallback" and self.config["fallback_to_agent"]:
                return self._fallback_to_original_agent(user_input)
            
            return result
            
        except Exception as e:
            print(f"[Error] Intent routing failed: {e}")
            # 出错时fallback到原Agent
            if self.config["fallback_to_agent"]:
                return self._fallback_to_original_agent(user_input)
            else:
                return {"error": str(e), "message": "处理失败，请重试"}
    
    def _handle_severity_analysis(self, user_input: str, route_result: Dict[str, Any]) -> Dict[str, Any]:
        """处理需要恋爱脑程度分析的情况"""
        if not self.original_agent:
            return {
                "message": "恋爱脑分析功能暂不可用",
                "fallback": True
            }
        
        try:
            # 调用原Agent进行恋爱脑程度分析
            # 这里应该调用severity tool，暂时模拟
            severity_result = {
                "severity_score": 7.5,  # 模拟分数
                "analysis": "检测到中等程度恋爱脑倾向",
                "recommendation": "建议理性分析，寻求专业建议"
            }
            
            # 根据严重程度决定后续路由
            if severity_result["severity_score"] >= 8.0:
                # 高风险，路由到help_tool
                return {
                    "message": "🚨 检测到高风险恋爱脑状态！建议立即寻求专业帮助",
                    "tool": "help_tool",
                    "severity": severity_result,
                    "pipeline": "severity_to_help"
                }
            else:
                # 中低风险，路由到roast_tool
                return {
                    "message": "💭 检测到恋爱脑倾向，姐来帮你理性分析一下...",
                    "tool": "roast_tool", 
                    "severity": severity_result,
                    "pipeline": "severity_to_roast"
                }
                
        except Exception as e:
            print(f"[Error] Severity analysis failed: {e}")
            return route_result  # 返回原路由结果
    
    def _fallback_to_original_agent(self, user_input: str) -> Dict[str, Any]:
        """Fallback到原有Agent处理"""
        if not self.original_agent:
            return {
                "message": "原有Agent不可用，请检查配置",
                "error": "agent_unavailable"
            }
        
        try:
            # 调用原有Agent处理
            result = self.original_agent.invoke({"input": user_input})
            
            return {
                "message": result.get("output", "处理完成"),
                "source": "original_agent",
                "pipeline": "fallback",
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            return {
                "message": f"原Agent处理失败: {str(e)}",
                "error": str(e),
                "source": "original_agent_error"
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        pipeline_stats = self.pipeline.get_stats()
        
        return {
            "intent_routing": pipeline_stats,
            "config": self.config,
            "agent_status": "available" if self.original_agent else "unavailable"
        }
    
    def configure(self, **kwargs):
        """配置Agent行为"""
        self.config.update(kwargs)
        print(f"配置已更新: {self.config}")


def test_agent_adapter():
    """测试Agent适配器"""
    print("🧪 测试意图感知Agent")
    print("=" * 60)
    
    # 初始化
    agent = IntentAwareAgent()
    agent.configure(debug_mode=True)  # 开启调试模式
    
    test_cases = [
        "给我一套海王话术练习",
        "他总是威胁我，我该怎么办？",
        "今天公司项目又延期了，烦死了",
        "我感觉我男朋友可能不爱我了，怎么办？",
        "朋友被渣男骗了，我要怎么安慰她？"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {user_input}")
        print("-" * 40)
        
        result = agent.process_input(user_input)
        
        print(f"回复: {result.get('message', 'No message')}")
        print(f"工具: {result.get('tool', 'Unknown')}")
        print(f"管道: {result.get('pipeline', 'Unknown')}")
        
        if result.get('severity'):
            severity = result['severity']
            print(f"恋爱脑分析: {severity.get('analysis')} (分数: {severity.get('severity_score')})")
    
    # 显示统计
    print("\n📊 性能统计:")
    stats = agent.get_stats()
    print(f"意图路由: {stats['intent_routing']}")
    print(f"Agent状态: {stats['agent_status']}")


if __name__ == "__main__":
    test_agent_adapter()
