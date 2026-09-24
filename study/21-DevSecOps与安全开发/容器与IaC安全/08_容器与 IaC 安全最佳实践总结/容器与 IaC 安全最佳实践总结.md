# 容器与 IaC 安全最佳实践总结

### 8.1 容器安全清单

| 类别 | 检查项 | 优先级 |
|------|-------|-------|
| 镜像安全 | 使用官方精简基础镜像 | 高 |
| 镜像安全 | 固定镜像版本标签 | 高 |
| 镜像安全 | 定期扫描镜像漏洞 | 高 |
| 镜像安全 | 镜像签名验证 | 中 |
| 镜像安全 | 不在镜像中存储密钥 | 高 |
| 运行时安全 | 非 root 用户运行 | 高 |
| 运行时安全 | 只读根文件系统 | 高 |
| 运行时安全 | 丢弃所有 capabilities | 高 |
| 运行时安全 | 启用 Seccomp | 中 |
| 运行时安全 | 资源限制 | 高 |
| 运行时安全 | 运行时安全监控 | 中 |

### 8.2 Kubernetes 安全清单

| 类别 | 检查项 | 优先级 |
|------|-------|-------|
| RBAC | 最小权限配置 | 高 |
| RBAC | 禁止 cluster-admin 过度授权 | 高 |
| Pod Security | Restricted 安全级别 | 高 |
| Pod Security | 禁止特权容器 | 高 |
| 网络安全 | 默认拒绝 Network Policy | 高 |
| 网络安全 | 最小允许网络策略 | 高 |
| 网络安全 | mTLS 服务网格 | 中 |
| 准入控制 | OPA Gatekeeper 策略 | 高 |
| 准入控制 | 镜像签名验证 | 中 |
| 密钥管理 | Vault 动态密钥 | 高 |
| 密钥管理 | 禁止 Secret 明文存储 | 高 |
| 审计 | 启用审计日志 | 高 |
| 监控 | 运行时安全监控(Falco) | 中 |
| 监控 | 安全基准检查(kube-bench) | 中 |

### 8.3 IaC 安全清单

| 类别 | 检查项 | 优先级 |
|------|-------|-------|
| 网络安全 | 安全组最小化规则 | 高 |
| 网络安全 | 禁止 0.0.0.0/0 入站 | 高 |
| 网络安全 | 数据库禁止公网访问 | 高 |
| IAM | 最小权限策略 | 高 |
| IAM | 禁止通配符权限 | 高 |
| 数据保护 | 存储加密 | 高 |
| 数据保护 | 数据库加密 | 高 |
| 数据保护 | 传输加密(TLS) | 高 |
| 密钥管理 | 禁止硬编码密钥 | 高 |
| 密钥管理 | 使用 Vault/KMS | 高 |
| 日志审计 | 启用操作日志 | 中 |
| 资源保护 | 启用删除保护 | 中 |
| IaC扫描 | tfsec/Checkov 扫描 | 高 |

---

> **总结**：容器与 IaC 安全是云原生安全的基石。容器安全需要从镜像构建到运行时全链路防护，Kubernetes 安全需要从集群到工作负载多层防御，IaC 安全需要将安全检查嵌入代码管理流程。关键是通过自动化工具链实现持续安全验证，确保基础设施配置始终符合安全标准。通过"安全即代码"的方式，将安全策略版本化管理、自动化验证、持续监控，才能真正构建安全的云原生生产环境。

---

## 🛠️ 补充：实战拓展

### 一、Checkov - IaC 安全扫描工具

#### 1.1 安装与基本使用
```bash
# 安装
pip install checkov
# 或 Docker 方式
docker pull bridgecrew/checkov

# 基本扫描 Terraform
checkov -d ./terraform/                  # 扫描目录
checkov -f ./terraform/main.tf           # 扫描单个文件

# 扫描 CloudFormation
checkov -d ./cloudformation/ --framework cloudformation

# 扫描 Kubernetes manifests
checkov -d ./k8s/ --framework kubernetes

# 扫描 Dockerfile
checkov -d ./docker/ --framework dockerfile

# 扫描多种框架
checkov -d . --framework all
# 支持的框架：terraform, cloudformation, kubernetes, dockerfile, 
#             serverless, arm, bicep, helm, kustomize, terraform_plan
```

#### 1.2 输出与报告
```bash
# 输出格式
checkov -d . --output cli               # 命令行输出（默认）
checkov -d . --output json              # JSON格式
checkov -d . --output junitxml          # JUnit XML
checkov -d . --output sarif            # SARIF格式（GitHub兼容）
checkov -d . --output cyclonedx        # CycloneDX SBOM

# 输出到文件
checkov -d . -o json --output-file-path checkov_results/

# 紧凑输出（只显示失败项）
checkov -d . --compact
checkov -d . --quiet

# 输出统计摘要
checkov -d . --summary
checkov -d . --summary-position top    # 摘要在顶部显示
```

#### 1.3 规则管理
```bash
# 列出所有可用规则
checkov --list

# 按类别列出规则
checkov --list --framework terraform

# 跳过指定规则
checkov -d . --skip-check CKV_AWS_1,CKV_AWS_2

# 只运行指定规则
checkov -d . --check CKV_AWS_1,CKV_AWS_2

# 按严重级别过滤
checkov -d . --soft-fail-on LOW        # 低风险不失败
checkov -d . --hard-fail-on CRITICAL   # 仅高危时失败
checkov -d . --check MEDIUM,HIGH,CRITICAL  # 只检查中危及以上

# 跳过指定路径
checkov -d . --skip-path ./terraform/modules/test/
checkov -d . --skip-path "*/test/*"    # 支持通配符

# 基线（Baseline）- 忽略已知问题
checkov -d . --create-baseline         # 创建基线
checkov -d . --baseline .checkov.baseline  # 使用基线
```

#### 1.4 配置文件 .checkov.yaml
```yaml
# .checkov.yaml 配置文件
compact: false
quiet: false
framework:
  - terraform
  - kubernetes
  - dockerfile

soft-fail-on:
  - LOW

hard-fail-on:
  - CRITICAL
  - HIGH

skip-check:
  - CKV_AWS_123
  - CKV_DOCKER_456

skip-path:
  - tests/
  - examples/

# 自定义规则目录
external-checks-dir:
  - ./custom_checks/

# 下载外部规则
download-external-modules: true
external-modules-download-path: .external_modules
```

#### 1.5 CI/CD 集成
```yaml
# GitHub Actions
- name: Checkov Scan
  uses: bridgecrewio/checkov-action@master
  with:
    directory: .
    framework: terraform
    soft_fail_on: LOW
    output_format: sarif
    output_file_path: ./checkov-results.sarif

# GitLab CI
checkov:
  stage: test
  image:
    name: bridgecrew/checkov:latest
    entrypoint:
      - '/usr/bin/env'
      - 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
  script:
    - checkov -d . --framework terraform --soft-fail-on LOW --output junitxml --output-file-path checkov-results.xml
  artifacts:
    reports:
      junit: checkov-results.xml
    when: always
```

### 二、tfsec - Terraform 静态安全分析

#### 2.1 安装与基本使用
```bash
# 安装
brew install tfsec                       # macOS
# 或下载二进制
curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash
# 或 Docker
docker pull aquasec/tfsec

# 基本扫描
tfsec .                                  # 扫描当前目录
tfsec ./terraform/modules/              # 扫描指定目录

# 指定Terraform版本
tfsec --tfvars-file variables.tfvars .
tfsec --exclude-downloaded-modules .     # 排除下载的模块

# 详细输出
tfsec -v .                               # 详细模式
tfsec --verbose .
tfsec --print-rego .                     # 打印Rego规则
```

#### 2.2 输出格式
```bash
# 输出格式
tfsec -f default .                      # 默认格式
tfsec -f json .                         # JSON格式
tfsec -f csv .                          # CSV格式
tfsec -f checkstyle .                   # Checkstyle格式
tfsec -f junit .                        # JUnit格式
tfsec -f sarif .                        # SARIF格式
tfsec -f sonarqube .                    # SonarQube格式

# 输出到文件
tfsec -f json -O tfsec_results.json .

# 只显示失败的检查
tfsec --include-failed .
```

#### 2.3 规则配置
```bash
# 列出所有规则
tfsec --list-all-checks

# 按严重级别过滤
tfsec --min-severity HIGH .             # 只显示高危及以上
tfsec --exclude-severity LOW .          # 排除低风险

# 禁用指定规则
tfsec --exclude-checks AWS001,AWS002 .

# 只运行指定规则
tfsec --include-checks AWS001,AWS002 .

# 自定义检查路径
tfsec --custom-check-dir ./custom_checks .
```

#### 2.4 忽略规则（代码内注释）
```hcl
# tfsec:ignore:AWS001 - 原因说明
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "public-read"  # tfsec:ignore:AWS002
}

# 忽略多个规则
# tfsec:ignore:AWS001 tfsec:ignore:AWS002 - 原因说明
resource "aws_security_group" "example" {
  name = "example-sg"
  
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 配置文件 tfsec.yml
---
minimum_severity: MEDIUM
exclude_checks:
  - AWS001
  - AWS002
exclude_paths:
  - tests/
  - examples/
```

### 三、KICS - 基础设施即代码安全扫描

#### 3.1 安装与基本使用
```bash
# Docker 方式（推荐）
docker pull checkmarx/kics:latest

# 基本扫描
kics scan -p ./terraform/               # 扫描路径
kics scan -p ./cloudformation/ -o ./results/  # 指定输出目录

# 扫描多种IaC类型
kics scan -p . --type terraform         # Terraform
kics scan -p . --type cloudformation    # CloudFormation
kics scan -p . --type kubernetes        # Kubernetes
kics scan -p . --type dockerfile        # Dockerfile
kics scan -p . --type ansible           # Ansible
kics scan -p . --type helm              # Helm Charts
kics scan -p . --type all               # 所有类型

# 多种类型同时扫描
kics scan -p . --type terraform,kubernetes,dockerfile
```

#### 3.2 输出与报告
```bash
# 输出格式
kics scan -p . -o results/ --report-formats json
kics scan -p . -o results/ --report-formats sarif
kics scan -p . -o results/ --report-formats html
kics scan -p . -o results/ --report-formats pdf
kics scan -p . -o results/ --report-formats junit
kics scan -p . -o results/ --report-formats glsast  # GitLab SAST格式
kics scan -p . -o results/ --report-formats sonarqube

# 多种格式同时输出
kics scan -p . -o results/ --report-formats json,sarif,html

# 输出文件名
kics scan -p . -o results/ --output-name kics_report

# 详细程度
kics scan -p . -v                       # 详细日志
kics scan -p . -vv                      # 更详细
kics scan -p . --silent                 # 静默模式
kics scan -p . --no-progress            # 不显示进度条
```

#### 3.3 规则与阈值配置
```bash
# 列出所有查询
kics generate-id --queries

# 严重级别阈值
kics scan -p . --fail-on high           # 高危才失败
kics scan -p . --fail-on medium         # 中危及以上失败
kics scan -p . --fail-on low            # 低危及以上失败
kics scan -p . --ignore-on-exit info    # 信息级不影响退出码

# 排除查询
kics scan -p . --exclude-queries a1b2c3d4,e5f6a7b8

# 只包含指定查询
kics scan -p . --include-queries a1b2c3d4

# 排除路径
kics scan -p . --exclude-paths "**/test/**,**/examples/**"

# 排除结果（基线）
kics scan -p . --exclude-results kics-results.json
```

#### 3.4 KICS 配置文件 kics.config
```json
{
  "path": ".",
  "output-path": "./kics-results",
  "type": "terraform,kubernetes,dockerfile",
  "report-formats": "json,sarif,html",
  "fail-on": "high",
  "ignore-on-exit": "info",
  "exclude-paths": [
    "tests/",
    "examples/",
    "**/node_modules/**"
  ],
  "exclude-queries": [
    "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"
  ],
  "queries-path": "./custom_queries/",
  "libraries-path": "./custom_libraries/",
  "timeout": 60,
  "parallel-scan": true,
  "minimal-ui": false,
  "no-color": false
}

# 使用配置文件
kics scan --config kics.config
```

### 四、其他 IaC 与容器安全工具

#### 4.1 Trivy - 容器与IaC综合扫描
```bash
# 安装
brew install aquasecurity/trivy/trivy
# 或 Docker
docker pull aquasec/trivy

# 容器镜像扫描
trivy image nginx:latest
trivy image --severity HIGH,CRITICAL nginx:latest
trivy image --format json -o image_scan.json nginx:latest
trivy image --ignore-unfixed nginx:latest          # 忽略无修复的漏洞

# IaC 扫描
trivy config ./terraform/                         # Terraform扫描
trivy config --severity CRITICAL,HIGH ./terraform/
trivy config --format json -o iac_scan.json ./terraform/
trivy config --misconf-scanners all ./k8s/        # Kubernetes扫描

# 文件系统扫描
trivy fs ./project/
trivy fs --scanners vuln,secret,misconfig ./project/

# 仓库扫描
trivy repo https://github.com/example/repo.git
trivy repo --branch main https://github.com/example/repo.git

# 秘钥扫描
trivy fs --scanners secret ./project/
trivy image --scanners secret nginx:latest

# SBOM 生成
trivy image --format spdx -o sbom.spdx nginx:latest
trivy image --format cyclonedx -o sbom.cdx.json nginx:latest
```

#### 4.2 Snyk IaC - SaaS IaC扫描
```bash
# 安装 Snyk CLI
npm install -g snyk

# 认证
snyk auth <API_TOKEN>

# IaC 扫描
snyk iac test ./terraform/
snyk iac test ./cloudformation/template.json
snyk iac test ./k8s/deployment.yaml
snyk iac test ./k8s/helm-chart/

# 输出选项
snyk iac test ./terraform/ --json > snyk_iac.json
snyk iac test ./terraform/ --sarif-file-output=snyk_iac.sarif

# 严重级别过滤
snyk iac test ./terraform/ --severity-threshold=high

# 监控模式
snyk iac test ./terraform/ --project-name=my-infra

# CI 集成
snyk iac test ./terraform/ --severity-threshold=critical || true
```

#### 4.3 Terrascan - Terrascan IaC扫描
```bash
# 安装
curl -L https://raw.githubusercontent.com/tenable/terrascan/master/docs/install.sh | bash
# 或 Docker
docker pull tenable/terrascan

# 基本扫描
terrascan scan -d ./terraform/
terrascan scan -i terraform -d ./terraform/
terrascan scan -i k8s -d ./k8s/
terrascan scan -i helm -d ./helm-chart/

# 输出格式
terrascan scan -d . -o json > terrascan_results.json
terrascan scan -d . -o yaml > terrascan_results.yaml
terrascan scan -d . -o xml > terrascan_results.xml
terrascan scan -d . -o sarif > terrascan_results.sarif

# 策略级别
terrascan scan -d . --severity high
terrascan scan -d . --policy-type aws

# 跳过规则
terrascan scan -d . --skip-rules AC_AWS_001,AC_AWS_002

# 自定义策略
terrascan scan -d . --policy-path ./custom_policies/
```

#### 4.4 Kubesec - Kubernetes 安全扫描
```bash
# 在线扫描
curl -sSX POST --data-binary @deployment.yaml https://v2.kubesec.io/scan

# Docker本地扫描
docker run -i kubesec/kubesec:latest scan /dev/stdin < deployment.yaml

# 扫描多个文件
kubesec scan deployment.yaml service.yaml ingress.yaml

# JSON输出
curl -sSX POST --data-binary @deployment.yaml https://v2.kubesec.io/scan | jq .

# 评分说明
# 10分以上：安全配置良好
# 0-10分：存在中等风险
# 负数分：存在严重安全问题
```

### 五、IaC 安全扫描 CI/CD 集成

#### 5.1 GitHub Actions 集成模板
```yaml
# .github/workflows/iac-security.yml
name: IaC Security Scan

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'k8s/**'
      - 'Dockerfile*'

jobs:
  checkov-scan:
    name: Checkov Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          soft_fail_on: LOW
          output_format: sarif
          output_file_path: checkov.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: checkov.sarif

  trivy-scan:
    name: Trivy IaC + Secret Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          format: 'sarif'
          output: 'trivy-results.sarif'
          exit-code: '1'
          ignore-unfixed: true

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: trivy-results.sarif

  kics-scan:
    name: KICS Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run KICS
        uses: Checkmarx/kics-github-action@v1.7.0
        with:
          path: '.'
          output_path: kics_results/
          output_formats: 'json,sarif'
          fail_on: high
          type: 'terraform,kubernetes,dockerfile'
```

#### 5.2 多工具对比与选型建议
```
┌─────────────────────────────────────────────────────────────────┐
│                  IaC 安全扫描工具对比                            │
├───────────┬──────────┬──────────┬──────────┬───────────────────┤
│ 特性       │ Checkov  │ tfsec    │ KICS     │ Trivy             │
├───────────┼──────────┼──────────┼──────────┼───────────────────┤
│ 开发商     │ Palo Alto│ Aqua     │ Checkmarx│ Aqua              │
│ 开源协议   │ Apache2.0│ MIT      │ Apache2.0│ Apache2.0         │
├───────────┼──────────┼──────────┼──────────┼───────────────────┤
│ 支持框架   │ 多       │ Terraform│ 最多     │ 多                │
│ Terraform │ ✓        │ ✓        │ ✓        │ ✓                 │
│ CloudFormation│ ✓    │ ✗        │ ✓        │ ✓                 │
│ Kubernetes│ ✓        │ ✗        │ ✓        │ ✓                 │
│ Dockerfile│ ✓        │ ✗        │ ✓        │ ✓                 │
│ Helm      │ ✓        │ ✗        │ ✓        │ ✓                 │
│ Ansible   │ ✗        │ ✗        │ ✓        │ ✗                 │
├───────────┼──────────┼──────────┼──────────┼───────────────────┤
│ 规则数量   │ 多       │ 中       │ 最多     │ 中                │
│ 自定义规则 │ ✓        │ ✓        │ ✓        │ ✓                 │
│ SARIF输出  │ ✓        │ ✓        │ ✓        │ ✓                 │
│ 基线功能   │ ✓        │ ✗        │ ✓        │ 部分              │
│ IDE插件    │ ✓        │ ✓        │ ✗        │ ✓                 │
├───────────┼──────────┼──────────┼──────────┼───────────────────┤
│ 适用场景   │ 企业级   │ TF专注   │ 多框架   │ 综合扫描          │
│ SaaS服务  │ 有       │ 有       │ 有       │ 有                │
└───────────┴──────────┴──────────┴──────────┴───────────────────┘

推荐组合：
- 主力工具：Checkov（规则丰富，社区活跃）
- 补充工具：Trivy（同时支持镜像扫描+秘钥扫描）
- Kubernetes专项：KICS + Kubesec
- Terraform专项：tfsec（轻量快速，适合pre-commit）
```

---

## 🚀 实战拓展

### 💻 常用工具
Nmap、Burp Suite、Wireshark、Metasploit、sqlmap、Python

### ⌨️ 关键命令
常用Linux命令、网络工具命令、脚本语言基础

### 🎯 练习建议
靶场练习、CTF比赛、SRC漏洞挖掘、自建实验环境

### 🛡️ 防御要点
安全意识、最小权限、纵深防御、持续监控、定期审计

### 📖 延伸阅读
相关技术文档、官方指南、安全博客、技术社区

---

