#!/usr/bin/env python3
"""
路由性能测试脚本 - 批量测试增强意图路由系统
"""

import sys
import os
import json
import time
import requests
from typing import Dict, List, Any
from collections import defaultdict, Counter

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class RoutingPerformanceTest:
    """路由性能测试器"""
    
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.test_results = []
        self.stats = defaultdict(int)
        
    def create_test_samples(self) -> List[Dict[str, str]]:
        """创建20个测试样本"""
        return [
            # 海王相关 (期望: seaking_tool)
            {"input": "给我一套海王话术练习", "expected_intent": "seaking", "expected_tool": "seaking_tool"},
            {"input": "我想学习撩妹技巧", "expected_intent": "seaking", "expected_tool": "seaking_tool"},
            {"input": "教我一些PUA话术", "expected_intent": "seaking", "expected_tool": "seaking_tool"},
            {"input": "如何成为海王高手", "expected_intent": "seaking", "expected_tool": "seaking_tool"},
            
            # 高风险情况 (期望: help_tool, search_tool)
            {"input": "他威胁要打我", "expected_intent": "risk", "expected_tool": "help_tool"},
            {"input": "男朋友总是冷暴力对我", "expected_intent": "romance", "expected_tool": "help_tool"},
            {"input": "我被男朋友控制了", "expected_intent": "risk", "expected_tool": "help_tool"},
            
            # 恋爱关系-他人 (期望: roast_tool)
            {"input": "朋友的男朋友出轨了", "expected_intent": "romance", "expected_tool": "roast_tool"},
            {"input": "室友被渣男骗了", "expected_intent": "romance", "expected_tool": "roast_tool"},
            {"input": "闺蜜男朋友劈腿", "expected_intent": "romance", "expected_tool": "roast_tool"},
            
            # 恋爱关系-自己 (期望: roast_tool 或 severity_analyzer)
            {"input": "我男朋友不回我消息", "expected_intent": "romance", "expected_tool": "roast_tool"},
            {"input": "我每天都在想他", "expected_intent": "romance", "expected_tool": "severity_analyzer"},
            {"input": "分手后还是忘不了他", "expected_intent": "romance", "expected_tool": "roast_tool"},
            {"input": "我控制不住刷他朋友圈", "expected_intent": "romance", "expected_tool": "severity_analyzer"},
            
            # 职场话题 (期望: talk_tool)
            {"input": "我同事老是针对我", "expected_intent": "daily", "expected_tool": "talk_tool"},
            {"input": "老板让我加班不给钱", "expected_intent": "daily", "expected_tool": "talk_tool"},
            {"input": "工作压力太大了", "expected_intent": "daily", "expected_tool": "talk_tool"},
            
            # 搜索请求 (期望: search_tool)
            {"input": "搜索一下恋爱脑治疗方法", "expected_intent": "search", "expected_tool": "search_tool"},
            
            # 日常话题 (期望: talk_tool 或 agent)
            {"input": "今天心情不好", "expected_intent": "daily", "expected_tool": "talk_tool"},
            {"input": "天气真不错", "expected_intent": "daily", "expected_tool": "agent"}
        ]
    
    def test_single_request(self, sample: Dict) -> Dict[str, Any]:
        """测试单个请求"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.server_url}/chat",
                json={"input": sample["input"]},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = (time.time() - start_time) * 1000
                
                return {
                    "input": sample["input"],
                    "expected_intent": sample["expected_intent"],
                    "expected_tool": sample["expected_tool"],
                    "response": result.get("response", ""),
                    "routing_info": result.get("routing_info", {}),
                    "performance": result.get("performance", {}),
                    "success": True,
                    "processing_time_ms": processing_time,
                    "status_code": response.status_code
                }
            else:
                return {
                    "input": sample["input"],
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "processing_time_ms": (time.time() - start_time) * 1000
                }
                
        except Exception as e:
            return {
                "input": sample["input"],
                "success": False,
                "error": str(e),
                "processing_time_ms": (time.time() - start_time) * 1000
            }
    
    def run_batch_test(self) -> Dict[str, Any]:
        """运行批量测试"""
        print("🧪 启动路由性能批量测试")
        print("=" * 80)
        
        samples = self.create_test_samples()
        print(f"📊 测试样本数量: {len(samples)}")
        print(f"🌐 服务器地址: {self.server_url}")
        print("-" * 80)
        
        # 测试服务器连接
        try:
            health_check = requests.get(f"{self.server_url}/", timeout=5)
            print(f"✅ 服务器连接正常 (状态码: {health_check.status_code})")
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
            return {"error": "服务器不可达"}
        
        print("\n开始测试...")
        
        # 执行测试
        for i, sample in enumerate(samples, 1):
            print(f"\n[{i:2d}/20] 测试: {sample['input'][:30]}...")
            
            result = self.test_single_request(sample)
            self.test_results.append(result)
            
            if result["success"]:
                routing_path = result["routing_info"].get("path", "unknown")
                tools_called = result["routing_info"].get("tools_called", [])
                token_saved = result["performance"].get("token_saved", False)
                
                print(f"     路由: {routing_path}")
                print(f"     工具: {tools_called}")
                print(f"     Token节省: {'✅' if token_saved else '❌'}")
                print(f"     耗时: {result['processing_time_ms']:.0f}ms")
            else:
                print(f"     ❌ 失败: {result['error']}")
            
            # 短暂延迟避免请求过频
            time.sleep(0.5)
        
        # 分析结果
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """分析测试结果"""
        print(f"\n📈 测试结果分析")
        print("=" * 80)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        total_tests = len(self.test_results)
        success_rate = len(successful_tests) / total_tests if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功率: {success_rate:.1%} ({len(successful_tests)}/{total_tests})")
        
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"  - {test['input'][:50]}... : {test['error']}")
        
        if not successful_tests:
            return {"error": "没有成功的测试结果"}
        
        # 1. 路由路径统计
        routing_paths = [r["routing_info"].get("path", "unknown") for r in successful_tests]
        path_counter = Counter(routing_paths)
        
        print(f"\n🛤️  路由路径分布:")
        for path, count in path_counter.most_common():
            percentage = count / len(successful_tests) * 100
            print(f"  {path:15s}: {count:2d}次 ({percentage:5.1f}%)")
        
        # 2. 工具调用统计
        all_tools = []
        for r in successful_tests:
            tools = r["routing_info"].get("tools_called", [])
            all_tools.extend(tools)
        
        tool_counter = Counter(all_tools)
        print(f"\n🔧 工具调用分布:")
        for tool, count in tool_counter.most_common():
            percentage = count / len(all_tools) * 100 if all_tools else 0
            print(f"  {tool:15s}: {count:2d}次 ({percentage:5.1f}%)")
        
        # 3. Token节省统计
        token_saved_count = sum(1 for r in successful_tests 
                               if r["performance"].get("token_saved", False))
        token_savings_rate = token_saved_count / len(successful_tests)
        
        print(f"\n💰 Token节省统计:")
        print(f"  节省次数: {token_saved_count}/{len(successful_tests)}")
        print(f"  节省率: {token_savings_rate:.1%}")
        
        # 4. 性能统计
        processing_times = [r["processing_time_ms"] for r in successful_tests]
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        min_time = min(processing_times)
        
        print(f"\n⏱️  性能统计:")
        print(f"  平均响应时间: {avg_time:.0f}ms")
        print(f"  最快响应时间: {min_time:.0f}ms")
        print(f"  最慢响应时间: {max_time:.0f}ms")
        
        # 5. 路由准确性分析
        print(f"\n🎯 路由准确性分析:")
        
        # 分类统计
        seaking_tests = [r for r in successful_tests if "海王" in r["input"] or "撩妹" in r["input"] or "PUA" in r["input"]]
        seaking_correct = sum(1 for r in seaking_tests if "seaking_tool" in r["routing_info"].get("tools_called", []))
        
        risk_tests = [r for r in successful_tests if "威胁" in r["input"] or "暴力" in r["input"] or "控制" in r["input"]]
        risk_correct = sum(1 for r in risk_tests if "help_tool" in r["routing_info"].get("tools_called", []))
        
        romance_tests = [r for r in successful_tests if "朋友" in r["input"] or "男朋友" in r["input"] or "出轨" in r["input"]]
        romance_correct = sum(1 for r in romance_tests if "roast_tool" in r["routing_info"].get("tools_called", []))
        
        workplace_tests = [r for r in successful_tests if "同事" in r["input"] or "老板" in r["input"] or "工作" in r["input"]]
        workplace_correct = sum(1 for r in workplace_tests if "talk_tool" in r["routing_info"].get("tools_called", []))
        
        print(f"  海王类别准确率: {seaking_correct}/{len(seaking_tests)} ({seaking_correct/len(seaking_tests)*100 if seaking_tests else 0:.1f}%)")
        print(f"  风险类别准确率: {risk_correct}/{len(risk_tests)} ({risk_correct/len(risk_tests)*100 if risk_tests else 0:.1f}%)")
        print(f"  恋爱类别准确率: {romance_correct}/{len(romance_tests)} ({romance_correct/len(romance_tests)*100 if romance_tests else 0:.1f}%)")
        print(f"  职场类别准确率: {workplace_correct}/{len(workplace_tests)} ({workplace_correct/len(workplace_tests)*100 if workplace_tests else 0:.1f}%)")
        
        # 6. 综合评分
        direct_route_rate = path_counter.get("direct", 0) / len(successful_tests)
        agent_fallback_rate = path_counter.get("agent_fallback", 0) / len(successful_tests)
        
        print(f"\n🏆 综合评分:")
        print(f"  直接路由率: {direct_route_rate:.1%}")
        print(f"  Agent兜底率: {agent_fallback_rate:.1%}")
        print(f"  Token节省率: {token_savings_rate:.1%}")
        print(f"  系统成功率: {success_rate:.1%}")
        
        # 计算综合得分 (0-100)
        score = (
            direct_route_rate * 40 +  # 直接路由权重40%
            token_savings_rate * 30 + # Token节省权重30%
            success_rate * 20 +       # 成功率权重20%
            (1 - agent_fallback_rate) * 10  # 减少兜底权重10%
        ) * 100
        
        print(f"  综合得分: {score:.1f}/100")
        
        return {
            "total_tests": total_tests,
            "success_rate": success_rate,
            "routing_distribution": dict(path_counter),
            "tool_distribution": dict(tool_counter),
            "token_savings_rate": token_savings_rate,
            "performance": {
                "avg_time_ms": avg_time,
                "min_time_ms": min_time,
                "max_time_ms": max_time
            },
            "accuracy": {
                "seaking": seaking_correct / len(seaking_tests) if seaking_tests else 0,
                "risk": risk_correct / len(risk_tests) if risk_tests else 0,
                "romance": romance_correct / len(romance_tests) if romance_tests else 0,
                "workplace": workplace_correct / len(workplace_tests) if workplace_tests else 0
            },
            "direct_route_rate": direct_route_rate,
            "agent_fallback_rate": agent_fallback_rate,
            "comprehensive_score": score,
            "detailed_results": self.test_results
        }
    
    def save_results(self, results: Dict, filename: str = "routing_test_results.json"):
        """保存测试结果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 测试结果已保存到: {filename}")
        except Exception as e:
            print(f"\n❌ 保存结果失败: {e}")


def main():
    """主函数"""
    print("🚀 路由性能测试工具")
    print("作者: Anti-Love-Brain-Agent Team")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    # 创建测试器
    tester = RoutingPerformanceTest()
    
    # 运行测试
    results = tester.run_batch_test()
    
    if "error" not in results:
        # 保存结果
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"routing_test_results_{timestamp}.json"
        tester.save_results(results, filename)
        
        print(f"\n✅ 测试完成！")
        print(f"🎯 关键指标:")
        print(f"  • 直接路由率: {results['direct_route_rate']:.1%}")
        print(f"  • Token节省率: {results['token_savings_rate']:.1%}")
        print(f"  • Agent兜底率: {results['agent_fallback_rate']:.1%}")
        print(f"  • 综合得分: {results['comprehensive_score']:.1f}/100")
    else:
        print(f"\n❌ 测试失败: {results['error']}")


if __name__ == "__main__":
    main()
