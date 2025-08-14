from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .config import llm
from .prompt_config import GLOBAL_SYSTEM_PROMPT
from .memory_manager import SmartMemoryManager
from .tools.severity import SeverityTool
from .tools.search import SearchTool
from .tools.roast import RoastTool
from .tools.help import HelpTool
from .tools.seaking import SeakingTool
from .tools.talk import TalkTool

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
        TalkTool(),
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

def invoke_agent_with_intent_params(agent: AgentExecutor, user_input: str, intent_params: dict = None) -> dict:
    """
    调用Agent并传递意图识别参数
    Args:
        agent: Agent执行器
        user_input: 用户输入
        intent_params: 意图识别参数对象
    Returns:
        Agent执行结果
    """
    # 如果有意图识别参数，将其格式化并插入到系统prompt中
    if intent_params:
        # 格式化意图识别参数为可读字符串
        params_str = f"风险:{intent_params.get('risk', 'unknown')} | 主体:{intent_params.get('subject', 'unknown')} | 意图:{intent_params.get('intent', 'unknown')} | 语调:{intent_params.get('tone', 'neutral')} | 工具:{','.join(intent_params.get('tools', []))} | 上下文:{intent_params.get('context', '无')}"
        
        # 创建一个临时的Agent，其prompt中的占位符被替换
        from .prompt_config import GLOBAL_SYSTEM_PROMPT
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.agents import create_openai_tools_agent, AgentExecutor
        from .config import llm
        from .tools.severity import SeverityTool
        from .tools.search import SearchTool
        from .tools.roast import RoastTool
        from .tools.help import HelpTool
        from .tools.seaking import SeakingTool
        from .tools.talk import TalkTool
        
        # 替换prompt中的意图识别参数占位符
        enhanced_prompt = GLOBAL_SYSTEM_PROMPT.replace("{{意图识别参数}}", params_str)
        
        tools = [
            SeverityTool(),
            SearchTool(),
            RoastTool(),
            HelpTool(),
            SeakingTool(),
            TalkTool(),
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", enhanced_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        
        temp_agent = create_openai_tools_agent(llm(temperature=0.7), tools, prompt)
        temp_executor = AgentExecutor(agent=temp_agent, tools=tools, memory=agent.memory, verbose=False, return_intermediate_steps=True)
        
        return temp_executor.invoke({"input": user_input})
    else:
        return agent.invoke({"input": user_input})

def reset_memory():
    """重置记忆（保留长期记忆）"""
    global smart_memory
    smart_memory.clear_session()
    return build_agent()
