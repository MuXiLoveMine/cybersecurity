# -*- coding: utf-8 -*-
"""
=============================================================================
终端安全实战案例
=============================================================================

安全声明：
    本文件仅用于授权安全测试和教育目的。
    所有代码均为教学演示，使用模拟数据，不涉及真实系统或网络。
    未经授权对他人系统进行安全测试是违法行为，请务必在获得书面授权后
    进行安全评估工作。作者不对任何滥用本代码的行为负责。

功能概览：
    1. Windows系统安全基线检查 - 密码策略、审核策略、服务配置、注册表安全
    2. Linux系统安全基线检查 - SSH配置、文件权限、内核参数、用户账户
    3. EDR行为检测模拟 - 进程监控、文件监控、注册表监控、网络连接监控
    4. 恶意代码行为分析 - 进程注入检测、持久化机制检查、网络C2检测
    5. 终端入侵检测规则生成 - 基于MITRE ATT&CK的检测规则
    6. 应急响应取证 - 内存分析、磁盘取证、日志分析

作者：终端安全学习工具
版本：1.0.0
日期：2024-01-01
=============================================================================
"""

import os
import re
import json
import hashlib
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


# ============================================================================
#  模拟数据定义区
# ============================================================================

# 模拟的Windows安全策略配置
模拟Windows安全策略 = {
    "密码策略": {
        "PasswordComplexity": {"当前值": 0, "标准值": 1, "说明": "密码复杂性要求"},
        "MinimumPasswordLength": {"当前值": 0, "标准值": 8, "说明": "最小密码长度"},
        "MinimumPasswordAge": {"当前值": 0, "标准值": 1, "说明": "最小密码年龄(天)"},
        "MaximumPasswordAge": {"当前值": 365, "标准值": 90, "说明": "最大密码年龄(天)"},
        "PasswordHistorySize": {"当前值": 0, "标准值": 5, "说明": "密码历史记录数"},
        "LockoutBadCount": {"当前值": 0, "标准值": 5, "说明": "锁定前错误次数"},
        "ResetLockoutCount": {"当前值": 30, "标准值": 30, "说明": "锁定重置时间(分钟)"},
        "LockoutDuration": {"当前值": 0, "标准值": 30, "说明": "锁定持续时间(分钟)"},
    },
    "审核策略": {
        "AuditSystemEvents": {"当前值": 0, "标准值": 1, "说明": "审核系统事件"},
        "AuditLogonEvents": {"当前值": 0, "标准值": 1, "说明": "审核登录事件"},
        "AuditObjectAccess": {"当前值": 0, "标准值": 1, "说明": "审核对象访问"},
        "AuditPrivilegeUse": {"当前值": 0, "标准值": 1, "说明": "审核特权使用"},
        "AuditPolicyChange": {"当前值": 0, "标准值": 1, "说明": "审核策略更改"},
        "AuditAccountManagement": {"当前值": 0, "标准值": 1, "说明": "审核账户管理"},
        "AuditProcessTracking": {"当前值": 0, "标准值": 1, "说明": "审核进程跟踪"},
    },
    "服务配置": {
        "RemoteRegistry": {"当前值": "Running", "标准值": "Stopped", "说明": "远程注册表服务"},
        "Telnet": {"当前值": "Running", "标准值": "Disabled", "说明": "Telnet服务"},
        "PrintSpooler": {"当前值": "Running", "标准值": "Stopped", "说明": "打印后台服务"},
        "SMB": {"当前值": "Running", "标准值": "Stopped", "说明": "SMB服务"},
        "RemoteDesktop": {"当前值": "Running", "标准值": "Disabled", "说明": "远程桌面服务"},
    },
    "注册表安全": {
        "RestrictAnonymous": {"当前值": 0, "标准值": 1, "说明": "限制匿名访问"},
        "AutoShareWks": {"当前值": 1, "标准值": 0, "说明": "禁止默认管理共享"},
        "AutoShareServer": {"当前值": 1, "标准值": 0, "说明": "禁止默认管理共享"},
        "DisableTaskMgr": {"当前值": 0, "标准值": 1, "说明": "禁用任务管理器(可选)"},
        "NoAutoUpdate": {"当前值": 1, "标准值": 0, "说明": "禁止自动更新"},
    }
}

# 模拟的Linux安全配置
模拟Linux安全配置 = {
    "SSH配置": {
        "PermitRootLogin": {"当前值": "yes", "标准值": "no", "说明": "允许Root登录"},
        "PasswordAuthentication": {"当前值": "yes", "标准值": "no", "说明": "密码认证"},
        "Protocol": {"当前值": "2,1", "标准值": "2", "说明": "SSH协议版本"},
        "MaxAuthTries": {"当前值": "6", "标准值": "3", "说明": "最大认证尝试"},
        "X11Forwarding": {"当前值": "yes", "标准值": "no", "说明": "X11转发"},
        "PermitEmptyPasswords": {"当前值": "yes", "标准值": "no", "说明": "空密码登录"},
        "Port": {"当前值": "22", "标准值": "2222", "说明": "SSH端口"},
        "ClientAliveInterval": {"当前值": "0", "标准值": "300", "说明": "客户端存活间隔"},
    },
    "文件权限": {
        "/etc/passwd": {"当前权限": "644", "标准权限": "644", "说明": "用户信息文件"},
        "/etc/shadow": {"当前权限": "644", "标准权限": "000", "说明": "密码哈希文件"},
        "/etc/group": {"当前权限": "644", "标准权限": "644", "说明": "组信息文件"},
        "/etc/sudoers": {"当前权限": "644", "标准权限": "440", "说明": "sudo配置文件"},
        "/etc/ssh/sshd_config": {"当前权限": "644", "标准权限": "600", "说明": "SSH配置文件"},
        "/etc/crontab": {"当前权限": "644", "标准权限": "600", "说明": "计划任务配置"},
        "/root/.ssh/authorized_keys": {"当前权限": "644", "标准权限": "600", "说明": "SSH公钥"},
        "/var/log/auth.log": {"当前权限": "644", "标准权限": "640", "说明": "认证日志"},
    },
    "内核参数": {
        "net.ipv4.ip_forward": {"当前值": "1", "标准值": "0", "说明": "IP转发"},
        "net.ipv4.tcp_syncookies": {"当前值": "0", "标准值": "1", "说明": "SYN Cookie"},
        "net.ipv4.conf.all.accept_redirects": {"当前值": "1", "标准值": "0", "说明": "接受ICMP重定向"},
        "kernel.randomize_va_space": {"当前值": "0", "标准值": "2", "说明": "地址空间随机化"},
        "fs.suid_dumpable": {"当前值": "1", "标准值": "0", "说明": "SUID转储"},
        "kernel.kptr_restrict": {"当前值": "0", "标准值": "1", "说明": "内核指针限制"},
    },
    "用户账户": [
        {"用户名": "root", "UID": 0, "状态": "已锁定", "说明": "超级用户"},
        {"用户名": "admin", "UID": 0, "状态": "活跃", "说明": "管理员账户(UID=0!)"},
        {"用户名": "test", "UID": 1000, "状态": "活跃", "说明": "测试账户"},
        {"用户名": "guest", "UID": 1001, "状态": "活跃", "说明": "访客账户(空密码)"},
        {"用户名": "appuser", "UID": 1002, "状态": "活跃", "说明": "应用账户"},
        {"用户名": "olduser", "UID": 1003, "状态": "活跃", "说明": "离职用户(未清理)"},
    ]
}

# 模拟的系统进程列表（含恶意进程）
模拟进程列表 = [
    {"PID": 1, "名称": "System", "路径": "C:\\Windows\\System32", "父PID": 0, "正常": True},
    {"PID": 4, "名称": "lsass.exe", "路径": "C:\\Windows\\System32", "父PID": 1, "正常": True},
    {"PID": 540, "名称": "svchost.exe", "路径": "C:\\Windows\\System32", "父PID": 4, "正常": True},
    {"PID": 560, "名称": "explorer.exe", "路径": "C:\\Windows", "父PID": 540, "正常": True},
    {"PID": 1024, "名称": "chrome.exe", "路径": "C:\\Program Files\\Google\\Chrome", "父PID": 560, "正常": True},
    {"PID": 2048, "名称": "svchost.exe", "路径": "C:\\Users\\Public\\Temp", "父PID": 560, "正常": False},
    {"PID": 3072, "名称": "powershell.exe", "路径": "C:\\Windows\\System32", "父PID": 2048, "正常": False},
    {"PID": 4096, "名称": "mshta.exe", "路径": "C:\\Windows\\System32", "父PID": 3072, "正常": False},
    {"PID": 5120, "名称": "conhost.exe", "路径": "C:\\Windows\\System32", "父PID": 4096, "正常": False},
    {"PID": 6144, "名称": "rundll32.exe", "路径": "C:\\Windows\\System32", "父PID": 4096, "正常": False},
    {"PID": 7168, "名称": "mimikatz.exe", "路径": "C:\\Users\\Public\\Temp", "父PID": 6144, "正常": False},
    {"PID": 8192, "名称": "nc.exe", "路径": "C:\\Users\\Public\\Temp", "父PID": 7168, "正常": False},
]

# 模拟的注册表启动项
模拟启动项 = [
    {"位置": "HKLM\\Run", "名称": "SecurityHealth", "值": "C:\\Windows\\System32\\SecurityHealthSystray.exe", "正常": True},
    {"位置": "HKCU\\Run", "名称": "OneDrive", "值": "C:\\Users\\user\\AppData\\Local\\Microsoft\\OneDrive\\OneDrive.exe", "正常": True},
    {"位置": "HKLM\\Run", "名称": "WindowsUpdate", "值": "C:\\Users\\Public\\Temp\\update.exe", "正常": False},
    {"位置": "HKCU\\Run", "名称": "SysHelper", "值": "C:\\Users\\Public\\Temp\\helper.dll", "正常": False},
    {"位置": "HKLM\\RunOnce", "名称": "Setup", "值": "C:\\Users\\Public\\Temp\\setup.exe", "正常": False},
    {"位置": "HKCU\\Run", "名称": "TaskScheduler", "值": "rundll32.exe C:\\Users\\Public\\Temp\\payload.dll,Start", "正常": False},
]

# 模拟的计划任务
模拟计划任务 = [
    {"名称": "GoogleUpdateTaskMachine", "路径": "C:\\Program Files\\Google\\Update\\GoogleUpdate.exe", "正常": True},
    {"名称": "SystemUpdate", "路径": "C:\\Users\\Public\\Temp\\update.exe -silent", "正常": False},
    {"名称": "DiskCleanup", "路径": "powershell -enc cABvAHcAZQByAHMAaABlAGwAbAA=", "正常": False},
    {"名称": "PerformanceMonitor", "路径": "C:\\Users\\Public\\Temp\\monitor.exe", "正常": False},
]

# 模拟的网络连接
模拟网络连接 = [
    {"PID": 1024, "协议": "TCP", "本地": "192.168.1.100:49152", "远程": "172.217.24.14:443", "状态": "ESTABLISHED", "正常": True},
    {"PID": 540, "协议": "TCP", "本地": "192.168.1.100:49153", "远程": "20.42.65.92:443", "状态": "ESTABLISHED", "正常": True},
    {"PID": 8192, "协议": "TCP", "本地": "192.168.1.100:49200", "远程": "45.137.21.9:4444", "状态": "ESTABLISHED", "正常": False},
    {"PID": 8192, "协议": "TCP", "本地": "192.168.1.100:49201", "远程": "45.137.21.9:4445", "状态": "ESTABLISHED", "正常": False},
    {"PID": 2048, "协议": "TCP", "本地": "192.168.1.100:49202", "远程": "193.27.14.7:8080", "状态": "ESTABLISHED", "正常": False},
    {"PID": 3072, "协议": "UDP", "本地": "0.0.0.0:5353", "远程": "*:*", "状态": "LISTENING", "正常": True},
]

# 模拟的事件日志
模拟Windows日志 = [
    {"事件ID": 4624, "类型": "登录成功", "时间": "2024-01-15 08:30:15", "用户": "admin", "来源": "192.168.1.50", "正常": True},
    {"事件ID": 4625, "类型": "登录失败", "时间": "2024-01-15 08:45:22", "用户": "admin", "来源": "192.168.1.50", "正常": True},
    {"事件ID": 4625, "类型": "登录失败", "时间": "2024-01-15 08:45:25", "用户": "admin", "来源": "192.168.1.50", "正常": True},
    {"事件ID": 4625, "类型": "登录失败", "时间": "2024-01-15 08:45:28", "用户": "admin", "来源": "192.168.1.50", "正常": True},
    {"事件ID": 4625, "类型": "登录失败", "时间": "2024-01-15 08:45:31", "用户": "admin", "来源": "192.168.1.50", "正常": True},
    {"事件ID": 4625, "类型": "登录失败", "时间": "2024-01-15 08:45:34", "用户": "admin", "来源": "192.168.1.50", "正常": True},
    {"事件ID": 4624, "类型": "登录成功", "时间": "2024-01-15 08:45:37", "用户": "admin", "来源": "192.168.1.50", "正常": False},
    {"事件ID": 4688, "类型": "进程创建", "时间": "2024-01-15 09:00:01", "用户": "admin", "来源": "powershell.exe", "正常": False},
    {"事件ID": 4697, "类型": "服务安装", "时间": "2024-01-15 09:01:30", "用户": "SYSTEM", "来源": "update.exe", "正常": False},
    {"事件ID": 7045, "类型": "新服务", "时间": "2024-01-15 09:01:30", "用户": "SYSTEM", "来源": "SystemUpdate", "正常": False},
]

# MITRE ATT&CK 技术映射
MITRE_ATTCK映射 = {
    "T1055": {"名称": "进程注入", "战术": "Defense Evasion, Privilege Escalation",
              "描述": "将代码注入到另一个进程中以隐藏恶意行为"},
    "T1547": {"名称": "Boot或Logon自动启动", "战术": "Persistence, Privilege Escalation",
              "描述": "通过注册表Run键、启动文件夹等实现持久化"},
    "T1053": {"名称": "计划任务", "战术": "Persistence, Privilege Escalation",
              "描述": "使用计划任务执行恶意代码"},
    "T1071": {"名称": "标准应用层协议", "战术": "Command and Control",
              "描述": "使用HTTP/HTTPS等标准协议进行C2通信"},
    "T1112": {"名称": "修改注册表", "战术": "Defense Evasion",
              "描述": "修改注册表以隐藏恶意配置或持久化"},
    "T1003": {"名称": "操作系统凭据转储", "战术": "Credential Access",
              "描述": "提取操作系统存储的凭据（如LSASS内存）"},
    "T1546": {"名称": "事件触发执行", "战术": "Persistence, Privilege Escalation",
              "描述": "通过WMI事件订阅、注册表回调等触发执行"},
    "T1059": {"名称": "命令和脚本解释器", "战术": "Execution",
              "描述": "使用PowerShell、cmd等执行恶意命令"},
    "T1021": {"名称": "远程服务", "战术": "Lateral Movement",
              "描述": "使用RDP、SMB等远程协议横向移动"},
    "T1486": {"名称": "磁盘加密", "战术": "Impact",
              "描述": "加密磁盘数据以勒索（勒索软件）"},
}


# ============================================================================
#  第一部分：Windows系统安全基线检查
# ============================================================================

class Windows安全基线检查器:
    """
    Windows系统安全基线检查工具

    功能说明：
        - 检查密码策略是否符合安全标准
        - 验证审核策略是否充分
        - 检查关键服务的运行状态
        - 审查注册表安全配置

    技术原理：
        Windows安全基线是一组安全配置标准，确保系统满足最低安全要求。
        通过secedit、组策略、注册表查询等方式检查系统配置。

        常用检查命令：
        - secedit /export /cfg policy.txt   导出安全策略
        - net accounts                       查看密码策略
        - auditpol /get /category:*         查看审核策略
        - sc query <service>                查询服务状态
        - reg query <key>                   查询注册表
    """

    def __init__(self):
        self.检查结果 = []
        self.不合规数 = 0
        print("[初始化] Windows安全基线检查器已就绪")

    def 检查密码策略(self):
        """
        检查密码策略配置

        技术说明：
            密码策略通过组策略(GPO)或secedit配置，包括：
            - 密码复杂性要求（大小写/数字/特殊字符）
            - 最小密码长度（建议>=8位）
            - 密码最大使用期限（建议<=90天）
            - 密码历史记录（防止重复使用）
            - 账户锁定策略
        """
        print("\n" + "=" * 70)
        print("Windows密码策略检查")
        print("=" * 70)
        print("  检查方法: secedit /export 或 net accounts\n")

        策略 = 模拟Windows安全策略["密码策略"]

        for 名称, 配置 in 策略.items():
            当前值 = 配置["当前值"]
            标准值 = 配置["标准值"]
            说明 = 配置["说明"]
            合规 = (当前值 == 标准值)

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      说明:   {说明}")
            print(f"      当前值: {当前值}")
            print(f"      标准值: {标准值}")
            print(f"      状态:   {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "密码策略",
                    "项目": 名称,
                    "当前值": 当前值,
                    "标准值": 标准值,
                    "风险": "高" if 名称 in ("PasswordComplexity", "MinimumPasswordLength",
                                        "LockoutBadCount") else "中",
                    "建议": self._生成密码策略建议(名称, 标准值)
                })
            print()

    def _生成密码策略建议(self, 名称: str, 标准值: Any) -> str:
        """生成密码策略修复建议"""
        建议 = {
            "PasswordComplexity": f"启用密码复杂性要求: net accounts /complexity:yes",
            "MinimumPasswordLength": f"设置最小密码长度为{标准值}: net accounts /minpwlen:{标准值}",
            "MaximumPasswordAge": f"设置最大密码年龄为{标准值}天: net accounts /maxpwage:{标准值}",
            "PasswordHistorySize": f"设置密码历史数为{标准值}: net accounts /uniquepw:{标准值}",
            "LockoutBadCount": f"设置锁定阈值为{标准值}次: net accounts /lockoutthreshold:{标准值}",
            "LockoutDuration": f"设置锁定时间为{标准值}分钟: net accounts /lockoutduration:{标准值}",
        }
        return 建议.get(名称, f"将{名称}设置为标准值: {标准值}")

    def 检查审核策略(self):
        """
        检查审核策略配置

        技术说明：
            Windows审核策略记录安全事件到安全日志，包括：
            - 登录/注销事件（Event ID 4624/4625/4634）
            - 对象访问审计（文件/注册表访问）
            - 特权使用审计
            - 账户管理审计（用户创建/删除/修改）
            - 策略更改审计

            检查命令: auditpol /get /category:*
        """
        print("=" * 70)
        print("Windows审核策略检查")
        print("=" * 70)
        print("  检查方法: auditpol /get /category:*\n")

        策略 = 模拟Windows安全策略["审核策略"]

        for 名称, 配置 in 策略.items():
            当前值 = 配置["当前值"]
            标准值 = 配置["标准值"]
            说明 = 配置["说明"]
            合规 = (当前值 == 标准值)

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      说明:   {说明}")
            print(f"      当前值: {'启用' if 当前值 else '禁用'}")
            print(f"      标准值: {'启用' if 标准值 else '禁用'}")
            print(f"      状态:   {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "审核策略",
                    "项目": 名称,
                    "当前值": 当前值,
                    "标准值": 标准值,
                    "风险": "中",
                    "建议": f"启用审核: auditpol /set /{名称}:/enable"
                })
            print()

    def 检查服务配置(self):
        """
        检查关键服务配置

        技术说明：
            某些Windows服务存在安全风险，建议关闭或禁用：
            - Telnet: 明文传输，应禁用
            - 远程注册表: 允许远程修改注册表，应停止
            - 打印后台: 可能被用于漏洞利用(PrintNightmare)
            - SMBv1: 存在已知漏洞(永恒之蓝)，应禁用
            - 远程桌面: 需严格限制访问

            检查命令: sc query <service> 或 Get-Service
        """
        print("=" * 70)
        print("Windows服务配置检查")
        print("=" * 70)
        print("  检查方法: sc query / Get-Service\n")

        服务列表 = 模拟Windows安全策略["服务配置"]

        for 名称, 配置 in 服务列表.items():
            当前值 = 配置["当前值"]
            标准值 = 配置["标准值"]
            说明 = 配置["说明"]
            合规 = (当前值 == 标准值)

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      说明:   {说明}")
            print(f"      当前状态: {当前值}")
            print(f"      标准状态: {标准值}")
            print(f"      状态:   {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "服务配置",
                    "项目": 名称,
                    "当前值": 当前值,
                    "标准值": 标准值,
                    "风险": "高" if 名称 in ("Telnet", "SMB") else "中",
                    "建议": f"停止并禁用服务: sc stop {名称}; sc config {名称} start=disabled"
                })
            print()

    def 检查注册表安全(self):
        """
        检查注册表安全配置

        技术说明：
            注册表安全配置影响系统安全行为：
            - RestrictAnonymous: 限制匿名SAM枚举
            - AutoShareWks/Server: 禁止默认管理共享(C$/D$/ADMIN$)
            - 屏蔽自动运行(AutoRun)
            - 限制远程访问注册表

            检查命令: reg query <key>
        """
        print("=" * 70)
        print("Windows注册表安全检查")
        print("=" * 70)
        print("  检查方法: reg query HKLM\\...\n")

        配置 = 模拟Windows安全策略["注册表安全"]

        for 名称, 设置 in 配置.items():
            当前值 = 设置["当前值"]
            标准值 = 设置["标准值"]
            说明 = 设置["说明"]
            合规 = (当前值 == 标准值)

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      说明:   {说明}")
            print(f"      当前值: {当前值}")
            print(f"      标准值: {标准值}")
            print(f"      状态:   {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "注册表安全",
                    "项目": 名称,
                    "当前值": 当前值,
                    "标准值": 标准值,
                    "风险": "中",
                    "建议": f"修改注册表: reg add HKLM\\... /v {名称} /t REG_DWORD /d {标准值} /f"
                })
            print()

    def 生成基线报告(self):
        """生成Windows安全基线报告"""
        print("=" * 70)
        print("Windows安全基线检查报告")
        print("=" * 70)

        合规数 = 0
        不合规数 = len(self.检查结果)
        总检查项 = 不合规数 + 合规数

        print(f"\n  总检查项: {总检查项}")
        print(f"  不合规:   {不合规数} 项")
        print(f"  合规率:   {((总检查项 - 不合规数) / 总检查项 * 100):.1f}%" if 总检查项 else "  合规率: 100%")

        if self.检查结果:
            print("\n  不合规项详情:")
            for i, r in enumerate(self.检查结果, 1):
                print(f"    {i}. [{r['风险']}] {r['类别']}/{r['项目']}")
                print(f"       当前: {r['当前值']}, 标准: {r['标准值']}")
                print(f"       建议: {r['建议']}")

        return {"不合规数": 不合规数, "总检查项": 总检查项}


# ============================================================================
#  第二部分：Linux系统安全基线检查
# ============================================================================

class Linux安全基线检查器:
    """
    Linux系统安全基线检查工具

    功能说明：
        - 检查SSH安全配置
        - 验证关键文件权限
        - 检查内核安全参数
        - 审计用户账户安全

    技术原理：
        Linux安全基线检查通过读取和分析系统配置文件实现：
        - SSH配置: /etc/ssh/sshd_config
        - 文件权限: ls -l 或 stat 命令
        - 内核参数: sysctl 命令
        - 用户信息: /etc/passwd, /etc/shadow
    """

    def __init__(self):
        self.检查结果 = []
        self.不合规数 = 0
        print("[初始化] Linux安全基线检查器已就绪")

    def 检查SSH配置(self):
        """
        检查SSH服务安全配置

        技术说明：
            SSH是Linux远程管理的主要方式，安全配置关键项：
            - 禁止Root直接登录（使用sudo提权）
            - 禁用密码认证（使用密钥认证）
            - 仅使用Protocol 2（Protocol 1已不安全）
            - 限制最大认证尝试次数
            - 修改默认端口22
            - 设置客户端存活检测

            检查命令: cat /etc/ssh/sshd_config
        """
        print("\n" + "=" * 70)
        print("Linux SSH安全配置检查")
        print("=" * 70)
        print("  检查文件: /etc/ssh/sshd_config\n")

        配置 = 模拟Linux安全配置["SSH配置"]

        for 名称, 设置 in 配置.items():
            当前值 = 设置["当前值"]
            标准值 = 设置["标准值"]
            说明 = 设置["说明"]
            合规 = (str(当前值) == str(标准值))

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      说明:   {说明}")
            print(f"      当前值: {当前值}")
            print(f"      标准值: {标准值}")
            print(f"      状态:   {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "SSH配置",
                    "项目": 名称,
                    "当前值": 当前值,
                    "标准值": 标准值,
                    "风险": "高" if 名称 in ("PermitRootLogin", "PasswordAuthentication",
                                        "PermitEmptyPasswords") else "中",
                    "建议": f"修改 /etc/ssh/sshd_config: {名称} {标准值}"
                })
            print()

    def 检查文件权限(self):
        """
        检查关键文件权限

        技术说明：
            关键系统文件的权限直接影响安全：
            - /etc/shadow: 密码哈希，应仅root可读(000或640)
            - /etc/sudoers: sudo配置，应440
            - /etc/ssh/sshd_config: SSH配置，应600
            - 日志文件: 应限制普通用户读取

            检查命令: ls -l /etc/shadow 或 stat -c '%a' /etc/shadow
        """
        print("=" * 70)
        print("Linux关键文件权限检查")
        print("=" * 70)
        print("  检查方法: stat -c '%a' <file> 或 ls -l <file>\n")

        权限列表 = 模拟Linux安全配置["文件权限"]

        for 文件, 配置 in 权限列表.items():
            当前权限 = 配置["当前权限"]
            标准权限 = 配置["标准权限"]
            说明 = 配置["说明"]
            合规 = (当前权限 == 标准权限)

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {文件}")
            print(f"      说明:     {说明}")
            print(f"      当前权限: {当前权限}")
            print(f"      标准权限: {标准权限}")
            print(f"      状态:     {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "文件权限",
                    "项目": 文件,
                    "当前值": 当前权限,
                    "标准值": 标准权限,
                    "风险": "高" if 文件 in ("/etc/shadow", "/etc/sudoers") else "中",
                    "建议": f"修改权限: chmod {标准权限} {文件}"
                })
            print()

    def 检查内核参数(self):
        """
        检查内核安全参数

        技术说明：
            Linux内核参数影响系统安全行为：
            - IP转发(net.ipv4.ip_forward): 路由器才需要启用
            - SYN Cookie: 防止SYN Flood攻击
            - 地址空间随机化(ASLR): 防止缓冲区溢出利用
            - 禁止ICMP重定向: 防止路由劫持
            - 内核指针限制: 防止内核信息泄露

            检查命令: sysctl <参数>
        """
        print("=" * 70)
        print("Linux内核安全参数检查")
        print("=" * 70)
        print("  检查方法: sysctl <parameter>\n")

        参数列表 = 模拟Linux安全配置["内核参数"]

        for 名称, 设置 in 参数列表.items():
            当前值 = 设置["当前值"]
            标准值 = 设置["标准值"]
            说明 = 设置["说明"]
            合规 = (str(当前值) == str(标准值))

            标识 = "[OK]" if 合规 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      说明:   {说明}")
            print(f"      当前值: {当前值}")
            print(f"      标准值: {标准值}")
            print(f"      状态:   {'合规' if 合规 else '不合规'}")

            if not 合规:
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "内核参数",
                    "项目": 名称,
                    "当前值": 当前值,
                    "标准值": 标准值,
                    "风险": "中",
                    "建议": f"设置参数: sysctl -w {名称}={标准值}"
                })
            print()

    def 检查用户账户(self):
        """
        检查用户账户安全

        技术说明：
            用户账户安全检查重点：
            - 检查UID=0的账户（应为唯一root）
            - 检查空密码账户
            - 检查已过期/离职的账户
            - 检查sudo权限分配
            - 检查默认/测试账户

            检查命令:
            - awk -F: '($3==0) {print}' /etc/passwd  检查UID=0
            - awk -F: '($2=="") {print}' /etc/shadow  检查空密码
            - passwd -S <user>  查看账户状态
        """
        print("=" * 70)
        print("Linux用户账户安全检查")
        print("=" * 70)
        print("  检查方法: cat /etc/passwd, cat /etc/shadow\n")

        用户列表 = 模拟Linux安全配置["用户账户"]

        # 检查UID=0的账户
        print("  [检查] UID=0 的账户:")
        uid0用户 = [u for u in 用户列表 if u["UID"] == 0]
        for u in uid0用户:
            if u["用户名"] == "root":
                print(f"    [OK] {u['用户名']} (UID={u['UID']}) - {u['说明']}")
            else:
                print(f"    [!!] {u['用户名']} (UID={u['UID']}) - {u['说明']}")
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "用户账户",
                    "项目": f"UID=0: {u['用户名']}",
                    "当前值": f"UID={u['UID']}",
                    "标准值": "UID=0仅root",
                    "风险": "高",
                    "建议": f"修改用户UID: usermod -u <new_uid> {u['用户名']}"
                })

        # 检查空密码和异常状态
        print("\n  [检查] 账户状态:")
        for u in 用户列表:
            名称 = u["用户名"]
            状态 = u["状态"]
            说明 = u["说明"]
            正常 = True

            if "空密码" in 说明:
                正常 = False
                print(f"    [!!] {名称} - {说明} (空密码)")
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "用户账户",
                    "项目": f"空密码: {名称}",
                    "当前值": "空密码",
                    "标准值": "禁用空密码",
                    "风险": "高",
                    "建议": f"锁定账户: passwd -l {名称} 或设置密码"
                })
            elif "离职" in 说明:
                正常 = False
                print(f"    [!!] {名称} - {说明}")
                self.不合规数 += 1
                self.检查结果.append({
                    "类别": "用户账户",
                    "项目": f"离职用户: {名称}",
                    "当前值": "账户活跃",
                    "标准值": "应禁用或删除",
                    "风险": "中",
                    "建议": f"禁用账户: usermod -L {名称} 或 userdel -r {名称}"
                })
            elif 正常:
                print(f"    [OK] {名称} (UID={u['UID']}) - {说明}")

    def 生成基线报告(self):
        """生成Linux安全基线报告"""
        print("\n" + "=" * 70)
        print("Linux安全基线检查报告")
        print("=" * 70)

        print(f"\n  不合规项: {self.不合规数} 个")

        高风险 = [r for r in self.检查结果 if r["风险"] == "高"]
        中风险 = [r for r in self.检查结果 if r["风险"] == "中"]

        print(f"    - 高风险: {len(高风险)}")
        print(f"    - 中风险: {len(中风险)}")

        if 高风险:
            print("\n  高风险不合规项:")
            for i, r in enumerate(高风险[:5], 1):
                print(f"    {i}. {r['类别']}/{r['项目']}")
                print(f"       当前: {r['当前值']}, 标准: {r['标准值']}")

        print("\n  修复建议:")
        print("    1. 使用自动化配置工具(Ansible/CIS Benchmark脚本)")
        print("    2. 禁用不必要的服务和账户")
        print("    3. 配置SSH密钥认证，禁用密码登录")
        print("    4. 定期审计文件权限和用户账户")
        print("    5. 加固内核网络参数")

        return {"不合规数": self.不合规数, "高风险数": len(高风险)}


# ============================================================================
#  第三部分：EDR行为检测模拟
# ============================================================================

class EDR行为检测模拟器:
    """
    EDR(终端检测与响应)行为检测模拟器

    功能说明：
        - 进程行为监控与分析
        - 文件系统变更监控
        - 注册表变更监控（Windows）
        - 网络连接监控
        - 行为基线异常检测

    技术原理：
        EDR通过在终端上部署agent，实时监控系统行为：
        1. 进程监控 - 记录进程创建/退出/注入行为
        2. 文件监控 - 检测文件创建/修改/删除/重命名
        3. 注册表监控 - 检测注册表键值修改
        4. 网络监控 - 记录网络连接和通信行为

        通过行为基线对比，检测异常行为模式，
        识别恶意软件的攻击行为链。
    """

    # 恶意行为检测规则
    检测规则 = {
        "异常路径执行": {
            "描述": "从非标准路径执行系统进程",
            "规则": lambda p: p["路径"] not in ("C:\\Windows\\System32", "C:\\Windows",
                                                   "C:\\Program Files", "C:\\Program Files (x86)"),
            "严重性": "高"
        },
        "进程链异常": {
            "描述": "可疑的进程父子关系链",
            "规则": lambda p: p.get("父PID") in [2048, 3072, 4096],
            "严重性": "高"
        },
        "已知恶意进程名": {
            "描述": "检测到已知恶意工具",
            "规则": lambda p: p["名称"] in ("mimikatz.exe", "nc.exe", "ncat.exe",
                                            "procdump.exe", "hashcat.exe", "hydra.exe"),
            "严重性": "严重"
        },
        "可疑路径": {
            "描述": "从临时目录执行",
            "规则": lambda p: "Temp" in p["路径"] or "Public" in p["路径"],
            "严重性": "中"
        }
    }

    def __init__(self):
        self.告警列表 = []
        print("[初始化] EDR行为检测模拟器已就绪")

    def 监控进程行为(self, 进程列表: List[Dict] = 模拟进程列表):
        """
        监控和分析进程行为

        技术说明：
            进程监控通过以下方式获取进程信息：
            - Windows: ETW(Event Tracing for Windows)、WMI事件
            - Linux: auditd、eBPF、/proc文件系统

            检测维度：
            1. 进程路径 - 系统进程应从标准路径运行
            2. 进程链 - 正常进程的父子关系是已知的
            3. 进程名 - 检测已知恶意工具
            4. 命令行 - 检测可疑命令行参数
        """
        print("\n" + "=" * 70)
        print("EDR - 进程行为监控与分析")
        print("=" * 70)
        print(f"  监控进程数: {len(进程列表)}\n")

        print("  进程列表:")
        print(f"  {'PID':>6s}  {'名称':20s}  {'路径':40s}  {'父PID':>6s}  {'状态'}")
        print("  " + "-" * 90)

        for p in 进程列表:
            状态标识 = "正常" if p["正常"] else "可疑"
            print(f"  {p['PID']:6d}  {p['名称']:20s}  {p['路径']:40s}  {p['父PID']:6d}  {状态标识}")

        # 应用检测规则
        print("\n  行为检测规则应用:")
        for 规则名, 规则配置 in self.检测规则.items():
            print(f"\n    [{规则名}] {规则配置['描述']}")
            for p in 进程列表:
                try:
                    if 规则配置["规则"](p):
                        严重性 = 规则配置["严重性"]
                        print(f"      [{严重性}] PID={p['PID']} {p['名称']} 路径={p['路径']}")
                        self.告警列表.append({
                            "类型": "进程行为",
                            "规则": 规则名,
                            "PID": p["PID"],
                            "名称": p["名称"],
                            "路径": p["路径"],
                            "严重性": 严重性,
                            "描述": f"{规则配置['描述']}: {p['名称']} from {p['路径']}"
                        })
                except Exception:
                    pass

    def 监控文件系统(self):
        """
        监控文件系统变更

        技术说明：
            文件系统监控检测：
            - 可执行文件创建（特别是临时目录）
            - 系统目录文件修改
            - 批量文件加密（勒索软件特征）
            - 配置文件篡改

            实现方式：
            - Windows: ReadDirectoryChangesW、ETW
            - Linux: inotify、auditd
        """
        print("\n" + "=" * 70)
        print("EDR - 文件系统变更监控")
        print("=" * 70)

        # 模拟文件变更事件
        文件事件 = [
            {"时间": "09:00:15", "操作": "创建", "路径": "C:\\Users\\Public\\Temp\\update.exe",
             "大小": 24576, "正常": False},
            {"时间": "09:00:20", "操作": "创建", "路径": "C:\\Users\\Public\\Temp\\helper.dll",
             "大小": 18432, "正常": False},
            {"时间": "09:01:00", "操作": "修改", "路径": "C:\\Windows\\System32\\drivers\\etc\\hosts",
             "大小": 1024, "正常": False},
            {"时间": "09:01:30", "操作": "创建", "路径": "C:\\Users\\admin\\AppData\\Local\\Temp\\payload.dll",
             "大小": 30720, "正常": False},
            {"时间": "09:02:00", "操作": "修改", "路径": "C:\\Users\\admin\\Documents\\report.docx",
             "大小": 51200, "正常": True},
            {"时间": "09:05:00", "操作": "批量加密", "路径": "C:\\Users\\admin\\Documents\\*.docx",
             "大小": 0, "正常": False},
        ]

        print(f"  检测到 {len(文件事件)} 个文件变更事件:\n")

        for event in 文件事件:
            路径 = event["路径"]
            操作 = event["操作"]
            时间 = event["时间"]
            大小 = event["大小"]
            正常 = event["正常"]

            # 风险判定
            if 操作 == "批量加密":
                风险 = "严重"
                描述 = "检测到批量文件加密行为，疑似勒索软件"
            elif "Temp" in 路径 and 路径.endswith((".exe", ".dll")):
                风险 = "高"
                描述 = "临时目录创建可执行文件"
            elif "hosts" in 路径:
                风险 = "高"
                描述 = "hosts文件被修改，可能DNS劫持"
            elif not 正常:
                风险 = "中"
                描述 = "可疑文件操作"
            else:
                风险 = "低"
                描述 = "正常文件操作"

            标识 = {"严重": "[!!]", "高": "[!!]", "中": "[? ]", "低": "[OK]"}[风险]
            print(f"  {标识} [{时间}] {操作}: {路径}")
            print(f"      大小: {大小} bytes | 风险: {风险} | {描述}")

            if 风险 in ("严重", "高", "中"):
                self.告警列表.append({
                    "类型": "文件变更",
                    "操作": 操作,
                    "路径": 路径,
                    "严重性": 风险,
                    "描述": 描述
                })

    def 监控注册表(self):
        """
        监控注册表变更（Windows）

        技术说明：
            注册表监控重点：
            - HKLM\Run / HKCU\Run (自启动项)
            - 服务注册表项 (服务安装)
            - 文件关联修改
            - 安全配置修改

            实现方式：
            - RegNotifyChangeKeyValue API
            - ETW注册表事件
            - Sysmon Event ID 12/13/14
        """
        print("\n" + "=" * 70)
        print("EDR - 注册表变更监控")
        print("=" * 70)

        # 检查启动项
        print("  检查自启动项:")
        print(f"  {'位置':20s}  {'名称':25s}  {'值':50s}  {'状态'}")
        print("  " + "-" * 100)

        for item in 模拟启动项:
            位置 = item["位置"]
            名称 = item["名称"]
            值 = item["值"]
            正常 = item["正常"]

            标识 = "[OK]" if 正常 else "[!!]"
            print(f"  {位置:20s}  {名称:25s}  {值:50s}  {标识}")

            if not 正常:
                self.告警列表.append({
                    "类型": "注册表变更",
                    "位置": 位置,
                    "名称": 名称,
                    "严重性": "高",
                    "描述": f"可疑启动项: {名称} -> {值}"
                })

        # 检查计划任务
        print("\n  检查计划任务:")
        for task in 模拟计划任务:
            名称 = task["名称"]
            路径 = task["路径"]
            正常 = task["正常"]

            标识 = "[OK]" if 正常 else "[!!]"
            print(f"  {标识} {名称}")
            print(f"      执行: {路径}")

            if not 正常:
                self.告警列表.append({
                    "类型": "注册表变更",
                    "位置": "计划任务",
                    "名称": 名称,
                    "严重性": "高",
                    "描述": f"可疑计划任务: {名称} -> {路径}"
                })

    def 监控网络连接(self, 连接列表: List[Dict] = 模拟网络连接):
        """
        监控网络连接行为

        技术说明：
            网络监控检测：
            - 异常出站连接（到已知恶意IP）
            - 非标准端口通信
            - 可疑进程的网络活动
            - DNS查询异常
            - 数据外传行为

            实现方式：
            - Windows: ETW网络事件、GetExtendedTcpTable
            - Linux: netlink socket、conntrack
        """
        print("\n" + "=" * 70)
        print("EDR - 网络连接监控")
        print("=" * 70)
        print(f"  监控连接数: {len(连接列表)}\n")

        # 已知恶意IP段
        恶意IP段 = ["45.137.21.", "193.27.14.", "185.141.25."]

        print(f"  {'PID':>6s}  {'协议':4s}  {'本地地址':25s}  {'远程地址':25s}  {'状态':12s}  {'判定'}")
        print("  " + "-" * 100)

        for conn in 连接列表:
            PID = conn["PID"]
            协议 = conn["协议"]
            本地 = conn["本地"]
            远程 = conn["远程"]
            状态 = conn["状态"]
            正常 = conn["正常"]

            判定 = "正常" if 正常 else "可疑"

            # 检查是否连接到恶意IP
            远程IP = 远程.split(":")[0] if ":" in 远程 else 远程
            是恶意IP = any(远程IP.startswith(段) for 段 in 恶意IP段)

            if 是恶意IP:
                判定 = "恶意C2"
                风险 = "严重"
            elif not 正常:
                判定 = "可疑"
                风险 = "高"
            else:
                风险 = "低"

            标识 = {"严重": "[!!]", "高": "[!!]", "低": "[OK]"}[风险]
            print(f"  {PID:6d}  {协议:4s}  {本地:25s}  {远程:25s}  {状态:12s}  {标识} {判定}")

            if 风险 in ("严重", "高"):
                self.告警列表.append({
                    "类型": "网络连接",
                    "PID": PID,
                    "远程地址": 远程,
                    "严重性": 风险,
                    "描述": f"{'连接已知恶意C2服务器' if 是恶意IP else '可疑网络连接'}: {远程}"
                })

    def 生成EDR报告(self):
        """生成EDR检测报告"""
        print("\n" + "=" * 70)
        print("EDR行为检测报告")
        print("=" * 70)

        严重 = [a for a in self.告警列表 if a["严重性"] == "严重"]
        高 = [a for a in self.告警列表 if a["严重性"] == "高"]
        中 = [a for a in self.告警列表 if a["严重性"] == "中"]

        print(f"\n  告警总数: {len(self.告警列表)}")
        print(f"    - 严重: {len(严重)}")
        print(f"    - 高:   {len(高)}")
        print(f"    - 中:   {len(中)}")

        if 严重:
            print("\n  严重告警:")
            for a in 严重:
                print(f"    [!!] {a['描述']}")

        print("\n  响应建议:")
        print("    1. 立即隔离受感染终端")
        print("    2. 阻断恶意C2通信")
        print("    3. 清除持久化机制")
        print("    4. 修改可能泄露的凭据")
        print("    5. 进行全盘恶意代码扫描")

        return {"严重": len(严重), "高": len(高), "中": len(中)}


# ============================================================================
#  第四部分：恶意代码行为分析
# ============================================================================

class 恶意代码行为分析器:
    """
    恶意代码行为分析工具

    功能说明：
        - 进程注入检测
        - 持久化机制检查
        - 网络C2通信检测
        - 权限提升行为检测
        - 横向移动行为检测

    技术原理：
        恶意代码的行为模式分析是安全防御的核心。
        通过分析恶意软件的行为链，理解攻击者的操作手法(TTPs)，
        并据此建立检测规则。

        常见恶意行为：
        1. 进程注入 - 将代码注入到合法进程中隐藏
        2. 持久化 - 注册启动项/服务/计划任务/计划任务
        3. 凭据窃取 - 从LSASS/浏览器中提取凭据
        4. C2通信 - 与控制服务器建立隐蔽通道
        5. 横向移动 - 使用凭据在其他主机上传播
    """

    def __init__(self):
        self.行为链 = []
        print("[初始化] 恶意代码行为分析器已就绪")

    def 检测进程注入(self):
        """
        检测进程注入行为

        技术说明：
            进程注入是将恶意代码加载到另一个进程中执行的技术，
            用于绕过安全检测和获取合法进程的权限。

            常见注入方式：
            1. DLL注入 - CreateRemoteThread + LoadLibrary
            2. 进程替换 - 挂起目标进程，替换内存映像
            3. 进程空心化 - 创建挂起进程，注入代码后恢复
            4. APC注入 - 利用异步过程调用注入
            5. 反射DLL注入 - 自实现加载器

            检测方法：
            - 监控VirtualAllocEx + WriteProcessMemory + CreateRemoteThread
            - 检查进程内存中的异常模块
            - 检查线程起始地址是否在合法模块中
            - Sysmon Event ID 8 (CreateRemoteThread)
        """
        print("\n" + "=" * 70)
        print("恶意代码行为分析 - 进程注入检测")
        print("=" * 70)

        # 模拟进程注入行为
        注入事件 = [
            {
                "时间": "09:00:05",
                "源进程": "update.exe (PID: 2048)",
                "目标进程": "explorer.exe (PID: 560)",
                "技术": "CreateRemoteThread",
                "API调用链": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
                              "CreateRemoteThread"],
                "检测": True,
                "ATTCK": "T1055"
            },
            {
                "时间": "09:00:10",
                "源进程": "update.exe (PID: 2048)",
                "目标进程": "svchost.exe (PID: 540)",
                "技术": "DLL注入",
                "API调用链": ["OpenProcess", "VirtualAllocEx", "WriteProcessMemory",
                              "LoadLibrary", "CreateRemoteThread"],
                "检测": True,
                "ATTCK": "T1055.001"
            }
        ]

        for event in 注入事件:
            print(f"\n  [{event['时间']}] 检测到进程注入行为")
            print(f"    源进程:   {event['源进程']}")
            print(f"    目标进程: {event['目标进程']}")
            print(f"    注入技术: {event['技术']}")
            print(f"    API调用链:")
            for api in event["API调用链"]:
                print(f"      -> {api}")
            print(f"    MITRE ATT&CK: {event['ATTCK']}")
            print(f"    判定: [严重] 进程注入攻击")

            self.行为链.append({
                "行为": "进程注入",
                "时间": event["时间"],
                "ATTCK": event["ATTCK"],
                "严重性": "严重",
                "描述": f"{event['源进程']} -> {event['目标进程']} ({event['技术']})"
            })

        # 检测建议
        print("\n  检测建议:")
        print("    1. 使用Sysmon监控CreateRemoteThread调用")
        print("    2. 检查进程内存中的异常模块加载")
        print("    3. 监控VirtualAllocEx+WriteProcessMemory组合")
        print("    4. 检查线程起始地址的合法性")

    def 检测持久化机制(self):
        """
        检测持久化机制

        技术说明：
            持久化是恶意代码在系统重启后仍然存活的技术：
            1. 注册表Run键 - 最常见的持久化方式
            2. 计划任务 - schtasks命令创建
            3. 服务安装 - 创建恶意Windows服务
            4. 启动文件夹 - 在启动文件夹放置恶意文件
            5. WMI事件订阅 - 通过WMI实现无文件持久化
            6. DLL劫持 - 替换合法应用的DLL

            检测方法：
            - 定期扫描注册表Run键
            - 审计划任务列表
            - 检查服务列表
            - Sysmon Event ID 12/13/14 (注册表)
            - Sysmon Event ID 7045 (服务安装)
        """
        print("\n" + "=" * 70)
        print("恶意代码行为分析 - 持久化机制检测")
        print("=" * 70)

        持久化项 = []

        # 检查注册表启动项
        print("\n  [检查] 注册表启动项:")
        for item in 模拟启动项:
            if not item["正常"]:
                print(f"    [!!] {item['位置']}\\{item['名称']}")
                print(f"         值: {item['值']}")
                持久化项.append({
                    "类型": "注册表启动项",
                    "位置": item["位置"],
                    "名称": item["名称"],
                    "ATTCK": "T1547.001"
                })

        # 检查计划任务
        print("\n  [检查] 计划任务:")
        for task in 模拟计划任务:
            if not task["正常"]:
                print(f"    [!!] 任务名: {task['名称']}")
                print(f"         执行: {task['路径']}")
                持久化项.append({
                    "类型": "计划任务",
                    "位置": task["名称"],
                    "名称": task["路径"],
                    "ATTCK": "T1053.005"
                })

        # 检查服务
        print("\n  [检查] 系统服务:")
        模拟服务 = [
            {"名称": "SystemUpdate", "路径": "C:\\Users\\Public\\Temp\\update.exe",
             "正常": False, "启动类型": "自动"},
        ]
        for svc in 模拟服务:
            if not svc["正常"]:
                print(f"    [!!] 服务: {svc['名称']}")
                print(f"         路径: {svc['路径']}")
                print(f"         启动: {svc['启动类型']}")
                持久化项.append({
                    "类型": "系统服务",
                    "位置": f"HKLM\\System\\CurrentControlSet\\Services\\{svc['名称']}",
                    "名称": svc["名称"],
                    "ATTCK": "T1543.003"
                })

        # 检查WMI订阅
        print("\n  [检查] WMI事件订阅:")
        模拟WMI = [
            {"名称": "SystemEventConsumer", "查询": "SELECT * FROM __InstanceModificationEvent",
             "正常": False}
        ]
        for wmi in 模拟WMI:
            if not wmi["正常"]:
                print(f"    [!!] WMI订阅: {wmi['名称']}")
                print(f"         查询: {wmi['查询']}")
                持久化项.append({
                    "类型": "WMI事件订阅",
                    "位置": "root\\subscription",
                    "名称": wmi["名称"],
                    "ATTCK": "T1546.003"
                })

        print(f"\n  持久化项总计: {len(持久化项)} 个")

        for item in 持久化项:
            self.行为链.append({
                "行为": "持久化",
                "ATTCK": item["ATTCK"],
                "严重性": "高",
                "描述": f"{item['类型']}: {item['名称']}"
            })

    def 检测网络C2(self):
        """
        检测网络C2(Command & Control)通信

        技术说明：
            C2通信是攻击者控制被感染主机的方式：
            1. 直连 - 直接连接C2服务器(固定IP/域名)
            2. 域名生成算法(DGA) - 动态生成域名
            3. 隧道 - DNS隧道、ICMP隧道、HTTP隧道
            4. 域前置 - 使用CDN隐藏真实C2
            5. 社交平台 - 使用Twitter/Telegram作为C2

            检测方法：
            - 网络流量分析（异常出站连接）
            - DNS查询日志分析
            - 域名信誉查询
            - Beacon行为检测（定时心跳包）
        """
        print("\n" + "=" * 70)
        print("恶意代码行为分析 - 网络C2通信检测")
        print("=" * 70)

        # 分析异常网络连接
        恶意连接 = [c for c in 模拟网络连接 if not c["正常"]]

        print(f"\n  检测到 {len(恶意连接)} 个可疑网络连接:\n")

        for conn in 恶意连接:
            远程IP = conn["远程"].split(":")[0]
            远程端口 = conn["远程"].split(":")[1] if ":" in conn["远程"] else "?"

            # 分析C2特征
            if 远程端口 in ("4444", "4445"):
                C2类型 = "反向Shell (Metasploit默认端口)"
                风险 = "严重"
            elif 远程端口 == "8080":
                C2类型 = "HTTP C2通道"
                风险 = "高"
            else:
                C2类型 = "未知C2通信"
                风险 = "高"

            print(f"  [{风险}] PID={conn['PID']} -> {conn['远程']}")
            print(f"    协议: {conn['协议']}")
            print(f"    远程IP: {远程IP}")
            print(f"    远程端口: {远程端口}")
            print(f"    状态: {conn['状态']}")
            print(f"    判定: {C2类型}")
            print(f"    MITRE ATT&CK: T1071")
            print()

            self.行为链.append({
                "行为": "C2通信",
                "ATTCK": "T1071",
                "严重性": 风险,
                "描述": f"PID={conn['PID']} 连接 {conn['远程']} ({C2类型})"
            })

    def 生成行为分析报告(self):
        """生成恶意代码行为分析报告"""
        print("\n" + "=" * 70)
        print("恶意代码行为分析报告")
        print("=" * 70)

        严重 = [b for b in self.行为链 if b["严重性"] == "严重"]
        高 = [b for b in self.行为链 if b["严重性"] == "高"]

        print(f"\n  检测行为数: {len(self.行为链)}")
        print(f"    - 严重: {len(严重)}")
        print(f"    - 高:   {len(高)}")

        # 输出攻击行为链
        print("\n  攻击行为链:")
        for i, 行为 in enumerate(self.行为链, 1):
            print(f"    {i}. [{行为['ATTCK']}] {行为['行为']}: {行为['描述']}")

        # ATT&CK映射
        print("\n  MITRE ATT&CK 技术映射:")
        attck集合 = set(b["ATTCK"] for b in self.行为链)
        for tid in sorted(attck集合):
            映射 = MITRE_ATTCK映射.get(tid, {})
            名称 = 映射.get("名称", "未知")
            战术 = 映射.get("战术", "未知")
            描述 = 映射.get("描述", "")
            print(f"    {tid}: {名称}")
            print(f"      战术: {战术}")
            print(f"      描述: {描述}")

        return {
            "行为总数": len(self.行为链),
            "严重数": len(严重),
            "高风险数": len(高),
            "ATTCK技术": list(attck集合)
        }


# ============================================================================
#  第五部分：终端入侵检测规则生成
# ============================================================================

class 入侵检测规则生成器:
    """
    基于MITRE ATT&CK的终端入侵检测规则生成器

    功能说明：
        - 根据ATT&CK技术生成检测规则
        - 输出Sigma规则格式
        - 输出Sysmon配置规则
        - 输出YARA检测规则
        - 生成检测覆盖矩阵

    技术原理：
        MITRE ATT&CK框架将攻击行为分为战术(Tactics)和技术(Techniques)，
        每个技术有唯一的ID（如T1055进程注入）。

        检测规则生成器将攻击行为转化为可执行的检测规则：
        - Sigma规则: 通用SIEM检测规则
        - Sysmon配置: Windows系统监控配置
        - YARA规则: 恶意文件特征检测
    """

    def __init__(self):
        self.规则列表 = []
        print("[初始化] 入侵检测规则生成器已就绪")

    def 生成Sysmon规则(self):
        """
        生成Sysmon监控配置规则

        技术说明：
            Sysmon是Windows系统监控工具，可记录：
            - Event ID 1: 进程创建
            - Event ID 3: 网络连接
            - Event ID 8: 远程线程创建(进程注入)
            - Event ID 11: 文件创建
            - Event ID 12/13/14: 注册表修改
            - Event ID 7045: 服务安装

            配置文件为XML格式，定义需要监控的事件类型和过滤条件。
        """
        print("\n" + "=" * 70)
        print("入侵检测规则生成 - Sysmon配置")
        print("=" * 70)

        sysmon规则 = """<Sysmon schemaversion="4.82">
  <!-- 事件提供者配置 -->
  <HashAlgorithms>SHA256</HashAlgorithms>
  <EventFiltering>

    <!-- 进程创建监控 (Event ID 1) -->
    <RuleGroup name="Process Creation" groupRelation="or">
      <ProcessCreate onmatch="include">
        <!-- 检测从临时目录执行的系统进程 -->
        <Rule name="Suspicious Process from Temp" >
          <Image condition="end with">\\Temp\\</Image>
        </Rule>
        <!-- 检测可疑进程名 -->
        <Rule name="Known Malware Process">
          <Image condition="is">mimikatz.exe</Image>
          <Image condition="is">procdump.exe</Image>
          <Image condition="is">nc.exe</Image>
        </Rule>
      </ProcessCreate>
    </RuleGroup>

    <!-- 网络连接监控 (Event ID 3) -->
    <RuleGroup name="Network Connections" groupRelation="or">
      <NetworkConnect onmatch="include">
        <!-- 检测连接到已知C2端口 -->
        <Rule name="C2 Port Connection">
          <DestinationPort condition="is">4444</DestinationPort>
          <DestinationPort condition="is">4445</DestinationPort>
        </Rule>
      </NetworkConnect>
    </RuleGroup>

    <!-- 进程注入检测 (Event ID 8) -->
    <RuleGroup name="Remote Thread" groupRelation="or">
      <CreateRemoteThread onmatch="include">
        <Rule name="Process Injection">
          <SourceImage condition="end with">\\Temp\\</SourceImage>
        </Rule>
      </CreateRemoteThread>
    </RuleGroup>

    <!-- 注册表持久化 (Event ID 12/13) -->
    <RuleGroup name="Registry Persistence" groupRelation="or">
      <RegistryEvent onmatch="include">
        <Rule name="Run Key Modification">
          <TargetObject condition="contains">\\Run\\</TargetObject>
        </Rule>
        <Rule name="Service Installation">
          <TargetObject condition="contains">\\Services\\</TargetObject>
        </Rule>
      </RegistryEvent>
    </RuleGroup>

  </EventFiltering>
</Sysmon>"""

        print("\n  生成的Sysmon配置规则:")
        print("  " + "-" * 60)
        for 行 in sysmon规则.split("\n"):
            print(f"  {行}")
        print("  " + "-" * 60)

        self.规则列表.append({"类型": "Sysmon", "规则数": 5})
        return sysmon规则

    def 生成Sigma规则(self):
        """
        生成Sigma检测规则

        技术说明：
            Sigma是通用的SIEM检测规则格式，类似于YAML。
            可转换为Splunk/ELK/QRadar等SIEM平台的查询语句。

            Sigma规则结构：
            - title: 规则标题
            - status: 规则状态(experimental/stable)
            - description: 规则描述
            - logsource: 日志来源
            - detection: 检测条件
            - level: 风险等级
        """
        print("\n" + "=" * 70)
        print("入侵检测规则生成 - Sigma规则")
        print("=" * 70)

        sigma规则 = [
            {
                "标题": "检测 - 可疑进程从临时目录执行",
                "ATTCK": "T1055",
                "级别": "high",
                "日志源": "Sysmon EventID 1",
                "内容": """title: Suspicious Process From Temp Directory
status: stable
description: Detects process execution from temp directory
logsource:
    product: windows
    category: process_creation
detection:
    selection:
        EventID: 1
        Image|contains:
            - '\\\\Temp\\\\'
            - '\\\\Public\\\\'
    condition: selection
level: high
tags:
    - attack.t1055
    - attack.defense_evasion"""
            },
            {
                "标题": "检测 - 进程注入行为",
                "ATTCK": "T1055",
                "级别": "critical",
                "日志源": "Sysmon EventID 8",
                "内容": """title: Process Injection via CreateRemoteThread
status: stable
description: Detects remote thread creation (process injection)
logsource:
    product: windows
    category: create_remote_thread
detection:
    selection:
        EventID: 8
        SourceImage|contains:
            - '\\\\Temp\\\\'
            - '\\\\Public\\\\'
    condition: selection
level: critical
tags:
    - attack.t1055
    - attack.privilege_escalation"""
            },
            {
                "标题": "检测 - 已知恶意C2端口连接",
                "ATTCK": "T1071",
                "级别": "critical",
                "日志源": "Sysmon EventID 3",
                "内容": """title: Known C2 Port Connection
status: stable
description: Detects connection to known C2 ports
logsource:
    product: windows
    category: network_connection
detection:
    selection:
        EventID: 3
        DestinationPort:
            - 4444
            - 4445
            - 8080
    condition: selection
level: critical
tags:
    - attack.t1071
    - attack.command_and_control"""
            }
        ]

        for 规则 in sigma规则:
            print(f"\n  [{规则['标题']}]")
            print(f"  ATT&CK: {规则['ATTCK']} | 级别: {规则['级别']} | 日志源: {规则['日志源']}")
            print("  " + "-" * 60)
            for 行 in 规则["内容"].split("\n"):
                print(f"  {行}")
            print("  " + "-" * 60)
            self.规则列表.append({"类型": "Sigma", "ATTCK": 规则["ATTCK"]})

        return sigma规则

    def 生成YARA规则(self):
        """
        生成YARA文件检测规则

        技术说明：
            YARA是恶意文件特征匹配工具，通过定义文本/二进制模式
            来识别恶意文件。YARA规则由元数据、字符串和条件组成。

            常用于：
            - 恶意软件家族识别
            - 文件特征提取
            - 内存扫描
        """
        print("\n" + "=" * 70)
        print("入侵检测规则生成 - YARA规则")
        print("=" * 70)

        yara规则 = """rule Malware_Generic_Packer
{
    meta:
        description = "检测通用恶意软件打包器"
        author = "Security Team"
        date = "2024-01-15"
        reference = "MITRE ATT&CK T1027"
        severity = "high"

    strings:
        // 可疑API调用
        $api1 = "VirtualAllocEx" wide ascii
        $api2 = "WriteProcessMemory" wide ascii
        $api3 = "CreateRemoteThread" wide ascii
        $api4 = "LoadLibraryA" wide ascii

        // 恶意行为字符串
        $str1 = "cmd.exe /c" wide ascii
        $str2 = "powershell -enc" wide ascii
        $str3 = "rundll32" wide ascii

        // 硬编码C2地址模式
        $c2 = /\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}:\\d{4,5}/

    condition:
        // 至少2个注入API + 1个行为字符串
        (2 of ($api*)) and (1 of ($str*))
        or $c2
}"""

        print("\n  生成的YARA规则:")
        print("  " + "-" * 60)
        for 行 in yara规则.split("\n"):
            print(f"  {行}")
        print("  " + "-" * 60)

        self.规则列表.append({"类型": "YARA", "规则数": 1})
        return yara规则

    def 生成检测覆盖矩阵(self):
        """
        生成MITRE ATT&CK检测覆盖矩阵

        技术说明：
            检测覆盖矩阵显示当前检测规则对ATT&CK技术的覆盖情况，
            帮助安全团队发现检测盲区。
        """
        print("\n" + "=" * 70)
        print("MITRE ATT&CK 检测覆盖矩阵")
        print("=" * 70)

        覆盖矩阵 = {
            "Initial Access": {
                "T1566 钓鱼": False,
                "T1190 漏洞利用": False,
            },
            "Execution": {
                "T1059 命令解释器": True,
                "T1053 计划任务": True,
                "T1106 原生API": True,
            },
            "Persistence": {
                "T1547 启动项": True,
                "T1053 计划任务": True,
                "T1543 服务": True,
                "T1546 事件触发": True,
            },
            "Privilege Escalation": {
                "T1068 漏洞提权": False,
                "T1055 进程注入": True,
            },
            "Defense Evasion": {
                "T1055 进程注入": True,
                "T1112 注册表修改": True,
                "T1027 混淆": False,
            },
            "Credential Access": {
                "T1003 凭据转储": True,
            },
            "Command and Control": {
                "T1071 标准协议": True,
                "T1571 非标准端口": True,
            },
            "Lateral Movement": {
                "T1021 远程服务": False,
            },
            "Impact": {
                "T1486 磁盘加密": False,
            }
        }

        已覆盖 = 0
        未覆盖 = 0

        for 战术, 技术列表 in 覆盖矩阵.items():
            print(f"\n  [{战术}]")
            for 技术, 覆盖 in 技术列表.items():
                标识 = "[x]" if 覆盖 else "[ ]"
                print(f"    {标识} {技术}")
                if 覆盖:
                    已覆盖 += 1
                else:
                    未覆盖 += 1

        总数 = 已覆盖 + 未覆盖
        覆盖率 = (已覆盖 / 总数 * 100) if 总数 else 0

        print(f"\n  覆盖率: {已覆盖}/{总数} ({覆盖率:.1f}%)")
        print(f"  已覆盖: {已覆盖} 个技术")
        print(f"  未覆盖: {未覆盖} 个技术")

        if 未覆盖:
            print("\n  检测盲区建议补充:")
            for 战术, 技术列表 in 覆盖矩阵.items():
                for 技术, 覆盖 in 技术列表.items():
                    if not 覆盖:
                        print(f"    -> {战术}/{技术}")

        return {"覆盖率": 覆盖率, "已覆盖": 已覆盖, "未覆盖": 未覆盖}


# ============================================================================
#  第六部分：应急响应取证
# ============================================================================

class 应急响应取证器:
    """
    应急响应与数字取证工具

    功能说明：
        - 内存取证分析
        - 磁盘取证分析
        - 系统日志分析
        - 时间线重建
        - 证据收集与保存

    技术原理：
        应急响应取证遵循严格的证据链流程：
        1. 识别 - 确认安全事件
        2. 收集 - 收集易失性数据(内存) -> 非易失性数据(磁盘)
        3. 分析 - 分析证据，还原攻击过程
        4. 报告 - 生成取证报告

        取证顺序（ volatility优先）：
        - 内存镜像（RAM）
        - 网络连接状态
        - 运行进程
        - 磁盘镜像
        - 系统日志
        - 应用日志
    """

    def __init__(self):
        self.证据列表 = []
        self.时间线 = []
        print("[初始化] 应急响应取证器已就绪")

    def 内存取证分析(self):
        """
        内存取证分析

        技术说明：
            内存取证使用Volatility等工具分析内存镜像，提取：
            - 进程列表（包括隐藏/rootkit进程）
            - 网络连接
            - 已加载模块（包括恶意DLL）
            - 注册表 hive
            - 凭据信息
            - 进程注入痕迹

            常用Volatility插件：
            - pslist/psxview: 进程列表
            - netscan: 网络连接
            - malfind: 检测注入代码
            - hashdump: 提取密码哈希
            - dumpfiles: 提取文件
        """
        print("\n" + "=" * 70)
        print("应急响应取证 - 内存分析")
        print("=" * 70)
        print("  工具: Volatility Framework")
        print("  镜像: memory.dmp (4GB)\n")

        # 模拟Volatility分析输出
        print("  [1] 进程列表 (volatility pslist):")
        print(f"  {'PID':>6s}  {'PPID':>6s}  {'名称':25s}  {'路径':45s}  {'状态'}")
        print("  " + "-" * 100)

        for p in 模拟进程列表:
            状态 = "正常" if p["正常"] else "可疑"
            print(f"  {p['PID']:6d}  {p['父PID']:6d}  {p['名称']:25s}  {p['路径']:45s}  {状态}")

        # 检测隐藏进程
        print("\n  [2] 隐藏进程检测 (volatility psxview):")
        print("    对比 pslist 和 psscan 结果...")
        print("    [!!] PID=2048 update.exe - 在psscan中存在但pslist中不存在")
        print("    [!!] PID=7168 mimikatz.exe - 在psscan中存在但pslist中不存在")
        print("    -> 可能使用进程 hollowing 技术隐藏")

        self.证据列表.append({
            "类型": "内存-进程",
            "发现": "隐藏进程: PID=2048, PID=7168",
            "重要性": "高"
        })

        # 网络连接
        print("\n  [3] 网络连接 (volatility netscan):")
        for conn in 模拟网络连接:
            if not conn["正常"]:
                print(f"    [!!] PID={conn['PID']} {conn['本地']} -> {conn['远程']} ({conn['状态']})")
                self.证据列表.append({
                    "类型": "内存-网络",
                    "发现": f"C2连接: PID={conn['PID']} -> {conn['远程']}",
                    "重要性": "严重"
                })

        # 检测注入代码
        print("\n  [4] 进程注入检测 (volatility malfind):")
        注入检测 = [
            {"进程": "explorer.exe (PID 560)", "地址": "0x00A50000", "权限": "RWX",
             "特征": "MZ头 - 可执行代码注入"},
            {"进程": "svchost.exe (PID 540)", "地址": "0x00B80000", "权限": "RWX",
             "特征": "MZ头 - 可执行代码注入"},
        ]
        for inj in 注入检测:
            print(f"    [!!] {inj['进程']} @ {inj['地址']} ({inj['权限']})")
            print(f"         特征: {inj['特征']}")
            self.证据列表.append({
                "类型": "内存-注入",
                "发现": f"进程注入: {inj['进程']} @ {inj['地址']}",
                "重要性": "严重"
            })

        # 凭据提取
        print("\n  [5] 凭据提取 (volatility hashdump):")
        凭据 = [
            {"用户": "Administrator", "LM": "aad3b435b51404eeaad3b435b51404ee",
             "NTLM": "8846f7eaee01123456789abcdef01234"},
            {"用户": "admin", "LM": "aad3b435b51404eeaad3b435b51404ee",
             "NTLM": "8846f7eaee056789abcdef0123456789"},
        ]
        for cred in 凭据:
            print(f"    用户: {cred['用户']}")
            print(f"    LM:   {cred['LM']}")
            print(f"    NTLM: {cred['NTLM']}")
            self.证据列表.append({
                "类型": "内存-凭据",
                "发现": f"凭据: {cred['用户']}",
                "重要性": "严重"
            })

    def 磁盘取证分析(self):
        """
        磁盘取证分析

        技术说明：
            磁盘取证分析磁盘镜像，提取：
            - 文件系统结构
            - 已删除文件恢复
            - 时间戳分析(MAC时间)
            - 注册表hive分析
            - 预读取文件分析(Prefetch)
            - 事件日志分析

            工具: FTK Imager, Autopsy, Eric Zimmerman工具集
        """
        print("\n" + "=" * 70)
        print("应急响应取证 - 磁盘分析")
        print("=" * 70)
        print("  工具: FTK Imager / Autopsy")
        print("  镜像: disk.e01 (256GB)\n")

        # 文件分析
        print("  [1] 可疑文件分析:")
        可疑文件 = [
            {"路径": "C:\\Users\\Public\\Temp\\update.exe", "大小": 24576,
             "SHA256": "a1b2c3d4e5f6...", "属性": "隐藏+系统",
             "判定": "恶意可执行文件"},
            {"路径": "C:\\Users\\Public\\Temp\\helper.dll", "大小": 18432,
             "SHA256": "f6e5d4c3b2a1...", "属性": "隐藏",
             "判定": "恶意DLL"},
            {"路径": "C:\\Users\\Public\\Temp\\config.dat", "大小": 1024,
             "SHA256": "1a2b3c4d5e6f...", "属性": "正常",
             "判定": "C2配置文件"},
        ]

        for f in 可疑文件:
            print(f"\n    [!!] {f['路径']}")
            print(f"        大小: {f['大小']} bytes")
            print(f"        属性: {f['属性']}")
            print(f"        SHA256: {f['SHA256']}")
            print(f"        判定: {f['判定']}")
            self.证据列表.append({
                "类型": "磁盘-文件",
                "发现": f"可疑文件: {f['路径']}",
                "重要性": "高"
            })

        # 预读取文件分析
        print("\n  [2] Prefetch分析:")
        prefetch = [
            {"文件": "UPDATE.EXE-20240115.PF", "运行次数": 15, "最近运行": "2024-01-15 09:00:15"},
            {"文件": "POWERSHELL.EXE-20240115.PF", "运行次数": 8, "最近运行": "2024-01-15 09:00:01"},
            {"文件": "MIMIKATZ.EXE-20240115.PF", "运行次数": 3, "最近运行": "2024-01-15 09:02:00"},
            {"文件": "NC.EXE-20240115.PF", "运行次数": 1, "最近运行": "2024-01-15 09:03:00"},
        ]
        for pf in prefetch:
            print(f"    {pf['文件']}")
            print(f"      运行{pf['运行次数']}次, 最近: {pf['最近运行']}")

        # MFT时间线
        print("\n  [3] MFT时间线分析:")
        mft事件 = [
            {"时间": "2024-01-15 08:30:15", "事件": "用户admin登录", "来源": "Security Log"},
            {"时间": "2024-01-15 08:45:37", "事件": "密码爆破成功(6次失败后)", "来源": "Security Log"},
            {"时间": "2024-01-15 09:00:01", "事件": "PowerShell执行(编码命令)", "来源": "Prefetch"},
            {"时间": "2024-01-15 09:00:05", "事件": "进程注入(explorer.exe)", "来源": "内存分析"},
            {"时间": "2024-01-15 09:00:15", "事件": "update.exe创建", "来源": "MFT"},
            {"时间": "2024-01-15 09:01:30", "事件": "服务SystemUpdate安装", "来源": "System Log"},
            {"时间": "2024-01-15 09:02:00", "事件": "mimikatz.exe运行(凭据提取)", "来源": "Prefetch"},
            {"时间": "2024-01-15 09:03:00", "事件": "nc.exe建立C2连接", "来源": "网络日志"},
            {"时间": "2024-01-15 09:05:00", "事件": "注册表Run键修改", "来源": "Sysmon"},
        ]

        for event in mft事件:
            print(f"    [{event['时间']}] {event['事件']} ({event['来源']})")
            self.时间线.append(event)

    def 日志分析(self):
        """
        系统日志分析

        技术说明：
            日志分析是取证的关键环节：
            - Windows: 安全日志、系统日志、应用日志
            - Linux: /var/log/auth.log, /var/log/syslog, /var/log/audit
            - 应用日志: Web服务器日志、数据库日志

            关键事件ID(Windows):
            - 4624/4625: 登录成功/失败
            - 4688: 进程创建
            - 4697: 服务安装
            - 7045: 新服务安装
        """
        print("\n" + "=" * 70)
        print("应急响应取证 - 日志分析")
        print("=" * 70)
        print("  日志源: Windows安全日志、Sysmon日志\n")

        # 分析登录事件
        print("  [1] 登录事件分析:")
        登录成功 = [e for e in 模拟Windows日志 if e["事件ID"] == 4624]
        登录失败 = [e for e in 模拟Windows日志 if e["事件ID"] == 4625]

        print(f"    登录成功: {len(登录成功)} 次")
        print(f"    登录失败: {len(登录失败)} 次")

        if len(登录失败) >= 5:
            print(f"\n    [!!] 检测到暴力破解行为:")
            print(f"         {len(登录失败)}次登录失败后成功")
            print(f"         来源IP: {登录失败[0]['来源']}")
            print(f"         目标用户: {登录失败[0]['用户']}")
            self.证据列表.append({
                "类型": "日志-暴力破解",
                "发现": f"暴力破解: {登录失败[0]['来源']} -> {登录失败[0]['用户']}",
                "重要性": "高"
            })

        # 分析进程创建
        print("\n  [2] 进程创建事件分析:")
        for event in 模拟Windows日志:
            if event["事件ID"] == 4688:
                print(f"    [{event['时间']}] 进程创建: {event['来源']} (用户: {event['用户']})")
                if not event["正常"]:
                    print(f"    [!!] 可疑进程创建")
                    self.证据列表.append({
                        "类型": "日志-进程",
                        "发现": f"可疑进程: {event['来源']}",
                        "重要性": "中"
                    })

        # 分析服务安装
        print("\n  [3] 服务安装事件分析:")
        for event in 模拟Windows日志:
            if event["事件ID"] in (4697, 7045):
                print(f"    [{event['时间']}] 新服务安装: {event['来源']} (用户: {event['用户']})")
                print(f"    [!!] 可疑服务安装")
                self.证据列表.append({
                    "类型": "日志-服务",
                    "发现": f"可疑服务: {event['来源']}",
                    "重要性": "高"
                })

    def 生成取证报告(self):
        """生成应急响应取证报告"""
        print("\n" + "=" * 70)
        print("应急响应取证报告")
        print("=" * 70)

        严重 = [e for e in self.证据列表 if e["重要性"] == "严重"]
        高 = [e for e in self.证据列表 if e["重要性"] == "高"]
        中 = [e for e in self.证据列表 if e["重要性"] == "中"]

        print(f"\n  证据总数: {len(self.证据列表)}")
        print(f"    - 严重: {len(严重)}")
        print(f"    - 高:   {len(高)}")
        print(f"    - 中:   {len(中)}")

        # 攻击时间线
        print("\n  攻击时间线重建:")
        for i, event in enumerate(self.时间线, 1):
            print(f"    {i}. [{event['时间']}] {event['事件']}")

        # 证据摘要
        print("\n  关键证据摘要:")
        类型集合 = defaultdict(list)
        for 证据 in self.证据列表:
            类型集合[证据["类型"]].append(证据)

        for 类型, 证据列表 in 类型集合.items():
            print(f"\n    [{类型}] ({len(证据列表)} 项)")
            for e in 证据列表[:3]:
                print(f"      - {e['发现']}")

        # 结论
        print("\n" + "=" * 70)
        print("  取证分析结论:")
        print("=" * 70)
        print("""
    1. 攻击入口: 暴力破解admin账户密码 (08:45)
    2. 初始执行: PowerShell编码命令执行 (09:00)
    3. 持久化:   注册表Run键 + 服务安装 + 计划任务 (09:01)
    4. 凭据窃取: mimikatz提取LSASS内存凭据 (09:02)
    5. C2通信:   nc.exe连接45.137.21.9:4444 (09:03)
    6. 防御绕过: 进程注入到explorer.exe和svchost.exe

    攻击者TTPs映射:
    - T1110 暴力破解
    - T1059 PowerShell执行
    - T1547/T1053/T1543 持久化
    - T1003 凭据转储
    - T1071 标准协议C2
    - T1055 进程注入
""")
        print("  响应建议:")
        print("    1. 立即隔离受感染主机")
        print("    2. 重置所有可能泄露的凭据")
        print("    3. 清除所有持久化机制")
        print("    4. 阻断C2通信IP(45.137.21.9)")
        print("    5. 全网扫描同类入侵痕迹")
        print("    6. 保留证据，必要时报警")

        return {
            "证据数": len(self.证据列表),
            "严重数": len(严重),
            "时间线事件数": len(self.时间线)
        }


# ============================================================================
#  主函数：演示所有案例
# ============================================================================

def main():
    """
    终端安全实战案例 - 演示主函数

    演示内容：
        1. Windows安全基线检查
        2. Linux安全基线检查
        3. EDR行为检测模拟
        4. 恶意代码行为分析
        5. 入侵检测规则生成
        6. 应急响应取证
    """
    print("=" * 70)
    print("        终端安全实战案例 - 演示程序")
    print("        仅用于授权安全测试和教育目的")
    print("=" * 70)
    print()
    print("本程序演示终端安全的核心技术，")
    print("包括系统基线检查、EDR行为检测、恶意代码分析、")
    print("入侵检测规则生成和应急响应取证。")
    print()

    # ========================================================
    # 案例一：Windows安全基线检查
    # ========================================================
    print("\n" + "#" * 70)
    print("#  案例一：Windows系统安全基线检查")
    print("#" * 70)

    win检查器 = Windows安全基线检查器()
    win检查器.检查密码策略()
    win检查器.检查审核策略()
    win检查器.检查服务配置()
    win检查器.检查注册表安全()
    win检查器.生成基线报告()

    # ========================================================
    # 案例二：Linux安全基线检查
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例二：Linux系统安全基线检查")
    print("#" * 70)

    linux检查器 = Linux安全基线检查器()
    linux检查器.检查SSH配置()
    linux检查器.检查文件权限()
    linux检查器.检查内核参数()
    linux检查器.检查用户账户()
    linux检查器.生成基线报告()

    # ========================================================
    # 案例三：EDR行为检测模拟
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例三：EDR行为检测模拟")
    print("#" * 70)

    edr = EDR行为检测模拟器()
    edr.监控进程行为()
    edr.监控文件系统()
    edr.监控注册表()
    edr.监控网络连接()
    edr.生成EDR报告()

    # ========================================================
    # 案例四：恶意代码行为分析
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例四：恶意代码行为分析")
    print("#" * 70)

    恶意分析器 = 恶意代码行为分析器()
    恶意分析器.检测进程注入()
    恶意分析器.检测持久化机制()
    恶意分析器.检测网络C2()
    恶意分析器.生成行为分析报告()

    # ========================================================
    # 案例五：入侵检测规则生成
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例五：终端入侵检测规则生成")
    print("#" * 70)

    规则生成器 = 入侵检测规则生成器()
    规则生成器.生成Sysmon规则()
    规则生成器.生成Sigma规则()
    规则生成器.生成YARA规则()
    规则生成器.生成检测覆盖矩阵()

    # ========================================================
    # 案例六：应急响应取证
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例六：应急响应取证")
    print("#" * 70)

    取证器 = 应急响应取证器()
    取证器.内存取证分析()
    取证器.磁盘取证分析()
    取证器.日志分析()
    取证器.生成取证报告()

    # ========================================================
    # 总结
    # ========================================================
    print("\n\n" + "=" * 70)
    print("                    演示总结")
    print("=" * 70)
    print("""
    本次演示涵盖了终端安全评估与响应的六个核心领域：

    1. Windows安全基线检查
       - 密码策略、审核策略、服务配置、注册表安全
       - 发现多项不合规配置并生成修复建议

    2. Linux安全基线检查
       - SSH配置、文件权限、内核参数、用户账户
       - 检测到不安全配置和异常用户账户

    3. EDR行为检测模拟
       - 进程行为、文件变更、注册表、网络连接监控
       - 检测到进程注入、持久化、C2通信等恶意行为

    4. 恶意代码行为分析
       - 进程注入检测、持久化机制、网络C2检测
       - 还原攻击行为链并映射MITRE ATT&CK技术

    5. 入侵检测规则生成
       - Sysmon配置、Sigma规则、YARA规则
       - 生成ATT&CK检测覆盖矩阵

    6. 应急响应取证
       - 内存取证、磁盘取证、日志分析
       - 重建攻击时间线，生成取证报告

    安全声明：
        本演示仅用于教育和授权测试目的。
        所有数据均为模拟生成，不涉及真实系统。
        未经授权对他人系统进行安全测试是违法行为。
    """)
    print("=" * 70)
    print("演示结束。")
    print("=" * 70)


if __name__ == "__main__":
    main()
