from typing import Type
import json
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..example_selector import ExampleSelector
from ..config import llm

class SeverityInput(BaseModel):
    user_text: str = Field(..., description="用户最新发言")
    context_summary: str = Field("", description="上文摘要，可为空")

class SeverityTool(BaseTool):
    name = "severity_analyzer"
    description = ("评估恋爱脑指数(0-100)和level(轻/中/重/危)，"
                   "危代表明显操控或安全风险。输出JSON字符串。")
    args_schema: Type[BaseModel] = SeverityInput
    
    def __init__(self):
        super().__init__()
        # 将 example_selector 存储为私有属性，避免 Pydantic 验证
        object.__setattr__(self, '_example_selector', ExampleSelector(max_examples=2))

    def _run(self, user_text: str, context_summary: str = "") -> str:
        # 使用智能示例选择器生成动态prompt
        prompt = self._example_selector.generate_dynamic_prompt(user_text, context_summary)
        
        # 调用LLM进行分析
        try:
            response = llm().invoke(prompt)
            # 尝试解析响应中的JSON
            content = response.content if hasattr(response, 'content') else str(response)
            
            # 查找JSON部分
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                # 验证JSON格式
                parsed = json.loads(json_str)
                return json_str
            else:
                # 如果没有找到JSON，返回默认值
                return '{"index": 30, "level": "轻", "signals": ["未能解析具体信号"], "switch_to_help": false}'
        except Exception as e:
            # 出错时返回默认值
            return '{"index": 30, "level": "轻", "signals": ["分析出错"], "switch_to_help": false}'

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
