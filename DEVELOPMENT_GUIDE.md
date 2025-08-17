# 🚀 Anti Love Brain Agent - 开发指南

> **基于Session记忆系统的高性能反恋爱脑智能助手**  
> 支持海王对战模式、智能记忆管理和多用户隔离

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Session Memory](https://img.shields.io/badge/Memory-Session%20Based-blue.svg)]()
[![Seaking Mode](https://img.shields.io/badge/Mode-Seaking%20Battle-orange.svg)]()

## 📋 目录

- [🎯 项目概述](#-项目概述)
- [🏗️ 系统架构](#️-系统架构)
- [🚀 核心功能](#-核心功能)
- [💾 记忆系统](#-记忆系统)
- [🌊 海王对战模式](#-海王对战模式)
- [🔧 开发环境](#-开发环境)
- [🚀 部署指南](#-部署指南)
- [📊 测试指南](#-测试指南)
- [🔍 故障排除](#-故障排除)

## 🎯 项目概述

### 项目简介
Anti Love Brain Agent 是一个基于 FastAPI 和 LangChain 的智能聊天助手，专门用于反恋爱脑咨询和海王对战训练。项目采用现代化的架构设计，支持多用户隔离、智能记忆管理和高性能对话处理。

### 核心特性
- **🎭 海王对战模式** - 模拟不同类型海王，提供实战训练
- **🧠 智能记忆系统** - 基于Session的持久化记忆管理
- **🌐 多用户隔离** - 每个用户独立的对话历史和记忆空间
- **⚡ 高性能架构** - 优化的路由系统和响应机制
- **🎨 现代化UI** - 美观的聊天界面和交互体验

## 🏗️ 系统架构

### 项目结构
```
anti_love_brain_agent/
├── 🚀 主应用
│   ├── app.py                    # FastAPI主应用，路由和API端点
│   ├── requirements.txt          # Python依赖包
│   ├── Procfile                  # Railway部署配置
│   ├── runtime.txt               # Python版本配置
│   └── config/railway.toml       # Railway构建配置
├── 🧠 智能核心 (src/)
│   ├── core/                     # 核心模块
│   │   ├── agent.py              # LangChain智能代理
│   │   ├── app_config.py         # 应用配置管理
│   │   ├── config.py             # 基础配置
│   │   └── severity_analyzer.py  # 恋爱脑严重程度分析
│   ├── memory/                   # 记忆管理系统
│   │   ├── memory_manager.py     # 智能记忆管理器
│   │   ├── memory_factory.py     # 记忆管理器工厂
│   │   └── redis_memory_manager.py # Redis记忆管理器
│   ├── prompts/                  # 提示词管理
│   │   ├── prompts.py            # 提示词模板
│   │   └── prompt_config.py      # 提示词配置
│   └── tools/                    # 专业工具集
│       ├── seaking.py            # 海王对战工具
│       ├── help.py               # 帮助工具
│       └── talk.py               # 日常聊天工具
├── 🎨 前端界面 (static/)
│   ├── chat.html                 # 主聊天界面
│   ├── index_modern.html         # 现代化主页面
│   ├── styles.css                # 样式文件
│   ├── personas.json             # 海王人设配置
│   └── favicon.svg               # 网站图标
└── 📚 文档
    ├── README.md                 # 项目说明
    ├── DEVELOPMENT_GUIDE.md      # 开发指南（本文件）
    └── FINAL_IMPLEMENTATION_SUMMARY.md # 实现总结
```

### 技术栈
- **后端框架**: FastAPI + Uvicorn
- **AI框架**: LangChain + OpenAI
- **记忆管理**: 内存存储 + Redis（可选）
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Railway + Docker

## 🚀 核心功能

### 1. 智能聊天系统
- **多模式支持**: 正常聊天、海王对战、帮助咨询
- **智能路由**: 根据用户输入自动选择最佳处理方式
- **实时响应**: 优化的响应机制，提供流畅的对话体验

### 2. 海王对战模式
- **多样化海王**: 支持不同类型和性格的海王模拟
- **实时评分**: 智能评分系统，实时反馈用户表现
- **战术指导**: 拽姐旁白提供专业的反套路建议

### 3. 记忆管理系统
- **Session隔离**: 基于Cookie的Session ID，确保用户数据隔离
- **智能压缩**: 自动压缩长对话，优化性能
- **持久化存储**: 支持内存和Redis两种存储方式

## 💾 记忆系统

### Session记忆架构
项目采用基于Session ID的记忆隔离系统，解决了IP频繁变化导致记忆丢失的问题：

```python
# Session ID生成和管理
def get_user_identifier(request: Request) -> str:
    session_id = request.cookies.get("sid")
    if session_id:
        return session_id
    else:
        new_session_id = uuid.uuid4().hex
        session_creation_times[new_session_id] = time.time()
        return new_session_id
```

### 记忆存储类型
1. **内存模式** (`MEMORY_STORAGE_TYPE=memory`)
   - 适合单机部署
   - 数据存储在进程内存中
   - 支持TTL自动清理

2. **Redis模式** (`MEMORY_STORAGE_TYPE=redis`)
   - 适合分布式部署
   - 数据持久化存储
   - 支持多实例共享

### 记忆管理特性
- **智能压缩**: 自动压缩长对话历史
- **分级存储**: 短期记忆 + 长期记忆
- **TTL清理**: 自动清理过期Session数据
- **用户隔离**: 每个Session独立的数据空间

## 🌊 海王对战模式

### 支持的对战类型
1. **🌊对战海王** - 男性海王 vs 女性用户
2. **🍵反茶艺大师** - 女性海王 vs 男性用户
3. **🌈决战通讯录之巅** - 同性海王对战
4. **💃姬圈擂台赛** - 女性海王 vs 女性用户

### 海王人设系统
```json
{
  "🌊对战海王": [
    {
      "persona": "ENTJ-霸道总裁型海王",
      "gender": "男",
      "description": "事业有成，霸道专横",
      "style": "强势主动，金钱攻势",
      "weakness": "害怕被拒绝，内心脆弱"
    }
  ]
}
```

### 对战流程
1. **选择模式**: 用户点击对战按钮
2. **人设生成**: 系统随机选择海王人设
3. **开始对战**: 海王发起第一句套路
4. **持续对话**: 用户回应，海王继续套路
5. **实时评分**: 拽姐旁白提供评分和建议
6. **胜利通关**: 达到100分即可通关

## 🔧 开发环境

### 环境要求
- Python 3.10+
- Node.js 16+ (可选，用于前端开发)
- Redis 6+ (可选，用于生产环境)

### 本地开发设置
```bash
# 1. 克隆项目
git clone <repository-url>
cd anti_love_brain_agent

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的API密钥

# 5. 启动开发服务器
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 环境变量配置
```bash
# 必需配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# 可选配置
LANGCHAIN_API_KEY=your_langsmith_key
ENABLE_IP_ISOLATION=true
MEMORY_STORAGE_TYPE=memory  # memory 或 redis
SESSION_TTL_DAYS=7
DEBUG=false

# Redis配置（如果使用Redis模式）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
MEMORY_TTL=604800  # 7天，单位秒
```

## 🚀 部署指南

### Railway部署（推荐）

#### 1. 准备部署
```bash
# 确保代码已提交到Git
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Railway配置
1. 在Railway Dashboard中连接GitHub仓库
2. 设置环境变量（参考上面的环境变量配置）
3. 配置构建命令（Railway会自动检测）

#### 3. 部署验证
```bash
# 检查应用状态
curl https://your-app.railway.app/health

# 测试聊天功能
curl -X POST https://your-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"测试消息"}'
```

### Docker部署
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 测试指南

### 单元测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_seaking.py
```

### API测试
```bash
# 测试聊天接口
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","button_type":"🌊对战海王"}'

# 测试系统状态
curl http://localhost:8000/system/status

# 测试重置功能
curl -X POST http://localhost:8000/reset
```

### 前端测试
1. 打开浏览器访问 `http://localhost:8000`
2. 测试各种聊天模式
3. 验证海王对战功能
4. 检查记忆持久化

## 🔍 故障排除

### 常见问题

#### 1. Session记忆丢失
**问题**: 用户对话历史丢失
**解决方案**: 
- 检查Cookie设置是否正确
- 验证Session TTL配置
- 确认浏览器Cookie功能正常

#### 2. 海王对战模式异常
**问题**: 海王对战功能不正常
**解决方案**:
- 检查 `personas.json` 文件是否存在
- 验证人设配置格式
- 查看后端日志错误信息

#### 3. 部署失败
**问题**: Railway部署失败
**解决方案**:
- 检查 `requirements.txt` 依赖
- 验证环境变量配置
- 确认 `Procfile` 配置正确

#### 4. 性能问题
**问题**: 响应速度慢
**解决方案**:
- 检查OpenAI API调用频率
- 优化记忆压缩策略
- 考虑使用Redis缓存

### 调试技巧

#### 启用调试模式
```bash
# 设置调试环境变量
export DEBUG=true
export RAILWAY_ENVIRONMENT=development
```

#### 查看日志
```bash
# 查看应用日志
tail -f logs/app.log

# 查看Railway日志
railway logs
```

#### 性能监控
```bash
# 检查系统状态
curl http://localhost:8000/system/status

# 查看路由统计
curl http://localhost:8000/system/routing/stats
```

## 📚 扩展开发

### 添加新的海王类型
1. 在 `static/personas.json` 中添加新人设
2. 更新 `AppConfig.SEAKING_MODES` 列表
3. 测试新人设功能

### 自定义记忆策略
1. 继承 `SmartMemoryManager` 类
2. 重写相关方法
3. 在 `memory_factory.py` 中注册

### 添加新的工具
1. 在 `src/tools/` 目录下创建新工具
2. 实现工具接口
3. 在 `app.py` 中注册路由

## 🤝 贡献指南

### 代码规范
- 使用Python类型注解
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串

### 提交规范
```bash
# 功能开发
git commit -m "feat: 添加新功能"

# 问题修复
git commit -m "fix: 修复某个问题"

# 文档更新
git commit -m "docs: 更新文档"
```

### 测试要求
- 新功能必须包含测试用例
- 确保所有测试通过
- 更新相关文档

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**🚀 开始您的开发之旅！**

*项目版本: v3.1 Session记忆系统 | 状态: 🟢 生产就绪*
