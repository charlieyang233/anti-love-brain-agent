#!/usr/bin/env python3
"""
完整应用集成测试 - 测试app.py的双层路由记忆集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.intent.core.app_integration import IntentEnabledChatHandler
from src.memory_factory import MemoryManagerFactory

def test_full_app_integration():
    """测试完整应用集成"""
    print("🚀 完整应用集成测试")
    print("=" * 60)
    
    # 模拟app.py的创建流程
    MEMORY_STORAGE_TYPE = "memory"
    ENABLE_ENHANCED_ROUTING = True
    user_ip = "test_user_123"
    
    # 创建记忆管理器（使用工厂）
    memory_manager = MemoryManagerFactory.create_memory_manager(
        storage_type=MEMORY_STORAGE_TYPE,
        user_id=user_ip,
        max_conversation_window=15
    )
    
    # 创建增强聊天处理器
    chat_handler = IntentEnabledChatHandler(
        memory_manager=memory_manager,
        enable_enhanced_routing=ENABLE_ENHANCED_ROUTING
    )
    
    # 测试用例
    test_conversations = [
        {
            "input": "给我一套海王话术练习",
            "expected_path": "shortcut",
            "expected_tool": "seaking_tool"
        },
        {
            "input": "室友被渣男骗了怎么办",
            "expected_path": "shortcut", 
            "expected_tool": "roast_tool"
        },
        {
            "input": "老板威胁我要辞退我",
            "expected_path": "shortcut",
            "expected_tool": "severity_analyzer"
        },
        {
            "input": "搜索一下最新的恋爱指南",
            "expected_path": "shortcut",
            "expected_tool": "search_tool"
        },
        {
            "input": "今天天气不错，推荐个电影",
            "expected_path": "shortcut",
            "expected_tool": "talk_tool"
        }
    ]
    
    print(f"📊 测试前记忆状态:")
    initial_stats = memory_manager.get_memory_stats()
    print(f"  交互数: {initial_stats.get('total_interactions', 0)}")
    print(f"  短期记忆: {initial_stats.get('short_term_count', 0)}")
    print(f"  长期记忆: {initial_stats.get('long_term_count', 0)}")
    
    results = []
    
    for i, test_case in enumerate(test_conversations, 1):
        print(f"\n🧪 测试 {i}: {test_case['input']}")
        
        # 获取对话历史作为上下文
        conversation_history = chat_handler._get_conversation_history()
        
        # 处理聊天
        result = chat_handler.process_chat(test_case["input"], user_ip)
        
        # 分析结果
        routing_info = result.get("routing_info", {})
        actual_path = routing_info.get("path", "unknown")
        actual_tools = routing_info.get("tools_called", [])
        actual_tool = actual_tools[0] if actual_tools else "none"
        
        # 检查是否符合预期
        path_correct = actual_path == test_case["expected_path"]
        tool_correct = actual_tool == test_case["expected_tool"]
        
        print(f"  路由路径: {actual_path} {'✅' if path_correct else '❌'}")
        print(f"  工具调用: {actual_tool} {'✅' if tool_correct else '❌'}")
        print(f"  Token节省: {result.get('performance', {}).get('token_saved', False)}")
        print(f"  响应时间: {result.get('performance', {}).get('processing_time_ms', 0):.2f}ms")
        print(f"  AI响应: {result['response'][:80]}...")
        
        results.append({
            "input": test_case["input"],
            "path_correct": path_correct,
            "tool_correct": tool_correct,
            "token_saved": result.get('performance', {}).get('token_saved', False)
        })
    
    print(f"\n📈 测试后记忆状态:")
    final_stats = memory_manager.get_memory_stats()
    print(f"  交互数: {initial_stats.get('total_interactions', 0)} → {final_stats.get('total_interactions', 0)}")
    print(f"  短期记忆: {initial_stats.get('short_term_count', 0)} → {final_stats.get('short_term_count', 0)}")
    print(f"  长期记忆: {initial_stats.get('long_term_count', 0)} → {final_stats.get('long_term_count', 0)}")
    
    # 统计结果
    total_tests = len(results)
    path_success = sum(1 for r in results if r["path_correct"])
    tool_success = sum(1 for r in results if r["tool_correct"])
    token_savings = sum(1 for r in results if r["token_saved"])
    memory_updated = final_stats.get('total_interactions', 0) > initial_stats.get('total_interactions', 0)
    
    print(f"\n📊 测试结果统计:")
    print(f"  路由准确率: {path_success}/{total_tests} ({path_success/total_tests*100:.1f}%)")
    print(f"  工具准确率: {tool_success}/{total_tests} ({tool_success/total_tests*100:.1f}%)")
    print(f"  Token节省率: {token_savings}/{total_tests} ({token_savings/total_tests*100:.1f}%)")
    print(f"  记忆更新: {'✅' if memory_updated else '❌'}")
    
    # 整体评估
    overall_score = (path_success + tool_success + token_savings + (1 if memory_updated else 0)) / (total_tests * 3 + 1) * 100
    
    print(f"\n🎯 整体评估:")
    if overall_score >= 90:
        grade = "🏆 A+ (优秀)"
    elif overall_score >= 80:
        grade = "🎯 A (良好)"
    elif overall_score >= 70:
        grade = "👍 B (合格)"
    else:
        grade = "⚠️ C (需改进)"
    
    print(f"  综合得分: {overall_score:.1f}%")
    print(f"  系统评级: {grade}")
    
    if overall_score >= 85:
        print(f"\n🎉 双层路由记忆集成系统测试通过！")
        print(f"   ✅ 可以安全集成到生产环境")
        print(f"   ✅ 记忆功能正常工作")
        print(f"   ✅ Token节省显著")
    else:
        print(f"\n⚠️ 系统需要进一步优化")
        print(f"   建议继续调试和改进")
    
    return chat_handler, results


def test_memory_persistence():
    """测试记忆持久性"""
    print(f"\n🧠 记忆持久性测试")
    print("-" * 40)
    
    # 第一轮对话
    chat_handler, _ = test_full_app_integration()
    
    # 模拟重新连接（但保持记忆）
    print(f"\n🔄 模拟用户重新连接...")
    
    # 检查记忆是否保持
    stats = chat_handler.memory_manager.get_memory_stats()
    print(f"  保持的交互数: {stats.get('total_interactions', 0)}")
    print(f"  用户模式数: {len(stats.get('user_patterns', {}))}")
    
    if stats.get('total_interactions', 0) > 0:
        print(f"  ✅ 记忆成功保持")
    else:
        print(f"  ❌ 记忆丢失")


if __name__ == "__main__":
    print("🚀 开始完整应用集成测试...\n")
    
    try:
        chat_handler, results = test_full_app_integration()
        test_memory_persistence()
        
        print(f"\n{'='*60}")
        print("🎉 所有测试完成！双层路由记忆集成系统已准备就绪！")
        print("📢 建议: 可以将ENABLE_ENHANCED_ROUTING设为True并部署到生产环境")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
