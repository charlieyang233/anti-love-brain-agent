from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

class SeverityInput(BaseModel):
    user_text: str = Field(..., description="用户最新发言")
    context_summary: str = Field("", description="上文摘要，可为空")

class SeverityTool(BaseTool):
    name = "severity_analyzer"
    description = ("评估恋爱脑指数(0-100)和level(轻/中/重/危)，"
                   "危代表明显操控或安全风险。输出JSON字符串。")
    args_schema: Type[BaseModel] = SeverityInput

    def _run(self, user_text: str, context_summary: str = "") -> str:
        prompt = f"""你是“恋爱脑程度识别器”。只输出JSON。
区间: 0-39轻，40-69中，70-89重，90-100危(明显操控/安全风险)。
返回: {{"index":0-100,"level":"轻|中|重|危","signals":["..."],"switch_to_help":true|false}}
用户发言：{user_text}
上下文提要：{context_summary}"""
        return prompt

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
