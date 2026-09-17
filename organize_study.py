#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习资料整理脚本
功能：
1. 根据 md 文件名创建文件夹
2. 按内容二级标题（##）分割大类，创建子文件夹和子 md 文件
3. 内容审核：检测是否缺少知识点、代码、工具、命令帮助等
4. 生成内容审核报告
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# 排除的子目录（已有专门结构的代码/工具目录）
EXCLUDE_DIRS = {
    'cpp', 'csharp', 'database', 'golang', 'java', 'javascript',
    'lua', 'perl', 'php', 'powershell', 'python', 'ruby', 'rust',
    'sql', 'tools', 'vulnerabilities', 'Linux', 'shell', 'kali'
}

# 需要检测的内容关键词
CONTENT_CHECKS = {
    'code': ['代码示例', '示例代码', '```', '代码实现', '代码片段', 'exp', 'poc'],
    'tools': ['工具', '工具推荐', '常用工具', '工具使用', 'Burp', 'Nmap', 'Metasploit', 'sqlmap', 'Wireshark'],
    'commands': ['命令', 'cmd', '命令行', '终端', '参数', '选项', '使用方法', '常用命令'],
    'knowledge': ['知识点', '原理', '概念', '基础', '详解', '核心', '总结'],
    'practice': ['实战', '案例', '练习', '实验', '实操', '演练'],
    'defense': ['防御', '防护', '加固', '修复', '解决方案', '防范'],
    'attack': ['攻击', '利用', '漏洞', 'exploit', 'payload'],
}

# 文件名非法字符替换
def sanitize_filename(name):
    """清理文件名中的非法字符"""
    # 移除或替换Windows非法字符
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    # 去除首尾空白和点
    name = name.strip().strip('.')
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    return name if name else 'unnamed'

def extract_heading_title(line):
    """从标题行提取标题文本"""
    # 移除 # 号和空格
    title = re.sub(r'^#+\s*', '', line).strip()
    # 移除编号前缀如 "一、" "2.1" 等
    title = re.sub(r'^[一二三四五六七八九十百千]+、\s*', '', title)
    title = re.sub(r'^\d+(\.\d+)*\s*[.、]?\s*', '', title)
    return title.strip()

def get_heading_level(line):
    """获取标题级别"""
    match = re.match(r'^(#{1,6})\s+', line)
    if match:
        return len(match.group(1))
    return 0

def parse_markdown_sections(content):
    """
    解析 Markdown 内容，按二级标题分割成大段
    返回: list of dict, 每个元素包含 title, level, content, subsections
    """
    lines = content.split('\n')
    sections = []
    current_section = None
    current_lines = []
    
    # 先找一级标题（文档标题）
    doc_title = "未命名文档"
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            doc_title = extract_heading_title(line)
            break
    
    # 检测 YAML frontmatter（只有第一行是 --- 才认为是 frontmatter）
    in_frontmatter = False
    if lines and lines[0].strip() == '---':
        in_frontmatter = True
    
    for i, line in enumerate(lines):
        # frontmatter 结束检测
        if in_frontmatter and line.strip() == '---' and i > 0:
            in_frontmatter = False
            continue
        if in_frontmatter:
            continue
        
        level = get_heading_level(line)
        
        if level == 2:  # 二级标题 - 作为大类
            # 保存上一个 section
            if current_section is not None:
                current_section['content'] = '\n'.join(current_lines).strip()
                sections.append(current_section)
            
            # 开始新的 section
            title = extract_heading_title(line)
            current_section = {
                'title': title,
                'raw_title': line.strip(),
                'level': level,
                'content_lines': [],
                'subsections': []
            }
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)
            
            # 跟踪三级标题作为子项
            if level == 3:
                sub_title = extract_heading_title(line)
                current_section['subsections'].append({
                    'title': sub_title,
                    'raw_title': line.strip()
                })
    
    # 保存最后一个 section
    if current_section is not None:
        current_section['content'] = '\n'.join(current_lines).strip()
        sections.append(current_section)
    
    return doc_title, sections

def analyze_content(content, section_title=""):
    """分析内容，检测缺少哪些类型的内容"""
    findings = defaultdict(list)
    content_lower = content.lower()
    
    for check_type, keywords in CONTENT_CHECKS.items():
        found = False
        for kw in keywords:
            if kw.lower() in content_lower:
                found = True
                break
        if not found:
            findings[check_type].append(f"缺少{check_type}相关内容")
    
    # 检查是否太短
    if len(content.strip()) < 200:
        findings['short'].append("内容过短，建议补充")
    
    # 检查是否有参考资料
    if '参考' not in content and '引用' not in content and '延伸阅读' not in content:
        findings['references'].append("缺少参考资料/延伸阅读")
    
    return dict(findings)

def generate_supplement_section(findings, section_title):
    """生成补充建议部分"""
    if not findings:
        return ""
    
    supplement_lines = [
        "\n\n---\n",
        "\n## 📋 内容审核与补充建议\n",
        f"\n> 针对「{section_title}」部分的内容审核结果：\n"
    ]
    
    type_names = {
        'code': '💻 代码示例',
        'tools': '🔧 工具推荐',
        'commands': '⌨️ 命令帮助',
        'knowledge': '📚 知识点补充',
        'practice': '🎯 实战练习',
        'defense': '🛡️ 防御方案',
        'attack': '⚔️ 攻击技术',
        'short': '📝 内容深度',
        'references': '📖 参考资料',
    }
    
    for check_type, items in findings.items():
        name = type_names.get(check_type, check_type)
        supplement_lines.append(f"\n### {name}\n")
        for item in items:
            supplement_lines.append(f"- ⚠️ {item}\n")
    
    # 添加通用补充建议
    supplement_lines.append("\n---\n")
    supplement_lines.append("\n## 📌 拓展学习资源\n")
    supplement_lines.append("\n### 推荐学习路径\n")
    supplement_lines.append("- 理论基础 → 工具实践 → 实战演练 → 深度研究\n")
    supplement_lines.append("- 建议搭建本地实验环境进行动手练习\n")
    supplement_lines.append("\n### 相关工具与资源\n")
    supplement_lines.append("- 在线实验平台：Hack The Box、TryHackMe、VulnHub\n")
    supplement_lines.append("- 技术文档：官方文档、RFC、OWASP 指南\n")
    supplement_lines.append("- 社区资源：GitHub、安全论坛、技术博客\n")
    
    return ''.join(supplement_lines)

def create_section_structure(base_dir, doc_title, sections, source_file):
    """
    创建文件夹结构和分割后的 md 文件
    """
    # 创建主文件夹（以文档标题命名）
    main_folder_name = sanitize_filename(doc_title)
    main_folder = os.path.join(base_dir, main_folder_name)
    os.makedirs(main_folder, exist_ok=True)
    
    # 生成索引文件
    index_lines = [
        f"# {doc_title}\n",
        f"\n> 本文档整理自：`{os.path.basename(source_file)}`\n",
        f"\n---\n",
        f"\n## 目录\n"
    ]
    
    all_findings = {}
    
    for i, section in enumerate(sections, 1):
        section_title = section['title']
        folder_name = sanitize_filename(f"{i:02d}_{section_title}")
        section_folder = os.path.join(main_folder, folder_name)
        os.makedirs(section_folder, exist_ok=True)
        
        # 分析内容
        findings = analyze_content(section['content'], section_title)
        all_findings[section_title] = findings
        
        # 生成补充内容
        supplement = generate_supplement_section(findings, section_title)
        
        # 创建章节主 md 文件
        section_md_path = os.path.join(section_folder, f"{sanitize_filename(section_title)}.md")
        with open(section_md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {section_title}\n\n")
            f.write(section['content'])
            if supplement:
                f.write(supplement)
        
        # 添加到索引
        index_lines.append(f"\n### [{i:02d}. {section_title}](./{folder_name}/{sanitize_filename(section_title)}.md)\n")
        
        # 如果有子章节，列出子章节
        if section['subsections']:
            for j, sub in enumerate(section['subsections'], 1):
                index_lines.append(f"  - {sub['title']}\n")
    
    # 生成整体审核报告
    index_lines.append(f"\n---\n")
    index_lines.append(f"\n## 📊 内容审核总览\n")
    
    total_sections = len(sections)
    sections_with_issues = sum(1 for f in all_findings.values() if f)
    
    index_lines.append(f"\n- 总章节数：{total_sections}\n")
    index_lines.append(f"- 待完善章节：{sections_with_issues}\n")
    index_lines.append(f"\n### 各章节审核状态\n")
    
    for section_title, findings in all_findings.items():
        status = "✅ 内容较完整" if not findings else f"⚠️ 需补充 {len(findings)} 项"
        index_lines.append(f"- **{section_title}**：{status}\n")
        if findings:
            for ftype in findings.keys():
                index_lines.append(f"  - 缺少：{ftype}\n")
    
    # 写入索引文件
    index_path = os.path.join(main_folder, "README.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.writelines(index_lines)
    
    return main_folder, all_findings

def process_directory(root_dir):
    """处理整个 study 目录"""
    print(f"开始处理目录: {root_dir}")
    print("=" * 60)
    
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'total_sections': 0,
        'skipped_files': 0,
    }
    
    all_reports = []
    
    # 遍历所有子目录
    for category_dir in sorted(os.listdir(root_dir)):
        cat_path = os.path.join(root_dir, category_dir)
        if not os.path.isdir(cat_path):
            continue
        if category_dir in EXCLUDE_DIRS:
            continue
        
        print(f"\n📁 处理分类: {category_dir}")
        print("-" * 40)
        
        # 处理该目录下的 md 文件
        for md_file in sorted(os.listdir(cat_path)):
            if not md_file.endswith('.md'):
                continue
            
            md_path = os.path.join(cat_path, md_file)
            if not os.path.isfile(md_path):
                continue
            
            stats['total_files'] += 1
            file_name = md_file[:-3]  # 移除 .md
            
            # 跳过已经在文件夹里的（通过判断是否已有同名文件夹）
            target_folder = os.path.join(cat_path, sanitize_filename(file_name))
            if os.path.exists(target_folder) and os.path.isdir(target_folder):
                # 检查是否已经处理过（有 README.md）
                if os.path.exists(os.path.join(target_folder, "README.md")):
                    stats['skipped_files'] += 1
                    print(f"  ⏭️  已处理跳过: {md_file}")
                    continue
            
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) < 50:
                    print(f"  ⏭️  内容过短跳过: {md_file}")
                    stats['skipped_files'] += 1
                    continue
                
                # 解析章节
                doc_title, sections = parse_markdown_sections(content)
                
                if not sections:
                    print(f"  ⏭️  无二级章节跳过: {md_file}")
                    stats['skipped_files'] += 1
                    continue
                
                print(f"  ✅ 处理: {md_file} ({len(sections)} 个章节)")
                
                # 创建结构
                main_folder, findings = create_section_structure(
                    cat_path, file_name, sections, md_path
                )
                
                stats['processed_files'] += 1
                stats['total_sections'] += len(sections)
                
                # 记录报告
                issue_count = sum(1 for f in findings.values() if f)
                all_reports.append({
                    'category': category_dir,
                    'file': md_file,
                    'sections': len(sections),
                    'issues': issue_count,
                    'folder': main_folder,
                })
                
            except Exception as e:
                print(f"  ❌ 错误: {md_file} - {e}")
                stats['skipped_files'] += 1
    
    # 生成总报告
    print("\n" + "=" * 60)
    print("📊 处理完成统计")
    print("=" * 60)
    print(f"总文件数: {stats['total_files']}")
    print(f"成功处理: {stats['processed_files']}")
    print(f"生成章节: {stats['total_sections']}")
    print(f"跳过文件: {stats['skipped_files']}")
    
    # 保存详细报告
    report_path = os.path.join(root_dir, "_整理报告.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 学习资料整理报告\n\n")
        f.write(f"> 生成时间：自动生成\n\n")
        f.write("## 统计概览\n\n")
        f.write(f"- 总文件数：{stats['total_files']}\n")
        f.write(f"- 成功处理：{stats['processed_files']}\n")
        f.write(f"- 生成章节：{stats['total_sections']}\n")
        f.write(f"- 跳过文件：{stats['skipped_files']}\n\n")
        
        f.write("## 处理详情\n\n")
        f.write("| 分类 | 文件 | 章节数 | 待完善章节 |\n")
        f.write("|------|------|--------|------------|\n")
        for r in all_reports:
            f.write(f"| {r['category']} | {r['file']} | {r['sections']} | {r['issues']} |\n")
    
    print(f"\n📝 详细报告已保存至: {report_path}")
    return stats

if __name__ == '__main__':
    study_dir = r"e:\cybersecurity\study"
    if not os.path.exists(study_dir):
        print(f"错误: 目录不存在 - {study_dir}")
        sys.exit(1)
    
    process_directory(study_dir)
