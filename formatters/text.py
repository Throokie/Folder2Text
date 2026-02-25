"""
纯文本格式化器

生成纯文本格式的输出文件。
"""

from pathlib import Path
from typing import List

from .base import BaseFormatter, FileSection


class TextFormatter(BaseFormatter):
    """纯文本格式化器"""
    
    SEPARATOR = "=" * 80
    SUB_SEPARATOR = "-" * 80
    
    def render(self) -> str:
        """渲染纯文本输出"""
        lines = []
        
        # 头部
        lines.append(self.SEPARATOR)
        lines.append(f"PROJECT: {self.project_name}")
        lines.append(f"PATH: {self.project_path}")
        lines.append(f"FILES: {self.total_files}")
        lines.append(f"SIZE: {self.human_size(self.total_size)}")
        lines.append(self.SEPARATOR)
        lines.append("")
        
        # 目录结构
        lines.append(self.SEPARATOR)
        lines.append("DIRECTORY STRUCTURE")
        lines.append(self.SEPARATOR)
        lines.append("")
        lines.append(self.structure)
        lines.append("")
        
        # 文件内容
        lines.append(self.SEPARATOR)
        lines.append("FILE CONTENTS")
        lines.append(self.SEPARATOR)
        lines.append("")
        
        for section in sorted(self.sections, key=lambda s: s.path):
            lines.append(self.SUB_SEPARATOR)
            lines.append(f"FILE: {section.path}")
            lines.append(f"SIZE: {self.human_size(section.size)}")
            lines.append(f"ENCODING: {section.encoding}")
            lines.append(f"LINES: {section.line_count}")
            lines.append(self.SUB_SEPARATOR)
            lines.append("")
            
            if section.content:
                lines.append(section.content)
                if not section.content.endswith('\n'):
                    lines.append('')
            elif section.error:
                lines.append(f"[ERROR: {section.error}]")
            else:
                lines.append("[Empty file]")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        return ".txt"
