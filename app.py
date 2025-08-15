from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
import re
import random
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 加载环境变量
load_dotenv()

# 配置LangSmith（必须在导入agent之前设置）
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "anti-love-test"

# 修复导入路径
from src.core.agent import build_agent
from src.core.severity_analyzer import analyze_severity, SeverityResult
from src.memory.memory_manager import SmartMemoryManager
# 延迟导入SeakingTool以避免循环导入
# from src.tools.seaking import SeakingTool

app = FastAPI(title="Anti Love Brain - 拽姐 Agent")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 记忆存储配置
MEMORY_STORAGE_TYPE = os.getenv("MEMORY_STORAGE_TYPE", "memory")  # "memory" 或 "redis"
ENABLE_IP_ISOLATION = os.getenv("ENABLE_IP_ISOLATION", "true").lower() == "true"

# 检查是否为开发环境
IS_DEVELOPMENT = os.getenv("RAILWAY_ENVIRONMENT") is None and os.getenv("PORT") is None

print(f"[CONFIG] IP Isolation: {ENABLE_IP_ISOLATION}")
print(f"[CONFIG] Memory Storage: {MEMORY_STORAGE_TYPE}")
print(f"[CONFIG] Development Mode: {IS_DEVELOPMENT}")

# 🌊 海王对战人设库
SEAKING_PERSONAS = {
    "🌊对战海王": {
        "personas": [
            "ENTJ-霸道总裁型海王",
            "ENFP-温柔暖男型海王", 
            "ISTP-高冷学霸型海王",
            "ESFJ-社交达人型海王",
            "INTJ-神秘精英型海王"
        ],
        "default_gender": "男",
        "user_gender": "女",
        "challenge_type": "海王对战"
    },
    "🍵反茶艺大师": {
        "personas": [
            "ENFJ-绿茶心机型海王",
            "ISFP-白莲花型海王",
            "ESTJ-女王型海王",
            "INFP-文艺女神型海王", 
            "ENTP-毒舌女王型海王"
        ],
        "default_gender": "女",
        "user_gender": "男",
        "challenge_type": "茶艺大师"
    },
    "🌈决战通讯录之巅": {
        "personas": [
            "ENFP-彩虹暖男型海王",
            "ISTJ-精英同志型海王",
            "ESFP-派对王子型海王",
            "INFJ-文艺同志型海王",
            "ESTP-运动型海王"
        ],
        "default_gender": "男",
        "user_gender": "男", 
        "challenge_type": "通讯录之巅"
    }
}

def get_user_identifier(request: Request) -> str:
    """统一的用户标识获取函数"""
    if not ENABLE_IP_ISOLATION:
        return "default_user"
    
    # 在开发环境中，可以使用固定标识符以便调试
    if IS_DEVELOPMENT:
        # 开发环境下为了方便调试，使用固定用户标识
        return "dev_user"
    
    # 生产环境使用真实IP
    return request.client.host

# 用户记忆管理器 - 简化为直接使用Agent架构
user_memory_managers: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    message: str
    persona: str = ""
    history: list = []
    # 🌊 新增按钮参数支持
    button_type: Optional[str] = None  # "🌊对战海王" | "🍵反茶艺大师" | "🌈决战通讯录之巅" | "正常聊天"
    seaking_score: Optional[int] = 0  # 海王对战得分
    is_first_seaking: Optional[bool] = True  # 是否首次海王对战
    # 🌊 新增人设参数支持
    gender: Optional[str] = None  # 海王性别
    user_gender: Optional[str] = None  # 用户性别
    challenge_type: Optional[str] = None  # 挑战类型

def get_memory_manager(user_ip: str):
    """获取用户的记忆管理器和Agent"""
    if user_ip not in user_memory_managers:
        # 直接创建记忆管理器
        memory_manager = SmartMemoryManager(
            max_tokens=1500,
            summary_trigger_ratio=0.8
        )
        
        # 创建Agent
        agent = build_agent(memory_manager)
        
        # 存储记忆管理器和Agent
        user_memory_managers[user_ip] = {
            "memory_manager": memory_manager,
            "agent": agent
        }
    return user_memory_managers[user_ip]

def generate_seaking_persona(button_type: str) -> Dict[str, Any]:
    """根据按钮类型生成随机海王人设"""
    if button_type not in SEAKING_PERSONAS:
        return {
            "persona": "ENTJ-高阶PUA",
            "gender": "男",
            "user_gender": "女",
            "challenge_type": "海王对战"
        }
    
    config = SEAKING_PERSONAS[button_type]
    selected_persona = random.choice(config["personas"])
    
    return {
        "persona": selected_persona,
        "gender": config["default_gender"],
        "user_gender": config["user_gender"],
        "challenge_type": config["challenge_type"]
    }

def parse_seaking_score(ai_response: str, prev_score: int) -> tuple[int, bool]:
    """从AI回复中解析得分和胜利状态"""
    try:
        # 查找拽姐旁白中的得分信息
        import re
        
        # 匹配"当前得分：X分"或"得分：X分"的模式
        score_patterns = [
            r'当前得分[：:]\s*(\d+)分',
            r'得分[：:]\s*(\d+)分',
            r'(\d+)分'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, ai_response)
            if match:
                score = int(match.group(1))
                return score, score >= 100
        
        # 检查是否包含"恭喜通关"
        if "恭喜通关" in ai_response or "通关" in ai_response:
            return 100, True
        
        # 如果没有找到得分，根据回复质量估算
        if "拽姐旁白" in ai_response:
            # 简单估算：如果回复质量好，给10分
            return prev_score + 10, (prev_score + 10) >= 100
        
        return prev_score, prev_score >= 100
        
    except Exception as e:
        print(f"[Error] Parse seaking score failed: {e}")
        return prev_score, prev_score >= 100

@app.get("/")
async def read_index():
    """主页面"""
    response = FileResponse('static/index.html')
    if IS_DEVELOPMENT:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.post("/chat")
async def chat(request: ChatRequest, req: Request):
    """聊天端点 - 支持直接海王对战和正常Agent模式"""
    user_ip = get_user_identifier(req)
    
    try:
        user_session = get_memory_manager(user_ip)
        memory_manager = user_session["memory_manager"]
        agent = user_session["agent"]
        
        # 🌊 检查是否为海王对战模式
        if request.button_type and request.button_type in ["🌊对战海王", "🍵反茶艺大师", "🌈决战通讯录之巅"]:
            return await handle_seaking_mode(request, memory_manager, user_ip)
        
        # 正常聊天模式 - 使用原有逻辑
        return await handle_normal_chat(request, memory_manager, agent)
        
    except Exception as e:
        print(f"[Error] Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_seaking_mode(request: ChatRequest, memory_manager, user_ip: str):
    """处理海王对战模式"""
    print(f"=== handle_seaking_mode 被调用 ===")
    print(f"请求参数: button_type={request.button_type}, persona={request.persona}")
    try:
        # 使用前端传递的人设信息，如果没有则生成新的
        if request.persona and request.gender and request.user_gender and request.challenge_type:
            persona_config = {
                "persona": request.persona,
                "gender": request.gender,
                "user_gender": request.user_gender,
                "challenge_type": request.challenge_type
            }
        else:
            # 生成海王人设
            persona_config = generate_seaking_persona(request.button_type)
        
        # 延迟导入SeakingTool以避免循环导入
        from src.tools.seaking import SeakingTool
        seaking_tool = SeakingTool()
        
        # 准备输入参数
        seaking_input = {
            "user_text": request.message,
            "persona": persona_config["persona"],
            "prev_score": request.seaking_score,
            "is_first_seaking": request.is_first_seaking,
            "challenge_type": persona_config["challenge_type"],
            "gender": persona_config["gender"],
            "user_gender": persona_config["user_gender"]
        }
        
        # 直接调用SeakingTool
        ai_response = seaking_tool._run(**seaking_input)
        
        # 从AI回复中解析得分和胜利状态
        new_score, is_victory = parse_seaking_score(ai_response, request.seaking_score)
        
        # 更新记忆（海王对战模式下的简化记忆）
        memory_manager.add_interaction(
            user_input=request.message,
            ai_response=ai_response,
            love_brain_level="海王对战",
            risk_signals=["海王对战模式"]
        )
        
        return {
            "response": ai_response,
            "love_brain_index": 0,  # 海王对战模式下不计算恋爱脑指数
            "love_brain_level": "海王对战",
            "risk_signals": ["海王对战模式"],
            "memory_stats": memory_manager.get_memory_stats(),
            "seaking_mode": {
                "button_type": request.button_type,
                "persona": persona_config["persona"],
                "challenge_type": persona_config["challenge_type"],
                "current_score": new_score,
                "is_victory": is_victory,
                "is_first_seaking": request.is_first_seaking
            },
            "routing_info": {
                "routing_type": "direct_seaking_tool",
                "success": True,
                "confidence": 1.0
            },
            "performance": {
                "token_saved": True,
                "processing_time_ms": 0,
                "routing_efficiency": 1.0
            }
        }
        
    except Exception as e:
        print(f"[Error] Seaking mode failed: {e}")
        return {
            "response": "海王对战系统暂时故障，请稍后再试...🚬",
            "love_brain_index": 0,
            "love_brain_level": "海王对战",
            "risk_signals": [],
            "memory_stats": memory_manager.get_memory_stats(),
            "seaking_mode": {
                "button_type": request.button_type,
                "error": True
            }
        }

async def handle_normal_chat(request: ChatRequest, memory_manager, agent):
    """处理正常聊天模式"""
    # 获取记忆上下文
    memory_context = memory_manager.get_memory_context_for_tool()
    
    # 🚀 异步severity分析 - Agent调用前的预处理器
    severity_result = await analyze_severity(request.message, memory_context)
    
    # 准备传递给Agent的输入
    if memory_context and memory_context != "无历史记忆":
        # 检查上下文长度，避免过长
        if len(memory_context) > 200:
            memory_context = memory_context[:197] + "..."
        combined_input = f"记忆上下文: {memory_context}\n用户输入: {request.message}"
    else:
        # 没有历史记忆时，直接使用用户输入
        combined_input = request.message
    
    # 如果是海王模拟模式，添加persona信息
    if request.persona and request.persona.strip():
        combined_input += f"\n\n海王人设: {request.persona}"
    
    # 将预分析结果传递给Agent，用于智能路由
    pre_analysis_json = severity_result.model_dump_json()
    combined_input += f"\n\n预分析结果: {pre_analysis_json}"
    
    # 直接调用Agent处理
    result = agent.invoke({
        "input": combined_input
    })
    ai_response = result.get("output", "处理失败，请重试")
    
    # 使用预分析结果，无需从中间步骤解析
    love_brain_index = severity_result.index
    love_brain_level = severity_result.level
    risk_signals = severity_result.signals
    
    # 更新记忆中的对话记录
    memory_manager.add_interaction(
        user_input=request.message,
        ai_response=ai_response,
        love_brain_level=love_brain_level,
        risk_signals=risk_signals
    )
    
    # 获取记忆统计
    memory_stats = memory_manager.get_memory_stats()
    
    return {
        "response": ai_response,
        "love_brain_index": love_brain_index,
        "love_brain_level": love_brain_level,
        "risk_signals": risk_signals,
        "memory_stats": memory_stats,
        "severity_analysis": {
            "confidence": severity_result.confidence,
            "switch_to_help": severity_result.switch_to_help
        },
        "routing_info": {
            "routing_type": "async_severity_agent",
            "final_tools": ["agent"],
            "success": True,
            "confidence": 1.0
        },
        "performance": {
            "token_saved": True,
            "processing_time_ms": 0,
            "routing_efficiency": 1.0
        },
        "debug_info": {} if os.getenv("DEBUG", "false").lower() != "true" else {
            "architecture": "async_severity_agent",
            "memory_type": MEMORY_STORAGE_TYPE,
            "ip_isolation": ENABLE_IP_ISOLATION,
            "pre_analysis_used": severity_result.index > 0
        }
    }

@app.post("/reset")
async def reset_chat(req: Request):
    """重置端点 - 清除短期记忆"""
    user_ip = get_user_identifier(req)
    
    try:
        user_session = get_memory_manager(user_ip)
        memory_manager = user_session["memory_manager"]
        
        # 重置记忆
        memory_manager.clear_session()
        
        # 重新创建Agent (确保使用新的记忆状态)
        agent = build_agent(memory_manager)
        user_memory_managers[user_ip]["agent"] = agent
        
        return {
            "message": "会话已重置，短期记忆已清除",
            "memory_stats": memory_manager.get_memory_stats(),
            "routing_enabled": False,  # 现在使用直接Agent架构
            "architecture": "direct_agent"
        }
    except Exception as e:
        print(f"[Error] Reset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def get_system_status(req: Request):
    """系统状态端点 - 显示路由和记忆状态"""
    user_ip = get_user_identifier(req)
    
    try:
        user_session = get_memory_manager(user_ip)
        memory_manager = user_session["memory_manager"]
        
        return {
            "status": "running",
            "memory_status": memory_manager.get_memory_stats(),
            "system_config": {
                "enhanced_routing_enabled": False, # 移除未使用的配置
                "ip_isolation_enabled": ENABLE_IP_ISOLATION,
                "memory_storage_type": MEMORY_STORAGE_TYPE,
                "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
            }
        }
    except Exception as e:
        print(f"[Error] Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/routing/stats")
async def get_routing_stats():
    """路由统计端点 - 显示全局路由性能"""
    try:
        return {
            "total_users": len(user_memory_managers),
            "enhanced_routing_enabled": False, # 移除未使用的配置
            "architecture": "direct_agent",
            "per_user_stats": {}
        }
    except Exception as e:
        print(f"[Error] Routing stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/stats")
async def get_memory_stats(request: Request):
    """获取记忆统计信息 - 供前端记忆按钮使用"""
    try:
        user_ip = get_user_identifier(request)
        user_session = get_memory_manager(user_ip)
        
        # 获取记忆统计
        memory_stats = user_session["memory_manager"].get_memory_stats()
        
        return {
            "conversation_count": memory_stats.get("conversation_count", 0),
            "estimated_tokens": memory_stats.get("estimated_tokens", 0),
            "max_tokens": memory_stats.get("max_tokens", 1000),
            "memory_usage_ratio": memory_stats.get("token_usage_ratio", 0),
            "user_patterns": memory_stats.get("user_patterns", {}),
            "pattern_count": memory_stats.get("pattern_count", 0),
            "short_term_count": memory_stats.get("short_term_count", 0),
            "long_term_count": memory_stats.get("long_term_count", 0)
        }
    except Exception as e:
        print(f"[Error] Memory stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/summary")
async def get_memory_summary(request: Request):
    """获取记忆详情摘要 - 供前端记忆按钮点击时显示"""
    try:
        user_ip = get_user_identifier(request)
        user_session = get_memory_manager(user_ip)
        
        # 获取记忆统计和上下文摘要
        memory_stats = user_session["memory_manager"].get_memory_stats()
        context_summary = user_session["memory_manager"].get_context_summary()
        
        # 获取长期记忆详细信息
        long_term_memory = user_session["memory_manager"].long_term_memory
        
        # 获取用户画像总结
        user_profile = user_session["memory_manager"].get_user_profile_summary()
        
        return {
            "stats": {
                "conversation_count": memory_stats.get("conversation_count", 0),
                "estimated_tokens": memory_stats.get("estimated_tokens", 0),
                "max_tokens": memory_stats.get("max_tokens", 1000),
                "memory_usage_ratio": memory_stats.get("memory_usage_ratio", 0),
                "user_patterns": memory_stats.get("user_patterns", {}),
                "pattern_count": memory_stats.get("pattern_count", 0),
                "short_term_count": memory_stats.get("short_term_count", 0),
                "long_term_count": memory_stats.get("long_term_count", 0)
            },
            "context_summary": context_summary or "暂无记忆上下文",
            "long_term_details": {
                "risk_history": long_term_memory.get("risk_history", []),
                "user_patterns": long_term_memory.get("user_patterns", {}),
                "key_insights": long_term_memory.get("key_insights", []),
                "persona_preferences": long_term_memory.get("persona_preferences", {})
            },
            "user_profile": user_profile
        }
    except Exception as e:
        print(f"[Error] Memory summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/seaking/personas")
async def get_seaking_personas():
    """获取海王人设库 - 供前端使用"""
    try:
        return {
            "personas": SEAKING_PERSONAS,
            "button_types": list(SEAKING_PERSONAS.keys()),
            "default_config": {
                "🌊对战海王": {
                    "default_gender": "男",
                    "user_gender": "女",
                    "challenge_type": "海王对战"
                },
                "🍵反茶艺大师": {
                    "default_gender": "女", 
                    "user_gender": "男",
                    "challenge_type": "茶艺大师"
                },
                "🌈决战通讯录之巅": {
                    "default_gender": "男",
                    "user_gender": "男", 
                    "challenge_type": "通讯录之巅"
                }
            }
        }
    except Exception as e:
        print(f"[Error] Get seaking personas failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/favicon.ico")
async def favicon():
    return FileResponse('static/favicon.svg')

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动 Anti Love Brain Agent")
    print(f"📊 增强路由: {'✅ 启用' if False else '❌ 禁用'}") # 移除未使用的配置
    print(f"🌐 IP隔离: {'✅ 启用' if ENABLE_IP_ISOLATION else '❌ 禁用'}")
    print(f"💾 记忆存储: {MEMORY_STORAGE_TYPE}")
    print("-" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
