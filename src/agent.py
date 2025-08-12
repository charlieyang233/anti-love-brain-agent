from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from .config import llm
from .prompts import GLOBAL_SYSTEM_PROMPT
from .tools.severity import SeverityTool
from .tools.search import SearchTool
from .tools.roast import RoastTool
from .tools.help import HelpTool
from .tools.seaking import SeakingTool

def build_agent() -> AgentExecutor:
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
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False)
    return executor
