"""
Markdown 格式化器

生成 Markdown 格式的输出文件。
"""

from pathlib import Path
from typing import List, Dict

from .base import BaseFormatter, FileSection


class MarkdownFormatter(BaseFormatter):
    """Markdown 格式化器"""
    
    # 扩展名到语言的映射
    LANGUAGE_MAP: Dict[str, str] = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.vue': 'vue',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.less': 'less',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.sql': 'sql',
        '.xml': 'xml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.gradle': 'gradle',
        '.dockerfile': 'dockerfile',
        '.makefile': 'makefile',
    }
    
    def render(self) -> str:
        """渲染 Markdown 输出"""
        lines = []
        
        # 标题
        lines.append(f"# {self.project_name}")
        lines.append("")
        
        # 项目信息
        lines.append("## 📋 项目信息")
        lines.append("")
        lines.append(f"| 属性 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 路径 | `{self.project_path}` |")
        lines.append(f"| 文件数 | {self.total_files} |")
        lines.append(f"| 总大小 | {self.human_size(self.total_size)} |")
        lines.append("")
        
        # 目录结构
        lines.append("## 📁 目录结构")
        lines.append("")
        lines.append("```")
        lines.append(self.structure)
        lines.append("```")
        lines.append("")
        
        # 文件内容
        lines.append("## 📄 文件内容")
        lines.append("")
        
        # 目录索引
        lines.append("### 文件索引")
        lines.append("")
        for section in sorted(self.sections, key=lambda s: s.path):
            anchor = section.path.lower().replace('/', '-').replace('.', '-')
            lines.append(f"- [{section.path}](#{anchor})")
        lines.append("")
        
        # 文件内容详情
        for section in sorted(self.sections, key=lambda s: s.path):
            anchor = section.path.lower().replace('/', '-').replace('.', '-')
            lines.append(f"### `{section.path}` {{#{anchor}}}")
            lines.append("")
            
            # 元信息
            lines.append(f"> 📊 大小: {self.human_size(section.size)} | ")
            lines.append(f"编码: {section.encoding} | ")
            lines.append(f"行数: {section.line_count}")
            lines.append("")
            
            if section.content:
                lang = self._get_language(section.path)
                lines.append(f"```{lang}")
                lines.append(section.content.rstrip())
                lines.append("```")
            elif section.error:
                lines.append(f"> ⚠️ **错误**: {section.error}")
            else:
                lines.append("> 📭 空文件")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return '\n'.join(lines)
    
    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        return ".md"
    
    def _get_language(self, path: str) -> str:
        """根据文件路径获取代码块语言"""
        ext = '.' + path.rsplit('.', 1)[-1] if '.' in path else ''
        return self.LANGUAGE_MAP.get(ext.lower(), '')
