#!/usr/bin/env python3
"""
双层路由系统测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.intent.dual_layer_router import DualLayerRouter

def test_dual_layer_routing():
    """测试双层路由系统"""
    router = DualLayerRouter()
    
    # 测试用例：涵盖第一层短路和第二层参考
    test_cases = [
        # === 第一层：短路规则测试 ===
        {
            "category": "🎯 第一层短路 - 显性海王模拟",
            "inputs": [
                "给我一套海王话术练习",
                "教我模拟PUA技巧，来对战几轮",
                "生成一些撩妹话术剧本"
            ],
            "expected_type": "shortcut",
            "expected_tools": ["seaking_tool"]
        },
        
        {
            "category": "🚨 第一层短路 - 显性高风险",
            "inputs": [
                "他威胁要打我",
                "男朋友家暴，怎么办？",
                "被威胁裸聊勒索"
            ],
            "expected_type": "shortcut",
            "expected_tools": ["severity_analyzer", "help_tool", "search_tool"]
        },
        
        {
            "category": "🆘 第一层短路 - 显性非恋爱求助", 
            "inputs": [
                "工作上的问题该怎么办？",
                "学习遇到困难如何解决？"
            ],
            "expected_type": "shortcut",
            "expected_tools": ["help_tool"]
        },
        
        {
            "category": "💔 第一层短路 - 显性恋爱毒舌",
            "inputs": [
                "朋友的男朋友出轨了，太渣了",
                "同事的女朋友劈腿，真恶心"
            ],
            "expected_type": "shortcut", 
            "expected_tools": ["roast_tool"]
        },
        
        {
            "category": "💬 第一层短路 - 显性日常聊天",
            "inputs": [
                "今天天气真不错",
                "最近看了部好电影"
            ],
            "expected_type": "shortcut",
            "expected_tools": ["talk_tool"]
        },
        
        # === 第二层：智能参考测试 ===
        {
            "category": "🤔 第二层参考 - 复杂恋爱情况",
            "inputs": [
                "我被男朋友控制了，不知道怎么办",
                "他对我忽冷忽热，我该不该分手？"
            ],
            "expected_type": "reference",
            "expected_signals": ["self_romance", "help_seeking"]
        },
        
        {
            "category": "🚨 高风险优先 - 冷暴力走高风险",
            "inputs": [
                "男朋友总是冷暴力对我，我很痛苦"
            ],
            "expected_type": "shortcut",
            "expected_tools": ["severity_analyzer", "help_tool", "search_tool"]
        },
        
        {
            "category": "😤 第二层参考 - 职场问题",
            "inputs": [
                "同事老是针对我，很烦"
            ],
            "expected_type": "reference",
            "expected_signals": ["workplace"]
        },
        
        {
            "category": "🆘 职场求助 - 走非恋爱求助",
            "inputs": [
                "老板让我加班不给钱，怎么办？"
            ],
            "expected_type": "shortcut",
            "expected_tools": ["help_tool"]
        },
        
        # === 兜底测试 ===
        {
            "category": "🔄 兜底 - 模糊表达",
            "inputs": [
                "我今天心情不好",
                "感觉生活没意思"
            ],
            "expected_type": "fallback",
            "expected_tools": ["original_agent"]
        }
    ]
    
    print("🚀 双层路由系统测试")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for test_group in test_cases:
        print(f"\n{test_group['category']}")
        print("-" * 40)
        
        for text in test_group["inputs"]:
            total_tests += 1
            result = router.route(text)
            
            print(f"输入: {text}")
            print(f"路由: {result.routing_type}")
            print(f"工具: {result.final_tools}")
            print(f"耗时: {result.processing_time_ms:.1f}ms")
            
            # 验证期望结果
            success = True
            if result.routing_type != test_group["expected_type"]:
                success = False
                print(f"❌ 路由类型错误: 期望{test_group['expected_type']}, 实际{result.routing_type}")
            
            if "expected_tools" in test_group:
                if result.final_tools != test_group["expected_tools"]:
                    success = False
                    print(f"❌ 工具错误: 期望{test_group['expected_tools']}, 实际{result.final_tools}")
            
            if "expected_signals" in test_group and result.reference_signal:
                detected_signals = list(result.reference_signal.matched_keywords.keys())
                for expected_signal in test_group["expected_signals"]:
                    if expected_signal not in detected_signals:
                        success = False
                        print(f"❌ 缺失信号: {expected_signal}")
            
            if success:
                print("✅ PASS")
                passed_tests += 1
            
            # 显示详细解释
            explanation = router.explain_routing(result)
            print(f"详情: {explanation}")
            print()
    
    print("=" * 60)
    print(f"📊 测试结果: {passed_tests}/{total_tests} 通过 ({passed_tests/total_tests*100:.1f}%)")
    
    # 显示系统统计
    stats = router.get_routing_stats()
    print(f"\n📈 系统统计:")
    print(f"  短路规则数: {stats['shortcut_rules']}")
    print(f"  参考模式数: {stats['reference_patterns']}")
    print(f"  关键词类别: {stats['keyword_categories']}")
    print(f"  总关键词数: {stats['total_keywords']}")
    
    return passed_tests == total_tests

def test_performance_comparison():
    """性能对比测试"""
    router = DualLayerRouter()
    
    test_samples = [
        "给我一套海王话术练习",
        "他威胁要打我", 
        "男朋友总是冷暴力对我",
        "今天天气真不错",
        "我今天心情不好"
    ]
    
    print("\n⚡ 性能对比测试")
    print("=" * 40)
    
    import time
    total_time = 0
    shortcut_count = 0
    reference_count = 0
    fallback_count = 0
    
    for sample in test_samples:
        start = time.time()
        result = router.route(sample)
        end = time.time()
        
        processing_time = (end - start) * 1000
        total_time += processing_time
        
        if result.routing_type == "shortcut":
            shortcut_count += 1
        elif result.routing_type == "reference": 
            reference_count += 1
        else:
            fallback_count += 1
        
        print(f"{sample[:20]:<20} | {result.routing_type:<10} | {processing_time:.1f}ms")
    
    print("-" * 40)
    print(f"平均耗时: {total_time/len(test_samples):.1f}ms")
    print(f"短路比例: {shortcut_count/len(test_samples)*100:.1f}%")
    print(f"参考比例: {reference_count/len(test_samples)*100:.1f}%") 
    print(f"兜底比例: {fallback_count/len(test_samples)*100:.1f}%")

if __name__ == "__main__":
    success = test_dual_layer_routing()
    test_performance_comparison()
    
    print(f"\n🎉 双层路由测试{'成功' if success else '失败'}")
    exit(0 if success else 1)
