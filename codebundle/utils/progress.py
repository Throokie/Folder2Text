"""
进度显示工具

提供终端进度条和状态显示功能。
"""

import sys
from typing import Optional
import time


class ProgressBar:
    """终端进度条"""
    
    def __init__(
        self,
        total: int,
        width: int = 40,
        fill_char: str = '█',
        empty_char: str = '░',
        prefix: str = '',
        suffix: str = '',
    ):
        """
        初始化进度条
        
        Args:
            total: 总数
            width: 进度条宽度
            fill_char: 填充字符
            empty_char: 空白字符
            prefix: 前缀文本
            suffix: 后缀文本
        """
        self.total = total
        self.width = width
        self.fill_char = fill_char
        self.empty_char = empty_char
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        self.start_time = time.time()
    
    def update(self, current: int, description: str = '') -> None:
        """
        更新进度
        
        Args:
            current: 当前进度
            description: 描述文本
        """
        self.current = current
        percent = (current / self.total) * 100 if self.total > 0 else 0
        filled = int(self.width * current / self.total) if self.total > 0 else 0
        empty = self.width - filled
        
        bar = self.fill_char * filled + self.empty_char * empty
        
        # 计算预计剩余时间
        elapsed = time.time() - self.start_time
        if current > 0 and current < self.total:
            eta = (elapsed / current) * (self.total - current)
            eta_str = f" ETA: {self._format_time(eta)}"
        else:
            eta_str = ""
        
        # 构建输出行
        line = f"\r{self.prefix}[{bar}] {percent:.1f}% ({current}/{self.total})"
        if description:
            line += f" {description[:20]:<20}"
        line += eta_str
        
        # 输出
        sys.stdout.write(line)
        sys.stdout.flush()
    
    def increment(self, description: str = '') -> None:
        """增加进度"""
        self.update(self.current + 1, description)
    
    def finish(self, message: str = '') -> None:
        """完成进度"""
        self.update(self.total, message or '完成')
        sys.stdout.write('\n')
        sys.stdout.flush()
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class Spinner:
    """终端旋转动画"""
    
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str = 'Loading'):
        """
        初始化旋转动画
        
        Args:
            message: 显示消息
        """
        self.message = message
        self.frame_index = 0
    
    def update(self) -> str:
        """更新并返回当前帧"""
        frame = self.FRAMES[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.FRAMES)
        return f"\r{frame} {self.message}"
    
    def set_message(self, message: str) -> None:
        """设置消息"""
        self.message = message


class StatusIndicator:
    """状态指示器"""
    
    SYMBOLS = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '⏳',
        'folder': '📁',
        'file': '📄',
        'config': '⚙️',
        'rocket': '🚀',
        'package': '📦',
        'search': '🔍',
        'chart': '📊',
    }
    
    @classmethod
    def print(cls, status: str, message: str) -> None:
        """打印状态消息"""
        symbol = cls.SYMBOLS.get(status, '•')
        print(f"{symbol} {message}")
    
    @classmethod
    def success(cls, message: str) -> None:
        """打印成功消息"""
        cls.print('success', message)
    
    @classmethod
    def error(cls, message: str) -> None:
        """打印错误消息"""
        cls.print('error', message)
    
    @classmethod
    def warning(cls, message: str) -> None:
        """打印警告消息"""
        cls.print('warning', message)
    
    @classmethod
    def info(cls, message: str) -> None:
        """打印信息消息"""
        cls.print('info', message)
