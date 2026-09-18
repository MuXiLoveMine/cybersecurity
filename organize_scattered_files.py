#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将散落在子目录（tools/、vulnerabilities/、代码/语言/ 等）中的 .md 和 .pdf 文件
移动或整理到对应的文件夹中

规则：
1. 如果有同名文件夹，移动进去（重复则删除源文件）
2. 如果没有同名文件夹且文件是主文档（内容较多的md），则创建基础文件夹结构
"""

import os
import shutil

STUDY_DIR = r"e:\cybersecurity\study"

def has_substantial_content(filepath):
    """判断文件是否有足够内容（超过一定行数/大小）"""
    try:
        size = os.path.getsize(filepath)
        return size > 5000  # 大于5KB认为是主文档
    except:
        return False

def create_basic_folder_structure(filepath, name_without_ext):
    """为单个md/pdf创建基础文件夹结构（仅移动文件，不做内容分割）"""
    dirpath = os.path.dirname(filepath)
    target_folder = os.path.join(dirpath, name_without_ext)
    
    # 创建文件夹
    os.makedirs(target_folder, exist_ok=True)
    
    # 移动md和pdf文件
    md_file = os.path.join(dirpath, name_without_ext + '.md')
    pdf_file = os.path.join(dirpath, name_without_ext + '.pdf')
    
    moved = []
    for f in [md_file, pdf_file]:
        if os.path.exists(f):
            dest = os.path.join(target_folder, os.path.basename(f))
            if not os.path.exists(dest):
                shutil.move(f, dest)
                moved.append(os.path.basename(f))
            else:
                # 已存在，删除源
                try:
                    os.remove(f)
                    moved.append(f"删除重复: {os.path.basename(f)}")
                except:
                    pass
    
    # 创建简易README
    readme_path = os.path.join(target_folder, 'README.md')
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {name_without_ext}\n\n")
            f.write(f"> 本文档包含 {name_without_ext} 相关内容。\n\n")
            f.write("---\n\n")
            f.write("## 文档列表\n\n")
            if os.path.exists(os.path.join(target_folder, name_without_ext + '.md')):
                f.write(f"- [{name_without_ext}.md](./{name_without_ext}.md)\n")
            if os.path.exists(os.path.join(target_folder, name_without_ext + '.pdf')):
                f.write(f"- [{name_without_ext}.pdf](./{name_without_ext}.pdf)\n")
    
    return target_folder, moved

def process_scattered_files(current_dir, depth=0):
    """递归处理散落文件"""
    
    moved_count = 0
    created_folders = 0
    deleted_duplicates = 0
    skipped = 0
    
    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return moved_count, created_folders, deleted_duplicates, skipped
    
    files = []
    dirs = []
    
    for entry in entries:
        entry_path = os.path.join(current_dir, entry)
        if os.path.isfile(entry_path):
            files.append(entry)
        elif os.path.isdir(entry_path):
            dirs.append(entry)
    
    # 先收集需要处理的 md/pdf 对
    md_pdf_pairs = {}  # name -> {'md': path, 'pdf': path}
    
    for filename in files:
        if filename == 'README.md':
            continue
        if filename.startswith('.') or filename.startswith('_'):
            continue
        if '整理报告' in filename or '总报告' in filename:
            continue
        if not (filename.endswith('.md') or filename.endswith('.pdf')):
            continue
        
        if filename.endswith('.md'):
            name = filename[:-3]
            if name not in md_pdf_pairs:
                md_pdf_pairs[name] = {}
            md_pdf_pairs[name]['md'] = os.path.join(current_dir, filename)
        else:
            name = filename[:-4]
            if name not in md_pdf_pairs:
                md_pdf_pairs[name] = {}
            md_pdf_pairs[name]['pdf'] = os.path.join(current_dir, filename)
    
    # 处理每一对
    for name, paths in md_pdf_pairs.items():
        target_folder = os.path.join(current_dir, name)
        md_path = paths.get('md')
        pdf_path = paths.get('pdf')
        
        # 检查是否已有同名文件夹
        if os.path.isdir(target_folder):
            # 移动文件进去
            any_moved = False
            for fpath in [md_path, pdf_path]:
                if fpath and os.path.exists(fpath):
                    dest = os.path.join(target_folder, os.path.basename(fpath))
                    if os.path.exists(dest):
                        # 重复文件，删除源
                        try:
                            src_size = os.path.getsize(fpath)
                            dst_size = os.path.getsize(dest)
                            if src_size == dst_size:
                                os.remove(fpath)
                                deleted_duplicates += 1
                                if depth <= 2:
                                    print(f"  🗑️  删除重复: {os.path.relpath(fpath, STUDY_DIR)}")
                        except:
                            skipped += 1
                    else:
                        shutil.move(fpath, dest)
                        moved_count += 1
                        any_moved = True
                        if depth <= 2:
                            print(f"  ✅ 已移动: {os.path.relpath(fpath, STUDY_DIR)}")
            
            if not any_moved and depth <= 2 and (md_path or pdf_path):
                # 只是删除了重复，不算移动
                pass
        else:
            # 没有同名文件夹，判断是否需要创建
            # 只对有实质内容的md文件创建文件夹
            if md_path and has_substantial_content(md_path):
                folder, moved = create_basic_folder_structure(current_dir, name)
                created_folders += 1
                moved_count += len([m for m in moved if not m.startswith('删除')])
                deleted_duplicates += len([m for m in moved if m.startswith('删除')])
                if depth <= 2:
                    print(f"  📁 创建文件夹: {os.path.relpath(folder, STUDY_DIR)}")
            else:
                skipped += 1
                if depth <= 1:
                    print(f"  ⏭️  跳过（无内容/无文件夹）: {os.path.relpath(md_path or pdf_path, STUDY_DIR)}")
    
    # 递归处理子目录
    for dirname in dirs:
        if dirname == '__pycache__' or dirname.startswith('.'):
            continue
        
        dirpath = os.path.join(current_dir, dirname)
        m, c, d, s = process_scattered_files(dirpath, depth + 1)
        moved_count += m
        created_folders += c
        deleted_duplicates += d
        skipped += s
    
    return moved_count, created_folders, deleted_duplicates, skipped

def main():
    print(f"开始处理目录: {STUDY_DIR}")
    print("=" * 60)
    
    moved, created, deleted, skipped = process_scattered_files(STUDY_DIR)
    
    print("\n" + "=" * 60)
    print("📊 整理完成统计")
    print("=" * 60)
    print(f"移动文件: {moved} 个")
    print(f"创建文件夹: {created} 个")
    print(f"删除重复文件: {deleted} 个")
    print(f"跳过文件: {skipped} 个")

if __name__ == '__main__':
    if not os.path.exists(STUDY_DIR):
        print(f"错误: 目录不存在 - {STUDY_DIR}")
        exit(1)
    
    main()
