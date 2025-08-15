from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts.prompts import TALK_INNER_GUIDE
from ..prompts.prompt_config import TALK_EXECUTION_PROMPT

class TalkInput(BaseModel):
    user_text: str = Field(..., description="用户发言内容")
    memory_context: str = Field(default="", description="由Agent提供的记忆上下文（可选）")

class TalkTool(BaseTool):
    name = "talk_tool"
    description = ("日常闲聊工具：只有用户期望非恋爱话题的日常闲聊、友情/亲情/职场/社会话题讨论吐槽时，才使用该工具。")
    args_schema: Type[BaseModel] = TalkInput

    def _run(self, user_text: str, memory_context: str = "", memory_manager=None) -> str:
        """闺蜜吹水搭子模式 - 直接调用LLM生成回复"""
        try:
            from ..core.config import llm
            
            # 格式化prompt模板
            formatted_prompt = TALK_EXECUTION_PROMPT.format(
                user_text=user_text,
                talk_guide=TALK_INNER_GUIDE,
            )
            
            # 直接调用LLM生成回复
            llm_instance = llm(temperature=0.1)
            response = llm_instance.invoke(formatted_prompt)
            
            # 返回生成的回复内容
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            # 降级处理：返回简单回复
            return f"姐没钱了，忙着打工赚草料！晚点再聊吧铁子！😭"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
