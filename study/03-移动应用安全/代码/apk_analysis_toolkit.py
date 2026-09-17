#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK分析工具箱 (APK Analysis Toolkit)
=======================================

本工具集集成了Android应用安全分析常用的各类工具：
1. AndroidManifest安全审计 - 权限、组件、备份、调试
2. APK静态分析工具 - 反编译、文件提取、资源分析
3. 组件安全检测 - Activity/Service/Receiver/Provider导出检查
4. 硬编码密钥检测 - 搜索敏感字符串、密钥、URL
5. 签名证书分析 - 签名算法、证书信息、自签名检测
6. 网络安全配置分析 - 明文流量、证书校验、HSTS
7. WebView安全检测 - JS接口、明文加载、调试模式
8. Frida Hook模板生成 - 常用Hook脚本模板

作者：移动应用安全学习工具
版本：1.0
用途：仅用于授权的安全测试和教育学习
"""

import os
import re
import sys
import hashlib
import base64
import zipfile
import struct
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime
from xml.etree import ElementTree as ET


# ============================================================
# 工具1: AndroidManifest安全审计
# ============================================================

class ManifestAuditor:
    """AndroidManifest.xml安全审计工具"""

    危险权限列表 = [
        ("INTERNET", "网络访问", "低"),
        ("READ_EXTERNAL_STORAGE", "读取外部存储", "中"),
        ("WRITE_EXTERNAL_STORAGE", "写入外部存储", "中"),
        ("READ_CONTACTS", "读取通讯录", "高"),
        ("READ_SMS", "读取短信", "高"),
        ("SEND_SMS", "发送短信", "高"),
        ("RECEIVE_SMS", "接收短信", "高"),
        ("CAMERA", "相机权限", "中"),
        ("RECORD_AUDIO", "录音权限", "高"),
        ("ACCESS_FINE_LOCATION", "精确定位", "高"),
        ("READ_PHONE_STATE", "读取手机状态", "中"),
        ("INSTALL_PACKAGES", "安装应用", "高"),
        ("SYSTEM_ALERT_WINDOW", "悬浮窗", "中"),
        ("BIND_ACCESSIBILITY_SERVICE", "无障碍服务", "高"),
    ]

    def __init__(self, manifest_xml: str = None):
        self.manifest = manifest_xml or self._get_sample_manifest()
        self.findings = []

    def _get_sample_manifest(self) -> str:
        """获取模拟Manifest"""
        lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"',
            '    package="com.example.vulnerableapp"',
            '    android:versionCode="15"',
            '    android:versionName="2.3.1">',
            '',
            '    <uses-permission android:name="android.permission.INTERNET" />',
            '    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />',
            '    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />',
            '    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />',
            '    <uses-permission android:name="android.permission.READ_CONTACTS" />',
            '    <uses-permission android:name="android.permission.READ_SMS" />',
            '    <uses-permission android:name="android.permission.SEND_SMS" />',
            '    <uses-permission android:name="android.permission.CAMERA" />',
            '    <uses-permission android:name="android.permission.RECORD_AUDIO" />',
            '',
            '    <application',
            '        android:name=".MyApplication"',
            '        android:debuggable="true"',
            '        android:allowBackup="true"',
            '        android:usesCleartextTraffic="true"',
            '        android:icon="@mipmap/ic_launcher"',
            '        android:label="@string/app_name"',
            '        android:theme="@style/AppTheme">',
            '',
            '        <activity',
            '            android:name=".MainActivity"',
            '            android:exported="true">',
            '            <intent-filter>',
            '                <action android:name="android.intent.action.MAIN" />',
            '                <category android:name="android.intent.category.LAUNCHER" />',
            '            </intent-filter>',
            '        </activity>',
            '',
            '        <activity',
            '            android:name=".WebViewActivity"',
            '            android:exported="true" />',
            '',
            '        <service',
            '            android:name=".UploadService"',
            '            android:exported="true" />',
            '',
            '        <receiver',
            '            android:name=".SmsReceiver"',
            '            android:exported="true">',
            '            <intent-filter>',
            '                <action android:name="android.provider.Telephony.SMS_RECEIVED" />',
            '            </intent-filter>',
            '        </receiver>',
            '',
            '        <provider',
            '            android:name=".DataProvider"',
            '            android:authorities="com.example.provider"',
            '            android:exported="true" />',
            '',
            '    </application>',
            '</manifest>',
        ]
        return '\n'.join(lines)

    def audit_permissions(self) -> List[Dict]:
        """审计权限"""
        results = []
        for perm_name, desc, risk in self.危险权限列表:
            if "android.permission." + perm_name in self.manifest:
                results.append({
                    "type": "权限",
                    "name": perm_name,
                    "risk": risk,
                    "desc": desc,
                })
        return results

    def audit_application(self) -> List[Dict]:
        """审计Application配置"""
        results = []
        if 'android:debuggable="true"' in self.manifest:
            results.append({
                "type": "应用配置",
                "name": "debuggable=true",
                "risk": "高",
                "desc": "应用可调试，攻击者可注入调试代码",
            })
        if 'android:allowBackup="true"' in self.manifest:
            results.append({
                "type": "应用配置",
                "name": "allowBackup=true",
                "risk": "中",
                "desc": "允许备份，数据可通过adb backup泄露",
            })
        if 'android:usesCleartextTraffic="true"' in self.manifest:
            results.append({
                "type": "应用配置",
                "name": "usesCleartextTraffic=true",
                "risk": "中",
                "desc": "允许明文HTTP流量，易被中间人攻击",
            })
        return results

    def audit_components(self) -> List[Dict]:
        """审计四大组件"""
        results = []

        exported_activities = re.findall(
            r'<activity[^>]*android:name="([^"]+)"[^>]*android:exported="true"',
            self.manifest
        )
        for act in exported_activities:
            results.append({
                "type": "组件",
                "name": "Activity: " + act,
                "risk": "中",
                "desc": "Activity已导出，可能被外部调用",
            })

        exported_services = re.findall(
            r'<service[^>]*android:name="([^"]+)"[^>]*android:exported="true"',
            self.manifest
        )
        for svc in exported_services:
            results.append({
                "type": "组件",
                "name": "Service: " + svc,
                "risk": "高",
                "desc": "Service已导出，可能被外部调用",
            })

        exported_receivers = re.findall(
            r'<receiver[^>]*android:name="([^"]+)"[^>]*android:exported="true"',
            self.manifest
        )
        for rcv in exported_receivers:
            results.append({
                "type": "组件",
                "name": "Receiver: " + rcv,
                "risk": "中",
                "desc": "BroadcastReceiver已导出",
            })

        exported_providers = re.findall(
            r'<provider[^>]*android:name="([^"]+)"[^>]*android:exported="true"',
            self.manifest
        )
        for prv in exported_providers:
            results.append({
                "type": "组件",
                "name": "Provider: " + prv,
                "risk": "高",
                "desc": "ContentProvider已导出，可能存在SQL注入/路径遍历",
            })

        return results

    def run_audit(self) -> List[Dict]:
        """执行完整审计"""
        print("\n" + "=" * 60)
        print("AndroidManifest 安全审计")
        print("=" * 60)

        all_findings = []
        all_findings.extend(self.audit_permissions())
        all_findings.extend(self.audit_application())
        all_findings.extend(self.audit_components())

        risk_count = defaultdict(int)
        for f in all_findings:
            risk_count[f["risk"]] += 1

        print("\n发现问题: %d 个" % len(all_findings))
        print("风险分布: 高危=%d 中危=%d 低危=%d" % (risk_count["高"], risk_count["中"], risk_count["低"]))
        print()

        current_type = ""
        for f in all_findings:
            if f["type"] != current_type:
                current_type = f["type"]
                print("\n【%s】" % current_type)
            risk_icon = "[!]" if f["risk"] == "高" else "[*]" if f["risk"] == "中" else "[-]"
            print("  %s [%s] %s" % (risk_icon, f["risk"], f["name"]))
            print("      %s" % f["desc"])

        print()
        return all_findings


# ============================================================
# 工具2: 硬编码密钥检测
# ============================================================

class HardcodedSecretDetector:
    """硬编码密钥/敏感信息检测工具"""

    敏感模式 = [
        ("API密钥", r'(api[_-]?key|apikey|API_KEY)\s*[:=]\s*["\'][A-Za-z0-9]{16,}["\']', "中"),
        ("密码", r'(password|passwd|pwd)\s*[:=]\s*["\'][^"\']{6,}["\']', "高"),
        ("AWS密钥", r'AKIA[0-9A-Z]{16}', "高"),
        ("私钥", r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', "严重"),
        ("服务器地址", r'https?://[a-zA-Z0-9.-]+\.[a-z]{2,}(:[0-9]+)?/api/', "低"),
        ("数据库连接", r'(jdbc|mysql|postgresql)://[a-zA-Z0-9:]*@?', "中"),
        ("Firebase", r'firebaseio\.com|firebaseapp\.com', "中"),
        ("Google API", r'AIza[0-9A-Za-z-_]{35}', "中"),
        ("Stripe密钥", r'sk_(live|test)_[a-zA-Z0-9]{24,}', "高"),
        ("GitHub Token", r'ghp_[a-zA-Z0-9]{36}', "高"),
        ("Base64长串", r'[A-Za-z0-9+/]{40,}={0,2}', "低"),
        ("Hex长串", r'[a-fA-F0-9]{40,}', "低"),
    ]

    def __init__(self, source_code: str = None):
        self.source = source_code or self._get_sample_code()
        self.findings = []

    def _get_sample_code(self) -> str:
        """获取模拟代码"""
        lines = [
            "public class ApiConfig {",
            '    public static final String API_KEY = "sk_live_abc123def456ghi789jkl012mno345";',
            '    public static final String DB_PASSWORD = "SuperSecret123!";',
            '    public static final String AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE";',
            '    public static final String AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";',
            '    public static final String SERVER_URL = "https://api.example.com/v1/";',
            '    public static final String FIREBASE_URL = "https://myapp-12345.firebaseio.com/";',
            '    public static final String GOOGLE_API_KEY = "AIzaSyDaGmWKa4JsXZexampleKey";',
            '    public static final String ENCRYPTION_KEY = "MIIEpAIBAAKCAQEA0Z1examplePrivateKey";',
            '',
            '    private String secretToken = "ghp_abcdefghijklmnopqrstuvwxyz0123456789";',
            '    private String adminPass = "admin@2024!";',
            "}",
        ]
        return '\n'.join(lines)

    def scan(self) -> List[Dict]:
        """执行扫描"""
        print("\n" + "=" * 60)
        print("硬编码密钥检测")
        print("=" * 60)

        results = []
        for name, pattern, risk in self.敏感模式:
            matches = re.findall(pattern, self.source, re.IGNORECASE)
            if matches:
                for match in matches[:3]:
                    match_str = str(match) if isinstance(match, str) else str(match[0] if isinstance(match, tuple) else match)
                    results.append({
                        "type": name,
                        "match": match_str[:50],
                        "risk": risk,
                    })

        risk_count = defaultdict(int)
        for f in results:
            risk_count[f["risk"]] += 1

        print("\n发现敏感信息: %d 处" % len(results))
        print("风险分布: 严重=%d 高危=%d 中危=%d 低危=%d" % (
            risk_count["严重"], risk_count["高"], risk_count["中"], risk_count["低"]))
        print()

        for i, f in enumerate(results, 1):
            risk_icon = "[!!]" if f["risk"] == "严重" else "[!]" if f["risk"] == "高" else "[*]" if f["risk"] == "中" else "[-]"
            print("  %s [%s] %s" % (risk_icon, f["risk"], f["type"]))
            print("       匹配: %s" % f["match"])

        print()
        return results


# ============================================================
# 工具3: WebView安全检测
# ============================================================

class WebViewSecurityChecker:
    """WebView安全检测工具"""

    风险项 = [
        ("setJavaScriptEnabled(true)", "启用JS", "中"),
        ("addJavascriptInterface", "JS接口注入", "高"),
        ("setAllowFileAccess(true)", "允许文件访问", "中"),
        ("setAllowContentAccess(true)", "允许Content访问", "低"),
        ("setAllowUniversalAccessFromFileURLs", "通用文件访问", "高"),
        ("setAllowFileAccessFromFileURLs", "文件域访问", "中"),
        ("setMixedContentMode", "混合内容模式", "中"),
        ("setWebContentsDebuggingEnabled(true)", "WebView调试", "高"),
        ("loadUrl(\"javascript:", "加载JS代码", "中"),
        ("evaluateJavascript", "执行JS", "中"),
        ("onReceivedSslError", "SSL错误处理", "高"),
        ("handler.proceed()", "忽略SSL错误", "高"),
    ]

    def __init__(self, source_code: str = None):
        self.source = source_code or self._get_sample_code()
        self.findings = []

    def _get_sample_code(self) -> str:
        """获取模拟WebView代码"""
        lines = [
            "public class WebViewActivity extends AppCompatActivity {",
            "    private WebView webView;",
            "",
            "    @Override",
            "    protected void onCreate(Bundle savedInstanceState) {",
            "        super.onCreate(savedInstanceState);",
            "        webView = new WebView(this);",
            "        webView.getSettings().setJavaScriptEnabled(true);",
            "        webView.getSettings().setAllowFileAccess(true);",
            '        webView.addJavascriptInterface(new JsInterface(), "Android");',
            "        webView.setWebContentsDebuggingEnabled(true);",
            "        webView.setWebViewClient(new WebViewClient() {",
            "            @Override",
            "            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {",
            "                handler.proceed();",
            "            }",
            "        });",
            "        String url = getIntent().getStringExtra(\"url\");",
            "        webView.loadUrl(url);",
            "    }",
            "",
            "    class JsInterface {",
            "        @JavascriptInterface",
            "        public String getPassword() {",
            '            return "secret_password_123";',
            "        }",
            "    }",
            "}",
        ]
        return '\n'.join(lines)

    def check(self) -> List[Dict]:
        """执行检测"""
        print("\n" + "=" * 60)
        print("WebView 安全检测")
        print("=" * 60)

        results = []
        for pattern, name, risk in self.风险项:
            if pattern in self.source:
                results.append({
                    "name": name,
                    "risk": risk,
                    "pattern": pattern,
                })

        risk_count = defaultdict(int)
        for f in results:
            risk_count[f["risk"]] += 1

        print("\n发现问题: %d 个" % len(results))
        print("风险分布: 高危=%d 中危=%d 低危=%d" % (risk_count["高"], risk_count["中"], risk_count["低"]))
        print()

        for f in results:
            risk_icon = "[!]" if f["risk"] == "高" else "[*]" if f["risk"] == "中" else "[-]"
            print("  %s [%s] %s" % (risk_icon, f["risk"], f["name"]))
            print("       代码: %s" % f["pattern"])

        print()
        return results


# ============================================================
# 工具4: Frida Hook模板生成器
# ============================================================

class FridaHookGenerator:
    """Frida Hook脚本模板生成器"""

    @staticmethod
    def generate_method_hook(class_name: str, method_name: str,
                              param_types: List[str] = None) -> str:
        """生成方法Hook模板"""
        params = param_types or ["int", "java.lang.String"]
        args = ["arg%d" % i for i in range(len(params))]
        args_str = ", ".join(args)
        log_lines = ""
        for i in range(len(params)):
            log_lines += '        console.log("  arg%d: " + arg%d);\n' % (i, i)

        hook_code = 'Java.perform(function() {\n'
        hook_code += '    var targetClass = Java.use("%s");\n' % class_name
        hook_code += '    targetClass.%s.implementation = function(%s) {\n' % (method_name, args_str)
        hook_code += '        console.log("[*] Hooked: %s.%s");\n' % (class_name, method_name)
        hook_code += log_lines
        hook_code += '        var result = this.%s(%s);\n' % (method_name, args_str)
        hook_code += '        console.log("  return: " + result);\n'
        hook_code += '        return result;\n'
        hook_code += '    };\n'
        hook_code += '});'
        return hook_code

    @staticmethod
    def generate_constructor_hook(class_name: str) -> str:
        """生成构造函数Hook模板"""
        code = 'Java.perform(function() {\n'
        code += '    var targetClass = Java.use("%s");\n' % class_name
        code += '    targetClass.$init.implementation = function() {\n'
        code += '        console.log("[*] Constructor called: %s");\n' % class_name
        code += '        for (var i = 0; i < arguments.length; i++) {\n'
        code += '            console.log("  arg" + i + ": " + arguments[i]);\n'
        code += '        }\n'
        code += '        this.$init.apply(this, arguments);\n'
        code += '    };\n'
        code += '});'
        return code

    @staticmethod
    def generate_ssl_unpinning() -> str:
        """生成SSL unpinning模板"""
        lines = [
            "Java.perform(function() {",
            "    // SSL Pinning bypass template",
            '    var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");',
            "    TrustManagerImpl.verifyChain.implementation = function() {",
            '        console.log("[*] SSL Pinning bypassed");',
            "        return;",
            "    };",
            "",
            "    // OkHttp bypass",
            "    try {",
            '        var CertificatePinner = Java.use("okhttp3.CertificatePinner");',
            "        CertificatePinner.check.implementation = function() {",
            '            console.log("[*] OkHttp pinning bypassed");',
            "            return;",
            "        };",
            "    } catch(e) {}",
            "});",
        ]
        return '\n'.join(lines)

    @staticmethod
    def generate_native_hook(lib_name: str, offset: int) -> str:
        """生成Native层Hook模板"""
        lines = [
            "// Native hook template (Frida + Interceptor)",
            'var baseAddr = Module.findBaseAddress("%s");' % lib_name,
            "var targetAddr = baseAddr.add(%d);" % offset,
            "",
            "Interceptor.attach(targetAddr, {",
            "    onEnter: function(args) {",
            '        console.log("[*] Native function called at offset 0x%x");' % offset,
            '        console.log("  arg0: " + args[0]);',
            '        console.log("  arg1: " + args[1]);',
            "        this.arg2 = args[2];",
            "    },",
            "    onLeave: function(retval) {",
            '        console.log("  return: " + retval);',
            "    }",
            "});",
        ]
        return '\n'.join(lines)

    @staticmethod
    def demo():
        """演示Frida Hook生成"""
        print("\n" + "=" * 60)
        print("Frida Hook 模板生成器演示")
        print("=" * 60)

        print("\n[方法Hook模板]")
        hook = FridaHookGenerator.generate_method_hook(
            "com.example.LoginActivity",
            "verifyPassword",
            ["java.lang.String"]
        )
        print(hook[:200] + "\n...")

        print("\n[SSL Unpinning模板]")
        print(FridaHookGenerator.generate_ssl_unpinning()[:150] + "...")
        print()


# ============================================================
# 工具5: APK签名分析
# ============================================================

class ApkSignatureAnalyzer:
    """APK签名证书分析工具"""

    @staticmethod
    def analyze_signature(cert_info: Dict = None) -> Dict:
        """分析APK签名"""
        print("\n" + "=" * 60)
        print("APK 签名证书分析")
        print("=" * 60)

        cert = cert_info or {
            "issuer": "CN=Example Corp, O=Example, C=US",
            "subject": "CN=Example Corp, O=Example, C=US",
            "serial_number": "1A2B3C4D",
            "valid_from": "2020-01-01",
            "valid_to": "2050-01-01",
            "algorithm": "SHA1withRSA",
            "key_size": 2048,
            "self_signed": True,
            "fingerprint_md5": "A1:B2:C3:D4:E5:F6:78:90:12:34:56:78:90:AB:CD:EF",
            "fingerprint_sha1": "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD",
            "fingerprint_sha256": "00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF",
        }

        findings = []

        if cert.get("self_signed"):
            findings.append(("自签名证书", "高", "证书为自签名，无法验证身份"))

        if "SHA1" in cert.get("algorithm", "").upper():
            findings.append(("弱签名算法(SHA1)", "中", "SHA1已被破解，建议使用SHA-256"))

        if cert.get("key_size", 0) < 2048:
            findings.append(("密钥长度不足", "高", "RSA密钥长度小于2048位"))

        print("\n  颁发者: %s" % cert["issuer"])
        print("  主体: %s" % cert["subject"])
        print("  序列号: %s" % cert["serial_number"])
        print("  有效期: %s ~ %s" % (cert["valid_from"], cert["valid_to"]))
        print("  签名算法: %s" % cert["algorithm"])
        print("  密钥长度: %d bits" % cert["key_size"])
        print("  自签名: %s" % ("是" if cert["self_signed"] else "否"))
        print("  MD5指纹: %s" % cert["fingerprint_md5"])
        print("  SHA1指纹: %s" % cert["fingerprint_sha1"])
        print("  SHA256指纹: %s" % cert["fingerprint_sha256"])

        if findings:
            print("\n  发现问题: %d 个" % len(findings))
            for name, risk, desc in findings:
                print("    [!] [%s] %s: %s" % (risk, name, desc))
        else:
            print("\n  [OK] 未发现明显问题")

        print()
        return cert


# ============================================================
# 主菜单
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("APK分析工具箱 (APK Analysis Toolkit)")
    print("=" * 60)
    print("""
请选择工具:
  1. AndroidManifest安全审计
  2. 硬编码密钥检测
  3. WebView安全检测
  4. Frida Hook模板生成器
  5. APK签名分析
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
            ManifestAuditor().run_audit()
        elif choice == "2":
            HardcodedSecretDetector().scan()
        elif choice == "3":
            WebViewSecurityChecker().check()
        elif choice == "4":
            FridaHookGenerator.demo()
        elif choice == "5":
            ApkSignatureAnalyzer.analyze_signature()
        elif choice == "6":
            print("\n[*] 运行全部工具演示...\n")
            ManifestAuditor().run_audit()
            HardcodedSecretDetector().scan()
            WebViewSecurityChecker().check()
            FridaHookGenerator.demo()
            ApkSignatureAnalyzer.analyze_signature()
            print("\n[*] 全部演示完成！")
        else:
            print("无效选项，请重新输入")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
