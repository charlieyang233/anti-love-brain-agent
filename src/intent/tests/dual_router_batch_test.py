#!/usr/bin/env python3
"""
双层路由批量性能测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import time
import json
from datetime import datetime
from src.intent.dual_router_adapter import DualRouterAdapter

def run_dual_router_batch_test():
    """运行双层路由批量测试"""
    
    # 使用相同的20个测试样本
    test_samples = [
        {"input": "给我一套海王话术练习", "category": "seaking"},
        {"input": "我想学习撩妹技巧", "category": "seaking"}, 
        {"input": "教我一些PUA话术", "category": "seaking"},
        {"input": "如何成为海王高手", "category": "seaking"},
        
        {"input": "他威胁要打我", "category": "risk"},
        {"input": "男朋友总是冷暴力对我", "category": "risk"},
        {"input": "我被男朋友控制了", "category": "risk"},
        {"input": "室友被渣男骗了", "category": "risk"},
        
        {"input": "朋友的男朋友出轨了", "category": "romance_other"},
        {"input": "闺蜜男朋友劈腿", "category": "romance_other"},
        {"input": "我男朋友不回我消息", "category": "romance_self"},
        {"input": "我每天都在想他", "category": "romance_self"},
        {"input": "分手后还是忘不了他", "category": "romance_self"},
        {"input": "我控制不住刷他朋友圈", "category": "romance_self"},
        
        {"input": "我同事老是针对我", "category": "workplace"},
        {"input": "老板让我加班不给钱", "category": "workplace"},
        {"input": "工作压力太大了", "category": "workplace"},
        
        {"input": "搜索一下恋爱脑治疗方法", "category": "search"},
        {"input": "今天心情不好", "category": "daily"},
        {"input": "天气真不错", "category": "daily"}
    ]
    
    adapter = DualRouterAdapter()
    
    print("🚀 双层路由批量性能测试")
    print("=" * 60)
    print(f"📊 测试样本数量: {len(test_samples)}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    results = []
    category_stats = {}
    
    for i, sample in enumerate(test_samples, 1):
        start_time = time.time()
        
        result = adapter.route(sample["input"])
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        # 记录结果
        test_result = {
            "input": sample["input"],
            "category": sample["category"],
            "routing_path": result["routing_path"],
            "tools_called": result["tools_called"],
            "token_saved": result["performance_metrics"]["token_saved"],
            "processing_time_ms": processing_time,
            "success": result["success"]
        }
        
        results.append(test_result)
        
        # 统计分类
        category = sample["category"]
        if category not in category_stats:
            category_stats[category] = {"total": 0, "shortcut": 0, "reference": 0, "fallback": 0, "token_saved": 0}
        
        category_stats[category]["total"] += 1
        
        if "direct" in result["routing_path"]:
            category_stats[category]["shortcut"] += 1
        elif "reference" in result["routing_path"]:
            category_stats[category]["reference"] += 1
        else:
            category_stats[category]["fallback"] += 1
            
        if result["performance_metrics"]["token_saved"]:
            category_stats[category]["token_saved"] += 1
        
        # 显示进度
        token_icon = "✅" if result["performance_metrics"]["token_saved"] else "❌"
        print(f"[{i:2d}/{len(test_samples)}] {sample['input'][:30]:<30}...")
        print(f"     路由: {result['routing_path']}")
        print(f"     工具: {result['tools_called']}")
        print(f"     Token节省: {token_icon}")
        print(f"     耗时: {processing_time:.0f}ms")
        print()
    
    # 获取总体统计
    overall_stats = adapter.get_performance_stats()
    
    # 计算指标
    total_tests = len(results)
    shortcut_count = sum(1 for r in results if "direct" in r["routing_path"])
    reference_count = sum(1 for r in results if "reference" in r["routing_path"])
    fallback_count = sum(1 for r in results if "fallback" in r["routing_path"])
    token_saved_count = sum(1 for r in results if r["token_saved"])
    avg_time = sum(r["processing_time_ms"] for r in results) / total_tests
    
    # 显示结果
    print("📈 双层路由测试结果分析")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"成功率: {sum(r['success'] for r in results)/total_tests*100:.1f}% ({sum(r['success'] for r in results)}/{total_tests})")
    print()
    
    print("🛤️  路由路径分布:")
    print(f"  短路直达      : {shortcut_count}次 ({shortcut_count/total_tests*100:.1f}%)")
    print(f"  智能参考      : {reference_count}次 ({reference_count/total_tests*100:.1f}%)")
    print(f"  兜底处理      : {fallback_count}次 ({fallback_count/total_tests*100:.1f}%)")
    print()
    
    print("💰 Token节省统计:")
    print(f"  节省次数: {token_saved_count}/{total_tests}")
    print(f"  节省率: {token_saved_count/total_tests*100:.1f}%")
    print()
    
    print("⏱️  性能统计:")
    print(f"  平均响应时间: {avg_time:.1f}ms")
    print(f"  最快响应时间: {min(r['processing_time_ms'] for r in results):.1f}ms")
    print(f"  最慢响应时间: {max(r['processing_time_ms'] for r in results):.1f}ms")
    print()
    
    print("🎯 分类准确性分析:")
    for category, stats in category_stats.items():
        shortcut_rate = stats["shortcut"] / stats["total"] * 100
        token_rate = stats["token_saved"] / stats["total"] * 100
        print(f"  {category:<15}: 短路率{shortcut_rate:5.1f}% Token节省率{token_rate:5.1f}% ({stats['token_saved']}/{stats['total']})")
    
    print()
    print("🏆 双层路由综合评分:")
    print(f"  短路直达率: {shortcut_count/total_tests*100:.1f}%")
    print(f"  Token节省率: {token_saved_count/total_tests*100:.1f}%")
    print(f"  平均响应时间: {avg_time:.1f}ms")
    print(f"  系统成功率: {sum(r['success'] for r in results)/total_tests*100:.1f}%")
    
    # 对比原系统
    print()
    print("📊 与原系统对比:")
    print("原系统 -> 双层路由")
    print(f"直接路由率: 55.0% -> {shortcut_count/total_tests*100:.1f}% ({'+' if shortcut_count/total_tests*100 > 55 else ''}{shortcut_count/total_tests*100 - 55:.1f}%)")
    print(f"Token节省率: 25.0% -> {token_saved_count/total_tests*100:.1f}% ({'+' if token_saved_count/total_tests*100 > 25 else ''}{token_saved_count/total_tests*100 - 25:.1f}%)")
    print(f"平均耗时: 24.0ms -> {avg_time:.1f}ms (-{24.0-avg_time:.1f}ms)")
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"dual_router_test_results_{timestamp}.json"
    
    output = {
        "timestamp": timestamp,
        "test_samples": test_samples,
        "results": results,
        "statistics": {
            "total_tests": total_tests,
            "shortcut_rate": shortcut_count/total_tests*100,
            "reference_rate": reference_count/total_tests*100,
            "fallback_rate": fallback_count/total_tests*100,
            "token_savings_rate": token_saved_count/total_tests*100,
            "average_time_ms": avg_time,
            "success_rate": sum(r['success'] for r in results)/total_tests*100
        },
        "category_breakdown": category_stats,
        "comparison_with_original": {
            "shortcut_improvement": shortcut_count/total_tests*100 - 55.0,
            "token_savings_improvement": token_saved_count/total_tests*100 - 25.0,
            "speed_improvement": 24.0 - avg_time
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: {filename}")
    print("✅ 双层路由批量测试完成！")
    
    return output

if __name__ == "__main__":
    run_dual_router_batch_test()
