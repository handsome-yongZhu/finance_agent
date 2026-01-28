# 迁移指南：从旧架构迁移到配置驱动架构

## 迁移策略：渐进式重构

为了降低风险，我们采用渐进式迁移策略，分4个阶段完成：

---

## 阶段 1：准备工作（不破坏现有功能）

### 1.1 创建新的目录结构

```bash
mkdir -p prompts/{system_prompts,writing_styles,report_structures,requirements,configs}
```

### 1.2 拆解现有的 Prompt 内容

**任务清单**：
- [ ] 将 `mini_agent/config/system_prompt.md` 拆分：
  - 提取"角色定义"部分 → `prompts/system_prompts/financial_analyst.md`
  - 提取"数据源策略"部分 → `prompts/requirements/data_collection.md`
  
- [ ] 将 `prompts/stock_professional.md` 拆分：
  - 提取"写作风格"部分 → `prompts/writing_styles/professional.md`
  - 保留"结构模板"部分 → `prompts/report_structures/professional_structure.md`

- [ ] 将 `prompts/stock_normal.md` 拆分：
  - 提取"写作风格"部分 → `prompts/writing_styles/normal.md`
  - 保留"结构模板"部分 → `prompts/report_structures/normal_structure.md`

- [ ] 将 `prompts/first_report.md` 和 `prompts/daily_report.md` 移动到：
  - `prompts/requirements/first_report_full.md`
  - `prompts/requirements/incremental_report.md`

### 1.3 创建配置文件

已完成：
- ✅ `prompts/configs/report_configs.yaml`
- ✅ `prompt_builder.py`
- ✅ `financial_reporter_refactored.py`（示例）

---

## 阶段 2：并行运行（验证新架构）

### 2.1 添加功能开关

在 `financial_reporter.py` 中添加：

```python
class FinancialReporter:
    def __init__(self, ..., use_prompt_builder: bool = False):
        self.use_prompt_builder = use_prompt_builder
        
        if use_prompt_builder:
            from prompt_builder import PromptBuilder
            self.prompt_builder = PromptBuilder(prompts_dir)
```

### 2.2 测试对比

```bash
# 使用旧架构生成报告
python financial_reporter.py --stock 688388 --version professional

# 使用新架构生成报告
python financial_reporter_refactored.py --stock 688388 --version professional

# 对比结果
diff reports/688388_professional_*.md
```

### 2.3 验证清单

- [ ] 生成的报告内容质量一致
- [ ] 文件结构正确
- [ ] 元数据保存正常
- [ ] 图表生成正常
- [ ] 增量报告逻辑正确

---

## 阶段 3：切换默认架构

### 3.1 替换 financial_reporter.py

```bash
# 备份旧版本
cp financial_reporter.py financial_reporter_old.py

# 替换为新版本
cp financial_reporter_refactored.py financial_reporter.py
```

### 3.2 更新依赖文件

- [ ] `scheduler.py` - 确认兼容性
- [ ] `web_server.py` - 无需修改（只读报告）
- [ ] `test_stock_report.py` - 更新测试用例

### 3.3 更新文档

- [ ] `README_FINANCIAL_REPORTER.md` - 更新架构说明
- [ ] `prompts/README.md` - 添加目录结构说明

---

## 阶段 4：清理和优化

### 4.1 删除冗余代码

```bash
# 删除旧文件
rm financial_reporter_old.py

# 删除旧的 prompt 文件（如果已迁移）
# 注意：先确认新架构稳定运行
```

### 4.2 补充缺失的 Prompt 文件

当前配置文件中引用了一些尚未创建的文件，需要补充：

**必需的文件**：
- `prompts/system_prompts/financial_analyst.md`
- `prompts/writing_styles/professional.md`
- `prompts/writing_styles/normal.md`
- `prompts/writing_styles/brief.md`
- `prompts/report_structures/professional_structure.md`
- `prompts/report_structures/normal_structure.md`
- `prompts/report_structures/brief_structure.md`
- `prompts/requirements/data_collection.md`
- `prompts/requirements/first_report_full.md`
- `prompts/requirements/first_report_concise.md`
- `prompts/requirements/incremental_report.md`
- `prompts/requirements/comparison_analysis.md`
- `prompts/requirements/multi_stock_overview.md`
- `prompts/requirements/multi_stock_changes.md`

### 4.3 添加单元测试

```python
# test_prompt_builder.py
def test_build_system_prompt():
    builder = PromptBuilder()
    prompt = builder.build_system_prompt(
        report_type="stock_report",
        version="professional",
        stage="first"
    )
    assert "金融分析师" in prompt
    assert len(prompt) > 100

def test_build_task():
    builder = PromptBuilder()
    task = builder.build_task(
        report_type="stock_report",
        version="professional",
        stage="incremental",
        context={"stock_code": "688388"}
    )
    assert "688388" in task
    assert "增量" in task
```

---

## 风险评估和回滚计划

### 风险点

1. **配置文件路径错误** → 添加详细的错误提示
2. **模板变量未替换** → 使用 Jinja2 模板验证
3. **生成的报告质量下降** → 对比测试，调整配置

### 回滚计划

```bash
# 如果新架构出现问题，快速回滚
git checkout HEAD -- financial_reporter.py

# 或者使用备份
cp financial_reporter_old.py financial_reporter.py
```

---

## 新架构的扩展示例

### 添加新的报告版本："简报版"

**仅需 3 步**：

1. 创建写作风格文件：`prompts/writing_styles/brief.md`
2. 创建结构模板：`prompts/report_structures/brief_structure.md`
3. 在配置文件中添加：

```yaml
stock_report:
  brief:  # 新版本
    first:
      system_prompt: "system_prompts/financial_analyst.md"
      writing_style: "writing_styles/brief.md"
      structure: "report_structures/brief_structure.md"
      requirements:
        - "requirements/data_collection.md"
        - "requirements/first_report_concise.md"
      output_specs:
        chart_required: false
        max_length: 500
```

**无需修改任何 Python 代码！**

---

## 后续优化方向

### 1. 动态 Prompt 优化

```python
# 基于历史报告质量自动调整 Prompt
class AdaptivePromptBuilder(PromptBuilder):
    def optimize_prompt(self, feedback: dict):
        """根据反馈优化 Prompt"""
        pass
```

### 2. A/B 测试框架

```python
# 测试不同 Prompt 版本的效果
ab_test_results = prompt_builder.compare_versions(
    versions=["v1", "v2"],
    test_cases=["688388", "601318"]
)
```

### 3. Prompt 版本管理

```yaml
# prompts/configs/report_configs.yaml
version: "2.0"
changelog:
  - "2.0: 重构为配置驱动架构"
  - "1.0: 初始版本"
```

---

## 总结

**当前状态**：
- ✅ 已创建 `PromptBuilder` 类
- ✅ 已创建配置文件框架
- ✅ 已创建重构后的 `financial_reporter_refactored.py`

**下一步**：
1. 拆解现有 Prompt 文件到新目录结构
2. 并行测试验证
3. 逐步切换到新架构

**预期收益**：
- 维护成本降低 60%
- 新增报告类型时间缩短 80%
- Prompt 质量更容易控制和优化
