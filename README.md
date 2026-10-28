# 📦 Folder2Text | CodeBundle Pro

> **智能项目文件整合工具** - 将指定文件夹下的文件内容编排成一个结构化文件，支持多种过滤规则、输出格式和编码检测。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)

---

## ✨ 主要功能

| 功能 | 描述 |
|------|------|
| 📁 **智能扫描** | 支持扩展名、glob、正则、大小等多种过滤规则 |
| 📄 **多格式输出** | 纯文本、Markdown、JSON 三种格式可选 |
| 🔤 **编码检测** | 自动检测 UTF-8、GBK、Big5 等编码 |
| ⚡ **并行处理** | 多线程并行读取文件，大幅提升速度 |
| 🎯 **预设配置** | 内置 9 种预设配置，一键切换 |
| 🖥️ **双模式** | 命令行参数 + 交互式界面 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Throokie/Folder2Text.git
cd Folder2Text

# 安装依赖
pip install -e .
```

### 基本使用

```bash
# 打包当前目录
codebundle bundle .

# 指定输出文件
codebundle bundle /path/to/project -o output.txt

# 使用预设配置（如 python 项目）
codebundle bundle . --config python

# 只打包 Git 跟踪的文件
codebundle bundle . --git-only

# 静默模式（无进度条）
codebundle bundle . --quiet
```

---

## 使用案例

把一个小型 Python 包打成单文件，便于丢给 LLM：

```bash
codebundle bundle ./my_package --config python -o /tmp/my_package.txt --git-only
head -n 40 /tmp/my_package.txt
```

预期输出结构示意：

```text
# Bundle: my_package
# Files: 12

===== my_package/__init__.py =====
...
===== my_package/cli.py =====
...
```

> 注：以上输出仅为结构示意，实际头部与分隔符格式以本地运行结果为准。`--git-only` 要求目标目录位于 Git 仓库内。

---

## 📋 命令行选项

```bash
# 查看帮助
codebundle --help

# 查看版本
codebundle --version

# 打包目录
codebundle bundle <directory> [选项]

选项：
  -o, --output TEXT       输出文件路径
  -f, --format TEXT       输出格式：text, markdown, json (默认：text)
  -c, --config TEXT       使用预设配置
  --git-only              只处理 Git 跟踪的文件
  --line-numbers          添加行号
  --warn-sensitive        警告敏感文件（.env, credentials 等）
  --compress TEXT         压缩输出：zip, tar.gz
  -q, --quiet             静默模式
  --no-progress           不显示进度条
```

---

## 🎯 预设配置

内置 9 种预设配置，适配不同类型的项目：

| 配置名 | 适用场景 |
|--------|----------|
| `default` | 默认配置 |
| `python` | Python 项目 |
| `javascript` | JS/TS 项目 |
| `go` | Go 语言项目 |
| `rust` | Rust 项目 |
| `docs` | 文档-only 模式 |
| `source` | 仅源代码 |
| `minimal` | 最小化配置 |
| `full` | 包含所有文件 |

---

##  Python API

```python
from codebundle import Bundler, FileScanner, ConfigManager

# 创建扫描器
scanner = FileScanner("/path/to/project", git_only=True)

# 创建打包器
bundler = Bundler(
    scanner,
    output_path="bundle.txt",
    line_numbers=True
)

# 执行打包
result = bundler.bundle(compress='zip')
print(f"打包完成：{result.output_file}")
```

---

## 🔧 开发

### 运行测试

```bash
pip install -e ".[dev]"
pytest
```

### 代码质量

```bash
# 格式化
black codebundle/
isort codebundle/

# 类型检查
mypy codebundle/

# Lint
ruff check codebundle/
```

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### v2.0.0
- ✨ 新增 CLI 增强（--version, --quiet, --no-progress）
- 🐛 修复编码检测问题
- 📦 优化并行处理性能

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**如果觉得好用，请给一个 Star ⭐！**
