from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置LangSmith（必须在导入agent之前设置）
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "anti-love-test"
# LANGSMITH_API_KEY应该已经在.env文件中设置了

from src.agent import build_agent
from src.memory_factory import MemoryManagerFactory

app = FastAPI(title="Anti Love Brain - 拽姐 Agent")

# 记忆存储配置
MEMORY_STORAGE_TYPE = os.getenv("MEMORY_STORAGE_TYPE", "memory")  # "memory" 或 "redis"
ENABLE_IP_ISOLATION = os.getenv("ENABLE_IP_ISOLATION", "true").lower() == "true"

# 多用户记忆管理器字典
user_memory_managers = {}

def get_user_id_from_ip(client_ip: str) -> str:
    """根据IP地址生成用户ID"""
    if not ENABLE_IP_ISOLATION:
        return "default_user"
    
    # 对IP地址进行哈希，生成固定的用户ID
    # 这样同一个IP总是得到相同的用户ID
    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:12]
    return f"ip_{ip_hash}"

def get_memory_manager(user_id: str):
    """获取或创建用户的记忆管理器"""
    if user_id not in user_memory_managers:
        user_memory_managers[user_id] = MemoryManagerFactory.create_memory_manager(
            storage_type=MEMORY_STORAGE_TYPE,
            user_id=user_id,
            max_conversation_window=15
        )
    
    return user_memory_managers[user_id]

def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    # Railway等云平台通常通过X-Forwarded-For头传递真实IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 取第一个IP（真实客户端IP）
        return forwarded_for.split(",")[0].strip()
    
    # 其他代理头
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 直接连接
    return request.client.host

# 简单的使用限制（可选）
ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "false").lower() == "true"
MAX_REQUESTS_PER_HOUR = int(os.getenv("MAX_REQUESTS_PER_HOUR", "30"))
request_counts = defaultdict(list)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatIn(BaseModel):
    message: str  # 改为message，与前端保持一致
    persona: str | None = None
    history: list = []  # 添加history字段
    prev_score: int = 50

@app.get("/")
def root():
    """返回前端页面"""
    return FileResponse('static/index.html')

@app.get("/health")
def health():
    """健康检查 - 包含配置信息"""
    health_info = {
        "status": "ok", 
        "message": "服务器运行正常",
        "memory_storage": MEMORY_STORAGE_TYPE,
        "ip_isolation": ENABLE_IP_ISOLATION,
        "rate_limit": ENABLE_RATE_LIMIT,
        "active_users": len(user_memory_managers)
    }
    
    # 检查Redis连接（如果使用Redis）
    if MEMORY_STORAGE_TYPE == "redis":
        try:
            # 尝试创建一个临时记忆管理器来测试连接
            test_manager = MemoryManagerFactory.create_memory_manager(
                storage_type="redis",
                user_id="health_check"
            )
            if hasattr(test_manager, 'redis_client'):
                test_manager.redis_client.ping()
                health_info["redis_status"] = "connected"
            else:
                health_info["redis_status"] = "fallback_to_memory"
        except Exception as e:
            health_info["redis_status"] = f"error: {str(e)}"
    
    return health_info

@app.post("/reset")
def reset_session(request: Request):
    """重置会话，清除聊天历史"""
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_ip(client_ip)
    
    user_memory_manager = get_memory_manager(user_id)
    user_memory_manager.clear_session()
    
    return {
        "status": "success", 
        "message": "会话已重置，长期记忆已保留",
        "user_id": user_id,
        "client_ip": client_ip,
        "memory_stats": user_memory_manager.get_memory_stats()
    }

@app.get("/memory/stats")
def get_memory_stats_endpoint(request: Request):
    """获取内存使用统计"""
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_ip(client_ip)
    
    user_memory_manager = get_memory_manager(user_id)
    return user_memory_manager.get_memory_stats()

@app.get("/memory/summary")
def get_memory_summary_endpoint(request: Request):
    """获取对话摘要"""
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_ip(client_ip)
    
    user_memory_manager = get_memory_manager(user_id)
    return {
        "context_summary": user_memory_manager.get_context_summary(),
        "stats": user_memory_manager.get_memory_stats()
    }

@app.post("/chat")
def chat(inp: ChatIn, request: Request):
    # 获取用户IP和用户ID
    client_ip = get_client_ip(request)
    user_id = get_user_id_from_ip(client_ip)
    
    # 获取该用户的记忆管理器和agent
    user_memory_manager = get_memory_manager(user_id)
    user_agent = build_agent(user_memory_manager)
    
    # 可选的使用限制检查
    if ENABLE_RATE_LIMIT:
        now = datetime.now()
        
        # 清理1小时前的记录
        request_counts[user_id] = [
            req_time for req_time in request_counts[user_id] 
            if now - req_time < timedelta(hours=1)
        ]
        
        # 检查是否超过限制
        if len(request_counts[user_id]) >= MAX_REQUESTS_PER_HOUR:
            raise HTTPException(
                status_code=429, 
                detail=f"使用过于频繁，每小时最多{MAX_REQUESTS_PER_HOUR}次请求，请稍后再试"
            )
        
        # 记录本次请求
        request_counts[user_id].append(now)
    
    user_input = inp.message  # 使用message字段
    # 只有在明确提供 persona 且不为空时才添加海王模拟提示
    if inp.persona and inp.persona.strip():
        user_input += f"\n（海王人设：{inp.persona}，上一轮得分：{inp.prev_score}）"
    
    res = user_agent.invoke({ "input": user_input })
    
    # 提取恋爱脑指数
    love_brain_index = None
    love_brain_level = None
    risk_signals = []
    
    # 从agent的完整响应中查找severity_analyzer的调用结果
    if hasattr(res, 'get') and 'intermediate_steps' in res:
        # 遍历中间步骤，查找severity_analyzer的输出
        for step in res['intermediate_steps']:
            if len(step) >= 2:
                action, observation = step
                if hasattr(action, 'tool') and action.tool == 'severity_analyzer':
                    try:
                        # 解析severity_analyzer的JSON输出
                        severity_result = json.loads(observation)
                        love_brain_index = severity_result.get('index')
                        love_brain_level = severity_result.get('level')
                        risk_signals = severity_result.get('signals', [])
                        break
                    except (json.JSONDecodeError, AttributeError):
                        continue
    
    # 获取原始输出
    raw_output = res.get("output", "")
    
    # 处理海王模拟的特殊输出格式
    if inp.persona and inp.persona.strip():
        # 检查是否是海王模拟的JSON输出格式
        if raw_output.startswith('```tool_outputs') or 'seaking_tool_response' in raw_output:
            try:
                # 尝试提取JSON部分
                json_match = re.search(r'\{[^{}]*"seaking_tool_response"[^{}]*\}', raw_output)
                if json_match:
                    seaking_data = json.loads(json_match.group())
                    if 'results' in seaking_data['seaking_tool_response']:
                        raw_output = seaking_data['seaking_tool_response']['results'][0]
                else:
                    # 如果找不到JSON，尝试提取括号内的内容
                    bracket_match = re.search(r'\[(.*?)\]', raw_output)
                    if bracket_match:
                        raw_output = bracket_match.group(1)
            except (json.JSONDecodeError, AttributeError, KeyError):
                # 如果解析失败，保持原输出
                pass
    
    # 添加到记忆管理器
    user_memory_manager.add_interaction(
        user_input=inp.message,
        ai_response=raw_output,
        love_brain_level=love_brain_level,
        risk_signals=risk_signals
    )
    
    response = {
        "response": raw_output,
        "raw": res,
        "user_id": user_id,
        "client_ip": client_ip,
        "memory_stats": user_memory_manager.get_memory_stats()
    }
    
    # 如果成功提取到恋爱脑指数，添加到响应中
    if love_brain_index is not None:
        response["love_brain_index"] = love_brain_index
        response["love_brain_level"] = love_brain_level
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    # Railway会提供PORT环境变量，本地开发使用8889
    port = int(os.getenv("PORT", 8889))
    
    print(f"🚀 启动拽姐Agent服务")
    print(f"💾 记忆存储模式: {MEMORY_STORAGE_TYPE}")
    print(f"🌐 IP隔离模式: {ENABLE_IP_ISOLATION}")
    print(f"🔌 运行端口: {port}")
    
    if MEMORY_STORAGE_TYPE == "redis":
        print(f"🔗 Redis配置: {os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
