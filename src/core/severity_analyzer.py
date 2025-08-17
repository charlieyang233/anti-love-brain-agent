#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恋爱脑分析器 - 简化版本
"""
import json
from typing import Dict, Any
from pydantic import BaseModel
from .config import llm


class SeverityResult(BaseModel):
    """恋爱脑分析结果"""
    index: int = 0
    level: str = "无"
    signals: list = []
    switch_to_help: bool = False
    confidence: float = 0.0


class SeverityAnalyzer:
    """恋爱脑分析器 - 简化版本"""
    
    def __init__(self):
        self.llm = llm(temperature=0.1)
        
        # 动态人设模板字典
        self.answerstyle = {
            "无": {
                "roleset": "你此时是闺蜜日常吹水模式，轻松友善但保持老李的犀利特色。你的目标是像真闺蜜一样陪用户聊天，可以适当吐槽但整体轻松。",
                "tone": "轻松、友善、略带毒舌的闺蜜感，既能损用户又能损那些让用户困扰的人或事。",
                "restrictions": "避免过度关心恋爱话题，保持日常闲聊的自然感，以共情+犀利吐槽为主，不安慰但让用户感到爽。",
                "output_length": "15-25字左右"
            },
            "轻": {
                "roleset": "你此时是关心调侃模式，温和、偶尔犀利调侃。你的目标是用老李特有的方式接地气的调侃、短促幽默、温和的提醒用户注意情绪健康，但不要过于严肃。",
                "tone": "温和犀利、关心中带调侃、略带挖苦、短促幽默",
                "restrictions": "避免直接批评用户行为，用调侃和暗讽的方式提醒，偶尔夹带网络热梗、讽刺MeMe金句",
                "output_length": "20字左右"
            },
            "中": {
                "roleset": "你此时是温和毒舌锐评模式，短促、有冲击力、语气刻薄。你的目标是通过毒舌直白犀利的分析客观真相，像刀一样狠且精准的戳破恋爱脑的幻想。",
                "tone": "理性、通俗易懂、犀利、善用困惑反问/狠梗/MeMe金句、有一定建设性",
                "restrictions": "底层逻辑保持客观分析问题，避免过度情绪化表达（避免如软饭男/普信男等涉及性别对立的词），保持老李特色",
                "output_length": "25-30字"
            },
            "重": {
                "roleset": "你此时是反恋爱脑且坚决干预模式，高强度毒舌劝阻。你的目标是用老李最犀利、真实尖锐、戏谑夸张的方式帮助用户祛魅/反pua，可适当口语化输出一些建设性建议。",
                "tone": "坚定、犀利、高强度毒舌、真实尖锐、关切、戏谑夸张、口语化",
                "restrictions": "必须明确用指出风险，强烈建议用户寻求专业帮助，语气要够狠够直接",
                "output_length": "25-35字"
            },
            "危": {
                "roleset": "你此时是紧急求助模式，立即阻止用户危险行为。你的目标是立即收起毒舌观察用户情绪，用合适的方式劝阻危险行为，必须提供紧急求助信息。",
                "tone": "紧急、坚决、保护性、可为了共情用户而适当夸张化情绪、提供情绪支持",
                "restrictions": "分析问题提供情绪支持，且必须提供1-2条具体的求助渠道和联系方式，语气要极其坚决",
                "output_length": "可提供较长建议，长度在30-50字左右"
            }
        }
        
        # 分析prompt
        self.prompt_template = """你是"恋爱脑程度识别器"。仔细分析用户的恋爱脑程度，严格按照标准评分，只输出JSON格式。

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

    def analyze_with_answerstyle(self, user_text: str, context_summary: str = "") -> Dict[str, Any]:
        """
        分析用户输入并返回对应的人设模板
        
        Args:
            user_text: 用户输入文本
            context_summary: 上下文摘要
            
        Returns:
            Dict: 包含severity结果和answerstyle模板的完整分析结果
        """
        # 1. 进行恋爱脑分析
        severity_result = self.analyze(user_text, context_summary)
        
        # 2. 根据级别选择对应的人设模板
        selected_style = self.answerstyle.get(severity_result.level, self.answerstyle["轻"])
        
        # 3. 构建动态prompt内容
        dynamic_prompt = self._build_dynamic_prompt(selected_style, severity_result)
        
        # 4. 返回完整的分析结果 + 人设模板
        return {
            "severity": severity_result.dict(),
            "answerstyle": selected_style,
            "dynamic_prompt": dynamic_prompt
        }

    def analyze(self, user_text: str, context_summary: str = "") -> SeverityResult:
        """
        分析用户输入的恋爱脑程度
        
        Args:
            user_text: 用户输入文本
            context_summary: 上下文摘要
            
        Returns:
            SeverityResult: 结构化的分析结果
        """
        try:
            # 构建prompt
            prompt = self.prompt_template.format(
                user_input=user_text,
                context_summary=context_summary
            )
            
            # 调用LLM
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # 解析JSON结果
            return self._parse_response(content)
            
        except Exception as e:
            print(f"LLM分析失败，使用降级策略: {e}")
            # 降级策略：使用关键词匹配
            return self._keyword_fallback(user_text)

    def _build_dynamic_prompt(self, style: Dict, severity: SeverityResult) -> str:
        """构建动态注入到全局prompt的内容"""
        return f"""
                ## 当前响应模式配置
                {style['roleset']}

                ## 响应风格要求
                - 语调特点：{style['tone']}
                - 输出长度：{style['output_length']}
                - 特殊限制：{style['restrictions']}

                ## 当前用户状态分析
                - 恋爱脑级别：{severity.level}级({severity.index}分)
                - 识别信号：{', '.join(severity.signals) if severity.signals else '无特殊信号'}
                - 需要专业帮助：{'是' if severity.switch_to_help else '否'}
                - 分析置信度：{severity.confidence:.1f}
                """

    def _parse_response(self, content: str) -> SeverityResult:
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
                # JSON解析失败，使用降级策略
                return self._keyword_fallback("")
                
        except Exception as e:
            print(f"JSON解析失败: {e}")
            return self._keyword_fallback("")

    def _keyword_fallback(self, user_text: str) -> SeverityResult:
        """降级策略：基于关键词匹配的分析"""
        # 风险关键词权重
        risk_keywords = {
            # 危险信号 (3.0)
            '自杀': 3.0, '自残': 3.0, '自伤': 3.0, '想死': 3.0,
            '暴力': 3.0, '威胁': 3.0, '裸聊': 3.0, '未成年': 3.0,
            
            # 重度信号 (2.0)
            '转账': 2.0, '借钱': 2.0, '万': 2.0, '辞职': 2.0,
            '跟踪': 2.0, '监控': 2.0, '操控': 2.0,
            
            # 中度信号 (1.5)
            '礼物': 1.5, '隐瞒': 1.5, '依赖': 1.5,
            
            # 轻度信号 (1.0)
            '焦虑': 1.0, '担心': 1.0, '消息': 1.0, '回复': 1.0,
        }
        
        # 恋爱相关关键词
        love_keywords = ['他', '她', '男朋友', '女朋友', '恋爱', '分手', '复合', '挽回', 
                        '喜欢', '爱', '不爱', '出轨', '背叛', '冷暴力', 'PUA', '控制', 
                        '依赖', '焦虑', '消息', '回复', '朋友圈', '约会', '礼物', '转账', 
                        '借钱', '结婚', '离婚']
        
        # 检查是否为恋爱话题
        if not any(keyword in user_text for keyword in love_keywords):
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
        
        for keyword, weight in risk_keywords.items():
            if keyword in user_text:
                score += weight
                detected_signals.append(keyword)
        
        # 检查大额数字
        if any(char.isdigit() for char in user_text) and any(word in user_text for word in ['万', '千', '转账', '借钱']):
            score += 1.5
            detected_signals.append('大额转账意愿')
        
        # 根据分数确定级别
        if score >= 3.0:
            level, index, switch_to_help = "危", 95, True
        elif score >= 2.0:
            level, index, switch_to_help = "重", 80, True
        elif score >= 1.0:
            level, index, switch_to_help = "中", 55, False
        else:
            level, index, switch_to_help = "轻", 30, False
        
        return SeverityResult(
            index=index,
            level=level,
            signals=detected_signals if detected_signals else ["情绪焦虑"],
            switch_to_help=switch_to_help,
            confidence=0.6
        )

    # 兼容性方法
    async def analyze_async(self, user_text: str, context_summary: str = "") -> SeverityResult:
        """异步版本（兼容性保留）"""
        return self.analyze(user_text, context_summary)

    async def analyze_with_answerstyle_async(self, user_text: str, context_summary: str = "") -> Dict[str, Any]:
        """异步版本（兼容性保留）"""
        return self.analyze_with_answerstyle(user_text, context_summary)


# 全局实例
severity_analyzer = SeverityAnalyzer()

# 便捷函数
def analyze_severity(user_text: str, context_summary: str = "") -> SeverityResult:
    """便捷的分析函数"""
    return severity_analyzer.analyze(user_text, context_summary)

def analyze_severity_with_style(user_text: str, context_summary: str = "") -> Dict[str, Any]:
    """便捷的带人设分析函数"""
    return severity_analyzer.analyze_with_answerstyle(user_text, context_summary)

# 兼容性保留
async def analyze_severity_async(user_text: str, context_summary: str = "") -> SeverityResult:
    """异步版本（兼容性保留）"""
    return severity_analyzer.analyze(user_text, context_summary)