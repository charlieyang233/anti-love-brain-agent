#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步Severity分析器测试脚本
"""
import asyncio
import json
from src.core.severity_analyzer import analyze_severity, SeverityResult

async def test_severity_analyzer():
    """测试异步severity分析器"""
    
    test_cases = [
        {
            "input": "他今天没回我消息，是不是不爱我了？我好焦虑",
            "expected_level": "轻",
            "description": "轻度焦虑"
        },
        {
            "input": "我每个月都给他买贵重礼物，但他从不回报",
            "expected_level": "中", 
            "description": "中度金钱付出"
        },
        {
            "input": "网恋三个月他要我转账5万块钱，真爱需要信任",
            "expected_level": "重",
            "description": "重度金钱风险"
        },
        {
            "input": "我有自杀的想法，觉得没有他活着没意思",
            "expected_level": "危",
            "description": "危险自伤倾向"
        },
        {
            "input": "今天天气真好，我想去公园散步",
            "expected_level": "无",
            "description": "无风险日常话题"
        },
        {
            "input": "今天加班到很晚，好累啊",
            "expected_level": "无",
            "description": "无风险工作话题"
        },
        {
            "input": "我想学Python编程，有什么建议吗？",
            "expected_level": "无",
            "description": "无风险学习话题"
        }
    ]
    
    print("🧪 开始测试异步Severity分析器...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 测试 {i}: {test_case['description']}")
        print(f"输入: {test_case['input']}")
        
        try:
            # 异步分析
            result = await analyze_severity(test_case['input'])
            
            print(f"结果: 指数={result.index}, 等级={result.level}, 置信度={result.confidence}")
            print(f"信号: {result.signals}")
            print(f"需要帮助: {result.switch_to_help}")
            
            # 验证结果
            if result.level == test_case['expected_level']:
                print("✅ 等级匹配")
            else:
                print(f"❌ 等级不匹配，期望: {test_case['expected_level']}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            print("-" * 50)

async def test_performance():
    """测试性能"""
    print("\n🚀 性能测试...")
    
    test_input = "他今天没回我消息，是不是不爱我了？我好焦虑"
    
    import time
    start_time = time.time()
    
    # 连续测试10次
    results = []
    for i in range(10):
        result = await analyze_severity(test_input)
        results.append(result)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10
    
    print(f"平均响应时间: {avg_time:.3f}秒")
    print(f"成功率: {len([r for r in results if r.confidence > 0])}/10")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_severity_analyzer())
    asyncio.run(test_performance())
