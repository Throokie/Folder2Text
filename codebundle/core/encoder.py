"""
智能编码检测器

自动检测文件编码，支持多种常见编码格式，
并提供安全的文件读取能力。
"""

import codecs
from typing import Optional, Tuple, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EncodingDetector:
    """智能文件编码检测器"""
    
    # 常见编码优先级列表（按优先级排序）
    ENCODING_PRIORITY = [
        'utf-8',
        'utf-8-sig',      # 带BOM的UTF-8
        'gbk',
        'gb2312',
        'gb18030',
        'big5',
        'shift_jis',      # 日文
        'euc-kr',         # 韩文
        'iso-8859-1',     # 西欧语言
        'cp1252',         # Windows西欧
        'latin-1',
    ]
    
    # 二进制文件特征签名
    BINARY_SIGNATURES = [
        b'\x00\x00\x00',  # 空字节
        b'\xff\xd8\xff',  # JPEG
        b'\x89PNG',       # PNG
        b'GIF8',          # GIF
        b'PK\x03\x04',    # ZIP
        b'\x1f\x8b',      # GZIP
        b'Rar!',          # RAR
        b'\x7fELF',       # ELF (Linux可执行文件)
        b'MZ',            # PE (Windows可执行文件)
    ]
    
    # 文本文件特征签名
    TEXT_SIGNATURES = [
        b'<?xml',         # XML
        b'<!DOCTYPE',     # HTML
        b'<html',         # HTML
        b'---\n',         # YAML front matter
        b'#!/',           # Shebang
        b'# -*- coding:', # Python encoding declaration
    ]
    
    def __init__(self, custom_encodings: Optional[List[str]] = None):
        """
        初始化编码检测器
        
        Args:
            custom_encodings: 自定义编码优先级列表
        """
        self.encodings = custom_encodings or self.ENCODING_PRIORITY.copy()
    
    def detect(self, file_path: Path, sample_size: int = 8192) -> Tuple[str, float]:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            sample_size: 采样大小（字节）
            
        Returns:
            (编码名称, 置信度) 元组
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
        except IOError as e:
            logger.warning(f"无法读取文件 {file_path}: {e}")
            return ('utf-8', 0.0)
        
        # 检查是否为二进制文件
        if self._is_binary(raw_data):
            return ('binary', 1.0)
        
        # 尝试各种编码
        best_encoding = 'utf-8'
        best_confidence = 0.0
        
        for encoding in self.encodings:
            try:
                # 尝试解码
                decoded = raw_data.decode(encoding)
                
                # 计算置信度
                confidence = self._calculate_confidence(decoded, raw_data, encoding)
                
                if confidence > best_confidence:
                    best_encoding = encoding
                    best_confidence = confidence
                    
                    # 高置信度时提前返回
                    if confidence > 0.95:
                        break
                        
            except (UnicodeDecodeError, LookupError):
                continue
        
        return (best_encoding, best_confidence)
    
    def _is_binary(self, data: bytes) -> bool:
        """检查数据是否为二进制"""
        # 检查二进制签名
        for sig in self.BINARY_SIGNATURES:
            if data.startswith(sig):
                return True
        
        # 检查空字节比例（二进制文件通常有较多空字节）
        null_count = data.count(b'\x00')
        if len(data) > 0 and null_count / len(data) > 0.1:
            return True
        
        # 检查非打印字符比例
        non_printable = sum(1 for b in data if b < 32 and b not in (9, 10, 13))
        if len(data) > 0 and non_printable / len(data) > 0.3:
            return True
        
        return False
    
    def _calculate_confidence(self, decoded: str, raw_data: bytes, encoding: str) -> float:
        """计算编码置信度"""
        confidence = 0.5  # 基础置信度
        
        # UTF-8 BOM 检测
        if encoding == 'utf-8-sig' and raw_data.startswith(codecs.BOM_UTF8):
            confidence += 0.4
        
        # 检查是否有编码声明
        first_lines = decoded[:500].lower()
        if f'coding: {encoding}' in first_lines or f'charset={encoding}' in first_lines:
            confidence += 0.3
        
        # 检查字符分布合理性
        chinese_chars = sum(1 for c in decoded if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > 0:
            # 如果有中文，中文编码置信度更高
            if encoding in ('gbk', 'gb2312', 'gb18030', 'utf-8'):
                confidence += 0.2
        
        # 检查是否有乱码特征
        replacement_chars = decoded.count('\ufffd')
        if replacement_chars > 0:
            confidence -= 0.3 * (replacement_chars / max(len(decoded), 1))
        
        return min(max(confidence, 0.0), 1.0)
    
    def read_file_safely(
        self, 
        file_path: Path, 
        fallback_encodings: Optional[List[str]] = None
    ) -> Tuple[Optional[str], str]:
        """
        安全读取文件，自动处理编码问题
        
        Args:
            file_path: 文件路径
            fallback_encodings: 备选编码列表
            
        Returns:
            (文件内容, 使用的编码) 元组，失败时返回 (None, '')
        """
        encodings_to_try = fallback_encodings or self.encodings.copy()
        
        # 首先检测编码
        detected_encoding, confidence = self.detect(file_path)
        
        if detected_encoding == 'binary':
            return (None, 'binary')
        
        # 将检测到的编码放在首位
        if detected_encoding != 'utf-8' and detected_encoding in encodings_to_try:
            encodings_to_try.remove(detected_encoding)
            encodings_to_try.insert(0, detected_encoding)
        
        # 尝试读取
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    content = f.read()
                return (content, encoding)
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                logger.debug(f"读取文件 {file_path} 时出错 ({encoding}): {e}")
                continue
        
        # 最后尝试使用 errors='replace'
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return (content, 'utf-8 (with replacements)')
        except Exception as e:
            logger.warning(f"无法读取文件 {file_path}: {e}")
            return (None, '')
    
    @staticmethod
    def is_text_file(file_path: Path) -> bool:
        """快速判断是否为文本文件"""
        detector = EncodingDetector()
        encoding, _ = detector.detect(file_path)
        return encoding != 'binary'
