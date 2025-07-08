# README.md 项目结构更新报告

## 更新内容

根据实际项目文件状态，更新了 README.md 中的项目结构和使用说明。

## 主要修改

### 1. 项目结构更新

**移除的文件**:

- `test.py` - 原始测试脚本（已删除）
- `test_new.py` - 新版测试脚本（已删除）
- `check_issues.py` - 项目问题检查脚本（已删除）

**新增的文件**:

- `generate_docx_report.py` - 实验报告生成脚本
- `智能通用新闻爬虫系统实验报告.docx` - 实验报告文档
- `.venv/` - 虚拟环境目录

### 2. 使用说明修改

**修改前**:

```markdown
1. **运行测试验证系统**（推荐先运行）：
   python test_new.py

2. **运行完整的爬虫程序**：
   python run.py
```

**修改后**:

```markdown
**直接运行爬虫程序**：

# 方法一：使用快速运行脚本（推荐）

python run.py

# 方法二：直接运行主程序

python crawler/main.py
```

### 3. 命令行选项更新

**移除**:

- `python test_new.py` - 运行测试
- `python check_issues.py` - 检查项目问题

**新增**:

- `python generate_docx_report.py` - 生成实验报告

### 4. 故障排除部分更新

**移除**:

- 运行 `python test_new.py` 进行诊断

**修改为**:

- 查看日志文件获取详细错误信息
- 尝试选择不同的新闻网站

### 5. 调试工具更新

**移除**:

- 运行测试: `python test_new.py`
- 检查项目问题: `python check_issues.py`

**新增**:

- 生成报告: `python generate_docx_report.py`
- 直接运行: `python run.py` 进行实时调试

## 现在的项目结构

```
crawler/
├── crawler/                     # 爬虫核心模块
│   ├── __init__.py             # 包初始化
│   ├── main.py                 # 主程序入口
│   ├── universal_spider.py     # 通用爬虫类
│   ├── site_detector.py        # 网站检测器
│   ├── data_manager.py         # 数据管理类
│   ├── config.py               # 配置文件
│   ├── utils.py                # 工具函数
│   └── spider.py               # 向后兼容的原爬虫类
├── data/                       # 数据存储目录
│   ├── spider.log              # 爬虫日志
│   ├── *.json                  # JSON格式数据
│   ├── *.csv                   # CSV格式数据
│   └── *.xlsx                  # Excel格式数据
├── .venv/                      # 虚拟环境目录
├── requirements.txt            # 依赖包列表
├── run.py                      # 快速运行脚本
├── generate_docx_report.py     # 实验报告生成脚本
├── 智能通用新闻爬虫系统实验报告.docx  # 实验报告文档
└── README.md                   # 项目说明
```

## 影响说明

这些更新使 README.md 与实际项目状态保持一致：

1. **用户体验改善**: 移除了对不存在文件的引用，避免用户困惑
2. **文档准确性**: 项目结构图现在准确反映实际文件布局
3. **使用指导优化**: 简化了运行步骤，直接指向可用的启动方式
4. **功能完整性**: 新增了实验报告生成的相关说明

现在用户可以直接按照 README.md 的说明使用项目，不会遇到文件不存在的问题。
