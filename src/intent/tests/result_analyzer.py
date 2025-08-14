#!/usr/bin/env python3
"""
路由测试结果分析器 - 深度分析测试结果
"""

import json
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Any


def analyze_test_results(filename: str):
    """分析测试结果"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return
    
    print("📊 详细路由测试结果分析")
    print("=" * 80)
    
    detailed_results = data.get("detailed_results", [])
    
    # 重新计算正确的统计数据
    successful_tests = [r for r in detailed_results if r["success"]]
    
    # 路由路径统计
    routing_paths = [r["routing_info"].get("path", "unknown") for r in successful_tests]
    path_counter = Counter(routing_paths)
    
    print(f"🛤️  路由路径详细分析:")
    total_success = len(successful_tests)
    for path, count in path_counter.most_common():
        percentage = count / total_success * 100
        print(f"  {path:20s}: {count:2d}次 ({percentage:5.1f}%)")
    
    # 工具调用统计
    all_tools = []
    for r in successful_tests:
        tools = r["routing_info"].get("tools_called", [])
        all_tools.extend(tools)
    
    tool_counter = Counter(all_tools)
    print(f"\n🔧 工具调用详细分析:")
    for tool, count in tool_counter.most_common():
        percentage = count / len(all_tools) * 100 if all_tools else 0
        print(f"  {tool:20s}: {count:2d}次 ({percentage:5.1f}%)")
    
    # Token节省分析
    token_saved_tests = [r for r in successful_tests 
                        if r["performance"].get("token_saved", False)]
    token_savings_rate = len(token_saved_tests) / total_success if total_success > 0 else 0
    
    print(f"\n💰 Token节省详细分析:")
    print(f"  节省成功: {len(token_saved_tests):2d}次")
    print(f"  总测试数: {total_success:2d}次")
    print(f"  节省率:   {token_savings_rate:5.1%}")
    
    print(f"\n  Token节省的请求:")
    for r in token_saved_tests:
        tools = ', '.join(r["routing_info"].get("tools_called", []))
        print(f"    • {r['input'][:40]:40s} -> {tools}")
    
    # 分类准确性分析
    print(f"\n🎯 分类准确性详细分析:")
    
    categories = {
        "海王类": ["海王", "撩妹", "PUA", "话术"],
        "风险类": ["威胁", "暴力", "控制"],
        "恋爱类": ["男朋友", "朋友", "出轨", "劈腿", "渣男"],
        "职场类": ["同事", "老板", "工作", "加班"],
        "搜索类": ["搜索"],
        "日常类": ["心情", "天气"]
    }
    
    expected_tools = {
        "海王类": ["seaking_tool"],
        "风险类": ["help_tool", "search_tool"],
        "恋爱类": ["roast_tool", "severity_analyzer"],
        "职场类": ["talk_tool"],
        "搜索类": ["search_tool"],
        "日常类": ["talk_tool", "original_agent"]
    }
    
    for category, keywords in categories.items():
        # 找到属于该类别的测试
        category_tests = []
        for r in successful_tests:
            if any(keyword in r["input"] for keyword in keywords):
                category_tests.append(r)
        
        if not category_tests:
            continue
            
        print(f"\n  {category} ({len(category_tests)}个测试):")
        
        # 分析路由准确性
        expected_tools_for_category = expected_tools.get(category, [])
        correct_routes = 0
        
        for r in category_tests:
            input_text = r["input"]
            actual_tools = r["routing_info"].get("tools_called", [])
            routing_path = r["routing_info"].get("path", "unknown")
            token_saved = r["performance"].get("token_saved", False)
            
            # 检查是否路由正确
            is_correct = any(tool in actual_tools for tool in expected_tools_for_category)
            if is_correct:
                correct_routes += 1
                status = "✅"
            else:
                status = "❌"
            
            tools_str = ', '.join(actual_tools)
            print(f"    {status} {input_text[:35]:35s} -> {routing_path:10s} ({tools_str}) {'💰' if token_saved else ''}")
        
        accuracy = correct_routes / len(category_tests) if category_tests else 0
        print(f"    准确率: {correct_routes}/{len(category_tests)} ({accuracy:.1%})")
    
    # 性能分析
    processing_times = [r["processing_time_ms"] for r in successful_tests]
    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    print(f"\n⏱️  性能详细分析:")
    print(f"  平均响应时间: {avg_time:.1f}ms")
    print(f"  最快响应:     {min(processing_times):.1f}ms" if processing_times else "  最快响应:     N/A")
    print(f"  最慢响应:     {max(processing_times):.1f}ms" if processing_times else "  最慢响应:     N/A")
    
    # 按路由路径分析性能
    path_times = defaultdict(list)
    for r in successful_tests:
        path = r["routing_info"].get("path", "unknown")
        path_times[path].append(r["processing_time_ms"])
    
    print(f"\n  按路由路径分析:")
    for path, times in path_times.items():
        avg_path_time = sum(times) / len(times)
        print(f"    {path:15s}: 平均 {avg_path_time:6.1f}ms (共{len(times)}次)")
    
    # 计算正确的综合评分
    direct_rate = path_counter.get("direct", 0) / total_success
    agent_rate = path_counter.get("agent_fallback", 0) / total_success
    success_rate = len(successful_tests) / len(detailed_results)
    
    print(f"\n🏆 重新计算的综合评分:")
    print(f"  直接路由率: {direct_rate:.1%}")
    print(f"  Agent兜底率: {agent_rate:.1%}")
    print(f"  Token节省率: {token_savings_rate:.1%}")
    print(f"  系统成功率: {success_rate:.1%}")
    
    # 正确的综合得分计算
    score = (
        direct_rate * 40 +         # 直接路由权重40%
        token_savings_rate * 30 +  # Token节省权重30%
        success_rate * 20 +        # 成功率权重20%
        (1 - agent_rate) * 10      # 减少兜底权重10%
    ) * 100
    
    print(f"  综合得分: {score:.1f}/100")
    
    # 改进建议
    print(f"\n💡 改进建议:")
    
    if direct_rate < 0.7:
        print(f"  • 直接路由率偏低({direct_rate:.1%})，建议优化意图识别规则")
    
    if token_savings_rate < 0.5:
        print(f"  • Token节省率偏低({token_savings_rate:.1%})，建议增加更多直接路由规则")
    
    if agent_rate > 0.3:
        print(f"  • Agent兜底率过高({agent_rate:.1%})，建议扩展路由覆盖范围")
    
    # 找出问题案例
    problem_cases = [r for r in successful_tests 
                    if r["routing_info"].get("path") == "agent_fallback"]
    
    if problem_cases:
        print(f"\n🚨 需要优化的Agent兜底案例:")
        for r in problem_cases[:5]:  # 只显示前5个
            print(f"  • {r['input']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # 使用最新的测试结果文件
        filename = "routing_test_results_20250814_182147.json"
    
    analyze_test_results(filename)
