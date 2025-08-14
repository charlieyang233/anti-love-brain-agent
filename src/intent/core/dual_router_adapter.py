#!/usr/bin/env python3
"""
双层路由集成适配器 - 将双层路由集成到现有系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.intent.core.dual_layer_router import DualLayerRouter, DualRoutingResult
from src.intent.legacy.basic_router import IntentResult
from typing import Dict, List, Optional, Any

class DualRouterAdapter:
    """双层路由适配器 - 桥接新旧系统"""
    
    def __init__(self):
        self.dual_router = DualLayerRouter()
        self.performance_stats = {
            "total_requests": 0,
            "shortcut_hits": 0,
            "reference_hits": 0, 
            "fallback_hits": 0,
            "total_processing_time": 0.0
        }
    
    def route(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """主路由接口 - 返回兼容的结果格式"""
        # 使用双层路由
        dual_result = self.dual_router.route(user_input, context)
        
        # 更新统计
        self._update_stats(dual_result)
        
        # 转换为兼容格式
        return self._convert_to_legacy_format(dual_result, user_input)
    
    def _update_stats(self, result: DualRoutingResult):
        """更新性能统计"""
        self.performance_stats["total_requests"] += 1
        self.performance_stats["total_processing_time"] += result.processing_time_ms
        
        if result.routing_type == "shortcut":
            self.performance_stats["shortcut_hits"] += 1
        elif result.routing_type == "reference":
            self.performance_stats["reference_hits"] += 1
        else:
            self.performance_stats["fallback_hits"] += 1
    
    def _convert_to_legacy_format(self, dual_result: DualRoutingResult, user_input: str) -> Dict[str, Any]:
        """转换为兼容现有系统的格式"""
        
        if dual_result.routing_type == "shortcut":
            return self._handle_shortcut_result(dual_result, user_input)
        elif dual_result.routing_type == "reference":
            return self._handle_reference_result(dual_result, user_input)
        else:
            return self._handle_fallback_result(dual_result, user_input)
    
    def _handle_shortcut_result(self, result: DualRoutingResult, user_input: str) -> Dict[str, Any]:
        """处理短路结果"""
        shortcut = result.shortcut_result
        
        # 确定路由路径
        if "seaking_tool" in shortcut.tools:
            routing_path = "direct"
            success = True
        elif "severity_analyzer" in shortcut.tools:
            routing_path = "high_risk_direct"
            success = True
        elif "roast_tool" in shortcut.tools:
            routing_path = "other_romance_direct"
            success = True
        else:
            routing_path = "direct"
            success = True
        
        return {
            "routing_path": routing_path,
            "tools_called": shortcut.tools,
            "success": success,
            "confidence": shortcut.confidence,
            "user_input": user_input,
            "performance_metrics": {
                "processing_time_ms": result.processing_time_ms,
                "token_saved": True,
                "routing_type": "shortcut",
                "rule_name": shortcut.rule_name
            },
            "debug_info": {
                "dual_routing": True,
                "rule_triggered": shortcut.rule_name,
                "bypass_agent": shortcut.bypass_agent
            }
        }
    
    def _handle_reference_result(self, result: DualRoutingResult, user_input: str) -> Dict[str, Any]:
        """处理参考信号结果"""
        reference = result.reference_signal
        
        # 生成Agent参考信号
        agent_context = {
            "enhanced_routing_signal": {
                "risk_level": reference.risk_level,
                "romance_context": reference.romance_context,
                "help_intent": reference.help_intent,
                "emotion_intensity": reference.emotion_intensity,
                "matched_keywords": reference.matched_keywords,
                "suggested_tools": reference.suggested_tools,
                "confidence_factors": reference.confidence_factors
            }
        }
        
        return {
            "routing_path": "agent_with_reference",
            "tools_called": ["original_agent"],
            "success": True,
            "confidence": result.confidence,
            "user_input": user_input,
            "agent_context": agent_context,
            "performance_metrics": {
                "processing_time_ms": result.processing_time_ms,
                "token_saved": False,
                "routing_type": "reference",
                "signals_detected": list(reference.matched_keywords.keys())
            },
            "debug_info": {
                "dual_routing": True,
                "reference_signals": reference.matched_keywords,
                "suggested_tools": reference.suggested_tools
            }
        }
    
    def _handle_fallback_result(self, result: DualRoutingResult, user_input: str) -> Dict[str, Any]:
        """处理兜底结果"""
        return {
            "routing_path": "agent_fallback",
            "tools_called": ["original_agent"],
            "success": True,
            "confidence": result.confidence,
            "user_input": user_input,
            "performance_metrics": {
                "processing_time_ms": result.processing_time_ms,
                "token_saved": False,
                "routing_type": "fallback",
                "reason": "no_clear_pattern"
            },
            "debug_info": {
                "dual_routing": True,
                "fallback_reason": "no_clear_pattern_detected"
            }
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        total = self.performance_stats["total_requests"]
        if total == 0:
            return self.performance_stats
        
        avg_time = self.performance_stats["total_processing_time"] / total
        shortcut_rate = self.performance_stats["shortcut_hits"] / total * 100
        reference_rate = self.performance_stats["reference_hits"] / total * 100
        fallback_rate = self.performance_stats["fallback_hits"] / total * 100
        
        return {
            **self.performance_stats,
            "average_processing_time_ms": avg_time,
            "shortcut_rate_percent": shortcut_rate,
            "reference_rate_percent": reference_rate,
            "fallback_rate_percent": fallback_rate,
            "token_savings_estimate": shortcut_rate  # 短路比例约等于Token节省率
        }
    
    def explain_routing(self, user_input: str) -> Dict[str, Any]:
        """解释路由决策"""
        dual_result = self.dual_router.route(user_input)
        explanation = self.dual_router.explain_routing(dual_result)
        
        # 添加适配器特有的信息
        explanation["adapter_info"] = {
            "legacy_compatible": True,
            "performance_mode": "dual_layer",
            "integration_status": "active"
        }
        
        return explanation

def test_adapter_integration():
    """测试适配器集成"""
    adapter = DualRouterAdapter()
    
    test_cases = [
        "给我一套海王话术练习",
        "他威胁要打我", 
        "男朋友总是冷暴力对我",
        "我被男朋友控制了",
        "今天天气真不错",
        "我今天心情不好"
    ]
    
    print("🔗 双层路由适配器测试")
    print("=" * 50)
    
    for user_input in test_cases:
        result = adapter.route(user_input)
        
        print(f"\n输入: {user_input}")
        print(f"路由路径: {result['routing_path']}")
        print(f"调用工具: {result['tools_called']}")
        print(f"Token节省: {'✅' if result['performance_metrics']['token_saved'] else '❌'}")
        print(f"耗时: {result['performance_metrics']['processing_time_ms']:.1f}ms")
        
        if "agent_context" in result:
            print(f"Agent参考: {list(result['agent_context']['enhanced_routing_signal']['matched_keywords'].keys())}")
    
    # 显示统计
    stats = adapter.get_performance_stats()
    print(f"\n📊 性能统计:")
    print(f"总请求数: {stats['total_requests']}")
    print(f"短路比例: {stats['shortcut_rate_percent']:.1f}%")
    print(f"参考比例: {stats['reference_rate_percent']:.1f}%")
    print(f"兜底比例: {stats['fallback_rate_percent']:.1f}%")
    print(f"平均耗时: {stats['average_processing_time_ms']:.1f}ms")
    print(f"Token节省估算: {stats['token_savings_estimate']:.1f}%")

if __name__ == "__main__":
    test_adapter_integration()
