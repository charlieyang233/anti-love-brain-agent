from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from typing import List, Dict, Any
import json
from .config import llm

class SmartMemoryManager:
    """智能记忆管理器 - 支持窗口记忆和长期模式追踪"""
    
    def __init__(self, max_conversation_window: int = 10, summary_trigger_ratio: float = 0.8):
        """
        初始化智能记忆管理器
        
        Args:
            max_conversation_window: 最大对话窗口大小（保留最近N轮对话）
            summary_trigger_ratio: 预留参数，用于未来扩展
        """
        self.max_conversation_window = max_conversation_window
        self.conversation_count = 0
        
        # 使用ConversationBufferWindowMemory进行窗口记忆
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=max_conversation_window,  # 保留最近k轮对话
            ai_prefix="拽姐",
            human_prefix="用户",
            output_key="output"  # 明确指定输出键，消除警告
        )
        
        # 长期记忆存储（关键信息持久化）
        self.long_term_memory = {
            "user_patterns": {},  # 用户恋爱模式记录
            "risk_history": [],   # 风险等级历史
            "key_insights": [],   # 关键洞察记录
            "persona_preferences": {}  # 海王模拟偏好
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
        
        # 更新长期记忆中的关键信息
        self._update_long_term_memory(user_input, ai_response, love_brain_level, risk_signals)
        
        # 检查是否需要压缩长期记忆
        self._maintain_long_term_memory()

    def _maintain_long_term_memory(self):
        """维护长期记忆，防止过度膨胀"""
        # 风险历史保持最近20条
        if len(self.long_term_memory["risk_history"]) > 20:
            self.long_term_memory["risk_history"] = self.long_term_memory["risk_history"][-20:]
        
        # 关键洞察保持最近10条
        if len(self.long_term_memory["key_insights"]) > 10:
            self.long_term_memory["key_insights"] = self.long_term_memory["key_insights"][-10:]

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
            "金钱依赖": ["转账", "借钱", "投资", "买单", "花钱"],
            "情绪依赖": ["想念", "焦虑", "失眠", "心情", "情绪"],
            "社交隔离": ["朋友", "家人", "同事", "社交", "联系"],
            "时间沉迷": ["整天", "一直", "24小时", "不停", "总是"]
        }
        
        for pattern_type, keywords in pattern_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                if pattern_type not in patterns:
                    patterns[pattern_type] = 0
                patterns[pattern_type] += 1

    def _check_and_optimize_memory(self):
        """检查并优化内存使用"""
        # 获取当前记忆使用情况
        current_tokens = self._estimate_token_count()
        
        if current_tokens > self.max_token_limit * self.summary_trigger_ratio:
            print(f"🧠 内存优化：当前使用{current_tokens}tokens，触发智能摘要...")
            self._trigger_advanced_summary()

    def _detect_user_patterns(self, user_input: str, love_brain_level: str):
        """检测用户恋爱行为模式"""
        patterns = self.long_term_memory["user_patterns"]
        
        # 关键词检测
        pattern_keywords = {
            "金钱依赖": ["转账", "借钱", "投资", "买单", "花钱"],
            "情绪依赖": ["想念", "焦虑", "失眠", "心情", "情绪"],
            "社交隔离": ["朋友", "家人", "同事", "社交", "联系"],
            "时间沉迷": ["整天", "一直", "24小时", "不停", "总是"]
        }
        
        for pattern_type, keywords in pattern_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                if pattern_type not in patterns:
                    patterns[pattern_type] = 0
                patterns[pattern_type] += 1

    def _estimate_token_count(self) -> int:
        """估算当前内存使用的token数量"""
        try:
            # 获取当前缓冲区内容
            buffer_messages = self.memory.chat_memory.messages
            total_chars = sum(len(str(msg.content)) for msg in buffer_messages)
            
            # 简单估算：中文字符*1.5，英文字符*0.5
            buffer_str = ' '.join(str(msg.content) for msg in buffer_messages)
            chinese_chars = len([c for c in buffer_str if '\u4e00' <= c <= '\u9fff'])
            other_chars = total_chars - chinese_chars
            return int(chinese_chars * 1.5 + other_chars * 0.5)
        except:
            return 0

    def _estimate_token_count(self) -> int:
        """估算当前内存使用的token数量"""
        try:
            # 简单估算：中文字符*1.5，英文单词*1.2
            memory_str = str(self.memory.buffer)
            chinese_chars = len([c for c in memory_str if '\u4e00' <= c <= '\u9fff'])
            other_chars = len(memory_str) - chinese_chars
            return int(chinese_chars * 1.5 + other_chars * 0.3)
        except:
            return 0

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
        """获取上下文摘要供工具使用"""
        summary_parts = []
        
        # 添加对话轮数信息
        summary_parts.append(f"已对话{self.conversation_count}轮")
        
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

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存使用统计"""
        estimated_tokens = self._estimate_token_count()
        max_tokens = self.max_conversation_window * 100  # 简单估算
        
        return {
            "conversation_count": self.conversation_count,
            "total_interactions": self.conversation_count,  # 添加总交互数
            "short_term_count": len(self.memory.chat_memory.messages) if hasattr(self.memory, 'chat_memory') else 0,
            "long_term_count": len(self.long_term_memory["risk_history"]),
            "estimated_tokens": estimated_tokens,
            "max_tokens": max_tokens,
            "token_usage_ratio": estimated_tokens / max_tokens if max_tokens > 0 else 0,
            "risk_history_count": len(self.long_term_memory["risk_history"]),
            "pattern_count": len(self.long_term_memory["user_patterns"]),
            "user_patterns": self.long_term_memory["user_patterns"]
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
            "memory_window": self.max_conversation_window
        }

    def import_memory(self, memory_data: Dict[str, Any]):
        """导入记忆数据（用于恢复）"""
        self.conversation_count = memory_data.get("conversation_count", 0)
        self.long_term_memory = memory_data.get("long_term_memory", {
            "user_patterns": {},
            "risk_history": [],
            "key_insights": [],
            "persona_preferences": {}
        })
