#!/bin/bash

# 拽姐 Anti Love Brain Agent - 本地测试脚本

echo "🧪 开始本地测试..."

# 检查是否存在.env文件
if [ ! -f .env ]; then
    echo "❌ 错误：未找到.env文件"
    echo "请确保.env文件存在并包含必要的API密钥"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：Python3未安装"
    exit 1
fi

# 安装依赖（如果需要）
echo "📦 检查依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# 测试启动
echo "🚀 启动本地服务..."
python -c "
import uvicorn
from app import app
print('✅ 服务配置正确！')
print('🌐 访问地址: http://localhost:8000')
print('💡 提示: 按 Ctrl+C 停止服务')
uvicorn.run(app, host='0.0.0.0', port=8000)
"
