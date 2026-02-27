# CodeBundle Pro

智能项目文件整合工具 - 将指定文件夹下的文件内容编排成一个结构化文件。

## ✨ 特性

- 🔍 **智能文件扫描** - 支持扩展名、glob 模式、正则表达式、文件大小等多种过滤规则
- 📝 **多种输出格式** - 支持纯文本、Markdown、JSON 三种格式
- 🔤 **智能编码检测** - 自动检测文件编码，支持 UTF-8、GBK、Big5 等多种编码
- ⚡ **并行处理** - 多线程并行读取文件，提升处理速度
- 📊 **进度显示** - 实时显示处理进度和预计剩余时间
- ⚙️ **配置管理** - 内置多种预设配置，支持自定义和继承
- 💻 **双模式** - 支持命令行参数和交互式两种使用方式

## 🚀 快速开始

### 交互模式

直接运行脚本进入交互模式：

```bash
python run_codebundle.py
```

### 命令行模式

```bash
# 打包当前目录
python run_codebundle.py bundle .

# 打包指定目录，使用指定配置
python run_codebundle.py bundle ./myproject -p "Python项目" -f markdown

# 查看可用配置
python run_codebundle.py profiles

# 扫描目录统计
python run_codebundle.py scan ./myproject
```

## 📋 内置配置

| 配置名称 | 描述 |
|---------|------|
| 通用/Web开发 | 适用于前端和全栈 Web 项目 |
| Python项目 | 适用于 Python 项目 |
| Go项目 | 适用于 Go 语言项目 |
| Rust项目 | 适用于 Rust 语言项目 |
| 前端/React | 适用于 React 前端项目 |
| Java/Kotlin | 适用于 Java/Kotlin 项目 |
| 最小化 | 只包含核心代码文件 |
| 完整备份 | 包含所有文本文件 |

## 📁 项目结构

```
codebundle/
├── __init__.py          # 包入口
├── __main__.py          # 模块入口
├── core/                # 核心模块
│   ├── scanner.py       # 文件扫描器
│   ├── bundler.py       # 打包器
│   └── encoder.py       # 编码检测器
├── formatters/          # 格式化器
│   ├── base.py          # 基类
│   ├── text.py          # 纯文本格式
│   ├── markdown.py      # Markdown 格式
│   └── json_fmt.py      # JSON 格式
├── config/              # 配置管理
│   └── manager.py       # 配置管理器
├── cli/                 # 命令行接口
│   ├── commands.py      # CLI 命令
│   └── interactive.py   # 交互模式
└── utils/               # 工具模块
    ├── git_ops.py       # Git 操作
    └── progress.py      # 进度显示
```

## 🔧 高级用法

### 自定义过滤规则

```python
from codebundle import FileScanner, Bundler
from pathlib import Path

# 创建扫描器
scanner = FileScanner(
    root_path=Path('./myproject'),
    include_extensions=['.py', '.js', '.ts'],
    exclude_extensions=['.min.js'],
    exclude_folders=['node_modules', '__pycache__'],
    max_file_size=5 * 1024 * 1024,  # 5MB
)

# 添加 glob 规则
scanner.add_glob_include('src/**/*.py')
scanner.add_glob_exclude('**/test_*.py')

# 添加正则规则
scanner.add_regex_exclude(r'.*_generated\.py$')

# 创建打包器并执行
bundler = Bundler(scanner, Path('output.md'))
result = bundler.bundle(format='markdown')

print(f"处理了 {result.total_files} 个文件")
```

### 自定义配置档案

```python
from codebundle.config.manager import ConfigManager, ProfileConfig

manager = ConfigManager()

# 创建自定义配置
custom_profile = ProfileConfig(
    name="我的项目",
    description="自定义配置",
    include_extensions=['.py', '.md', '.txt'],
    exclude_folders=['.git', '__pycache__', 'venv'],
    max_file_size="2MB",
)

# 保存配置
manager.add_profile(custom_profile)
manager.save()
```

## 📄 输出示例

### Markdown 格式

```markdown
# myproject

## 📋 项目信息

| 属性 | 值 |
|------|-----|
| 路径 | `/path/to/myproject` |
| 文件数 | 42 |
| 总大小 | 156.8 KB |

## 📁 目录结构

```
myproject/
├── src/
│   ├── main.py
│   └── utils.py
└── README.md
```

## 📄 文件内容

### `src/main.py`

> 📊 大小: 2.3 KB | 编码: utf-8 | 行数: 85

```python
def main():
    print("Hello, World!")
```
```

## 🆚 与原版对比

| 特性 | 原版 | CodeBundle Pro |
|------|------|----------------|
| 架构 | 单文件 | 模块化 |
| 过滤规则 | 仅扩展名 | 扩展名 + glob + 正则 + 大小 |
| 输出格式 | 纯文本 | 文本 + Markdown + JSON |
| 编码检测 | 简单 try-catch | 智能检测 + 多编码支持 |
| 处理方式 | 串行 | 并行 |
| 进度显示 | 无 | 进度条 + ETA |
| 配置管理 | JSON 硬编码 | 预设 + 自定义 + 继承 |

## 📜 许可证

MIT License
