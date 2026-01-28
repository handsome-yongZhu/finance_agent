# Prompt 架构快速入门

## 核心概念：正交分离

两个独立的维度：

```
分析视角（如何分析）     写作形式（如何组织）
    ↓                        ↓
professional             first
normal                   incremental
```

**组合示例**：
- `professional` × `first` = 专业深度分析的首次完整报告
- `normal` × `incremental` = 通俗叙事风格的增量更新报告

## 目录结构一览

```
prompts/
├── base/                      # 基础系统提示
├── analysis_perspectives/     # 分析视角：professional / normal
├── writing_formats/           # 写作形式：first / incremental
├── report_structures/         # 具体结构：{perspective}_{format}.md
├── components/                # 可复用组件
└── configs/                   # 组装配置
    └── report_configs.yaml
```

## 使用方法

### Python 代码

```python
from prompt_builder import PromptBuilder

builder = PromptBuilder()

# 构建系统提示词
system_prompt = builder.build_system_prompt(
    perspective="professional",  # 或 "normal"
    format="first"              # 或 "incremental"
)

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
```

### 所有支持的组合

| 分析视角 | 写作形式 | 配置键 | 说明 |
|---------|---------|--------|------|
| professional | first | `professional_first` | 专业深度分析，首次完整报告 |
| professional | incremental | `professional_incremental` | 专业深度分析，增量更新报告 |
| normal | first | `normal_first` | 通俗叙事风格，首次完整报告（6段式） |
| normal | incremental | `normal_incremental` | 通俗叙事风格，增量更新报告（6段式） |

## 为什么这样设计？

### 问题：旧架构的混乱

```python
# 旧架构：复杂的条件判断
if version == "professional":
    if is_first_report:
        template = self.stock_professional_template
        additional = ""
    else:
        template = self.stock_professional_template
        additional = "这是增量报告..."
else:  # normal
    if is_first_report:
        template = self.stock_normal_template
        additional = ""
    else:
        # ... 更多嵌套条件
```

**问题**：
- 逻辑混在代码里
- 难以维护和扩展
- 职责不清晰

### 解决：正交分离

```python
# 新架构：清晰的维度分离
system_prompt = builder.build_system_prompt(
    perspective="professional",  # 分析视角
    format="first"              # 写作形式
)
```

**优势**：
- 两个维度完全独立
- 配置驱动，无需改代码
- 扩展简单（新增维度自动组合）

## 如何扩展？

### 新增一种分析视角（如"量化分析"）

1. 创建文件：`analysis_perspectives/quantitative.md`
2. 创建结构模板：
   - `report_structures/quantitative_first.md`
   - `report_structures/quantitative_incremental.md`
3. 更新配置：`configs/report_configs.yaml`
4. 完成！无需修改任何 Python 代码

### 新增一种写作形式（如"周报"）

1. 创建文件：`writing_formats/weekly.md`
2. 创建结构模板：
   - `report_structures/professional_weekly.md`
   - `report_structures/normal_weekly.md`
3. 更新配置
4. 完成！

## 文件说明

### `analysis_perspectives/` - 分析视角

决定"用什么方法分析"：

- **professional.md**：专业深度分析
  - 基本面分析（财务、业绩、行业地位）
  - 技术面分析（趋势、量价、指标）
  - 估值分析（PE/PB对比、DCF模型）
  - 行业分析（产业趋势、竞争格局）

- **normal.md**：通俗叙事分析
  - 热点事件切入法
  - 逻辑链推导法
  - 宏观映射法
  - 结构化拆解法（3个维度）

### `writing_formats/` - 写作形式

决定"如何组织内容"：

- **first_time.md**：首次完整报告
  - 包含所有背景信息
  - 完整的数据展示
  - 详尽的分析框架

- **incremental.md**：增量更新报告
  - 只关注变化
  - 对比上次报告
  - 简化重复信息

### `report_structures/` - 报告结构

具体的报告大纲模板，每个文件对应一种组合。

### `components/` - 可复用组件

所有报告都会用到的通用片段：
- `data_requirements.md` - 数据搜索要求
- `chart_specifications.md` - 图表生成规格
- `compliance_rules.md` - 合规要求

## 测试

```bash
# 运行测试
python prompt_builder.py

# 输出会显示：
# - 系统提示词长度
# - 任务描述长度
# - 输出规格
# - 所有支持的组合
```

## 下一步

1. **阅读完整文档**：`ARCHITECTURE.md`
2. **查看配置文件**：`configs/report_configs.yaml`
3. **开始创建 Prompt 文件**：按照目录结构创建对应的 .md 文件
4. **迁移指南**：`MIGRATION_GUIDE.md`（如何从旧架构迁移）

## 常见问题

**Q: 为什么要分成两个维度？**

A: 因为"如何分析"和"如何组织"是两个独立的关注点。分离后可以独立优化，组合灵活。

**Q: 新增报告类型需要改代码吗？**

A: 不需要！只需要创建对应的 Prompt 文件和更新配置文件即可。

**Q: 旧的 Prompt 文件怎么办？**

A: 可以保留作为参考，或者按照迁移指南拆解到新目录结构中。

**Q: 如果我只想要 3 种组合怎么办？**

A: 配置文件中只定义你需要的组合即可。未定义的组合会报错。
