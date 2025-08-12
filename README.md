# 反恋爱脑闺蜜 Agent（拽姐）

基于 **LangChain Tools Agent** 的多工具 Agent（毒舌锐评 / 求助分析 / 海王模拟），
支持 API2D(OpenAI 兼容) 与 SerpAPI 搜索摘要。

## 🚀 快速启动

### 本地开发部署

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd anti_love_brain_agent

# 2. 创建虚拟环境
python -m venv .venv && source .venv/bin/activate  # Windows 用 .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 在 .env 里填入：OPENAI_API_KEY（API2D 转发密钥）、SERPAPI_API_KEY（可选）

# 5. 启动服务
./test_local.sh
# 或者手动启动：uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 开发服务管理

```bash
# 启动开发服务器（自动重载）
./start_dev.sh

# 本地测试
./test_local.sh

# 手动启动
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 💜 使用方式

### Web 前端界面（推荐）
- 访问 `http://localhost:8000` 
- 粉紫色优雅风格设计
- 支持打字机效果的AI回复
- 可选择不同海王模拟模式

### API 调用
```bash
# POST http://127.0.0.1:8000/chat
# body: { "input": "他两天不回我，我该怎么办？" }

# 海王模拟模式
# body: { "input": "我想练习对付海王", "persona": "高冷学霸型" }

# 重置对话
# POST http://127.0.0.1:8000/reset
```

## 📁 目录结构
```
anti_love_brain_agent/
├── app.py                 # FastAPI 入口 + 静态文件服务
├── static/
│   └── index.html         # 前端聊天界面
├── src/
│   ├── config.py          # LLM 初始化（API2D 兼容）
│   ├── prompts.py         # 全局系统提示与工具内部写作指引
│   ├── agent.py           # 创建 Tools Agent + Memory
│   └── tools/
│       ├── severity.py    # 恋爱脑程度识别器
│       ├── roast.py       # 毒舌锐评工具
│       ├── help.py        # 求助分析工具
│       ├── seaking.py     # 海王模拟工具
│       └── search.py      # 搜索摘要工具
├── requirements.txt       # Python 依赖
├── .env.example          # 环境变量模板
├── test_local.sh         # 本地测试脚本
└── start_dev.sh          # 开发启动脚本
```

## 💡 功能说明

### 智能工具调用流程
1. **恋爱脑程度识别**：Agent 首先评估用户问题的恋爱脑指数与等级
2. **危险等级处理**：若识别为"危"级，优先调用求助分析工具
3. **搜索增强**：需要案例警示时调用搜索工具获取相关信息
4. **海王模拟**：特殊模式下提供三段式回复（海王话术/建议/拽姐点评）

### 角色特色
- **拽姐人设**：毒舌直言，理性清醒，反恋爱脑专家
- **多样化回复**：根据情况调用不同工具组合
- **记忆功能**：支持多轮对话上下文记忆

## 🛠️ VS Code 开发支持

项目包含 VS Code 任务配置：
- `Ctrl/Cmd + Shift + P` → `Tasks: Run Task` → 选择对应任务
- 支持开发服务器启动、测试等任务

## 🔧 环境变量配置

在 `.env` 文件中配置：

```env
# OpenAI API 配置（使用 API2D 转发）
OPENAI_API_KEY=your_api2d_key_here
OPENAI_BASE_URL=https://oa.api2d.net/v1

# SerpAPI 搜索（可选）
SERPAPI_API_KEY=your_serpapi_key_here
```

## 🎯 特色功能

### 🎀 优雅前端界面
- 粉紫色渐变设计
- 流畅的打字机动画效果
- 响应式布局适配
- 海王模式智能解析

### 🧠 智能分析
- 恋爱脑程度量化评估
- 个性化建议生成
- 实时搜索信息整合
- 多场景海王话术模拟

### 🚀 开发友好
- 热重载开发模式
- 完整的错误处理
- 详细的日志输出
- VS Code 任务集成

## 📖 API 文档

启动服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

MIT License
