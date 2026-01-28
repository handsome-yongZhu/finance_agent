# 🚀 金融报告自动化系统

基于 Mini Agent 的自动化金融数据调研与报告生成系统

## ✨ 功能特性

- 🤖 **AI 智能分析**：使用 MiniMax M2.1 模型进行金融数据分析
- ⏰ **定时自动执行**：每天自动调研金融数据并生成报告
- 🌐 **Web 可视化**：美观的 Web 界面展示所有历史报告
- 📊 **多维度数据**：覆盖股市、汇率、大宗商品、财经新闻等
- 🐳 **一键部署**：Docker Compose 一键启动所有服务
- 📱 **响应式设计**：支持桌面和移动端访问

## 📸 系统预览

### Web 界面
- 报告列表页：展示所有历史报告
- 报告详情页：美观的 Markdown 渲染
- 统计信息：成功/失败报告数量统计

### 报告内容
- 市场概览
- 主要指数表现
- 热点板块分析
- 重要新闻和政策
- 市场展望

## 🚀 快速开始

### 一键启动

```bash
# 1. 配置 API Key
vim mini_agent/config/config.yaml

# 2. 启动系统
./start.sh

# 3. 访问 Web 界面
打开浏览器访问: http://localhost:8080
```

### 手动启动

```bash
# 使用 Docker Compose
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 📁 项目结构

```
Finance-Agent/
├── financial_reporter.py      # 报告生成核心模块
├── scheduler.py                # 定时任务调度器
├── web_server.py               # Web 服务器
├── templates/                  # Web 界面模板
│   ├── index.html             # 报告列表页
│   └── report.html            # 报告详情页
├── prompts/                    # Prompt 模板目录 ⭐ 新增
│   ├── first_report.md        # 首次完整报告模板
│   ├── daily_report.md        # 每日增量报告模板
│   └── README.md              # 模板使用说明
├── Dockerfile                  # Docker 镜像构建
├── docker-compose.yml          # 服务编排配置
├── start.sh                    # 启动脚本
├── stop.sh                     # 停止脚本
├── DEPLOYMENT.md               # 详细部署文档
└── reports/                    # 报告存储目录
    ├── financial_report_*.md  # 报告文件
    └── metadata/              # 报告元数据
```

## ⚙️ 配置说明

### 1. 修改调度时间

编辑 `docker-compose.yml`：

```yaml
environment:
  - SCHEDULE_TIME=09:00  # 修改为你想要的时间
```

### 2. 自定义报告模板 ⭐ 新功能

系统使用独立的 Prompt 模板文件，可以灵活调整报告结构：

```bash
# 编辑首次完整报告模板
vim prompts/first_report.md

# 编辑每日增量报告模板
vim prompts/daily_report.md
```

**模板变量**：
- `{date}` - 报告日期
- `{stocks}` - 股票代码列表

**详细说明**：查看 [prompts/README.md](prompts/README.md)

### 3. 调整资源限制

编辑 `docker-compose.yml` 中的 `resources` 配置。

## 🔧 常用命令

```bash
# 启动服务
./start.sh
# 或
docker-compose up -d

# 停止服务
./stop.sh
# 或
docker-compose down

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web        # Web 服务器
docker-compose logs -f scheduler  # 调度器

# 重启服务
docker-compose restart

# 手动生成报告（测试用）
docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports

# 立即执行一次定时任务
docker-compose exec scheduler python scheduler.py --once --reports-dir /app/reports
```

## 📊 API 接口

系统提供以下 REST API：

### 获取所有报告

```bash
GET http://localhost:8080/api/reports

Response:
[
  {
    "date": "2026-01-22",
    "timestamp": "2026-01-22T09:00:00",
    "filename": "financial_report_20260122_090000.md",
    "status": "success",
    "file_size": 12345
  }
]
```

### 获取报告内容

```bash
GET http://localhost:8080/api/report/<filename>

Response:
{
  "success": true,
  "content": "<html>...",
  "markdown": "# 报告内容..."
}
```

### 健康检查

```bash
GET http://localhost:8080/health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-22T10:00:00"
}
```

## 🌐 Web 界面访问

启动后访问：**http://localhost:8080**

界面功能：
- ✅ 查看所有历史报告
- ✅ 查看报告详细内容
- ✅ 下载 Markdown 格式报告
- ✅ 查看生成统计信息

## 🔐 生产环境部署

详细的生产环境部署指南请参考：[DEPLOYMENT.md](DEPLOYMENT.md)

包括：
- 安全配置
- Nginx 反向代理
- HTTPS 配置
- 备份策略
- 监控和日志
- 性能优化

## 🐛 故障排查

### 问题 1：报告生成失败

**解决方案：**
1. 检查 API Key 配置
2. 确认 MCP 工具已启用
3. 查看调度器日志：`docker-compose logs scheduler`

### 问题 2：Web 无法访问

**解决方案：**
1. 确认容器运行：`docker-compose ps`
2. 检查端口占用：`lsof -i :8080`
3. 查看 Web 日志：`docker-compose logs web`

### 问题 3：定时任务未执行

**解决方案：**
1. 检查调度器状态：`docker-compose ps scheduler`
2. 确认时区设置正确
3. 查看日志中的下次执行时间

## 📈 系统监控

### 查看服务状态

```bash
# 所有服务状态
docker-compose ps

# 资源使用情况
docker stats
```

### 报告统计

访问 Web 首页查看：
- 总报告数
- 成功生成数
- 失败数量

## 🎯 扩展功能

### 1. 自定义报告模板 ✅ 已实现

通过 `prompts/` 目录下的 Markdown 模板文件自定义报告结构，无需修改代码：
- `first_report.md` - 首次完整报告
- `daily_report.md` - 每日增量报告

详见：[prompts/README.md](prompts/README.md)

### 2. 添加邮件通知

在报告生成后自动发送邮件通知。

### 3. 多时段报告

配置多个调度器，生成早中晚不同时段的报告。

### 4. 自定义报告类型

创建不同行业、不同风格的报告模板（周报、月报等）。

### 5. 数据可视化

添加图表展示功能，使报告更加直观。

## 🔄 更新与维护

### 更新系统

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

### 备份数据

```bash
# 备份报告目录
tar -czf reports-backup-$(date +%Y%m%d).tar.gz reports/

# 恢复数据
tar -xzf reports-backup-20260122.tar.gz
```

## 📚 相关文档

- [完整部署指南](DEPLOYMENT.md) - 详细的部署说明
- [Mini Agent 文档](README_CN.md) - Mini Agent 项目说明
- [MiniMax 文档](https://platform.minimaxi.com/document) - API 文档

## 💡 使用建议

1. **首次部署**：先手动执行一次确保配置正确
2. **定时设置**：根据市场开盘时间设置合适的调度时间
3. **资源监控**：定期检查系统资源使用情况
4. **数据备份**：定期备份报告数据
5. **日志清理**：定期清理旧日志文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 支持

- GitHub Issues: https://github.com/MiniMax-AI/Mini-Agent/issues
- MiniMax 官方文档: https://platform.minimaxi.com/document

---

**⭐ 如果这个项目对您有帮助，请给它一个 Star！**

## 快速命令参考

```bash
# 启动
./start.sh

# 停止
./stop.sh

# 查看日志
docker-compose logs -f

# 测试生成
docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports

# 访问界面
http://localhost:8080
```

🎉 **开始使用金融报告自动化系统吧！**
