#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevSecOps 安全流水线工具包 (DevSecOps Pipeline Toolkit)
======================================================

功能说明：
    本工具包实现了一套完整的 DevSecOps 安全扫描流水线工具，包含：
    1. SAST 结果解析器 - 解析 SonarQube / Semgrep JSON 报告
    2. 依赖漏洞扫描器 - 检查 requirements.txt / package.json 中的已知漏洞
    3. Dockerfile 安全检查器 - 检查特权模式、硬编码密钥、不安全基础镜像
    4. Terraform 安全审计器 - 检查安全组规则开放、IAM 过权、加密缺失
    5. 安全门禁评估器 - 根据扫描结果决定是否阻断流水线
    6. 漏洞报告聚合器 - 合并多个工具的安全发现，生成统一报告

使用方式：
    python devsecops_pipeline.py --mode scan --path /project/path
    python devsecops_pipeline.py --mode parse --sast semgrep-report.json
    python devsecops_pipeline.py --mode gate --reports-dir ./reports/
    python devsecops_pipeline.py --mode aggregate --reports-dir ./reports/

作者：DevSecOps 学习工具
版本：1.0.0
"""

import json
import os
import re
import sys
import argparse
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# 第一部分：数据模型定义
# ============================================================

class Severity(Enum):
    """安全发现严重程度枚举"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """从字符串转换为枚举值（不区分大小写）"""
        mapping = {
            "critical": cls.CRITICAL,
            "high": cls.HIGH,
            "medium": cls.MEDIUM,
            "low": cls.LOW,
            "info": cls.INFO,
            "error": cls.HIGH,       # Semgrep ERROR 映射为 HIGH
            "warning": cls.MEDIUM,    # Semgrep WARNING 映射为 MEDIUM
            "blocker": cls.CRITICAL,  # SonarQube Blocker 映射为 CRITICAL
            "major": cls.HIGH,        # SonarQube Major 映射为 HIGH
            "minor": cls.LOW,         # SonarQube Minor 映射为 LOW
        }
        return mapping.get(value.lower(), cls.INFO)


@dataclass
class SecurityFinding:
    """
    安全发现数据类 - 统一表示各工具发现的安全问题

    属性说明：
        tool: 发现该问题的安全工具名称
        rule_id: 规则 ID
        severity: 严重程度
        title: 问题标题
        description: 问题描述
        file_path: 涉及的文件路径
        line_number: 行号
        category: 漏洞类别（如 SQL注入、XSS 等）
        cwe: CWE 编号
        remediation: 修复建议
        confidence: 置信度（HIGH/MEDIUM/LOW）
        evidence: 证据（代码片段等）
    """
    tool: str
    rule_id: str
    severity: Severity
    title: str
    description: str = ""
    file_path: str = ""
    line_number: int = 0
    category: str = ""
    cwe: str = ""
    remediation: str = ""
    confidence: str = "MEDIUM"
    evidence: str = ""


@dataclass
class GateResult:
    """
    安全门禁评估结果

    属性说明：
        passed: 是否通过门禁
        total_findings: 总发现数
        severity_counts: 各严重程度的数量统计
        blocking_findings: 阻断流水线的发现列表
        warnings: 警告信息列表
        summary: 评估总结
    """
    passed: bool
    total_findings: int
    severity_counts: Dict[str, int]
    blocking_findings: List[SecurityFinding] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    summary: str = ""


# ============================================================
# 第二部分：SAST 结果解析器
# ============================================================

class SASTParser:
    """
    SAST 结果解析器

    支持解析以下工具的 JSON 格式报告：
    - SonarQube（静态代码质量与安全分析）
    - Semgrep（轻量级模式匹配扫描器）
    - Bandit（Python 专用安全扫描器）
    """

    @staticmethod
    def parse_semgrep(report_path: str) -> List[SecurityFinding]:
        """
        解析 Semgrep JSON 报告

        Semgrep 报告结构：
        {
            "results": [
                {
                    "check_id": "python.django.security.injection.sql",
                    "path": "src/views.py",
                    "start": {"line": 42, "col": 10},
                    "extra": {
                        "message": "检测到SQL注入",
                        "severity": "ERROR",
                        "metadata": {
                            "cwe": "CWE-89",
                            "owasp": "A03:2021"
                        }
                    }
                }
            ]
        }

        参数：
            report_path: Semgrep JSON 报告文件路径
        返回：
            标准化的安全发现列表
        """
        findings = []

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[错误] 无法读取 Semgrep 报告: {e}")
            return findings

        # 遍历 Semgrep 扫描结果
        for result in data.get('results', []):
            extra = result.get('extra', {})
            metadata = extra.get('metadata', {})

            finding = SecurityFinding(
                tool='semgrep',
                rule_id=result.get('check_id', 'unknown'),
                severity=Severity.from_string(extra.get('severity', 'INFO')),
                title=result.get('check_id', '').split('.')[-1],
                description=extra.get('message', '无描述'),
                file_path=result.get('path', ''),
                line_number=result.get('start', {}).get('line', 0),
                category=metadata.get('category', ''),
                cwe=metadata.get('cwe', ''),
                remediation=metadata.get('fix', ''),
                confidence=metadata.get('confidence', 'MEDIUM'),
                evidence=extra.get('lines', ''),
            )
            findings.append(finding)

        return findings

    @staticmethod
    def parse_sonarqube(report_path: str) -> List[SecurityFinding]:
        """
        解析 SonarQube JSON 报告

        SonarQube 报告结构：
        {
            "issues": [
                {
                    "rule": "python:S2077",
                    "severity": "CRITICAL",
                    "type": "VULNERABILITY",
                    "component": "project:src/main.py",
                    "line": 25,
                    "message": "使用不安全的哈希算法",
                    "textRange": {"startLine": 25}
                }
            ]
        }

        参数：
            report_path: SonarQube JSON 报告文件路径
        返回：
            标准化的安全发现列表
        """
        findings = []

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[错误] 无法读取 SonarQube 报告: {e}")
            return findings

        # SonarQube 的 issues 列表
        for issue in data.get('issues', []):
            # 只关注安全漏洞类型的问题
            if issue.get('type') not in ('VULNERABILITY', 'SECURITY_HOTSPOT', 'BUG'):
                continue

            # 从 component 中提取文件路径
            component = issue.get('component', '')
            file_path = component.split(':')[-1] if ':' in component else component

            finding = SecurityFinding(
                tool='sonarqube',
                rule_id=issue.get('rule', 'unknown'),
                severity=Severity.from_string(issue.get('severity', 'INFO')),
                title=issue.get('rule', ''),
                description=issue.get('message', '无描述'),
                file_path=file_path,
                line_number=issue.get('line', issue.get('textRange', {}).get('startLine', 0)),
                category='vulnerability' if issue.get('type') == 'VULNERABILITY' else 'security_hotspot',
                remediation=issue.get('effort', ''),
            )
            findings.append(finding)

        return findings

    @staticmethod
    def parse_bandit(report_path: str) -> List[SecurityFinding]:
        """
        解析 Bandit JSON 报告

        Bandit 报告结构：
        {
            "results": [
                {
                    "test_id": "B608",
                    "test_name": "hardcoded_sql_expresssion",
                    "issue_severity": "HIGH",
                    "issue_confidence": "MEDIUM",
                    "issue_text": "Possible SQL injection vector",
                    "filename": "src/db.py",
                    "line_number": 15,
                    "issue_cwe": {"id": 89, "link": "..."}
                }
            ]
        }

        参数：
            report_path: Bandit JSON 报告文件路径
        返回：
            标准化的安全发现列表
        """
        findings = []

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[错误] 无法读取 Bandit 报告: {e}")
            return findings

        for result in data.get('results', []):
            cwe_info = result.get('issue_cwe', {})

            finding = SecurityFinding(
                tool='bandit',
                rule_id=result.get('test_id', 'unknown'),
                severity=Severity.from_string(result.get('issue_severity', 'INFO')),
                title=result.get('test_name', ''),
                description=result.get('issue_text', '无描述'),
                file_path=result.get('filename', ''),
                line_number=result.get('line_number', 0),
                category=result.get('test_name', ''),
                cwe=f"CWE-{cwe_info.get('id', '')}" if cwe_info.get('id') else '',
                confidence=result.get('issue_confidence', 'MEDIUM'),
            )
            findings.append(finding)

        return findings


# ============================================================
# 第三部分：依赖漏洞扫描器
# ============================================================

class DependencyScanner:
    """
    依赖漏洞扫描器

    扫描项目依赖文件中的已知漏洞：
    - Python: requirements.txt
    - Node.js: package.json / package-lock.json

    使用内置的已知漏洞数据库（演示用，生产环境应接入 NVD/OSV API）
    """

    # 已知漏洞数据库（演示数据，实际应使用在线 API 或本地 CVE 数据库）
    KNOWN_VULNERABILITIES = {
        # Python 包已知漏洞
        "django": [
            {"version_range": "<3.2.16", "cve": "CVE-2022-36359", "severity": "HIGH",
             "description": "Django 目录遍历漏洞", "fixed_version": "3.2.16"},
            {"version_range": "<4.0.8", "cve": "CVE-2022-34265", "severity": "CRITICAL",
             "description": "Django SQL注入漏洞", "fixed_version": "4.0.8"},
        ],
        "flask": [
            {"version_range": "<2.2.5", "cve": "CVE-2023-30861", "severity": "HIGH",
             "description": "Flask Cookie 安全问题", "fixed_version": "2.2.5"},
        ],
        "requests": [
            {"version_range": "<2.31.0", "cve": "CVE-2023-32681", "severity": "MEDIUM",
             "description": "Requests 代理认证信息泄露", "fixed_version": "2.31.0"},
            {"version_range": "<2.20.0", "cve": "CVE-2018-18074", "severity": "HIGH",
             "description": "Requests 认证信息泄露", "fixed_version": "2.20.0"},
        ],
        "pyyaml": [
            {"version_range": "<5.4", "cve": "CVE-2020-14343", "severity": "HIGH",
             "description": "PyYAML 任意代码执行", "fixed_version": "5.4"},
        ],
        "jinja2": [
            {"version_range": "<3.1.3", "cve": "CVE-2024-22195", "severity": "HIGH",
             "description": "Jinja2 XSS 漏洞", "fixed_version": "3.1.3"},
        ],
        "cryptography": [
            {"version_range": "<41.0.2", "cve": "CVE-2023-38325", "severity": "HIGH",
             "description": "Cryptography NULL指针解引用", "fixed_version": "41.0.2"},
        ],
        # Node.js 包已知漏洞
        "lodash": [
            {"version_range": "<4.17.21", "cve": "CVE-2021-23337", "severity": "HIGH",
             "description": "Lodash 命令注入", "fixed_version": "4.17.21"},
            {"version_range": "<4.17.20", "cve": "CVE-2020-8203", "severity": "HIGH",
             "description": "Lodash 原型链污染", "fixed_version": "4.17.20"},
        ],
        "express": [
            {"version_range": "<4.17.3", "cve": "CVE-2022-24999", "severity": "HIGH",
             "description": "Express 原型链污染", "fixed_version": "4.17.3"},
        ],
        "axios": [
            {"version_range": "<0.21.2", "cve": "CVE-2021-3749", "severity": "HIGH",
             "description": "Axios ReDoS 漏洞", "fixed_version": "0.21.2"},
        ],
        "minimist": [
            {"version_range": "<1.2.6", "cve": "CVE-2021-44906", "severity": "CRITICAL",
             "description": "Minimist 原型链污染", "fixed_version": "1.2.6"},
        ],
    }

    @staticmethod
    def _parse_version(version_str: str) -> Tuple[int, ...]:
        """将版本字符串解析为可比较的元组，如 '3.2.1' -> (3, 2, 1)"""
        # 移除版本字符串中的非数字前缀（如 v1.0.0 -> 1.0.0）
        version_str = re.sub(r'^[^0-9]+', '', str(version_str))
        # 按点分割并提取数字部分
        parts = re.findall(r'\d+', version_str)
        return tuple(int(p) for p in parts) if parts else (0,)

    @staticmethod
    def _is_vulnerable(version: str, version_range: str) -> bool:
        """
        检查版本是否在漏洞范围内

        参数：
            version: 实际安装的版本号
            version_range: 漏洞影响的版本范围，如 "<3.2.16"
        返回：
            True 如果版本在漏洞范围内
        """
        installed = DependencyScanner._parse_version(version)
        # 解析范围表达式（目前支持 < 和 <=）
        if version_range.startswith('<='):
            threshold = DependencyScanner._parse_version(version_range[2:])
            return installed <= threshold
        elif version_range.startswith('<'):
            threshold = DependencyScanner._parse_version(version_range[1:])
            return installed < threshold
        elif version_range.startswith('>='):
            threshold = DependencyScanner._parse_version(version_range[2:])
            return installed >= threshold
        # 默认：精确匹配
        threshold = DependencyScanner._parse_version(version_range)
        return installed == threshold

    @classmethod
    def scan_requirements_txt(cls, file_path: str) -> List[SecurityFinding]:
        """
        扫描 Python requirements.txt 文件中的已知漏洞

        requirements.txt 格式示例：
            django==3.2.0
            flask>=2.0.0
            requests~=2.25.0

        参数：
            file_path: requirements.txt 文件路径
        返回：
            发现的漏洞列表
        """
        findings = []

        if not os.path.exists(file_path):
            print(f"[警告] requirements.txt 不存在: {file_path}")
            return findings

        # 正则表达式匹配 Python 包名和版本号
        # 支持格式：package==1.0.0, package>=1.0.0, package~=1.0, package
        pattern = re.compile(r'^([a-zA-Z0-9_-]+)\s*([><=~!]+[0-9.]+)?')

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳过注释行和空行
                if not line or line.startswith('#') or line.startswith('-'):
                    continue

                match = pattern.match(line)
                if not match:
                    continue

                package_name = match.group(1).lower()
                version_spec = match.group(2)

                # 提取实际版本号
                if version_spec:
                    # 从版本规范中提取纯版本号
                    version = re.sub(r'[><=~!]+', '', version_spec)
                else:
                    version = '0.0.0'  # 未指定版本，视为最旧版本

                # 检查已知漏洞
                if package_name in cls.KNOWN_VULNERABILITIES:
                    for vuln in cls.KNOWN_VULNERABILITIES[package_name]:
                        if cls._is_vulnerable(version, vuln['version_range']):
                            finding = SecurityFinding(
                                tool='dependency-scanner',
                                rule_id=vuln['cve'],
                                severity=Severity.from_string(vuln['severity']),
                                title=f"{package_name} 已知漏洞: {vuln['cve']}",
                                description=vuln['description'],
                                file_path=file_path,
                                line_number=line_num,
                                category='dependency_vulnerability',
                                cwe='CWE-1035',  # 使用过时依赖
                                remediation=f"升级到 {vuln['fixed_version']} 或更高版本",
                                confidence='HIGH',
                                evidence=f"{package_name}=={version} (影响范围: {vuln['version_range']})",
                            )
                            findings.append(finding)

        return findings

    @classmethod
    def scan_package_json(cls, file_path: str) -> List[SecurityFinding]:
        """
        扫描 Node.js package.json 文件中的已知漏洞

        package.json 中的 dependencies 格式：
        {
            "dependencies": {
                "lodash": "4.17.15",
                "express": "^4.17.1"
            }
        }

        参数：
            file_path: package.json 文件路径
        返回：
            发现的漏洞列表
        """
        findings = []

        if not os.path.exists(file_path):
            print(f"[警告] package.json 不存在: {file_path}")
            return findings

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[错误] package.json 解析失败: {e}")
            return findings

        # 检查 dependencies 和 devDependencies
        for dep_type in ['dependencies', 'devDependencies']:
            dependencies = data.get(dep_type, {})
            for package_name, version_spec in dependencies.items():
                package_name = package_name.lower()

                # 从版本规范中提取纯版本号
                # 支持 ^1.0.0, ~1.0.0, 1.0.0, >=1.0.0 等格式
                version = re.sub(r'[\^~>=<]+', '', str(version_spec))

                # 检查已知漏洞
                if package_name in cls.KNOWN_VULNERABILITIES:
                    for vuln in cls.KNOWN_VULNERABILITIES[package_name]:
                        if cls._is_vulnerable(version, vuln['version_range']):
                            finding = SecurityFinding(
                                tool='dependency-scanner',
                                rule_id=vuln['cve'],
                                severity=Severity.from_string(vuln['severity']),
                                title=f"{package_name} 已知漏洞: {vuln['cve']}",
                                description=vuln['description'],
                                file_path=file_path,
                                category='dependency_vulnerability',
                                cwe='CWE-1035',
                                remediation=f"升级到 {vuln['fixed_version']} 或更高版本",
                                confidence='HIGH',
                                evidence=f"{package_name}@{version} (影响范围: {vuln['version_range']})",
                            )
                            findings.append(finding)

        return findings


# ============================================================
# 第四部分：Dockerfile 安全检查器
# ============================================================

class DockerfileChecker:
    """
    Dockerfile 安全检查器

    检查 Dockerfile 中的常见安全配置问题：
    - 特权模式运行
    - 硬编码密钥/密码
    - 不安全的基础镜像
    - root 用户运行
    - 缺少健康检查
    - 使用 latest 标签
    - 不安全的 apt-get 使用
    """

    # 不安全的基础镜像列表
    INSECURE_BASE_IMAGES = {
        'ubuntu:latest', 'debian:latest', 'centos:latest',
        'python:latest', 'node:latest', 'ruby:latest',
        'golang:latest', 'java:latest', 'openjdk:latest',
    }

    # 敏感信息关键词模式
    SECRET_PATTERNS = [
        (re.compile(r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
         "硬编码密码"),
        (re.compile(r'(?:secret|api_key|apikey|access_key)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
         "硬编码密钥/API Key"),
        (re.compile(r'(?:token|auth_token)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
         "硬编码 Token"),
        (re.compile(r'AKIA[0-9A-Z]{16}', re.IGNORECASE),
         "AWS 访问密钥泄露"),
        (re.compile(r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----'),
         "私钥泄露"),
        (re.compile(r'(?:mysql|postgres)://[^:]+:[^@]+@'),
         "数据库连接字符串中的密码"),
    ]

    @classmethod
    def check(cls, dockerfile_path: str) -> List[SecurityFinding]:
        """
        执行 Dockerfile 安全检查

        参数：
            dockerfile_path: Dockerfile 文件路径
        返回：
            发现的安全问题列表
        """
        findings = []

        if not os.path.exists(dockerfile_path):
            print(f"[警告] Dockerfile 不存在: {dockerfile_path}")
            return findings

        # 读取 Dockerfile 内容
        with open(dockerfile_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 检查项标记
        has_user_directive = False
        has_healthcheck = False
        has_non_root_user = False
        base_image = ""
        base_image_line = 0

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 跳过注释和空行
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # 提取指令和参数
            parts = line_stripped.split(None, 1)
            instruction = parts[0].upper() if parts else ""
            args = parts[1] if len(parts) > 1 else ""

            # ========== 检查1：不安全基础镜像 ==========
            if instruction == 'FROM':
                base_image = args.split()[0] if args else ""
                base_image_line = line_num
                # 检查是否使用 latest 标签
                if base_image.endswith(':latest') or ':' not in base_image:
                    findings.append(SecurityFinding(
                        tool='dockerfile-checker',
                        rule_id='DOCKERFILE-001',
                        severity=Severity.MEDIUM,
                        title="使用不稳定的镜像标签",
                        description=f"基础镜像 {base_image} 使用了 latest 标签或未指定版本，"
                                   f"可能导致构建不可重现",
                        file_path=dockerfile_path,
                        line_number=line_num,
                        category='image_tag',
                        remediation="使用固定版本标签，如 python:3.11-slim",
                    ))
                # 检查已知不安全镜像
                if base_image.lower() in cls.INSECURE_BASE_IMAGES:
                    findings.append(SecurityFinding(
                        tool='dockerfile-checker',
                        rule_id='DOCKERFILE-002',
                        severity=Severity.LOW,
                        title="使用不安全的基础镜像",
                        description=f"基础镜像 {base_image} 在不安全镜像列表中",
                        file_path=dockerfile_path,
                        line_number=line_num,
                        category='base_image',
                        remediation="使用官方精简镜像（slim/alpine）",
                    ))

            # ========== 检查2：root 用户运行 ==========
            if instruction == 'USER':
                has_user_directive = True
                user_spec = args.split(':')[0]
                if user_spec.lower() not in ('root', '0'):
                    has_non_root_user = True

            # ========== 检查3：特权模式 ==========
            if instruction in ('RUN', 'CMD', 'ENTRYPOINT'):
                # 检查是否使用 --privileged（虽然在 Dockerfile 中不应该出现）
                if '--privileged' in args:
                    findings.append(SecurityFinding(
                        tool='dockerfile-checker',
                        rule_id='DOCKERFILE-003',
                        severity=Severity.HIGH,
                        title="检测到特权模式",
                        description="Dockerfile 中使用了 --privileged 标志，可能导致容器逃逸",
                        file_path=dockerfile_path,
                        line_number=line_num,
                        category='privileged_mode',
                        remediation="移除 --privileged 标志，使用最小权限原则",
                    ))

            # ========== 检查4：硬编码密钥 ==========
            for pattern, description in cls.SECRET_PATTERNS:
                matches = pattern.findall(line_stripped)
                if matches:
                    findings.append(SecurityFinding(
                        tool='dockerfile-checker',
                        rule_id='DOCKERFILE-004',
                        severity=Severity.CRITICAL,
                        title=f"检测到{description}",
                        description=f"在 Dockerfile 第 {line_num} 行发现疑似{description}",
                        file_path=dockerfile_path,
                        line_number=line_num,
                        category='hardcoded_secret',
                        cwe='CWE-798',
                        remediation="使用环境变量或密钥管理工具（如 Vault）传递敏感信息",
                        confidence='HIGH',
                        evidence=line_stripped[:100],  # 截断显示
                    ))

            # ========== 检查5：不安全 apt-get 使用 ==========
            if 'apt-get' in line_stripped:
                # 检查 apt-get install 后没有 --no-install-recommends
                if 'install' in line_stripped and '--no-install-recommends' not in line_stripped:
                    findings.append(SecurityFinding(
                        tool='dockerfile-checker',
                        rule_id='DOCKERFILE-005',
                        severity=Severity.LOW,
                        title="apt-get install 未使用 --no-install-recommends",
                        description="未使用 --no-install-recommends 会安装不必要的推荐包，"
                                   "增加攻击面",
                        file_path=dockerfile_path,
                        line_number=line_num,
                        category='package_install',
                        remediation="添加 --no-install-recommends 参数",
                    ))
                # 检查 apt-get 后没有清理
                if 'install' in line_stripped and 'rm -rf' not in lines[line_num] and \
                   'autoremove' not in lines[line_num] if line_num < len(lines) else True:
                    pass  # 需要更复杂的行上下文分析

            # ========== 检查6：健康检查 ==========
            if instruction == 'HEALTHCHECK':
                has_healthcheck = True

            # ========== 检查7：ADD 指令（不安全） ==========
            if instruction == 'ADD' and ('://' in args or '*' in args):
                findings.append(SecurityFinding(
                    tool='dockerfile-checker',
                    rule_id='DOCKERFILE-006',
                    severity=Severity.LOW,
                    title="使用 ADD 指令下载远程文件",
                    description="ADD 指令可从远程 URL 下载文件，存在安全风险。"
                               "应使用 COPY + 手动下载",
                    file_path=dockerfile_path,
                    line_number=line_num,
                    category='add_instruction',
                    remediation="使用 COPY 替代 ADD",
                ))

            # ========== 检查8：apt-get update 与 install 分离 ==========
            if 'apt-get update' in line_stripped and 'install' not in line_stripped:
                # 单独的 apt-get update 会缓存包索引，导致缓存失效问题
                if 'rm -rf' not in line_stripped:
                    findings.append(SecurityFinding(
                        tool='dockerfile-checker',
                        rule_id='DOCKERFILE-007',
                        severity=Severity.LOW,
                        title="apt-get update 未在同一层清理缓存",
                        description="单独的 apt-get update 会增加镜像层大小并缓存包索引",
                        file_path=dockerfile_path,
                        line_number=line_num,
                        category='layer_cache',
                        remediation="将 apt-get update 和 install 合并在同一 RUN 指令中，"
                                   "并在末尾清理缓存",
                    ))

        # ========== 检查9：缺少 USER 指令（以 root 运行） ==========
        if not has_non_root_user:
            findings.append(SecurityFinding(
                tool='dockerfile-checker',
                rule_id='DOCKERFILE-008',
                severity=Severity.HIGH,
                title="容器以 root 用户运行",
                description="Dockerfile 未指定非 root 用户，容器将以 root 权限运行",
                file_path=dockerfile_path,
                line_number=0,
                category='root_user',
                cwe='CWE-250',
                remediation="添加 USER 指令指定非 root 用户运行",
            ))

        # ========== 检查10：缺少健康检查 ==========
        if not has_healthcheck:
            findings.append(SecurityFinding(
                tool='dockerfile-checker',
                rule_id='DOCKERFILE-009',
                severity=Severity.LOW,
                title="缺少 HEALTHCHECK 指令",
                description="Dockerfile 未定义健康检查，容器编排系统无法检测应用健康状态",
                file_path=dockerfile_path,
                line_number=0,
                category='healthcheck',
                remediation="添加 HEALTHCHECK 指令定义健康检查",
            ))

        return findings


# ============================================================
# 第五部分：Terraform 安全审计器
# ============================================================

class TerraformAuditor:
    """
    Terraform 安全审计器

    检查 Terraform 配置文件中的常见安全问题：
    - 安全组规则过于开放（0.0.0.0/0）
    - IAM 策略权限过大（Action: *）
    - 存储服务未启用加密
    - 数据库禁止公网访问
    - 硬编码密钥
    """

    @classmethod
    def check(cls, terraform_dir: str) -> List[SecurityFinding]:
        """
        扫描 Terraform 配置目录

        参数：
            terraform_dir: Terraform 配置文件目录路径
        返回：
            发现的安全问题列表
        """
        findings = []

        if not os.path.exists(terraform_dir):
            print(f"[警告] Terraform 目录不存在: {terraform_dir}")
            return findings

        # 递归查找所有 .tf 文件
        tf_files = []
        for root, dirs, files in os.walk(terraform_dir):
            for file in files:
                if file.endswith('.tf'):
                    tf_files.append(os.path.join(root, file))

        for tf_file in tf_files:
            file_findings = cls._check_file(tf_file)
            findings.extend(file_findings)

        return findings

    @classmethod
    def _check_file(cls, file_path: str) -> List[SecurityFinding]:
        """检查单个 Terraform 文件"""
        findings = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # 使用正则表达式匹配 Terraform 资源块
        # 提取资源类型和名称
        resource_pattern = re.compile(r'resource\s+"([^"]+)"\s+"([^"]+)"')
        current_resource_type = ""
        current_resource_name = ""

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 匹配资源声明
            res_match = resource_pattern.search(line)
            if res_match:
                current_resource_type = res_match.group(1)
                current_resource_name = res_match.group(2)
                continue

            # ========== 检查1：安全组规则 0.0.0.0/0 ==========
            if 'cidr_blocks' in line and '0.0.0.0/0' in line:
                # 判断端口范围
                port = "未知"
                # 向上查找 from_port
                for i in range(line_num - 2, max(line_num - 10, 0), -1):
                    if i < len(lines):
                        prev_line = lines[i - 1]
                        if 'from_port' in prev_line:
                            port_match = re.search(r'from_port\s*=\s*(\d+)', prev_line)
                            if port_match:
                                port = port_match.group(1)
                            break

                severity = Severity.HIGH if port in ('22', '3389', '3306', '5432') else Severity.MEDIUM
                port_name = {'22': 'SSH', '3389': 'RDP', '3306': 'MySQL',
                             '5432': 'PostgreSQL'}.get(port, f'端口{port}')

                findings.append(SecurityFinding(
                    tool='terraform-auditor',
                    rule_id='TF-AWS-001',
                    severity=severity,
                    title=f"安全组规则对全网开放: {port_name}",
                    description=f"安全组规则允许 0.0.0.0/0 访问 {port_name} 端口，"
                               f"可能导致未授权访问",
                    file_path=file_path,
                    line_number=line_num,
                    category='open_security_group',
                    cwe='CWE-284',
                    remediation=f"限制 {port_name} 端口的访问来源 IP",
                ))

            # ========== 检查2：IAM 策略权限过大 ==========
            if 'action' in line.lower() and '*' in line:
                # 排除资源 ARN 中的通配符（如 s3:::bucket/*）
                if 'Action' in line or 'action' in line:
                    # 检查是否是 Action 中的通配符
                    if re.search(r'action\s*=\s*["\']\*["\']', line, re.IGNORECASE) or \
                       re.search(r'action\s*=\s*\[.*"\*".*\]', line, re.IGNORECASE):
                        findings.append(SecurityFinding(
                            tool='terraform-auditor',
                            rule_id='TF-AWS-002',
                            severity=Severity.CRITICAL,
                            title="IAM 策略使用通配符权限",
                            description="IAM 策略中 Action 使用了通配符 *，授予了过大权限",
                            file_path=file_path,
                            line_number=line_num,
                            category='iam_overprivileged',
                            cwe='CWE-269',
                            remediation="使用最小权限原则，仅授予必要的 Action",
                        ))

            # ========== 检查3：Resource 通配符 ==========
            if 'resource' in line.lower() and '"*"' in line and 'arn' not in line.lower():
                if re.search(r'resource\s*=\s*["\']\*["\']', line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        tool='terraform-auditor',
                        rule_id='TF-AWS-003',
                        severity=Severity.HIGH,
                        title="IAM 策略 Resource 使用通配符",
                        description="IAM 策略中 Resource 使用了通配符 *，可访问所有资源",
                        file_path=file_path,
                        line_number=line_num,
                        category='iam_overprivileged',
                        cwe='CWE-269',
                        remediation="指定具体的资源 ARN",
                    ))

            # ========== 检查4：存储未加密 ==========
            if 'storage_encrypted' in line and 'false' in line.lower():
                findings.append(SecurityFinding(
                    tool='terraform-auditor',
                    rule_id='TF-AWS-004',
                    severity=Severity.HIGH,
                    title="数据库存储未加密",
                    description="数据库实例 storage_encrypted 设置为 false，数据未加密存储",
                    file_path=file_path,
                    line_number=line_num,
                    category='encryption_disabled',
                    cwe='CWE-311',
                    remediation="设置 storage_encrypted = true",
                ))

            # ========== 检查5：S3 ACL public-read ==========
            if 'acl' in line and ('public-read' in line or 'public-read-write' in line):
                findings.append(SecurityFinding(
                    tool='terraform-auditor',
                    rule_id='TF-AWS-005',
                    severity=Severity.CRITICAL,
                    title="S3 存储桶公开访问",
                    description="S3 存储桶 ACL 设置为 public-read，允许任何人读取内容",
                    file_path=file_path,
                    line_number=line_num,
                    category='public_storage',
                    cwe='CWE-200',
                    remediation="设置 acl 为 private，并启用 Block Public Access",
                ))

            # ========== 检查6：数据库公网可访问 ==========
            if 'publicly_accessible' in line and 'true' in line.lower():
                findings.append(SecurityFinding(
                    tool='terraform-auditor',
                    rule_id='TF-AWS-006',
                    severity=Severity.HIGH,
                    title="数据库公网可访问",
                    description="数据库实例 publicly_accessible 设置为 true，暴露在公网",
                    file_path=file_path,
                    line_number=line_num,
                    category='public_database',
                    cwe='CWE-284',
                    remediation="设置 publicly_accessible = false",
                ))

            # ========== 检查7：硬编码密钥 ==========
            secret_patterns = [
                (r'(?:password|secret|token|api_key)\s*=\s*["\'][^"\']{8,}["\']', "硬编码密钥"),
                (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
            ]
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE) and 'var.' not in line and \
                   'data.' not in line and '${' not in line:
                    findings.append(SecurityFinding(
                        tool='terraform-auditor',
                        rule_id='TF-AWS-007',
                        severity=Severity.CRITICAL,
                        title=f"检测到{desc}",
                        description=f"Terraform 配置中检测到{desc}",
                        file_path=file_path,
                        line_number=line_num,
                        category='hardcoded_secret',
                        cwe='CWE-798',
                        remediation="使用变量引用或密钥管理服务（Vault/KMS）",
                        confidence='HIGH',
                    ))

            # ========== 检查8：缺少版本控制（S3） ==========
            if 'aws_s3_bucket' in lines[max(0, line_num - 5):line_num + 1][0] if line_num > 0 else False:
                # 检查 S3 桶是否启用了版本控制
                pass  # 需要更复杂的块级分析

        return findings


# ============================================================
# 第六部分：安全门禁评估器
# ============================================================

class SecurityGate:
    """
    安全门禁评估器

    根据安全扫描结果评估是否应该阻断流水线。
    支持可配置的严重程度阈值和自定义规则。
    """

    # 默认门禁策略：各严重程度的最大允许数量
    DEFAULT_POLICY = {
        'CRITICAL': 0,   # Critical 漏洞必须为 0（阻断）
        'HIGH': 0,        # High 漏洞必须为 0（阻断）
        'MEDIUM': 10,     # Medium 漏洞允许 10 个以内
        'LOW': 50,        # Low 漏洞允许 50 个以内
        'INFO': 999,      # Info 不阻断
    }

    def __init__(self, policy: Optional[Dict[str, int]] = None,
                 fail_level: str = 'high'):
        """
        初始化安全门禁评估器

        参数：
            policy: 自定义门禁策略，格式为 {severity: max_count}
            fail_level: 阻断级别，'critical' 仅阻断 Critical，'high' 阻断 Critical+High
        """
        self.policy = policy or self.DEFAULT_POLICY.copy()
        self.fail_level = fail_level.upper()

        # 根据阻断级别调整策略
        if fail_level.lower() == 'critical':
            # 仅 Critical 阻断，High 也允许
            self.policy['CRITICAL'] = 0
            self.policy['HIGH'] = 999
        elif fail_level.lower() == 'high':
            self.policy['CRITICAL'] = 0
            self.policy['HIGH'] = 0

    def evaluate(self, findings: List[SecurityFinding]) -> GateResult:
        """
        评估安全门禁

        参数：
            findings: 所有工具的安全发现列表
        返回：
            门禁评估结果
        """
        # 统计各严重程度的数量
        severity_counts = {s.value: 0 for s in Severity}
        blocking_findings = []

        for finding in findings:
            sev = finding.severity.value
            if sev in severity_counts:
                severity_counts[sev] += 1

            # 判断是否为阻断项
            max_allowed = self.policy.get(sev, 999)
            if severity_counts[sev] > max_allowed:
                blocking_findings.append(finding)

        # 判断门禁是否通过
        passed = True
        warnings = []

        for severity_str, count in severity_counts.items():
            max_allowed = self.policy.get(severity_str, 999)
            if count > max_allowed:
                passed = False
                warnings.append(
                    f"[阻断] {severity_str} 级别发现 {count} 个，"
                    f"超过阈值 {max_allowed}"
                )
            elif count > 0:
                warnings.append(
                    f"[警告] {severity_str} 级别发现 {count} 个"
                    f"（阈值 {max_allowed}）"
                )

        # 生成汇总信息
        summary = self._generate_summary(findings, severity_counts, passed)

        return GateResult(
            passed=passed,
            total_findings=len(findings),
            severity_counts=severity_counts,
            blocking_findings=blocking_findings,
            warnings=warnings,
            summary=summary,
        )

    @staticmethod
    def _generate_summary(findings: List[SecurityFinding],
                          counts: Dict[str, int],
                          passed: bool) -> str:
        """生成门禁评估汇总信息"""
        status = "通过" if passed else "未通过"
        summary = (
            f"安全门禁评估结果: {status}\n"
            f"总发现数: {len(findings)}\n"
            f"  Critical: {counts['CRITICAL']}\n"
            f"  High:     {counts['HIGH']}\n"
            f"  Medium:   {counts['MEDIUM']}\n"
            f"  Low:      {counts['LOW']}\n"
            f"  Info:     {counts['INFO']}\n"
        )

        if not passed:
            # 列出阻断项的前5个
            blocking = [f for f in findings
                        if f.severity in (Severity.CRITICAL, Severity.HIGH)]
            if blocking:
                summary += f"\n阻断项（前5个）:\n"
                for f in blocking[:5]:
                    summary += (
                        f"  [{f.severity.value}] {f.tool}: {f.title}\n"
                        f"    文件: {f.file_path}:{f.line_number}\n"
                        f"    修复: {f.remediation}\n"
                    )

        return summary

    def print_result(self, result: GateResult):
        """打印门禁评估结果"""
        print("\n" + "=" * 70)
        print("                    安全门禁评估报告")
        print("=" * 70)
        print(result.summary)
        print("-" * 70)

        if result.warnings:
            for warning in result.warnings:
                print(f"  {warning}")

        print("=" * 70)
        status = "[PASSED] 安全门禁通过，可以继续部署" if result.passed else \
                 "[BLOCKED] 安全门禁未通过，流水线被阻断"
        print(f"\n  {status}")
        print("=" * 70)


# ============================================================
# 第七部分：漏洞报告聚合器
# ============================================================

class ReportAggregator:
    """
    漏洞报告聚合器

    合并多个安全工具的扫描结果，生成统一的安全发现报告。
    支持去重、分类统计和多种输出格式。
    """

    def __init__(self):
        self.findings: List[SecurityFinding] = []

    def add_findings(self, findings: List[SecurityFinding]):
        """添加安全发现列表"""
        self.findings.extend(findings)

    def add_from_json(self, report_path: str, tool: str):
        """
        从 JSON 报告文件添加发现

        参数：
            report_path: JSON 报告文件路径
            tool: 工具名称（semgrep/sonarqube/bandit/trivy）
        """
        parser = SASTParser()
        if tool == 'semgrep':
            findings = parser.parse_semgrep(report_path)
        elif tool == 'sonarqube':
            findings = parser.parse_sonarqube(report_path)
        elif tool == 'bandit':
            findings = parser.parse_bandit(report_path)
        else:
            print(f"[警告] 不支持的工具类型: {tool}")
            return
        self.findings.extend(findings)

    def deduplicate(self) -> List[SecurityFinding]:
        """
        去重：移除重复的安全发现

        去重逻辑：相同 tool + rule_id + file_path + line_number 视为重复
        """
        seen = set()
        unique_findings = []

        for finding in self.findings:
            # 生成唯一标识
            key = hashlib.md5(
                f"{finding.tool}:{finding.rule_id}:"
                f"{finding.file_path}:{finding.line_number}".encode()
            ).hexdigest()

            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)

        self.findings = unique_findings
        return unique_findings

    def sort_by_severity(self) -> List[SecurityFinding]:
        """按严重程度排序（从高到低）"""
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        self.findings.sort(key=lambda f: severity_order.get(f.severity, 5))
        return self.findings

    def generate_summary(self) -> Dict[str, Any]:
        """生成聚合统计摘要"""
        severity_counts = {s.value: 0 for s in Severity}
        tool_counts = {}
        category_counts = {}

        for finding in self.findings:
            sev = finding.severity.value
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

            tool_counts[finding.tool] = tool_counts.get(finding.tool, 0) + 1

            cat = finding.category or 'unknown'
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            'scan_time': datetime.datetime.now().isoformat(),
            'total_findings': len(self.findings),
            'by_severity': severity_counts,
            'by_tool': tool_counts,
            'by_category': category_counts,
        }

    def generate_report(self, output_format: str = 'json',
                        output_path: str = None) -> str:
        """
        生成安全报告

        参数：
            output_format: 输出格式（json/text/html）
            output_path: 输出文件路径
        返回：
            报告内容字符串
        """
        # 先去重和排序
        self.deduplicate()
        self.sort_by_severity()

        summary = self.generate_summary()

        if output_format == 'json':
            report = self._generate_json_report(summary)
        elif output_format == 'text':
            report = self._generate_text_report(summary)
        elif output_format == 'html':
            report = self._generate_html_report(summary)
        else:
            report = self._generate_text_report(summary)

        # 写入文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"[信息] 报告已保存到: {output_path}")

        return report

    def _generate_json_report(self, summary: Dict) -> str:
        """生成 JSON 格式报告"""
        report = {
            'metadata': {
                'report_type': 'DevSecOps Aggregated Security Report',
                'generated_at': summary['scan_time'],
                'tool_version': '1.0.0',
            },
            'summary': summary,
            'findings': [
                {
                    'tool': f.tool,
                    'rule_id': f.rule_id,
                    'severity': f.severity.value,
                    'title': f.title,
                    'description': f.description,
                    'file_path': f.file_path,
                    'line_number': f.line_number,
                    'category': f.category,
                    'cwe': f.cwe,
                    'remediation': f.remediation,
                    'confidence': f.confidence,
                    'evidence': f.evidence,
                }
                for f in self.findings
            ],
        }
        return json.dumps(report, indent=2, ensure_ascii=False)

    def _generate_text_report(self, summary: Dict) -> str:
        """生成文本格式报告"""
        lines = []
        lines.append("=" * 70)
        lines.append("          DevSecOps 安全扫描聚合报告")
        lines.append("=" * 70)
        lines.append(f"扫描时间: {summary['scan_time']}")
        lines.append(f"总发现数: {summary['total_findings']}")
        lines.append("")
        lines.append("按严重程度统计:")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = summary['by_severity'].get(sev, 0)
            lines.append(f"  {sev:10s}: {count}")
        lines.append("")
        lines.append("按工具统计:")
        for tool, count in summary['by_tool'].items():
            lines.append(f"  {tool:20s}: {count}")
        lines.append("")
        lines.append("按类别统计:")
        for cat, count in sorted(summary['by_category'].items(),
                                  key=lambda x: -x[1]):
            lines.append(f"  {cat:30s}: {count}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("详细发现列表:")
        lines.append("-" * 70)

        for i, f in enumerate(self.findings, 1):
            lines.append(f"\n[{i}] [{f.severity.value}] {f.tool}: {f.title}")
            lines.append(f"    规则ID: {f.rule_id}")
            if f.file_path:
                lines.append(f"    文件: {f.file_path}:{f.line_number}")
            if f.description:
                lines.append(f"    描述: {f.description}")
            if f.cwe:
                lines.append(f"    CWE: {f.cwe}")
            if f.remediation:
                lines.append(f"    修复建议: {f.remediation}")
            if f.evidence:
                lines.append(f"    证据: {f.evidence[:100]}")

        lines.append("\n" + "=" * 70)
        return '\n'.join(lines)

    def _generate_html_report(self, summary: Dict) -> str:
        """生成 HTML 格式报告（简化版）"""
        html_parts = ['<html><head><meta charset="utf-8">']
        html_parts.append('<style>')
        html_parts.append('body{font-family:sans-serif;margin:20px;}')
        html_parts.append('table{border-collapse:collapse;width:100%;}')
        html_parts.append('th,td{border:1px solid #ddd;padding:8px;text-align:left;}')
        html_parts.append('.CRITICAL{background:#ff4444;color:white;}')
        html_parts.append('.HIGH{background:#ff8844;color:white;}')
        html_parts.append('.MEDIUM{background:#ffcc44;}')
        html_parts.append('.LOW{background:#88cc88;}')
        html_parts.append('</style></head><body>')
        html_parts.append('<h1>DevSecOps 安全扫描聚合报告</h1>')
        html_parts.append(f'<p>扫描时间: {summary["scan_time"]}</p>')
        html_parts.append(f'<p>总发现数: {summary["total_findings"]}</p>')

        # 严重程度统计
        html_parts.append('<h2>按严重程度统计</h2><table>')
        html_parts.append('<tr><th>严重程度</th><th>数量</th></tr>')
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            count = summary['by_severity'].get(sev, 0)
            html_parts.append(f'<tr class="{sev}"><td>{sev}</td><td>{count}</td></tr>')
        html_parts.append('</table>')

        # 详细发现
        html_parts.append('<h2>详细发现</h2><table>')
        html_parts.append('<tr><th>#</th><th>严重程度</th><th>工具</th>'
                          '<th>标题</th><th>文件</th><th>修复建议</th></tr>')
        for i, f in enumerate(self.findings, 1):
            file_loc = f"{f.file_path}:{f.line_number}" if f.file_path else ""
            html_parts.append(
                f'<tr class="{f.severity.value}">'
                f'<td>{i}</td><td>{f.severity.value}</td>'
                f'<td>{f.tool}</td><td>{f.title}</td>'
                f'<td>{file_loc}</td><td>{f.remediation}</td></tr>'
            )
        html_parts.append('</table></body></html>')

        return '\n'.join(html_parts)


# ============================================================
# 第八部分：主程序入口与命令行接口
# ============================================================

def run_scan(project_path: str) -> List[SecurityFinding]:
    """
    执行完整的安全扫描

    参数：
        project_path: 项目根目录路径
    返回：
        所有工具的安全发现列表
    """
    all_findings = []
    print(f"\n[信息] 开始扫描项目: {project_path}")

    # 1. 依赖漏洞扫描
    print("\n[扫描] 依赖漏洞扫描...")
    req_file = os.path.join(project_path, 'requirements.txt')
    if os.path.exists(req_file):
        dep_findings = DependencyScanner.scan_requirements_txt(req_file)
        all_findings.extend(dep_findings)
        print(f"  requirements.txt: 发现 {len(dep_findings)} 个漏洞")

    pkg_file = os.path.join(project_path, 'package.json')
    if os.path.exists(pkg_file):
        dep_findings = DependencyScanner.scan_package_json(pkg_file)
        all_findings.extend(dep_findings)
        print(f"  package.json: 发现 {len(dep_findings)} 个漏洞")

    # 2. Dockerfile 安全检查
    print("\n[扫描] Dockerfile 安全检查...")
    dockerfile_path = os.path.join(project_path, 'Dockerfile')
    if os.path.exists(dockerfile_path):
        docker_findings = DockerfileChecker.check(dockerfile_path)
        all_findings.extend(docker_findings)
        print(f"  Dockerfile: 发现 {len(docker_findings)} 个问题")
    else:
        print("  Dockerfile 不存在，跳过")

    # 3. Terraform 安全审计
    print("\n[扫描] Terraform 安全审计...")
    tf_dir = os.path.join(project_path, 'terraform')
    if os.path.isdir(tf_dir):
        tf_findings = TerraformAuditor.check(tf_dir)
        all_findings.extend(tf_findings)
        print(f"  terraform/: 发现 {len(tf_findings)} 个问题")
    else:
        print("  terraform/ 目录不存在，跳过")

    return all_findings


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description='DevSecOps 安全流水线工具包',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 扫描项目目录
  python devsecops_pipeline.py --mode scan --path /project/path

  # 解析 SAST 报告
  python devsecops_pipeline.py --mode parse --sast-semgrep semgrep.json
  python devsecops_pipeline.py --mode parse --sast-sonar sonarqube.json

  # 安全门禁评估
  python devsecops_pipeline.py --mode gate --reports-dir ./reports/

  # 聚合报告
  python devsecops_pipeline.py --mode aggregate --reports-dir ./reports/ --output-format json
        """
    )

    parser.add_argument('--mode', type=str, default='scan',
                        choices=['scan', 'parse', 'gate', 'aggregate'],
                        help='运行模式: scan=扫描, parse=解析报告, gate=安全门禁, aggregate=聚合报告')
    parser.add_argument('--path', type=str, default='.',
                        help='项目路径（scan 模式）')
    parser.add_argument('--sast-semgrep', type=str, help='Semgrep JSON 报告路径')
    parser.add_argument('--sast-sonar', type=str, help='SonarQube JSON 报告路径')
    parser.add_argument('--sast-bandit', type=str, help='Bandit JSON 报告路径')
    parser.add_argument('--reports-dir', type=str, default='./reports',
                        help='报告目录路径')
    parser.add_argument('--fail-level', type=str, default='high',
                        choices=['critical', 'high', 'medium', 'low'],
                        help='安全门禁阻断级别')
    parser.add_argument('--output-format', type=str, default='text',
                        choices=['json', 'text', 'html'],
                        help='输出报告格式')
    parser.add_argument('--output', type=str, default='security-report.txt',
                        help='输出文件路径')

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("        DevSecOps 安全流水线工具包 v1.0.0")
    print("=" * 70)

    if args.mode == 'scan':
        # 扫描模式
        findings = run_scan(args.path)

        # 安全门禁评估
        gate = SecurityGate(fail_level=args.fail_level)
        result = gate.evaluate(findings)
        gate.print_result(result)

        # 生成报告
        aggregator = ReportAggregator()
        aggregator.add_findings(findings)
        report = aggregator.generate_report(
            output_format=args.output_format,
            output_path=args.output
        )

        sys.exit(0 if result.passed else 1)

    elif args.mode == 'parse':
        # 报告解析模式
        aggregator = ReportAggregator()

        if args.sast_semgrep:
            print(f"\n[解析] Semgrep 报告: {args.sast_semgrep}")
            aggregator.add_from_json(args.sast_semgrep, 'semgrep')

        if args.sast_sonar:
            print(f"\n[解析] SonarQube 报告: {args.sast_sonar}")
            aggregator.add_from_json(args.sast_sonar, 'sonarqube')

        if args.sast_bandit:
            print(f"\n[解析] Bandit 报告: {args.sast_bandit}")
            aggregator.add_from_json(args.sast_bandit, 'bandit')

        # 输出聚合报告
        report = aggregator.generate_report(
            output_format=args.output_format,
            output_path=args.output
        )

        print(f"\n[信息] 共发现 {len(aggregator.findings)} 个安全问题")
        print(f"[信息] 报告已保存到: {args.output}")

    elif args.mode == 'gate':
        # 安全门禁模式
        findings = []

        # 从报告目录加载所有 JSON 报告
        reports_dir = args.reports_dir
        if os.path.isdir(reports_dir):
            parser = SASTParser()
            for file in os.listdir(reports_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(reports_dir, file)
                    # 自动识别报告类型
                    if 'semgrep' in file.lower():
                        findings.extend(parser.parse_semgrep(file_path))
                    elif 'sonar' in file.lower():
                        findings.extend(parser.parse_sonarqube(file_path))
                    elif 'bandit' in file.lower():
                        findings.extend(parser.parse_bandit(file_path))

        gate = SecurityGate(fail_level=args.fail_level)
        result = gate.evaluate(findings)
        gate.print_result(result)

        sys.exit(0 if result.passed else 1)

    elif args.mode == 'aggregate':
        # 聚合报告模式
        aggregator = ReportAggregator()
        parser = SASTParser()

        reports_dir = args.reports_dir
        if os.path.isdir(reports_dir):
            for file in os.listdir(reports_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(reports_dir, file)
                    print(f"[聚合] 处理: {file}")
                    if 'semgrep' in file.lower():
                        aggregator.add_from_json(file_path, 'semgrep')
                    elif 'sonar' in file.lower():
                        aggregator.add_from_json(file_path, 'sonarqube')
                    elif 'bandit' in file.lower():
                        aggregator.add_from_json(file_path, 'bandit')

        report = aggregator.generate_report(
            output_format=args.output_format,
            output_path=args.output
        )

        print(f"\n[信息] 聚合完成，共 {len(aggregator.findings)} 个发现")
        print(f"[信息] 报告已保存到: {args.output}")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
