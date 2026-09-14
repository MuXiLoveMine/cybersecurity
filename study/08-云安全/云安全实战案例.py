#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
 云安全实战案例工具集
================================================================================

[安全声明]
    本工具集仅供授权安全测试、网络安全教学和防御研究使用。
    严禁用于未经授权的云资源探测、数据窃取或任何非法用途。
    使用者须确保已获得云资源所有者的书面授权，并遵守当地法律法规。
    严禁尝试访问非授权的云存储桶、数据库或计算实例。
    作者不对任何滥用本工具造成的后果承担责任。

[文件说明]
    本文件涵盖云安全领域的六大实战主题：
      1. 云存储安全检测 —— S3/OSS Bucket公开访问、ACL审计、敏感数据扫描
      2. IAM权限审计 —— 最小权限检查、过度权限检测、闲置密钥检测
      3. 云网络安全 —— 安全组审计、网络ACL检查、暴露面分析
      4. 容器安全检测 —— Docker镜像漏洞、K8s配置审计、RBAC检查
      5. Serverless安全 —— 函数权限检查、事件源验证、环境变量泄露
      6. 云合规检查 —— 等保2.0云安全要求、CIS基准检查

    所有输出均为模拟数据，不依赖外部第三方库，仅使用 Python 标准库。
    代码可直接运行，适合课堂教学和自主学习演示。

[运行方式]
    python 云安全实战案例.py
================================================================================
"""

import os
import re
import json
import time
import hashlib
import base64
from datetime import datetime, timedelta
from collections import defaultdict, Counter


# ============================================================================
# 模块一：云存储安全检测
# ============================================================================

class 云存储安全检测器:
    """
    云存储安全检测器 —— 检测S3/OSS等对象存储的安全配置。

    技术原理：
        云对象存储（AWS S3 / 阿里云OSS / 腾讯云COS / Azure Blob）是企业
        数据湖和静态网站托管的常用方案。常见的存储安全风险包括：
        1. Bucket公开访问：ACL或策略配置为public-read，任何人可读取
        2. List权限暴露：允许匿名ListObjects，可枚举所有文件
        3. Write权限暴露：允许匿名PutObject，可上传恶意文件
        4. 敏感数据泄露：存储桶中包含密码、密钥、PII等敏感数据
        5. 版本控制未启用：无法恢复误删或被加密勒索的文件
        6. 日志未启用：无法审计谁访问了什么数据
        7. 传输未加密：HTTP明文访问，数据可被嗅探

        检测工具：aws-cli、boto3、scoutsuite、prowler、cloudsploit。
        公开Bucket枚举：grayhatwarfare、buckets.grayhatwarfare.com。
    """

    # 模拟S3 Bucket列表
    Bucket列表 = [
        {
            "名称": "company-prod-data",
            "区域": "us-east-1",
            "大小": "2.3 TB",
            "对象数": 152340,
            "公开访问": False,
            "ACL": "私有",
            "策略": "BucketPolicy-2024",
            "版本控制": True,
            "日志": True,
            "加密": "SSE-S3",
            "TLS": True,
            "标签": {"环境": "生产", "数据类型": "业务数据", "合规": "PCI-DSS"}
        },
        {
            "名称": "company-backup-archive",
            "区域": "us-east-1",
            "大小": "5.7 TB",
            "对象数": 892000,
            "公开访问": False,
            "ACL": "私有",
            "策略": "无",
            "版本控制": True,
            "日志": False,
            "加密": "无",
            "TLS": True,
            "标签": {"环境": "生产", "数据类型": "备份归档"}
        },
        {
            "名称": "company-public-assets",
            "区域": "ap-northeast-1",
            "大小": "150 GB",
            "对象数": 45200,
            "公开访问": True,
            "ACL": "public-read",
            "策略": "PublicReadGetObject",
            "版本控制": False,
            "日志": False,
            "加密": "SSE-S3",
            "TLS": True,
            "标签": {"环境": "生产", "数据类型": "静态资源"}
        },
        {
            "名称": "company-dev-uploads",
            "区域": "us-west-2",
            "大小": "45 GB",
            "对象数": 8900,
            "公开访问": True,
            "ACL": "public-read-write",
            "策略": "PublicReadWrite",
            "版本控制": False,
            "日志": False,
            "加密": "无",
            "TLS": False,
            "标签": {"环境": "开发", "数据类型": "测试数据"}
        },
        {
            "名称": "company-logs-central",
            "区域": "us-east-1",
            "大小": "1.2 TB",
            "对象数": 1200000,
            "公开访问": False,
            "ACL": "私有",
            "策略": "LogDeliveryWrite",
            "版本控制": True,
            "日志": True,
            "加密": "SSE-KMS",
            "TLS": True,
            "标签": {"环境": "生产", "数据类型": "安全日志"}
        },
        {
            "名称": "company-temp-share",
            "区域": "ap-southeast-1",
            "大小": "2.1 GB",
            "对象数": 120,
            "公开访问": True,
            "ACL": "public-read",
            "策略": "无",
            "版本控制": False,
            "日志": False,
            "加密": "无",
            "TLS": False,
            "标签": {"环境": "临时", "数据类型": "文件分享"}
        }
    ]

    # 模拟敏感对象内容
    敏感对象 = [
        {"Bucket": "company-dev-uploads", "Key": "config/database.yml",
         "类型": "数据库配置", "风险": "严重",
         "内容": "production:\n  host: 10.0.1.100\n  username: db_admin\n  password: Pr0dDB$ecret2024\n  port: 3306"},
        {"Bucket": "company-dev-uploads", "Key": ".env.production",
         "类型": "环境变量文件", "风险": "严重",
         "内容": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\nDB_PASSWORD=Admin@2024"},
        {"Bucket": "company-dev-uploads", "Key": "secrets/api_keys.json",
         "类型": "API密钥文件", "风险": "严重",
         "内容": '{"stripe": "sk_live_51Hxxx...", "twilio": "ACxxx...", "sendgrid": "SG.xxx..."}'},
        {"Bucket": "company-dev-uploads", "Key": "ssh/id_rsa",
         "类型": "SSH私钥", "风险": "严重",
         "内容": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAxxx...\n-----END RSA PRIVATE KEY-----"},
        {"Bucket": "company-dev-uploads", "Key": "backup/customer_data.csv",
         "类型": "客户PII数据", "风险": "高",
         "内容": "id,name,email,phone,id_card\n1,张三,zhangsan@email.com,13800001111,110101199001011234"},
        {"Bucket": "company-temp-share", "Key": "reports/financial_2024Q3.xlsx",
         "类型": "财务报表", "风险": "高",
         "内容": "[二进制Excel文件 - 含季度财务数据]"},
        {"Bucket": "company-temp-share", "Key": "contracts/vendor_agreement.pdf",
         "类型": "合同文件", "风险": "中",
         "内容": "[PDF文件 - 供应商合同协议]"},
        {"Bucket": "company-public-assets", "Key": "js/config.js",
         "类型": "前端配置泄露", "风险": "高",
         "内容": "const API_KEY = 'AIzaSyB-xxxxxxxxxxxxxxxxxxxx';\nconst ENDPOINT = 'https://api.internal.company.com';"},
    ]

    def __init__(self):
        self.检测结果 = []
        self.公开Bucket = []

    def 扫描Bucket列表(self):
        """扫描云账户下所有存储桶"""
        print("=" * 70)
        print("[存储扫描] 枚举云账户下所有对象存储Bucket...")
        print("=" * 70)

        print(f"\n  [*] 正在枚举S3 Buckets...")
        time.sleep(0.5)
        print(f"  [+] 共发现 {len(self.Bucket列表)} 个Bucket\n")

        print(f"  {'Bucket名称':<28} {'区域':<16} {'大小':<10} {'对象数':<10} {'公开'}")
        print(f"  {'-'*28} {'-'*16} {'-'*10} {'-'*10} {'-'*6}")

        for b in self.Bucket列表:
            公开 = "是!" if b["公开访问"] else "否"
            print(f"  {b['名称']:<28} {b['区域']:<16} {b['大小']:<10} "
                  f"{b['对象数']:<10} {公开}")
            if b["公开访问"]:
                self.公开Bucket.append(b)
                self.检测结果.append(("Bucket公开访问", "严重",
                                        f"{b['名称']} - {b['ACL']}"))

        print(f"\n  [+] 公开访问的Bucket: {len(self.公开Bucket)} 个")
        return self.Bucket列表

    def 审计ACL配置(self):
        """审计Bucket ACL（访问控制列表）配置"""
        print("\n" + "-" * 70)
        print("[ACL审计] 检查存储桶访问控制列表配置...")
        print("-" * 70)

        ACL风险等级 = {
            "private": ("安全", "仅Bucket所有者可访问"),
            "public-read": ("严重", "任何人可读取对象内容"),
            "public-read-write": ("严重", "任何人可读写，极度危险"),
            "authenticated-read": ("中", "任何AWS认证用户可读"),
            "log-delivery-write": ("低", "日志投递服务可写"),
        }

        print(f"\n  {'Bucket名称':<28} {'ACL':<22} {'风险':<6} {'说明'}")
        print(f"  {'-'*28} {'-'*22} {'-'*6} {'-'*30}")

        for b in self.Bucket列表:
            风险, 说明 = ACL风险等级.get(b["ACL"].lower(), ("未知", "未知ACL"))
            print(f"  {b['名称']:<28} {b['ACL']:<22} {风险:<6} {说明}")

        # 检查Bucket策略
        print(f"\n  [Bucket策略检查]")
        for b in self.Bucket列表:
            if b["策略"] != "无":
                print(f"\n  Bucket: {b['名称']}")
                print(f"  策略: {b['策略']}")

                # 分析策略中的风险
                if "Public" in b["策略"]:
                    print(f"    [!] 策略允许公开访问")
                    self.检测结果.append(("策略公开访问", "严重",
                                            f"{b['名称']} - {b['策略']}"))
                if "Write" in b["策略"] and "Public" in b["策略"]:
                    print(f"    [!] 策略允许公开写入！可上传任意文件")
                    self.检测结果.append(("策略公开写入", "严重",
                                            f"{b['名称']} - {b['策略']}"))

        return self.检测结果

    def 扫描敏感数据(self):
        """扫描公开Bucket中的敏感数据"""
        print("\n" + "-" * 70)
        print("[敏感数据] 扫描公开存储桶中的敏感文件...")
        print("-" * 70)

        # 敏感文件模式
        敏感模式 = {
            ".env": "环境变量文件",
            ".pem": "SSL证书/私钥",
            "id_rsa": "SSH私钥",
            ".key": "密钥文件",
            "password": "密码文件",
            "secret": "密钥文件",
            "credential": "凭据文件",
            ".sql": "数据库导出",
            ".csv": "数据文件(可能含PII)",
            ".xlsx": "Excel文件(可能含敏感数据)",
            "config": "配置文件",
            "database": "数据库配置",
            "api_key": "API密钥文件",
        }

        公开Bucket名称 = [b["名称"] for b in self.公开Bucket]
        公开敏感文件 = [f for f in self.敏感对象 if f["Bucket"] in 公开Bucket名称]

        print(f"\n  [敏感文件检测结果]")
        print(f"  扫描Bucket: {', '.join(公开Bucket名称)}")
        print(f"  发现敏感文件: {len(公开敏感文件)} 个\n")

        print(f"  {'文件路径':<40} {'类型':<15} {'风险':<6}")
        print(f"  {'-'*40} {'-'*15} {'-'*6}")

        for f in 公开敏感文件:
            print(f"  {f['Bucket']}/{f['Key']:<38} {f['类型']:<15} {f['风险']}")
            self.检测结果.append(("敏感数据泄露", f["风险"],
                                    f"{f['Bucket']}/{f['Key']} - {f['类型']}"))

        # 展示敏感文件内容预览
        print(f"\n  [敏感文件内容预览]")
        for f in 公开敏感文件[:4]:
            print(f"\n  ── {f['Bucket']}/{f['Key']}")
            print(f"     类型: {f['类型']}  风险: {f['风险']}")
            预览 = f['内容'][:80].replace('\n', '\\n')
            print(f"     预览: {预览}...")

        return 公开敏感文件

    def 检查存储配置(self):
        """检查存储桶安全配置（加密、版本、日志、TLS）"""
        print("\n" + "-" * 70)
        print("[配置检查] 检查存储桶安全配置...")
        print("-" * 70)

        配置检查项 = [
            ("版本控制", "启用版本控制以防止误删和勒索", "v", "版本控制"),
            ("日志", "启用访问日志以审计数据访问", "l", "日志"),
            ("加密", "启用SSE-S3或SSE-KMS加密", "e", "加密"),
            ("TLS", "强制HTTPS传输加密", "t", "TLS"),
        ]

        print(f"\n  {'Bucket名称':<28} {'版本':<6} {'日志':<6} {'加密':<10} {'TLS':<6} {'问题数'}")
        print(f"  {'-'*28} {'-'*6} {'-'*6} {'-'*10} {'-'*6} {'-'*6}")

        for b in self.Bucket列表:
            问题数 = 0
            if not b["版本控制"]:
                问题数 += 1
            if not b["日志"]:
                问题数 += 1
            if b["加密"] == "无":
                问题数 += 1
            if not b["TLS"]:
                问题数 += 1

            print(f"  {b['名称']:<28} {'是' if b['版本控制'] else '否':<6} "
                  f"{'是' if b['日志'] else '否':<6} "
                  f"{b['加密']:<10} {'是' if b['TLS'] else '否':<6} {问题数}")

            if 问题数 > 0:
                self.检测结果.append(("配置缺陷", "中" if 问题数 <= 2 else "高",
                                        f"{b['名称']} - {问题数}项配置缺失"))

        print(f"\n  [配置建议]")
        建议 = [
            "1. 所有生产Bucket启用版本控制（防误删+勒索恢复）",
            "2. 所有Bucket启用服务器端加密（SSE-KMS推荐）",
            "3. 所有Bucket启用访问日志（审计合规）",
            "4. 使用Bucket Policy强制TLS（拒绝HTTP请求）",
            "5. 启用S3 Object Lock实现WORM存储（防篡改）",
            "6. 配置Lifecycle策略自动迁移冷数据到Glacier",
        ]
        for s in 建议:
            print(f"    {s}")

    def 生成存储检测报告(self):
        """生成云存储安全检测报告"""
        print("\n" + "=" * 70)
        print("[存储报告] 云存储安全检测综合报告")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.检测结果)
        print(f"\n  [检测摘要]")
        print(f"    Bucket总数      : {len(self.Bucket列表)}")
        print(f"    公开访问Bucket  : {len(self.公开Bucket)}")
        print(f"    敏感数据泄露文件: {sum(1 for r in self.检测结果 if r[0]=='敏感数据泄露')}")
        print(f"    安全问题总数    : {len(self.检测结果)}")

        print(f"\n  [风险分布]")
        for 风险 in ["严重", "高", "中", "低"]:
            print(f"    {风险}: {风险统计.get(风险, 0)} 项")

        print(f"\n  [修复建议优先级]")
        修复建议 = [
            "P0: 立即关闭company-dev-uploads的公开读写权限",
            "P0: 立即清除公开Bucket中的密钥/密码/PII文件",
            "P0: 轮换泄露的AWS密钥和数据库密码",
            "P1: 关闭company-temp-share和company-public-assets的公开读权限",
            "P1: 为所有未加密Bucket启用SSE-KMS",
            "P2: 启用版本控制和访问日志",
            "P2: 配置Bucket Policy强制HTTPS传输",
            "P3: 建立存储安全自动化扫描流水线",
        ]
        for s in 修复建议:
            print(f"    {s}")

        return {"Bucket数": len(self.Bucket列表),
                "公开Bucket": len(self.公开Bucket),
                "问题数": len(self.检测结果)}


# ============================================================================
# 模块二：IAM权限审计
# ============================================================================

class IAM权限审计器:
    """
    IAM权限审计器 —— 审计云身份和访问管理（IAM）安全配置。

    技术原理：
        IAM（Identity and Access Management）是云安全的核心，控制谁可以
        访问什么云资源。常见的IAM安全风险：
        1. 过度权限：授予了超出工作需要的权限（如管理员权限给开发人员）
        2. 违反最小权限原则：使用*通配符授权所有操作
        3. 闲置访问密钥：创建后从未使用或长期未轮换的AK/SK
        4. Root账户使用：使用Root账户进行日常操作
        5. 缺乏MFA：关键账户未启用多因素认证
        6. 交叉账户角色：外部账户可扮演的角色权限过大
        7. 密码策略弱：密码长度/复杂度/轮换策略不符合要求

        审计工具：AWS IAM Access Analyzer、CloudTrail、scoutsuite、prowler。
        IAM策略语言：JSON格式的Statement+Action+Resource+Effect。
    """

    # 模拟IAM用户列表
    IAM用户 = [
        {
            "用户名": "admin-root",
            "类型": "根账户",
            "权限": "AdministratorAccess",
            "MFA": False,
            "最后登录": "2024-09-01",
            "密钥数": 2,
            "密钥状态": ["活跃-30天未轮换", "活跃-180天未轮换"],
            "风险": "严重"
        },
        {
            "用户名": "dev-team-lead",
            "类型": "IAM用户",
            "权限": "PowerUserAccess + EC2FullAccess",
            "MFA": True,
            "最后登录": "2024-09-10",
            "密钥数": 1,
            "密钥状态": ["活跃-90天"],
            "风险": "中"
        },
        {
            "用户名": "dev-junior-01",
            "类型": "IAM用户",
            "权限": "AdministratorAccess",
            "MFA": False,
            "最后登录": "2024-08-15",
            "密钥数": 1,
            "密钥状态": ["活跃-200天未轮换"],
            "风险": "高"
        },
        {
            "用户名": "ci-cd-deploy",
            "类型": "服务角色",
            "权限": "EC2FullAccess + S3FullAccess + IAMFullAccess",
            "MFA": "N/A",
            "最后登录": "2024-09-11",
            "密钥数": 1,
            "密钥状态": ["活跃-365天未轮换"],
            "风险": "高"
        },
        {
            "用户名": "data-analyst",
            "类型": "IAM用户",
            "权限": "AmazonS3ReadOnlyAccess + AthenaFullAccess",
            "MFA": True,
            "最后登录": "2024-09-09",
            "密钥数": 0,
            "密钥状态": [],
            "风险": "低"
        },
        {
            "用户名": "external-auditor",
            "类型": "外部角色",
            "权限": "ReadOnlyAccess",
            "MFA": True,
            "最后登录": "2024-07-20",
            "密钥数": 0,
            "密钥状态": [],
            "风险": "中"
        },
        {
            "用户名": "old-service-account",
            "类型": "服务角色",
            "权限": "EC2FullAccess + S3FullAccess + LambdaFullAccess",
            "MFA": "N/A",
            "最后登录": "2023-12-01",
            "密钥数": 2,
            "密钥状态": ["闲置-280天", "闲置-280天"],
            "风险": "高"
        },
        {
            "用户名": "intern-summer",
            "类型": "IAM用户",
            "权限": "AdministratorAccess",
            "MFA": False,
            "最后登录": "2024-08-30",
            "密钥数": 1,
            "密钥状态": ["活跃-30天"],
            "风险": "严重"
        }
    ]

    # 模拟IAM策略
    IAM策略 = [
        {
            "名称": "AdminFullAccess",
            "附加用户": ["admin-root", "dev-junior-01", "intern-summer"],
            "Statement": {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            },
            "风险": "严重",
            "说明": "使用通配符授权所有操作和所有资源，违反最小权限原则"
        },
        {
            "名称": "CICD-Deploy-Policy",
            "附加用户": ["ci-cd-deploy"],
            "Statement": {
                "Effect": "Allow",
                "Action": ["ec2:*", "s3:*", "iam:*"],
                "Resource": "*"
            },
            "风险": "高",
            "说明": "CI/CD服务拥有IAMFullAccess，可创建新管理员账户"
        },
        {
            "名称": "DataAnalyst-Policy",
            "附加用户": ["data-analyst"],
            "Statement": {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket", "athena:*"],
                "Resource": ["arn:aws:s3:::company-prod-data/*",
                             "arn:aws:s3:::company-logs-central/*"]
            },
            "风险": "低",
            "说明": "遵循最小权限原则，仅授权特定Bucket的特定操作"
        },
        {
            "名称": "OldService-Policy",
            "附加用户": ["old-service-account"],
            "Statement": {
                "Effect": "Allow",
                "Action": ["ec2:*", "s3:*", "lambda:*"],
                "Resource": "*"
            },
            "风险": "高",
            "说明": "闲置服务账户拥有过度权限，且服务已停用280天"
        }
    ]

    def __init__(self):
        self.审计结果 = []

    def 检查最小权限原则(self):
        """检查IAM策略是否符合最小权限原则"""
        print("=" * 70)
        print("[权限审计] 检查IAM策略最小权限原则合规性...")
        print("=" * 70)

        print(f"\n  [最小权限原则检查]")
        违规列表 = []
        for 策略 in self.IAM策略:
            违规 = False
            违规原因 = []

            # 检查Action通配符
            action = 策略["Statement"]["Action"]
            if action == "*" or (isinstance(action, list) and "*" in action):
                违规 = True
                违规原因.append("Action使用通配符*")

            # 检查Resource通配符
            resource = 策略["Statement"]["Resource"]
            if resource == "*" or (isinstance(resource, list) and "*" in resource):
                违规 = True
                违规原因.append("Resource使用通配符*")

            状态 = "违规" if 违规 else "合规"
            print(f"\n  策略: {策略['名称']}")
            print(f"  附加: {', '.join(策略['附加用户'])}")
            print(f"  Action: {action}")
            print(f"  Resource: {resource}")
            print(f"  状态: {状态}  风险: {策略['风险']}")
            if 违规:
                print(f"  违规原因: {', '.join(违规原因)}")
                print(f"  说明: {策略['说明']}")
                违规列表.append(策略)
                self.审计结果.append(("最小权限违规", 策略["风险"],
                                        f"{策略['名称']} - {策略['说明']}"))

        print(f"\n  [+] 共 {len(self.IAM策略)} 个策略，{len(违规列表)} 个违规")
        return 违规列表

    def 检测过度权限(self):
        """检测IAM用户的过度权限分配"""
        print("\n" + "-" * 70)
        print("[过度权限] 检测用户是否拥有超出工作需要的权限...")
        print("-" * 70)

        # 权限矩阵分析
        过度权限检测 = []
        for 用户 in self.IAM用户:
            权限 = 用户["权限"]
            过度 = False
            问题 = []

            if "AdministratorAccess" in 权限:
                过度 = True
                问题.append("拥有管理员权限")
            if "IAMFullAccess" in 权限 and "服务" not in 用户["类型"]:
                过度 = True
                问题.append("拥有IAM管理权限")
            if "*" in 权限:
                过度 = True
                问题.append("使用通配符权限")

            if 过度:
                过度权限检测.append((用户, 问题))

        print(f"\n  {'用户名':<25} {'类型':<12} {'权限':<45} {'风险':<6}")
        print(f"  {'-'*25} {'-'*12} {'-'*45} {'-'*6}")

        for 用户 in self.IAM用户:
            print(f"  {用户['用户名']:<25} {用户['类型']:<12} "
                  f"{用户['权限']:<45} {用户['风险']:<6}")

        print(f"\n  [过度权限分析]")
        for 用户, 问题 in 过度权限检测:
            print(f"\n  用户: {用户['用户名']} ({用户['类型']})")
            print(f"  权限: {用户['权限']}")
            print(f"  问题: {'; '.join(问题)}")
            print(f"  风险: {用户['风险']}")
            建议 = "降级为最小权限，仅保留工作所需操作" if "管理员" not in 用户["类型"] else \
                   "Root账户应仅用于账户级操作，日常使用IAM用户"
            print(f"  建议: {建议}")
            self.审计结果.append(("过度权限", 用户["风险"],
                                    f"{用户['用户名']} - {'; '.join(问题)}"))

        return 过度权限检测

    def 检测闲置密钥(self):
        """检测闲置的访问密钥（Access Key）"""
        print("\n" + "-" * 70)
        print("[闲置密钥] 检测长期未使用或未轮换的访问密钥...")
        print("-" * 70)

        闲置密钥 = []
        未轮换密钥 = []

        for 用户 in self.IAM用户:
            if 用户["密钥数"] == 0:
                continue

            for 状态 in 用户["密钥状态"]:
                if "闲置" in 状态:
                    闲置密钥.append((用户["用户名"], 状态))
                    self.审计结果.append(("闲置密钥", "高",
                                            f"{用户['用户名']} - {状态}"))
                elif "未轮换" in 状态:
                    未轮换密钥.append((用户["用户名"], 状态))
                    self.审计结果.append(("密钥未轮换", "中",
                                            f"{用户['用户名']} - {状态}"))

        print(f"\n  [闲置访问密钥] (从未使用或长期不活跃)")
        print(f"  {'用户名':<25} {'密钥状态':<25}")
        print(f"  {'-'*25} {'-'*25}")
        for 用户, 状态 in 闲置密钥:
            print(f"  {用户:<25} {状态:<25}")

        print(f"\n  [未轮换访问密钥] (超过90天未轮换)")
        print(f"  {'用户名':<25} {'密钥状态':<25}")
        print(f"  {'-'*25} {'-'*25}")
        for 用户, 状态 in 未轮换密钥:
            print(f"  {用户:<25} {状态:<25}")

        print(f"\n  [+] 闲置密钥: {len(闲置密钥)} 个")
        print(f"  [+] 未轮换密钥: {len(未轮换密钥)} 个")
        print(f"  [建议]")
        建议 = [
            "1. 立即禁用所有闲置访问密钥",
            "2. 超过90天的密钥应轮换",
            "3. CI/CD使用IAM角色替代长期密钥",
            "4. 启用AWS Credential Report定期审计",
            "5. 使用AWS IAM Access Analyzer检测外部访问",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"闲置密钥": len(闲置密钥), "未轮换密钥": len(未轮换密钥)}

    def 检查MFA配置(self):
        """检查多因素认证（MFA）配置"""
        print("\n" + "-" * 70)
        print("[MFA检查] 检查多因素认证配置情况...")
        print("-" * 70)

        print(f"\n  {'用户名':<25} {'类型':<12} {'MFA':<8} {'风险':<6} {'建议'}")
        print(f"  {'-'*25} {'-'*12} {'-'*8} {'-'*6} {'-'*30}")

        无MFA用户 = []
        for 用户 in self.IAM用户:
            mfa状态 = "已启用" if 用户["MFA"] else "未启用!"
            建议 = "-" if 用户["MFA"] else "立即启用MFA"
            if not 用户["MFA"] and 用户["MFA"] != "N/A":
                无MFA用户.append(用户)
                self.审计结果.append(("未启用MFA", 用户["风险"],
                                        f"{用户['用户名']} - 未启用MFA"))

            print(f"  {用户['用户名']:<25} {用户['类型']:<12} "
                  f"{mfa状态:<8} {用户['风险']:<6} {建议}")

        print(f"\n  [+] 未启用MFA的用户: {len(无MFA用户)} 个")
        for u in 无MFA用户:
            print(f"    - {u['用户名']} ({u['类型']}) - {u['风险']}风险")

    def 生成IAM审计报告(self):
        """生成IAM权限审计报告"""
        print("\n" + "=" * 70)
        print("[IAM报告] IAM权限审计综合报告")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.审计结果)
        print(f"\n  [审计摘要]")
        print(f"    IAM用户/角色: {len(self.IAM用户)} 个")
        print(f"    IAM策略     : {len(self.IAM策略)} 个")
        print(f"    安全问题    : {len(self.审计结果)} 项")

        print(f"\n  [风险分布]")
        for 风险 in ["严重", "高", "中", "低"]:
            print(f"    {风险}: {风险统计.get(风险, 0)} 项")

        print(f"\n  [修复建议]")
        建议 = [
            "P0: Root账户启用MFA，停止日常使用Root操作",
            "P0: 回收intern-summer和dev-junior-01的管理员权限",
            "P0: 禁用old-service-account的闲置密钥",
            "P1: CI/CD角色改用STS临时凭证替代长期密钥",
            "P1: 所有IAM用户启用MFA（特别是高权限用户）",
            "P1: 限制策略中的*通配符，使用精确Action和Resource",
            "P2: 实施密码策略（12位+/90天轮换/不可重用）",
            "P3: 使用AWS IAM Access Analyzer持续监控权限",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"用户数": len(self.IAM用户), "问题数": len(self.审计结果)}


# ============================================================================
# 模块三：云网络安全
# ============================================================================

class 云网络安全审计器:
    """
    云网络安全审计器 —— 审计安全组、网络ACL和暴露面。

    技术原理：
        云网络安全通过安全组（Security Group）和网络ACL（Network ACL）
        实现虚拟防火墙。常见风险：
        1. 安全组规则过宽：0.0.0.0/0入站规则暴露服务到互联网
        2. 管理端口暴露：SSH(22)/RDP(3389)/数据库端口对公网开放
        3. 缺乏网络分段：所有实例在同一子网，无隔离
        4. 出站规则过宽：0.0.0.0/0出站允许任意出站通信
        5. 安全组互相引用混乱：安全组间循环引用导致权限扩散
        6. 默认安全组使用：使用云平台默认安全组（通常过宽）

        审计工具：AWS VPC Flow Logs、scoutsuite、prowler、Lacework。
    """

    # 模拟安全组规则
    安全组列表 = [
        {
            "名称": "web-servers-sg",
            "ID": "sg-0abc123def456",
            "入站规则": [
                {"端口": 80, "协议": "TCP", "来源": "0.0.0.0/0", "风险": "低",
                 "说明": "HTTP公开访问（正常）"},
                {"端口": 443, "协议": "TCP", "来源": "0.0.0.0/0", "风险": "低",
                 "说明": "HTTPS公开访问（正常）"},
                {"端口": 22, "协议": "TCP", "来源": "0.0.0.0/0", "风险": "严重",
                 "说明": "SSH对全网开放！应限制来源IP"},
                {"端口": 8080, "协议": "TCP", "来源": "0.0.0.0/0", "风险": "中",
                 "说明": "管理后台对公网开放"}
            ],
            "出站规则": [
                {"端口": "ALL", "协议": "ALL", "目的": "0.0.0.0/0", "风险": "中",
                 "说明": "允许所有出站流量"}
            ],
            "关联实例": 5
        },
        {
            "名称": "database-sg",
            "ID": "sg-0def789ghi012",
            "入站规则": [
                {"端口": 3306, "协议": "TCP", "来源": "0.0.0.0/0", "风险": "严重",
                 "说明": "MySQL对全网开放！"},
                {"端口": 22, "协议": "TCP", "来源": "0.0.0.0/0", "风险": "严重",
                 "说明": "SSH对全网开放！"},
                {"端口": 6379, "协议": "TCP", "来源": "10.0.1.0/24", "风险": "低",
                 "说明": "Redis仅内网访问（正常）"}
            ],
            "出站规则": [
                {"端口": "ALL", "协议": "ALL", "目的": "0.0.0.0/0", "风险": "中",
                 "说明": "允许所有出站流量"}
            ],
            "关联实例": 3
        },
        {
            "名称": "app-servers-sg",
            "ID": "sg-0jkl345mno678",
            "入站规则": [
                {"端口": 8080, "协议": "TCP", "来源": "sg-0abc123def456", "风险": "低",
                 "说明": "仅Web安全组可访问应用层"},
                {"端口": 22, "协议": "TCP", "来源": "10.0.0.0/16", "风险": "低",
                 "说明": "SSH仅内网可访问"}
            ],
            "出站规则": [
                {"端口": 443, "协议": "TCP", "目的": "0.0.0.0/0", "风险": "低",
                 "说明": "仅允许HTTPS出站"},
                {"端口": 3306, "协议": "TCP", "目的": "sg-0def789ghi012", "风险": "低",
                 "说明": "仅允许访问数据库安全组"}
            ],
            "关联实例": 8
        },
        {
            "名称": "default-sg",
            "ID": "sg-default",
            "入站规则": [
                {"端口": "ALL", "协议": "ALL", "来源": "0.0.0.0/0", "风险": "严重",
                 "说明": "默认安全组全部开放！"}
            ],
            "出站规则": [
                {"端口": "ALL", "协议": "ALL", "目的": "0.0.0.0/0", "风险": "中",
                 "说明": "允许所有出站"}
            ],
            "关联实例": 2
        }
    ]

    # 模拟网络ACL
    网络ACL列表 = [
        {"子网": "10.0.1.0/24 (Public)", "入站规则": [
            {"规则": 100, "端口": "80,443", "协议": "TCP", "来源": "0.0.0.0/0",
             "动作": "ALLOW", "风险": "低"},
            {"规则": 110, "端口": "22", "协议": "TCP", "来源": "0.0.0.0/0",
             "动作": "ALLOW", "风险": "严重"},
            {"规则": "*", "端口": "ALL", "协议": "ALL", "来源": "0.0.0.0/0",
             "动作": "DENY", "风险": "低"}
        ]},
        {"子网": "10.0.2.0/24 (Private-App)", "入站规则": [
            {"规则": 100, "端口": "8080", "协议": "TCP", "来源": "10.0.1.0/24",
             "动作": "ALLOW", "风险": "低"},
            {"规则": "*", "端口": "ALL", "协议": "ALL", "来源": "0.0.0.0/0",
             "动作": "DENY", "风险": "低"}
        ]},
        {"子网": "10.0.3.0/24 (Private-DB)", "入站规则": [
            {"规则": 100, "端口": "3306", "协议": "TCP", "来源": "10.0.2.0/24",
             "动作": "ALLOW", "风险": "低"},
            {"规则": "*", "端口": "ALL", "协议": "ALL", "来源": "0.0.0.0/0",
             "动作": "DENY", "风险": "低"}
        ]}
    ]

    def __init__(self):
        self.审计结果 = []

    def 审计安全组规则(self):
        """审计安全组入站/出站规则"""
        print("=" * 70)
        print("[安全组审计] 检查安全组规则配置...")
        print("=" * 70)

        for sg in self.安全组列表:
            print(f"\n  ── 安全组: {sg['名称']} ({sg['ID']})")
            print(f"     关联实例: {sg['关联实例']} 台")
            print(f"\n     [入站规则]")
            print(f"     {'端口':<10} {'协议':<6} {'来源':<16} {'风险':<6} {'说明'}")
            print(f"     {'-'*10} {'-'*6} {'-'*16} {'-'*6} {'-'*35}")

            for 规则 in sg["入站规则"]:
                来源 = 规则["来源"]
                if "0.0.0.0/0" in 来源:
                    风险 = 规则["风险"]
                    print(f"     {str(规则['端口']):<10} {规则['协议']:<6} "
                          f"{来源:<16} {风险:<6} {规则['说明']}")
                    if 风险 in ["严重", "高"]:
                        self.审计结果.append(("安全组规则过宽", 风险,
                                                f"{sg['名称']} - 端口{规则['端口']}对0.0.0.0/0开放"))
                else:
                    print(f"     {str(规则['端口']):<10} {规则['协议']:<6} "
                          f"{来源:<16} {规则['风险']:<6} {规则['说明']}")

            print(f"\n     [出站规则]")
            for 规则 in sg["出站规则"]:
                print(f"     {str(规则['端口']):<10} {规则['协议']:<6} "
                      f"{规则['目的']:<16} {规则['风险']:<6} {规则['说明']}")
                if "0.0.0.0/0" in 规则["目的"] and 规则["端口"] == "ALL":
                    self.审计结果.append(("出站规则过宽", "中",
                                            f"{sg['名称']} - 出站全部开放"))

    def 检查网络ACL(self):
        """检查网络ACL配置"""
        print("\n" + "-" * 70)
        print("[网络ACL] 检查网络访问控制列表配置...")
        print("-" * 70)

        for acl in self.网络ACL列表:
            print(f"\n  ── 子网: {acl['子网']}")
            print(f"     {'规则#':<8} {'端口':<12} {'协议':<6} {'来源':<16} {'动作':<6} {'风险'}")
            print(f"     {'-'*8} {'-'*12} {'-'*6} {'-'*16} {'-'*6} {'-'*6}")

            for 规则 in acl["入站规则"]:
                print(f"     {str(规则['规则']):<8} {str(规则['端口']):<12} "
                      f"{规则['协议']:<6} {规则['来源']:<16} "
                      f"{规则['动作']:<6} {规则['风险']}")

                if "0.0.0.0/0" in 规则["来源"] and 规则["动作"] == "ALLOW" \
                   and 规则["风险"] == "严重":
                    self.审计结果.append(("NACL规则过宽", "严重",
                                            f"{acl['子网']} - 端口{规则['端口']}对公网开放"))

    def 分析暴露面(self):
        """分析互联网暴露面"""
        print("\n" + "-" * 70)
        print("[暴露面分析] 分析面向互联网的服务和端口...")
        print("-" * 70)

        暴露服务 = [
            {"服务": "SSH", "端口": 22, "来源": "0.0.0.0/0",
             "实例数": 12, "风险": "严重",
             "建议": "限制来源IP为堡垒机/VPN网段"},
            {"服务": "HTTP", "端口": 80, "来源": "0.0.0.0/0",
             "实例数": 5, "风险": "低",
             "建议": "正常Web服务，确保有WAF防护"},
            {"服务": "HTTPS", "端口": 443, "来源": "0.0.0.0/0",
             "实例数": 5, "风险": "低",
             "建议": "正常Web服务，确保证书有效"},
            {"服务": "MySQL", "端口": 3306, "来源": "0.0.0.0/0",
             "实例数": 3, "风险": "严重",
             "建议": "数据库绝不可对公网开放！"},
            {"服务": "管理后台", "端口": 8080, "来源": "0.0.0.0/0",
             "实例数": 2, "风险": "高",
             "建议": "管理后台应通过VPN/堡垒机访问"},
            {"服务": "Redis", "端口": 6379, "来源": "0.0.0.0/0",
             "实例数": 1, "风险": "严重",
             "建议": "Redis绝不可对公网开放！"},
        ]

        print(f"\n  [公网暴露服务统计]")
        print(f"  {'服务':<12} {'端口':<8} {'来源':<14} {'实例数':<8} {'风险':<6} {'建议'}")
        print(f"  {'-'*12} {'-'*8} {'-'*14} {'-'*8} {'-'*6} {'-'*40}")

        for s in 暴露服务:
            print(f"  {s['服务']:<12} {s['端口']:<8} {s['来源']:<14} "
                  f"{s['实例数']:<8} {s['风险']:<6} {s['建议']}")
            if s["风险"] in ["严重", "高"]:
                self.审计结果.append(("公网暴露", s["风险"],
                                        f"{s['服务']}(端口{s['端口']}) - {s['实例数']}实例"))

        print(f"\n  [暴露面摘要]")
        严重暴露 = [s for s in 暴露服务 if s["风险"] == "严重"]
        print(f"    严重暴露服务: {len(严重暴露)} 个")
        for s in 严重暴露:
            print(f"      - {s['服务']} (端口{s['端口']}) - {s['实例数']}台实例")
        print(f"    总暴露实例数: {sum(s['实例数'] for s in 暴露服务)} 台")

    def 生成网络安全报告(self):
        """生成云网络安全审计报告"""
        print("\n" + "=" * 70)
        print("[网络报告] 云网络安全审计综合报告")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.审计结果)
        print(f"\n  [审计摘要]")
        print(f"    安全组数  : {len(self.安全组列表)} 个")
        print(f"    网络ACL   : {len(self.网络ACL列表)} 个")
        print(f"    安全问题  : {len(self.审计结果)} 项")

        print(f"\n  [风险分布]")
        for 风险 in ["严重", "高", "中", "低"]:
            print(f"    {风险}: {风险统计.get(风险, 0)} 项")

        print(f"\n  [修复建议]")
        建议 = [
            "P0: 立即关闭SSH(22)对0.0.0.0/0的开放，限制为堡垒机IP",
            "P0: 立即关闭MySQL(3306)和Redis(6379)对公网的暴露",
            "P0: 不使用default安全组，创建最小权限安全组替代",
            "P1: 管理端口(22/3389/8080)通过堡垒机/Session Manager访问",
            "P1: 出站规则限制为必要的IP和端口范围",
            "P2: 实施网络分段（Public/App/DB三层子网隔离）",
            "P2: 启用VPC Flow Logs审计网络流量",
            "P3: 部署AWS Network Firewall或第三方云防火墙",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"安全组数": len(self.安全组列表), "问题数": len(self.审计结果)}


# ============================================================================
# 模块四：容器安全检测
# ============================================================================

class 容器安全检测器:
    """
    容器安全检测器 —— 检测Docker镜像和Kubernetes集群安全。

    技术原理：
        容器化部署（Docker + Kubernetes）是云原生应用的标准模式。
        容器安全风险：
        1. 镜像漏洞：基础镜像包含已知CVE漏洞
        2. 镜像配置不当：以root运行、包含敏感信息、使用latest标签
        3. K8s API Server暴露：API Server对公网开放且认证弱
        4. RBAC配置不当：默认ServiceAccount权限过大
        5. Pod安全策略缺失：允许特权容器、host网络、host PID
        6. Secret管理不当：Secret以明文环境变量或文件挂载
        7. 网络策略缺失：所有Pod可互相访问

        检测工具：Trivy、Clair、Grype（镜像扫描）；
        kube-bench（CIS基准）、kube-hunter（渗透测试）、kubeaudit（配置审计）。
    """

    # 模拟Docker镜像扫描结果
    镜像扫描结果 = [
        {
            "镜像": "nginx:1.21.0",
            "大小": "142MB",
            "层数": 5,
            "基础镜像": "debian:buster-slim",
            "漏洞": [
                {"CVE": "CVE-2023-44487", "组件": "nghttp2", "严重度": "严重",
                 "CVSS": 7.5, "修复版本": "1.52.0", "描述": "HTTP/2快速重置DoS漏洞"},
                {"CVE": "CVE-2022-40302", "组件": "libxml2", "严重度": "高",
                 "CVSS": 7.4, "修复版本": "2.9.14", "描述": "整数溢出导致堆溢出"},
                {"CVE": "CVE-2021-23133", "组件": "curl", "严重度": "高",
                 "CVSS": 7.1, "修复版本": "7.77.0", "描述": "HSTS缓冲区溢出"},
                {"CVE": "CVE-2022-1304", "组件": "e2fsprogs", "严重度": "中",
                 "CVSS": 6.5, "修复版本": "1.46.5", "描述": "文件系统操作越界写"},
            ],
            "配置问题": [
                "以root用户运行容器",
                "未设置只读根文件系统",
                "未设置内存限制",
            ]
        },
        {
            "镜像": "company-app:latest",
            "大小": "890MB",
            "层数": 12,
            "基础镜像": "python:3.9",
            "漏洞": [
                {"CVE": "CVE-2023-0286", "组件": "openssl", "严重度": "严重",
                 "CVSS": 7.4, "修复版本": "1.1.1t", "描述": "X.400地址处理空指针解引用"},
                {"CVE": "CVE-2022-40897", "组件": "python", "严重度": "高",
                 "CVSS": 8.2, "修复版本": "3.9.17", "描述": "zipimport空指针解引用"},
                {"CVE": "CVE-2023-24329", "组件": "python", "严重度": "严重",
                 "CVSS": 9.8, "修复版本": "3.9.17", "描述": "urllib URL解析缺陷"},
            ],
            "配置问题": [
                "使用latest标签（不可追溯）",
                "镜像中包含.git目录（源码泄露）",
                "包含硬编码数据库密码（环境变量）",
                "镜像体积过大(890MB)，应使用多阶段构建优化",
                "以root用户运行容器",
            ]
        },
        {
            "镜像": "redis:7.0-alpine",
            "大小": "28MB",
            "层数": 3,
            "基础镜像": "alpine:3.17",
            "漏洞": [],
            "配置问题": [
                "使用非root用户运行（合规）",
                "设置了只读根文件系统（合规）",
            ]
        }
    ]

    # 模拟K8s集群配置
    K8s配置 = {
        "集群版本": "v1.27.3",
        "API Server暴露": True,
        "API Server认证": "RBAC + 证书认证",
        "匿名访问": False,
        "Pod安全策略": "未启用",
        "网络策略": "未配置",
        "Secret加密": "未启用",
        "审计日志": "未启用",
        "etcd加密": "未启用",
        "ServiceAccount令牌": "自动挂载（默认）",
    }

    # 模拟K8s RBAC配置
    RBAC配置 = [
        {
            "角色": "cluster-admin",
            "绑定类型": "ClusterRoleBinding",
            "主体": "default:ServiceAccount",
            "命名空间": "所有",
            "权限": "*/*（全部资源的全部操作）",
            "风险": "严重",
            "说明": "default ServiceAccount拥有集群管理员权限"
        },
        {
            "角色": "edit",
            "绑定类型": "RoleBinding",
            "主体": "dev-team:Group",
            "命名空间": "production",
            "权限": "pods/services/deployments的创建/删除",
            "风险": "高",
            "说明": "开发团队可在生产命名空间创建Pod"
        },
        {
            "角色": "view",
            "绑定类型": "RoleBinding",
            "主体": "auditor:User",
            "命名空间": "monitoring",
            "权限": "pods/services/logs只读",
            "风险": "低",
            "说明": "审计员只读权限（合规）"
        },
        {
            "角色": "cluster-admin",
            "绑定类型": "ClusterRoleBinding",
            "主体": "ci-cd:ServiceAccount",
            "命名空间": "所有",
            "权限": "*/*（全部资源的全部操作）",
            "风险": "严重",
            "说明": "CI/CD服务账户拥有集群管理员权限"
        }
    ]

    def __init__(self):
        self.检测结果 = []

    def 扫描Docker镜像漏洞(self):
        """扫描Docker镜像中的已知漏洞"""
        print("=" * 70)
        print("[镜像扫描] 扫描Docker镜像已知漏洞...")
        print("=" * 70)

        for 镜像 in self.镜像扫描结果:
            print(f"\n  ── 镜像: {镜像['镜像']}")
            print(f"     大小: {镜像['大小']}  层数: {镜像['层数']}  基础: {镜像['基础镜像']}")
            print(f"     漏洞数: {len(镜像['漏洞'])}")

            if 镜像["漏洞"]:
                print(f"\n     [漏洞列表]")
                print(f"     {'CVE':<20} {'组件':<15} {'严重度':<8} {'CVSS':<6} {'修复版本':<12}")
                print(f"     {'-'*20} {'-'*15} {'-'*8} {'-'*6} {'-'*12}")

                for v in 镜像["漏洞"]:
                    print(f"     {v['CVE']:<20} {v['组件']:<15} "
                          f"{v['严重度']:<8} {v['CVSS']:<6} {v['修复版本']:<12}")
                    self.检测结果.append(("镜像漏洞", v["严重度"],
                                            f"{镜像['镜像']} - {v['CVE']}({v['组件']})"))

            print(f"\n     [配置问题]")
            for 问题 in 镜像["配置问题"]:
                合规 = "合规" if "合规" in 问题 else "不合规"
                print(f"     [{合规}] {问题}")
                if "合规" not in 问题:
                    self.检测结果.append(("镜像配置", "高",
                                            f"{镜像['镜像']} - {问题}"))

        # 漏洞统计
        总漏洞 = sum(len(m["漏洞"]) for m in self.镜像扫描结果)
        严重漏洞 = sum(1 for m in self.镜像扫描结果 for v in m["漏洞"] if v["严重度"] == "严重")
        print(f"\n  [漏洞统计]")
        print(f"    扫描镜像数: {len(self.镜像扫描结果)}")
        print(f"    总漏洞数  : {总漏洞}")
        print(f"    严重漏洞  : {严重漏洞}")

        return {"镜像数": len(self.镜像扫描结果), "漏洞数": 总漏洞}

    def 审计K8s配置(self):
        """审计Kubernetes集群安全配置"""
        print("\n" + "-" * 70)
        print("[K8s审计] Kubernetes集群安全配置审计...")
        print("-" * 70)

        配置检查 = [
            ("API Server公网暴露", self.K8s配置["API Server暴露"], "严重",
             "API Server应对公网关闭，仅通过VPN/堡垒机访问"),
            ("Pod安全策略(PSP)", self.K8s配置["Pod安全策略"] == "已启用", "高",
             "应启用PSP/Pod Security Standards限制特权容器"),
            ("网络策略", self.K8s配置["网络策略"] == "已配置", "高",
             "应配置NetworkPolicy实现Pod间网络隔离"),
            ("Secret静态加密", self.K8s配置["Secret加密"] == "已启用", "严重",
             "应对etcd中的Secret启用静态加密"),
            ("审计日志", self.K8s配置["审计日志"] == "已启用", "中",
             "应启用API Server审计日志记录所有操作"),
            ("etcd数据加密", self.K8s配置["etcd加密"] == "已启用", "高",
             "应对etcd数据卷启用静态加密"),
            ("匿名访问禁用", not self.K8s配置["匿名访问"], "低",
             "已禁用匿名访问（合规）"),
            ("ServiceAccount令牌自动挂载", self.K8s配置["ServiceAccount令牌"] == "禁用", "中",
             "应在不需要的Pod中禁用SA令牌自动挂载"),
        ]

        print(f"\n  {'检查项':<35} {'状态':<10} {'风险':<6} {'建议'}")
        print(f"  {'-'*35} {'-'*10} {'-'*6} {'-'*40}")

        for 检查, 状态, 风险, 建议 in 配置检查:
            状态文本 = "合规" if 状态 else "不合规"
            print(f"  {检查:<35} {状态文本:<10} {风险:<6} {建议[:40]}")
            if not 状态:
                self.检测结果.append(("K8s配置", 风险, f"{检查} - {建议}"))

    def 检查RBAC(self):
        """检查K8s RBAC（基于角色的访问控制）配置"""
        print("\n" + "-" * 70)
        print("[RBAC检查] 检查Kubernetes RBAC配置...")
        print("-" * 70)

        print(f"\n  [RBAC绑定配置]")
        for rbac in self.RBAC配置:
            print(f"\n  ── 角色: {rbac['角色']} ({rbac['绑定类型']})")
            print(f"     主体   : {rbac['主体']}")
            print(f"     命名空间: {rbac['命名空间']}")
            print(f"     权限   : {rbac['权限']}")
            print(f"     风险   : {rbac['风险']}")
            print(f"     说明   : {rbac['说明']}")
            self.检测结果.append(("RBAC配置", rbac["风险"],
                                    f"{rbac['角色']} -> {rbac['主体']} - {rbac['说明']}"))

        print(f"\n  [RBAC风险分析]")
        风险 = [
            "1. default ServiceAccount拥有cluster-admin权限 -> 应限制为最小权限",
            "2. CI/CD ServiceAccount拥有cluster-admin权限 -> 应使用专用受限角色",
            "3. 开发团队可在production命名空间创建Pod -> 应分离dev/prod权限",
            "4. 未使用NetworkPolicy -> 所有Pod可互相访问，缺乏隔离",
        ]
        for r in 风险:
            print(f"    {r}")

    def 生成容器安全报告(self):
        """生成容器安全检测报告"""
        print("\n" + "=" * 70)
        print("[容器报告] 容器安全检测综合报告")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.检测结果)
        print(f"\n  [检测摘要]")
        print(f"    镜像数  : {len(self.镜像扫描结果)}")
        print(f"    K8s版本 : {self.K8s配置['集群版本']}")
        print(f"    RBAC绑定: {len(self.RBAC配置)} 个")
        print(f"    安全问题: {len(self.检测结果)} 项")

        print(f"\n  [风险分布]")
        for 风险 in ["严重", "高", "中", "低"]:
            print(f"    {风险}: {风险统计.get(风险, 0)} 项")

        print(f"\n  [修复建议]")
        建议 = [
            "P0: 更新含严重CVE的镜像到安全版本",
            "P0: 移除镜像中的硬编码密码和.git目录",
            "P0: 关闭K8s API Server公网暴露",
            "P0: 启用etcd静态加密保护Secret",
            "P1: 使用非root用户运行容器",
            "P1: 回收default和CI/CD的cluster-admin权限",
            "P1: 启用Pod Security Standards替代PSP",
            "P2: 配置NetworkPolicy实现Pod间网络隔离",
            "P2: 启用K8s审计日志",
            "P3: 集成Trivy到CI/CD流水线实现镜像自动扫描",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"镜像数": len(self.镜像扫描结果), "问题数": len(self.检测结果)}


# ============================================================================
# 模块五：Serverless安全
# ============================================================================

class Serverless安全检测器:
    """
    Serverless安全检测器 —— 检测无服务器函数（Lambda/函数计算）安全。

    技术原理：
        Serverless架构（AWS Lambda / 阿里云函数计算 / Azure Functions）
        虽然消除了服务器管理负担，但引入了新的安全挑战：
        1. 函数权限过大：Lambda角色拥有过度IAM权限
        2. 事件源验证缺失：未验证触发器的来源和输入
        3. 环境变量泄露：密钥和凭据存储在环境变量中
        4. 函数代码漏洞：依赖库漏洞、代码注入
        5. 冷启动信息泄露：容器复用导致跨请求数据泄露
        6. API Gateway配置：未认证的API端点暴露
        7. 日志含敏感信息：函数日志输出包含密码/Token

        检测工具：Lumigo、Datadog Serverless、PureSec、AWS Lambda Insight。
    """

    # 模拟Lambda函数列表
    函数列表 = [
        {
            "名称": "user-auth-handler",
            "运行时": "Python 3.11",
            "执行角色": "lambda-exec-role",
            "角色权限": "dynamodb:* + s3:GetObject + secretsmanager:GetSecretValue",
            "触发器": "API Gateway (POST /auth)",
            "环境变量": {"DB_HOST": "10.0.1.100", "DB_PASS": "Admin@2024",
                        "JWT_SECRET": "MyJwtSecret2024!"},
            "超时": 30,
            "内存": 256,
            "VPC": "已配置",
            "X-Ray追踪": True,
            "最后修改": "2024-09-01",
            "风险": ["环境变量中存储密钥", "DynamoDB全权限", "API Gateway无认证"]
        },
        {
            "名称": "data-processor",
            "运行时": "Node.js 18",
            "执行角色": "lambda-full-access",
            "角色权限": "*（AdministratorAccess）",
            "触发器": "S3事件 (PutObject)",
            "环境变量": {"AWS_ACCESS_KEY_ID": "AKIA...",
                        "AWS_SECRET_ACCESS_KEY": "wJal..."},
            "超时": 300,
            "内存": 1024,
            "VPC": "未配置",
            "X-Ray追踪": False,
            "最后修改": "2024-08-15",
            "风险": ["Lambda角色拥有AdministratorAccess", "环境变量存储AWS密钥",
                      "未配置VPC（无法访问私有资源）", "无X-Ray追踪"]
        },
        {
            "名称": "image-resizer",
            "运行时": "Python 3.11",
            "执行角色": "lambda-s3-access",
            "角色权限": "s3:GetObject + s3:PutObject（特定Bucket）",
            "触发器": "S3事件 (PutObject)",
            "环境变量": {"OUTPUT_BUCKET": "company-resized-images"},
            "超时": 60,
            "内存": 512,
            "VPC": "未配置",
            "X-Ray追踪": True,
            "最后修改": "2024-09-10",
            "风险": []
        },
        {
            "名称": "scheduled-cleanup",
            "运行时": "Python 3.9",
            "执行角色": "lambda-cleanup-role",
            "角色权限": "s3:DeleteObject + s3:ListBucket",
            "触发器": "EventBridge (cron: 0 2 * * *)",
            "环境变量": {},
            "超时": 120,
            "内存": 128,
            "VPC": "未配置",
            "X-Ray追踪": False,
            "最后修改": "2024-07-01",
            "风险": ["运行时版本过旧(Python 3.9)", "无X-Ray追踪"]
        },
        {
            "名称": "api-webhook-handler",
            "运行时": "Node.js 18",
            "执行角色": "lambda-webhook-role",
            "角色权限": "sqs:SendMessage + sns:Publish",
            "触发器": "API Gateway (POST /webhook)",
            "环境变量": {"WEBHOOK_SECRET": "whsec_abc123",
                        "SLACK_TOKEN": "xoxb-..."},
            "超时": 10,
            "内存": 256,
            "VPC": "已配置",
            "X-Ray追踪": True,
            "最后修改": "2024-09-05",
            "风险": ["环境变量存储Slack Token", "API Gateway未验证Webhook签名"]
        }
    ]

    def __init__(self):
        self.检测结果 = []

    def 检查函数权限(self):
        """检查Lambda函数执行角色权限"""
        print("=" * 70)
        print("[权限检查] 检查Serverless函数执行角色权限...")
        print("=" * 70)

        for fn in self.函数列表:
            print(f"\n  ── 函数: {fn['名称']}")
            print(f"     运行时 : {fn['运行时']}")
            print(f"     执行角色: {fn['执行角色']}")
            print(f"     角色权限: {fn['角色权限']}")
            print(f"     触发器 : {fn['触发器']}")

            权限 = fn["角色权限"]
            if "*" in 权限 or "AdministratorAccess" in 权限:
                print(f"     [!] 严重: 函数角色拥有管理员权限!")
                self.检测结果.append(("函数权限过大", "严重",
                                        f"{fn['名称']} - {fn['角色权限']}"))
            elif "FullAccess" in 权限 or ":*" in 权限:
                print(f"     [!] 高风险: 函数角色权限过宽")
                self.检测结果.append(("函数权限过宽", "高",
                                        f"{fn['名称']} - {fn['角色权限']}"))
            else:
                print(f"     [+] 权限配置合理（最小权限）")

            # 检查风险列表
            for r in fn["风险"]:
                if "权限" in r:
                    print(f"     [!] {r}")

    def 验证事件源(self):
        """验证函数触发器/事件源安全配置"""
        print("\n" + "-" * 70)
        print("[事件源验证] 检查函数触发器安全配置...")
        print("-" * 70)

        for fn in self.函数列表:
            触发器 = fn["触发器"]
            print(f"\n  函数: {fn['名称']}")
            print(f"  触发器: {触发器}")

            if "API Gateway" in 触发器:
                print(f"    [检查] API Gateway认证配置...")
                if "无认证" in str(fn["风险"]):
                    print(f"    [!] API Gateway端点未配置认证!")
                    print(f"    [!] 任何人可调用此函数")
                    self.检测结果.append(("API未认证", "严重",
                                            f"{fn['名称']} - API Gateway无认证"))
                else:
                    print(f"    [+] API Gateway已配置认证")

            if "S3" in 触发器:
                print(f"    [检查] S3事件触发配置...")
                print(f"    [+] S3事件触发器配置合理")

            if "EventBridge" in 触发器 or "cron" in 触发器:
                print(f"    [检查] 定时触发配置...")
                print(f"    [+] 定时触发器配置合理")

            if "webhook" in fn["名称"].lower():
                print(f"    [!] Webhook函数未验证请求签名!")
                self.检测结果.append(("Webhook未验证", "高",
                                        f"{fn['名称']} - 未验证Webhook签名"))

    def 检测环境变量泄露(self):
        """检测函数环境变量中的敏感信息"""
        print("\n" + "-" * 70)
        print("[环境变量] 检测函数环境变量中的敏感信息泄露...")
        print("-" * 70)

        敏感模式 = [
            (r"(?i)(password|passwd|pwd)", "密码"),
            (r"(?i)(secret|token|api_key|apikey)", "密钥/令牌"),
            (r"(?i)(AWS_ACCESS_KEY|AWS_SECRET_KEY)", "AWS密钥"),
            (r"(?i)(SLACK_TOKEN)", "Slack令牌"),
            (r"(?i)(JWT_SECRET)", "JWT密钥"),
            (r"(?i)(DB_PASS|DB_PASSWORD)", "数据库密码"),
        ]

        for fn in self.函数列表:
            环境变量 = fn.get("环境变量", {})
            if not 环境变量:
                continue

            print(f"\n  函数: {fn['名称']}")
            发现敏感 = False

            for 变量名, 变量值 in 环境变量.items():
                for 模式, 类型 in 敏感模式:
                    if re.search(模式, 变量名):
                        掩码值 = str(变量值)[:4] + "***" if len(str(变量值)) > 4 else "***"
                        print(f"    [!] {变量名} = {掩码值}  (类型: {类型})")
                        发现敏感 = True
                        self.检测结果.append(("环境变量泄露", "严重",
                                                f"{fn['名称']} - {变量名}({类型})"))
                        break

            if not 发现敏感:
                print(f"    [+] 未发现敏感环境变量")

        print(f"\n  [修复建议]")
        建议 = [
            "1. 使用AWS Secrets Manager / Parameter Store存储密钥",
            "2. 运行时动态获取密钥，不硬编码在环境变量中",
            "3. 使用KMS加密环境变量",
            "4. 定期审计函数环境变量配置",
        ]
        for s in 建议:
            print(f"    {s}")

    def 生成Serverless报告(self):
        """生成Serverless安全检测报告"""
        print("\n" + "=" * 70)
        print("[Serverless报告] Serverless安全检测综合报告")
        print("=" * 70)

        风险统计 = Counter(r[1] for r in self.检测结果)
        print(f"\n  [检测摘要]")
        print(f"    函数总数  : {len(self.函数列表)}")
        print(f"    安全问题  : {len(self.检测结果)} 项")

        print(f"\n  [风险分布]")
        for 风险 in ["严重", "高", "中", "低"]:
            print(f"    {风险}: {风险统计.get(风险, 0)} 项")

        print(f"\n  [修复建议]")
        建议 = [
            "P0: 移除data-processor的AdministratorAccess权限",
            "P0: 将环境变量中的密钥迁移到Secrets Manager",
            "P0: 为API Gateway端点添加认证（Cognito/IAM）",
            "P1: 验证Webhook请求签名（HMAC）",
            "P1: 为所有函数配置VPC和X-Ray追踪",
            "P2: 升级过旧的运行时版本",
            "P3: 部署Serverless安全扫描工具（PureSec/Lumigo）",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"函数数": len(self.函数列表), "问题数": len(self.检测结果)}


# ============================================================================
# 模块六：云合规检查
# ============================================================================

class 云合规检查器:
    """
    云合规检查器 —— 对照等保2.0和CIS基准检查云安全合规性。

    技术原理：
        云安全合规检查是对照行业安全标准对云环境进行合规性评估：
        1. 等保2.0（网络安全等级保护2.0）：
           - 适用于中国境内的信息系统，五个安全等级
           - 云安全扩展要求：基础设施、平台、应用三层安全
           - 关键控制项：身份认证、访问控制、安全审计、数据加密

        2. CIS Benchmark（互联网安全中心基准）：
           - AWS Foundations Benchmark：IAM/日志/监控/网络/加密
           - Azure Foundations Benchmark
           - GCP Foundation Benchmark
           - 提供具体的技术控制配置检查项

        3. 其他标准：SOC 2、ISO 27001、PCI-DSS、HIPAA、GDPR

        合规工具：AWS Security Hub、Azure Security Center、scoutsuite、prowler。
    """

    # 等保2.0云安全检查项
    等保检查项 = {
        "安全物理环境": [
            {"项": "数据中心物理安全", "标准": "机房位于合规数据中心",
             "状态": "合规", "说明": "使用云厂商合规机房"},
            {"项": "设备访问控制", "标准": "物理设备访问受控",
             "状态": "合规", "说明": "由云厂商负责物理安全"},
        ],
        "安全通信网络": [
            {"项": "网络隔离", "标准": "VPC实现网络隔离",
             "状态": "合规", "说明": "已配置VPC和子网"},
            {"项": "通信加密", "标准": "传输使用TLS加密",
             "状态": "不合规", "说明": "部分服务仍使用HTTP明文"},
            {"项": "边界防护", "标准": "部署防火墙/WAF",
             "状态": "合规", "说明": "已配置安全组+NACL"},
        ],
        "安全区域边界": [
            {"项": "访问控制", "标准": "边界实施白名单访问",
             "状态": "部分合规", "说明": "部分安全组0.0.0.0/0开放"},
            {"项": "入侵防范", "标准": "部署IDS/IPS",
             "状态": "不合规", "说明": "未部署云入侵检测"},
            {"项": "恶意代码防范", "标准": "部署反恶意代码",
             "状态": "不合规", "说明": "未部署容器恶意代码扫描"},
        ],
        "安全计算环境": [
            {"项": "身份鉴别", "标准": "多因素认证+强密码",
             "状态": "不合规", "说明": "部分用户未启用MFA"},
            {"项": "访问控制", "标准": "最小权限原则",
             "状态": "不合规", "说明": "存在AdministratorAccess用户"},
            {"项": "安全审计", "标准": "审计日志保留6个月+",
             "状态": "部分合规", "说明": "CloudTrail已启用，但日志保留不足"},
            {"项": "入侵防范", "标准": "主机入侵检测",
             "状态": "不合规", "说明": "未部署HIDS/EDR"},
            {"项": "恶意代码防范", "标准": "终端反恶意代码",
             "状态": "不合规", "说明": "EC2未安装安全代理"},
            {"项": "数据完整性", "标准": "关键数据完整性校验",
             "状态": "部分合规", "说明": "部分Bucket启用版本控制"},
            {"项": "数据保密性", "标准": "数据传输和存储加密",
             "状态": "不合规", "说明": "部分Bucket和EBS未加密"},
            {"项": "数据备份恢复", "标准": "数据定期备份",
             "状态": "合规", "说明": "已配置快照和跨区域复制"},
        ],
        "安全管理中心": [
            {"项": "集中管控", "标准": "安全运营中心(SOC)",
             "状态": "不合规", "说明": "未部署集中安全运营平台"},
            {"项": "安全审计集中", "标准": "日志集中采集分析",
             "状态": "部分合规", "说明": "部分日志已集中，但分析不足"},
            {"项": "安全管理", "标准": "统一安全策略管理",
             "状态": "不合规", "说明": "缺乏统一安全策略配置"},
        ]
    }

    # CIS AWS Benchmark检查项（简化版）
    CIS检查项 = [
        {"编号": "1.1", "检查": "避免使用Root账户",
         "状态": "不合规", "风险": "严重",
         "说明": "Root账户在过去30天有API调用记录"},
        {"编号": "1.2", "检查": "Root账户启用MFA",
         "状态": "不合规", "风险": "严重",
         "说明": "Root账户未启用MFA"},
        {"编号": "1.3", "检查": "IAM密码策略",
         "状态": "不合规", "风险": "高",
         "说明": "密码策略不满足最小长度和复杂度要求"},
        {"编号": "1.4", "检查": "所有用户启用MFA",
         "状态": "不合规", "风险": "高",
         "说明": "部分IAM用户未启用MFA"},
        {"编号": "1.5", "检查": "无过度权限策略",
         "状态": "不合规", "风险": "高",
         "说明": "存在使用*通配符的策略"},
        {"编号": "2.1", "检查": "启用CloudTrail",
         "状态": "合规", "风险": "低",
         "说明": "CloudTrail已启用多区域日志"},
        {"编号": "2.2", "检查": "CloudTrail日志加密",
         "状态": "合规", "风险": "低",
         "说明": "日志已启用SSE-KMS加密"},
        {"编号": "2.3", "检查": "CloudWatch告警",
         "状态": "不合规", "风险": "中",
         "说明": "未配置安全事件告警"},
        {"编号": "3.1", "检查": "安全组不开放0.0.0.0/0",
         "状态": "不合规", "风险": "严重",
         "说明": "多个安全组开放22/3306端口"},
        {"编号": "3.2", "检查": "默认安全组限制流量",
         "状态": "不合规", "风险": "高",
         "说明": "default安全组开放所有流量"},
        {"编号": "3.3", "检查": "网络ACL限制流量",
         "状态": "合规", "风险": "低",
         "说明": "网络ACL配置合理"},
        {"编号": "4.1", "检查": "S3 Bucket禁止公开访问",
         "状态": "不合规", "风险": "严重",
         "说明": "存在公开Bucket"},
        {"编号": "4.2", "检查": "S3 Bucket启用版本控制",
         "状态": "部分合规", "风险": "中",
         "说明": "部分Bucket未启用版本控制"},
        {"编号": "4.3", "检查": "S3 Bucket启用加密",
         "状态": "不合规", "风险": "中",
         "说明": "部分Bucket未启用加密"},
        {"编号": "5.1", "检查": "EBS卷加密",
         "状态": "不合规", "风险": "高",
         "说明": "部分EBS卷未启用加密"},
        {"编号": "5.2", "检查": "RDS实例加密",
         "状态": "不合规", "风险": "高",
         "说明": "RDS实例未启用存储加密"},
        {"编号": "5.3", "检查": "RDS自动备份",
         "状态": "合规", "风险": "低",
         "说明": "RDS自动备份已启用"},
        {"编号": "6.1", "检查": "CloudFront启用WAF",
         "状态": "不合规", "风险": "中",
         "说明": "CloudFront分发未关联WAF"},
    ]

    def __init__(self):
        self.合规结果 = {}

    def 执行等保检查(self):
        """执行等保2.0云安全合规检查"""
        print("=" * 70)
        print("[等保2.0] 云安全等级保护合规检查")
        print("=" * 70)

        总检查数 = 0
        合规数 = 0
        不合规数 = 0
        部分合规数 = 0

        for 类别, 检查列表 in self.等保检查项.items():
            print(f"\n  [{'='*15} {类别} {'='*15}]")
            print(f"  {'检查项':<25} {'状态':<10} {'说明'}")
            print(f"  {'-'*25} {'-'*10} {'-'*40}")

            for item in 检查列表:
                print(f"  {item['项']:<25} {item['状态']:<10} {item['说明'][:40]}")
                总检查数 += 1
                if item["状态"] == "合规":
                    合规数 += 1
                elif item["状态"] == "不合规":
                    不合规数 += 1
                else:
                    部分合规数 += 1

        合规率 = (合规数 + 部分合规数 * 0.5) / 总检查数 * 100
        print(f"\n  [等保2.0合规情况]")
        print(f"    总检查项: {总检查数}")
        print(f"    合规    : {合规数}")
        print(f"    部分合规: {部分合规数}")
        print(f"    不合规  : {不合规数}")
        print(f"    合规率  : {合规率:.1f}%")
        print(f"    等保级别: 三级（适用于重要业务系统）")

        return {"合规率": 合规率, "不合规": 不合规数}

    def 执行CIS检查(self):
        """执行CIS Benchmark合规检查"""
        print("\n" + "-" * 70)
        print("[CIS基准] CIS AWS Foundations Benchmark检查")
        print("-" * 70)

        合规数 = 0
        不合规数 = 0
        部分合规数 = 0

        当前章节 = None
        章节名 = {"1": "IAM（身份和访问管理）", "2": "日志和监控",
                   "3": "网络", "4": "存储", "5": "数据库", "6": "CDN/WAF"}

        for item in self.CIS检查项:
            章节 = item["编号"][0]
            if 章节 != 当前章节:
                当前章节 = 章节
                print(f"\n  [{'='*10} {章节名.get(章节, '其他')} {'='*10}]")

            状态标记 = {"合规": "[+]", "不合规": "[!]", "部分合规": "[~]"}
            标记 = 状态标记.get(item["状态"], "[?]")
            print(f"  {标记} CIS {item['编号']}: {item['检查']}")
            print(f"      状态: {item['状态']}  风险: {item['风险']}")
            print(f"      说明: {item['说明']}")

            if item["状态"] == "合规":
                合规数 += 1
            elif item["状态"] == "不合规":
                不合规数 += 1
            else:
                部分合规数 += 1

        总数 = len(self.CIS检查项)
        合规率 = (合规数 + 部分合规数 * 0.5) / 总数 * 100
        print(f"\n  [CIS Benchmark合规情况]")
        print(f"    总检查项: {总数}")
        print(f"    合规    : {合规数}")
        print(f"    部分合规: {部分合规数}")
        print(f"    不合规  : {不合规数}")
        print(f"    合规率  : {合规率:.1f}%")

        return {"合规率": 合规率, "不合规": 不合规数}

    def 生成合规报告(self):
        """生成云安全合规检查综合报告"""
        print("\n" + "=" * 70)
        print("[合规报告] 云安全合规检查综合报告")
        print("=" * 70)

        print(f"\n  [合规标准概览]")
        标准 = [
            ("等保2.0", "中国网络安全等级保护", "三级", "55%", "不合规"),
            ("CIS AWS Benchmark", "CIS云安全基准", "v1.4", "42%", "不合规"),
            ("SOC 2 Type II", "服务组织控制", "Type II", "N/A", "未审计"),
            ("ISO 27001", "信息安全管理体系", "2022", "N/A", "未认证"),
            ("PCI-DSS", "支付卡行业安全", "v4.0", "N/A", "不适用"),
        ]

        print(f"  {'标准':<22} {'描述':<22} {'版本':<8} {'合规率':<8} {'状态'}")
        print(f"  {'-'*22} {'-'*22} {'-'*8} {'-'*8} {'-'*10}")
        for s in 标准:
            print(f"  {s[0]:<22} {s[1]:<22} {s[2]:<8} {s[3]:<8} {s[4]}")

        print(f"\n  [合规整改路线图]")
        路线图 = [
            ("Phase 1 (0-30天)", "P0级别整改",
             "Root账户MFA、禁用过度权限、关闭公网暴露端口"),
            ("Phase 2 (30-60天)", "P1级别整改",
             "数据加密、日志审计、MFA全覆盖、网络分段"),
            ("Phase 3 (60-90天)", "P2级别整改",
             "部署IDS/IPS、HIDS/EDR、安全运营中心"),
            ("Phase 4 (90-180天)", "合规认证",
             "等保三级测评、SOC 2审计、ISO 27001认证"),
        ]

        for 阶段, 目标, 内容 in 路线图:
            print(f"\n  {阶段}: {目标}")
            print(f"    内容: {内容}")

        print(f"\n  [合规建议]")
        建议 = [
            "1. 使用AWS Security Hub / Azure Security Center持续合规监控",
            "2. 集成Cloud Custodian / OPA实现策略即代码",
            "3. 在CI/CD流水线中嵌入合规检查（pre-commit/部署前）",
            "4. 建立月度合规审查机制，跟踪整改进度",
            "5. 聘请第三方测评机构进行等保测评",
            "6. 建立安全事件响应流程（IRP）满足合规审计要求",
        ]
        for s in 建议:
            print(f"    {s}")

        return {"标准数": len(标准)}


# ============================================================================
# 主函数：演示所有云安全案例的运行
# ============================================================================

def 主函数():
    """主函数：演示所有云安全实战案例"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " 云安全实战案例工具集 ".center(50) + "║")
    print("║" + " Cloud Security Practical Case Study ".center(50) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("  [安全声明]")
    print("  本工具仅用于授权安全测试和网络安全教学研究。")
    print("  严禁用于未授权的云资源探测、数据窃取或任何非法操作。")
    print("  所有检测均在模拟环境中进行，不涉及真实云资源。")
    print("  使用者须遵守《网络安全法》《数据安全法》等相关法律法规。")
    print()

    # ===== 案例一：云存储安全检测 =====
    print("\n" + "█" * 70)
    print("█ 案例一：云存储安全检测".ljust(69) + "█")
    print("█" * 70)

    存储检测器 = 云存储安全检测器()
    存储检测器.扫描Bucket列表()
    存储检测器.审计ACL配置()
    存储检测器.扫描敏感数据()
    存储检测器.检查存储配置()
    存储检测器.生成存储检测报告()

    # ===== 案例二：IAM权限审计 =====
    print("\n\n" + "█" * 70)
    print("█ 案例二：IAM权限审计".ljust(69) + "█")
    print("█" * 70)

    iam审计器 = IAM权限审计器()
    iam审计器.检查最小权限原则()
    iam审计器.检测过度权限()
    iam审计器.检测闲置密钥()
    iam审计器.检查MFA配置()
    iam审计器.生成IAM审计报告()

    # ===== 案例三：云网络安全 =====
    print("\n\n" + "█" * 70)
    print("█ 案例三：云网络安全审计".ljust(69) + "█")
    print("█" * 70)

    网络审计器 = 云网络安全审计器()
    网络审计器.审计安全组规则()
    网络审计器.检查网络ACL()
    网络审计器.分析暴露面()
    网络审计器.生成网络安全报告()

    # ===== 案例四：容器安全检测 =====
    print("\n\n" + "█" * 70)
    print("█ 案例四：容器安全检测".ljust(69) + "█")
    print("█" * 70)

    容器检测器 = 容器安全检测器()
    容器检测器.扫描Docker镜像漏洞()
    容器检测器.审计K8s配置()
    容器检测器.检查RBAC()
    容器检测器.生成容器安全报告()

    # ===== 案例五：Serverless安全 =====
    print("\n\n" + "█" * 70)
    print("█ 案例五：Serverless安全检测".ljust(69) + "█")
    print("█" * 70)

    serverless检测器 = Serverless安全检测器()
    serverless检测器.检查函数权限()
    serverless检测器.验证事件源()
    serverless检测器.检测环境变量泄露()
    serverless检测器.生成Serverless报告()

    # ===== 案例六：云合规检查 =====
    print("\n\n" + "█" * 70)
    print("█ 案例六：云合规检查".ljust(69) + "█")
    print("█" * 70)

    合规检查器 = 云合规检查器()
    合规检查器.执行等保检查()
    合规检查器.执行CIS检查()
    合规检查器.生成合规报告()

    # ===== 总结 =====
    print("\n\n" + "=" * 70)
    print("  [全部案例演示完成]")
    print("=" * 70)
    print(f"  演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  涵盖主题: 存储安全 / IAM审计 / 网络安全 / 容器安全 / Serverless / 合规检查")
    print()
    print("  [安全提示]")
    print("  1. 所有检测均在模拟环境中进行，不涉及真实云资源")
    print("  2. 实际云安全测试须获得云账户所有者书面授权")
    print("  3. 发现的安全漏洞应及时通报云厂商和安全团队")
    print("  4. 定期执行合规检查，确保持续合规")
    print("  5. 遵守《网络安全法》《数据安全法》《个人信息保护法》")
    print("=" * 70)


if __name__ == "__main__":
    主函数()
