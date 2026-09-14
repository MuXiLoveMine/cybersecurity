# -*- coding: utf-8 -*-
"""
=============================================================================
基础网络安全实战案例
=============================================================================

安全声明：
    本文件仅用于授权安全测试和教育目的。
    所有代码均为教学演示，使用模拟数据，不涉及真实系统或网络。
    未经授权对他人系统进行安全测试是违法行为，请务必在获得书面授权后
    进行安全评估工作。作者不对任何滥用本代码的行为负责。

功能概览：
    1. 网络协议分析工具 - TCP/IP协议栈解析、数据包结构分析、常见协议识别
    2. 端口扫描与服务探测 - TCP连接扫描、SYN半开扫描、服务版本识别
    3. Linux系统安全审计 - 用户权限检查、文件权限审计、服务配置核查
    4. Python安全编程实践 - 输入验证、加密使用、安全编码规范检查
    5. Shell脚本安全审计 - 命令注入检测、变量引用检查、安全脚本编写
    6. 密码安全与身份认证 - 密码强度检测、哈希算法对比、多因素认证模拟

作者：基础网络安全学习工具
版本：1.0.0
日期：2024-01-01
=============================================================================
"""

import os
import re
import sys
import json
import hashlib
import base64
import socket
import struct
import random
import string
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict


# ============================================================================
#  模拟数据定义区
# ============================================================================

# 模拟网络数据包捕获
模拟网络数据包 = [
    {
        "序号": 1,
        "时间": "0.000000",
        "源IP": "192.168.1.100",
        "目的IP": "192.168.1.1",
        "协议": "TCP",
        "源端口": 54321,
        "目的端口": 80,
        "标志位": "SYN",
        "长度": 64,
        "载荷": ""
    },
    {
        "序号": 2,
        "时间": "0.001234",
        "源IP": "192.168.1.1",
        "目的IP": "192.168.1.100",
        "协议": "TCP",
        "源端口": 80,
        "目的端口": 54321,
        "标志位": "SYN-ACK",
        "长度": 64,
        "载荷": ""
    },
    {
        "序号": 3,
        "时间": "0.001567",
        "源IP": "192.168.1.100",
        "目的IP": "192.168.1.1",
        "协议": "TCP",
        "源端口": 54321,
        "目的端口": 80,
        "标志位": "ACK",
        "长度": 52,
        "载荷": ""
    },
    {
        "序号": 4,
        "时间": "0.002000",
        "源IP": "192.168.1.100",
        "目的IP": "192.168.1.1",
        "协议": "HTTP",
        "源端口": 54321,
        "目的端口": 80,
        "标志位": "PSH-ACK",
        "长度": 320,
        "载荷": "GET /index.html HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0\r\nAccept: text/html\r\nCookie: sessionid=abc123xyz\r\n"
    },
    {
        "序号": 5,
        "时间": "0.025000",
        "源IP": "192.168.1.1",
        "目的IP": "192.168.1.100",
        "协议": "HTTP",
        "源端口": 80,
        "目的端口": 54321,
        "标志位": "PSH-ACK",
        "长度": 512,
        "载荷": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nSet-Cookie: sessionid=def456uvw\r\n\r\n<html><body>Hello World</body></html>"
    },
    {
        "序号": 6,
        "时间": "0.100000",
        "源IP": "192.168.1.100",
        "目的IP": "8.8.8.8",
        "协议": "DNS",
        "源端口": 5353,
        "目的端口": 53,
        "标志位": "-",
        "长度": 78,
        "载荷": "查询: www.google.com A记录"
    },
    {
        "序号": 7,
        "时间": "0.150000",
        "源IP": "10.0.0.5",
        "目的IP": "10.0.0.255",
        "协议": "ARP",
        "源端口": 0,
        "目的端口": 0,
        "标志位": "请求",
        "长度": 42,
        "载荷": "Who has 10.0.0.1? Tell 10.0.0.5"
    },
    {
        "序号": 8,
        "时间": "0.200000",
        "源IP": "192.168.1.100",
        "目的IP": "192.168.1.1",
        "协议": "FTP",
        "源端口": 54322,
        "目的端口": 21,
        "标志位": "PSH-ACK",
        "长度": 95,
        "载荷": "USER admin\r\nPASS Admin@123\r\n"
    }
]

# 模拟Linux系统配置
模拟Linux系统配置 = {
    "用户信息": [
        {"用户名": "root", "UID": 0, "GID": 0, "Shell": "/bin/bash", "家目录": "/root", "状态": "正常"},
        {"用户名": "admin", "UID": 1000, "GID": 1000, "Shell": "/bin/bash", "家目录": "/home/admin", "状态": "正常"},
        {"用户名": "testuser", "UID": 1001, "GID": 1001, "Shell": "/bin/bash", "家目录": "/home/testuser", "状态": "正常"},
        {"用户名": "backdoor", "UID": 0, "GID": 0, "Shell": "/bin/bash", "家目录": "/tmp/.backdoor", "状态": "可疑"},
        {"用户名": "www-data", "UID": 33, "GID": 33, "Shell": "/usr/sbin/nologin", "家目录": "/var/www", "状态": "正常"},
    ],
    "SUID文件": [
        "/usr/bin/passwd",
        "/usr/bin/sudo",
        "/usr/bin/su",
        "/tmp/.hidden/shell",
        "/usr/bin/find",
        "/home/user/.bashrc",
    ],
    "监听端口": [
        {"端口": 22, "服务": "ssh", "地址": "0.0.0.0", "状态": "正常"},
        {"端口": 80, "服务": "http", "地址": "0.0.0.0", "状态": "正常"},
        {"端口": 443, "服务": "https", "地址": "0.0.0.0", "状态": "正常"},
        {"端口": 3306, "服务": "mysql", "地址": "0.0.0.0", "状态": "风险"},
        {"端口": 4444, "服务": "unknown", "地址": "0.0.0.0", "状态": "可疑"},
        {"端口": 6379, "服务": "redis", "地址": "127.0.0.1", "状态": "正常"},
    ],
    "计划任务": [
        {"用户": "root", "时间": "*/5 * * * *", "命令": "/usr/bin/apt-get update", "状态": "正常"},
        {"用户": "www-data", "时间": "0 3 * * *", "命令": "/var/www/backup.sh", "状态": "正常"},
        {"用户": "root", "时间": "@reboot", "命令": "/tmp/.hidden/backdoor.sh", "状态": "可疑"},
    ]
}

# 常见端口与服务映射
常见端口服务 = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
}

# 密码强度字典
弱密码字典 = [
    "password", "123456", "12345678", "qwerty", "abc123",
    "admin", "letmein", "welcome", "monkey", "dragon",
    "111111", "iloveyou", "sunshine", "princess", "football"
]


# ============================================================================
#  案例1: 网络协议分析工具
# ============================================================================

class 网络协议分析器:
    """
    网络协议分析实战工具

    功能:
    1. 解析TCP/IP协议栈各层头部
    2. 识别常见网络攻击特征
    3. HTTP会话分析
    4. 异常流量检测
    """

    def __init__(self):
        self.数据包列表 = []
        self.统计信息 = defaultdict(int)

    def 加载数据包(self, 数据包列表):
        self.数据包列表 = 数据包列表
        print(f"[*] 已加载 {len(数据包列表)} 个数据包")

    def 协议统计(self):
        """统计各协议数据包数量"""
        print("\n" + "=" * 60)
        print("协议分布统计")
        print("=" * 60)

        协议统计 = defaultdict(int)
        总字节数 = 0

        for pkt in self.数据包列表:
            协议统计[pkt["协议"]] += 1
            总字节数 += pkt["长度"]

        for 协议, 数量 in sorted(协议统计.items(), key=lambda x: x[1], reverse=True):
            百分比 = (数量 / len(self.数据包列表)) * 100
            print(f"  {协议:8s}: {数量:3d} 个 ({百分比:5.1f}%)")

        print(f"\n总数据包数: {len(self.数据包列表)}")
        print(f"总字节数: {总字节数} bytes ({总字节数/1024:.2f} KB)")

    def TCP握手分析(self):
        """分析TCP三次握手过程"""
        print("\n" + "=" * 60)
        print("TCP 三次握手分析")
        print("=" * 60)

        syn包 = [p for p in self.数据包列表 if p["协议"] == "TCP" and p["标志位"] == "SYN"]
        synack包 = [p for p in self.数据包列表 if p["协议"] == "TCP" and p["标志位"] == "SYN-ACK"]
        ack包 = [p for p in self.数据包列表 if p["协议"] == "TCP" and p["标志位"] == "ACK"]

        print(f"  SYN包数量: {len(syn包)}")
        print(f"  SYN-ACK包数量: {len(synack包)}")
        print(f"  ACK包数量: {len(ack包)}")

        if syn包 and synack包:
            print("\n  [✓] 检测到完整TCP连接建立过程")
            print(f"      客户端: {syn包[0]['源IP']}:{syn包[0]['源端口']}")
            print(f"      服务端: {syn包[0]['目的IP']}:{syn包[0]['目的端口']}")
        else:
            print("\n  [!] 未检测到完整TCP握手")

    def HTTP会话分析(self):
        """分析HTTP请求和响应"""
        print("\n" + "=" * 60)
        print("HTTP 会话分析")
        print("=" * 60)

        http包 = [p for p in self.数据包列表 if p["协议"] == "HTTP" and p["载荷"]]

        for pkt in http包:
            载荷 = pkt["载荷"]
            if 载荷.startswith("GET") or 载荷.startswith("POST"):
                print(f"\n  [请求] {pkt['源IP']} -> {pkt['目的IP']}")
                行列表 = 载荷.strip().split("\r\n")
                print(f"      方法: {行列表[0]}")

                # 检测敏感信息
                if "Cookie:" in 载荷:
                    cookie_match = re.search(r'Cookie:\s*(.+)', 载荷)
                    if cookie_match:
                        print(f"      [!] 发现Cookie: {cookie_match.group(1)[:50]}...")

            elif 载荷.startswith("HTTP"):
                print(f"\n  [响应] {pkt['源IP']} -> {pkt['目的IP']}")
                行列表 = 载荷.strip().split("\r\n")
                print(f"      状态: {行列表[0]}")

                if "Set-Cookie:" in 载荷:
                    print(f"      [!] 服务器设置了新Cookie")

    def 敏感信息检测(self):
        """检测数据包中的敏感信息"""
        print("\n" + "=" * 60)
        print("敏感信息检测")
        print("=" * 60)

        敏感模式 = [
            ("明文密码", r'(PASS|pass|password|pwd)\s*[:=]\s*\S+'),
            ("Cookie/Session", r'(Cookie|Set-Cookie|sessionid)\s*[:=]\s*\S+'),
            ("授权令牌", r'(Authorization|token|Bearer)\s*[:=]\s*\S+'),
            ("SQL语句", r'(SELECT|INSERT|UPDATE|DELETE)\s+.+'),
            ("IP地址", r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
        ]

        发现数 = 0
        for pkt in self.数据包列表:
            if not pkt["载荷"]:
                continue

            for 类型, 模式 in 敏感模式:
                matches = re.findall(模式, pkt["载荷"], re.IGNORECASE)
                if matches:
                    发现数 += len(matches)
                    print(f"\n  [!] 数据包 #{pkt['序号']} 发现{类型}:")
                    for m in matches[:3]:
                        m_str = str(m) if isinstance(m, str) else str(m[0] if isinstance(m, tuple) else m)
                        print(f"      - {m_str[:60]}")

        if 发现数 == 0:
            print("  [✓] 未检测到敏感信息泄露")
        else:
            print(f"\n  共发现 {发现数} 处敏感信息")

    def 运行全部分析(self):
        self.协议统计()
        self.TCP握手分析()
        self.HTTP会话分析()
        self.敏感信息检测()


# ============================================================================
#  案例2: 端口扫描与服务探测
# ============================================================================

class 端口扫描器:
    """
    端口扫描与服务探测实战工具

    功能:
    1. TCP连接扫描模拟
    2. SYN半开扫描原理演示
    3. 服务版本识别
    4. 常见漏洞端口标记
    """

    def __init__(self, 目标IP="192.168.1.100"):
        self.目标IP = 目标IP
        self.扫描结果 = []

    def TCP连接扫描(self, 端口范围=(1, 1024)):
        """模拟TCP全连接扫描"""
        print("\n" + "=" * 60)
        print(f"TCP 全连接扫描 - 目标: {self.目标IP}")
        print("=" * 60)

        print(f"  端口范围: {端口范围[0]} - {端口范围[1]}")
        print(f"  扫描类型: TCP Connect()")
        print()

        # 模拟开放端口（基于常见端口）
        开放端口 = [22, 80, 443, 3306, 8080]
        过滤端口 = [135, 139, 445]

        print(f"  {'端口':<8} {'状态':<10} {'服务':<15} {'说明'}")
        print(f"  {'-'*8} {'-'*10} {'-'*15} {'-'*20}")

        for 端口 in range(端口范围[0], 端口范围[1] + 1):
            if 端口 in 开放端口:
                服务 = 常见端口服务.get(端口, "unknown")
                self.扫描结果.append({"端口": 端口, "状态": "open", "服务": 服务})
                print(f"  {端口:<8} {'open':<10} {服务:<15} 端口开放")
            elif 端口 in 过滤端口:
                print(f"  {端口:<8} {'filtered':<10} {'-':<15} 被过滤")
            # 其他端口默认关闭，不打印

        print(f"\n  扫描完成: 发现 {len(开放端口)} 个开放端口")

    def SYN扫描演示(self):
        """演示SYN半开扫描原理"""
        print("\n" + "=" * 60)
        print("SYN 半开扫描原理演示")
        print("=" * 60)

        print("""
  SYN扫描（半开扫描）原理：
  ┌─────────────┐         SYN         ┌─────────────┐
  │  扫描主机    │ ─────────────────> │  目标主机    │
  └─────────────┘                    └─────────────┘

  端口开放情况:
  - 开放: 目标返回 SYN-ACK → 扫描器发送 RST 断开连接
  - 关闭: 目标返回 RST
  - 过滤: 无响应/ICMP不可达

  优点: 不建立完整连接，更隐蔽
  缺点: 需要raw socket权限，可能被IDS检测到
        """)

        # 模拟SYN扫描结果
        目标端口 = [22, 23, 80, 443, 3389]
        print(f"  模拟SYN扫描结果 (目标: {self.目标IP}):")
        print(f"  {'端口':<8} {'响应':<12} {'状态':<10}")
        print(f"  {'-'*8} {'-'*12} {'-'*10}")

        模拟响应 = {
            22: "SYN-ACK",
            23: "RST",
            80: "SYN-ACK",
            443: "SYN-ACK",
            3389: "无响应"
        }

        状态映射 = {
            "SYN-ACK": "open",
            "RST": "closed",
            "无响应": "filtered"
        }

        for 端口 in 目标端口:
            响应 = 模拟响应[端口]
            状态 = 状态映射[响应]
            print(f"  {端口:<8} {响应:<12} {状态:<10}")

    def 服务版本识别(self):
        """模拟服务版本探测"""
        print("\n" + "=" * 60)
        print("服务版本识别")
        print("=" * 60)

        服务版本 = {
            22: ("SSH", "OpenSSH 8.2p1 Ubuntu 4ubuntu0.5"),
            80: ("HTTP", "Apache/2.4.41 (Ubuntu)"),
            443: ("HTTPS", "nginx/1.18.0 (Ubuntu) OpenSSL/1.1.1f"),
            3306: ("MySQL", "MySQL 8.0.32-0ubuntu0.20.04.2"),
            8080: ("HTTP-Proxy", "Apache Tomcat/9.0.31"),
        }

        print(f"  {'端口':<8} {'服务':<12} {'版本信息'}")
        print(f"  {'-'*8} {'-'*12} {'-'*40}")

        for 端口, (服务, 版本) in 服务版本.items():
            print(f"  {端口:<8} {服务:<12} {版本}")

        # 漏洞提示
        print("\n  [漏洞提示]")
        漏洞提示 = [
            ("OpenSSH 8.2p1", "CVE-2020-14145 (信息泄露)"),
            ("Apache 2.4.41", "CVE-2021-41773 (路径穿越)"),
            ("MySQL 8.0.32", "需检查是否存在弱口令"),
        ]
        for 服务版本号, 漏洞 in 漏洞提示:
            print(f"    ! {服务版本号}: {漏洞}")

    def 运行全部扫描(self):
        self.TCP连接扫描()
        self.SYN扫描演示()
        self.服务版本识别()


# ============================================================================
#  案例3: Linux系统安全审计
# ============================================================================

class Linux安全审计器:
    """
    Linux系统安全审计实战工具

    功能:
    1. 用户账户安全检查
    2. 文件权限审计
    3. 服务与端口安全
    4. 可疑项检测
    """

    def __init__(self):
        self.系统配置 = 模拟Linux系统配置
        self.风险项 = []

    def 用户账户审计(self):
        """审计用户账户安全"""
        print("\n" + "=" * 60)
        print("用户账户安全审计")
        print("=" * 60)

        print(f"\n  系统用户总数: {len(self.系统配置['用户信息'])}")
        print(f"\n  {'用户名':<15} {'UID':<6} {'GID':<6} {'Shell':<20} {'状态'}")
        print(f"  {'-'*15} {'-'*6} {'-'*6} {'-'*20} {'-'*10}")

        风险UID0 = []
        for 用户 in self.系统配置["用户信息"]:
            print(f"  {用户['用户名']:<15} {用户['UID']:<6} {用户['GID']:<6} {用户['Shell']:<20} {用户['状态']}")
            if 用户["UID"] == 0 and 用户["用户名"] != "root":
                风险UID0.append(用户["用户名"])

        print(f"\n  [检查结果]")
        print(f"    UID=0的用户: {len([u for u in self.系统配置['用户信息'] if u['UID']==0])} 个")

        if 风险UID0:
            print(f"    [!] 风险: 存在非root的UID 0用户: {', '.join(风险UID0)}")
            self.风险项.append(f"非root的UID 0用户: {', '.join(风险UID0)}")
        else:
            print(f"    [✓] 仅root用户UID为0")

        # 检查可登录用户
        可登录用户 = [u["用户名"] for u in self.系统配置["用户信息"] if "nologin" not in u["Shell"] and "false" not in u["Shell"]]
        print(f"    可交互登录用户: {len(可登录用户)} 个 ({', '.join(可登录用户)})")

    def SUID文件审计(self):
        """审计SUID/SGID文件"""
        print("\n" + "=" * 60)
        print("SUID 文件审计")
        print("=" * 60)

        print(f"\n  发现 SUID 文件: {len(self.系统配置['SUID文件'])} 个")

        # 已知安全的SUID程序
        安全SUID = [
            "/usr/bin/passwd", "/usr/bin/sudo", "/usr/bin/su",
            "/usr/bin/mount", "/usr/bin/umount", "/usr/bin/ping"
        ]

        可疑SUID = []
        for 文件 in self.系统配置["SUID文件"]:
            状态 = "正常" if any(文件.endswith(s.split('/')[-1]) for s in 安全SUID) else "可疑"
            if 状态 == "可疑":
                可疑SUID.append(文件)
            标记 = "  " if 状态 == "正常" else "!"
            print(f"    {标记} {文件} [{状态}]")

        if 可疑SUID:
            print(f"\n  [!] 发现 {len(可疑SUID)} 个可疑SUID文件:")
            for f in 可疑SUID:
                print(f"      - {f}")
            self.风险项.append(f"可疑SUID文件: {len(可疑SUID)}个")
        else:
            print(f"\n  [✓] 未发现可疑SUID文件")

    def 端口服务审计(self):
        """审计监听端口和服务"""
        print("\n" + "=" * 60)
        print("端口与服务审计")
        print("=" * 60)

        print(f"\n  {'端口':<8} {'服务':<12} {'监听地址':<15} {'状态':<8} {'说明'}")
        print(f"  {'-'*8} {'-'*12} {'-'*15} {'-'*8} {'-'*20}")

        风险端口 = []
        for 端口信息 in self.系统配置["监听端口"]:
            说明 = ""
            if 端口信息["状态"] == "风险":
                说明 = "数据库端口对外暴露"
                风险端口.append(端口信息)
            elif 端口信息["状态"] == "可疑":
                说明 = "未知服务，建议核查"
                风险端口.append(端口信息)

            print(f"  {端口信息['端口']:<8} {端口信息['服务']:<12} {端口信息['地址']:<15} {端口信息['状态']:<8} {说明}")

        if 风险端口:
            self.风险项.append(f"风险端口: {len(风险端口)}个")

    def 计划任务审计(self):
        """审计计划任务"""
        print("\n" + "=" * 60)
        print("计划任务审计")
        print("=" * 60)

        可疑任务 = []
        for 任务 in self.系统配置["计划任务"]:
            print(f"\n  用户: {任务['用户']}")
            print(f"  时间: {任务['时间']}")
            print(f"  命令: {任务['命令']}")
            print(f"  状态: {任务['状态']}")

            if 任务["状态"] == "可疑":
                可疑任务.append(任务)

        if 可疑任务:
            print(f"\n  [!] 发现 {len(可疑任务)} 个可疑计划任务")
            self.风险项.append(f"可疑计划任务: {len(可疑任务)}个")

    def 生成审计报告(self):
        """生成安全审计报告"""
        print("\n" + "=" * 60)
        print("Linux 安全审计报告")
        print("=" * 60)

        print(f"\n  审计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  审计项目: 用户账户、SUID文件、端口服务、计划任务")
        print(f"  发现风险: {len(self.风险项)} 项")

        if self.风险项:
            print(f"\n  风险清单:")
            for i, 风险 in enumerate(self.风险项, 1):
                print(f"    {i}. {风险}")

        print(f"\n  安全建议:")
        print(f"    1. 删除或禁用不必要的UID 0账户")
        print(f"    2. 移除可疑SUID文件的s权限")
        print(f"    3. 限制数据库端口仅内网访问")
        print(f"    4. 清理可疑计划任务")
        print(f"    5. 启用日志审计功能")

    def 运行全部审计(self):
        self.用户账户审计()
        self.SUID文件审计()
        self.端口服务审计()
        self.计划任务审计()
        self.生成审计报告()


# ============================================================================
#  案例4: 密码安全与身份认证
# ============================================================================

class 密码安全工具:
    """
    密码安全与身份认证实战工具

    功能:
    1. 密码强度检测
    2. 哈希算法对比演示
    3. 彩虹表攻击模拟
    4. 多因素认证模拟
    """

    def __init__(self):
        self.弱密码集 = set(弱密码字典)

    def 密码强度检测(self, 密码=""):
        """检测密码强度"""
        print("\n" + "=" * 60)
        print("密码强度检测")
        print("=" * 60)

        if not 密码:
            测试密码 = [
                "123456",
                "password",
                "abc123",
                "P@ssw0rd",
                "MyStr0ngP@ss!",
                "K9#mP2$xL8!qR7",
            ]
        else:
            测试密码 = [密码]

        print(f"\n  {'密码':<25} {'长度':<6} {'强度':<10} {'评分'}")
        print(f"  {'-'*25} {'-'*6} {'-'*10} {'-'*20}")

        for pwd in 测试密码:
            评分, 强度, 详情 = self._评估密码(pwd)
            进度条 = "█" * int(评分 / 5) + "░" * (20 - int(评分 / 5))
            print(f"  {pwd:<25} {len(pwd):<6} {强度:<10} {进度条} {评分}/100")

        print(f"\n  密码强度评估标准:")
        print(f"    弱: 0-40分 (短/简单/常见)")
        print(f"    中: 41-70分 (长度够但复杂度不足)")
        print(f"    强: 71-100分 (长且复杂，含多种字符)")

    def _评估密码(self, 密码):
        """内部密码评估函数"""
        评分 = 0
        详情 = []

        # 长度评分
        长度 = len(密码)
        if 长度 >= 12:
            评分 += 25
        elif 长度 >= 8:
            评分 += 15
        elif 长度 >= 6:
            评分 += 5

        # 字符类型评分
        if re.search(r'[a-z]', 密码):
            评分 += 10
        if re.search(r'[A-Z]', 密码):
            评分 += 15
        if re.search(r'[0-9]', 密码):
            评分 += 15
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', 密码):
            评分 += 20

        # 常见密码扣分
        if 密码.lower() in self.弱密码集:
            评分 = min(评分, 20)

        # 强度等级
        if 评分 < 40:
            强度 = "弱"
        elif 评分 < 70:
            强度 = "中"
        else:
            强度 = "强"

        return 评分, 强度, 详情

    def 哈希算法对比(self):
        """对比不同哈希算法的安全性"""
        print("\n" + "=" * 60)
        print("哈希算法安全对比")
        print("=" * 60)

        测试密码 = "P@ssw0rd123"
        print(f"\n  测试密码: {测试密码}")
        print()

        算法列表 = [
            ("MD5", hashlib.md5),
            ("SHA-1", hashlib.sha1),
            ("SHA-256", hashlib.sha256),
            ("SHA-512", hashlib.sha512),
        ]

        print(f"  {'算法':<12} {'哈希值':<64} {'长度(bit)':<10} {'安全性'}")
        print(f"  {'-'*12} {'-'*64} {'-'*10} {'-'*10}")

        安全性 = {
            "MD5": "不安全",
            "SHA-1": "弱",
            "SHA-256": "安全",
            "SHA-512": "高安全"
        }

        for 名称, 算法 in 算法列表:
            哈希值 = 算法(测试密码.encode()).hexdigest()
            bit长度 = len(哈希值) * 4
            print(f"  {名称:<12} {哈希值:<64} {bit长度:<10} {安全性[名称]}")

        print(f"""
  安全建议:
    - 绝对不要使用MD5存储密码
    - SHA-1已被破解，不推荐使用
    - 推荐使用 SHA-256 或更高版本
    - 密码存储应使用加盐哈希 (bcrypt/scrypt/Argon2)
        """)

    def 加盐哈希演示(self):
        """演示加盐哈希的原理"""
        print("\n" + "=" * 60)
        print("加盐哈希原理演示")
        print("=" * 60)

        密码 = "user_password"
        print(f"\n  原始密码: {密码}")

        # 无盐哈希
        无盐哈希 = hashlib.sha256(密码.encode()).hexdigest()
        print(f"\n  无盐 SHA-256:")
        print(f"    哈希值: {无盐哈希}")

        # 加盐哈希
        import secrets
        salt = secrets.token_hex(16)
        加盐密码 = (密码 + salt).encode()
        加盐哈希 = hashlib.sha256(加盐密码).hexdigest()

        print(f"\n  加盐 SHA-256:")
        print(f"    盐值: {salt}")
        print(f"    哈希值: {加盐哈希}")

        # 另一个盐值
        salt2 = secrets.token_hex(16)
        加盐哈希2 = hashlib.sha256((密码 + salt2).encode()).hexdigest()

        print(f"\n  不同盐值的相同密码:")
        print(f"    盐值: {salt2}")
        print(f"    哈希值: {加盐哈希2}")

        print(f"""
  加盐的作用:
    - 相同密码因盐值不同产生不同哈希
    - 有效抵御彩虹表攻击
    - 每个用户应使用独立的随机盐
        """)

    def 多因素认证模拟(self):
        """模拟多因素认证流程"""
        print("\n" + "=" * 60)
        print("多因素认证 (MFA) 模拟")
        print("=" * 60)

        print("""
  MFA 认证因素类型:
    1. 知识因素 (Something you know): 密码、PIN码
    2. 持有因素 (Something you have): 手机、令牌、U盾
    3. 生物因素 (Something you are): 指纹、人脸、虹膜
    4. 位置因素 (Somewhere you are): IP地址、地理位置
    5. 行为因素 (Something you do): 打字习惯、操作模式
        """)

        # 模拟TOTP
        print("  模拟 TOTP (基于时间的一次性密码):")
        print()

        # 生成伪TOTP码
        时间戳 = int(datetime.now().timestamp() / 30)
        seed = "JBSWY3DPEHPK3PXP"  # 示例密钥
        totp_input = f"{时间戳}{seed}".encode()
        totp_hash = hashlib.sha1(totp_input).hexdigest()
        # 简单的TOTP生成模拟
        offset = int(totp_hash[-1], 16)
        binary = int(totp_hash[offset * 2:offset * 2 + 8], 16) & 0x7fffffff
        totp_code = str(binary % 1000000).zfill(6)

        print(f"    密钥: {seed}")
        print(f"    当前时间片: {时间戳}")
        print(f"    TOTP验证码: {totp_code[:3]} {totp_code[3:]}")
        print(f"    有效期: 30秒")

        print(f"""
  常见MFA方式对比:
    - 短信验证码: 方便但易被劫持 (SIM Swap)
    - TOTP (Google Authenticator): 较安全，需设备同步
    - 硬件密钥 (YubiKey): 最安全，防钓鱼
    - 生物识别: 方便但存在隐私问题
        """)

    def 运行全部(self):
        self.密码强度检测()
        self.哈希算法对比()
        self.加盐哈希演示()
        self.多因素认证模拟()


# ============================================================================
#  案例5: Python安全编码检查
# ============================================================================

class Python安全代码审查:
    """
    Python安全编码规范检查工具

    功能:
    1. 常见安全漏洞检测
    2. 不安全函数检测
    3. 输入验证检查
    4. 加密使用规范检查
    """

    def __init__(self):
        self.检测规则 = {
            "命令注入": [
                (r'os\.system\s*\(', "os.system 可能导致命令注入，推荐使用 subprocess"),
                (r'eval\s*\(', "eval() 执行任意代码，存在严重安全风险"),
                (r'exec\s*\(', "exec() 执行任意代码，存在严重安全风险"),
                (r'subprocess\.(call|Popen)\s*\(.*shell\s*=\s*True', "subprocess使用shell=True可能导致命令注入"),
            ],
            "SQL注入": [
                (r'["\'].*\%s.*["\']\s*\%\s*', "字符串拼接SQL查询，存在SQL注入风险"),
                (r'f"[^"]*\{[^}]+\}[^"]*"\s*\.?\s*execute', "f-string拼接SQL，存在SQL注入风险"),
                (r'\+\s*["\'].*SELECT|INSERT|UPDATE|DELETE', "字符串拼接SQL语句"),
            ],
            "路径遍历": [
                (r'open\s*\(\s*request\.', "直接使用用户输入打开文件，可能路径遍历"),
                (r'send_file\s*\(\s*.*\+', "文件路径拼接可能导致路径遍历"),
            ],
            "不安全反序列化": [
                (r'pickle\.loads\s*\(', "pickle反序列化不可信数据可执行任意代码"),
                (r'yaml\.load\s*\(', "yaml.load 不安全，使用 yaml.safe_load"),
            ],
            "弱加密": [
                (r'hashlib\.md5\s*\(', "MD5不安全，用于密码存储请用 bcrypt"),
                (r'hashlib\.sha1\s*\(', "SHA-1已被破解，推荐使用 SHA-256"),
                (r'DES|3DES', "DES/3DES已过时，使用AES"),
            ],
            "XSS风险": [
                (r'render_template_string\s*\(', "模板字符串可能导致XSS"),
                (r'Markup\s*\(', "标记为安全字符串可能导致XSS"),
            ]
        }

    def 扫描代码(self, 代码内容):
        """扫描Python代码中的安全问题"""
        print("\n" + "=" * 60)
        print("Python 安全代码审查")
        print("=" * 60)

        行列表 = 代码内容.split("\n")
        问题总数 = 0

        for 漏洞类型, 规则列表 in self.检测规则.items():
            发现问题 = []
            for 行号, 行内容 in enumerate(行列表, 1):
                for 模式, 说明 in 规则列表:
                    if re.search(模式, 行内容):
                        发现问题.append((行号, 行内容.strip(), 说明))

            if 发现问题:
                print(f"\n  【{漏洞类型}】 - 发现 {len(发现问题)} 处")
                for 行号, 代码, 说明 in 发现问题:
                    print(f"    第{行号}行: {代码[:60]}")
                    print(f"      说明: {说明}")
                问题总数 += len(发现问题)

        if 问题总数 == 0:
            print("\n  [✓] 未发现明显安全问题")
        else:
            print(f"\n  [!] 共发现 {问题总数} 处潜在安全问题")

        return 问题总数

    def 安全编码清单(self):
        """输出Python安全编码清单"""
        print("\n" + "=" * 60)
        print("Python 安全编码清单")
        print("=" * 60)

        清单 = [
            ("输入验证", [
                "始终验证所有外部输入（用户输入、文件、网络数据）",
                "使用白名单验证而非黑名单",
                "限制输入长度和格式",
                "使用类型提示和数据校验库（pydantic, marshmallow）",
            ]),
            ("输出编码", [
                "HTML输出时进行转义，防止XSS",
                "SQL查询使用参数化查询/ORM",
                "Shell命令使用参数列表而非字符串拼接",
            ]),
            ("加密安全", [
                "密码存储使用 bcrypt/scrypt/Argon2",
                "对称加密使用 AES-GCM",
                "使用标准库，不自行实现加密算法",
                "密钥管理使用专用密钥管理服务",
            ]),
            ("依赖安全", [
                "定期更新依赖包",
                "使用 pip-audit/safety 扫描漏洞依赖",
                "使用虚拟环境隔离依赖",
                "锁定依赖版本（requirements.txt / poetry.lock）",
            ]),
            ("文件操作", [
                "验证文件路径，防止路径遍历",
                "限制可访问的目录范围",
                "安全处理文件上传（类型、大小、名称）",
            ]),
        ]

        for 分类, 条目 in 清单:
            print(f"\n  ■ {分类}")
            for 条 in 条目:
                print(f"    □ {条}")

    def 运行演示(self):
        # 示例代码
        示例代码 = '''
import os
import hashlib
import pickle
import subprocess

def login(username, password):
    # SQL注入风险
    sql = "SELECT * FROM users WHERE username='%s'" % username
    cursor.execute(sql)

    # 弱哈希
    hashed = hashlib.md5(password.encode()).hexdigest()

def run_command(cmd):
    # 命令注入
    os.system("ping " + cmd)

def load_data(data):
    # 不安全反序列化
    obj = pickle.loads(data)
'''
        self.扫描代码(示例代码)
        self.安全编码清单()


# ============================================================================
#  主函数
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("基础网络安全实战案例集")
    print("=" * 70)
    print("""
请选择要运行的实战案例:

  1. 网络协议分析工具
  2. 端口扫描与服务探测
  3. Linux系统安全审计
  4. 密码安全与身份认证
  5. Python安全编码检查
  6. 运行全部案例
  0. 退出
""")

    while True:
        try:
            choice = input("\n请输入选项 (0-6): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if choice == "0":
            print("再见！")
            break
        elif choice == "1":
            analyzer = 网络协议分析器()
            analyzer.加载数据包(模拟网络数据包)
            analyzer.运行全部分析()
        elif choice == "2":
            scanner = 端口扫描器()
            scanner.运行全部扫描()
        elif choice == "3":
            auditor = Linux安全审计器()
            auditor.运行全部审计()
        elif choice == "4":
            pwd_tool = 密码安全工具()
            pwd_tool.运行全部()
        elif choice == "5":
            reviewer = Python安全代码审查()
            reviewer.运行演示()
        elif choice == "6":
            print("\n" + "=" * 70)
            print("正在运行全部实战案例...")
            print("=" * 70)

            analyzer = 网络协议分析器()
            analyzer.加载数据包(模拟网络数据包)
            analyzer.运行全部分析()

            scanner = 端口扫描器()
            scanner.运行全部扫描()

            auditor = Linux安全审计器()
            auditor.运行全部审计()

            pwd_tool = 密码安全工具()
            pwd_tool.运行全部()

            reviewer = Python安全代码审查()
            reviewer.运行演示()

            print("\n" + "=" * 70)
            print("所有案例运行完成！")
            print("=" * 70)
        else:
            print("无效选项，请重新输入 (0-6)")

        print("\n" + "-" * 70)


if __name__ == "__main__":
    main()
