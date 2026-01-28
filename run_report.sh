#!/bin/bash
# 一键生成报告脚本
# Quick Report Generation Script

echo "🚀 开始生成金融报告..."
echo "📊 将为所有股票生成 normal 和 professional 两个版本"
echo ""

# 检查是否在容器环境
if [ -f /.dockerenv ]; then
    # 在容器内直接运行
    python scheduler.py --once --reports-dir /app/reports
else
    # 在宿主机上通过 docker-compose 执行
    docker-compose exec -T scheduler python scheduler.py --once --reports-dir /app/reports
fi

echo ""
echo "✅ 报告生成完成！"
echo "📂 访问 Web 界面查看：http://localhost:8080"