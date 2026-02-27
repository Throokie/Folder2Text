#!/usr/bin/env python3
"""
CodeBundle Pro 测试脚本

测试核心功能是否正常工作。
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        from codebundle import Bundler, FileScanner, ConfigManager
        print("  ✅ 核心模块导入成功")
    except ImportError as e:
        print(f"  ❌ 核心模块导入失败: {e}")
        return False
    
    try:
        from codebundle.core.encoder import EncodingDetector
        print("  ✅ 编码检测器导入成功")
    except ImportError as e:
        print(f"  ❌ 编码检测器导入失败: {e}")
        return False
    
    try:
        from codebundle.formatters import TextFormatter, MarkdownFormatter, JsonFormatter
        print("  ✅ 格式化器导入成功")
    except ImportError as e:
        print(f"  ❌ 格式化器导入失败: {e}")
        return False
    
    return True


def test_config_manager():
    """测试配置管理器"""
    print("\n📋 测试配置管理器...")
    
    from codebundle.config.manager import ConfigManager
    
    manager = ConfigManager()
    profiles = manager.list_profiles()
    
    print(f"  ✅ 加载了 {len(profiles)} 个配置档案")
    
    # 测试获取配置
    profile = manager.get_profile("Python项目")
    if profile:
        print(f"  ✅ Python项目配置: 包含 {len(profile.include_extensions)} 个扩展名")
    else:
        print("  ⚠️ 未找到 Python项目 配置")
    
    return True


def test_scanner():
    """测试文件扫描器"""
    print("\n🔍 测试文件扫描器...")
    
    from codebundle.core.scanner import FileScanner
    
    # 扫描当前项目
    scanner = FileScanner(
        root_path=Path(__file__).parent,
        include_extensions=['.py'],
        exclude_folders=['__pycache__', '.git', 'node_modules'],
    )
    
    files = scanner.scan_all()
    print(f"  ✅ 扫描到 {len(files)} 个 Python 文件")
    
    stats = scanner.get_statistics()
    print(f"  ✅ 总大小: {stats['total_size_human']}")
    
    return True


def test_encoder():
    """测试编码检测器"""
    print("\n🔤 测试编码检测器...")
    
    from codebundle.core.encoder import EncodingDetector
    
    detector = EncodingDetector()
    
    # 测试检测当前文件
    test_file = Path(__file__)
    encoding, confidence = detector.detect(test_file)
    print(f"  ✅ 检测到文件编码: {encoding} (置信度: {confidence:.2f})")
    
    # 测试安全读取
    content, used_encoding = detector.read_file_safely(test_file)
    if content:
        print(f"  ✅ 成功读取文件，使用编码: {used_encoding}")
    else:
        print("  ❌ 读取文件失败")
        return False
    
    return True


def test_bundler():
    """测试打包器"""
    print("\n📦 测试打包器...")
    
    from codebundle.core.scanner import FileScanner
    from codebundle.core.bundler import Bundler
    from codebundle.config.manager import ConfigManager
    
    # 创建临时输出路径
    output_path = Path(__file__).parent / "test_output.txt"
    
    # 创建扫描器
    scanner = FileScanner(
        root_path=Path(__file__).parent / "codebundle",
        include_extensions=['.py'],
        exclude_folders=['__pycache__', '.git'],
    )
    
    # 创建打包器
    bundler = Bundler(
        scanner=scanner,
        output_path=output_path,
    )
    
    # 执行打包
    result = bundler.bundle(format='text')
    
    if result.success:
        print(f"  ✅ 打包成功: {result.total_files} 个文件")
        print(f"  ✅ 输出文件: {output_path}")
        print(f"  ✅ 耗时: {result.processing_time:.2f} 秒")
        
        # 清理测试文件
        if output_path.exists():
            output_path.unlink()
            print("  ✅ 已清理测试文件")
    else:
        print(f"  ❌ 打包失败: {result.errors}")
        return False
    
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("  CodeBundle Pro 功能测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("配置管理器", test_config_manager),
        ("文件扫描器", test_scanner),
        ("编码检测器", test_encoder),
        ("打包器", test_bundler),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            results.append((name, False))
    
    # 汇总
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print("-" * 60)
    print(f"  总计: {passed}/{total} 通过")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
