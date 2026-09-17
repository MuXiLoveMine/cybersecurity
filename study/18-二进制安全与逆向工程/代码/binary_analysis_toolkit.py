#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二进制分析工具包 (Binary Analysis Toolkit)
===========================================

本工具集集成了二进制安全与逆向分析常用的各类工具：
1. 文件格式识别器 - PE/ELF/Mach-O、文件类型、架构识别
2. 字符串提取工具 - 提取二进制中的ASCII/Unicode字符串
3. 危险API检测 - 进程注入、代码执行、网络等危险API
4. 加壳检测工具 - 检测常见壳和混淆器
5. ROP Gadget查找器 - 查找ret指令前的gadget
6. Shellcode编码器 - 多种编码/解码方式

作者：二进制安全学习工具
版本：1.0
用途：仅用于授权的安全测试和教育学习
"""

import os
import re
import sys
import struct
import hashlib
import base64
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime


# ============================================================
# 工具1: 文件格式识别器
# ============================================================

class FileFormatIdentifier:
    """二进制文件格式识别工具"""

    文件类型表 = [
        (b"MZ", "PE (Windows可执行文件)", "Windows"),
        (b"\x7fELF", "ELF (Linux可执行文件)", "Linux"),
        (b"\xcf\xfa\xed\xfe", "Mach-O 64位 (LE)", "macOS/iOS"),
        (b"\xfe\xed\xfa\xce", "Mach-O 32位 (BE)", "macOS"),
        (b"PK\x03\x04", "ZIP压缩包", "Archive"),
        (b"\x89PNG", "PNG图片", "Image"),
        (b"GIF89a", "GIF图片", "Image"),
        (b"\xff\xd8\xff", "JPEG图片", "Image"),
        (b"%PDF", "PDF文档", "Document"),
        (b"dex\n", "DEX (Android Dalvik)", "Android"),
    ]

    PE架构表 = {
        0x8664: "x86-64 (AMD64)",
        0x014c: "x86 (i386)",
        0xaa64: "ARM64",
        0x01c0: "ARM",
    }

    ELF架构表 = {
        0x3E: "x86-64",
        0x03: "x86",
        0xB7: "ARM64",
        0x28: "ARM",
        0xF3: "RISC-V",
    }

    def identify_from_data(self, data: bytes) -> Dict:
        """从二进制数据识别格式"""
        result = {
            "文件大小": len(data),
            "MD5": hashlib.md5(data).hexdigest(),
            "SHA256": hashlib.sha256(data).hexdigest(),
        }

        file_type = "未知"
        platform = "未知"

        for magic, ftype, plat in self.文件类型表:
            if data.startswith(magic):
                file_type = ftype
                platform = plat
                break

        result["文件类型"] = file_type
        result["平台"] = platform

        if data.startswith(b"MZ") and len(data) > 64:
            try:
                pe_offset = struct.unpack_from('<I', data, 0x3C)[0]
                if pe_offset < len(data) - 4 and data[pe_offset:pe_offset+2] == b"PE":
                    result["PE签名偏移"] = hex(pe_offset)
                    machine = struct.unpack_from('<H', data, pe_offset + 4)[0]
                    result["架构"] = self.PE架构表.get(machine, "未知(%s)" % hex(machine))
                    num_sections = struct.unpack_from('<H', data, pe_offset + 6)[0]
                    result["节区数"] = num_sections
            except:
                pass

        if data.startswith(b"\x7fELF") and len(data) > 20:
            try:
                ei_class = data[4]
                result["位数"] = "32位" if ei_class == 1 else "64位"
                ei_data = data[5]
                result["字节序"] = "小端(LE)" if ei_data == 1 else "大端(BE)"
                if ei_data == 1:
                    e_machine = struct.unpack_from('<H', data, 18)[0]
                    e_type = struct.unpack_from('<H', data, 16)[0]
                else:
                    e_machine = struct.unpack_from('>H', data, 18)[0]
                    e_type = struct.unpack_from('>H', data, 16)[0]
                result["架构"] = self.ELF架构表.get(e_machine, "未知(%s)" % hex(e_machine))
                type_map = {1: "可重定位", 2: "可执行", 3: "共享对象", 4: "核心转储"}
                result["类型"] = type_map.get(e_type, "未知(%d)" % e_type)
            except:
                pass

        return result

    def identify_demo(self):
        """演示文件识别"""
        print("\n" + "=" * 60)
        print("文件格式识别演示")
        print("=" * 60)

        pe_header = b"MZ" + b"\x00" * 58 + struct.pack('<I', 0x80)
        pe_header += b"\x00" * 60
        pe_header += b"PE\x00\x00" + struct.pack('<H', 0x8664)
        pe_header += b"\x00" * 20 + struct.pack('<H', 4)

        result = self.identify_from_data(pe_header)

        print("\n文件大小: %d 字节" % result["文件大小"])
        print("MD5: %s" % result["MD5"])
        print("文件类型: %s" % result["文件类型"])
        print("平台: %s" % result["平台"])
        if '架构' in result:
            print("架构: %s" % result["架构"])
        if '节区数' in result:
            print("节区数: %s" % result["节区数"])
        print()

        elf_header = b"\x7fELF"
        elf_header += bytes([2])
        elf_header += bytes([1])
        elf_header += bytes([1])
        elf_header += b"\x00" * 9
        elf_header += struct.pack('<H', 2)
        elf_header += struct.pack('<H', 0x3E)

        result2 = self.identify_from_data(elf_header)
        print("\n[ELF文件示例]")
        print("文件类型: %s" % result2["文件类型"])
        print("位数: %s" % result2.get("位数", "未知"))
        print("字节序: %s" % result2.get("字节序", "未知"))
        print("架构: %s" % result2.get("架构", "未知"))
        print("类型: %s" % result2.get("类型", "未知"))
        print()


# ============================================================
# 工具2: 字符串提取工具
# ============================================================

class StringExtractor:
    """二进制字符串提取工具"""

    @staticmethod
    def extract_ascii_strings(data: bytes, min_length: int = 4) -> List[str]:
        """提取ASCII字符串"""
        strings = []
        current = []

        for byte in data:
            if 0x20 <= byte <= 0x7E:
                current.append(chr(byte))
            else:
                if len(current) >= min_length:
                    strings.append(''.join(current))
                current = []

        if len(current) >= min_length:
            strings.append(''.join(current))

        return strings

    @staticmethod
    def extract_unicode_strings(data: bytes, min_length: int = 4) -> List[str]:
        """提取Unicode字符串"""
        strings = []
        i = 0
        while i < len(data) - 1:
            current = []
            while i < len(data) - 1:
                char_low = data[i]
                char_high = data[i + 1]
                if char_high == 0 and 0x20 <= char_low <= 0x7E:
                    current.append(chr(char_low))
                    i += 2
                else:
                    break
            if len(current) >= min_length:
                strings.append(''.join(current))
            i += 1

        return strings

    @staticmethod
    def find_sensitive_strings(strings: List[str]) -> List[Tuple[str, str]]:
        """查找敏感字符串"""
        敏感模式 = [
            (r'password|passwd|pwd', "密码相关"),
            (r'api[_-]?key|secret|token', "密钥相关"),
            (r'http://|https://', "URL地址"),
            (r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run', "注册表启动项"),
            (r'cmd\.exe|powershell|wscript|cscript', "命令执行相关"),
            (r'KERNEL32|ntdll|user32|advapi32', "系统DLL"),
            (r'CreateRemoteThread|WriteProcessMemory|VirtualAlloc', "注入相关API"),
        ]

        findings = []
        for s in strings:
            for pattern, category in 敏感模式:
                if re.search(pattern, s, re.IGNORECASE):
                    findings.append((s, category))
                    break

        return findings

    @staticmethod
    def demo():
        """演示字符串提取"""
        print("\n" + "=" * 60)
        print("字符串提取工具演示")
        print("=" * 60)

        binary_data = (
            b"\x00\x00\x00\x00"
            b"This is a test string\x00"
            b"\x00\x00"
            b"password123\x00"
            b"\x00"
            b"http://evil.com/malware.exe\x00"
            b"\x00\x00"
            b"CreateRemoteThread\x00"
            b"\x00\x00\x00"
        )

        strings = StringExtractor.extract_ascii_strings(binary_data)
        print("\n提取到 %d 个ASCII字符串:" % len(strings))
        for s in strings:
            print("  - %s" % s)

        sensitive = StringExtractor.find_sensitive_strings(strings)
        print("\n发现 %d 个敏感字符串:" % len(sensitive))
        for s, category in sensitive:
            print("  [!] [%s] %s" % (category, s))

        print()


# ============================================================
# 工具3: 危险API检测
# ============================================================

class DangerousAPIDetector:
    """危险API检测工具"""

    危险API列表 = [
        ("CreateRemoteThread", "进程注入", "高危"),
        ("CreateRemoteThreadEx", "进程注入", "高危"),
        ("WriteProcessMemory", "进程内存写入", "高危"),
        ("ReadProcessMemory", "进程内存读取", "中危"),
        ("VirtualAllocEx", "远程内存分配", "高危"),
        ("VirtualProtectEx", "远程内存保护修改", "高危"),
        ("OpenProcess", "打开进程", "中危"),
        ("WinExec", "执行程序", "高危"),
        ("ShellExecute", "Shell执行", "高危"),
        ("ShellExecuteEx", "Shell执行", "高危"),
        ("CreateProcess", "创建进程", "中危"),
        ("system", "执行系统命令", "高危"),
        ("popen", "执行系统命令", "高危"),
        ("LoadLibrary", "加载DLL", "中危"),
        ("GetProcAddress", "获取函数地址", "中危"),
        ("RegSetValueEx", "设置注册表值", "中危"),
        ("RegCreateKeyEx", "创建注册表键", "中危"),
        ("InternetOpen", "网络连接", "中危"),
        ("InternetOpenUrl", "打开URL", "中危"),
        ("HttpSendRequest", "HTTP请求", "中危"),
        ("recv", "接收数据", "低危"),
        ("send", "发送数据", "低危"),
        ("IsDebuggerPresent", "检测调试器", "低危"),
        ("CheckRemoteDebuggerPresent", "远程调试检测", "低危"),
        ("OutputDebugString", "输出调试信息", "低危"),
    ]

    def __init__(self, imports: List[str] = None):
        self.imports = imports or self._get_sample_imports()

    def _get_sample_imports(self) -> List[str]:
        return [
            "CreateRemoteThread",
            "WriteProcessMemory",
            "VirtualAllocEx",
            "OpenProcess",
            "WinExec",
            "LoadLibraryA",
            "GetProcAddress",
            "RegSetValueExA",
            "InternetOpenUrlA",
            "HttpSendRequestA",
            "IsDebuggerPresent",
            "CheckRemoteDebuggerPresent",
            "recv",
            "send",
            "CreateFileA",
            "ReadFile",
            "WriteFile",
            "CloseHandle",
        ]

    def detect(self) -> List[Dict]:
        """检测危险API"""
        print("\n" + "=" * 60)
        print("危险API检测")
        print("=" * 60)

        findings = []
        api_map = {}
        for api, cat, risk in self.危险API列表:
            api_map[api.lower()] = (api, cat, risk)

        for imp in self.imports:
            if imp.lower() in api_map:
                api_name, category, risk = api_map[imp.lower()]
                findings.append({
                    "api": api_name,
                    "category": category,
                    "risk": risk,
                })

        risk_count = defaultdict(int)
        for f in findings:
            risk_count[f["risk"]] += 1

        print("\n导入API总数: %d" % len(self.imports))
        print("危险API数: %d" % len(findings))
        print("风险分布: 高危=%d 中危=%d 低危=%d" % (
            risk_count["高危"], risk_count["中危"], risk_count["低危"]))
        print()

        current_cat = ""
        for f in findings:
            if f["category"] != current_cat:
                current_cat = f["category"]
                print("\n【%s】" % current_cat)
            icon = "[!]" if f["risk"] == "高危" else "[*]" if f["risk"] == "中危" else "[-]"
            print("  %s [%s] %s" % (icon, f["risk"], f["api"]))

        print()
        return findings


# ============================================================
# 工具4: 加壳检测工具
# ============================================================

class PackerDetector:
    """加壳检测工具"""

    常见壳特征 = [
        ("UPX", ["UPX!", "UPX0", "UPX1", "UPX2"], "UPX压缩壳"),
        ("ASProtect", [".aspack", "ASProtect"], "ASProtect加密壳"),
        ("Themida", ["Themida"], "Themida虚拟机保护"),
        ("VMProtect", ["vmp0", "VMProtect"], "VMProtect虚拟机保护"),
        ("Enigma", ["Enigma"], "Enigma保护壳"),
        ("Armadillo", ["armadillo"], "Armadillo保护壳"),
        ("NSIS", ["NSIS"], "NSIS安装程序"),
        ("WinRAR", ["WinRAR"], "WinRAR自解压"),
    ]

    def __init__(self, data: bytes = None, sections: List[str] = None):
        self.data = data or b""
        self.sections = sections or [".text", ".rdata", ".data", ".rsrc"]

    def detect(self) -> List[Tuple[str, str]]:
        """检测加壳"""
        print("\n" + "=" * 60)
        print("加壳检测")
        print("=" * 60)

        findings = []

        print("\n节区列表: %s" % ", ".join(self.sections))
        print()

        for packer_name, signatures, desc in self.常见壳特征:
            for sig in signatures:
                if sig in self.sections or (self.data and sig.encode() in self.data):
                    findings.append((packer_name, desc))
                    break

        异常特征 = []
        if len(self.sections) < 3:
            异常特征.append("节区数量异常少")
        if ".text" not in self.sections:
            异常特征.append("缺少.text节区")

        if 异常特征 and not findings:
            findings.append(("未知壳/混淆", "存在异常特征，可能加壳或混淆"))

        if findings:
            print("发现 %d 个加壳迹象:" % len(findings))
            for name, desc in findings:
                print("  [!] %s: %s" % (name, desc))
        else:
            print("[OK] 未发现明显加壳迹象")

        if 异常特征:
            print("\n异常特征:")
            for feat in 异常特征:
                print("  - %s" % feat)

        print()
        return findings


# ============================================================
# 工具5: ROP Gadget查找器
# ============================================================

class ROPGadgetFinder:
    """ROP Gadget查找工具（简化版）"""

    @staticmethod
    def find_ret_gadgets(data: bytes, max_length: int = 8) -> List[Tuple[int, str]]:
        """查找ret (0xC3) 前面的gadget"""
        gadgets = []

        for i in range(len(data)):
            if data[i] == 0xC3:
                for length in range(1, max_length + 1):
                    start = i - length
                    if start < 0:
                        break
                    gadget_bytes = data[start:i + 1]
                    hex_str = gadget_bytes.hex()
                    gadgets.append((start, hex_str))

        return gadgets

    @staticmethod
    def demo():
        """演示ROP Gadget查找"""
        print("\n" + "=" * 60)
        print("ROP Gadget 查找器演示")
        print("=" * 60)

        code = bytes([
            0x58, 0xC3,
            0x5B, 0xC3,
            0x59, 0xC3,
            0x5A, 0xC3,
            0x5F, 0xC3,
            0x5E, 0xC3,
            0x5D, 0xC3,
            0xC3,
            0x90, 0x90, 0xC3,
            0xFF, 0xE0,
        ])

        gadgets = ROPGadgetFinder.find_ret_gadgets(code, max_length=3)

        print("\n找到 %d 个以ret结尾的gadget (简化版)" % len(gadgets))
        print()

        useful = [
            ("pop eax ; ret", "58c3"),
            ("pop ebx ; ret", "5bc3"),
            ("pop ecx ; ret", "59c3"),
            ("pop edx ; ret", "5ac3"),
        ]

        print("【有用的Gadget示例】")
        for name, hex_code in useful:
            print("  %-20s %s" % (name, hex_code))

        print("""
【ROP攻击原理】
1. 程序存在栈溢出漏洞
2. 控制eip寄存器
3. 用程序中已有的代码片段(gadget)拼接代码
4. 每个gadget以ret结尾，串起来形成ROP链
5. 最终执行系统调用或shellcode

【常见用途】
- 禁用NX/DEP保护时执行shellcode
- 调用system('/bin/sh')
- mprotect + 跳转到shellcode
- execve系统调用
""")

        print()


# ============================================================
# 工具6: Shellcode编码工具
# ============================================================

class ShellcodeEncoder:
    """Shellcode编码工具"""

    @staticmethod
    def xor_encode(shellcode: bytes, key: int = 0x41) -> bytes:
        """XOR编码"""
        return bytes([b ^ key for b in shellcode])

    @staticmethod
    def add_encode(shellcode: bytes, value: int = 1) -> bytes:
        """加法编码"""
        return bytes([(b + value) & 0xFF for b in shellcode])

    @staticmethod
    def sub_encode(shellcode: bytes, value: int = 1) -> bytes:
        """减法编码"""
        return bytes([(b - value) & 0xFF for b in shellcode])

    @staticmethod
    def rotate_left(shellcode: bytes, bits: int = 1) -> bytes:
        """循环左移"""
        return bytes([((b << bits) | (b >> (8 - bits))) & 0xFF for b in shellcode])

    @staticmethod
    def format_c_shellcode(shellcode: bytes) -> str:
        """格式化为C语言风格"""
        hex_str = ''.join('\\x%02x' % b for b in shellcode)
        return '"' + hex_str + '"'

    @staticmethod
    def format_python_shellcode(shellcode: bytes) -> str:
        """格式化为Python风格"""
        return "b'" + ''.join('\\x%02x' % b for b in shellcode) + "'"

    @staticmethod
    def demo():
        """演示Shellcode编码"""
        print("\n" + "=" * 60)
        print("Shellcode 编码工具演示")
        print("=" * 60)

        sample_shellcode = bytes([0x31, 0xC0, 0x50, 0x68, 0x2F, 0x2F, 0x73, 0x68])

        print("\n原始shellcode:")
        print("  %s" % sample_shellcode.hex())
        c_fmt = ShellcodeEncoder.format_c_shellcode(sample_shellcode)
        print("  C格式: %s..." % c_fmt[:60])

        print("\nXOR编码 (key=0x41):")
        xor_encoded = ShellcodeEncoder.xor_encode(sample_shellcode, 0x41)
        print("  %s" % xor_encoded.hex())

        print("\n加法编码 (+1):")
        add_encoded = ShellcodeEncoder.add_encode(sample_shellcode, 1)
        print("  %s" % add_encoded.hex())

        print("""
【编码器用途】
1. 坏字符绕过 - 去除shellcode中的0x00等坏字符
2. 杀毒软件绕过 - 变形躲避特征码检测
3. 大小限制 - 特定场景下的优化

【注意】
本工具仅用于学习研究，请勿用于非法用途
""")
        print()


# ============================================================
# 主菜单
# ============================================================

def main():
    print("\n" + "=" * 60)
    print("二进制分析工具包 (Binary Analysis Toolkit)")
    print("=" * 60)
    print("""
请选择工具:
  1. 文件格式识别器
  2. 字符串提取工具
  3. 危险API检测
  4. 加壳检测
  5. ROP Gadget查找器
  6. Shellcode编码工具
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
            FileFormatIdentifier().identify_demo()
        elif choice == "2":
            StringExtractor.demo()
        elif choice == "3":
            DangerousAPIDetector().detect()
        elif choice == "4":
            PackerDetector(sections=[".text", ".rdata", ".data"]).detect()
        elif choice == "5":
            ROPGadgetFinder.demo()
        elif choice == "6":
            ShellcodeEncoder.demo()
        elif choice == "7":
            print("\n[*] 运行全部工具演示...\n")
            FileFormatIdentifier().identify_demo()
            StringExtractor.demo()
            DangerousAPIDetector().detect()
            PackerDetector(sections=[".text", ".rdata", ".data"]).detect()
            ROPGadgetFinder.demo()
            ShellcodeEncoder.demo()
            print("\n[*] 全部演示完成！")
        else:
            print("无效选项，请重新输入")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
