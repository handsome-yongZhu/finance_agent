FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（包括中文字体）
RUN apt-get update && apt-get install -y \
    git \
    curl \
    cron \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app

# 升级pip
RUN pip install --no-cache-dir --upgrade pip

# 先安装 mini_agent 的基础依赖
RUN pip install --no-cache-dir \
    pydantic>=2.0.0 \
    pyyaml>=6.0.0 \
    httpx>=0.27.0 \
    mcp>=1.0.0 \
    requests>=2.31.0 \
    tiktoken>=0.5.0 \
    prompt-toolkit>=3.0.0 \
    anthropic>=0.39.0 \
    openai>=1.57.4 \
    agent-client-protocol>=0.6.0

# 安装金融报告系统的额外依赖
RUN pip install --no-cache-dir \
    flask>=3.0.0 \
    markdown>=3.5.0 \
    schedule>=1.2.0 \
    matplotlib>=3.8.0 \
    pandas>=2.0.0 \
    numpy>=1.24.0


# 配置matplotlib使用中文字体
RUN python3 -c "import matplotlib; print(matplotlib.matplotlib_fname())" && \
    mkdir -p /root/.cache/matplotlib && \
    echo "font.family: sans-serif" >> /etc/matplotlibrc && \
    echo "font.sans-serif: WenQuanYi Zen Hei, Noto Sans CJK SC, DejaVu Sans" >> /etc/matplotlibrc && \
    echo "axes.unicode_minus: False" >> /etc/matplotlibrc

# 创建报告目录
RUN mkdir -p /app/reports /app/reports/metadata /app/reports/images

# 暴露 Web 服务端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 默认启动 Web 服务器
CMD ["python", "web_server.py", "--host", "0.0.0.0", "--port", "8080"]