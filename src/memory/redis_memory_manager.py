import redis
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferWindowMemory
from ..core.config import llm

class RedisMemoryManager:
    """基于Redis的生产级长期记忆管理器"""
    
    def __init__(self, 
                 redis_host: str = "localhost", 
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 redis_password: Optional[str] = None,
                 user_id: Optional[str] = None,
                 max_tokens: int = 1500,
                 summary_trigger_ratio: float = 0.8,
                 memory_ttl: int = 7 * 24 * 3600):  # 7天过期
        """
        初始化Redis记忆管理器
        
        Args:
            redis_host: Redis主机地址
            redis_port: Redis端口
            redis_db: Redis数据库编号
            redis_password: Redis密码
            user_id: 用户ID，用于多用户隔离
            max_tokens: 最大token数量
            summary_trigger_ratio: 压缩触发比例
            memory_ttl: 长期记忆TTL（秒）
        """
        # Redis连接
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True
        )
        
        # 用户标识
        self.user_id = user_id or str(uuid.uuid4())
        self.memory_ttl = memory_ttl
        
        # 短期记忆（仍使用内存窗口）
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=15,  # 固定窗口大小
            ai_prefix="拽姐",
            human_prefix="用户",
            output_key="output"  # 明确指定输出键，消除警告
        )
        
        # Redis键名前缀
        self.key_prefix = f"memory:{self.user_id}"
        
        # 初始化长期记忆结构
        self._initialize_long_term_memory()
    
    def _initialize_long_term_memory(self):
        """初始化长期记忆Redis数据结构"""
        keys = [
            f"{self.key_prefix}:user_patterns",    # Hash: 用户行为模式
            f"{self.key_prefix}:risk_history",     # List: 风险历史记录
            f"{self.key_prefix}:key_insights",     # List: 关键洞察
            f"{self.key_prefix}:preferences",      # Hash: 用户偏好
            f"{self.key_prefix}:metadata"          # Hash: 元数据（计数器等）
        ]
        
        # 为所有键设置TTL
        for key in keys:
            if not self.redis_client.exists(key):
                # 初始化空数据结构
                if "history" in key or "insights" in key:
                    self.redis_client.lpush(key, "[]")  # 空列表占位符
                    self.redis_client.lpop(key)  # 立即移除，创建空列表
                else:
                    self.redis_client.hset(key, "initialized", "true")
                    self.redis_client.hdel(key, "initialized")  # 创建空hash
            
            self.redis_client.expire(key, self.memory_ttl)
    
    def add_interaction(self, user_input: str, ai_response: str, 
                       love_brain_level: str = None, risk_signals: List[str] = None):
        """添加一轮对话到记忆中"""
        # 更新对话计数
        conversation_count = self.redis_client.hincrby(
            f"{self.key_prefix}:metadata", 
            "conversation_count", 
            1
        )
        
        # 添加到短期记忆（内存窗口）
        self.memory.save_context(
            {"input": user_input},
            {"output": ai_response}
        )
        
        # 更新长期记忆（Redis）
        self._update_long_term_memory_redis(
            user_input, ai_response, love_brain_level, risk_signals, conversation_count
        )
        
        # 刷新TTL
        self._refresh_ttl()
    
    def _update_long_term_memory_redis(self, user_input: str, ai_response: str, 
                                     love_brain_level: str, risk_signals: List[str], round_num: int):
        """更新Redis中的长期记忆"""
        
        # 1. 更新用户行为模式
        if love_brain_level and love_brain_level in ["重", "危"]:
            self._detect_and_update_patterns(user_input)
        
        # 2. 记录风险历史
        if love_brain_level:
            risk_record = {
                "round": round_num,
                "level": love_brain_level,
                "timestamp": datetime.now().isoformat(),
                "signals": risk_signals or [],
                "input_preview": user_input[:100]  # 保存前100字符
            }
            self.redis_client.lpush(
                f"{self.key_prefix}:risk_history",
                json.dumps(risk_record, ensure_ascii=False)
            )
            
            # 保持风险历史不超过50条
            self.redis_client.ltrim(f"{self.key_prefix}:risk_history", 0, 49)
        
        # 3. 记录关键洞察
        if love_brain_level in ["重", "危"]:
            insight = {
                "round": round_num,
                "level": love_brain_level,
                "content": f"第{round_num}轮：{love_brain_level}级风险 - {user_input[:50]}...",
                "timestamp": datetime.now().isoformat()
            }
            self.redis_client.lpush(
                f"{self.key_prefix}:key_insights",
                json.dumps(insight, ensure_ascii=False)
            )
            
            # 保持关键洞察不超过20条
            self.redis_client.ltrim(f"{self.key_prefix}:key_insights", 0, 19)
    
    def _detect_and_update_patterns(self, user_input: str):
        """检测并更新用户行为模式到Redis"""
        pattern_keywords = {
            "金钱依赖": ["转账", "借钱", "投资", "买单", "花钱", "红包", "转钱"],
            "情绪依赖": ["想念", "焦虑", "失眠", "心情", "情绪", "难过", "开心"],
            "社交隔离": ["朋友", "家人", "同事", "社交", "联系", "孤独", "alone"],
            "时间沉迷": ["整天", "一直", "24小时", "不停", "总是", "每天", "时刻"]
        }
        
        for pattern, keywords in pattern_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                self.redis_client.hincrby(
                    f"{self.key_prefix}:user_patterns",
                    pattern,
                    1
                )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        # 从Redis获取长期记忆统计
        conversation_count = int(self.redis_client.hget(f"{self.key_prefix}:metadata", "conversation_count") or 0)
        
        # 估算token使用（短期记忆）
        estimated_tokens = self._estimate_tokens()
        max_tokens = 1500  # 窗口最大token估算
        
        # 获取用户行为模式
        user_patterns = {}
        pattern_data = self.redis_client.hgetall(f"{self.key_prefix}:user_patterns")
        for pattern, count in pattern_data.items():
            user_patterns[pattern] = int(count)
        
        return {
            "conversation_count": conversation_count,
            "estimated_tokens": estimated_tokens,
            "max_tokens": max_tokens,
            "memory_usage_ratio": estimated_tokens / max_tokens if max_tokens > 0 else 0,
            "user_patterns": user_patterns,
            "storage_type": "redis",
            "user_id": self.user_id
        }
    
    def get_context_summary(self) -> str:
        """获取上下文摘要（从Redis读取长期记忆）"""
        try:
            # 从Redis获取数据
            conversation_count = int(self.redis_client.hget(f"{self.key_prefix}:metadata", "conversation_count") or 0)
            
            # 获取用户行为模式
            user_patterns = {}
            pattern_data = self.redis_client.hgetall(f"{self.key_prefix}:user_patterns")
            for pattern, count in pattern_data.items():
                user_patterns[pattern] = int(count)
            
            # 获取最近的风险历史
            risk_history_raw = self.redis_client.lrange(f"{self.key_prefix}:risk_history", 0, 4)
            risk_history = []
            for record in risk_history_raw:
                try:
                    risk_history.append(json.loads(record))
                except json.JSONDecodeError:
                    continue
            
            # 构建摘要
            summary = f"已对话{conversation_count}轮"
            
            if user_patterns:
                pattern_summary = ", ".join([f"{k}({v}次)" for k, v in user_patterns.items() if v > 0])
                summary += f" | 行为模式: {pattern_summary}"
            
            if risk_history:
                recent_risks = [r["level"] for r in risk_history[:3]]
                summary += f" | 风险历史: {', '.join(recent_risks)}"
            
            return summary
            
        except Exception as e:
            return f"无法获取记忆摘要: {str(e)}"
    
    def _estimate_tokens(self) -> int:
        """估算当前短期记忆的token使用量"""
        messages = self.memory.chat_memory.messages
        total_chars = sum(len(msg.content) for msg in messages)
        # 中文约1.5倍token，英文约0.5倍
        estimated_tokens = int(total_chars * 0.8)
        return estimated_tokens
    
    def _refresh_ttl(self):
        """刷新所有记忆键的TTL"""
        keys = [
            f"{self.key_prefix}:user_patterns",
            f"{self.key_prefix}:risk_history", 
            f"{self.key_prefix}:key_insights",
            f"{self.key_prefix}:preferences",
            f"{self.key_prefix}:metadata"
        ]
        
        for key in keys:
            self.redis_client.expire(key, self.memory_ttl)
    
    def reset_short_term_memory(self):
        """重置短期记忆，保留长期记忆"""
        self.memory.clear()
        # Redis中的长期记忆保持不变
    
    def clear_all_memory(self):
        """清除所有记忆（包括Redis长期记忆）"""
        keys = [
            f"{self.key_prefix}:user_patterns",
            f"{self.key_prefix}:risk_history",
            f"{self.key_prefix}:key_insights", 
            f"{self.key_prefix}:preferences",
            f"{self.key_prefix}:metadata"
        ]
        
        # 清除Redis数据
        self.redis_client.delete(*keys)
        
        # 清除短期记忆
        self.memory.clear()
    
    def export_memory_from_redis(self) -> Dict[str, Any]:
        """从Redis导出完整记忆数据"""
        data = {}
        
        # 元数据
        metadata = self.redis_client.hgetall(f"{self.key_prefix}:metadata")
        data["metadata"] = metadata
        
        # 用户模式
        user_patterns = self.redis_client.hgetall(f"{self.key_prefix}:user_patterns")
        data["user_patterns"] = {k: int(v) for k, v in user_patterns.items()}
        
        # 风险历史
        risk_history_raw = self.redis_client.lrange(f"{self.key_prefix}:risk_history", 0, -1)
        data["risk_history"] = []
        for record in risk_history_raw:
            try:
                data["risk_history"].append(json.loads(record))
            except json.JSONDecodeError:
                continue
        
        # 关键洞察
        insights_raw = self.redis_client.lrange(f"{self.key_prefix}:key_insights", 0, -1)
        data["key_insights"] = []
        for insight in insights_raw:
            try:
                data["key_insights"].append(json.loads(insight))
            except json.JSONDecodeError:
                continue
        
        return data
    
    def get_user_analytics(self) -> Dict[str, Any]:
        """获取用户行为分析报告"""
        memory_data = self.export_memory_from_redis()
        
        # 分析风险趋势
        risk_trend = []
        if memory_data.get("risk_history"):
            recent_risks = memory_data["risk_history"][:10]  # 最近10次
            risk_levels = {"轻": 1, "中": 2, "重": 3, "危": 4}
            risk_trend = [risk_levels.get(r["level"], 0) for r in recent_risks]
        
        # 分析行为模式分布
        pattern_distribution = memory_data.get("user_patterns", {})
        total_patterns = sum(pattern_distribution.values())
        
        pattern_percentages = {}
        if total_patterns > 0:
            for pattern, count in pattern_distribution.items():
                pattern_percentages[pattern] = round((count / total_patterns) * 100, 1)
        
        return {
            "user_id": self.user_id,
            "total_conversations": len(memory_data.get("risk_history", [])),
            "risk_trend": risk_trend,
            "pattern_distribution": pattern_percentages,
            "high_risk_episodes": len([r for r in memory_data.get("risk_history", []) if r["level"] in ["重", "危"]]),
            "analysis_timestamp": datetime.now().isoformat()
        }
