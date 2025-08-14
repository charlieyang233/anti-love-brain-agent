#!/usr/bin/env python3
"""
双层路由记忆集成 - 确保所有路由路径都正确更新全局记忆
增强版：为Agent提供结构化的意图分析参数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.intent.core.dual_layer_router import DualLayerRouter, DualRoutingResult
from src.intent.core.enhanced_agent_params import EnhancedAgentParameterBuilder
from src.intent.core.simplified_agent_params import SimplifiedAgentParameterBuilder
from src.memory_manager import SmartMemoryManager
from typing import Dict, Any, Optional
import json

class DualRouterMemoryIntegration:
    """双层路由记忆集成"""
    
    def __init__(self, memory_manager: SmartMemoryManager, param_mode: str = "simplified"):
        """初始化双层路由记忆集成
        
        Args:
            memory_manager: 记忆管理器
            param_mode: 参数模式 'simplified'(6字段) 或 'enhanced'(37字段)
        """
        self.dual_router = DualLayerRouter()
        self.memory_manager = memory_manager
        self.tool_simulators = self._setup_tool_simulators()
        self.param_mode = param_mode
        
        # 参数构建器选择
        if param_mode == "simplified":
            self.param_builder = SimplifiedAgentParameterBuilder()
        else:
            self.param_builder = EnhancedAgentParameterBuilder(
                self.dual_router, 
                self.memory_manager
            )
        
    def process_with_memory_update(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """处理用户输入并确保记忆更新"""
        
        # 1. 双层路由
        dual_result = self.dual_router.route(user_input, context)
        
        # 2. 执行工具并获取响应
        tool_response = self._execute_tools(dual_result, user_input)
        
        # 3. 统一记忆更新
        self._update_memory(user_input, tool_response, dual_result)
        
        # 4. 构造返回结果
        return self._build_response(tool_response, dual_result)
    
    def _execute_tools(self, dual_result: DualRoutingResult, user_input: str) -> str:
        """执行工具并获取响应"""
        if dual_result.routing_type == "shortcut":
            # 简单直达：单工具或非上下文敏感
            if len(dual_result.final_tools) == 1:
                tool_name = dual_result.final_tools[0]
                return self._call_tool(tool_name, user_input, dual_result)
            else:
                # 多工具组合调用
                return self._call_tool_combination(dual_result.final_tools, user_input, dual_result)
                
        elif dual_result.routing_type == "shortcut_with_context":
            # 上下文敏感的快捷路由：需要考虑对话连贯性
            return self._call_contextual_tools(dual_result.final_tools, user_input, dual_result)
            
        elif dual_result.routing_type == "reference":
            # 参考信号指导的Agent调用
            return self._call_agent_with_reference(user_input, dual_result.reference_signal)
            
        else:
            # 兜底Agent调用
            return self._call_original_agent(user_input)
    
    def _call_tool_combination(self, tools: list, user_input: str, dual_result: DualRoutingResult) -> str:
        """调用工具组合（如severity+search+help）"""
        responses = []
        
        for tool_name in tools:
            if tool_name in self.tool_simulators:
                response = self.tool_simulators[tool_name](user_input, dual_result)
                responses.append(f"[{tool_name}]: {response}")
            else:
                responses.append(f"[{tool_name}]: 处理了 {user_input}")
        
        return " | ".join(responses)
    
    def _call_contextual_tools(self, tools: list, user_input: str, dual_result: DualRoutingResult) -> str:
        """调用上下文敏感的工具（考虑对话连贯性）"""
        # 获取上下文信息
        recent_memory = self.memory_manager.get_recent_context(limit=3)
        context_summary = self._summarize_context(recent_memory)
        
        if len(tools) == 1:
            # 单工具但需要上下文
            tool_name = tools[0]
            contextual_input = f"[上下文: {context_summary}] {user_input}"
            
            if tool_name in self.tool_simulators:
                return self.tool_simulators[tool_name](contextual_input, dual_result)
            else:
                return f"基于对话上下文，{tool_name}处理: {user_input}"
        else:
            # 多工具组合且需要上下文
            return self._call_tool_combination(tools, f"[上下文: {context_summary}] {user_input}", dual_result)
    
    def _summarize_context(self, recent_memory: list) -> str:
        """总结最近的对话上下文"""
        if not recent_memory:
            return "无历史对话"
        
        # 简单提取最近的话题和情绪
        topics = []
        for interaction in recent_memory[-2:]:  # 最近2次对话
            if hasattr(interaction, 'user_input'):
                topics.append(interaction.user_input[:20] + "...")
        
        return f"最近讨论: {', '.join(topics)}" if topics else "无相关上下文"
    
    def _call_tool(self, tool_name: str, user_input: str, dual_result: DualRoutingResult) -> str:
        """调用具体工具"""
        if tool_name in self.tool_simulators:
            return self.tool_simulators[tool_name](user_input, dual_result)
        else:
            return f"调用了{tool_name}工具处理: {user_input}"
    
    def _call_agent_with_reference(self, user_input: str, reference_signal) -> str:
        """调用Agent并使用参考信号"""
        # 构建完整的路由结果用于参数构建
        dual_result = DualRoutingResult(
            routing_type="reference",
            reference_signal=reference_signal,
            final_tools=reference_signal.suggested_tools,
            confidence=0.7,
            processing_time_ms=0.5
        )
        
        # 根据参数模式构建不同类型的参数
        if self.param_mode == "simplified":
            # 简化模式：6字段参数
            conversation_history = self.memory_manager.get_recent_context(limit=3)
            agent_params = self.param_builder.build_params(
                reference_signal, user_input, conversation_history
            )
            
            # 调用真实Agent并传递意图识别参数
            try:
                from src.agent import build_agent, invoke_agent_with_intent_params
                agent = build_agent(self.memory_manager)
                result = invoke_agent_with_intent_params(agent, user_input, agent_params)
                return result.get("output", "Agent调用失败")
            except Exception as e:
                # 兜底返回模拟结果
                param_summary = f"6字段简化参数: {agent_params['intent']}|{agent_params['risk']}|{agent_params['subject']}"
                return f"Agent处理({self.param_mode}模式): {user_input[:30]}... | {param_summary}"
        else:
            # 增强模式：37字段参数  
            agent_params = self.param_builder.build_agent_parameters(user_input, dual_result)
            param_summary = f"37字段增强参数: {len(agent_params)}个分类"
            return f"Agent处理({self.param_mode}模式): {user_input[:30]}... | {param_summary}"
    
    def _call_original_agent(self, user_input: str) -> str:
        """调用原始Agent"""
        # 构建兜底路由结果
        dual_result = DualRoutingResult(
            routing_type="fallback",
            final_tools=["original_agent"],
            confidence=0.3,
            processing_time_ms=0.2,
            debug_info={"reason": "no_clear_pattern"}
        )
        
        # 根据参数模式构建参数
        if self.param_mode == "simplified":
            # 简化模式：创建基础意图结果
            class BasicIntentResult:
                def __init__(self):
                    self.intent = "unknown"
                    self.subject = "unknown"
                    self.risk_level = "none"
                    self.help_seeking = True
                    self.confidence = 0.3
            
            basic_intent = BasicIntentResult()
            agent_params = self.param_builder.build_params(basic_intent, user_input)
            
            # 调用真实Agent并传递兜底参数
            try:
                from src.agent import build_agent, invoke_agent_with_intent_params
                agent = build_agent(self.memory_manager)
                result = invoke_agent_with_intent_params(agent, user_input, agent_params)
                return result.get("output", "兜底Agent调用失败")
            except Exception as e:
                # 兜底返回模拟结果
                param_summary = f"简化兜底参数: {agent_params['intent']}|{agent_params['tone']}"
                return f"兜底Agent({self.param_mode}模式): {user_input[:30]}... | {param_summary}"
        else:
            # 增强模式
            agent_params = self.param_builder.build_agent_parameters(user_input, dual_result)
            param_summary = f"增强兜底参数: {len(agent_params)}个字段"
            return f"兜底Agent({self.param_mode}模式): {user_input[:30]}... | {param_summary}"
    
    def _update_memory(self, user_input: str, ai_response: str, dual_result: DualRoutingResult):
        """统一记忆更新"""
        
        # 提取恋爱脑相关信息
        love_brain_level = self._extract_love_brain_level(dual_result, ai_response)
        risk_signals = self._extract_risk_signals(dual_result, user_input)
        
        # 更新短期和长期记忆
        self.memory_manager.add_interaction(
            user_input=user_input,
            ai_response=ai_response,
            love_brain_level=love_brain_level,
            risk_signals=risk_signals
        )
        
        # 添加路由元数据
        self._add_routing_metadata(dual_result)
    
    def _extract_love_brain_level(self, dual_result: DualRoutingResult, ai_response: str) -> Optional[str]:
        """从路由结果提取恋爱脑等级"""
        
        # 如果调用了severity工具，直接提取
        if dual_result.final_tools and "severity" in dual_result.final_tools[0]:
            # 从模拟的severity响应中提取
            if "高风险" in ai_response:
                return "重"
            elif "中风险" in ai_response:
                return "中"
            else:
                return "轻"
        
        # 根据路由类型推断
        if dual_result.routing_type == "shortcut":
            # 短路规则的情况
            if dual_result.shortcut_result:
                rule_name = dual_result.debug_info.get("rule", "")
                if "高风险" in rule_name:
                    return "重"
                elif "恋爱" in rule_name:
                    return "轻"
        
        elif dual_result.routing_type == "reference":
            # 参考信号的情况
            if dual_result.reference_signal:
                factors = dual_result.reference_signal.confidence_factors
                if "high_risk" in factors:
                    return "中"
                elif "romance" in str(factors):
                    return "轻"
        
        return None
    
    def _extract_risk_signals(self, dual_result: DualRoutingResult, user_input: str) -> list:
        """提取风险信号"""
        risk_signals = []
        
        # 检查高风险关键词
        high_risk_words = ["威胁", "家暴", "自杀", "裸聊", "勒索", "暴力"]
        for word in high_risk_words:
            if word in user_input:
                risk_signals.append(f"高风险词汇:{word}")
        
        # 从路由结果提取
        if dual_result.routing_type == "reference" and dual_result.reference_signal:
            factors = dual_result.reference_signal.confidence_factors
            if "risk_detection" in factors:
                risk_signals.append("风险检测信号")
        
        return risk_signals
    
    def _add_routing_metadata(self, dual_result: DualRoutingResult):
        """添加路由元数据到用户画像"""
        # 这里可以扩展为更详细的用户行为分析
        routing_insight = {
            "routing_type": dual_result.routing_type,
            "confidence": dual_result.confidence,
            "token_saved": dual_result.routing_type == "shortcut",
            "processing_time": dual_result.processing_time_ms
        }
        
        # 可以调用memory_manager的扩展方法来记录这些元数据
        # self.memory_manager.add_user_insight("routing_behavior", routing_insight)
    
    def _build_response(self, ai_response: str, dual_result: DualRoutingResult) -> Dict[str, Any]:
        """构造标准化响应"""
        return {
            "response": ai_response,
            "routing_info": {
                "routing_type": dual_result.routing_type,  # 修复：使用正确的字段名
                "final_tools": dual_result.final_tools,   # 修复：使用正确的字段名
                "success": True,
                "confidence": dual_result.confidence
            },
            "performance": {
                "token_saved": dual_result.routing_type == "shortcut",
                "processing_time_ms": dual_result.processing_time_ms,
                "routing_efficiency": self._calculate_efficiency(dual_result)
            },
            "memory_updated": True,  # 添加记忆更新状态
            "memory_stats": self.memory_manager.get_memory_stats(),
            "debug_info": dual_result.debug_info if dual_result.debug_info else {}
        }
    
    def _calculate_efficiency(self, dual_result: DualRoutingResult) -> float:
        """计算路由效率"""
        if dual_result.routing_type == "shortcut":
            return 1.0  # 最高效率
        elif dual_result.routing_type == "reference":
            return 0.7  # 中等效率
        else:
            return 0.3  # 低效率(兜底)
    
    def _setup_tool_simulators(self) -> Dict[str, callable]:
        """设置工具模拟器"""
        return {
            "seaking_tool": self._simulate_seaking_tool,
            "roast_tool": self._simulate_roast_tool,
            "help_tool": self._simulate_help_tool,
            "search_tool": self._simulate_search_tool,
            "severity_analyzer": self._simulate_severity_tool,
            "talk_tool": self._simulate_talk_tool
        }
    
    def _simulate_seaking_tool(self, user_input: str, dual_result: DualRoutingResult) -> str:
        """模拟海王工具"""
        return f"🎯 海王话术生成完成！为您量身定制撩妹技巧，注意适度使用哦~ (输入: {user_input})"
    
    def _simulate_roast_tool(self, user_input: str, dual_result: DualRoutingResult) -> str:
        """模拟毒舌工具"""
        return f"🔥 拽姐模式激活！直接点醒你，别再恋爱脑了，清醒点姐妹！(输入: {user_input})"
    
    def _simulate_help_tool(self, user_input: str, dual_result: DualRoutingResult) -> str:
        """模拟帮助工具"""
        return f"💡 为您提供专业建议和指导，理性分析问题解决方案。(输入: {user_input})"
    
    def _simulate_search_tool(self, user_input: str, dual_result: DualRoutingResult) -> str:
        """模拟搜索工具"""  
        return f"🔍 搜索功能已启动，为您查找相关信息和资料。(输入: {user_input})"
    
    def _simulate_severity_tool(self, user_input: str, dual_result: DualRoutingResult) -> str:
        """模拟风险评估工具"""
        return f"⚠️ 风险评估完成：检测到潜在风险信号，建议谨慎处理。(输入: {user_input})"
    
    def _simulate_talk_tool(self, user_input: str, dual_result: DualRoutingResult) -> str:
        """模拟聊天工具"""
        return f"💬 愉快聊天模式！让我们轻松谈论这个话题。(输入: {user_input})"


    def compare_param_modes(self, user_input: str) -> Dict[str, Any]:
        """比较两种参数模式的输出差异"""
        # 准备路由结果
        dual_result = self.dual_router.route(user_input)
        
        # 简化模式参数
        simplified_builder = SimplifiedAgentParameterBuilder()
        
        # 创建基础意图结果
        class BasicIntentResult:
            def __init__(self):
                self.intent = getattr(dual_result.reference_signal, 'intent', 'unknown') if dual_result.reference_signal else 'unknown'
                self.subject = 'unknown'
                self.risk_level = 'none'
                self.help_seeking = True
                self.confidence = dual_result.confidence
        
        basic_intent = BasicIntentResult()
        simplified_params = simplified_builder.build_params(basic_intent, user_input)
        
        # 增强模式参数
        enhanced_builder = EnhancedAgentParameterBuilder(self.dual_router, self.memory_manager)
        enhanced_params = enhanced_builder.build_agent_parameters(user_input, dual_result)
        
        return {
            "user_input": user_input,
            "simplified_params": simplified_params,
            "enhanced_params": enhanced_params,
            "simplified_size": len(str(simplified_params)),
            "enhanced_size": len(str(enhanced_params)),
            "size_ratio": len(str(enhanced_params)) / len(str(simplified_params))
        }


def test_memory_integration():
    """测试记忆集成功能"""
    print("🧪 双层路由记忆集成测试")
    print("=" * 60)
    
    # 创建记忆管理器
    from src.memory_manager import SmartMemoryManager
    memory_manager = SmartMemoryManager(max_conversation_window=15)
    
    # 创建双层路由记忆集成 - 默认简化模式
    integration = DualRouterMemoryIntegration(memory_manager, param_mode="simplified")
    
    # 测试用例
    test_cases = [
        "我想学习撩妹技巧",  # 应该调用seaking_tool
        "室友被渣男骗了",    # 应该调用roast_tool
        "老板威胁我",        # 应该调用severity_analyzer
        "查一下这个人",      # 应该调用search_tool
        "今天天气怎么样"     # 应该调用talk_tool
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_input}")
        
        # 获取处理前的记忆状态
        memory_before = memory_manager.get_memory_stats()
        
        # 处理输入
        result = integration.process_with_memory_update(test_input)
        
        # 获取处理后的记忆状态  
        memory_after = memory_manager.get_memory_stats()
        
        print(f"  路由类型: {result['routing_info']['path']}")
        print(f"  工具调用: {result['routing_info']['tools_called']}")
        print(f"  Token节省: {result['performance']['token_saved']}")
        print(f"  记忆更新: 交互数 {memory_before.get('total_interactions', 0)} → {memory_after.get('total_interactions', 0)}")
        print(f"  AI响应: {result['response'][:50]}...")
        
        # 验证记忆是否更新
        if memory_after.get('total_interactions', 0) > memory_before.get('total_interactions', 0):
            print("  ✅ 记忆已正确更新")
        else:
            print("  ❌ 记忆更新失败")
    
    print(f"\n📊 最终记忆统计:")
    final_stats = memory_manager.get_memory_stats()
    print(f"  总交互数: {final_stats.get('total_interactions', 0)}")
    print(f"  短期记忆: {final_stats.get('short_term_count', 0)}")
    print(f"  长期记忆: {final_stats.get('long_term_count', 0)}")
    
    return integration


if __name__ == "__main__":
    integration = test_memory_integration()
    print("\n🎉 双层路由记忆集成测试完成！")
