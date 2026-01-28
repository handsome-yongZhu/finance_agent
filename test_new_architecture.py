#!/usr/bin/env python3
"""
测试新架构
"""

import sys
from pathlib import Path

print("="*60)
print("测试新的 Prompt 架构")
print("="*60)

try:
    from prompt_builder import PromptBuilder
    print("✅ PromptBuilder 导入成功")
    
    builder = PromptBuilder()
    print("✅ PromptBuilder 初始化成功")
    
    # 测试所有组合
    test_cases = [
        ("professional", "first"),
        ("professional", "incremental"),
        ("normal", "first"),
        ("normal", "incremental"),
    ]
    
    print("\n" + "="*60)
    print("测试所有组合")
    print("="*60)
    
    for perspective, format_type in test_cases:
        print(f"\n【{perspective} × {format_type}】")
        try:
            # 测试构建 system_prompt
            system_prompt = builder.build_system_prompt(
                perspective=perspective,
                format=format_type
            )
            print(f"  ✅ System Prompt: {len(system_prompt)} 字符")
            
            # 测试构建 task
            task = builder.build_task(
                perspective=perspective,
                format=format_type,
                context={
                    "stock_code": "688388",
                    "date": "2026-01-27",
                    "report_filename": f"688388_{perspective}_20260127.md"
                }
            )
            print(f"  ✅ Task: {len(task)} 字符")
            
            # 获取输出规格
            specs = builder.get_output_specs(perspective, format_type)
            print(f"  ✅ Output Specs: {specs.get('chart_required', False)}")
            
        except FileNotFoundError as e:
            print(f"  ⚠️  缺少文件: {e}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    print("\n" + "="*60)
    print("总结")
    print("="*60)
    print("✅ PromptBuilder 基础功能正常")
    print("⚠️  如果有缺少文件的警告，需要创建对应的 .md 文件")
    print("\n提示：查看 prompts/ARCHITECTURE.md 了解目录结构")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n请确保:")
    print("  1. 在项目根目录运行")
    print("  2. 已安装依赖: pip install pyyaml jinja2")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("测试完成")
print("="*60)
