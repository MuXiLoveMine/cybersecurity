# Python恶意代码分析辅助脚本

### 6.1 PE文件结构分析脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PE文件结构分析工具
解析PE文件的关键结构，输出分析报告
依赖：pip install pefile
仅用于授权安全研究和教育学习
"""

import pefile
import sys
import math
from collections import defaultdict


def calculate_entropy(data):
    """计算数据熵值（衡量随机性/加密程度）"""
    if not data:
        return 0.0
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def analyze_pe(filepath):
    """分析PE文件结构"""
    try:
        pe = pefile.PE(filepath)
    except pefile.PEFormatError:
        print(f"[!] {filepath} 不是有效的PE文件")
        return

    print("=" * 60)
    print(f"PE文件分析报告: {filepath}")
    print("=" * 60)

    # --- DOS头 ---
    print("\n[1] DOS头")
    print(f"  MZ签名: {'有效' if pe.DOS_HEADER.e_magic == 0x5A4D else '无效'}")
    print(f"  PE头偏移(e_lfanew): 0x{pe.DOS_HEADER.e_lfanew:08X}")

    # --- 文件头 ---
    print("\n[2] 文件头")
    machine_map = {0x14C: "x86", 0x8664: "x64", 0xAA64: "ARM64"}
    machine = machine_map.get(pe.FILE_HEADER.Machine, f"未知(0x{pe.FILE_HEADER.Machine:X})")
    print(f"  架构: {machine}")
    print(f"  节数量: {pe.FILE_HEADER.NumberOfSections}")
    timestamp = pe.FILE_HEADER.TimeDateStamp
    print(f"  时间戳: 0x{timestamp:08X}")

    # --- 节信息 ---
    print("\n[3] 节信息")
    print(f"  {'节名':<10} {'虚拟地址':>10} {'虚拟大小':>10} {'原始大小':>10} {'熵值':>8} {'属性':>10}")
    for section in pe.sections:
        name = section.Name.rstrip(b'\x00').decode('ascii', errors='replace')
        entropy = calculate_entropy(section.get_data())
        flags = []
        if section.Characteristics & 0x20000000: flags.append("X")
        if section.Characteristics & 0x40000000: flags.append("R")
        if section.Characteristics & 0x80000000: flags.append("W")
        flag_str = "|".join(flags)
        print(f"  {name:<10} 0x{section.VirtualAddress:08X} {section.Misc_VirtualSize:8d} "
              f"{section.SizeOfRawData:8d} {entropy:8.4f} {flag_str:>10}")

        # 高熵值节可能被加密/加壳
        if entropy > 7.0:
            print(f"    [!] 节'{name}'熵值极高({entropy:.2f})，可能被加密或加壳")
        # 可写且可执行的节
        if (section.Characteristics & 0x20000000 and
            section.Characteristics & 0x80000000):
            print(f"    [!] 节'{name}'同时可写可执行，可疑（可能自修改代码）")

    # --- 入口点 ---
    print("\n[4] 入口点")
    print(f"  OEP(AddressOfEntryPoint): 0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:08X}")
    print(f"  镜像基址(ImageBase): 0x{pe.OPTIONAL_HEADER.ImageBase:08X}")

    # --- TLS回调 ---
    print("\n[5] TLS回调函数")
    if hasattr(pe, 'DIRECTORY_ENTRY_TLS') and pe.DIRECTORY_ENTRY_TLS:
        tls = pe.DIRECTORY_ENTRY_TLS.struct
        print(f"  TLS回调地址: 0x{tls.AddressOfCallBacks:08X}")
        print("  [!] 存在TLS回调，可能在OEP前执行代码（反调试常见）")
    else:
        print("  无TLS目录")

    # --- 整体熵值 ---
    print("\n[6] 整体文件熵值")
    with open(filepath, 'rb') as f:
        data = f.read()
    overall_entropy = calculate_entropy(data)
    print(f"  整体熵值: {overall_entropy:.4f}")
    if overall_entropy > 7.5:
        print("  [!] 整体熵值极高，文件可能被加壳或加密")
    elif overall_entropy > 6.5:
        print("  [!] 熵值偏高，可能经过压缩")

    pe.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python pe_analyzer.py <PE文件路径>")
        sys.exit(1)
    analyze_pe(sys.argv[1])
```

### 6.2 导入表提取与可疑API检测脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入表提取与可疑API检测工具
提取PE文件的导入表，检测可疑API组合模式
依赖：pip install pefile
仅用于授权安全研究和教育学习
"""

import pefile
import sys
from collections import defaultdict


# 可疑API分类规则
SUSPICIOUS_APIS = {
    "进程注入": [
        "CreateRemoteThread", "CreateRemoteThreadEx",
        "VirtualAllocEx", "VirtualProtectEx",
        "WriteProcessMemory", "ReadProcessMemory",
        "QueueUserAPC", "NtUnmapViewOfSection",
        "SetThreadContext", "GetThreadContext",
    ],
    "进程操作": [
        "CreateProcess", "CreateProcessA", "CreateProcessW",
        "OpenProcess", "TerminateProcess", "CreateThread",
    ],
    "内存操作": [
        "VirtualAlloc", "VirtualProtect", "VirtualFree",
        "HeapAlloc", "RtlMoveMemory", "memcpy",
    ],
    "文件操作": [
        "CreateFile", "CreateFileA", "CreateFileW",
        "WriteFile", "ReadFile", "DeleteFile",
        "CopyFile", "MoveFile", "FindFirstFile", "FindNextFile",
        "CreateFileMapping", "MapViewOfFile",
    ],
    "注册表操作": [
        "RegOpenKeyEx", "RegOpenKeyExA", "RegOpenKeyExW",
        "RegSetValueEx", "RegSetValueExA", "RegSetValueExW",
        "RegCreateKeyEx", "RegDeleteKey", "RegDeleteValue",
        "RegQueryValueEx", "RegEnumKey", "RegEnumValue",
    ],
    "网络通信": [
        "InternetOpen", "InternetOpenUrl", "InternetConnect",
        "HttpOpenRequest", "HttpSendRequest", "InternetReadFile",
        "WinHttpOpen", "WinHttpConnect", "WinHttpOpenRequest",
        "WSAStartup", "socket", "connect", "send", "recv",
    ],
    "反调试": [
        "IsDebuggerPresent", "CheckRemoteDebuggerPresent",
        "NtQueryInformationProcess", "NtSetInformationThread",
        "GetTickCount", "GetTickCount64", "QueryPerformanceCounter",
        "OutputDebugString", "NtClose",
    ],
    "权限操作": [
        "OpenProcessToken", "OpenThreadToken",
        "AdjustTokenPrivileges", "LookupPrivilegeValue",
        "ImpersonateLoggedOnUser", "SetThreadToken",
    ],
    "加密操作": [
        "CryptEncrypt", "CryptDecrypt", "CryptGenKey",
        "CryptImportKey", "CryptExportKey", "CryptDeriveKey",
        "BCryptEncrypt", "BCryptDecrypt", "BCryptGenerateSymmetricKey",
    ],
    "服务操作": [
        "CreateService", "CreateServiceA", "CreateServiceW",
        "StartService", "StartServiceA", "StartServiceW",
        "ChangeServiceConfig", "DeleteService",
    ],
    "动态加载": [
        "LoadLibrary", "LoadLibraryA", "LoadLibraryW",
        "LoadLibraryEx", "LoadLibraryExA", "LoadLibraryExW",
        "GetProcAddress", "LdrLoadDll",
    ],
}

# 行为模式检测规则
BEHAVIOR_PATTERNS = {
    "DLL注入（经典）": {
        "apis": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread"],
        "min_match": 3,
    },
    "进程镂空（Hollowing）": {
        "apis": ["CreateProcess", "ZwUnmapViewOfSection", "VirtualAllocEx",
                 "WriteProcessMemory", "SetThreadContext", "ResumeThread"],
        "min_match": 4,
    },
    "勒索软件加密": {
        "apis": ["FindFirstFile", "FindNextFile", "CryptEncrypt", "CryptGenKey",
                 "WriteFile", "DeleteFile"],
        "min_match": 4,
    },
    "反调试+反沙箱": {
        "apis": ["IsDebuggerPresent", "GetTickCount", "Sleep", "FindWindow"],
        "min_match": 3,
    },
    "C2通信（HTTP）": {
        "apis": ["InternetConnect", "HttpOpenRequest", "HttpSendRequest",
                 "InternetReadFile"],
        "min_match": 3,
    },
    "权限提升": {
        "apis": ["OpenProcessToken", "AdjustTokenPrivileges", "LookupPrivilegeValue"],
        "min_match": 2,
    },
}


def analyze_imports(filepath):
    """分析PE文件导入表"""
    try:
        pe = pefile.PE(filepath)
    except pefile.PEFormatError:
        print(f"[!] {filepath} 不是有效的PE文件")
        return

    print("=" * 60)
    print(f"导入表分析报告: {filepath}")
    print("=" * 60)

    if not hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
        print("[!] 未找到导入表（可能被加壳）")
        pe.close()
        return

    # 收集所有导入函数
    all_imports = []
    imports_by_dll = defaultdict(list)

    print("\n[1] 导入的DLL和函数")
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll_name = entry.dll.decode('ascii', errors='replace')
        funcs = []
        for func in entry.imports:
            if func.name:
                fname = func.name.decode('ascii', errors='replace')
                funcs.append(fname)
                all_imports.append(fname)
        imports_by_dll[dll_name] = funcs
        print(f"\n  {dll_name} ({len(funcs)}个函数)")
        for f in funcs:
            print(f"    - {f}")

    # 可疑API检测
    print("\n[2] 可疑API检测")
    found_suspicious = defaultdict(list)
    for category, api_list in SUSPICIOUS_APIS.items():
        for api in api_list:
            for imp in all_imports:
                if api.lower() in imp.lower():
                    found_suspicious[category].append(imp)

    if found_suspicious:
        for category, apis in found_suspicious.items():
            print(f"\n  [{category}]")
            for api in set(apis):
                print(f"    {api}")
    else:
        print("  未发现可疑API")

    # 行为模式检测
    print("\n[3] 行为模式推断")
    api_set = set(a.lower() for a in all_imports)
    for pattern_name, rule in BEHAVIOR_PATTERNS.items():
        matches = [a for a in rule["apis"] if a.lower() in api_set]
        if len(matches) >= rule["min_match"]:
            print(f"\n  [!] 可能行为: {pattern_name}")
            print(f"      匹配API({len(matches)}/{len(rule['apis'])}): {', '.join(matches)}")

    pe.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python import_analyzer.py <PE文件路径>")
        sys.exit(1)
    analyze_imports(sys.argv[1])
```

### 6.3 字符串提取与IOC匹配脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字符串提取与IOC匹配工具
从二进制文件中提取字符串，自动匹配IP/域名/URL/注册表路径等IOC
仅用于授权安全研究和教育学习
"""

import re
import sys
import base64
from collections import defaultdict


# IOC正则规则
IOC_PATTERNS = {
    "IPv4地址": re.compile(r'\b(\d{1,3}\.){3}\d{1,3}\b'),
    "URL": re.compile(r'https?://[^\s<>"\']+', re.IGNORECASE),
    "域名": re.compile(
        r'\b([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.'
        r'(com|net|org|io|ru|cn|tk|info|biz|xyz|top|onion))\b',
        re.IGNORECASE
    ),
    "注册表路径": re.compile(
        r'(HKLM|HKCU|HKEY_LOCAL_MACHINE|HKEY_CURRENT_USER)\\[^\s\'"]+',
        re.IGNORECASE
    ),
    "文件路径": re.compile(r'[A-Za-z]:\\[^\s\'"<>\|]{2,}'),
    "互斥体名": re.compile(r'(Global|Local)\\[^\s\'"]+', re.IGNORECASE),
    "Base64编码": re.compile(r'[A-Za-z0-9+/]{40,}={0,2}'),
    "比特币地址": re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
    "邮箱地址": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "洋葱地址": re.compile(r'\b[a-z2-7]{16,56}\.onion\b', re.IGNORECASE),
    "GUID": re.compile(
        r'\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}'
        r'-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?'
    ),
}

# 可疑关键词
SUSPICIOUS_KEYWORDS = [
    "IsDebuggerPresent", "CheckRemoteDebuggerPresent",
    "VirtualAlloc", "CreateRemoteThread", "WriteProcessMemory",
    "VirtualProtect", "LoadLibrary", "GetProcAddress",
    "cmd.exe", "powershell", "vssadmin", "bcdedit", "wbadmin",
    "netsh", "schtasks", "sc create", "wmic",
    "bitcoin", "ransom", "decrypt", "encrypt",
    "Tor", ".onion", "Mutex",
    "svchost.exe", "explorer.exe",  # 进程注入目标
    "AppData", "Temp", "ProgramData",
    "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
]


def extract_strings(filepath, min_length=4):
    """从二进制文件提取ASCII和Unicode字符串"""
    with open(filepath, 'rb') as f:
        data = f.read()

    # ASCII字符串
    ascii_strings = re.findall(b'[\x20-\x7e]{%d,}' % min_length, data)
    ascii_strings = [s.decode('ascii', errors='replace') for s in ascii_strings]

    # Unicode(UTF-16LE)字符串
    unicode_pattern = re.compile(
        b'(?:[\x20-\x7e]\x00){%d,}' % min_length
    )
    unicode_strings = unicode_pattern.findall(data)
    unicode_strings = [
        s.decode('utf-16-le', errors='replace').strip('\x00')
        for s in unicode_strings
    ]

    return ascii_strings + unicode_strings


def match_iocs(strings):
    """匹配IOC模式"""
    results = defaultdict(set)
    for s in strings:
        for ioc_type, pattern in IOC_PATTERNS.items():
            matches = pattern.findall(s)
            for m in matches:
                if isinstance(m, tuple):
                    m = m[0] if isinstance(m[0], str) else ''.join(m)
                # 排除明显误报
                if ioc_type == "IPv4地址" and m.startswith(("0.0.", "127.0", "255.255")):
                    continue
                if ioc_type == "文件路径" and m.startswith("0."):
                    continue
                results[ioc_type].add(m)
    return results


def try_base64_decode(strings):
    """尝试解码Base64字符串"""
    decoded = []
    for s in strings:
        for match in IOC_PATTERNS["Base64编码"].findall(s):
            if len(match) >= 40:
                try:
                    decoded_text = base64.b64decode(match).decode('utf-8', errors='replace')
                    # 检查解码后是否包含有意义的文本
                    if any(c.isalpha() for c in decoded_text) and len(decoded_text) > 5:
                        decoded.append((match[:40] + "...", decoded_text[:80]))
                except Exception:
                    pass
    return decoded


def match_keywords(strings):
    """匹配可疑关键词"""
    found = defaultdict(list)
    for kw in SUSPICIOUS_KEYWORDS:
        for s in strings:
            if kw.lower() in s.lower():
                found[kw].append(s[:120])
    return found


def analyze_file(filepath):
    """主分析函数"""
    print("=" * 60)
    print(f"字符串与IOC分析报告: {filepath}")
    print("=" * 60)

    strings = extract_strings(filepath)
    print(f"\n[0] 提取到 {len(strings)} 个字符串")

    # IOC匹配
    print("\n[1] IOC匹配结果")
    iocs = match_iocs(strings)
    for ioc_type, values in iocs.items():
        if values:
            print(f"\n  [{ioc_type}] ({len(values)}个)")
            for v in sorted(values)[:20]:  # 每类最多显示20个
                print(f"    {v}")
            if len(values) > 20:
                print(f"    ... 还有 {len(values) - 20} 个")

    # Base64解码
    print("\n[2] Base64解码尝试")
    decoded = try_base64_decode(strings)
    if decoded:
        for encoded, text in decoded[:10]:
            print(f"  {encoded}")
            print(f"    → {text}")
    else:
        print("  未发现可解码的Base64字符串")

    # 可疑关键词
    print("\n[3] 可疑关键词匹配")
    keywords = match_keywords(strings)
    if keywords:
        for kw, contexts in keywords.items():
            print(f"\n  [{kw}] ({len(contexts)}处)")
            for ctx in contexts[:3]:
                print(f"    {ctx}")
    else:
        print("  未发现可疑关键词")

    # 综合判断
    print("\n[4] 综合判断")
    risk_factors = []
    if iocs.get("IPv4地址"):
        risk_factors.append("包含IP地址（可能为C2）")
    if iocs.get("URL"):
        risk_factors.append("包含URL（可能为C2或下载地址）")
    if iocs.get("域名"):
        risk_factors.append("包含域名（可能为C2）")
    if iocs.get("注册表路径"):
        risk_factors.append("包含注册表路径（可能持久化）")
    if iocs.get("洋葱地址"):
        risk_factors.append("包含.onion地址（Tor通信）")
    if iocs.get("比特币地址"):
        risk_factors.append("包含比特币地址（可能为勒索软件）")
    if any(kw in keywords for kw in ["IsDebuggerPresent", "CreateRemoteThread"]):
        risk_factors.append("包含反调试/注入相关关键词")
    if any(kw in keywords for kw in ["vssadmin", "bcdedit", "wbadmin"]):
        risk_factors.append("包含影子副本删除命令（可能为勒索软件）")

    if risk_factors:
        for f in risk_factors:
            print(f"  [!] {f}")
    else:
        print("  未发现明显风险因素")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python string_ioc_analyzer.py <文件路径>")
        sys.exit(1)
    analyze_file(sys.argv[1])
```

### 6.4 简易行为分析日志解析脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为分析日志解析工具
解析ProcMon CSV日志或Sysmon日志，提取关键行为摘要
仅用于授权安全研究和教育学习
"""

import csv
import sys
import json
from collections import defaultdict, Counter


def parse_procmon_csv(filepath):
    """解析ProcMon导出的CSV日志"""
    print("=" * 60)
    print(f"ProcMon日志分析报告: {filepath}")
    print("=" * 60)

    file_ops = []
    reg_ops = []
    proc_ops = []
    net_ops = []

    with open(filepath, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            operation = row.get('Operation', '')
            path = row.get('Path', '')
            process = row.get('Process Name', '')
            detail = row.get('Detail', '')

            entry = {'process': process, 'path': path, 'detail': detail[:200]}

            if 'File' in operation or operation in ['CreateFile', 'WriteFile',
                    'ReadFile', 'DeleteFile', 'FindFirstFile', 'FindNextFile',
                    'SetFileAttributes', 'RenameFile']:
                file_ops.append(entry)
            elif 'Reg' in operation:
                reg_ops.append(entry)
            elif 'Process' in operation or 'Thread' in operation:
                proc_ops.append(entry)
            elif 'TCP' in operation or 'UDP' in operation or 'Socket' in operation:
                net_ops.append(entry)

    # 文件操作摘要
    print(f"\n[1] 文件操作 ({len(file_ops)}条)")
    write_ops = [e for e in file_ops if 'Write' in e.get('detail', '') or 'WriteFile' in str(e)]
    delete_ops = [e for e in file_ops if 'Delete' in str(e)]
    print(f"  写操作: {len(write_ops)}")
    print(f"  删除操作: {len(delete_ops)}")
    if delete_ops:
        print("  删除的文件:")
        for e in delete_ops[:10]:
            print(f"    {e['path']}")

    # 注册表操作摘要
    print(f"\n[2] 注册表操作 ({len(reg_ops)}条)")
    set_ops = [e for e in reg_ops if 'SetValue' in str(e.get('detail', '')) or 'RegSet' in str(e)]
    print(f"  写入操作: {len(set_ops)}")
    # 持久化位置检查
    persistence_paths = [
        "Run\\", "RunOnce\\", "Services\\", "Winlogon\\",
        "Image File Execution Options\\", "Userinit"
    ]
    persistence_ops = [e for e in reg_ops if any(p in e['path'] for p in persistence_paths)]
    if persistence_ops:
        print("  [!] 持久化相关注册表操作:")
        for e in persistence_ops[:10]:
            print(f"    {e['path']}")

    # 进程操作摘要
    print(f"\n[3] 进程操作 ({len(proc_ops)}条)")
    create_procs = [e for e in proc_ops if 'Create' in str(e.get('detail', ''))]
    if create_procs:
        print(f"  进程创建: {len(create_procs)}")
        for e in create_procs[:10]:
            print(f"    {e['path']} - {e['detail'][:80]}")

    # 网络操作摘要
    print(f"\n[4] 网络操作 ({len(net_ops)}条)")
    for e in net_ops[:10]:
        print(f"    {e['path']} - {e['detail'][:80]}")

    # 行为模式检测
    print("\n[5] 行为模式检测")
    patterns = []
    if delete_ops and any('shadow' in e['path'].lower() for e in delete_ops):
        patterns.append("影子副本删除（勒索软件特征）")
    if persistence_ops:
        patterns.append("注册表持久化")
    if any('.exe' in e['path'].lower() for e in write_ops):
        patterns.append("释放可执行文件")
    if net_ops:
        patterns.append("网络通信")

    for p in patterns:
        print(f"  [!] {p}")

    # 统计
    print("\n[6] 操作统计")
    all_ops = file_ops + reg_ops + proc_ops + net_ops
    process_counter = Counter(e['process'] for e in all_ops)
    for proc, count in process_counter.most_common(5):
        print(f"  {proc}: {count}次操作")


def parse_sysmon_jsonl(filepath):
    """解析Sysmon JSONL格式日志"""
    print("=" * 60)
    print(f"Sysmon日志分析报告: {filepath}")
    print("=" * 60)

    events = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # 按Event ID分类
    event_types = {1: "进程创建", 3: "网络连接", 7: "镜像加载",
                   8: "远程线程创建", 10: "进程访问",
                   11: "文件创建", 12/13/14: "注册表",
                   22: "DNS查询"}

    print(f"\n总事件数: {len(events)}")
    id_counter = Counter(e.get('EventID') for e in events)
    for eid, count in id_counter.most_common():
        name = event_types.get(eid, f"EventID {eid}")
        print(f"  {name}: {count}")

    # 进程创建事件分析
    proc_creates = [e for e in events if e.get('EventID') == 1]
    if proc_creates:
        print(f"\n[1] 进程创建事件 ({len(proc_creates)}条)")
        for e in proc_creates[:15]:
            image = e.get('Image', 'N/A')
            cmd = e.get('CommandLine', 'N/A')
            parent = e.get('ParentImage', 'N/A')
            print(f"  进程: {image}")
            print(f"  命令行: {cmd[:100]}")
            print(f"  父进程: {parent}")
            print()

    # 网络连接分析
    net_conns = [e for e in events if e.get('EventID') == 3]
    if net_conns:
        print(f"\n[2] 网络连接事件 ({len(net_conns)}条)")
        dest_ips = Counter(e.get('DestinationIp') for e in net_conns)
        for ip, count in dest_ips.most_common(10):
            ports = [e.get('DestinationPort') for e in net_conns if e.get('DestinationIp') == ip]
            print(f"  {ip} (端口{set(ports)}, {count}次)")

    # 远程线程创建（注入检测）
    remote_threads = [e for e in events if e.get('EventID') == 8]
    if remote_threads:
        print(f"\n[3] 远程线程创建 ({len(remote_threads)}条) - 可疑注入行为")
        for e in remote_threads[:10]:
            print(f"  源: {e.get('SourceImage', 'N/A')}")
            print(f"  目标: {e.get('TargetImage', 'N/A')}")
            print(f"  函数: {e.get('StartFunction', 'N/A')}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python log_parser.py procmon <ProcMon CSV文件>")
        print("  python log_parser.py sysmon <Sysmon JSONL文件>")
        sys.exit(1)

    log_type = sys.argv[1]
    filepath = sys.argv[2]

    if log_type == "procmon":
        parse_procmon_csv(filepath)
    elif log_type == "sysmon":
        parse_sysmon_jsonl(filepath)
    else:
        print(f"[!] 未知日志类型: {log_type}")
        sys.exit(1)
```

---

---

