#!/usr/bin/env python3
"""
测试单股票报告生成功能
Test Stock Report Generation
"""

import asyncio
from financial_reporter import FinancialReporter
from datetime import datetime


async def test_normal_report():
    """测试普通版报告生成"""
    print("\n" + "="*60)
    print("测试 1: 生成普通版报告（6段式）")
    print("="*60)
    
    reporter = FinancialReporter(
        config_path="mini_agent/config/config.yaml",
        reports_dir="./reports",
        prompts_dir="./prompts"
    )
    
    # 生成寒武纪的普通版报告
    try:
        metadata = await reporter.generate_stock_report(
            stock_code="688256",  # 寒武纪
            version="normal"
        )
        
        print("\n✅ 普通版报告生成成功！")
        print(f"📄 文件位置: {metadata['filepath']}")
        print(f"📊 文件大小: {metadata['file_size']} 字节")
        print(f"⏰ 生成时间: {metadata['timestamp']}")
        
        return True
    except Exception as e:
        print(f"\n❌ 普通版报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_professional_report():
    """测试专业版报告生成"""
    print("\n" + "="*60)
    print("测试 2: 生成专业版报告（深度研报）")
    print("="*60)
    
    reporter = FinancialReporter()
    
    # 生成寒武纪的专业版报告
    try:
        metadata = await reporter.generate_stock_report(
            stock_code="688256",  # 寒武纪
            version="professional"
        )
        
        print("\n✅ 专业版报告生成成功！")
        print(f"📄 文件位置: {metadata['filepath']}")
        print(f"📊 文件大小: {metadata['file_size']} 字节")
        print(f"⏰ 生成时间: {metadata['timestamp']}")
        
        return True
    except Exception as e:
        print(f"\n❌ 专业版报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_incremental_report():
    """测试增量报告功能"""
    print("\n" + "="*60)
    print("测试 3: 测试增量报告（需要先有历史报告）")
    print("="*60)
    
    reporter = FinancialReporter()
    
    # 检查是否已有历史报告
    all_reports = reporter.get_all_reports()
    stock_reports = [
        r for r in all_reports 
        if r.get('stock_code') == '688256' 
        and r.get('version') == 'normal'
        and r.get('status') == 'success'
    ]
    
    if stock_reports:
        print(f"✅ 找到 {len(stock_reports)} 个历史报告")
        print(f"📖 最近一次: {stock_reports[0]['date']}")
        print("\n现在生成增量报告...")
        
        try:
            metadata = await reporter.generate_stock_report(
                stock_code="688256",
                version="normal"
            )
            
            print("\n✅ 增量报告生成成功！")
            print(f"📄 文件位置: {metadata['filepath']}")
            print("\n💡 提示: Agent 已经读取了历史报告，只写了变化部分")
            
            return True
        except Exception as e:
            print(f"\n❌ 增量报告生成失败: {e}")
            return False
    else:
        print("⚠️  没有找到历史报告，这将是首次报告")
        print("💡 提示: 运行两次测试才能看到增量效果")
        return None


async def test_batch_generate():
    """测试批量生成多只股票"""
    print("\n" + "="*60)
    print("测试 4: 批量生成多只股票的报告")
    print("="*60)
    
    reporter = FinancialReporter()
    
    stocks = [
        ("688256", "寒武纪"),
        ("688981", "中芯国际"),
        ("688012", "中微公司"),
    ]
    
    results = []
    
    for stock_code, stock_name in stocks:
        print(f"\n📊 正在生成 {stock_name}({stock_code}) 的报告...")
        
        try:
            metadata = await reporter.generate_stock_report(
                stock_code=stock_code,
                version="normal"
            )
            print(f"   ✅ {stock_name} 报告生成成功")
            results.append((stock_code, True))
        except Exception as e:
            print(f"   ❌ {stock_name} 报告生成失败: {e}")
            results.append((stock_code, False))
    
    # 统计结果
    success_count = sum(1 for _, success in results if success)
    print(f"\n📈 批量生成完成: {success_count}/{len(stocks)} 成功")
    
    return success_count == len(stocks)


async def test_view_reports():
    """查看所有已生成的报告"""
    print("\n" + "="*60)
    print("测试 5: 查看所有已生成的报告")
    print("="*60)
    
    reporter = FinancialReporter()
    
    all_reports = reporter.get_all_reports()
    
    # 按股票代码分组
    by_stock = {}
    for report in all_reports:
        if report.get('status') == 'success':
            stock_code = report.get('stock_code', 'unknown')
            if stock_code not in by_stock:
                by_stock[stock_code] = []
            by_stock[stock_code].append(report)
    
    print(f"\n📊 共找到 {len(all_reports)} 个报告")
    print(f"📈 涉及 {len(by_stock)} 只股票\n")
    
    for stock_code, reports in sorted(by_stock.items()):
        print(f"【{stock_code}】{len(reports)} 个报告:")
        for r in reports[:3]:  # 只显示最近3个
            print(f"  - {r['date']} | {r['version']}版 | {r.get('file_size', 0)} 字节")
        if len(reports) > 3:
            print(f"  ... 还有 {len(reports) - 3} 个更早的报告")
        print()
    
    return True


async def main():
    """主测试函数"""
    print("\n" + "🚀"*30)
    print("单股票报告生成系统 - 功能测试")
    print("🚀"*30)
    
    # 选择测试项目
    print("\n请选择测试项目:")
    print("1. 测试普通版报告生成")
    print("2. 测试专业版报告生成")
    print("3. 测试增量报告功能")
    print("4. 批量生成多只股票")
    print("5. 查看所有已生成报告")
    print("6. 运行所有测试")
    print("0. 退出")
    
    choice = input("\n请输入选择 (0-6): ").strip()
    
    test_results = {}
    
    if choice == "1":
        test_results["普通版报告"] = await test_normal_report()
    elif choice == "2":
        test_results["专业版报告"] = await test_professional_report()
    elif choice == "3":
        test_results["增量报告"] = await test_incremental_report()
    elif choice == "4":
        test_results["批量生成"] = await test_batch_generate()
    elif choice == "5":
        test_results["查看报告"] = await test_view_reports()
    elif choice == "6":
        print("\n🔄 运行所有测试...\n")
        test_results["普通版报告"] = await test_normal_report()
        await asyncio.sleep(2)
        test_results["专业版报告"] = await test_professional_report()
        await asyncio.sleep(2)
        test_results["增量报告"] = await test_incremental_report()
        await asyncio.sleep(2)
        test_results["批量生成"] = await test_batch_generate()
        await asyncio.sleep(2)
        test_results["查看报告"] = await test_view_reports()
    elif choice == "0":
        print("\n👋 退出测试")
        return
    else:
        print("\n❌ 无效选择")
        return
    
    # 显示测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, result in test_results.items():
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  跳过"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n💡 提示:")
    print("- 查看生成的报告: ls -lh reports/*.md")
    print("- 查看报告元数据: cat reports/metadata/*.json")
    print("- 查看图表: ls -lh reports/images/*/")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
