#!/bin/bash
# 火山云服务器一键部署脚本
# Volcano Cloud Server Deployment Script

set -e

echo "================================================"
echo "  🚀 金融报告系统 - 火山云一键部署"
echo "================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    echo -e "${RED}❌ 无法识别操作系统${NC}"
    exit 1
fi

echo -e "${GREEN}📍 检测到系统：$OS${NC}"
echo ""

# 安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker 已安装${NC}"
        docker --version
    else
        echo -e "${YELLOW}📦 安装 Docker...${NC}"
        curl -fsSL https://get.docker.com | sh
        systemctl start docker
        systemctl enable docker
        echo -e "${GREEN}✅ Docker 安装完成${NC}"
        docker --version
    fi
}

# 安装 Docker Compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose 已安装${NC}"
        docker-compose --version
    else
        echo -e "${YELLOW}📦 安装 Docker Compose...${NC}"
        
        # 安装最新版本的 Docker Compose
        DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
        
        if [ -z "$DOCKER_COMPOSE_VERSION" ]; then
            echo -e "${YELLOW}⚠️  无法获取最新版本，使用默认版本 v2.24.5${NC}"
            DOCKER_COMPOSE_VERSION="v2.24.5"
        fi
        
        curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        
        # 创建软链接
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        
        echo -e "${GREEN}✅ Docker Compose 安装完成${NC}"
        docker-compose --version
    fi
}

# 安装 Git
install_git() {
    if command -v git &> /dev/null; then
        echo -e "${GREEN}✅ Git 已安装${NC}"
    else
        echo -e "${YELLOW}📦 安装 Git...${NC}"
        if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
            apt-get update && apt-get install -y git
        elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
            yum install -y git
        fi
        echo -e "${GREEN}✅ Git 安装完成${NC}"
    fi
}

# 配置防火墙
configure_firewall() {
    echo -e "${YELLOW}🔒 配置防火墙...${NC}"
    
    # UFW (Ubuntu/Debian)
    if command -v ufw &> /dev/null; then
        ufw allow 8080/tcp
        echo -e "${GREEN}✅ UFW 防火墙已配置（开放8080端口）${NC}"
    fi
    
    # Firewalld (CentOS/RHEL)
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=8080/tcp
        firewall-cmd --reload
        echo -e "${GREEN}✅ Firewalld 防火墙已配置（开放8080端口）${NC}"
    fi
    
    # Iptables（如果没有上面的防火墙）
    if ! command -v ufw &> /dev/null && ! command -v firewall-cmd &> /dev/null; then
        if command -v iptables &> /dev/null; then
            iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
            # 尝试保存规则
            if command -v iptables-save &> /dev/null; then
                iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ Iptables 防火墙已配置（开放8080端口）${NC}"
        fi
    fi
}

# 克隆或更新项目
setup_project() {
    echo -e "${YELLOW}📥 设置项目...${NC}"
    
    PROJECT_DIR="Finance-Agent"
    
    if [ -d "$PROJECT_DIR" ]; then
        echo -e "${YELLOW}项目目录已存在，正在更新...${NC}"
        cd "$PROJECT_DIR"
        git pull || echo -e "${YELLOW}⚠️  Git pull 失败，请检查${NC}"
    else
        echo -e "${YELLOW}正在克隆项目...${NC}"
        echo ""
        echo -e "${YELLOW}请输入你的项目Git仓库地址:${NC}"
        echo -e "${YELLOW}例如: https://github.com/username/Finance-Agent.git${NC}"
        read -r GIT_REPO
        
        if [ -z "$GIT_REPO" ]; then
            echo -e "${RED}❌ 未输入Git仓库地址${NC}"
            exit 1
        fi
        
        git clone "$GIT_REPO" "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
    
    echo -e "${GREEN}✅ 项目设置完成${NC}"
}

# 配置 API Key
configure_api_key() {
    echo ""
    echo -e "${YELLOW}⚙️  配置 API Key...${NC}"
    
    if [ ! -f "mini_agent/config/config.yaml" ]; then
        if [ -f "mini_agent/config/config-example.yaml" ]; then
            cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
            echo -e "${GREEN}✅ 配置文件已创建${NC}"
        else
            echo -e "${RED}❌ 配置示例文件不存在${NC}"
            exit 1
        fi
    fi
    
    echo ""
    echo -e "${YELLOW}请选择配置方式:${NC}"
    echo "1) 手动编辑配置文件"
    echo "2) 使用环境变量（推荐）"
    read -p "请选择 [1-2]: " -n 1 -r
    echo
    
    if [[ $REPLY == "2" ]]; then
        echo ""
        echo -e "${YELLOW}请输入你的 MiniMax API Key:${NC}"
        read -r API_KEY
        
        if [ -z "$API_KEY" ]; then
            echo -e "${RED}❌ API Key 不能为空${NC}"
            exit 1
        fi
        
        # 创建 .env 文件
        cat > .env << EOF
MINIMAX_API_KEY=$API_KEY
MINIMAX_API_BASE=https://api.minimaxi.com
SCHEDULE_TIME=10:00
TZ=Asia/Shanghai
EOF
        echo -e "${GREEN}✅ 环境变量配置完成${NC}"
    else
        echo ""
        echo -e "${YELLOW}请编辑配置文件: mini_agent/config/config.yaml${NC}"
        echo -e "${YELLOW}按任意键打开编辑器...${NC}"
        read -n 1 -s -r
        ${EDITOR:-vim} mini_agent/config/config.yaml
    fi
}

# 启动服务
start_services() {
    echo ""
    echo -e "${YELLOW}🚀 启动服务...${NC}"
    
    # 创建报告目录
    mkdir -p reports reports/metadata reports/images
    
    # 使用 docker-compose 启动
    docker-compose up -d
    
    echo -e "${GREEN}✅ 服务已启动${NC}"
}

# 等待服务就绪
wait_for_services() {
    echo ""
    echo -e "${YELLOW}⏳ 等待服务就绪...${NC}"
    
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 服务已就绪${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        RETRY_COUNT=$((RETRY_COUNT + 1))
    done
    
    echo ""
    echo -e "${YELLOW}⚠️  服务启动超时，请手动检查${NC}"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}  ✅ 部署完成！${NC}"
    echo "================================================"
    echo ""
    
    # 获取公网IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || curl -s api.ipify.org 2>/dev/null || echo "")
    
    if [ -n "$SERVER_IP" ]; then
        echo -e "${GREEN}📍 访问地址:${NC}"
        echo -e "   ${GREEN}http://$SERVER_IP:8080${NC}"
    else
        echo -e "${YELLOW}📍 访问地址: http://你的服务器IP:8080${NC}"
    fi
    
    echo ""
    echo "================================================"
    echo -e "${GREEN}  常用命令${NC}"
    echo "================================================"
    echo "  查看服务状态:   docker-compose ps"
    echo "  查看日志:       docker-compose logs -f"
    echo "  查看Web日志:    docker-compose logs -f web"
    echo "  查看调度器日志: docker-compose logs -f scheduler"
    echo "  停止服务:       docker-compose down"
    echo "  重启服务:       docker-compose restart"
    echo "  更新项目:       git pull && docker-compose up -d --build"
    echo "  手动生成报告:   docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports"
    echo ""
    echo "================================================"
    echo ""
    
    # 显示服务状态
    echo -e "${GREEN}📊 服务状态:${NC}"
    docker-compose ps
    echo ""
    
    # 重要提示
    echo "================================================"
    echo -e "${YELLOW}  💡 重要提示${NC}"
    echo "================================================"
    echo "  1. ⚠️  请在火山云控制台的【安全组】中开放 8080 端口"
    echo "     路径: 云服务器 → 实例 → 安全组 → 配置规则 → 添加规则"
    echo "     规则: 协议类型=TCP, 端口=8080, 来源=0.0.0.0/0"
    echo ""
    echo "  2. 🔒 建议配置 HTTPS（可选）"
    echo "     使用 Nginx + Let's Encrypt 证书"
    echo ""
    echo "  3. 📊 首次部署后，可以手动触发一次报告生成测试:"
    echo "     docker-compose exec scheduler python financial_reporter.py --reports-dir /app/reports"
    echo ""
    echo "================================================"
    echo ""
    echo -e "${GREEN}🎉 部署成功！开始使用你的金融报告系统吧！${NC}"
    echo ""
}

# 主流程
main() {
    echo "开始部署..."
    echo ""
    
    # 1. 安装依赖
    install_git
    echo ""
    install_docker
    echo ""
    install_docker_compose
    echo ""
    
    # 2. 配置防火墙
    configure_firewall
    echo ""
    
    # 3. 设置项目
    setup_project
    
    # 4. 配置 API Key
    configure_api_key
    
    # 5. 启动服务
    start_services
    
    # 6. 等待服务就绪
    wait_for_services
    
    # 7. 显示部署信息
    show_deployment_info
}

# 运行主流程
main
