import os
import zipfile
import shutil
import json
import subprocess
import sys

# 配置文件名
CONFIG_FILE = "bundle_configs.json"

def load_configs():
    """加载配置，如果没有则创建默认配置"""
    # 1. 定义最新的默认配置（基于你的要求更新）
    default_configs = {
        "全栈开发/Web/AI": {
            "include_extensions": [
                ".py", ".java", ".c", ".cpp", ".h", ".txt", ".md", ".json", 
                ".gradle", ".xml", ".html", ".js", ".ts", ".tsx", ".jsx", 
                ".vue", ".css", ".scss", ".go", ".rs", ".yaml", ".yml"
            ],
            "exclude_extensions": [
                ".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".so", 
                ".zip", ".pyc", ".class", ".o", ".obj"
            ],
            "include_folders": [],
            "exclude_folders": [
                "node_modules", ".git", "__pycache__", "build", "dist", 
                "venv", ".venv", "target", ".idea", ".vscode"
            ]
        },
        "KeyboardAutomation/MyKeymap": {
            "include_extensions": [
                ".go", ".py", ".vue", ".ts", ".tsx", ".js", ".json", 
                ".html", ".css", ".scss", ".md", ".txt"
            ],
            "exclude_extensions": [
                ".png", ".jpg", ".jpeg", ".gif", ".ico", ".exe", ".dll", 
                ".zip", ".pyc", ".class", ".o", ".obj", "pnpm-lock.yaml", "yarn.lock"
            ],
            "include_folders": [
                "config-ui/src", "config-ui/components", "config-ui/views",
                "config-server", "config-server/internal", "config-server/cmd",
                "bin/html", "bin/lib", "tailwind"
            ],
            "exclude_folders": [
                "node_modules", ".git", "__pycache__", "dist", "build", 
                "venv", ".venv", "target", ".idea", ".vscode", "public/locales"
            ],
            "priority_keywords": [
                "MyKeymap", "keymap", "remap", "hotkey", "sendkey", 
                "lanzou_client", "config-server", "config-ui", "tailwind/help_page"
            ]
        },
        "Treeledge": {
            "include_extensions": [
                ".ts", ".tsx", ".rs", ".js", ".jsx", ".json", ".html", 
                ".css", ".md", ".toml", ".yaml", ".yml", ".sql"
            ],
            "exclude_extensions": [
                ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", 
                ".exe", ".dll", ".so", ".zip", ".pyc", ".class", ".o", ".obj",
                "pnpm-lock.yaml", "package-lock.json"
            ],
            "include_folders": [
                "src", "api", "apps", "packages", "services", 
                "components", "hooks", "pages", "utils", "store", 
                "context", "libs", "src-tauri", "tauri-plugins"
            ],
            "exclude_folders": [
                "node_modules", ".git", "__pycache__", "build", "dist", 
                "venv", ".venv", "target", ".idea", ".vscode",
                "gen", "fastlane", "icons", "screenshots", "images",
                "public/locales"
            ]
        }
    }

    # 2. 如果文件不存在，直接创建并返回
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_configs, f, indent=4, ensure_ascii=False)
        return default_configs

    # 3. 如果文件存在，读取它
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            current_configs = json.load(f)
    except json.JSONDecodeError:
        print("配置文件格式错误，将使用默认配置。")
        return default_configs

    # 4. 自动合并：补充缺失的 key
    needs_update = False
    for key, value in default_configs.items():
        if key not in current_configs:
            current_configs[key] = value
            needs_update = True
    
    # 5. 写回文件
    if needs_update:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_configs, f, indent=4, ensure_ascii=False)
            
    return current_configs

def handle_git_operations(directory_path, filter_settings, output_file, commit_message):
    """Git 自动化处理 - 支持自定义提交信息"""
    abs_target_dir = os.path.abspath(directory_path)
    print(f"\n[Git 保护检查] 正在目标目录执行操作: {abs_target_dir}")
    
    # 环境变量：解决 identity unknown (Error 128)
    custom_env = os.environ.copy()
    # 如果用户系统没有配置，使用默认 bot 身份
    if "GIT_AUTHOR_NAME" not in custom_env:
        custom_env["GIT_AUTHOR_NAME"] = "BundleTool"
        custom_env["GIT_AUTHOR_EMAIL"] = "bot@bundle.tool"
        custom_env["GIT_COMMITTER_NAME"] = "BundleTool"
        custom_env["GIT_COMMITTER_EMAIL"] = "bot@bundle.tool"

    try:
        # 1. 检查并初始化
        if not os.path.exists(os.path.join(abs_target_dir, ".git")):
            print("初始化 Git 仓库...")
            subprocess.run(["git", "init"], cwd=abs_target_dir, check=True, capture_output=True)

        # 2. 更新 .gitignore
        gitignore_path = os.path.join(abs_target_dir, ".gitignore")
        ignore_rules = {os.path.basename(output_file), ".gitignore", "temp_extract/"}
        
        if filter_settings.get('exclude_extensions'):
            for ext in filter_settings['exclude_extensions']:
                ignore_rules.add(f"*{ext}")
        if filter_settings.get('exclude_folders'):
            for folder in filter_settings['exclude_folders']:
                ignore_rules.add(f"{folder}/")

        # 读取现有的规则，避免重复追加（可选优化）
        existing_rules = set()
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_rules = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        
        # 将新规则合并
        final_rules = existing_rules.union(ignore_rules)

        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("# Generated by Bundle Tool\n")
            for rule in sorted(final_rules):
                f.write(f"{rule}\n")

        # 3. Add
        subprocess.run(["git", "add", "."], cwd=abs_target_dir, check=True, capture_output=True)
        
        # 4. Commit
        status = subprocess.run(["git", "status", "--porcelain"], cwd=abs_target_dir, capture_output=True, text=True)
        if status.stdout.strip():
            print(f"执行提交，信息: '{commit_message}'")
            result = subprocess.run(
                ["git", "commit", "-m", commit_message], 
                cwd=abs_target_dir, 
                env=custom_env,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("Git 自动提交成功！")
            else:
                print(f"Git 提交失败 (Code {result.returncode}): {result.stderr}")
        else:
            print("工作区干净，无需提交。")
            
    except subprocess.CalledProcessError as e:
        print(f"执行 Git 命令时出错: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        print(f"Git 模块异常: {str(e)}")

def bundle_directory_to_text(directory_path, output_file, config):
    """核心处理逻辑"""
    abs_dir = os.path.abspath(directory_path)
    try:
        print(f"开始遍历目录: {abs_dir}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"=== PROJECT: {os.path.basename(abs_dir)} ===\n")
            f.write(f"=== PATH: {abs_dir} ===\n\n")
            
            # 获取 include_folders (如果为空列表，则代表包含所有非排除目录)
            whitelist_folders = config.get('include_folders', [])

            # --- 1. 结构树 ---
            f.write("=== STRUCTURE ===\n")
            for root, dirs, files in os.walk(abs_dir):
                # 排除逻辑
                dirs[:] = [d for d in dirs if d not in config['exclude_folders'] and not d.startswith('.')]
                
                # 如果定义了白名单文件夹，且当前 root 是根目录，
                # 我们可以简单过滤 dirs，只保留白名单起头的路径
                # (注意：简单的白名单逻辑比较复杂，这里暂时保持原有的排除优先逻辑，
                #  如果用户配置了 include_folders，通常是用于提示重点，而非强制只读这些)
                
                rel_path = os.path.relpath(root, abs_dir)
                level = 0 if rel_path == "." else rel_path.count(os.sep) + 1
                indent = ' ' * 4 * level
                f.write(f"{indent}{os.path.basename(root)}/\n")
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if config['include_extensions'] and ext not in config['include_extensions']: continue
                    if config['exclude_extensions'] and ext in config['exclude_extensions']: continue
                    f.write(f"{' ' * 4 * (level + 1)}{file}\n")
            
            f.write("\n" + "="*60 + "\n\n")

            # --- 2. 内容 ---
            for root, dirs, files in os.walk(abs_dir):
                dirs[:] = [d for d in dirs if d not in config['exclude_folders'] and not d.startswith('.')]
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if config['include_extensions'] and ext not in config['include_extensions']: continue
                    if config['exclude_extensions'] and ext in config['exclude_extensions']: continue
                    
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, abs_dir)
                    
                    f.write(f"FILE: {rel_file_path}\n" + "-"*20 + "\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as cf:
                            f.write(cf.read())
                    except UnicodeDecodeError:
                         # 尝试用 latin-1 读取防止报错，或者直接跳过
                        f.write("[Binary or Non-UTF8 Content]")
                    except Exception as e:
                        f.write(f"[Error reading file: {str(e)}]")
                    f.write("\n\n" + "="*60 + "\n\n")
        return True
    except Exception as e:
        print(f"文件写入失败: {e}")
        return False

def navigate_and_select_directory():
    """交互式目录导航选择器"""
    current_path = os.getcwd()
    
    while True:
        try:
            # 获取当前目录下的子目录
            all_items = os.listdir(current_path)
            dirs = [d for d in all_items if os.path.isdir(os.path.join(current_path, d)) and not d.startswith('.')]
            dirs.sort()
        except PermissionError:
            print(f"没有权限访问: {current_path}")
            current_path = os.path.dirname(current_path)
            continue

        print("\n" + "-"*50)
        print(f"当前位置: {current_path}")
        print("-"*50)
        print("[0]  ✅ 选中此目录 (开始处理)")
        print("[1]  📂 输入绝对路径...")
        print("[..] ⬆️  返回上一级")
        print("-" * 30)
        
        # 分页显示目录，避免太多刷屏
        for i, d in enumerate(dirs, 2):
            print(f"[{i}]  {d}")
        
        choice = input("\n请选择序号或输入命令: ").strip()

        if choice == '0':
            return os.path.abspath(current_path)
        
        elif choice == '1':
            manual_path = input("请输入绝对路径: ").strip()
            if os.path.exists(manual_path) and os.path.isdir(manual_path):
                current_path = manual_path
            else:
                print("❌ 路径不存在或不是文件夹！")
        
        elif choice == '..':
            parent = os.path.dirname(current_path)
            if parent == current_path:
                print("已经是根目录了。")
            else:
                current_path = parent
        
        else:
            try:
                idx = int(choice) - 2
                if 0 <= idx < len(dirs):
                    # 进入子目录
                    current_path = os.path.join(current_path, dirs[idx])
                else:
                    print("❌ 无效的序号")
            except ValueError:
                print("❌ 输入无效")

def display_config_profiles(configs):
    print("\n=== 过滤配置详情列表 ===")
    profile_names = list(configs.keys())
    
    for idx, name in enumerate(profile_names, 1):
        # 简单展示摘要
        print(f"[{idx}] {name}")
    return profile_names

def interactive_mode():
    while True:
        print("\n" + "="*40)
        print("  AI 项目上下文整合工具 (Pro)")
        print("="*40)
        print("1. 处理 ZIP 文件")
        print("2. 浏览/选择 文件夹 (支持递归导航)")
        print("3. 退出")
        
        mode = input("\n请选择模式: ").strip()
        if mode == '3': break
        
        target_path = ""
        output_name = ""
        
        # --- 1. 选取目标 ---
        if mode == '2':
            target_path = navigate_and_select_directory()
            if not target_path: continue
            folder_name = os.path.basename(target_path)
            output_name = f"{folder_name}_context.txt"
            
        elif mode == '1':
            zips = [f for f in os.listdir() if f.lower().endswith('.zip')]
            if not zips: print("❌ 当前目录下没发现ZIP文件！"); continue
            for i, f in enumerate(zips, 1): print(f"{i}. {f}")
            try:
                idx = int(input("请选择ZIP序号: ")) - 1
                target_path = os.path.abspath(zips[idx])
                output_name = zips[idx].replace('.zip', '_context.txt')
            except: continue
        else: continue

        # --- 2. 选取配置 ---
        configs = load_configs()
        profile_names = display_config_profiles(configs)
        
        c_choice = input(f"选择配置序号 (1-{len(profile_names)}, 默认1): ").strip()
        try:
            idx = int(c_choice) - 1
            if 0 <= idx < len(profile_names):
                selected_config_name = profile_names[idx]
            else:
                selected_config_name = profile_names[0]
        except:
            selected_config_name = profile_names[0]
            
        selected_config = configs[selected_config_name]
        print(f"已选择配置: {selected_config_name}")

        # --- 3. 自定义 Git 提交信息 (仅文件夹模式) ---
        commit_msg = "Auto-commit by bundle tool"
        if mode == '2':
            print("\n[Git 设置]")
            user_msg = input(f"请输入 Commit 信息 (回车使用默认: '{commit_msg}'): ").strip()
            if user_msg:
                commit_msg = user_msg

        # --- 4. 执行 ---
        if mode == '2':
            if bundle_directory_to_text(target_path, output_name, selected_config):
                handle_git_operations(target_path, selected_config, output_name, commit_msg)
        else:
            # ZIP 模式
            temp_dir = os.path.abspath("temp_extract_bundle")
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
            try:
                print("正在解压...")
                with zipfile.ZipFile(target_path, 'r') as zr: zr.extractall(temp_dir)
                bundle_directory_to_text(temp_dir, output_name, selected_config)
            except Exception as e:
                print(f"处理ZIP出错: {e}")
            finally:
                if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        
        print(f"\n✅ 处理完成！输出文件: {output_name}")

if __name__ == "__main__":
    interactive_mode()