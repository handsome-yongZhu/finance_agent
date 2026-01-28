#!/usr/bin/env python3
"""
Prompt 构建器 - 基于正交分离的设计

核心理念：将报告生成分解为两个正交维度
  1. 分析视角（如何分析）：professional / normal
  2. 写作形式（如何组织）：first / incremental

两个维度可以自由组合，形成 2×2 = 4 种报告类型
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template


class PromptBuilder:
    """基于正交分离的 Prompt 构建器"""
    
    def __init__(self, prompts_dir: str = "./prompts"):
        """
        初始化 Prompt 构建器
        
        Args:
            prompts_dir: prompts 目录路径
        """
        self.prompts_dir = Path(prompts_dir)
        
        # 加载配置
        config_path = self.prompts_dir / "configs" / "report_configs.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            self.configs = yaml.safe_load(f)
    
    def build_prompt(
        self,
        perspective: str,  # 分析视角: professional / normal
        format: str,       # 写作形式: first / incremental
        context: Dict[str, Any] = None
    ) -> str:
        """
        构建完整的 Prompt
        
        Args:
            perspective: 分析视角（professional / normal）
            format: 写作形式（first / incremental）
            context: 上下文变量（用于模板替换）
        
        Returns:
            完整的 Prompt
        """
        if context is None:
            context = {}
        
        # 构建配置键
        config_key = f"{perspective}_{format}"
        
        if config_key not in self.configs['report_types']['stock_report']:
            raise ValueError(f"配置不存在: {config_key}")
        
        config = self.configs['report_types']['stock_report'][config_key]
        
        # 加载并组装所有组件
        parts = []
        for component_path in config['components']:
            content = self._load_file(component_path)
            parts.append(content)
        
        # 组装完整 Prompt
        prompt = "\n\n---\n\n".join(parts)
        
        # 替换模板变量
        return self._render_template(prompt, context)
    
    def build_system_prompt(
        self,
        perspective: str,
        format: str = None
    ) -> str:
        """
        构建系统提示词部分（不包含具体任务）
        
        Args:
            perspective: 分析视角
            format: 写作形式（可选，用于加载写作格式指南）
        
        Returns:
            系统提示词
        """
        parts = []
        
        # 1. 基础系统提示
        parts.append(self._load_file("base/system_prompt.md"))
        
        # 2. 分析视角
        parts.append(self._load_file(f"analysis_perspectives/{perspective}.md"))
        
        # 3. 写作形式指南（如果需要）
        if format:
            parts.append(self._load_file(f"writing_formats/{format}.md"))
        
        # 4. 通用组件
        parts.append(self._load_file("components/data_requirements.md"))
        parts.append(self._load_file("components/chart_specifications.md"))
        parts.append(self._load_file("components/compliance_rules.md"))
        
        return "\n\n---\n\n".join(parts)
    
    def build_task(
        self,
        perspective: str,
        format: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        构建任务描述（报告结构部分）
        
        Args:
            perspective: 分析视角
            format: 写作形式
            context: 上下文变量
        
        Returns:
            任务描述
        """
        if context is None:
            context = {}
        
        # 加载报告结构模板
        structure_path = f"report_structures/{perspective}_{format}.md"
        structure = self._load_file(structure_path)
        
        # 构建任务头部
        header = self._build_task_header(perspective, format, context)
        
        # 组装
        task = f"{header}\n\n{structure}"
        
        # 替换变量
        return self._render_template(task, context)
    
    def get_output_specs(
        self,
        perspective: str,
        format: str
    ) -> Dict[str, Any]:
        """获取输出规格"""
        config_key = f"{perspective}_{format}"
        config = self.configs['report_types']['stock_report'][config_key]
        return config.get('output_specs', {})
    
    def _load_file(self, relative_path: str) -> str:
        """加载文件内容"""
        file_path = self.prompts_dir / relative_path
        
        if not file_path.exists():
            # 如果文件不存在，返回占位符
            return f"<!-- TODO: Create {relative_path} -->"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def _render_template(self, content: str, context: Dict[str, Any]) -> str:
        """渲染模板变量"""
        template = Template(content)
        return template.render(**context)
    
    def _build_task_header(
        self,
        perspective: str,
        format: str,
        context: Dict[str, Any]
    ) -> str:
        """构建任务头部"""
        perspective_name = "专业版" if perspective == "professional" else "普通版"
        format_name = "首次完整报告" if format == "first" else "增量更新报告"
        
        return f"""# 任务：生成股票分析报告（{perspective_name} - {format_name}）

**股票代码**：{context.get('stock_code', 'N/A')}
**报告日期**：{context.get('date', 'N/A')}
**分析视角**：{perspective_name}
**写作形式**：{format_name}
**保存文件名**：`{context.get('report_filename', 'N/A')}`
"""


# 使用示例
if __name__ == "__main__":
    builder = PromptBuilder()
    
    print("="*60)
    print("示例 1：专业视角 × 首次报告")
    print("="*60)
    
    # 构建系统提示词
    system_prompt = builder.build_system_prompt(
        perspective="professional",
        format="first"
    )
    print(f"\n系统提示词长度: {len(system_prompt)} 字符")
    print(f"预览:\n{system_prompt[:300]}...\n")
    
    # 构建任务描述
    task = builder.build_task(
        perspective="professional",
        format="first",
        context={
            "stock_code": "688388",
            "date": "2026-01-27",
            "report_filename": "688388_professional_20260127.md"
        }
    )
    print(f"\n任务描述长度: {len(task)} 字符")
    print(f"预览:\n{task[:300]}...\n")
    
    # 获取输出规格
    specs = builder.get_output_specs("professional", "first")
    print(f"\n输出规格: {specs}\n")
    
    print("="*60)
    print("示例 2：通俗视角 × 增量报告")
    print("="*60)
    
    system_prompt = builder.build_system_prompt(
        perspective="normal",
        format="incremental"
    )
    print(f"\n系统提示词长度: {len(system_prompt)} 字符")
    
    task = builder.build_task(
        perspective="normal",
        format="incremental",
        context={
            "stock_code": "688388",
            "date": "2026-01-27",
            "last_date": "2026-01-20",
            "report_filename": "688388_normal_20260127.md"
        }
    )
    print(f"任务描述长度: {len(task)} 字符")
    
    specs = builder.get_output_specs("normal", "incremental")
    print(f"\n输出规格: {specs}\n")
    
    print("="*60)
    print("支持的所有组合:")
    print("="*60)
    for perspective in ["professional", "normal"]:
        for format in ["first", "incremental"]:
            key = f"{perspective}_{format}"
            print(f"  - {key}")
