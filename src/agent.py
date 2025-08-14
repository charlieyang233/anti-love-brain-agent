from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .config import llm
from .prompts import GLOBAL_SYSTEM_PROMPT
from .memory_manager import SmartMemoryManager
from .tools.severity import SeverityTool
from .tools.search import SearchTool
from .tools.roast import RoastTool
from .tools.help import HelpTool
from .tools.seaking import SeakingTool

# 全局记忆管理器实例（用于向后兼容）
smart_memory = SmartMemoryManager(max_conversation_window=15, summary_trigger_ratio=0.8)

def build_agent(memory_manager=None) -> AgentExecutor:
    """
    构建智能代理
    Args:
        memory_manager: 可选的内存管理器，如果未提供则使用全局默认实例
    """
    # 如果没有提供内存管理器，使用全局默认实例
    if memory_manager is None:
        memory_manager = smart_memory
    
    tools = [
        SeverityTool(),
        SearchTool(),
        RoastTool(),
        HelpTool(),
        SeakingTool(),
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", GLOBAL_SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm(temperature=0.7), tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, memory=memory_manager.memory, verbose=False, return_intermediate_steps=True)
    return executor

def get_memory_manager() -> SmartMemoryManager:
    """获取全局记忆管理器实例"""
    return smart_memory

def reset_memory():
    """重置记忆（保留长期记忆）"""
    global smart_memory
    smart_memory.clear_session()
    return build_agent()
