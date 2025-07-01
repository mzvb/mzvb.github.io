import os
import json
from datetime import datetime

def update_file_list():
    # 获取 p/ 目录下的所有 .md 文件
    files = [f for f in os.listdir('p') if f.endswith('.md')]
    
    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 读取现有的 list.json 文件
    if os.path.exists('list.json'):
        with open('list.json', 'r') as f:
            file_list = json.load(f)
    else:
        file_list = []

    # 更新文件列表
    for file in files:
        # 如果该文件还没有在 list.json 中，则添加
        if not any(f[0] == file for f in file_list):
            file_list.append([file, timestamp])

    # 保存回 list.json
    with open('list.json', 'w') as f:
        json.dump(file_list, f, indent=4)

if __name__ == "__main__":
    update_file_list()
