"""
命令行接口

支持命令行参数和交互式两种使用模式。
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import logging

from ..core.scanner import FileScanner, FilterRule, FilterType
from ..core.bundler import Bundler
from ..config.manager import ConfigManager


def setup_logging(verbose: bool = False) -> None:
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="codebundle",
        description="智能项目文件整合工具 - 将项目文件内容打包成单个文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式
  codebundle
  
  # 打包当前目录
  codebundle bundle . -o output.txt
  
  # 使用指定配置
  codebundle bundle ./myproject -p "Python项目" -f markdown
  
  # 列出可用配置
  codebundle profiles
  
  # 查看配置详情
  codebundle show "Python项目"
""",
    )

    parser.add_argument("-v", "--version", action="store_true", help="显示版本号并退出")

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="静默模式，只输出错误信息"
    )

    parser.add_argument("--no-progress", action="store_true", help="禁用进度条显示")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # bundle 命令
    bundle_parser = subparsers.add_parser("bundle", help="打包项目文件")
    bundle_parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("."),
        help="要打包的目录路径（默认：当前目录）",
    )
    bundle_parser.add_argument(
        "-o", "--output", type=Path, help="输出文件路径（默认：<项目名>_bundle.txt）"
    )
    bundle_parser.add_argument(
        "-p", "--profile", type=str, default="通用/Web开发", help="使用的配置档案名称"
    )
    bundle_parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=["text", "markdown", "json"],
        default="text",
        help="输出格式",
    )
    bundle_parser.add_argument(
        "--include-ext", type=str, nargs="+", help="额外包含的扩展名"
    )
    bundle_parser.add_argument(
        "--exclude-ext", type=str, nargs="+", help="额外排除的扩展名"
    )
    bundle_parser.add_argument(
        "--max-size", type=str, default="10MB", help="最大文件大小（如：1MB, 500KB）"
    )
    bundle_parser.add_argument(
        "-v", "--verbose", action="store_true", help="显示详细输出"
    )
    bundle_parser.add_argument(
        "--dry-run", action="store_true", help="只显示将要处理的文件，不实际输出"
    )
    bundle_parser.add_argument(
        "--line-numbers",
        action="store_true",
        help="在输出中添加行号",
    )
    bundle_parser.add_argument(
        "--git-only",
        action="store_true",
        help="只打包 Git 跟踪的文件",
    )

    # profiles 命令
    profiles_parser = subparsers.add_parser("profiles", help="列出所有配置档案")
    profiles_parser.add_argument(
        "-v", "--verbose", action="store_true", help="显示详细信息"
    )

    # show 命令
    show_parser = subparsers.add_parser("show", help="显示配置档案详情")
    show_parser.add_argument("name", type=str, help="配置档案名称")

    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="扫描目录并显示统计")
    scan_parser.add_argument(
        "path", type=Path, nargs="?", default=Path("."), help="要扫描的目录路径"
    )
    scan_parser.add_argument(
        "-p", "--profile", type=str, default="通用/Web开发", help="使用的配置档案名称"
    )
    scan_parser.add_argument(
        "-v", "--verbose", action="store_true", help="显示详细输出"
    )

    return parser


def cmd_bundle(args: argparse.Namespace) -> int:
    """执行 bundle 命令"""
    quiet = getattr(args, "quiet", False)
    no_progress = getattr(args, "no_progress", False)

    setup_logging(args.verbose)

    config_manager = ConfigManager()
    profile = config_manager.get_profile(args.profile)

    if not profile:
        if not quiet:
            print(f"❌ 配置档案不存在: {args.profile}")
            print(f"可用配置: {', '.join(config_manager.list_profiles())}")
        return 1

    source_path = args.path.resolve()
    if not source_path.exists():
        if not quiet:
            print(f"❌ 路径不存在: {source_path}")
        return 1

    if args.output:
        output_path = args.output
    else:
        output_path = Path(
            f"{source_path.name}_bundle.{args.format if args.format != 'markdown' else 'md'}"
        )

    scanner = FileScanner(
        root_path=source_path,
        include_extensions=profile.include_extensions,
        exclude_extensions=profile.exclude_extensions,
        include_folders=profile.include_folders,
        exclude_folders=profile.exclude_folders,
        max_file_size=ConfigManager.parse_size(args.max_size),
    )

    if args.include_ext:
        for ext in args.include_ext:
            scanner.add_include_extension(ext)

    if args.exclude_ext:
        for ext in args.exclude_ext:
            scanner.add_exclude_extension(ext)

    git_only = getattr(args, "git_only", False)
    tracked_files = None

    if git_only:
        from ..utils.git_ops import GitOperations

        git_ops = GitOperations(source_path)
        if not git_ops.is_git_repo():
            if not quiet:
                print("❌ --git-only 需要在 Git 仓库中使用")
            return 1
        tracked_files = set(git_ops.get_tracked_files())
        if not tracked_files:
            if not quiet:
                print("⚠️ 没有找到 Git 跟踪的文件")

    if args.dry_run:
        if not quiet:
            print(f"\n📁 扫描目录: {source_path}")
            print(f"📋 配置档案: {profile.name}")
            if git_only:
                print("🔗 模式: 只包含 Git 跟踪的文件")
            print(f"📏 最大文件大小: {args.max_size}")
            print("\n将要处理的文件:")
            print("-" * 60)

            files = scanner.scan_all()
            if tracked_files:
                files = [f for f in files if f.relative_path in tracked_files]
            for f in sorted(files, key=lambda x: x.relative_path):
                size_kb = f.size / 1024
                print(f"  {f.relative_path} ({size_kb:.1f} KB)")

            total_size = sum(f.size for f in files)
            print("-" * 60)
            print(
                f"总计: {len(files)} 个文件, {FileScanner._human_readable_size(total_size)}"
            )
        return 0

    show_progress = not (quiet or no_progress or args.verbose)

    def progress_callback(current: int, total: int, filename: str):
        if show_progress:
            percent = (current / total) * 100 if total > 0 else 0
            bar_length = 30
            filled = int(bar_length * current / total) if total > 0 else 0
            bar = "█" * filled + "░" * (bar_length - filled)
            print(
                f"\r[{bar}] {percent:.1f}% ({current}/{total}) {filename[:30]:<30}",
                end="",
                flush=True,
            )

    file_filter = None
    if tracked_files:
        file_filter = lambda f: f.relative_path in tracked_files

    bundler = Bundler(
        scanner=scanner,
        output_path=output_path,
        show_progress=show_progress,
        progress_callback=progress_callback if show_progress else None,
        line_numbers=getattr(args, "line_numbers", False),
        file_filter=file_filter,
    )

    if not quiet:
        print(f"\n🚀 开始打包: {source_path}")
        print(f"📋 配置档案: {profile.name}")
        print(f"📄 输出格式: {args.format}")

    result = bundler.bundle(format=args.format)

    if show_progress:
        print()

    if result.success:
        if not quiet:
            print(f"\n✅ 打包完成!")
            print(f"📄 输出文件: {result.output_path}")
            print(f"📊 文件数量: {result.total_files}")
            print(f"📦 总大小: {result.total_size / 1024 / 1024:.2f} MB")
            print(f"⏱️  耗时: {result.processing_time:.2f} 秒")

            if result.warnings:
                print(f"\n⚠️  警告:")
                for w in result.warnings:
                    print(f"  - {w}")
        return 0
    else:
        if not quiet:
            print(f"\n❌ 打包失败!")
            for e in result.errors:
                print(f"  - {e}")
        return 1


def cmd_profiles(args: argparse.Namespace) -> int:
    """执行 profiles 命令"""
    config_manager = ConfigManager()
    profiles = config_manager.list_profiles()

    print("\n📋 可用配置档案:")
    print("=" * 60)

    for name in profiles:
        profile = config_manager.get_profile(name)
        if profile:
            builtin = " (内置)" if name in config_manager.BUILTIN_PRESETS else ""
            print(f"\n  📁 {name}{builtin}")
            if profile.description:
                print(f"     {profile.description}")

            if args.verbose:
                print(
                    f"     包含扩展: {', '.join(profile.include_extensions[:10])}{'...' if len(profile.include_extensions) > 10 else ''}"
                )
                print(
                    f"     排除扩展: {', '.join(profile.exclude_extensions[:10])}{'...' if len(profile.exclude_extensions) > 10 else ''}"
                )
                print(
                    f"     排除目录: {', '.join(profile.exclude_folders[:5])}{'...' if len(profile.exclude_folders) > 5 else ''}"
                )

    print("\n" + "=" * 60)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """执行 show 命令"""
    config_manager = ConfigManager()
    profile = config_manager.get_profile(args.name)

    if not profile:
        print(f"❌ 配置档案不存在: {args.name}")
        return 1

    print(f"\n📋 配置档案: {profile.name}")
    print("=" * 60)

    if profile.description:
        print(f"\n描述: {profile.description}")

    print(f"\n包含扩展名 ({len(profile.include_extensions)}):")
    print(f"  {', '.join(profile.include_extensions) or '(全部)'}")

    print(f"\n排除扩展名 ({len(profile.exclude_extensions)}):")
    print(f"  {', '.join(profile.exclude_extensions) or '(无)'}")

    print(f"\n包含目录 ({len(profile.include_folders)}):")
    print(f"  {', '.join(profile.include_folders) or '(全部)'}")

    print(f"\n排除目录 ({len(profile.exclude_folders)}):")
    for folder in profile.exclude_folders:
        print(f"  - {folder}")

    print(f"\n最大文件大小: {profile.max_file_size}")
    print(f"默认输出格式: {profile.output_format}")

    if profile.inherit:
        print(f"继承自: {profile.inherit}")

    print()
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    """执行 scan 命令"""
    setup_logging(args.verbose)

    config_manager = ConfigManager()
    profile = config_manager.get_profile(args.profile)

    if not profile:
        print(f"❌ 配置档案不存在: {args.profile}")
        return 1

    source_path = args.path.resolve()
    if not source_path.exists():
        print(f"❌ 路径不存在: {source_path}")
        return 1

    scanner = FileScanner(
        root_path=source_path,
        include_extensions=profile.include_extensions,
        exclude_extensions=profile.exclude_extensions,
        include_folders=profile.include_folders,
        exclude_folders=profile.exclude_folders,
    )

    print(f"\n📁 扫描目录: {source_path}")
    print(f"📋 配置档案: {profile.name}")
    print("\n" + "-" * 60)

    stats = scanner.get_statistics()

    print(f"\n📊 统计信息:")
    print(f"  文件总数: {stats['total_files']}")
    print(f"  总大小: {stats['total_size_human']}")

    if stats["extensions"]:
        print(f"\n📁 扩展名分布:")
        for ext, count in list(stats["extensions"].items())[:15]:
            print(f"  {ext or '(无扩展名)':<15} {count:>5} 个文件")

    if args.verbose:
        print(f"\n📄 文件列表:")
        files = scanner.scan_all()
        for f in sorted(files, key=lambda x: x.relative_path):
            print(f"  {f.relative_path}")

    print()
    return 0


def main() -> int:
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        from .. import __version__

        print(f"codebundle {__version__}")
        return 0

    if args.quiet:
        import logging

        logging.basicConfig(level=logging.ERROR)

    if not args.command:
        if args.quiet:
            return 1
        from .interactive import InteractiveMode

        return InteractiveMode().run()

    if args.command == "bundle":
        return cmd_bundle(args)
    elif args.command == "profiles":
        if args.quiet:
            return 0
        return cmd_profiles(args)
    elif args.command == "show":
        return cmd_show(args)
    elif args.command == "scan":
        return cmd_scan(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
