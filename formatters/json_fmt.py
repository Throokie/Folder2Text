"""
JSON 格式化器

生成 JSON 格式的输出文件，便于程序化处理。
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base import BaseFormatter, FileSection


class JsonFormatter(BaseFormatter):
    """JSON 格式化器"""
    
    def __init__(
        self,
        project_name: str,
        project_path: str,
        total_files: int,
        total_size: int,
        include_content: bool = True,
        pretty_print: bool = True,
    ):
        """
        初始化 JSON 格式化器
        
        Args:
            project_name: 项目名称
            project_path: 项目路径
            total_files: 文件总数
            total_size: 总大小
            include_content: 是否包含文件内容
            pretty_print: 是否美化输出
        """
        super().__init__(project_name, project_path, total_files, total_size)
        self.include_content = include_content
        self.pretty_print = pretty_print
    
    def render(self) -> str:
        """渲染 JSON 输出"""
        data: Dict[str, Any] = {
            "meta": {
                "version": "2.0.0",
                "generator": "CodeBundle Pro",
            },
            "project": {
                "name": self.project_name,
                "path": self.project_path,
                "total_files": self.total_files,
                "total_size": self.total_size,
                "total_size_human": self.human_size(self.total_size),
            },
            "structure": self.structure,
            "files": [],
        }
        
        for section in sorted(self.sections, key=lambda s: s.path):
            file_data: Dict[str, Any] = {
                "path": section.path,
                "size": section.size,
                "size_human": self.human_size(section.size),
                "encoding": section.encoding,
                "line_count": section.line_count,
            }
            
            if section.error:
                file_data["error"] = section.error
                file_data["content"] = None
            elif self.include_content:
                file_data["content"] = section.content
            
            data["files"].append(file_data)
        
        # 统计信息
        extensions: Dict[str, int] = {}
        for section in self.sections:
            ext = '.' + section.path.rsplit('.', 1)[-1] if '.' in section.path else '(no ext)'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        data["statistics"] = {
            "extensions": dict(sorted(extensions.items(), key=lambda x: -x[1])),
            "total_lines": sum(s.line_count for s in self.sections),
            "total_chars": sum(len(s.content) for s in self.sections if s.content),
        }
        
        if self.pretty_print:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        return ".json"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（便于进一步处理）"""
        return json.loads(self.render())
