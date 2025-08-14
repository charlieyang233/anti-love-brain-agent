#!/usr/bin/env python3
"""
增强Agent参数传递器
为Agent提供结构化、丰富的意图分析信息
"""

from typing import Dict, Any, List, Optional
from dataclasses import asdict
import time

class EnhancedAgentParameterBuilder:
    """增强Agent参数构建器"""
    
    def __init__(self, dual_router, memory_manager):
        self.dual_router = dual_router
        self.memory_manager = memory_manager
        
    def build_agent_parameters(self, user_input: str, dual_result, context: Dict = None) -> Dict[str, Any]:
        """构建完整的Agent参数"""
        
        return {
            "intent_analysis": self._build_intent_analysis(dual_result),
            "content_analysis": self._build_content_analysis(user_input, dual_result),
            "context_signals": self._build_context_signals(dual_result),
            "agent_guidance": self._build_agent_guidance(dual_result),
            "memory_context": self._build_memory_context(),
            "technical_meta": self._build_technical_meta(dual_result),
            "user_input": user_input,
            "timestamp": time.time()
        }
    
    def _build_intent_analysis(self, dual_result) -> Dict[str, Any]:
        """构建意图分析信息"""
        return {
            "routing_path": dual_result.routing_type,
            "confidence": dual_result.confidence,
            "processing_time_ms": dual_result.processing_time_ms,
            "rule_triggered": dual_result.shortcut_result.rule_name if dual_result.shortcut_result else None,
            "context_aware": dual_result.shortcut_result.context_aware if dual_result.shortcut_result else False,
            "bypass_agent": dual_result.shortcut_result.bypass_agent if dual_result.shortcut_result else None
        }
    
    def _build_content_analysis(self, user_input: str, dual_result) -> Dict[str, Any]:
        """构建内容分析信息"""
        matched_keywords = {}
        keyword_coverage = 0.0
        
        if dual_result.reference_signal:
            # 从参考信号提取匹配的关键词
            signal = dual_result.reference_signal
            matched_keywords = self._extract_matched_keywords(user_input, signal)
            keyword_coverage = len([k for v in matched_keywords.values() for k in v]) / len(user_input.split())
        
        return {
            "matched_keywords": matched_keywords,
            "keyword_coverage": min(1.0, keyword_coverage),
            "text_complexity": self._assess_text_complexity(user_input),
            "text_length": len(user_input),
            "question_marks": user_input.count("？") + user_input.count("?"),
            "exclamation_marks": user_input.count("！") + user_input.count("!")
        }
    
    def _build_context_signals(self, dual_result) -> Dict[str, Any]:
        """构建上下文信号信息"""
        if dual_result.reference_signal:
            signal = dual_result.reference_signal
            return {
                "risk_level": signal.risk_level,
                "romance_context": signal.romance_context,
                "help_intent": signal.help_intent,
                "emotion_intensity": signal.emotion_intensity,
                "matched_patterns": list(signal.matched_keywords.keys()),
                "confidence_factors": signal.confidence_factors
            }
        else:
            return {
                "risk_level": "none",
                "romance_context": {"subject": "unknown", "behaviors": [], "emotions": []},
                "help_intent": False,
                "emotion_intensity": 0.0,
                "matched_patterns": [],
                "confidence_factors": {}
            }
    
    def _build_agent_guidance(self, dual_result) -> Dict[str, Any]:
        """构建Agent指导信息"""
        guidance = {
            "suggested_tools": dual_result.final_tools or [],
            "reasoning": self._generate_reasoning(dual_result),
            "priority_aspects": self._get_priority_aspects(dual_result),
            "avoid_aspects": self._get_avoid_aspects(dual_result),
            "response_tone": self._suggest_response_tone(dual_result),
            "safety_level": self._assess_safety_level(dual_result)
        }
        
        return guidance
    
    def _build_memory_context(self) -> Dict[str, Any]:
        """构建记忆上下文信息"""
        try:
            recent_context = self.memory_manager.get_recent_context(limit=5)
            recent_topics = []
            emotional_indicators = []
            
            for interaction in recent_context:
                if hasattr(interaction, 'user_input'):
                    # 提取话题关键词
                    topics = self._extract_topics(interaction.user_input)
                    recent_topics.extend(topics)
                    
                    # 提取情绪指标
                    emotion = self._detect_emotion(interaction.user_input)
                    if emotion:
                        emotional_indicators.append(emotion)
            
            return {
                "recent_topics": list(set(recent_topics))[:5],  # 去重并限制数量
                "user_emotional_state": self._summarize_emotional_state(emotional_indicators),
                "conversation_flow": self._analyze_conversation_flow(recent_context),
                "context_continuity": len(recent_context) > 0
            }
        except:
            return {
                "recent_topics": [],
                "user_emotional_state": "unknown",
                "conversation_flow": "new_conversation",
                "context_continuity": False
            }
    
    def _build_technical_meta(self, dual_result) -> Dict[str, Any]:
        """构建技术元数据"""
        return {
            "router_version": "dual_layer_v2_enhanced",
            "fallback_reason": self._get_fallback_reason(dual_result),
            "performance_stats": {
                "token_saved": dual_result.routing_type in ["shortcut", "shortcut_with_context"],
                "routing_efficiency": self._calculate_routing_efficiency(dual_result),
                "optimization_level": self._get_optimization_level(dual_result)
            },
            "debug_info": dual_result.debug_info or {}
        }
    
    # === 辅助方法 ===
    
    def _extract_matched_keywords(self, user_input: str, signal) -> Dict[str, List[str]]:
        """提取匹配的关键词详情"""
        matched = {}
        user_lower = user_input.lower()
        
        # 检查各类关键词
        for category, keywords in self.dual_router.keywords.items():
            found_keywords = [kw for kw in keywords if kw in user_lower]
            if found_keywords:
                matched[category] = found_keywords
        
        return matched
    
    def _assess_text_complexity(self, text: str) -> str:
        """评估文本复杂度"""
        length = len(text)
        word_count = len(text.split())
        
        if length < 10 or word_count < 3:
            return "simple"
        elif length < 50 or word_count < 10:
            return "medium"
        else:
            return "complex"
    
    def _generate_reasoning(self, dual_result) -> str:
        """生成推理说明"""
        if dual_result.routing_type == "shortcut":
            return f"明确匹配到规则: {dual_result.shortcut_result.rule_name}，可直接处理"
        elif dual_result.routing_type == "shortcut_with_context":
            return f"匹配到规则: {dual_result.shortcut_result.rule_name}，但需要考虑对话上下文"
        elif dual_result.routing_type == "reference":
            risk = dual_result.reference_signal.risk_level
            return f"检测到{risk}风险等级的复杂情况，需要智能分析处理"
        else:
            return "无明确模式匹配，需要通用Agent处理"
    
    def _get_priority_aspects(self, dual_result) -> List[str]:
        """获取优先处理方面"""
        if not dual_result.reference_signal:
            return ["通用对话处理"]
        
        aspects = []
        signal = dual_result.reference_signal
        
        if signal.risk_level in ["medium", "high"]:
            aspects.append("风险评估")
        if signal.help_intent:
            aspects.append("情感支持")
        if signal.romance_context.get("subject") == "self":
            aspects.append("自我保护意识")
        if signal.emotion_intensity > 0.5:
            aspects.append("情绪疏导")
        
        return aspects or ["理解用户需求"]
    
    def _get_avoid_aspects(self, dual_result) -> List[str]:
        """获取应避免的方面"""
        if not dual_result.reference_signal:
            return []
        
        avoid = []
        signal = dual_result.reference_signal
        
        if signal.risk_level == "high":
            avoid.extend(["轻视风险", "提供危险建议"])
        if signal.romance_context.get("subject") == "self":
            avoid.append("直接建议分手")
        if signal.emotion_intensity > 0.7:
            avoid.append("过于理性的分析")
        
        return avoid
    
    def _suggest_response_tone(self, dual_result) -> str:
        """建议回应语调"""
        if not dual_result.reference_signal:
            return "friendly"
        
        signal = dual_result.reference_signal
        
        if signal.risk_level == "high":
            return "serious_supportive"
        elif signal.risk_level == "medium":
            return "caring_cautious"
        elif signal.help_intent:
            return "warm_helpful"
        elif signal.emotion_intensity > 0.5:
            return "empathetic"
        else:
            return "friendly"
    
    def _assess_safety_level(self, dual_result) -> str:
        """评估安全级别"""
        if not dual_result.reference_signal:
            return "safe"
        
        risk = dual_result.reference_signal.risk_level
        return {"none": "safe", "low": "caution", "medium": "alert", "high": "critical"}.get(risk, "safe")
    
    def _extract_topics(self, text: str) -> List[str]:
        """提取话题关键词"""
        # 简单的话题提取逻辑
        common_topics = ["工作", "学习", "感情", "家庭", "朋友", "健康", "压力", "心情"]
        return [topic for topic in common_topics if topic in text]
    
    def _detect_emotion(self, text: str) -> Optional[str]:
        """检测情绪"""
        positive_words = ["开心", "高兴", "快乐", "满意"]
        negative_words = ["难过", "生气", "烦躁", "压力", "累"]
        
        if any(word in text for word in positive_words):
            return "positive"
        elif any(word in text for word in negative_words):
            return "negative"
        return None
    
    def _summarize_emotional_state(self, emotions: List[str]) -> str:
        """总结情绪状态"""
        if not emotions:
            return "neutral"
        
        positive_count = emotions.count("positive")
        negative_count = emotions.count("negative")
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "mixed"
    
    def _analyze_conversation_flow(self, context: List) -> str:
        """分析对话流程"""
        if not context:
            return "new_conversation"
        elif len(context) == 1:
            return "initial_inquiry"
        elif len(context) < 5:
            return "developing_discussion"
        else:
            return "extended_conversation"
    
    def _get_fallback_reason(self, dual_result) -> Optional[str]:
        """获取兜底原因"""
        if dual_result.routing_type == "fallback":
            return dual_result.debug_info.get("reason", "no_clear_pattern")
        return None
    
    def _calculate_routing_efficiency(self, dual_result) -> float:
        """计算路由效率"""
        efficiency_map = {
            "shortcut": 1.0,
            "shortcut_with_context": 0.9,
            "reference": 0.7,
            "fallback": 0.3
        }
        return efficiency_map.get(dual_result.routing_type, 0.3)
    
    def _get_optimization_level(self, dual_result) -> str:
        """获取优化级别"""
        if dual_result.routing_type in ["shortcut", "shortcut_with_context"]:
            return "high"
        elif dual_result.routing_type == "reference":
            return "medium"
        else:
            return "low"
