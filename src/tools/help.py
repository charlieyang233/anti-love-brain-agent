from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts.prompts import HELP_INNER_GUIDE
from ..prompts.prompt_config import HELP_EXECUTION_PROMPT


class HelpInput(BaseModel):
    user_text: str = Field(..., description="用户发言")
    memory_context: str = Field(default="", description="由Agent提供的记忆上下文（可选）")

class HelpTool(BaseTool):
    name = "help_tool"
    description = ("情感求助分析工具：只有用户有显著的情感求助意图或恋爱脑严重程度为【危险】等级场景，才使用该工具输出情感咨询专家的建议。")
    args_schema: Type[BaseModel] = HelpInput

    def _run(self, user_text: str, memory_context: str = "") -> str:
        """情感求助分析工具 - 直接调用LLM生成回复"""
        try:
            from ..core.config import llm
            
            # 格式化prompt模板
            formatted_prompt = HELP_EXECUTION_PROMPT.format(
                user_text=user_text,
                evidence="",  # 搜索功能已移除，evidence为空
                help_guide=HELP_INNER_GUIDE,
            )
            
            # 直接调用LLM生成回复
            llm_instance = llm(temperature=0.1)
            response = llm_instance.invoke(formatted_prompt)
            
            # 返回生成的回复内容
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            return f"姐妹啊，姐脑子暂时宕机了🚬等我缓缓先！"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
