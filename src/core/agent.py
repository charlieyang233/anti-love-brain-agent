from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..prompts.prompts import GLOBAL_SYSTEM_PROMPT
from .config import llm
from ..memory.memory_manager import SmartMemoryManager
# from ..tools.severity import SeverityTool  # 已移除：现在在app.py中直接进行预分析
from ..tools.help import HelpTool

from ..tools.talk import TalkTool



# 全局记忆管理器实例（用于向后兼容）
smart_memory = SmartMemoryManager(max_tokens=1500, summary_trigger_ratio=0.8)

def build_agent(memory_manager=None, answer_style: str = "") -> AgentExecutor:
    """
    构建智能代理
    Args:
        memory_manager: 可选的内存管理器，如果未提供则使用全局默认实例
        answer_style: 动态人设模板内容，将注入到全局prompt中
    """
    # 如果没有提供内存管理器，使用全局默认实例
    if memory_manager is None:
        memory_manager = smart_memory
    
    # 注意：SeakingTool已被重构为SeakingChain，不再用于Agent工具列表
    
    tools = [
        # SeverityTool(),  # 已移除：现在在app.py中直接进行预分析并通过动态人设传递结果
        HelpTool(),
        TalkTool(),
    ]

    # 动态注入answer_style到全局prompt
    enhanced_system_prompt = GLOBAL_SYSTEM_PROMPT.format(answer_style=answer_style)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", enhanced_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm(temperature=0.1), tools, prompt)
    
    # 确保Agent使用传入的记忆实例 - 修复记忆绑定问题
    executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory_manager.memory,  # 直接使用传入的记忆实例
        verbose=True,  # 启用调试信息
        return_intermediate_steps=True,  # 返回中间步骤
        handle_parsing_errors=True,  # 处理解析错误
        max_iterations=3,  # 减少最大迭代次数
        early_stopping_method="generate"  # 使用生成停止方法
    )
    
    # 验证记忆绑定是否成功（调试用）- 使用type检查而不是is检查
    if type(executor.memory) != type(memory_manager.memory):
        print(f"⚠️ 警告：Agent记忆类型不匹配，将强制设置")
        executor.memory = memory_manager.memory
    elif hasattr(executor.memory, 'memory_key') and hasattr(memory_manager.memory, 'memory_key'):
        if executor.memory.memory_key != memory_manager.memory.memory_key:
            print(f"⚠️ 警告：Agent记忆配置不匹配，将强制设置")
            executor.memory = memory_manager.memory
        
    return executor

def get_memory_manager() -> SmartMemoryManager:
    """获取全局记忆管理器实例"""
    return smart_memory

def reset_memory():
    """重置记忆（保留长期记忆）"""
    global smart_memory
    smart_memory.clear_session()
    return build_agent()
