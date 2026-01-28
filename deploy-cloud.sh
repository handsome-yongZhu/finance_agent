#!/bin/bash
# 云服务器一键部署脚本
# 适用于腾讯云、阿里云、华为云等任意云服务器

set -e

echo "================================================"
echo "  🚀 金融报告系统 - 云端一键部署"
echo "================================================"
echo ""

# 检测系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    echo "❌ 无法识别操作系统"
    exit 1
fi

echo "📍 检测到系统：$OS"
echo ""

# 安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        echo "✅ Docker 已安装"
    else
        echo "📦 安装 Docker..."
        curl -fsSL https://get.docker.com | sh
        systemctl start docker
        systemctl enable docker
        echo "✅ Docker 安装完成"
    fi
}

# 安装 Docker Compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose 已安装"
    else
        echo "📦 安装 Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        echo "✅ Docker Compose 安装完成"
    fi
}

# 配置防火墙
configure_firewall() {
    echo "🔒 配置防火墙..."
    
    # UFW (Ubuntu/Debian)
    if command -v ufw &> /dev/null; then
        ufw allow 8080/tcp
        echo "✅ UFW 防火墙已配置"
    fi
    
    # Firewalld (CentOS/RHEL)
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=8080/tcp
        firewall-cmd --reload
        echo "✅ Firewalld 防火墙已配置"
    fi
}

# 主安装流程
main() {
    echo "开始安装..."
    echo ""
    
    # 1. 安装 Docker
    install_docker
    echo ""
    
    # 2. 安装 Docker Compose
    install_docker_compose
    echo ""
    
    # 3. 检查配置文件
    if [ ! -f "mini_agent/config/config.yaml" ]; then
        echo "⚠️  警告：配置文件不存在"
        echo "正在创建配置文件..."
        cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
        echo ""
        echo "⚠️  请编辑配置文件并填入你的 API Key："
        echo "   vim mini_agent/config/config.yaml"
        echo ""
        read -p "是否现在编辑配置文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-vim} mini_agent/config/config.yaml
        else
            echo ""
            echo "❌ 请先配置 API Key 后再运行部署："
            echo "   vim mini_agent/config/config.yaml"
            echo "   然后再次运行: ./deploy-cloud.sh"
            exit 1
        fi
    fi
    
    # 4. 配置防火墙
    configure_firewall
    echo ""
    
    # 5. 创建报告目录
    mkdir -p reports reports/metadata
    echo "✅ 报告目录已创建"
    echo ""
    
    # 6. 启动服务
    echo "🚀 启动服务..."
    docker-compose up -d
    echo ""
    
    # 7. 等待服务启动
    echo "⏳ 等待服务就绪..."
    sleep 5
    
    # 8. 显示部署信息
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "获取失败")
    
    echo ""
    echo "================================================"
    echo "  ✅ 部署完成！"
    echo "================================================"
    echo ""
    echo "📍 访问地址："
    if [ "$SERVER_IP" != "获取失败" ]; then
        echo "   http://$SERVER_IP:8080"
    else
        echo "   http://你的服务器IP:8080"
    fi
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
    echo ""
    
    # 9. 显示服务状态
    echo "📊 服务状态："
    docker-compose ps
    echo ""
    
    # 10. 测试健康检查
    echo "🔍 测试服务健康状态..."
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Web 服务运行正常"
    else
        echo "⚠️  Web 服务尚未就绪，请稍候重试"
    fi
    
    echo ""
    echo "🎉 部署成功！开始使用你的金融报告系统吧！"
    echo ""
    echo "💡 提示："
    echo "   1. 记得在云服务商控制台的安全组中开放 8080 端口"
    echo "   2. 如需配置域名，请参考 DEPLOY_CLOUD.md"
    echo "   3. 建议配置 HTTPS 以提高安全性"
    echo ""
}

# 运行主流程
main
