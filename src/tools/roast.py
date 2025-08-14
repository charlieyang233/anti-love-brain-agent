from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts import ROAST_INNER_GUIDE

class RoastInput(BaseModel):
    user_text: str = Field(..., description="用户发言")
    level: str = Field(..., description="轻|中|重")
    evidence: str = Field(default="", description="可选：搜索摘要或证据")

class RoastTool(BaseTool):
    name = "roast_tool"
    description = ("当用户分享/吐槽或恋爱相关行为时使用。根据严重程度输出一段自然口语化的老李吐槽，可融合evidence作为案例警示。")
    args_schema: Type[BaseModel] = RoastInput

    def _run(self, user_text: str, level: str, evidence: str = "") -> str:
        return f"""请用老李口吻输出。
                    任务：给出一段自然口语化的毒舌锐评。
                    用户：{user_text}
                    严重程度：{level}
                    若有证据可融入：{evidence or "无"}
                    写作要求：{ROAST_INNER_GUIDE}
                """

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
