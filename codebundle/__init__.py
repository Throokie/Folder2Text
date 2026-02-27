"""
CodeBundle Pro - 智能项目文件整合工具

将指定文件夹下的文件内容编排成一个结构化文件，
支持多种过滤规则、输出格式和智能编码检测。
"""

__version__ = "2.0.0"
__author__ = "CodeBundle Team"

from .core.bundler import Bundler
from .core.scanner import FileScanner
from .config.manager import ConfigManager

__all__ = ["Bundler", "FileScanner", "ConfigManager"]
