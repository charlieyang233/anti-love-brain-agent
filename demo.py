#!/usr/bin/env python3
"""
Anti Love Brain Agent - 功能演示脚本
验证双层路由系统和所有工具功能正常工作
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_api_endpoint():
    """测试API端点功能"""
    import httpx
    
    base_url = "http://localhost:8000"
    
    print("🔍 测试API端点...")
    
    test_cases = [
        {
            "name": "系统状态检查",
            "endpoint": "/system/status",
            "method": "GET"
        },
        {
            "name": "海王识别测试", 
            "endpoint": "/chat",
            "method": "POST",
            "data": {"input": "给我一套海王话术练习"}
        },
        {
            "name": "恋爱脑分析测试",
            "endpoint": "/chat", 
            "method": "POST",
            "data": {"input": "他两天不回我消息，我该怎么办？"}
        },
        {
            "name": "日常聊天测试",
            "endpoint": "/chat",
            "method": "POST", 
            "data": {"input": "今天天气真好"}
        },
        {
            "name": "路由统计查看",
            "endpoint": "/system/routing/stats",
            "method": "GET"
        }
    ]
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test in test_cases:
            try:
                print(f"  📊 {test['name']}...")
                
                if test['method'] == 'GET':
                    response = await client.get(f"{base_url}{test['endpoint']}")
                else:
                    response = await client.post(
                        f"{base_url}{test['endpoint']}", 
                        json=test['data'],
                        headers={"Content-Type": "application/json"}
                    )
                
                if response.status_code == 200:
                    result_data = response.json()
                    print(f"    ✅ 成功 - 状态码: {response.status_code}")
                    
                    # 显示关键信息
                    if 'routing_info' in result_data:
                        routing = result_data['routing_info']
                        print(f"    🎯 路由类型: {routing.get('routing_type', 'unknown')}")
                        print(f"    ⚡ 处理时间: {routing.get('processing_time_ms', 0):.2f}ms")
                    
                    if 'response' in result_data:
                        response_text = result_data['response'][:100] + "..." if len(result_data['response']) > 100 else result_data['response']
                        print(f"    💬 响应: {response_text}")
                    
                    results.append({
                        "test": test['name'],
                        "status": "success",
                        "data": result_data
                    })
                else:
                    print(f"    ❌ 失败 - 状态码: {response.status_code}")
                    print(f"    📝 错误: {response.text}")
                    results.append({
                        "test": test['name'], 
                        "status": "failed",
                        "error": response.text
                    })
                    
            except Exception as e:
                print(f"    ❌ 异常: {str(e)}")
                results.append({
                    "test": test['name'],
                    "status": "error", 
                    "error": str(e)
                })
            
            print()
    
    return results

def test_local_components():
    """测试本地组件功能"""
    print("🔧 测试本地组件...")
    
    try:
        # 测试环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        print("  📋 检查环境变量...")
        required_vars = ["OPENAI_API_KEY"]
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"    ✅ {var}: 已设置")
            else:
                print(f"    ❌ {var}: 未设置")
        
        # 测试双层路由系统
        print("  🎯 测试双层路由系统...")
        from src.intent.core.dual_layer_router import DualLayerRouter
        
        router = DualLayerRouter()
        test_inputs = [
            "给我一套海王话术",
            "他不回我消息", 
            "今天天气不错"
        ]
        
        for test_input in test_inputs:
            result = router.route(test_input)
            print(f"    📝 输入: {test_input}")
            print(f"    🎯 路由类型: {result.routing_type}")
            print(f"    ⚡ 处理时间: {result.processing_time_ms:.2f}ms")
            print()
        
        # 测试记忆管理器
        print("  🧠 测试记忆管理器...")
        from src.memory_manager import SmartMemoryManager
        
        memory = SmartMemoryManager(max_conversation_window=5)
        memory.add_interaction("测试用户输入", "测试AI回复")
        stats = memory.get_memory_stats()
        print(f"    📊 记忆统计: {stats}")
        
        print("  ✅ 本地组件测试完成\n")
        return True
        
    except Exception as e:
        print(f"  ❌ 本地组件测试失败: {str(e)}\n")
        return False

def generate_report(api_results, local_success):
    """生成测试报告"""
    print("📊 测试报告生成中...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "local_components": "success" if local_success else "failed",
        "api_tests": api_results,
        "summary": {
            "total_tests": len(api_results),
            "successful": len([r for r in api_results if r['status'] == 'success']),
            "failed": len([r for r in api_results if r['status'] != 'success'])
        }
    }
    
    # 保存报告
    report_file = f"demo_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 测试报告已保存: {report_file}")
    
    # 显示总结
    success_rate = (report['summary']['successful'] / report['summary']['total_tests']) * 100
    print(f"\n🎯 测试总结:")
    print(f"  📊 API测试: {report['summary']['successful']}/{report['summary']['total_tests']} 通过 ({success_rate:.1f}%)")
    print(f"  🔧 本地组件: {'✅ 通过' if local_success else '❌ 失败'}")
    
    if success_rate >= 80 and local_success:
        print(f"\n🎉 项目状态: 🟢 健康")
        print(f"🚀 双层路由系统运行正常，可以开始使用！")
    else:
        print(f"\n⚠️  项目状态: 🟡 需要检查")
        print(f"🔍 请检查失败的测试项目并修复问题")

async def main():
    """主函数"""
    print("🚀 Anti Love Brain Agent - 功能演示")
    print("=" * 50)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试本地组件
    local_success = test_local_components()
    
    # 测试API端点（需要服务器运行）
    try:
        api_results = await test_api_endpoint()
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        print("💡 请确保服务器正在运行: python -m uvicorn app:app --reload")
        api_results = []
    
    # 生成报告
    generate_report(api_results, local_success)
    
    print("\n🎯 演示完成！")
    print("📚 查看完整文档: PROJECT_GUIDE.md")
    print("⚡ 快速开始: QUICK_START.md")

if __name__ == "__main__":
    asyncio.run(main())
