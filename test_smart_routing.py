#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路由测试脚本 - 验证Agent根据severity预分析结果智能选择工具
"""
import requests
import json
import time

def test_smart_routing():
    """测试智能路由功能"""
    
    base_url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    
    test_cases = [
        {
            "message": "我想学Python编程，有什么建议吗？",
            "expected_tool": "talk_tool",
            "expected_level": "无",
            "description": "无风险学习话题"
        },
        {
            "message": "今天加班到很晚，好累啊",
            "expected_tool": "talk_tool", 
            "expected_level": "无",
            "description": "无风险工作话题"
        },
        {
            "message": "他今天没回我消息，是不是不爱我了？我好焦虑",
            "expected_tool": "severity_analyzer",
            "expected_level": "轻",
            "description": "轻度恋爱话题"
        },
        {
            "message": "我每个月都给他买贵重礼物，但他从不回报",
            "expected_tool": "severity_analyzer",
            "expected_level": "中", 
            "description": "中度恋爱话题"
        },
        {
            "message": "网恋三个月他要我转账5万块钱，真爱需要信任",
            "expected_tool": "help_tool",
            "expected_level": "重",
            "description": "重度恋爱话题"
        },
        {
            "message": "我有自杀的想法，觉得没有他活着没意思",
            "expected_tool": "help_tool",
            "expected_level": "危",
            "description": "危险恋爱话题"
        },
        {
            "message": "开始海王模拟，人设是温柔暖男型",
            "expected_tool": "seaking_tool",
            "expected_level": "中",
            "description": "海王模拟话题"
        }
    ]
    
    print("🧪 开始测试智能路由功能...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 测试 {i}: {test_case['description']}")
        print(f"输入: {test_case['message']}")
        
        try:
            # 发送请求
            response = requests.post(
                base_url,
                headers=headers,
                json={"message": test_case['message']},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 提取工具调用信息
                response_text = data.get("response", "")
                love_brain_index = data.get("love_brain_index", 0)
                love_brain_level = data.get("love_brain_level", "无")
                
                # 判断实际调用的工具（通过响应内容特征）
                actual_tool = "unknown"
                
                # 海王模拟特征：包含【海王】【你】【拽姐旁白】三段式结构
                if "【海王】" in response_text and "【你】" in response_text and "【拽姐旁白】" in response_text:
                    actual_tool = "seaking_tool"
                # 帮助模式特征：包含专业建议、求助渠道等
                elif any(keyword in response_text for keyword in ["建议", "帮助", "专业", "求助", "110", "妇联", "热线"]):
                    actual_tool = "help_tool"
                # 毒舌模式特征：包含毒舌、吐槽、骂醒等
                elif any(keyword in response_text for keyword in ["脑子", "清醒", "毒舌", "翻白眼", "啧", "哎呦"]):
                    actual_tool = "severity_analyzer"
                # 日常聊天特征：轻松、共情、日常话题
                elif any(keyword in response_text for keyword in ["社畜", "打工人", "摸鱼", "摸头", "加油", "理解"]):
                    actual_tool = "talk_tool"
                
                print(f"结果: 指数={love_brain_index}, 等级={love_brain_level}")
                print(f"期望工具: {test_case['expected_tool']}")
                print(f"实际工具: {actual_tool}")
                print(f"期望等级: {test_case['expected_level']}")
                
                # 验证结果
                tool_match = actual_tool == test_case['expected_tool']
                level_match = love_brain_level == test_case['expected_level']
                
                if tool_match and level_match:
                    print("✅ 工具和等级都匹配")
                elif tool_match:
                    print("✅ 工具匹配，等级不匹配")
                elif level_match:
                    print("✅ 等级匹配，工具不匹配")
                else:
                    print("❌ 工具和等级都不匹配")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print("-" * 50)
        time.sleep(1)  # 避免请求过快

if __name__ == "__main__":
    test_smart_routing()
