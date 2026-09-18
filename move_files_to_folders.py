#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将散落在目录中的 .md 和 .pdf 文件移动到对应的同名文件夹中
递归处理所有层级
"""

import os
import shutil

STUDY_DIR = r"e:\cybersecurity\study"

def move_files_recursive(current_dir, depth=0):
    """递归遍历目录，将当前目录下的md/pdf文件移动到同名子文件夹中"""
    
    moved_md = 0
    moved_pdf = 0
    skipped = 0
    errors = 0
    
    # 获取当前目录下的所有文件和目录
    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return moved_md, moved_pdf, skipped, errors
    
    files = []
    dirs = []
    
    for entry in entries:
        entry_path = os.path.join(current_dir, entry)
        if os.path.isfile(entry_path):
            files.append(entry)
        elif os.path.isdir(entry_path):
            dirs.append(entry)
    
    # 处理当前目录下的文件
    for filename in files:
        filepath = os.path.join(current_dir, filename)
        
        # 只处理 .md 和 .pdf 文件
        if not (filename.endswith('.md') or filename.endswith('.pdf')):
            continue
        
        # 跳过隐藏文件、以下划线开头的文件
        if filename.startswith('.') or filename.startswith('_'):
            continue
        
        # 跳过整理报告
        if '整理报告' in filename or '总报告' in filename:
            continue
        
        # 获取文件名（不含扩展名）
        if filename.endswith('.md'):
            name_without_ext = filename[:-3]
        else:
            name_without_ext = filename[:-4]
        
        # 检查是否有同名文件夹
        target_folder = os.path.join(current_dir, name_without_ext)
        
        if not os.path.isdir(target_folder):
            skipped += 1
            if depth <= 2:  # 只打印较浅的层级
                print(f"  ⏭️  无对应文件夹: {os.path.relpath(filepath, STUDY_DIR)}")
            continue
        
        # 目标路径
        dest_path = os.path.join(target_folder, filename)
        
        # 如果目标文件已存在
        if os.path.exists(dest_path):
            try:
                src_size = os.path.getsize(filepath)
                dst_size = os.path.getsize(dest_path)
                if src_size == dst_size:
                    # 文件完全相同，删除源文件
                    try:
                        os.remove(filepath)
                        skipped += 1
                        if depth <= 2:
                            print(f"  🗑️  删除重复源文件: {os.path.relpath(filepath, STUDY_DIR)}")
                    except:
                        skipped += 1
                    continue
            except:
                pass
        
        # 移动文件
        try:
            shutil.move(filepath, dest_path)
            if filename.endswith('.md'):
                moved_md += 1
            else:
                moved_pdf += 1
            if depth <= 2:
                print(f"  ✅ 已移动: {os.path.relpath(filepath, STUDY_DIR)} → {name_without_ext}/")
        except Exception as e:
            errors += 1
            print(f"  ❌ 移动失败: {os.path.relpath(filepath, STUDY_DIR)} - {e}")
    
    # 递归处理子目录
    for dirname in dirs:
        # 跳过一些明显不需要处理的目录（Python缓存等）
        if dirname == '__pycache__' or dirname.startswith('.'):
            continue
        
        dirpath = os.path.join(current_dir, dirname)
        sub_moved_md, sub_moved_pdf, sub_skipped, sub_errors = move_files_recursive(dirpath, depth + 1)
        moved_md += sub_moved_md
        moved_pdf += sub_moved_pdf
        skipped += sub_skipped
        errors += sub_errors
    
    return moved_md, moved_pdf, skipped, errors

def main():
    print(f"开始处理目录: {STUDY_DIR}")
    print("=" * 60)
    
    moved_md, moved_pdf, skipped, errors = move_files_recursive(STUDY_DIR)
    
    print("\n" + "=" * 60)
    print("📊 移动完成统计")
    print("=" * 60)
    print(f"移动 MD 文件: {moved_md} 个")
    print(f"移动 PDF 文件: {moved_pdf} 个")
    print(f"跳过/删除重复: {skipped} 个")
    print(f"错误: {errors} 个")

if __name__ == '__main__':
    if not os.path.exists(STUDY_DIR):
        print(f"错误: 目录不存在 - {STUDY_DIR}")
        exit(1)
    
    main()
