#!/usr/bin/env python3
"""
双层路由系统 - 短路直达 + 智能参考
"""

import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from collections import Counter

@dataclass
class ShortcutResult:
    """短路规则结果"""
    rule_name: str
    matched: bool
    tools: List[str]
    confidence: float = 1.0
    bypass_agent: bool = True
    context_aware: bool = False  # 新增：是否需要上下文连贯性

@dataclass
class ReferenceSignal:
    """智能参考信号"""
    risk_level: str  # none/low/medium/high
    romance_context: Dict
    help_intent: bool
    emotion_intensity: float
    matched_keywords: Dict
    suggested_tools: List[str]
    confidence_factors: Dict

@dataclass
class DualRoutingResult:
    """双层路由结果"""
    routing_type: str  # shortcut|reference|fallback
    shortcut_result: Optional[ShortcutResult] = None
    reference_signal: Optional[ReferenceSignal] = None
    final_tools: List[str] = None
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    debug_info: Dict = None

class DualLayerRouter:
    """双层路由器：短路直达 + 智能参考"""
    
    def __init__(self):
        self._load_keyword_sets()
        self._load_shortcut_rules()
        self._load_reference_patterns()
    
    def _load_keyword_sets(self):
        """加载关键词集合"""
        self.keywords = {
            # === 第一层：短路规则关键词 ===
            "seaking_words": ["海王", "话术", "撩妹", "撩人", "pua技巧", "恋爱技巧", "撩", "泡妞"],
            "action_words": ["练习", "模拟", "对战", "生成", "教我", "训练", "演练", "来一套", "给我", "学习", "想学", "如何", "怎么"],
            "seaking_intent": ["成为海王", "当海王", "海王高手", "撩妹高手", "恋爱大师", "撩妹大师", "成为撩妹", "当撩妹"],
            "help_words": ["怎么办", "该不该", "要不要", "如何", "怎么做", "求助", "帮忙"],
            "high_risk_words": ["威胁", "家暴", "打我", "自杀", "裸聊", "勒索", "暴力", "殴打", "跟踪", "下药", "未成年", "冷暴力"],
            "daily_clear": ["天气", "电影", "美食", "编程", "旅游", "明星", "游戏"],
            
            # === 第二层：参考信号关键词 ===
            "medium_risk": ["控制", "被骗", "散布", "报复", "胁迫"],
            "romance_self": ["男朋友", "女朋友", "对象", "我的", "我们", "他对我", "她对我"],
            "romance_other": ["朋友的", "别人的", "同事的", "她的男朋友", "他的女朋友", "室友", "闺蜜"],
            "romance_behaviors": ["已读不回", "出轨", "分手", "复合", "暧昧", "备胎", "劈腿", "背叛"],
            "negative_emotions": ["生气", "难过", "失望", "痛苦", "绝望", "愤怒", "烦", "恶心", "渣"],
            "workplace": ["同事", "老板", "领导", "加班", "工作", "职场", "公司", "上司"],
        }
    
    def _load_shortcut_rules(self):
        """加载短路规则（绝对确定性，但保持对话连贯性）"""
        self.shortcut_rules = {
            "显性海王模拟": {
                "priority": 2,
                "condition": self._check_seaking_practice,
                "tools": ["seaking_tool"],
                "context_aware": True,  # 需要考虑上下文
                "description": "明确的海王话术练习需求"
            },
            
            "显性高风险": {
                "priority": 1,  # 最高优先级
                "condition": self._check_high_risk,
                "tools": ["severity_analyzer", "search_tool", "help_tool"],  # 组合调用
                "context_aware": True,  # 高风险需要上下文分析
                "description": "高风险情况，需要综合分析"
            },
            
            "显性非恋爱求助": {
                "priority": 3,
                "condition": self._check_pure_help,
                "tools": ["help_tool"],
                "context_aware": False,  # 简单求助可直达
                "description": "纯粹的非恋爱求助"
            },
            
            "显性他人恋爱毒舌": {
                "priority": 4,
                "condition": self._check_other_romance_roast,
                "tools": ["roast_tool"],
                "context_aware": False,  # 他人恋爱可直达毒舌
                "description": "明确的他人恋爱吐槽"
            },
            
            "显性自己恋爱行为": {
                "priority": 3,
                "condition": self._check_self_romance_behavior,
                "tools": ["severity_analyzer", "roast_tool"],  # 组合调用：先分析再毒舌
                "context_aware": True,  # 自己的情感问题需要上下文
                "description": "自己的恋爱行为问题，需要分析"
            },
            
            "显性日常聊天": {
                "priority": 5,
                "condition": self._check_daily_chat,
                "tools": ["talk_tool"],
                "context_aware": False,  # 日常聊天可直达
                "description": "明确的日常话题"
            }
        }
    
    def _load_reference_patterns(self):
        """加载参考信号模式"""
        self.reference_patterns = {
            "multi_intent": "检测到多重意图",
            "ambiguous_risk": "模糊风险信号", 
            "complex_romance": "复杂恋爱情况",
            "emotional_support": "需要情感支持",
            "workplace_issue": "职场相关问题"
        }
    
    def route(self, text: str, context: Dict = None) -> DualRoutingResult:
        """主路由接口"""
        import time
        start_time = time.time()
        
        context = context or {}
        text_lower = text.lower()
        
        # 第一层：尝试短路规则
        shortcut_result = self._try_shortcut_rules(text, text_lower, context)
        
        if shortcut_result and shortcut_result.matched:
            processing_time = (time.time() - start_time) * 1000
            
            # 根据context_aware决定是否完全绕过Agent
            if shortcut_result.context_aware:
                # 需要上下文的情况：提供强烈建议但不完全绕过
                routing_type = "shortcut_with_context"
                confidence = 0.9  # 高置信度但不是绝对
            else:
                # 简单情况：可以直接绕过
                routing_type = "shortcut"
                confidence = 1.0
            
            return DualRoutingResult(
                routing_type=routing_type,
                shortcut_result=shortcut_result,
                final_tools=shortcut_result.tools,
                confidence=confidence,
                processing_time_ms=processing_time,
                debug_info={
                    "rule": shortcut_result.rule_name,
                    "context_aware": shortcut_result.context_aware,
                    "tool_combination": len(shortcut_result.tools) > 1
                }
            )
        
        # 第二层：生成参考信号
        reference_signal = self._generate_reference_signal(text, text_lower, context)
        
        if reference_signal:
            processing_time = (time.time() - start_time) * 1000
            return DualRoutingResult(
                routing_type="reference",
                reference_signal=reference_signal,
                final_tools=reference_signal.suggested_tools,
                confidence=0.6,  # 中等置信度，需要Agent确认
                processing_time_ms=processing_time,
                debug_info={"signals": list(reference_signal.confidence_factors.keys())}
            )
        
        # 兜底：完全交给Agent
        processing_time = (time.time() - start_time) * 1000
        return DualRoutingResult(
            routing_type="fallback",
            final_tools=["original_agent"],
            confidence=0.3,
            processing_time_ms=processing_time,
            debug_info={"reason": "no_clear_pattern"}
        )
    
    def _try_shortcut_rules(self, text: str, text_lower: str, context: Dict) -> Optional[ShortcutResult]:
        """尝试短路规则"""
        # 按优先级排序
        sorted_rules = sorted(
            self.shortcut_rules.items(), 
            key=lambda x: x[1]["priority"]
        )
        
        for rule_name, rule_config in sorted_rules:
            condition_func = rule_config["condition"]
            if condition_func(text, text_lower, context):
                return ShortcutResult(
                    rule_name=rule_name,
                    matched=True,
                    tools=rule_config["tools"],
                    confidence=1.0,
                    bypass_agent=not rule_config.get("context_aware", False),  # context_aware的不完全绕过
                    context_aware=rule_config.get("context_aware", False)
                )
        
        return None
    
    # === 短路规则条件检查函数 ===
    
    def _check_seaking_practice(self, text: str, text_lower: str, context: Dict) -> bool:
        """检查：显性海王模拟"""
        # 直接海王意图词检测
        if any(intent in text_lower for intent in self.keywords["seaking_intent"]):
            return True
            
        has_seaking = any(word in text_lower for word in self.keywords["seaking_words"])
        has_action = any(word in text_lower for word in self.keywords["action_words"])
        
        # 排除求助语境
        has_help = any(word in text_lower for word in self.keywords["help_words"])
        has_negative = any(word in text_lower for word in ["被", "防", "识别", "反pua", "止损"])
        
        return has_seaking and has_action and not has_help and not has_negative
    
    def _check_high_risk(self, text: str, text_lower: str, context: Dict) -> bool:
        """检查：显性高风险（组合调用severity_analyzer+search+help）"""
        return any(word in text_lower for word in self.keywords["high_risk_words"])
    
    def _check_pure_help(self, text: str, text_lower: str, context: Dict) -> bool:
        """检查：显性非恋爱求助"""
        has_help = any(word in text_lower for word in self.keywords["help_words"])
        
        # 完全不含恋爱相关词
        romance_words = (self.keywords["romance_self"] + 
                        self.keywords["romance_other"] + 
                        self.keywords["romance_behaviors"])
        has_romance = any(word in text_lower for word in romance_words)
        
        # 特殊处理：工作、学习、健身等明确非恋爱求助
        clear_help_topics = ["工作", "学习", "健身", "考试", "面试", "技能", "专业"]
        has_clear_help = any(topic in text_lower for topic in clear_help_topics)
        
        return (has_help and not has_romance) or has_clear_help
    
    def _check_other_romance_roast(self, text: str, text_lower: str, context: Dict) -> bool:
        """检查：显性他人恋爱毒舌"""
        has_other_romance = any(word in text_lower for word in self.keywords["romance_other"])
        has_negative_emotion = any(word in text_lower for word in self.keywords["negative_emotions"])
        has_romance_behavior = any(word in text_lower for word in self.keywords["romance_behaviors"])
        
        # 增加负面评价词汇
        negative_words = ["渣", "恶心", "垃圾", "烦人", "讨厌", "劈腿"]
        has_negative_comment = any(word in text_lower for word in negative_words)
        
        return has_other_romance and (has_negative_emotion or has_romance_behavior or has_negative_comment)
    
    def _check_self_romance_behavior(self, text: str, text_lower: str, context: Dict) -> bool:
        """检查：显性自己恋爱行为（组合调用severity_analyzer+roast）"""
        has_romance_self = any(word in text_lower for word in self.keywords["romance_self"])
        has_romance_behavior = any(word in text_lower for word in self.keywords["romance_behaviors"])
        
        # 自己的恋爱情况 + 行为描述
        return has_romance_self and has_romance_behavior
    
    def _check_daily_chat(self, text: str, text_lower: str, context: Dict) -> bool:
        """检查：显性日常聊天"""
        has_daily = any(word in text_lower for word in self.keywords["daily_clear"])
        
        # 不含求助、风险、恋爱等严肃语境
        serious_words = (self.keywords["help_words"] + 
                        self.keywords["high_risk_words"] + 
                        self.keywords["medium_risk"] +
                        self.keywords["romance_self"])
        has_serious = any(word in text_lower for word in serious_words)
        
        return has_daily and not has_serious
    
    def _generate_reference_signal(self, text: str, text_lower: str, context: Dict) -> Optional[ReferenceSignal]:
        """生成智能参考信号"""
        signals = {}
        confidence_factors = {}
        suggested_tools = []
        
        # 检测风险等级
        risk_level = "none"
        if any(word in text_lower for word in self.keywords["medium_risk"]):
            risk_level = "medium"
            signals["medium_risk"] = True
            confidence_factors["risk_detection"] = 0.7
        
        # 检测恋爱上下文
        romance_context = {"subject": "unknown", "behaviors": [], "emotions": []}
        
        if any(word in text_lower for word in self.keywords["romance_self"]):
            romance_context["subject"] = "self"
            signals["self_romance"] = True
            confidence_factors["romance_self"] = 0.8
        elif any(word in text_lower for word in self.keywords["romance_other"]):
            romance_context["subject"] = "other" 
            signals["other_romance"] = True
            confidence_factors["romance_other"] = 0.8
        
        # 检测行为和情绪
        for behavior in self.keywords["romance_behaviors"]:
            if behavior in text_lower:
                romance_context["behaviors"].append(behavior)
        
        for emotion in self.keywords["negative_emotions"]:
            if emotion in text_lower:
                romance_context["emotions"].append(emotion)
        
        # 检测求助意图
        help_intent = any(word in text_lower for word in self.keywords["help_words"])
        if help_intent:
            signals["help_seeking"] = True
            confidence_factors["help_intent"] = 0.9
        
        # 检测情绪强度
        emotion_intensity = len([e for e in self.keywords["negative_emotions"] if e in text_lower]) * 0.3
        emotion_intensity += text.count("！") * 0.2 + text.count("？") * 0.1
        emotion_intensity = min(1.0, emotion_intensity)
        
        # 检测职场相关
        workplace_detected = any(word in text_lower for word in self.keywords["workplace"])
        if workplace_detected:
            signals["workplace"] = True
            confidence_factors["workplace"] = 0.7
        
        # 决定建议工具
        if signals.get("medium_risk") and signals.get("self_romance"):
            suggested_tools = ["talk_tool", "help_tool"]  # 复杂情况
        elif signals.get("other_romance"):
            suggested_tools = ["roast_tool", "talk_tool"]  # 他人恋爱
        elif signals.get("workplace"):
            suggested_tools = ["talk_tool"]  # 职场问题
        elif signals.get("help_seeking"):
            suggested_tools = ["help_tool", "talk_tool"]  # 求助
        else:
            suggested_tools = ["talk_tool"]  # 默认聊天
        
        # 如果没有明确信号，返回None（走兜底）
        if not signals:
            return None
        
        return ReferenceSignal(
            risk_level=risk_level,
            romance_context=romance_context,
            help_intent=help_intent,
            emotion_intensity=emotion_intensity,
            matched_keywords=signals,
            suggested_tools=suggested_tools,
            confidence_factors=confidence_factors
        )
    
    def get_routing_stats(self) -> Dict:
        """获取路由统计信息"""
        return {
            "shortcut_rules": len(self.shortcut_rules),
            "reference_patterns": len(self.reference_patterns),
            "keyword_categories": len(self.keywords),
            "total_keywords": sum(len(words) for words in self.keywords.values())
        }
    
    def explain_routing(self, result: DualRoutingResult) -> Dict:
        """解释路由决策"""
        explanation = {
            "routing_type": result.routing_type,
            "confidence": result.confidence,
            "processing_time": f"{result.processing_time_ms:.1f}ms"
        }
        
        if result.routing_type in ["shortcut", "shortcut_with_context"]:
            explanation.update({
                "rule_triggered": result.shortcut_result.rule_name,
                "bypass_agent": result.shortcut_result.bypass_agent,
                "context_aware": result.shortcut_result.context_aware,
                "tools_called": result.shortcut_result.tools,
                "tool_combination": len(result.shortcut_result.tools) > 1,
                "explanation": self._get_rule_explanation(result.shortcut_result.rule_name)
            })
        elif result.routing_type == "reference":
            explanation.update({
                "signals_detected": list(result.reference_signal.matched_keywords.keys()),
                "risk_level": result.reference_signal.risk_level,
                "help_intent": result.reference_signal.help_intent,
                "suggested_tools": result.reference_signal.suggested_tools,
                "agent_decision_needed": True
            })
        else:
            explanation.update({
                "reason": "no_clear_pattern_detected",
                "fallback_to": "original_agent"
            })
        
        return explanation
    
    def _get_rule_explanation(self, rule_name: str) -> str:
        """获取规则解释"""
        explanations = {
            "显性海王模拟": "检测到明确的海王话术练习需求，但会考虑对话上下文",
            "显性高风险": "检测到高风险情况，将组合调用风险分析、搜索和帮助工具",
            "显性非恋爱求助": "检测到非恋爱相关的求助，直接提供帮助",
            "显性他人恋爱毒舌": "检测到他人恋爱问题的吐槽，直接进行毒舌",
            "显性自己恋爱行为": "检测到自己的恋爱行为问题，将先分析再毒舌",
            "显性日常聊天": "检测到日常话题，直接进行聊天"
        }
        return explanations.get(rule_name, "未知规则")
