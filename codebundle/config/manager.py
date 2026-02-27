"""
配置管理器

支持 YAML/JSON 配置文件，配置继承和预设模板。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path.home() / ".codebundle" / "config.yaml"
LOCAL_CONFIG_NAME = ".codebundle.yaml"


@dataclass
class ProfileConfig:
    """配置档案"""
    name: str
    description: str = ""
    include_extensions: List[str] = field(default_factory=list)
    exclude_extensions: List[str] = field(default_factory=list)
    include_folders: List[str] = field(default_factory=list)
    exclude_folders: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    max_file_size: str = "10MB"
    output_format: str = "text"
    inherit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'ProfileConfig':
        """从字典创建"""
        return cls(name=name, **{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ConfigManager:
    """配置管理器"""
    
    BUILTIN_PRESETS = {
        "通用/Web开发": ProfileConfig(
            name="通用/Web开发",
            description="适用于前端和全栈 Web 项目",
            include_extensions=[
                ".py", ".java", ".c", ".cpp", ".h", ".txt", ".md", ".json",
                ".gradle", ".xml", ".html", ".js", ".ts", ".tsx", ".jsx",
                ".vue", ".css", ".scss", ".go", ".rs", ".yaml", ".yml", ".toml"
            ],
            exclude_extensions=[
                ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
                ".exe", ".dll", ".so", ".zip", ".pyc", ".class", ".o", ".obj",
                ".wasm", ".ttf", ".woff", ".woff2", ".eot"
            ],
            exclude_folders=[
                "node_modules", ".git", "__pycache__", "build", "dist",
                "venv", ".venv", "target", ".idea", ".vscode", ".next",
                "coverage", ".nuxt", "out", "public", "static"
            ],
            max_file_size="5MB"
        ),
        
        "Python项目": ProfileConfig(
            name="Python项目",
            description="适用于 Python 项目",
            include_extensions=[
                ".py", ".pyx", ".pyi", ".txt", ".md", ".rst", ".json",
                ".yaml", ".yml", ".toml", ".cfg", ".ini", ".env.example"
            ],
            exclude_extensions=[
                ".pyc", ".pyo", ".pyd", ".so", ".dll", ".egg", ".whl"
            ],
            exclude_folders=[
                "__pycache__", ".git", "venv", ".venv", "env", ".env",
                "build", "dist", "*.egg-info", ".mypy_cache", ".pytest_cache",
                ".tox", "htmlcov", ".idea", ".vscode"
            ],
            max_file_size="5MB"
        ),
        
        "Go项目": ProfileConfig(
            name="Go项目",
            description="适用于 Go 语言项目",
            include_extensions=[
                ".go", ".mod", ".sum", ".yaml", ".yml", ".json", ".md", ".txt",
                ".sql", ".proto", ".tmpl", ".html"
            ],
            exclude_extensions=[
                ".exe", ".dll", ".so", ".a", ".test"
            ],
            exclude_folders=[
                ".git", "vendor", "bin", "pkg", ".idea", ".vscode"
            ],
            max_file_size="5MB"
        ),
        
        "Rust项目": ProfileConfig(
            name="Rust项目",
            description="适用于 Rust 语言项目",
            include_extensions=[
                ".rs", ".toml", ".md", ".txt", ".json", ".yaml", ".yml",
                ".sql", ".wasm"
            ],
            exclude_extensions=[
                ".exe", ".dll", ".so", ".a", ".rlib", ".rmeta"
            ],
            exclude_folders=[
                ".git", "target", ".idea", ".vscode"
            ],
            max_file_size="5MB"
        ),
        
        "前端/React": ProfileConfig(
            name="前端/React",
            description="适用于 React 前端项目",
            include_extensions=[
                ".js", ".jsx", ".ts", ".tsx", ".json", ".css", ".scss",
                ".less", ".html", ".md", ".yaml", ".yml"
            ],
            exclude_extensions=[
                ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
                ".ttf", ".woff", ".woff2", ".eot", ".map"
            ],
            exclude_folders=[
                "node_modules", ".git", "build", "dist", ".next", "coverage",
                ".nuxt", "out", "public", "static", ".idea", ".vscode"
            ],
            max_file_size="5MB"
        ),
        
        "Java/Kotlin": ProfileConfig(
            name="Java/Kotlin",
            description="适用于 Java/Kotlin 项目",
            include_extensions=[
                ".java", ".kt", ".kts", ".gradle", ".xml", ".properties",
                ".yaml", ".yml", ".json", ".md", ".txt", ".sql"
            ],
            exclude_extensions=[
                ".class", ".jar", ".war", ".ear", ".exe", ".dll"
            ],
            exclude_folders=[
                ".git", "target", "build", "out", ".gradle", ".idea", ".vscode"
            ],
            max_file_size="5MB"
        ),
        
        "配置文件": ProfileConfig(
            name="配置文件",
            description="适用于配置文件收集，包含各种配置格式",
            include_extensions=[
                ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
                ".config", ".xml", ".properties", ".env", ".env.example",
                ".editorconfig", ".gitignore", ".dockerignore", ".eslintrc",
                ".prettierrc", ".babelrc", ".md", ".txt", ".sh", ".bash", ".zsh"
            ],
            exclude_extensions=[
                ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
                ".exe", ".dll", ".so", ".zip"
            ],
            exclude_folders=[
                "node_modules", ".git", "__pycache__", "build", "dist",
                "venv", ".venv", "target", ".idea", ".vscode"
            ],
            max_file_size="1MB"
        ),
        
        "最小化": ProfileConfig(
            name="最小化",
            description="只包含核心代码文件",
            include_extensions=[
                ".py", ".js", ".ts", ".go", ".rs", ".java", ".kt", ".c", ".cpp"
            ],
            exclude_extensions=[],
            exclude_folders=[
                "node_modules", ".git", "__pycache__", "build", "dist",
                "venv", ".venv", "target", "test", "tests", "__tests__",
                ".idea", ".vscode", "docs", "examples"
            ],
            max_file_size="1MB"
        ),
        
        "完整备份": ProfileConfig(
            name="完整备份",
            description="包含所有文本文件",
            include_extensions=[],
            exclude_extensions=[
                ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
                ".exe", ".dll", ".so", ".zip", ".tar", ".gz", ".rar",
                ".pyc", ".class", ".o", ".obj", ".pdf", ".doc", ".docx"
            ],
            exclude_folders=[
                ".git", "node_modules", "__pycache__", ".idea", ".vscode"
            ],
            max_file_size="50MB"
        ),
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """初始化配置管理器"""
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.profiles: Dict[str, ProfileConfig] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        self.profiles = {k: v for k, v in self.BUILTIN_PRESETS.items()}
        
        if self.config_path.exists():
            try:
                self._load_from_file(self.config_path)
                logger.info(f"已加载配置文件: {self.config_path}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        local_config = Path.cwd() / LOCAL_CONFIG_NAME
        if local_config.exists():
            try:
                self._load_from_file(local_config)
                logger.info(f"已加载本地配置: {local_config}")
            except Exception as e:
                logger.warning(f"加载本地配置失败: {e}")
    
    def _load_from_file(self, path: Path) -> None:
        """从文件加载配置"""
        content = path.read_text(encoding='utf-8')
        
        if path.suffix in ('.yaml', '.yml'):
            try:
                import yaml
                data = yaml.safe_load(content) or {}
            except ImportError:
                import json
                data = json.loads(content)
        else:
            import json
            data = json.loads(content)
        
        profiles = data.get('profiles', {})
        for name, profile_data in profiles.items():
            profile = ProfileConfig.from_dict(name, profile_data)
            
            if profile.inherit and profile.inherit in self.profiles:
                profile = self._merge_profiles(self.profiles[profile.inherit], profile)
            
            self.profiles[name] = profile
    
    def _merge_profiles(self, base: ProfileConfig, override: ProfileConfig) -> ProfileConfig:
        """合并两个配置档案"""
        base_dict = base.to_dict()
        override_dict = override.to_dict()
        
        merged = {}
        for key in base_dict:
            if key == 'name':
                merged[key] = override_dict.get(key, base_dict[key])
            elif key in ('include_extensions', 'include_folders', 'include_patterns'):
                base_list = base_dict.get(key, [])
                override_list = override_dict.get(key, [])
                merged[key] = list(set(base_list + override_list))
            elif key in ('exclude_extensions', 'exclude_folders', 'exclude_patterns'):
                base_list = base_dict.get(key, [])
                override_list = override_dict.get(key, [])
                merged[key] = list(set(base_list + override_list))
            elif override_dict.get(key) is not None:
                merged[key] = override_dict[key]
            else:
                merged[key] = base_dict[key]
        
        return ProfileConfig(**merged)
    
    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """获取配置档案"""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """列出所有配置档案名称"""
        return list(self.profiles.keys())
    
    def add_profile(self, profile: ProfileConfig) -> None:
        """添加配置档案"""
        self.profiles[profile.name] = profile
    
    def remove_profile(self, name: str) -> bool:
        """删除配置档案"""
        if name in self.BUILTIN_PRESETS:
            logger.warning(f"不能删除内置预设: {name}")
            return False
        if name in self.profiles:
            del self.profiles[name]
            return True
        return False
    
    def save(self, path: Optional[Path] = None) -> None:
        """保存配置到文件"""
        save_path = path or self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        custom_profiles = {
            name: profile.to_dict()
            for name, profile in self.profiles.items()
            if name not in self.BUILTIN_PRESETS
        }
        
        data = {'profiles': custom_profiles}
        
        if save_path.suffix in ('.yaml', '.yml'):
            try:
                import yaml
                content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            except ImportError:
                import json
                content = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            import json
            content = json.dumps(data, indent=2, ensure_ascii=False)
        
        save_path.write_text(content, encoding='utf-8')
        logger.info(f"配置已保存到: {save_path}")
    
    @staticmethod
    def parse_size(size_str: str) -> int:
        """解析大小字符串为字节数"""
        size_str = size_str.strip().upper()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 ** 2,
            'GB': 1024 ** 3,
        }
        
        for suffix, mult in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    return int(float(size_str[:-len(suffix)]) * mult)
                except ValueError:
                    pass
        
        try:
            return int(size_str)
        except ValueError:
            return 10 * 1024 * 1024
