#!/usr/bin/env python3
"""
测试TalkTool功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.talk import TalkTool

def test_talk_tool():
    """测试TalkTool"""
    try:
        talk_tool = TalkTool()
        
        # 测试简单输入
        result = talk_tool._run("你好")
        print("TalkTool测试结果:")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # 测试日常话题
        result = talk_tool._run("今天天气不错")
        print("日常话题测试结果:")
        print(result)
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_talk_tool()
