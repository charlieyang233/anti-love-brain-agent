from typing import Type
import json
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from ..prompts.prompts import HELP_INNER_GUIDE, ROAST_INNER_GUIDE

class SeverityInput(BaseModel):
    user_text: str = Field(..., description="用户最新发言")
    context_summary: str = Field("", description="上文摘要，可为空")
    pre_analysis: str = Field("", description="预分析结果（JSON格式）")

class SeverityTool(BaseTool):
    name = "severity_analyzer"
    description = ("反恋爱脑工具：只有用户明确讨论恋爱相关话题时 或 预分析结果中level为“轻/中/重/危险”时，才会调用当前工具来生成毒舌锐评/情感分析回复。")
    args_schema: Type[BaseModel] = SeverityInput

    def _run(self, user_text: str, context_summary: str = "", pre_analysis: str = "") -> str:
        """恋爱脑程度识别器 - 简化版本，直接返回格式化prompt"""
        try:
            # 如果有预分析结果，直接返回格式化的结果
            if pre_analysis:
                try:
                    # 解析预分析结果
                    analysis_data = json.loads(pre_analysis)
                    
                    # 根据分析结果生成相应的回复
                    if analysis_data.get("switch_to_help", False):
                        # 危险情况，返回帮助建议
                        return self._generate_help_response(user_text, analysis_data, context_summary)
                    else:
                        # 其他情况，返回毒舌锐评
                        return self._generate_roast_response(user_text, analysis_data, context_summary)
                        
                except json.JSONDecodeError:
                    # 预分析结果解析失败，直接返回毒舌锐评
                    pass
            
            # 简化处理：直接返回毒舌锐评prompt
            return self._generate_roast_response(user_text, {"level": "轻"}, context_summary)
                    
        except Exception as e:
            # 全局错误处理
            return f"""姐🧠脑子宕机了！但姐建议你冷静一下🚬"""

    def _generate_help_response(self, user_text: str, analysis_data: dict, context_summary: str) -> str:
        """生成帮助建议回复"""
        from ..prompts.prompt_config import HELP_EXECUTION_PROMPT
        from ..core.config import llm
        
        prompt = HELP_EXECUTION_PROMPT.format(
            user_text=user_text,
            help_guide=HELP_INNER_GUIDE,
        )
        
        # 直接调用LLM生成回复
        llm_instance = llm(temperature=0.7)
        response = llm_instance.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)

    def _generate_roast_response(self, user_text: str, analysis_data: dict, context_summary: str) -> str:
        """生成毒舌锐评回复"""
        from ..prompts.prompt_config import ROAST_EXECUTION_PROMPT
        from ..core.config import llm
        
        level = analysis_data.get("level", "轻")
        
        prompt = ROAST_EXECUTION_PROMPT.format(
            user_text=user_text,
            level=level,
            roast_guide=ROAST_INNER_GUIDE,
        )
        
        # 直接调用LLM生成回复
        llm_instance = llm(temperature=0.7)
        response = llm_instance.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
