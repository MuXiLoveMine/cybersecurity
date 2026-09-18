#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理只有 README.md 的空文件夹 + 统计 README/总结 文件数量
"""
import os
import shutil
import sys

STUDY_DIR = r"e:\cybersecurity\study"

def clean_empty_readme_dirs(current_dir):
    deleted = 0
    try:
        entries = os.listdir(current_dir)
    except:
        return 0
    
    subdirs = [e for e in entries if os.path.isdir(os.path.join(current_dir, e))]
    
    # 先递归子目录
    for sd in subdirs:
        if sd.startswith('.') or sd == '__pycache__':
            continue
        deleted += clean_empty_readme_dirs(os.path.join(current_dir, sd))
    
    # 再检查当前目录下的子文件夹
    try:
        entries = os.listdir(current_dir)
    except:
        return deleted
    
    for entry in entries:
        ep = os.path.join(current_dir, entry)
        if not os.path.isdir(ep):
            continue
        if entry.startswith('.') or entry == '__pycache__':
            continue
        try:
            inner = os.listdir(ep)
        except:
            continue
        if len(inner) == 1 and inner[0] == 'README.md':
            rp = os.path.join(ep, 'README.md')
            try:
                sz = os.path.getsize(rp)
                if sz < 1024:
                    shutil.rmtree(ep)
                    deleted += 1
            except:
                pass
    return deleted

def count_files(current_dir):
    readme_count = 0
    summary_count = 0
    total_readme_size = 0
    total_summary_size = 0
    short_readme = 0
    short_summary = 0
    
    try:
        entries = os.listdir(current_dir)
    except:
        return readme_count, summary_count, total_readme_size, total_summary_size, short_readme, short_summary
    
    subdirs = [e for e in entries if os.path.isdir(os.path.join(current_dir, e))]
    
    for entry in entries:
        ep = os.path.join(current_dir, entry)
        if os.path.isfile(ep):
            if entry == 'README.md':
                readme_count += 1
                try:
                    sz = os.path.getsize(ep)
                    total_readme_size += sz
                    if sz < 500:
                        short_readme += 1
                except:
                    pass
            elif '总结' in entry and entry.endswith('.md'):
                summary_count += 1
                try:
                    sz = os.path.getsize(ep)
                    total_summary_size += sz
                    if sz < 300:
                        short_summary += 1
                except:
                    pass
    
    for sd in subdirs:
        if sd.startswith('.') or sd == '__pycache__':
            continue
        r, s, tr, ts, sr, ss = count_files(os.path.join(current_dir, sd))
        readme_count += r
        summary_count += s
        total_readme_size += tr
        total_summary_size += ts
        short_readme += sr
        short_summary += ss
    
    return readme_count, summary_count, total_readme_size, total_summary_size, short_readme, short_summary

def main():
    print("Step 1: Cleaning empty README-only folders...")
    sys.stdout.flush()
    deleted = clean_empty_readme_dirs(STUDY_DIR)
    print(f"Deleted {deleted} empty folders")
    sys.stdout.flush()
    
    print("Step 2: Counting README and summary files...")
    sys.stdout.flush()
    rc, sc, trs, tss, sr, ss = count_files(STUDY_DIR)
    print(f"README.md: {rc} total, {sr} short (<500 chars)")
    print(f"Summary md: {sc} total, {ss} short (<300 chars)")
    print(f"Total README size: {trs} chars")
    print(f"Total summary size: {tss} chars")
    sys.stdout.flush()

if __name__ == '__main__':
    main()
