#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
security_cases.py —— Python 安全案例示例（防御/授权测试视角）

涵盖 3 个安全案例：
  1. 端口扫描器 (PortScanner) — 基础 TCP 端口扫描器，仅用于授权环境
  2. 日志分析器 (LogAnalyzer) — 分析认证日志，检测暴力破解等异常
  3. 哈希校验工具 (FileHashChecker) — 计算/校验文件哈希，用于完整性检查

运行方式：
  python security_cases.py          # 运行所有示例
  python security_cases.py --help   # 查看命令行用法
  python security_cases.py scan 127.0.0.1 -p 1-1000  # 端口扫描

注意：
  - 所有工具仅限在授权的环境中使用
  - 端口扫描器仅供学习和授权测试，请勿用于未授权目标
  - 生产环境使用前请充分测试
"""

import os
import sys
import socket
import hashlib
import re
import json
import argparse
from datetime import datetime


# ============================================================
# 案例 1：端口扫描器
# ============================================================

class PortScanner:
    """基础 TCP 端口扫描器

    使用 socket 进行 TCP connect 扫描，适用于授权环境下的
    端口探测、安全基线检查、资产发现等场景。

    ⚠️ 仅限对有明确书面授权的目标使用。
    ⚠️ 生产环境使用请注意频率，避免影响目标系统。

    Attributes:
        target: 目标 IP 地址
        timeout: 连接超时时间（秒）
        open_ports: 扫描发现的开放端口列表
    """

    def __init__(self, target, timeout=2.0):
        """初始化端口扫描器

        Args:
            target: 目标 IP 地址或主机名
            timeout: 连接超时时间，默认 2 秒
        """
        self.target = target
        self.timeout = timeout
        self.open_ports = []

    @staticmethod
    def parse_ports(port_str):
        """解析端口范围字符串

        支持格式：
          - 单个端口: "22"
          - 端口范围: "1-1000"
          - 多个端口: "22,80,443,8080"
          - 混合: "22,80-90,443"

        Args:
            port_str: 端口字符串

        Returns:
            list: 端口号列表（已排序去重）

        Raises:
            ValueError: 端口格式不正确
        """
        ports = set()

        for part in port_str.split(","):
            part = part.strip()
            if not part:
                continue

            if "-" in part:
                # 范围格式
                try:
                    start, end = part.split("-", 1)
                    start = int(start.strip())
                    end = int(end.strip())
                    if start < 1 or end > 65535 or start > end:
                        raise ValueError(f"无效的端口范围: {part}")
                    for p in range(start, end + 1):
                        ports.add(p)
                except ValueError as e:
                    raise ValueError(f"端口格式错误: {part} ({e})")
            else:
                # 单个端口
                try:
                    p = int(part)
                    if p < 1 or p > 65535:
                        raise ValueError(f"端口超出范围: {p}")
                    ports.add(p)
                except ValueError as e:
                    raise ValueError(f"无效的端口号: {part} ({e})")

        if not ports:
            raise ValueError("没有有效的端口")

        return sorted(ports)

    def scan_port(self, port):
        """扫描单个端口

        Args:
            port: 端口号

        Returns:
            bool: 端口开放返回 True，否则返回 False
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            return result == 0
        except socket.gaierror:
            print(f"  错误: 无法解析主机名 {self.target}")
            return False
        except socket.timeout:
            return False
        except Exception:
            return False

    def scan(self, port_list, verbose=False):
        """扫描指定端口列表

        Args:
            port_list: 端口号列表
            verbose: 是否显示详细进度

        Returns:
            list: 开放的端口列表
        """
        self.open_ports = []
        total = len(port_list)

        for i, port in enumerate(port_list, 1):
            is_open = self.scan_port(port)

            if is_open:
                self.open_ports.append(port)
                if verbose:
                    print(f"  [{i}/{total}] 端口 {port:>5}: OPEN ✓")
            elif verbose and i % 100 == 0:
                print(f"  进度: {i}/{total} 已扫描，发现 {len(self.open_ports)} 个开放端口")

        return self.open_ports

    def get_service_name(self, port):
        """获取常见端口对应的服务名（简化版）

        Args:
            port: 端口号

        Returns:
            str: 服务名，未知返回 "unknown"
        """
        common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            6379: "Redis",
            8080: "HTTP-Proxy",
            8443: "HTTPS-Alt",
        }
        return common_ports.get(port, "unknown")

    def get_result_dict(self):
        """获取字典格式的扫描结果

        Returns:
            dict: 扫描结果
        """
        return {
            "target": self.target,
            "scan_time": datetime.now().isoformat(),
            "timeout": self.timeout,
            "open_ports": [
                {"port": p, "service": self.get_service_name(p)}
                for p in self.open_ports
            ],
            "total_open": len(self.open_ports)
        }

    def print_result(self):
        """打印扫描结果"""
        print(f"\n  扫描结果: {self.target}")
        print(f"  扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  开放端口数: {len(self.open_ports)}")
        print("  " + "-" * 40)

        if not self.open_ports:
            print("  没有发现开放端口")
        else:
            print(f"  {'端口':>8}  {'服务':<15}  状态")
            print("  " + "-" * 40)
            for port in self.open_ports:
                service = self.get_service_name(port)
                print(f"  {port:>8}  {service:<15}  OPEN")

        print("  " + "-" * 40)


# ============================================================
# 案例 2：日志分析器（安全检测）
# ============================================================

class SecurityLogAnalyzer:
    """安全日志分析器

    分析认证日志，检测暴力破解、异常登录时间、可疑 IP 等安全问题。
    适用于安全运营、应急响应、合规审计等场景。

    支持的日志格式：
      - Linux auth.log / secure 格式
      - 简化的通用认证日志

    Attributes:
        log_path: 日志文件路径
        failed_logins: 登录失败记录
        success_logins: 登录成功记录
        ip_stats: 各 IP 统计
        user_stats: 各用户统计
    """

    # 常见的登录失败关键词
    FAILURE_KEYWORDS = [
        "Failed password",
        "authentication failure",
        "FAILED LOGIN",
        "Invalid user",
        "Connection closed by",
        "error: PAM: Authentication failure",
    ]

    # 常见的登录成功关键词
    SUCCESS_KEYWORDS = [
        "Accepted password",
        "Accepted publickey",
        "session opened",
        "LOGIN",
    ]

    def __init__(self, log_path):
        """初始化日志分析器

        Args:
            log_path: 日志文件路径
        """
        self.log_path = log_path
        self.failed_logins = []
        self.success_logins = []
        self.ip_stats = {}
        self.user_stats = {}

    def analyze(self):
        """分析日志文件

        Returns:
            bool: 分析成功返回 True
        """
        if not os.path.exists(self.log_path):
            print(f"  错误: 日志文件不存在: {self.log_path}")
            return False

        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    line = line.strip()
                    if not line:
                        continue
                    self._process_line(line, line_num)
            return True
        except PermissionError:
            print(f"  错误: 没有权限读取文件: {self.log_path}")
            return False
        except Exception as e:
            print(f"  错误: 读取文件失败: {e}")
            return False

    def _extract_ip(self, line):
        """从日志行中提取 IP 地址

        Args:
            line: 日志行

        Returns:
            str or None: 提取到的 IP 地址
        """
        # IPv4 正则
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
        match = re.search(ip_pattern, line)
        return match.group(0) if match else None

    def _extract_user(self, line):
        """从日志行中提取用户名

        Args:
            line: 日志行

        Returns:
            str or None: 提取到的用户名
        """
        # 匹配 "for username" 或 "user username" 模式
        patterns = [
            r'for\s+(\S+)\s+from',
            r'user\s+(\S+)',
            r'USER\s+(\S+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                user = match.group(1)
                if user.lower() not in ("invalid", "root@"):
                    return user
        return None

    def _extract_time(self, line):
        """提取日志时间（简化处理）

        Args:
            line: 日志行

        Returns:
            str or None: 时间字符串
        """
        # 匹配常见的时间格式
        patterns = [
            r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})',  # ISO 格式
            r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',     # syslog 格式
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return None

    def _process_line(self, line, line_num):
        """处理单行日志

        Args:
            line: 日志行内容
            line_num: 行号
        """
        ip = self._extract_ip(line)
        user = self._extract_user(line)
        time_str = self._extract_time(line)

        # 判断是失败还是成功
        is_failure = any(kw in line for kw in self.FAILURE_KEYWORDS)
        is_success = any(kw in line for kw in self.SUCCESS_KEYWORDS)

        record = {
            "line_num": line_num,
            "ip": ip,
            "user": user,
            "time": time_str,
            "content": line[:150]  # 只存前 150 字符
        }

        if is_failure:
            self.failed_logins.append(record)

            # 更新 IP 统计
            if ip:
                if ip not in self.ip_stats:
                    self.ip_stats[ip] = {"failed": 0, "success": 0, "users": set()}
                self.ip_stats[ip]["failed"] += 1
                if user:
                    self.ip_stats[ip]["users"].add(user)

            # 更新用户统计
            if user:
                if user not in self.user_stats:
                    self.user_stats[user] = {"failed": 0, "success": 0, "ips": set()}
                self.user_stats[user]["failed"] += 1
                if ip:
                    self.user_stats[user]["ips"].add(ip)

        if is_success:
            self.success_logins.append(record)

            if ip:
                if ip not in self.ip_stats:
                    self.ip_stats[ip] = {"failed": 0, "success": 0, "users": set()}
                self.ip_stats[ip]["success"] += 1
                if user:
                    self.ip_stats[ip]["users"].add(user)

            if user:
                if user not in self.user_stats:
                    self.user_stats[user] = {"failed": 0, "success": 0, "ips": set()}
                self.user_stats[user]["success"] += 1
                if ip:
                    self.user_stats[user]["ips"].add(ip)

    def detect_brute_force(self, threshold=5):
        """检测暴力破解（某个 IP 失败次数超过阈值）

        Args:
            threshold: 失败次数阈值，默认 5 次

        Returns:
            list: 可疑 IP 列表 [(ip, failed_count, success_count), ...]
        """
        suspects = []
        for ip, stats in self.ip_stats.items():
            if stats["failed"] >= threshold:
                suspects.append((ip, stats["failed"], stats["success"]))

        # 按失败次数降序排列
        suspects.sort(key=lambda x: x[1], reverse=True)
        return suspects

    def get_suspicious_users(self, threshold=5):
        """获取可疑的用户（被多次尝试登录失败的）

        Args:
            threshold: 失败次数阈值

        Returns:
            list: [(username, failed_count, ip_count), ...]
        """
        suspicious = []
        for user, stats in self.user_stats.items():
            if stats["failed"] >= threshold:
                suspicious.append((user, stats["failed"], len(stats["ips"])))

        suspicious.sort(key=lambda x: x[1], reverse=True)
        return suspicious

    def get_summary(self):
        """获取分析摘要

        Returns:
            dict: 摘要信息
        """
        total_lines = len(self.failed_logins) + len(self.success_logins)
        total_failed = len(self.failed_logins)
        total_success = len(self.success_logins)
        failure_rate = (total_failed / total_lines * 100) if total_lines > 0 else 0

        return {
            "log_file": self.log_path,
            "total_auth_events": total_lines,
            "failed_logins": total_failed,
            "successful_logins": total_success,
            "failure_rate": round(failure_rate, 2),
            "unique_ips": len(self.ip_stats),
            "unique_users": len(self.user_stats),
            "brute_force_suspects": len(self.detect_brute_force()),
        }

    def print_report(self):
        """打印分析报告"""
        summary = self.get_summary()

        print(f"\n  安全日志分析报告")
        print("  " + "=" * 50)
        print(f"  日志文件: {summary['log_file']}")
        print(f"  认证事件总数: {summary['total_auth_events']}")
        print(f"  登录成功: {summary['successful_logins']}")
        print(f"  登录失败: {summary['failed_logins']}")
        print(f"  失败率: {summary['failure_rate']}%")
        print(f"  涉及 IP 数: {summary['unique_ips']}")
        print(f"  涉及用户数: {summary['unique_users']}")
        print(f"  可疑暴力破解 IP: {summary['brute_force_suspects']} 个")

        # 暴力破解可疑 IP
        suspects = self.detect_brute_force()
        if suspects:
            print("\n  暴力破解可疑 IP Top 10:")
            print(f"  {'IP':<18} {'失败次数':>8} {'成功次数':>8}")
            print("  " + "-" * 40)
            for ip, failed, success in suspects[:10]:
                print(f"  {ip:<18} {failed:>8} {success:>8}")

        # 可疑用户
        suspicious_users = self.get_suspicious_users()
        if suspicious_users:
            print("\n  被暴力尝试的用户 Top 10:")
            print(f"  {'用户名':<20} {'失败次数':>8} {'涉及IP数':>8}")
            print("  " + "-" * 40)
            for user, failed, ip_count in suspicious_users[:10]:
                print(f"  {user:<20} {failed:>8} {ip_count:>8}")


# ============================================================
# 案例 3：文件哈希校验工具
# ============================================================

class FileHashChecker:
    """文件哈希校验工具

    用于文件完整性检查、恶意文件哈希比对、
    软件发布校验等安全场景。

    支持的算法：MD5、SHA1、SHA256、SHA512

    Attributes:
        algorithm: 使用的哈希算法
        chunk_size: 大文件分块读取的大小
    """

    SUPPORTED_ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]

    def __init__(self, algorithm="sha256", chunk_size=8192):
        """初始化哈希校验器

        Args:
            algorithm: 哈希算法，默认 sha256
            chunk_size: 大文件分块读取的字节数

        Raises:
            ValueError: 不支持的算法
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"不支持的算法: {algorithm}. "
                f"支持: {', '.join(self.SUPPORTED_ALGORITHMS)}"
            )
        self.algorithm = algorithm
        self.chunk_size = chunk_size

    def calculate_file_hash(self, filepath):
        """计算文件的哈希值

        Args:
            filepath: 文件路径

        Returns:
            str: 十六进制格式的哈希值

        Raises:
            FileNotFoundError: 文件不存在
            PermissionError: 没有读取权限
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        if not os.path.isfile(filepath):
            raise ValueError(f"不是文件: {filepath}")

        # 根据算法选择哈希对象
        if self.algorithm == "md5":
            hasher = hashlib.md5()
        elif self.algorithm == "sha1":
            hasher = hashlib.sha1()
        elif self.algorithm == "sha256":
            hasher = hashlib.sha256()
        elif self.algorithm == "sha512":
            hasher = hashlib.sha512()
        else:
            raise ValueError(f"未知算法: {self.algorithm}")

        # 分块读取大文件，避免内存溢出
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()

    def calculate_string_hash(self, text):
        """计算字符串的哈希值

        Args:
            text: 字符串内容

        Returns:
            str: 十六进制格式的哈希值
        """
        if isinstance(text, str):
            text = text.encode("utf-8")

        if self.algorithm == "md5":
            return hashlib.md5(text).hexdigest()
        elif self.algorithm == "sha1":
            return hashlib.sha1(text).hexdigest()
        elif self.algorithm == "sha256":
            return hashlib.sha256(text).hexdigest()
        elif self.algorithm == "sha512":
            return hashlib.sha512(text).hexdigest()

    def verify_file(self, filepath, expected_hash):
        """校验文件哈希是否匹配

        Args:
            filepath: 文件路径
            expected_hash: 期望的哈希值

        Returns:
            tuple: (是否匹配, 实际哈希值)
        """
        actual_hash = self.calculate_file_hash(filepath)
        expected_hash = expected_hash.lower().strip()
        return actual_hash == expected_hash, actual_hash

    def calculate_directory_hashes(self, dir_path, recursive=True):
        """计算目录下所有文件的哈希

        Args:
            dir_path: 目录路径
            recursive: 是否递归子目录

        Returns:
            dict: {文件路径: 哈希值}
        """
        if not os.path.isdir(dir_path):
            raise ValueError(f"不是目录: {dir_path}")

        results = {}

        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    file_hash = self.calculate_file_hash(filepath)
                    # 保存相对路径
                    rel_path = os.path.relpath(filepath, dir_path)
                    results[rel_path] = file_hash
                except (PermissionError, OSError):
                    # 跳过无法读取的文件
                    continue

            if not recursive:
                break

        return results

    def compare_directories(self, dir1, dir2):
        """比较两个目录的文件哈希

        用于完整性检查、文件篡改检测等场景。

        Args:
            dir1: 第一个目录（基准）
            dir2: 第二个目录（待检测）

        Returns:
            dict: 比较结果，包含 added/removed/modified/unchanged
        """
        hash1 = self.calculate_directory_hashes(dir1)
        hash2 = self.calculate_directory_hashes(dir2)

        files1 = set(hash1.keys())
        files2 = set(hash2.keys())

        added = files2 - files1        # 新增的文件
        removed = files1 - files2      # 删除的文件
        common = files1 & files2       # 都有的文件

        modified = []
        unchanged = []

        for filepath in common:
            if hash1[filepath] != hash2[filepath]:
                modified.append(filepath)
            else:
                unchanged.append(filepath)

        return {
            "added": sorted(list(added)),
            "removed": sorted(list(removed)),
            "modified": sorted(modified),
            "unchanged": sorted(unchanged),
            "dir1_count": len(hash1),
            "dir2_count": len(hash2),
        }

    def export_to_json(self, hashes_dict, output_path):
        """导出哈希结果到 JSON 文件

        Args:
            hashes_dict: 哈希字典
            output_path: 输出文件路径
        """
        data = {
            "algorithm": self.algorithm,
            "generated_at": datetime.now().isoformat(),
            "file_count": len(hashes_dict),
            "hashes": hashes_dict
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_sample_files(output_dir):
        """生成示例文件（用于演示）

        Args:
            output_dir: 输出目录

        Returns:
            list: 生成的文件路径列表
        """
        os.makedirs(output_dir, exist_ok=True)

        samples = [
            ("readme.txt", "这是一个示例文件。\n用于测试哈希校验功能。\n"),
            ("config.ini", "[security]\nenabled = true\npassword = secret\n"),
            ("data.csv", "ip,port,status\n127.0.0.1,22,open\n127.0.0.1,80,open\n"),
        ]

        generated = []
        for filename, content in samples:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            generated.append(filepath)

        return generated


# ============================================================
# 命令行接口
# ============================================================

def build_argparse():
    """构建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Python 安全案例集（防御/授权测试视角）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s demo                        运行所有演示
  %(prog)s scan 127.0.0.1 -p 1-1000    端口扫描
  %(prog)s log auth.log                日志分析
  %(prog)s hash file.txt               计算文件哈希
  %(prog)s hash --verify abc123 file.txt  校验哈希

⚠️  所有工具仅限在授权环境中使用
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # ----- demo 命令 -----
    demo_parser = subparsers.add_parser("demo", help="运行所有示例演示")

    # ----- scan 命令（端口扫描）-----
    scan_parser = subparsers.add_parser("scan", help="端口扫描（仅限授权目标）")
    scan_parser.add_argument("target", help="目标 IP 地址")
    scan_parser.add_argument(
        "-p", "--ports", default="1-1000",
        help="端口范围 (默认: 1-1000)"
    )
    scan_parser.add_argument(
        "-t", "--timeout", type=float, default=2.0,
        help="超时时间（秒），默认 2.0"
    )
    scan_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="显示详细进度"
    )
    scan_parser.add_argument(
        "-o", "--output", help="输出结果到 JSON 文件"
    )

    # ----- log 命令（日志分析）-----
    log_parser = subparsers.add_parser("log", help="安全日志分析")
    log_parser.add_argument("logfile", help="日志文件路径")
    log_parser.add_argument(
        "--threshold", type=int, default=5,
        help="暴力破解检测阈值（默认 5 次）"
    )
    log_parser.add_argument(
        "--json", help="导出分析结果到 JSON 文件"
    )

    # ----- hash 命令（哈希校验）-----
    hash_parser = subparsers.add_parser("hash", help="文件哈希校验")
    hash_parser.add_argument("target", help="文件或目录路径")
    hash_parser.add_argument(
        "-a", "--algorithm",
        choices=["md5", "sha1", "sha256", "sha512"],
        default="sha256",
        help="哈希算法（默认 sha256）"
    )
    hash_parser.add_argument(
        "--verify", help="校验指定的哈希值"
    )
    hash_parser.add_argument(
        "--recursive", action="store_true",
        help="目录递归计算"
    )
    hash_parser.add_argument(
        "-o", "--output", help="导出结果到 JSON 文件"
    )

    return parser


def run_demo():
    """运行所有演示"""
    print("=" * 60)
    print("  Python 安全案例演示")
    print("  Security Cases Demo (Defensive Perspective)")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    # ===== 案例 1：端口扫描器 =====
    print("\n" + "=" * 60)
    print("【案例 1】端口扫描器")
    print("=" * 60)
    print("\n  ⚠️  演示：扫描本地回环地址 127.0.0.1 的常用端口")
    print("  ⚠️  仅限授权目标使用！")

    scanner = PortScanner("127.0.0.1", timeout=1.0)
    # 只扫描几个常用端口，演示用
    ports = [22, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080]
    print(f"\n  扫描目标: 127.0.0.1")
    print(f"  扫描端口数: {len(ports)}")
    print(f"  超时时间: 1.0s")
    print(f"  正在扫描...")

    scanner.scan(ports)
    scanner.print_result()

    # ===== 案例 2：日志分析器 =====
    print("\n" + "=" * 60)
    print("【案例 2】安全日志分析器")
    print("=" * 60)

    # 生成示例日志
    sample_log_path = os.path.join(output_dir, "auth_sample.log")
    sample_logs = [
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
        "Oct 10 10:00:11 server sshd[1011]: Failed password for root from 10.0.0.5 port 22 ssh2",
        "Oct 10 10:00:12 server sshd[1012]: Failed password for user from 10.0.0.8 port 22 ssh2",
        "Oct 10 10:00:13 server sshd[1013]: Failed password for oracle from 10.0.0.5 port 22 ssh2",
        "Oct 10 10:00:14 server sshd[1014]: Failed password for mysql from 10.0.0.6 port 22 ssh2",
        "Oct 10 10:00:15 server sshd[1015]: Failed password for postgres from 10.0.0.5 port 22 ssh2",
    ]

    with open(sample_log_path, "w", encoding="utf-8") as f:
        for line in sample_logs:
            f.write(line + "\n")

    print(f"\n  生成示例日志: {sample_log_path}")

    analyzer = SecurityLogAnalyzer(sample_log_path)
    if analyzer.analyze():
        analyzer.print_report()

    # ===== 案例 3：哈希校验 =====
    print("\n" + "=" * 60)
    print("【案例 3】文件哈希校验工具")
    print("=" * 60)

    # 生成示例文件
    sample_dir = os.path.join(output_dir, "hash_demo")
    FileHashChecker.generate_sample_files(sample_dir)
    print(f"\n  生成示例文件目录: {sample_dir}")

    checker = FileHashChecker("sha256")

    # 计算单个文件哈希
    test_file = os.path.join(sample_dir, "readme.txt")
    file_hash = checker.calculate_file_hash(test_file)
    print(f"\n  文件 SHA256: {file_hash}")
    print(f"  文件: readme.txt")

    # 校验哈希
    is_match, actual = checker.verify_file(test_file, file_hash)
    print(f"  哈希校验: {'✓ 匹配' if is_match else '✗ 不匹配'}")

    # 计算目录哈希
    print(f"\n  目录哈希计算 ({sample_dir}):")
    dir_hashes = checker.calculate_directory_hashes(sample_dir)
    for filepath, h in sorted(dir_hashes.items()):
        print(f"    {filepath:<20} {h}")

    # 导出结果
    hash_output = os.path.join(output_dir, "hashes.json")
    checker.export_to_json(dir_hashes, hash_output)
    print(f"\n  哈希结果已导出: {hash_output}")

    print("\n" + "=" * 60)
    print("  所有案例演示完成！")
    print("  输出文件保存在 code/output/ 目录下")
    print("=" * 60)


def main():
    """主函数"""
    parser = build_argparse()
    args = parser.parse_args()

    if args.command == "demo" or args.command is None:
        run_demo()

    elif args.command == "scan":
        # 端口扫描
        print(f"  端口扫描: {args.target}")
        print(f"  端口: {args.ports}")
        print(f"  超时: {args.timeout}s")
        print(f"  ⚠️  仅限授权目标使用！")

        scanner = PortScanner(args.target, timeout=args.timeout)
        try:
            ports = PortScanner.parse_ports(args.ports)
        except ValueError as e:
            print(f"  错误: {e}")
            sys.exit(1)

        print(f"  共 {len(ports)} 个端口，开始扫描...")
        scanner.scan(ports, verbose=args.verbose)
        scanner.print_result()

        if args.output:
            result = scanner.get_result_dict()
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n  结果已保存到: {args.output}")

    elif args.command == "log":
        # 日志分析
        print(f"  分析日志: {args.logfile}")
        analyzer = SecurityLogAnalyzer(args.logfile)
        if analyzer.analyze():
            analyzer.print_report()

            if args.json:
                result = {
                    "summary": analyzer.get_summary(),
                    "brute_force_suspects": [
                        {"ip": ip, "failed_count": f, "success_count": s}
                        for ip, f, s in analyzer.detect_brute_force(args.threshold)
                    ],
                    "suspicious_users": [
                        {"user": u, "failed_count": f, "ip_count": c}
                        for u, f, c in analyzer.get_suspicious_users(args.threshold)
                    ]
                }
                with open(args.json, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n  结果已保存到: {args.json}")
        else:
            sys.exit(1)

    elif args.command == "hash":
        # 哈希校验
        checker = FileHashChecker(args.algorithm)
        target = args.target

        if os.path.isfile(target):
            # 单个文件
            file_hash = checker.calculate_file_hash(target)
            print(f"  {args.algorithm.upper()}: {file_hash}")
            print(f"  文件: {target}")

            if args.verify:
                is_match, actual = checker.verify_file(target, args.verify)
                print(f"  校验结果: {'✓ 匹配' if is_match else '✗ 不匹配'}")
                if not is_match:
                    print(f"  期望值: {args.verify}")
                    print(f"  实际值: {actual}")

        elif os.path.isdir(target):
            # 目录
            print(f"  计算目录哈希: {target}")
            print(f"  算法: {args.algorithm.upper()}")
            print(f"  递归: {'是' if args.recursive else '否'}")

            hashes = checker.calculate_directory_hashes(target, recursive=args.recursive)
            print(f"  共 {len(hashes)} 个文件\n")

            for filepath, h in sorted(hashes.items())[:20]:
                print(f"    {filepath}")
                print(f"      {h}")

            if len(hashes) > 20:
                print(f"    ... 还有 {len(hashes) - 20} 个文件")

            if args.output:
                checker.export_to_json(hashes, args.output)
                print(f"\n  结果已保存到: {args.output}")

        else:
            print(f"  错误: 路径不存在: {target}")
            sys.exit(1)


if __name__ == "__main__":
    main()
