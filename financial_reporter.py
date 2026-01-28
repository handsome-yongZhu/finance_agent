#!/usr/bin/env python3
"""
金融报告生成模块
Financial Report Generator Module
自动调研金融数据并生成报告
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from mini_agent.agent import Agent
from mini_agent.config import Config
from mini_agent.llm import LLMClient
from mini_agent.schema import LLMProvider
from mini_agent.tools.bash_tool import BashTool, BashOutputTool
from mini_agent.tools.file_tools import ReadTool, WriteTool, EditTool
from mini_agent.tools.mcp_loader import load_mcp_tools_async

from prompt_builder import PromptBuilder


class FinancialReporter:
    """金融报告生成器 - 使用正交分离架构"""
    
    def __init__(self, config_path: str = None, reports_dir: str = "./reports", prompts_dir: str = "./prompts"):
        """
        初始化金融报告生成器
        
        Args:
            config_path: 配置文件路径
            reports_dir: 报告存储目录
            prompts_dir: Prompt 模板目录
        """
        # 加载配置
        if config_path:
            self.config = Config.from_yaml(config_path)
        else:
            self.config = Config.load()
        
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.metadata_dir = self.reports_dir / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        self.images_dir = self.reports_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 PromptBuilder（新架构）
        self.prompts_dir = Path(prompts_dir)
        self.prompt_builder = PromptBuilder(prompts_dir)
        
        print("✅ 金融报告生成器初始化完成（使用正交分离架构）")
    
    async def generate_stock_report(
        self, 
        stock_code: str, 
        version: str = "professional", 
        date: datetime = None
    ) -> Dict[str, Any]:
        """
        为单个股票生成报告
        
        Args:
            stock_code: 股票代码
            version: 报告版本 ("professional" 或 "normal")，对应分析视角
            date: 报告日期，默认为今天
            
        Returns:
            报告元数据字典
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        date_str_short = date.strftime("%Y%m%d")
        report_filename = f"{stock_code}_{version}_{date_str_short}.md"
        
        print(f"\n{'='*60}")
        print(f"🔄 开始生成 {stock_code} 的{version}版报告...")
        print(f"{'='*60}\n")
        
        # 检查历史报告，判断是首次还是增量
        last_report_content, last_report_date, is_first_report = self._check_history(
            stock_code, version
        )
        
        # 确定写作形式
        format_type = "first" if is_first_report else "incremental"
        
        if is_first_report:
            print(f"✨ 这是{stock_code}的首次{version}版报告")
        else:
            print(f"📖 找到{stock_code}的上次{version}版报告：{last_report_date}")
        
        # 构建上下文
        context = {
            "stock_code": stock_code,
            "date": date_str,
            "report_filename": report_filename,
            "last_date": last_report_date,
        }
        
        # 使用 PromptBuilder 构建 system_prompt 和 task
        try:
            system_prompt = self.prompt_builder.build_system_prompt(
                perspective=version,  # professional / normal
                format=format_type    # first / incremental
            )
            
            task = self.prompt_builder.build_task(
                perspective=version,
                format=format_type,
                context=context
            )
        except Exception as e:
            print(f"⚠️  Prompt 构建失败: {e}")
            print(f"⚠️  提示: 请确保 prompts/ 目录下的文件结构完整")
            print(f"⚠️  需要的文件: analysis_perspectives/{version}.md, writing_formats/{format_type}.md 等")
            raise
        
        # 创建 Agent 并执行
        agent = await self._create_agent(stock_code, system_prompt)
        
        try:
            # 如果是增量报告，先让 Agent 阅读上次报告
            if not is_first_report and last_report_content:
                print(f"📚 让 Agent 阅读{stock_code}的上次报告...\n")
                context_message = self._build_context_message(
                    stock_code, version, last_report_date, last_report_content
                )
                agent.add_user_message(context_message)
            
            # 执行任务
            print("🤖 AI Agent 开始工作...\n")
            agent.add_user_message(task)
            result = await agent.run()
            
            # 验证和保存
            report_path = self.reports_dir / report_filename
            if not report_path.exists():
                raise FileNotFoundError(f"Agent未能生成报告文件：{report_filename}")
            
            # 保存元数据
            metadata = self._save_metadata(
                stock_code=stock_code,
                version=version,
                date=date,
                date_str=date_str,
                report_filename=report_filename,
                report_path=report_path,
                result=result,
                status="success"
            )
            
            print(f"\n{'='*60}")
            print(f"✅ {stock_code} {version}版报告生成成功！")
            print(f"📄 报告位置：{report_path}")
            print(f"{'='*60}\n")
            
            return metadata
            
        except Exception as e:
            print(f"\n❌ 报告生成失败：{str(e)}\n")
            
            # 保存错误元数据
            metadata = self._save_metadata(
                stock_code=stock_code,
                version=version,
                date=date,
                date_str=date_str,
                status="failed",
                error=str(e)
            )
            raise
    
    async def _create_agent(self, stock_code: str, system_prompt: str) -> Agent:
        """
        创建配置好的Agent实例
        
        Args:
            stock_code: 股票代码
            system_prompt: 系统提示词（由 PromptBuilder 构建）
        """
        # 1. 创建LLM客户端
        provider = LLMProvider.ANTHROPIC if self.config.llm.provider.lower() == "anthropic" else LLMProvider.OPENAI
        llm_client = LLMClient(
            api_key=self.config.llm.api_key,
            provider=provider,
            api_base=self.config.llm.api_base,
            model=self.config.llm.model,
        )
        
        # 2. 为该股票创建图片目录
        stock_images_dir = self.images_dir / stock_code
        stock_images_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. 初始化工具
        tools = []
        tools.extend([
            WriteTool(workspace_dir=str(self.reports_dir)),
            ReadTool(workspace_dir=str(self.reports_dir)),
        ])
        tools.append(BashTool())
        tools.append(BashOutputTool())
        
        # 加载 MCP 工具
        try:
            mcp_tools = await load_mcp_tools_async()
            if mcp_tools:
                tools.extend(mcp_tools)
                print(f"✅ 加载了 {len(mcp_tools)} 个 MCP 工具")
        except Exception as e:
            print(f"⚠️  MCP工具加载失败: {e}")
        
        # 4. 创建Agent（使用传入的 system_prompt）
        agent = Agent(
            llm_client=llm_client,
            system_prompt=system_prompt,  # 来自 PromptBuilder
            tools=tools,
            max_steps=self.config.agent.max_steps,
            workspace_dir=str(self.reports_dir),
        )
        
        return agent
    
    def _check_history(self, stock_code: str, version: str) -> tuple:
        """
        检查历史报告
        
        Returns:
            (last_report_content, last_report_date, is_first_report)
        """
        all_reports = self.get_all_reports()
        stock_reports = [
            r for r in all_reports 
            if r.get('status') == 'success' 
            and r.get('stock_code') == stock_code
            and r.get('version') == version
        ]
        
        if not stock_reports:
            return None, None, True
        
        last_report = stock_reports[0]
        last_report_date = last_report.get('date')
        last_report_path = self.reports_dir / last_report['filename']
        
        if last_report_path.exists():
            with open(last_report_path, 'r', encoding='utf-8') as f:
                last_report_content = f.read()
            return last_report_content, last_report_date, False
        
        return None, None, True
    
    def _build_context_message(
        self,
        stock_code: str,
        version: str,
        last_report_date: str,
        last_report_content: str
    ) -> str:
        """构建上下文消息（让 Agent 阅读上次报告）"""
        return f"""在生成今天的报告之前，请先阅读{stock_code}上次的{version}版报告（{last_report_date}）：

---
{last_report_content}
---

**已读完上次报告**，你现在了解了该股票的：
- 历史价格水平和趋势
- 公司基本情况
- 之前的分析结论

接下来生成今天的报告时，请注意增量原则，重点关注变化。"""
    
    def _save_metadata(self, **kwargs) -> Dict[str, Any]:
        """保存报告元数据"""
        metadata = {}
        
        # 基础信息
        date = kwargs.get('date', datetime.now())
        date_str = kwargs.get('date_str', date.strftime("%Y-%m-%d"))
        datetime_str = date.strftime("%Y%m%d_%H%M%S")
        
        metadata['date'] = date_str
        metadata['timestamp'] = date.isoformat()
        metadata['stock_code'] = kwargs.get('stock_code')
        metadata['version'] = kwargs.get('version')
        metadata['status'] = kwargs.get('status', 'success')
        
        # 成功时的信息
        if metadata['status'] == 'success':
            metadata['filename'] = kwargs.get('report_filename')
            metadata['filepath'] = str(kwargs.get('report_path'))
            metadata['file_size'] = kwargs.get('report_path').stat().st_size
            
            result = kwargs.get('result', '')
            metadata['agent_output'] = result[:200] + "..." if len(result) > 200 else result
            
            metadata_file = self.metadata_dir / f"report_{metadata['stock_code']}_{metadata['version']}_{datetime_str}.json"
        else:
            # 失败时的信息
            metadata['error'] = kwargs.get('error')
            metadata_file = self.metadata_dir / f"report_{metadata['stock_code']}_{metadata['version']}_{datetime_str}_failed.json"
        
        # 保存到文件
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata
    
    def get_all_reports(self) -> list:
        """获取所有报告的元数据列表"""
        reports = []
        for metadata_file in self.metadata_dir.glob("report_*.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    reports.append(metadata)
            except Exception as e:
                print(f"读取元数据文件失败 {metadata_file}: {e}")
        
        reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return reports
    
    def get_report_content(self, filename: str) -> str:
        """获取指定报告的内容"""
        report_path = self.reports_dir / filename
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                return f.read()
        return None


async def main():
    """主函数 - 用于测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="金融报告生成器")
    parser.add_argument("--config", help="配置文件路径", default=None)
    parser.add_argument("--reports-dir", help="报告存储目录", default="./reports")
    parser.add_argument("--prompts-dir", help="Prompt 模板目录", default="./prompts")
    parser.add_argument("--stock", help="股票代码", default="688388")
    parser.add_argument("--version", help="报告版本", choices=["professional", "normal"], default="professional")
    args = parser.parse_args()
    
    reporter = FinancialReporter(
        config_path=args.config,
        reports_dir=args.reports_dir,
        prompts_dir=args.prompts_dir
    )
    
    await reporter.generate_stock_report(
        stock_code=args.stock,
        version=args.version
    )


if __name__ == "__main__":
    asyncio.run(main())
