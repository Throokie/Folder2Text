"""
格式化器基类

定义输出格式化器的接口和通用功能。
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class FileSection:
    """文件区块"""
    path: str
    content: str
    size: int
    encoding: str
    line_count: int
    error: str = ""


class BaseFormatter(ABC):
    """格式化器基类"""
    
    def __init__(
        self,
        project_name: str,
        project_path: str,
        total_files: int,
        total_size: int,
    ):
        """
        初始化格式化器
        
        Args:
            project_name: 项目名称
            project_path: 项目路径
            total_files: 文件总数
            total_size: 总大小
        """
        self.project_name = project_name
        self.project_path = project_path
        self.total_files = total_files
        self.total_size = total_size
        self.sections: List[FileSection] = []
        self.structure: str = ""
    
    def set_structure(self, structure: str) -> None:
        """设置目录结构"""
        self.structure = structure
    
    def add_section(self, section: FileSection) -> None:
        """添加文件区块"""
        self.sections.append(section)
    
    @abstractmethod
    def render(self) -> str:
        """渲染输出内容"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """获取输出文件扩展名"""
        pass
    
    def write(self, output_path: Path) -> None:
        """写入输出文件"""
        content = self.render()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
    
    @staticmethod
    def human_size(size: int) -> str:
        """转换为人类可读的大小格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
