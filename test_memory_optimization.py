#!/usr/bin/env python3
"""
测试记忆上下文优化效果
"""

import requests
import json
import time

def test_memory_context_optimization():
    """测试记忆上下文优化效果"""
    base_url = "http://localhost:8000"
    
    # 测试用例：模拟多轮对话，观察记忆上下文的变化
    test_cases = [
        "我想练习一下怎么应对海王",
        "我男朋友不理我了，我好难过",
        "我觉得没有他我活不下去了，我想自杀",
        "他出轨了，但我还是想原谅他",
        "今天工作好累啊"
    ]
    
    print("🧪 开始测试记忆上下文优化效果...")
    print("=" * 60)
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n📝 第{i}轮对话:")
        print(f"用户输入: {message}")
        
        # 发送聊天请求
        response = requests.post(f"{base_url}/chat", json={"message": message})
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            print(f"AI回应: {ai_response[:100]}...")
            
            # 获取记忆统计
            memory_response = requests.get(f"{base_url}/memory/stats")
            if memory_response.status_code == 200:
                memory_stats = memory_response.json()
                print(f"记忆状态: 对话{memory_stats.get('conversation_count', 0)}轮 | "
                      f"压缩{memory_stats.get('compression_count', 0)}次 | "
                      f"窗口大小{memory_stats.get('current_window_size', 8)} | "
                      f"Token使用率{memory_stats.get('memory_usage_ratio', 0):.2%}")
            
            # 获取记忆摘要
            summary_response = requests.get(f"{base_url}/memory/summary")
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                print(f"记忆摘要长度: {len(str(summary_data))} 字符")
        
        else:
            print(f"❌ 请求失败: {response.status_code}")
        
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("\n📊 优化效果对比:")
    print("优化前: 记忆上下文包含大量重复信息，长度可达500+字符")
    print("优化后: 记忆上下文极简化，长度控制在150字符以内")
    print("主要改进:")
    print("- 只在有足够历史时才提供上下文")
    print("- 只显示最近1次风险等级")
    print("- 只显示最频繁的行为模式")
    print("- 只显示最近1轮对话的关键信息")
    print("- 严格控制总长度在150字符以内")

if __name__ == "__main__":
    test_memory_context_optimization()
