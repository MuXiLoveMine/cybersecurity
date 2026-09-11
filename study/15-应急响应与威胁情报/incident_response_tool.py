# -*- coding: utf-8 -*-
"""
应急响应辅助工具 (Incident Response Toolkit)
=============================================

功能：
    1. Web 日志分析器 - 分析 Nginx/Apache 访问日志，发现攻击痕迹
    2. 系统日志分析器 - 分析 Windows/Linux 系统日志中的安全事件
    3. 进程分析工具 - 分析进程列表，发现可疑进程
    4. 网络连接分析 - 分析网络连接，发现可疑通信
    5. IOC 匹配检测 - 将日志/进程/网络数据与 IOC 进行匹配
    6. 威胁情报查询模拟 - 模拟查询威胁情报平台
    7. 事件时间线生成 - 根据日志和事件生成时间线

使用方法：
    python incident_response_tool.py --help
    python incident_response_tool.py weblog --file access.log
    python incident_response_tool.py process --file ps.txt
    python incident_response_tool.py network --file netstat.txt
    python incident_response_tool.py ioc --file access.log --ioc iocs.txt
    python incident_response_tool.py timeline --dir ./logs/

作者：应急响应学习工具
版本：1.0
日期：2024-01-01
"""

import os
import re
import sys
import json
import argparse
import hashlib
from datetime import datetime
from collections import Counter, defaultdict
from urllib.parse import urlparse, unquote


# ============================================================
# 配置部分
# ============================================================

# 默认的 IOC 列表（内置一些常见的恶意指标，用于演示）
DEFAULT_IOCS = {
    "ips": [
        "192.168.1.100",
        "10.0.0.55",
        "172.16.0.88",
        "45.33.32.156",  # 示例恶意 IP
        "185.220.101.34",  # Tor 出口节点示例
    ],
    "domains": [
        "malicious-example.com",
        "evil-c2-server.net",
        "phishing-site.org",
        "cryptominer-pool.xyz",
    ],
    "urls": [
        "/admin/login.php",
        "/backdoor/shell.php",
        "/wp-content/uploads/shell.php",
    ],
    "file_hashes": {
        "md5": [
            "d41d8cd98f00b204e9800998ecf8427e",  # 空文件 MD5（示例）
            "e99a18c428cb38d5f260853678922e03",  # 示例 MD5
        ],
        "sha256": [
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # 空文件 SHA256
        ]
    },
    "process_names": [
        "mimikatz.exe",
        "psexec.exe",
        "nc.exe",
        "netcat.exe",
        "reverse_shell.exe",
        "cryptominer.exe",
        "minerd",
        "xmrig",
    ]
}

# SQL 注入特征正则表达式
SQL_INJECTION_PATTERNS = [
    r"(?i)union(\s)+select",
    r"(?i)select.*from",
    r"(?i)insert(\s)+into",
    r"(?i)delete(\s)+from",
    r"(?i)drop(\s)+table",
    r"(?i)update.*set",
    r"(?i)or(\s)+1=1",
    r"(?i)and(\s)+1=1",
    r"(?i)'(\s)+or(\s)+'",
    r"(?i)sleep\s*\(",
    r"(?i)benchmark\s*\(",
    r"(?i)information_schema",
    r"(?i)xp_cmdshell",
    r"(?i)--",
    r"(?i);.*--",
]

# XSS 攻击特征正则表达式
XSS_PATTERNS = [
    r"(?i)<script",
    r"(?i)javascript:",
    r"(?i)onerror\s*=",
    r"(?i)onload\s*=",
    r"(?i)onclick\s*=",
    r"(?i)eval\s*\(",
    r"(?i)alert\s*\(",
    r"(?i)document\.cookie",
    r"(?i)<iframe",
    r"(?i)<img.*onerror",
]

# 命令注入特征正则表达式
COMMAND_INJECTION_PATTERNS = [
    r";\s*(ls|cat|whoami|id|uname|net|wget|curl)",
    r"\|\s*(ls|cat|whoami|id|uname|net|wget|curl)",
    r"`[^`]+`",
    r"\$\([^)]+\)",
    r"(?i)(?:;|&&|\|\||`)\s*(rm|cp|mv|wget|curl|nc|bash|sh)",
]

# 路径遍历特征正则表达式
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"%2e%2e%2f",
    r"%2e%2e/",
    r"\.\.%2f",
    r"/etc/passwd",
    r"/windows/system32",
    r"\\windows\\system32",
]

# Webshell 特征关键词
WEBSHELL_KEYWORDS = [
    "eval(",
    "assert(",
    "system(",
    "exec(",
    "shell_exec(",
    "passthru(",
    "base64_decode",
    "cmd=",
    "pass=",
    "execute",
]


# ============================================================
# 工具类：日志解析器
# ============================================================

class LogParser:
    """日志解析器基类"""

    def __init__(self):
        self.log_entries = []

    def parse(self, log_file):
        """解析日志文件，由子类实现"""
        raise NotImplementedError


class NginxLogParser(LogParser):
    """Nginx 访问日志解析器"""

    # Nginx 默认 combined 日志格式正则
    # 格式：$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
    LOG_PATTERN = re.compile(
        r'(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+'
        r'\[(?P<time>[^\]]+)\]\s+'
        r'"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<protocol>[^"]+)"\s+'
        r'(?P<status>\d+)\s+(?P<size>\d+)\s+'
        r'"(?P<referer>[^"]*)"\s+'
        r'"(?P<user_agent>[^"]*)"'
    )

    def parse(self, log_file):
        """
        解析 Nginx 访问日志

        参数：
            log_file: 日志文件路径

        返回：
            list: 解析后的日志条目列表
        """
        print(f"[*] 正在解析 Nginx 日志: {log_file}")
        self.log_entries = []
        count = 0

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    match = self.LOG_PATTERN.match(line)
                    if match:
                        entry = match.groupdict()
                        # 转换状态码和大小为整数
                        entry['status'] = int(entry['status'])
                        entry['size'] = int(entry['size'])
                        # 解析时间
                        try:
                            # 时间格式: 10/Oct/2000:13:55:36 -0700
                            entry['datetime'] = datetime.strptime(
                                entry['time'].split()[0],
                                '%d/%b/%Y:%H:%M:%S'
                            )
                        except ValueError:
                            entry['datetime'] = None
                        self.log_entries.append(entry)
                        count += 1

            print(f"[+] 成功解析 {count} 条日志记录")
            return self.log_entries

        except FileNotFoundError:
            print(f"[!] 错误：文件不存在 - {log_file}")
            return []
        except Exception as e:
            print(f"[!] 解析日志时出错: {e}")
            return []


# ============================================================
# 功能 1：Web 日志分析器
# ============================================================

class WebLogAnalyzer:
    """
    Web 日志分析器

    功能：
        - 统计访问量 Top IP
        - 检测 SQL 注入攻击
        - 检测 XSS 攻击
        - 检测命令注入
        - 检测路径遍历
        - 检测 Webshell 访问
        - 统计状态码分布
        - 分析扫描器特征
    """

    def __init__(self, log_entries):
        """
        初始化 Web 日志分析器

        参数：
            log_entries: 解析后的日志条目列表
        """
        self.log_entries = log_entries
        self.findings = []  # 发现的安全问题

    def analyze(self):
        """执行完整的 Web 日志分析"""
        print("\n" + "=" * 60)
        print("Web 日志分析报告")
        print("=" * 60)

        # 基本统计
        self._basic_statistics()

        # 攻击检测
        self._detect_sql_injection()
        self._detect_xss()
        self._detect_command_injection()
        self._detect_path_traversal()
        self._detect_webshell_access()
        self._detect_scanner()

        # 输出发现总结
        self._print_findings()

        return self.findings

    def _basic_statistics(self):
        """基本统计信息"""
        print("\n--- 基本统计信息 ---")

        if not self.log_entries:
            print("  没有日志数据")
            return

        # 总请求数
        total_requests = len(self.log_entries)
        print(f"  总请求数: {total_requests}")

        # 独立 IP 数
        unique_ips = len(set(e['ip'] for e in self.log_entries))
        print(f"  独立 IP 数: {unique_ips}")

        # 时间范围
        times = [e['datetime'] for e in self.log_entries if e['datetime']]
        if times:
            print(f"  时间范围: {min(times)} ~ {max(times)}")

        # Top 10 访问 IP
        ip_counter = Counter(e['ip'] for e in self.log_entries)
        print(f"\n  Top 10 访问 IP:")
        for ip, count in ip_counter.most_common(10):
            print(f"    {ip:20s} {count:6d} 次")

        # 状态码分布
        status_counter = Counter(e['status'] for e in self.log_entries)
        print(f"\n  状态码分布:")
        for status, count in sorted(status_counter.items()):
            percentage = (count / total_requests) * 100
            print(f"    {status}: {count:6d} ({percentage:5.2f}%)")

        # Top 10 访问路径
        path_counter = Counter(e['path'].split('?')[0] for e in self.log_entries)
        print(f"\n  Top 10 访问路径:")
        for path, count in path_counter.most_common(10):
            print(f"    {count:6d}  {path}")

    def _detect_sql_injection(self):
        """检测 SQL 注入攻击"""
        print("\n--- SQL 注入检测 ---")

        sql_attack_entries = []
        for entry in self.log_entries:
            # 对 URL 路径和查询参数进行检测
            url_decoded = unquote(entry['path'])
            for pattern in SQL_INJECTION_PATTERNS:
                if re.search(pattern, url_decoded):
                    sql_attack_entries.append(entry)
                    break

        if sql_attack_entries:
            print(f"  [!] 发现 {len(sql_attack_entries)} 条疑似 SQL 注入请求")
            # 按 IP 统计
            ip_counter = Counter(e['ip'] for e in sql_attack_entries)
            print(f"  涉及 {len(ip_counter)} 个 IP 地址")
            for ip, count in ip_counter.most_common(5):
                print(f"    {ip}: {count} 次")

            # 记录发现
            for entry in sql_attack_entries[:10]:  # 最多记录 10 条
                self.findings.append({
                    'type': 'SQL注入',
                    'severity': 'high',
                    'ip': entry['ip'],
                    'path': entry['path'],
                    'time': entry.get('time', 'unknown'),
                    'description': f"疑似 SQL 注入攻击请求"
                })
        else:
            print("  [+] 未发现 SQL 注入攻击痕迹")

    def _detect_xss(self):
        """检测 XSS 攻击"""
        print("\n--- XSS 攻击检测 ---")

        xss_entries = []
        for entry in self.log_entries:
            url_decoded = unquote(entry['path'])
            for pattern in XSS_PATTERNS:
                if re.search(pattern, url_decoded):
                    xss_entries.append(entry)
                    break

        if xss_entries:
            print(f"  [!] 发现 {len(xss_entries)} 条疑似 XSS 请求")
            ip_counter = Counter(e['ip'] for e in xss_entries)
            print(f"  涉及 {len(ip_counter)} 个 IP 地址")

            for entry in xss_entries[:5]:
                self.findings.append({
                    'type': 'XSS',
                    'severity': 'medium',
                    'ip': entry['ip'],
                    'path': entry['path'],
                    'time': entry.get('time', 'unknown'),
                    'description': f"疑似 XSS 攻击请求"
                })
        else:
            print("  [+] 未发现 XSS 攻击痕迹")

    def _detect_command_injection(self):
        """检测命令注入攻击"""
        print("\n--- 命令注入检测 ---")

        cmd_injection_entries = []
        for entry in self.log_entries:
            url_decoded = unquote(entry['path'])
            for pattern in COMMAND_INJECTION_PATTERNS:
                if re.search(pattern, url_decoded):
                    cmd_injection_entries.append(entry)
                    break

        if cmd_injection_entries:
            print(f"  [!] 发现 {len(cmd_injection_entries)} 条疑似命令注入请求")
            ip_counter = Counter(e['ip'] for e in cmd_injection_entries)
            print(f"  涉及 {len(ip_counter)} 个 IP 地址")

            for entry in cmd_injection_entries[:5]:
                self.findings.append({
                    'type': '命令注入',
                    'severity': 'high',
                    'ip': entry['ip'],
                    'path': entry['path'],
                    'time': entry.get('time', 'unknown'),
                    'description': f"疑似命令注入攻击请求"
                })
        else:
            print("  [+] 未发现命令注入攻击痕迹")

    def _detect_path_traversal(self):
        """检测路径遍历攻击"""
        print("\n--- 路径遍历检测 ---")

        traversal_entries = []
        for entry in self.log_entries:
            url_decoded = unquote(entry['path'])
            for pattern in PATH_TRAVERSAL_PATTERNS:
                if re.search(pattern, url_decoded):
                    traversal_entries.append(entry)
                    break

        if traversal_entries:
            print(f"  [!] 发现 {len(traversal_entries)} 条疑似路径遍历请求")
            ip_counter = Counter(e['ip'] for e in traversal_entries)
            print(f"  涉及 {len(ip_counter)} 个 IP 地址")

            for entry in traversal_entries[:5]:
                self.findings.append({
                    'type': '路径遍历',
                    'severity': 'medium',
                    'ip': entry['ip'],
                    'path': entry['path'],
                    'time': entry.get('time', 'unknown'),
                    'description': f"疑似路径遍历攻击请求"
                })
        else:
            print("  [+] 未发现路径遍历攻击痕迹")

    def _detect_webshell_access(self):
        """检测 Webshell 访问"""
        print("\n--- Webshell 访问检测 ---")

        webshell_entries = []
        for entry in self.log_entries:
            url_decoded = unquote(entry['path']).lower()
            # 检测可疑的文件扩展名和路径
            if re.search(r'\.(php|jsp|asp|aspx|sh)$', url_decoded):
                # 进一步检查是否有 Webshell 特征
                for keyword in WEBSHELL_KEYWORDS:
                    if keyword.lower() in url_decoded:
                        webshell_entries.append(entry)
                        break

        if webshell_entries:
            print(f"  [!] 发现 {len(webshell_entries)} 条疑似 Webshell 访问请求")
            ip_counter = Counter(e['ip'] for e in webshell_entries)
            print(f"  涉及 {len(ip_counter)} 个 IP 地址")

            for entry in webshell_entries[:10]:
                self.findings.append({
                    'type': 'Webshell访问',
                    'severity': 'critical',
                    'ip': entry['ip'],
                    'path': entry['path'],
                    'time': entry.get('time', 'unknown'),
                    'description': f"疑似 Webshell 访问"
                })
        else:
            print("  [+] 未发现 Webshell 访问痕迹")

    def _detect_scanner(self):
        """检测扫描器和自动化工具"""
        print("\n--- 扫描器检测 ---")

        # 常见扫描器 User-Agent 特征
        scanner_patterns = [
            r'(?i)sqlmap',
            r'(?i)nmap',
            r'(?i)nikto',
            r'(?i)nessus',
            r'(?i)acunetix',
            r'(?i)appscan',
            r'(?i)burp',
            r'(?i)scanner',
            r'(?i)crawler',
            r'(?i)spider',
            r'(?i)python-requests',
            r'(?i)curl',
            r'(?i)wget',
            r'(?i)httrack',
        ]

        scanner_entries = []
        for entry in self.log_entries:
            user_agent = entry.get('user_agent', '')
            for pattern in scanner_patterns:
                if re.search(pattern, user_agent):
                    scanner_entries.append(entry)
                    break

        # 另一种检测方法：短时间内大量 404 请求
        ip_404_count = defaultdict(int)
        for entry in self.log_entries:
            if entry['status'] == 404:
                ip_404_count[entry['ip']] += 1

        # 超过阈值的判定为扫描（这里阈值设为 50）
        scan_ips = {ip: count for ip, count in ip_404_count.items() if count >= 50}

        if scanner_entries or scan_ips:
            total_scanner = len(set(e['ip'] for e in scanner_entries)) + len(scan_ips)
            print(f"  [!] 发现疑似扫描活动")
            if scanner_entries:
                print(f"    通过 User-Agent 识别: {len(set(e['ip'] for e in scanner_entries))} 个 IP")
            if scan_ips:
                print(f"    通过 404 统计识别: {len(scan_ips)} 个 IP")
                for ip, count in sorted(scan_ips.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"      {ip}: {count} 个 404 请求")
        else:
            print("  [+] 未发现明显的扫描活动")

    def _print_findings(self):
        """打印发现的安全问题总结"""
        print("\n" + "=" * 60)
        print("安全问题总结")
        print("=" * 60)

        if not self.findings:
            print("  [+] 未发现明显的安全问题")
            return

        # 按严重程度统计
        severity_counter = Counter(f['severity'] for f in self.findings)
        print(f"  共发现 {len(self.findings)} 个安全问题")
        for sev in ['critical', 'high', 'medium', 'low']:
            count = severity_counter.get(sev, 0)
            if count > 0:
                print(f"    {sev.upper()}: {count}")

        # 按类型统计
        type_counter = Counter(f['type'] for f in self.findings)
        print(f"\n  按类型分布:")
        for ftype, count in type_counter.most_common():
            print(f"    {ftype}: {count}")

        # 详细列表
        print(f"\n  详细列表 (最多显示 20 条):")
        for i, finding in enumerate(self.findings[:20], 1):
            print(f"    {i:2d}. [{finding['severity'].upper()}] {finding['type']}")
            print(f"        IP: {finding['ip']}")
            print(f"        路径: {finding['path'][:80]}")
            print(f"        时间: {finding['time']}")


# ============================================================
# 功能 2：系统日志分析器
# ============================================================

class SystemLogAnalyzer:
    """
    系统日志分析器

    功能：
        - 分析 Windows 安全事件（登录、进程创建等）
        - 分析 Linux 认证日志
        - 检测暴力破解
        - 检测异常登录
        - 检测可疑进程创建
    """

    def __init__(self):
        self.findings = []

    def analyze_linux_auth_log(self, log_file):
        """
        分析 Linux 认证日志 (/var/log/auth.log 或 /var/log/secure)

        参数：
            log_file: 日志文件路径
        """
        print(f"\n{'=' * 60}")
        print("Linux 认证日志分析")
        print("=" * 60)

        failed_logins = []  # 登录失败记录
        successful_logins = []  # 登录成功记录
        sudo_commands = []  # sudo 命令
        ssh_events = []  # SSH 相关事件

        # SSH 登录失败正则
        ssh_failed_pattern = re.compile(
            r'(?P<time>\w+\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+sshd\[\d+\]:\s+'
            r'Failed password for (invalid user )?(?P<user>\S+) from (?P<ip>\S+) port'
        )

        # SSH 登录成功正则
        ssh_success_pattern = re.compile(
            r'(?P<time>\w+\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+sshd\[\d+\]:\s+'
            r'Accepted \S+ for (?P<user>\S+) from (?P<ip>\S+) port'
        )

        # sudo 命令正则
        sudo_pattern = re.compile(
            r'(?P<time>\w+\s+\d+\s+\d+:\d+:\d+)\s+\S+\s+sudo:\s+'
            r'(?P<user>\S+)\s+.*COMMAND=(?P<command>.+)'
        )

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # 匹配 SSH 登录失败
                    match = ssh_failed_pattern.search(line)
                    if match:
                        failed_logins.append(match.groupdict())
                        continue

                    # 匹配 SSH 登录成功
                    match = ssh_success_pattern.search(line)
                    if match:
                        successful_logins.append(match.groupdict())
                        continue

                    # 匹配 sudo 命令
                    match = sudo_pattern.search(line)
                    if match:
                        sudo_commands.append(match.groupdict())
                        continue

            # 输出统计
            print(f"\n--- 登录统计 ---")
            print(f"  登录成功次数: {len(successful_logins)}")
            print(f"  登录失败次数: {len(failed_logins)}")
            print(f"  sudo 命令执行次数: {len(sudo_commands)}")

            # 登录成功用户统计
            if successful_logins:
                user_counter = Counter(e['user'] for e in successful_logins)
                print(f"\n  登录成功用户 Top 10:")
                for user, count in user_counter.most_common(10):
                    print(f"    {user}: {count} 次")

                # 登录成功 IP 统计
                ip_counter = Counter(e['ip'] for e in successful_logins)
                print(f"\n  登录成功 IP Top 10:")
                for ip, count in ip_counter.most_common(10):
                    print(f"    {ip}: {count} 次")

            # 暴力破解检测
            self._detect_brute_force(failed_logins, successful_logins)

            # 异常时间登录检测
            self._detect_abnormal_time_login(successful_logins)

            # sudo 命令分析
            if sudo_commands:
                print(f"\n--- Sudo 命令分析 ---")
                print(f"  共执行 {len(sudo_commands)} 条 sudo 命令")
                user_counter = Counter(e['user'] for e in sudo_commands)
                print(f"  涉及用户: {list(user_counter.keys())}")
                print(f"  最近 10 条 sudo 命令:")
                for cmd in sudo_commands[-10:]:
                    print(f"    {cmd['time']} {cmd['user']}: {cmd['command'][:80]}")

        except FileNotFoundError:
            print(f"[!] 错误：文件不存在 - {log_file}")
        except Exception as e:
            print(f"[!] 分析日志时出错: {e}")

    def _detect_brute_force(self, failed_logins, successful_logins):
        """检测暴力破解攻击"""
        print(f"\n--- 暴力破解检测 ---")

        if not failed_logins:
            print("  [+] 未发现登录失败记录")
            return

        # 按 IP 统计登录失败次数
        ip_failed_counter = Counter(e['ip'] for e in failed_logins)

        # 阈值：同一 IP 失败超过 10 次判定为暴力破解尝试
        brute_force_ips = {ip: count for ip, count in ip_failed_counter.items() if count >= 10}

        if brute_force_ips:
            print(f"  [!] 发现 {len(brute_force_ips)} 个 IP 存在暴力破解尝试")
            for ip, count in sorted(brute_force_ips.items(), key=lambda x: x[1], reverse=True):
                print(f"    {ip}: {count} 次失败登录")

                # 检查该 IP 是否有登录成功（表示暴力破解成功）
                success_from_ip = [e for e in successful_logins if e['ip'] == ip]
                if success_from_ip:
                    print(f"      ⚠  警告：该 IP 有 {len(success_from_ip)} 次登录成功！")
                    for s in success_from_ip:
                        print(f"        用户: {s['user']}, 时间: {s['time']}")
                        self.findings.append({
                            'type': '暴力破解成功',
                            'severity': 'critical',
                            'ip': ip,
                            'user': s['user'],
                            'time': s['time'],
                            'description': f"暴力破解成功，IP {ip} 以用户 {s['user']} 登录"
                        })

                # 记录发现
                self.findings.append({
                    'type': '暴力破解尝试',
                    'severity': 'high',
                    'ip': ip,
                    'failed_count': count,
                    'description': f"来自 {ip} 的暴力破解尝试，共 {count} 次失败登录"
                })
        else:
            print("  [+] 未发现明显的暴力破解行为")

    def _detect_abnormal_time_login(self, successful_logins):
        """检测异常时间的登录（如凌晨登录）"""
        print(f"\n--- 异常时间登录检测 ---")

        abnormal_logins = []
        for login in successful_logins:
            try:
                # 解析时间（假设格式为 "Oct  1 00:00:00"）
                time_str = login['time'].split()
                if len(time_str) >= 3:
                    hour = int(time_str[2].split(':')[0])
                    # 凌晨 0-5 点的登录判定为异常时间
                    if 0 <= hour < 5:
                        abnormal_logins.append(login)
            except (ValueError, IndexError):
                pass

        if abnormal_logins:
            print(f"  [!] 发现 {len(abnormal_logins)} 次异常时间（凌晨）登录")
            for login in abnormal_logins[:10]:
                print(f"    {login['time']} 用户: {login['user']}, IP: {login['ip']}")
                self.findings.append({
                    'type': '异常时间登录',
                    'severity': 'medium',
                    'ip': login['ip'],
                    'user': login['user'],
                    'time': login['time'],
                    'description': f"凌晨时间登录"
                })
        else:
            print("  [+] 未发现异常时间登录")


# ============================================================
# 功能 3：进程分析工具
# ============================================================

class ProcessAnalyzer:
    """
    进程分析工具

    功能：
        - 分析进程列表
        - 检测可疑进程名
        - 检测异常路径的进程
        - 检测高 CPU/内存占用进程
        - 检测隐藏进程（对比 ps 和 /proc）
    """

    def __init__(self):
        self.findings = []

    def analyze_linux_ps(self, ps_file):
        """
        分析 Linux ps 命令输出

        参数：
            ps_file: ps aux 输出的文件路径
        """
        print(f"\n{'=' * 60}")
        print("Linux 进程分析")
        print("=" * 60)

        processes = []

        try:
            with open(ps_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            if not lines:
                print("  [!] 进程列表为空")
                return

            # 解析 ps aux 输出
            # 格式: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
            header = lines[0].split()
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 10)  # 最多分割 10 次，命令部分保留空格
                if len(parts) >= 11:
                    proc = {
                        'user': parts[0],
                        'pid': int(parts[1]),
                        'cpu': float(parts[2]),
                        'mem': float(parts[3]),
                        'vsz': parts[4],
                        'rss': parts[5],
                        'tty': parts[6],
                        'stat': parts[7],
                        'start': parts[8],
                        'time': parts[9],
                        'command': parts[10]
                    }
                    processes.append(proc)

            print(f"  总进程数: {len(processes)}")

            # 按 CPU 排序
            print(f"\n--- CPU 占用 Top 10 ---")
            sorted_by_cpu = sorted(processes, key=lambda x: x['cpu'], reverse=True)
            for proc in sorted_by_cpu[:10]:
                print(f"  {proc['pid']:6d}  CPU: {proc['cpu']:5.1f}%  "
                      f"MEM: {proc['mem']:5.1f}%  {proc['command'][:60]}")

            # 按内存排序
            print(f"\n--- 内存占用 Top 10 ---")
            sorted_by_mem = sorted(processes, key=lambda x: x['mem'], reverse=True)
            for proc in sorted_by_mem[:10]:
                print(f"  {proc['pid']:6d}  CPU: {proc['cpu']:5.1f}%  "
                      f"MEM: {proc['mem']:5.1f}%  {proc['command'][:60]}")

            # 可疑进程检测
            self._detect_suspicious_processes(processes)

            # 可疑路径检测
            self._detect_suspicious_paths(processes)

            # root 运行的可疑进程
            self._detect_root_suspicious(processes)

        except FileNotFoundError:
            print(f"  [!] 错误：文件不存在 - {ps_file}")
        except Exception as e:
            print(f"  [!] 分析进程时出错: {e}")

    def _detect_suspicious_processes(self, processes):
        """检测可疑进程名"""
        print(f"\n--- 可疑进程名检测 ---")

        suspicious = []
        known_malicious = [name.lower() for name in DEFAULT_IOCS['process_names']]

        for proc in processes:
            # 获取进程名（命令的第一个词）
            proc_name = proc['command'].split()[0].split('/')[-1].lower()

            # 检查是否为已知恶意进程
            if proc_name in known_malicious:
                suspicious.append((proc, '已知恶意进程名'))
                continue

            # 检查随机字符的进程名（常见于挖矿程序）
            if len(proc_name) > 10 and proc_name.isalnum() and proc_name == proc_name.lower():
                # 简单的随机性检测（元音字母比例低）
                vowels = sum(1 for c in proc_name if c in 'aeiou')
                if vowels / len(proc_name) < 0.15 and len(proc_name) >= 8:
                    suspicious.append((proc, '疑似随机命名进程'))
                    continue

            # 检查伪装系统进程（如数字0代替字母o）
            system_processes = ['sshd', 'bash', 'systemd', 'nginx', 'apache', 'mysql']
            for sys_proc in system_processes:
                if sys_proc in proc_name and proc_name != sys_proc:
                    # 检查是否是类似但不同的名字
                    if len(proc_name) == len(sys_proc) and proc_name != sys_proc:
                        suspicious.append((proc, f'疑似伪装 {sys_proc} 进程'))
                        break

        if suspicious:
            print(f"  [!] 发现 {len(suspicious)} 个可疑进程")
            for proc, reason in suspicious:
                print(f"    PID: {proc['pid']:6d}  命令: {proc['command'][:70]}")
                print(f"      原因: {reason}")
                self.findings.append({
                    'type': '可疑进程',
                    'severity': 'high',
                    'pid': proc['pid'],
                    'command': proc['command'],
                    'description': reason
                })
        else:
            print("  [+] 未发现明显的可疑进程")

    def _detect_suspicious_paths(self, processes):
        """检测运行在可疑路径的进程"""
        print(f"\n--- 可疑路径进程检测 ---")

        suspicious_paths = []
        # 可疑的路径前缀
        suspicious_prefixes = [
            '/tmp/',
            '/var/tmp/',
            '/dev/shm/',
            '/run/shm/',
            '/var/www/html/',  # Web 目录下的可执行进程可疑
            '/home/',
        ]

        for proc in processes:
            cmd = proc['command']
            for prefix in suspicious_prefixes:
                if cmd.startswith(prefix) or f' {prefix}' in cmd:
                    suspicious_paths.append((proc, prefix))
                    break

        if suspicious_paths:
            print(f"  [!] 发现 {len(suspicious_paths)} 个运行在可疑路径的进程")
            for proc, path in suspicious_paths[:10]:
                print(f"    PID: {proc['pid']:6d}  路径: {path}")
                print(f"      命令: {proc['command'][:70]}")
                self.findings.append({
                    'type': '可疑路径进程',
                    'severity': 'medium',
                    'pid': proc['pid'],
                    'command': proc['command'],
                    'suspicious_path': path,
                    'description': f'进程运行在可疑路径 {path}'
                })
        else:
            print("  [+] 未发现运行在可疑路径的进程")

    def _detect_root_suspicious(self, processes):
        """检测 root 运行的可疑进程"""
        print(f"\n--- Root 权限可疑进程检测 ---")

        root_processes = [p for p in processes if p['user'] == 'root']
        print(f"  Root 运行的进程数: {len(root_processes)}")

        # 检查常见的非 root 进程是否以 root 运行
        suspicious_root = []
        # 通常不应该以 root 运行的进程名关键词
        non_root_keywords = ['nginx', 'apache', 'httpd', 'mysql', 'redis', 'mongodb', 'node']

        for proc in root_processes:
            proc_name = proc['command'].split()[0].split('/')[-1].lower()
            for keyword in non_root_keywords:
                if keyword in proc_name:
                    # 这些服务的主进程可以是 root，但 worker 进程通常不是
                    # 这里只做提示
                    pass

        # 检查以 root 运行的可疑命令
        suspicious_cmds = ['nc ', 'netcat', 'socat', 'ncat', 'bash -i', 'python -c', 'perl -e']
        for proc in root_processes:
            for cmd in suspicious_cmds:
                if cmd in proc['command'].lower():
                    suspicious_root.append((proc, f'root 执行 {cmd}'))
                    break

        if suspicious_root:
            print(f"  [!] 发现 {len(suspicious_root)} 个 root 运行的可疑进程")
            for proc, reason in suspicious_root[:10]:
                print(f"    PID: {proc['pid']:6d}  {reason}")
                print(f"      命令: {proc['command'][:70]}")
                self.findings.append({
                    'type': 'Root可疑进程',
                    'severity': 'high',
                    'pid': proc['pid'],
                    'command': proc['command'],
                    'description': reason
                })
        else:
            print("  [+] 未发现 root 运行的明显可疑进程")


# ============================================================
# 功能 4：网络连接分析
# ============================================================

class NetworkAnalyzer:
    """
    网络连接分析工具

    功能：
        - 分析网络连接
        - 检测可疑外联
        - 检测异常监听端口
        - 检测已知恶意 IP 连接
        - 统计连接分布
    """

    def __init__(self):
        self.findings = []

    def analyze_netstat(self, netstat_file):
        """
        分析 netstat 输出

        参数：
            netstat_file: netstat -tulnp 或 netstat -ano 输出文件
        """
        print(f"\n{'=' * 60}")
        print("网络连接分析")
        print("=" * 60)

        connections = []

        try:
            with open(netstat_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # 尝试解析 netstat 输出
            for line in lines:
                line = line.strip()
                if not line or line.startswith('Active') or line.startswith('Proto'):
                    continue

                parts = line.split()
                if len(parts) >= 4:
                    # 尝试识别格式
                    if parts[0] in ['tcp', 'tcp6', 'udp', 'udp6']:
                        # Linux netstat 格式
                        conn = self._parse_linux_netstat(parts)
                        if conn:
                            connections.append(conn)

            print(f"  总连接数: {len(connections)}")

            # 统计连接状态
            state_counter = Counter(c['state'] for c in connections if c.get('state'))
            print(f"\n--- 连接状态统计 ---")
            for state, count in state_counter.most_common():
                print(f"    {state}: {count}")

            # 监听端口分析
            listening = [c for c in connections if c['state'] == 'LISTEN']
            print(f"\n--- 监听端口 ({len(listening)} 个) ---")
            for conn in listening[:20]:
                print(f"    {conn['proto']:6s} {conn['local']:30s} {conn.get('pid', 'N/A')}")

            # 建立的连接分析
            established = [c for c in connections if c['state'] == 'ESTABLISHED']
            print(f"\n--- 已建立连接 ({len(established)} 个) ---")
            for conn in established[:20]:
                print(f"    {conn['proto']:6s} {conn['local']:25s} ↔ {conn['remote']:25s}")

            # 可疑连接检测
            self._detect_suspicious_connections(connections)

            # 外联统计
            self._analyze_external_connections(connections)

        except FileNotFoundError:
            print(f"  [!] 错误：文件不存在 - {netstat_file}")
        except Exception as e:
            print(f"  [!] 分析网络连接时出错: {e}")

    def _parse_linux_netstat(self, parts):
        """解析 Linux netstat 输出行"""
        try:
            proto = parts[0]
            recv_q = parts[1]
            send_q = parts[2]
            local = parts[3]
            remote = parts[4]
            state = parts[5] if len(parts) > 5 else ''
            pid = parts[-1] if len(parts) > 6 else ''

            return {
                'proto': proto,
                'local': local,
                'remote': remote,
                'state': state,
                'pid': pid
            }
        except (IndexError, ValueError):
            return None

    def _detect_suspicious_connections(self, connections):
        """检测可疑网络连接"""
        print(f"\n--- 可疑连接检测 ---")

        malicious_ip_matches = []
        suspicious_ports = []
        suspicious_outbound = []

        # 已知恶意端口
        known_malicious_ports = [
            4444,  # Metasploit 默认
            5555,  # 常见后门端口
            6666,  # 常见后门端口
            7777,  # 常见后门端口
            8888,  # 常见后门端口
            31337,  # Elite/后门
            44443,  # 常见 C2
            44444,  # 常见 C2
        ]

        # 可疑的出站端口（非常用端口）
        common_outbound_ports = {80, 443, 53, 8080, 8443, 22, 25, 465, 587, 110, 995, 143, 993}

        for conn in connections:
            if conn['state'] == 'ESTABLISHED':
                # 提取远程 IP 和端口
                remote_parts = conn['remote'].rsplit(':', 1)
                if len(remote_parts) == 2:
                    remote_ip = remote_parts[0]
                    try:
                        remote_port = int(remote_parts[1])
                    except ValueError:
                        remote_port = 0

                    # 检测恶意 IP
                    if remote_ip in DEFAULT_IOCS['ips']:
                        malicious_ip_matches.append(conn)

                    # 检测可疑端口
                    if remote_port in known_malicious_ports:
                        suspicious_ports.append((conn, remote_port))

                    # 检测非常用出站端口
                    if remote_port not in common_outbound_ports and remote_port > 1024:
                        # 排除内网 IP
                        if not self._is_private_ip(remote_ip):
                            suspicious_outbound.append((conn, remote_port))

        # 输出结果
        if malicious_ip_matches:
            print(f"  [!] 发现 {len(malicious_ip_matches)} 个连接到已知恶意 IP")
            for conn in malicious_ip_matches:
                print(f"    {conn['local']} ↔ {conn['remote']}")
                self.findings.append({
                    'type': '恶意IP连接',
                    'severity': 'critical',
                    'local': conn['local'],
                    'remote': conn['remote'],
                    'description': f"连接到已知恶意 IP {conn['remote']}"
                })
        else:
            print("  [+] 未发现连接到已知恶意 IP")

        if suspicious_ports:
            print(f"  [!] 发现 {len(suspicious_ports)} 个连接到可疑端口")
            for conn, port in suspicious_ports[:10]:
                print(f"    端口 {port}: {conn['local']} ↔ {conn['remote']}")
                self.findings.append({
                    'type': '可疑端口连接',
                    'severity': 'high',
                    'local': conn['local'],
                    'remote': conn['remote'],
                    'port': port,
                    'description': f"连接到可疑端口 {port}"
                })

        if suspicious_outbound:
            print(f"  [!] 发现 {len(suspicious_outbound)} 个非常用端口出站连接")
            for conn, port in suspicious_outbound[:10]:
                print(f"    端口 {port}: {conn['local']} ↔ {conn['remote']}")
                self.findings.append({
                    'type': '异常出站连接',
                    'severity': 'medium',
                    'local': conn['local'],
                    'remote': conn['remote'],
                    'port': port,
                    'description': f"出站连接到非常用端口 {port}"
                })

    def _analyze_external_connections(self, connections):
        """分析外联连接"""
        print(f"\n--- 外联连接统计 ---")

        external_connections = []
        for conn in connections:
            if conn['state'] == 'ESTABLISHED':
                remote_ip = conn['remote'].rsplit(':', 1)[0]
                if not self._is_private_ip(remote_ip):
                    external_connections.append(conn)

        if external_connections:
            print(f"  外联连接总数: {len(external_connections)}")

            # 统计外联 IP
            remote_ips = Counter(c['remote'].rsplit(':', 1)[0] for c in external_connections)
            print(f"  外联 IP 数: {len(remote_ips)}")
            print(f"  Top 10 外联 IP:")
            for ip, count in remote_ips.most_common(10):
                print(f"    {ip}: {count} 个连接")
        else:
            print("  无外联连接")

    def _is_private_ip(self, ip):
        """判断是否为内网 IP"""
        # 简化判断，实际应使用 ipaddress 模块
        if ip.startswith('10.'):
            return True
        if ip.startswith('172.16.') or ip.startswith('172.17.') or ip.startswith('172.18.') or \
           ip.startswith('172.19.') or ip.startswith('172.2') or ip.startswith('172.30.') or \
           ip.startswith('172.31.'):
            return True
        if ip.startswith('192.168.'):
            return True
        if ip == '127.0.0.1' or ip == '::1':
            return True
        return False


# ============================================================
# 功能 5：IOC 匹配检测
# ============================================================

class IOCChecker:
    """
    IOC 匹配检测器

    功能：
        - 加载 IOC 列表
        - 在日志/网络/进程数据中匹配 IOC
        - 输出匹配结果
        - 支持多种 IOC 类型（IP、域名、URL、哈希）
    """

    def __init__(self, ioc_file=None):
        """
        初始化 IOC 检测器

        参数：
            ioc_file: IOC 文件路径，如果为 None 则使用默认 IOC
        """
        self.iocs = self._load_iocs(ioc_file)
        self.matches = []

    def _load_iocs(self, ioc_file):
        """加载 IOC 列表"""
        if ioc_file and os.path.exists(ioc_file):
            print(f"[*] 从文件加载 IOC: {ioc_file}")
            iocs = {
                'ips': [],
                'domains': [],
                'urls': [],
                'md5': [],
                'sha256': [],
            }

            try:
                with open(ioc_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        # 格式: type:value
                        if ':' in line:
                            ioc_type, value = line.split(':', 1)
                            ioc_type = ioc_type.lower().strip()
                            value = value.strip()
                            if ioc_type in iocs:
                                iocs[ioc_type].append(value)
                            elif ioc_type == 'ip':
                                iocs['ips'].append(value)
                            elif ioc_type == 'domain':
                                iocs['domains'].append(value)
                            elif ioc_type == 'url':
                                iocs['urls'].append(value)
                        else:
                            # 自动判断类型
                            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', line):
                                iocs['ips'].append(line)
                            elif '.' in line and '/' not in line:
                                iocs['domains'].append(line)
                            elif '/' in line:
                                iocs['urls'].append(line)

                total = sum(len(v) for v in iocs.values())
                print(f"[+] 加载了 {total} 个 IOC")
                return iocs

            except Exception as e:
                print(f"[!] 加载 IOC 文件失败: {e}，使用默认 IOC")
                return DEFAULT_IOCS
        else:
            print("[*] 使用默认 IOC 列表")
            return DEFAULT_IOCS

    def check_web_log(self, log_entries):
        """
        在 Web 日志中匹配 IOC

        参数：
            log_entries: 解析后的日志条目列表
        """
        print(f"\n{'=' * 60}")
        print("IOC 匹配检测 - Web 日志")
        print("=" * 60)

        ip_iocs = set(self.iocs.get('ips', []))
        url_iocs = set(self.iocs.get('urls', []))

        ip_matches = []
        url_matches = []

        for entry in log_entries:
            # IP 匹配
            if entry['ip'] in ip_iocs:
                ip_matches.append(entry)

            # URL 路径匹配
            path = entry['path']
            for url_ioc in url_iocs:
                if url_ioc in path:
                    url_matches.append(entry)
                    break

        # 输出结果
        total_matches = len(set(ip_matches + url_matches))
        print(f"\n  匹配到的 IOC 总数: {total_matches}")

        if ip_matches:
            print(f"\n  [!] IP 匹配: {len(ip_matches)} 条")
            unique_ips = set(e['ip'] for e in ip_matches)
            print(f"    涉及 IP: {', '.join(unique_ips)}")
            for entry in ip_matches[:5]:
                print(f"    {entry['time']} {entry['ip']} {entry['path'][:60]}")
                self.matches.append({
                    'type': 'IP匹配',
                    'severity': 'critical',
                    'ioc': entry['ip'],
                    'context': f"{entry['time']} {entry['path']}",
                    'description': f"日志中匹配到恶意 IP {entry['ip']}"
                })

        if url_matches:
            print(f"\n  [!] URL 匹配: {len(url_matches)} 条")
            for entry in url_matches[:5]:
                print(f"    {entry['time']} {entry['ip']} {entry['path'][:60]}")
                self.matches.append({
                    'type': 'URL匹配',
                    'severity': 'high',
                    'ioc': entry['path'],
                    'context': f"IP: {entry['ip']}, 时间: {entry['time']}",
                    'description': f"日志中匹配到恶意 URL"
                })

        if not ip_matches and not url_matches:
            print("  [+] 未匹配到 IOC")

        return self.matches

    def check_network_connections(self, connections):
        """
        在网络连接中匹配 IOC

        参数：
            connections: 网络连接列表
        """
        print(f"\n{'=' * 60}")
        print("IOC 匹配检测 - 网络连接")
        print("=" * 60)

        ip_iocs = set(self.iocs.get('ips', []))
        matches = []

        for conn in connections:
            remote_ip = conn['remote'].rsplit(':', 1)[0]
            if remote_ip in ip_iocs:
                matches.append(conn)

        if matches:
            print(f"\n  [!] 发现 {len(matches)} 个连接匹配恶意 IP IOC")
            for conn in matches:
                print(f"    {conn['local']} ↔ {conn['remote']}")
                self.matches.append({
                    'type': '网络IP匹配',
                    'severity': 'critical',
                    'ioc': conn['remote'],
                    'context': conn['local'],
                    'description': f"网络连接到已知恶意 IP {conn['remote']}"
                })
        else:
            print("  [+] 网络连接中未匹配到 IOC")

        return self.matches


# ============================================================
# 功能 6：威胁情报查询模拟
# ============================================================

class ThreatIntelSimulator:
    """
    威胁情报查询模拟器

    功能：
        - 模拟查询 IP 信誉
        - 模拟查询域名信息
        - 模拟查询文件哈希
        - 模拟查询威胁情报
        - 返回模拟的威胁情报结果

    说明：
        这是一个模拟器，使用内置的示例数据演示威胁情报查询功能。
        实际使用时需要接入真实的威胁情报 API。
    """

    def __init__(self):
        # 模拟的威胁情报数据库
        self.intel_db = {
            'ips': {
                '45.33.32.156': {
                    'reputation': 'malicious',
                    'malware_families': ['Emotet', 'TrickBot'],
                    'first_seen': '2023-01-15',
                    'last_seen': '2024-01-10',
                    'country': 'US',
                    'asn': 'AS7018',
                    'tags': ['C2', 'botnet', 'spam'],
                    'confidence': 'high',
                    'related_actors': ['APT-XX', 'CyberCrime-Group-A']
                },
                '185.220.101.34': {
                    'reputation': 'suspicious',
                    'malware_families': [],
                    'first_seen': '2022-06-01',
                    'last_seen': '2024-01-15',
                    'country': 'DE',
                    'asn': 'AS200012',
                    'tags': ['Tor-exit', 'anonymous'],
                    'confidence': 'medium',
                    'related_actors': []
                },
                '192.168.1.100': {
                    'reputation': 'internal',
                    'malware_families': [],
                    'tags': ['internal-ip'],
                    'confidence': 'high',
                    'description': '内网 IP 地址'
                }
            },
            'domains': {
                'malicious-example.com': {
                    'reputation': 'malicious',
                    'malware_families': ['Emotet'],
                    'first_seen': '2023-12-01',
                    'last_seen': '2024-01-15',
                    'registrar': 'Example Registrar',
                    'created': '2023-11-15',
                    'tags': ['phishing', 'C2'],
                    'confidence': 'high',
                    'related_ips': ['45.33.32.156'],
                    'related_actors': ['CyberCrime-Group-A']
                },
                'evil-c2-server.net': {
                    'reputation': 'malicious',
                    'malware_families': ['CobaltStrike'],
                    'first_seen': '2023-09-01',
                    'last_seen': '2024-01-10',
                    'registrar': 'Another Registrar',
                    'created': '2023-08-20',
                    'tags': ['C2', 'cobalt-strike'],
                    'confidence': 'high',
                    'related_ips': ['1.2.3.4'],
                    'related_actors': ['APT-YY']
                }
            },
            'hashes': {
                'd41d8cd98f00b204e9800998ecf8427e': {
                    'reputation': 'unknown',
                    'file_type': 'text/plain',
                    'file_size': 0,
                    'detection_rate': '0/70',
                    'tags': ['empty-file'],
                    'confidence': 'low',
                    'description': '空文件 MD5（示例）'
                }
            },
            'actors': {
                'APT-XX': {
                    'name': 'APT-XX',
                    'type': 'nation-state',
                    'origin': 'Country X',
                    'motivation': 'espionage',
                    'first_seen': '2015',
                    'targets': ['government', 'defense', 'technology'],
                    'ttps': ['spear-phishing', 'watering-hole', 'zero-day'],
                    'tools': ['Custom-Malware-A', 'CobaltStrike'],
                    'confidence': 'high'
                },
                'CyberCrime-Group-A': {
                    'name': 'CyberCrime-Group-A',
                    'type': 'cyber-crime',
                    'origin': 'Eastern Europe',
                    'motivation': 'financial',
                    'first_seen': '2018',
                    'targets': ['finance', 'retail'],
                    'ttps': ['phishing', 'malware', 'ransomware'],
                    'tools': ['Emotet', 'TrickBot', 'Ryuk'],
                    'confidence': 'high'
                }
            }
        }

    def query_ip(self, ip_address):
        """
        查询 IP 地址的威胁情报

        参数：
            ip_address: IP 地址

        返回：
            dict: 威胁情报信息
        """
        print(f"\n{'=' * 60}")
        print(f"威胁情报查询 - IP: {ip_address}")
        print("=" * 60)

        # 从模拟数据库查询
        intel = self.intel_db['ips'].get(ip_address)

        if intel:
            print(f"\n  信誉: {intel['reputation']}")
            print(f"  置信度: {intel['confidence']}")
            if intel.get('country'):
                print(f"  国家: {intel['country']}")
            if intel.get('asn'):
                print(f"  ASN: {intel['asn']}")
            if intel.get('first_seen'):
                print(f"  首次发现: {intel['first_seen']}")
            if intel.get('last_seen'):
                print(f"  最近发现: {intel['last_seen']}")
            if intel.get('malware_families'):
                print(f"  关联恶意软件: {', '.join(intel['malware_families'])}")
            if intel.get('tags'):
                print(f"  标签: {', '.join(intel['tags'])}")
            if intel.get('related_actors'):
                print(f"  关联攻击者: {', '.join(intel['related_actors'])}")
            if intel.get('description'):
                print(f"  描述: {intel['description']}")
        else:
            # 未知 IP，生成模拟的基础信息
            print(f"\n  信誉: unknown")
            print(f"  置信度: low")
            print(f"  说明: 该 IP 未在威胁情报库中找到记录")
            print(f"  建议: 进一步分析该 IP 的行为特征")

        return intel

    def query_domain(self, domain):
        """
        查询域名的威胁情报

        参数：
            domain: 域名

        返回：
            dict: 威胁情报信息
        """
        print(f"\n{'=' * 60}")
        print(f"威胁情报查询 - 域名: {domain}")
        print("=" * 60)

        intel = self.intel_db['domains'].get(domain)

        if intel:
            print(f"\n  信誉: {intel['reputation']}")
            print(f"  置信度: {intel['confidence']}")
            print(f"  注册商: {intel.get('registrar', 'N/A')}")
            print(f"  创建时间: {intel.get('created', 'N/A')}")
            print(f"  首次发现: {intel.get('first_seen', 'N/A')}")
            print(f"  最近发现: {intel.get('last_seen', 'N/A')}")
            if intel.get('malware_families'):
                print(f"  关联恶意软件: {', '.join(intel['malware_families'])}")
            if intel.get('tags'):
                print(f"  标签: {', '.join(intel['tags'])}")
            if intel.get('related_ips'):
                print(f"  关联 IP: {', '.join(intel['related_ips'])}")
            if intel.get('related_actors'):
                print(f"  关联攻击者: {', '.join(intel['related_actors'])}")
        else:
            print(f"\n  信誉: unknown")
            print(f"  置信度: low")
            print(f"  说明: 该域名未在威胁情报库中找到记录")

        return intel

    def query_hash(self, file_hash):
        """
        查询文件哈希的威胁情报

        参数：
            file_hash: 文件哈希（MD5/SHA1/SHA256）

        返回：
            dict: 威胁情报信息
        """
        print(f"\n{'=' * 60}")
        print(f"威胁情报查询 - 文件哈希: {file_hash}")
        print("=" * 60)

        intel = self.intel_db['hashes'].get(file_hash)

        if intel:
            print(f"\n  信誉: {intel['reputation']}")
            print(f"  文件类型: {intel.get('file_type', 'N/A')}")
            print(f"  文件大小: {intel.get('file_size', 'N/A')}")
            print(f"  检测率: {intel.get('detection_rate', 'N/A')}")
            if intel.get('tags'):
                print(f"  标签: {', '.join(intel['tags'])}")
            if intel.get('description'):
                print(f"  描述: {intel['description']}")
        else:
            print(f"\n  信誉: unknown")
            print(f"  置信度: low")
            print(f"  说明: 该哈希未在威胁情报库中找到记录")
            print(f"  建议: 使用沙箱或多引擎扫描进一步分析")

        return intel

    def query_actor(self, actor_name):
        """
        查询攻击者/威胁组织信息

        参数：
            actor_name: 攻击者名称

        返回：
            dict: 攻击者信息
        """
        print(f"\n{'=' * 60}")
        print(f"威胁情报查询 - 攻击者: {actor_name}")
        print("=" * 60)

        intel = self.intel_db['actors'].get(actor_name)

        if intel:
            print(f"\n  名称: {intel['name']}")
            print(f"  类型: {intel['type']}")
            print(f"  来源: {intel['origin']}")
            print(f"  动机: {intel['motivation']}")
            print(f"  首次发现: {intel['first_seen']}")
            print(f"  目标行业: {', '.join(intel['targets'])}")
            print(f"  攻击手法 (TTP): {', '.join(intel['ttps'])}")
            print(f"  使用工具: {', '.join(intel['tools'])}")
            print(f"  置信度: {intel['confidence']}")
        else:
            print(f"\n  未找到该攻击者的详细信息")
            print(f"  建议: 搜索威胁情报平台获取更多信息")

        return intel


# ============================================================
# 功能 7：事件时间线生成器
# ============================================================

class TimelineGenerator:
    """
    事件时间线生成器

    功能：
        - 从多种日志中提取事件
        - 按时间排序生成时间线
        - 标注关键事件
        - 输出可视化时间线
        - 生成时间线报告
    """

    def __init__(self):
        self.events = []

    def add_events(self, events, source='unknown'):
        """
        添加事件到时间线

        参数：
            events: 事件列表，每个事件包含 time、type、description 等字段
            source: 事件来源（如 'nginx-log', 'auth-log'）
        """
        for event in events:
            event['source'] = source
            self.events.append(event)

    def generate_timeline(self, output_file=None):
        """
        生成时间线

        参数：
            output_file: 输出文件路径，如果为 None 则打印到屏幕
        """
        print(f"\n{'=' * 60}")
        print("事件时间线")
        print("=" * 60)

        if not self.events:
            print("  没有事件数据")
            return

        # 按时间排序
        sorted_events = sorted(self.events, key=lambda x: x.get('time', ''))

        # 生成时间线文本
        timeline_lines = []
        timeline_lines.append("=" * 70)
        timeline_lines.append("事件时间线")
        timeline_lines.append("=" * 70)
        timeline_lines.append(f"总事件数: {len(sorted_events)}")
        timeline_lines.append("")

        # 按严重程度标记
        severity_marks = {
            'critical': '[!!!]',
            'high': '[!!]',
            'medium': '[!]',
            'low': '[i]',
            'info': '[i]',
        }

        for i, event in enumerate(sorted_events, 1):
            time_str = event.get('time', 'unknown')
            event_type = event.get('type', 'unknown')
            severity = event.get('severity', 'info')
            description = event.get('description', '')
            source = event.get('source', 'unknown')
            mark = severity_marks.get(severity, '[i]')

            line = f"{i:4d}. {mark} {time_str} | {event_type:15s} | {description[:60]}"
            timeline_lines.append(line)

            if event.get('ip'):
                timeline_lines.append(f"      IP: {event['ip']}")
            if event.get('source'):
                timeline_lines.append(f"      来源: {source}")

        timeline_lines.append("")
        timeline_lines.append("=" * 70)
        timeline_lines.append("图例:")
        timeline_lines.append("  [!!!] Critical - 严重")
        timeline_lines.append("  [!!]  High     - 高危")
        timeline_lines.append("  [!]   Medium   - 中危")
        timeline_lines.append("  [i]   Info     - 信息")
        timeline_lines.append("=" * 70)

        # 输出
        timeline_text = '\n'.join(timeline_lines)
        print(timeline_text)

        # 保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(timeline_text)
                print(f"\n[+] 时间线已保存到: {output_file}")
            except Exception as e:
                print(f"\n[!] 保存时间线失败: {e}")

        return sorted_events

    def generate_from_logs(self, log_dir, output_file=None):
        """
        从日志目录生成时间线（简化版本）

        参数：
            log_dir: 日志目录
            output_file: 输出文件
        """
        print(f"\n[*] 从目录 {log_dir} 收集日志事件...")

        # 扫描目录中的日志文件
        if not os.path.isdir(log_dir):
            print(f"[!] 目录不存在: {log_dir}")
            return

        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if not os.path.isfile(filepath):
                continue

            # 根据文件名判断日志类型并解析
            if 'access' in filename.lower() or 'nginx' in filename.lower():
                print(f"  处理 Web 日志: {filename}")
                parser = NginxLogParser()
                entries = parser.parse(filepath)
                if entries:
                    # 将日志转换为事件
                    for entry in entries:
                        self.events.append({
                            'time': entry.get('time', ''),
                            'type': 'web-access',
                            'severity': 'info',
                            'ip': entry.get('ip', ''),
                            'description': f"{entry['method']} {entry['path'][:50]} - {entry['status']}",
                            'source': filename
                        })

            elif 'auth' in filename.lower() or 'secure' in filename.lower():
                print(f"  处理认证日志: {filename}")
                # 这里可以调用 SystemLogAnalyzer 来提取事件
                # 简化处理，直接读取
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            if 'Failed password' in line:
                                self.events.append({
                                    'time': line[:15],
                                    'type': 'auth-failure',
                                    'severity': 'medium',
                                    'description': line.strip()[:80],
                                    'source': filename
                                })
                            elif 'Accepted' in line:
                                self.events.append({
                                    'time': line[:15],
                                    'type': 'auth-success',
                                    'severity': 'info',
                                    'description': line.strip()[:80],
                                    'source': filename
                                })
                except Exception as e:
                    print(f"    处理出错: {e}")

        print(f"[+] 共收集 {len(self.events)} 个事件")

        # 生成时间线
        return self.generate_timeline(output_file)


# ============================================================
# 主函数：命令行接口
# ============================================================

def main():
    """主函数：解析命令行参数并执行相应功能"""

    parser = argparse.ArgumentParser(
        description='应急响应辅助工具 (Incident Response Toolkit)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析 Web 访问日志
  python incident_response_tool.py weblog --file access.log

  # 分析 Linux 认证日志
  python incident_response_tool.py syslog --file auth.log

  # 分析进程列表
  python incident_response_tool.py process --file ps_aux.txt

  # 分析网络连接
  python incident_response_tool.py network --file netstat.txt

  # IOC 匹配检测（Web 日志）
  python incident_response_tool.py ioc --file access.log --ioc iocs.txt

  # 查询威胁情报
  python incident_response_tool.py intel --type ip --value 45.33.32.156
  python incident_response_tool.py intel --type domain --value malicious-example.com

  # 生成事件时间线
  python incident_response_tool.py timeline --dir ./logs/ --output timeline.txt

  # 运行所有分析（完整应急响应分析）
  python incident_response_tool.py full --weblog access.log --authlog auth.log --psfile ps.txt --netfile netstat.txt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # --- Web 日志分析 ---
    weblog_parser = subparsers.add_parser('weblog', help='Web 日志分析')
    weblog_parser.add_argument('--file', required=True, help='Web 访问日志文件路径')
    weblog_parser.add_argument('--format', default='nginx', choices=['nginx', 'apache'],
                               help='日志格式 (默认: nginx)')

    # --- 系统日志分析 ---
    syslog_parser = subparsers.add_parser('syslog', help='系统日志分析')
    syslog_parser.add_argument('--file', required=True, help='系统日志文件路径')
    syslog_parser.add_argument('--type', default='linux-auth',
                               choices=['linux-auth', 'windows-security'],
                               help='日志类型 (默认: linux-auth)')

    # --- 进程分析 ---
    process_parser = subparsers.add_parser('process', help='进程分析')
    process_parser.add_argument('--file', required=True, help='进程列表文件路径')
    process_parser.add_argument('--os', default='linux', choices=['linux', 'windows'],
                                help='操作系统类型 (默认: linux)')

    # --- 网络连接分析 ---
    network_parser = subparsers.add_parser('network', help='网络连接分析')
    network_parser.add_argument('--file', required=True, help='网络连接文件路径')
    network_parser.add_argument('--os', default='linux', choices=['linux', 'windows'],
                                help='操作系统类型 (默认: linux)')

    # --- IOC 匹配 ---
    ioc_parser = subparsers.add_parser('ioc', help='IOC 匹配检测')
    ioc_parser.add_argument('--file', required=True, help='要检测的文件路径（日志/网络等）')
    ioc_parser.add_argument('--ioc', help='IOC 文件路径（可选，不指定则使用默认 IOC）')
    ioc_parser.add_argument('--type', default='weblog', choices=['weblog', 'network', 'process'],
                            help='文件类型 (默认: weblog)')

    # --- 威胁情报查询 ---
    intel_parser = subparsers.add_parser('intel', help='威胁情报查询（模拟）')
    intel_parser.add_argument('--type', required=True,
                              choices=['ip', 'domain', 'hash', 'actor'],
                              help='查询类型')
    intel_parser.add_argument('--value', required=True, help='要查询的值')

    # --- 时间线生成 ---
    timeline_parser = subparsers.add_parser('timeline', help='事件时间线生成')
    timeline_parser.add_argument('--dir', help='日志目录路径')
    timeline_parser.add_argument('--output', help='输出文件路径')

    # --- 完整分析 ---
    full_parser = subparsers.add_parser('full', help='完整应急响应分析')
    full_parser.add_argument('--weblog', help='Web 访问日志')
    full_parser.add_argument('--authlog', help='认证日志')
    full_parser.add_argument('--psfile', help='进程列表文件')
    full_parser.add_argument('--netfile', help='网络连接文件')
    full_parser.add_argument('--ioc', help='IOC 文件')
    full_parser.add_argument('--report', help='报告输出文件')

    args = parser.parse_args()

    # 打印欢迎信息
    print("=" * 60)
    print("应急响应辅助工具 v1.0")
    print("Incident Response Toolkit")
    print("=" * 60)

    if not args.command:
        parser.print_help()
        return

    # --- 处理 Web 日志分析 ---
    if args.command == 'weblog':
        parser_obj = NginxLogParser()
        entries = parser_obj.parse(args.file)
        if entries:
            analyzer = WebLogAnalyzer(entries)
            analyzer.analyze()

    # --- 处理系统日志分析 ---
    elif args.command == 'syslog':
        analyzer = SystemLogAnalyzer()
        if args.type == 'linux-auth':
            analyzer.analyze_linux_auth_log(args.file)

    # --- 处理进程分析 ---
    elif args.command == 'process':
        analyzer = ProcessAnalyzer()
        if args.os == 'linux':
            analyzer.analyze_linux_ps(args.file)

    # --- 处理网络连接分析 ---
    elif args.command == 'network':
        analyzer = NetworkAnalyzer()
        if args.os == 'linux':
            analyzer.analyze_netstat(args.file)

    # --- 处理 IOC 匹配 ---
    elif args.command == 'ioc':
        checker = IOCChecker(args.ioc)

        if args.type == 'weblog':
            log_parser = NginxLogParser()
            entries = log_parser.parse(args.file)
            if entries:
                checker.check_web_log(entries)

        elif args.type == 'network':
            # 简化处理，实际需要解析网络连接文件
            print("网络连接 IOC 匹配需要先解析网络连接文件")

    # --- 处理威胁情报查询 ---
    elif args.command == 'intel':
        intel = ThreatIntelSimulator()

        if args.type == 'ip':
            intel.query_ip(args.value)
        elif args.type == 'domain':
            intel.query_domain(args.value)
        elif args.type == 'hash':
            intel.query_hash(args.value)
        elif args.type == 'actor':
            intel.query_actor(args.value)

    # --- 处理时间线生成 ---
    elif args.command == 'timeline':
        timeline = TimelineGenerator()
        if args.dir:
            timeline.generate_from_logs(args.dir, args.output)
        else:
            print("请指定 --dir 参数")

    # --- 处理完整分析 ---
    elif args.command == 'full':
        print("\n[*] 开始完整应急响应分析...\n")
        all_findings = []

        # Web 日志分析
        if args.weblog and os.path.exists(args.weblog):
            log_parser = NginxLogParser()
            entries = log_parser.parse(args.weblog)
            if entries:
                weblog_analyzer = WebLogAnalyzer(entries)
                weblog_analyzer.analyze()
                all_findings.extend(weblog_analyzer.findings)

                # IOC 匹配
                ioc_checker = IOCChecker(args.ioc)
                ioc_checker.check_web_log(entries)
                all_findings.extend(ioc_checker.matches)

        # 认证日志分析
        if args.authlog and os.path.exists(args.authlog):
            syslog_analyzer = SystemLogAnalyzer()
            syslog_analyzer.analyze_linux_auth_log(args.authlog)
            all_findings.extend(syslog_analyzer.findings)

        # 进程分析
        if args.psfile and os.path.exists(args.psfile):
            proc_analyzer = ProcessAnalyzer()
            proc_analyzer.analyze_linux_ps(args.psfile)
            all_findings.extend(proc_analyzer.findings)

        # 网络分析
        if args.netfile and os.path.exists(args.netfile):
            net_analyzer = NetworkAnalyzer()
            net_analyzer.analyze_netstat(args.netfile)
            all_findings.extend(net_analyzer.findings)

        # 输出总结
        print("\n" + "=" * 60)
        print("完整分析总结")
        print("=" * 60)
        print(f"共发现 {len(all_findings)} 个安全问题")

        if all_findings:
            severity_counter = Counter(f.get('severity', 'info') for f in all_findings)
            for sev in ['critical', 'high', 'medium', 'low', 'info']:
                count = severity_counter.get(sev, 0)
                if count > 0:
                    print(f"  {sev.upper()}: {count}")

            type_counter = Counter(f.get('type', 'unknown') for f in all_findings)
            print(f"\n按类型分布:")
            for ftype, count in type_counter.most_common():
                print(f"  {ftype}: {count}")

        # 生成报告
        if args.report:
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("应急响应分析报告")
            report_lines.append("=" * 60)
            report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"发现问题总数: {len(all_findings)}")
            report_lines.append("")
            report_lines.append("详细问题列表:")
            report_lines.append("-" * 60)
            for i, finding in enumerate(all_findings, 1):
                report_lines.append(f"{i}. [{finding.get('severity', 'info').upper()}] {finding.get('type', 'unknown')}")
                report_lines.append(f"   描述: {finding.get('description', '')}")
                if finding.get('ip'):
                    report_lines.append(f"   IP: {finding['ip']}")
                report_lines.append("")

            report_text = '\n'.join(report_lines)
            try:
                with open(args.report, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\n[+] 分析报告已保存到: {args.report}")
            except Exception as e:
                print(f"\n[!] 保存报告失败: {e}")

    print("\n[*] 分析完成")


if __name__ == '__main__':
    main()
