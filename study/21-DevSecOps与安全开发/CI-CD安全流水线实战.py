#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DevSecOps CI/CD 安全流水线实战案例
====================================

本文件演示了一个完整的 DevSecOps 安全流水线，涵盖从代码提交到部署的
全生命周期安全扫描。适用于安全学习者理解 CI/CD 中的安全实践。

模块清单:
  1. Git 仓库安全扫描器   —— 敏感信息泄露检测
  2. SAST 安全扫描集成器  —— 静态应用安全测试
  3. 依赖安全扫描器       —— 第三方依赖漏洞检测
  4. 容器镜像安全扫描器   —— Dockerfile 与镜像层分析
  5. Kubernetes 安全审计器 —— K8s 清单安全检查
  6. 安全门禁评估器       —— 流水线阻断决策与综合报告

运行方式:
    python CI-CD安全流水线实战.py scan --repo ./myproject
    python CI-CD安全流水线实战.py sast --input semgrep.json
    python CI-CD安全流水线实战.py deps --file requirements.txt
    python CI-CD安全流水线实战.py docker --file Dockerfile
    python CI-CD安全流水线实战.py k8s --file deploy.yaml
    python CI-CD安全流水线实战.py gate --report ./reports

注意: 本代码仅用于学习目的，模拟真实扫描行为，不连接实际外部服务。
"""

import os
import re
import json
import argparse
import hashlib
import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum

# ============================================================
#  第一部分：基础数据类定义
# ============================================================

class Severity(Enum):
    """漏洞严重等级枚举，对应 CVSS 评分区间"""
    CRITICAL = "严重"   # CVSS 9.0-10.0
    HIGH = "高危"       # CVSS 7.0-8.9
    MEDIUM = "中危"     # CVSS 4.0-6.9
    LOW = "低危"        # CVSS 0.1-3.9
    INFO = "信息"       # 信息性发现

    @property
    def weight(self) -> int:
        """返回权重值，用于优先级排序（越大越紧急）"""
        return {"严重": 5, "高危": 4, "中危": 3, "低危": 2, "信息": 1}.get(self.value, 0)


@dataclass
class Finding:
    """安全发现基类——所有扫描器的输出统一结构"""
    scanner: str             # 扫描器名称
    rule_id: str             # 规则编号
    title: str               # 漏洞标题
    severity: str            # 严重等级（中文）
    description: str         # 详细描述
    file_path: str = ""     # 文件路径
    line_number: int = 0    # 行号
    code_snippet: str = ""  # 代码片段
    remediation: str = ""   # 修复建议
    cwe: str = ""           # CWE 编号
    confidence: str = "高"  # 置信度


@dataclass
class ScanResult:
    """单次扫描结果集合"""
    scanner_name: str
    findings: List[Finding] = field(default_factory=list)
    scan_duration: float = 0.0
    total_files: int = 0
    scanned_files: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "严重")

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "高危")

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "中危")

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "低危")


# ============================================================
#  第二部分：Git 仓库安全扫描器
# ============================================================

class GitRepoScanner:
    """
    Git 仓库安全扫描器

    功能:
      - 扫描代码中的敏感信息泄露（API密钥、密码、Token、私钥）
      - 检查 .git 目录是否意外暴露在 Web 根目录
      - 检查 .env 环境变量文件是否被提交到仓库
      - 输出 JSON 格式的扫描报告
    """

    # 敏感信息正则匹配规则集
    # 每条规则: (规则ID, 名称, 正则表达式, 严重等级, 描述)
    SECRET_PATTERNS = [
        (
            "GIT001",
            "AWS Access Key ID",
            r'AKIA[0-9A-Z]{16}',
            "高危",
            "检测到 AWS Access Key ID，攻击者可利用该密钥访问云资源"
        ),
        (
            "GIT002",
            "AWS Secret Access Key",
            r'(?i)aws[_\-]?secret[_\-]?access[_\-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']',
            "严重",
            "检测到 AWS Secret Access Key 明文存储"
        ),
        (
            "GIT003",
            "GitHub Personal Access Token",
            r'ghp_[0-9a-zA-Z]{36}',
            "高危",
            "检测到 GitHub Personal Access Token，可被用于仓库越权访问"
        ),
        (
            "GIT004",
            "GitHub OAuth Token",
            r'gho_[0-9a-zA-Z]{36}',
            "高危",
            "检测到 GitHub OAuth Token"
        ),
        (
            "GIT005",
            "GitLab Personal Access Token",
            r'glpat-[0-9a-zA-Z\-]{20}',
            "高危",
            "检测到 GitLab Personal Access Token"
        ),
        (
            "GIT006",
            "数据库连接字符串",
            r'(?i)(mysql|mssql|postgres|mongodb)://[\w\-]+:[^@]+@[\w\-\.]+:\d+',
            "严重",
            "数据库连接串中包含明文密码"
        ),
        (
            "GIT007",
            "私钥文件头",
            r'-----BEGIN (RSA |EC |DSA |OPENSSH |)PRIVATE KEY-----',
            "严重",
            "检测到私钥文件内容，私钥泄露将导致身份冒充"
        ),
        (
            "GIT008",
            "JWT Token",
            r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+',
            "中危",
            "检测到硬编码 JWT Token"
        ),
        (
            "GIT009",
            "Slack Token",
            r'xox[baprs]-[0-9a-zA-Z\-]{10,}',
            "高危",
            "检测到 Slack API Token"
        ),
        (
            "GIT010",
            "通用密码赋值",
            r'(?i)(password|passwd|pwd|pass)\s*[:=]\s*["\']([^"\']{4,})["\']',
            "中危",
            "检测到代码中硬编码密码赋值"
        ),
        (
            "GIT011",
            "Google API Key",
            r'AIza[0-9A-Za-z\-_]{35}',
            "高危",
            "检测到 Google API Key"
        ),
        (
            "GIT012",
            "Stripe Secret Key",
            r'sk_live_[0-9a-zA-Z]{24,}',
            "严重",
            "检测到 Stripe 生产环境 Secret Key"
        ),
    ]

    # 需要检查是否被提交到仓库的敏感文件列表
    SENSITIVE_FILES = [
        ".env",
        ".env.local",
        ".env.production",
        ".env.staging",
        "id_rsa",
        "id_dsa",
        "id_ed25519",
        ".npmrc",
        ".pypirc",
        "credentials.json",
        "service-account.json",
    ]

    def __init__(self, repo_path: str):
        """
        初始化 Git 仓库扫描器

        参数:
            repo_path: Git 仓库的本地路径
        """
        self.repo_path = os.path.abspath(repo_path)
        self.findings: List[Finding] = []

        # 需要跳过的目录（依赖包、构建产物等）
        self.skip_dirs = {
            "node_modules", ".git", "venv", "__pycache__",
            ".venv", "dist", "build", ".tox", ".eggs"
        }
        # 需要扫描的文件扩展名
        self.scan_extensions = {
            ".py", ".js", ".ts", ".java", ".go", ".rb",
            ".php", ".yml", ".yaml", ".json", ".xml",
            ".conf", ".cfg", ".ini", ".sh", ".env", ""
        }

    def scan(self) -> ScanResult:
        """执行完整的 Git 仓库安全扫描"""
        start_time = datetime.datetime.now()
        self.findings = []

        if not os.path.isdir(self.repo_path):
            print(f"[!] 仓库路径不存在: {self.repo_path}")
            return ScanResult(scanner_name="GitRepoScanner")

        print(f"[*] 开始扫描 Git 仓库: {self.repo_path}")

        # 第一步：扫描敏感文件泄露
        self._scan_sensitive_files()

        # 第二步：扫描 .git 目录泄露风险
        self._check_git_directory_exposure()

        # 第三步：扫描代码文件中的敏感信息
        total_files = 0
        scanned_files = 0
        for root, dirs, files in os.walk(self.repo_path):
            # 跳过不需要扫描的目录
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]

            for filename in files:
                filepath = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()

                # 扫描所有文本类型文件
                total_files += 1
                if ext in self.scan_extensions or filename.startswith(".env"):
                    self._scan_file(filepath)
                    scanned_files += 1

        duration = (datetime.datetime.now() - start_time).total_seconds()
        result = ScanResult(
            scanner_name="GitRepoScanner",
            findings=self.findings,
            scan_duration=round(duration, 2),
            total_files=total_files,
            scanned_files=scanned_files
        )
        print(f"[*] Git 仓库扫描完成: 发现 {len(self.findings)} 个问题, 耗时 {duration:.2f}s")
        return result

    def _scan_sensitive_files(self) -> None:
        """检查敏感文件是否被提交到仓库中"""
        for sfile in self.SENSITIVE_FILES:
            filepath = os.path.join(self.repo_path, sfile)
            if os.path.isfile(filepath):
                self.findings.append(Finding(
                    scanner="GitRepoScanner",
                    rule_id="GIT100",
                    title=f"敏感文件泄露: {sfile}",
                    severity="严重",
                    description=f"敏感文件 {sfile} 被发现存在于仓库根目录中，"
                                f"可能包含凭据、密钥等敏感信息",
                    file_path=filepath,
                    remediation="将敏感文件加入 .gitignore，使用密钥管理服务替代"
                ))

    def _check_git_directory_exposure(self) -> None:
        """检查 .git 目录是否暴露在 Web 可访问路径下"""
        git_dir = os.path.join(self.repo_path, ".git")
        if os.path.isdir(git_dir):
            # 检查是否在 Web 根目录（通常包含 index.html 或类似文件）
            web_indicators = ["index.html", "index.php", "public", "www", "htdocs"]
            for indicator in web_indicators:
                if os.path.exists(os.path.join(self.repo_path, indicator)):
                    self.findings.append(Finding(
                        scanner="GitRepoScanner",
                        rule_id="GIT101",
                        title=".git 目录暴露风险",
                        severity="高危",
                        description="Web 根目录下存在 .git 目录，"
                                    "攻击者可通过访问 .git/ 目录重建源代码",
                        file_path=git_dir,
                        remediation="配置 Web 服务器禁止访问 .git 目录，"
                                    "或仅将构建产物部署到生产环境"
                    ))
                    break

    def _scan_file(self, filepath: str) -> None:
        """扫描单个文件中的敏感信息"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except (IOError, PermissionError):
            return

        for line_num, line in enumerate(lines, 1):
            for rule_id, name, pattern, severity, desc in self.SECRET_PATTERNS:
                match = re.search(pattern, line)
                if match:
                    # 对代码片段做脱敏处理
                    snippet = line.strip()[:120]
                    # 将匹配到的敏感值替换为星号
                    masked = re.sub(pattern, "***REDACTED***", snippet)

                    self.findings.append(Finding(
                        scanner="GitRepoScanner",
                        rule_id=rule_id,
                        title=name,
                        severity=severity,
                        description=desc,
                        file_path=filepath,
                        line_number=line_num,
                        code_snippet=masked,
                        remediation="将敏感信息移至环境变量或密钥管理服务（如 Vault/AWS Secrets Manager）",
                        cwe="CWE-798"
                    ))

    def to_json(self) -> str:
        """输出 JSON 格式的扫描报告"""
        results = [asdict(f) for f in self.findings]
        return json.dumps(
            {
                "scan_type": "git_repository_scan",
                "scan_time": datetime.datetime.now().isoformat(),
                "repo_path": self.repo_path,
                "total_findings": len(self.findings),
                "findings": results
            },
            ensure_ascii=False,
            indent=2
        )


# ============================================================
#  第三部分：SAST 安全扫描集成器
# ============================================================

class SASTIntegrator:
    """
    SAST（静态应用安全测试）安全扫描集成器

    功能:
      - 模拟解析 Semgrep 扫描结果（JSON 格式）
      - 模拟解析 Bandit（Python 安全扫描）结果
      - 漏洞去重与优先级排序
      - 误报管理（白名单/抑制规则）
      - 生成安全门禁判定
    """

    def __init__(self):
        self.findings: List[Finding] = []
        self.suppressed: List[Finding] = []  # 被抑制的误报
        # 误报白名单: {文件路径: [规则ID列表]}
        self.whitelist: Dict[str, List[str]] = {}
        # 抑制规则: 规则ID -> 抑制原因
        self.suppress_rules: Dict[str, str] = {}

    def add_whitelist(self, file_path: str, rule_ids: List[str]) -> None:
        """添加误报白名单条目"""
        self.whitelist[file_path] = rule_ids

    def add_suppress_rule(self, rule_id: str, reason: str) -> None:
        """添加规则抑制条目"""
        self.suppress_rules[rule_id] = reason

    def parse_semgrep_result(self, json_str: str) -> List[Finding]:
        """
        解析 Semgrep JSON 输出

        Semgrep 是一种轻量级多语言 SAST 工具，其 JSON 输出包含 results 数组。
        本方法将其转换为统一的 Finding 结构。
        """
        semgrep_findings = []
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            print("[!] Semgrep 结果 JSON 解析失败")
            return semgrep_findings

        for result in data.get("results", []):
            # 映射 Semgrep 严重等级到中文
            sev_map = {"ERROR": "严重", "WARNING": "中危", "INFO": "信息"}
            severity = sev_map.get(result.get("extra", {}).get("severity", "INFO"), "信息")

            finding = Finding(
                scanner="Semgrep",
                rule_id=result.get("check_id", "SEMGREP_UNKNOWN"),
                title=result.get("extra", {}).get("message", "Semgrep 发现"),
                severity=severity,
                description=result.get("extra", {}).get("message", ""),
                file_path=result.get("path", ""),
                line_number=result.get("start", {}).get("line", 0),
                code_snippet=result.get("extra", {}).get("lines", ""),
                remediation=result.get("extra", {}).get("fix", "请参考 Semgrep 规则文档修复"),
                cwe=result.get("extra", {}).get("metadata", {}).get("cwe", [""])[0] if
                      isinstance(result.get("extra", {}).get("metadata", {}).get("cwe"), list) else ""
            )
            semgrep_findings.append(finding)

        self.findings.extend(semgrep_findings)
        print(f"[*] Semgrep 结果解析完成: {len(semgrep_findings)} 个发现")
        return semgrep_findings

    def parse_bandit_result(self, json_str: str) -> List[Finding]:
        """
        解析 Bandit JSON 输出

        Bandit 是 Python 专用的安全扫描工具，其 JSON 输出包含 results 数组，
        每条结果包含 issue 级别、行号、文件路径等信息。
        """
        bandit_findings = []
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            print("[!] Bandit 结果 JSON 解析失败")
            return bandit_findings

        for result in data.get("results", []):
            # 映射 Bandit 级别: HIGH/MEDIUM/LOW
            sev_map = {"HIGH": "高危", "MEDIUM": "中危", "LOW": "低危"}
            severity = sev_map.get(result.get("issue_severity", "LOW"), "低危")

            finding = Finding(
                scanner="Bandit",
                rule_id=result.get("test_id", "BANDIT_UNKNOWN"),
                title=result.get("test_name", "Bandit 发现"),
                severity=severity,
                description=result.get("issue_text", ""),
                file_path=result.get("filename", ""),
                line_number=result.get("line_number", 0),
                code_snippet=result.get("line_range", ""),
                remediation="请参考 Bandit 规则文档修复",
                cwe=result.get("issue_cwe", {}).get("id", "")
            )
            bandit_findings.append(finding)

        self.findings.extend(bandit_findings)
        print(f"[*] Bandit 结果解析完成: {len(bandit_findings)} 个发现")
        return bandit_findings

    def deduplicate(self) -> int:
        """
        漏洞去重

        基于 (文件路径, 行号, 规则ID) 组合去重，
        保留置信度最高的记录。
        """
        seen = {}
        unique_findings = []
        for f in self.findings:
            # 使用 文件+行号+规则 作为去重键
            key = (f.file_path, f.line_number, f.rule_id)
            if key in seen:
                # 比较置信度，保留更高的
                existing = seen[key]
                conf_order = {"高": 3, "中": 2, "低": 1, "信息": 0}
                if conf_order.get(f.confidence, 0) > conf_order.get(existing.confidence, 0):
                    seen[key] = f
            else:
                seen[key] = f

        unique_findings = list(seen.values())
        removed = len(self.findings) - len(unique_findings)
        self.findings = unique_findings
        print(f"[*] 去重完成: 移除 {removed} 个重复发现")
        return removed

    def apply_whitelist(self) -> int:
        """应用白名单和抑制规则，过滤误报"""
        remaining = []
        suppressed_count = 0

        for f in self.findings:
            # 检查文件级白名单
            if f.file_path in self.whitelist:
                if f.rule_id in self.whitelist[f.file_path]:
                    self.suppressed.append(f)
                    suppressed_count += 1
                    continue

            # 检查全局抑制规则
            if f.rule_id in self.suppress_rules:
                self.suppressed.append(f)
                suppressed_count += 1
                continue

            remaining.append(f)

        self.findings = remaining
        print(f"[*] 误报过滤完成: 抑制 {suppressed_count} 个误报")
        return suppressed_count

    def sort_by_priority(self) -> List[Finding]:
        """按严重等级和置信度排序（最紧急的在前）"""
        sev_weight = {"严重": 5, "高危": 4, "中危": 3, "低危": 2, "信息": 1}
        conf_weight = {"高": 3, "中": 2, "低": 1, "信息": 0}
        return sorted(
            self.findings,
            key=lambda f: (sev_weight.get(f.severity, 0), conf_weight.get(f.confidence, 0)),
            reverse=True
        )

    def evaluate_gate(self, policy: dict = None) -> Tuple[bool, str]:
        """
        安全门禁判定

        根据策略评估是否阻断流水线。
        默认策略: 严重/高危漏洞数量超过阈值则阻断。

        参数:
            policy: 门禁策略字典，例如:
                {
                    "max_critical": 0,   # 严重漏洞允许数
                    "max_high": 2,      # 高危漏洞允许数
                    "max_medium": 10    # 中危漏洞允许数
                }
        """
        if policy is None:
            policy = {"max_critical": 0, "max_high": 0, "max_medium": 10}

        critical = sum(1 for f in self.findings if f.severity == "严重")
        high = sum(1 for f in self.findings if f.severity == "高危")
        medium = sum(1 for f in self.findings if f.severity == "中危")

        if critical > policy["max_critical"]:
            return False, f"门禁失败: {critical} 个严重漏洞 (阈值 {policy['max_critical']})"
        if high > policy["max_high"]:
            return False, f"门禁失败: {high} 个高危漏洞 (阈值 {policy['max_high']})"
        if medium > policy["max_medium"]:
            return False, f"门禁失败: {medium} 个中危漏洞 (阈值 {policy['max_medium']})"

        return True, f"门禁通过: 严重 {critical}, 高危 {high}, 中危 {medium}"

    def to_json(self) -> str:
        """输出 JSON 格式报告"""
        return json.dumps({
            "scan_type": "sast_integration",
            "total_findings": len(self.findings),
            "suppressed_findings": len(self.suppressed),
            "findings": [asdict(f) for f in self.sort_by_priority()]
        }, ensure_ascii=False, indent=2)


# ============================================================
#  第四部分：依赖安全扫描器
# ============================================================

class DependencyScanner:
    """
    依赖安全扫描器

    功能:
      - 解析 requirements.txt / package.json / go.mod 中的依赖
      - 检查已知漏洞（模拟 OSV/CVE 数据库查询）
      - 许可证合规检查
      - 依赖树分析和传递依赖漏洞检测
      - 生成依赖安全报告
    """

    # 模拟漏洞数据库（实际应查询 OSV/NVD API）
    MOCK_VULN_DB = {
        "requests": [
            {"cve": "CVE-2023-32681", "severity": "中危",
             "description": "Requests 存在 Cookie 泄露漏洞", "fixed_version": "2.31.0"}
        ],
        "django": [
            {"cve": "CVE-2023-23969", "severity": "高危",
             "description": "Django 存在 SQL 注入漏洞", "fixed_version": "4.1.6"},
            {"cve": "CVE-2023-41164", "severity": "中危",
             "description": "Django 存在拒绝服务漏洞", "fixed_version": "4.2.5"}
        ],
        "flask": [
            {"cve": "CVE-2023-30861", "severity": "高危",
             "description": "Flask 存在 Cookie 安全绕过漏洞", "fixed_version": "2.2.5"}
        ],
        "lodash": [
            {"cve": "CVE-2021-23337", "severity": "高危",
             "description": "Lodash 命令注入漏洞", "fixed_version": "4.17.21"}
        ],
        "log4j": [
            {"cve": "CVE-2021-44228", "severity": "严重",
             "description": "Log4Shell 远程代码执行漏洞（Log4j）", "fixed_version": "2.17.1"}
        ],
    }

    # 模拟许可证合规数据库
    LICENSE_DB = {
        "MIT": {"compliant": True, "note": "宽松许可证，允许商业使用"},
        "Apache-2.0": {"compliant": True, "note": "宽松许可证，允许商业使用"},
        "BSD-2-Clause": {"compliant": True, "note": "宽松许可证"},
        "BSD-3-Clause": {"compliant": True, "note": "宽松许可证"},
        "GPL-2.0": {"compliant": False, "note": "传染性许可证，要求开源衍生作品"},
        "GPL-3.0": {"compliant": False, "note": "传染性许可证，要求开源衍生作品"},
        "LGPL-3.0": {"compliant": False, "note": "弱传染性许可证，需注意链接方式"},
    }

    def __init__(self):
        self.dependencies: List[dict] = []
        self.findings: List[Finding] = []
        self.license_issues: List[dict] = []

    def parse_requirements_txt(self, filepath: str) -> List[dict]:
        """
        解析 Python requirements.txt 文件

        格式示例:
            requests>=2.20.0
            django==4.1.6
            flask~=2.0
        """
        deps = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith("#"):
                        continue
                    # 跳过直接引用（git/egg）
                    if line.startswith("git+") or "://" in line:
                        continue

                    # 解析 包名 + 版本约束
                    match = re.match(r'^([a-zA-Z0-9_\-]+)\s*(.*)$', line)
                    if match:
                        name = match.group(1).lower()
                        version_spec = match.group(2).strip()
                        deps.append({
                            "name": name,
                            "version_spec": version_spec,
                            "ecosystem": "pypi",
                            "source_file": filepath
                        })
        except FileNotFoundError:
            print(f"[!] 文件不存在: {filepath}")

        self.dependencies.extend(deps)
        print(f"[*] requirements.txt 解析完成: {len(deps)} 个依赖")
        return deps

    def parse_package_json(self, filepath: str) -> List[dict]:
        """
        解析 Node.js package.json 文件

        提取 dependencies 和 devDependencies 中的依赖
        """
        deps = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[!] package.json 解析失败: {e}")
            return deps

        for section in ["dependencies", "devDependencies", "peerDependencies"]:
            for name, version in data.get(section, {}).items():
                deps.append({
                    "name": name.lower(),
                    "version_spec": version,
                    "ecosystem": "npm",
                    "source_file": filepath,
                    "dependency_type": section
                })

        self.dependencies.extend(deps)
        print(f"[*] package.json 解析完成: {len(deps)} 个依赖")
        return deps

    def parse_go_mod(self, filepath: str) -> List[dict]:
        """
        解析 Go go.mod 文件

        格式示例:
            require (
                github.com/gin-gonic/gin v1.7.0
                github.com/sirupsen/logrus v1.9.0
            )
        """
        deps = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"[!] 文件不存在: {filepath}")
            return deps

        # 匹配 require 块内的依赖
        require_pattern = r'require\s+(?:\(\s+)?(.*?)(?:\)|\n\n|\Z)'
        matches = re.findall(require_pattern, content, re.DOTALL)

        for block in matches:
            for line in block.strip().split("\n"):
                line = line.strip()
                if not line or line.startswith("//"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    deps.append({
                        "name": parts[0].lower(),
                        "version_spec": parts[1],
                        "ecosystem": "go",
                        "source_file": filepath
                    })

        self.dependencies.extend(deps)
        print(f"[*] go.mod 解析完成: {len(deps)} 个依赖")
        return deps

    def check_vulnerabilities(self) -> List[Finding]:
        """
        检查已知漏洞

        模拟查询 OSV（Open Source Vulnerability）数据库，
        实际环境中应调用 https://api.osv.dev/v1/query
        """
        vuln_findings = []
        for dep in self.dependencies:
            name = dep["name"]
            # 去除可能的版本前缀（如 @types/xxx）
            clean_name = name.split("/")[-1]

            if clean_name in self.MOCK_VULN_DB:
                for vuln in self.MOCK_VULN_DB[clean_name]:
                    vuln_findings.append(Finding(
                        scanner="DependencyScanner",
                        rule_id=vuln["cve"],
                        title=f"依赖漏洞: {name} - {vuln['description']}",
                        severity=vuln["severity"],
                        description=f"依赖 {name} {dep.get('version_spec', '')} "
                                    f"存在已知漏洞 {vuln['cve']}",
                        file_path=dep.get("source_file", ""),
                        remediation=f"升级到 {vuln['fixed_version']} 或更高版本",
                        cwe="CWE-1104"
                    ))

        self.findings.extend(vuln_findings)
        print(f"[*] 漏洞检查完成: 发现 {len(vuln_findings)} 个依赖漏洞")
        return vuln_findings

    def check_licenses(self, detected_licenses: Dict[str, str] = None) -> List[dict]:
        """
        许可证合规检查

        参数:
            detected_licenses: {包名: 许可证} 映射
                               如果为空则使用模拟数据
        """
        if detected_licenses is None:
            # 模拟检测到的许可证
            detected_licenses = {
                "requests": "Apache-2.0",
                "django": "BSD-3-Clause",
                "flask": "BSD-3-Clause",
                "lodash": "MIT",
                "some-gpl-package": "GPL-3.0",
            }

        issues = []
        for pkg, license_id in detected_licenses.items():
            license_info = self.LICENSE_DB.get(license_id)
            if license_info and not license_info["compliant"]:
                issues.append({
                    "package": pkg,
                    "license": license_id,
                    "compliant": False,
                    "note": license_info["note"]
                })
                self.findings.append(Finding(
                    scanner="DependencyScanner",
                    rule_id="LIC001",
                    title=f"许可证不合规: {pkg} ({license_id})",
                    severity="中危",
                    description=f"包 {pkg} 使用 {license_id} 许可证: {license_info['note']}",
                    file_path="",
                    remediation=f"替换 {pkg} 为使用兼容许可证的替代包"
                ))

        self.license_issues = issues
        print(f"[*] 许可证检查完成: {len(issues)} 个不合规项")
        return issues

    def to_json(self) -> str:
        """生成 JSON 格式的依赖安全报告"""
        return json.dumps({
            "scan_type": "dependency_scan",
            "total_dependencies": len(self.dependencies),
            "total_findings": len(self.findings),
            "license_issues": len(self.license_issues),
            "dependencies": self.dependencies,
            "findings": [asdict(f) for f in self.findings]
        }, ensure_ascii=False, indent=2)


# ============================================================
#  第五部分：容器镜像安全扫描器
# ============================================================

class ContainerImageScanner:
    """
    容器镜像安全扫描器

    功能:
      - 解析 Dockerfile 检查安全问题
      - 模拟镜像层分析
      - 检查镜像中已知漏洞
      - 生成 CIS Docker Benchmark 合规报告
    """

    # CIS Docker Benchmark 关键检查项
    CIS_CHECKS = {
        "CIS-4.1": "为容器创建非 root 用户",
        "CIS-4.6": "为容器设置只读文件系统",
        "CIS-5.3": "确保容器不使用特权模式",
        "CIS-5.10": "为容器设置内存限制",
        "CIS-5.11": "为容器设置 CPU 优先级",
        "CIS-5.12": "为容器设置只读根文件系统",
        "CIS-4.7": "确保容器不使用 --privileged 标志",
    }

    # 不安全的基础镜像
    UNSAFE_BASE_IMAGES = {
        "ubuntu:latest": "使用 latest 标签无法保证版本可追溯",
        "python:latest": "使用 latest 标签，建议指定具体版本",
        "node:latest": "使用 latest 标签，建议指定具体版本",
        "alpine:latest": "使用 latest 标签，建议指定具体版本",
    }

    def __init__(self):
        self.findings: List[Finding] = []
        self.dockerfile_path: str = ""

    def scan_dockerfile(self, filepath: str) -> ScanResult:
        """
        解析并扫描 Dockerfile

        检查项:
          - 特权模式 (privileged)
          - root 用户运行
          - 不安全基础镜像
          - 硬编码密钥
          - 无健康检查
        """
        self.dockerfile_path = filepath
        start_time = datetime.datetime.now()
        self.findings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[!] Dockerfile 不存在: {filepath}")
            return ScanResult(scanner_name="ContainerImageScanner")

        has_user_directive = False
        has_healthcheck = False

        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # 检查 FROM 指令——基础镜像安全性
            if line_stripped.upper().startswith("FROM"):
                image = line_stripped.split()[1] if len(line_stripped.split()) > 1 else ""
                if image in self.UNSAFE_BASE_IMAGES:
                    self.findings.append(Finding(
                        scanner="ContainerImageScanner",
                        rule_id="DOCKER001",
                        title="不安全的基础镜像",
                        severity="中危",
                        description=self.UNSAFE_BASE_IMAGES[image],
                        file_path=filepath,
                        line_number=line_num,
                        code_snippet=line_stripped,
                        remediation="指定具体版本标签，如 python:3.11-slim"
                    ))

            # 检查 USER 指令——是否使用非 root 用户
            if line_stripped.upper().startswith("USER"):
                has_user_directive = True
                user = line_stripped.split(None, 1)[1] if len(line_stripped.split()) > 1 else ""
                if user.strip() == "root" or user.strip() == "0":
                    self.findings.append(Finding(
                        scanner="ContainerImageScanner",
                        rule_id="DOCKER002",
                        title="容器以 root 用户运行",
                        severity="高危",
                        description="容器以 root 用户运行，违反 CIS-4.1",
                        file_path=filepath,
                        line_number=line_num,
                        code_snippet=line_stripped,
                        remediation="创建非 root 用户并切换: RUN useradd -m appuser && USER appuser",
                        cwe="CWE-250"
                    ))

            # 检查 RUN 指令中的特权操作或硬编码密钥
            if line_stripped.upper().startswith("RUN"):
                # 检查硬编码密码/密钥
                secret_patterns = [
                    (r'export\s+\w*PASSWORD\w*=\s*\S+', "硬编码密码"),
                    (r'export\s+\w*API_KEY\w*=\s*\S+', "硬编码 API Key"),
                    (r'export\s+\w*SECRET\w*=\s*\S+', "硬编码 Secret"),
                    (r'--password[=\s]\S+', "命令行密码参数"),
                    (r'wget\s+.*://.*:.*@', "URL 中包含凭据"),
                ]
                for pattern, desc in secret_patterns:
                    if re.search(pattern, line_stripped, re.IGNORECASE):
                        self.findings.append(Finding(
                            scanner="ContainerImageScanner",
                            rule_id="DOCKER003",
                            title=f"硬编码敏感信息: {desc}",
                            severity="严重",
                            description=f"Dockerfile RUN 指令中{desc}",
                            file_path=filepath,
                            line_number=line_num,
                            code_snippet=line_stripped[:100],
                            remediation="使用构建参数(--build-arg)或运行时环境变量",
                            cwe="CWE-798"
                        ))

            # 检查 HEALTHCHECK 指令
            if line_stripped.upper().startswith("HEALTHCHECK"):
                has_healthcheck = True

            # 检查 ADD 指令（应使用 COPY 代替）
            if line_stripped.upper().startswith("ADD"):
                self.findings.append(Finding(
                    scanner="ContainerImageScanner",
                    rule_id="DOCKER004",
                    title="使用 ADD 而非 COPY",
                    severity="低危",
                    description="ADD 指令支持远程 URL 和自动解压，可能引入安全风险",
                    file_path=filepath,
                    line_number=line_num,
                    code_snippet=line_stripped,
                    remediation="使用 COPY 指令替代 ADD"
                ))

        # 如果没有 USER 指令，默认以 root 运行
        if not has_user_directive:
            self.findings.append(Finding(
                scanner="ContainerImageScanner",
                rule_id="DOCKER005",
                title="未设置非 root 用户",
                severity="高危",
                description="Dockerfile 中未设置 USER 指令，容器默认以 root 运行",
                file_path=filepath,
                remediation="添加 USER 指令指定非 root 用户运行",
                cwe="CWE-250"
            ))

        # 如果没有 HEALTHCHECK 指令
        if not has_healthcheck:
            self.findings.append(Finding(
                scanner="ContainerImageScanner",
                rule_id="DOCKER006",
                title="缺少健康检查",
                severity="低危",
                description="Dockerfile 中未设置 HEALTHCHECK，容器异常无法被自动检测",
                file_path=filepath,
                remediation="添加 HEALTHCHECK 指令，例如: HEALTHCHECK --interval=30s CMD curl -f http://localhost/"
            ))

        duration = (datetime.datetime.now() - start_time).total_seconds()
        result = ScanResult(
            scanner_name="ContainerImageScanner",
            findings=self.findings,
            scan_duration=round(duration, 2),
            total_files=1,
            scanned_files=1
        )
        print(f"[*] Dockerfile 扫描完成: {len(self.findings)} 个发现")
        return result

    def simulate_layer_scan(self, image_name: str) -> List[Finding]:
        """
        模拟镜像层分析

        实际环境中可调用 Trivy / Grype / Clair 等工具。
        此处模拟分析结果用于学习演示。
        """
        mock_findings = [
            Finding(
                scanner="ContainerImageScanner",
                rule_id="CVE-2023-26136",
                title="镜像层漏洞: ingamb <= 0.1.7 (tough-cookie 依赖)",
                severity="高危",
                description=f"镜像 {image_name} 的中间层包含存在漏洞的 ingamb 包",
                file_path="layer:sha256:a1b2c3...",
                remediation="重新构建镜像，更新依赖"
            ),
            Finding(
                scanner="ContainerImageScanner",
                rule_id="CVE-2023-37924",
                title="镜像层漏洞: jQuery < 3.5.0 (XSS)",
                severity="中危",
                description=f"镜像 {image_name} 的前端层包含旧版 jQuery",
                file_path="layer:sha256:d4e5f6...",
                remediation="更新 jQuery 到 3.5.0 或更高版本"
            ),
        ]
        self.findings.extend(mock_findings)
        print(f"[*] 镜像层模拟分析完成: {len(mock_findings)} 个发现")
        return mock_findings

    def generate_cis_report(self) -> dict:
        """生成 CIS Docker Benchmark 合规报告"""
        passed = []
        failed = []
        for check_id, desc in self.CIS_CHECKS.items():
            # 模拟检查结果
            is_pass = not any(
                check_id.replace("CIS-", "DOCKER") in f.rule_id
                for f in self.findings
            )
            if is_pass:
                passed.append({"check_id": check_id, "description": desc, "status": "PASS"})
            else:
                failed.append({"check_id": check_id, "description": desc, "status": "FAIL"})

        report = {
            "benchmark": "CIS Docker Benchmark v1.6.0",
            "total_checks": len(self.CIS_CHECKS),
            "passed": len(passed),
            "failed": len(failed),
            "compliance_rate": f"{len(passed)/len(self.CIS_CHECKS)*100:.1f}%",
            "details": {"passed": passed, "failed": failed}
        }
        return report


# ============================================================
#  第六部分：Kubernetes 安全审计器
# ============================================================

class KubernetesAuditor:
    """
    Kubernetes 安全审计器

    功能:
      - 解析 K8s YAML 清单文件
      - 检查安全上下文（runAsRoot, privileged, allowPrivilegeEscalation）
      - 检查网络策略缺失
      - 检查 RBAC 过度权限
      - 检查资源限制缺失
      - 检查敏感信息以 Secret 明文存储
      - 生成 K8s 安全审计报告
    """

    # K8s 安全检查规则定义
    CHECK_RULES = {
        "K8S001": {
            "title": "容器以 root 用户运行",
            "severity": "高危",
            "check": "securityContext.runAsRoot != false",
            "remediation": "在 securityContext 中设置 runAsRoot: false 或 runAsUser: > 0"
        },
        "K8S002": {
            "title": "容器使用特权模式",
            "severity": "严重",
            "check": "securityContext.privileged == true",
            "remediation": "移除 privileged: true，使用 capabilities 精确授权"
        },
        "K8S003": {
            "title": "允许特权提升",
            "severity": "高危",
            "check": "securityContext.allowPrivilegeEscalation == true",
            "remediation": "设置 allowPrivilegeEscalation: false"
        },
        "K8S004": {
            "title": "缺少资源限制",
            "severity": "中危",
            "check": "resources.limits or resources.requests missing",
            "remediation": "设置 resources.requests 和 resources.limits"
        },
        "K8S005": {
            "title": "Secret 以明文存储敏感信息",
            "severity": "高危",
            "check": "Secret with data in base64 (not encrypted at rest)",
            "remediation": "使用外部密钥管理服务（如 Vault/Sealed Secrets）"
        },
        "K8S006": {
            "title": "缺少网络策略",
            "severity": "中危",
            "check": "No NetworkPolicy defined",
            "remediation": "定义 NetworkPolicy 限制 Pod 间通信"
        },
        "K8S007": {
            "title": "RBAC 权限过大",
            "severity": "高危",
            "check": "ClusterRole with verbs=['*'] on resources=['*']",
            "remediation": "遵循最小权限原则，精确定义 verbs 和 resources"
        },
        "K8S008": {
            "title": "未设置 readOnlyRootFilesystem",
            "severity": "中危",
            "check": "securityContext.readOnlyRootFilesystem != true",
            "remediation": "设置 readOnlyRootFilesystem: true"
        },
        "K8S009": {
            "title": "使用默认 ServiceAccount",
            "severity": "中危",
            "check": "serviceAccountName not specified",
            "remediation": "创建专用 ServiceAccount 并配置最小权限"
        },
    }

    def __init__(self):
        self.findings: List[Finding] = []
        self.resources: List[dict] = []
        self.has_network_policy = False

    def scan_yaml(self, filepath: str) -> ScanResult:
        """
        扫描 K8s YAML 清单文件

        本方法通过简单的文本解析来检查安全问题，
        不依赖 PyYAML（保持零依赖运行）。
        """
        start_time = datetime.datetime.now()
        self.findings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"[!] YAML 文件不存在: {filepath}")
            return ScanResult(scanner_name="KubernetesAuditor")

        # 简化版 YAML 解析——检查关键模式
        self._check_security_context(content, filepath)
        self._check_privileged(content, filepath)
        self._check_allow_privilege_escalation(content, filepath)
        self._check_resource_limits(content, filepath)
        self._check_secrets(content, filepath)
        self._check_network_policy(content, filepath)
        self._check_rbac(content, filepath)
        self._check_readonly_rootfs(content, filepath)
        self._check_service_account(content, filepath)

        duration = (datetime.datetime.now() - start_time).total_seconds()
        result = ScanResult(
            scanner_name="KubernetesAuditor",
            findings=self.findings,
            scan_duration=round(duration, 2),
            total_files=1,
            scanned_files=1
        )
        print(f"[*] K8s YAML 审计完成: {len(self.findings)} 个发现")
        return result

    def _check_security_context(self, content: str, filepath: str) -> None:
        """检查 runAsRoot 配置"""
        if "runAsRoot: true" in content or ("runAsRoot" not in content and "runAsUser" not in content):
            self.findings.append(Finding(
                scanner="KubernetesAuditor",
                rule_id="K8S001",
                title=self.CHECK_RULES["K8S001"]["title"],
                severity=self.CHECK_RULES["K8S001"]["severity"],
                description="容器未设置 runAsRoot: false，默认以 root 运行",
                file_path=filepath,
                remediation=self.CHECK_RULES["K8S001"]["remediation"]
            ))

    def _check_privileged(self, content: str, filepath: str) -> None:
        """检查特权模式"""
        if "privileged: true" in content:
            self.findings.append(Finding(
                scanner="KubernetesAuditor",
                rule_id="K8S002",
                title=self.CHECK_RULES["K8S002"]["title"],
                severity=self.CHECK_RULES["K8S002"]["severity"],
                description="容器以特权模式运行，等同于宿主机 root",
                file_path=filepath,
                remediation=self.CHECK_RULES["K8S002"]["remediation"]
            ))

    def _check_allow_privilege_escalation(self, content: str, filepath: str) -> None:
        """检查 allowPrivilegeEscalation"""
        if "allowPrivilegeEscalation: true" in content:
            self.findings.append(Finding(
                scanner="KubernetesAuditor",
                rule_id="K8S003",
                title=self.CHECK_RULES["K8S003"]["title"],
                severity=self.CHECK_RULES["K8S003"]["severity"],
                description="允许子进程获取比父进程更多权限",
                file_path=filepath,
                remediation=self.CHECK_RULES["K8S003"]["remediation"]
            ))

    def _check_resource_limits(self, content: str, filepath: str) -> None:
        """检查资源限制"""
        if "resources:" in content and "limits:" not in content:
            self.findings.append(Finding(
                scanner="KubernetesAuditor",
                rule_id="K8S004",
                title=self.CHECK_RULES["K8S004"]["title"],
                severity=self.CHECK_RULES["K8S004"]["severity"],
                description="定义了 resources 但未设置 limits",
                file_path=filepath,
                remediation=self.CHECK_RULES["K8S004"]["remediation"]
            ))

    def _check_secrets(self, content: str, filepath: str) -> None:
        """检查 Secret 明文存储"""
        if "kind: Secret" in content and "data:" in content:
            self.findings.append(Finding(
                scanner="KubernetesAuditor",
                rule_id="K8S005",
                title=self.CHECK_RULES["K8S005"]["title"],
                severity=self.CHECK_RULES["K8S005"]["severity"],
                description="Secret 中的数据仅做 base64 编码，非加密存储",
                file_path=filepath,
                remediation=self.CHECK_RULES["K8S005"]["remediation"]
            ))

    def _check_network_policy(self, content: str, filepath: str) -> None:
        """检查网络策略缺失"""
        if "kind: NetworkPolicy" in content:
            self.has_network_policy = True
        elif "kind: Deployment" in content or "kind: Pod" in content:
            if not self.has_network_policy:
                self.findings.append(Finding(
                    scanner="KubernetesAuditor",
                    rule_id="K8S006",
                    title=self.CHECK_RULES["K8S006"]["title"],
                    severity=self.CHECK_RULES["K8S006"]["severity"],
                    description="未发现 NetworkPolicy 定义，Pod 间通信不受限制",
                    file_path=filepath,
                    remediation=self.CHECK_RULES["K8S006"]["remediation"]
                ))

    def _check_rbac(self, content: str, filepath: str) -> None:
        """检查 RBAC 过度权限"""
        if "kind: ClusterRole" in content or "kind: Role" in content:
            if ('verbs: ["*"]' in content or "verbs:\n  - '*'" in content):
                self.findings.append(Finding(
                    scanner="KubernetesAuditor",
                    rule_id="K8S007",
                    title=self.CHECK_RULES["K8S007"]["title"],
                    severity=self.CHECK_RULES["K8S007"]["severity"],
                    description="RBAC 规则使用通配符 '*' 授予全部权限",
                    file_path=filepath,
                    remediation=self.CHECK_RULES["K8S007"]["remediation"]
                ))

    def _check_readonly_rootfs(self, content: str, filepath: str) -> None:
        """检查只读根文件系统"""
        if "securityContext:" in content and "readOnlyRootFilesystem: true" not in content:
            self.findings.append(Finding(
                scanner="KubernetesAuditor",
                rule_id="K8S008",
                title=self.CHECK_RULES["K8S008"]["title"],
                severity=self.CHECK_RULES["K8S008"]["severity"],
                description="未设置只读根文件系统",
                file_path=filepath,
                remediation=self.CHECK_RULES["K8S008"]["remediation"]
            ))

    def _check_service_account(self, content: str, filepath: str) -> None:
        """检查 ServiceAccount"""
        if ("kind: Deployment" in content or "kind: Pod" in content):
            if "serviceAccountName:" not in content:
                self.findings.append(Finding(
                    scanner="KubernetesAuditor",
                    rule_id="K8S009",
                    title=self.CHECK_RULES["K8S009"]["title"],
                    severity=self.CHECK_RULES["K8S009"]["severity"],
                    description="未指定 serviceAccountName，将使用默认 SA",
                    file_path=filepath,
                    remediation=self.CHECK_RULES["K8S009"]["remediation"]
                ))

    def to_json(self) -> str:
        """生成 JSON 格式的 K8s 安全审计报告"""
        return json.dumps({
            "scan_type": "kubernetes_audit",
            "total_findings": len(self.findings),
            "checks_applied": len(self.CHECK_RULES),
            "findings": [asdict(f) for f in self.findings]
        }, ensure_ascii=False, indent=2)


# ============================================================
#  第七部分：安全门禁评估器
# ============================================================

class SecurityGateEvaluator:
    """
    安全门禁评估器

    功能:
      - 汇总所有扫描结果
      - 根据策略评估是否阻断流水线
      - 生成流水线安全仪表盘数据
      - 输出 Markdown 格式综合报告
    """

    # 默认安全门禁策略
    DEFAULT_POLICY = {
        "git_secrets": {"max_critical": 0, "max_high": 0, "max_medium": 5},
        "sast": {"max_critical": 0, "max_high": 2, "max_medium": 10},
        "dependencies": {"max_critical": 0, "max_high": 3, "max_medium": 20},
        "container": {"max_critical": 0, "max_high": 1, "max_medium": 5},
        "k8s": {"max_critical": 0, "max_high": 2, "max_medium": 10},
    }

    def __init__(self, policy: dict = None):
        self.policy = policy or self.DEFAULT_POLICY
        self.scan_results: Dict[str, ScanResult] = {}
        self.gate_status: bool = True
        self.gate_messages: List[str] = []

    def add_result(self, name: str, result: ScanResult) -> None:
        """添加扫描结果"""
        self.scan_results[name] = result
        print(f"[*] 已添加扫描结果: {name} ({len(result.findings)} 个发现)")

    def evaluate(self) -> Tuple[bool, List[str]]:
        """评估安全门禁"""
        self.gate_status = True
        self.gate_messages = []

        # 映射扫描器名称到策略键
        policy_map = {
            "GitRepoScanner": "git_secrets",
            "SASTIntegrator": "sast",
            "DependencyScanner": "dependencies",
            "ContainerImageScanner": "container",
            "KubernetesAuditor": "k8s",
        }

        for scanner_name, result in self.scan_results.items():
            policy_key = policy_map.get(scanner_name, scanner_name)
            if policy_key not in self.policy:
                continue

            thresholds = self.policy[policy_key]
            critical = result.critical_count
            high = result.high_count
            medium = result.medium_count

            if critical > thresholds.get("max_critical", 0):
                self.gate_status = False
                self.gate_messages.append(
                    f"[{scanner_name}] 门禁失败: 严重漏洞 {critical} > {thresholds['max_critical']}"
                )
            elif high > thresholds.get("max_high", 0):
                self.gate_status = False
                self.gate_messages.append(
                    f"[{scanner_name}] 门禁失败: 高危漏洞 {high} > {thresholds['max_high']}"
                )
            elif medium > thresholds.get("max_medium", 100):
                self.gate_status = False
                self.gate_messages.append(
                    f"[{scanner_name}] 门禁失败: 中危漏洞 {medium} > {thresholds['max_medium']}"
                )
            else:
                self.gate_messages.append(
                    f"[{scanner_name}] 门禁通过: 严重 {critical}, 高危 {high}, 中危 {medium}"
                )

        status_text = "通过" if self.gate_status else "阻断"
        print(f"\n{'='*60}")
        print(f"  安全门禁判定: {status_text}")
        print(f"{'='*60}")
        for msg in self.gate_messages:
            print(f"  {msg}")
        print(f"{'='*60}\n")

        return self.gate_status, self.gate_messages

    def generate_dashboard_data(self) -> dict:
        """生成流水线安全仪表盘数据"""
        dashboard = {
            "pipeline_status": "通过" if self.gate_status else "阻断",
            "scan_time": datetime.datetime.now().isoformat(),
            "summary": {
                "total_findings": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "scanners": {}
        }

        for name, result in self.scan_results.items():
            scanner_data = {
                "findings_count": len(result.findings),
                "critical": result.critical_count,
                "high": result.high_count,
                "medium": result.medium_count,
                "low": result.low_count,
                "duration": result.scan_duration,
            }
            dashboard["scanners"][name] = scanner_data
            dashboard["summary"]["total_findings"] += len(result.findings)
            dashboard["summary"]["critical"] += result.critical_count
            dashboard["summary"]["high"] += result.high_count
            dashboard["summary"]["medium"] += result.medium_count
            dashboard["summary"]["low"] += result.low_count

        return dashboard

    def generate_markdown_report(self) -> str:
        """生成 Markdown 格式综合安全报告"""
        md = []
        md.append("# DevSecOps CI/CD 安全流水线报告\n")
        md.append(f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        status = "通过" if self.gate_status else "阻断"
        status_emoji = "[PASS]" if self.gate_status else "[FAIL]"
        md.append(f"**流水线状态**: {status_emoji} {status}\n")

        # 仪表盘摘要
        dashboard = self.generate_dashboard_data()
        md.append("\n## 摘要\n")
        md.append("| 指标 | 数值 |")
        md.append("|------|------|")
        md.append(f"| 总发现数 | {dashboard['summary']['total_findings']} |")
        md.append(f"| 严重 | {dashboard['summary']['critical']} |")
        md.append(f"| 高危 | {dashboard['summary']['high']} |")
        md.append(f"| 中危 | {dashboard['summary']['medium']} |")
        md.append(f"| 低危 | {dashboard['summary']['low']} |")

        # 各扫描器详情
        md.append("\n## 扫描器详情\n")
        for name, result in self.scan_results.items():
            md.append(f"### {name}\n")
            md.append(f"- 发现总数: {len(result.findings)}")
            md.append(f"- 严重: {result.critical_count} | 高危: {result.high_count} | "
                      f"中危: {result.medium_count} | 低危: {result.low_count}")
            md.append(f"- 扫描耗时: {result.scan_duration}s\n")

            if result.findings:
                md.append("| 严重等级 | 规则ID | 标题 | 文件 | 修复建议 |")
                md.append("|----------|--------|------|------|----------|")
                for f in result.findings[:20]:  # 限制最多20条
                    file_short = os.path.basename(f.file_path) if f.file_path else "-"
                    md.append(f"| {f.severity} | {f.rule_id} | {f.title} | {file_short} | {f.remediation} |")

        # 门禁判定详情
        md.append("\n## 安全门禁判定\n")
        for msg in self.gate_messages:
            md.append(f"- {msg}")

        md.append("\n## 建议措施\n")
        if self.gate_status:
            md.append("1. 流水线已通过安全门禁，可以继续部署")
            md.append("2. 建议定期重新扫描以发现新漏洞")
            md.append("3. 中低危问题应在后续迭代中逐步修复")
        else:
            md.append("1. **流水线已被阻断**，请先修复阻塞性问题")
            md.append("2. 优先修复严重和高危漏洞")
            md.append("3. 修复后重新触发流水线")
            md.append("4. 如确认为误报，可添加白名单后重新评估")

        return "\n".join(md)


# ============================================================
#  第八部分：模拟测试数据与演示函数
# ============================================================

# 模拟的 Semgrep 扫描结果（JSON 字符串）
MOCK_SEMGREP_OUTPUT = json.dumps({
    "results": [
        {
            "check_id": "python.lang.security.audit.dangerous-subprocess-use",
            "path": "app/utils.py",
            "start": {"line": 42},
            "extra": {
                "message": "检测到 subprocess 使用 shell=True，可能导致命令注入",
                "severity": "WARNING",
                "lines": "subprocess.run(user_input, shell=True)",
                "metadata": {"cwe": ["CWE-78: OS Command Injection"]}
            }
        },
        {
            "check_id": "python.lang.security.audit.ftp-request",
            "path": "app/file_downloader.py",
            "start": {"line": 15},
            "extra": {
                "message": "检测到使用 FTP 协议传输数据，明文传输不安全",
                "severity": "INFO",
                "lines": "ftp = FTP(host)",
                "metadata": {"cwe": ["CWE-319: Cleartext Transmission"]}
            }
        },
    ]
})

# 模拟的 Bandit 扫描结果
MOCK_BANDIT_OUTPUT = json.dumps({
    "results": [
        {
            "test_id": "B602",
            "test_name": "subprocess_popen_with_shell_equals_true",
            "issue_severity": "HIGH",
            "issue_text": "subprocess.call 使用 shell=True，存在命令注入风险",
            "filename": "app/runner.py",
            "line_number": 28,
            "issue_cwe": {"id": "CWE-78"}
        },
        {
            "test_id": "B301",
            "test_name": "blacklist_calls_pickle",
            "issue_severity": "MEDIUM",
            "issue_text": "检测到 pickle.loads 使用，反序列化可能导致远程代码执行",
            "filename": "app/cache.py",
            "line_number": 55,
            "issue_cwe": {"id": "CWE-502"}
        },
    ]
})

# 模拟的 Dockerfile 内容
MOCK_DOCKERFILE = """FROM python:latest
RUN pip install requests django==3.2
RUN export DATABASE_PASSWORD=s3cr3tPass123
RUN export API_KEY=sk_live_abc123def456
COPY . /app
WORKDIR /app
CMD ["python", "app.py"]
"""

# 模拟的 K8s YAML
MOCK_K8S_YAML = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: myapp:latest
        securityContext:
          privileged: true
          allowPrivilegeEscalation: true
        ports:
        - containerPort: 8080
"""

# 模拟的 requirements.txt
MOCK_REQUIREMENTS = """requests>=2.20.0
django==3.2.0
flask~=2.0
"""


def run_full_pipeline_demo():
    """
    运行完整的 CI/CD 安全流水线演示

    此函数串联所有扫描器，展示完整的 DevSecOps 流程。
    """
    print("=" * 70)
    print("  DevSecOps CI/CD 安全流水线 - 完整演示")
    print("=" * 70)

    # 创建临时测试文件
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="devsecops_")

    # 创建模拟项目结构
    project_dir = os.path.join(tmpdir, "test_project")
    os.makedirs(project_dir, exist_ok=True)

    # 写入模拟源码文件（含敏感信息）
    with open(os.path.join(project_dir, "config.py"), "w") as f:
        f.write('''# 应用配置文件
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
DB_URL = "mysql://admin:password123@db.example.com:3306/mydb"
PRIVATE_KEY = "-----BEGIN RSA PRIVATE KEY-----\\nMIIEpAIBAAKCAQEA..."
''')

    # 写入 .env 文件（模拟泄露）
    with open(os.path.join(project_dir, ".env"), "w") as f:
        f.write("SECRET_KEY=mysecretkey123\n")

    # 写入 Dockerfile
    dockerfile_path = os.path.join(project_dir, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(MOCK_DOCKERFILE)

    # 写入 K8s YAML
    k8s_yaml_path = os.path.join(project_dir, "deploy.yaml")
    with open(k8s_yaml_path, "w") as f:
        f.write(MOCK_K8S_YAML)

    # 写入 requirements.txt
    req_path = os.path.join(project_dir, "requirements.txt")
    with open(req_path, "w") as f:
        f.write(MOCK_REQUIREMENTS)

    # ---- 初始化安全门禁评估器 ----
    gate = SecurityGateEvaluator()

    # ---- 第一步：Git 仓库安全扫描 ----
    print("\n[阶段 1/5] Git 仓库安全扫描")
    git_scanner = GitRepoScanner(project_dir)
    git_result = git_scanner.scan()
    gate.add_result("GitRepoScanner", git_result)

    # ---- 第二步：SAST 安全扫描 ----
    print("\n[阶段 2/5] SAST 静态安全扫描")
    sast = SASTIntegrator()
    # 添加白名单（模拟误报抑制）
    sast.add_whitelist("app/file_downloader.py", ["python.lang.security.audit.ftp-request"])
    sast.parse_semgrep_result(MOCK_SEMGREP_OUTPUT)
    sast.parse_bandit_result(MOCK_BANDIT_OUTPUT)
    sast.deduplicate()
    sast.apply_whitelist()
    sast_result = ScanResult(
        scanner_name="SASTIntegrator",
        findings=sast.findings,
        scan_duration=1.5,
        total_files=50,
        scanned_files=48
    )
    gate.add_result("SASTIntegrator", sast_result)

    # ---- 第三步：依赖安全扫描 ----
    print("\n[阶段 3/5] 依赖安全扫描")
    dep_scanner = DependencyScanner()
    dep_scanner.parse_requirements_txt(req_path)
    dep_scanner.check_vulnerabilities()
    dep_scanner.check_licenses()
    dep_result = ScanResult(
        scanner_name="DependencyScanner",
        findings=dep_scanner.findings,
        scan_duration=0.8,
        total_files=1,
        scanned_files=1
    )
    gate.add_result("DependencyScanner", dep_result)

    # ---- 第四步：容器镜像安全扫描 ----
    print("\n[阶段 4/5] 容器镜像安全扫描")
    container_scanner = ContainerImageScanner()
    container_result = container_scanner.scan_dockerfile(dockerfile_path)
    container_scanner.simulate_layer_scan("myapp:latest")
    container_result.findings = container_scanner.findings
    gate.add_result("ContainerImageScanner", container_result)

    # 打印 CIS 合规报告
    cis_report = container_scanner.generate_cis_report()
    print(f"\n  CIS Docker Benchmark 合规率: {cis_report['compliance_rate']}")

    # ---- 第五步：Kubernetes 安全审计 ----
    print("\n[阶段 5/5] Kubernetes 安全审计")
    k8s_auditor = KubernetesAuditor()
    k8s_result = k8s_auditor.scan_yaml(k8s_yaml_path)
    gate.add_result("KubernetesAuditor", k8s_result)

    # ---- 安全门禁评估 ----
    print("\n[最终阶段] 安全门禁评估")
    gate_status, messages = gate.evaluate()

    # ---- 生成综合报告 ----
    report = gate.generate_markdown_report()
    report_path = os.path.join(tmpdir, "security_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n[*] 综合报告已保存: {report_path}")

    # 输出仪表盘数据
    dashboard = gate.generate_dashboard_data()
    dashboard_path = os.path.join(tmpdir, "dashboard.json")
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    print(f"[*] 仪表盘数据已保存: {dashboard_path}")

    # 清理临时文件
    import shutil
    shutil.rmtree(tmpdir)
    print(f"[*] 临时文件已清理: {tmpdir}")

    print("\n演示完成！")
    return gate_status


# ============================================================
#  第九部分：命令行入口
# ============================================================

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description="DevSecOps CI/CD 安全流水线实战工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 扫描 Git 仓库
  python %(prog)s scan --repo ./myproject

  # SAST 集成
  python %(prog)s sast --input semgrep.json

  # 依赖扫描
  python %(prog)s deps --file requirements.txt

  # Dockerfile 扫描
  python %(prog)s docker --file Dockerfile

  # K8s 审计
  python %(prog)s k8s --file deploy.yaml

  # 完整流水线演示
  python %(prog)s demo
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # scan 子命令——Git 仓库扫描
    scan_parser = subparsers.add_parser("scan", help="Git 仓库安全扫描")
    scan_parser.add_argument("--repo", required=True, help="Git 仓库路径")

    # sast 子命令——SAST 集成
    sast_parser = subparsers.add_parser("sast", help="SAST 扫描结果集成")
    sast_parser.add_argument("--input", required=True, help="Semgrep/Bandit JSON 结果文件")

    # deps 子命令——依赖扫描
    deps_parser = subparsers.add_parser("deps", help="依赖安全扫描")
    deps_parser.add_argument("--file", required=True, help="依赖文件路径")

    # docker 子命令——容器扫描
    docker_parser = subparsers.add_parser("docker", help="Dockerfile 安全扫描")
    docker_parser.add_argument("--file", required=True, help="Dockerfile 路径")

    # k8s 子命令——K8s 审计
    k8s_parser = subparsers.add_parser("k8s", help="Kubernetes 安全审计")
    k8s_parser.add_argument("--file", required=True, help="K8s YAML 文件路径")

    # gate 子命令——安全门禁评估
    gate_parser = subparsers.add_parser("gate", help="安全门禁评估")
    gate_parser.add_argument("--report", required=True, help="报告目录路径")

    # demo 子命令——完整演示
    subparsers.add_parser("demo", help="运行完整流水线演示")

    args = parser.parse_args()

    if args.command == "scan":
        # Git 仓库扫描
        scanner = GitRepoScanner(args.repo)
        result = scanner.scan()
        print("\n" + scanner.to_json())

    elif args.command == "sast":
        # SAST 集成
        sast = SASTIntegrator()
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
        sast.parse_semgrep_result(content)
        sast.deduplicate()
        passed, msg = sast.evaluate_gate()
        print(f"\n门禁状态: {'通过' if passed else '阻断'}")
        print(msg)
        print("\n" + sast.to_json())

    elif args.command == "deps":
        # 依赖扫描
        dep_scanner = DependencyScanner()
        ext = os.path.splitext(args.file)[1]
        if ext == ".txt":
            dep_scanner.parse_requirements_txt(args.file)
        elif args.file.endswith("package.json"):
            dep_scanner.parse_package_json(args.file)
        elif args.file.endswith("go.mod"):
            dep_scanner.parse_go_mod(args.file)
        dep_scanner.check_vulnerabilities()
        dep_scanner.check_licenses()
        print("\n" + dep_scanner.to_json())

    elif args.command == "docker":
        # Dockerfile 扫描
        container_scanner = ContainerImageScanner()
        result = container_scanner.scan_dockerfile(args.file)
        print(f"\n发现 {len(result.findings)} 个问题:")
        for f in result.findings:
            print(f"  [{f.severity}] {f.title} (行 {f.line_number})")
        cis_report = container_scanner.generate_cis_report()
        print(f"\nCIS 合规率: {cis_report['compliance_rate']}")

    elif args.command == "k8s":
        # K8s 审计
        k8s_auditor = KubernetesAuditor()
        result = k8s_auditor.scan_yaml(args.file)
        print(f"\n发现 {len(result.findings)} 个问题:")
        for f in result.findings:
            print(f"  [{f.severity}] {f.title}")
        print("\n" + k8s_auditor.to_json())

    elif args.command == "gate":
        # 安全门禁评估（从报告目录加载）
        gate = SecurityGateEvaluator()
        print("请先运行各扫描器生成结果，再汇总评估。")
        print("或运行 'demo' 子命令查看完整流程。")

    elif args.command == "demo":
        # 完整演示
        run_full_pipeline_demo()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
