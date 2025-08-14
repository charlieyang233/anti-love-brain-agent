from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts import ROAST_INNER_GUIDE

class RoastInput(BaseModel):
    user_text: str = Field(..., description="用户发言")
    level: str = Field(..., description="轻|中|重")
    evidence: str = Field(default="", description="可选：搜索摘要或证据")

class RoastTool(BaseTool):
    name = "roast_tool"
    description = ("💥 毒舌锐评恋爱脑工具：用于纯分享/吐槽场景。根据恋爱脑程度调整毒舌强度：轻度温和挖苦(≤20字)，"
                   "中度直白犀利+困惑反问+祛魅(25-30字)，重度高强度直怼+戏谑夸张+案例警示(30-50字)。"
                   "口语化开头直戳痛点，极端祛魅揭露真相，可融入evidence作案例警示。拽姐人设，不讲道理只暴击。")
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
