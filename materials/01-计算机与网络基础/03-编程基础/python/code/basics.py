#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
basics.py —— Python 基础语法示例（安全从业者视角）

涵盖内容：
  1. 数据类型（字符串、列表、字典、元组、集合）
  2. 控制流（if/elif/else、for、while）
  3. 函数（参数、返回值、文档字符串）
  4. 文件操作（文本、JSON、CSV）
  5. 异常处理（try/except/finally）
  6. 类与对象（面向对象基础）
  7. 正则表达式（re 模块）
  8. 命令行参数（argparse）

运行方式：
  python basics.py

注意：本文件用于学习和参考，可以直接运行查看输出。
"""

import os
import json
import csv
import re
import argparse


# ============================================================
# 1. 数据类型
# ============================================================

def demo_data_types():
    """数据类型示例：字符串、列表、字典、集合"""
    print("=" * 60)
    print("【1. 数据类型】")
    print("=" * 60)

    # ----- 字符串 -----
    print("\n1.1 字符串")
    ip = "192.168.1.100"
    print(f"  IP 地址: {ip}")
    print(f"  转大写: {ip.upper()}")  # 字符串方法
    print(f"  以 192 开头: {ip.startswith('192')}")
    print(f"  分割成四段: {ip.split('.')}")

    # f-string 格式化（安全脚本中常用）
    port = 443
    url = f"https://{ip}:{port}/api"
    print(f"  构造 URL: {url}")

    # ----- 列表 -----
    print("\n1.2 列表")
    ip_list = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.1"]
    print(f"  IP 列表: {ip_list}")
    print(f"  长度: {len(ip_list)}")
    print(f"  第一个: {ip_list[0]}")
    print(f"  包含 10.0.0.2? {'10.0.0.2' in ip_list}")

    # 遍历列表
    print("  遍历列表:")
    for i, ip_addr in enumerate(ip_list, 1):
        print(f"    [{i}] {ip_addr}")

    # ----- 字典 -----
    print("\n1.3 字典")
    vuln_info = {
        "cve": "CVE-2024-12345",
        "severity": "high",
        "cvss": 8.9,
        "port": 8080,
        "affected": True
    }
    print(f"  漏洞信息: {vuln_info}")
    print(f"  CVE 编号: {vuln_info['cve']}")
    print(f"  严重程度: {vuln_info.get('severity', 'unknown')}")

    # 遍历字典
    print("  遍历键值对:")
    for key, value in vuln_info.items():
        print(f"    {key}: {value}")

    # ----- 集合（去重神器）-----
    print("\n1.4 集合（去重）")
    ioc_list = ["1.1.1.1", "2.2.2.2", "1.1.1.1", "3.3.3.3", "2.2.2.2"]
    ioc_set = set(ioc_list)
    print(f"  原始列表: {ioc_list}")
    print(f"  去重后: {ioc_set}")

    # 集合运算（安全中常用：白名单过滤）
    whitelist = {"2.2.2.2", "5.5.5.5"}
    malicious = ioc_set - whitelist  # 差集：去掉白名单后的
    print(f"  白名单: {whitelist}")
    print(f"  去掉白名单后的恶意 IOC: {malicious}")


# ============================================================
# 2. 控制流
# ============================================================

def demo_control_flow():
    """控制流示例：条件判断、循环"""
    print("\n" + "=" * 60)
    print("【2. 控制流】")
    print("=" * 60)

    # ----- 条件判断 -----
    print("\n2.1 条件判断")
    severity = "high"

    if severity == "critical":
        print("  严重等级：致命 → 立即处置")
    elif severity == "high":
        print("  严重等级：高危 → 24 小时内处置")
    elif severity == "medium":
        print("  严重等级：中危 → 计划处置")
    elif severity == "low":
        print("  严重等级：低危 → 择机处置")
    else:
        print(f"  未知等级：{severity}")

    # 多条件判断
    score = 85
    has_poc = True
    if score >= 90 and has_poc:
        print("  高危且有 POC：最高优先级")
    elif score >= 70 or has_poc:
        print("  较高优先级")
    else:
        print("  普通优先级")

    # ----- for 循环 -----
    print("\n2.2 for 循环")
    ports = [21, 22, 23, 25, 53, 80, 443, 3306, 8080]
    print(f"  扫描端口列表: {ports}")

    open_count = 0
    for port in ports:
        # 模拟端口检测（这里用简单的偶数模拟"开放"）
        is_open = port % 2 == 0 or port == 22
        status = "open" if is_open else "closed"
        if is_open:
            open_count += 1
        print(f"    端口 {port:>5}: {status}")

    print(f"  共发现 {open_count} 个开放端口")

    # ----- while 循环 -----
    print("\n2.3 while 循环")
    count = 0
    max_attempts = 3
    while count < max_attempts:
        print(f"  第 {count + 1} 次重试...")
        count += 1
    print(f"  已达到最大重试次数 {max_attempts}")


# ============================================================
# 3. 函数
# ============================================================

def validate_ip(ip_str):
    """验证 IP 地址格式是否正确（简化版）

    Args:
        ip_str: 要验证的 IP 地址字符串

    Returns:
        bool: 格式正确返回 True，否则返回 False

    示例:
        >>> validate_ip("192.168.1.1")
        True
        >>> validate_ip("999.999.999.999")
        False
    """
    parts = ip_str.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True


def calculate_hash(text, algorithm="sha256"):
    """计算字符串的哈希值

    Args:
        text: 要计算哈希的字符串
        algorithm: 哈希算法，支持 md5、sha1、sha256

    Returns:
        str: 十六进制格式的哈希值
    """
    import hashlib

    text_bytes = text.encode("utf-8")

    if algorithm.lower() == "md5":
        return hashlib.md5(text_bytes).hexdigest()
    elif algorithm.lower() == "sha1":
        return hashlib.sha1(text_bytes).hexdigest()
    elif algorithm.lower() == "sha256":
        return hashlib.sha256(text_bytes).hexdigest()
    else:
        raise ValueError(f"不支持的算法: {algorithm}")


def demo_functions():
    """函数示例"""
    print("\n" + "=" * 60)
    print("【3. 函数】")
    print("=" * 60)

    print("\n3.1 IP 地址验证")
    test_ips = ["192.168.1.1", "10.0.0.1", "256.1.1.1", "abc", "1.2.3"]
    for ip in test_ips:
        result = validate_ip(ip)
        print(f"  {ip:>15}: {'✓ 有效' if result else '✗ 无效'}")

    print("\n3.2 哈希计算")
    test_text = "password123"
    for algo in ["md5", "sha1", "sha256"]:
        h = calculate_hash(test_text, algo)
        print(f"  {algo:>8}('{test_text}') = {h}")


# ============================================================
# 4. 文件操作
# ============================================================

def demo_file_operations():
    """文件操作示例：文本、JSON、CSV"""
    print("\n" + "=" * 60)
    print("【4. 文件操作】")
    print("=" * 60)

    # 确保输出目录存在
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    # ----- 文本文件 -----
    print("\n4.1 文本文件读写")
    txt_path = os.path.join(output_dir, "sample_log.txt")

    # 写入
    sample_logs = [
        "192.168.1.100 - - [10/Oct/2024:10:00:01 +0800] \"GET /index.html HTTP/1.1\" 200 1234",
        "192.168.1.101 - - [10/Oct/2024:10:00:02 +0800] \"POST /login HTTP/1.1\" 200 567",
        "10.0.0.5 - - [10/Oct/2024:10:00:03 +0800] \"GET /admin HTTP/1.1\" 403 89",
        "192.168.1.100 - - [10/Oct/2024:10:00:04 +0800] \"GET /api/users HTTP/1.1\" 200 2345",
        "10.0.0.5 - - [10/Oct/2024:10:00:05 +0800] \"POST /admin/login HTTP/1.1\" 401 45",
    ]
    with open(txt_path, "w", encoding="utf-8") as f:
        for line in sample_logs:
            f.write(line + "\n")
    print(f"  已写入示例日志: {txt_path}")

    # 读取并统计
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        print(f"  读取到 {len(lines)} 行日志")

        # 统计 4xx 状态码
        error_count = 0
        for line in lines:
            # 简单提取状态码（HTTP 状态码在引号后的第三个字段）
            parts = line.split('"')
            if len(parts) >= 2:
                status_part = parts[2].strip().split()
                if status_part and status_part[0].startswith("4"):
                    error_count += 1
        print(f"  4xx 错误请求数: {error_count}")

    # ----- JSON -----
    print("\n4.2 JSON 读写")
    json_path = os.path.join(output_dir, "scan_result.json")

    scan_data = {
        "target": "192.168.1.100",
        "scan_time": "2024-10-10T10:00:00",
        "open_ports": [22, 80, 443, 8080],
        "vulnerabilities": [
            {"id": "CVE-2024-1234", "severity": "high", "port": 8080},
            {"id": "CVE-2024-5678", "severity": "medium", "port": 80}
        ],
        "summary": {
            "total_ports": 1000,
            "open_ports": 4,
            "vuln_count": 2
        }
    }

    # 写入 JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scan_data, f, indent=2, ensure_ascii=False)
    print(f"  已写入 JSON: {json_path}")

    # 读取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  目标: {data['target']}")
    print(f"  开放端口: {data['open_ports']}")
    print(f"  漏洞数量: {data['summary']['vuln_count']}")

    # ----- CSV -----
    print("\n4.3 CSV 读写")
    csv_path = os.path.join(output_dir, "vuln_report.csv")

    # 写入 CSV
    vuln_rows = [
        {"IP": "192.168.1.100", "Port": 8080, "CVE": "CVE-2024-1234", "Severity": "high"},
        {"IP": "192.168.1.100", "Port": 80, "CVE": "CVE-2024-5678", "Severity": "medium"},
        {"IP": "192.168.1.101", "Port": 22, "CVE": "CVE-2024-9012", "Severity": "critical"},
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["IP", "Port", "CVE", "Severity"])
        writer.writeheader()
        writer.writerows(vuln_rows)
    print(f"  已写入 CSV: {csv_path}")

    # 读取 CSV 并筛选高危
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        high_risk = [row for row in reader if row["Severity"] in ("high", "critical")]
    print(f"  高危漏洞数: {len(high_risk)}")
    for vuln in high_risk:
        print(f"    - {vuln['IP']}:{vuln['Port']} {vuln['CVE']} ({vuln['Severity']})")


# ============================================================
# 5. 异常处理
# ============================================================

def demo_exception_handling():
    """异常处理示例"""
    print("\n" + "=" * 60)
    print("【5. 异常处理】")
    print("=" * 60)

    # 5.1 基础异常捕获
    print("\n5.1 基础异常捕获")

    def safe_divide(a, b):
        """安全的除法运算"""
        try:
            result = a / b
            return result, None  # (结果, 错误信息)
        except ZeroDivisionError:
            return None, "除数不能为零"
        except TypeError:
            return None, "类型错误"
        except Exception as e:
            return None, f"其他错误: {e}"

    test_cases = [(10, 2), (10, 0), ("10", 2), (10, "a")]
    for a, b in test_cases:
        result, error = safe_divide(a, b)
        if error:
            print(f"  {a} / {b} = ✗ {error}")
        else:
            print(f"  {a} / {b} = {result}")

    # 5.2 文件操作中的异常处理
    print("\n5.2 文件操作的异常处理")

    def safe_read_file(filepath):
        """安全地读取文件"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read(), None
        except FileNotFoundError:
            return None, f"文件不存在: {filepath}"
        except PermissionError:
            return None, f"没有权限读取: {filepath}"
        except UnicodeDecodeError:
            return None, "文件编码错误"
        except Exception as e:
            return None, f"读取失败: {e}"

    # 测试存在的文件
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    existing_file = os.path.join(output_dir, "sample_log.txt")
    content, err = safe_read_file(existing_file)
    if err:
        print(f"  读取: {err}")
    else:
        print(f"  读取成功，共 {len(content)} 字节")

    # 测试不存在的文件
    content, err = safe_read_file("/nonexistent/file.txt")
    print(f"  不存在的文件: {err}")

    # 5.3 finally 的用法
    print("\n5.3 finally 清理资源")
    print("  （无论是否有异常，finally 都会执行，用于释放资源）")


# ============================================================
# 6. 类与对象
# ============================================================

class LogAnalyzer:
    """简单的日志分析器类

    用于分析认证日志，统计登录失败、异常 IP 等。
    这是一个面向对象编程的示例。

    Attributes:
        log_path: 日志文件路径
        failed_logins: 登录失败记录列表
        ip_stats: 各 IP 的统计数据
    """

    def __init__(self, log_path):
        """初始化日志分析器

        Args:
            log_path: 要分析的日志文件路径
        """
        self.log_path = log_path
        self.failed_logins = []
        self.ip_stats = {}

    def analyze(self):
        """分析日志文件

        Returns:
            bool: 分析成功返回 True
        """
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    self._process_line(line.strip())
            return True
        except FileNotFoundError:
            print(f"  错误: 文件不存在 {self.log_path}")
            return False

    def _process_line(self, line):
        """处理单行日志（内部方法）

        Args:
            line: 日志行
        """
        # 提取 IP（简化的正则，匹配 IP 地址）
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
        if not ip_match:
            return

        ip = ip_match.group()

        # 统计每个 IP 的出现次数
        if ip not in self.ip_stats:
            self.ip_stats[ip] = {"total": 0, "failed": 0}
        self.ip_stats[ip]["total"] += 1

        # 判断是否是登录失败（包含 Failed 或 failure）
        if "Failed" in line or "failure" in line.lower():
            self.failed_logins.append({"ip": ip, "line": line})
            self.ip_stats[ip]["failed"] += 1

    def get_top_failed_ips(self, top_n=10):
        """获取登录失败次数最多的 IP

        Args:
            top_n: 返回前 N 个

        Returns:
            list: [(ip, count), ...] 按失败次数降序
        """
        # 筛选出有失败记录的 IP，按失败次数排序
        failed_ips = [
            (ip, stats["failed"])
            for ip, stats in self.ip_stats.items()
            if stats["failed"] > 0
        ]
        failed_ips.sort(key=lambda x: x[1], reverse=True)
        return failed_ips[:top_n]

    def get_summary(self):
        """获取分析摘要

        Returns:
            dict: 摘要信息
        """
        total_lines = sum(s["total"] for s in self.ip_stats.values())
        total_failed = len(self.failed_logins)
        unique_ips = len(self.ip_stats)
        failure_rate = (total_failed / total_lines * 100) if total_lines > 0 else 0

        return {
            "total_lines": total_lines,
            "total_failed": total_failed,
            "unique_ips": unique_ips,
            "failure_rate": round(failure_rate, 2),
            "top_failed": self.get_top_failed_ips(5)
        }


def demo_classes():
    """类与对象示例"""
    print("\n" + "=" * 60)
    print("【6. 类与对象】")
    print("=" * 60)

    print("\n6.1 LogAnalyzer 日志分析器示例")

    # 创建示例日志文件
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    auth_log_path = os.path.join(output_dir, "auth_sample.log")

    sample_auth_logs = [
        "Oct 10 10:00:01 server sshd[1001]: Failed password for root from 10.0.0.5 port 22 ssh2",
        "Oct 10 10:00:02 server sshd[1002]: Failed password for admin from 10.0.0.5 port 22 ssh2",
        "Oct 10 10:00:03 server sshd[1003]: Accepted password for alice from 192.168.1.10 port 22 ssh2",
        "Oct 10 10:00:04 server sshd[1004]: Failed password for root from 10.0.0.6 port 22 ssh2",
        "Oct 10 10:00:05 server sshd[1005]: Failed password for root from 10.0.0.5 port 22 ssh2",
        "Oct 10 10:00:06 server sshd[1006]: Accepted password for bob from 192.168.1.11 port 22 ssh2",
        "Oct 10 10:00:07 server sshd[1007]: Failed password for test from 10.0.0.7 port 22 ssh2",
        "Oct 10 10:00:08 server sshd[1008]: Failed password for root from 10.0.0.5 port 22 ssh2",
        "Oct 10 10:00:09 server sshd[1009]: Accepted publickey for deploy from 192.168.1.20 port 22 ssh2",
        "Oct 10 10:00:10 server sshd[1010]: Failed password for administrator from 10.0.0.6 port 22 ssh2",
    ]

    with open(auth_log_path, "w", encoding="utf-8") as f:
        for line in sample_auth_logs:
            f.write(line + "\n")

    # 使用 LogAnalyzer 类
    analyzer = LogAnalyzer(auth_log_path)
    if analyzer.analyze():
        summary = analyzer.get_summary()
        print(f"  总行数: {summary['total_lines']}")
        print(f"  失败次数: {summary['total_failed']}")
        print(f"  唯一 IP 数: {summary['unique_ips']}")
        print(f"  失败率: {summary['failure_rate']}%")
        print(f"  失败最多的 IP Top 5:")
        for ip, count in summary["top_failed"]:
            print(f"    - {ip}: {count} 次")


# ============================================================
# 7. 正则表达式
# ============================================================

def demo_regex():
    """正则表达式示例（安全场景常用）"""
    print("\n" + "=" * 60)
    print("【7. 正则表达式】")
    print("=" * 60)

    # 示例日志文本
    log_text = """
2024-10-10 10:00:01 192.168.1.100 GET /index.html 200
2024-10-10 10:00:02 10.0.0.5 POST /login 401
2024-10-10 10:00:03 192.168.1.101 GET /admin 403
Contact: admin@example.com, support@test.org
MD5: d41d8cd98f00b204e9800998ecf8427e
SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
URL: https://www.example.com/path?query=test
"""

    # ----- IP 地址提取 -----
    print("\n7.1 提取 IP 地址")
    # 简化的 IPv4 正则
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = re.findall(ip_pattern, log_text)
    print(f"  找到 {len(ips)} 个 IP: {ips}")

    # ----- 邮箱提取 -----
    print("\n7.2 提取邮箱地址")
    email_pattern = r'[\w.+-]+@[\w-]+\.[\w.-]+'
    emails = re.findall(email_pattern, log_text)
    print(f"  找到 {len(emails)} 个邮箱: {emails}")

    # ----- 哈希值提取 -----
    print("\n7.3 提取哈希值")
    # MD5 (32 位十六进制)
    md5_pattern = r'\b[a-fA-F0-9]{32}\b'
    md5_hashes = re.findall(md5_pattern, log_text)
    print(f"  MD5 哈希: {md5_hashes}")

    # SHA256 (64 位十六进制)
    sha256_pattern = r'\b[a-fA-F0-9]{64}\b'
    sha256_hashes = re.findall(sha256_pattern, log_text)
    print(f"  SHA256 哈希: {sha256_hashes}")

    # ----- URL 提取 -----
    print("\n7.4 提取 URL")
    url_pattern = r'https?://[\w./?=&%-]+'
    urls = re.findall(url_pattern, log_text)
    print(f"  URL: {urls}")

    # ----- 日志解析 -----
    print("\n7.5 解析日志行")
    log_line = "2024-10-10 10:00:01 192.168.1.100 GET /index.html 200"
    log_pattern = r'(\S+\s\S+)\s(\S+)\s(\S+)\s(\S+)\s(\d+)'
    m = re.match(log_pattern, log_line)
    if m:
        print(f"  时间: {m.group(1)}")
        print(f"  IP: {m.group(2)}")
        print(f"  方法: {m.group(3)}")
        print(f"  路径: {m.group(4)}")
        print(f"  状态码: {m.group(5)}")

    # ----- 替换（数据脱敏）-----
    print("\n7.6 数据脱敏（隐藏 IP 最后一段）")
    # 把 IP 的最后一段换成 .x
    masked = re.sub(r'(\d+\.\d+\.\d+)\.\d+', r'\1.x', log_text)
    # 只打印 IP 相关的行
    for line in masked.strip().split("\n"):
        if re.search(ip_pattern, line):
            print(f"  {line.strip()}")


# ============================================================
# 8. 命令行参数
# ============================================================

def demo_argparse():
    """命令行参数解析示例（argparse）"""
    print("\n" + "=" * 60)
    print("【8. 命令行参数 (argparse)】")
    print("=" * 60)
    print("  （此示例在脚本内模拟，实际使用时从命令行传参）")

    # 模拟命令行参数
    import sys
    original_argv = sys.argv
    sys.argv = ["script.py", "127.0.0.1", "-p", "1-100", "-t", "2", "-o", "result.json"]

    parser = argparse.ArgumentParser(
        description="示例端口扫描器（仅用于授权测试）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s 192.168.1.1 -p 1-1000
  %(prog)s 10.0.0.1 -p 22,80,443 -t 3 -o result.json
        """
    )

    # 位置参数
    parser.add_argument("target", help="目标 IP 地址")

    # 可选参数
    parser.add_argument(
        "-p", "--ports",
        default="1-1000",
        help="端口范围，如 1-1000 或 22,80,443 (默认: 1-1000)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=2.0,
        help="连接超时时间，单位秒 (默认: 2.0)"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出结果到 JSON 文件"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    args = parser.parse_args()

    print(f"\n  目标 IP: {args.target}")
    print(f"  端口范围: {args.ports}")
    print(f"  超时时间: {args.timeout}s")
    print(f"  输出文件: {args.output or '无'}")
    print(f"  详细模式: {'是' if args.verbose else '否'}")

    # 恢复原始 argv
    sys.argv = original_argv


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数：依次运行所有示例"""
    print("\n" + "=" * 60)
    print("  Python 基础语法示例（安全从业者视角）")
    print("  Python Basics for Security Practitioners")
    print("=" * 60)

    demo_data_types()
    demo_control_flow()
    demo_functions()
    demo_file_operations()
    demo_exception_handling()
    demo_classes()
    demo_regex()
    demo_argparse()

    print("\n" + "=" * 60)
    print("  所有示例运行完成！")
    print("  输出文件保存在 code/output/ 目录下")
    print("=" * 60)


if __name__ == "__main__":
    main()
