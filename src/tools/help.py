from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts import HELP_INNER_GUIDE

class HelpInput(BaseModel):
    user_text: str = Field(..., description="用户发言")
    evidence: str = Field(default="", description="可选：搜索摘要或证据")

class HelpTool(BaseTool):
    name = "help_tool"
    description = ("当用户明确求助恋爱情感问题或恋爱脑严重程度识别为【危】时使用。输出专家式拆解+行动建议，语气收敛但保留老李收尾。")
    args_schema: Type[BaseModel] = HelpInput

    def _run(self, user_text: str, evidence: str = "") -> str:
        return f"""请用“高级情感专家”+老李收尾的混合口吻，输出一段自然连贯的话。
                    用户：{user_text}
                    可融入证据：{evidence or "无"}
                    写作要求：{HELP_INNER_GUIDE}"""

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
