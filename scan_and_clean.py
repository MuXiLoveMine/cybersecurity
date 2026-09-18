#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 清理只有 README.md 的空文件夹
2. 扫描所有 README.md 和 总结.md，输出内容质量报告
"""

import os
import shutil

STUDY_DIR = r"e:\cybersecurity\study"

def clean_empty_readme_dirs(current_dir, depth=0):
    """清理只有 README.md 的空文件夹（叶子节点目录）"""
    deleted = 0
    errors = 0
    
    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return deleted, errors
    
    subdirs = []
    files = []
    for entry in entries:
        entry_path = os.path.join(current_dir, entry)
        if os.path.isdir(entry_path):
            subdirs.append(entry)
        else:
            files.append(entry)
    
    # 先递归处理子目录
    for subdir in subdirs:
        if subdir == '__pycache__' or subdir.startswith('.'):
            continue
        sub_path = os.path.join(current_dir, subdir)
        d, e = clean_empty_readme_dirs(sub_path, depth + 1)
        deleted += d
        errors += e
    
    # 再判断当前目录的子文件夹是否为空
    # 重新读取（因为可能有子目录被删了）
    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return deleted, errors
    
    for entry in entries:
        entry_path = os.path.join(current_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        if entry == '__pycache__' or entry.startswith('.'):
            continue
        
        try:
            inner_entries = os.listdir(entry_path)
        except:
            continue
        
        # 只有一个文件且是 README.md
        if len(inner_entries) == 1 and inner_entries[0] == 'README.md':
            readme_path = os.path.join(entry_path, 'README.md')
            try:
                size = os.path.getsize(readme_path)
                # README 很小（< 1KB）说明是自动生成的空文件
                if size < 1024:
                    shutil.rmtree(entry_path)
                    deleted += 1
                    if depth <= 3:
                        print(f"  🗑️  删除空目录: {os.path.relpath(entry_path, STUDY_DIR)}")
            except Exception as e:
                errors += 1
                print(f"  ❌ 删除失败: {os.path.relpath(entry_path, STUDY_DIR)} - {e}")
    
    return deleted, errors

def scan_content_quality(current_dir, depth=0):
    """扫描所有 README.md 和 总结.md 的内容质量"""
    readme_issues = []
    summary_issues = []
    
    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return readme_issues, summary_issues
    
    subdirs = []
    for entry in entries:
        entry_path = os.path.join(current_dir, entry)
        if os.path.isdir(entry_path):
            subdirs.append(entry)
    
    # 检查当前目录的 README.md
    readme_path = os.path.join(current_dir, 'README.md')
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = analyze_readme_quality(content, readme_path)
            if issues:
                readme_issues.append({
                    'path': os.path.relpath(readme_path, STUDY_DIR),
                    'issues': issues,
                    'size': len(content)
                })
        except:
            pass
    
    # 检查当前目录下所有 总结.md
    for entry in entries:
        if '总结' in entry and entry.endswith('.md'):
            summary_path = os.path.join(current_dir, entry)
            try:
                with open(summary_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = analyze_summary_quality(content, summary_path)
                if issues:
                    summary_issues.append({
                        'path': os.path.relpath(summary_path, STUDY_DIR),
                        'issues': issues,
                        'size': len(content)
                    })
            except:
                pass
    
    # 递归子目录
    for subdir in subdirs:
        if subdir == '__pycache__' or subdir.startswith('.'):
            continue
        sub_path = os.path.join(current_dir, subdir)
        r, s = scan_content_quality(sub_path, depth + 1)
        readme_issues.extend(r)
        summary_issues.extend(s)
    
    return readme_issues, summary_issues

def analyze_readme_quality(content, filepath):
    """分析 README.md 质量，返回问题列表"""
    issues = []
    content_lower = content.lower()
    
    # 内容过短
    if len(content) < 500:
        issues.append('内容过短（<500字符）')
    
    # 缺少目录/章节列表
    if '目录' not in content and '章节' not in content and '##' not in content:
        issues.append('缺少目录/章节导航')
    
    # 缺少内容审核总览
    if '内容审核' not in content and '审核总览' not in content:
        issues.append('缺少内容审核总览')
    
    # 只有标题和简单说明
    lines = [l for l in content.strip().split('\n') if l.strip()]
    if len(lines) < 10:
        issues.append('内容行数过少（<10行）')
    
    return issues

def analyze_summary_quality(content, filepath):
    """分析 总结.md 质量，返回问题列表"""
    issues = []
    content_lower = content.lower()
    
    # 内容过短
    if len(content) < 300:
        issues.append('内容过短（<300字符）')
    
    # 缺少实战拓展
    if '实战拓展' not in content and '补充' not in content:
        issues.append('缺少实战拓展内容')
    
    # 缺少学习要点/总结要点
    if '要点' not in content and '总结' not in content[50:]:
        issues.append('缺少明确的总结要点')
    
    # 缺少推荐工具/资源
    if '工具' not in content and '资源' not in content and '推荐' not in content:
        issues.append('缺少推荐工具/学习资源')
    
    return issues

def main():
    print("=" * 70)
    print("🧹 第一步：清理只有 README.md 的空文件夹")
    print("=" * 70)
    
    deleted, errors = clean_empty_readme_dirs(STUDY_DIR)
    print(f"\n✅ 删除空目录: {deleted} 个，错误: {errors} 个")
    
    print("\n" + "=" * 70)
    print("📋 第二步：扫描 README.md 和 总结.md 内容质量")
    print("=" * 70)
    
    readme_issues, summary_issues = scan_content_quality(STUDY_DIR)
    
    print(f"\n📄 有问题的 README.md: {len(readme_issues)} 个")
    if readme_issues:
        for item in readme_issues[:30]:  # 只显示前30个
            print(f"\n  📁 {item['path']}")
            for issue in item['issues']:
                print(f"     ⚠️  {issue}")
        if len(readme_issues) > 30:
            print(f"\n  ... 还有 {len(readme_issues) - 30} 个")
    
    print(f"\n📝 有问题的 总结.md: {len(summary_issues)} 个")
    if summary_issues:
        for item in summary_issues[:30]:  # 只显示前30个
            print(f"\n  📁 {item['path']}")
            for issue in item['issues']:
                print(f"     ⚠️  {issue}")
        if len(summary_issues) > 30:
            print(f"\n  ... 还有 {len(summary_issues) - 30} 个")
    
    # 保存详细报告
    report_path = os.path.join(STUDY_DIR, '_内容质量扫描报告.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 内容质量扫描报告\n\n")
        f.write(f"> 扫描时间：自动生成\n\n")
        f.write("---\n\n")
        
        f.write("## 统计概览\n\n")
        f.write(f"- 有问题的 README.md：{len(readme_issues)} 个\n")
        f.write(f"- 有问题的 总结.md：{len(summary_issues)} 个\n")
        f.write(f"- 删除空目录：{deleted} 个\n\n")
        
        f.write("---\n\n")
        f.write("## 有问题的 README.md\n\n")
        for item in readme_issues:
            f.write(f"### {item['path']}\n\n")
            f.write(f"- 文件大小：{item['size']} 字符\n")
            for issue in item['issues']:
                f.write(f"- ⚠️ {issue}\n")
            f.write("\n")
        
        f.write("---\n\n")
        f.write("## 有问题的 总结.md\n\n")
        for item in summary_issues:
            f.write(f"### {item['path']}\n\n")
            f.write(f"- 文件大小：{item['size']} 字符\n")
            for issue in item['issues']:
                f.write(f"- ⚠️ {issue}\n")
            f.write("\n")
    
    print(f"\n📝 详细报告已保存至: {report_path}")

if __name__ == '__main__':
    if not os.path.exists(STUDY_DIR):
        print(f"错误: 目录不存在 - {STUDY_DIR}")
        exit(1)
    
    main()
