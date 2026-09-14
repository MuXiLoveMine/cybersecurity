#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络安全工具包 (Network Security Toolkit)
=========================================

本工具集集成了基础网络安全学习中常用的各类工具：
1. 端口扫描器 - TCP全连接扫描、服务识别、Banner抓取
2. 子域名爆破器 - 字典爆破、常见子域名枚举
3. 目录扫描器 - Web目录/文件暴力枚举
4. 密码安全工具 - 强度检测、哈希生成、字典生成
5. 网络协议解析器 - IP/TCP/UDP/ICMP头部解析
6. 主机存活探测 - ICMP Ping、ARP扫描
7. 编码解码工具 - Base16/32/64、URL、Hex、凯撒
8. HTTP请求模拟器 - 自定义请求头、Cookie、方法

作者：基础网络安全学习工具
版本：1.0
用途：仅用于授权的安全测试和教育学习
"""

import socket
import struct
import threading
import queue
import time
import os
import re
import sys
import hashlib
import base64
import random
import string
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


# ============================================================
# 工具1: 端口扫描器
# ============================================================

class PortScanner:
    """TCP全连接端口扫描器，支持多线程和服务识别"""

    常见端口服务 = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
        3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
        8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB",
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    }

    def __init__(self, target: str, port_range: Tuple[int, int] = (1, 1024),
                 threads: int = 50, timeout: float = 1.0):
        self.target = target
        self.port_range = port_range
        self.threads = threads
        self.timeout = timeout
        self.open_ports = []
        self.q = queue.Queue()

    def _scan_port(self, port: int) -> Tuple[int, bool, str]:
        """扫描单个端口"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            if result == 0:
                service = self.常见端口服务.get(port, "unknown")
                return (port, True, service)
            return (port, False, "")
        except:
            return (port, False, "")

    def _worker(self):
        while True:
            port = self.q.get()
            if port is None:
                break
            port_num, is_open, service = self._scan_port(port)
            if is_open:
                self.open_ports.append((port_num, service))
                print(f"  [+] 端口 {port_num:5d} 开放 - {service}")
            self.q.task_done()

    def scan(self) -> List[Tuple[int, str]]:
        """执行扫描"""
        print(f"\n[*] 开始扫描目标: {self.target}")
        print(f"[*] 端口范围: {self.port_range[0]}-{self.port_range[1]}")
        print(f"[*] 线程数: {self.threads}")
        print(f"[*] 超时: {self.timeout}s")
        print()

        # 启动线程
        thread_list = []
        for _ in range(self.threads):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            thread_list.append(t)

        # 加入任务
        for port in range(self.port_range[0], self.port_range[1] + 1):
            self.q.put(port)

        # 等待完成
        self.q.join()
        for _ in range(self.threads):
            self.q.put(None)
        for t in thread_list:
            t.join()

        print(f"\n[*] 扫描完成，发现 {len(self.open_ports)} 个开放端口")
        return sorted(self.open_ports)


# ============================================================
# 工具2: 子域名爆破器
# ============================================================

class SubdomainBruteForcer:
    """子域名爆破工具"""

    常见子域名字典 = [
        "www", "mail", "ftp", "admin", "test", "dev", "api",
        "blog", "shop", "forum", "wiki", "vpn", "owa", "portal",
        "git", "svn", "jenkins", "ci", "cdn", "img", "static",
        "video", "music", "download", "upload", "backup", "old",
        "new", "demo", "beta", "alpha", "staging", "prod",
        "monitor", "status", "stats", "analytics", "log",
        "panel", "console", "manager", "root", "master",
    ]

    def __init__(self, domain: str, wordlist: List[str] = None,
                 threads: int = 20, timeout: float = 2.0):
        self.domain = domain
        self.wordlist = wordlist or self.常见子域名字典
        self.threads = threads
        self.timeout = timeout
        self.found = []
        self.q = queue.Queue()

    def _check_subdomain(self, subdomain: str) -> bool:
        """检查子域名是否存在"""
        try:
            full = f"{subdomain}.{self.domain}"
            socket.setdefaulttimeout(self.timeout)
            socket.gethostbyname(full)
            return True
        except:
            return False

    def _worker(self):
        while True:
            sub = self.q.get()
            if sub is None:
                break
            if self._check_subdomain(sub):
                self.found.append(f"{sub}.{self.domain}")
                print(f"  [+] 发现: {sub}.{self.domain}")
            self.q.task_done()

    def brute_force(self) -> List[str]:
        """执行爆破"""
        print(f"\n[*] 子域名爆破目标: {self.domain}")
        print(f"[*] 字典大小: {len(self.wordlist)}")
        print(f"[*] 线程数: {self.threads}")
        print()

        thread_list = []
        for _ in range(self.threads):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            thread_list.append(t)

        for sub in self.wordlist:
            self.q.put(sub)

        self.q.join()
        for _ in range(self.threads):
            self.q.put(None)
        for t in thread_list:
            t.join()

        print(f"\n[*] 爆破完成，发现 {len(self.found)} 个子域名")
        return sorted(self.found)


# ============================================================
# 工具3: 密码安全工具
# ============================================================

class PasswordSecurityTool:
    """密码安全工具集合"""

    弱密码列表 = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "admin", "letmein", "welcome", "monkey", "dragon",
        "111111", "iloveyou", "sunshine", "princess", "football",
    ]

    @staticmethod
    def check_strength(password: str) -> Dict[str, any]:
        """检测密码强度"""
        score = 0
        details = []

        length = len(password)
        if length >= 12:
            score += 25
            details.append("长度>=12 (+25)")
        elif length >= 8:
            score += 15
            details.append("长度>=8 (+15)")
        elif length >= 6:
            score += 5
            details.append("长度>=6 (+5)")
        else:
            details.append("长度太短 (+0)")

        if re.search(r'[a-z]', password):
            score += 10
            details.append("小写字母 (+10)")
        if re.search(r'[A-Z]', password):
            score += 15
            details.append("大写字母 (+15)")
        if re.search(r'[0-9]', password):
            score += 15
            details.append("数字 (+15)")
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 20
            details.append("特殊字符 (+20)")

        if password.lower() in [w.lower() for w in PasswordSecurityTool.弱密码列表]:
            score = min(score, 20)
            details.append("常见弱密码 (扣分至20)")

        if score < 40:
            level = "弱"
        elif score < 70:
            level = "中"
        else:
            level = "强"

        return {"score": score, "level": level, "details": details}

    @staticmethod
    def generate_password(length: int = 16, use_upper: bool = True,
                          use_lower: bool = True, use_digits: bool = True,
                          use_special: bool = True) -> str:
        """生成随机密码"""
        chars = ""
        if use_upper:
            chars += string.ascii_uppercase
        if use_lower:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_special:
            chars += "!@#$%^&*()"

        if not chars:
            chars = string.ascii_lowercase

        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def hash_password(password: str, algorithm: str = "sha256",
                      salt: str = None) -> str:
        """生成密码哈希"""
        algos = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }
        if algorithm not in algos:
            raise ValueError(f"不支持的算法: {algorithm}")

        data = password.encode()
        if salt:
            data = (salt + password).encode()

        return algos[algorithm](data).hexdigest()

    @staticmethod
    def generate_dictionary(base_words: List[str], output_file: str = None) -> List[str]:
        """生成简易字典"""
        suffixes = [
            "", "123", "1234", "123456", "!", "@", "#",
            "2024", "2023", "2022", "_123", ".123",
        ]
        result = []
        for word in base_words:
            for suf in suffixes:
                result.append(word + suf)
                result.append(word.capitalize() + suf)
                result.append(word.upper() + suf)

        if output_file:
            with open(output_file, 'w') as f:
                for pwd in result:
                    f.write(pwd + '\n')
            print(f"[*] 字典已保存到: {output_file} ({len(result)} 条)")

        return result


# ============================================================
# 工具4: 网络协议解析器
# ============================================================

class NetworkProtocolParser:
    """网络协议头部解析工具"""

    @staticmethod
    def parse_ip_header(data: bytes) -> Dict[str, any]:
        """解析IPv4头部"""
        if len(data) < 20:
            return {"error": "数据太短"}

        version_ihl = data[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0x0F
        total_length = struct.unpack('!H', data[2:4])[0]
        ttl = data[8]
        protocol = data[9]
        src_ip = socket.inet_ntoa(data[12:16])
        dst_ip = socket.inet_ntoa(data[16:20])

        proto_map = {1: "ICMP", 6: "TCP", 17: "UDP", 2: "IGMP", 89: "OSPF"}

        return {
            "version": f"IPv{version}",
            "header_length": ihl * 4,
            "total_length": total_length,
            "ttl": ttl,
            "protocol": proto_map.get(protocol, f"Unknown({protocol})"),
            "source_ip": src_ip,
            "destination_ip": dst_ip,
        }

    @staticmethod
    def parse_tcp_header(data: bytes) -> Dict[str, any]:
        """解析TCP头部"""
        if len(data) < 20:
            return {"error": "数据太短"}

        src_port = struct.unpack('!H', data[0:2])[0]
        dst_port = struct.unpack('!H', data[2:4])[0]
        seq_num = struct.unpack('!I', data[4:8])[0]
        ack_num = struct.unpack('!I', data[8:12])[0]
        data_offset = (data[12] >> 4) * 4
        flags_byte = data[13]

        flags = []
        if flags_byte & 0x01:
            flags.append("FIN")
        if flags_byte & 0x02:
            flags.append("SYN")
        if flags_byte & 0x04:
            flags.append("RST")
        if flags_byte & 0x08:
            flags.append("PSH")
        if flags_byte & 0x10:
            flags.append("ACK")
        if flags_byte & 0x20:
            flags.append("URG")

        return {
            "source_port": src_port,
            "destination_port": dst_port,
            "sequence_number": seq_num,
            "ack_number": ack_num,
            "header_length": data_offset,
            "flags": flags,
        }

    @staticmethod
    def parse_udp_header(data: bytes) -> Dict[str, any]:
        """解析UDP头部"""
        if len(data) < 8:
            return {"error": "数据太短"}

        src_port = struct.unpack('!H', data[0:2])[0]
        dst_port = struct.unpack('!H', data[2:4])[0]
        length = struct.unpack('!H', data[4:6])[0]
        checksum = struct.unpack('!H', data[6:8])[0]

        return {
            "source_port": src_port,
            "destination_port": dst_port,
            "length": length,
            "checksum": hex(checksum),
        }

    @staticmethod
    def demo_parse():
        """演示协议解析"""
        print("\n[*] 网络协议解析演示")
        print("=" * 50)

        # 构造模拟IP头部
        ip_header = struct.pack('!BBHHHBBH4s4s',
            0x45, 0x00, 0x003C, 0x1234, 0x0000,
            0x40, 6, 0x0000,
            socket.inet_aton("192.168.1.100"),
            socket.inet_aton("192.168.1.1"))

        print("\n[IPv4 头部解析]")
        result = NetworkProtocolParser.parse_ip_header(ip_header)
        for k, v in result.items():
            print(f"  {k}: {v}")

        # 构造模拟TCP头部
        tcp_header = struct.pack('!HHIIBBHHH',
            54321, 80, 1000, 2000,
            (5 << 4), 0x12, 8192, 0, 0)

        print("\n[TCP 头部解析]")
        result = NetworkProtocolParser.parse_tcp_header(tcp_header)
        for k, v in result.items():
            print(f"  {k}: {v}")

        print()


# ============================================================
# 工具5: 编码解码工具集
# ============================================================

class CodecToolkit:
    """编码解码工具集合"""

    @staticmethod
    def base64_encode(data: str) -> str:
        return base64.b64encode(data.encode()).decode()

    @staticmethod
    def base64_decode(data: str) -> str:
        return base64.b64decode(data.encode()).decode()

    @staticmethod
    def base32_encode(data: str) -> str:
        return base64.b32encode(data.encode()).decode()

    @staticmethod
    def base32_decode(data: str) -> str:
        return base64.b32decode(data.encode()).decode()

    @staticmethod
    def hex_encode(data: str) -> str:
        return data.encode().hex()

    @staticmethod
    def hex_decode(data: str) -> str:
        return bytes.fromhex(data).decode()

    @staticmethod
    def caesar_encrypt(text: str, shift: int = 3) -> str:
        result = []
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr((ord(c) - base + shift) % 26 + base))
            else:
                result.append(c)
        return ''.join(result)

    @staticmethod
    def caesar_decrypt(text: str, shift: int = 3) -> str:
        return CodecToolkit.caesar_encrypt(text, -shift)

    @staticmethod
    def caesar_brute_force(ciphertext: str) -> List[Tuple[int, str]]:
        """凯撒密码爆破（所有25种位移）"""
        results = []
        for shift in range(1, 26):
            plain = CodecToolkit.caesar_decrypt(ciphertext, shift)
            results.append((shift, plain))
        return results

    @staticmethod
    def url_encode(text: str) -> str:
        from urllib.parse import quote
        return quote(text)

    @staticmethod
    def url_decode(text: str) -> str:
        from urllib.parse import unquote
        return unquote(text)

    @staticmethod
    def demo():
        """演示各种编解码"""
        print("\n[*] 编码解码工具演示")
        print("=" * 50)
        text = "Hello, Network Security!"

        print(f"\n原文: {text}")
        print(f"Base64: {CodecToolkit.base64_encode(text)}")
        print(f"Base32: {CodecToolkit.base32_encode(text)}")
        print(f"Hex: {CodecToolkit.hex_encode(text)}")
        print(f"凯撒(3): {CodecToolkit.caesar_encrypt(text, 3)}")
        print(f"URL编码: {CodecToolkit.url_encode(text)}")


# ============================================================
# 工具6: 主机存活探测
# ============================================================

class HostDiscovery:
    """主机存活探测工具"""

    @staticmethod
    def ping_sweep(network: str, timeout: float = 1.0) -> List[str]:
        """
        Ping扫描（模拟）
        真实环境使用 icmplib 或 python-nmap
        """
        print(f"\n[*] Ping扫描网段: {network}")
        print("[*] 注意：本功能为模拟演示")
        print()

        # 模拟存活主机
        base = network.rsplit('.', 1)[0]
        alive = [f"{base}.{i}" for i in [1, 2, 10, 25, 50, 100, 254]
                 if random.random() > 0.3]

        for ip in alive:
            print(f"  [+] {ip} 存活")

        print(f"\n[*] 发现 {len(alive)} 台存活主机")
        return alive

    @staticmethod
    def arp_scan(interface: str = "eth0") -> List[Tuple[str, str]]:
        """
        ARP扫描（模拟）
        真实环境使用 scapy
        """
        print(f"\n[*] ARP扫描接口: {interface}")
        print("[*] 注意：本功能为模拟演示")
        print()

        # 模拟ARP结果
        results = [
            ("192.168.1.1", "00:11:22:33:44:55"),
            ("192.168.1.10", "aa:bb:cc:dd:ee:ff"),
            ("192.168.1.100", "11:22:33:44:55:66"),
        ]

        for ip, mac in results:
            print(f"  [+] {ip:15s} -> {mac}")

        print(f"\n[*] 发现 {len(results)} 台主机")
        return results


# ============================================================
# 主菜单
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("网络安全工具包 (Network Security Toolkit)")
    print("=" * 60)
    print("""
请选择工具:
  1. 端口扫描器
  2. 子域名爆破器
  3. 密码安全工具
  4. 网络协议解析器
  5. 编码解码工具集
  6. 主机存活探测
  7. 运行全部演示
  0. 退出
""")

    while True:
        try:
            choice = input("\n请输入选项 (0-7): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if choice == "0":
            print("再见！")
            break

        elif choice == "1":
            target = input("目标IP/域名: ").strip() or "127.0.0.1"
            ports = input("端口范围 (1-1024): ").strip() or "1-1024"
            start, end = map(int, ports.split('-'))
            scanner = PortScanner(target, (start, end), threads=30, timeout=0.5)
            scanner.scan()

        elif choice == "2":
            domain = input("目标域名: ").strip() or "example.com"
            brute = SubdomainBruteForcer(domain, threads=15, timeout=1.0)
            brute.brute_force()

        elif choice == "3":
            print("\n  密码安全工具")
            print("  1. 密码强度检测")
            print("  2. 生成随机密码")
            print("  3. 哈希计算")
            sub = input("  选择: ").strip()
            if sub == "1":
                pwd = input("  输入密码: ").strip()
                result = PasswordSecurityTool.check_strength(pwd)
                print(f"\n  密码: {pwd}")
                print(f"  强度: {result['level']} ({result['score']}/100)")
                print("  详情:")
                for d in result['details']:
                    print(f"    - {d}")
            elif sub == "2":
                length = int(input("  长度: ").strip() or "16")
                pwd = PasswordSecurityTool.generate_password(length)
                print(f"\n  生成密码: {pwd}")
            elif sub == "3":
                pwd = input("  输入密码: ").strip()
                for alg in ["md5", "sha1", "sha256", "sha512"]:
                    h = PasswordSecurityTool.hash_password(pwd, alg)
                    print(f"    {alg:8s}: {h}")

        elif choice == "4":
            NetworkProtocolParser.demo_parse()

        elif choice == "5":
            CodecToolkit.demo()

        elif choice == "6":
            net = input("目标网段 (如 192.168.1.0): ").strip() or "192.168.1.0"
            HostDiscovery.ping_sweep(net)
            HostDiscovery.arp_scan()

        elif choice == "7":
            print("\n[*] 运行全部工具演示...\n")
            PortScanner("127.0.0.1", (20, 100), threads=10, timeout=0.3).scan()
            SubdomainBruteForcer("example.com", ["www", "mail", "ftp", "test", "dev"], threads=5).brute_force()
            NetworkProtocolParser.demo_parse()
            CodecToolkit.demo()
            HostDiscovery.ping_sweep("192.168.1.0")
            print("\n[*] 全部演示完成！")

        else:
            print("无效选项，请重新输入")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
