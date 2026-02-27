"""
文件扫描器

负责扫描目录、应用过滤规则、收集符合条件的文件列表。
支持 glob 模式、正则表达式、大小限制等多种过滤方式。
"""

import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Set, Optional, Callable, Iterator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FilterType(Enum):
    """过滤类型"""
    EXTENSION = "extension"      # 扩展名
    GLOB = "glob"               # Glob 模式
    REGEX = "regex"             # 正则表达式
    SIZE = "size"               # 文件大小
    CUSTOM = "custom"           # 自定义函数


@dataclass
class FileInfo:
    """文件信息"""
    path: Path                  # 文件路径
    relative_path: str          # 相对路径
    size: int                   # 文件大小（字节）
    extension: str              # 扩展名
    is_text: bool = True        # 是否为文本文件
    encoding: str = "utf-8"     # 文件编码
    metadata: Dict = field(default_factory=dict)  # 额外元数据
    
    def __lt__(self, other: 'FileInfo') -> bool:
        """按路径排序"""
        return self.relative_path < other.relative_path


@dataclass
class FilterRule:
    """过滤规则"""
    rule_type: FilterType
    pattern: str
    is_include: bool = True     # True=包含规则, False=排除规则
    priority: int = 0           # 优先级（数字越大越优先）
    
    def match(self, file_info: FileInfo) -> bool:
        """检查文件是否匹配此规则"""
        if self.rule_type == FilterType.EXTENSION:
            ext = file_info.extension.lower()
            pattern = self.pattern.lower()
            if pattern.startswith('.'):
                return ext == pattern
            return ext == f'.{pattern}' or ext == pattern
            
        elif self.rule_type == FilterType.GLOB:
            return fnmatch.fnmatch(file_info.relative_path, self.pattern)
            
        elif self.rule_type == FilterType.REGEX:
            try:
                return bool(re.search(self.pattern, file_info.relative_path))
            except re.error:
                return False
                
        elif self.rule_type == FilterType.SIZE:
            return self._match_size(file_info.size)
            
        return False
    
    def _match_size(self, size: int) -> bool:
        """匹配文件大小"""
        def parse_size(s: str) -> int:
            s = s.strip().upper()
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            for suffix, mult in multipliers.items():
                if s.endswith(suffix):
                    return int(float(s[:-len(suffix)]) * mult)
            return int(s)
        
        pattern = self.pattern.strip()
        
        if '-' in pattern:
            min_size, max_size = pattern.split('-', 1)
            return parse_size(min_size) <= size <= parse_size(max_size)
        elif pattern.startswith('>'):
            return size > parse_size(pattern[1:])
        elif pattern.startswith('<'):
            return size < parse_size(pattern[1:])
        else:
            return size == parse_size(pattern)


class FileScanner:
    """文件扫描器"""
    
    def __init__(
        self,
        root_path: Path,
        include_extensions: Optional[List[str]] = None,
        exclude_extensions: Optional[List[str]] = None,
        include_folders: Optional[List[str]] = None,
        exclude_folders: Optional[List[str]] = None,
        max_file_size: Optional[int] = None,
        follow_symlinks: bool = False,
    ):
        """
        初始化文件扫描器
        """
        self.root_path = Path(root_path).resolve()
        self.follow_symlinks = follow_symlinks
        self.max_file_size = max_file_size or 10 * 1024 * 1024
        
        self.filter_rules: List[FilterRule] = []
        
        if include_extensions:
            for ext in include_extensions:
                self.add_rule(FilterRule(FilterType.EXTENSION, ext, is_include=True, priority=10))
        
        if exclude_extensions:
            for ext in exclude_extensions:
                self.add_rule(FilterRule(FilterType.EXTENSION, ext, is_include=False, priority=20))
        
        self.include_folders = set(include_folders or [])
        self.exclude_folders = set(exclude_folders or [])
        self.custom_filters: List[Callable[[FileInfo], bool]] = []
    
    def add_rule(self, rule: FilterRule) -> 'FileScanner':
        """添加过滤规则"""
        self.filter_rules.append(rule)
        return self
    
    def add_include_extension(self, ext: str) -> 'FileScanner':
        """添加包含扩展名"""
        if not ext.startswith('.'):
            ext = '.' + ext
        self.add_rule(FilterRule(FilterType.EXTENSION, ext, is_include=True, priority=25))
        return self
    
    def add_exclude_extension(self, ext: str) -> 'FileScanner':
        """添加排除扩展名"""
        if not ext.startswith('.'):
            ext = '.' + ext
        self.add_rule(FilterRule(FilterType.EXTENSION, ext, is_include=False, priority=30))
        return self
    
    def add_glob_include(self, pattern: str, priority: int = 5) -> 'FileScanner':
        """添加 glob 包含模式"""
        self.add_rule(FilterRule(FilterType.GLOB, pattern, is_include=True, priority=priority))
        return self
    
    def add_glob_exclude(self, pattern: str, priority: int = 15) -> 'FileScanner':
        """添加 glob 排除模式"""
        self.add_rule(FilterRule(FilterType.GLOB, pattern, is_include=False, priority=priority))
        return self
    
    def add_regex_include(self, pattern: str, priority: int = 5) -> 'FileScanner':
        """添加正则包含模式"""
        self.add_rule(FilterRule(FilterType.REGEX, pattern, is_include=True, priority=priority))
        return self
    
    def add_regex_exclude(self, pattern: str, priority: int = 15) -> 'FileScanner':
        """添加正则排除模式"""
        self.add_rule(FilterRule(FilterType.REGEX, pattern, is_include=False, priority=priority))
        return self
    
    def add_custom_filter(
        self, 
        filter_func: Callable[[FileInfo], bool],
        is_include: bool = True
    ) -> 'FileScanner':
        """添加自定义过滤函数"""
        self.custom_filters.append((filter_func, is_include))
        return self
    
    def _should_include_folder(self, folder_path: Path) -> bool:
        """判断是否应该包含此文件夹"""
        rel_path = folder_path.relative_to(self.root_path)
        rel_path_str = str(rel_path).replace('\\', '/')
        
        for excluded in self.exclude_folders:
            if rel_path_str == excluded or rel_path_str.startswith(excluded + '/'):
                return False
        
        if self.include_folders:
            for included in self.include_folders:
                if rel_path_str == included or rel_path_str.startswith(included + '/'):
                    return True
                if included.startswith(rel_path_str + '/'):
                    return True
            return False
        
        return True
    
    def _should_include_file(self, file_info: FileInfo) -> Tuple[bool, str]:
        """判断是否应该包含此文件"""
        if file_info.size > self.max_file_size:
            return (False, f"文件过大 ({file_info.size} > {self.max_file_size})")
        
        sorted_rules = sorted(self.filter_rules, key=lambda r: -r.priority)
        has_include_rule = any(r.is_include for r in self.filter_rules)
        matched_include = False
        
        for rule in sorted_rules:
            if rule.match(file_info):
                if rule.is_include:
                    matched_include = True
                else:
                    return (False, f"被排除规则匹配: {rule.pattern}")
        
        if has_include_rule and not matched_include:
            return (False, "未匹配任何包含规则")
        
        for filter_func, is_include in self.custom_filters:
            try:
                if filter_func(file_info):
                    if not is_include:
                        return (False, "被自定义过滤器排除")
                elif is_include:
                    return (False, "未通过自定义过滤器")
            except Exception as e:
                logger.warning(f"自定义过滤器执行错误: {e}")
        
        return (True, "通过所有过滤规则")
    
    def scan(self) -> Iterator[FileInfo]:
        """扫描目录，生成文件信息"""
        if not self.root_path.exists():
            raise FileNotFoundError(f"目录不存在: {self.root_path}")
        
        if not self.root_path.is_dir():
            raise NotADirectoryError(f"不是目录: {self.root_path}")
        
        for root, dirs, files in self.root_path.walk(follow_symlinks=self.follow_symlinks):
            dirs[:] = [d for d in dirs if self._should_include_folder(root / d)]
            
            for filename in files:
                file_path = root / filename
                
                try:
                    stat = file_path.stat()
                except OSError as e:
                    logger.warning(f"无法获取文件信息 {file_path}: {e}")
                    continue
                
                file_info = FileInfo(
                    path=file_path,
                    relative_path=str(file_path.relative_to(self.root_path)).replace('\\', '/'),
                    size=stat.st_size,
                    extension=file_path.suffix.lower(),
                )
                
                should_include, reason = self._should_include_file(file_info)
                
                if should_include:
                    logger.debug(f"包含文件: {file_info.relative_path}")
                    yield file_info
                else:
                    logger.debug(f"排除文件: {file_info.relative_path} ({reason})")
    
    def scan_all(self) -> List[FileInfo]:
        """扫描并返回所有文件列表"""
        return list(self.scan())
    
    def get_statistics(self) -> Dict:
        """获取扫描统计信息"""
        files = self.scan_all()
        
        total_size = sum(f.size for f in files)
        extensions: Dict[str, int] = {}
        
        for f in files:
            ext = f.extension or '(no extension)'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_human': self._human_readable_size(total_size),
            'extensions': dict(sorted(extensions.items(), key=lambda x: -x[1])),
            'root_path': str(self.root_path),
            'files': files,
        }
    
    @staticmethod
    def _human_readable_size(size: int) -> str:
        """转换为人类可读的大小格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def build_tree(self, files: Optional[List[FileInfo]] = None) -> str:
        """
        构建目录树字符串 - 修复版，正确显示目录层级
        """
        if files is None:
            files = self.scan_all()
        
        if not files:
            return f"{self.root_path.name}/\n  (空)"
        
        # 按路径排序
        files = sorted(files, key=lambda f: f.relative_path)
        
        # 构建树结构 - 使用嵌套字典
        tree_dict = {}
        for f in files:
            parts = f.relative_path.split('/')
            current = tree_dict
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # 文件 - 标记为 FileInfo 对象
                    current[part] = f
                else:
                    # 目录 - 创建嵌套字典
                    if part not in current:
                        current[part] = {}
                    current = current[part]
        
        # 递归生成树字符串
        lines = [f"{self.root_path.name}/"]
        self._build_tree_recursive(tree_dict, lines, "")
        return '\n'.join(lines)
    
    def _build_tree_recursive(self, tree_dict: Dict, lines: List[str], prefix: str) -> None:
        """递归构建目录树"""
        # 排序：目录在前，文件在后，同类型按名称排序
        items = sorted(tree_dict.items(), key=lambda x: (not isinstance(x[1], dict), x[0]))
        
        for i, (name, value) in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "
            
            if isinstance(value, dict):
                # 目录
                lines.append(f"{prefix}{connector}{name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                self._build_tree_recursive(value, lines, new_prefix)
            else:
                # 文件
                lines.append(f"{prefix}{connector}{name}")
