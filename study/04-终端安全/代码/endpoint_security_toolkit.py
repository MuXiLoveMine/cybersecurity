#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终端安全工具包 (Endpoint Security Toolkit)
===========================================

本工具集集成了终端安全防护与检测常用的各类工具：
1. Windows安全基线检查器 - 密码策略、审核策略、服务、注册表
2. Linux安全基线检查器 - SSH、用户权限、文件系统、内核参数
3. 恶意代码行为分析器 - 进程、启动项、计划任务、网络连接
4. EDR检测规则生成器 - Sigma规则、YARA规则、Sysmon配置
5. 主机加固脚本生成器 - 自动生成加固脚本

作者：终端安全学习工具
版本：1.0
用途：仅用于授权的安全测试和教育学习
"""

import os
import re
import sys
import hashlib
import json
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


# ============================================================
# 工具1: Windows安全基线检查器
# ============================================================

class WindowsBaselineChecker:
    """Windows安全基线检查工具"""

    def __init__(self):
        self.系统配置 = self._get_sample_config()
        self.findings = []

    def _get_sample_config(self) -> Dict:
        """获取模拟配置"""
        return {
            "密码策略": {
                "密码复杂性": {"当前": "未启用", "标准": "启用", "风险": "高"},
                "最小密码长度": {"当前": 0, "标准": 8, "风险": "高"},
                "最大密码年龄": {"当前": 365, "标准": 90, "风险": "中"},
                "密码历史记录": {"当前": 0, "标准": 5, "风险": "中"},
                "账户锁定阈值": {"当前": 0, "标准": 5, "风险": "高"},
                "账户锁定时间": {"当前": 0, "标准": 30, "风险": "中"},
            },
            "审核策略": {
                "审核登录事件": {"当前": "无", "标准": "成功+失败", "风险": "高"},
                "审核对象访问": {"当前": "无", "标准": "成功+失败", "风险": "中"},
                "审核进程跟踪": {"当前": "无", "标准": "成功", "风险": "中"},
                "审核策略更改": {"当前": "无", "标准": "成功+失败", "风险": "中"},
                "审核账户管理": {"当前": "无", "标准": "成功+失败", "风险": "高"},
            },
            "服务配置": {
                "RemoteRegistry": {"当前": "运行", "标准": "停止", "风险": "高"},
                "Telnet": {"当前": "运行", "标准": "禁用", "风险": "高"},
                "PrintSpooler": {"当前": "运行", "标准": "停止(不需要打印)", "风险": "低"},
                "SMBv1": {"当前": "启用", "标准": "禁用", "风险": "高"},
            },
            "注册表安全": {
                "RestrictAnonymous": {"当前": 0, "标准": 1, "风险": "高"},
                "AutoShareServer": {"当前": 1, "标准": 0, "风险": "中"},
                "DisableCAD": {"当前": 1, "标准": 0, "风险": "低"},
                "NoAutoUpdate": {"当前": 1, "标准": 0, "风险": "中"},
            },
            "防火墙": {
                "状态": {"当前": "关闭", "标准": "开启", "风险": "高"},
                "入站规则数": {"当前": 25, "标准": "<10", "风险": "中"},
            },
            "自动更新": {
                "状态": {"当前": "禁用", "标准": "启用", "风险": "高"},
            },
        }

    def check(self) -> List[Dict]:
        """执行基线检查"""
        print("\n" + "=" * 60)
        print("Windows 安全基线检查")
        print("=" * 60)

        all_findings = []

        for category, items in self.系统配置.items():
            print("\n【%s】" % category)
            for name, config in items.items():
                current = str(config["当前"])
                standard = str(config["标准"])
                risk = config["风险"]
                is_ok = current == standard

                if not is_ok:
                    all_findings.append({
                        "category": category,
                        "name": name,
                        "current": current,
                        "standard": standard,
                        "risk": risk,
                    })
                    icon = "[!]" if risk == "高" else "[*]" if risk == "中" else "[-]"
                    print("  %s [%s] %s" % (icon, risk, name))
                    print("       当前: %s  标准: %s" % (current, standard))
                else:
                    print("  [OK] %s: %s" % (name, current))

        risk_count = defaultdict(int)
        for f in all_findings:
            risk_count[f["risk"]] += 1

        print("\n检查完成，发现 %d 项不符合基线" % len(all_findings))
        print("风险分布: 高危=%d 中危=%d 低危=%d" % (risk_count["高"], risk_count["中"], risk_count["低"]))
        print()

        return all_findings


# ============================================================
# 工具2: Linux安全基线检查器
# ============================================================

class LinuxBaselineChecker:
    """Linux安全基线检查工具"""

    def __init__(self):
        self.系统配置 = self._get_sample_config()
        self.findings = []

    def _get_sample_config(self) -> Dict:
        """获取模拟配置"""
        return {
            "SSH配置": {
                "PermitRootLogin": {"当前": "yes", "标准": "no", "风险": "高"},
                "PasswordAuthentication": {"当前": "yes", "标准": "no(密钥登录)", "风险": "中"},
                "PermitEmptyPasswords": {"当前": "no", "标准": "no", "风险": "低"},
                "X11Forwarding": {"当前": "yes", "标准": "no", "风险": "中"},
                "MaxAuthTries": {"当前": 6, "标准": 3, "风险": "中"},
                "Protocol": {"当前": "2", "标准": "2", "风险": "低"},
            },
            "用户账户": {
                "UID=0的用户数": {"当前": 2, "标准": 1, "风险": "高"},
                "空密码用户数": {"当前": 1, "标准": 0, "风险": "高"},
                "可登录用户数": {"当前": 15, "标准": "<10", "风险": "中"},
                "sudo用户数": {"当前": 5, "标准": "<3", "风险": "中"},
            },
            "文件权限": {
                "/etc/passwd": {"当前": "644", "标准": "644", "风险": "低"},
                "/etc/shadow": {"当前": "644", "标准": "600", "风险": "高"},
                "/etc/sudoers": {"当前": "640", "标准": "440", "风险": "中"},
                "/tmp": {"当前": "777 + sticky", "标准": "1777", "风险": "低"},
            },
            "内核参数": {
                "net.ipv4.ip_forward": {"当前": 1, "标准": 0, "风险": "中"},
                "net.ipv4.conf.all.accept_redirects": {"当前": 1, "标准": 0, "风险": "中"},
                "net.ipv4.icmp_echo_ignore_all": {"当前": 0, "标准": 1, "风险": "低"},
                "kernel.randomize_va_space": {"当前": 2, "标准": 2, "风险": "低"},
            },
            "服务配置": {
                "不必要服务数": {"当前": 8, "标准": "<3", "风险": "中"},
                "r服务(rcp/rsh/rexec)": {"当前": "存在", "标准": "移除", "风险": "高"},
                "telnet": {"当前": "已安装", "标准": "移除", "风险": "高"},
            },
        }

    def check(self) -> List[Dict]:
        """执行基线检查"""
        print("\n" + "=" * 60)
        print("Linux 安全基线检查")
        print("=" * 60)

        all_findings = []

        for category, items in self.系统配置.items():
            print("\n【%s】" % category)
            for name, config in items.items():
                current = str(config["当前"])
                standard = str(config["标准"])
                risk = config["风险"]
                is_ok = current == standard

                if not is_ok:
                    all_findings.append({
                        "category": category,
                        "name": name,
                        "current": current,
                        "standard": standard,
                        "risk": risk,
                    })
                    icon = "[!]" if risk == "高" else "[*]" if risk == "中" else "[-]"
                    print("  %s [%s] %s" % (icon, risk, name))
                    print("       当前: %s  标准: %s" % (current, standard))
                else:
                    print("  [OK] %s: %s" % (name, current))

        risk_count = defaultdict(int)
        for f in all_findings:
            risk_count[f["risk"]] += 1

        print("\n检查完成，发现 %d 项不符合基线" % len(all_findings))
        print("风险分布: 高危=%d 中危=%d 低危=%d" % (risk_count["高"], risk_count["中"], risk_count["低"]))
        print()

        return all_findings


# ============================================================
# 工具3: 恶意代码行为分析器
# ============================================================

class MalwareBehaviorAnalyzer:
    """恶意代码行为分析工具"""

    def __init__(self):
        self.行为日志 = self._get_sample_logs()

    def _get_sample_logs(self) -> List[Dict]:
        """获取模拟行为日志"""
        return [
            {"时间": "10:00:01", "类型": "进程创建", "进程": "svchost.exe", "父进程": "services.exe", "路径": "C:\\Windows\\System32\\svchost.exe", "风险": "低"},
            {"时间": "10:05:23", "类型": "进程创建", "进程": "powershell.exe", "父进程": "winword.exe", "路径": "C:\\Users\\user\\AppData\\Local\\Temp\\ps.exe", "风险": "高"},
            {"时间": "10:05:25", "类型": "文件操作", "进程": "powershell.exe", "操作": "写入", "路径": "C:\\Users\\user\\AppData\\Roaming\\mimikatz.exe", "风险": "高"},
            {"时间": "10:05:30", "类型": "注册表操作", "进程": "powershell.exe", "操作": "修改", "路径": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "风险": "高"},
            {"时间": "10:06:00", "类型": "网络连接", "进程": "powershell.exe", "方向": "出站", "目标IP": "192.168.1.100:4444", "风险": "高"},
            {"时间": "10:06:30", "类型": "进程创建", "进程": "cmd.exe", "父进程": "powershell.exe", "命令行": "cmd.exe /c whoami /priv", "风险": "中"},
            {"时间": "10:07:00", "类型": "进程创建", "进程": "mimikatz.exe", "父进程": "powershell.exe", "命令行": "mimikatz.exe privilege::debug sekurlsa::logonpasswords", "风险": "严重"},
            {"时间": "10:08:00", "类型": "网络连接", "进程": "mimikatz.exe", "方向": "出站", "目标IP": "attacker.com:8080", "风险": "严重"},
            {"时间": "10:10:00", "类型": "计划任务", "操作": "创建", "任务名": "Windows Update Service", "执行程序": "C:\\Users\\user\\AppData\\Roaming\\backdoor.exe", "风险": "高"},
        ]

    def analyze(self) -> Dict:
        """分析恶意行为"""
        print("\n" + "=" * 60)
        print("恶意代码行为分析")
        print("=" * 60)

        print("\n分析 %d 条行为日志..." % len(self.行为日志))
        print()

        risk_count = defaultdict(int)
        type_count = defaultdict(int)
        for log in self.行为日志:
            risk_count[log["风险"]] += 1
            type_count[log["类型"]] += 1

        print("行为类型分布:")
        for t, c in type_count.items():
            print("  %s: %d 条" % (t, c))

        print("\n风险分布:")
        print("  严重: %d 条" % risk_count["严重"])
        print("  高危: %d 条" % risk_count["高"])
        print("  中危: %d 条" % risk_count["中"])
        print("  低危: %d 条" % risk_count["低"])

        print("\n【可疑行为详情】")
        for log in self.行为日志:
            if log["风险"] in ["高", "严重"]:
                icon = "[!!]" if log["风险"] == "严重" else "[!]"
                print("  %s [%s] [%s] %s" % (icon, log["风险"], log["时间"], log["类型"]))
                print("       进程: %s" % log.get("进程", "N/A"))
                extra = log.get("命令行") or log.get("路径") or log.get("目标IP") or log.get("操作", "")
                print("       详情: %s" % extra)

        print("\n【攻击链分析】")
        print("  1. 初始访问: Word文档宏执行 -> PowerShell")
        print("  2. 工具下载: 下载 mimikatz 到本地")
        print("  3. 凭据窃取: mimikatz 抓取登录凭据")
        print("  4. 数据外传: 将凭据发送到C2服务器")
        print("  5. 持久化: 创建计划任务维持访问")
        print()

        return {"risk_count": dict(risk_count), "type_count": dict(type_count)}


# ============================================================
# 工具4: EDR检测规则生成器
# ============================================================

class EDRRuleGenerator:
    """EDR检测规则生成器"""

    @staticmethod
    def generate_sigma_rule(title: str, description: str,
                            detection: Dict = None, level: str = "high") -> str:
        """生成Sigma规则"""
        rule_lines = [
            "title: " + title,
            "id: %08d-abcd-efgh-ijkl-mnopqrstuvwx" % random.randint(10000000, 99999999),
            "status: experimental",
            "description: " + description,
            "author: Security Researcher",
            "date: " + datetime.now().strftime("%Y-%m-%d"),
            "tags:",
            "  - attack.execution",
            "logsource:",
            "  category: process_creation",
            "  product: windows",
            "detection:",
            "  selection:",
            "    Image|endswith:",
            "      - '\\\\powershell.exe'",
            "    CommandLine|contains:",
            "      - 'mimikatz'",
            "      - 'sekurlsa'",
            "  condition: selection",
            "falsepositives:",
            "  - 合法的安全测试",
            "level: " + level,
        ]
        return '\n'.join(rule_lines)

    @staticmethod
    def generate_yara_rule(rule_name: str, description: str,
                           strings: List[str], condition: str = "all of them") -> str:
        """生成YARA规则"""
        str_rules = ""
        for i, s in enumerate(strings, 1):
            str_rules += '        $str%d = "%s" ascii\n' % (i, s)

        rule = "rule " + rule_name + " {\n"
        rule += "    meta:\n"
        rule += '        description = "' + description + '"\n'
        rule += '        author = "Security Researcher"\n'
        rule += '        date = "' + datetime.now().strftime("%Y-%m-%d") + '"\n'
        rule += '        severity = "high"\n'
        rule += "    strings:\n"
        rule += str_rules
        rule += "    condition:\n"
        rule += "        " + condition + "\n"
        rule += "}"
        return rule

    @staticmethod
    def generate_sysmon_config() -> str:
        """生成Sysmon配置模板"""
        lines = [
            '<Sysmon schemaversion="4.80">',
            '  <!-- Sysmon 安全配置模板 -->',
            '  <EventFiltering>',
            '    <!-- 进程创建监控 -->',
            '    <ProcessCreate onmatch="exclude">',
            '      <Image condition="end with">\\\\svchost.exe</Image>',
            '    </ProcessCreate>',
            '',
            '    <!-- 网络连接监控 -->',
            '    <NetworkConnect onmatch="include">',
            '      <DestinationPort condition="is">4444</DestinationPort>',
            '      <DestinationPort condition="is">8080</DestinationPort>',
            '    </NetworkConnect>',
            '',
            '    <!-- 文件创建监控 -->',
            '    <FileCreate onmatch="include">',
            '      <TargetFilename condition="end with">.exe</TargetFilename>',
            '      <TargetFilename condition="end with">.dll</TargetFilename>',
            '      <TargetFilename condition="contains">\\\\AppData\\\\</TargetFilename>',
            '    </FileCreate>',
            '',
            '    <!-- 注册表修改监控 -->',
            '    <RegistryEvent onmatch="include">',
            '      <TargetObject condition="contains">\\\\CurrentVersion\\\\Run</TargetObject>',
            '    </RegistryEvent>',
            '  </EventFiltering>',
            '</Sysmon>',
        ]
        return '\n'.join(lines)

    @staticmethod
    def demo():
        """演示规则生成"""
        print("\n" + "=" * 60)
        print("EDR 检测规则生成器演示")
        print("=" * 60)

        print("\n[Sigma规则示例 - Mimikatz检测]")
        sigma = EDRRuleGenerator.generate_sigma_rule(
            "Mimikatz Credential Dumping",
            "检测mimikatz凭据转储工具的使用",
            {},
            "high"
        )
        print(sigma[:200] + "\n...")

        print("\n[YARA规则示例 - 恶意软件检测]")
        yara = EDRRuleGenerator.generate_yara_rule(
            "Malware_Sample_X",
            "检测X恶意软件家族",
            ["MZ", "This program cannot", "malware_marker_string"]
        )
        print(yara[:200] + "\n...")

        print("\n[Sysmon配置示例]")
        print(EDRRuleGenerator.generate_sysmon_config()[:200] + "\n...")
        print()


# ============================================================
# 工具5: 主机加固脚本生成器
# ============================================================

class HardeningScriptGenerator:
    """主机加固脚本生成器"""

    @staticmethod
    def generate_windows_hardening() -> str:
        """生成Windows加固脚本"""
        lines = [
            "@echo off",
            "echo ============================================",
            "echo Windows 安全加固脚本",
            "echo ============================================",
            "echo.",
            "",
            "REM 1. 密码策略",
            "echo [1/8] 配置密码策略...",
            "net accounts /minpwlen:8 /maxpwage:90 /minpwage:1 /uniquepw:5",
            "net accounts /lockoutthreshold:5 /lockoutduration:30 /lockoutwindow:30",
            "",
            "REM 2. 审核策略",
            "echo [2/8] 配置审核策略...",
            'auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable',
            'auditpol /set /category:"Account Management" /success:enable /failure:enable',
            'auditpol /set /category:"Policy Change" /success:enable /failure:enable',
            "",
            "REM 3. 禁用不必要服务",
            "echo [3/8] 禁用危险服务...",
            "sc config RemoteRegistry start= disabled",
            "sc config Telnet start= disabled",
            "sc config TFTP start= disabled",
            "",
            "REM 4. 防火墙配置",
            "echo [4/8] 启用防火墙...",
            "netsh advfirewall set allprofiles state on",
            "",
            "REM 5. 自动更新",
            "echo [5/8] 启用自动更新...",
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update" /v AUOptions /t REG_DWORD /d 3 /f',
            "",
            "REM 6. 禁用SMBv1",
            "echo [6/8] 禁用SMBv1...",
            "Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol",
            "",
            "REM 7. UAC设置",
            "echo [7/8] 启用UAC...",
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 1 /f',
            "",
            "REM 8. 事件日志",
            "echo [8/8] 配置事件日志大小...",
            "wevtutil sl Security /ms:262144000",
            "wevtutil sl System /ms:262144000",
            "",
            "echo.",
            "echo ============================================",
            "echo 加固完成，请重启系统",
            "echo ============================================",
            "pause",
        ]
        return '\n'.join(lines)

    @staticmethod
    def generate_linux_hardening() -> str:
        """生成Linux加固脚本"""
        lines = [
            "#!/bin/bash",
            "# ============================================",
            "# Linux 安全加固脚本",
            "# ============================================",
            "",
            'echo "[1/10] 更新系统..."',
            "apt update && apt upgrade -y",
            "",
            'echo "[2/10] 配置SSH安全..."',
            "sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config",
            "sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config",
            "sed -i 's/#MaxAuthTries 6/MaxAuthTries 3/' /etc/ssh/sshd_config",
            "systemctl restart sshd",
            "",
            'echo "[3/10] 设置密码策略..."',
            "sed -i 's/PASS_MAX_DAYS.*/PASS_MAX_DAYS 90/' /etc/login.defs",
            "sed -i 's/PASS_MIN_LEN.*/PASS_MIN_LEN 8/' /etc/login.defs",
            "",
            'echo "[4/10] 配置防火墙(ufw)..."',
            "ufw default deny incoming",
            "ufw default allow outgoing",
            "ufw allow 22",
            "ufw allow 80",
            "ufw allow 443",
            "ufw enable",
            "",
            'echo "[5/10] 禁用不必要服务..."',
            "systemctl disable telnet",
            "systemctl disable rsh",
            "systemctl disable rexec",
            "",
            'echo "[6/10] 配置文件权限..."',
            "chmod 600 /etc/shadow",
            "chmod 644 /etc/passwd",
            "chmod 440 /etc/sudoers",
            "",
            'echo "[7/10] 内核参数加固..."',
            'echo "net.ipv4.ip_forward = 0" >> /etc/sysctl.conf',
            'echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.conf',
            'echo "net.ipv4.conf.all.accept_source_route = 0" >> /etc/sysctl.conf',
            'echo "kernel.randomize_va_space = 2" >> /etc/sysctl.conf',
            "sysctl -p",
            "",
            'echo "[8/10] 配置审计服务..."',
            "systemctl enable auditd",
            "systemctl start auditd",
            "",
            'echo "[9/10] 安装入侵检测..."',
            "apt install -y rkhunter chkrootkit",
            "",
            'echo "[10/10] 禁用SUID程序..."',
            "chmod u-s /usr/bin/find",
            "chmod u-s /usr/bin/wget",
            "",
            'echo ""',
            'echo "============================================"',
            'echo "加固完成，请重启系统"',
            'echo "============================================"',
        ]
        return '\n'.join(lines)

    @staticmethod
    def demo():
        """演示加固脚本生成"""
        print("\n" + "=" * 60)
        print("主机加固脚本生成器演示")
        print("=" * 60)

        print("\n[Windows加固脚本示例]")
        win_script = HardeningScriptGenerator.generate_windows_hardening()
        print(win_script[:300] + "\n...")

        print("\n[Linux加固脚本示例]")
        linux_script = HardeningScriptGenerator.generate_linux_hardening()
        print(linux_script[:300] + "\n...")
        print()


# ============================================================
# 主菜单
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("终端安全工具包 (Endpoint Security Toolkit)")
    print("=" * 60)
    print("""
请选择工具:
  1. Windows安全基线检查
  2. Linux安全基线检查
  3. 恶意代码行为分析
  4. EDR检测规则生成器
  5. 主机加固脚本生成器
  6. 运行全部演示
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
            WindowsBaselineChecker().check()
        elif choice == "2":
            LinuxBaselineChecker().check()
        elif choice == "3":
            MalwareBehaviorAnalyzer().analyze()
        elif choice == "4":
            EDRRuleGenerator.demo()
        elif choice == "5":
            HardeningScriptGenerator.demo()
        elif choice == "6":
            print("\n[*] 运行全部工具演示...\n")
            WindowsBaselineChecker().check()
            LinuxBaselineChecker().check()
            MalwareBehaviorAnalyzer().analyze()
            EDRRuleGenerator.demo()
            HardeningScriptGenerator.demo()
            print("\n[*] 全部演示完成！")
        else:
            print("无效选项，请重新输入")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
