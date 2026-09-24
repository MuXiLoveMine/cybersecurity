# Python勒索软件检测脚本示例

### 6.1 勒索信特征检测脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
勒索信特征检测脚本
扫描指定目录，检测已知勒索软件的勒索信文件
仅用于安全教育和授权研究
"""

import os
import re
from pathlib import Path


# 已知勒索信文件名模式
RANSOM_NOTE_PATTERNS = [
    # 文件名模式
    "restore-my-files.txt", "restore_files.txt",
    "read_instructions.txt", "read_me.txt", "readme.txt",
    "how_to_decrypt.txt", "how_to_recover.txt",
    "help_decrypt.txt", "help_recover.txt",
    "ransom.txt", "ransom_note.txt",
    "decryption_instructions.txt",
    "your_files_are_locked.txt",
    "recovery_key.txt",
    "!!!_readme_!!!.txt",
    "_readme_.txt",
    "info.txt", "note.txt",
    # 带家族特征
    "lockbit.txt", "conti.txt", "blackcat.txt",
    "clop_readme.txt", "akira_readme.txt",
]

# 勒索信内容关键词模式（多语言）
RANSOM_CONTENT_PATTERNS = [
    r"your files.*encrypt",       # 你的文件已被加密
    r"all.*files.*encrypt",
    r"to decrypt.*files",
    r"bitcoin|btc|monero|xmr",   # 加密货币
    r"\.onion",                    # Tor隐藏服务
    r"tor browser",
    r"ransom|payment|decrypt",   # 赎金/支付/解密
    r"your data.*stolen",         # 数据已窃取（双重勒索）
    r"leak.*data|publish.*data",
    r"private key|recovery key",
    r"deadline|countdown|timer", # 倒计时
]

# 加密文件后缀模式（常见勒索软件后缀）
ENCRYPTED_EXTENSIONS = [
    ".lockbit", ".conti", ".blackcat", ".clop", ".akira",
    ".revil", ".sodinokibi", ".ryuk", ".locky",
    ".encrypted", ".locked", ".crypto", ".enc",
    ".ransom", ".lockedby", ".crypted",
    ".encrypted_rsa", ".wcry", ".wnry",
]


def scan_ransom_notes(directory):
    """扫描目录中的勒索信文件"""
    found_notes = []
    found_encrypted = []
    found_by_content = []

    print("=" * 60)
    print(f"勒索信特征扫描: {directory}")
    print("=" * 60)

    file_count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_count += 1

            # 检查文件名是否匹配已知勒索信
            filename_lower = filename.lower()
            for pattern in RANSOM_NOTE_PATTERNS:
                if pattern in filename_lower:
                    found_notes.append(filepath)
                    break

            # 检查文件后缀是否为已知加密后缀
            for ext in ENCRYPTED_EXTENSIONS:
                if filename_lower.endswith(ext):
                    found_encrypted.append(filepath)
                    break

            # 检查.txt/.hta/.html文件内容是否匹配勒索信特征
            if (filename_lower.endswith(('.txt', '.hta', '.html', '.htm'))
                    and filepath not in found_notes):
                try:
                    with open(filepath, 'r', encoding='utf-8',
                             errors='ignore') as f:
                        content = f.read(10000)  # 只读前10KB
                    for pattern in RANSOM_CONTENT_PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_by_content.append(
                                (filepath, pattern))
                            break
                except (PermissionError, OSError):
                    pass

    print(f"\n扫描文件总数: {file_count}")

    if found_notes:
        print(f"\n[!] 发现匹配文件名的勒索信 ({len(found_notes)}个)")
        for f in found_notes:
            print(f"    {f}")

    if found_by_content:
        print(f"\n[!] 内容匹配勒索信特征的文件 ({len(found_by_content)}个)")
        for f, pattern in found_by_content:
            print(f"    {f} (匹配: {pattern})")

    if found_encrypted:
        print(f"\n[!] 发现疑似加密文件 ({len(found_encrypted)}个)")
        for f in found_encrypted[:20]:
            print(f"    {f}")
        if len(found_encrypted) > 20:
            print(f"    ... 共 {len(found_encrypted)} 个")

    if not found_notes and not found_by_content and not found_encrypted:
        print("\n[OK] 未发现勒索信特征")

    # 风险评估
    print("\n--- 风险评估 ---")
    risk_score = 0
    if found_notes:
        risk_score += 50
    if found_by_content:
        risk_score += 30
    if found_encrypted:
        risk_score += 20

    if risk_score >= 80:
        print(f"风险等级: 极高 ({risk_score}/100) - 可能正在遭受勒索软件攻击！")
    elif risk_score >= 50:
        print(f"风险等级: 高 ({risk_score}/100) - 发现勒索软件特征，请立即排查！")
    elif risk_score >= 20:
        print(f"风险等级: 中 ({risk_score}/100) - 存在可疑文件，建议进一步分析")
    else:
        print(f"风险等级: 低 ({risk_score}/100) - 未发现明显勒索软件特征")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python ransom_note_detector.py <目录路径>")
        sys.exit(1)
    scan_ransom_notes(sys.argv[1])
```

### 6.2 文件熵值异常检测脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件熵值异常检测脚本
计算文件熵值，识别被加密的高熵值文件
仅用于安全教育和授权研究
"""

import os
import sys
import math
from collections import defaultdict


def calculate_entropy(filepath, max_size=1024 * 1024):
    """计算文件熵值（限制读取大小以提高性能）"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read(max_size)
    except (PermissionError, OSError):
        return None

    if not data:
        return 0.0

    # 统计字节频率
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1

    # 香农熵
    length = len(data)
    entropy = 0.0
    for count in freq.values():
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)

    return entropy


def is_likely_text(filepath):
    """判断文件是否为文本文件"""
    text_extensions = ['.txt', '.log', '.csv', '.json', '.xml',
                      '.ini', '.cfg', '.py', '.js', '.html',
                      '.md', '.bat', '.ps1', '.sh']
    ext = os.path.splitext(filepath)[1].lower()
    return ext in text_extensions


def scan_entropy_anomalies(directory, threshold=7.0, max_files=None):
    """扫描目录中熵值异常的文件"""
    print("=" * 60)
    print(f"文件熵值异常检测: {directory}")
    print(f"熵值阈值: {threshold} (高熵值可能表示加密)")
    print("=" * 60)

    high_entropy_files = []
    encrypted_candidates = []
    total_files = 0
    scanned = 0
    errors = 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            total_files += 1

            # 跳过目录过多的情况
            if max_files and scanned >= max_files:
                continue

            entropy = calculate_entropy(filepath)
            if entropy is None:
                errors += 1
                continue
            scanned += 1

            # 文本文件高熵值 = 异常（文本文件熵值通常 < 5）
            if entropy >= threshold:
                ext = os.path.splitext(filename)[1].lower()
                if is_likely_text(filepath):
                    # 文本文件高熵值 → 极可疑
                    encrypted_candidates.append(
                        (filepath, entropy, "文本文件但熵值极高"))
                else:
                    high_entropy_files.append(
                        (filepath, entropy, ext))

    print(f"\n扫描文件总数: {total_files}")
    print(f"成功扫描: {scanned}")
    print(f"扫描失败: {errors}")

    if encrypted_candidates:
        print(f"\n[!!!] 极可疑 - 文本文件被加密 ({len(encrypted_candidates)}个)")
        print("  文本文件熵值正常应 < 5.0，高于7.0极可能被加密")
        for f, e, note in encrypted_candidates[:20]:
            print(f"  熵值={e:.4f} | {f}")
            print(f"         ({note})")

    if high_entropy_files:
        print(f"\n[!] 高熵值文件 ({len(high_entropy_files)}个)")
        print("  这些文件可能被加密或压缩")
        for f, e, ext in high_entropy_files[:20]:
            print(f"  熵值={e:.4f} | {ext or '(无后缀)'} | {f}")
        if len(high_entropy_files) > 20:
            print(f"  ... 共 {len(high_entropy_files)} 个")

    # 熵值分布统计
    print("\n--- 熵值分布统计 ---")
    if scanned > 0:
        ranges = [(0, 3, "低(正常文本)"), (3, 5, "中低(正常文件)"),
                  (5, 7, "中高(压缩/二进制)"), (7, 7.5, "高(可能加密)"),
                  (7.5, 8, "极高(很可能加密)")]
        # 重新扫描计算分布（简化：使用已收集数据）
        # 实际实现中可以在此循环中累计统计
        print(f"  扫描了 {scanned} 个文件")
        print(f"  高熵值(>{threshold}): {len(high_entropy_files) + len(encrypted_candidates)} 个")
        print(f"  异常比例: {(len(high_entropy_files) + len(encrypted_candidates)) / scanned * 100:.1f}%")

    # 建议
    if encrypted_candidates or (len(high_entropy_files) > 10):
        print("\n[建议] 检测到大量高熵值文件，可能正在发生文件加密")
        print("  1. 立即检查是否有活跃的勒索软件进程")
        print("  2. 检查最近创建的文件（勒索信）")
        print("  3. 断开网络连接并启动事件响应")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python entropy_detector.py <目录路径> [熵值阈值]")
        sys.exit(1)

    directory = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 7.0
    scan_entropy_anomalies(directory, threshold)
```

### 6.3 vssadmin删除行为检测脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vssadmin删除行为检测脚本
分析Windows事件日志，检测卷影副本删除行为
仅用于安全教育和授权研究
"""

import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime


# 可疑命令模式
SUSPICIOUS_COMMANDS = [
    {
        "pattern": r"vssadmin.*delete.*shadow",
        "severity": "极高",
        "description": "vssadmin删除卷影副本（勒索软件常见行为）",
    },
    {
        "pattern": r"wmic.*shadowcopy.*delete",
        "severity": "极高",
        "description": "wmic删除卷影副本",
    },
    {
        "pattern": r"wbadmin.*delete.*catalog",
        "severity": "极高",
        "description": "wbadmin删除备份目录",
    },
    {
        "pattern": r"bcdedit.*safeboot",
        "severity": "高",
        "description": "修改启动配置进入安全模式",
    },
    {
        "pattern": r"bcdedit.*recoveryenabled\s+no",
        "severity": "高",
        "description": "禁用恢复模式",
    },
    {
        "pattern": r"bcdedit.*bootstatuspolicy.*ignore",
        "severity": "高",
        "description": "修改启动状态策略（阻止恢复界面）",
    },
    {
        "pattern": r"vssadmin.*list\s+shadow",
        "severity": "中",
        "description": "枚举卷影副本（勒索软件侦察阶段）",
    },
    {
        "pattern": r"vssadmin.*list\s+writers",
        "severity": "中",
        "description": "枚举VSS写入器（勒索软件侦察阶段）",
    },
]


def parse_sysmon_xml(filepath):
    """解析Sysmon导出的XML事件日志"""
    findings = []

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        print(f"[!] 无法解析XML文件: {filepath}")
        return findings
    except FileNotFoundError:
        print(f"[!] 文件不存在: {filepath}")
        return findings

    # 遍历事件
    for event in root:
        event_data = {}
        ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}

        event_id_elem = event.find('.//ns:EventID', ns)
        if event_id_elem is None:
            continue
        event_id = event_id_elem.text

        # 只处理进程创建事件（Event ID 1）
        if event_id != "1":
            continue

        # 提取EventData
        for data in event.findall('.//ns:Data', ns):
            name = data.get('Name', '')
            value = data.text or ''
            event_data[name] = value

        command_line = event_data.get('CommandLine', '')
        image = event_data.get('Image', '')
        utc_time = event_data.get('UtcTime', '')
        user = event_data.get('User', '')
        parent_image = event_data.get('ParentImage', '')

        if not command_line:
            continue

        # 检查可疑命令
        for rule in SUSPICIOUS_COMMANDS:
            if re.search(rule["pattern"], command_line, re.IGNORECASE):
                findings.append({
                    'time': utc_time,
                    'severity': rule["severity"],
                    'description': rule["description"],
                    'image': image,
                    'command': command_line[:200],
                    'parent': parent_image,
                    'user': user,
                })

    return findings


def parse_evtx_text(filepath):
    """解析文本格式的Windows事件日志（如wevtutil qe导出）"""
    findings = []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # 简化的文本解析：查找包含可疑命令的行
    for rule in SUSPICIOUS_COMMANDS:
        for match in re.finditer(rule["pattern"], content, re.IGNORECASE):
            # 获取上下文
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end].replace('\n', ' ')

            findings.append({
                'time': '未知',
                'severity': rule["severity"],
                'description': rule["description"],
                'image': '未知',
                'command': match.group(0)[:200],
                'parent': '未知',
                'user': '未知',
                'context': context[:200],
            })

    return findings


def analyze_log(filepath):
    """主分析函数"""
    print("=" * 60)
    print(f"卷影副本删除行为检测: {filepath}")
    print("=" * 60)

    # 根据文件类型选择解析方式
    if filepath.lower().endswith('.xml'):
        findings = parse_sysmon_xml(filepath)
    else:
        findings = parse_evtx_text(filepath)

    if not findings:
        print("\n[OK] 未检测到卷影副本删除行为")
        return

    print(f"\n[!] 检测到 {len(findings)} 条可疑事件")

    # 按严重程度排序
    severity_order = {"极高": 0, "高": 1, "中": 2, "低": 3}
    findings.sort(key=lambda x: severity_order.get(x['severity'], 99))

    # 统计
    severity_count = defaultdict(int)
    for f in findings:
        severity_count[f['severity']] += 1

    print("\n--- 严重程度统计 ---")
    for sev in ["极高", "高", "中", "低"]:
        if severity_count[sev]:
            print(f"  {sev}: {severity_count[sev]} 条")

    # 显示详情
    print("\n--- 可疑事件详情 ---")
    for i, f in enumerate(findings[:20]):
        print(f"\n事件 #{i+1}")
        print(f"  严重程度: {f['severity']}")
        print(f"  描述: {f['description']}")
        print(f"  时间: {f['time']}")
        print(f"  进程: {f['image']}")
        print(f"  父进程: {f.get('parent', 'N/A')}")
        print(f"  用户: {f.get('user', 'N/A')}")
        print(f"  命令行: {f['command']}")
        if 'context' in f:
            print(f"  上下文: {f['context']}")

    if len(findings) > 20:
        print(f"\n... 共 {len(findings)} 条事件")

    # 响应建议
    high_count = severity_count.get("极高", 0) + severity_count.get("高", 0)
    if high_count > 0:
        print("\n[紧急] 检测到高危卷影副本删除行为！")
        print("  这通常是勒索软件加密前的防御规避步骤")
        print("  建议：")
        print("  1. 立即排查对应时间点的所有进程行为")
        print("  2. 检查文件系统是否有加密行为")
        print("  3. 检查是否已有勒索信文件出现")
        print("  4. 启动勒索软件应急响应流程")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python vssadmin_detector.py <Sysmon XML日志>")
        print("  python vssadmin_detector.py <文本格式事件日志>")
        print("")
        print("示例:")
        print("  python vssadmin_detector.py sysmon_export.xml")
        print("  python vssadmin_detector.py evtx_text_export.txt")
        sys.exit(1)
    analyze_log(sys.argv[1])
```

---

---

