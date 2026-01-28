#!/bin/bash
# 快速启动脚本

set -e

echo "================================================"
echo "  金融报告系统 - 启动脚本"
echo "================================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查配置文件
if [ ! -f "mini_agent/config/config.yaml" ]; then
    echo "⚠️  警告：配置文件不存在"
    echo "正在从示例文件创建配置..."
    cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
    echo ""
    echo "✅ 配置文件已创建: mini_agent/config/config.yaml"
    echo ""
    echo "⚠️  请编辑配置文件并填入你的 API Key："
    echo "   vim mini_agent/config/config.yaml"
    echo ""
    read -p "是否现在编辑配置文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-vim} mini_agent/config/config.yaml
    else
        echo "请手动编辑配置文件后再启动系统"
        exit 1
    fi
fi

# 创建报告目录
mkdir -p reports reports/metadata

echo ""
echo "🚀 正在启动服务..."
echo ""

# 启动服务
docker-compose up -d

echo ""
echo "✅ 服务启动成功！"
echo ""
echo "================================================"
echo "  访问信息"
echo "================================================"
echo "  🌐 Web 界面: http://localhost:8080"
echo "  📊 健康检查: http://localhost:8080/health"
echo ""
echo "================================================"
echo "  常用命令"
echo "================================================"
echo "  查看日志:     docker-compose logs -f"
echo "  停止服务:     docker-compose down"
echo "  重启服务:     docker-compose restart"
echo "  查看状态:     docker-compose ps"
echo "  手动生成报告: docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports"
echo ""
echo "================================================"

# 显示服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

# 等待服务健康检查
echo ""
echo "⏳ 等待服务就绪..."
sleep 5

# 检查 Web 服务健康状态
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Web 服务已就绪"
else
    echo "⚠️  Web 服务尚未就绪，请稍候..."
fi

echo ""
echo "🎉 系统已启动完成！"
echo ""
