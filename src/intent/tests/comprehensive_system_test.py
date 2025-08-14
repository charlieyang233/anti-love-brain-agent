#!/usr/bin/env python3
"""
综合系统测试 - 验证优化后的完整路由+记忆系统
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.intent.core.dual_router_memory import DualRouterMemoryIntegration
from src.memory_manager import SmartMemoryManager

def create_test_memory_manager():
    """创建测试用的内存管理器"""
    class MockMemoryManager:
        def __init__(self):
            self.interactions = []
            self.routing_metadata = []
            
        def add_interaction(self, user_input, ai_response, love_brain_level=None, risk_signals=None):
            self.interactions.append({
                'user_input': user_input,
                'ai_response': ai_response,
                'love_brain_level': love_brain_level,
                'risk_signals': risk_signals
            })
            
        def get_recent_context(self, limit=3):
            return self.interactions[-limit:] if self.interactions else []
            
        def add_routing_metadata(self, metadata):
            self.routing_metadata.append(metadata)
            
        def get_memory_stats(self):
            return {
                "total_interactions": len(self.interactions),
                "routing_metadata_count": len(self.routing_metadata)
            }
    
    return MockMemoryManager()

def test_context_aware_routing():
    """测试上下文敏感路由"""
    print("=== 上下文敏感路由测试 ===")
    
    memory_manager = create_test_memory_manager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    # 1. 第一轮对话：建立上下文
    response1 = integration.process_with_memory_update("我最近心情不好")
    print(f"第1轮: {response1['response'][:100]}...")
    
    # 2. 第二轮对话：海王练习（应该考虑之前的心情不好）
    response2 = integration.process_with_memory_update("教我一套撩妹话术")
    print(f"第2轮: {response2['response'][:100]}...")
    
    # 验证是否考虑了上下文
    assert "上下文" in response2['response'] or "最近讨论" in response2['response']
    print("✅ 上下文连贯性验证通过")

def test_tool_combinations():
    """测试工具组合调用"""
    print("\n=== 工具组合调用测试 ===")
    
    memory_manager = create_test_memory_manager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    # 1. 高风险组合：severity + search + help
    response1 = integration.process_with_memory_update("他威胁要伤害我")
    print(f"高风险组合: {response1['response'][:150]}...")
    
    # 验证包含了所有三个工具
    assert "severity_analyzer" in response1['response']
    assert "search_tool" in response1['response'] 
    assert "help_tool" in response1['response']
    
    # 2. 自己恋爱行为组合：severity + roast
    response2 = integration.process_with_memory_update("我男朋友出轨了")
    print(f"恋爱行为组合: {response2['response'][:150]}...")
    
    # 验证包含了两个工具
    assert "severity_analyzer" in response2['response']
    assert "roast_tool" in response2['response']
    
    print("✅ 工具组合验证通过")

def test_memory_consistency():
    """测试记忆一致性"""
    print("\n=== 记忆一致性测试 ===")
    
    memory_manager = create_test_memory_manager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    test_cases = [
        "教我海王话术",           # 短路（上下文敏感）
        "他威胁我",              # 短路（工具组合）
        "朋友的男朋友很渣",       # 短路（简单）
        "我觉得感情好复杂",       # 参考信号
        "今天天气真好",          # 日常聊天
    ]
    
    for i, case in enumerate(test_cases, 1):
        response = integration.process_with_memory_update(case)
        print(f"第{i}轮: '{case}' -> {response['routing_info']['path']}")
        
        # 验证每次都有记忆更新
        assert len(memory_manager.interactions) == i
        assert memory_manager.interactions[-1]['user_input'] == case
    
    print(f"✅ 记忆一致性验证通过，共记录{len(memory_manager.interactions)}次交互")

def test_routing_explanation():
    """测试路由解释"""
    print("\n=== 路由解释测试 ===")
    
    memory_manager = create_test_memory_manager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    test_cases = [
        ("给我一套海王话术", "shortcut_with_context", "上下文"),
        ("他要自杀", "shortcut_with_context", "组合"),
        ("朋友的男朋友很渣", "shortcut", "直接"),  # 明确的romance_other + negative
        ("我男朋友总是控制我", "reference", "参考"),  # 包含medium_risk关键词
    ]
    
    for case, expected_type, description in test_cases:
        response = integration.process_with_memory_update(case)
        
        print(f"'{case}':")
        print(f"  期望类型: {expected_type}")
        print(f"  实际类型: {response['routing_info']['path']}")
        print(f"  特征: {description}")
        print(f"  响应: {response['response'][:50]}...")
        
        # 类型验证
        assert response['routing_info']['path'] == expected_type, f"期望{expected_type}，实际{response['routing_info']['path']}"
        
        print()
    
    print("✅ 路由解释验证通过")

def test_performance_summary():
    """测试性能总结"""
    print("\n=== 性能总结测试 ===")
    
    memory_manager = create_test_memory_manager()
    integration = DualRouterMemoryIntegration(memory_manager)
    
    # 模拟100次路由
    test_inputs = [
        "教我撩妹话术",      # shortcut_with_context
        "他威胁我",          # shortcut_with_context (组合)
        "朋友男朋友渣",      # shortcut
        "感情好复杂",        # reference
        "今天天气好",        # shortcut
    ] * 20
    
    routing_types = []
    processing_times = []
    
    for input_text in test_inputs:
        response = integration.process_with_memory_update(input_text)
        routing_types.append(response['routing_info']['path'])
        processing_times.append(response['performance'].get('processing_time_ms', 0))
    
    # 统计
    from collections import Counter
    type_counts = Counter(routing_types)
    avg_time = sum(processing_times) / len(processing_times)
    
    print(f"总路由次数: {len(routing_types)}")
    print(f"路由类型分布: {dict(type_counts)}")
    print(f"平均处理时间: {avg_time:.2f}ms")
    
    # 计算优化效果
    shortcut_ratio = (type_counts['shortcut'] + type_counts['shortcut_with_context']) / len(routing_types)
    print(f"短路成功率: {shortcut_ratio:.1%}")
    
    assert shortcut_ratio >= 0.6  # 至少60%短路成功率
    print("✅ 性能表现符合预期")

def main():
    """主测试函数"""
    print("🚀 开始综合系统测试...")
    print("📝 测试内容:")
    print("  1. 上下文敏感路由")
    print("  2. 工具组合调用") 
    print("  3. 记忆一致性")
    print("  4. 路由解释")
    print("  5. 性能总结")
    print()
    
    try:
        test_context_aware_routing()
        test_tool_combinations()
        test_memory_consistency()
        test_routing_explanation()
        test_performance_summary()
        
        print("\n🎉 综合测试全部通过！")
        print("\n📊 优化成果:")
        print("✅ 解决了多轮对话连贯性问题")
        print("✅ 正确实现severity_analyzer组合调用")
        print("✅ 简化规则，避免过度复杂")
        print("✅ 保持100%记忆更新保证")
        print("✅ 提供完整的路由解释和性能监控")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
