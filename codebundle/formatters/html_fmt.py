"""
HTML 格式化器

生成带语法高亮的 HTML 格式输出文件。
"""

import html
from pathlib import Path
from typing import Dict

from .base import BaseFormatter, FileSection


class HtmlFormatter(BaseFormatter):
    """HTML 格式化器"""

    LANGUAGE_MAP: Dict[str, str] = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".vue": "vue",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".less": "less",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".sql": "sql",
        ".xml": "xml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",
    }

    def __init__(
        self,
        project_name: str,
        project_path: str,
        total_files: int,
        total_size: int,
        dark_theme: bool = False,
    ):
        super().__init__(project_name, project_path, total_files, total_size)
        self.dark_theme = dark_theme

    def render(self) -> str:
        """渲染 HTML 输出"""
        lines = []

        lines.append("<!DOCTYPE html>")
        lines.append('<html lang="zh-CN">')
        lines.append("<head>")
        lines.append(f"<title>{html.escape(self.project_name)} - CodeBundle</title>")
        lines.append('<meta charset="UTF-8">')
        lines.append(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        )
        lines.append("<style>")
        lines.append(self._get_css())
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")

        lines.append('<div class="container">')

        lines.append(f"<h1>{html.escape(self.project_name)}</h1>")

        lines.append('<div class="info-box">')
        lines.append("<h2>项目信息</h2>")
        lines.append("<table>")
        lines.append(
            f"<tr><td>路径</td><td><code>{html.escape(self.project_path)}</code></td></tr>"
        )
        lines.append(f"<tr><td>文件数</td><td>{self.total_files}</td></tr>")
        lines.append(
            f"<tr><td>总大小</td><td>{self.human_size(self.total_size)}</td></tr>"
        )
        lines.append("</table>")
        lines.append("</div>")

        lines.append('<div class="structure-box">')
        lines.append("<h2>目录结构</h2>")
        lines.append(f"<pre>{html.escape(self.structure)}</pre>")
        lines.append("</div>")

        lines.append("<h2>文件内容</h2>")

        lines.append('<div class="toc">')
        lines.append("<h3>文件索引</h3>")
        lines.append("<ul>")
        for section in sorted(self.sections, key=lambda s: s.path):
            anchor = self._get_anchor(section.path)
            lines.append(
                f'<li><a href="#{anchor}">{html.escape(section.path)}</a></li>'
            )
        lines.append("</ul>")
        lines.append("</div>")

        for section in sorted(self.sections, key=lambda s: s.path):
            anchor = self._get_anchor(section.path)
            lines.append(f'<div class="file-section" id="{anchor}">')
            lines.append(f"<h3><code>{html.escape(section.path)}</code></h3>")
            lines.append('<div class="file-meta">')
            lines.append(f"<span>大小: {self.human_size(section.size)}</span>")
            lines.append(f"<span>编码: {section.encoding}</span>")
            lines.append(f"<span>行数: {section.line_count}</span>")
            lines.append("</div>")

            if section.content:
                lang = self._get_language(section.path)
                lines.append(f'<pre><code class="language-{lang}">')
                lines.append(html.escape(section.content.rstrip()))
                lines.append("</code></pre>")
            elif section.error:
                lines.append(
                    f'<div class="error">错误: {html.escape(section.error)}</div>'
                )
            else:
                lines.append('<div class="empty">空文件</div>')

            lines.append("</div>")

        lines.append("</div>")
        lines.append("</body>")
        lines.append("</html>")

        return "\n".join(lines)

    def get_file_extension(self) -> str:
        return ".html"

    def _get_anchor(self, path: str) -> str:
        return path.lower().replace("/", "-").replace(".", "-").replace("_", "-")

    def _get_language(self, path: str) -> str:
        ext = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        return self.LANGUAGE_MAP.get(ext.lower(), "")

    def _get_css(self) -> str:
        if self.dark_theme:
            return """
                :root {
                    --bg: #1e1e1e;
                    --fg: #d4d4d4;
                    --accent: #569cd6;
                    --border: #404040;
                    --code-bg: #2d2d2d;
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: var(--bg);
                    color: var(--fg);
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: var(--accent); border-bottom: 2px solid var(--border); padding-bottom: 10px; }
                h2 { color: var(--accent); margin-top: 30px; }
                h3 { color: #ce9178; }
                .info-box, .structure-box, .file-section {
                    background: var(--code-bg);
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                }
                table { border-collapse: collapse; width: 100%; }
                td { padding: 8px; border-bottom: 1px solid var(--border); }
                td:first-child { color: #9cdcfe; width: 120px; }
                code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px; }
                pre {
                    background: var(--code-bg);
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                }
                pre code { background: none; padding: 0; }
                .file-meta { color: #9cdcfe; font-size: 14px; margin-bottom: 10px; }
                .file-meta span { margin-right: 20px; }
                .toc { background: var(--code-bg); padding: 15px; border-radius: 8px; }
                .toc ul { list-style: none; padding: 0; columns: 3; }
                .toc li { margin: 5px 0; }
                a { color: var(--accent); text-decoration: none; }
                a:hover { text-decoration: underline; }
                .error { color: #f44747; padding: 10px; background: rgba(244,71,71,0.1); border-radius: 4px; }
                .empty { color: #808080; font-style: italic; }
            """
        else:
            return """
                :root {
                    --bg: #ffffff;
                    --fg: #24292e;
                    --accent: #0366d6;
                    --border: #e1e4e8;
                    --code-bg: #f6f8fa;
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: var(--bg);
                    color: var(--fg);
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: var(--accent); border-bottom: 2px solid var(--border); padding-bottom: 10px; }
                h2 { color: var(--accent); margin-top: 30px; }
                h3 { color: #6f42c1; }
                .info-box, .structure-box, .file-section {
                    background: var(--code-bg);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    padding: 15px;
                    margin: 15px 0;
                }
                table { border-collapse: collapse; width: 100%; }
                td { padding: 8px; border-bottom: 1px solid var(--border); }
                td:first-child { color: #586069; width: 120px; }
                code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; }
                pre {
                    background: var(--code-bg);
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                    border: 1px solid var(--border);
                }
                pre code { background: none; padding: 0; border: none; }
                .file-meta { color: #586069; font-size: 14px; margin-bottom: 10px; }
                .file-meta span { margin-right: 20px; }
                .toc { background: var(--code-bg); padding: 15px; border-radius: 8px; border: 1px solid var(--border); }
                .toc ul { list-style: none; padding: 0; columns: 3; }
                .toc li { margin: 5px 0; }
                a { color: var(--accent); text-decoration: none; }
                a:hover { text-decoration: underline; }
                .error { color: #cb2431; padding: 10px; background: #ffeef0; border-radius: 4px; }
                .empty { color: #6a737d; font-style: italic; }
            """
