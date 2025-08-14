# Railway部署配置指南

## 🚀 Railway部署步骤

### 1. 准备GitHub仓库
```bash
# 提交所有更改
git add .
git commit -m "feat: 添加基于IP隔离的Redis记忆管理系统"
git push origin main
```

### 2. 在Railway创建项目
1. 访问 [railway.app](https://railway.app)
2. 点击 "New Project" 
3. 选择 "Deploy from GitHub repo"
4. 选择你的 `anti-love-brain-agent` 仓库

### 3. 配置环境变量
在Railway项目设置中添加以下环境变量：

```env
# AI配置
OPENAI_API_KEY=你的OpenAI密钥
OPENAI_BASE_URL=https://oa.api2d.net/v1
OPENAI_MODEL=gemini-2.0-flash
LANGSMITH_API_KEY=你的LangSmith密钥

# 记忆存储配置
MEMORY_STORAGE_TYPE=memory
# 如果要使用Redis，改为: MEMORY_STORAGE_TYPE=redis

# IP隔离配置
ENABLE_IP_ISOLATION=true

# 使用限制
ENABLE_RATE_LIMIT=true
MAX_REQUESTS_PER_HOUR=100

# LangSmith配置
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=anti-love-railway
```

### 4. (可选) 添加Redis服务
如果要使用Redis记忆存储：

1. 在Railway项目中点击 "Add Service"
2. 选择 "Database" > "Redis"
3. Railway会自动创建Redis实例并提供连接信息
4. 更新环境变量：
```env
MEMORY_STORAGE_TYPE=redis
REDIS_HOST=Redis连接主机
REDIS_PORT=Redis端口
REDIS_PASSWORD=Redis密码（如果有）
```

### 5. 部署配置
Railway会自动检测Python项目，但可以创建 `railway.toml` 文件优化部署：

```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 6. 端口配置
Railway会自动分配端口，更新 `app.py` 中的端口配置：

```python
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8889))  # Railway会提供PORT环境变量
    uvicorn.run(app, host="0.0.0.0", port=port)
```

## 🎯 IP隔离工作原理

### 用户标识生成
```python
def get_user_id_from_ip(client_ip: str) -> str:
    """根据IP地址生成用户ID"""
    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:12]
    return f"ip_{ip_hash}"
```

### IP获取逻辑
```python
def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    # Railway通过X-Forwarded-For头传递真实IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host
```

### 记忆隔离效果
- 每个IP地址对应唯一的用户ID
- 同一IP的用户共享记忆（适合家庭/办公室环境）
- 不同IP的用户完全隔离
- 数据持久化（如果使用Redis）

## 📊 监控和调试

### 健康检查接口
```bash
curl https://your-railway-app.up.railway.app/health
```

### 查看用户记忆状态
```bash
curl https://your-railway-app.up.railway.app/memory/stats
```

### 测试IP隔离
用不同的网络环境（如手机热点、VPN）访问应用，验证记忆隔离效果。

## 🔧 故障排除

### 1. Redis连接失败
- 检查Redis服务是否正常运行
- 验证环境变量设置
- 应用会自动回退到内存模式

### 2. 端口配置问题
- 确保使用 `PORT` 环境变量
- Railway会自动分配端口

### 3. IP获取异常
- 检查代理头设置
- 验证 `X-Forwarded-For` 头是否正确传递

## 🎉 部署完成
部署成功后，你将拥有：
- ✅ 基于IP的用户隔离
- ✅ 智能记忆管理
- ✅ 自动故障恢复
- ✅ 生产级性能监控
