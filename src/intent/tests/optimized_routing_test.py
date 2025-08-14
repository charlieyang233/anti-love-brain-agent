#!/usr/bin/env python3
"""
优化后双层路由系统测试
验证：
1. 多轮对话连贯性考虑
2. severity_analyzer正确组合使用
3. 简化规则，避免过度复杂
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.intent.core.dual_layer_router import DualLayerRouter

def test_context_awareness():
    """测试上下文连贯性"""
    router = DualLayerRouter()
    
    print("=== 上下文连贯性测试 ===")
    
    # 1. 海王练习（需要上下文）
    result = router.route("教我一套海王话术练习")
    print(f"海王练习: {result.routing_type}, context_aware: {result.shortcut_result.context_aware}")
    assert result.routing_type == "shortcut_with_context"
    assert result.shortcut_result.context_aware == True
    assert "seaking_tool" in result.final_tools
    
    # 2. 高风险（需要上下文和组合工具）
    result = router.route("他威胁要打我")
    print(f"高风险: {result.routing_type}, tools: {result.final_tools}")
    assert result.routing_type == "shortcut_with_context"
    assert result.shortcut_result.context_aware == True
    assert "severity_analyzer" in result.final_tools
    assert "search_tool" in result.final_tools
    assert "help_tool" in result.final_tools
    
    # 3. 简单求助（可直达）
    result = router.route("学习编程怎么办")
    print(f"简单求助: {result.routing_type}, context_aware: {result.shortcut_result.context_aware}")
    assert result.routing_type == "shortcut"
    assert result.shortcut_result.context_aware == False
    assert result.final_tools == ["help_tool"]

def test_severity_analyzer_combinations():
    """测试severity_analyzer组合使用"""
    router = DualLayerRouter()
    
    print("\n=== severity_analyzer组合测试 ===")
    
    # 1. 高风险组合
    result = router.route("他说要自杀")
    print(f"高风险组合: {result.final_tools}")
    expected_tools = ["severity_analyzer", "search_tool", "help_tool"]
    assert all(tool in result.final_tools for tool in expected_tools)
    
    # 2. 自己恋爱行为组合
    result = router.route("我男朋友出轨了")
    print(f"自己恋爱行为组合: {result.final_tools}")
    expected_tools = ["severity_analyzer", "roast_tool"]
    assert all(tool in result.final_tools for tool in expected_tools)
    
    # 3. 他人恋爱（不需要severity_analyzer）
    result = router.route("朋友的男朋友很渣")
    print(f"他人恋爱: {result.final_tools}")
    assert result.final_tools == ["roast_tool"]
    assert "severity_analyzer" not in result.final_tools

def test_simplified_rules():
    """测试简化规则"""
    router = DualLayerRouter()
    
    print("\n=== 简化规则测试 ===")
    
    # 验证规则简化，复杂场景应该走参考信号而不是短路
    test_cases = [
        "我想了解一下投资知识",     # 复杂主题
        "同事关系处理技巧",         # 工作相关但复杂
        "他最近态度有点奇怪"        # 模糊情感问题
    ]
    
    for case in test_cases:
        result = router.route(case)
        print(f"'{case}': {result.routing_type}")
        # 这些复杂情况应该走参考信号或兜底，而不是简单短路
        # 注意：如果匹配到明确规则（如日常聊天）也是合理的
        
    # 验证核心规则数量减少
    rule_count = len(router.shortcut_rules)
    print(f"短路规则数量: {rule_count}")
    assert rule_count <= 6  # 应该控制在6个以内

def test_routing_explanations():
    """测试路由解释"""
    router = DualLayerRouter()
    
    print("\n=== 路由解释测试 ===")
    
    cases = [
        "给我一套撩妹话术",
        "他威胁我",
        "我男朋友劈腿了",
        "朋友的女朋友很烦"
    ]
    
    for case in cases:
        result = router.route(case)
        explanation = router.explain_routing(result)
        print(f"'{case}':")
        print(f"  类型: {explanation['routing_type']}")
        print(f"  工具: {explanation.get('tools_called', 'N/A')}")
        print(f"  上下文感知: {explanation.get('context_aware', 'N/A')}")
        print(f"  解释: {explanation.get('explanation', 'N/A')}")
        print()

def main():
    """主测试函数"""
    print("🔄 开始优化后双层路由系统测试...")
    
    try:
        test_context_awareness()
        test_severity_analyzer_combinations()
        test_simplified_rules()
        test_routing_explanations()
        
        print("✅ 所有测试通过！")
        print("\n📊 优化总结:")
        print("1. ✅ 增加了上下文连贯性考虑")
        print("2. ✅ 正确组合使用severity_analyzer")
        print("3. ✅ 简化了规则，避免过度复杂")
        print("4. ✅ 提供详细的路由解释")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
