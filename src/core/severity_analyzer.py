#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步恋爱脑分析器 - Agent调用前的预处理器
"""
import json
import asyncio
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel
try:
    from .config import llm
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.core.config import llm

class SeverityResult(BaseModel):
    """恋爱脑分析结果"""
    index: int = 0
    level: str = "无"
    signals: list = []
    switch_to_help: bool = False
    confidence: float = 0.0

class AsyncSeverityAnalyzer:
    """异步恋爱脑分析器 - 优化版本"""
    
    def __init__(self):
        self.llm = llm(temperature=0.1)  # 低温度确保一致性
        
        # 保留原有的prompt内容
        self.base_prompt = """你是"恋爱脑程度识别器"。仔细分析用户的恋爱脑程度，严格按照标准评分，只输出JSON格式。

                            ## 评分标准
                            - **无风险(0):** 非恋爱话题，如日常闲聊、工作学习、兴趣爱好等
                            - **轻度(0-39):** 情绪焦虑、过度解读对方行为
                            - **中度(40-69):** 经济付出、隐瞒关系、改变习惯  
                            - **重度(70-89):** 大额转账、重大人生决定、自伤想法
                            - **危险(90-100):** 暴力威胁、违法行为、控制人身自由

                            ## 判断规则
                            1. **重要：** 如果用户谈论的是日常话题（天气、工作、学习、娱乐、生活、加班、项目、考试、游戏、购物、旅游、美食、健身等），必须返回无风险，index=0
                            2. 如果用户谈论的是恋爱相关话题（他、她、男朋友、女朋友、恋爱、分手、复合、挽回、喜欢、爱、不爱、出轨、背叛、冷暴力、PUA、控制、依赖、焦虑、消息、回复、朋友圈、约会、礼物、转账、借钱、结婚、离婚等），按严重程度评分
                            3. 如果不确定，优先判断为轻度而非无风险

                            ## 输出格式
                            {{"index":0-100,"level":"无|轻|中|重|危","signals":["具体风险信号"],"switch_to_help":true|false}}

                            switch_to_help规则：无风险/轻度/中度=false，重度/危险=true

                            用户发言：{user_input}
                            上下文提要：{context_summary}"""
    
    async def analyze(self, user_text: str, context_summary: str = "") -> SeverityResult:
        """
        异步分析用户输入的恋爱脑程度
        
        Args:
            user_text: 用户输入文本
            context_summary: 上下文摘要
            
        Returns:
            SeverityResult: 结构化的分析结果
        """
        try:
            # 直接使用LLM + prompt
            prompt = self.base_prompt.format(
                user_input=user_text,
                context_summary=context_summary
            )
            
            # 异步调用LLM
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # 解析JSON结果
            result = self._parse_llm_response(content)
            return result
            
        except Exception as e:
            print(f"LLM分析失败，使用降级策略: {e}")
            # 降级策略：使用关键词匹配
            return self._fallback_keyword_analysis(user_text)
    
    def _parse_llm_response(self, content: str) -> SeverityResult:
        """解析LLM响应"""
        try:
            # 查找JSON格式的结果
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                
                return SeverityResult(
                    index=data.get("index", 0),
                    level=data.get("level", "无"),
                    signals=data.get("signals", []),
                    switch_to_help=data.get("switch_to_help", False),
                    confidence=0.9  # 成功解析的置信度
                )
            else:
                # 尝试从文本中提取信息
                return self._extract_from_text(content)
                
        except Exception as e:
            print(f"JSON解析失败: {e}")
            return self._extract_from_text(content)
    
    def _extract_from_text(self, content: str) -> SeverityResult:
        """从文本中提取信息（降级处理）"""
        # 简单的关键词匹配
        level_keywords = {
            "轻": ["轻", "轻度", "0-39"],
            "中": ["中", "中度", "40-69"],
            "重": ["重", "重度", "70-89"],
            "危险": ["危", "危险", "90-100"]  # 修正等级名称
        }
        
        # 检查是否为非恋爱话题
        non_love_keywords = ["天气", "散步", "公园", "工作", "学习", "吃饭", "睡觉", "电影", "音乐", "运动"]
        if any(keyword in content for keyword in non_love_keywords):
            return SeverityResult(
                index=0,
                level="无",
                signals=["非恋爱话题"],
                switch_to_help=False,
                confidence=0.8
            )
        
        detected_level = "轻"
        detected_index = 30
        
        for level, keywords in level_keywords.items():
            if any(keyword in content for keyword in keywords):
                detected_level = level
                if level == "轻":
                    detected_index = 30
                elif level == "中":
                    detected_index = 55
                elif level == "重":
                    detected_index = 80
                elif level == "危险":
                    detected_index = 95
                break
        
        return SeverityResult(
            index=detected_index,
            level=detected_level,
            signals=["文本解析"],
            switch_to_help=detected_level in ["重", "危险"],
            confidence=0.5
        )

    def _fallback_keyword_analysis(self, user_text: str) -> SeverityResult:
        """降级策略：基于关键词匹配的分析"""
        # 从example_selector.py中提取的关键风险信号
        critical_signals = {
            # 危险信号 (最高权重)
            '自杀': 3.0, '自残': 3.0, '自伤': 3.0, '想死': 3.0,
            '暴力': 3.0, '威胁': 3.0, '裸聊': 3.0, '未成年': 3.0,
            '软禁': 3.0, '传销': 3.0, '诈骗': 3.0, '强迫': 3.0,
            
            # 重度信号
            '转账': 2.0, '借钱': 2.0, '万': 2.0, '辞职': 2.0,
            '断绝': 2.0, '跟踪': 2.0, '监控': 2.0, '操控': 2.0,
            
            # 中度信号
            '礼物': 1.5, '隐瞒': 1.5, '价值观': 1.5, '依赖': 1.5,
            '检查': 1.5, '疏远': 1.5, '冷淡': 1.5,
            
            # 轻度信号
            '焦虑': 1.0, '担心': 1.0, '消息': 1.0, '回复': 1.0,
            '迎合': 1.0, '改变': 1.0, '理想化': 1.0, '完美': 1.0,
        }
        
        # 恋爱相关关键词
        love_keywords = ['他', '她', '男朋友', '女朋友', '恋爱', '分手', '复合', '挽回', 
                        '喜欢', '爱', '不爱', '出轨', '背叛', '冷暴力', 'PUA', '控制', 
                        '依赖', '焦虑', '消息', '回复', '朋友圈', '约会', '礼物', '转账', 
                        '借钱', '结婚', '离婚', '海王', '模拟', '对战', '话术']
        
        # 检查是否为恋爱话题
        has_love_content = any(keyword in user_text for keyword in love_keywords)
        
        # 特殊处理：海王模拟相关关键词
        seaking_keywords = ['海王', '模拟', '对战', '话术', '练习']
        is_seaking_request = any(keyword in user_text for keyword in seaking_keywords)
        
        if is_seaking_request:
            return SeverityResult(
                index=50,
                level="中",
                signals=["海王模拟请求"],
                switch_to_help=False,
                confidence=0.9
            )
        
        if not has_love_content:
            return SeverityResult(
                index=0,
                level="无",
                signals=["非恋爱话题"],
                switch_to_help=False,
                confidence=0.8
            )
        
        # 计算风险分数
        score = 0.0
        detected_signals = []
        
        for keyword, weight in critical_signals.items():
            if keyword in user_text:
                score += weight
                detected_signals.append(keyword)
        
        # 检查大额数字
        if any(char.isdigit() for char in user_text):
            if any(word in user_text for word in ['万', '千', '转账', '借钱']):
                score += 1.5
                if '大额转账' not in detected_signals:
                    detected_signals.append('大额转账')
        
        # 根据分数确定级别
        if score >= 3.0:
            level = "危险"
            index = 95
            switch_to_help = True
        elif score >= 2.0:
            level = "重"
            index = 80
            switch_to_help = True
        elif score >= 1.0:
            level = "中"
            index = 55
            switch_to_help = False
        else:
            level = "轻"
            index = 30
            switch_to_help = False
        
        return SeverityResult(
            index=index,
            level=level,
            signals=detected_signals if detected_signals else ["关键词匹配"],
            switch_to_help=switch_to_help,
            confidence=0.6
        )

# 全局实例
severity_analyzer = AsyncSeverityAnalyzer()

async def analyze_severity(user_text: str, context_summary: str = "") -> SeverityResult:
    """便捷的异步分析函数"""
    return await severity_analyzer.analyze(user_text, context_summary)
