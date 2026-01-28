# ☁️ 云端部署指南 - 三种超简洁方案

> 将你的金融报告系统部署到公网，随时随地访问

---

## 🎯 推荐方案对比

| 方案 | 难度 | 成本 | 部署时间 | 推荐指数 |
|------|------|------|----------|----------|
| **Railway** | ⭐ 最简单 | $5/月 | 5分钟 | ⭐⭐⭐⭐⭐ |
| **腾讯云轻量服务器** | ⭐⭐ 简单 | ￥74/年 | 10分钟 | ⭐⭐⭐⭐⭐ |
| **Render** | ⭐ 最简单 | 免费/￥7/月 | 5分钟 | ⭐⭐⭐⭐ |

---

## 方案一：Railway（推荐 - 最简单）

> 零配置，Git Push 即部署，自动 HTTPS

### ✨ 特点
- ✅ 最简单：几乎零配置
- ✅ 自动 HTTPS 域名
- ✅ 自动构建部署
- ✅ 支持定时任务（Cron）
- ❌ 需要信用卡验证

### 📝 部署步骤

#### 1. 准备工作

```bash
# 在项目根目录创建 railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python web_server.py --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
EOF

# 创建 Procfile（用于定时任务）
cat > Procfile << 'EOF'
web: python web_server.py --host 0.0.0.0 --port $PORT
scheduler: python scheduler.py --reports-dir /app/reports --time 09:30
EOF
```

#### 2. 注册并部署

1. 访问 [Railway.app](https://railway.app)
2. 使用 GitHub 账号登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择你的项目仓库
6. Railway 会自动检测 Dockerfile 并开始部署

#### 3. 配置环境变量

在 Railway Dashboard 中添加：

```
MINIMAX_API_KEY=你的API密钥
MINIMAX_API_BASE=https://api.minimaxi.com
SCHEDULE_TIME=09:30
```

#### 4. 添加定时任务服务

```bash
# 在 Railway Dashboard 中点击 "New Service"
# 选择同一个仓库，但使用不同的启动命令
Start Command: python scheduler.py --reports-dir /app/reports --time 09:30
```

#### 5. 获取访问地址

Railway 会自动分配一个域名：`https://your-app.railway.app`

### 💰 费用

- **免费额度**：$5 试用额度（约可用一周）
- **付费计划**：$5/月起（包含足够的资源）

---

## 方案二：腾讯云轻量服务器（推荐 - 性价比最高）

> 国内访问快，价格便宜，完全掌控

### ✨ 特点
- ✅ 国内访问速度快
- ✅ 价格便宜（￥74/年起）
- ✅ 完全控制权
- ✅ 可以跑其他服务
- ❌ 需要简单的 Linux 操作

### 📝 部署步骤

#### 1. 购买服务器

1. 访问 [腾讯云轻量应用服务器](https://cloud.tencent.com/product/lighthouse)
2. 选择配置：
   - **地域**：国内任意（推荐就近）
   - **镜像**：Docker 镜像（或 Ubuntu 22.04）
   - **套餐**：2核2G（￥74/年）够用
3. 购买后记录服务器 IP 地址

#### 2. 连接服务器

```bash
# 使用 SSH 连接（密码在腾讯云控制台重置）
ssh root@你的服务器IP
```

#### 3. 一键部署脚本

```bash
# 运行这个脚本，自动完成所有部署
curl -fsSL https://raw.githubusercontent.com/你的用户名/Finance-Agent/main/deploy-tencent.sh | bash
```

或者手动部署：

```bash
# 1. 安装 Docker（如果镜像没有自带）
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 2. 克隆项目
git clone https://github.com/你的用户名/Finance-Agent.git
cd Finance-Agent

# 3. 配置 API Key
vim mini_agent/config/config.yaml
# 填入你的 API Key

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

#### 4. 配置域名（可选）

```bash
# 如果你有域名，配置 Nginx 反向代理
apt install nginx -y

# 创建 Nginx 配置
cat > /etc/nginx/sites-available/finance-reporter << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/finance-reporter /etc/nginx/sites-enabled/
nginx -t && nginx -s reload
```

#### 5. 配置 HTTPS（可选但推荐）

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 自动配置 HTTPS
certbot --nginx -d your-domain.com
```

#### 6. 访问系统

- **直接访问**：`http://你的服务器IP:8080`
- **域名访问**：`https://your-domain.com`

### 💰 费用

- **服务器**：￥74/年（2核2G，3M带宽，50GB存储）
- **域名**：￥9/年起（.com 域名约 ￥55/年）
- **总计**：￥83-129/年

---

## 方案三：Render（最简单的免费方案）

> 完全免费，但有一些限制

### ✨ 特点
- ✅ 完全免费
- ✅ 零配置部署
- ✅ 自动 HTTPS
- ❌ 免费版会休眠（15分钟无访问后）
- ❌ 定时任务不稳定

### 📝 部署步骤

#### 1. 创建配置文件

```bash
# 创建 render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: financial-reporter-web
    env: docker
    dockerfilePath: ./Dockerfile
    dockerCommand: python web_server.py --host 0.0.0.0 --port $PORT
    envVars:
      - key: MINIMAX_API_KEY
        sync: false
      - key: MINIMAX_API_BASE
        value: https://api.minimaxi.com
    healthCheckPath: /health
    
  - type: worker
    name: financial-reporter-scheduler
    env: docker
    dockerfilePath: ./Dockerfile
    dockerCommand: python scheduler.py --reports-dir /app/reports --time 09:30
    envVars:
      - key: MINIMAX_API_KEY
        sync: false
EOF
```

#### 2. 部署

1. 访问 [Render.com](https://render.com)
2. 使用 GitHub 登录
3. 点击 "New +"  → "Blueprint"
4. 连接你的 GitHub 仓库
5. Render 会自动读取 `render.yaml` 并部署
6. 在环境变量中填入 `MINIMAX_API_KEY`

#### 3. 访问

Render 会分配一个域名：`https://your-app.onrender.com`

### ⚠️ 注意事项

- 免费版服务会在 15 分钟无访问后休眠
- 首次访问需要等待服务唤醒（约 30 秒）
- 定时任务可能不够稳定

### 💰 费用

- **免费版**：完全免费，有休眠限制
- **付费版**：$7/月，无休眠，更稳定

---

## 🎯 我的推荐

### 预算有限 → 腾讯云轻量服务器
- 一年不到 100 元
- 国内访问快
- 稳定可靠

### 追求简单 → Railway
- 几分钟部署完成
- 自动化程度最高
- 每月 $5 可接受

### 完全免费 → Render
- 零成本
- 接受休眠限制
- 适合测试和个人使用

---

## 🚀 快速部署脚本

### 腾讯云一键部署

```bash
# 创建部署脚本
cat > deploy-tencent.sh << 'SCRIPT'
#!/bin/bash
set -e

echo "================================"
echo "金融报告系统 - 腾讯云一键部署"
echo "================================"

# 安装 Docker
if ! command -v docker &> /dev/null; then
    echo "📦 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 克隆项目
echo "📥 克隆项目..."
if [ ! -d "Finance-Agent" ]; then
    git clone https://github.com/MiniMax-AI/Mini-Agent.git Finance-Agent
fi
cd Finance-Agent

# 配置文件
echo "⚙️  配置系统..."
if [ ! -f mini_agent/config/config.yaml ]; then
    cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
    echo "请编辑配置文件并填入 API Key："
    echo "vim mini_agent/config/config.yaml"
    exit 1
fi

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 显示状态
echo ""
echo "✅ 部署完成！"
echo "访问地址：http://$(curl -s ifconfig.me):8080"
echo ""
echo "常用命令："
echo "  查看日志: cd Finance-Agent && docker-compose logs -f"
echo "  停止服务: cd Finance-Agent && docker-compose down"
echo "  重启服务: cd Finance-Agent && docker-compose restart"
SCRIPT

chmod +x deploy-tencent.sh

# 上传到服务器并执行
scp deploy-tencent.sh root@你的服务器IP:/root/
ssh root@你的服务器IP "bash /root/deploy-tencent.sh"
```

---

## 🔒 安全建议

1. **修改默认端口**
```yaml
# docker-compose.yml
ports:
  - "8888:8080"  # 使用非标准端口
```

2. **配置防火墙**
```bash
# 腾讯云控制台 → 防火墙 → 只开放必要端口
# 允许：22(SSH), 80(HTTP), 443(HTTPS), 8080(自定义)
```

3. **定期备份**
```bash
# 添加到 crontab
0 2 * * * tar -czf /backup/reports-$(date +\%Y\%m\%d).tar.gz /root/Finance-Agent/reports
```

4. **使用环境变量存储密钥**
```bash
# 不要把 API Key 写在代码里
export MINIMAX_API_KEY="your-key"
```

---

## 📊 部署后验证

```bash
# 1. 检查服务状态
curl http://your-domain:8080/health

# 2. 查看日志
docker-compose logs -f

# 3. 手动触发报告生成（测试）
docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports

# 4. 访问 Web 界面
在浏览器打开: http://your-domain:8080
```

---

## 🆘 常见问题

### Q: 服务启动失败？
```bash
# 查看详细错误
docker-compose logs

# 检查端口占用
lsof -i :8080
```

### Q: 无法访问 Web 界面？
```bash
# 检查防火墙
ufw status
ufw allow 8080

# 腾讯云检查安全组规则
```

### Q: 定时任务不执行？
```bash
# 查看调度器日志
docker-compose logs scheduler

# 检查容器时区
docker-compose exec scheduler date
```

---

## 💡 小贴士

1. **第一次部署建议用腾讯云轻量服务器**：
   - 价格便宜，一年不到 100 元
   - 完全掌控，不怕服务商限制
   - 国内访问速度快

2. **域名购买**：
   - 阿里云、腾讯云都有便宜的域名
   - .top/.xyz 等域名只要几元/年
   - 配置好后访问体验更好

3. **监控告警**：
   - 使用云服务商的监控功能
   - 配置报告生成失败的通知

---

准备好了吗？选择一个方案，10 分钟后就能在公网访问你的金融报告系统！🚀
