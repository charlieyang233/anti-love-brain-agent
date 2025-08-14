from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from serpapi import GoogleSearch
import os
from ..config import llm
from ..prompt_config import SEARCH_KEYWORDS_TEMPLATES, SEARCH_SUMMARY_PROMPT

class SearchInput(BaseModel):
    query: str = Field(..., description="检索关键词，例如：恋爱 骗局 已读不回 借钱")
    risk_category: str = Field("", description="风险类别，用于优化搜索关键词")
    num: int = Field(3, description="返回结果条数，1-5")

def _detect_risk_category(query: str) -> str:
    """基于用户输入检测风险类别，匹配SEARCH_KEYWORDS_TEMPLATES"""
    query_lower = query.lower()
    
    # 检测恋爱诈骗
    if any(word in query_lower for word in ["骗", "转账", "借钱", "投资", "诈骗", "骗局", "骗钱"]):
        return "恋爱诈骗"
    
    # 检测PUA识别
    if any(word in query_lower for word in ["pua", "操控", "套路", "控制", "精神", "情感操控"]):
        return "PUA识别"
    
    # 检测网恋风险
    if any(word in query_lower for word in ["网恋", "见面", "线上", "虚假身份", "网友"]):
        return "网恋风险"
    
    # 检测金钱纠纷
    if any(word in query_lower for word in ["不还", "经济纠纷", "借贷", "投资", "金钱"]):
        return "金钱纠纷"
    
    # 检测安全威胁
    if any(word in query_lower for word in ["威胁", "暴力", "骚扰", "stalking", "分手", "恐吓"]):
        return "安全威胁"
    
    # 广义恋爱风险 - 默认归类到恋爱诈骗
    if any(word in query_lower for word in ["恋爱", "感情", "男友", "女友", "对象"]):
        return "恋爱诈骗"
    
    return ""

def _get_search_results(keywords: str, num: int = 3) -> list:
    """调用搜索API获取结果"""
    api_key = os.getenv("SERPAPI_API_KEY", "")
    if not api_key:
        return []
    
    params = {
        "engine": "google",
        "q": keywords,
        "api_key": api_key,
        "hl": "zh-CN",
        "gl": "cn",
        "num": min(5, max(1, num)),
        "safe": "active"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            return []
        
        organic = results.get("organic_results", [])
        search_results = []
        
        for r in organic[:num]:
            title = r.get("title", "")
            link = r.get("link", "")
            snippet = r.get("snippet", "")  # 获取搜索结果摘要
            if title:
                # 简单判断来源类型
                source_type = "新闻报道"
                if any(k in link.lower() for k in ["gov.cn", "police"]):
                    source_type = "警方通报"
                elif any(k in link.lower() for k in ["zhihu", "weibo"]):
                    source_type = "受害者分享"
                
                search_results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,  # 包含摘要内容
                    "source_type": source_type
                })
        
        return search_results
        
    except Exception:
        return []

def _generate_evidence(search_results: list, risk_category: str) -> str:
    """使用LLM+SEARCH_SUMMARY_PROMPT生成evidence"""
    if not search_results:
        return f"未检索到具体案例，但{risk_category}风险需要警惕。"
    
    # 格式化搜索结果
    formatted_results = []
    for r in search_results:
        result_text = f"标题：{r['title']}\n来源：{r['source_type']}"
        if r.get('snippet'):
            result_text += f"\n内容：{r['snippet']}"
        formatted_results.append(result_text)
    
    search_results_text = "\n\n".join(formatted_results)
    
    try:
        # 使用SEARCH_SUMMARY_PROMPT
        prompt = SEARCH_SUMMARY_PROMPT.format(
            search_results=search_results_text,
            risk_category=risk_category
        )
        
        response = llm().invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        if content and len(content.strip()) > 5:
            return content.strip()
        else:
            return f"相关{risk_category}案例已被多次报道，需保持警惕。(来源：网络搜索)"
            
    except Exception:
        return f"相关{risk_category}案例已被多次报道，需保持警惕。(来源：网络搜索)"

class SearchTool(BaseTool):
    name = "search_tool"
    description = ("🔍 案例检索工具：当severity_analyzer检测到【重度/危险】等级需要案例警示时使用。"
                   "用SerpAPI检索恋爱诈骗、PUA识别、网恋风险、金钱纠纷、安全威胁等相关案例，生成evidence用于roast_tool和help_tool的案例警示。")
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, risk_category: str = "", num: int = 3) -> str:
        # 1. 检测风险类别
        detected_category = _detect_risk_category(query)
        
        # 2. 如果LLM提供了risk_category，尝试映射到预定义类别
        if risk_category:
            risk_lower = risk_category.lower()
            # 智能映射非预定义类别
            if "骗" in risk_lower or "欺骗" in risk_lower or "诈骗" in risk_lower:
                detected_category = "恋爱诈骗"
            elif "pua" in risk_lower or "操控" in risk_lower or "控制" in risk_lower:
                detected_category = "PUA识别"
            elif "网恋" in risk_lower or "网友" in risk_lower:
                detected_category = "网恋风险"
            elif "金钱" in risk_lower or "借钱" in risk_lower or "经济" in risk_lower:
                detected_category = "金钱纠纷"
            elif "威胁" in risk_lower or "暴力" in risk_lower or "安全" in risk_lower:
                detected_category = "安全威胁"
        
        # 3. 如果仍未找到合适类别，默认使用恋爱诈骗
        if not detected_category or detected_category not in SEARCH_KEYWORDS_TEMPLATES:
            detected_category = "恋爱诈骗"
        
        # 4. 获取对应的搜索关键词
        keywords = SEARCH_KEYWORDS_TEMPLATES[detected_category][0]
        
        # 5. 调用搜索API
        search_results = _get_search_results(keywords, num)
        
        # 6. 使用LLM+SEARCH_SUMMARY_PROMPT生成evidence
        evidence = _generate_evidence(search_results, detected_category)
        
        return evidence

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
