# -*- coding: utf-8 -*-
"""
=============================================================================
移动应用安全实战案例
=============================================================================

安全声明：
    本文件仅用于授权安全测试和教育目的。
    所有代码均为教学演示，使用模拟数据，不涉及真实应用或系统。
    未经授权对他人应用进行安全测试是违法行为，请务必在获得书面授权后
    进行安全评估工作。作者不对任何滥用本代码的行为负责。

功能概览：
    1. APK静态分析工具 - 解析AndroidManifest.xml、检查导出组件、硬编码密钥检测
    2. Android组件安全检测 - Activity/Service/Receiver/Provider导出漏洞扫描
    3. 移动应用流量抓包与中间人攻击检测
    4. iOS应用安全检查 - IPA解包分析、Info.plist安全配置检查
    5. 移动应用加固检测 - 代码混淆检查、反调试检测
    6. 数据存储安全审计 - SharedPreferences/SQLite/外部存储敏感数据扫描

作者：移动应用安全学习工具
版本：1.0.0
日期：2024-01-01
=============================================================================
"""

import os
import re
import json
import hashlib
import base64
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from xml.etree import ElementTree as ET


# ============================================================================
#  模拟数据定义区
# ============================================================================

# 模拟的 AndroidManifest.xml 内容
模拟AndroidManifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.vulnerableapp"
    versionCode="15"
    versionName="2.3.1">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.READ_SMS" />
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />

    <application
        android:name=".MyApplication"
        android:debuggable="true"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".AdminActivity"
            android:exported="true"
            android:permission="" />

        <activity
            android:name=".LoginActivity"
            android:exported="false" />

        <service
            android:name=".BackgroundService"
            android:exported="true" />

        <receiver
            android:name=".SMSReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.provider.Telephony.SMS_RECEIVED" />
            </intent-filter>
        </receiver>

        <provider
            android:name=".ContentProvider"
            android:authorities="com.example.vulnerableapp.provider"
            android:exported="true"
            android:grantUriPermission="true" />

    </application>
</manifest>
"""

# 模拟的APK中DEX文件反编译代码片段（含硬编码敏感信息）
模拟反编译代码 = """
public class AppConfig {
    private static final String API_KEY = "sk-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c";
    private static final String SECRET_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
    private static final String DB_PASSWORD = "P@ssw0rd123!";

    // AWS凭证
    private static final String AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE";
    private static final String AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";

    // 服务器地址
    private static final String SERVER_URL = "http://192.168.1.100:8080/api/v1/";

    public static String encrypt(String data) {
        // 使用硬编码的AES密钥
        String key = "1234567890abcdef";
        // AES加密实现（简化）
        return Base64.encodeToString(data.getBytes(), 0);
    }

    public static boolean checkDebug() {
        // 弱调试检测 - 仅检查Debug.isDebuggerConnected()
        return android.os.Debug.isDebuggerConnected();
    }

    public static String getDeviceID(Context context) {
        // 收集设备信息并上传
        String imei = ((TelephonyManager)context.getSystemService(Context.TELEPHONY_SERVICE)).getDeviceId();
        return imei;
    }
}
"""

# 模拟的 iOS Info.plist 内容
模拟InfoPlist = {
    "CFBundleName": "VulnerableApp",
    "CFBundleIdentifier": "com.example.vulnerableapp",
    "CFBundleShortVersionString": "2.3.1",
    "CFBundleVersion": "15",
    "UIRequiredDeviceCapabilities": ["armv7"],
    "UISupportedInterfaceOrientations": ["UIInterfaceOrientationPortrait"],
    "NSAppTransportSecurity": {
        "NSAllowsArbitraryLoads": True,
        "NSAllowsLocalNetworking": True
    },
    "NSCameraUsageDescription": "需要访问相机",
    "NSLocationWhenInUseUsageDescription": "需要获取位置信息",
    "NSContactsUsageDescription": "需要访问通讯录",
    "NSPhotoLibraryUsageDescription": "需要访问相册",
    "UIBackgroundModes": ["remote-notification", "audio"],
    "LSApplicationQueriesSchemes": ["weixin", "alipay", "mqq"],
    "CFBundleURLTypes": [
        {
            "CFBundleURLName": "com.example.vulnerableapp",
            "CFBundleURLSchemes": ["vulnerableapp"]
        }
    ]
}

# 模拟的SharedPreferences数据
模拟SharedPreferences = {
    "user_session": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.signature",
    "user_password": "Admin@123456",
    "auth_token": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSJ9.sig",
    "remember_login": "true",
    "last_login_time": "2024-01-15 10:30:00",
    "server_address": "http://192.168.1.100:8080",
    "api_key": "sk-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c",
    "device_id": "356938035634534",
    "gps_location": "39.9042,116.4074",
    "payment_info": "6222020200112345678",
    "contact_list_sync": "true"
}

# 模拟的SQLite数据库内容
模拟SQLite数据 = [
    {"表名": "users", "列": ["id", "username", "password", "email", "phone", "idcard", "realname"]},
    {"表名": "payment", "列": ["id", "card_no", "cvv", "expiry", "amount"]},
    {"表名": "messages", "列": ["id", "from_user", "to_user", "content", "timestamp"]},
    {"表名": "location_history", "列": ["id", "lat", "lng", "timestamp", "address"]},
    {"表名": "contacts", "列": ["id", "name", "phone", "email"]},
]

# 模拟的网络抓包数据
模拟抓包数据 = [
    {"协议": "HTTP", "方法": "POST", "URL": "http://192.168.1.100:8080/api/v1/login",
     "请求体": "username=admin&password=Admin@123456", "风险": "明文传输凭据"},
    {"协议": "HTTP", "方法": "GET", "URL": "http://192.168.1.100:8080/api/v1/user/profile",
     "请求体": "", "风险": "无加密传输用户数据"},
    {"协议": "HTTP", "方法": "POST", "URL": "http://192.168.1.100:8080/api/v1/payment",
     "请求体": "card_no=6222020200112345678&cvv=123&amount=99.00", "风险": "明文传输支付信息"},
    {"协议": "HTTPS", "方法": "POST", "URL": "https://api.example.com/auth/token",
     "请求体": "grant_type=password&username=admin", "风险": "正常加密传输"},
]

# 模拟的加固检测结果
模拟加固信息 = {
    "是否加壳": False,
    "壳类型": "无",
    "代码混淆": False,
    "混淆工具": "无",
    "反调试检测": False,
    "反调试方式": [],
    "完整性校验": False,
    "签名校验": False,
    "SO层保护": False,
    "资源加密": False,
}

# 模拟APK文件结构
模拟APK结构 = {
    "AndroidManifest.xml": "二进制XML文件",
    "classes.dex": "Dalvik字节码",
    "classes2.dex": "Dalvik字节码(多DEX)",
    "resources.arsc": "编译后的资源文件",
    "res/": "资源文件目录",
    "assets/": "原始资产文件",
    "lib/": "Native库目录",
    "META-INF/": "签名信息",
    "lib/armeabi-v7a/libnative.so": "ARM原生库",
    "lib/arm64-v8a/libnative.so": "ARM64原生库",
}


# ============================================================================
#  第一部分：APK静态分析工具
# ============================================================================

class APK静态分析器:
    """
    APK静态分析工具

    功能说明：
        - 解析AndroidManifest.xml，提取应用基本信息
        - 检查导出组件，识别安全风险
        - 检测硬编码密钥、Token等敏感信息
        - 分析APK文件结构
        - 检查应用安全配置（debuggable、allowBackup等）

    技术原理：
        APK文件本质是一个ZIP压缩包，包含：
        - AndroidManifest.xml: 应用清单文件（编译为二进制XML）
        - classes.dex: Dalvik虚拟机字节码
        - resources.arsc: 编译后的资源表
        - res/: 资源文件
        - lib/: Native库
        - META-INF/: 签名信息

        静态分析通过解析这些文件，发现潜在安全漏洞，
        不需要运行应用即可发现大量安全问题。
    """

    def __init__(self, apk路径: str = "模拟APK"):
        """初始化APK分析器"""
        self.apk路径 = apk路径
        self.分析结果 = {
            "应用信息": {},
            "权限列表": [],
            "组件列表": [],
            "安全问题": [],
            "文件结构": {},
        }
        self.风险等级 = {"高": 0, "中": 0, "低": 0}
        print(f"[初始化] APK静态分析器已就绪，目标: {apk路径}")

        # APK结构分析
        self._分析APK结构()

    def _分析APK结构(self):
        """分析APK文件内部结构"""
        print("\n" + "=" * 70)
        print("【步骤1】APK文件结构分析")
        print("=" * 70)
        print(f"正在分析APK文件: {self.apk路径}")
        print("-" * 70)

        for 文件, 说明 in 模拟APK结构.items():
            文件类型 = "目录" if 文件.endswith("/") else "文件"
            print(f"  [{文件类型:4s}] {文件:45s} {说明}")

        self.分析结果["文件结构"] = 模拟APK结构
        print(f"\n共发现 {len(模拟APK结构)} 个文件/目录")

    def 解析AndroidManifest(self, manifest内容: str = 模拟AndroidManifest):
        """
        解析AndroidManifest.xml

        技术说明：
            AndroidManifest.xml是APK的核心配置文件，包含：
            - 应用包名、版本号
            - 申请的权限
            - 四大组件声明（Activity/Service/Receiver/Provider）
            - 应用安全属性配置

            原始APK中的Manifest是二进制XML格式（AXML），
            需要使用专门的解析器（如apktool）还原为文本XML。
            本示例使用文本XML模拟解析过程。
        """
        print("\n" + "=" * 70)
        print("【步骤2】AndroidManifest.xml 解析")
        print("=" * 70)

        try:
            # 解析XML
            root = ET.fromstring(manifest内容)

            # 提取应用基本信息
            包名 = root.attrib.get("package", "未知")
            版本号 = root.attrib.get("versionCode", "未知")
            版本名 = root.attrib.get("versionName", "未知")

            应用信息 = {
                "包名": 包名,
                "版本号": 版本号,
                "版本名": 版本名,
            }

            print(f"  包名:        {包名}")
            print(f"  版本号:      {版本号}")
            print(f"  版本名:      {版本名}")

            # 提取权限列表
            权限列表 = []
            命名空间 = "{http://schemas.android.com/apk/res/android}"

            for perm in root.iter("uses-permission"):
                权限名 = perm.attrib.get(f"{命名空间}name", "未知")
                权限列表.append(权限名)

            print(f"\n  申请权限 ({len(权限列表)} 个):")
            for i, p in enumerate(权限列表, 1):
                风险 = self._评估权限风险(p)
                print(f"    {i:2d}. {p}")
                print(f"        风险等级: {风险}")

            self.分析结果["应用信息"] = 应用信息
            self.分析结果["权限列表"] = 权限列表

            # 检查应用安全配置
            self._检查安全配置(root, 命名空间)

            # 提取组件信息
            self._提取组件信息(root, 命名空间)

            return 应用信息

        except ET.ParseError as e:
            print(f"  [错误] XML解析失败: {e}")
            return None

    def _评估权限风险(self, 权限名: str) -> str:
        """评估权限的风险等级"""
        高风险权限 = {
            "SEND_SMS", "READ_SMS", "READ_CONTACTS", "WRITE_CONTACTS",
            "READ_PHONE_STATE", "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION",
            "RECORD_AUDIO", "CAMERA", "READ_EXTERNAL_STORAGE",
            "WRITE_EXTERNAL_STORAGE", "READ_CALL_LOG", "CALL_PHONE",
            "SYSTEM_ALERT_WINDOW", "REQUEST_INSTALL_PACKAGES"
        }
        低风险权限 = {
            "INTERNET", "ACCESS_NETWORK_STATE", "ACCESS_WIFI_STATE",
            "WAKE_LOCK", "VIBRATE", "FOREGROUND_SERVICE"
        }

        # 提取权限名称的核心部分
        核心名 = 权限名.split(".")[-1] if "." in 权限名 else 权限名

        if 核心名 in 高风险权限:
            return "高"
        elif 核心名 in 低风险权限:
            return "低"
        else:
            return "中"

    def _检查安全配置(self, root, 命名空间):
        """检查应用级别的安全配置"""
        print("\n  安全配置检查:")
        print("-" * 50)

        app_elem = root.find("application")
        if app_elem is not None:
            debuggable = app_elem.attrib.get(f"{命名空间}debuggable", "false")
            allowBackup = app_elem.attrib.get(f"{命名空间}allowBackup", "true")

            # debuggable检查
            if debuggable == "true":
                print(f"    [!] android:debuggable = true  -> 高风险: 可被调试器附加")
                self._添加安全问题("高", "debuggable=true",
                                   "应用可在调试模式下运行，攻击者可附加调试器获取运行时数据")
            else:
                print(f"    [OK] android:debuggable = false -> 正常")

            # allowBackup检查
            if allowBackup == "true":
                print(f"    [!] android:allowBackup = true  -> 中风险: 可被adb backup提取数据")
                self._添加安全问题("中", "allowBackup=true",
                                   "应用数据可被adb backup提取，可能导致敏感数据泄露")
            else:
                print(f"    [OK] android:allowBackup = false -> 正常")

    def _提取组件信息(self, root, 命名空间):
        """提取四大组件信息"""
        组件类型映射 = {
            "activity": "Activity",
            "activity-alias": "Activity Alias",
            "service": "Service",
            "receiver": "Broadcast Receiver",
            "provider": "Content Provider"
        }

        print("\n  组件清单:")
        print("-" * 50)

        组件列表 = []
        for 标签名, 类型名 in 组件类型映射.items():
            for 组件 in root.iter(标签名):
                组件名 = 组件.attrib.get(f"{命名空间}name", "未知")
                导出 = 组件.attrib.get(f"{命名空间}exported", "未指定")
                权限 = 组件.attrib.get(f"{命名空间}permission", "无")

                组件信息 = {
                    "类型": 类型名,
                    "名称": 组件名,
                    "导出": 导出,
                    "权限": 权限
                }
                组件列表.append(组件信息)

                print(f"    [{类型名:18s}] {组件名}")
                print(f"      exported={导出}, permission={权限}")

        self.分析结果["组件列表"] = 组件列表

    def 检测硬编码密钥(self, 代码内容: str = 模拟反编译代码):
        """
        检测硬编码的敏感信息

        技术说明：
            通过反编译DEX文件获取Java源码后，使用正则表达式
            扫描硬编码的敏感信息：
            - API密钥 (API_KEY, api_key, sk-xxx)
            - 访问令牌 (TOKEN, token, ghp_xxx)
            - 密码 (PASSWORD, password, pwd)
            - AWS密钥 (AKIA开头)
            - 加密密钥 (key, secret)
            - 数据库连接字符串
            - 服务器地址

            硬编码密钥是移动应用最常见的安全漏洞之一，
            攻击者可通过反编译直接获取这些敏感信息。
        """
        print("\n" + "=" * 70)
        print("【步骤3】硬编码密钥检测")
        print("=" * 70)
        print("正在扫描反编译代码中的敏感信息...\n")

        # 定义敏感信息检测正则表达式
        检测规则 = {
            "API密钥": [
                r'(?:api_key|API_KEY|apikey)\s*[=:]\s*["\']([^"\']{20,})["\']',
                r'sk-[a-zA-Z0-9]{20,}',
            ],
            "访问令牌": [
                r'(?:token|TOKEN|Token)\s*[=:]\s*["\']([^"\']{20,})["\']',
                r'ghp_[a-zA-Z0-9]{36}',
            ],
            "密码": [
                r'(?:password|PASSWORD|passwd|pwd)\s*[=:]\s*["\']([^"\']{3,})["\']',
            ],
            "AWS密钥": [
                r'AKIA[A-Z0-9]{16}',
                r'aws_secret_access_key\s*[=:]\s*["\']([^"\']{20,})["\']',
            ],
            "加密密钥": [
                r'(?:secret|SECRET|Secret|key|KEY|Key)\s*[=:]\s*["\']([^"\']{8,32})["\']',
            ],
            "服务器地址": [
                r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+',
            ],
            "AES密钥": [
                r'(?:AES|aes)\s*(?:key|KEY)\s*[=:]\s*["\']([a-zA-Z0-9]{16})["\']',
            ],
        }

        发现列表 = []
        代码行列表 = 代码内容.strip().split("\n")

        for 行号, 行内容 in enumerate(代码行列表, 1):
            for 类型, 规则列表 in 检测规则.items():
                for 规则 in 规则列表:
                    匹配结果 = re.search(规则, 行内容)
                    if 匹配结果:
                        匹配值 = 匹配结果.group(0)
                        发现列表.append({
                            "行号": 行号,
                            "类型": 类型,
                            "匹配": 匹配值,
                            "代码": 行内容.strip()
                        })

        # 输出检测结果
        if 发现列表:
            print(f"  [!] 发现 {len(发现列表)} 处硬编码敏感信息:\n")
            for i, 发现 in enumerate(发现列表, 1):
                print(f"  {i}. 行{发现['行号']:3d} [{发现['类型']}]")
                print(f"     匹配: {发现['匹配']}")
                print(f"     代码: {发现['代码']}")
                print()
                self._添加安全问题("高", f"硬编码{发现['类型']}",
                                   f"在代码中硬编码了{发现['类型']}，可被反编译获取")
        else:
            print("  [OK] 未发现硬编码敏感信息")

        return 发现列表

    def _添加安全问题(self, 风险: str, 标题: str, 描述: str):
        """添加安全问题"""
        self.分析结果["安全问题"].append({
            "风险": 风险,
            "标题": 标题,
            "描述": 描述
        })
        self.风险等级[风险] = self.风险等级.get(风险, 0) + 1

    def 生成分析报告(self):
        """生成静态分析报告"""
        print("\n" + "=" * 70)
        print("【步骤4】静态分析报告")
        print("=" * 70)

        总问题数 = len(self.分析结果["安全问题"])
        print(f"\n  分析目标: {self.apk路径}")
        print(f"  权限数量: {len(self.分析结果['权限列表'])}")
        print(f"  组件数量: {len(self.分析结果['组件列表'])}")
        print(f"  安全问题: {总问题数} 个")
        print(f"    - 高风险: {self.风险等级['高']} 个")
        print(f"    - 中风险: {self.风险等级['中']} 个")
        print(f"    - 低风险: {self.风险等级['低']} 个")

        if self.分析结果["安全问题"]:
            print("\n  安全问题详情:")
            for i, 问题 in enumerate(self.分析结果["安全问题"], 1):
                标识 = {"高": "!!", "中": "!", "低": "?"}
                print(f"    {i}. [{标识[问题['风险']]}] {问题['标题']} ({问题['风险']}风险)")
                print(f"       {问题['描述']}")

        # 安全评分
        评分 = 100
        评分 -= self.风险等级["高"] * 15
        评分 -= self.风险等级["中"] * 8
        评分 -= self.风险等级["低"] * 3
        评分 = max(0, 评分)
        评级 = "A" if 评分 >= 90 else "B" if 评分 >= 75 else "C" if 评分 >= 60 else "D" if 评分 >= 40 else "F"

        print(f"\n  安全评分: {评分}/100 ({评级}级)")

        return {
            "总问题数": 总问题数,
            "风险分布": self.风险等级,
            "安全评分": 评分,
            "安全评级": 评级
        }


# ============================================================================
#  第二部分：Android组件安全检测
# ============================================================================

class Android组件安全检测器:
    """
    Android组件安全检测工具

    功能说明：
        - 扫描导出的Activity组件（可能被越权调用）
        - 检测导出的Service组件（可能被恶意启动）
        - 检查导出的BroadcastReceiver（可能被伪造广播触发）
        - 分析导出的ContentProvider（可能存在数据泄露/SQL注入）
        - 识别未受权限保护的导出组件

    技术原理：
        Android四大组件（Activity、Service、BroadcastReceiver、
        ContentProvider）可以通过 android:exported="true" 导出，
        使其他应用可以调用。如果导出组件没有适当的权限保护，
        可能导致：
        - 越权访问敏感功能
        - 数据泄露
        - 组件注入攻击
        - 恶意应用伪造Intent触发行为

        安全检测的核心是识别"导出 + 无权限保护"的危险组件。
    """

    # 组件安全等级定义
    组件风险规则 = {
        "Activity": {
            "导出无权限": ("高", "可被任意应用启动，可能导致越权操作"),
            "导出有权限": ("低", "已有权限保护，风险较低"),
            "未导出": ("安全", "组件未导出，无外部访问风险"),
        },
        "Service": {
            "导出无权限": ("高", "可被恶意应用启动/绑定，执行后台任务"),
            "导出有权限": ("低", "已有权限保护"),
            "未导出": ("安全", "组件未导出"),
        },
        "Broadcast Receiver": {
            "导出无权限": ("高", "可被伪造广播触发，执行恶意逻辑"),
            "导出有权限": ("低", "已有权限保护"),
            "未导出": ("安全", "组件未导出"),
        },
        "Content Provider": {
            "导出无权限": ("高", "可被任意应用访问，存在数据泄露风险"),
            "导出有权限": ("中", "权限保护可能不足"),
            "未导出": ("安全", "组件未导出"),
            "grantUriPermission": ("高", "允许URI授权转移，可能被利用"),
        }
    }

    def __init__(self):
        self.检测结果 = []
        print("[初始化] Android组件安全检测器已就绪")

    def 扫描组件(self, 组件列表: List[Dict]):
        """
        扫描组件安全状态

        参数:
            组件列表: 从AndroidManifest解析的组件信息列表
        """
        print("\n" + "=" * 70)
        print("Android组件安全扫描")
        print("=" * 70)

        for 组件 in 组件列表:
            类型 = 组件["类型"]
            名称 = 组件["名称"]
            导出 = 组件["导出"]
            权限 = 组件["权限"]

            print(f"\n  组件: [{类型}] {名称}")
            print(f"  exported = {导出}")
            print(f"  permission = {权限}")

            # 判断安全状态
            风险, 描述 = self._评估组件风险(类型, 导出, 权限, 组件)

            if 风险 == "安全":
                print(f"  [OK] 状态: {描述}")
            elif 风险 == "低":
                print(f"  [?]  状态: {描述}")
            else:
                print(f"  [!!] 状态: {风险}风险 - {描述}")
                # 提供修复建议
                建议 = self._生成修复建议(类型, 名称)
                print(f"  [修复] {建议}")

            self.检测结果.append({
                "组件类型": 类型,
                "组件名称": 名称,
                "风险等级": 风险,
                "描述": 描述,
                "导出状态": 导出,
                "权限保护": 权限
            })

    def _评估组件风险(self, 类型: str, 导出: str, 权限: str, 组件: dict) -> Tuple[str, str]:
        """评估单个组件的风险等级"""
        if 导出 not in ("true", True):
            return "安全", "组件未导出，无外部访问风险"

        # 导出组件
        if 权限 in ("无", "", None):
            规则 = self.组件风险规则.get(类型, {}).get("导出无权限", ("高", "存在安全风险"))
            return 规则
        else:
            规则 = self.组件风险规则.get(类型, {}).get("导出有权限", ("低", "已有权限保护"))
            return 规则

    def _生成修复建议(self, 类型: str, 名称: str) -> str:
        """生成组件安全修复建议"""
        建议 = {
            "Activity": f"将 {名称} 的 android:exported 设置为 false，或添加自定义权限保护",
            "Service": f"将 {名称} 的 android:exported 设置为 false，或添加签名级权限",
            "Broadcast Receiver": f"将 {名称} 设置为未导出，使用 LocalBroadcastManager",
            "Content Provider": f"为 {名称} 添加读写权限，设置 android:exported=false，关闭 grantUriPermission"
        }
        return 建议.get(类型, "将组件设置为未导出或添加权限保护")

    def 模拟组件攻击(self):
        """
        模拟对导出组件的攻击

        技术说明：
            演示如何通过Intent调用其他应用的导出组件。
            实际安全测试中使用adb命令或测试代码验证组件是否可被调用。
        """
        print("\n" + "=" * 70)
        print("组件攻击模拟测试")
        print("=" * 70)

        # 模拟攻击测试
        测试用例 = [
            {
                "目标组件": "AdminActivity",
                "攻击方式": "直接启动导出的AdminActivity",
                "adb命令": "adb shell am start -n com.example.vulnerableapp/.AdminActivity",
                "结果": "成功启动 -> 攻击者可访问管理界面",
                "风险": "高",
            },
            {
                "目标组件": "BackgroundService",
                "攻击方式": "启动/绑定导出的Service",
                "adb命令": "adb shell am startservice -n com.example.vulnerableapp/.BackgroundService",
                "结果": "成功启动 -> 攻击者可触发后台服务",
                "风险": "高",
            },
            {
                "目标组件": "SMSReceiver",
                "攻击方式": "发送伪造短信广播",
                "adb命令": "adb shell am broadcast -a android.provider.Telephony.SMS_RECEIVED",
                "结果": "成功触发 -> 攻击者可伪造短信触发接收器",
                "风险": "高",
            },
            {
                "目标组件": "ContentProvider",
                "攻击方式": "通过content URI查询数据",
                "adb命令": "adb shell content query --uri content://com.example.vulnerableapp.provider/users",
                "结果": "成功查询 -> 攻击者可读取敏感数据",
                "风险": "高",
            }
        ]

        for i, 测试 in enumerate(测试用例, 1):
            print(f"\n  测试{i}: {测试['攻击方式']}")
            print(f"  目标: {测试['目标组件']}")
            print(f"  命令: {测试['adb命令']}")
            print(f"  结果: {测试['结果']}")
            print(f"  风险: {测试['风险']}")

    def 输出检测报告(self):
        """输出组件安全检测报告"""
        print("\n" + "=" * 70)
        print("组件安全检测报告")
        print("=" * 70)

        高风险 = [r for r in self.检测结果 if r["风险等级"] == "高"]
        中风险 = [r for r in self.检测结果 if r["风险等级"] == "中"]
        低风险 = [r for r in self.检测结果 if r["风险等级"] == "低"]
        安全 = [r for r in self.检测结果 if r["风险等级"] == "安全"]

        print(f"\n  组件总数: {len(self.检测结果)}")
        print(f"  高风险:   {len(高风险)} 个")
        print(f"  中风险:   {len(中风险)} 个")
        print(f"  低风险:   {len(低风险)} 个")
        print(f"  安全:     {len(安全)} 个")

        if 高风险:
            print("\n  高风险组件列表:")
            for r in 高风险:
                print(f"    [{r['组件类型']:18s}] {r['组件名称']}")
                print(f"      导出={r['导出状态']}, 权限={r['权限保护']}")

        return {
            "高风险数": len(高风险),
            "中风险数": len(中风险),
            "低风险数": len(低风险),
            "安全数": len(安全)
        }


# ============================================================================
#  第三部分：移动应用流量抓包与中间人攻击检测
# ============================================================================

class 流量安全分析器:
    """
    移动应用流量抓包与中间人攻击检测

    功能说明：
        - 分析应用网络流量，识别明文传输
        - 检测证书校验是否安全
        - 检查SSL/TLS配置是否正确
        - 识别中间人攻击风险
        - 分析API通信安全

    技术原理：
        移动应用通过HTTP/HTTPS与后端通信。安全分析需要：
        1. 使用代理工具（如Burp Suite、Charles）抓取应用流量
        2. 检查是否使用HTTPS加密传输
        3. 验证证书校验实现是否安全（是否信任所有证书）
        4. 检查是否有证书绑定（Certificate Pinning）
        5. 分析API是否传输敏感数据

        常见漏洞：
        - 使用HTTP明文传输敏感数据
        - 自定义TrustManager信任所有证书
        - 未实现证书绑定
        - API密钥在URL参数中传输
    """

    def __init__(self):
        self.流量记录 = []
        self.安全风险 = []
        print("[初始化] 流量安全分析器已就绪")

    def 分析流量(self, 抓包数据: List[Dict] = 模拟抓包数据):
        """
        分析网络流量数据

        参数:
            抓包数据: 抓包工具导出的流量记录列表
        """
        print("\n" + "=" * 70)
        print("网络流量安全分析")
        print("=" * 70)
        print(f"共分析 {len(抓包数据)} 条流量记录\n")

        for i, 流量 in enumerate(抓包数据, 1):
            协议 = 流量["协议"]
            方法 = 流量["方法"]
            URL = 流量["URL"]
            请求体 = 流量["请求体"]
            风险 = 流量["风险"]

            print(f"  [{i}] {协议} {方法} {URL}")
            if 请求体:
                print(f"      请求体: {请求体}")
            print(f"      风险:   {风险}")

            # 检查协议安全性
            if 协议 == "HTTP":
                self.安全风险.append({
                    "风险等级": "高",
                    "问题": "使用HTTP明文传输",
                    "URL": URL,
                    "描述": "数据未加密，可被中间人窃听/篡改"
                })

                # 检查请求体中是否含敏感数据
                if self._检查敏感数据(请求体):
                    self.安全风险.append({
                        "风险等级": "高",
                        "问题": "明文传输敏感数据",
                        "URL": URL,
                        "描述": f"请求体中包含敏感信息: {请求体}"
                    })

            # 检查URL参数中的敏感信息
            if "?" in URL:
                参数部分 = URL.split("?")[1]
                if self._检查敏感数据(参数部分):
                    self.安全风险.append({
                        "风险等级": "中",
                        "问题": "URL参数包含敏感信息",
                        "URL": URL,
                        "描述": "敏感信息在URL参数中传输，可能被日志/缓存记录"
                    })

            self.流量记录.append(流量)
            print()

    def _检查敏感数据(self, 数据: str) -> bool:
        """检查数据中是否包含敏感信息"""
        敏感关键词 = ["password", "pwd", "token", "key", "secret",
                      "card", "cvv", "身份证", "密码", "token"]
        数据小写 = 数据.lower()
        return any(kw in 数据小写 for kw in 敏感关键词)

    def 检查证书安全(self):
        """
        检查应用的SSL/TLS证书校验安全性

        技术说明：
            安全的HTTPS实现应该：
            1. 验证服务器证书链
            2. 检查证书有效期
            3. 验证证书域名匹配
            4. 实施证书绑定（Certificate Pinning）

            不安全的实现：
            - 自定义TrustManager信任所有证书
            - HostnameVerifier允许所有主机名
            - 未实现证书绑定
        """
        print("=" * 70)
        print("SSL/TLS证书安全检查")
        print("=" * 70)

        检查项 = [
            ("证书链验证", False, "高",
             "自定义TrustManager信任所有证书，中间人可替换证书"),
            ("域名验证", False, "高",
             "HostnameVerifier允许所有主机名，无法防止域名欺骗"),
            ("证书绑定", False, "中",
             "未实施Certificate Pinning，可能遭受中间人攻击"),
            ("证书过期检查", True, "低",
             "已实现证书过期检查"),
            ("自签名证书处理", False, "中",
             "允许自签名证书，存在安全风险"),
        ]

        for 检查, 通过, 风险, 描述 in 检查项:
            状态 = "[OK] " if 通过 else "[!!] "
            print(f"  {状态}{检查}: {'通过' if 通过 else '未通过'}")
            print(f"        {描述}")
            if not 通过:
                self.安全风险.append({
                    "风险等级": 风险,
                    "问题": f"证书安全: {检查}",
                    "URL": "全局",
                    "描述": 描述
                })

    def 生成流量报告(self):
        """生成流量安全分析报告"""
        print("\n" + "=" * 70)
        print("流量安全分析报告")
        print("=" * 70)

        高风险 = [r for r in self.安全风险 if r["风险等级"] == "高"]
        中风险 = [r for r in self.安全风险 if r["风险等级"] == "中"]
        低风险 = [r for r in self.安全风险 if r["风险等级"] == "低"]

        print(f"\n  流量总数:   {len(self.流量记录)}")
        print(f"  HTTP流量:   {sum(1 for f in self.流量记录 if f['协议'] == 'HTTP')}")
        print(f"  HTTPS流量:  {sum(1 for f in self.流量记录 if f['协议'] == 'HTTPS')}")
        print(f"  安全风险:   {len(self.安全风险)} 个")
        print(f"    - 高风险: {len(高风险)}")
        print(f"    - 中风险: {len(中风险)}")
        print(f"    - 低风险: {len(低风险)}")

        if 高风险:
            print("\n  高风险问题:")
            for r in 高风险:
                print(f"    [!!] {r['问题']}: {r['URL']}")
                print(f"         {r['描述']}")

        print("\n  修复建议:")
        print("    1. 所有API通信强制使用HTTPS")
        print("    2. 实现严格的证书校验，拒绝无效证书")
        print("    3. 实施证书绑定(Certificate Pinning)")
        print("    4. 敏感数据不要放在URL参数中")
        print("    5. 实现网络安全配置(Network Security Config)")

        return {
            "流量总数": len(self.流量记录),
            "HTTP流量": sum(1 for f in self.流量记录 if f["协议"] == "HTTP"),
            "HTTPS流量": sum(1 for f in self.流量记录 if f["协议"] == "HTTPS"),
            "高风险数": len(高风险)
        }


# ============================================================================
#  第四部分：iOS应用安全检查
# ============================================================================

class iOS应用安全检查器:
    """
    iOS应用安全检查工具

    功能说明：
        - IPA文件解包分析（IPA本质是ZIP文件）
        - Info.plist安全配置检查
        - 检查ATS(App Transport Security)配置
        - 检测越狱检测实现
        - 检查数据存储安全
        - 验证二进制保护机制

    技术原理：
        iOS应用安装包(IPA)是一个ZIP文件，包含：
        - Payload/AppName.app/  应用主目录
        - Info.plist            应用配置文件
        - 可执行二进制文件       Mach-O格式
        - 资源文件

        安全检查重点：
        1. ATS配置 - 是否允许HTTP明文传输
        2. 二进制保护 - PIE/Stack Canary/ARC
        3. 越狱检测 - 是否检测越狱环境
        4. 数据存储 - Keychain/NSUserDefaults使用
        5. 权限声明 - 申请的隐私权限是否合理
    """

    def __init__(self, ipa路径: str = "模拟IPA"):
        self.ipa路径 = ipa路径
        self.检查结果 = []
        print(f"[初始化] iOS应用安全检查器已就绪，目标: {ipa路径}")

    def 解包分析IPA(self):
        """
        解包IPA文件并分析结构

        技术说明：
            IPA文件本质是ZIP压缩包，解压后结构为：
            Payload/
              AppName.app/
                Info.plist          应用配置
                AppName             可执行文件
                *.storyboardc       编译后的UI
                Assets.car          编译后的资源
                Frameworks/         框架
                各种 .plist/.json   配置文件

            可执行文件是Mach-O格式，可使用otool等工具分析。
        """
        print("\n" + "=" * 70)
        print("IPA文件解包分析")
        print("=" * 70)

        # 模拟IPA解包后的结构
        ipa结构 = {
            "Payload/VulnerableApp.app/Info.plist": "应用配置文件",
            "Payload/VulnerableApp.app/VulnerableApp": "Mach-O可执行文件",
            "Payload/VulnerableApp.app/Assets.car": "编译后的资源",
            "Payload/VulnerableApp.app/Frameworks/": "动态框架",
            "Payload/VulnerableApp.app/embedded.mobileprovision": "描述文件",
            "Payload/VulnerableApp.app/_CodeSignature/": "代码签名",
            "Payload/VulnerableApp.app/Settings.bundle/": "设置包",
        }

        print(f"解包文件: {self.ipa路径}\n")
        for 文件, 说明 in ipa结构.items():
            print(f"  {文件:55s} {说明}")

        print(f"\n共发现 {len(ipa结构)} 个文件/目录")
        return ipa结构

    def 检查InfoPlist(self, plist数据: dict = 模拟InfoPlist):
        """
        检查Info.plist安全配置

        技术说明：
            Info.plist是iOS应用的核心配置文件，包含：
            - 应用标识符和版本信息
            - 权限描述（使用隐私API需要声明用途）
            - 网络安全配置（ATS）
            - URL Scheme
            - 后台模式

            安全检查重点：
            1. ATS配置 - NSAllowsArbitraryLoads=true 允许HTTP
            2. 权限声明 - 检查是否申请了过多的隐私权限
            3. URL Scheme - 检查自定义URL Scheme
            4. 后台模式 - 检查是否启用了不必要的后台模式
        """
        print("\n" + "=" * 70)
        print("Info.plist 安全配置检查")
        print("=" * 70)

        # 应用基本信息
        应用名 = plist数据.get("CFBundleName", "未知")
        包标识 = plist数据.get("CFBundleIdentifier", "未知")
        版本 = plist数据.get("CFBundleShortVersionString", "未知")
        构建号 = plist数据.get("CFBundleVersion", "未知")

        print(f"\n  应用名称:   {应用名}")
        print(f"  包标识符:   {包标识}")
        print(f"  版本:       {版本} (Build {构建号})")

        # ATS配置检查
        self._检查ATS配置(plist数据)

        # 权限声明检查
        self._检查权限声明(plist数据)

        # URL Scheme检查
        self._检查URLScheme(plist数据)

        # 后台模式检查
        self._检查后台模式(plist数据)

    def _检查ATS配置(self, plist数据: dict):
        """检查App Transport Security配置"""
        print("\n  [ATS配置检查]")
        print("  " + "-" * 50)

        ats = plist数据.get("NSAppTransportSecurity", {})

        if ats.get("NSAllowsArbitraryLoads", False):
            print("    [!!] NSAllowsArbitraryLoads = true")
            print("         高风险: 允许所有HTTP明文传输")
            self.检查结果.append({
                "风险": "高",
                "问题": "ATS允许HTTP明文传输",
                "建议": "设置NSAllowsArbitraryLoads=false，强制HTTPS"
            })
        else:
            print("    [OK] NSAllowsArbitraryLoads = false (仅允许HTTPS)")

        if ats.get("NSAllowsLocalNetworking", False):
            print("    [?]  NSAllowsLocalNetworking = true")
            print("         中风险: 允许本地网络HTTP通信")
            self.检查结果.append({
                "风险": "中",
                "问题": "ATS允许本地HTTP",
                "建议": "评估是否必须使用本地HTTP"
            })

    def _检查权限声明(self, plist数据: dict):
        """检查隐私权限声明"""
        print("\n  [权限声明检查]")
        print("  " + "-" * 50)

        权限映射 = {
            "NSCameraUsageDescription": "相机",
            "NSLocationWhenInUseUsageDescription": "位置(使用时)",
            "NSLocationAlwaysUsageDescription": "位置(始终)",
            "NSContactsUsageDescription": "通讯录",
            "NSPhotoLibraryUsageDescription": "相册",
            "NSMicrophoneUsageDescription": "麦克风",
            "NSFaceIDUsageDescription": "Face ID",
            "NSHealthShareUsageDescription": "健康数据"
        }

        申请的权限 = []
        for key, 描述 in 权限映射.items():
            if key in plist数据:
                申请的权限.append((描述, plist数据[key]))
                print(f"    [权限] {描述:10s} 用途: {plist数据[key]}")

        if len(申请的权限) > 4:
            print(f"\n    [!] 申请了 {len(申请的权限)} 个隐私权限，请评估必要性")
            self.检查结果.append({
                "风险": "中",
                "问题": f"申请了{len(申请的权限)}个隐私权限",
                "建议": "审查是否所有权限都是必要的，移除不需要的权限"
            })

    def _检查URLScheme(self, plist数据: dict):
        """检查自定义URL Scheme"""
        print("\n  [URL Scheme检查]")
        print("  " + "-" * 50)

        urlTypes = plist数据.get("CFBundleURLTypes", [])
        for ut in urlTypes:
            名称 = ut.get("CFBundleURLName", "")
            schemes = ut.get("CFBundleURLSchemes", [])
            for s in schemes:
                print(f"    [Scheme] {s}")
                if s in ("http", "https"):
                    print(f"      [!!] 注册了通用Scheme: {s}，可能劫持浏览器")
                    self.检查结果.append({
                        "风险": "高",
                        "问题": f"注册通用URL Scheme: {s}",
                        "建议": "不要注册http/https等通用Scheme"
                    })

    def _检查后台模式(self, plist数据: dict):
        """检查后台运行模式"""
        print("\n  [后台模式检查]")
        print("  " + "-" * 50)

        bgModes = plist数据.get("UIBackgroundModes", [])
        危险模式 = {"audio", "voip", "location"}

        for mode in bgModes:
            标识 = "[!!]" if mode in 危险模式 else "[OK]"
            print(f"    {标识} {mode}")

        if "location" in bgModes:
            print("      [!] 后台定位可能泄露用户位置信息")
            self.检查结果.append({
                "风险": "中",
                "问题": "启用了后台定位",
                "建议": "评估后台定位的必要性"
            })

    def 检查二进制保护(self):
        """
        检查Mach-O二进制文件的保护机制

        技术说明：
            iOS二进制文件的安全保护机制包括：
            1. PIE (Position Independent Executable) - 地址空间随机化
            2. Stack Canary - 栈溢出保护
            3. ARC (Automatic Reference Counting) - 内存安全
            4. Restrict - 限制调试器附加

            使用otool工具检查：
            otool -hv Binary    检查PIE标志
            otool -Iv Binary    检查Stack Canary
        """
        print("\n" + "=" * 70)
        print("二进制保护机制检查")
        print("=" * 70)

        检查项 = [
            ("PIE (位置无关可执行文件)", True, "启用地址空间随机化"),
            ("Stack Canary (栈溢出保护)", True, "防止栈溢出攻击"),
            ("ARC (自动引用计数)", True, "内存管理安全"),
            ("Restrict (限制调试)", False, "未限制调试器附加，可被调试"),
            ("Code Signing (代码签名)", True, "已签名验证"),
        ]

        for 名称, 状态, 描述 in 检查项:
            标识 = "[OK] " if 状态 else "[!!] "
            print(f"  {标识}{名称}: {'已启用' if 状态 else '未启用'}")
            print(f"        {描述}")
            if not 状态:
                self.检查结果.append({
                    "风险": "中",
                    "问题": f"{名称}未启用",
                    "建议": f"启用{名称}以增强二进制安全性"
                })

    def 生成iOS报告(self):
        """生成iOS安全检查报告"""
        print("\n" + "=" * 70)
        print("iOS应用安全检查报告")
        print("=" * 70)

        高 = [r for r in self.检查结果 if r["风险"] == "高"]
        中 = [r for r in self.检查结果 if r["风险"] == "中"]
        低 = [r for r in self.检查结果 if r["风险"] == "低"]

        print(f"\n  检查项目: {len(self.检查结果)} 个问题")
        print(f"    - 高风险: {len(高)}")
        print(f"    - 中风险: {len(中)}")
        print(f"    - 低风险: {len(低)}")

        if self.检查结果:
            print("\n  问题详情:")
            for i, r in enumerate(self.检查结果, 1):
                print(f"    {i}. [{r['风险']}] {r['问题']}")
                print(f"       建议: {r['建议']}")

        return {"高风险": len(高), "中风险": len(中), "低风险": len(低)}


# ============================================================================
#  第五部分：移动应用加固检测
# ============================================================================

class 应用加固检测器:
    """
    移动应用加固检测工具

    功能说明：
        - 检测应用是否加壳（加固保护）
        - 识别壳类型（梆梆/爱加密/360加固/腾讯乐固等）
        - 检查代码混淆程度
        - 检测反调试机制
        - 检查完整性校验
        - 分析SO层保护

    技术原理：
        应用加固通过以下方式保护应用：
        1. 代码加壳 - 将DEX文件加密，运行时动态解密
        2. 代码混淆 - 增加代码阅读难度（ProGuard/DexGuard）
        3. 反调试 - 检测调试器附加（ptrace/调试标志）
        4. 完整性校验 - 校验APK签名/文件完整性
        5. SO层保护 - 在Native层实现关键逻辑和保护

        检测方法：
        - 分析DEX文件结构是否被修改
        - 检查application类是否被替换为壳的入口
        - 检查是否存在加固SDK特征文件
        - 反编译后检查代码混淆程度
    """

    # 常见加固厂商特征
    加固特征 = {
        "梆梆安全": ["com.bangcle.", "com.secapk.", "libsecexe.so"],
        "爱加密": ["com.ijiami.", "libijiami.", "ijiami.dat"],
        "360加固": ["com.stub.", "libjiagu.", "classes.dat"],
        "腾讯乐固": ["com.tencent.StubShell.", "libshella.", "libshellx."],
        "娜迦(NAGA)": ["com.nagapk.", "libnaga."],
        "阿里聚安全": ["com.ali.", "libmobisec."],
        "百度加固": ["com.baidu.mobads.", "libbaiduprotect."],
        "通付盾": ["com.tongfudun.", "libtup."],
    }

    # 混淆检测关键词
    混淆特征 = {
        "ProGuard": ["a.", "b.", "c.", "a.b.c", "a.a.a"],
        "DexGuard": ["O000000o", "O0000OOo", "O0O0O0O0"],
        "Allatori": ["a1", "b2", "c3"],
    }

    def __init__(self):
        self.检测结果 = {}
        print("[初始化] 应用加固检测器已就绪")

    def 检测加壳(self):
        """检测应用是否加壳"""
        print("\n" + "=" * 70)
        print("应用加壳检测")
        print("=" * 70)

        # 模拟检测APK文件特征
        模拟文件特征 = {
            "classes.dex": "标准DEX文件",
            "classes2.dex": "标准DEX文件",
            "lib/armeabi-v7a/libnative.so": "标准SO库",
            # 无加固SDK特征文件
        }

        检测到壳 = False
        壳类型 = "无"

        print("\n  扫描APK文件特征...")
        for 文件, 说明 in 模拟文件特征.items():
            print(f"    {文件:45s} {说明}")

        # 检查加固厂商特征
        print("\n  匹配加固厂商特征...")
        for 厂商, 特征列表 in self.加固特征.items():
            匹配 = any(特征 in str(模拟文件特征) for 特征 in 特征列表)
            if 匹配:
                print(f"    [匹配] {厂商}")
                检测到壳 = True
                壳类型 = 厂商
            else:
                print(f"    [未匹配] {厂商}")

        if 检测到壳:
            print(f"\n  [结果] 检测到加固: {壳类型}")
            self.检测结果["加壳状态"] = True
            self.检测结果["壳类型"] = 壳类型
        else:
            print(f"\n  [结果] 未检测到加固保护")
            self.检测结果["加壳状态"] = False
            self.检测结果["壳类型"] = "无"

    def 检测代码混淆(self):
        """
        检测代码混淆程度

        技术说明：
            代码混淆通过重命名类/方法/字段名称，使反编译代码难以理解。
            常见混淆工具：
            - ProGuard: 基本混淆，将类名替换为短名称(a/b/c)
            - DexGuard: 高级混淆，支持字符串加密、反调试
            - Allatori: 支持流式混淆

            检测方法：分析反编译代码中的类名/方法名模式
        """
        print("\n" + "=" * 70)
        print("代码混淆检测")
        print("=" * 70)

        # 模拟反编译代码片段（未混淆）
        代码片段 = """
        public class AppConfig {
            private static final String API_KEY = "sk-xxx";
            public static String encrypt(String data) { ... }
            public static String decrypt(String data) { ... }
        }
        public class UserManager {
            public User login(String username, String password) { ... }
            public void logout() { ... }
        }
        """

        # 混淆检测
        混淆标志 = {
            "类名替换": False,     # a.class, b.class 等
            "方法名替换": False,    # a(), b() 等
            "字段名替换": False,    # a, b, c 等
            "字符串加密": False,    # DexGuard特征
        }

        # 检查混淆特征
        has混淆 = False
        for 工具, 特征列表 in self.混淆特征.items():
            for 特征 in 特征列表:
                if 特征 in 代码片段:
                    print(f"  [匹配] {工具}混淆特征: {特征}")
                    has混淆 = True
                    混淆标志["类名替换"] = True

        if not has混淆:
            print("  [结果] 代码未混淆")
            print("         类名/方法名保留原始可读名称")
            print("         [!] 建议启用ProGuard/DexGuard混淆")
        else:
            print("  [结果] 检测到代码混淆")

        self.检测结果["代码混淆"] = has混淆

        # 输出混淆建议
        print("\n  混淆建议:")
        print("    1. 启用ProGuard进行基本混淆")
        print("    2. 关键逻辑使用DexGuard高级混淆")
        print("    3. 敏感字符串加密存储")
        print("    4. 关键方法使用Native实现")

    def 检测反调试(self):
        """
        检测反调试机制

        技术说明：
            反调试通过以下方式阻止调试器附加：
            1. 检测Debug.isDebuggerConnected()
            2. 检测ptrace附加
            3. 检测调试器端口
            4. 检测模拟器环境
            5. 检测Root/越狱环境

            常见的反调试检测点：
            - android.os.Debug.isDebuggerConnected()
            - /proc/self/status 中的 TracerPid
            - /proc/self/wchan 检查
            - SigningInfo 检测Hook框架
        """
        print("\n" + "=" * 70)
        print("反调试检测")
        print("=" * 70)

        检查项 = [
            ("Debug.isDebuggerConnected()检测", False, "Java层调试器检测"),
            ("ptrace附加检测", False, "Native层调试器检测"),
            ("/proc/self/status检测", False, "通过/proc检测调试器"),
            ("模拟器检测", False, "检测是否运行在模拟器"),
            ("Root检测", False, "检测设备是否Root"),
            ("Hook框架检测", False, "检测Xposed/Frida框架"),
            ("签名校验", False, "校验应用签名是否被修改"),
            ("文件完整性校验", False, "校验APK文件完整性"),
        ]

        检测到 = 0
        for 名称, 状态, 描述 in 检查项:
            标识 = "[OK] " if 状态 else "[!!] "
            print(f"  {标识}{名称}: {'已实现' if 状态 else '未实现'}")
            print(f"        {描述}")
            if 状态:
                检测到 += 1

        self.检测结果["反调试检测"] = 检测到 > 0
        self.检测结果["完整性校验"] = False

        print(f"\n  [结果] 已实现 {检测到}/{len(检查项)} 项保护")
        if 检测到 < 3:
            print("  [!] 反调试保护不足，建议增加以下保护:")
            print("      1. 多层调试器检测(Java层+Native层)")
            print("      2. 实现签名校验")
            print("      3. 检测Xposed/Frida等Hook框架")
            print("      4. 实现文件完整性校验")

    def 生成加固报告(self):
        """生成加固检测报告"""
        print("\n" + "=" * 70)
        print("应用加固检测报告")
        print("=" * 70)

        print(f"\n  加壳状态:     {'已加壳' if self.检测结果.get('加壳状态') else '未加壳'}")
        print(f"  壳类型:       {self.检测结果.get('壳类型', '无')}")
        print(f"  代码混淆:     {'已混淆' if self.检测结果.get('代码混淆') else '未混淆'}")
        print(f"  反调试检测:   {'已实现' if self.检测结果.get('反调试检测') else '未实现'}")
        print(f"  完整性校验:   {'已实现' if self.检测结果.get('完整性校验') else '未实现'}")

        加固项数 = sum(1 for v in self.检测结果.values() if v is True or (isinstance(v, str) and v != "无"))
        print(f"\n  加固覆盖率: {加固项数}/5 项")

        if 加固项数 < 2:
            print("\n  [!] 应用几乎无任何保护，建议:")
            print("      1. 使用商业加固方案(梆梆/360/腾讯乐固)")
            print("      2. 启用代码混淆")
            print("      3. 实现反调试保护")
            print("      4. 添加完整性校验")
            print("      5. 关键逻辑放入SO层")

        return self.检测结果


# ============================================================================
#  第六部分：数据存储安全审计
# ============================================================================

class 数据存储安全审计器:
    """
    移动应用数据存储安全审计工具

    功能说明：
        - 检查SharedPreferences中的敏感数据
        - 审计SQLite数据库存储安全
        - 检查外部存储(SD卡)文件安全
        - 检查Keychain/Keystore使用
        - 检查日志中的敏感信息
        - 检查备份文件安全

    技术原理：
        Android/iOS数据存储位置：
        1. SharedPreferences - XML明文存储（默认无加密）
        2. SQLite数据库 - 文件级存储，root后可读取
        3. 外部存储 - 任意应用可读取
        4. 内部存储 - 应用私有目录
        5. Keychain(iOS)/Keystore(Android) - 安全存储

        安全要求：
        - 敏感数据不应明文存储在SharedPreferences
        - 数据库中的密码/Token应加密
        - 外部存储不应存放敏感数据
        - 应使用Keystore/Keychain存储密钥
    """

    # 敏感数据检测关键词
    敏感关键词 = [
        "password", "pwd", "pass", "passwd",
        "token", "auth", "session", "cookie",
        "key", "secret", "api_key",
        "card", "cvv", "account",
        "idcard", "id_card", "身份证",
        "phone", "mobile", "手机",
        "location", "gps", "位置",
        "payment", "支付",
        "device_id", "imei",
    ]

    def __init__(self):
        self.发现列表 = []
        print("[初始化] 数据存储安全审计器已就绪")

    def 审计SharedPreferences(self, 数据: dict = 模拟SharedPreferences):
        """
        审计SharedPreferences存储

        技术说明：
            SharedPreferences是Android轻量级数据存储方案，
            数据以XML明文格式存储在：
            /data/data/<package_name>/shared_prefs/*.xml

            默认不加密，root设备或adb backup可直接读取。
            Android Keystore可提供加密SharedPreferences。
        """
        print("\n" + "=" * 70)
        print("SharedPreferences 存储审计")
        print("=" * 70)
        print(f"  存储文件: shared_prefs/user_data.xml")
        print(f"  键值对数: {len(数据)}\n")

        for 键, 值 in 数据.items():
            风险 = self._评估数据风险(键, 值)
            加密 = self._是否加密(值)

            标识 = {
                "高": "[!!]",
                "中": "[? ]",
                "低": "[OK]"
            }

            print(f"  {标识[风险]} {键}")
            print(f"      值: {self._脱敏显示(键, 值)}")
            print(f"      加密: {'是' if 加密 else '否'}")
            print(f"      风险: {风险}")

            if 风险 in ("高", "中"):
                self.发现列表.append({
                    "存储位置": "SharedPreferences",
                    "键名": 键,
                    "风险": 风险,
                    "问题": "敏感数据明文存储" if not 加密 else "加密存储但密钥管理需检查",
                })
            print()

    def _评估数据风险(self, 键: str, 值: str) -> str:
        """评估存储数据的风险等级"""
        键小写 = 键.lower()
        值str = str(值)

        # 高敏感数据
        高敏感 = ["password", "pwd", "token", "secret", "api_key",
                  "card", "cvv", "payment", "idcard", "session"]
        # 中敏感数据
        中敏感 = ["phone", "mobile", "location", "gps", "device_id",
                  "imei", "auth", "server"]

        for kw in 高敏感:
            if kw in 键小写:
                return "高"

        for kw in 中敏感:
            if kw in 键小写:
                return "中"

        return "低"

    def _是否加密(self, 值: str) -> bool:
        """检查值是否已加密"""
        值str = str(值)
        # Base64编码不算加密
        # 检查是否是明文（包含可读字符）
        if 值str.startswith(("Bearer ", "http://", "sk-", "ghp_")):
            return False
        # 简单检查：如果值是纯数字或常见密码格式，视为未加密
        if re.match(r'^[a-zA-Z0-9@!#$%^&*]{6,20}$', 值str):
            return False
        return False  # 模拟数据均为未加密

    def _脱敏显示(self, 键: str, 值: str) -> str:
        """脱敏显示敏感值"""
        值str = str(值)
        if len(值str) <= 4:
            return 值str[:1] + "***"
        return 值str[:3] + "***" + 值str[-3:]

    def 审计SQLite数据库(self, 表信息: List[Dict] = 模拟SQLite数据):
        """
        审计SQLite数据库存储

        技术说明：
            SQLite数据库文件存储在：
            /data/data/<package_name>/databases/*.db

            安全风险：
            1. 敏感字段明文存储（password/credit_card等）
            2. 数据库文件未加密
            3. SQL注入风险（拼接查询语句）
            4. 数据库备份文件泄露

            推荐使用SQLCipher加密数据库。
        """
        print("=" * 70)
        print("SQLite 数据库存储审计")
        print("=" * 70)
        print(f"  数据库文件: databases/app_data.db\n")

        敏感字段 = ["password", "pwd", "card_no", "cvv", "idcard",
                   "phone", "email", "realname", "content"]

        for 表 in 表信息:
            表名 = 表["表名"]
            列列表 = 表["列"]
            print(f"  表: {表名}")
            print(f"  列: {', '.join(列列表)}")

            风险列 = []
            for 列 in 列列表:
                if any(kw in 列.lower() for kw in 敏感字段):
                    风险列.append(列)

            if 风险列:
                print(f"  [!!] 敏感字段: {', '.join(风险列)}")
                print(f"       这些字段明文存储，存在泄露风险")
                for col in 风险列:
                    self.发现列表.append({
                        "存储位置": f"SQLite:{表名}.{col}",
                        "键名": col,
                        "风险": "高",
                        "问题": "数据库敏感字段明文存储"
                    })
            else:
                print(f"  [OK] 未发现敏感字段")

            print()

    def 审计外部存储(self):
        """
        审计外部存储文件

        技术说明：
            外部存储(SD卡/共享存储)中的文件：
            - 任何有READ_EXTERNAL_STORAGE权限的应用可读取
            - 文件可被文件管理器查看
            - 卸载应用后文件仍保留

            安全要求：
            - 不应在外部存储存放敏感数据
            - 如必须使用，应加密后存储
        """
        print("=" * 70)
        print("外部存储文件审计")
        print("=" * 70)

        # 模拟外部存储文件列表
        外部文件 = [
            {"路径": "/sdcard/AppData/user_config.json", "大小": "2KB",
             "内容": '{"username":"admin","password":"Admin@123"}'},
            {"路径": "/sdcard/AppData/cache/tmp.dat", "大小": "15KB",
             "内容": "二进制缓存数据"},
            {"路径": "/sdcard/AppData/logs/app.log", "大小": "150KB",
             "内容": "应用日志(含敏感操作记录)"},
            {"路径": "/sdcard/AppData/backup/user_backup.bak", "大小": "500KB",
             "内容": "用户数据备份(含密码/token)"},
            {"路径": "/sdcard/AppData/images/avatar.png", "大小": "3MB",
             "内容": "用户头像图片"},
        ]

        print(f"  扫描路径: /sdcard/AppData/")
        print(f"  发现文件: {len(外部文件)} 个\n")

        for f in 外部文件:
            路径 = f["路径"]
            内容 = f["内容"]

            # 检查文件内容是否含敏感数据
            has敏感 = self._检查文件内容(内容)

            标识 = "[!!]" if has敏感 else "[OK]"
            print(f"  {标识} {f['路径']}")
            print(f"       大小: {f['大小']}")
            print(f"       内容预览: {内容[:60]}...")

            if has敏感:
                print(f"       [!] 外部存储包含敏感数据，任意应用可读取")
                self.发现列表.append({
                    "存储位置": 路径,
                    "风险": "高",
                    "问题": "外部存储包含敏感数据，任意应用可读取"
                })
            print()

    def _检查文件内容(self, 内容: str) -> bool:
        """检查文件内容是否包含敏感数据"""
        内容小写 = 内容.lower()
        敏感词 = ["password", "pwd", "token", "key", "secret",
                  "card", "cvv", "身份证", "密码"]
        return any(kw in 内容小写 for kw in 敏感词)

    def 生成审计报告(self):
        """生成数据存储安全审计报告"""
        print("\n" + "=" * 70)
        print("数据存储安全审计报告")
        print("=" * 70)

        高风险 = [r for r in self.发现列表 if r["风险"] == "高"]
        中风险 = [r for r in self.发现列表 if r["风险"] == "中"]

        print(f"\n  发现问题: {len(self.发现列表)} 个")
        print(f"    - 高风险: {len(高风险)}")
        print(f"    - 中风险: {len(中风险)}")

        if 高风险:
            print("\n  高风险问题:")
            for i, r in enumerate(高风险, 1):
                print(f"    {i}. [{r['存储位置']}] {r['问题']}")

        print("\n  存储安全建议:")
        print("    1. 敏感数据使用Android Keystore加密存储")
        print("    2. 数据库使用SQLCipher加密")
        print("    3. 禁止在外部存储存放敏感数据")
        print("    4. 日志中不输出敏感信息")
        print("    5. 使用EncryptedSharedPreferences替代明文SharedPreferences")
        print("    6. 定期清理缓存和备份文件")

        return {
            "总问题数": len(self.发现列表),
            "高风险数": len(高风险),
            "中风险数": len(中风险)
        }


# ============================================================================
#  主函数：演示所有案例
# ============================================================================

def main():
    """
    移动应用安全实战案例 - 演示主函数

    演示内容：
        1. APK静态分析
        2. Android组件安全检测
        3. 移动应用流量分析
        4. iOS应用安全检查
        5. 应用加固检测
        6. 数据存储安全审计
    """
    print("=" * 70)
    print("        移动应用安全实战案例 - 演示程序")
    print("        仅用于授权安全测试和教育目的")
    print("=" * 70)
    print()
    print("本程序演示移动应用安全评估的核心技术，")
    print("包括APK静态分析、组件安全检测、流量分析、")
    print("iOS安全检查、加固检测和数据存储审计。")
    print()

    # ========================================================
    # 案例一：APK静态分析
    # ========================================================
    print("\n" + "#" * 70)
    print("#  案例一：APK静态分析")
    print("#" * 70)

    分析器 = APK静态分析器("vulnerableapp_v2.3.1.apk")
    分析器.解析AndroidManifest()
    分析器.检测硬编码密钥()
    分析器.生成分析报告()

    # ========================================================
    # 案例二：Android组件安全检测
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例二：Android组件安全检测")
    print("#" * 70)

    组件检测器 = Android组件安全检测器()

    # 从分析器获取组件列表
    组件列表 = 分析器.分析结果["组件列表"]
    组件检测器.扫描组件(组件列表)
    组件检测器.模拟组件攻击()
    组件检测器.输出检测报告()

    # ========================================================
    # 案例三：移动应用流量分析
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例三：移动应用流量抓包与中间人攻击检测")
    print("#" * 70)

    流量分析器 = 流量安全分析器()
    流量分析器.分析流量()
    流量分析器.检查证书安全()
    流量分析器.生成流量报告()

    # ========================================================
    # 案例四：iOS应用安全检查
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例四：iOS应用安全检查")
    print("#" * 70)

    ios检查器 = iOS应用安全检查器("VulnerableApp_v2.3.1.ipa")
    ios检查器.解包分析IPA()
    ios检查器.检查InfoPlist()
    ios检查器.检查二进制保护()
    ios检查器.生成iOS报告()

    # ========================================================
    # 案例五：应用加固检测
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例五：移动应用加固检测")
    print("#" * 70)

    加固检测器 = 应用加固检测器()
    加固检测器.检测加壳()
    加固检测器.检测代码混淆()
    加固检测器.检测反调试()
    加固检测器.生成加固报告()

    # ========================================================
    # 案例六：数据存储安全审计
    # ========================================================
    print("\n\n" + "#" * 70)
    print("#  案例六：数据存储安全审计")
    print("#" * 70)

    审计器 = 数据存储安全审计器()
    审计器.审计SharedPreferences()
    审计器.审计SQLite数据库()
    审计器.审计外部存储()
    审计器.生成审计报告()

    # ========================================================
    # 总结
    # ========================================================
    print("\n\n" + "=" * 70)
    print("                    演示总结")
    print("=" * 70)
    print("""
    本次演示涵盖了移动应用安全评估的六个核心领域：

    1. APK静态分析
       - 解析AndroidManifest.xml提取应用信息
       - 检测硬编码密钥、Token等敏感信息
       - 检查debuggable、allowBackup等安全配置

    2. Android组件安全
       - 四大组件导出状态扫描
       - 无权限保护的导出组件风险评估
       - 组件攻击模拟测试

    3. 流量安全分析
       - HTTP/HTTPS流量检查
       - 明文传输敏感数据检测
       - SSL/TLS证书校验安全性检查

    4. iOS应用安全
       - IPA解包分析与Info.plist检查
       - ATS配置与权限声明审查
       - 二进制保护机制验证

    5. 应用加固检测
       - 加壳检测与壳类型识别
       - 代码混淆程度评估
       - 反调试与完整性校验检测

    6. 数据存储安全
       - SharedPreferences明文敏感数据检测
       - SQLite数据库敏感字段审计
       - 外部存储文件安全检查

    安全声明：
        本演示仅用于教育和授权测试目的。
        所有数据均为模拟生成，不涉及真实应用。
        未经授权对他人应用进行安全测试是违法行为。
    """)
    print("=" * 70)
    print("演示结束。")
    print("=" * 70)


if __name__ == "__main__":
    main()
