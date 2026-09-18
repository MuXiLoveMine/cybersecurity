#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理错误创建的空文件夹（只有README.md的文件夹）
这些是递归脚本在处理子章节时错误创建的
"""

import os
import shutil

STUDY_DIR = r"e:\cybersecurity\study"

def is_empty_readme_folder(dirpath):
    """判断文件夹是否是只有README的空文件夹"""
    try:
        entries = os.listdir(dirpath)
    except:
        return False
    
    # 只有一个文件
    if len(entries) != 1:
        return False
    
    # 那个文件是 README.md
    if entries[0] != 'README.md':
        return False
    
    # 检查 README.md 的大小（空的或很小的）
    readme_path = os.path.join(dirpath, 'README.md')
    try:
        size = os.path.getsize(readme_path)
        # 小于1KB认为是自动生成的空README
        if size < 1024:
            return True
    except:
        pass
    
    return False

def has_numbered_sibling(dirpath, folder_name):
    """检查是否有带编号前缀的兄弟文件夹（如 02_xxx）"""
    parent = os.path.dirname(dirpath)
    try:
        siblings = os.listdir(parent)
    except:
        return False
    
    for sib in siblings:
        sib_path = os.path.join(parent, sib)
        if not os.path.isdir(sib_path):
            continue
        if sib == folder_name:
            continue
        # 检查是否是编号开头的同名文件夹
        if sib.endswith('_' + folder_name) or sib.endswith(folder_name):
            # 格式：02_章节名
            import re
            if re.match(r'^\d{2}_', sib):
                return True
    
    return False

def clean_empty_folders(current_dir, depth=0):
    """递归清理空文件夹"""
    
    deleted = 0
    errors = 0
    
    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return deleted, errors
    
    dirs = []
    for entry in entries:
        entry_path = os.path.join(current_dir, entry)
        if os.path.isdir(entry_path):
            dirs.append(entry)
    
    # 先递归处理子目录
    for dirname in dirs:
        if dirname == '__pycache__' or dirname.startswith('.'):
            continue
        
        dirpath = os.path.join(current_dir, dirname)
        sub_deleted, sub_errors = clean_empty_folders(dirpath, depth + 1)
        deleted += sub_deleted
        errors += sub_errors
    
    # 再检查当前目录下的子文件夹是否需要删除
    for dirname in dirs:
        if dirname == '__pycache__' or dirname.startswith('.'):
            continue
        
        dirpath = os.path.join(current_dir, dirname)
        
        # 判断是否是空README文件夹，并且有带编号的兄弟文件夹
        if is_empty_readme_folder(dirpath) and has_numbered_sibling(dirpath, dirname):
            try:
                shutil.rmtree(dirpath)
                deleted += 1
                if depth <= 3:
                    print(f"  🗑️  删除空文件夹: {os.path.relpath(dirpath, STUDY_DIR)}")
            except Exception as e:
                errors += 1
                print(f"  ❌ 删除失败: {os.path.relpath(dirpath, STUDY_DIR)} - {e}")
    
    return deleted, errors

def main():
    print("=" * 60)
    print("🧹 清理错误创建的空文件夹（只有README的）")
    print("=" * 60)
    
    deleted, errors = clean_empty_folders(STUDY_DIR)
    
    print("\n" + "=" * 60)
    print(f"✅ 清理完成：删除 {deleted} 个空文件夹，{errors} 个错误")
    print("=" * 60)

if __name__ == '__main__':
    if not os.path.exists(STUDY_DIR):
        print(f"错误: 目录不存在 - {STUDY_DIR}")
        exit(1)
    
    main()
