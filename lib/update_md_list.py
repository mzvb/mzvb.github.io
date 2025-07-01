# lib/update_md_list.py
import json
import os
import datetime
import subprocess

# 获取脚本自身的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 仓库的根目录 (假设脚本在 lib 目录下，那么根目录就是 lib 的上一级)
REPO_ROOT = os.path.join(SCRIPT_DIR, '..')
# pages 目录的绝对路径
PAGES_DIR_ABS = os.path.join(REPO_ROOT, 'p')
# list.json 文件的绝对路径 (假设它在仓库根目录)
LIST_JSON_PATH_ABS = os.path.join(REPO_ROOT, 'list.json')


def get_latest_md_file_in_pages(pages_dir_abs):
    """
    在指定的绝对路径目录下查找最新修改的 .md 文件。
    """
    if not os.path.isdir(pages_dir_abs):
        print(f"警告: Markdown 目录 '{pages_dir_abs}' 不存在。")
        return None

    try:
        # 使用 subprocess 在 pages_dir_abs 内部执行 ls 命令
        # 注意：这里直接传入绝对路径给 ls，而不是先 cd 进去，这样更健壮
        command = f"ls -t '{pages_dir_abs}'/*.md 2>/dev/null | head -1"
        result = subprocess.check_output(command, shell=True, text=True)
        file_path_abs = result.strip()
        
        if file_path_abs:
            # 返回相对于仓库根目录的路径，例如 'pages/my-document.md'
            # 这需要将绝对路径转换为相对路径
            return os.path.relpath(file_path_abs, REPO_ROOT)
        return None
    except subprocess.CalledProcessError as e:
        # 如果 ls 没有找到文件，会返回非零退出码，被 CalledProcessError 捕获
        # 如果是其他 ls 错误，也会被捕获
        print(f"执行 ls 命令失败或未找到文件: {e}")
        return None
    except Exception as e:
        print(f"获取最新 .md 文件时发生意外错误: {e}")
        return None

def update_json_list(file_name_relative_to_repo_root, json_file_path_abs):
    """
    更新 JSON 文件，如果文件已存在则更新其日期，否则添加新记录。
    """
    # 获取当前日期，使用UTC时间以保持一致性
    current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    
    data = []
    if os.path.exists(json_file_path_abs):
        with open(json_file_path_abs, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list): # 确保是列表格式
                    print(f"警告: '{json_file_path_abs}' 不是一个列表，将被重置。")
                    data = []
            except json.JSONDecodeError:
                print(f"警告: '{json_file_path_abs}' 内容无效或为空，将被重置。")
                data = []

    found = False
    for item in data:
        # 这里的 filename 应该就是相对路径
        if item.get("filename") == file_name_relative_to_repo_root:
            item["updated_at"] = current_date
            found = True
            break
    
    if not found:
        data.append({"filename": file_name_relative_to_repo_root, "updated_at": current_date})
    
    # 可选：按文件名排序，使 JSON 内容更稳定（便于版本控制）
    data.sort(key=lambda x: x.get("filename", ""))

    with open(json_file_path_abs, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False) # ensure_ascii=False 支持中文显示
    
    print(f"'{file_name_relative_to_repo_root}' 的记录已更新到 '{json_file_path_abs}'。")
    with open(json_file_path_abs, 'r', encoding='utf-8') as f:
        print("\n更新后的 JSON 内容:")
        print(f.read())


if __name__ == "__main__":
    print(f"脚本目录: {SCRIPT_DIR}")
    print(f"仓库根目录: {REPO_ROOT}")
    print(f"Markdown 目录: {PAGES_DIR_ABS}")
    print(f"JSON 文件路径: {LIST_JSON_PATH_ABS}")

    latest_md = get_latest_md_file_in_pages(PAGES_DIR_ABS)
    
    if latest_md:
        print(f"检测到最新修改的 Markdown 文件 (相对路径): {latest_md}")
        update_json_list(latest_md, LIST_JSON_PATH_ABS)
    else:
        print(f"在 '{PAGES_DIR_ABS}' 中未找到任何 Markdown 文件。")
