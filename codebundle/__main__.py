"""入口点 - 支持 python -m codebundle 运行"""

import sys
from .cli.commands import main

if __name__ == "__main__":
    sys.exit(main())
