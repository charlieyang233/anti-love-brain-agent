from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts import SEAKING_INNER_GUIDE

class SeakingInput(BaseModel):
    user_text: str = Field(..., description="用户最近一句回应")
    persona: str = Field("ENTJ-高阶PUA", description="海王人设")
    prev_score: int = Field(50, description="上一轮得分0-100")

class SeakingTool(BaseTool):
    name = "seaking_tool"
    description = ("当用户要求模拟/挑战时使用。输出一轮：海王台词/用户可选回应建议/拽姐旁白+得分。")
    args_schema: Type[BaseModel] = SeakingInput

    def _run(self, user_text: str, persona: str = "ENTJ-高阶PUA", prev_score: int = 50) -> str:
        return f"""对战一轮。
persona：{persona}
上一轮得分：{prev_score}
用户最近输入：{user_text}
规则：{SEAKING_INNER_GUIDE}"""

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
