#!/usr/bin/env python3
"""
增强Agent参数传递测试
展示向Agent传递的结构化意图分析参数
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.intent.core.dual_router_memory import DualRouterMemoryIntegration
from src.intent.core.enhanced_agent_params import EnhancedAgentParameterBuilder
import json

def create_test_memory_manager():
    """创建测试用的内存管理器"""
    class MockMemoryManager:
        def __init__(self):
            self.interactions = [
                {"user_input": "我最近工作压力很大", "ai_response": "理解你的压力"},
                {"user_input": "总是加班到很晚", "ai_response": "注意身体健康"}
            ]
            
        def add_interaction(self, **kwargs):
            self.interactions.append(kwargs)
            
        def get_recent_context(self, limit=3):
            return self.interactions[-limit:]
            
        def add_routing_metadata(self, metadata):
            pass
            
        def get_memory_stats(self):
            return {"total_interactions": len(self.interactions)}
    
    return MockMemoryManager()

def test_enhanced_agent_parameters():
    """测试增强的Agent参数传递"""
    print("🚀 增强Agent参数传递测试")
    print("=" * 80)
    
    memory_manager = create_test_memory_manager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    # 测试不同场景的Agent参数
    test_cases = [
        {
            "input": "我男朋友总是控制我，怎么办？",
            "scenario": "中等风险的自身恋爱问题",
            "expected_route": "reference"
        },
        {
            "input": "感情问题真的很复杂啊",
            "scenario": "模糊的情感表达",
            "expected_route": "fallback"
        },
        {
            "input": "朋友的男朋友经常对她大喊大叫",
            "scenario": "他人恋爱问题",
            "expected_route": "reference或shortcut"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*20} 测试案例 {i} {'='*20}")
        print(f"📝 输入: {case['input']}")
        print(f"🎯 场景: {case['scenario']}")
        print(f"🔮 预期路由: {case['expected_route']}")
        
        # 获取路由结果
        dual_result = integration.dual_router.route(case['input'])
        print(f"✅ 实际路由: {dual_result.routing_type}")
        
        # 构建增强参数
        enhanced_params = integration.param_builder.build_agent_parameters(
            case['input'], dual_result
        )
        
        print(f"\n📊 传递给Agent的完整参数结构:")
        print("```json")
        print(json.dumps(enhanced_params, indent=2, ensure_ascii=False))
        print("```")
        
        # 重点展示关键信息
        print(f"\n🔍 关键参数摘要:")
        print(f"  🎪 路由路径: {enhanced_params['intent_analysis']['routing_path']}")
        print(f"  🎯 置信度: {enhanced_params['intent_analysis']['confidence']}")
        print(f"  ⚡ 处理时间: {enhanced_params['intent_analysis']['processing_time_ms']:.2f}ms")
        print(f"  🏷️ 触发规则: {enhanced_params['intent_analysis']['rule_triggered']}")
        print(f"  🔄 上下文敏感: {enhanced_params['intent_analysis']['context_aware']}")
        
        print(f"\n  📝 内容分析:")
        content = enhanced_params['content_analysis']
        print(f"    匹配关键词: {list(content['matched_keywords'].keys())}")
        print(f"    覆盖率: {content['keyword_coverage']:.1%}")
        print(f"    复杂度: {content['text_complexity']}")
        
        print(f"\n  🚨 上下文信号:")
        signals = enhanced_params['context_signals']
        print(f"    风险等级: {signals['risk_level']}")
        print(f"    恋爱上下文: {signals['romance_context']['subject']}")
        print(f"    求助意图: {signals['help_intent']}")
        print(f"    情绪强度: {signals['emotion_intensity']:.2f}")
        
        print(f"\n  🎯 Agent指导:")
        guidance = enhanced_params['agent_guidance']
        print(f"    建议工具: {guidance['suggested_tools']}")
        print(f"    推理说明: {guidance['reasoning']}")
        print(f"    优先方面: {guidance['priority_aspects']}")
        print(f"    避免方面: {guidance['avoid_aspects']}")
        print(f"    回应语调: {guidance['response_tone']}")
        print(f"    安全级别: {guidance['safety_level']}")
        
        print(f"\n  🧠 记忆上下文:")
        memory = enhanced_params['memory_context']
        print(f"    最近话题: {memory['recent_topics']}")
        print(f"    情绪状态: {memory['user_emotional_state']}")
        print(f"    对话流程: {memory['conversation_flow']}")
        
        print(f"\n  ⚙️ 技术元数据:")
        meta = enhanced_params['technical_meta']
        print(f"    路由器版本: {meta['router_version']}")
        print(f"    兜底原因: {meta['fallback_reason']}")
        print(f"    路由效率: {meta['performance_stats']['routing_efficiency']:.1%}")
        print(f"    优化级别: {meta['performance_stats']['optimization_level']}")

def demonstrate_parameter_usage():
    """演示参数使用方式"""
    print(f"\n\n{'='*80}")
    print("🎭 Agent如何使用这些参数")
    print("=" * 80)
    
    print("""
📋 **参数使用指南**:

1️⃣ **意图理解** (intent_analysis):
   - routing_path: 判断处理复杂度
   - confidence: 决定回应的确定性
   - rule_triggered: 了解匹配的具体规则

2️⃣ **内容解析** (content_analysis):
   - matched_keywords: 理解用户关注点
   - text_complexity: 调整回应详细程度
   - keyword_coverage: 评估理解准确度

3️⃣ **情境感知** (context_signals):
   - risk_level: 决定安全防护措施
   - romance_context: 定制恋爱相关回应
   - emotion_intensity: 调整情感支持力度

4️⃣ **策略指导** (agent_guidance):
   - suggested_tools: 参考工具建议
   - reasoning: 理解路由逻辑
   - priority_aspects: 关注重点方面
   - avoid_aspects: 避免敏感话题
   - response_tone: 选择合适语调

5️⃣ **历史连贯** (memory_context):
   - recent_topics: 保持话题连续性
   - user_emotional_state: 理解情绪背景
   - conversation_flow: 适应对话阶段

6️⃣ **性能优化** (technical_meta):
   - routing_efficiency: 了解处理效率
   - fallback_reason: 理解兜底原因
   - debug_info: 调试和优化参考
""")

    print("""
🔧 **Agent实现示例**:

```python
def process_with_enhanced_params(user_input, enhanced_params):
    # 1. 根据风险等级调整安全措施
    risk = enhanced_params['context_signals']['risk_level']
    if risk in ['medium', 'high']:
        enable_safety_protocols()
    
    # 2. 根据语调建议调整回应风格
    tone = enhanced_params['agent_guidance']['response_tone']
    set_response_tone(tone)
    
    # 3. 根据优先方面调整回应重点
    priorities = enhanced_params['agent_guidance']['priority_aspects']
    focus_on_aspects(priorities)
    
    # 4. 考虑历史上下文保持连贯性
    recent_topics = enhanced_params['memory_context']['recent_topics']
    maintain_context_continuity(recent_topics)
    
    # 5. 根据置信度决定回应确定性
    confidence = enhanced_params['intent_analysis']['confidence']
    adjust_response_certainty(confidence)
    
    return generate_response(user_input, enhanced_params)
```
""")

def main():
    """主测试函数"""
    test_enhanced_agent_parameters()
    demonstrate_parameter_usage()
    
    print(f"\n\n🎉 **总结**:")
    print("✅ 增强参数传递系统已完成，为Agent提供:")
    print("   📊 结构化的意图分析结果")
    print("   🎯 详细的内容和上下文信息")
    print("   🎭 具体的处理策略指导")
    print("   🧠 丰富的历史记忆上下文")
    print("   ⚙️ 完整的技术元数据")
    print("\n💡 这些参数让Agent能够:")
    print("   🔍 更准确地理解用户意图")
    print("   🎨 提供更个性化的回应")
    print("   🛡️ 更好地处理风险情况")
    print("   🔄 保持更好的对话连贯性")

if __name__ == "__main__":
    main()
