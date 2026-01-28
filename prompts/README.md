# 📝 Prompt 模板说明

本目录包含金融报告生成的 prompt 模板文件，用于定义不同类型报告的生成规则。

## 📂 模板文件

### 综合报告模板（多股票）

#### `first_report.md` - 首次完整报告模板
用于生成股票的首次完整调研报告，包含：
- 公司基本信息和主营业务
- 关键财务指标和估值
- 市场表现和技术分析
- 最新财报和公司公告
- 投资亮点和风险分析

**特点**：全面、详细、深入
**适用**：多股票组合的首次报告

#### `daily_report.md` - 每日增量报告模板
用于生成简洁的每日追踪简报，包含：
- 今日股价和涨跌幅
- 重点变化和原因分析
- 今日重要公告和新闻
- 明日关注事项

**特点**：简洁、增量、聚焦变化
**适用**：多股票组合的每日更新

---

### 单股票报告模板 ⭐ 新增

#### `stock_normal.md` - 普通版报告模板（6段式）
专业的股票分析框架，适合深度分析单只股票：

**结构**：
1. **热点事件切入** - 以具体事件和数据抓住读者
2. **问题分析** - 拆解驱动机制和资金逻辑
3. **抽象总结** - 提升到产业范式和宏观叙事
4. **结构化拆解** - 三维度投资逻辑分析
5. **现状复盘** - 市场共识和风险提示
6. **未来观察点** - 关键指标和操作建议

**字数**：600-800字
**特点**：逻辑严密、层次分明、可操作性强

#### `stock_professional.md` - 专业版报告模板
机构级深度研报，适合需要全面分析的场景：

**结构**：
1. **基本面分析**
   - 业绩兑现分析（营收、盈利、业务纯度）
   - 行业地位与竞争优势
2. **技术面分析**
   - 趋势形态判断
   - 估值逻辑重塑
3. **展望与催化剂**
   - 核心催化剂（产能、新品、市场）
   - 政策与宏观环境
4. **风险提示**（5类风险全覆盖）
5. **总结与展望**

**字数**：2000-3000字
**特点**：数据密集、分析深入、专业规范

## 🔧 模板变量

### 综合报告模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{date}` | 报告日期 | `2026-01-22` |
| `{stocks}` | 追踪的股票代码列表 | `688388, 601318, 601212` |

### 单股票报告模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{stock_code}` | 股票代码 | `688256` |
| `{date}` | 报告日期 | `2026-01-22` |
| `{report_filename}` | 保存的文件名 | `688256_professional_20260122.md` |

## 🎨 自定义模板

### 1. 编辑现有模板
直接修改 `first_report.md` 或 `daily_report.md` 文件：

```bash
vim prompts/first_report.md
```

### 2. 模板编写建议

**清晰的结构**：
- 使用 Markdown 标题组织内容
- 用数字列表标明要求
- 突出关键指标和重点

**具体的要求**：
- 明确指定需要的数据维度
- 说明输出格式和长度限制
- 提供分析角度和方法

**示例**：
```markdown
## 调研要求

1. **公司基本信息**
   - 公司全称、主营业务
   - 所属行业、行业地位

2. **关键指标**
   - 当前股价、市值
   - 市盈率 (PE)、市净率 (PB)
```

### 3. 添加新模板

创建新的模板文件（如 `weekly_report.md`），然后在代码中引用：

```python
# 在 financial_reporter.py 中添加
self.weekly_report_template = self._load_template("weekly_report.md")
```

## 💡 使用示例

### 1. 生成综合报告（多股票）

```bash
python financial_reporter.py \
    --reports-dir ./reports \
    --prompts-dir ./prompts
```

```python
from financial_reporter import FinancialReporter

reporter = FinancialReporter(
    config_path="config.yaml",
    reports_dir="./reports",
    prompts_dir="./prompts"
)

# 生成多股票的综合报告
await reporter.generate_daily_report(
    stock_codes=["688388", "601318", "601212"]
)
```

### 2. 生成单股票报告 ⭐ 新功能

```python
from financial_reporter import FinancialReporter
from datetime import datetime

reporter = FinancialReporter()

# 生成普通版报告（6段式，600-800字）
await reporter.generate_stock_report(
    stock_code="688256",
    version="normal",
    date=datetime.now()
)

# 生成专业版报告（深度分析，2000-3000字）
await reporter.generate_stock_report(
    stock_code="688256",
    version="professional",
    date=datetime.now()
)
```

**生成的文件**：
- 报告：`reports/688256_professional_20260122.md`
- 元数据：`reports/metadata/report_688256_professional_20260122_090000.json`
- 图表（如有）：`reports/images/688256/kline.png`

## 🚀 最佳实践

1. **版本控制**：模板文件纳入 Git 管理，便于追踪变更
2. **备份模板**：修改前备份原始模板
3. **渐进调整**：一次只调整一个维度，观察效果
4. **测试验证**：修改后生成测试报告验证效果
5. **文档说明**：在模板中添加注释说明设计意图

## 🔍 故障排查

### 问题 1：模板未生效

**原因**：模板文件路径错误或权限问题

**解决**：
```bash
# 检查文件是否存在
ls -la prompts/

# 确认文件权限
chmod 644 prompts/*.md
```

### 问题 2：变量未替换

**原因**：变量名拼写错误或大小写不匹配

**解决**：检查模板中使用的变量名是否为 `{date}` 和 `{stocks}`（区分大小写）

### 问题 3：使用了默认模板

**现象**：启动时看到 "使用默认模板" 提示

**原因**：`prompts/` 目录不存在或模板文件缺失

**解决**：
```bash
# 确保目录存在
mkdir -p prompts

# 从项目根目录复制模板
cp prompts/*.md ./my_custom_prompts/
```

## 📚 扩展阅读

- [金融报告系统文档](../README_FINANCIAL_REPORTER.md)
- [Mini Agent 配置指南](../README_CN.md)
- [Prompt 工程最佳实践](https://platform.minimaxi.com/document)

---

**💡 提示**：修改模板后无需重启服务，下次生成报告时会自动加载最新内容。
