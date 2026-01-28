#!/usr/bin/env python3
"""
定时任务调度器
Scheduler for Daily Financial Reports
每天定时生成金融报告
"""

import asyncio
import schedule
import time
import yaml
from datetime import datetime
from pathlib import Path

from financial_reporter import FinancialReporter


class ReportScheduler:
    """报告调度器"""
    
    def __init__(self, config_path: str = None, reports_dir: str = "./reports", 
                 schedule_time: str = "09:00", stocks_config_path: str = "stocks_config.yaml"):
        """
        初始化调度器
        
        Args:
            config_path: 配置文件路径
            reports_dir: 报告存储目录
            schedule_time: 每天执行时间，格式："HH:MM"
            stocks_config_path: 股票配置文件路径
        """
        self.reporter = FinancialReporter(config_path, reports_dir)
        self.schedule_time = schedule_time
        self.is_running = False
        
        # 从stocks_config.yaml加载股票列表
        self.stocks = self._load_stocks_config(stocks_config_path)
        
    def _load_stocks_config(self, config_path: str) -> list:
        """加载股票配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                stocks = config.get('stocks', [])
                print(f"📊 已加载 {len(stocks)} 只股票配置")
                for stock in stocks:
                    print(f"   - {stock['code']}: {stock['name']}")
                return stocks
        except Exception as e:
            print(f"⚠️  加载股票配置失败: {e}")
            print("使用默认配置")
            return [
                {"code": "688388", "name": "嘉元科技"},
                {"code": "688256", "name": "寒武纪"},
            ]
        
    async def generate_report_task(self):
        """执行报告生成任务（异步）- 串行为每只股票生成2个版本"""
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 定时任务触发")
        print(f"📊 将为 {len(self.stocks)} 只股票生成报告（每只2个版本）")
        print(f"🔄 串行执行模式：逐个生成，避免资源冲突")
        print(f"{'='*60}\n")
        
        total_count = len(self.stocks) * 2
        success_count = 0
        failed_count = 0
        start_time = datetime.now()
        
        # 串行处理每只股票
        for idx, stock in enumerate(self.stocks, 1):
            stock_code = stock['code']
            stock_name = stock['name']
            
            print(f"\n{'─'*60}")
            print(f"📈 [{idx}/{len(self.stocks)}] 处理：{stock_name} ({stock_code})")
            print(f"{'─'*60}\n")
            
            # 生成普通版报告
            try:
                print(f"🔄 生成普通版报告...")
                await self.reporter.generate_stock_report(
                    stock_code=stock_code,
                    version="normal"
                )
                success_count += 1
                print(f"✅ {stock_name} 普通版报告生成成功")
            except Exception as e:
                failed_count += 1
                print(f"❌ {stock_name} 普通版报告生成失败: {e}")
            
            # 等待5秒避免API限流
            print(f"⏳ 等待5秒...")
            await asyncio.sleep(5)
            
            # 生成专业版报告
            try:
                print(f"🔄 生成专业版报告...")
                await self.reporter.generate_stock_report(
                    stock_code=stock_code,
                    version="professional"
                )
                success_count += 1
                print(f"✅ {stock_name} 专业版报告生成成功")
            except Exception as e:
                failed_count += 1
                print(f"❌ {stock_name} 专业版报告生成失败: {e}")
            
            # 股票之间等待10秒
            if idx < len(self.stocks):
                print(f"\n⏳ 等待10秒后处理下一只股票...")
                await asyncio.sleep(10)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 汇总统计
        print(f"\n{'='*60}")
        print(f"📊 报告生成完成")
        print(f"{'='*60}")
        print(f"⏱️  总耗时: {duration/60:.1f} 分钟")
        print(f"✅ 成功: {success_count}/{total_count}")
        print(f"❌ 失败: {failed_count}/{total_count}")
        print(f"{'='*60}\n")
    
    def _run_async_task(self):
        """同步包装器，用于 schedule 调用"""
        # 直接运行异步任务
        asyncio.run(self.generate_report_task())
    
    def start(self):
        """启动调度器"""
        print(f"\n{'='*60}")
        print(f"📅 金融报告调度器启动")
        print(f"{'='*60}")
        print(f"⏰ 每天 {self.schedule_time} 自动生成报告")
        print(f"📂 报告保存目录：{self.reporter.reports_dir}")
        print(f"🔄 执行模式：串行（避免资源冲突）")
        print(f"{'='*60}\n")
        
        # 设置定时任务
        schedule.every().day.at(self.schedule_time).do(self._run_async_task)
        
        # 显示下一次执行时间
        next_run = schedule.next_run()
        if next_run:
            print(f"⏭️  下次执行时间：{next_run.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.is_running = True
        
        # 主循环
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n\n⏹️  调度器已停止")
            self.is_running = False
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
    
    async def run_once(self):
        """立即执行一次任务（用于测试）"""
        print("🚀 手动触发任务...\n")
        await self.generate_report_task()


def main():
    """主函数（同步）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="金融报告定时调度器")
    parser.add_argument("--config", help="配置文件路径", default=None)
    parser.add_argument("--reports-dir", help="报告存储目录", default="./reports")
    parser.add_argument("--time", help="每天执行时间 (HH:MM)", default="09:00")
    parser.add_argument("--once", action="store_true", help="立即执行一次（不启动定时任务）")
    args = parser.parse_args()
    
    scheduler = ReportScheduler(
        config_path=args.config,
        reports_dir=args.reports_dir,
        schedule_time=args.time
    )
    
    if args.once:
        # 立即执行一次（需要用asyncio.run）
        asyncio.run(scheduler.run_once())
    else:
        # 启动定时调度（同步阻塞）
        scheduler.start()


if __name__ == "__main__":
    main()