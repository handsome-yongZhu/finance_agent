# 金融报告系统部署指南

> 自动化金融数据调研与报告生成系统

## 📋 系统概述

这是一个基于 Mini Agent 的自动化金融报告系统，具备以下功能：

- 🤖 **AI 驱动**：使用 MiniMax M2.1 模型进行智能分析
- ⏰ **定时任务**：每天自动生成金融市场分析报告
- 🌐 **Web 界面**：美观的报告展示和管理界面
- 📊 **数据调研**：通过 MCP 工具自动搜索最新金融数据
- 🐳 **容器化**：Docker 一键部署，易于扩展

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  🌐 Web 服务器 (Flask)                          │
│  端口: 8080                                     │
│  功能: 报告展示、下载                           │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ⏰ 定时调度器 (Schedule)                       │
│  默认: 每天 09:00                               │
│  功能: 自动生成报告                             │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  🤖 Mini Agent                                  │
│  功能: AI 调研与分析                            │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  📂 报告存储                                    │
│  路径: ./reports                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 🚀 快速部署

### 方式一：Docker Compose 部署（推荐）

#### 1. 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- MiniMax API Key

#### 2. 配置步骤

```bash
# 1. 克隆项目（如果还没有）
git clone https://github.com/MiniMax-AI/Mini-Agent.git
cd Mini-Agent

# 2. 配置 API Key
vim mini_agent/config/config.yaml
```

编辑配置文件，填入你的 API Key：

```yaml
api_key: "YOUR_API_KEY_HERE"
api_base: "https://api.minimaxi.com"  # 或 https://api.minimax.io
model: "MiniMax-M2.1"
provider: "anthropic"

# 确保 MCP 工具已启用（用于网络搜索）
tools:
  enable_mcp: true
  mcp_config_path: "mcp.json"
```

#### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web        # Web 服务器日志
docker-compose logs -f scheduler  # 调度器日志
```

#### 4. 访问系统

打开浏览器访问：**http://localhost:8080**

#### 5. 管理命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 手动触发报告生成（用于测试）
docker-compose exec scheduler python scheduler.py --once --reports-dir /app/reports
```

### 方式二：本地部署

#### 1. 安装依赖

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步项目依赖
uv sync

# 安装额外依赖
uv pip install flask markdown schedule
```

#### 2. 配置

```bash
# 复制配置文件
cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml

# 编辑配置，填入 API Key
vim mini_agent/config/config.yaml
```

#### 3. 启动服务

```bash
# 终端 1: 启动 Web 服务器
python web_server.py --reports-dir ./reports --port 8080

# 终端 2: 启动定时调度器
python scheduler.py --reports-dir ./reports --time 09:00

# 或者手动生成一次报告（用于测试）
python financial_reporter.py --reports-dir ./reports
```

## ⚙️ 配置说明

### 调度时间配置

修改 `docker-compose.yml` 中的环境变量：

```yaml
environment:
  - SCHEDULE_TIME=09:00  # 修改为你想要的时间（24小时制）
```

或在启动时指定：

```bash
SCHEDULE_TIME=15:30 docker-compose up -d
```

### 报告主题配置

编辑 `financial_reporter.py` 中的 `topics` 列表来自定义调研主题：

```python
topics = [
    "今日A股市场主要指数的涨跌情况",
    "今日美股三大指数的表现",
    "今日黄金、原油等大宗商品价格变化",
    "今日人民币兑美元汇率变化",
    "近期重要的财经新闻和政策",
    # 添加你自己的主题...
]
```

### 资源限制配置

在 `docker-compose.yml` 中调整资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # CPU 核心数
      memory: 4G       # 内存限制
```

## 📊 使用说明

### Web 界面功能

1. **报告列表**：查看所有历史报告
2. **报告详情**：点击"查看报告"阅读完整内容
3. **下载报告**：下载 Markdown 格式的原始报告
4. **统计信息**：总报告数、成功数、失败数

### API 接口

系统提供以下 API 接口：

```bash
# 获取所有报告列表
GET http://localhost:8080/api/reports

# 获取指定报告内容
GET http://localhost:8080/api/report/<filename>

# 健康检查
GET http://localhost:8080/health
```

### 手动生成报告

```bash
# Docker 环境
docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports

# 本地环境
python financial_reporter.py --reports-dir ./reports
```

## 🔧 故障排查

### 问题 1：报告生成失败

**检查项：**

1. 确认 API Key 配置正确
2. 检查网络连接（需要访问 MiniMax API）
3. 确认 MCP 工具已启用（用于网络搜索）
4. 查看调度器日志：`docker-compose logs scheduler`

### 问题 2：Web 界面无法访问

**检查项：**

1. 确认容器运行状态：`docker-compose ps`
2. 检查端口占用：`lsof -i :8080`
3. 查看 Web 服务日志：`docker-compose logs web`

### 问题 3：定时任务未执行

**检查项：**

1. 确认调度器容器运行：`docker-compose ps scheduler`
2. 检查时区设置（容器内时区应为 Asia/Shanghai）
3. 查看调度器日志确认下次执行时间

## 🔐 生产环境部署建议

### 1. 安全配置

```bash
# 设置文件权限
chmod 600 mini_agent/config/config.yaml

# 使用环境变量传递敏感信息
docker-compose.yml:
  environment:
    - MINIMAX_API_KEY=${MINIMAX_API_KEY}
```

### 2. 反向代理（使用 Nginx）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. HTTPS 配置

```bash
# 使用 Let's Encrypt
certbot --nginx -d your-domain.com
```

### 4. 备份策略

```bash
# 定期备份报告目录
0 2 * * * tar -czf /backup/reports-$(date +\%Y\%m\%d).tar.gz /path/to/reports
```

### 5. 监控和日志

```bash
# 集成日志收集
docker-compose.yml:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

## 📈 性能优化

### 1. 资源调整

根据实际负载调整 CPU 和内存限制。

### 2. 报告缓存

对于频繁访问的报告，可以添加缓存层。

### 3. 数据库存储

对于大量报告，建议使用数据库存储元数据：

```python
# 可选：使用 SQLite 或 PostgreSQL
# 替换 JSON 文件存储
```

## 🎯 扩展功能

### 1. 邮件通知

在报告生成后发送邮件：

```python
# 在 financial_reporter.py 中添加
import smtplib
from email.mime.text import MIMEText

def send_email_notification(report_path):
    # 实现邮件发送逻辑
    pass
```

### 2. 多时段报告

生成不同时段的报告：

```yaml
# docker-compose.yml
services:
  scheduler-morning:
    command: python scheduler.py --time 09:00
  scheduler-afternoon:
    command: python scheduler.py --time 15:00
```

### 3. 自定义报告模板

创建不同类型的报告模板。

## 📞 技术支持

- 项目地址：https://github.com/MiniMax-AI/Mini-Agent
- 问题反馈：提交 GitHub Issue
- MiniMax 文档：https://platform.minimaxi.com/document

## 📄 许可证

MIT License

---

**⭐ 如果这个项目对您有帮助，请给它一个 Star！**
