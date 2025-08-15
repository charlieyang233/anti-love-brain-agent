from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts.prompts import SEAKING_INNER_GUIDE
from ..prompts.prompt_config import SEAKING_EXECUTION_PROMPT
from ..core.config import llm

class SeakingInput(BaseModel):
    user_text: str = Field(..., description="用户最近一句回应")
    persona: str = Field("ENTJ-高阶PUA", description="海王人设")
    prev_score: int = Field(50, description="上一轮得分0-100")

class SeakingTool(BaseTool):
    name = "seaking_tool"
    description = ("海王模拟器工具：在用户明确要求模拟海王对战/恋爱游戏/模拟海王套路/练习反pua/练习海王话术/挑战海王游戏/海王模拟对战时使用，需要模拟AI海王和用户进行对战。")
    args_schema: Type[BaseModel] = SeakingInput

    def _run(self, user_text: str, persona: str = "ENTJ-高阶PUA", prev_score: int = 50) -> str:
        """海王模拟对战模式 - 直接调用LLM生成回复"""
        
        try:
            # 格式化prompt模板
            formatted_prompt = SEAKING_EXECUTION_PROMPT.format(
                persona=persona,
                seaking_guide=SEAKING_INNER_GUIDE
            )
            
            # 直接调用LLM生成回复
            llm_instance = llm(temperature=0.1)  # 降低温度确保格式一致性
            response = llm_instance.invoke(formatted_prompt)
            
            return response.content.strip()
        except Exception as e:
            # 降级处理：返回简单的对战回复
            return f"海王断网了，还在骑马赶来的路上...🚬"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
