# -*- coding: utf-8 -*-
"""
=============================================================================
DevSecOps与安全开发实战案例
=============================================================================

安全声明：
    本文件仅用于授权安全测试和教育目的。
    所有代码均为教学演示，使用模拟数据，不涉及真实系统或生产环境。
    未经授权对他人系统进行安全测试是违法行为，请务必在获得书面授权后
    进行安全评估工作。作者不对任何滥用本代码的行为负责。

功能概览：
    1. 安全开发生命周期(SDL)实践 - 需求分析、设计、编码、测试、运维各阶段安全活动
    2. SAST静态应用安全测试 - 源代码安全扫描、常见漏洞检测、代码审查清单
    3. DAST动态应用安全测试 - 黑盒扫描原理、爬虫与漏洞探测、认证扫描
    4. CI/CD安全流水线 - 构建安全、依赖扫描、镜像扫描、安全门禁
    5. 容器与IaC安全 - Docker安全配置、Kubernetes安全、Terraform安全审计
    6. 安全左移实践 - 开发者安全工具、IDE安全插件、提交前检查

作者：DevSecOps与安全开发学习工具
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
import string
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


# ============================================================================
#  模拟数据定义区
# ============================================================================

# 模拟源代码文件
模拟源代码 = {
    "app.py": '''
import os
import hashlib
import pickle
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

SECRET_KEY = "hardcoded_secret_key_12345"
DB_PASSWORD = "admin@123"

@app.route("/login")
def login():
    username = request.args.get("username")
    password = request.args.get("password")
    # SQL注入风险
    sql = "SELECT * FROM users WHERE username='%s' AND password='%s'" % (username, password)
    cursor.execute(sql)
    return "ok"

@app.route("/greet")
def greet():
    name = request.args.get("name", "Guest")
    # XSS风险
    return render_template_string("<h1>Hello " + name + "</h1>")

@app.route("/run")
def run_cmd():
    cmd = request.args.get("cmd")
    # 命令注入风险
    result = os.system("ping -c 1 " + cmd)
    return str(result)

@app.route("/load")
def load_data():
    data = request.data
    # 不安全反序列化
    obj = pickle.loads(data)
    return "loaded"

@app.route("/hash")
def hash_password():
    pwd = request.args.get("pwd")
    # 弱哈希
    hashed = hashlib.md5(pwd.encode()).hexdigest()
    return hashed
''',
    "Dockerfile": '''
FROM ubuntu:latest
USER root
RUN apt-get update && apt-get install -y curl wget
COPY . /app
WORKDIR /app
EXPOSE 8080
CMD ["python", "app.py"]
''',
    "terraform/main.tf": '''
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
  acl    = "public-read"

  tags = {
    Name = "Data Bucket"
  }
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Web security group"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
''',
    "k8s/deployment.yaml": '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: myapp:latest
        ports:
        - containerPort: 8080
        securityContext:
          privileged: true
          runAsUser: 0
''',
}

# 模拟依赖包漏洞
模拟依赖漏洞 = [
    {
        "包名": "django",
        "当前版本": "3.2.0",
        "最新版本": "3.2.20",
        "CVE": "CVE-2023-36053",
        "严重程度": "高危",
        "描述": "Django URL验证绕过漏洞",
        "影响范围": ">=3.2,<3.2.20"
    },
    {
        "包名": "requests",
        "当前版本": "2.25.0",
        "最新版本": "2.31.0",
        "CVE": "CVE-2023-32681",
        "严重程度": "中危",
        "描述": "requests库代理凭据泄露",
        "影响范围": "<2.31.0"
    },
    {
        "包名": "pyyaml",
        "当前版本": "5.3",
        "最新版本": "6.0.1",
        "CVE": "CVE-2020-14343",
        "严重程度": "高危",
        "描述": "PyYAML反序列化代码执行",
        "影响范围": "<5.4"
    },
    {
        "包名": "flask",
        "当前版本": "1.1.2",
        "最新版本": "2.3.3",
        "CVE": "CVE-2023-30861",
        "严重程度": "中危",
        "描述": "Flask会话Cookie安全问题",
        "影响范围": "<2.3.2"
    },
    {
        "包名": "cryptography",
        "当前版本": "2.9",
        "最新版本": "41.0.3",
        "CVE": "CVE-2023-38325",
        "严重程度": "中危",
        "描述": "cryptography RSA填充Oracle漏洞",
        "影响范围": "<41.0.3"
    },
]

# CI/CD流水线阶段定义
CI阶段 = [
    "代码提交",
    "静态代码分析 (SAST)",
    "依赖漏洞扫描 (SCA)",
    "单元测试",
    "容器镜像构建",
    "镜像安全扫描",
    "部署到测试环境",
    "动态安全测试 (DAST)",
    "合规检查",
    "部署到生产环境",
]


# ============================================================================
#  案例1: 安全开发生命周期(SDL)
# ============================================================================

class SDL实践指南:
    """
    安全开发生命周期实践

    功能:
    1. SDL各阶段安全活动介绍
    2. 安全需求清单
    3. 安全设计原则
    4. 安全测试清单
    """

    def SDL阶段介绍(self):
        """介绍SDL各阶段"""
        print("\n" + "=" * 60)
        print("安全开发生命周期 (SDL)")
        print("=" * 60)

        SDL阶段 = [
            ("1. 需求分析阶段", [
                "安全需求收集 (保密性、完整性、可用性)",
                "威胁建模 (STRIDE方法)",
                "数据分类分级",
                "合规性要求分析 (等保、GDPR等)",
                "安全验收标准定义",
            ]),
            ("2. 设计阶段", [
                "安全架构设计",
                "攻击面分析",
                "安全设计原则 (最小权限、纵深防御...)",
                "密码学方案设计",
                "身份认证与授权设计",
                "设计评审 (Security Design Review)",
            ]),
            ("3. 编码阶段", [
                "安全编码规范培训",
                "代码静态分析 (SAST)",
                "代码审查 (Code Review)",
                "IDE安全插件 (SonarLint等)",
                "安全单元测试",
            ]),
            ("4. 测试阶段", [
                "功能安全测试",
                "渗透测试 (Penetration Testing)",
                "模糊测试 (Fuzzing)",
                "动态安全测试 (DAST)",
                "安全回归测试",
            ]),
            ("5. 发布/运维阶段", [
                "安全配置基线",
                "漏洞扫描与修复",
                "安全监控与告警",
                "日志审计",
                "应急响应准备",
                "补丁管理",
            ]),
        ]

        for 阶段名, 活动列表 in SDL阶段:
            print(f"\n  ■ {阶段名}")
            for 活动 in 活动列表:
                print(f"    • {活动}")

    def 安全设计原则(self):
        """安全设计原则"""
        print("\n" + "=" * 60)
        print("安全设计原则")
        print("=" * 60)

        原则列表 = [
            ("最小权限原则", "每个组件/用户只拥有完成任务所需的最小权限",
             "例子：数据库账号只授予SELECT权限，而不是ALL PRIVILEGES"),
            ("纵深防御原则", "多层安全防护，一层失效还有下一层",
             "例子：WAF + 输入验证 + 参数化查询 共同防御SQL注入"),
            ("默认安全原则", "默认配置应该是最安全的状态，用户按需开启功能",
             "例子：新用户默认禁用不必要的功能，需要管理员授权"),
            ("故障安全原则", "系统异常时默认进入安全状态（拒绝访问）",
             "例子：认证服务宕机时，默认拒绝所有登录请求"),
            ("职责分离原则", "关键操作需要多人/多角色配合，防止单点作恶",
             "例子：转账操作需要操作员录入 + 审核员确认"),
            ("不信任原则", "默认不信任任何外部输入和第三方组件",
             "例子：所有API输入都要验证，即使来自内部服务"),
            ("简单性原则", "安全机制越简单越可靠，避免复杂设计",
             "例子：使用标准加密库，不要自己实现加密算法"),
            ("隐私保护原则", "最小化数据收集，数据脱敏，隐私设计",
             "例子：日志中不记录敏感信息（密码、身份证号）"),
        ]

        for 名称, 说明, 例子 in 原则列表:
            print(f"\n  【{名称}】")
            print(f"    说明: {说明}")
            print(f"    {例子}")

    def 威胁建模STRIDE(self):
        """STRIDE威胁建模方法"""
        print("\n" + "=" * 60)
        print("威胁建模 - STRIDE 方法")
        print("=" * 60)

        print("""
  STRIDE 是微软提出的威胁分类方法，用于系统地识别安全威胁。
        """)

        STRIDE列表 = [
            ("S - Spoofing (仿冒)", "冒充他人身份",
             "攻击者伪造管理员身份登录系统",
             "强身份认证、多因素认证"),
            ("T - Tampering (篡改)", "修改数据或代码",
             "攻击者修改交易金额",
             "完整性校验、数字签名、审计日志"),
            ("R - Repudiation (抵赖)", "否认操作行为",
             "用户否认进行了转账操作",
             "操作日志、数字签名、时间戳"),
            ("I - Information Disclosure (信息泄露)", "敏感信息暴露",
             "数据库泄露用户密码",
             "加密存储、访问控制、数据脱敏"),
            ("D - Denial of Service (拒绝服务)", "系统不可用",
             "DDoS攻击导致网站无法访问",
             "限流、高可用架构、WAF"),
            ("E - Elevation of Privilege (权限提升)", "获得更高权限",
             "普通用户提升为管理员权限",
             "最小权限、权限分离、定期审计"),
        ]

        print(f"  {'威胁类型':<30} {'定义':<15} {'示例':<25} {'缓解措施'}")
        print(f"  {'-'*30} {'-'*15} {'-'*25} {'-'*20}")
        for 类型, 定义, 示例, 缓解 in STRIDE列表:
            print(f"  {类型:<30} {定义:<15} {示例:<25} {缓解}")

    def 运行全部(self):
        self.SDL阶段介绍()
        self.安全设计原则()
        self.威胁建模STRIDE()


# ============================================================================
#  案例2: SAST静态应用安全测试
# ============================================================================

class SAST扫描器:
    """
    静态应用安全测试工具

    功能:
    1. 源代码漏洞扫描
    2. 硬编码密钥检测
    3. 安全编码规范检查
    4. 扫描报告生成
    """

    def __init__(self):
        self.源代码 = 模拟源代码
        self.扫描结果 = []

        # 检测规则
        self.检测规则 = {
            "命令注入": [
                (r'os\.system\s*\(', "os.system存在命令注入风险"),
                (r'subprocess\.call\s*\(.*shell\s*=\s*True', "subprocess shell=True注入风险"),
                (r'eval\s*\(', "eval执行任意代码风险"),
                (r'exec\s*\(', "exec执行任意代码风险"),
            ],
            "SQL注入": [
                (r'["\'].*\%s.*["\']\s*\%\s*', "字符串格式化SQL注入"),
                (r'\+\s*["\'].*SELECT|INSERT|UPDATE|DELETE', "字符串拼接SQL"),
                (r'f"[^"]*\{[^}]+\}[^"]*"\s*.*execute', "f-string拼接SQL"),
            ],
            "XSS": [
                (r'render_template_string\s*\(', "模板字符串可能导致XSS"),
                (r'Markup\s*\(', "标记安全字符串可能导致XSS"),
            ],
            "不安全反序列化": [
                (r'pickle\.loads\s*\(', "pickle反序列化代码执行"),
                (r'yaml\.load\s*\(', "yaml.load不安全反序列化"),
            ],
            "弱加密": [
                (r'hashlib\.md5\s*\(', "MD5弱哈希算法"),
                (r'hashlib\.sha1\s*\(', "SHA-1弱哈希算法"),
                (r'DES\.new', "DES弱加密算法"),
            ],
            "硬编码密钥": [
                (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', "硬编码SECRET_KEY"),
                (r'PASSWORD\s*=\s*["\'][^"\']+["\']', "硬编码密码"),
                (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "硬编码API密钥"),
                (r'AKIA[0-9A-Z]{16}', "AWS访问密钥"),
            ],
        }

    def 扫描文件(self, 文件名, 代码内容):
        """扫描单个文件"""
        行列表 = 代码内容.split("\n")

        for 漏洞类型, 规则列表 in self.检测规则.items():
            for 行号, 行内容 in enumerate(行列表, 1):
                for 模式, 说明 in 规则列表:
                    if re.search(模式, 行内容, re.IGNORECASE):
                        self.扫描结果.append({
                            "文件": 文件名,
                            "行号": 行号,
                            "类型": 漏洞类型,
                            "代码": 行内容.strip(),
                            "说明": 说明,
                        })

    def 执行扫描(self):
        """执行完整扫描"""
        print("\n" + "=" * 60)
        print("SAST 静态安全扫描")
        print("=" * 60)

        print(f"\n  扫描文件数: {len(self.源代码)}")
        print(f"  检测规则数: {sum(len(r) for r in self.检测规则.values())}")
        print()

        for 文件名, 代码 in self.源代码.items():
            print(f"  [*] 扫描: {文件名} ({len(代码)} 字节)")
            self.扫描文件(文件名, 代码)

        self.生成报告()

    def 生成报告(self):
        """生成扫描报告"""
        print("\n" + "=" * 60)
        print("SAST 扫描报告")
        print("=" * 60)

        print(f"\n  扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  发现漏洞: {len(self.扫描结果)} 个")
        print()

        # 按文件和类型分组
        按文件 = defaultdict(list)
        按类型 = defaultdict(int)
        for item in self.扫描结果:
            按文件[item["文件"]].append(item)
            按类型[item["类型"]] += 1

        print("  【按漏洞类型统计】")
        for 类型, 数量 in sorted(按类型.items(), key=lambda x: x[1], reverse=True):
            print(f"    {类型}: {数量} 个")
        print()

        print("  【详细结果】")
        for 文件名, 漏洞列表 in 按文件.items():
            print(f"\n  ▶ {文件名} ({len(漏洞列表)}个问题)")
            for 漏洞 in 漏洞列表:
                print(f"    第{漏洞['行号']}行 [{漏洞['类型']}]")
                print(f"      代码: {漏洞['代码'][:60]}")
                print(f"      说明: {漏洞['说明']}")

        print(f"""
  修复建议:
    1. 所有SQL查询使用参数化查询或ORM
    2. 移除硬编码密钥，使用环境变量或密钥管理服务
    3. 使用安全的哈希算法 (SHA-256或bcrypt)
    4. 避免使用eval/exec和不安全反序列化
    5. 输出编码防止XSS
    6. 将扫描集成到CI/CD流水线中
        """)

    def 运行扫描(self):
        self.执行扫描()


# ============================================================================
#  案例3: 依赖漏洞扫描 (SCA)
# ============================================================================

class SCA依赖扫描:
    """
    软件成分分析 (SCA) - 依赖漏洞扫描

    功能:
    1. 依赖清单生成
    2. 漏洞匹配
    3. 许可证合规检查
    4. 修复建议
    """

    def __init__(self):
        self.漏洞库 = 模拟依赖漏洞

    def 扫描依赖(self):
        """扫描依赖漏洞"""
        print("\n" + "=" * 60)
        print("SCA 依赖漏洞扫描")
        print("=" * 60)

        print(f"\n  扫描项目: Python Web应用")
        print(f"  依赖包数: {len(self.漏洞库)}")
        print(f"  漏洞库: 模拟CVE数据库")
        print()

        print(f"  {'包名':<15} {'当前版本':<12} {'最新版本':<12} {'严重程度':<8} {'CVE编号'}")
        print(f"  {'-'*15} {'-'*12} {'-'*12} {'-'*8} {'-'*20}")

        高危数 = 0
        中危数 = 0
        低危数 = 0

        for 漏洞 in self.漏洞库:
            print(f"  {漏洞['包名']:<15} {漏洞['当前版本']:<12} {漏洞['最新版本']:<12} {漏洞['严重程度']:<8} {漏洞['CVE']}")
            if 漏洞["严重程度"] == "高危":
                高危数 += 1
            elif 漏洞["严重程度"] == "中危":
                中危数 += 1
            else:
                低危数 += 1

        print(f"\n  漏洞统计: 高危={高危数} 中危={中危数} 低危={低危数}")
        print(f"  风险等级: {'严重' if 高危数 > 0 else '中等' if 中危数 > 0 else '低'}")

        # 详细信息
        print("\n  【漏洞详情】")
        for i, 漏洞 in enumerate(self.漏洞库, 1):
            print(f"\n  {i}. {漏洞['包名']} {漏洞['当前版本']}")
            print(f"     CVE: {漏洞['CVE']} ({漏洞['严重程度']})")
            print(f"     描述: {漏洞['描述']}")
            print(f"     影响: {漏洞['影响范围']}")
            print(f"     修复: 升级到 {漏洞['最新版本']}")

    def 许可证检查(self):
        """许可证合规检查"""
        print("\n" + "=" * 60)
        print("许可证合规检查")
        print("=" * 60)

        模拟依赖许可证 = [
            ("django", "BSD-3-Clause", "兼容"),
            ("requests", "Apache-2.0", "兼容"),
            ("flask", "BSD-3-Clause", "兼容"),
            ("pyyaml", "MIT", "兼容"),
            ("cryptography", "Apache-2.0 / BSD", "兼容"),
            ("gpl-lib", "GPL-3.0", "风险"),
            ("agpl-lib", "AGPL-3.0", "高风险"),
        ]

        print(f"\n  {'包名':<20} {'许可证':<20} {'合规状态'}")
        print(f"  {'-'*20} {'-'*20} {'-'*10}")

        风险项 = []
        for 包名, 许可证, 状态 in 模拟依赖许可证:
            print(f"  {包名:<20} {许可证:<20} {状态}")
            if 状态 != "兼容":
                风险项.append((包名, 许可证, 状态))

        if 风险项:
            print(f"\n  [!] 发现 {len(风险项)} 个许可证风险:")
            for 包名, 许可证, 状态 in 风险项:
                print(f"    - {包名}: {许可证} ({状态})")
                print(f"      GPL/AGPL许可证可能要求开源你的代码")
        else:
            print("\n  [✓] 所有依赖许可证合规")

    def 修复建议(self):
        """生成修复建议"""
        print("\n" + "=" * 60)
        print("修复优先级建议")
        print("=" * 60)

        print("""
  【修复优先级】
  P0 (立即修复):  高危漏洞且有公开EXP，可被远程利用
  P1 (尽快修复):  高危漏洞，影响核心业务
  P2 (计划修复):  中危漏洞，有缓解措施
  P3 (低优先级):  低危漏洞，难以利用或影响小

  【修复策略】
  1. 直接升级到最新安全版本 (首选)
  2. 如果无法升级，寻找替代方案
  3. 应用临时缓解措施 (WAF规则、配置调整)
  4. 监控漏洞情报，关注新的利用方式
        """)

        print("  【SCA工具推荐】")
        工具列表 = [
            ("Dependabot", "GitHub官方，自动提PR"),
            ("Snyk", "商业工具，支持多语言"),
            ("OWASP Dependency-Check", "开源，Java为主"),
            ("pip-audit", "Python官方工具"),
            ("Trivy", "开源，支持容器和依赖"),
        ]
        for 工具, 说明 in 工具列表:
            print(f"    • {工具:<25} {说明}")

    def 运行全部(self):
        self.扫描依赖()
        self.许可证检查()
        self.修复建议()


# ============================================================================
#  案例4: CI/CD安全流水线
# ============================================================================

class CICD安全流水线:
    """
    CI/CD安全流水线实战

    功能:
    1. 安全流水线架构
    2. 各阶段安全门禁
    3. 安全左移实践
    """

    def 流水线架构(self):
        """介绍安全流水线架构"""
        print("\n" + "=" * 60)
        print("CI/CD 安全流水线架构")
        print("=" * 60)

        print("""
  开发者 ──提交代码──> Git仓库 ──触发CI──> 流水线
                                          │
                       ┌────────────────────┼────────────────────┐
                       ▼                    ▼                    ▼
                  代码质量检查        安全扫描           单元测试
                  (lint/format)    (SAST/SCA)         (覆盖率)
                       │                    │                    │
                       └────────────────────┼────────────────────┘
                                            ▼
                                       构建镜像
                                            │
                                            ▼
                                       镜像扫描
                                       (Trivy等)
                                            │
                                            ▼
                                     部署到测试环境
                                            │
                                            ▼
                                       集成测试 + DAST
                                            │
                                            ▼
                                       合规检查
                                            │
                                            ▼
                                     部署到生产环境
                                            │
                                            ▼
                                     运行时安全监控
        """)

    def 安全门禁配置(self):
        """安全门禁配置"""
        print("\n" + "=" * 60)
        print("安全门禁 (Security Gates) 配置")
        print("=" * 60)

        门禁列表 = [
            ("SAST门禁", "禁止新增加高危漏洞", "新增高危=0, 新增中危<=2", "构建失败"),
            ("SCA门禁", "依赖漏洞在可接受范围内", "高危=0, 中危<=5", "构建失败"),
            ("密钥扫描门禁", "禁止代码中提交密钥", "硬编码密钥=0", "构建失败"),
            ("镜像扫描门禁", "容器镜像无高危漏洞", "高危=0, 可利用<=2", "阻止部署"),
            ("DAST门禁", "关键漏洞已修复", "高危=0", "阻止上线"),
            ("合规门禁", "满足合规要求", "合规检查通过", "阻止上线"),
        ]

        print(f"  {'门禁名称':<15} {'门禁规则':<20} {'阈值':<20} {'触发动作'}")
        print(f"  {'-'*15} {'-'*20} {'-'*20} {'-'*10}")
        for 名称, 规则, 阈值, 动作 in 门禁列表:
            print(f"  {名称:<15} {规则:<20} {阈值:<20} {动作}")

    def 流水线模拟(self):
        """模拟流水线执行"""
        print("\n" + "=" * 60)
        print("流水线执行模拟")
        print("=" * 60)

        print(f"\n  触发事件: 代码提交 (push to main)")
        print(f"  提交者: developer@example.com")
        print(f"  提交ID: a1b2c3d4e5f6")
        print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 模拟各阶段
        阶段结果 = [
            ("代码拉取", "通过", "5s"),
            ("代码质量检查", "通过", "15s"),
            ("SAST静态扫描", "通过", "30s", "发现2个中危，0个新增高危"),
            ("SCA依赖扫描", "警告", "20s", "发现1个高危依赖，需要评估"),
            ("单元测试", "通过", "45s", "覆盖率 85.2%"),
            ("容器构建", "通过", "60s"),
            ("镜像安全扫描", "警告", "25s", "发现3个高危系统包"),
            ("部署测试环境", "通过", "40s"),
            ("DAST动态扫描", "通过", "120s"),
            ("合规检查", "通过", "10s"),
        ]

        成功数 = 0
        警告数 = 0
        for i, 阶段 in enumerate(阶段结果, 1):
            名称 = 阶段[0]
            状态 = 阶段[1]
            耗时 = 阶段[2]
            备注 = 阶段[3] if len(阶段) > 3 else ""

            if 状态 == "通过":
                图标 = "✓"
                成功数 += 1
            else:
                图标 = "⚠"
                警告数 += 1

            print(f"  [{i:02d}] {图标} {名称:<20} [{状态:<4}] {耗时:<6} {备注}")

        print(f"""
  流水线结果: {'部分通过，存在警告' if 警告数 > 0 else '全部通过'}
  通过阶段: {成功数}/{len(阶段结果)}
  警告阶段: {警告数}/{len(阶段结果)}

  需要关注:
    1. SCA发现高危依赖，建议尽快升级
    2. 镜像存在高危系统包，建议重建基础镜像

  建议: 设置更严格的门禁，高危漏洞零容忍
        """)

    def 安全左移实践(self):
        """安全左移实践"""
        print("\n" + "=" * 60)
        print("安全左移 (Shift-Left) 实践")
        print("=" * 60)

        print("""
  【理念】
  将安全工作从运维/测试阶段提前到开发甚至需求阶段，
  越早发现问题，修复成本越低。

  缺陷修复成本对比:
    需求阶段:  1x
    设计阶段:  3x
    编码阶段:  6x
    测试阶段:  15x
    生产阶段:  100x
        """)

        左移措施 = [
            ("开发前", "安全培训、威胁建模、安全需求"),
            ("编码时", "安全编码规范、IDE插件、代码片段"),
            ("提交前", "pre-commit钩子、本地SAST扫描"),
            ("提交后", "CI流水线SAST/SCA/密钥扫描"),
            ("合并前", "代码审查、安全审批"),
            ("部署前", "DAST扫描、渗透测试、合规检查"),
        ]

        print("  【左移措施】")
        for 阶段, 措施 in 左移措施:
            print(f"    {阶段:<10} → {措施}")

        print("""
  【pre-commit 钩子示例】
  1. 代码格式化 (black / prettier)
  2. 代码风格检查 (flake8 / eslint)
  3. 密钥检测 (gitleaks / truffleHog)
  4. 本地SAST (bandit / semgrep)
  5. 单元测试 (pytest / jest)
        """)

    def 运行全部(self):
        self.流水线架构()
        self.安全门禁配置()
        self.流水线模拟()
        self.安全左移实践()


# ============================================================================
#  案例5: 容器与IaC安全
# ============================================================================

class 容器与IaC安全:
    """
    容器与基础设施即代码安全

    功能:
    1. Dockerfile安全审计
    2. Kubernetes安全配置
    3. Terraform安全扫描
    4. 基础设施即代码最佳实践
    """

    def Dockerfile审计(self):
        """审计Dockerfile安全"""
        print("\n" + "=" * 60)
        print("Dockerfile 安全审计")
        print("=" * 60)

        dockerfile = 模拟源代码["Dockerfile"]
        print("\n  待审计Dockerfile:")
        for i, line in enumerate(dockerfile.strip().split('\n'), 1):
            print(f"    {i:2d}| {line.strip()}")

        print("\n  【安全问题】")
        问题列表 = [
            ("使用latest标签", "高", "FROM ubuntu:latest",
             "latest标签不可复现，应使用具体版本号"),
            ("以root用户运行", "高", "USER root",
             "容器不应以root运行，应创建普通用户"),
            ("安装不必要的包", "中", "apt-get install -y curl wget",
             "最小化安装，只安装必需的包"),
            ("缺少健康检查", "中", "无HEALTHCHECK指令",
             "添加HEALTHCHECK指令监控容器健康状态"),
            ("缺少.dockerignore", "低", "无.dockerignore文件",
             "使用.dockerignore排除不必要的文件"),
        ]

        for i, (问题, 严重程度, 位置, 建议) in enumerate(问题列表, 1):
            print(f"\n  {i}. [{严重程度}] {问题}")
            print(f"     位置: {位置}")
            print(f"     建议: {建议}")

        print("""
  【Dockerfile安全最佳实践】
    1. 使用最小基础镜像 (alpine / distroless)
    2. 使用具体版本标签，避免latest
    3. 非root用户运行容器
    4. 多阶段构建减少镜像大小
    5. 合并RUN指令减少层数
    6. 添加HEALTHCHECK健康检查
    7. 不在镜像中存储敏感信息
    8. 使用.dockerignore排除无关文件
    9. 定期更新基础镜像
   10. 镜像签名与验证
        """)

    def K8s安全审计(self):
        """审计Kubernetes配置"""
        print("\n" + "=" * 60)
        print("Kubernetes 安全配置审计")
        print("=" * 60)

        k8s配置 = 模拟源代码["k8s/deployment.yaml"]
        print("\n  待审计K8s Deployment:")
        for i, line in enumerate(k8s配置.strip().split('\n'), 1):
            print(f"    {i:2d}| {line}")

        print("\n  【安全问题】")
        问题列表 = [
            ("特权模式运行", "严重", "privileged: true",
             "特权容器可逃逸到宿主机，绝对禁止"),
            ("以root用户运行", "高", "runAsUser: 0",
             "应设置runAsNonRoot: true"),
            ("缺少资源限制", "中", "无resources字段",
             "应设置CPU/内存限制防止资源耗尽"),
            ("缺少安全上下文", "中", "securityContext配置不全",
             "应配置readOnlyRootFilesystem, allowPrivilegeEscalation等"),
            ("使用latest标签", "中", "image: myapp:latest",
             "应使用具体版本号"),
        ]

        for i, (问题, 严重程度, 位置, 建议) in enumerate(问题列表, 1):
            print(f"\n  {i}. [{严重程度}] {问题}")
            print(f"     位置: {位置}")
            print(f"     建议: {建议}")

        print("""
  【Kubernetes安全最佳实践】
    Pod安全标准 (PSS):
    - Privileged: 完全开放（不推荐）
    - Baseline: 基本安全限制
    - Restricted: 严格限制（推荐）

  关键安全配置:
    - runAsNonRoot: true
    - readOnlyRootFilesystem: true
    - allowPrivilegeEscalation: false
    - capabilities: drop: ["ALL"]
    - seccompProfile: RuntimeDefault
    - resources: limits & requests
        """)

    def Terraform安全审计(self):
        """审计Terraform配置"""
        print("\n" + "=" * 60)
        print("Terraform IaC 安全审计")
        print("=" * 60)

        tf代码 = 模拟源代码["terraform/main.tf"]
        print("\n  待审计Terraform代码:")
        for i, line in enumerate(tf代码.strip().split('\n'), 1):
            print(f"    {i:2d}| {line}")

        print("\n  【安全问题】")
        问题列表 = [
            ("S3桶公开读取", "高", 'acl = "public-read"',
             "S3桶不应公开读取，应使用私有ACL"),
            ("SSH端口全网开放", "高", 'cidr_blocks = ["0.0.0.0/0"] 端口22',
             "SSH端口应限制为特定IP访问"),
            ("全端口开放", "严重", 'from_port = 0 to_port = 65535',
             "安全组不应开放所有端口，按需开放"),
            ("缺少加密配置", "中", "无server_side_encryption_configuration",
             "S3桶应启用服务端加密"),
            ("缺少版本控制", "低", "无versioning配置",
             "建议启用版本控制防止误删除"),
        ]

        for i, (问题, 严重程度, 位置, 建议) in enumerate(问题列表, 1):
            print(f"\n  {i}. [{严重程度}] {问题}")
            print(f"     位置: {位置}")
            print(f"     建议: {建议}")

        print("""
  【IaC安全工具】
    - Checkov: 开源IaC静态分析
    - tfsec: Terraform安全扫描
    - Terrascan: 多平台IaC扫描
    - KICS: 开源IaC安全扫描
    - SonarQube: 代码质量+IaC
        """)

    def 运行全部(self):
        self.Dockerfile审计()
        self.K8s安全审计()
        self.Terraform安全审计()


# ============================================================================
#  主函数
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("DevSecOps与安全开发实战案例集")
    print("=" * 70)
    print("""
请选择要运行的实战案例:

  1. 安全开发生命周期(SDL)实践
  2. SAST静态应用安全测试
  3. SCA依赖漏洞扫描
  4. CI/CD安全流水线
  5. 容器与IaC安全
  6. 运行全部案例
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
            sdl = SDL实践指南()
            sdl.运行全部()
        elif choice == "2":
            sast = SAST扫描器()
            sast.运行扫描()
        elif choice == "3":
            sca = SCA依赖扫描()
            sca.运行全部()
        elif choice == "4":
            cicd = CICD安全流水线()
            cicd.运行全部()
        elif choice == "5":
            iac = 容器与IaC安全()
            iac.运行全部()
        elif choice == "6":
            print("\n" + "=" * 70)
            print("正在运行全部实战案例...")
            print("=" * 70)

            sdl = SDL实践指南()
            sdl.运行全部()

            sast = SAST扫描器()
            sast.运行扫描()

            sca = SCA依赖扫描()
            sca.运行全部()

            cicd = CICD安全流水线()
            cicd.运行全部()

            iac = 容器与IaC安全()
            iac.运行全部()

            print("\n" + "=" * 70)
            print("所有案例运行完成！")
            print("=" * 70)
        else:
            print("无效选项，请重新输入 (0-6)")

        print("\n" + "-" * 70)


if __name__ == "__main__":
    main()
