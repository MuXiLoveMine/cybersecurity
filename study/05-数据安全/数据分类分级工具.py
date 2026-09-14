#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分类分级自动化工具

功能：
  - 基于正则模式匹配的自动数据分类（PII/金融/医疗等）
  - 敏感度评分
  - 分级标签生成
  - 分类报告输出（HTML/JSON）

用法：
  python 数据分类分级工具.py <目标路径> [--output report.html]
  python 数据分类分级工具.py scan /path/to/data
  python 数据分类分级工具.py classify "需要分析的文本内容"

依赖：
  pip install rich jinja2
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class DataCategory(Enum):
    """数据类别枚举"""
    PII = "个人身份信息"
    FINANCIAL = "金融数据"
    MEDICAL = "医疗健康数据"
    CREDENTIAL = "凭证数据"
    SENSITIVE = "敏感配置数据"
    NETWORK = "网络标识信息"
    BIOMETRIC = "生物识别信息"
    DEVICE = "设备标识信息"
    EDUCATION = "教育信息"
    LEGAL = "法律信息"
    GENERAL = "一般数据"


class DataLevel(Enum):
    """数据分级枚举"""
    L4 = ("核心数据", "国家安全/重大利益", 100)
    L3 = ("重要数据", "重要个人信息/敏感数据", 70)
    L2 = ("较重要数据", "一般个人信息", 40)
    L1 = ("一般数据", "非敏感数据", 10)

    def __init__(self, label: str, description: str, threshold: int):
        self.label = label
        self.description = description
        self.threshold = threshold


@dataclass
class MatchResult:
    """匹配结果"""
    category: DataCategory
    pattern_name: str
    matched_value: str
    position: int
    risk_score: int
    masked_value: str


@dataclass
class FileScanResult:
    """文件扫描结果"""
    file_path: str
    file_size: int
    file_hash: str
    total_matches: int
    matches: List[MatchResult] = field(default_factory=list)
    categories_found: Set[DataCategory] = field(default_factory=set)
    max_risk_score: int = 0
    data_level: DataLevel = DataLevel.L1
    summary: str = ""


class DataClassificationPatterns:
    """数据分类正则模式库"""

    PATTERNS = {
        DataCategory.PII: {
            "身份证号": {
                "regex": r"\b[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b",
                "risk": 80,
            },
            "护照号": {
                "regex": r"\b[EK]\d{8}\b",
                "risk": 70,
            },
            "军官证号": {
                "regex": r"\b(?:南|北|沈|兰|京|济|广|成|藏|新|海)\d{6,8}\b",
                "risk": 60,
            },
            "中国手机号": {
                "regex": r"\b1[3-9]\d{9}\b",
                "risk": 50,
            },
            "国际手机号": {
                "regex": r"\+\d{1,3}[\s\-]?\d{4,14}",
                "risk": 40,
            },
            "电子邮箱": {
                "regex": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "risk": 45,
            },
            "中文姓名": {
                "regex": r"[\u4e00-\u9fa5]{2,4}(?:先生|女士|同志|教授|医生|律师)",
                "risk": 35,
            },
            "家庭住址": {
                "regex": r"(?:[\u4e00-\u9fa5]{2,8}(?:省|市|区|县|镇|乡|村))+(?:\d+号)?(?:\d+室)?",
                "risk": 40,
            },
            "出生日期": {
                "regex": r"\b(?:19|20)\d{2}[-/年](?:0[1-9]|1[0-2])[-/月](?:0[1-9]|[12]\d|3[01])[日]?\b",
                "risk": 30,
            },
            "社保编号": {
                "regex": r"\b\d{3}-\d{2}-\d{4}\b",
                "risk": 65,
            },
        },

        DataCategory.FINANCIAL: {
            "银行卡号(16位)": {
                "regex": r"\b(?:4\d{15}|5[1-5]\d{14}|62\d{14}|622\d{13})\b",
                "risk": 85,
            },
            "银行卡号(19位)": {
                "regex": r"\b62\d{17}\b",
                "risk": 85,
            },
            "信用卡号": {
                "regex": r"\b(?:4\d{3}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}|5[1-5]\d{2}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4})\b",
                "risk": 90,
            },
            "银行账号": {
                "regex": r"\b\d{16,19}\b",
                "risk": 70,
            },
            "CVV码": {
                "regex": r"(?:CVV|CVC|安全码)[:\s]*(\d{3})",
                "risk": 95,
            },
            "支付宝账号": {
                "regex": r"\b(?:支付宝|alipay)[：:\s]*[\w@.-]+\b",
                "risk": 65,
            },
            "微信支付": {
                "regex": r"\b(?:微信支付|wxpay)[：:\s]*[\w]+\b",
                "risk": 60,
            },
            "加密货币地址": {
                "regex": r"\b(?:bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,34}\b",
                "risk": 55,
            },
            "以太坊地址": {
                "regex": r"\b0x[a-fA-F0-9]{40}\b",
                "risk": 55,
            },
        },

        DataCategory.MEDICAL: {
            "病历号": {
                "regex": r"\b(?:病历号|病案号|MRN)[：:\s]*\d{6,12}\b",
                "risk": 75,
            },
            "医保编号": {
                "regex": r"\b(?:医保|社保|医疗保险)[：:\s]*\d{8,20}\b",
                "risk": 70,
            },
            "诊断代码(ICD)": {
                "regex": r"\b[A-Z]\d{2}(?:\.\d{1,3})?\b",
                "risk": 50,
            },
            "处方信息": {
                "regex": r"\b(?:处方|Rx|医嘱)[：:\s]*[\u4e00-\u9fa5\w\s,，。]+",
                "risk": 65,
            },
            "医疗检查结果": {
                "regex": r"\b(?:(?:血|尿|便)常规|CT|MRI|B超|心电图|肝功能|肾功能)[：:\s]*[\d.\u4e00-\u9fa5]+",
                "risk": 60,
            },
        },

        DataCategory.CREDENTIAL: {
            "密码模式": {
                "regex": r"(?:password|passwd|pwd|密码|口令)[：:\s]*\S{6,}",
                "risk": 85,
            },
            "API密钥": {
                "regex": r"(?:api[_\-]?key|apikey)[：:\s=]+[A-Za-z0-9_\-]{20,}",
                "risk": 90,
            },
            "Access Key": {
                "regex": r"\bAKIA[0-9A-Z]{16}\b",
                "risk": 95,
            },
            "Secret Key": {
                "regex": r"\b[A-Za-z0-9/+=]{40}\b",
                "risk": 80,
            },
            "私钥文件标记": {
                "regex": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
                "risk": 100,
            },
            "JWT Token": {
                "regex": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
                "risk": 85,
            },
            "OAuth Token": {
                "regex": r"ya29\.[A-Za-z0-9_-]+",
                "risk": 85,
            },
            "Bearer Token": {
                "regex": r"Bearer\s+[A-Za-z0-9_\-.+=]+",
                "risk": 80,
            },
            "数据库连接串": {
                "regex": r"(?:mongodb|mysql|postgres|redis|amqp)://\w+:\w+@",
                "risk": 90,
            },
            "SSH连接串": {
                "regex": r"ssh://\w+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
                "risk": 70,
            },
        },

        DataCategory.SENSITIVE: {
            "内部IP地址": {
                "regex": r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b",
                "risk": 40,
            },
            "服务器配置": {
                "regex": r"(?:server_name|listen|proxy_pass|root|DocumentRoot)\s+\S+",
                "risk": 35,
            },
            "环境变量配置": {
                "regex": r"(?:DATABASE_URL|SECRET_KEY|API_SECRET|PRIVATE_KEY)\s*[=:]\s*\S+",
                "risk": 75,
            },
            "配置文件路径": {
                "regex": r"(?:/etc/|/var/|/opt/|/home/|C:\\(?:Windows|Users|Program))\S+",
                "risk": 25,
            },
            "内部域名": {
                "regex": r"\b[\w.-]+\.(?:internal|corp|local|intranet|lan)\b",
                "risk": 30,
            },
        },

        DataCategory.NETWORK: {
            "公网IP地址": {
                "regex": r"\b(?:(?!10\.|172\.(?:1[6-9]|2\d|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b",
                "risk": 20,
            },
            "MAC地址": {
                "regex": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
                "risk": 25,
            },
            "域名": {
                "regex": r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b",
                "risk": 15,
            },
            "URL": {
                "regex": r"https?://[^\s<>"']+",
                "risk": 15,
            },
            "端口号": {
                "regex": r"(?:port|端口)[:\s]*\d{2,5}\b",
                "risk": 10,
            },
        },

        DataCategory.BIOMETRIC: {
            "指纹数据": {
                "regex": r"(?:fingerprint|指纹|FP)[：:\s]*[A-Za-z0-9+/=]{50,}",
                "risk": 90,
            },
            "人脸特征": {
                "regex": r"(?:face_id|faceid|人脸|face_data)[：:\s]*[A-Za-z0-9+/=]{50,}",
                "risk": 90,
            },
            "虹膜数据": {
                "regex": r"(?:iris|虹膜)[：:\s]*[A-Za-z0-9+/=]{50,}",
                "risk": 90,
            },
            "声纹数据": {
                "regex": r"(?:voiceprint|声纹|voice_id)[：:\s]*[A-Za-z0-9+/=]{50,}",
                "risk": 85,
            },
        },

        DataCategory.DEVICE: {
            "IMEI号": {
                "regex": r"\b\d{15}\b",
                "risk": 45,
            },
            "IMSI号": {
                "regex": r"\b\d{12,15}\b",
                "risk": 50,
            },
            "Android ID": {
                "regex": r"\b[0-9a-f]{16}\b",
                "risk": 30,
            },
            "设备UUID": {
                "regex": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
                "risk": 25,
            },
            "设备序列号": {
                "regex": r"(?:serial|序列号|SN)[：:\s]*[A-Za-z0-9]{8,20}",
                "risk": 35,
            },
        },
    }

    @classmethod
    def get_all_patterns(cls) -> Dict[DataCategory, Dict]:
        return cls.PATTERNS


class DataClassifier:
    """数据分类分级引擎"""

    # 文件扩展名与预期内容的映射
    FILE_TYPE_MAP = {
        ".sql": "数据库导出文件",
        ".csv": "表格数据",
        ".json": "JSON数据",
        ".xml": "XML数据",
        ".log": "日志文件",
        ".conf": "配置文件",
        ".env": "环境配置",
        ".properties": "属性配置",
        ".yaml": "YAML配置",
        ".yml": "YAML配置",
        ".txt": "文本文件",
        ".xml": "XML文件",
    }

    # 最大文件读取大小 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self):
        self.patterns = DataClassificationPatterns.get_all_patterns()
        self._compile_patterns()
        self.results: List[FileScanResult] = []

    def _compile_patterns(self):
        """预编译所有正则表达式"""
        self.compiled_patterns: Dict[DataCategory, List[Tuple]] = {}
        for category, patterns in self.patterns.items():
            compiled = []
            for name, info in patterns.items():
                try:
                    compiled.append((name, re.compile(info["regex"]), info["risk"]))
                except re.error as e:
                    pass
            self.compiled_patterns[category] = compiled

    def classify_text(self, text: str) -> List[MatchResult]:
        """对文本内容进行分类匹配"""
        results = []

        for category, compiled_list in self.compiled_patterns.items():
            for name, pattern, risk in compiled_list:
                for match in pattern.finditer(text):
                    matched_value = match.group()
                    masked = self._mask_value(matched_value, name)
                    results.append(MatchResult(
                        category=category,
                        pattern_name=name,
                        matched_value=matched_value,
                        position=match.start(),
                        risk_score=risk,
                        masked_value=masked,
                    ))

        return results

    def _mask_value(self, value: str, pattern_name: str) -> str:
        """对敏感值进行脱敏处理"""
        if len(value) <= 2:
            return "*" * len(value)

        # 根据类型采用不同的脱敏策略
        if "身份证" in pattern_name:
            return value[:6] + "********" + value[-4:]
        elif "手机" in pattern_name or "电话" in pattern_name:
            return value[:3] + "****" + value[-4:]
        elif "银行卡" in pattern_name or "信用卡" in pattern_name:
            return value[:4] + "************" + value[-4:]
        elif "邮箱" in pattern_name:
            at = value.find("@")
            if at > 1:
                return value[0] + "***" + value[at:]
            return value[:1] + "***"
        elif "密码" in pattern_name or "密钥" in pattern_name or "key" in pattern_name.lower():
            return "*" * len(value)
        elif "IP" in pattern_name or "ip" in pattern_name.lower():
            parts = value.split(".")
            if len(parts) == 4:
                return parts[0] + "." + parts[1] + ".*.*"
        else:
            # 通用脱敏：保留首尾，中间用*替换
            mid_len = len(value) - 4
            if mid_len > 0:
                return value[:2] + "*" * min(mid_len, 10) + value[-2:]
            return "**" + value[-2:]

        return "*" * len(value)

    def scan_file(self, file_path: str) -> FileScanResult:
        """扫描单个文件"""
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            return FileScanResult(
                file_path=str(path),
                file_size=file_size,
                file_hash="N/A",
                total_matches=0,
                summary="文件过大，已跳过"
            )

        # 计算文件哈希
        file_hash = self._calculate_hash(path)

        # 读取文件内容
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return FileScanResult(
                file_path=str(path),
                file_size=file_size,
                file_hash=file_hash,
                total_matches=0,
                summary=f"读取失败: {e}"
            )

        # 执行分类
        matches = self.classify_text(content)

        # 构建结果
        result = FileScanResult(
            file_path=str(path),
            file_size=file_size,
            file_hash=file_hash,
            total_matches=len(matches),
            matches=matches,
        )

        # 统计类别
        for m in matches:
            result.categories_found.add(m.category)

        # 计算最高风险分
        if matches:
            result.max_risk_score = max(m.risk_score for m in matches)
        else:
            result.max_risk_score = 0

        # 确定数据级别
        result.data_level = self._determine_level(result.max_risk_score)

        # 生成摘要
        result.summary = self._generate_summary(result)

        return result

    def scan_directory(self, dir_path: str, recursive: bool = True) -> List[FileScanResult]:
        """扫描目录"""
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"目录不存在: {dir_path}")

        results = []
        files = path.rglob("*") if recursive else path.glob("*")

        for f in files:
            if f.is_file() and f.suffix.lower() in [
                ".txt", ".csv", ".json", ".xml", ".log",
                ".conf", ".env", ".yaml", ".yml", ".properties",
                ".sql", ".ini", ".cfg", ".md"
            ]:
                try:
                    result = self.scan_file(str(f))
                    results.append(result)
                except Exception as e:
                    pass

        return results

    def _calculate_hash(self, path: Path) -> str:
        """计算文件SHA256哈希"""
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
        except Exception:
            return "ERROR"
        return h.hexdigest()[:16]

    def _determine_level(self, max_risk: int) -> DataLevel:
        """根据最高风险分确定数据级别"""
        for level in reversed(list(DataLevel)):
            if max_risk >= level.threshold:
                return level
        return DataLevel.L1

    def _generate_summary(self, result: FileScanResult) -> str:
        """生成文件扫描摘要"""
        if result.total_matches == 0:
            return "未发现敏感数据"

        parts = []
        for cat in result.categories_found:
            count = sum(1 for m in result.matches if m.category == cat)
            parts.append(f"{cat.value}({count}项)")

        level = result.data_level
        return f"发现{result.total_matches}项敏感数据，涉及: {', '.join(parts)}，级别: {level.label}"

    def generate_html_report(self, results: List[FileScanResult], output_path: str):
        """生成HTML分类报告"""
        # 统计信息
        total_files = len(results)
        files_with_sensitive = sum(1 for r in results if r.total_matches > 0)
        total_matches = sum(r.total_matches for r in results)

        # 按类别统计
        category_stats = defaultdict(int)
        for r in results:
            for m in r.matches:
                category_stats[m.category.value] += 1

        # 按级别统计
        level_stats = defaultdict(int)
        for r in results:
            if r.total_matches > 0:
                level_stats[r.data_level.label] += 1

        # 生成HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>数据分类分级报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; background: white; }}
        th {{ background: #2c3e50; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 200px; }}
        .card h3 {{ margin: 0; color: #2c3e50; font-size: 14px; }}
        .card .number {{ font-size: 36px; font-weight: bold; color: #3498db; margin: 10px 0 0 0; }}
        .level-l4 {{ background: #e74c3c; color: white; }}
        .level-l3 {{ background: #e67e22; color: white; }}
        .level-l2 {{ background: #f1c40f; }}
        .level-l1 {{ background: #2ecc71; color: white; }}
        .category-bar {{ display: inline-block; width: 200px; height: 20px; background: #3498db; border-radius: 3px; margin-right: 10px; }}
    </style>
</head>
<body>
    <h1>数据分类分级自动化报告</h1>
    <p>生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="summary">
        <div class="card"><h3>扫描文件总数</h3><div class="number">{total_files}</div></div>
        <div class="card"><h3>含敏感数据文件</h3><div class="number" style="color:#e67e22">{files_with_sensitive}</div></div>
        <div class="card"><h3>敏感数据项</h3><div class="number" style="color:#e74c3c">{total_matches}</div></div>
    </div>
"""

        # 数据级别分布
        html += "    <h2>数据级别分布</h2>\n    <table>\n        <tr><th>级别</th><th>描述</th><th>文件数</th></tr>\n"
        for level in DataLevel:
            count = level_stats.get(level.label, 0)
            css_class = f"level-{level.name.lower()}"
            html += f'        <tr class="{css_class}"><td>{level.label}</td><td>{level.description}</td><td>{count}</td></tr>\n'
        html += "    </table>\n"

        # 数据类别分布
        html += "    <h2>数据类别分布</h2>\n    <table>\n        <tr><th>类别</th><th>匹配数</th><th>占比</th></tr>\n"
        for cat_name, count in sorted(category_stats.items(), key=lambda x: -x[1]):
            pct = (count / total_matches * 100) if total_matches > 0 else 0
            bar_width = int(pct)
            html += f'        <tr><td>{cat_name}</td><td>{count}</td><td><span class="category-bar" style="width:{bar_width * 2}px"></span>{pct:.1f}%</td></tr>\n'
        html += "    </table>\n"

        # 文件详情
        html += "    <h2>文件扫描详情</h2>\n    <table>\n        <tr><th>文件路径</th><th>大小</th><th>匹配数</th><th>最高风险</th><th>级别</th><th>摘要</th></tr>\n"
        for r in sorted(results, key=lambda x: -x.max_risk_score):
            size_kb = r.file_size / 1024
            level_class = f"level-{r.data_level.name.lower()}"
            html += f'        <tr class="{level_class}"><td>{r.file_path}</td><td>{size_kb:.1f}KB</td><td>{r.total_matches}</td><td>{r.max_risk_score}</td><td>{r.data_level.label}</td><td>{r.summary}</td></tr>\n'
        html += "    </table>\n"

        # 敏感数据详情（仅显示前100项）
        html += "    <h2>敏感数据匹配详情（前100项）</h2>\n    <table>\n        <tr><th>文件</th><th>类别</th><th>模式名称</th><th>脱敏值</th><th>风险分</th><th>位置</th></tr>\n"
        all_matches = []
        for r in results:
            for m in r.matches:
                all_matches.append((r.file_path, m))
        for file_path, m in sorted(all_matches, key=lambda x: -x[1].risk_score)[:100]:
            html += f'        <tr><td>{Path(file_path).name}</td><td>{m.category.value}</td><td>{m.pattern_name}</td><td>{m.masked_value}</td><td>{m.risk_score}</td><td>{m.position}</td></tr>\n'
        html += "    </table>\n"

        html += "</body>\n</html>"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    def generate_json_report(self, results: List[FileScanResult], output_path: str):
        """生成JSON报告"""
        report = {
            "report_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_files": len(results),
                "files_with_sensitive": sum(1 for r in results if r.total_matches > 0),
                "total_matches": sum(r.total_matches for r in results),
            },
            "files": [],
        }

        for r in results:
            file_data = {
                "file_path": r.file_path,
                "file_size": r.file_size,
                "file_hash": r.file_hash,
                "total_matches": r.total_matches,
                "max_risk_score": r.max_risk_score,
                "data_level": r.data_level.label,
                "categories": [c.value for c in r.categories_found],
                "summary": r.summary,
                "matches": [],
            }
            for m in r.matches:
                file_data["matches"].append({
                    "category": m.category.value,
                    "pattern_name": m.pattern_name,
                    "masked_value": m.masked_value,
                    "risk_score": m.risk_score,
                    "position": m.position,
                })
            report["files"].append(file_data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="数据分类分级自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python 数据分类分级工具.py scan /path/to/data --output report.html
  python 数据分类分级工具.py classify "文本内容"
  python 数据分类分级工具.py scan ./config --json results.json
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # scan子命令
    scan_parser = subparsers.add_parser("scan", help="扫描文件或目录")
    scan_parser.add_argument("path", help="目标文件或目录路径")
    scan_parser.add_argument("--output", "-o", default="classification_report.html",
                            help="HTML报告输出路径")
    scan_parser.add_argument("--json", "-j", help="JSON报告输出路径")
    scan_parser.add_argument("--no-recursive", action="store_true",
                            help="不递归扫描子目录")

    # classify子命令
    classify_parser = subparsers.add_parser("classify", help="分析文本内容")
    classify_parser.add_argument("text", help="要分析的文本内容")
    classify_parser.add_argument("--json", "-j", help="JSON结果输出路径")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    classifier = DataClassifier()

    if args.command == "scan":
        print("=" * 60)
        print("数据分类分级扫描")
        print(f"目标: {args.path}")
        print("=" * 60)

        if os.path.isfile(args.path):
            results = [classifier.scan_file(args.path)]
        elif os.path.isdir(args.path):
            results = classifier.scan_directory(args.path, recursive=not args.no_recursive)
        else:
            print(f"错误: 路径不存在: {args.path}", file=sys.stderr)
            sys.exit(1)

        print(f"\n扫描完成，共扫描 {len(results)} 个文件")
        print(f"含敏感数据文件: {sum(1 for r in results if r.total_matches > 0)}")
        print(f"敏感数据项总数: {sum(r.total_matches for r in results)}")

        for r in results:
            if r.total_matches > 0:
                print(f"\n  [{r.data_level.label}] {r.file_path}")
                print(f"    {r.summary}")
                for m in r.matches[:5]:
                    print(f"    - {m.category.value} / {m.pattern_name}: {m.masked_value} (风险: {m.risk_score})")
                if r.total_matches > 5:
                    print(f"    ... 还有 {r.total_matches - 5} 项")

        # 生成报告
        classifier.generate_html_report(results, args.output)
        print(f"\nHTML报告已保存: {args.output}")

        if args.json:
            classifier.generate_json_report(results, args.json)
            print(f"JSON报告已保存: {args.json}")

    elif args.command == "classify":
        print("=" * 60)
        print("文本分类分析")
        print("=" * 60)

        matches = classifier.classify_text(args.text)

        if not matches:
            print("未发现敏感数据")
        else:
            print(f"发现 {len(matches)} 项敏感数据:\n")
            for m in matches:
                print(f"  [{m.category.value}] {m.pattern_name}")
                print(f"    脱敏值: {m.masked_value}")
                print(f"    风险分: {m.risk_score}")
                print()

        if args.json:
            report = {
                "matches": [
                    {
                        "category": m.category.value,
                        "pattern_name": m.pattern_name,
                        "masked_value": m.masked_value,
                        "risk_score": m.risk_score,
                        "position": m.position,
                    }
                    for m in matches
                ]
            }
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"JSON结果已保存: {args.json}")

    print("\n分析完成。")


if __name__ == "__main__":
    main()
