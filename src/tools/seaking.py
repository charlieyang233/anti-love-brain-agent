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
    description = ("🌊 海王模拟对战工具：用户明确要求模拟/挑战/对战/练习AI海王挑战时使用。生成三段式对战："
                   "【海王】按人设说套路话(PUA/转移/试探/冷暴力) → 【你】极短回应建议(括号内) → "
                   "【拽姐旁白】点评要害+战术提示+得分(0-100)。连续两次明确边界+拒绝不对等要求则胜利。"
                   "支持高冷学霸型、温柔暖男型、霸道总裁型等人设。台词口语化真实，保持拽姐人设。")
    args_schema: Type[BaseModel] = SeakingInput

    def _run(self, user_text: str, persona: str = "ENTJ-高阶PUA", prev_score: int = 50) -> str:
        return f"""对战一轮。
persona：{persona}
上一轮得分：{prev_score}
用户最近输入：{user_text}
规则：{SEAKING_INNER_GUIDE}"""

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
