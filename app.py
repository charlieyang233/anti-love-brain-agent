from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.agent import build_agent
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = FastAPI(title="Anti Love Brain - 拽姐 Agent")
agent = build_agent()

# 简单的使用限制（可选）
ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "false").lower() == "true"
MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "30"))
request_counts = defaultdict(list)

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
    # 可选的使用限制检查
    if ENABLE_RATE_LIMIT:
        client_id = "default"  # 在真实应用中可以用IP或用户ID
        now = datetime.now()
        
        # 清理1小时前的记录
        request_counts[client_id] = [
            req_time for req_time in request_counts[client_id] 
            if now - req_time < timedelta(hours=1)
        ]
        
        # 检查是否超过限制
        if len(request_counts[client_id]) >= MAX_REQUESTS_PER_HOUR:
            raise HTTPException(
                status_code=429, 
                detail=f"使用过于频繁，每小时最多{MAX_REQUESTS_PER_HOUR}次请求，请稍后再试"
            )
        
        # 记录本次请求
        request_counts[client_id].append(now)
    
    user_input = inp.input
    # 只有在明确提供 persona 且不为空时才添加海王模拟提示
    if inp.persona and inp.persona.strip():
        user_input += f"\n（海王人设：{inp.persona}，上一轮得分：{inp.prev_score}）"
    
    res = agent.invoke({ "input": user_input })
    return { "reply": res.get("output", ""), "raw": res }
