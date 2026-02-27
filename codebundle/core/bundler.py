"""
核心打包器

负责将扫描到的文件内容整合成指定格式的输出文件。
支持多种输出格式和并行处理。
"""

import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .scanner import FileScanner, FileInfo
from .encoder import EncodingDetector

logger = logging.getLogger(__name__)


@dataclass
class BundleResult:
    """打包结果"""

    success: bool
    output_path: Path
    total_files: int
    total_size: int
    processing_time: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileContent:
    """文件内容"""

    file_info: FileInfo
    content: Optional[str]
    encoding: str
    error: Optional[str] = None
    line_count: int = 0
    char_count: int = 0


class Bundler:
    """核心打包器"""

    def __init__(
        self,
        scanner: FileScanner,
        output_path: Path,
        max_workers: int = 4,
        show_progress: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        line_numbers: bool = False,
        file_filter: Optional[Callable[[FileInfo], bool]] = None,
    ):
        """
        初始化打包器

        Args:
            scanner: 文件扫描器
            output_path: 输出路径
            max_workers: 最大并行工作数
            show_progress: 是否显示进度
            progress_callback: 进度回调函数
            line_numbers: 是否添加行号
            file_filter: 文件过滤函数，返回 True 表示包含该文件
        """
        self.scanner = scanner
        self.output_path = Path(output_path)
        self.max_workers = max_workers
        self.show_progress = show_progress
        self.progress_callback = progress_callback
        self.line_numbers = line_numbers
        self.file_filter = file_filter
        self.encoder = EncodingDetector()
        self.formatter: Optional[Callable] = None

    def set_formatter(self, formatter: Callable) -> "Bundler":
        """设置输出格式化器"""
        self.formatter = formatter
        return self

    def _read_file(self, file_info: FileInfo) -> FileContent:
        """读取单个文件内容"""
        content, encoding = self.encoder.read_file_safely(file_info.path)

        if content is None:
            return FileContent(
                file_info=file_info,
                content=None,
                encoding=encoding,
                error="无法读取文件（可能是二进制文件）",
            )

        return FileContent(
            file_info=file_info,
            content=content,
            encoding=encoding,
            line_count=content.count("\n") + 1,
            char_count=len(content),
        )

    def _read_files_parallel(self, files: List[FileInfo]) -> List[FileContent]:
        """并行读取文件"""
        contents = []
        total = len(files)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self._read_file, f): f for f in files}

            completed = 0
            for future in as_completed(future_to_file):
                file_info = future_to_file[future]
                try:
                    content = future.result()
                    contents.append(content)
                except Exception as e:
                    logger.error(f"读取文件失败 {file_info.path}: {e}")
                    contents.append(
                        FileContent(
                            file_info=file_info, content=None, encoding="", error=str(e)
                        )
                    )

                completed += 1
                if self.progress_callback:
                    self.progress_callback(completed, total, file_info.relative_path)

        return contents

    def bundle(self, format: str = "text") -> BundleResult:
        """执行打包操作"""
        start_time = time.time()
        errors = []
        warnings = []

        try:
            logger.info(f"开始扫描目录: {self.scanner.root_path}")
            files = self.scanner.scan_all()

            if self.file_filter:
                files = [f for f in files if self.file_filter(f)]
                logger.info(f"过滤后剩余 {len(files)} 个文件")

            if not files:
                warnings.append("没有找到符合条件的文件")

            logger.info(f"找到 {len(files)} 个文件")

            logger.info("开始读取文件内容...")
            contents = self._read_files_parallel(files)

            logger.info(f"生成输出文件: {self.output_path}")
            self._write_output(contents, format, files)

            total_size = sum(f.size for f in files)
            processing_time = time.time() - start_time

            statistics = {
                "total_files": len(files),
                "total_size": total_size,
                "processing_time": processing_time,
                "format": format,
                "errors_count": len([c for c in contents if c.error]),
                "total_lines": sum(c.line_count for c in contents if c.content),
                "total_chars": sum(c.char_count for c in contents if c.content),
            }

            return BundleResult(
                success=True,
                output_path=self.output_path,
                total_files=len(files),
                total_size=total_size,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings,
                statistics=statistics,
            )

        except Exception as e:
            logger.error(f"打包失败: {e}")
            return BundleResult(
                success=False,
                output_path=self.output_path,
                total_files=0,
                total_size=0,
                processing_time=time.time() - start_time,
                errors=[str(e)],
            )

    def _write_output(
        self, contents: List[FileContent], format: str, files: List[FileInfo]
    ) -> None:
        """写入输出文件"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "markdown" or format == "md":
            self._write_markdown(contents, files)
        elif format == "json":
            self._write_json(contents)
        elif format == "html":
            self._write_html(contents, files)
        else:
            self._write_text(contents, files)

    def _write_text(self, contents: List[FileContent], files: List[FileInfo]) -> None:
        """写入纯文本格式"""
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write(f"PROJECT: {self.scanner.root_path.name}\n")
            f.write(f"PATH: {self.scanner.root_path}\n")
            f.write(f"FILES: {len(contents)}\n")
            if self.line_numbers:
                f.write("LINE_NUMBERS: enabled\n")
            f.write("=" * 80 + "\n\n")

            f.write("=" * 80 + "\n")
            f.write("DIRECTORY STRUCTURE\n")
            f.write("=" * 80 + "\n\n")
            f.write(self.scanner.build_tree(files))
            f.write("\n\n")

            f.write("=" * 80 + "\n")
            f.write("FILE CONTENTS\n")
            f.write("=" * 80 + "\n\n")

            for content in sorted(contents, key=lambda c: c.file_info.relative_path):
                f.write("-" * 80 + "\n")
                f.write(f"FILE: {content.file_info.relative_path}\n")
                f.write(f"SIZE: {content.file_info.size} bytes\n")
                f.write(f"ENCODING: {content.encoding}\n")
                f.write("-" * 80 + "\n\n")

                if content.content:
                    output_content = self._add_line_numbers(content.content)
                    f.write(output_content)
                    if not output_content.endswith("\n"):
                        f.write("\n")
                else:
                    f.write(f"[ERROR: {content.error or 'Unable to read file'}]\n")

                f.write("\n")

    def _write_markdown(
        self, contents: List[FileContent], files: List[FileInfo]
    ) -> None:
        """写入 Markdown 格式"""
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(f"# {self.scanner.root_path.name}\n\n")

            f.write("## 📋 项目信息\n\n")
            f.write(f"- **路径**: `{self.scanner.root_path}`\n")
            f.write(f"- **文件数**: {len(contents)}\n")
            f.write(
                f"- **总大小**: {self._human_size(sum(c.file_info.size for c in contents))}\n\n"
            )
            if self.line_numbers:
                f.write("- **行号**: 已启用\n\n")

            f.write("## 📁 目录结构\n\n")
            f.write("```\n")
            f.write(self.scanner.build_tree(files))
            f.write("\n```\n\n")

            f.write("## 📄 文件内容\n\n")

            for content in sorted(contents, key=lambda c: c.file_info.relative_path):
                f.write(f"### `{content.file_info.relative_path}`\n\n")

                f.write(f"> 大小: {self._human_size(content.file_info.size)} | ")
                f.write(f"编码: {content.encoding} | ")
                f.write(f"行数: {content.line_count if content.content else 'N/A'}\n\n")

                if content.content:
                    output_content = (
                        self._add_line_numbers(content.content)
                        if self.line_numbers
                        else content.content
                    )
                    lang = self._get_language(content.file_info.extension)
                    f.write(f"```{lang}\n")
                    f.write(output_content.rstrip())
                    f.write("\n```\n\n")
                else:
                    f.write(f"> ⚠️ {content.error or '无法读取文件'}\n\n")

                f.write("---\n\n")

    def _write_json(self, contents: List[FileContent]) -> None:
        """写入 JSON 格式"""
        import json

        data = {
            "project": {
                "name": self.scanner.root_path.name,
                "path": str(self.scanner.root_path),
                "total_files": len(contents),
                "total_size": sum(c.file_info.size for c in contents),
            },
            "structure": self.scanner.build_tree(
                [c.file_info for c in contents if not c.error]
            ),
            "files": [],
        }

        for content in sorted(contents, key=lambda c: c.file_info.relative_path):
            file_data = {
                "path": content.file_info.relative_path,
                "size": content.file_info.size,
                "encoding": content.encoding,
                "line_count": content.line_count if content.content else 0,
                "content": content.content,
            }
            if content.error:
                file_data["error"] = content.error
            data["files"].append(file_data)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _write_html(self, contents: List[FileContent], files: List[FileInfo]) -> None:
        """写入 HTML 格式"""
        from ..formatters.html_fmt import HtmlFormatter

        formatter = HtmlFormatter(
            project_name=self.scanner.root_path.name,
            project_path=str(self.scanner.root_path),
            total_files=len(contents),
            total_size=sum(c.file_info.size for c in contents),
        )

        formatter.set_structure(self.scanner.build_tree(files))

        for content in sorted(contents, key=lambda c: c.file_info.relative_path):
            from ..formatters.base import FileSection

            section = FileSection(
                path=content.file_info.relative_path,
                content=content.content or "",
                size=content.file_info.size,
                encoding=content.encoding,
                line_count=content.line_count,
                error=content.error or "",
            )
            formatter.add_section(section)

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(formatter.render())

    @staticmethod
    def _human_size(size: int) -> str:
        """转换为人类可读的大小格式"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _add_line_numbers(self, content: str) -> str:
        """添加行号到内容"""
        if not self.line_numbers:
            return content
        lines = content.splitlines()
        max_width = len(str(len(lines)))
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:>{max_width}} | {line}")
        return "\n".join(numbered_lines)

    @staticmethod
    def _get_language(extension: str) -> str:
        """根据扩展名获取代码块语言"""
        lang_map = {
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
            ".conf": "ini",
            ".dockerfile": "dockerfile",
            ".makefile": "makefile",
        }
        return lang_map.get(extension.lower(), "")
