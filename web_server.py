#!/usr/bin/env python3
"""
Web 服务器 - 展示金融报告
Web Server for Financial Reports
提供 Web 界面展示所有历史报告
"""

from flask import Flask, render_template, jsonify, send_from_directory
from pathlib import Path
import markdown
from datetime import datetime
import yaml
import re
from collections import defaultdict

from financial_reporter import FinancialReporter


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 初始化报告生成器（用于读取报告）
reporter = None
stocks_config = {}


def init_reporter(config_path=None, reports_dir="./reports"):
    """初始化报告生成器"""
    global reporter, stocks_config
    reporter = FinancialReporter(config_path, reports_dir)
    
    # 加载股票配置
    try:
        with open("stocks_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            stocks_config = {stock['code']: stock for stock in config.get('stocks', [])}
    except Exception as e:
        print(f"警告: 无法加载股票配置: {e}")
        stocks_config = {}


@app.route('/')
def index():
    """首页 - 按股票代码分组的报告"""
    reports_by_stock = get_reports_by_stock()
    
    return render_template('index.html', 
                         stocks=stocks_config,
                         reports_by_stock=reports_by_stock)


@app.route('/api/reports')
def api_reports():
    """API - 获取所有报告列表"""
    reports = reporter.get_all_reports()
    return jsonify(reports)


@app.route('/api/report/<filename>')
def api_report_content(filename):
    """API - 获取指定报告内容"""
    content = reporter.get_report_content(filename)
    if content:
        # 转换 Markdown 到 HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'tables',           # 表格支持
                'fenced_code',      # 代码块支持
                'nl2br',            # 换行符支持
                'attr_list',        # 属性列表（图片尺寸控制）
                'md_in_html'        # HTML中的Markdown
            ]
        )
        return jsonify({
            'success': True,
            'content': html_content,
            'markdown': content
        })
    else:
        return jsonify({
            'success': False,
            'error': '报告不存在'
        }), 404


@app.route('/report/<filename>')
def view_report(filename):
    """查看报告详情页"""
    content = reporter.get_report_content(filename)
    if content:
        # 转换 Markdown 到 HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'tables',           # 表格支持
                'fenced_code',      # 代码块支持
                'nl2br',            # 换行符支持
                'attr_list',        # 属性列表（图片尺寸控制）
                'md_in_html'        # HTML中的Markdown
            ]
        )
        return render_template('report.html', 
                             filename=filename, 
                             content=html_content)
    else:
        return "报告不存在", 404


@app.route('/download/<filename>')
def download_report(filename):
    """下载报告"""
    return send_from_directory(
        reporter.reports_dir,
        filename,
        as_attachment=True
    )


@app.route('/api/stocks/<stock_code>/versions')
def api_stock_versions(stock_code):
    """API - 获取指定股票的所有版本和报告"""
    reports_by_stock = get_reports_by_stock()
    
    if stock_code not in reports_by_stock:
        return jsonify({
            'success': False,
            'error': '股票代码不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'stock_code': stock_code,
        'stock_name': stocks_config.get(stock_code, {}).get('name', stock_code),
        'versions': reports_by_stock[stock_code]
    })


def get_reports_by_stock():
    """按股票代码分组报告"""
    reports = reporter.get_all_reports()
    grouped = defaultdict(lambda: {'professional': [], 'normal': []})
    
    # 报告文件名格式: {stock_code}_{version}_{date}.md
    # 例如: 688388_professional_20260122.md 或 688388_normal_20260122.md
    pattern = r'^(\d+)_(professional|normal)_(\d{8})\.md$'
    
    for report in reports:
        if report.get('status') != 'success':
            continue
            
        filename = report.get('filename', '')
        match = re.match(pattern, filename)
        
        if match:
            stock_code, version, date_str = match.groups()
            # 格式化日期: 20260122 -> 2026-01-22
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            
            grouped[stock_code][version].append({
                'filename': filename,
                'date': formatted_date,
                'date_str': date_str,
                'timestamp': report.get('timestamp', '')
            })
    
    # 按日期排序（最新的在前面）
    for stock_code in grouped:
        for version in ['professional', 'normal']:
            grouped[stock_code][version].sort(
                key=lambda x: x['date_str'], 
                reverse=True
            )
    
    return dict(grouped)


@app.route('/images/<path:filename>')
def serve_image(filename):
    """提供图片静态文件服务"""
    images_dir = reporter.reports_dir / 'images' if reporter else Path('./reports/images')
    return send_from_directory(images_dir, filename)


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="金融报告 Web 服务器")
    parser.add_argument("--config", help="配置文件路径", default=None)
    parser.add_argument("--reports-dir", help="报告存储目录", default="./reports")
    parser.add_argument("--host", help="服务器地址", default="0.0.0.0")
    parser.add_argument("--port", help="服务器端口", type=int, default=8080)
    parser.add_argument("--debug", action="store_true", help="调试模式")
    args = parser.parse_args()
    
    # 初始化
    init_reporter(args.config, args.reports_dir)
    
    print(f"\n{'='*60}")
    print(f"🌐 金融报告 Web 服务器启动")
    print(f"{'='*60}")
    print(f"📍 访问地址：http://{args.host}:{args.port}")
    print(f"📂 报告目录：{reporter.reports_dir}")
    print(f"{'='*60}\n")
    
    # 启动服务器
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == "__main__":
    main()
