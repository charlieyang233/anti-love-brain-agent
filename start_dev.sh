#!/bin/bash

# Anti Love Brain Agent 开发服务器启动脚本

echo "🚀 启动 Anti Love Brain Agent 开发服务器..."

# 激活虚拟环境
source .venv/bin/activate

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  正在加载环境变量..."
    export $(cat .env | xargs)
fi

# 启动服务器
echo "📡 启动 FastAPI 服务器 (http://localhost:8000)"
echo "📚 API 文档: http://localhost:8000/docs"
echo "🔄 自动重载已启用"
echo "⏹️  按 Ctrl+C 停止服务器"
echo ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
