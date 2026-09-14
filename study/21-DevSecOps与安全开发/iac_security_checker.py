#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IaC 安全检查工具 (IaC Security Checker)
=========================================

功能概述：
  - 解析 Terraform (.tf) 和 CloudFormation (.json/.yaml/.yml) 配置文件
  - 检测常见 IaC 安全风险，包括：
    1. 安全组规则过于开放（0.0.0.0/0 入站）
    2. IAM 策略过度授权（Action: * 或 Resource: *）
    3. 存储资源未加密（EBS / S3 / RDS）
    4. 日志记录未启用（CloudTrail / S3 访问日志）
    5. 硬编码密钥与凭证（AWS Key ID、私钥、API Token）
    6. 资源公开暴露（S3 Bucket 公开读写、RDS 公开访问）
    7. 弱密码/默认密码（RDS 密码、数据库密码）
    8. 缺少网络隔离（子网无 NAT 网关、安全组无出站限制）

使用方式：
  python iac_security_checker.py <目录或文件路径> [--format json|text|html] [--output report.txt]

依赖：
  pip install pyyaml hcl2

作者: 网络安全学习项目
"""

import os
import re
import json
import hashlib
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# 尝试导入可选依赖（若缺失则降级处理）
# ============================================================================

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None

try:
    import hcl2
    HAS_HCL2 = True
except ImportError:
    HAS_HCL2 = False
    hcl2 = None


# ============================================================================
# 数据模型定义
# ============================================================================

class SeverityLevel(Enum):
    """漏洞严重等级"""
    CRITICAL = "严重"
    HIGH = "高危"
    MEDIUM = "中危"
    LOW = "低危"
    INFO = "提示"

    def __str__(self):
        return self.value

    @property
    def score(self) -> int:
        """获取严重等级分数，用于排序"""
        scores = {
            SeverityLevel.CRITICAL: 4,
            SeverityLevel.HIGH: 3,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 1,
            SeverityLevel.INFO: 0
        }
        return scores[self]


@dataclass
class SecurityFinding:
    """安全发现（检测结果）"""
    rule_id: str                    # 规则编号
    rule_name: str                   # 规则名称
    severity: SeverityLevel          # 严重等级
    description: str                 # 问题描述
    file_path: str                   # 文件路径
    line_number: int                 # 行号（如果可确定）
    resource_type: str               # 资源类型
    resource_name: str               # 资源名称
    remediation: str                 # 修复建议
    cwe_id: str = ""                 # CWE 编号
    details: Dict[str, Any] = field(default_factory=dict)  # 额外细节


@dataclass
class ScanReport:
    """扫描报告"""
    scan_time: str
    target_path: str
    total_files: int
    total_findings: int
    findings: List[SecurityFinding]
    summary: Dict[str, int]

    def __post_init__(self):
        """计算统计摘要"""
        self.summary = {}
        for level in SeverityLevel:
            count = len([f for f in self.findings if f.severity == level])
            self.summary[level.name] = count
        self.total_findings = len(self.findings)


# ============================================================================
# 检测规则基类
# ============================================================================

class IaCRule:
    """IaC 安全检测规则基类"""
    
    def __init__(self):
        self.rule_id: str = ""
        self.rule_name: str = ""
        self.severity: SeverityLevel = SeverityLevel.INFO
        self.description: str = ""
        self.remediation: str = ""
        self.cwe_id: str = ""

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        """检查 Terraform 配置"""
        return []

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        """检查 CloudFormation 配置"""
        return []

    def _create_finding(self, file_path: str, line: int, rtype: str, 
                        rname: str, details: Dict = None) -> SecurityFinding:
        """创建安全发现对象"""
        return SecurityFinding(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            severity=self.severity,
            description=self.description,
            file_path=file_path,
            line_number=line,
            resource_type=rtype,
            resource_name=rname,
            remediation=self.remediation,
            cwe_id=self.cwe_id,
            details=details or {}
        )


# ============================================================================
# 规则 1: 安全组规则过于开放
# ============================================================================

class OpenSecurityGroupRule(IaCRule):
    """检测安全组入站规则对 0.0.0.0/0 开放敏感端口"""

    SENSITIVE_PORTS = {
        '22': 'SSH',
        '3389': 'RDP',
        '3306': 'MySQL',
        '5432': 'PostgreSQL',
        '1433': 'SQL Server',
        '6379': 'Redis',
        '27017': 'MongoDB',
        '9200': 'Elasticsearch',
        '5601': 'Kibana',
        '8080': 'HTTP-Alt',
        '8443': 'HTTPS-Alt',
        '11211': 'Memcached',
        '9042': 'Cassandra',
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-001"
        self.rule_name = "安全组规则过于开放"
        self.severity = SeverityLevel.HIGH
        self.description = "安全组入站规则允许 0.0.0.0/0 访问敏感端口，可能导致未授权访问"
        self.remediation = "限制 CIDR 范围到特定 IP 段，仅允许必要的来源地址访问敏感端口"
        self.cwe_id = "CWE-284"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                if 'aws_security_group' not in rtype and 'aws_security_group_rule' not in rtype:
                    continue
                    
                for rname, config in rdata.items():
                    if not isinstance(config, dict):
                        continue
                    
                    # 检查 ingress 规则
                    ingress_rules = config.get('ingress', [])
                    if isinstance(ingress_rules, dict):
                        ingress_rules = [ingress_rules]
                    
                    for rule in ingress_rules:
                        if not isinstance(rule, dict):
                            continue
                        cidr_blocks = rule.get('cidr_blocks', [])
                        if isinstance(cidr_blocks, str):
                            cidr_blocks = [cidr_blocks]
                        
                        for cidr in cidr_blocks:
                            if cidr == '0.0.0.0/0' or cidr == '::/0':
                                ports = rule.get('from_port', [0])
                                if isinstance(ports, (int, str)):
                                    ports = [ports]
                                
                                for port in ports:
                                    port_str = str(port)
                                    if port_str in self.SENSITIVE_PORTS:
                                        findings.append(self._create_finding(
                                            file_path=file_path,
                                            line=0,
                                            rtype=rtype,
                                            rname=rname,
                                            details={
                                                'port': port_str,
                                                'service': self.SENSITIVE_PORTS[port_str],
                                                'cidr': cidr,
                                                'protocol': rule.get('protocol', 'tcp')
                                            }
                                        ))
                                    elif port_str == '0':
                                        # 所有端口
                                        findings.append(self._create_finding(
                                            file_path=file_path,
                                            line=0,
                                            rtype=rtype,
                                            rname=rname,
                                            details={
                                                'port': 'all',
                                                'service': '所有端口',
                                                'cidr': cidr,
                                                'protocol': rule.get('protocol', '-1')
                                            }
                                        ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            if 'SecurityGroup' not in rtype:
                continue
            
            properties = rdef.get('Properties', {})
            
            # AWS::EC2::SecurityGroup
            if rtype == 'AWS::EC2::SecurityGroup':
                ingress_rules = properties.get('SecurityGroupIngress', [])
                if isinstance(ingress_rules, dict):
                    ingress_rules = [ingress_rules]
                
                for rule in ingress_rules:
                    cidr = rule.get('CidrIp', '')
                    if cidr in ('0.0.0.0/0', '::/0'):
                        port = rule.get('FromPort', 0)
                        port_str = str(port)
                        if port_str in self.SENSITIVE_PORTS:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'port': port_str,
                                    'service': self.SENSITIVE_PORTS[port_str],
                                    'cidr': cidr
                                }
                            ))
            
            # AWS::EC2::SecurityGroupIngress
            elif rtype == 'AWS::EC2::SecurityGroupIngress':
                cidr = properties.get('CidrIp', '')
                if cidr in ('0.0.0.0/0', '::/0'):
                    port = properties.get('FromPort', 0)
                    port_str = str(port)
                    if port_str in self.SENSITIVE_PORTS:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line=0,
                            rtype=rtype,
                            rname=rname,
                            details={
                                'port': port_str,
                                'service': self.SENSITIVE_PORTS[port_str],
                                'cidr': cidr
                            }
                        ))
        
        return findings


# ============================================================================
# 规则 2: IAM 策略过度授权
# ============================================================================

class OverPrivilegedIAMRule(IaCRule):
    """检测 IAM 策略中的过度授权（Action: * 或 Resource: *）"""

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-002"
        self.rule_name = "IAM 策略过度授权"
        self.severity = SeverityLevel.CRITICAL
        self.description = "IAM 策略授予了过于宽泛的权限（Action: * 或 Resource: *），违反最小权限原则"
        self.remediation = "遵循最小权限原则，仅授予必要的 Action 和特定 Resource ARN"
        self.cwe_id = "CWE-269"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                if 'iam_role' in rtype or 'iam_policy' in rtype or 'iam_user' in rtype:
                    for rname, config in rdata.items():
                        if not isinstance(config, dict):
                            continue
                        
                        # 检查内联策略
                        policy_data = config.get('policy', {})
                        if isinstance(policy_data, list):
                            policy_data = policy_data[0] if policy_data else {}
                        
                        statements = self._extract_policy_statements(policy_data)
                        for stmt in statements:
                            actions = stmt.get('actions', stmt.get('Action', []))
                            resources_arn = stmt.get('resources', stmt.get('Resource', []))
                            
                            if isinstance(actions, str):
                                actions = [actions]
                            if isinstance(resources_arn, str):
                                resources_arn = [resources_arn]
                            
                            has_wildcard_action = '*' in actions
                            has_wildcard_resource = '*' in resources_arn
                            
                            if has_wildcard_action or has_wildcard_resource:
                                findings.append(self._create_finding(
                                    file_path=file_path,
                                    line=0,
                                    rtype=rtype,
                                    rname=rname,
                                    details={
                                        'wildcard_action': has_wildcard_action,
                                        'wildcard_resource': has_wildcard_resource,
                                        'actions': actions[:5],
                                        'resources': resources_arn[:5]
                                    }
                                ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            if 'IAM' not in rtype:
                continue
            
            properties = rdef.get('Properties', {})
            
            # 检查 ManagedPolicyArns
            managed_policies = properties.get('ManagedPolicyArns', [])
            if isinstance(managed_policies, str):
                managed_policies = [managed_policies]
            for arn in managed_policies:
                if 'AdministratorAccess' in arn or arn.endswith(':*'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={
                            'issue': '管理员策略或通配符策略',
                            'policy_arn': arn
                        }
                    ))
            
            # 检查内联策略
            policies = properties.get('Policies', [])
            if isinstance(policies, dict):
                policies = [policies]
            
            for policy in policies:
                policy_doc = policy.get('PolicyDocument', {})
                statements = policy_doc.get('Statement', [])
                if isinstance(statements, dict):
                    statements = [statements]
                
                for stmt in statements:
                    actions = stmt.get('Action', [])
                    resources_arn = stmt.get('Resource', [])
                    
                    if isinstance(actions, str):
                        actions = [actions]
                    if isinstance(resources_arn, str):
                        resources_arn = [resources_arn]
                    
                    has_wildcard_action = '*' in actions
                    has_wildcard_resource = '*' in resources_arn
                    
                    if has_wildcard_action or has_wildcard_resource:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line=0,
                            rtype=rtype,
                            rname=rname,
                            details={
                                'wildcard_action': has_wildcard_action,
                                'wildcard_resource': has_wildcard_resource,
                                'actions': actions[:5],
                                'resources': resources_arn[:5]
                            }
                        ))
        
        return findings

    def _extract_policy_statements(self, policy_data: Dict) -> List[Dict]:
        """从策略数据中提取语句"""
        if not isinstance(policy_data, dict):
            return []
        
        policy_doc = policy_data.get('policy_document', policy_data)
        if isinstance(policy_doc, list):
            policy_doc = policy_doc[0] if policy_doc else {}
        
        if not isinstance(policy_doc, dict):
            return []
        
        statements = policy_doc.get('statement', policy_doc.get('Statement', []))
        if isinstance(statements, dict):
            statements = [statements]
        if isinstance(statements, list):
            # 统一 key 为小写
            normalized = []
            for s in statements:
                if isinstance(s, dict):
                    normalized.append({k.lower(): v for k, v in s.items()})
            return normalized
        return []


# ============================================================================
# 规则 3: 存储资源未加密
# ============================================================================

class UnencryptedStorageRule(IaCRule):
    """检测存储资源（S3 Bucket、EBS Volume、RDS）未启用加密"""

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-003"
        self.rule_name = "存储资源未加密"
        self.severity = SeverityLevel.HIGH
        self.description = "存储资源未启用加密，可能导致敏感数据泄露"
        self.remediation = "为所有存储资源启用加密：S3 启用 server-side encryption，EBS 启用 KMS 加密，RDS 启用 storage encryption"
        self.cwe_id = "CWE-311"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                for rname, config in rdata.items():
                    if not isinstance(config, dict):
                        continue
                    
                    # S3 Bucket 未加密
                    if 'aws_s3_bucket' in rtype:
                        server_side = config.get('server_side_encryption_configuration', [])
                        if not server_side or len(server_side) == 0:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'issue': 'S3 Bucket 未配置服务器端加密',
                                    'recommendation': '添加 server_side_encryption_configuration 块'
                                }
                            ))
                    
                    # EBS Volume 未加密
                    if 'aws_ebs_volume' in rtype:
                        encrypted = config.get('encrypted', [False])
                        if isinstance(encrypted, list):
                            encrypted = encrypted[0] if encrypted else False
                        if not encrypted:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'issue': 'EBS Volume 未启用加密',
                                    'recommendation': '设置 encrypted = true'
                                }
                            ))
                    
                    # RDS 实例未加密
                    if 'aws_db_instance' in rtype:
                        storage_encrypted = config.get('storage_encrypted', [False])
                        if isinstance(storage_encrypted, list):
                            storage_encrypted = storage_encrypted[0] if storage_encrypted else False
                        if not storage_encrypted:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'issue': 'RDS 实例存储未加密',
                                    'recommendation': '设置 storage_encrypted = true'
                                }
                            ))
                    
                    # DynamoDB 表未加密
                    if 'aws_dynamodb_table' in rtype:
                        server_side = config.get('server_side_encryption', [])
                        if not server_side or len(server_side) == 0:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'issue': 'DynamoDB 表未启用加密',
                                    'recommendation': '添加 server_side_encryption 块'
                                }
                            ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            properties = rdef.get('Properties', {})
            
            # S3 Bucket
            if rtype == 'AWS::S3::Bucket':
                bucket_enc = properties.get('BucketEncryption', {})
                if not bucket_enc:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={'issue': 'S3 Bucket 未配置加密'}
                    ))
            
            # EBS Volume
            elif rtype == 'AWS::EC2::Volume':
                encrypted = properties.get('Encrypted', False)
                if not encrypted:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={'issue': 'EBS Volume 未启用加密'}
                    ))
            
            # RDS Instance
            elif rtype in ('AWS::RDS::DBInstance', 'AWS::RDS::DBCluster'):
                storage_encrypted = properties.get('StorageEncrypted', False)
                if not storage_encrypted:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={'issue': 'RDS 存储未加密'}
                    ))
            
            # DynamoDB Table
            elif rtype == 'AWS::DynamoDB::Table':
                sse_spec = properties.get('SSESpecification', {})
                if not sse_spec.get('SSEEnabled', False):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={'issue': 'DynamoDB 表未启用加密'}
                    ))
        
        return findings


# ============================================================================
# 规则 4: 日志记录未启用
# ============================================================================

class DisabledLoggingRule(IaCRule):
    """检测云服务日志记录未启用（CloudTrail、S3 访问日志、VPC Flow Logs）"""

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-004"
        self.rule_name = "日志记录未启用"
        self.severity = SeverityLevel.MEDIUM
        self.description = "云资源日志记录未启用，可能导致安全事件无法追溯"
        self.remediation = "启用 CloudTrail、S3 访问日志和 VPC Flow Logs 等关键日志服务"
        self.cwe_id = "CWE-778"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        has_cloudtrail = False
        has_vpc_flow_log = False
        s3_buckets = []
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                if 'aws_cloudtrail' in rtype:
                    has_cloudtrail = True
                if 'aws_flow_log' in rtype:
                    has_vpc_flow_log = True
                if 'aws_s3_bucket' in rtype:
                    for rname, config in rdata.items():
                        if isinstance(config, dict):
                            s3_buckets.append((rname, config))
        
        if not has_cloudtrail:
            findings.append(self._create_finding(
                file_path=file_path,
                line=0,
                rtype='N/A',
                rname='N/A',
                details={'issue': '未配置 AWS CloudTrail，API 调用无法审计'}
            ))
        
        # 检查 S3 Bucket 是否启用访问日志
        for bname, bconfig in s3_buckets:
            logging_config = bconfig.get('logging', [])
            if not logging_config or len(logging_config) == 0:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line=0,
                    rtype='aws_s3_bucket',
                    rname=bname,
                    details={'issue': 'S3 Bucket 未启用访问日志'}
                ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        has_cloudtrail = False
        has_vpc_flow_log = False
        s3_buckets = []
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            if rtype == 'AWS::CloudTrail::Trail':
                has_cloudtrail = True
            elif rtype == 'AWS::EC2::FlowLog':
                has_vpc_flow_log = True
            elif rtype == 'AWS::S3::Bucket':
                s3_buckets.append((rname, rdef.get('Properties', {})))
        
        if not has_cloudtrail:
            findings.append(self._create_finding(
                file_path=file_path,
                line=0,
                rtype='N/A',
                rname='N/A',
                details={'issue': '未配置 AWS CloudTrail'}
            ))
        
        for bname, bprops in s3_buckets:
            logging_cfg = bprops.get('LoggingConfiguration', {})
            if not logging_cfg:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line=0,
                    rtype='AWS::S3::Bucket',
                    rname=bname,
                    details={'issue': 'S3 Bucket 未启用访问日志'}
                ))
        
        return findings


# ============================================================================
# 规则 5: 硬编码密钥与凭证
# ============================================================================

class HardcodedSecretsRule(IaCRule):
    """检测配置文件中的硬编码密钥和凭证"""

    # AWS Access Key ID 模式
    AWS_KEY_PATTERN = re.compile(r'AKIA[0-9A-Z]{16}')
    # AWS Secret Access Key 模式（40 字符 base64）
    AWS_SECRET_PATTERN = re.compile(r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+]{40}(?![A-Za-z0-9/+=])')
    # 私钥模式
    PRIVATE_KEY_PATTERN = re.compile(r'-----BEGIN (RSA |EC |DSA |OPENSSH |)PRIVATE KEY-----')
    # 通用密码/密钥赋值
    PASSWORD_PATTERN = re.compile(r'(password|passwd|pwd|secret|api_key|apikey|access_key|token)\s*[=:]\s*["\']?([^\s"\']{8,})["\']?', re.IGNORECASE)
    # 数据库连接字符串
    DB_CONN_PATTERN = re.compile(r'(mongodb|postgresql|mysql|redis)://[^\s:]+:([^\s@]+)@', re.IGNORECASE)

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-005"
        self.rule_name = "硬编码密钥与凭证"
        self.severity = SeverityLevel.CRITICAL
        self.description = "在 IaC 配置文件中检测到硬编码的密钥、密码或凭证"
        self.remediation = "使用变量引用、密钥管理服务（AWS Secrets Manager / SSM Parameter Store）或环境变量管理凭证"
        self.cwe_id = "CWE-798"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        # Terraform HCL 的硬编码检测主要通过原始文本
        return []

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        # CloudFormation 也需要通过原始文本检测
        return []

    def check_raw_text(self, content: str, file_path: str) -> List[SecurityFinding]:
        """检查原始文本内容中的硬编码凭证"""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 跳过注释行和变量引用行
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                continue
            if 'var.' in line or 'data.aws_secretsmanager' in line or 'resolve(ssm:' in line:
                continue
            if '${' in line and '}' in line:
                continue  # 变量插值
            
            # AWS Access Key ID
            aws_keys = self.AWS_KEY_PATTERN.findall(line)
            for key in aws_keys:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line=line_num,
                    rtype='Credential',
                    rname='AWSAccessKeyId',
                    details={
                        'type': 'AWS Access Key ID',
                        'value_masked': key[:7] + '*' * 9
                    }
                ))
            
            # 私钥
            if self.PRIVATE_KEY_PATTERN.search(line):
                findings.append(self._create_finding(
                    file_path=file_path,
                    line=line_num,
                    rtype='Credential',
                    rname='PrivateKey',
                    details={'type': '私钥内容'}
                ))
            
            # 通用密码赋值
            password_matches = self.PASSWORD_PATTERN.findall(line)
            for attr, value in password_matches:
                # 过滤明显非密钥的值
                if value.lower() in ('changeme', 'placeholder', 'example', 'your_password_here'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=line_num,
                        rtype='Credential',
                        rname=attr,
                        details={
                            'type': '密码/密钥赋值',
                            'attribute': attr,
                            'value_masked': value[:2] + '*' * (len(value) - 2) if len(value) > 2 else '**'
                        }
                    ))
                elif len(value) >= 8 and not value.startswith('${'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=line_num,
                        rtype='Credential',
                        rname=attr,
                        details={
                            'type': '密码/密钥赋值',
                            'attribute': attr,
                            'value_masked': value[:2] + '*' * (len(value) - 2) if len(value) > 2 else '**'
                        }
                    ))
            
            # 数据库连接字符串
            db_matches = self.DB_CONN_PATTERN.findall(line)
            for db_type, password in db_matches:
                findings.append(self._create_finding(
                    file_path=file_path,
                    line=line_num,
                    rtype='Credential',
                    rname='DatabaseConnection',
                    details={
                        'type': f'{db_type} 连接字符串中的密码',
                        'value_masked': '*' * len(password)
                    }
                ))
        
        return findings


# ============================================================================
# 规则 6: S3 Bucket 公开访问
# ============================================================================

class PublicS3BucketRule(IaCRule):
    """检测 S3 Bucket 公开读写权限"""

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-006"
        self.rule_name = "S3 Bucket 公开访问"
        self.severity = SeverityLevel.CRITICAL
        self.description = "S3 Bucket 配置了公开读写权限，可能导致数据泄露"
        self.remediation = "移除公开 ACL，启用 Block Public Access，使用 Bucket Policy 精确控制访问"
        self.cwe_id = "CWE-284"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                # S3 Bucket ACL
                if 'aws_s3_bucket_acl' in rtype:
                    for rname, config in rdata.items():
                        if not isinstance(config, dict):
                            continue
                        acl = config.get('acl', ['private'])
                        if isinstance(acl, list):
                            acl = acl[0] if acl else 'private'
                        if acl in ('public-read', 'public-read-write', 'website'):
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'acl': acl,
                                    'risk': '公开访问' if acl == 'public-read' else '公开读写'
                                }
                            ))
                
                # S3 Bucket 公开策略
                if 'aws_s3_bucket_policy' in rtype:
                    for rname, config in rdata.items():
                        if not isinstance(config, dict):
                            continue
                        policy = config.get('policy', {})
                        if isinstance(policy, str):
                            try:
                                policy = json.loads(policy)
                            except (json.JSONDecodeError, TypeError):
                                policy = {}
                        statements = policy.get('Statement', []) if isinstance(policy, dict) else []
                        if isinstance(statements, dict):
                            statements = [statements]
                        
                        for stmt in statements:
                            if not isinstance(stmt, dict):
                                continue
                            principal = stmt.get('Principal', {})
                            if isinstance(principal, str) and principal == '*':
                                findings.append(self._create_finding(
                                    file_path=file_path,
                                    line=0,
                                    rtype=rtype,
                                    rname=rname,
                                    details={
                                        'issue': 'Bucket Policy 授予 Principal: * 权限',
                                        'effect': stmt.get('Effect', 'Allow')
                                    }
                                ))
                            elif isinstance(principal, dict) and principal.get('AWS') == '*':
                                findings.append(self._create_finding(
                                    file_path=file_path,
                                    line=0,
                                    rtype=rtype,
                                    rname=rname,
                                    details={
                                        'issue': 'Bucket Policy 授予 AWS: * 权限',
                                        'effect': stmt.get('Effect', 'Allow')
                                    }
                                ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            if rtype != 'AWS::S3::Bucket':
                continue
            
            properties = rdef.get('Properties', {})
            
            # 检查 Public Access Block
            public_block = properties.get('PublicAccessBlockConfiguration', {})
            if public_block:
                block_acls = public_block.get('BlockPublicAcls', False)
                block_policies = public_block.get('BlockPublicPolicy', False)
                if not block_acls or not block_policies:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={
                            'issue': 'Public Access Block 未完全启用',
                            'block_public_acls': block_acls,
                            'block_public_policy': block_policies
                        }
                    ))
            
            # 检查 ACL
            access_control = properties.get('AccessControl', '')
            if access_control in ('PublicRead', 'PublicReadWrite'):
                findings.append(self._create_finding(
                    file_path=file_path,
                    line=0,
                    rtype=rtype,
                    rname=rname,
                    details={'acl': access_control}
                ))
        
        return findings


# ============================================================================
# 规则 7: 弱密码/默认密码检测
# ============================================================================

class WeakPasswordRule(IaCRule):
    """检测弱密码或默认密码"""

    COMMON_WEAK_PASSWORDS = {
        'password', 'admin', 'root', '123456', 'password123',
        'admin123', 'root123', 'changeme', 'welcome', 'welcome1',
        'qwerty', 'letmein', 'monkey', 'master', 'dragon',
        'Passw0rd', 'P@ssw0rd', 'Pass@123', 'passw0rd'
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-007"
        self.rule_name = "弱密码或默认密码"
        self.severity = SeverityLevel.HIGH
        self.description = "检测到弱密码或默认密码，可能导致暴力破解或未授权访问"
        self.remediation = "使用强密码（至少12位，包含大小写字母、数字和特殊字符），通过 Secrets Manager 管理凭证"
        self.cwe_id = "CWE-521"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                for rname, config in rdata.items():
                    if not isinstance(config, dict):
                        continue
                    
                    # 检查 RDS 密码
                    if 'aws_db_instance' in rtype or 'aws_rds_cluster' in rtype:
                        password = config.get('password', [None])
                        if isinstance(password, list):
                            password = password[0] if password else None
                        if password and isinstance(password, str):
                            if password.lower() in self.COMMON_WEAK_PASSWORDS:
                                findings.append(self._create_finding(
                                    file_path=file_path,
                                    line=0,
                                    rtype=rtype,
                                    rname=rname,
                                    details={
                                        'issue': 'RDS 使用弱密码/默认密码',
                                        'password': '*' * len(password)
                                    }
                                ))
                    
                    # 检查数据库用户名是否为默认值
                    if 'aws_db_instance' in rtype:
                        username = config.get('username', [None])
                        if isinstance(username, list):
                            username = username[0] if username else None
                        if username and username.lower() in ('admin', 'root', 'sa', 'postgres'):
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={
                                    'issue': 'RDS 使用默认管理员用户名',
                                    'username': username
                                }
                            ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            properties = rdef.get('Properties', {})
            
            if 'RDS' in rtype:
                # 检查密码
                password = properties.get('MasterUserPassword', '')
                if isinstance(password, str) and password.lower() in self.COMMON_WEAK_PASSWORDS:
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={'issue': 'RDS 使用弱密码'}
                    ))
                
                # 检查用户名
                username = properties.get('MasterUsername', '')
                if isinstance(username, str) and username.lower() in ('admin', 'root', 'sa'):
                    findings.append(self._create_finding(
                        file_path=file_path,
                        line=0,
                        rtype=rtype,
                        rname=rname,
                        details={'issue': 'RDS 使用默认用户名', 'username': username}
                    ))
        
        return findings


# ============================================================================
# 规则 8: 缺少网络隔离
# ============================================================================

class NetworkIsolationRule(IaCRule):
    """检测网络隔离配置不足（子网无 NAT、安全组无出站限制等）"""

    def __init__(self):
        super().__init__()
        self.rule_id = "IAC-008"
        self.rule_name = "网络隔离不足"
        self.severity = SeverityLevel.MEDIUM
        self.description = "网络架构缺少必要的隔离措施，可能扩大攻击面"
        self.remediation = "使用私有子网 + NAT 网关架构，限制安全组出站规则，启用 VPC Flow Logs"
        self.cwe_id = "CWE-284"

    def check_terraform(self, parsed_data: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = parsed_data.get('resource', [])
        
        has_nat_gateway = False
        security_groups = []
        
        for resource_block in resources:
            for rtype, rdata in resource_block.items():
                if 'aws_nat_gateway' in rtype:
                    has_nat_gateway = True
                if 'aws_security_group' in rtype:
                    for rname, config in rdata.items():
                        if isinstance(config, dict):
                            security_groups.append((rname, config))
        
        # 检查安全组是否缺少出站规则限制
        for sg_name, sg_config in security_groups:
            egress_rules = sg_config.get('egress', [])
            if isinstance(egress_rules, dict):
                egress_rules = [egress_rules]
            
            for rule in egress_rules:
                if not isinstance(rule, dict):
                    continue
                cidr_blocks = rule.get('cidr_blocks', [])
                if isinstance(cidr_blocks, str):
                    cidr_blocks = [cidr_blocks]
                
                if '0.0.0.0/0' in cidr_blocks:
                    # 出站允许所有流量
                    ports = rule.get('from_port', [0])
                    if isinstance(ports, (int, str)):
                        ports = [ports]
                    if '0' in [str(p) for p in ports]:
                        findings.append(self._create_finding(
                            file_path=file_path,
                            line=0,
                            rtype='aws_security_group',
                            rname=sg_name,
                            details={
                                'issue': '安全组出站规则允许所有端口到 0.0.0.0/0',
                                'recommendation': '限制出站端口和目标 CIDR'
                            }
                        ))
        
        return findings

    def check_cloudformation(self, template: Dict, file_path: str) -> List[SecurityFinding]:
        findings = []
        resources = template.get('Resources', {})
        
        for rname, rdef in resources.items():
            rtype = rdef.get('Type', '')
            
            if rtype == 'AWS::EC2::SecurityGroup':
                properties = rdef.get('Properties', {})
                egress_rules = properties.get('SecurityGroupEgress', [])
                if isinstance(egress_rules, dict):
                    egress_rules = [egress_rules]
                
                for rule in egress_rules:
                    cidr = rule.get('CidrIp', '')
                    if cidr == '0.0.0.0/0':
                        port = rule.get('FromPort', 0)
                        if port == 0:
                            findings.append(self._create_finding(
                                file_path=file_path,
                                line=0,
                                rtype=rtype,
                                rname=rname,
                                details={'issue': '出站规则允许所有端口'}
                            ))
        
        return findings


# ============================================================================
# 文件解析器
# ============================================================================

class TerraformParser:
    """Terraform HCL 文件解析器"""

    @staticmethod
    def parse(file_path: str) -> Optional[Dict]:
        """解析 Terraform (.tf) 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if HAS_HCL2:
                import io
                parsed = hcl2.load(io.StringIO(content))
                return parsed
            else:
                # 降级：使用简单正则提取资源块
                return TerraformParser._fallback_parse(content)
        except Exception as e:
            print(f"[警告] 解析 Terraform 文件失败: {file_path} - {e}")
            return None

    @staticmethod
    def _fallback_parse(content: str) -> Dict:
        """降级解析：使用正则表达式提取基本结构"""
        result = {'resource': []}
        
        # 匹配 resource "type" "name" { ... }
        pattern = re.compile(r'resource\s+"(\w+)"\s+"(\w+)"\s*\{', re.MULTILINE)
        matches = pattern.finditer(content)
        
        for match in matches:
            rtype = match.group(1)
            rname = match.group(2)
            resource_block = {rtype: {rname: {'_raw': True}}}
            result['resource'].append(resource_block)
        
        return result

    @staticmethod
    def read_raw(file_path: str) -> str:
        """读取原始文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[错误] 读取文件失败: {file_path} - {e}")
            return ""


class CloudFormationParser:
    """CloudFormation 模板解析器"""

    @staticmethod
    def parse(file_path: str) -> Optional[Dict]:
        """解析 CloudFormation 模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.endswith('.json'):
                return json.loads(content)
            elif file_path.endswith(('.yaml', '.yml')):
                if HAS_YAML:
                    return yaml.safe_load(content)
                else:
                    print("[警告] PyYAML 未安装，跳过 YAML 文件")
                    return None
            else:
                # 尝试自动检测
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    if HAS_YAML:
                        return yaml.safe_load(content)
                    return None
        except Exception as e:
            print(f"[警告] 解析 CloudFormation 模板失败: {file_path} - {e}")
            return None

    @staticmethod
    def read_raw(file_path: str) -> str:
        """读取原始文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[错误] 读取文件失败: {file_path} - {e}")
            return ""


# ============================================================================
# 扫描引擎
# ============================================================================

class IaCScanner:
    """IaC 安全扫描引擎"""

    def __init__(self):
        self.rules: List[IaCRule] = [
            OpenSecurityGroupRule(),
            OverPrivilegedIAMRule(),
            UnencryptedStorageRule(),
            DisabledLoggingRule(),
            HardcodedSecretsRule(),
            PublicS3BucketRule(),
            WeakPasswordRule(),
            NetworkIsolationRule()
        ]
        self.supported_extensions = {
            '.tf', '.tf.json',  # Terraform
            '.json', '.yaml', '.yml', '.template'  # CloudFormation
        }

    def scan_path(self, path: str) -> ScanReport:
        """扫描指定路径下的所有 IaC 文件"""
        scan_start = datetime.datetime.now()
        
        all_findings: List[SecurityFinding] = []
        files_scanned = 0
        
        if os.path.isfile(path):
            all_findings.extend(self.scan_file(path))
            files_scanned = 1
        else:
            for root, dirs, files in os.walk(path):
                # 跳过 .git 和 .terraform 目录
                dirs[:] = [d for d in dirs if d not in ('.git', '.terraform', 'node_modules', '__pycache__')]
                
                for filename in files:
                    file_path = os.path.join(root, filename)
                    ext = os.path.splitext(filename)[1].lower()
                    
                    # 处理 .tf.json 双扩展名
                    if filename.endswith('.tf.json'):
                        ext = '.tf.json'
                    
                    if ext in self.supported_extensions:
                        all_findings.extend(self.scan_file(file_path))
                        files_scanned += 1
        
        scan_end = datetime.datetime.now()
        
        report = ScanReport(
            scan_time=scan_start.strftime('%Y-%m-%d %H:%M:%S'),
            target_path=os.path.abspath(path),
            total_files=files_scanned,
            total_findings=len(all_findings),
            findings=all_findings,
            summary={}
        )
        
        return report

    def scan_file(self, file_path: str) -> List[SecurityFinding]:
        """扫描单个文件"""
        findings: List[SecurityFinding] = []
        
        ext = os.path.splitext(file_path)[1].lower()
        if file_path.endswith('.tf.json'):
            ext = '.tf.json'
        
        if ext == '.tf':
            # Terraform HCL 文件
            parsed = TerraformParser.parse(file_path)
            raw_content = TerraformParser.read_raw(file_path)
            
            if parsed:
                for rule in self.rules:
                    try:
                        findings.extend(rule.check_terraform(parsed, file_path))
                    except Exception as e:
                        print(f"[警告] 规则 {rule.rule_id} 执行失败: {e}")
            
            # 硬编码检测需要原始文本
            if raw_content:
                for rule in self.rules:
                    if hasattr(rule, 'check_raw_text'):
                        try:
                            findings.extend(rule.check_raw_text(raw_content, file_path))
                        except Exception as e:
                            print(f"[警告] 规则 {rule.rule_id} 文本检测失败: {e}")
        
        elif ext in ('.json', '.yaml', '.yml', '.template'):
            # CloudFormation 模板
            # 判断是 Terraform JSON 还是 CloudFormation
            raw_content = CloudFormationParser.read_raw(file_path)
            
            # 先尝试判断是否为 CloudFormation
            is_cfn = False
            try:
                if ext == '.json':
                    template = json.loads(raw_content)
                else:
                    if HAS_YAML:
                        template = yaml.safe_load(raw_content)
                    else:
                        template = {}
                
                if isinstance(template, dict):
                    if 'Resources' in template or 'AWSTemplateFormatVersion' in template:
                        is_cfn = True
            except Exception:
                template = {}
            
            if is_cfn and template:
                for rule in self.rules:
                    try:
                        findings.extend(rule.check_cloudformation(template, file_path))
                    except Exception as e:
                        print(f"[警告] 规则 {rule.rule_id} 执行失败: {e}")
                
                # 硬编码检测
                if raw_content:
                    for rule in self.rules:
                        if hasattr(rule, 'check_raw_text'):
                            try:
                                findings.extend(rule.check_raw_text(raw_content, file_path))
                            except Exception as e:
                                print(f"[警告] 规则 {rule.rule_id} 文本检测失败: {e}")
            elif ext == '.tf.json':
                # Terraform JSON 格式
                parsed = CloudFormationParser.parse(file_path)
                if parsed:
                    for rule in self.rules:
                        try:
                            findings.extend(rule.check_terraform(parsed, file_path))
                        except Exception as e:
                            print(f"[警告] 规则 {rule.rule_id} 执行失败: {e}")
        
        return findings


# ============================================================================
# 报告生成器
# ============================================================================

class ReportGenerator:
    """扫描报告生成器"""

    @staticmethod
    def generate_text(report: ScanReport) -> str:
        """生成文本格式报告"""
        lines = []
        lines.append("=" * 80)
        lines.append("IaC 安全检查报告")
        lines.append("=" * 80)
        lines.append(f"扫描时间: {report.scan_time}")
        lines.append(f"扫描路径: {report.target_path}")
        lines.append(f"扫描文件数: {report.total_files}")
        lines.append(f"发现问题数: {report.total_findings}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("严重程度统计:")
        for level in SeverityLevel:
            count = report.summary.get(level.name, 0)
            if count > 0:
                lines.append(f"  {level.value}: {count}")
        lines.append("-" * 80)
        lines.append("")
        
        if not report.findings:
            lines.append("未发现安全问题。")
        else:
            # 按严重程度排序
            sorted_findings = sorted(
                report.findings,
                key=lambda f: f.severity.score,
                reverse=True
            )
            
            for i, finding in enumerate(sorted_findings, 1):
                lines.append(f"[{i}] {finding.severity.value} - {finding.rule_name}")
                lines.append(f"    规则编号: {finding.rule_id}")
                lines.append(f"    文件: {finding.file_path}")
                if finding.line_number > 0:
                    lines.append(f"    行号: {finding.line_number}")
                lines.append(f"    资源: {finding.resource_type} / {finding.resource_name}")
                lines.append(f"    描述: {finding.description}")
                if finding.cwe_id:
                    lines.append(f"    CWE: {finding.cwe_id}")
                if finding.details:
                    lines.append(f"    详情: {json.dumps(finding.details, ensure_ascii=False, indent=6)}")
                lines.append(f"    修复: {finding.remediation}")
                lines.append("")
        
        lines.append("=" * 80)
        return '\n'.join(lines)

    @staticmethod
    def generate_json(report: ScanReport) -> str:
        """生成 JSON 格式报告"""
        data = {
            'scan_time': report.scan_time,
            'target_path': report.target_path,
            'total_files': report.total_files,
            'total_findings': report.total_findings,
            'summary': report.summary,
            'findings': [
                {
                    'rule_id': f.rule_id,
                    'rule_name': f.rule_name,
                    'severity': f.severity.value,
                    'severity_code': f.severity.name,
                    'description': f.description,
                    'file_path': f.file_path,
                    'line_number': f.line_number,
                    'resource_type': f.resource_type,
                    'resource_name': f.resource_name,
                    'remediation': f.remediation,
                    'cwe_id': f.cwe_id,
                    'details': f.details
                }
                for f in sorted(report.findings, 
                              key=lambda f: f.severity.score, 
                              reverse=True)
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def generate_html(report: ScanReport) -> str:
        """生成 HTML 格式报告"""
        severity_colors = {
            SeverityLevel.CRITICAL: '#dc3545',
            SeverityLevel.HIGH: '#fd7e14',
            SeverityLevel.MEDIUM: '#ffc107',
            SeverityLevel.LOW: '#17a2b8',
            SeverityLevel.INFO: '#6c757d'
        }
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>IaC 安全检查报告</title>
    <style>
        body {{ font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; margin: 20px; background: #f8f9fa; }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .summary {{ display: flex; gap: 15px; margin: 20px 0; }}
        .summary-card {{ padding: 15px 25px; border-radius: 8px; color: white; text-align: center; min-width: 120px; }}
        .summary-card .count {{ font-size: 2em; font-weight: bold; }}
        .summary-card .label {{ font-size: 0.9em; }}
        .finding {{ background: white; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 5px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .finding-header {{ font-weight: bold; font-size: 1.1em; margin-bottom: 8px; }}
        .finding-detail {{ margin: 3px 0; color: #555; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; color: white; font-size: 0.85em; margin-right: 8px; }}
        pre {{ background: #f1f3f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>IaC 安全检查报告</h1>
    <div style="color: #666;">
        <p>扫描时间: {report.scan_time}</p>
        <p>扫描路径: {report.target_path}</p>
        <p>扫描文件数: {report.total_files} | 发现问题数: {report.total_findings}</p>
    </div>
    <div class="summary">
"""
        
        for level in SeverityLevel:
            count = report.summary.get(level.name, 0)
            color = severity_colors.get(level, '#6c757d')
            html += f'        <div class="summary-card" style="background: {color};">\n'
            html += f'            <div class="count">{count}</div>\n'
            html += f'            <div class="label">{level.value}</div>\n'
            html += f'        </div>\n'
        
        html += "    </div>\n"
        
        if not report.findings:
            html += "    <p style='font-size: 1.2em; color: green;'>未发现安全问题。</p>\n"
        else:
            sorted_findings = sorted(
                report.findings,
                key=lambda f: f.severity.score,
                reverse=True
            )
            
            for i, f in enumerate(sorted_findings, 1):
                color = severity_colors.get(f.severity, '#6c757d')
                details_json = json.dumps(f.details, ensure_ascii=False, indent=2) if f.details else ''
                html += f"""
    <div class="finding" style="border-left-color: {color};">
        <div class="finding-header">
            <span class="badge" style="background: {color};">{f.severity.value}</span>
            {f.rule_name}
            <span style="font-size: 0.85em; color: #999;">({f.rule_id})</span>
        </div>
        <div class="finding-detail"><strong>文件:</strong> {f.file_path}</div>
        {f'<div class="finding-detail"><strong>行号:</strong> {f.line_number}</div>' if f.line_number > 0 else ''}
        <div class="finding-detail"><strong>资源:</strong> {f.resource_type} / {f.resource_name}</div>
        <div class="finding-detail"><strong>描述:</strong> {f.description}</div>
        {f'<div class="finding-detail"><strong>CWE:</strong> {f.cwe_id}</div>' if f.cwe_id else ''}
        {f'<div class="finding-detail"><strong>详情:</strong><pre>{details_json}</pre></div>' if details_json else ''}
        <div class="finding-detail"><strong>修复建议:</strong> {f.remediation}</div>
    </div>
"""
        
        html += """
</body>
</html>"""
        return html


# ============================================================================
# 示例 IaC 文件生成（用于测试和演示）
# ============================================================================

class SampleIaCGenerator:
    """生成包含安全问题的示例 IaC 文件"""

    @staticmethod
    def generate_terraform_sample() -> str:
        """生成包含安全问题的 Terraform 示例"""
        return '''# ===========================================
# Terraform 示例配置（包含安全问题）
# ===========================================

# 安全组 - 开放敏感端口到 0.0.0.0/0
resource "aws_security_group" "web_sg" {
  name        = "web-security-group"
  description = "Web Security Group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM 角色 - 过度授权
resource "aws_iam_role_policy" "admin_policy" {
  name = "admin-policy"
  role = aws_iam_role.app_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "*"
        Resource = "*"
        Effect   = "Allow"
      }
    ]
  })
}

# S3 Bucket - 未加密 + 公开访问
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-sensitive-data-bucket"
}

resource "aws_s3_bucket_acl" "data_bucket_acl" {
  bucket = aws_s3_bucket.data_bucket.id
  acl    = "public-read"
}

# RDS - 未加密 + 弱密码
resource "aws_db_instance" "database" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  username             = "admin"
  password             = "password123"
  storage_encrypted    = false
  publicly_accessible  = true
}

# EBS Volume - 未加密
resource "aws_ebs_volume" "data_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = false
}

# 硬编码凭证
resource "aws_db_instance" "app_db" {
  username = "root"
  password = "AKIAIOSFODNN7EXAMPLE"
}
'''

    @staticmethod
    def generate_cloudformation_sample() -> str:
        """生成包含安全问题的 CloudFormation 示例"""
        return json.dumps({
            "AWSTemplateFormatVersion": "2010-09-09",
            "Resources": {
                "WebSecurityGroup": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Properties": {
                        "GroupDescription": "Web Security Group",
                        "SecurityGroupIngress": [
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 22,
                                "ToPort": 22,
                                "CidrIp": "0.0.0.0/0"
                            },
                            {
                                "IpProtocol": "tcp",
                                "FromPort": 3306,
                                "ToPort": 3306,
                                "CidrIp": "0.0.0.0/0"
                            }
                        ],
                        "SecurityGroupEgress": [
                            {
                                "IpProtocol": "-1",
                                "FromPort": 0,
                                "ToPort": 0,
                                "CidrIp": "0.0.0.0/0"
                            }
                        ]
                    }
                },
                "AdminRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Action": "*",
                                "Resource": "*",
                                "Principal": {"AWS": "*"}
                            }]
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/AdministratorAccess"
                        ]
                    }
                },
                "DataBucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": "my-sensitive-data-bucket",
                        "AccessControl": "PublicRead"
                    }
                },
                "Database": {
                    "Type": "AWS::RDS::DBInstance",
                    "Properties": {
                        "AllocatedStorage": "20",
                        "DBInstanceClass": "db.t3.micro",
                        "Engine": "mysql",
                        "MasterUsername": "admin",
                        "MasterUserPassword": "password123",
                        "StorageEncrypted": False,
                        "PubliclyAccessible": True
                    }
                },
                "DataVolume": {
                    "Type": "AWS::EC2::Volume",
                    "Properties": {
                        "Size": 100,
                        "AvailabilityZone": "us-east-1a",
                        "Encrypted": False
                    }
                }
            }
        }, indent=2, ensure_ascii=False)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='IaC 安全检查工具 - 检测 Terraform/CloudFormation 配置中的安全风险',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python iac_security_checker.py ./terraform/
  python iac_security_checker.py ./cloudformation/ --format json --output report.json
  python iac_security_checker.py template.yaml --format html --output report.html
  python iac_security_checker.py --generate-samples
        """
    )
    
    parser.add_argument('path', nargs='?', help='要扫描的目录或文件路径')
    parser.add_argument('--format', choices=['text', 'json', 'html'], default='text',
                        help='报告输出格式（默认: text）')
    parser.add_argument('--output', '-o', help='输出文件路径（不指定则打印到终端）')
    parser.add_argument('--generate-samples', action='store_true',
                        help='生成包含安全问题的示例 IaC 文件')
    
    args = parser.parse_args()
    
    # 生成示例文件模式
    if args.generate_samples:
        print("=" * 60)
        print("生成示例 IaC 文件...")
        print("=" * 60)
        
        sample_tf = SampleIaCGenerator.generate_terraform_sample()
        tf_path = "sample_terraform.tf"
        with open(tf_path, 'w', encoding='utf-8') as f:
            f.write(sample_tf)
        print(f"[+] 已生成: {tf_path}")
        
        sample_cfn = SampleIaCGenerator.generate_cloudformation_sample()
        cfn_path = "sample_cloudformation.json"
        with open(cfn_path, 'w', encoding='utf-8') as f:
            f.write(sample_cfn)
        print(f"[+] 已生成: {cfn_path}")
        
        print("\n现在可以用以下命令扫描这些示例文件:")
        print(f"  python iac_security_checker.py {tf_path}")
        print(f"  python iac_security_checker.py {cfn_path}")
        return
    
    if not args.path:
        parser.print_help()
        return
    
    # 验证路径
    if not os.path.exists(args.path):
        print(f"[错误] 路径不存在: {args.path}")
        return
    
    # 执行扫描
    print(f"[*] 开始扫描: {args.path}")
    scanner = IaCScanner()
    report = scanner.scan_path(args.path)
    
    # 生成报告
    if args.format == 'json':
        report_content = ReportGenerator.generate_json(report)
    elif args.format == 'html':
        report_content = ReportGenerator.generate_html(report)
    else:
        report_content = ReportGenerator.generate_text(report)
    
    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n[+] 报告已保存到: {args.output}")
    else:
        print(report_content)
    
    # 打印摘要
    print(f"\n{'=' * 60}")
    print(f"扫描完成 - 共扫描 {report.total_files} 个文件，发现 {report.total_findings} 个问题")
    for level in SeverityLevel:
        count = report.summary.get(level.name, 0)
        if count > 0:
            print(f"  {level.value}: {count}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
