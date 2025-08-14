#!/usr/bin/env python3
"""
简化的智能体参数构建器 - 6字段高效结构
基于原始smart_router设计理念，保持精简而有效的参数传递
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json

@dataclass
class SimplifiedAgentParams:
    """简化的智能体参数 - 6字段核心结构"""
    risk: str  # none|low|medium|high - 风险等级评估
    subject: str  # self|other|unknown - 主体识别
    intent: str  # seaking|risk|romance|daily|unknown - 核心意图
    tone: str  # supportive|neutral|cautious|urgent - 响应语调
    tools: List[str]  # 推荐使用的工具组合
    context: str  # 关键上下文信息摘要

class SimplifiedAgentParameterBuilder:
    """简化的智能体参数构建器"""
    
    def __init__(self):
        """初始化参数构建器"""
        self.tone_mapping = {
            # 风险等级到语调的映射
            "high": "urgent",
            "medium": "cautious", 
            "low": "supportive",
            "none": "neutral"
        }
        
        self.intent_tools = {
            # 意图到工具的标准映射
            "seaking": ["seaking"],
            "risk": ["severity", "help"],
            "romance": ["roast", "help"],
            "daily": ["search"],
            "unknown": ["help"]
        }
    
    def build_params(self, intent_result, user_input: str, conversation_history: List = None) -> Dict[str, Any]:
        """构建简化的智能体参数
        
        Args:
            intent_result: 意图分析结果
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            简化的6字段参数字典
        """
        # 1. 风险等级评估
        risk_level = self._assess_risk_level(intent_result, user_input)
        
        # 2. 主体识别
        subject = self._identify_subject(intent_result, user_input)
        
        # 3. 核心意图 - 增强意图识别
        intent = self._identify_intent(intent_result, user_input)
        
        # 4. 响应语调
        tone = self._determine_tone(risk_level, intent, intent_result)
        
        # 5. 工具组合
        tools = self._recommend_tools(intent, risk_level, intent_result)
        
        # 6. 关键上下文
        context = self._extract_key_context(intent_result, user_input, conversation_history)
        
        params = {
            "risk": risk_level,
            "subject": subject,
            "intent": intent,
            "tone": tone,
            "tools": tools,
            "context": context
        }
        
        return params
    
    def _identify_intent(self, intent_result, user_input: str) -> str:
        """增强的意图识别"""
        # 从意图结果获取意图
        if hasattr(intent_result, 'intent') and intent_result.intent != 'unknown':
            return intent_result.intent
        
        # 基于关键词的意图识别
        user_lower = user_input.lower()
        
        # 海王相关
        seaking_keywords = ["撩妹", "话术", "撩", "泡妞", "约会", "聊天技巧", "怎么追"]
        if any(keyword in user_lower for keyword in seaking_keywords):
            return "seaking"
        
        # 风险相关
        risk_keywords = ["威胁", "家暴", "被骗", "勒索", "报复", "散布"]
        if any(keyword in user_lower for keyword in risk_keywords):
            return "risk"
        
        # 情感相关
        romance_keywords = ["男朋友", "女朋友", "对象", "分手", "复合", "冷暴力", "pua", "被pua", "渣男", "绿茶"]
        if any(keyword in user_lower for keyword in romance_keywords):
            return "romance"
        
        # 日常相关
        daily_keywords = ["天气", "股市", "新闻", "电影", "美食", "工作"]
        if any(keyword in user_lower for keyword in daily_keywords):
            return "daily"
        
        # 求助信号
        help_keywords = ["怎么办", "该不该", "要不要", "如何", "怎么做", "求助", "帮忙"]
        if any(keyword in user_lower for keyword in help_keywords):
            # 根据上下文确定具体意图
            if any(keyword in user_lower for keyword in romance_keywords):
                return "romance"
            elif any(keyword in user_lower for keyword in risk_keywords):
                return "risk"
        
        return "unknown"
    
    def _assess_risk_level(self, intent_result, user_input: str) -> str:
        """评估风险等级"""
        # 从意图结果获取风险等级
        if hasattr(intent_result, 'risk_level'):
            return intent_result.risk_level
        
        # 强化的关键词风险评估
        user_lower = user_input.lower()
        
        high_risk_keywords = ["威胁", "家暴", "自杀", "裸聊", "勒索", "暴力", "未成年", "散布", "隐私"]
        medium_risk_keywords = ["转账", "被骗", "胁迫", "报复", "冷暴力", "pua", "被pua"]
        low_risk_keywords = ["情感操控", "煤气灯", "打压", "控制"]
        
        if any(keyword in user_lower for keyword in high_risk_keywords):
            return "high"
        elif any(keyword in user_lower for keyword in medium_risk_keywords):
            return "medium"
        elif any(keyword in user_lower for keyword in low_risk_keywords):
            return "low"
        else:
            return "none"
    
    def _identify_subject(self, intent_result, user_input: str) -> str:
        """识别谈论主体"""
        # 从意图结果获取主体
        if hasattr(intent_result, 'subject'):
            return intent_result.subject
        
        # 强化的主体识别
        user_lower = user_input.lower()
        
        # 自己相关的指示词
        self_indicators = ["我", "自己", "我的", "我们", "他对我", "她对我", "男朋友", "女朋友", "对象"]
        # 他人相关的指示词
        other_indicators = ["朋友", "同事", "别人", "她的", "他的", "室友", "同学", "朋友的"]
        
        self_score = sum(1 for indicator in self_indicators if indicator in user_lower)
        other_score = sum(1 for indicator in other_indicators if indicator in user_lower)
        
        if self_score > other_score:
            return "self"
        elif other_score > self_score:
            return "other"
        else:
            return "unknown"
    
    def _determine_tone(self, risk_level: str, intent: str, intent_result) -> str:
        """确定响应语调"""
        # 基于风险等级的语调映射
        base_tone = self.tone_mapping.get(risk_level, "neutral")
        
        # 特殊意图的语调调整
        if intent == "seaking" and risk_level == "none":
            return "neutral"  # 海王练习保持中性
        elif intent == "romance" and hasattr(intent_result, 'help_seeking') and intent_result.help_seeking:
            return "supportive"  # 情感求助使用支持性语调
        
        return base_tone
    
    def _recommend_tools(self, intent: str, risk_level: str, intent_result) -> List[str]:
        """推荐工具组合"""
        # 基础工具映射
        base_tools = self.intent_tools.get(intent, ["help"])
        
        # 根据风险等级调整工具组合
        if risk_level in ["medium", "high"]:
            # 中高风险情况，优先使用severity和help
            if "severity" not in base_tools:
                base_tools = ["severity", "help"]
        
        # 特殊组合逻辑
        if intent == "romance" and risk_level != "none":
            # 情感问题有风险时，组合使用roast和help
            return ["roast", "help"]
        elif intent == "seaking" and risk_level != "none":
            # 海王相关有风险时，转为帮助模式
            return ["help"]
        
        return base_tools
    
    def _extract_key_context(self, intent_result, user_input: str, conversation_history: List = None) -> str:
        """提取关键上下文信息"""
        context_parts = []
        
        # 1. 关键特征摘要
        if hasattr(intent_result, 'matched_features') and intent_result.matched_features:
            key_features = []
            for category, data in intent_result.matched_features.items():
                if isinstance(data, dict) and data.get('matches'):
                    key_features.extend(data['matches'][:2])  # 每类最多2个关键词
            
            if key_features:
                context_parts.append(f"关键词: {', '.join(key_features[:4])}")  # 最多4个关键词
        
        # 2. 情感状态
        emotion_keywords = ["焦虑", "担心", "害怕", "生气", "难过", "开心", "紧张", "失望"]
        detected_emotions = [word for word in emotion_keywords if word in user_input]
        if detected_emotions:
            context_parts.append(f"情感: {', '.join(detected_emotions[:2])}")
        
        # 3. 求助信号
        if hasattr(intent_result, 'help_seeking') and intent_result.help_seeking:
            context_parts.append("求助信号明确")
        
        # 4. 对话轮次
        if conversation_history and len(conversation_history) > 0:
            context_parts.append(f"多轮对话({len(conversation_history)}轮)")
        
        # 5. 置信度信息
        if hasattr(intent_result, 'confidence'):
            confidence = intent_result.confidence
            if confidence >= 0.8:
                context_parts.append("高置信度")
            elif confidence <= 0.5:
                context_parts.append("低置信度")
        
        return " | ".join(context_parts) if context_parts else "标准对话"
    
    def format_for_agent(self, params: Dict[str, Any]) -> str:
        """将参数格式化为智能体可读的简洁字符串"""
        return json.dumps(params, ensure_ascii=False, separators=(',', ':'))
    
    def create_agent_prompt_context(self, params: Dict[str, Any]) -> str:
        """创建智能体提示词上下文"""
        risk_desc = {
            "none": "无风险",
            "low": "低风险", 
            "medium": "中等风险",
            "high": "高风险"
        }
        
        subject_desc = {
            "self": "用户自身情况",
            "other": "他人情况",
            "unknown": "主体不明"
        }
        
        tone_desc = {
            "supportive": "支持性回应",
            "neutral": "中性回应", 
            "cautious": "谨慎回应",
            "urgent": "紧急回应"
        }
        
        context_lines = [
            f"风险等级: {risk_desc.get(params['risk'], params['risk'])}",
            f"讨论主体: {subject_desc.get(params['subject'], params['subject'])}",
            f"核心意图: {params['intent']}",
            f"建议语调: {tone_desc.get(params['tone'], params['tone'])}",
            f"推荐工具: {', '.join(params['tools'])}",
            f"关键上下文: {params['context']}"
        ]
        
        return "\n".join(context_lines)

# 使用示例
def create_simplified_params(intent_result, user_input: str, conversation_history: List = None) -> Dict[str, Any]:
    """创建简化的智能体参数的便捷函数"""
    builder = SimplifiedAgentParameterBuilder()
    return builder.build_params(intent_result, user_input, conversation_history)
