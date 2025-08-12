from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.agent import build_agent
import os

app = FastAPI(title="Anti Love Brain - 拽姐 Agent")
agent = build_agent()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatIn(BaseModel):
    input: str
    persona: str | None = None
    prev_score: int = 50

@app.get("/")
def root():
    """返回前端页面"""
    return FileResponse('static/index.html')

@app.get("/health")
def health():
    return {"status": "ok", "message": "服务器运行正常"}

@app.post("/reset")
def reset_session():
    """重置会话，清除聊天历史"""
    global agent
    agent = build_agent()  # 重新构建agent来清除历史
    return {"status": "success", "message": "会话已重置"}

@app.post("/chat")
def chat(inp: ChatIn):
    user_input = inp.input
    # 只有在明确提供 persona 且不为空时才添加海王模拟提示
    if inp.persona and inp.persona.strip():
        user_input += f"\n（海王人设：{inp.persona}，上一轮得分：{inp.prev_score}）"
    
    res = agent.invoke({ "input": user_input })
    return { "reply": res.get("output", ""), "raw": res }
