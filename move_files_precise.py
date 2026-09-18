#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精准移动散落的 md/pdf 文件到对应文件夹
只处理指定目录下的文件
"""

import os
import shutil

STUDY_DIR = r"e:\cybersecurity\study"

def move_file_to_folder(filepath, target_folder):
    """移动单个文件到目标文件夹，如果目标已存在且大小相同则删除源文件"""
    if not os.path.exists(filepath):
        return 'not_found'
    
    filename = os.path.basename(filepath)
    os.makedirs(target_folder, exist_ok=True)
    dest_path = os.path.join(target_folder, filename)
    
    if os.path.exists(dest_path):
        try:
            src_size = os.path.getsize(filepath)
            dst_size = os.path.getsize(dest_path)
            if src_size == dst_size:
                os.remove(filepath)
                return 'deleted_duplicate'
        except:
            pass
    
    try:
        shutil.move(filepath, dest_path)
        return 'moved'
    except Exception as e:
        print(f"  错误: {e}")
        return 'error'

def process_tools_dir():
    """处理 tools 目录"""
    tools_dir = os.path.join(STUDY_DIR, "02-Web应用安全", "tools")
    if not os.path.exists(tools_dir):
        print("tools 目录不存在")
        return
    
    print("\n🔧 处理 tools 目录")
    print("-" * 40)
    
    # 已有文件夹的工具：移动md/pdf进去
    tools_with_folder = ['Burp_Suite', 'Metasploit', 'Nmap', 'sqlmap']
    for tool in tools_with_folder:
        folder = os.path.join(tools_dir, tool)
        md_file = os.path.join(tools_dir, f"{tool}使用指南.md")
        pdf_file = os.path.join(tools_dir, f"{tool}使用指南.pdf")
        
        # Burp_Suite 文件名是 Burp_Suite使用指南
        if tool == 'Burp_Suite':
            md_file = os.path.join(tools_dir, "Burp_Suite使用指南.md")
            pdf_file = os.path.join(tools_dir, "Burp_Suite使用指南.pdf")
        
        for f in [md_file, pdf_file]:
            if os.path.exists(f):
                result = move_file_to_folder(f, folder)
                fname = os.path.basename(f)
                if result == 'moved':
                    print(f"  ✅ 移动: {fname} → {tool}/")
                elif result == 'deleted_duplicate':
                    print(f"  🗑️ 删除重复: {fname}")
    
    # 没有文件夹的工具：Dirsearch、Wireshark
    new_tools = ['Dirsearch', 'Wireshark']
    for tool in new_tools:
        md_name = f"{tool}使用指南.md"
        pdf_name = f"{tool}使用指南.pdf"
        md_file = os.path.join(tools_dir, md_name)
        pdf_file = os.path.join(tools_dir, pdf_name)
        
        if os.path.exists(md_file):
            target_folder = os.path.join(tools_dir, f"{tool}使用指南")
            os.makedirs(target_folder, exist_ok=True)
            
            # 移动文件
            for f in [md_file, pdf_file]:
                if os.path.exists(f):
                    result = move_file_to_folder(f, target_folder)
                    fname = os.path.basename(f)
                    if result == 'moved':
                        print(f"  📁 创建并移动: {fname} → {tool}使用指南/")
            
            # 创建简易 README
            readme = os.path.join(target_folder, "README.md")
            if not os.path.exists(readme):
                with open(readme, 'w', encoding='utf-8') as f:
                    f.write(f"# {tool}使用指南\n\n")
                    f.write(f"> 本文档包含 {tool} 工具的使用指南。\n\n")
                    f.write("---\n\n")
                    f.write("## 文档列表\n\n")
                    f.write(f"- [{md_name}](./{md_name})\n")
                    if os.path.exists(os.path.join(target_folder, pdf_name)):
                        f.write(f"- [{pdf_name}](./{pdf_name})\n")

def process_vulnerabilities_dir():
    """处理 vulnerabilities 目录"""
    vuln_dir = os.path.join(STUDY_DIR, "02-Web应用安全", "vulnerabilities")
    if not os.path.exists(vuln_dir):
        print("vulnerabilities 目录不存在")
        return
    
    print("\n💉 处理 vulnerabilities 目录")
    print("-" * 40)
    
    md_file = os.path.join(vuln_dir, "核心Web漏洞.md")
    pdf_file = os.path.join(vuln_dir, "核心Web漏洞.pdf")
    
    if os.path.exists(md_file):
        target_folder = os.path.join(vuln_dir, "核心Web漏洞")
        os.makedirs(target_folder, exist_ok=True)
        
        for f in [md_file, pdf_file]:
            if os.path.exists(f):
                result = move_file_to_folder(f, target_folder)
                fname = os.path.basename(f)
                if result == 'moved':
                    print(f"  ✅ 移动: {fname} → 核心Web漏洞/")
                elif result == 'deleted_duplicate':
                    print(f"  🗑️ 删除重复: {fname}")

def process_code_dir():
    """处理代码目录下的各语言 md/pdf 文件"""
    code_dir = os.path.join(STUDY_DIR, "02-Web应用安全", "代码")
    if not os.path.exists(code_dir):
        print("代码目录不存在")
        return
    
    print("\n💻 处理代码目录")
    print("-" * 40)
    
    # 各语言目录及其 md 文件
    lang_files = {
        'cpp': ['C++基础', '进阶知识与使用案例'],
        'csharp': ['C#基础', '进阶知识与使用案例'],
        'database': ['数据库安全'],
        'golang': ['Go语言基础', '进阶知识与使用案例'],
        'java': ['Java基础', '进阶知识与使用案例'],
        'javascript': ['JavaScript基础', '进阶知识与使用案例'],
        'lua': ['Lua基础', '进阶知识与使用案例'],
        'perl': ['Perl基础', '进阶知识与使用案例'],
        'php': ['PHP基础', '进阶知识与使用案例'],
        'powershell': ['PowerShell基础', '进阶知识与使用案例'],
        'python': ['Python基础'],
        'ruby': ['Ruby基础', '进阶知识与使用案例'],
        'rust': ['Rust基础', '进阶知识与使用案例'],
        'sql': ['MySQL基础'],
    }
    
    moved_count = 0
    for lang, files in lang_files.items():
        lang_dir = os.path.join(code_dir, lang)
        if not os.path.exists(lang_dir):
            continue
        
        for base_name in files:
            md_file = os.path.join(lang_dir, f"{base_name}.md")
            pdf_file = os.path.join(lang_dir, f"{base_name}.pdf")
            target_folder = os.path.join(lang_dir, base_name)
            
            if os.path.exists(md_file):
                os.makedirs(target_folder, exist_ok=True)
                
                for f in [md_file, pdf_file]:
                    if os.path.exists(f):
                        result = move_file_to_folder(f, target_folder)
                        fname = os.path.basename(f)
                        if result == 'moved':
                            print(f"  ✅ 移动: {lang}/{fname} → {base_name}/")
                            moved_count += 1
                        elif result == 'deleted_duplicate':
                            print(f"  🗑️ 删除重复: {lang}/{fname}")
    
    if moved_count == 0:
        print("  (无需要移动的文件)")

def process_linux_subdir():
    """处理 Linux 子目录下的散落文件"""
    linux_dir = os.path.join(STUDY_DIR, "01-基础网络安全", "Linux网络与安全配置指南", "Linux")
    if not os.path.exists(linux_dir):
        print("Linux 子目录不存在")
        return
    
    print("\n🐧 处理 Linux 子目录")
    print("-" * 40)
    
    # 顶层 md/pdf 文件
    top_files = ['Linux全部命令手册', 'Linux系统', 'Vim编辑器使用指南']
    for name in top_files:
        md_file = os.path.join(linux_dir, f"{name}.md")
        pdf_file = os.path.join(linux_dir, f"{name}.pdf")
        target_folder = os.path.join(linux_dir, name)
        
        if os.path.exists(md_file):
            os.makedirs(target_folder, exist_ok=True)
            for f in [md_file, pdf_file]:
                if os.path.exists(f):
                    result = move_file_to_folder(f, target_folder)
                    fname = os.path.basename(f)
                    if result == 'moved':
                        print(f"  ✅ 移动: {fname} → {name}/")
                    elif result == 'deleted_duplicate':
                        print(f"  🗑️ 删除重复: {fname}")
    
    # kali 子目录
    kali_dir = os.path.join(linux_dir, 'kali')
    if os.path.exists(kali_dir):
        kali_md = os.path.join(kali_dir, "Kali基本配置指南.md")
        kali_pdf = os.path.join(kali_dir, "Kali基本配置指南.pdf")
        target_folder = os.path.join(kali_dir, "Kali基本配置指南")
        
        if os.path.exists(kali_md):
            os.makedirs(target_folder, exist_ok=True)
            for f in [kali_md, kali_pdf]:
                if os.path.exists(f):
                    result = move_file_to_folder(f, target_folder)
                    fname = os.path.basename(f)
                    if result == 'moved':
                        print(f"  ✅ 移动: kali/{fname} → Kali基本配置指南/")
                    elif result == 'deleted_duplicate':
                        print(f"  🗑️ 删除重复: kali/{fname}")

def process_study_root():
    """处理 study 根目录下的全局 md 文件"""
    print("\n📚 处理 study 根目录全局文件")
    print("-" * 40)
    
    root_files = [
        '学习方法与效率提升指南',
        '工具速查手册',
        '法律合规红线手册',
        '网络安全365天每日学习计划',
        '网络安全52周详细学习路线',
        '网络安全学习路线',
        '职业发展与求职指南',
        '阶段性测试与自我评估',
    ]
    
    # 移动到一个统一的"通用资源"文件夹？还是各自创建文件夹？
    # 创建各自的文件夹
    for name in root_files:
        md_file = os.path.join(STUDY_DIR, f"{name}.md")
        if os.path.exists(md_file):
            target_folder = os.path.join(STUDY_DIR, name)
            os.makedirs(target_folder, exist_ok=True)
            
            result = move_file_to_folder(md_file, target_folder)
            if result == 'moved':
                print(f"  ✅ 移动: {name}.md → {name}/")
            
            # 创建 README
            readme = os.path.join(target_folder, "README.md")
            if not os.path.exists(readme):
                with open(readme, 'w', encoding='utf-8') as f:
                    f.write(f"# {name}\n\n")
                    f.write(f"> 本文档包含 {name} 相关内容。\n\n")
                    f.write("---\n\n")
                    f.write("## 文档列表\n\n")
                    f.write(f"- [{name}.md](./{name}.md)\n")

def main():
    print("=" * 60)
    print("📦 精准移动散落文件到对应文件夹")
    print("=" * 60)
    
    process_tools_dir()
    process_vulnerabilities_dir()
    process_code_dir()
    process_linux_subdir()
    process_study_root()
    
    print("\n" + "=" * 60)
    print("✅ 处理完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
