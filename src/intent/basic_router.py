#!/usr/bin/env python3
"""
基础意图路由器 - 轻量级前置分流
避免文件创建后变空的问题，直接用终端创建
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Route:
    tool: str
    reason: str
    debug: Dict
    confidence: float = 0.0

def intent_route(text: str) -> Route:
    """轻量级意图路由器"""
    t = text.strip().lower()
    
    # Stage 0: 直达路由
    # 1. 海王练习
    if any(w in t for w in ["海王", "话术", "练习", "模拟", "pua", "对战"]):
        return Route("seaking_tool", "seaking_direct", {"keywords": "海王相关"}, 1.0)
    
    # 2. 高风险
    if any(w in t for w in ["威胁", "家暴", "打我", "自杀", "裸聊", "勒索"]):
        return Route("help_tool", "high_risk", {"keywords": "高风险"}, 1.0)
    
    # Stage 1: 简单分类
    # 3. 非情感话题
    if any(w in t for w in ["天气", "电影", "美食", "工作", "同事", "编程"]):
        return Route("talk_tool", "non_emotion", {"keywords": "日常话题"}, 0.8)
    
    # 4. 恋爱话题分析
    has_love = any(w in t for w in ["男朋友", "女朋友", "对象", "恋爱", "分手", "出轨"])
    has_help = any(w in t for w in ["怎么办", "该不该", "求助", "帮我"])
    is_other = any(w in t for w in ["朋友的", "别人的", "同事的"])
    
    if has_love:
        if has_help and not is_other:
            return Route("severity_analyzer", "love_help_uncertain", {"恋爱求助": True}, 0.6)
        elif is_other:
            return Route("roast_tool", "other_love_vent", {"他人恋爱": True}, 0.9)
        else:
            return Route("severity_analyzer", "love_uncertain", {"恋爱话题": True}, 0.6)
    
    # 5. 兜底
    return Route("talk_tool", "default", {"未分类": True}, 0.5)

def test_router():
    """测试路由器"""
    test_cases = [
        ("给我一套海王话术练习", "seaking_tool"),
        ("他威胁要打我", "help_tool"),
        ("今天天气真好", "talk_tool"),
        ("我男朋友总是冷暴力", "severity_analyzer"),
        ("朋友的男朋友出轨了", "roast_tool"),
        ("我该怎么办？", "talk_tool"),  # 无明确上下文
    ]
    
    print("🧪 基础路由器测试")
    print("=" * 40)
    
    correct = 0
    for text, expected in test_cases:
        route = intent_route(text)
        actual = route.tool
        is_correct = actual == expected
        
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} {text}")
        print(f"   期望: {expected}")
        print(f"   实际: {actual} (置信度: {route.confidence:.2f})")
        print(f"   原因: {route.reason}")
        print()
    
    accuracy = correct / len(test_cases) * 100
    print(f"📊 准确率: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    return accuracy >= 70

if __name__ == "__main__":
    test_router()
