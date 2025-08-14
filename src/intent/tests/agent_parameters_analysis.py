#!/usr/bin/env python3
"""
Agent参数传递分析和优化
分析当前系统如何向Agent传递意图识别信息
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.intent.core.dual_layer_router import DualLayerRouter
from src.intent.core.dual_router_memory import DualRouterMemoryIntegration

def analyze_agent_parameters():
    """分析Agent参数传递"""
    print("🔍 Agent参数传递分析")
    print("=" * 60)
    
    # 创建模拟的内存管理器
    class MockMemoryManager:
        def __init__(self):
            self.interactions = []
            
        def add_interaction(self, **kwargs):
            self.interactions.append(kwargs)
            
        def get_recent_context(self, limit=3):
            return [
                {"user_input": "我最近压力很大"},
                {"user_input": "工作不顺心"}
            ][-limit:]
            
        def add_routing_metadata(self, metadata):
            pass
            
        def get_memory_stats(self):
            return {"total_interactions": len(self.interactions)}
    
    memory_manager = MockMemoryManager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    # 测试不同的Agent调用场景
    test_cases = [
        ("我男朋友总是控制我", "reference"),  # 参考信号
        ("感情问题很复杂", "fallback"),      # 兜底
        ("这个情况很特殊", "fallback"),      # 兜底
    ]
    
    print("\n📋 当前Agent参数传递情况:")
    
    for i, (case, expected_type) in enumerate(test_cases, 1):
        print(f"\n{i}. 测试用例: '{case}'")
        print(f"   期望路由: {expected_type}")
        
        # 获取路由结果
        dual_result = integration.dual_router.route(case)
        
        print(f"   实际路由: {dual_result.routing_type}")
        print(f"   工具建议: {dual_result.final_tools}")
        print(f"   处理时间: {dual_result.processing_time_ms:.2f}ms")
        
        if dual_result.routing_type == "reference":
            print(f"   参考信号:")
            signal = dual_result.reference_signal
            print(f"     - 风险等级: {signal.risk_level}")
            print(f"     - 恋爱上下文: {signal.romance_context}")
            print(f"     - 求助意图: {signal.help_intent}")
            print(f"     - 情绪强度: {signal.emotion_intensity:.2f}")
            print(f"     - 匹配关键词: {list(signal.matched_keywords.keys())}")
            print(f"     - 置信度因子: {signal.confidence_factors}")
            print(f"     - 建议工具: {signal.suggested_tools}")
            
        elif dual_result.routing_type == "fallback":
            print(f"   兜底信息: 无明确模式，完全交给Agent")
            
        print(f"   调试信息: {dual_result.debug_info}")

def design_enhanced_agent_parameters():
    """设计增强的Agent参数传递"""
    print("\n\n🚀 增强Agent参数传递设计")
    print("=" * 60)
    
    print("\n📦 当前参数结构问题:")
    print("1. reference路由：只传递简单的confidence_factors字符串")
    print("2. fallback路由：几乎没有传递任何意图信息")
    print("3. 缺少结构化的意图分析结果")
    print("4. 没有传递关键词匹配详情")
    print("5. 缺少推理路径和置信度信息")
    
    print("\n✨ 建议的增强参数结构:")
    
    enhanced_params = {
        "intent_analysis": {
            "routing_path": "reference",  # shortcut/shortcut_with_context/reference/fallback
            "confidence": 0.7,
            "processing_time_ms": 0.8,
            "rule_triggered": None,  # 如果是shortcut，显示触发的规则
        },
        
        "content_analysis": {
            "matched_keywords": {
                "romance_self": ["男朋友", "我们"],
                "medium_risk": ["控制"],
                "negative_emotions": []
            },
            "keyword_coverage": 0.6,  # 关键词覆盖率
            "text_complexity": "medium",  # simple/medium/complex
        },
        
        "context_signals": {
            "risk_level": "medium",  # none/low/medium/high
            "romance_context": {
                "subject": "self",  # self/other/unknown
                "behaviors": ["控制"],
                "emotions": []
            },
            "help_intent": False,
            "emotion_intensity": 0.3
        },
        
        "agent_guidance": {
            "suggested_tools": ["talk_tool", "help_tool"],
            "reasoning": "检测到中等风险的自身恋爱问题，建议谨慎处理",
            "priority_aspects": ["风险评估", "情感支持"],
            "avoid_aspects": ["直接建议分手"]
        },
        
        "memory_context": {
            "recent_topics": ["压力", "工作"],
            "user_emotional_state": "negative",
            "conversation_flow": "seeking_help"
        },
        
        "technical_meta": {
            "router_version": "dual_layer_v2",
            "fallback_reason": None,  # 如果是fallback，说明原因
            "performance_stats": {
                "token_saved": False,
                "routing_efficiency": 0.7
            }
        }
    }
    
    print("```python")
    import json
    print(json.dumps(enhanced_params, indent=2, ensure_ascii=False))
    print("```")
    
    print("\n🎯 增强参数的价值:")
    print("1. Agent可以更好地理解用户意图")
    print("2. 提供具体的处理建议和注意事项") 
    print("3. 包含丰富的上下文信息")
    print("4. 支持个性化响应策略")
    print("5. 便于调试和性能优化")

def main():
    """主函数"""
    analyze_agent_parameters()
    design_enhanced_agent_parameters()
    
    print("\n\n💡 总结:")
    print("当前系统向Agent传递的参数比较简单，主要包括：")
    print("- reference路由：基本的confidence_factors信息")
    print("- fallback路由：几乎无额外信息")
    print("\n建议增强参数传递，提供结构化的意图分析结果，")
    print("帮助Agent做出更精准和个性化的响应。")

if __name__ == "__main__":
    main()
