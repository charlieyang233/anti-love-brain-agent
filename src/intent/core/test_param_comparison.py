#!/usr/bin/env python3
"""
参数模式对比测试 - 简化vs增强参数模式的效果对比
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

from src.intent.core.dual_router_memory import DualRouterMemoryIntegration
from src.memory_manager import SmartMemoryManager
import json

def test_parameter_modes():
    """测试两种参数模式的对比"""
    print("🔍 参数模式对比测试")
    print("=" * 80)
    
    # 创建记忆管理器
    memory_manager = SmartMemoryManager(max_conversation_window=15)
    
    # 创建双层路由集成（简化模式）
    integration = DualRouterMemoryIntegration(memory_manager, param_mode="simplified")
    
    # 测试用例
    test_cases = [
        "我男朋友对我冷暴力，怎么办？",
        "教我一些撩妹话术",
        "同事威胁要散布我的隐私",
        "朋友被PUA了，我该怎么劝她？",
        "今天股市涨了吗？"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {user_input}")
        print("-" * 60)
        
        # 获取参数对比
        comparison = integration.compare_param_modes(user_input)
        
        print("🔸 简化参数 (6字段):")
        simplified = comparison["simplified_params"]
        for key, value in simplified.items():
            print(f"  {key}: {value}")
        
        print(f"\n📊 参数大小对比:")
        print(f"  简化参数: {comparison['simplified_size']} 字符")
        print(f"  增强参数: {comparison['enhanced_size']} 字符") 
        print(f"  大小比率: {comparison['size_ratio']:.1f}x")
        
        print(f"\n🎯 简化参数JSON:")
        print(json.dumps(simplified, ensure_ascii=False, indent=2))
        
        # 展示增强参数的结构（不展示全部内容以节省空间）
        enhanced = comparison["enhanced_params"]
        print(f"\n🔹 增强参数结构 ({len(enhanced)}个字段):")
        for category, content in enhanced.items():
            if isinstance(content, dict):
                print(f"  {category}: {len(content)} 个子字段")
            else:
                print(f"  {category}: {type(content).__name__}")
        
        print("\n" + "=" * 80)

def test_routing_with_simplified_params():
    """测试使用简化参数的完整路由流程"""
    print("\n🚀 简化参数路由流程测试")
    print("=" * 60)
    
    # 创建记忆管理器
    memory_manager = SmartMemoryManager(max_conversation_window=15)
    
    # 创建简化模式的路由集成
    integration = DualRouterMemoryIntegration(memory_manager, param_mode="simplified")
    
    # 测试对话流程
    conversation = [
        "我最近在追一个女生",
        "她总是已读不回我的消息",
        "我是不是应该多发点消息给她？",
        "朋友说我这样很像舔狗",
        "那我应该怎么办呢？"
    ]
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n第 {i} 轮对话: {user_input}")
        print("-" * 40)
        
        # 处理输入并获取响应
        result = integration.process_with_memory_update(user_input)
        
        print(f"路由结果: {result['routing_info']['routing_type']}")
        print(f"使用工具: {result['routing_info']['final_tools']}")
        print(f"响应: {result['response'][:100]}...")
        print(f"记忆更新: {'✓' if result['memory_updated'] else '✗'}")

def main():
    """主测试函数"""
    try:
        test_parameter_modes()
        test_routing_with_simplified_params()
        
        print("\n✅ 所有测试完成！")
        print("\n💡 总结:")
        print("- 简化参数(6字段): 高效、简洁、易于理解")
        print("- 增强参数(37字段): 详细、全面、占用更多token")
        print("- 推荐使用简化模式以提高效率和降低成本")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
