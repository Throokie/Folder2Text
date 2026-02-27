#!/usr/bin/env python3
"""
CodeBundle Pro 启动脚本

直接运行此脚本即可使用 CodeBundle Pro。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from codebundle.cli.commands import main

if __name__ == "__main__":
    sys.exit(main())
