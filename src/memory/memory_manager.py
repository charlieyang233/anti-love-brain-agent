from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any
import json
import re

class SmartMemoryManager:
    """智能记忆管理器 - 支持动态窗口、智能压缩和分级存储"""
    
    def __init__(self, max_tokens: int = 1500, summary_trigger_ratio: float = 0.8):
        """
        初始化智能记忆管理器
        
        Args:
            max_tokens: 最大token限制
            summary_trigger_ratio: 触发压缩的阈值比例
        """
        self.max_tokens = max_tokens
        self.summary_trigger_ratio = summary_trigger_ratio
        self.conversation_count = 0
        self.compression_count = 0
        
        # 动态窗口记忆 - 初始窗口大小
        self.current_window_size = 8
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=self.current_window_size,
            ai_prefix="拽姐",
            human_prefix="用户",
            output_key="output"
        )
        
        # 分级记忆存储
        self.long_term_memory = {
            "user_patterns": {},      # 用户行为模式
            "risk_history": [],       # 风险等级历史（最近20条）
            "key_insights": [],       # 关键洞察（最近10条）
            "persona_preferences": {}, # 海王模拟偏好
            "compressed_summaries": [] # 压缩摘要历史
        }
        
        # 记忆压缩配置
        self.compression_config = {
            "max_risk_history": 20,
            "max_key_insights": 10,
            "max_summaries": 5,
            "compression_threshold": 0.2  # 20%时触发压缩，更早开始压缩
        }

    def add_interaction(self, user_input: str, ai_response: str, 
                       love_brain_level: str = None, risk_signals: List[str] = None):
        """添加一轮对话到记忆中"""
        self.conversation_count += 1
        
        # 添加到短期记忆
        self.memory.save_context(
            {"input": user_input},
            {"output": ai_response}
        )
        
        # 更新长期记忆
        self._update_long_term_memory(user_input, ai_response, love_brain_level, risk_signals)
        
        # 检查是否需要智能压缩
        self._smart_compression_check()

    def _smart_compression_check(self):
        """智能压缩检查"""
        current_tokens = self._estimate_token_count()
        usage_ratio = current_tokens / self.max_tokens
        
        if usage_ratio > self.compression_config["compression_threshold"]:
            self._compress_memory()
            self.compression_count += 1

    def _compress_memory(self):
        """智能记忆压缩"""
        try:
            # 1. 压缩短期记忆窗口
            if self.current_window_size > 4:
                self.current_window_size = max(4, self.current_window_size - 2)
                # 重新创建memory实例
                old_messages = self.memory.chat_memory.messages
                self.memory = ConversationBufferWindowMemory(
                    memory_key="chat_history",
                    return_messages=True,
                    k=self.current_window_size,
                    ai_prefix="拽姐",
                    human_prefix="用户",
                    output_key="output"
                )
                # 保留最近的消息
                for msg in old_messages[-self.current_window_size*2:]:
                    if hasattr(msg, 'content'):
                        self.memory.chat_memory.add_message(msg)
            
            # 2. 生成压缩摘要
            if len(self.memory.chat_memory.messages) > 6:
                summary = self._generate_compression_summary()
                if summary:
                    self.long_term_memory["compressed_summaries"].append({
                        "round": self.conversation_count,
                        "summary": summary,
                        "window_size": self.current_window_size
                    })
                    # 限制摘要数量
                    if len(self.long_term_memory["compressed_summaries"]) > self.compression_config["max_summaries"]:
                        self.long_term_memory["compressed_summaries"] = self.long_term_memory["compressed_summaries"][-self.compression_config["max_summaries"]:]
            
            # 3. 维护长期记忆大小
            self._maintain_long_term_memory()
            
            print(f"✅ 记忆压缩完成 - 窗口大小: {self.current_window_size}, 压缩次数: {self.compression_count}")
            
        except Exception as e:
            print(f"⚠️ 记忆压缩失败: {e}")

    def _generate_compression_summary(self) -> str:
        """生成压缩摘要 - 极简版本，避免重复"""
        try:
            messages = self.memory.chat_memory.messages
            if len(messages) < 4:
                return ""
            
            # 只提取最近1轮对话的核心信息
            recent_user_input = ""
            recent_ai_response = ""
            
            # 从后往前找最近一轮对话
            for i in range(len(messages) - 1, 0, -2):
                if i > 0:
                    ai_msg = messages[i] if hasattr(messages[i], 'content') else None
                    user_msg = messages[i-1] if hasattr(messages[i-1], 'content') else None
                    
                    if user_msg and ai_msg:
                        user_content = str(user_msg.content).strip()
                        ai_content = str(ai_msg.content).strip()
                        
                        # 过滤系统信息
                        if not any(keyword in user_content for keyword in ["记忆上下文", "当前状态", "历史摘要"]):
                            recent_user_input = user_content[:50]  # 大幅缩短
                        if not any(keyword in ai_content for keyword in ["记忆上下文", "当前状态", "历史摘要"]):
                            recent_ai_response = ai_content[:50]  # 大幅缩短
                        break
            
            # 生成极简摘要
            summary_parts = []
            if recent_user_input:
                summary_parts.append(f"用户: {recent_user_input}...")
            if recent_ai_response:
                summary_parts.append(f"AI: {recent_ai_response}...")
            
            result = " | ".join(summary_parts)
            
            # 严格控制长度
            if len(result) > 120:  # 大幅减少长度限制
                result = result[:117] + "..."
            
            return result
            
        except Exception as e:
            print(f"⚠️ 生成压缩摘要失败: {e}")
            return ""

    def _maintain_long_term_memory(self):
        """维护长期记忆大小"""
        # 风险历史保持最近N条
        if len(self.long_term_memory["risk_history"]) > self.compression_config["max_risk_history"]:
            self.long_term_memory["risk_history"] = self.long_term_memory["risk_history"][-self.compression_config["max_risk_history"]:]
        
        # 关键洞察保持最近N条
        if len(self.long_term_memory["key_insights"]) > self.compression_config["max_key_insights"]:
            self.long_term_memory["key_insights"] = self.long_term_memory["key_insights"][-self.compression_config["max_key_insights"]:]

    def _update_long_term_memory(self, user_input: str, ai_response: str, 
                                love_brain_level: str = None, risk_signals: List[str] = None):
        """更新长期记忆中的关键信息"""
        
        # 记录风险等级历史
        if love_brain_level:
            self.long_term_memory["risk_history"].append({
                "round": self.conversation_count,
                "level": love_brain_level,
                "signals": risk_signals or []
            })

        # 检测用户恋爱模式
        self._detect_user_patterns(user_input, love_brain_level)
        
        # 提取关键洞察
        if love_brain_level in ["重", "危"]:
            insight = f"第{self.conversation_count}轮：{love_brain_level}级风险 - {user_input[:50]}..."
            self.long_term_memory["key_insights"].append(insight)

    def _detect_user_patterns(self, user_input: str, love_brain_level: str):
        """检测用户恋爱行为模式"""
        patterns = self.long_term_memory["user_patterns"]
        
        # 关键词检测
        pattern_keywords = {
            "金钱依赖": ["转账", "借钱", "投资", "买单", "花钱", "钱", "经济"],
            "情绪依赖": ["想念", "焦虑", "失眠", "心情", "情绪", "难过", "伤心", "痛苦"],
            "社交隔离": ["朋友", "家人", "同事", "社交", "联系", "孤立", "孤独"],
            "时间沉迷": ["整天", "一直", "24小时", "不停", "总是", "时刻", "每时每刻"],
            "自我怀疑": ["我是不是", "我配吗", "我错了", "我不够好", "自卑"],
            "过度理想化": ["完美", "理想", "童话", "王子", "公主", "命中注定"],
            "控制欲": ["管我", "限制", "不允许", "必须", "应该", "要求"]
        }
        
        for pattern_type, keywords in pattern_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                if pattern_type not in patterns:
                    patterns[pattern_type] = 0
                patterns[pattern_type] += 1

    def _estimate_token_count(self) -> int:
        """更准确的token数量估算"""
        try:
            # 获取当前缓冲区内容
            buffer_messages = self.memory.chat_memory.messages
            total_tokens = 0
            
            for msg in buffer_messages:
                if hasattr(msg, 'content'):
                    content = str(msg.content)
                    # 更准确的token估算
                    tokens = self._count_tokens_accurately(content)
                    total_tokens += tokens
            
            # 加上长期记忆的token估算
            long_term_tokens = self._estimate_long_term_tokens()
            
            return total_tokens + long_term_tokens
            
        except Exception as e:
            print(f"⚠️ Token估算失败: {e}")
            return 0

    def _count_tokens_accurately(self, text: str) -> int:
        """更准确的token计算"""
        if not text:
            return 0
        
        # 中文字符（包括标点）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))
        
        # 英文字符和数字
        english_chars = len(re.findall(r'[a-zA-Z0-9]', text))
        
        # 空格和标点
        spaces_punct = len(re.findall(r'[\s\.,!?;:()\[\]{}"\'-]', text))
        
        # GPT-4的token估算规则
        # 中文：约1.5个字符 = 1个token
        # 英文：约4个字符 = 1个token
        # 标点符号：约1个字符 = 1个token
        
        chinese_tokens = int(chinese_chars / 1.5)
        english_tokens = int(english_chars / 4)
        punct_tokens = spaces_punct
        
        return chinese_tokens + english_tokens + punct_tokens

    def _estimate_long_term_tokens(self) -> int:
        """估算长期记忆的token数量"""
        long_term_tokens = 0
        
        # 用户模式
        patterns = self.long_term_memory["user_patterns"]
        if patterns:
            patterns_text = json.dumps(patterns, ensure_ascii=False)
            long_term_tokens += self._count_tokens_accurately(patterns_text)
        
        # 风险历史
        risk_history = self.long_term_memory["risk_history"]
        if risk_history:
            risk_text = json.dumps(risk_history[-5:], ensure_ascii=False)  # 只计算最近5条
            long_term_tokens += self._count_tokens_accurately(risk_text)
        
        # 关键洞察
        key_insights = self.long_term_memory["key_insights"]
        if key_insights:
            insights_text = " ".join(key_insights[-3:])  # 只计算最近3条
            long_term_tokens += self._count_tokens_accurately(insights_text)
        
        # 压缩摘要
        compressed_summaries = self.long_term_memory["compressed_summaries"]
        if compressed_summaries:
            summaries_text = " ".join([s["summary"] for s in compressed_summaries[-2:]])  # 只计算最近2条
            long_term_tokens += self._count_tokens_accurately(summaries_text)
        
        return long_term_tokens

    def _trigger_advanced_summary(self):
        """触发高级摘要机制"""
        # ConversationSummaryBufferMemory 会自动处理摘要
        # 这里我们可以添加额外的优化逻辑
        try:
            # 强制触发摘要
            if hasattr(self.memory, 'prune'):
                self.memory.prune()
            
            print(f"✅ 内存优化完成，当前轮次：{self.conversation_count}")
        except Exception as e:
            print(f"⚠️ 内存优化出现问题：{e}")

    def get_context_summary(self) -> str:
        """获取上下文摘要供工具使用 - 优化版本"""
        summary_parts = []
        
        # 添加对话轮数信息
        summary_parts.append(f"已对话{self.conversation_count}轮")
        
        # 添加压缩信息
        if self.compression_count > 0:
            summary_parts.append(f"已压缩{self.compression_count}次")
        
        # 添加风险历史摘要
        if self.long_term_memory["risk_history"]:
            recent_risks = self.long_term_memory["risk_history"][-3:]  # 最近3次
            risk_summary = "，".join([f"{r['level']}级" for r in recent_risks])
            summary_parts.append(f"风险历史：{risk_summary}")
        
        # 添加用户模式
        if self.long_term_memory["user_patterns"]:
            top_patterns = sorted(self.long_term_memory["user_patterns"].items(), 
                                key=lambda x: x[1], reverse=True)[:2]
            pattern_summary = "，".join([f"{p[0]}({p[1]}次)" for p in top_patterns])
            summary_parts.append(f"行为模式：{pattern_summary}")
        
        return " | ".join(summary_parts) if summary_parts else ""
    
    def get_memory_context_for_tool(self) -> str:
        """为工具获取记忆上下文 - 极简版本，避免冗余"""
        # 只在有足够历史时才提供上下文
        if self.conversation_count <= 1:
            return ""
        
        context_parts = []
        
        # 1. 简化的状态信息
        status_info = []
        if self.conversation_count > 1:
            status_info.append(f"对话{self.conversation_count}轮")
        
        # 只显示最近1次风险等级
        if self.long_term_memory["risk_history"]:
            latest_risk = self.long_term_memory["risk_history"][-1]["level"]
            status_info.append(f"风险{latest_risk}级")
        
        # 只显示最频繁的行为模式
        if self.long_term_memory["user_patterns"]:
            top_pattern = max(self.long_term_memory["user_patterns"].items(), key=lambda x: x[1])
            if top_pattern[1] >= 2:  # 只显示出现2次以上的模式
                status_info.append(top_pattern[0])
        
        if status_info:
            context_parts.append(" | ".join(status_info))
        
        # 2. 只显示最近1轮对话的关键信息
        recent_context = self.get_recent_context(limit=1)
        if recent_context:
            ctx = recent_context[0]
            user_input = ctx.get('user_input', '').strip()
            if user_input:
                # 提取用户输入的关键信息（前30字符）
                key_info = user_input[:30].replace('\n', ' ').strip()
                if len(user_input) > 30:
                    key_info += "..."
                context_parts.append(f"上轮: {key_info}")
        
        # 3. 只显示最近1个关键洞察（如果有）
        key_insights = self.long_term_memory["key_insights"]
        if key_insights:
            latest_insight = key_insights[-1]
            # 提取洞察的核心内容
            if "：" in latest_insight:
                insight_content = latest_insight.split("：", 1)[1]
                if insight_content:
                    context_parts.append(f"洞察: {insight_content[:50]}...")
        
        if not context_parts:
            return ""
        
        # 严格控制总长度
        result = " | ".join(context_parts)
        if len(result) > 150:  # 大幅减少长度限制
            result = result[:147] + "..."
        
        return result
    
    def _clean_nested_context(self, text: str) -> str:
        """清理嵌套的上下文信息"""
        if not text:
            return ""
        
        # 移除嵌套的"记忆上下文:"标签
        text = re.sub(r'记忆上下文:\s*', '', text)
        
        # 移除嵌套的"当前状态:"标签
        text = re.sub(r'当前状态:\s*', '', text)
        
        # 移除重复的对话轮数信息
        text = re.sub(r'已对话\d+轮\s*\|?\s*', '', text)
        
        # 移除重复的压缩信息
        text = re.sub(r'已压缩\d+次\s*\|?\s*', '', text)
        
        # 清理多余的分隔符
        text = re.sub(r'\|\s*\|', '|', text)
        text = re.sub(r'^\|\s*', '', text)
        text = re.sub(r'\s*\|$', '', text)
        
        return text.strip()

    def get_recent_context(self, limit: int = 3) -> List[Dict[str, str]]:
        """获取最近的对话上下文
        
        Args:
            limit: 获取最近N轮对话
            
        Returns:
            包含最近对话的列表，每个元素包含 user_input 和 ai_response
        """
        recent_interactions = []
        
        try:
            # 从memory获取最近的消息
            if hasattr(self.memory, 'chat_memory') and hasattr(self.memory.chat_memory, 'messages'):
                messages = self.memory.chat_memory.messages
                
                # 配对用户输入和AI响应
                for i in range(len(messages) - 1, -1, -2):  # 倒序遍历，每次跳2个
                    if i > 0 and len(recent_interactions) < limit:
                        ai_msg = messages[i] if hasattr(messages[i], 'content') else None
                        user_msg = messages[i-1] if hasattr(messages[i-1], 'content') else None
                        
                        if user_msg and ai_msg:
                            interaction = {
                                "user_input": user_msg.content,
                                "ai_response": ai_msg.content
                            }
                            recent_interactions.append(interaction)
                
                # 因为是倒序添加的，需要翻转以保持时间顺序
                recent_interactions.reverse()
                
        except Exception as e:
            print(f"⚠️ 获取最近上下文时出错: {e}")
        
        return recent_interactions

    def get_user_profile_summary(self) -> Dict[str, Any]:
        """生成用户画像总结"""
        profile = {
            "patterns": {},
            "risk_trend": "",
            "personality_traits": [],
            "summary": ""
        }
        
        # 分析行为模式
        patterns = self.long_term_memory["user_patterns"]
        if patterns:
            # 按频率排序
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
            profile["patterns"] = dict(sorted_patterns[:5])  # 取前5个
            
            # 生成模式描述
            pattern_descriptions = []
            for pattern, count in sorted_patterns[:3]:
                if count >= 3:
                    pattern_descriptions.append(f"重度{pattern}")
                elif count >= 2:
                    pattern_descriptions.append(f"中度{pattern}")
                else:
                    pattern_descriptions.append(f"轻度{pattern}")
            
            if pattern_descriptions:
                profile["summary"] += f"行为特征：{', '.join(pattern_descriptions)}。"
        
        # 分析风险趋势
        risk_history = self.long_term_memory["risk_history"]
        if risk_history:
            recent_risks = risk_history[-5:]  # 最近5次
            high_risk_count = sum(1 for r in recent_risks if r["level"] in ["重", "危"])
            if high_risk_count >= 3:
                profile["risk_trend"] = "高风险趋势"
            elif high_risk_count >= 1:
                profile["risk_trend"] = "中等风险"
            else:
                profile["risk_trend"] = "低风险"
            
            profile["summary"] += f" 风险状态：{profile['risk_trend']}。"
        
        # 生成个性特征
        traits = []
        if patterns.get("情绪依赖", 0) >= 2:
            traits.append("情感敏感型")
        if patterns.get("金钱依赖", 0) >= 2:
            traits.append("经济依赖型")
        if patterns.get("社交隔离", 0) >= 2:
            traits.append("社交退缩型")
        if patterns.get("过度理想化", 0) >= 2:
            traits.append("理想主义型")
        if patterns.get("自我怀疑", 0) >= 2:
            traits.append("自我怀疑型")
        
        if traits:
            profile["personality_traits"] = traits
            profile["summary"] += f" 个性特征：{', '.join(traits)}。"
        
        # 如果没有足够数据，提供默认描述
        if not profile["summary"]:
            profile["summary"] = "用户画像数据不足，需要更多对话来生成准确分析。"
        
        return profile

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存使用统计"""
        estimated_tokens = self._estimate_token_count()
        
        return {
            "conversation_count": self.conversation_count,
            "total_interactions": self.conversation_count,
            "short_term_count": len(self.memory.chat_memory.messages) if hasattr(self.memory, 'chat_memory') else 0,
            "long_term_count": len(self.long_term_memory["risk_history"]),
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.max_tokens,
            "memory_usage_ratio": estimated_tokens / self.max_tokens if self.max_tokens > 0 else 0,
            "risk_history_count": len(self.long_term_memory["risk_history"]),
            "pattern_count": len(self.long_term_memory["user_patterns"]),
            "user_patterns": self.long_term_memory["user_patterns"],
            "compression_count": self.compression_count,
            "current_window_size": self.current_window_size
        }

    def clear_session(self):
        """清除当前会话（保留长期记忆）"""
        self.memory.clear()
        self.conversation_count = 0
        # 注意：不清除long_term_memory，保持用户画像

    def export_memory(self) -> Dict[str, Any]:
        """导出记忆数据（用于持久化）"""
        return {
            "conversation_count": self.conversation_count,
            "long_term_memory": self.long_term_memory,
            "memory_window": self.current_window_size # 导出当前窗口大小
        }

    def import_memory(self, memory_data: Dict[str, Any]):
        """导入记忆数据（用于恢复）"""
        self.conversation_count = memory_data.get("conversation_count", 0)
        self.long_term_memory = memory_data.get("long_term_memory", {
            "user_patterns": {},
            "risk_history": [],
            "key_insights": [],
            "persona_preferences": {},
            "compressed_summaries": []
        })
        self.current_window_size = memory_data.get("memory_window", 8) # 导入窗口大小


