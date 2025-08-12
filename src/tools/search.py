from typing import Type, List, Tuple
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from serpapi import GoogleSearch
import os, re

class SearchInput(BaseModel):
    query: str = Field(..., description="检索关键词，例如：恋爱 骗局 已读不回 借钱")
    num: int = Field(5, description="返回结果条数，1-10")

def _source_type(url: str) -> str:
    url = url.lower()
    if any(k in url for k in ["gov.cn", "police", "ga.gov", "mps.gov"]):
        return "警方通报"
    if any(k in url for k in ["news", "xinhuanet", "people", "thepaper", "163.com", "sina.com", "sohu.com", "qq.com"]):
        return "新闻报道"
    if any(k in url for k in ["zhihu", "weibo", "bilibili", "douban", "xiaohongshu", "reddit"]):
        return "受害者分享/社区"
    return "网络信息"

def _clean(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def _summarize(items: List[Tuple[str, str]]) -> str:
    if not items:
        return "（未检索到可靠案例，请谨慎对待涉及转账/借款/裸聊/不对等付出的要求。）"
    points = []
    sources = set()
    for title, src_type in items[:3]:
        t = _clean(title)
        if t:
            points.append(t)
        sources.add(src_type)
    if not points:
        return "（检索到相关案例，核心风险：情感诱导+金钱索取/个人信息获取。来源：{}。）".format("、".join(sources) or "网络信息")
    main = "；".join(points[:2])
    return f"近期有相似情形被报道：{main}。来源：{ '、'.join(sorted(sources)) }。"

class SearchTool(BaseTool):
    name = "search_tool"
    description = ("当需要案例警示时使用。用 SerpAPI 检索，返回1-2句通俗摘要（不贴链接），并注明来源类型。")
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str, num: int = 5) -> str:
        api_key = os.getenv("SERPAPI_API_KEY", "")
        if not api_key:
            return "（示例摘要）多起“已读不回后借钱/投资”的恋爱骗局被警方/媒体披露，常以情感为由拖延与索取。来源：警方通报、新闻报道。"
        params = {"engine":"google","q":query,"api_key":api_key,"hl":"zh-CN","gl":"cn","num":max(1,min(10,num)),"safe":"active"}
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            organic = results.get("organic_results", []) or []
            items: List[Tuple[str, str]] = []
            for r in organic:
                title = r.get("title") or ""
                link = r.get("link") or ""
                src_type = _source_type(link)
                text = title
                if text:
                    items.append((text, src_type))
            return _summarize(items)
        except Exception:
            return "（检索暂不可用，请避免转账/借款/裸聊与不对等付出，若遭遇威胁请保留证据并寻求警方帮助。）"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError
