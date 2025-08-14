# 🚀 生产环境部署指南

## 🎯 快速部署

### 一键部署脚本
```bash
# 给脚本执行权限
chmod +x deploy_production.sh

# 运行部署脚本
./deploy_production.sh
```

## 📋 部署前准备

### 1. 环境要求
- Docker >= 20.10.0
- Docker Compose >= 2.0.0
- 4GB+ 可用内存
- 2GB+ 可用磁盘空间

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
nano .env
```

必需的环境变量：
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://oa.api2d.net/v1
```

## 🛠️ 手动部署步骤

### 1. 构建生产环境镜像
```bash
docker-compose -f docker-compose.production.yml build --no-cache
```

### 2. 启动服务
```bash
docker-compose -f docker-compose.production.yml up -d
```

### 3. 检查服务状态
```bash
docker-compose -f docker-compose.production.yml ps
```

### 4. 查看日志
```bash
docker-compose -f docker-compose.production.yml logs -f
```

## 🔧 高级配置

### 使用Nginx反向代理
```bash
# 启动包含Nginx的完整服务
docker-compose -f docker-compose.production.yml --profile production-with-nginx up -d
```

### SSL证书配置
1. 将SSL证书文件放在 `ssl/` 目录下
2. 编辑 `nginx.conf` 中的HTTPS配置
3. 重启Nginx服务

## 📊 监控和维护

### 服务管理命令
```bash
# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 重启服务
docker-compose -f docker-compose.production.yml restart

# 停止服务
docker-compose -f docker-compose.production.yml down

# 查看实时日志
docker-compose -f docker-compose.production.yml logs -f anti-love-brain-agent

# 进入容器调试
docker exec -it anti-love-brain-agent-prod bash
```

### 健康检查
服务包含自动健康检查，可以通过以下方式查看：
```bash
docker inspect anti-love-brain-agent-prod | grep -A 10 Health
```

### 日志管理
日志文件位置：
- 应用日志：`./logs/`
- Docker日志：使用 `docker logs` 命令查看

## 🌐 访问服务

部署成功后，可以通过以下地址访问：
- 直接访问：http://localhost:8000
- 通过Nginx：http://localhost:80

## 🚨 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker-compose -f docker-compose.production.yml logs
   ```

2. **网络连接问题**
   ```bash
   # 检查网络配置
   docker network ls
   docker network inspect anti-love-brain-network
   ```

3. **环境变量问题**
   ```bash
   # 检查环境变量是否正确加载
   docker exec anti-love-brain-agent-prod env | grep OPENAI
   ```

### 重新部署
```bash
# 完全重新部署
docker-compose -f docker-compose.production.yml down
docker system prune -f
./deploy_production.sh
```

## 📈 性能优化

### 生产环境建议
1. 增加worker进程数量
2. 配置负载均衡
3. 设置日志轮转
4. 监控资源使用情况

### 扩展配置
可以通过修改 `docker-compose.production.yml` 来调整：
- 内存限制
- CPU限制
- 副本数量
- 网络配置

## 🔐 安全考虑

1. 使用非root用户运行应用
2. 限制容器权限
3. 定期更新基础镜像
4. 配置防火墙规则
5. 使用HTTPS加密通信

## 📞 技术支持

如果遇到部署问题，请：
1. 查看日志文件
2. 检查环境配置
3. 确认网络连接
4. 联系技术支持
