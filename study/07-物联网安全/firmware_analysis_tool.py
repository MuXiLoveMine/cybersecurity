#!/usr/bin/env python3
"""
IoT固件分析工具
================

功能:
1. 固件格式识别与解包
2. 文件系统提取与挂载
3. 敏感信息扫描（密码、密钥、证书）
4. 二进制漏洞分析（缓冲区溢出、硬编码凭证）
5. 固件比对与差异分析
6. 固件安全评估报告生成

作者: IoT Security Researcher
版本: 1.0.0
"""

import os
import sys
import re
import struct
import hashlib
import logging
import json
import argparse
import subprocess
import zipfile
import tarfile
import gzip
import binascii
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict, Counter

# ============================================================
# 日志配置
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('firmware_analysis.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger('FirmwareAnalyzer')

# ============================================================
# 固件格式识别
# ============================================================

class FirmwareFormat:
    """固件格式识别器"""

    # 固件魔数签名表
    MAGIC_SIGNATURES = {
        'uImage': {
            'magic': b'\x27\x05\x19\x56',
            'offset': 0,
            'description': 'U-Boot Linux Image',
            'header_size': 64,
        },
        'SquashFS': {
            'magic': b'hsqs',
            'offset': 0,
            'description': 'SquashFS Filesystem',
            'header_size': 96,
        },
        'SquashFS_BE': {
            'magic': b'sqsh',
            'offset': 0,
            'description': 'SquashFS Filesystem (Big Endian)',
        },
        'JFFS2': {
            'magic': b'\x85\x19',
            'offset': 0,
            'description': 'JFFS2 Filesystem',
        },
        'JFFS2_OLD': {
            'magic': b'\x84\x19',
            'offset': 0,
            'description': 'JFFS2 Filesystem (Old)',
        },
        'CramFS': {
            'magic': b'\x45\x3d\xcd\x28',
            'offset': 0,
            'description': 'Compressed ROM File System',
        },
        'UBIFS': {
            'magic': b'\x31\x18\x10\x06',
            'offset': 0,
            'description': 'UBI File System',
        },
        'GZIP': {
            'magic': b'\x1f\x8b',
            'offset': 0,
            'description': 'GZIP Compressed',
        },
        'LZMA': {
            'magic': b'\x5d\x00\x00',
            'offset': 0,
            'description': 'LZMA Compressed',
        },
        'XZ': {
            'magic': b'\xfd\x37\x7a\x58\x5a\x00',
            'offset': 0,
            'description': 'XZ Compressed',
        },
        'ELF': {
            'magic': b'\x7fELF',
            'offset': 0,
            'description': 'ELF Executable',
        },
        'TPFX': {
            'magic': b'TPFX',
            'offset': 0,
            'description': 'TP-Link Firmware',
        },
        'DLK': {
            'magic': b'DLK\x00',
            'offset': 0,
            'description': 'D-Link Firmware',
        },
        'BROADCOM': {
            'magic': b'\x2a\x12\x34\x56',
            'offset': 0,
            'description': 'Broadcom Firmware',
        },
        'SEAMA': {
            'magic': b'\x5e\xa3\xa4\x00',
            'offset': 0,
            'description': 'Seama Firmware',
        },
    }

    @classmethod
    def identify(cls, data: bytes) -> List[Dict[str, Any]]:
        """识别固件格式"""
        results = []

        for name, sig_info in cls.MAGIC_SIGNATURES.items():
            magic = sig_info['magic']
            offset = sig_info['offset']

            if len(data) >= offset + len(magic):
                if data[offset:offset + len(magic)] == magic:
                    results.append({
                        'format': name,
                        'description': sig_info['description'],
                        'offset': offset,
                    })

        # 扫描整个文件查找嵌入式文件系统
        for name, sig_info in cls.MAGIC_SIGNATURES.items():
            magic = sig_info['magic']
            search_pos = 0
            while search_pos < len(data) - len(magic):
                pos = data.find(magic, search_pos)
                if pos == -1:
                    break
                if pos > 0:  # 不在文件开头
                    already_found = any(
                        r['offset'] == pos for r in results
                    )
                    if not already_found:
                        results.append({
                            'format': name,
                            'description': sig_info['description'],
                            'offset': pos,
                        })
                search_pos = pos + 1

        return results


# ============================================================
# 固件解包器
# ============================================================

class FirmwareUnpacker:
    """固件解包工具"""

    def __init__(self, output_dir: str = './firmware_extracted'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def unpack(self, firmware_path: str) -> Dict[str, Any]:
        """解包固件"""
        logger.info(f"开始解包: {firmware_path}")

        with open(firmware_path, 'rb') as f:
            data = f.read()

        # 识别格式
        formats = FirmwareFormat.identify(data)
        logger.info(f"识别到 {len(formats)} 个格式标记")

        result = {
            'file': firmware_path,
            'size': len(data),
            'md5': hashlib.md5(data).hexdigest(),
            'sha256': hashlib.sha256(data).hexdigest(),
            'formats': formats,
            'extracted_files': [],
        }

        # 按格式解包
        for fmt in formats:
            try:
                extracted = self._extract_by_format(data, fmt)
                result['extracted_files'].extend(extracted)
            except Exception as e:
                logger.warning(f"解包 {fmt['format']} 失败: {e}")

        # 尝试使用binwalk提取
        try:
            binwalk_result = self._binwalk_extract(firmware_path)
            if binwalk_result:
                result['extracted_files'].extend(binwalk_result)
        except Exception as e:
            logger.debug(f"binwalk提取失败: {e}")

        logger.info(f"共提取 {len(result['extracted_files'])} 个文件")
        return result

    def _extract_by_format(self, data: bytes,
                           fmt: Dict) -> List[str]:
        """按格式提取"""
        extracted = []
        fmt_name = fmt['format']
        offset = fmt['offset']

        if fmt_name == 'GZIP':
            extracted_path = os.path.join(
                self.output_dir, f'gzip_{offset}.bin'
            )
            try:
                decompressed = gzip.decompress(data[offset:])
                with open(extracted_path, 'wb') as f:
                    f.write(decompressed)
                extracted.append(extracted_path)
                logger.info(f"解压GZIP: {extracted_path}")
            except Exception:
                pass

        elif fmt_name == 'SquashFS':
            extracted_path = os.path.join(
                self.output_dir, 'squashfs.img'
            )
            with open(extracted_path, 'wb') as f:
                f.write(data[offset:])
            extracted.append(extracted_path)
            logger.info(f"提取SquashFS: {extracted_path}")

            # 尝试用unsquashfs解包
            try:
                sqfs_dir = os.path.join(self.output_dir, 'squashfs_root')
                subprocess.run(
                    ['unsquashfs', '-d', sqfs_dir, extracted_path],
                    capture_output=True, timeout=60
                )
                if os.path.exists(sqfs_dir):
                    extracted.append(sqfs_dir)
            except Exception as e:
                logger.debug(f"unsquashfs失败: {e}")

        elif fmt_name == 'uImage':
            # 解析U-Boot镜像头
            header = data[offset:offset + 64]
            if len(header) >= 64:
                magic, hcrc, os_type, arch, img_type = struct.unpack(
                    '>IIIII', header[:20]
                )
                img_size = struct.unpack('>I', header[20:24])[0]
                logger.info(f"uImage: OS={os_type}, Arch={arch}, "
                          f"Size={img_size}")

                # 提取内核镜像
                kernel_path = os.path.join(
                    self.output_dir, 'kernel.img'
                )
                with open(kernel_path, 'wb') as f:
                    f.write(data[offset + 64:offset + 64 + img_size])
                extracted.append(kernel_path)

        elif fmt_name == 'ELF':
            extracted_path = os.path.join(
                self.output_dir, f'elf_{offset}.bin'
            )
            with open(extracted_path, 'wb') as f:
                f.write(data[offset:])
            extracted.append(extracted_path)

        return extracted

    def _binwalk_extract(self, firmware_path: str) -> List[str]:
        """使用binwalk提取"""
        try:
            result = subprocess.run(
                ['binwalk', '-e', '-C', self.output_dir,
                 firmware_path],
                capture_output=True, timeout=120, text=True
            )
            extracted = []
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    extracted.append(os.path.join(root, file))
            return extracted
        except FileNotFoundError:
            logger.debug("binwalk未安装")
            return []
        except Exception:
            return []


# ============================================================
# 敏感信息扫描器
# ============================================================

class SensitiveInfoScanner:
    """敏感信息扫描器"""

    # 敏感信息正则模式
    PATTERNS = {
        'password': [
            re.compile(rb'password\s*[=:]\s*["\']?(.+?)["\']?[\s\r\n]',
                      re.IGNORECASE),
            re.compile(rb'passwd\s*[=:]\s*["\']?(.+?)["\']?[\s\r\n]',
                      re.IGNORECASE),
            re.compile(rb'pwd\s*[=:]\s*["\']?(.+?)["\']?[\s\r\n]',
                      re.IGNORECASE),
        ],
        'private_key': [
            re.compile(rb'-----BEGIN\s+RSA\s+PRIVATE\s+KEY-----'),
            re.compile(rb'-----BEGIN\s+EC\s+PRIVATE\s+KEY-----'),
            re.compile(rb'-----BEGIN\s+PRIVATE\s+KEY-----'),
            re.compile(rb'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----'),
        ],
        'certificate': [
            re.compile(rb'-----BEGIN\s+CERTIFICATE-----'),
        ],
        'api_key': [
            re.compile(rb'api[_-]?key\s*[=:]\s*["\'](.+?)["\']',
                      re.IGNORECASE),
            re.compile(rb'secret\s*[=:]\s*["\'](.+?)["\']',
                      re.IGNORECASE),
            re.compile(rb'token\s*[=:]\s*["\'](.+?)["\']',
                      re.IGNORECASE),
        ],
        'database': [
            re.compile(rb'(mysql|postgres|mongodb|redis)://'
                      rb'(\w+):(\w+)@(\w+)', re.IGNORECASE),
        ],
        'ip_address': [
            re.compile(rb'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'),
        ],
        'email': [
            re.compile(rb'[\w.]+@[\w.]+\.\w+'),
        ],
        'url': [
            re.compile(rb'https?://[\w./\-?=&]+'),
        ],
        'shadow_file': [
            re.compile(rb'root:[$].*'),
            re.compile(rb'\w+:[$][^:]+:'),
        ],
        'config_files': [
            re.compile(rb'config\.json'),
            re.compile(rb'config\.xml'),
            re.compile(rb'config\.conf'),
        ],
        'telnet_credentials': [
            re.compile(rb'telnet.*?password.*?(\w+)',
                      re.IGNORECASE | re.DOTALL),
        ],
        'ssh_config': [
            re.compile(rb'PermitRootLogin\s+(yes|prohibit-password)',
                      re.IGNORECASE),
            re.compile(rb'PasswordAuthentication\s+yes',
                      re.IGNORECASE),
        ],
        'wifi_credentials': [
            re.compile(rb'ssid\s*[=:]\s*["\'](.+?)["\']',
                      re.IGNORECASE),
            re.compile(rb'wpa_passphrase\s+(.+?)[\r\n]',
                      re.IGNORECASE),
            re.compile(rb'psk\s*[=:]\s*["\'](.+?)["\']',
                      re.IGNORECASE),
        ],
    }

    # 常见默认凭证
    DEFAULT_CREDENTIALS = [
        (b'admin', b'admin'),
        (b'admin', b'password'),
        (b'admin', b'1234'),
        (b'admin', b''),
        (b'root', b'root'),
        (b'root', b''),
        (b'root', b'toor'),
        (b'root', b'admin'),
        (b'admin', b'admin123'),
        (b'guest', b'guest'),
        (b'user', b'user'),
        (b'support', b'support'),
        (b'admin', b'12345'),
        (b'admin', b'123456'),
        (b'admin', b'password123'),
        (b'admin', b'admin@123'),
    ]

    def __init__(self):
        self.findings = []

    def scan_file(self, filepath: str) -> List[Dict[str, Any]]:
        """扫描单个文件"""
        findings = []

        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            # 如果文件太大，只扫描前面部分
            if len(data) > 10 * 1024 * 1024:
                data = data[:10 * 1024 * 1024]
                logger.debug(f"文件过大, 截断扫描: {filepath}")

            for category, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    for match in pattern.finditer(data):
                        finding = {
                            'file': filepath,
                            'category': category,
                            'match': match.group(0).decode(
                                'utf-8', errors='replace'
                            )[:200],
                            'offset': match.start(),
                        }
                        # 提取捕获组
                        if match.groups():
                            finding['extracted'] = match.group(1).decode(
                                'utf-8', errors='replace'
                            )[:100]
                        findings.append(finding)

            # 检查默认凭证
            for username, password in self.DEFAULT_CREDENTIALS:
                if username in data and password in data:
                    # 检查它们是否靠近
                    for pos in range(len(data) - len(username)):
                        if data[pos:pos + len(username)] == username:
                            nearby = data[pos:pos + 50]
                            if password in nearby:
                                findings.append({
                                    'file': filepath,
                                    'category': 'default_credential',
                                    'match': f'{username.decode()}:{password.decode()}',
                                    'offset': pos,
                                })
                                break

        except Exception as e:
            logger.debug(f"扫描文件失败 {filepath}: {e}")

        self.findings.extend(findings)
        return findings

    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """扫描整个目录"""
        all_findings = []

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                findings = self.scan_file(filepath)
                all_findings.extend(findings)

        # 按类别统计
        category_counts = Counter(f['category'] for f in all_findings)
        logger.info("敏感信息扫描完成:")
        for cat, count in category_counts.items():
            logger.info(f"  {cat}: {count}")

        return all_findings


# ============================================================
# 二进制漏洞分析器
# ============================================================

class BinaryAnalyzer:
    """二进制文件安全分析"""

    # 危险函数列表
    DANGEROUS_FUNCTIONS = {
        'strcpy': '缓冲区溢出 - 无边界检查的字符串复制',
        'strcat': '缓冲区溢出 - 无边界检查的字符串拼接',
        'sprintf': '缓冲区溢出 - 无边界检查的格式化输出',
        'vsprintf': '缓冲区溢出 - 无边界检查的格式化输出',
        'gets': '缓冲区溢出 - 无长度限制的输入读取',
        'scanf': '格式化字符串漏洞',
        'sscanf': '格式化字符串漏洞',
        'fscanf': '格式化字符串漏洞',
        'system': '命令注入风险',
        'popen': '命令注入风险',
        'execve': '命令注入风险',
        'execl': '命令注入风险',
        'execv': '命令注入风险',
        'popen': '命令注入风险',
        'strtok': '非线程安全',
        'rand': '弱随机数生成器',
        'crypt': '弱加密函数',
        'MD5': '弱哈希算法',
        'SHA1': '弱哈希算法',
        'DES': '弱加密算法',
    }

    # 安全编译选项检查
    SECURITY_FEATURES = {
        'NX': '不可执行栈 (NX/DEP)',
        'PIE': '位置无关可执行文件',
        'RELRO': '只读重定位 (RELRO)',
        'Stack_Canary': '栈保护 (Stack Canary)',
        'FORTIFY': '源码 fortified (FORTIFY_SOURCE)',
    }

    def __init__(self):
        self.results = {}

    def analyze_elf(self, filepath: str) -> Dict[str, Any]:
        """分析ELF文件"""
        result = {
            'file': filepath,
            'type': 'ELF',
            'arch': '',
            'bits': 0,
            'endian': '',
            'dangerous_functions': [],
            'security_features': {},
            'strings': [],
        }

        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            # 解析ELF头
            if data[:4] == b'\x7fELF':
                result['bits'] = 32 if data[4] == 1 else 64
                result['endian'] = 'LE' if data[5] == 1 else 'BE'

                # 机器类型
                if result['bits'] == 32:
                    machine = struct.unpack('<H', data[18:20])[0]
                else:
                    machine = struct.unpack('<H', data[18:20])[0]

                arch_map = {
                    0x03: 'x86',
                    0x08: 'MIPS',
                    0x28: 'ARM',
                    0x3E: 'x86_64',
                    0xB7: 'AArch64',
                    0x16: 'RISC-V',
                }
                result['arch'] = arch_map.get(machine, f'Unknown({hex(machine)})')

            # 检查危险函数
            for func_name, description in self.DANGEROUS_FUNCTIONS.items():
                # 在字符串表中查找
                pattern = func_name.encode() + b'\x00'
                if pattern in data:
                    result['dangerous_functions'].append({
                        'function': func_name,
                        'risk': description,
                    })

            # 检查安全编译选项
            result['security_features'] = self._check_security_features(
                filepath, data
            )

            # 提取有意义的字符串
            result['strings'] = self._extract_interesting_strings(data)

        except Exception as e:
            result['error'] = str(e)

        return result

    def _check_security_features(self, filepath: str,
                                 data: bytes) -> Dict[str, bool]:
        """检查安全编译选项"""
        features = {
            'NX': False,
            'PIE': False,
            'RELRO': False,
            'Stack_Canary': False,
            'FORTIFY': False,
        }

        # NX: 检查PT_GNU_STACK段
        if b'GNU_STACK' in data:
            # 查找program header中的GNU_STACK
            idx = data.find(b'GNU_STACK')
            if idx > 0:
                # 检查flags (在program header中)
                # flags字段在offset + 4*4 (32位) 或 4*8 (64位)
                features['NX'] = True

        # PIE: 检查ELF类型
        if data[:4] == b'\x7fELF':
            elf_type = struct.unpack('<H', data[16:18])[0]
            if elf_type == 3:  # ET_DYN = 共享对象/PIE
                features['PIE'] = True

        # RELRO: 检查GNU_RELRO段
        if b'GNU_RELRO' in data:
            features['RELRO'] = True
            if b'BIND_NOW' in data:
                features['RELRO'] = 'Full'

        # Stack Canary: 检查canary符号
        canary_names = [
            b'__stack_chk_fail',
            b'__stack_chk_guard',
            b'__intel_security_cookie',
        ]
        for name in canary_names:
            if name in data:
                features['Stack_Canary'] = True
                break

        # FORTIFY: 检查fortified函数
        fortify_funcs = [
            b'__sprintf_chk',
            b'__strcpy_chk',
            b'__strcat_chk',
            b'__memcpy_chk',
            b'__snprintf_chk',
        ]
        for func in fortify_funcs:
            if func in data:
                features['FORTIFY'] = True
                break

        return features

    def _extract_interesting_strings(self, data: bytes,
                                      min_len: int = 4,
                                      max_strings: int = 100) -> List[str]:
        """提取有意义的字符串"""
        strings = []
        current = b''

        for byte in data:
            if 32 <= byte <= 126:  # 可打印ASCII
                current += bytes([byte])
            else:
                if len(current) >= min_len:
                    s = current.decode('ascii', errors='ignore')
                    # 过滤有意义的字符串
                    if self._is_interesting(s):
                        strings.append(s)
                        if len(strings) >= max_strings:
                            break
                current = b''

        return strings

    def _is_interesting(self, s: str) -> bool:
        """判断字符串是否有意义"""
        interesting_keywords = [
            'password', 'passwd', 'pwd', 'secret', 'key', 'token',
            'admin', 'root', 'config', 'debug', 'shell', 'cmd',
            'exec', 'system', 'telnet', 'ssh', 'ftp', 'http',
            'api', 'url', 'host', 'port', 'user', 'login',
            'auth', 'cert', 'crypto', 'encrypt', 'decrypt',
            'firmware', 'version', 'build', 'update',
            'netgear', 'tplink', 'dlink', 'linksys',
            'wpa', 'ssid', 'wifi',
        ]

        s_lower = s.lower()
        for keyword in interesting_keywords:
            if keyword in s_lower:
                return True
        return False


# ============================================================
# 固件差异分析器
# ============================================================

class FirmwareDiffer:
    """固件版本差异分析"""

    def __init__(self):
        self.results = {}

    def compare(self, old_dir: str, new_dir: str) -> Dict[str, Any]:
        """比较两个固件版本"""
        result = {
            'old_version': old_dir,
            'new_version': new_dir,
            'added': [],
            'removed': [],
            'modified': [],
            'summary': {},
        }

        old_files = self._get_file_list(old_dir)
        new_files = self._get_file_list(new_dir)

        old_set = set(old_files.keys())
        new_set = set(new_files.keys())

        # 新增文件
        for f in new_set - old_set:
            result['added'].append(f)

        # 删除文件
        for f in old_set - new_set:
            result['removed'].append(f)

        # 修改文件
        common = old_set & new_set
        for f in common:
            old_hash = old_files[f]
            new_hash = new_files[f]
            if old_hash != new_hash:
                result['modified'].append({
                    'file': f,
                    'old_hash': old_hash,
                    'new_hash': new_hash,
                })

        # 汇总
        result['summary'] = {
            'total_old': len(old_files),
            'total_new': len(new_files),
            'added_count': len(result['added']),
            'removed_count': len(result['removed']),
            'modified_count': len(result['modified']),
        }

        return result

    def _get_file_list(self, directory: str) -> Dict[str, str]:
        """获取目录下所有文件及其哈希"""
        files = {}
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                relpath = os.path.relpath(filepath, directory)
                try:
                    with open(filepath, 'rb') as f:
                        files[relpath] = hashlib.sha256(
                            f.read()
                        ).hexdigest()
                except Exception:
                    pass
        return files


# ============================================================
# 固件安全评估报告
# ============================================================

class SecurityReport:
    """固件安全评估报告生成器"""

    SEVERITY_LEVELS = {
        'CRITICAL': 4,
        'HIGH': 3,
        'MEDIUM': 2,
        'LOW': 1,
        'INFO': 0,
    }

    def __init__(self):
        self.findings = []

    def add_finding(self, severity: str, category: str,
                    description: str, file: str = '',
                    recommendation: str = ''):
        """添加安全发现"""
        self.findings.append({
            'severity': severity,
            'category': category,
            'description': description,
            'file': file,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat(),
        })

    def generate(self, output_path: str = 'firmware_security_report.json'):
        """生成报告"""
        # 按严重程度排序
        self.findings.sort(
            key=lambda x: self.SEVERITY_LEVELS.get(x['severity'], 0),
            reverse=True
        )

        # 统计
        stats = defaultdict(int)
        for finding in self.findings:
            stats[finding['severity']] += 1
            stats[finding['category']] += 1

        report = {
            'title': 'IoT固件安全评估报告',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_findings': len(self.findings),
                'by_severity': dict(stats),
            },
            'findings': self.findings,
            'recommendations': self._get_recommendations(),
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"安全报告已生成: {output_path}")
        self._print_summary(report)

    def _get_recommendations(self) -> List[str]:
        """生成总体建议"""
        recommendations = []

        # 检查是否有默认凭证
        if any(f['category'] == 'default_credential' for f in self.findings):
            recommendations.append(
                "发现默认凭证: 必须修改所有默认密码, 使用强密码策略"
            )

        # 检查是否有硬编码密钥
        if any(f['category'] == 'private_key' for f in self.findings):
            recommendations.append(
                "发现硬编码私钥: 移除固件中的私钥, 使用设备唯一密钥"
            )

        # 检查是否有危险函数
        if any(f['category'] == 'dangerous_function' for f in self.findings):
            recommendations.append(
                "发现危险函数: 替换为安全版本(strcpy→strncpy, "
                "sprintf→snprintf等)"
            )

        # 检查安全编译选项
        if any(f['category'] == 'missing_security_feature'
               for f in self.findings):
            recommendations.append(
                "缺少安全编译选项: 启用NX, PIE, RELRO, "
                "Stack Canary和FORTIFY_SOURCE"
            )

        # 检查调试信息
        if any(f['category'] == 'debug_info' for f in self.findings):
            recommendations.append(
                "发现调试信息: 生产版本应去除调试符号和调试接口"
            )

        if not recommendations:
            recommendations.append("未发现重大安全问题, 建议持续监控")

        return recommendations

    def _print_summary(self, report: dict):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("IoT固件安全评估报告")
        print("=" * 60)
        print(f"生成时间: {report['generated_at']}")
        print(f"发现总数: {report['summary']['total_findings']}")
        print("\n按严重程度:")
        for sev, count in report['summary']['by_severity'].items():
            if sev in self.SEVERITY_LEVELS:
                print(f"  {sev}: {count}")
        print("\n建议:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        print("=" * 60)


# ============================================================
# 主分析器
# ============================================================

class FirmwareAnalyzer:
    """IoT固件分析主工具"""

    def __init__(self, firmware_path: str,
                 output_dir: str = './firmware_analysis'):
        self.firmware_path = firmware_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.unpacker = FirmwareUnpacker(
            os.path.join(output_dir, 'extracted')
        )
        self.scanner = SensitiveInfoScanner()
        self.binary_analyzer = BinaryAnalyzer()
        self.report = SecurityReport()

    def run_full_analysis(self):
        """运行完整分析流程"""
        logger.info("=" * 60)
        logger.info("IoT固件安全分析")
        logger.info("=" * 60)

        # 1. 固件解包
        logger.info("\n[1/5] 固件解包")
        unpack_result = self.unpacker.unpack(self.firmware_path)
        self._report_unpacking(unpack_result)

        # 2. 敏感信息扫描
        logger.info("\n[2/5] 敏感信息扫描")
        extract_dir = os.path.join(self.output_dir, 'extracted')
        if os.path.exists(extract_dir):
            findings = self.scanner.scan_directory(extract_dir)
            self._report_sensitive_info(findings)

        # 3. 二进制分析
        logger.info("\n[3/5] 二进制安全分析")
        self._analyze_binaries(extract_dir)

        # 4. 文件系统权限分析
        logger.info("\n[4/5] 文件系统权限分析")
        self._analyze_permissions(extract_dir)

        # 5. 生成报告
        logger.info("\n[5/5] 生成安全评估报告")
        report_path = os.path.join(self.output_dir,
                                   'firmware_security_report.json')
        self.report.generate(report_path)

        logger.info("\n分析完成!")
        logger.info(f"输出目录: {self.output_dir}")

    def _report_unpacking(self, result: dict):
        """报告解包结果"""
        if result.get('formats'):
            for fmt in result['formats']:
                self.report.add_finding(
                    'INFO', 'firmware_format',
                    f"固件格式: {fmt['format']} "
                    f"({fmt['description']}), 偏移: {fmt['offset']}"
                )

        self.report.add_finding(
            'INFO', 'firmware_info',
            f"固件大小: {result['size']} bytes, "
            f"SHA-256: {result['sha256'][:16]}..."
        )

    def _report_sensitive_info(self, findings: list):
        """报告敏感信息"""
        for finding in findings:
            category = finding['category']
            match = finding.get('match', '')[:100]

            if category in ('private_key', 'certificate'):
                self.report.add_finding(
                    'CRITICAL', category,
                    f"发现{category}: {match}",
                    finding['file'],
                    "移除固件中的密钥/证书, 使用设备唯一密钥"
                )
            elif category == 'default_credential':
                self.report.add_finding(
                    'HIGH', category,
                    f"发现默认凭证: {match}",
                    finding['file'],
                    "修改所有默认密码为强密码"
                )
            elif category in ('password', 'api_key', 'wifi_credentials'):
                self.report.add_finding(
                    'HIGH', category,
                    f"发现硬编码{category}: {match[:50]}",
                    finding['file'],
                    "使用安全的密钥管理, 避免硬编码"
                )
            elif category == 'database':
                self.report.add_finding(
                    'HIGH', category,
                    f"发现数据库连接字符串: {match[:50]}",
                    finding['file'],
                    "移除数据库凭证, 使用安全的配置管理"
                )
            elif category == 'shadow_file':
                self.report.add_finding(
                    'HIGH', category,
                    f"发现密码哈希文件: {match[:50]}",
                    finding['file'],
                    "使用更强的密码哈希(如bcrypt/scrypt)"
                )
            elif category == 'ssh_config':
                self.report.add_finding(
                    'MEDIUM', category,
                    f"SSH不安全配置: {match}",
                    finding['file'],
                    "禁用root登录, 禁用密码认证"
                )

    def _analyze_binaries(self, directory: str):
        """分析二进制文件"""
        elf_count = 0

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)

                try:
                    with open(filepath, 'rb') as f:
                        magic = f.read(4)

                    if magic == b'\x7fELF':
                        elf_count += 1
                        result = self.binary_analyzer.analyze_elf(filepath)

                        # 报告危险函数
                        for func in result.get('dangerous_functions', []):
                            self.report.add_finding(
                                'HIGH', 'dangerous_function',
                                f"危险函数 {func['function']}: "
                                f"{func['risk']}",
                                filepath,
                                f"替换 {func['function']} 为安全版本"
                            )

                        # 报告缺少的安全特性
                        for feature, enabled in result.get(
                            'security_features', {}
                        ).items():
                            if not enabled:
                                self.report.add_finding(
                                    'MEDIUM', 'missing_security_feature',
                                    f"缺少安全特性: "
                                    f"{self.binary_analyzer.SECURITY_FEATURES.get(feature, feature)}",
                                    filepath,
                                    f"启用 {feature} 编译选项"
                                )

                except Exception as e:
                    logger.debug(f"分析失败 {filepath}: {e}")

        logger.info(f"分析了 {elf_count} 个ELF文件")

    def _analyze_permissions(self, directory: str):
        """分析文件权限"""
        world_writable = []
        suid_files = []

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    stat = os.stat(filepath)
                    mode = stat.st_mode

                    # 世界可写文件
                    if mode & 0o002:
                        world_writable.append(filepath)

                    # SUID文件
                    if mode & 0o4000:
                        suid_files.append(filepath)

                except Exception:
                    pass

        for f in world_writable[:20]:
            self.report.add_finding(
                'MEDIUM', 'world_writable',
                f"世界可写文件: {os.path.basename(f)}",
                f,
                "限制文件权限, 移除其他用户写权限"
            )

        for f in suid_files[:20]:
            self.report.add_finding(
                'HIGH', 'suid_binary',
                f"SUID文件: {os.path.basename(f)}",
                f,
                "审查SUID二进制, 移除不必要的SUID位"
            )


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='IoT固件分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 完整分析固件
  python firmware_analysis_tool.py -f firmware.bin

  # 指定输出目录
  python firmware_analysis_tool.py -f firmware.bin -o ./output

  # 仅扫描敏感信息
  python firmware_analysis_tool.py -f firmware.bin --scan-only

  # 比较两个版本
  python firmware_analysis_tool.py --diff old_dir new_dir
        """
    )

    parser.add_argument('-f', '--firmware', help='固件文件路径')
    parser.add_argument('-o', '--output', default='./firmware_analysis',
                        help='输出目录 (默认: ./firmware_analysis)')
    parser.add_argument('--scan-only', action='store_true',
                        help='仅扫描敏感信息')
    parser.add_argument('--diff', nargs=2, metavar=('OLD', 'NEW'),
                        help='比较两个固件版本')

    args = parser.parse_args()

    if args.diff:
        differ = FirmwareDiffer()
        result = differ.compare(args.diff[0], args.diff[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if not args.firmware:
        parser.print_help()
        return

    if not os.path.exists(args.firmware):
        logger.error(f"固件文件不存在: {args.firmware}")
        sys.exit(1)

    analyzer = FirmwareAnalyzer(args.firmware, args.output)

    if args.scan_only:
        # 解包
        unpack_result = analyzer.unpacker.unpack(args.firmware)
        extract_dir = os.path.join(args.output, 'extracted')
        # 扫描
        findings = analyzer.scanner.scan_directory(extract_dir)
        # 生成报告
        for finding in findings:
            analyzer._report_sensitive_info([finding])
        report_path = os.path.join(args.output,
                                   'scan_report.json')
        analyzer.report.generate(report_path)
    else:
        analyzer.run_full_analysis()


if __name__ == '__main__':
    main()
