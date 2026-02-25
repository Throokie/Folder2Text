"""
交互式模式

提供友好的命令行交互界面，支持目录导航、配置选择等功能。
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import shutil

from ..core.scanner import FileScanner
from ..core.bundler import Bundler
from ..config.manager import ConfigManager


class InteractiveMode:
    """交互式模式"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.current_path = Path.cwd()
    
    def run(self) -> int:
        """运行交互式模式"""
        while True:
            self._show_main_menu()
            choice = input("\n请选择: ").strip()
            
            if choice == '1':
                self._bundle_folder()
            elif choice == '2':
                self._bundle_zip()
            elif choice == '3':
                self._scan_directory()
            elif choice == '4':
                self._show_profiles()
            elif choice == '5':
                self._custom_bundle()
            elif choice in ('0', 'q', 'quit', 'exit'):
                print("\n👋 再见!")
                return 0
            else:
                print("❌ 无效选择，请重试")
    
    def _show_main_menu(self) -> None:
        """显示主菜单"""
        self._clear_screen()
        print("\n" + "=" * 60)
        print("  📦 CodeBundle Pro - 智能项目文件整合工具")
        print("=" * 60)
        print(f"\n  当前目录: {self.current_path}")
        print("\n  ┌─────────────────────────────────────────────────┐")
        print("  │                                                 │")
        print("  │   [1] 📁 打包文件夹          [2] 📦 打包 ZIP     │")
        print("  │                                                 │")
        print("  │   [3] 🔍 扫描目录统计        [4] 📋 查看配置     │")
        print("  │                                                 │")
        print("  │   [5] ⚙️  自定义打包                             │")
        print("  │                                                 │")
        print("  │   [0] 🚪 退出                                   │")
        print("  │                                                 │")
        print("  └─────────────────────────────────────────────────┘")
    
    def _clear_screen(self) -> None:
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _navigate_directory(self) -> Optional[Path]:
        """目录导航"""
        current = self.current_path
        
        while True:
            print("\n" + "-" * 60)
            print(f"📂 当前位置: {current}")
            print("-" * 60)
            
            # 获取子目录
            try:
                items = list(current.iterdir())
                dirs = sorted([d for d in items if d.is_dir() and not d.name.startswith('.')])
            except PermissionError:
                print("❌ 没有访问权限")
                current = current.parent
                continue
            
            print("\n[0] ✅ 选择此目录")
            print("[1] 📝 输入路径...")
            print("[..] ⬆️  上级目录")
            print("-" * 40)
            
            # 显示子目录
            for i, d in enumerate(dirs[:20], 2):
                print(f"[{i}] 📁 {d.name}")
            
            if len(dirs) > 20:
                print(f"    ... 还有 {len(dirs) - 20} 个目录")
            
            choice = input("\n选择: ").strip()
            
            if choice == '0':
                return current
            elif choice == '1':
                path = input("输入路径: ").strip()
                if path:
                    new_path = Path(path).expanduser().resolve()
                    if new_path.exists() and new_path.is_dir():
                        current = new_path
                    else:
                        print("❌ 路径不存在或不是目录")
            elif choice == '..':
                parent = current.parent
                if parent != current:
                    current = parent
            else:
                try:
                    idx = int(choice) - 2
                    if 0 <= idx < len(dirs):
                        current = dirs[idx]
                except ValueError:
                    pass
    
    def _select_profile(self) -> Optional[str]:
        """选择配置档案"""
        profiles = self.config_manager.list_profiles()
        
        print("\n📋 选择配置档案:")
        print("-" * 60)
        
        for i, name in enumerate(profiles, 1):
            profile = self.config_manager.get_profile(name)
            builtin = " (内置)" if name in self.config_manager.BUILTIN_PRESETS else ""
            desc = f" - {profile.description}" if profile and profile.description else ""
            print(f"  [{i}] {name}{builtin}{desc}")
        
        print("-" * 60)
        
        choice = input(f"选择 (1-{len(profiles)}, 默认 1): ").strip()
        
        try:
            idx = int(choice) - 1 if choice else 0
            if 0 <= idx < len(profiles):
                return profiles[idx]
        except ValueError:
            pass
        
        return profiles[0] if profiles else None
    
    def _select_format(self) -> str:
        """选择输出格式"""
        formats = ['text', 'markdown', 'json']
        
        print("\n📄 选择输出格式:")
        print("  [1] 纯文本 (text)")
        print("  [2] Markdown (markdown)")
        print("  [3] JSON (json)")
        
        choice = input("选择 (1-3, 默认 1): ").strip()
        
        try:
            idx = int(choice) - 1 if choice else 0
            if 0 <= idx < len(formats):
                return formats[idx]
        except ValueError:
            pass
        
        return 'text'
    
    def _bundle_folder(self) -> None:
        """打包文件夹"""
        print("\n📁 打包文件夹模式")
        print("=" * 60)
        
        # 选择目录
        target_path = self._navigate_directory()
        if not target_path:
            return
        
        # 选择配置
        profile_name = self._select_profile()
        if not profile_name:
            print("❌ 没有可用的配置档案")
            return
        
        profile = self.config_manager.get_profile(profile_name)
        
        # 选择格式
        output_format = self._select_format()
        
        # 输出文件名
        default_output = f"{target_path.name}_bundle.{output_format if output_format != 'markdown' else 'md'}"
        output_name = input(f"输出文件名 (默认: {default_output}): ").strip()
        output_path = Path(output_name) if output_name else Path(default_output)
        
        # 确认
        print(f"\n准备打包:")
        print(f"  📁 目录: {target_path}")
        print(f"  📋 配置: {profile_name}")
        print(f"  📄 格式: {output_format}")
        print(f"  💾 输出: {output_path}")
        
        if input("\n确认执行? (y/n): ").strip().lower() != 'y':
            print("已取消")
            return
        
        # 执行打包
        self._execute_bundle(target_path, output_path, profile, output_format)
    
    def _bundle_zip(self) -> None:
        """打包 ZIP 文件"""
        print("\n📦 打包 ZIP 文件模式")
        print("=" * 60)
        
        # 查找 ZIP 文件
        zip_files = list(Path('.').glob('*.zip'))
        
        if not zip_files:
            print("❌ 当前目录没有 ZIP 文件")
            return
        
        print("\n可用的 ZIP 文件:")
        for i, zf in enumerate(zip_files, 1):
            size_mb = zf.stat().st_size / 1024 / 1024
            print(f"  [{i}] {zf.name} ({size_mb:.2f} MB)")
        
        choice = input(f"\n选择 (1-{len(zip_files)}): ").strip()
        
        try:
            idx = int(choice) - 1
            if not (0 <= idx < len(zip_files)):
                return
            zip_path = zip_files[idx]
        except ValueError:
            return
        
        # 选择配置和格式
        profile_name = self._select_profile()
        profile = self.config_manager.get_profile(profile_name)
        output_format = self._select_format()
        
        # 解压并打包
        import zipfile
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\n📂 解压中...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            # 找到解压后的根目录
            temp_path = Path(temp_dir)
            extracted = list(temp_path.iterdir())
            if len(extracted) == 1 and extracted[0].is_dir():
                source_path = extracted[0]
            else:
                source_path = temp_path
            
            output_path = Path(zip_path.stem + f"_bundle.{output_format if output_format != 'markdown' else 'md'}")
            self._execute_bundle(source_path, output_path, profile, output_format)
    
    def _scan_directory(self) -> None:
        """扫描目录"""
        print("\n🔍 扫描目录模式")
        print("=" * 60)
        
        target_path = self._navigate_directory()
        if not target_path:
            return
        
        profile_name = self._select_profile()
        profile = self.config_manager.get_profile(profile_name)
        
        if not profile:
            print("❌ 配置不存在")
            return
        
        scanner = FileScanner(
            root_path=target_path,
            include_extensions=profile.include_extensions,
            exclude_extensions=profile.exclude_extensions,
            include_folders=profile.include_folders,
            exclude_folders=profile.exclude_folders,
        )
        
        print(f"\n📊 扫描结果:")
        print("-" * 60)
        
        stats = scanner.get_statistics()
        
        print(f"\n  📁 目录: {stats['root_path']}")
        print(f"  📄 文件数: {stats['total_files']}")
        print(f"  📦 总大小: {stats['total_size_human']}")
        
        if stats['extensions']:
            print(f"\n  📊 扩展名分布:")
            for ext, count in list(stats['extensions'].items())[:10]:
                bar = '█' * min(count // 2, 20)
                print(f"    {ext or '(无)':<12} {count:>4} {bar}")
        
        input("\n按回车继续...")
    
    def _show_profiles(self) -> None:
        """显示配置档案"""
        print("\n📋 配置档案列表")
        print("=" * 60)
        
        for name in self.config_manager.list_profiles():
            profile = self.config_manager.get_profile(name)
            if not profile:
                continue
            
            builtin = " [内置]" if name in self.config_manager.BUILTIN_PRESETS else ""
            print(f"\n📁 {name}{builtin}")
            
            if profile.description:
                print(f"   {profile.description}")
            
            print(f"   包含扩展: {len(profile.include_extensions)} 个")
            print(f"   排除扩展: {len(profile.exclude_extensions)} 个")
            print(f"   排除目录: {len(profile.exclude_folders)} 个")
        
        input("\n按回车继续...")
    
    def _custom_bundle(self) -> None:
        """自定义打包"""
        print("\n⚙️  自定义打包模式")
        print("=" * 60)
        
        target_path = self._navigate_directory()
        if not target_path:
            return
        
        print("\n自定义过滤规则 (留空跳过):")
        
        include_ext = input("包含扩展名 (如 .py .js .ts): ").strip()
        exclude_ext = input("排除扩展名 (如 .png .jpg): ").strip()
        exclude_dirs = input("排除目录 (如 node_modules .git): ").strip()
        max_size = input("最大文件大小 (如 5MB): ").strip() or "10MB"
        
        output_format = self._select_format()
        
        output_name = f"{target_path.name}_custom.{output_format if output_format != 'markdown' else 'md'}"
        output_path = Path(input(f"输出文件名 (默认: {output_name}): ").strip() or output_name)
        
        # 构建配置
        profile = self.config_manager.get_profile("通用/Web开发")
        if profile:
            profile = type('ProfileConfig', (), {
                'name': '自定义',
                'include_extensions': include_ext.split() if include_ext else profile.include_extensions,
                'exclude_extensions': exclude_ext.split() if exclude_ext else profile.exclude_extensions,
                'include_folders': [],
                'exclude_folders': exclude_dirs.split() if exclude_dirs else profile.exclude_folders,
                'max_file_size': max_size,
            })()
        
        self._execute_bundle(target_path, output_path, profile, output_format)
    
    def _execute_bundle(
        self, 
        source_path: Path, 
        output_path: Path, 
        profile, 
        output_format: str
    ) -> None:
        """执行打包操作"""
        print("\n🚀 开始打包...")
        
        # 进度回调
        def progress_callback(current: int, total: int, filename: str):
            percent = (current / total) * 100 if total > 0 else 0
            bar_length = 30
            filled = int(bar_length * current / total) if total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.1f}% ({current}/{total}) {filename[:30]:<30}", end='', flush=True)
        
        scanner = FileScanner(
            root_path=source_path,
            include_extensions=profile.include_extensions,
            exclude_extensions=profile.exclude_extensions,
            include_folders=profile.include_folders,
            exclude_folders=profile.exclude_folders,
            max_file_size=self.config_manager.parse_size(getattr(profile, 'max_file_size', '10MB')),
        )
        
        bundler = Bundler(
            scanner=scanner,
            output_path=output_path,
            progress_callback=progress_callback,
        )
        
        result = bundler.bundle(format=output_format)
        
        print()  # 换行
        
        if result.success:
            print(f"\n✅ 打包完成!")
            print(f"📄 输出文件: {result.output_path.absolute()}")
            print(f"📊 文件数量: {result.total_files}")
            print(f"📦 总大小: {result.total_size / 1024 / 1024:.2f} MB")
            print(f"⏱️  耗时: {result.processing_time:.2f} 秒")
        else:
            print(f"\n❌ 打包失败!")
            for e in result.errors:
                print(f"  - {e}")
        
        input("\n按回车继续...")
