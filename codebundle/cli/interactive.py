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
from ..config.manager import ConfigManager, ProfileConfig


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
                self._show_profiles()
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
        print("  │   [3] 📋 查看配置档案                           │")
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
        """选择配置档案（显示详细信息）"""
        profiles = self.config_manager.list_profiles()
        
        while True:
            print("\n" + "=" * 60)
            print("📋 选择配置档案")
            print("=" * 60)
            
            for i, name in enumerate(profiles, 1):
                profile = self.config_manager.get_profile(name)
                builtin = " (内置)" if name in self.config_manager.BUILTIN_PRESETS else ""
                print(f"\n  [{i}] {name}{builtin}")
                if profile:
                    if profile.description:
                        print(f"      📝 {profile.description}")
                    # 显示包含的扩展名
                    if profile.include_extensions:
                        exts = sorted(profile.include_extensions)[:10]
                        more = f" ... 共{len(profile.include_extensions)}个" if len(profile.include_extensions) > 10 else ""
                        print(f"      ✅ 包含: {', '.join(exts)}{more}")
                    # 显示排除的扩展名
                    if profile.exclude_extensions:
                        exts = sorted(profile.exclude_extensions)[:6]
                        more = f" ... 共{len(profile.exclude_extensions)}个" if len(profile.exclude_extensions) > 6 else ""
                        print(f"      ❌ 排除: {', '.join(exts)}{more}")
            
            print("\n" + "-" * 60)
            print("💡 输入序号选择 | 输入 'd <序号>' 查看详情 | 回车默认选第1个")
            
            choice = input("\n选择: ").strip().lower()
            
            if choice.startswith('d '):
                try:
                    idx = int(choice[2:]) - 1
                    if 0 <= idx < len(profiles):
                        self._show_profile_detail(profiles[idx])
                except ValueError:
                    pass
                continue
            
            try:
                if not choice:
                    idx = 0
                else:
                    idx = int(choice) - 1
                
                if 0 <= idx < len(profiles):
                    return profiles[idx]
            except ValueError:
                for name in profiles:
                    if choice in name.lower():
                        return name
            
            print("❌ 无效选择")
    
    def _show_profile_detail(self, profile_name: str) -> None:
        """显示配置档案详情"""
        profile = self.config_manager.get_profile(profile_name)
        if not profile:
            return
        
        print("\n" + "=" * 60)
        print(f"📋 配置档案: {profile_name}")
        print("=" * 60)
        
        if profile.description:
            print(f"\n📝 描述: {profile.description}")
        
        print(f"\n✅ 包含扩展名 ({len(profile.include_extensions)}):")
        if profile.include_extensions:
            exts = sorted(profile.include_extensions)
            for i in range(0, len(exts), 10):
                print(f"   {', '.join(exts[i:i+10])}")
        else:
            print("   (全部)")
        
        print(f"\n❌ 排除扩展名 ({len(profile.exclude_extensions)}):")
        if profile.exclude_extensions:
            exts = sorted(profile.exclude_extensions)
            for i in range(0, len(exts), 10):
                print(f"   {', '.join(exts[i:i+10])}")
        else:
            print("   (无)")
        
        print(f"\n📁 排除目录 ({len(profile.exclude_folders)}):")
        for folder in sorted(profile.exclude_folders):
            print(f"   - {folder}")
        
        print(f"\n📏 最大文件大小: {profile.max_file_size}")
        
        input("\n按回车继续...")
    
    def _select_format(self) -> str:
        """选择输出格式"""
        formats = ['text', 'markdown', 'json']
        
        print("\n📄 选择输出格式:")
        print("  [1] 纯文本 - 简单直接")
        print("  [2] Markdown (markdown) - 带语法高亮，适合阅读")
        print("  [3] JSON (json) - 结构化数据，便于程序处理")
        
        choice = input("选择 (1-3, 默认 1): ").strip()
        
        try:
            idx = int(choice) - 1 if choice else 0
            if 0 <= idx < len(formats):
                return formats[idx]
        except ValueError:
            pass
        
        return 'text'
    
    def _adjust_extensions(self, profile: ProfileConfig) -> ProfileConfig:
        """调整扩展名配置"""
        include_exts = list(profile.include_extensions)
        exclude_exts = list(profile.exclude_extensions)
        
        while True:
            print("\n" + "-" * 60)
            print("⚙️  扩展名调整")
            print("-" * 60)
            print(f"\n✅ 当前包含扩展名 ({len(include_exts)}):")
            if include_exts:
                exts = sorted(include_exts)
                for i in range(0, len(exts), 10):
                    print(f"   {', '.join(exts[i:i+10])}")
            else:
                print("   (全部)")
            
            print(f"\n❌ 当前排除扩展名 ({len(exclude_exts)}):")
            if exclude_exts:
                exts = sorted(exclude_exts)
                for i in range(0, len(exts), 10):
                    print(f"   {', '.join(exts[i:i+10])}")
            else:
                print("   (无)")
            
            print("\n[1] ➕ 添加包含扩展名")
            print("[2] ➖ 移除包含扩展名")
            print("[3] ➕ 添加排除扩展名")
            print("[4] ➖ 移除排除扩展名")
            print("[0] ✅ 完成调整")
            
            choice = input("\n选择: ").strip()
            
            if choice == '1':
                exts = input("输入要添加的扩展名 (如 .py .js .ts): ").strip()
                for ext in exts.split():
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    if ext not in include_exts:
                        include_exts.append(ext)
                print(f"✅ 已添加")
            
            elif choice == '2':
                exts = input("输入要移除的扩展名 (如 .py .js): ").strip()
                for ext in exts.split():
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    if ext in include_exts:
                        include_exts.remove(ext)
                print(f"✅ 已移除")
            
            elif choice == '3':
                exts = input("输入要排除的扩展名 (如 .min.js .bak): ").strip()
                for ext in exts.split():
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    if ext not in exclude_exts:
                        exclude_exts.append(ext)
                print(f"✅ 已添加排除")
            
            elif choice == '4':
                exts = input("输入要移除排除的扩展名: ").strip()
                for ext in exts.split():
                    if not ext.startswith('.'):
                        ext = '.' + ext
                    if ext in exclude_exts:
                        exclude_exts.remove(ext)
                print(f"✅ 已移除排除")
            
            elif choice == '0':
                break
        
        return ProfileConfig(
            name=profile.name + " (已调整)",
            description=profile.description,
            include_extensions=include_exts,
            exclude_extensions=exclude_exts,
            include_folders=profile.include_folders,
            exclude_folders=profile.exclude_folders,
            max_file_size=profile.max_file_size,
        )
    
    def _show_scan_preview(self, scanner: FileScanner) -> bool:
        """显示扫描预览，返回是否继续"""
        print("\n🔍 正在扫描目录...")
        
        stats = scanner.get_statistics()
        
        print("\n" + "=" * 60)
        print("📊 扫描结果预览")
        print("=" * 60)
        
        print(f"\n  📁 目录: {stats['root_path']}")
        print(f"  📄 文件数: {stats['total_files']}")
        print(f"  📦 总大小: {stats['total_size_human']}")
        
        if stats['extensions']:
            print(f"\n  📊 扩展名分布:")
            for ext, count in list(stats['extensions'].items())[:15]:
                bar = '█' * min(count, 30)
                print(f"    {ext or '(无扩展名)':<12} {count:>4} {bar}")
        
        if stats['total_files'] == 0:
            print("\n⚠️  没有找到符合条件的文件！")
            return False
        
        # 询问是否查看详细文件列表
        print("\n" + "-" * 60)
        choice = input("是否查看详细文件列表? (y/N): ").strip().lower()
        
        if choice == 'y':
            print("\n📄 文件列表:")
            print("-" * 60)
            files = sorted(stats['files'], key=lambda x: x.relative_path)
            for f in files:
                size_kb = f.size / 1024
                print(f"  {f.relative_path} ({size_kb:.1f} KB)")
            print("-" * 60)
            print(f"  共 {len(files)} 个文件")
        
        # 确认是否继续
        print("\n" + "-" * 60)
        choice = input("确认打包这些文件? (Y/n): ").strip().lower()
        
        return choice != 'n'
    
    def _bundle_folder(self) -> None:
        """打包文件夹（优化后的流程）"""
        print("\n📁 打包文件夹")
        print("=" * 60)
        
        # Step 1: 选择目录
        print("\n【步骤 1/5】选择目录")
        target_path = self._navigate_directory()
        if not target_path:
            return
        
        # Step 2: 选择配置档案
        print("\n【步骤 2/5】选择配置档案")
        profile_name = self._select_profile()
        if not profile_name:
            print("❌ 没有可用的配置档案")
            return
        
        profile = self.config_manager.get_profile(profile_name)
        
        # Step 3: 调整扩展名
        print("\n【步骤 3/5】调整扩展名（可选）")
        choice = input("是否需要调整扩展名配置? (y/N): ").strip().lower()
        if choice == 'y':
            profile = self._adjust_extensions(profile)
        
        # Step 4: 扫描预览
        print("\n【步骤 4/5】扫描预览")
        
        scanner = FileScanner(
            root_path=target_path,
            include_extensions=profile.include_extensions,
            exclude_extensions=profile.exclude_extensions,
            include_folders=profile.include_folders,
            exclude_folders=profile.exclude_folders,
            max_file_size=self.config_manager.parse_size(profile.max_file_size),
        )
        
        if not self._show_scan_preview(scanner):
            print("❌ 已取消")
            input("\n按回车继续...")
            return
        
        # Step 5: 选择格式并执行
        print("\n【步骤 5/5】选择输出格式")
        output_format = self._select_format()
        
        # 输出文件名
        default_output = f"{target_path.name}_bundle.{output_format if output_format != 'markdown' else 'md'}"
        output_name = input(f"\n输出文件名 (默认: {default_output}): ").strip()
        output_path = Path(output_name) if output_name else Path(default_output)
        
        # 执行打包
        self._execute_bundle(scanner, output_path, output_format)
    
    def _bundle_zip(self) -> None:
        """打包 ZIP 文件"""
        print("\n📦 打包 ZIP 文件")
        print("=" * 60)
        
        zip_files = list(Path('.').glob('*.zip'))
        
        if not zip_files:
            print("❌ 当前目录没有 ZIP 文件")
            input("\n按回车继续...")
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
        
        # 选择配置
        profile_name = self._select_profile()
        profile = self.config_manager.get_profile(profile_name)
        
        # 调整扩展名
        choice = input("\n是否需要调整扩展名配置? (y/N): ").strip().lower()
        if choice == 'y':
            profile = self._adjust_extensions(profile)
        
        # 解压并打包
        import zipfile
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\n📂 解压中...")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            temp_path = Path(temp_dir)
            extracted = list(temp_path.iterdir())
            if len(extracted) == 1 and extracted[0].is_dir():
                source_path = extracted[0]
            else:
                source_path = temp_path
            
            scanner = FileScanner(
                root_path=source_path,
                include_extensions=profile.include_extensions,
                exclude_extensions=profile.exclude_extensions,
                include_folders=profile.include_folders,
                exclude_folders=profile.exclude_folders,
                max_file_size=self.config_manager.parse_size(profile.max_file_size),
            )
            
            if not self._show_scan_preview(scanner):
                print("❌ 已取消")
                input("\n按回车继续...")
                return
            
            output_format = self._select_format()
            output_path = Path(zip_path.stem + f"_bundle.{output_format if output_format != 'markdown' else 'md'}")
            
            self._execute_bundle(scanner, output_path, output_format)
    
    def _show_profiles(self) -> None:
        """显示配置档案列表"""
        print("\n📋 配置档案列表")
        print("=" * 60)
        
        profiles = self.config_manager.list_profiles()
        
        for name in profiles:
            profile = self.config_manager.get_profile(name)
            if not profile:
                continue
            
            builtin = " [内置]" if name in self.config_manager.BUILTIN_PRESETS else ""
            print(f"\n📁 {name}{builtin}")
            
            if profile.description:
                print(f"   📝 {profile.description}")
            
            # 显示扩展名摘要
            if profile.include_extensions:
                exts = sorted(profile.include_extensions)[:6]
                more = f" ... +{len(profile.include_extensions)-6}" if len(profile.include_extensions) > 6 else ""
                print(f"   ✅ 包含: {', '.join(exts)}{more}")
            
            if profile.exclude_extensions:
                exts = sorted(profile.exclude_extensions)[:4]
                more = f" ... +{len(profile.exclude_extensions)-4}" if len(profile.exclude_extensions) > 4 else ""
                print(f"   ❌ 排除: {', '.join(exts)}{more}")
            
            print(f"   📁 排除目录: {len(profile.exclude_folders)} 个")
        
        print("\n" + "-" * 60)
        choice = input("输入序号查看详情，或回车返回: ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                self._show_profile_detail(profiles[idx])
        except ValueError:
            pass
    
    def _execute_bundle(
        self, 
        scanner: FileScanner, 
        output_path: Path, 
        output_format: str
    ) -> None:
        """执行打包操作"""
        print("\n🚀 开始打包...")
        
        def progress_callback(current: int, total: int, filename: str):
            percent = (current / total) * 100 if total > 0 else 0
            bar_length = 30
            filled = int(bar_length * current / total) if total > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r[{bar}] {percent:.1f}% ({current}/{total}) {filename[:30]:<30}", end='', flush=True)
        
        bundler = Bundler(
            scanner=scanner,
            output_path=output_path,
            progress_callback=progress_callback,
        )
        
        result = bundler.bundle(format=output_format)
        
        print()
        
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
