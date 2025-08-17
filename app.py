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

# 导入配置管理
from src.core.app_config import AppConfig

# 配置LangSmith（必须在导入agent之前设置）
AppConfig.setup_langsmith()

# 修复导入路径
from src.core.agent import build_agent
from src.core.severity_analyzer import SeverityResult, severity_analyzer
from src.memory.memory_manager import SmartMemoryManager

app = FastAPI(title="Anti Love Brain - 拽姐 Agent")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 打印配置信息
AppConfig.print_startup_info()

def get_user_identifier(request: Request) -> str:
    """统一的用户标识获取函数"""
    print(f"[DEBUG] ===== 用户标识获取 =====")
    print(f"[DEBUG] ENABLE_IP_ISOLATION: {AppConfig.ENABLE_IP_ISOLATION}")
    print(f"[DEBUG] IS_DEVELOPMENT: {AppConfig.IS_DEVELOPMENT}")
    print(f"[DEBUG] RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
    print(f"[DEBUG] PORT: {os.getenv('PORT')}")
    
    if not AppConfig.ENABLE_IP_ISOLATION:
        print(f"[DEBUG] IP隔离禁用，使用default_user")
        return "default_user"
    
    # 在开发环境中，可以使用固定标识符以便调试
    if AppConfig.IS_DEVELOPMENT:
        # 开发环境下为了方便调试，使用固定用户标识
        print(f"[DEBUG] 开发环境，使用dev_user")
        return "dev_user"
    
    # 生产环境：优先使用X-Forwarded-For头部，避免VPN导致的IP变化问题
    # 如果VPN导致IP频繁变化，可以考虑使用其他稳定的标识方式
    user_ip = request.headers.get("X-Forwarded-For", request.client.host)
    if "," in user_ip:
        # X-Forwarded-For可能包含多个IP，取第一个
        user_ip = user_ip.split(",")[0].strip()
    
    # VPN兼容方案：如果检测到IP变化频繁，使用更稳定的标识
    # 这里可以添加基于User-Agent或其他稳定特征的标识逻辑
    # 暂时先使用IP，但添加VPN检测提示
    
    print(f"[DEBUG] 生产环境，使用IP: {user_ip}")
    print(f"[DEBUG] X-Forwarded-For: {request.headers.get('X-Forwarded-For', 'None')}")
    print(f"[DEBUG] Client Host: {request.client.host}")
    print(f"[DEBUG] User-Agent: {request.headers.get('User-Agent', 'None')[:50]}...")
    print(f"[DEBUG] ===== 用户标识获取完成 =====")
    return user_ip

# 用户记忆管理器 - 简化为直接使用Agent架构
user_memory_managers: Dict[str, Any] = {}

# 海王对战历史管理 - 只保存上一轮对话
seaking_last_conversations: Dict[str, str] = {}

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
    description: Optional[str] = None  # 人设描述
    style: Optional[str] = None  # 人设风格
    weakness: Optional[str] = None  # 人设弱点

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
    personas_data = AppConfig.load_personas()
    
    if button_type not in personas_data:
        return {
            "persona": "ENTJ-高阶PUA",
            "gender": "男",
            "user_gender": "女",
            "challenge_type": "海王对战",
            "description": "以刺激、新鲜感制造情绪过山车，擅长用“临时计划+高频邀约”建立优势地位，习惯在临界亲密前切换目标。",
            "style": "夜生活达人、运动控、擅长即兴决策与肢体语言",
            "weakness": "耐心差、厌倦快，深度关系维护能力低"
        }
    
    config = personas_data[button_type]
    if "personas" in config and config["personas"]:
        selected_persona = random.choice(config["personas"])
        return {
            "persona": selected_persona.get("name", "ENTJ-高阶PUA"),
            "gender": selected_persona.get("gender", "男"),
            "user_gender": selected_persona.get("user_gender", "女"),
            "challenge_type": selected_persona.get("challenge_type", "海王对战"),
            "description": selected_persona.get("description", "以刺激、新鲜感制造情绪过山车，擅长用“临时计划+高频邀约”建立优势地位，习惯在临界亲密前切换目标。"),
            "style": selected_persona.get("style", "夜生活达人、运动控、擅长即兴决策与肢体语言"),
            "weakness": selected_persona.get("weakness", "耐心差、厌倦快，深度关系维护能力低")
        }
    
    # 降级处理
    return {
        "persona": "ENTJ-高阶PUA",
        "gender": "男",
        "user_gender": "女",
        "challenge_type": "海王对战",
        "description": "以刺激、新鲜感制造情绪过山车，擅长用“临时计划+高频邀约”建立优势地位，习惯在临界亲密前切换目标。",
        "style": "夜生活达人、运动控、擅长即兴决策与肢体语言",
        "weakness": "耐心差、厌倦快，深度关系维护能力低"
    }

def parse_seaking_score(ai_response: str, prev_score: int, is_first_round: bool = False) -> tuple[int, bool]:
    """从AI回复中解析得分和胜利状态"""
    try:
        print(f"[DEBUG] 解析得分 - AI回复: {ai_response[:200]}...")
        print(f"[DEBUG] 解析得分 - 上轮得分: {prev_score}")
        
        # 检查是否通关
        if "🎉恭喜挑战成功" in ai_response or "恭喜通关" in ai_response:
            print(f"[DEBUG] 检测到通关信息")
            return 100, True
        
        # 检查是否是第一轮对话（基于对话历史判断）
        if is_first_round:
            print(f"[DEBUG] 检测到第一轮对话，保持得分为0")
            return 0, False
        
        # 更精确的得分匹配模式 - 专门匹配拽姐旁白中的得分
        score_patterns = [
            r'【拽姐旁白】.*?当前得分[：:]\s*(\d+)',  # 匹配拽姐旁白中的当前得分
            r'当前得分[：:]\s*(\d+)',  # 匹配当前得分
            r'得分[：:]\s*(\d+)'  # 匹配得分
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, ai_response)
            if match:
                score = int(match.group(1))
                print(f"[DEBUG] 成功解析得分: {score} (使用模式: {pattern})")
                return score, score >= 100
        
        # 如果没有找到明确的得分，保持原得分不变
        print(f"[DEBUG] 未找到得分信息，保持原得分: {prev_score}")
        return prev_score, prev_score >= 100
        
    except Exception as e:
        print(f"[Error] Parse seaking score failed: {e}")
        print(f"[DEBUG] 异常情况，返回原得分: {prev_score}")
        return prev_score, prev_score >= 100

@app.get("/")
async def read_index():
    """主页面"""
    response = FileResponse('static/index_modern.html')
    if AppConfig.IS_DEVELOPMENT:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.get("/chat")
async def read_chat():
    """聊天页面"""
    response = FileResponse('static/chat.html')
    if AppConfig.IS_DEVELOPMENT:
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
        if request.button_type and AppConfig.is_seaking_mode(request.button_type):
            return await handle_seaking_mode(request, memory_manager, user_ip)
        
        # 正常聊天模式 - 使用同步优化逻辑
        return handle_normal_chat(request, memory_manager, agent)
        
    except Exception as e:
        print(f"[Error] Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_seaking_mode(request: ChatRequest, memory_manager, user_ip: str):
    """处理海王对战模式"""
    print(f"=== handle_seaking_mode 被调用 ===")
    print(f"请求参数: button_type={request.button_type}, persona={request.persona}")
    try:
        # 使用前端传递的人设信息，如果没有则生成新的
        if request.persona and request.gender and request.user_gender and request.challenge_type and request.description and request.style and request.weakness:
            # 前端已传递完整人设信息，直接使用
            persona_config = {
                "persona": request.persona,
                "gender": request.gender,
                "user_gender": request.user_gender,
                "challenge_type": request.challenge_type,
                "description": request.description,
                "style": request.style,
                "weakness": request.weakness
            }
            print(f"[DEBUG] 使用前端传递的人设: {request.persona}")
        else:
            # 生成海王人设（通常只在第一次切换模式时发生）
            persona_config = generate_seaking_persona(request.button_type)
            print(f"[DEBUG] 生成新的随机人设: {persona_config['persona']}")
        
        # 使用新的SeakingChain
        from src.tools.seaking import SeakingChain
        seaking_chain = SeakingChain()
        
        # 获取上一轮对话 - 使用后端独立维护的海王对话历史
        last_conversation = seaking_last_conversations.get(user_ip, "（这是第一轮对话）")
        is_first_round = last_conversation == "（这是第一轮对话）"
        print(f"[DEBUG] ===== 海王模式对话历史检查 =====")
        print(f"[DEBUG] 用户IP: {user_ip}")
        print(f"[DEBUG] 当前seaking_last_conversations内容: {dict(seaking_last_conversations)}")
        print(f"[DEBUG] 本用户的上一轮对话: {repr(last_conversation)}")
        print(f"[DEBUG] 是否为第一轮: {is_first_round}")
        print(f"[DEBUG] ===== 对话历史检查结束 =====")
        
        # 直接调用SeakingChain
        ai_response = seaking_chain.run(
            persona=persona_config["persona"],
            user_input=request.message,
            current_score=request.seaking_score,
            challenge_type=persona_config["challenge_type"],
            # 传入海王性别、用户性别
            gender=persona_config["gender"],
            user_gender=persona_config["user_gender"],
            description=persona_config["description"],
            style=persona_config["style"],
            weakness=persona_config["weakness"],
            last_conversation=last_conversation
        )
        
        # 从AI回复中解析得分和胜利状态
        new_score, is_victory = parse_seaking_score(ai_response, request.seaking_score, is_first_round)
        print(f"[DEBUG] 海王得分处理结果: 原得分={request.seaking_score}, 新得分={new_score}, 是否通关={is_victory}")
        
        # 检查是否通关
        if "🎉恭喜挑战成功" in ai_response:
            is_victory = True
            new_score = 100
            print(f"[DEBUG] 检测到通关消息，强制设置得分为100")
            # 通关后清除对话历史
            seaking_last_conversations.pop(user_ip, None)
        else:
            # 保存当前对话历史供下一轮使用
            # 无论是否第一轮，都需要保存本轮对话给下轮使用
            
            # 提取海王的回复（在【海王】和【拽姐旁白】之间的内容）
            seaking_reply = ""
            if "【海王】" in ai_response:
                # 提取海王回复部分
                seaking_part = ai_response.split("【海王】")[1]
                if "【拽姐旁白】" in seaking_part:
                    seaking_reply = seaking_part.split("【拽姐旁白】")[0].strip()
                else:
                    seaking_reply = seaking_part.strip()
                # 清理格式，移除人设名称前缀
                if "：" in seaking_reply:
                    seaking_reply = seaking_reply.split("：", 1)[1].strip()
            
            # 保存格式：海王回复 + 用户回复
            conversation_record = f"海王：{seaking_reply}\n用户：{request.message}"
            seaking_last_conversations[user_ip] = conversation_record
            print(f"[DEBUG] ===== 对话历史保存详情 =====")
            print(f"[DEBUG] 用户IP: {user_ip}")
            print(f"[DEBUG] 海王回复: \"{seaking_reply}\"")
            print(f"[DEBUG] 用户消息: \"{request.message}\"")
            print(f"[DEBUG] 完整对话记录: \"{conversation_record}\"")
            print(f"[DEBUG] 保存后的seaking_last_conversations: {dict(seaking_last_conversations)}")
            print(f"[DEBUG] ===== 对话历史保存完成 =====")
        
        # 海王对战模式不更新全局记忆，避免影响正常聊天
        
        return {
            "response": ai_response,
            "love_brain_index": 0,  # 海王对战模式下不计算恋爱脑指数
            "love_brain_level": "海王对战",
            "risk_signals": ["海王对战模式"],
            "memory_stats": memory_manager.get_memory_stats(),  # 保持原有记忆状态
            "seaking_mode": {
                "button_type": request.button_type,
                "persona": persona_config["persona"],
                "challenge_type": persona_config["challenge_type"],
                "current_score": new_score,
                "is_victory": is_victory,
                "is_first_seaking": False  # 新的Chain不需要首次对话概念
            },
            "routing_info": {
                "routing_type": "direct_seaking_tool",
                "success": True
            },
            "performance": {
                "token_saved": True,
                "processing_time_ms": 0
            }
        }
        
    except Exception as e:
        print(f"[Error] Seaking mode failed: {e}")
        return {
            "response": "海王对战系统暂时故障，请稍后再试...🚬",
            "love_brain_index": 0,
            "love_brain_level": "海王对战",
            "risk_signals": [],
            "memory_stats": memory_manager.get_memory_stats(),  # 保持原有记忆状态
            "seaking_mode": {
                "button_type": request.button_type,
                "error": True
            }
        }

def handle_normal_chat(request: ChatRequest, memory_manager, agent):
    """处理正常聊天模式 - 全同步架构，简化设计"""
    import time
    
    print(f"[DEBUG] handle_normal_chat 被调用，使用全同步架构")
    
    # 开始性能计时
    start_time = time.time()
    
    # 获取记忆上下文
    memory_context = memory_manager.get_memory_context_for_tool()
    
    # 🚀 同步severity分析 + 动态人设选择
    analysis_start = time.time()
    analysis_result = severity_analyzer.analyze_with_answerstyle(request.message, memory_context)
    analysis_time = time.time() - analysis_start
    
    severity_result = SeverityResult(**analysis_result["severity"])
    
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
    
    # 🎯 构建带动态人设的Agent
    agent_build_start = time.time()
    enhanced_agent = build_agent(
        memory_manager=memory_manager,
        answer_style=analysis_result["dynamic_prompt"]
    )
    agent_build_time = time.time() - agent_build_start
    
    # 注意：预分析结果已通过动态人设注入到Agent的system prompt中，无需重复传递
    
    # 🎯 执行带动态人设的Agent
    agent_exec_start = time.time()
    result = enhanced_agent.invoke({
        "input": combined_input
    })
    agent_exec_time = time.time() - agent_exec_start
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
    
    # 计算总耗时
    total_time = time.time() - start_time
    
    return {
        "response": ai_response,
        "love_brain_index": love_brain_index,
        "love_brain_level": love_brain_level,
        "risk_signals": risk_signals,
        "memory_stats": memory_stats,
        # "severity_analysis": 已合并到顶层字段，避免重复数据
        # "answerstyle_used": 前端未使用，已移除避免数据冗余
        "routing_info": {
            "routing_type": "sync_dynamic_persona_agent",
            "success": True
        },
        "performance": {
            "total_time_ms": int(total_time * 1000),
            "analysis_time_ms": int(analysis_time * 1000),
            "agent_build_time_ms": int(agent_build_time * 1000),
            "agent_exec_time_ms": int(agent_exec_time * 1000),
            "architecture": "sync_optimized",
            "routing_efficiency": 1.0
        },
        "debug_info": {} if os.getenv("DEBUG", "false").lower() != "true" else {
            "architecture": "sync_dynamic_persona_agent",
            "memory_type": AppConfig.MEMORY_STORAGE_TYPE,
            "ip_isolation": AppConfig.ENABLE_IP_ISOLATION,
            "pre_analysis_used": severity_result.index > 0,
            "selected_persona_preview": analysis_result["answerstyle"]["roleset"][:50] + "...",
            "performance_breakdown": {
                "analysis_percentage": int((analysis_time / total_time) * 100),
                "agent_build_percentage": int((agent_build_time / total_time) * 100),
                "agent_exec_percentage": int((agent_exec_time / total_time) * 100)
            }
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
        
        # 清除海王对战历史
        seaking_last_conversations.pop(user_ip, None)
        
        # 重新创建Agent (确保使用新的记忆状态)
        agent = build_agent(memory_manager)
        user_memory_managers[user_ip]["agent"] = agent
        
        return {
            "message": "会话已重置，短期记忆已清除",
            "memory_stats": memory_manager.get_memory_stats(),
            "routing_enabled": False,
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
                "enhanced_routing_enabled": False,
                "ip_isolation_enabled": AppConfig.ENABLE_IP_ISOLATION,
                "memory_storage_type": AppConfig.MEMORY_STORAGE_TYPE,
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
            "enhanced_routing_enabled": False,
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
        # 从 JSON 文件读取人设配置
        personas_file = os.path.join("static", "personas.json")
        with open(personas_file, 'r', encoding='utf-8') as f:
            personas_data = json.load(f)
        
        # 直接返回人设数据，保持与前端期望的结构一致
        return personas_data
    except Exception as e:
        print(f"[Error] Get seaking personas failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查端点 - Railway部署需要"""
    return {"status": "healthy", "service": "anti-love-brain-agent"}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse('static/favicon.svg')

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动 Anti Love Brain Agent")
    print(f"📊 增强路由: {'✅ 启用' if False else '❌ 禁用'}")
    print(f"🌐 IP隔离: {'✅ 启用' if AppConfig.ENABLE_IP_ISOLATION else '❌ 禁用'}")
    print(f"💾 记忆存储: {AppConfig.MEMORY_STORAGE_TYPE}")
    print("-" * 50)
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
