#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云安全配置检查工具 (Cloud Security Check Tool)
==================================================

功能说明：
    本工具用于检查云平台的安全配置，包括对象存储权限、IAM 策略、
    安全组规则、密钥轮换、日志审计等方面的安全检查，
    并生成详细的安全报告。

支持的检查项：
    1. S3 / OSS 存储桶权限检查
    2. IAM / RAM 策略分析
    3. 安全组规则审计
    4. 访问密钥轮换检查
    5. 日志审计配置检查
    6. 综合安全评分

使用方式：
    python cloud_security_check.py                    # 使用模拟数据运行
    python cloud_security_check.py --mode aws         # 使用真实 AWS API
    python cloud_security_check.py --mode aliyun      # 使用真实阿里云 API
    python cloud_security_check.py --report report.html  # 生成 HTML 报告

作者：云安全学习工具
版本：1.0.0
"""

import json
import os
import sys
import argparse
import datetime
import html
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


# ============================================================
# 数据类定义：用于存储检查结果
# ============================================================

@dataclass
class CheckResult:
    """
    单项检查结果的数据类

    属性说明：
        check_name: 检查项名称
        category: 检查类别（存储/身份/网络/日志等）
        severity: 风险等级（critical/high/medium/low/info）
        status: 检查状态（pass/fail/warning）
        resource: 资源名称
        description: 问题描述
        recommendation: 修复建议
        details: 详细信息
    """
    check_name: str
    category: str
    severity: str
    status: str
    resource: str
    description: str
    recommendation: str
    details: str = ""


@dataclass
class SecurityReport:
    """
    安全报告的数据类

    属性说明：
        scan_time: 扫描时间
        platform: 云平台类型
        total_checks: 总检查项数
        passed_checks: 通过的检查项数
        failed_checks: 失败的检查项数
        warning_checks: 警告的检查项数
        results: 所有检查结果列表
        score: 安全评分（0-100）
    """
    scan_time: str = ""
    platform: str = "模拟环境"
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    results: List[CheckResult] = field(default_factory=list)
    score: float = 0.0


# ============================================================
# 模拟数据生成：用于演示和测试
# ============================================================

def generate_mock_s3_buckets() -> List[Dict[str, Any]]:
    """
    生成模拟的 S3 存储桶数据

    返回值：
        包含多个存储桶配置的列表，每个字典包含桶名、权限、加密配置等信息
    """
    return [
        {
            "name": "company-prod-data",
            "acl": "private",  # 访问控制列表：私有（安全）
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "arn:aws:iam::123456789012:user/app-user"},
                        "Action": ["s3:GetObject", "s3:PutObject"],
                        "Resource": "arn:aws:s3:::company-prod-data/*"
                    }
                ]
            },
            "encryption": True,  # 服务端加密：已启用
            "versioning": True,  # 版本控制：已启用
            "logging": True,  # 访问日志：已启用
            "public_access_block": True,  # 阻止公开访问：已启用
            "objects_count": 15000
        },
        {
            "name": "company-dev-assets",
            "acl": "public-read",  # 访问控制：公共读（不安全）
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",  # 允许所有人（不安全）
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::company-dev-assets/*"
                    }
                ]
            },
            "encryption": False,  # 未启用加密
            "versioning": False,  # 未启用版本控制
            "logging": False,  # 未启用访问日志
            "public_access_block": False,  # 未阻止公开访问
            "objects_count": 3200
        },
        {
            "name": "company-backup-2024",
            "acl": "private",
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",  # 策略中 Principal 为通配符
                        "Action": "s3:ListBucket",
                        "Resource": "arn:aws:s3:::company-backup-2024",
                        "Condition": {
                            "IpAddress": {
                                "aws:SourceIp": "10.0.0.0/8"  # 但有 IP 限制
                            }
                        }
                    }
                ]
            },
            "encryption": True,
            "versioning": True,
            "logging": False,  # 未启用日志
            "public_access_block": True,
            "objects_count": 500
        },
        {
            "name": "company-public-website",
            "acl": "public-read",  # 网站静态资源，公开读取是合理的
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::company-public-website/*"
                    }
                ]
            },
            "encryption": True,
            "versioning": True,
            "logging": True,
            "public_access_block": False,  # 网站托管需要关闭
            "objects_count": 2800
        }
    ]


def generate_mock_iam_users() -> List[Dict[str, Any]]:
    """
    生成模拟的 IAM 用户数据

    返回值：
        包含多个 IAM 用户配置的列表
    """
    return [
        {
            "username": "admin-user",
            "mfa_enabled": True,  # 已启用 MFA
            "access_keys": [
                {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE1",
                    "status": "Active",
                    "create_date": "2024-08-15",  # 创建时间（1个月前，在90天内）
                    "last_used_date": "2024-09-10",
                    "age_days": 27  # 密钥年龄（天）
                }
            ],
            "policies": [
                {"name": "AdministratorAccess", "type": "managed"}
            ],
            "last_login": "2024-09-10",
            "password_last_rotated": "2024-06-01"
        },
        {
            "username": "dev-user-1",
            "mfa_enabled": False,  # 未启用 MFA（不安全）
            "access_keys": [
                {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE2",
                    "status": "Active",
                    "create_date": "2024-01-10",  # 超过 90 天未轮换
                    "last_used_date": "2024-09-05",
                    "age_days": 244  # 密钥年龄 244 天
                },
                {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE3",
                    "status": "Inactive",
                    "create_date": "2023-06-01",
                    "last_used_date": "2023-12-01",
                    "age_days": 467
                }
            ],
            "policies": [
                {"name": "AmazonEC2FullAccess", "type": "managed"},
                {"name": "AmazonS3FullAccess", "type": "managed"}
            ],
            "last_login": "2024-09-08",
            "password_last_rotated": "2023-11-01"
        },
        {
            "username": "ci-cd-user",
            "mfa_enabled": False,  # CI/CD 用户通常不使用密码登录
            "access_keys": [
                {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE4",
                    "status": "Active",
                    "create_date": "2024-06-01",  # 102 天，接近 90 天阈值
                    "last_used_date": "2024-09-10",
                    "age_days": 102
                }
            ],
            "policies": [
                {
                    "name": "CI-CD-Policy",
                    "type": "inline",
                    "document": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetObject",
                                    "s3:PutObject",
                                    "ec2:Describe*"
                                ],
                                "Resource": "*"  # 资源通配符（不推荐）
                            }
                        ]
                    }
                }
            ],
            "last_login": "Never",  # 从未登录控制台（正常，API 用户）
            "password_last_rotated": "N/A"
        },
        {
            "username": "old-user-not-used",
            "mfa_enabled": False,
            "access_keys": [
                {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE5",
                    "status": "Active",  # 密钥仍活跃但用户长期未使用
                    "create_date": "2022-03-15",
                    "last_used_date": "2023-08-20",  # 一年多未使用
                    "age_days": 910
                }
            ],
            "policies": [
                {"name": "ReadOnlyAccess", "type": "managed"}
            ],
            "last_login": "2023-06-01",  # 超过一年未登录
            "password_last_rotated": "2022-03-15"
        }
    ]


def generate_mock_iam_roles() -> List[Dict[str, Any]]:
    """
    生成模拟的 IAM 角色数据
    """
    return [
        {
            "role_name": "EC2-App-Role",
            "assume_role_policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "policies": [
                {
                    "name": "AppPolicy",
                    "type": "inline",
                    "document": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetObject",
                                    "s3:ListBucket"
                                ],
                                "Resource": [
                                    "arn:aws:s3:::app-data-bucket",
                                    "arn:aws:s3:::app-data-bucket/*"
                                ]
                            }
                        ]
                    }
                }
            ]
        },
        {
            "role_name": "Admin-Role",
            "assume_role_policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},  # 信任所有 AWS 账户（危险）
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "policies": [
                {"name": "AdministratorAccess", "type": "managed"}
            ]
        },
        {
            "role_name": "Lambda-Execution-Role",
            "assume_role_policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "policies": [
                {"name": "AWSLambdaBasicExecutionRole", "type": "managed"},
                {
                    "name": "LambdaCustomPolicy",
                    "type": "inline",
                    "document": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "dynamodb:*",  # 权限过大
                                "Resource": "*"
                            }
                        ]
                    }
                }
            ]
        }
    ]


def generate_mock_security_groups() -> List[Dict[str, Any]]:
    """
    生成模拟的安全组数据
    """
    return [
        {
            "group_id": "sg-webserver",
            "group_name": "web-server-sg",
            "description": "Web 服务器安全组",
            "inbound_rules": [
                {
                    "protocol": "tcp",
                    "port": 80,
                    "source": "0.0.0.0/0",  # HTTP 对全网开放（合理）
                    "description": "HTTP access"
                },
                {
                    "protocol": "tcp",
                    "port": 443,
                    "source": "0.0.0.0/0",  # HTTPS 对全网开放（合理）
                    "description": "HTTPS access"
                },
                {
                    "protocol": "tcp",
                    "port": 22,
                    "source": "10.0.1.0/24",  # SSH 仅允许内网（安全）
                    "description": "SSH from internal"
                }
            ],
            "outbound_rules": [
                {
                    "protocol": "-1",  # 所有协议
                    "port": "all",
                    "destination": "0.0.0.0/0",
                    "description": "Allow all outbound"
                }
            ]
        },
        {
            "group_id": "sg-database",
            "group_name": "database-sg",
            "description": "数据库安全组",
            "inbound_rules": [
                {
                    "protocol": "tcp",
                    "port": 3306,
                    "source": "sg-webserver",  # 仅允许 Web 安全组访问（安全）
                    "description": "MySQL from web servers"
                }
            ],
            "outbound_rules": [
                {
                    "protocol": "-1",
                    "port": "all",
                    "destination": "0.0.0.0/0",
                    "description": "Allow all outbound"
                }
            ]
        },
        {
            "group_id": "sg-bastion",
            "group_name": "bastion-sg",
            "description": "堡垒机安全组",
            "inbound_rules": [
                {
                    "protocol": "tcp",
                    "port": 22,
                    "source": "0.0.0.0/0",  # SSH 对全网开放（不安全）
                    "description": "SSH from anywhere"
                }
            ],
            "outbound_rules": [
                {
                    "protocol": "tcp",
                    "port": 22,
                    "destination": "10.0.0.0/16",
                    "description": "SSH to internal"
                }
            ]
        },
        {
            "group_id": "sg-risky",
            "group_name": "risky-app-sg",
            "description": "存在风险的应用安全组",
            "inbound_rules": [
                {
                    "protocol": "tcp",
                    "port": 22,
                    "source": "0.0.0.0/0",  # SSH 公网开放
                    "description": "SSH open to world"
                },
                {
                    "protocol": "tcp",
                    "port": 3389,
                    "source": "0.0.0.0/0",  # RDP 公网开放
                    "description": "RDP open to world"
                },
                {
                    "protocol": "tcp",
                    "port": 3306,
                    "source": "0.0.0.0/0",  # MySQL 公网开放
                    "description": "MySQL open to world"
                },
                {
                    "protocol": "tcp",
                    "port": 6379,
                    "source": "0.0.0.0/0",  # Redis 公网开放
                    "description": "Redis open to world"
                },
                {
                    "protocol": "-1",
                    "port": "all",
                    "source": "0.0.0.0/0",  # 所有端口全部开放（极危险）
                    "description": "All ports open"
                }
            ],
            "outbound_rules": [
                {
                    "protocol": "-1",
                    "port": "all",
                    "destination": "0.0.0.0/0",
                    "description": "Allow all outbound"
                }
            ]
        }
    ]


def generate_mock_cloudtrail_config() -> Dict[str, Any]:
    """
    生成模拟的 CloudTrail/操作审计配置
    """
    return {
        "trails": [
            {
                "name": "main-trail",
                "is_multi_region_trail": True,  # 多区域跟踪（好）
                "log_file_validation_enabled": True,  # 日志文件验证（好）
                "s3_bucket_name": "company-cloudtrail-logs",
                "is_logging": True,  # 正在记录（好）
                "kms_key_id": "arn:aws:kms:us-east-1:123456789012:key/abc123",  # 加密（好）
                "include_global_service_events": True  # 包含全局服务事件（好）
            }
        ],
        "cloudwatch_logs_enabled": True,  # 集成 CloudWatch（好）
        "sns_notifications_enabled": False,  # 未启用 SNS 告警（可改进）
        "bucket_public_access": False,  # 日志桶不公开（好）
        "bucket_versioning": True,  # 日志桶版本控制（好）
        "management_events": True,  # 记录管理事件（好）
        "data_events_s3": False,  # 未记录 S3 数据事件（可选）
        "data_events_lambda": False  # 未记录 Lambda 数据事件（可选）
    }


# ============================================================
# 检查模块 1：S3 / OSS 存储桶权限检查
# ============================================================

def check_s3_bucket_permissions(buckets: List[Dict[str, Any]]) -> List[CheckResult]:
    """
    检查 S3 存储桶的安全配置

    检查项包括：
        - 存储桶是否公开访问
        - 存储桶策略是否过宽
        - 是否启用服务端加密
        - 是否启用版本控制
        - 是否启用访问日志
        - 是否启用阻止公开访问

    参数：
        buckets: 存储桶配置列表

    返回值：
        检查结果列表
    """
    results = []

    for bucket in buckets:
        bucket_name = bucket["name"]

        # 检查 1：公开访问检查（ACL 为 public-read 或 public-read-write）
        if bucket["acl"] in ["public-read", "public-read-write"]:
            # 如果是网站托管用途，可能是合理的，需要结合业务判断
            if "website" in bucket_name or "static" in bucket_name:
                severity = "low"
                status = "warning"
                description = f"存储桶 {bucket_name} ACL 为 {bucket['acl']}，可能是网站托管用途"
                recommendation = "确认该桶是否确实需要公开访问，如非必要请设置为私有"
            else:
                severity = "critical"
                status = "fail"
                description = f"存储桶 {bucket_name} ACL 为 {bucket['acl']}，存在数据泄露风险"
                recommendation = "立即将存储桶 ACL 修改为私有（private），并审查存储桶策略"

            results.append(CheckResult(
                check_name="S3 存储桶 ACL 检查",
                category="存储安全",
                severity=severity,
                status=status,
                resource=bucket_name,
                description=description,
                recommendation=recommendation,
                details=f"当前 ACL: {bucket['acl']}"
            ))

        # 检查 2：阻止公开访问配置
        if not bucket["public_access_block"]:
            results.append(CheckResult(
                check_name="S3 阻止公开访问配置",
                category="存储安全",
                severity="high",
                status="fail",
                resource=bucket_name,
                description=f"存储桶 {bucket_name} 未启用 '阻止公开访问' 设置",
                recommendation="启用 Block Public Access 设置，防止配置错误导致的公开访问",
                details="建议启用全部四项阻止公开访问设置"
            ))

        # 检查 3：存储桶策略中的 Principal 通配符
        policy = bucket.get("policy", {})
        statements = policy.get("Statement", [])
        for stmt in statements:
            if stmt.get("Effect") == "Allow" and stmt.get("Principal") == "*":
                # 检查是否有条件限制
                condition = stmt.get("Condition", {})
                if not condition:
                    results.append(CheckResult(
                        check_name="S3 存储桶策略检查",
                        category="存储安全",
                        severity="critical",
                        status="fail",
                        resource=bucket_name,
                        description=f"存储桶 {bucket_name} 策略中存在 Principal: '*' 且无条件限制",
                        recommendation="限制 Principal 为特定的 IAM 用户/角色，或添加条件限制",
                        details=f"策略语句: {json.dumps(stmt, indent=2, ensure_ascii=False)}"
                    ))
                elif "IpAddress" in condition:
                    results.append(CheckResult(
                        check_name="S3 存储桶策略检查",
                        category="存储安全",
                        severity="medium",
                        status="warning",
                        resource=bucket_name,
                        description=f"存储桶 {bucket_name} 策略使用 Principal: '*' 但有 IP 限制",
                        recommendation="建议使用具体的 Principal 替代通配符，遵循最小权限原则",
                        details=f"IP 限制条件: {json.dumps(condition, indent=2, ensure_ascii=False)}"
                    ))

        # 检查 4：服务端加密
        if not bucket["encryption"]:
            results.append(CheckResult(
                check_name="S3 服务端加密检查",
                category="数据安全",
                severity="medium",
                status="fail",
                resource=bucket_name,
                description=f"存储桶 {bucket_name} 未启用服务端加密",
                recommendation="启用 SSE-S3 或 SSE-KMS 服务端加密，保护静态数据",
                details="推荐使用 SSE-KMS 以便进行密钥使用审计"
            ))

        # 检查 5：版本控制
        if not bucket["versioning"]:
            results.append(CheckResult(
                check_name="S3 版本控制检查",
                category="存储安全",
                severity="low",
                status="fail",
                resource=bucket_name,
                description=f"存储桶 {bucket_name} 未启用版本控制",
                recommendation="启用版本控制，防止意外删除和数据篡改",
                details="版本控制可保留对象的多个版本，支持恢复误删除的数据"
            ))

        # 检查 6：访问日志
        if not bucket["logging"]:
            results.append(CheckResult(
                check_name="S3 访问日志检查",
                category="日志审计",
                severity="medium",
                status="fail",
                resource=bucket_name,
                description=f"存储桶 {bucket_name} 未启用访问日志",
                recommendation="启用存储桶访问日志，用于安全审计和问题排查",
                details="访问日志记录所有对存储桶的请求，建议将日志保存到独立的日志桶"
            ))

    return results


# ============================================================
# 检查模块 2：IAM / RAM 策略分析
# ============================================================

def check_iam_config(users: List[Dict[str, Any]], roles: List[Dict[str, Any]]) -> List[CheckResult]:
    """
    检查 IAM 身份与访问管理配置

    检查项包括：
        - 用户 MFA 启用情况
        - 管理员权限用户数量
        - 权限过大的策略
        - 角色信任策略
        - 未使用的用户

    参数：
        users: IAM 用户列表
        roles: IAM 角色列表

    返回值：
        检查结果列表
    """
    results = []

    # ============= 用户相关检查 =============

    for user in users:
        username = user["username"]

        # 检查 1：MFA 启用情况
        if not user["mfa_enabled"]:
            # 从未登录控制台的 API 用户可以不启用 MFA
            if user["last_login"] == "Never":
                results.append(CheckResult(
                    check_name="IAM 用户 MFA 检查",
                    category="身份安全",
                    severity="info",
                    status="pass",
                    resource=username,
                    description=f"API 用户 {username} 未启用 MFA（未使用控制台登录）",
                    recommendation="API 用户建议使用角色和临时凭证，而非长期密钥",
                    details="该用户从未登录控制台，主要用于 API 访问"
                ))
            else:
                results.append(CheckResult(
                    check_name="IAM 用户 MFA 检查",
                    category="身份安全",
                    severity="high",
                    status="fail",
                    resource=username,
                    description=f"用户 {username} 未启用多因素认证（MFA）",
                    recommendation="为所有控制台用户启用 MFA，特别是高权限用户",
                    details="MFA 是防止账号被入侵的重要安全措施"
                ))

        # 检查 2：管理员权限
        policies = user.get("policies", [])
        is_admin = any(p["name"] == "AdministratorAccess" for p in policies)
        if is_admin:
            results.append(CheckResult(
                check_name="IAM 管理员权限检查",
                category="身份安全",
                severity="high",
                status="warning",
                resource=username,
                description=f"用户 {username} 拥有管理员权限（AdministratorAccess）",
                recommendation="审查管理员用户是否必要，遵循最小权限原则，减少管理员数量",
                details="管理员账户应严格控制数量，并启用最强的安全保护（MFA、强密码等）"
            ))

        # 检查 3：策略中的通配符权限
        for policy in policies:
            if policy.get("type") == "inline":
                doc = policy.get("document", {})
                statements = doc.get("Statement", [])
                for stmt in statements:
                    actions = stmt.get("Action", [])
                    resources = stmt.get("Resource", [])
                    if isinstance(actions, str) and actions == "*":
                        results.append(CheckResult(
                            check_name="IAM 策略权限检查",
                            category="身份安全",
                            severity="critical",
                            status="fail",
                            resource=f"{username}/{policy['name']}",
                            description=f"用户 {username} 的策略 {policy['name']} 中 Action 为 '*'",
                            recommendation="将 Action 细化为具体需要的 API 操作，遵循最小权限原则",
                            details=f"策略内容: {json.dumps(stmt, indent=2, ensure_ascii=False)}"
                        ))
                    if isinstance(resources, str) and resources == "*":
                        results.append(CheckResult(
                            check_name="IAM 策略资源检查",
                            category="身份安全",
                            severity="medium",
                            status="warning",
                            resource=f"{username}/{policy['name']}",
                            description=f"用户 {username} 的策略 {policy['name']} 中 Resource 为 '*'",
                            recommendation="将 Resource 限定为具体的资源 ARN，避免资源通配符",
                            details=f"策略内容: {json.dumps(stmt, indent=2, ensure_ascii=False)}"
                        ))

        # 检查 4：长期未使用的用户
        last_login = user.get("last_login", "")
        if last_login != "Never" and last_login != "N/A":
            try:
                last_login_date = datetime.datetime.strptime(last_login, "%Y-%m-%d")
                days_since_login = (datetime.datetime.now() - last_login_date).days
                if days_since_login > 180:  # 超过 180 天未登录
                    results.append(CheckResult(
                        check_name="IAM 用户活跃度检查",
                        category="身份安全",
                        severity="medium",
                        status="warning",
                        resource=username,
                        description=f"用户 {username} 已超过 {days_since_login} 天未登录",
                        recommendation="考虑禁用或删除长期未使用的用户，减少攻击面",
                        details=f"最后登录时间: {last_login}"
                    ))
            except ValueError:
                pass

    # ============= 角色相关检查 =============

    for role in roles:
        role_name = role["role_name"]
        trust_policy = role.get("assume_role_policy_document", {})
        statements = trust_policy.get("Statement", [])

        for stmt in statements:
            if stmt.get("Effect") == "Allow":
                principal = stmt.get("Principal", {})

                # 检查 5：角色信任策略是否过宽
                if principal == "*" or principal.get("AWS") == "*":
                    results.append(CheckResult(
                        check_name="IAM 角色信任策略检查",
                        category="身份安全",
                        severity="critical",
                        status="fail",
                        resource=role_name,
                        description=f"角色 {role_name} 的信任策略允许所有主体扮演（Principal: '*'）",
                        recommendation="立即修改信任策略，只允许可信的账户或服务扮演该角色",
                        details=f"信任策略: {json.dumps(stmt, indent=2, ensure_ascii=False)}"
                    ))

                # 检查 6：角色的权限是否过大
                role_policies = role.get("policies", [])
                for policy in role_policies:
                    if policy["name"] == "AdministratorAccess":
                        results.append(CheckResult(
                            check_name="IAM 角色权限检查",
                            category="身份安全",
                            severity="high",
                            status="warning",
                            resource=role_name,
                            description=f"角色 {role_name} 拥有管理员权限",
                            recommendation="审查角色是否需要管理员权限，遵循最小权限原则",
                            details="角色权限过大时，若被滥用将造成严重后果"
                        ))

    return results


# ============================================================
# 检查模块 3：访问密钥轮换检查
# ============================================================

def check_access_key_rotation(users: List[Dict[str, Any]]) -> List[CheckResult]:
    """
    检查访问密钥的轮换情况

    检查项包括：
        - 密钥年龄是否超过 90 天
        - 是否存在未使用的密钥
        - 密钥是否超过最大使用天数

    参数：
        users: IAM 用户列表

    返回值：
        检查结果列表
    """
    results = []
    MAX_KEY_AGE_DAYS = 90  # 建议的最大密钥使用天数
    WARNING_KEY_AGE_DAYS = 60  # 警告阈值

    for user in users:
        username = user["username"]
        access_keys = user.get("access_keys", [])

        for key in access_keys:
            key_id = key["access_key_id"]
            key_age = key.get("age_days", 0)
            status = key.get("status", "Active")

            if status != "Active":
                # 非活跃密钥，检查是否需要清理
                if key_age > 365:
                    results.append(CheckResult(
                        check_name="访问密钥清理检查",
                        category="身份安全",
                        severity="low",
                        status="warning",
                        resource=f"{username}/{key_id}",
                        description=f"用户 {username} 的非活跃密钥 {key_id} 已存在 {key_age} 天",
                        recommendation="删除不再使用的访问密钥，减少凭证泄露风险",
                        details=f"密钥状态: {status}, 创建时间: {key.get('create_date', 'N/A')}"
                    ))
                continue

            # 检查密钥年龄
            if key_age > MAX_KEY_AGE_DAYS:
                results.append(CheckResult(
                    check_name="访问密钥轮换检查",
                    category="身份安全",
                    severity="high",
                    status="fail",
                    resource=f"{username}/{key_id}",
                    description=f"用户 {username} 的密钥 {key_id} 已使用 {key_age} 天，超过 {MAX_KEY_AGE_DAYS} 天阈值",
                    recommendation="立即轮换该访问密钥，建议每 90 天轮换一次",
                    details=f"密钥年龄: {key_age} 天, 建议阈值: {MAX_KEY_AGE_DAYS} 天"
                ))
            elif key_age > WARNING_KEY_AGE_DAYS:
                results.append(CheckResult(
                    check_name="访问密钥轮换检查",
                    category="身份安全",
                    severity="medium",
                    status="warning",
                    resource=f"{username}/{key_id}",
                    description=f"用户 {username} 的密钥 {key_id} 已使用 {key_age} 天，即将达到轮换阈值",
                    recommendation=f"请在 {MAX_KEY_AGE_DAYS - key_age} 天内轮换该访问密钥",
                    details=f"密钥年龄: {key_age} 天, 警告阈值: {WARNING_KEY_AGE_DAYS} 天"
                ))

            # 检查密钥最后使用时间
            last_used = key.get("last_used_date", "N/A")
            if last_used != "N/A":
                try:
                    last_used_date = datetime.datetime.strptime(last_used, "%Y-%m-%d")
                    days_since_used = (datetime.datetime.now() - last_used_date).days
                    if days_since_used > 90:  # 超过 90 天未使用
                        results.append(CheckResult(
                            check_name="访问密钥使用率检查",
                            category="身份安全",
                            severity="medium",
                            status="warning",
                            resource=f"{username}/{key_id}",
                            description=f"密钥 {key_id} 已超过 {days_since_used} 天未使用",
                            recommendation="考虑删除长期未使用的密钥，减少攻击面",
                            details=f"最后使用时间: {last_used}"
                        ))
                except ValueError:
                    pass

    return results


# ============================================================
# 检查模块 4：安全组规则审计
# ============================================================

def check_security_groups(security_groups: List[Dict[str, Any]]) -> List[CheckResult]:
    """
    审计安全组规则配置

    检查项包括：
        - 高危端口是否公网开放
        - 是否存在全端口开放
        - 入站规则是否过于宽松
        - 出站规则是否需要限制

    参数：
        security_groups: 安全组配置列表

    返回值：
        检查结果列表
    """
    results = []

    # 定义高危端口列表
    HIGH_RISK_PORTS = {
        22: "SSH（远程登录）",
        23: "Telnet（明文传输）",
        3389: "RDP（远程桌面）",
        3306: "MySQL（数据库）",
        5432: "PostgreSQL（数据库）",
        6379: "Redis（缓存数据库）",
        27017: "MongoDB（数据库）",
        9200: "Elasticsearch（搜索引擎）",
        11211: "Memcached（缓存）",
        2375: "Docker API（容器管理）",
        2379: "etcd（K8s 键值存储）",
        6443: "Kubernetes API Server"
    }

    for sg in security_groups:
        sg_id = sg["group_id"]
        sg_name = sg["group_name"]
        inbound_rules = sg.get("inbound_rules", [])

        all_ports_open = False

        for rule in inbound_rules:
            port = rule["port"]
            source = rule["source"]

            # 检查 1：所有端口公网开放
            if port == "all" and source == "0.0.0.0/0":
                all_ports_open = True
                results.append(CheckResult(
                    check_name="安全组全端口开放检查",
                    category="网络安全",
                    severity="critical",
                    status="fail",
                    resource=sg_name,
                    description=f"安全组 {sg_name} 存在所有端口对 0.0.0.0/0 开放的规则",
                    recommendation="立即删除该规则，只开放必要的端口和来源",
                    details="这是最危险的安全组配置，等于没有防火墙"
                ))
                break  # 已经发现最严重的问题，不需要继续检查

            # 检查 2：高危端口公网开放
            if isinstance(port, int) and port in HIGH_RISK_PORTS and source == "0.0.0.0/0":
                service_name = HIGH_RISK_PORTS[port]
                severity = "critical" if port in [3306, 6379, 27017, 9200] else "high"

                results.append(CheckResult(
                    check_name="安全组高危端口检查",
                    category="网络安全",
                    severity=severity,
                    status="fail",
                    resource=sg_name,
                    description=f"安全组 {sg_name} 中 {service_name} 端口 {port} 对 0.0.0.0/0 开放",
                    recommendation=f"限制 {service_name} 端口 {port} 的访问来源，仅允许可信 IP 或安全组访问",
                    details=f"规则: {port} <- {source}"
                ))

        # 检查 3：安全组入站规则数量（过多可能意味着管理混乱）
        if len(inbound_rules) > 20:
            results.append(CheckResult(
                check_name="安全组规则数量检查",
                category="网络安全",
                severity="low",
                status="warning",
                resource=sg_name,
                description=f"安全组 {sg_name} 入站规则数量较多（{len(inbound_rules)} 条）",
                recommendation="定期审查安全组规则，移除不再需要的规则，保持最小权限",
                details="规则过多可能导致管理混乱，增加配置错误的风险"
            ))

        # 检查 4：出站规则（可选检查）
        outbound_rules = sg.get("outbound_rules", [])
        has_all_outbound = any(
            r.get("port") == "all" and r.get("destination") == "0.0.0.0/0"
            for r in outbound_rules
        )
        if has_all_outbound:
            results.append(CheckResult(
                check_name="安全组出站规则检查",
                category="网络安全",
                severity="info",
                status="warning",
                resource=sg_name,
                description=f"安全组 {sg_name} 出站规则允许所有流量",
                recommendation="根据业务需要限制出站流量，防止被入侵后数据外传或横向移动",
                details="默认出站全部允许是常见配置，高安全环境建议限制"
            ))

    return results


# ============================================================
# 检查模块 5：日志审计配置检查
# ============================================================

def check_logging_audit(cloudtrail_config: Dict[str, Any]) -> List[CheckResult]:
    """
    检查日志与审计配置

    检查项包括：
        - CloudTrail/操作审计是否启用
        - 是否为多区域跟踪
        - 是否启用日志文件验证
        - 日志是否加密存储
        - 是否配置告警

    参数：
        cloudtrail_config: CloudTrail 配置

    返回值：
        检查结果列表
    """
    results = []

    trails = cloudtrail_config.get("trails", [])

    if not trails:
        results.append(CheckResult(
            check_name="操作审计启用检查",
            category="日志审计",
            severity="critical",
            status="fail",
            resource="CloudTrail/操作审计",
            description="未启用 CloudTrail/操作审计",
            recommendation="立即启用操作审计，记录所有 API 调用活动",
            details="操作审计是云安全的基础，用于安全审计、合规检查和事件响应"
        ))
        return results

    for trail in trails:
        trail_name = trail["name"]

        # 检查 1：是否正在记录
        if not trail.get("is_logging", False):
            results.append(CheckResult(
                check_name="操作审计日志状态检查",
                category="日志审计",
                severity="high",
                status="fail",
                resource=trail_name,
                description=f"跟踪 {trail_name} 当前未在记录日志",
                recommendation="启用日志记录，确保所有 API 调用都被记录",
                details="未记录的操作将无法进行安全审计和事件追溯"
            ))

        # 检查 2：多区域跟踪
        if not trail.get("is_multi_region_trail", False):
            results.append(CheckResult(
                check_name="操作审计多区域检查",
                category="日志审计",
                severity="medium",
                status="fail",
                resource=trail_name,
                description=f"跟踪 {trail_name} 不是多区域跟踪",
                recommendation="启用多区域跟踪，覆盖所有区域的 API 调用",
                details="攻击者可能在未监控的区域进行操作"
            ))

        # 检查 3：日志文件验证
        if not trail.get("log_file_validation_enabled", False):
            results.append(CheckResult(
                check_name="操作审计日志完整性检查",
                category="日志审计",
                severity="medium",
                status="fail",
                resource=trail_name,
                description=f"跟踪 {trail_name} 未启用日志文件完整性验证",
                recommendation="启用日志文件验证，防止日志被篡改",
                details="日志完整性验证使用哈希算法确保日志文件未被修改"
            ))

        # 检查 4：日志加密
        if not trail.get("kms_key_id"):
            results.append(CheckResult(
                check_name="操作审计日志加密检查",
                category="日志审计",
                severity="low",
                status="warning",
                resource=trail_name,
                description=f"跟踪 {trail_name} 未使用 KMS 加密日志文件",
                recommendation="使用 KMS 密钥加密日志文件，增强日志安全性",
                details="日志文件可能包含敏感信息，建议加密存储"
            ))

        # 检查 5：全局服务事件
        if not trail.get("include_global_service_events", False):
            results.append(CheckResult(
                check_name="操作审计全局服务事件检查",
                category="日志审计",
                severity="medium",
                status="fail",
                resource=trail_name,
                description=f"跟踪 {trail_name} 未包含全局服务事件（如 IAM）",
                recommendation="启用全局服务事件记录，覆盖 IAM 等全局服务的操作",
                details="IAM 操作是安全监控的重点，必须被记录"
            ))

    # 检查 6：日志存储桶安全
    if not cloudtrail_config.get("bucket_public_access", True):
        # bucket_public_access 为 False 表示未公开（安全）
        results.append(CheckResult(
            check_name="日志存储桶公开访问检查",
            category="日志审计",
            severity="info",
            status="pass",
            resource="日志存储桶",
            description="日志存储桶未公开访问",
            recommendation="保持当前配置，确保日志桶为私有",
            details="日志数据属于敏感信息，必须严格控制访问权限"
        ))
    else:
        results.append(CheckResult(
            check_name="日志存储桶公开访问检查",
            category="日志审计",
            severity="critical",
            status="fail",
            resource="日志存储桶",
            description="日志存储桶存在公开访问风险",
            recommendation="立即将日志存储桶设置为私有，防止日志泄露",
            details="日志泄露可能导致攻击者了解安全配置和监控策略"
        ))

    # 检查 7：告警配置
    if not cloudtrail_config.get("sns_notifications_enabled", False):
        results.append(CheckResult(
            check_name="操作审计告警检查",
            category="日志审计",
            severity="medium",
            status="warning",
            resource="CloudTrail/操作审计",
            description="未配置操作审计实时告警",
            recommendation="配置关键操作的实时告警（如登录、权限变更等），及时发现异常",
            details="建议结合 CloudWatch/云监控配置告警规则"
        ))

    # 检查 8：数据事件（可选）
    if not cloudtrail_config.get("data_events_s3", False):
        results.append(CheckResult(
            check_name="数据事件记录检查",
            category="日志审计",
            severity="info",
            status="warning",
            resource="CloudTrail/操作审计",
            description="未记录 S3 数据事件",
            recommendation="对敏感存储桶启用数据事件记录，监控对象级别的操作",
            details="数据事件会增加日志量和成本，建议仅对敏感桶启用"
        ))

    return results


# ============================================================
# 安全评分计算
# ============================================================

def calculate_security_score(results: List[CheckResult]) -> float:
    """
    根据检查结果计算安全评分（0-100 分）

    评分规则：
        - 满分 100 分
        - 严重问题（critical）扣 15 分
        - 高危问题（high）扣 10 分
        - 中危问题（medium）扣 5 分
        - 低危问题（low）扣 2 分
        - 信息类（info）不扣分
        - 最低 0 分

    参数：
        results: 检查结果列表

    返回值：
        安全评分（保留 1 位小数）
    """
    score = 100.0

    # 各风险等级对应的扣分
    penalty_map = {
        "critical": 15,
        "high": 10,
        "medium": 5,
        "low": 2,
        "info": 0
    }

    for result in results:
        if result.status == "fail" or result.status == "warning":
            penalty = penalty_map.get(result.severity, 0)
            score -= penalty

    # 最低 0 分
    return max(0.0, round(score, 1))


# ============================================================
# 报告生成：文本报告
# ============================================================

def generate_text_report(report: SecurityReport) -> str:
    """
    生成文本格式的安全报告

    参数：
        report: 安全报告数据对象

    返回值：
        格式化的文本报告字符串
    """
    lines = []
    lines.append("=" * 70)
    lines.append("                   云 安 全 配 置 检 查 报 告")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"扫描时间：{report.scan_time}")
    lines.append(f"云平台：{report.platform}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("【扫描概览】")
    lines.append("-" * 70)
    lines.append(f"  总检查项数：{report.total_checks}")
    lines.append(f"  通过项数：  {report.passed_checks}")
    lines.append(f"  警告项数：  {report.warning_checks}")
    lines.append(f"  失败项数：  {report.failed_checks}")
    lines.append(f"  安全评分：  {report.score} / 100")
    lines.append("")

    # 安全等级评定
    if report.score >= 90:
        grade = "优秀（A）"
    elif report.score >= 80:
        grade = "良好（B）"
    elif report.score >= 70:
        grade = "一般（C）"
    elif report.score >= 60:
        grade = "较差（D）"
    else:
        grade = "危险（F）"
    lines.append(f"  安全等级：  {grade}")
    lines.append("")

    # 按类别统计
    lines.append("-" * 70)
    lines.append("【各分类检查统计】")
    lines.append("-" * 70)

    category_stats = {}
    for result in report.results:
        cat = result.category
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "pass": 0, "fail": 0, "warning": 0}
        category_stats[cat]["total"] += 1
        if result.status == "pass":
            category_stats[cat]["pass"] += 1
        elif result.status == "fail":
            category_stats[cat]["fail"] += 1
        elif result.status == "warning":
            category_stats[cat]["warning"] += 1

    for cat, stats in sorted(category_stats.items()):
        lines.append(f"  {cat}：共 {stats['total']} 项，通过 {stats['pass']}，警告 {stats['warning']}，失败 {stats['fail']}")
    lines.append("")

    # 严重问题列表
    critical_issues = [r for r in report.results if r.severity == "critical" and r.status != "pass"]
    if critical_issues:
        lines.append("-" * 70)
        lines.append("【严重问题（Critical）- 请立即处理】")
        lines.append("-" * 70)
        for i, result in enumerate(critical_issues, 1):
            lines.append(f"  {i}. [{result.category}] {result.resource}")
            lines.append(f"     问题：{result.description}")
            lines.append(f"     建议：{result.recommendation}")
            lines.append("")

    # 高危问题列表
    high_issues = [r for r in report.results if r.severity == "high" and r.status != "pass"]
    if high_issues:
        lines.append("-" * 70)
        lines.append("【高危问题（High）- 请尽快处理】")
        lines.append("-" * 70)
        for i, result in enumerate(high_issues, 1):
            lines.append(f"  {i}. [{result.category}] {result.resource}")
            lines.append(f"     问题：{result.description}")
            lines.append(f"     建议：{result.recommendation}")
            lines.append("")

    # 中危问题列表
    medium_issues = [r for r in report.results if r.severity == "medium" and r.status != "pass"]
    if medium_issues:
        lines.append("-" * 70)
        lines.append("【中危问题（Medium）- 建议修复】")
        lines.append("-" * 70)
        for i, result in enumerate(medium_issues, 1):
            lines.append(f"  {i}. [{result.category}] {result.resource}")
            lines.append(f"     问题：{result.description}")
            lines.append(f"     建议：{result.recommendation}")
            lines.append("")

    # 总结建议
    lines.append("-" * 70)
    lines.append("【安全建议总结】")
    lines.append("-" * 70)
    lines.append("  1. 立即处理所有严重（Critical）和高危（High）问题")
    lines.append("  2. 为所有 IAM 用户启用 MFA 多因素认证")
    lines.append("  3. 遵循最小权限原则，定期审计和清理权限")
    lines.append("  4. 定期轮换访问密钥（建议 90 天以内）")
    lines.append("  5. 严格控制安全组规则，禁止高危端口公网开放")
    lines.append("  6. 确保所有存储桶为私有，启用加密和日志")
    lines.append("  7. 启用全区域操作审计，配置关键操作告警")
    lines.append("  8. 建立定期安全审计机制，持续改进安全配置")
    lines.append("")
    lines.append("=" * 70)
    lines.append("                        报告结束")
    lines.append("=" * 70)

    return "\n".join(lines)


# ============================================================
# 报告生成：HTML 报告
# ============================================================

def generate_html_report(report: SecurityReport) -> str:
    """
    生成 HTML 格式的安全报告

    参数：
        report: 安全报告数据对象

    返回值：
        HTML 格式的报告字符串
    """
    # 严重等级对应的颜色和图标
    severity_styles = {
        "critical": {"color": "#dc2626", "bg": "#fef2f2", "label": "严重"},
        "high": {"color": "#ea580c", "bg": "#fff7ed", "label": "高危"},
        "medium": {"color": "#ca8a04", "bg": "#fefce8", "label": "中危"},
        "low": {"color": "#2563eb", "bg": "#eff6ff", "label": "低危"},
        "info": {"color": "#6b7280", "bg": "#f9fafb", "label": "信息"}
    }

    # 计算安全等级
    if report.score >= 90:
        grade = "优秀"
        grade_color = "#16a34a"
    elif report.score >= 80:
        grade = "良好"
        grade_color = "#2563eb"
    elif report.score >= 70:
        grade = "一般"
        grade_color = "#ca8a04"
    elif report.score >= 60:
        grade = "较差"
        grade_color = "#ea580c"
    else:
        grade = "危险"
        grade_color = "#dc2626"

    # 按类别分组
    category_groups = {}
    for result in report.results:
        cat = result.category
        if cat not in category_groups:
            category_groups[cat] = []
        category_groups[cat].append(result)

    # 生成问题列表 HTML
    issues_html = ""
    for cat, results in sorted(category_groups.items()):
        # 只显示非通过的项
        issues = [r for r in results if r.status != "pass"]
        if not issues:
            continue

        issues_html += f"""
        <div class="category-section">
            <h3 class="category-title">{html.escape(cat)}</h3>
            <div class="issues-list">
        """

        for result in issues:
            style = severity_styles.get(result.severity, severity_styles["info"])
            issues_html += f"""
                <div class="issue-card" style="border-left: 4px solid {style['color']};">
                    <div class="issue-header">
                        <span class="severity-badge" style="background-color: {style['color']};">{style['label']}</span>
                        <span class="issue-resource">{html.escape(result.resource)}</span>
                    </div>
                    <div class="issue-name">{html.escape(result.check_name)}</div>
                    <div class="issue-desc">{html.escape(result.description)}</div>
                    <div class="issue-recommend">
                        <strong>修复建议：</strong>{html.escape(result.recommendation)}
                    </div>
                    {f'<div class="issue-details"><details><summary>查看详情</summary><pre>{html.escape(result.details)}</pre></details></div>' if result.details else ''}
                </div>
            """

        issues_html += """
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>云安全配置检查报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            background-color: #f3f4f6;
            color: #1f2937;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .report-header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .report-header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .report-header .subtitle {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .summary-card .number {{
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .summary-card .label {{
            color: #6b7280;
            font-size: 14px;
        }}
        .score-card .number {{
            color: {grade_color};
            font-size: 48px;
        }}
        .score-card .grade {{
            color: {grade_color};
            font-size: 18px;
            font-weight: bold;
            margin-top: 4px;
        }}
        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        .section h2 {{
            font-size: 20px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }}
        .category-section {{
            margin-bottom: 30px;
        }}
        .category-title {{
            font-size: 16px;
            color: #374151;
            margin-bottom: 15px;
            padding-left: 12px;
            border-left: 4px solid #3b82f6;
        }}
        .issues-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .issue-card {{
            background: #fafafa;
            border-radius: 8px;
            padding: 16px;
            background-color: white;
            border: 1px solid #e5e7eb;
        }}
        .issue-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .severity-badge {{
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .issue-resource {{
            font-weight: 600;
            color: #1f2937;
        }}
        .issue-name {{
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 6px;
        }}
        .issue-desc {{
            font-size: 14px;
            color: #374151;
            margin-bottom: 8px;
        }}
        .issue-recommend {{
            font-size: 13px;
            color: #059669;
            background: #ecfdf5;
            padding: 8px 12px;
            border-radius: 6px;
        }}
        .issue-details {{
            margin-top: 8px;
            font-size: 12px;
        }}
        .issue-details details {{
            cursor: pointer;
        }}
        .issue-details pre {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin-top: 8px;
            font-size: 12px;
            line-height: 1.5;
        }}
        .recommendations {{
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 20px;
            border-radius: 8px;
        }}
        .recommendations h3 {{
            color: #1e40af;
            margin-bottom: 12px;
        }}
        .recommendations ol {{
            padding-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 8px;
        }}
        .report-footer {{
            text-align: center;
            color: #9ca3af;
            font-size: 12px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>云安全配置检查报告</h1>
            <div class="subtitle">扫描时间：{html.escape(report.scan_time)} | 云平台：{html.escape(report.platform)}</div>
        </div>

        <div class="summary-cards">
            <div class="summary-card score-card">
                <div class="number">{report.score}</div>
                <div class="label">安全评分</div>
                <div class="grade">{grade}</div>
            </div>
            <div class="summary-card">
                <div class="number">{report.total_checks}</div>
                <div class="label">检查项总数</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color: #16a34a;">{report.passed_checks}</div>
                <div class="label">通过项</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color: #dc2626;">{report.failed_checks}</div>
                <div class="label">失败项</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color: #ca8a04;">{report.warning_checks}</div>
                <div class="label">警告项</div>
            </div>
        </div>

        <div class="section">
            <h2>安全问题清单</h2>
            {issues_html}
        </div>

        <div class="section">
            <div class="recommendations">
                <h3>安全建议总结</h3>
                <ol>
                    <li><strong>立即处理</strong>所有严重（Critical）和高危（High）安全问题</li>
                    <li>为所有 IAM / RAM 用户<strong>启用 MFA 多因素认证</strong></li>
                    <li>遵循<strong>最小权限原则</strong>，定期审计和清理权限配置</li>
                    <li>定期轮换访问密钥（建议<strong>90 天</strong>以内）</li>
                    <li>严格控制安全组规则，<strong>禁止高危端口公网开放</strong></li>
                    <li>确保所有对象存储桶为<strong>私有</strong>，启用加密和访问日志</li>
                    <li>启用<strong>全区域操作审计</strong>，配置关键操作实时告警</li>
                    <li>建立<strong>定期安全审计</strong>机制，持续改进安全配置</li>
                </ol>
            </div>
        </div>

        <div class="report-footer">
            本报告由云安全配置检查工具自动生成 | 仅供学习和参考使用
        </div>
    </div>
</body>
</html>"""

    return html_content


# ============================================================
# 主程序入口
# ============================================================

def run_mode_mock() -> SecurityReport:
    """
    模拟模式：使用内置的模拟数据运行安全检查

    返回值：
        安全报告对象
    """
    print("[*] 正在使用模拟数据运行安全检查...")
    print()

    # 生成模拟数据
    buckets = generate_mock_s3_buckets()
    users = generate_mock_iam_users()
    roles = generate_mock_iam_roles()
    security_groups = generate_mock_security_groups()
    cloudtrail_config = generate_mock_cloudtrail_config()

    # 运行各项检查
    all_results = []

    print("  [1/5] 检查 S3 存储桶权限...")
    s3_results = check_s3_bucket_permissions(buckets)
    all_results.extend(s3_results)
    print(f"        发现 {len(s3_results)} 个问题")

    print("  [2/5] 检查 IAM 配置...")
    iam_results = check_iam_config(users, roles)
    all_results.extend(iam_results)
    print(f"        发现 {len(iam_results)} 个问题")

    print("  [3/5] 检查访问密钥轮换...")
    key_results = check_access_key_rotation(users)
    all_results.extend(key_results)
    print(f"        发现 {len(key_results)} 个问题")

    print("  [4/5] 审计安全组规则...")
    sg_results = check_security_groups(security_groups)
    all_results.extend(sg_results)
    print(f"        发现 {len(sg_results)} 个问题")

    print("  [5/5] 检查日志审计配置...")
    log_results = check_logging_audit(cloudtrail_config)
    all_results.extend(log_results)
    print(f"        发现 {len(log_results)} 个问题")

    print()

    # 统计结果
    passed = sum(1 for r in all_results if r.status == "pass")
    failed = sum(1 for r in all_results if r.status == "fail")
    warning = sum(1 for r in all_results if r.status == "warning")

    # 计算安全评分
    score = calculate_security_score(all_results)

    # 构建报告
    report = SecurityReport(
        scan_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        platform="模拟环境 (Mock)",
        total_checks=len(all_results),
        passed_checks=passed,
        failed_checks=failed,
        warning_checks=warning,
        results=all_results,
        score=score
    )

    return report


def run_mode_aws() -> Optional[SecurityReport]:
    """
    AWS 模式：使用真实 AWS API 进行安全检查

    注意：需要安装 boto3 并配置好 AWS 凭证
    """
    try:
        import boto3
    except ImportError:
        print("[!] 错误：未安装 boto3 库，请先安装：pip install boto3")
        return None

    print("[*] 正在使用 AWS API 运行安全检查...")
    print("[*] 注意：请确保已配置好 AWS 凭证（~/.aws/credentials）")
    print()

    try:
        # 这里可以实现真实的 AWS API 调用
        # 由于是学习工具，这里给出调用示例框架
        print("  [提示] 真实 AWS 模式需要以下权限：")
        print("        - s3:ListBuckets, s3:GetBucketPolicy, s3:GetEncryptionConfiguration")
        print("        - iam:ListUsers, iam:ListAccessKeys, iam:GetUserPolicy")
        print("        - ec2:DescribeSecurityGroups")
        print("        - cloudtrail:DescribeTrails, cloudtrail:GetTrailStatus")
        print()
        print("  [提示] 为了演示方便，当前使用模拟数据。")
        print("        如需真实扫描，请实现对应的 boto3 调用代码。")
        print()

        # 实际使用时，可替换为真实的 API 调用
        # 这里暂时使用模拟数据
        return run_mode_mock()

    except Exception as e:
        print(f"[!] 错误：{e}")
        return None


def main():
    """
    主函数：解析命令行参数，执行安全检查，生成报告
    """
    parser = argparse.ArgumentParser(
        description="云安全配置检查工具 v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python cloud_security_check.py                    # 使用模拟数据
  python cloud_security_check.py --mode aws         # 使用 AWS API
  python cloud_security_check.py --report report.html  # 生成 HTML 报告
  python cloud_security_check.py --json result.json   # 输出 JSON 结果
        """
    )

    parser.add_argument(
        "--mode",
        choices=["mock", "aws", "aliyun"],
        default="mock",
        help="运行模式：mock（模拟数据）/ aws（AWS API）/ aliyun（阿里云 API），默认 mock"
    )

    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="生成 HTML 格式报告，指定输出文件路径"
    )

    parser.add_argument(
        "--json",
        type=str,
        default=None,
        help="输出 JSON 格式结果，指定输出文件路径"
    )

    args = parser.parse_args()

    # 打印欢迎信息
    print()
    print("=" * 60)
    print("        云安全配置检查工具 v1.0.0")
    print("=" * 60)
    print()

    # 根据模式运行检查
    if args.mode == "mock":
        report = run_mode_mock()
    elif args.mode == "aws":
        report = run_mode_aws()
        if report is None:
            sys.exit(1)
    elif args.mode == "aliyun":
        print("[*] 阿里云模式开发中，暂时使用模拟数据...")
        print()
        report = run_mode_mock()
    else:
        print(f"[!] 不支持的模式：{args.mode}")
        sys.exit(1)

    # 生成文本报告并打印
    text_report = generate_text_report(report)
    print(text_report)

    # 保存 HTML 报告
    if args.report:
        html_report = generate_html_report(report)
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(html_report)
        print(f"[+] HTML 报告已保存到：{args.report}")

    # 保存 JSON 结果
    if args.json:
        # 将结果转换为可序列化的格式
        json_data = {
            "scan_time": report.scan_time,
            "platform": report.platform,
            "total_checks": report.total_checks,
            "passed_checks": report.passed_checks,
            "failed_checks": report.failed_checks,
            "warning_checks": report.warning_checks,
            "score": report.score,
            "results": [
                {
                    "check_name": r.check_name,
                    "category": r.category,
                    "severity": r.severity,
                    "status": r.status,
                    "resource": r.resource,
                    "description": r.description,
                    "recommendation": r.recommendation,
                    "details": r.details
                }
                for r in report.results
            ]
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"[+] JSON 结果已保存到：{args.json}")

    print()
    print("[*] 检查完成！")
    print()


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    main()
