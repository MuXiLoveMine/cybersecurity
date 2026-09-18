# SCA 与 SBOM 实战指南

> 现代软件 80% 以上由开源组件构成，供应链安全已成为 DevSecOps 的关键环节。本文档系统讲解软件成分分析（SCA）、软件物料清单（SBOM）的原理、工具实战、漏洞数据库、许可证合规及供应链安全框架，并提供 CI/CD 集成方案与 Python 实战脚本。

---

## 目录

1. [软件成分分析（SCA）概述](#一软件成分分析sca概述)
2. [SBOM（软件物料清单）](#二sbom软件物料清单)
3. [SCA 工具实战](#三sca-工具实战)
4. [漏洞数据库](#四漏洞数据库)
5. [许可证合规](#五许可证合规)
6. [供应链安全](#六供应链安全)
7. [SCA 在 CI/CD 中的集成](#七sca-在-cicd-中的集成)
8. [Python SCA 工具示例](#八python-sca-工具示例)

---

## 一、软件成分分析（SCA）概述

### 1.1 开源组件安全风险

```
现代软件构成：

┌─────────────────────────────────────────┐
│            应用程序                      │
│  ┌─────────────────────────────────┐    │
│  │     自研代码（约 10-30%）        │    │
│  ├─────────────────────────────────┤    │
│  │  第三方库（约 40-60%）           │    │
│  │  ├── 直接依赖                    │    │
│  │  │   ├── requests==2.28.0       │    │
│  │  │   ├── django==4.2.0          │    │
│  │  │   └── ...                    │    │
│  │  └── 间接依赖（传递依赖）        │    │
│  │      ├── urllib3               │    │
│  │      ├── certifi               │    │
│  │      └── ...（可达数百个）      │    │
│  ├─────────────────────────────────┤    │
│  │  基础镜像层（约 20-30%）         │    │
│  │  ├── OS 包（apt/yum）           │    │
│  │  └── 系统库                     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

风险点：
├── 已知漏洞（CVE）        → 组件含已公开漏洞
├── 许可证合规              → GPL 等传染性许可证风险
├── 废弃/未维护组件         → 无人修复漏洞
├── 供应链投毒              → 恶意代码注入上游包
├── 依赖混淆                → 名称相似包伪装
└── 版本漂移                → 间接依赖版本不一致
```

**典型案例：**
- **Log4Shell（CVE-2021-44228）**：Log4j2 JNDI 注入，CVSS 10.0，影响全球数百万系统
- **LeftPad 事件**：一个 11 行代码的 npm 包删除导致数千个项目构建失败
- **XZ Utils 后门**：攻击者两年渗透开源项目，在压缩库中植入后门

### 1.2 SCA 在 DevSecOps 中的角色

```
DevSecOps 流水线中的安全测试层次：

代码提交 → 编译构建 → 测试 → 打包 → 部署 → 运行
   │          │        │       │       │       │
  SAST      SCA      DAST    SCA     镜像    RASP
  静态分析  组件分析   动态    SBOM   漏洞   运行时
           依赖扫描   测试    生成   扫描   保护
```

SCA 在 DevSecOps 中负责：
- **开发阶段**：IDE 插件实时告警依赖漏洞
- **构建阶段**：CI 流水线扫描依赖 + 生成 SBOM
- **部署阶段**：镜像/容器漏洞扫描
- **运行阶段**：持续监控新漏洞（零日漏洞响应）

### 1.3 SCA vs SAST vs DAST

```
┌──────────┬────────────┬─────────────┬──────────────┐
│ 维度     │ SAST       │ SCA         │ DAST         │
├──────────┼────────────┼─────────────┼──────────────┤
│ 分析对象  │ 源代码     │ 依赖清单     │ 运行中应用    │
│ 检测内容  │ 自研代码   │ 第三方组件   │ 运行时行为    │
│ 漏洞类型  │ 注入/XSS   │ CVE已知漏洞  │ 业务逻辑漏洞  │
│ 时机      │ 编码阶段   │ 构建/部署    │ 测试/生产     │
│ 误报率    │ 较高       │ 低          │ 中等         │
│ 发现速度  │ 分钟级     │ 秒级        │ 分钟~小时     │
│ 许可证    │ 不覆盖     │ 覆盖        │ 不覆盖       │
└──────────┴────────────┴─────────────┴──────────────┘

三者互补：SAST 管自研代码 → SCA 管第三方依赖 → DAST 管运行时
```

---

## 二、SBOM（软件物料清单）

### 2.1 SBOM 定义与重要性

SBOM（Software Bill of Materials）是软件组件的正式、结构化清单，记录软件中所有组件的详细信息：

```
SBOM 记录的核心字段：

├── 组件名称         → "log4j-core"
├── 版本号           → "2.14.1"
├── 供应商           → "Apache Software Foundation"
├── 唯一标识符       → "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"
├── 许可证           → "Apache-2.0"
├── 文件哈希         → "SHA256: a1b2c3..."
├── 依赖关系         → 上下游依赖链
├── PURL             → Package URL 标识
└── CPE              → Common Platform Enumeration

SBOM 的价值：
1. 漏洞快速响应：新 CVE 发布时，秒级定位受影响系统
2. 合规要求：美国行政令 14028 要求政府软件必须提供 SBOM
3. 供应链透明：了解软件中到底用了什么
4. 许可证审计：识别合规风险
5. 组件治理：发现废弃/重复/冲突依赖
```

### 2.2 SBOM 格式标准

#### SPDX（Software Package Data Exchange）

```json
// SPDX 2.3 格式示例（JSON）
{
  "spdxVersion": "SPDX-2.3",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "my-application",
  "creationInfo": {
    "created": "2026-09-12T10:00:00Z",
    "creators": ["Organization: MyCorp", "Tool: cyclonedx-bom"]
  },
  "packages": [
    {
      "SPDXID": "SPDXRef-Package-log4j",
      "name": "log4j-core",
      "versionInfo": "2.14.1",
      "supplier": "Organization: Apache",
      "downloadLocation": "https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-core/2.14.1/",
      "licenseConcluded": "Apache-2.0",
      "licenseDeclared": "Apache-2.0",
      "copyrightText": "Copyright Apache Software Foundation",
      "externalRefs": [
        {
          "referenceCategory": "PACKAGE-MANAGER",
          "referenceType": "purl",
          "referenceLocator": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"
        }
      ]
    }
  ]
}
```

#### CycloneDX

```json
// CycloneDX 1.5 格式示例（JSON）
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:3e671687-335b-4e21-83bb-aae4f6d6f689",
  "version": 1,
  "metadata": {
    "timestamp": "2026-09-12T10:00:00Z",
    "tools": [{"vendor": "CycloneDX", "name": "cyclonedx-bom", "version": "4.0.0"}]
  },
  "components": [
    {
      "type": "library",
      "bom-ref": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
      "name": "log4j-core",
      "version": "2.14.1",
      "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
      "licenses": [{"license": {"id": "Apache-2.0"}}],
      "supplier": {"name": "Apache Software Foundation"}
    }
  ]
}
```

#### 格式对比

```
┌──────────────┬────────────────────┬───────────────────────┐
│ 维度         │ SPDX              │ CycloneDX             │
├──────────────┼────────────────────┼───────────────────────┤
│ 制定者       │ Linux Foundation   │ OWASP                 │
│ 主要场景     │ 合规/许可证        │ 安全/漏洞关联         │
│ 支持语言     │ 通用               │ 通用（原生支持多语言） │
│ 漏洞字段     │ 弱（需扩展）        │ 强（原生 VEX 支持）   │
│ 格式         │ JSON/Tag/RDF/YAML  │ JSON/XML              │
│ 社区活跃度   │ 高                 │ 高（DevSecOps 首选）  │
│ 法规要求     │ 美国政府推荐       │ 行业广泛采用          │
└──────────────┴────────────────────┴───────────────────────┘
```

### 2.3 SBOM 生成工具对比

```
┌───────────────────┬──────────────────┬──────────────────────────┐
│ 工具              │ 支持格式          │ 覆盖生态                 │
├───────────────────┼──────────────────┼──────────────────────────┤
│ cyclonedx-bom     │ CycloneDX        │ npm/maven/pip/go/cargo   │
│ syft              │ SPDX/CycloneDX   │ 通用(镜像+目录+包管理器) │
│ trivy             │ SPDX/CycloneDX   │ 镜像+FS+代码库           │
│ spdx-tools        │ SPDX             │ 通用(Java生态)           │
│ bom (npm)         │ SPDX/CycloneDX   │ Node.js                  │
│ gradle-cyclonedx  │ CycloneDX        │ Java(Gradle)             │
└───────────────────┴──────────────────┴──────────────────────────┘
```

### 2.4 SBOM 在供应链安全中的作用

```
漏洞响应流程（基于 SBOM）：

1. 新 CVE 发布（如 Log4Shell）
2. 查询条件：组件名=log4j-core, 版本<2.15.0
3. 扫描所有系统的 SBOM
4. 输出受影响清单：
   ├── 系统 A: log4j-core 2.14.1 → 需升级
   ├── 系统 B: log4j-core 2.12.1 → 需升级
   └── 系统 C: log4j-core 2.17.1 → 不受影响
5. 自动创建工单 → 修复 → 验证 → SBOM 更新
```

---

## 三、SCA 工具实战

### 3.1 OWASP Dependency-Check

```xml
<!-- Maven 集成 pom.xml -->
<plugin>
    <groupId>org.owasp</groupId>
    <artifactId>dependency-check-maven</artifactId>
    <version>9.0.9</version>
    <configuration>
        <formats>
            <format>HTML</format>
            <format>JSON</format>
        </formats>
        <failBuildOnCVSS>7</failBuildOnCVSS>  <!-- CVSS>=7 构建失败 -->
        <suppressionFile>dependency-suppressions.xml</suppressionFile>
    </configuration>
    <executions>
        <execution>
            <goals><goal>check</goal></goals>
        </execution>
    </executions>
</plugin>
```

```bash
# CLI 使用
dependency-check --project "myapp" --scan ./target/ --format JSON --format HTML
# 输出：dependency-check-report.html / .json
```

### 3.2 Snyk

```bash
# 安装
npm install -g snyk

# 扫描项目
snyk test                  # 扫描当前项目依赖
snyk test --severity=high  # 仅显示高危以上
snyk monitor               # 持续监控（新漏洞通知）

# 扫描 Docker 镜像
snyk container test nginx:1.21

# 扫描 IaC
snyk iac test              # 扫描 Terraform/K8s 配置

# 自动修复
snyk fix                   # 自动升级可修复的依赖
```

```yaml
# Snyk 配置文件 .snyk
version: v1.25.0
ignore:
  'CVE-2021-44228':
    - '*':
        reason: '已通过WAF规则缓解，计划下个迭代修复'
        expires: '2026-10-01'
```

### 3.3 Trivy

```bash
# 安装
# Linux: sudo apt-get install trivy
# macOS: brew install trivy
# Windows: choco install trivy

# 扫描容器镜像
trivy image python:3.12-slim
trivy image --severity HIGH,CRITICAL myapp:latest

# 扫描文件系统
trivy fs --severity HIGH,CRITICAL /path/to/project

# 扫描代码库
trivy repo https://github.com/user/repo

# 生成 SBOM
trivy image --format cyclonedx --output sbom.json myapp:latest
trivy image --format spdx-json --output sbom.spdx.json myapp:latest

# 扫描 SBOM 中的漏洞
trivy sbom --format json sbom.json

# 配置文件 trivy.yaml
severity:
  - HIGH
  - CRITICAL
ignore-unfixed: true  # 仅报告有修复方案的漏洞
scanners:
  - vuln
  - license
  - secret
```

### 3.4 Grype

```bash
# 安装
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh

# 扫描镜像
grype myapp:latest
grype myapp:latest --only-fixed       # 仅显示有修复的
grype myapp:latest --severity-high    # 仅高危以上

# 扫描 SBOM
grype sbom:./sbom.cyclonedx.json
grype sbom:./sbom.spdx.json

# 输出格式
grype myapp:latest -o json > vuln-report.json
grype myapp:latest -o table  # 默认表格输出

# 策略配置 .grype.yaml
only-fixed: true
severity-threshold: high
```

### 3.5 各语言包管理器安全扫描

```bash
# === npm audit (Node.js) ===
npm audit                     # 检查 package.json 依赖漏洞
npm audit --audit-level=high  # 仅显示高危以上
npm audit fix                 # 自动修复可修复的
npm audit fix --force         # 激进修复（可能引入breaking change）

# === pip-audit / safety (Python) ===
pip install pip-audit
pip-audit                     # 扫描当前环境
pip-audit -r requirements.txt # 扫描 requirements 文件
pip-audit --format json       # JSON 输出
pip-audit --strict            # 严格模式（含间接依赖）

pip install safety
safety check                  # 检查已知漏洞
safety check --output json   # JSON 输出

# === mvn dependency-check (Java) ===
mvn org.owasp:dependency-check-maven:check
# 或使用 Maven 目标
mvn verify -Pdependency-check

# === go vuln check (Go) ===
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...             # 扫描 Go 代码
govulncheck -json ./...       # JSON 输出

# === cargo audit (Rust) ===
cargo install cargo-audit
cargo audit                   # 扫描 Cargo.lock
cargo audit deny --severity high  # 高危时退出码非0
```

---

## 四、漏洞数据库

### 4.1 NVD（National Vulnerability Database）

NVD 是美国 NIST 维护的全球最大公开漏洞数据库，是 CVE 的增强版：

```
NVD 数据结构：
├── CVE ID        → CVE-2021-44228
├── 描述           → Apache Log4j2 JNDI 注入
├── CVSS 3.x 分数 → 10.0（Critical）
├── 向量           → CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
├── CWE            → CWE-502 (Deserialization)
├── CPE            → cpe:2.3:a:apache:log4j:2.14.1
├── 参考链接       → 补丁/分析报告
└── 发布/修改日期   → 2021-12-10
```

```bash
# NVD API 查询示例
curl "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2021-44228" \
  -H "apiKey: YOUR_API_KEY"
```

### 4.2 GitHub Advisory Database

```
GitHub Advisory Database 特点：
├── 覆盖 npm/PyPI/Maven/RubyGems/Go/Cargo
├── GitHub 维护 + 社区贡献
├── 直接关联 GitHub Dependabot
├── 包含 GHSA（GitHub Security Advisory）ID
└── 比 NVD 更快收录新漏洞
```

```bash
# GraphQL API 查询
gh api graphql -f query='
{
  securityAdvisory(ghsaId: "GHSA-jfh8-c2jp-5v3q") {
    summary
    severity
    cvss { score vector }
    vulnerabilities(first: 10) {
      nodes { package { name ecosystem } vulnerableVersionRange }
    }
  }
}'
```

### 4.3 OSV（Open Source Vulnerability Database）

```bash
# OSV API 查询（REST）
# 查询特定包的漏洞
curl -X POST https://api.osv.dev/v1/query -d '{
  "package": {
    "name": "log4j-core",
    "ecosystem": "Maven"
  },
  "version": "2.14.1"
}'

# 查询特定漏洞
curl https://api.osv.dev/v1/vulns/CVE-2021-44228
```

```
漏洞数据库对比：
┌───────────────┬───────────────┬───────────────┐
│ 维度          │ NVD           │ GitHub Adv.   │ OSV
├───────────────┼───────────────┼───────────────┤
│ 维护者        │ NIST(美国)    │ GitHub        │ Google
│ 覆盖范围      │ 通用(CPE)     │ 多语言生态    │ 多语言生态
│ 更新速度      │ 中(1-7天)     │ 快(社区驱动)  │ 快(聚合源)
│ API 免费      │ 是(有限速)    │ 是            │ 是(无限速)
│ 供应链信息    │ 弱            │ 强            │ 强
│ 数据格式      │ JSON/XML     │ JSON          │ JSON
└───────────────┴───────────────┴───────────────┘
```

### 4.4 商业漏洞数据库

- **VulnDB**（Risk Based Security）：覆盖面广，含非 CVE 漏洞
- **Sonatype Nexus**：聚焦 Maven/PyPI 供应链
- **Veracode SourceClear**：与 SAST 集成
- **Snyk Vulnerability DB**：多语言覆盖，更新快

---

## 五、许可证合规

### 5.1 开源许可证风险

```
许可证风险等级：

┌──────────────────────────────────────────────────────────┐
│              风险  │  许可证  │  说明                   │
├──────────────────────────────────────────────────────────┤
│  🟢 低风险    │  MIT     │  宽松，保留版权声明即可     │
│               │  BSD-2/3  │  宽松                      │
│               │  Apache-2.0│ 宽松，含专利授权          │
│               │  ISC      │  极简宽松                  │
├──────────────────────────────────────────────────────────┤
│  🟡 中风险    │  LGPL    │  弱传染性，动态链接可避免   │
│               │  MPL-2.0  │  弱传染性，文件级           │
│               │  EPL-2.0  │  弱传染性                   │
├──────────────────────────────────────────────────────────┤
│  🔴 高风险    │  GPL-2.0 │  强传染性，衍生作品须开源   │
│               │  GPL-3.0  │  强传染性 + 专利反制        │
│               │  AGPL-3.0 │  网络服务也须开源          │
├──────────────────────────────────────────────────────────┤
│  ⛔ 禁止      │  SSPL    │  MongoDB 许可证，争议大     │
│               │  Proprietary│ 未授权使用闭源组件       │
│               │  Unlicensed│ 无许可证 = 保留所有权利  │
└──────────────────────────────────────────────────────────┘
```

### 5.2 许可证扫描工具

```bash
# ScanCode（通用）
pip install scancode-toolkit
scancode --license --package /path/to/project
# 输出：license扫描报告 JSON/HTML

# licensefinder (Ruby/Rails)
license_finder

# license-checker (npm)
npx license-checker --production --json > licenses.json

# go-licenses (Go)
go install github.com/google/go-licenses@latest
go-licenses report ./... > licenses.csv
```

### 5.3 许可证策略管理

```python
# 许可证策略示例
LICENSE_POLICY = {
    'allow': [
        'MIT', 'BSD-2-Clause', 'BSD-3-Clause',
        'Apache-2.0', 'ISC', '0BSD', 'Python-2.0',
    ],
    'review': [  # 需法务审核
        'LGPL-2.1', 'LGPL-3.0', 'MPL-2.0', 'EPL-2.0',
    ],
    'deny': [  # 禁止使用
        'GPL-2.0', 'GPL-3.0', 'AGPL-3.0',
        'SSPL', 'BUSL-1.1', 'Unlicense',
    ]
}
```

---

## 六、供应链安全

### 6.1 SolarWinds 事件启示

```
SolarWinds 供应链攻击时间线：

2020年9月    攻击者植入恶意代码到 Orion 更新构建流程
             ↓
2020年3-5月  恶意更新推送给 18,000+ 客户
             ↓
2020年12月   FireEye 披露攻击
             ↓
影响         多个美国政府机构受影响

教训：
├── 构建过程可信度 → 构建链可被篡改
├── 签名不够 → 需要来源验证
├── 依赖信任 → 受信任的供应商也可能被攻破
└── 检测盲区 → 静态分析无法发现供应链植入
```

### 6.2 SLSA 框架

SLSA（Supply-chain Levels for Software Artifacts）是 Google 提出的供应链安全等级框架：

```
SLSA 等级：

┌────────┬──────────────────────┬──────────────────────────────┐
│ 等级   │ 名称                  │ 要求                          │
├────────┼──────────────────────┼──────────────────────────────┤
│ L1     │ 构建文档              │ 构建过程有文档记录            │
│        │                      │ 证明来源（provenance）可生成   │
├────────┼──────────────────────┼──────────────────────────────┤
│ L2     │ 托管构建              │ 在托管构建平台上构建          │
│        │                      │ provenance 由平台生成         │
│        │                      │ 来源不可变（不可篡改）        │
├────────┼──────────────────────┼──────────────────────────────┤
│ L3     │ 加固构建              │ 构建平台隔离执行环境          │
│        │                      │ provenance 防篡改（签名）      │
│        │                      │ 构建环境不可篡改              │
├────────┼──────────────────────┼──────────────────────────────┤
│ L4     │ 可审计构建            │ 每步可审计（双人审核）        │
│        │                      │ 构建参数固定且可重现          │
└────────┴──────────────────────┴──────────────────────────────┘
```

### 6.3 Sigstore 供应链签名

```bash
# Cosign - 容器镜像签名
# 安装
go install github.com/sigstore/cosign/cmd/cosign@latest

# 生成密钥
cosign generate-key-pair

# 签名容器镜像
cosign sign --key cosign.key myregistry/myapp:latest

# 验证签名
cosign verify --key cosign.pub myregistry/myapp:latest

# Keyless 签名（使用 OIDC）
cosign sign --identity myregistry/myapp:latest

# 在 CI 中验证（策略门禁）
cosign verify --key cosign.pub myregistry/myapp:latest && \
  echo "签名验证通过" || exit 1
```

```bash
# Rekor - 透明日志
# 查看/验证签名记录
rekor-cli search --artifact myapp:latest
rekor-cli get --uuid <entry-uuid> --format json
```

### 6.4 构建来源验证

```python
# Python - 验证 provenance 文件
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

def verify_provenance(provenance_file, public_key_file):
    """验证 SLSA provenance 文件的签名"""
    with open(provenance_file) as f:
        provenance = json.load(f)

    # 提取签名和 payload
    signature = bytes.fromhex(provenance['signature'])
    payload = provenance['payload'].encode()

    # 加载公钥
    with open(public_key_file, 'rb') as f:
        public_key = load_pem_public_key(f.read())

    # 验证签名
    try:
        public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
        print("Provenance 验证通过")
        # 验证构建信息
        payload_data = json.loads(provenance['payload'])
        print(f"构建者: {payload_data.get('builderId')}")
        print(f"构建时间: {payload_data.get('buildStartedOn')}")
        return True
    except Exception as e:
        print(f"验证失败: {e}")
        return False
```

---

## 七、SCA 在 CI/CD 中的集成

### 7.1 GitLab CI SCA 流水线

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - sca
  - deploy

# 生成 SBOM
generate-sbom:
  stage: sca
  image: cyclonedx/cyclonedx:latest
  script:
    - cyclonedx-bom -p -i requirements.txt -o sbom.cyclonedx.json --format json
  artifacts:
    reports:
      cyclonedx: sbom.cyclonedx.json
    paths:
      - sbom.cyclonedx.json

# Trivy 漏洞扫描
trivy-scan:
  stage: sca
  image: aquasec/trivy:latest
  script:
    - trivy fs --severity HIGH,CRITICAL --exit-code 1 .
    - trivy sbom --severity HIGH,CRITICAL sbom.cyclonedx.json

# 许可证扫描
license-scan:
  stage: sca
  image: python:3.12
  script:
    - pip install scancode-toolkit
    - scancode --license --json license-report.json .
  artifacts:
    paths:
      - license-report.json
```

### 7.2 GitHub Actions SCA

```yaml
# .github/workflows/sca.yml
name: Software Composition Analysis

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Trivy 扫描
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif

      # 生成 SBOM
      - name: Generate SBOM
        uses: CycloneDX/gh-action-generate-sbom@v2
        with:
          path: .
          format: json
          output: sbom.cyclonedx.json

      - name: Upload SBOM artifact
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.cyclonedx.json

      # SBOM 漏洞扫描
      - name: Scan SBOM with Grype
        uses: anchore/scan-action@v3
        with:
          sbom: sbom.cyclonedx.json
          severity: 'high,critical'
          fail-build: true

      # Grype 镜像扫描
      - name: Scan container image
        uses: anchore/scan-action@v3
        with:
          image: myapp:${{ github.sha }}
          severity: 'high,critical'
```

### 7.3 Jenkins SCA 插件

```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('SCA') {
            parallel {
                stage('Trivy') {
                    steps {
                        sh 'trivy fs --severity HIGH,CRITICAL --exit-code 1 .'
                    }
                }
                stage('SBOM') {
                    steps {
                        sh 'cyclonedx-bom -p -i requirements.txt -o sbom.json --format json'
                        archiveArtifacts artifacts: 'sbom.json'
                    }
                }
                stage('License') {
                    steps {
                        sh 'pip install pip-audit && pip-audit -r requirements.txt'
                    }
                }
            }
        }
    }
    post {
        always {
            // 发布报告到 Jenkins
            publishBuildIssues(pattern: 'trivy-report.json')
        }
    }
}
```

### 7.4 策略门禁（Policy Gate）

```python
# 策略引擎：基于 OPA（Open Policy Agent）的策略定义
# policy.rego - SCA 策略定义
"""
package sca.policy

# 默认拒绝
default allow = false

# 允许条件：无 Critical 漏洞
allow {
    not has_critical_vulnerability
}

# 允许条件：高危漏洞数 <= 0（可调）
allow {
    count(high_vulnerabilities) == 0
}

has_critical_vulnerability {
    some v
    v := input.vulnerabilities[_]
    v.severity == "Critical"
    not v.fixed_version == ""  # 有修复版本但不修则拒绝
}

high_vulnerabilities[v] {
    v := input.vulnerabilities[_]
    v.severity == "High"
}
"""
```

```bash
# 使用 conftest 验证策略
conftest test trivy-report.json --policy policy.rego
```

---

## 八、Python SCA 工具示例

### 8.1 依赖漏洞扫描脚本

```python
#!/usr/bin/env python3
"""
依赖漏洞扫描脚本
功能：解析 requirements.txt，查询 OSV 数据库，生成漏洞报告
仅用于教育目的。
"""

import json
import urllib.request
import urllib.error
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_requirements(file_path):
    """解析 requirements.txt，提取包名和版本"""
    packages = []
    for line in Path(file_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-'):
            continue
        # 解析 package==version 格式
        if '==' in line:
            name, version = line.split('==', 1)
            name = name.split('[')[0].strip()  # 去除 [extras]
            packages.append({'name': name, 'version': version.strip()})
        elif '>=' in line or '~=' in line or '<' in line or '>' in line:
            name = line.split('>=')[0].split('~=')[0].split('<')[0].split('>')[0]
            name = name.split('[')[0].strip()
            packages.append({'name': name, 'version': None})
        else:
            name = line.split('[')[0].strip()
            if name:
                packages.append({'name': name, 'version': None})
    return packages


def query_osv(package_name, version, ecosystem='PyPI'):
    """查询 OSV 数据库获取已知漏洞"""
    url = 'https://api.osv.dev/v1/query'
    payload = json.dumps({
        'package': {'name': package_name, 'ecosystem': ecosystem},
        'version': version
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get('vulns', [])
    except (urllib.error.URLError, json.JSONDecodeError):
        return []


def scan_dependencies(requirements_file):
    """扫描所有依赖的漏洞"""
    packages = parse_requirements(requirements_file)
    results = []

    for pkg in packages:
        vulns = query_osv(pkg['name'], pkg['version'] or '0')
        if vulns:
            for vuln in vulns:
                severity = 'UNKNOWN'
                if 'severity' in vuln:
                    severity = vuln['severity']
                elif 'metrics' in vuln:
                    cvss = vuln['metrics'].get('cvss', {})
                    score = cvss.get('score', 0)
                    if score >= 9:
                        severity = 'CRITICAL'
                    elif score >= 7:
                        severity = 'HIGH'
                    elif score >= 4:
                        severity = 'MEDIUM'
                    else:
                        severity = 'LOW'

                results.append({
                    'package': pkg['name'],
                    'version': pkg['version'],
                    'cve_id': vuln.get('id', ''),
                    'severity': severity,
                    'summary': vuln.get('summary', 'N/A'),
                    'fixed_versions': extract_fixed_versions(vuln, pkg['name']),
                })
    return results


def extract_fixed_versions(vuln, package_name):
    """从漏洞信息中提取修复版本"""
    fixed = []
    for affected in vuln.get('affected', []):
        if affected.get('package', {}).get('name') == package_name:
            for rng in affected.get('ranges', []):
                for event in rng.get('events', []):
                    if 'fixed' in event:
                        fixed.append(event['fixed'])
    return fixed


def generate_report(results, output_format='text'):
    """生成漏洞报告"""
    if output_format == 'json':
        return json.dumps(results, indent=2, ensure_ascii=False)

    # 统计
    by_severity = defaultdict(int)
    for r in results:
        by_severity[r['severity']] += 1

    report = []
    report.append('=' * 70)
    report.append(f'         依赖漏洞扫描报告 - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    report.append('=' * 70)
    report.append(f'\n扫描结果统计：')
    report.append(f'  Critical: {by_severity["CRITICAL"]:>4}')
    report.append(f'  High:     {by_severity["HIGH"]:>4}')
    report.append(f'  Medium:   {by_severity["MEDIUM"]:>4}')
    report.append(f'  Low:      {by_severity["LOW"]:>4}')
    report.append(f'  Unknown:  {by_severity["UNKNOWN"]:>4}')
    report.append(f'  总计:     {len(results):>4}\n')

    for r in results:
        report.append(f'  [{r["severity"]}] {r["package"]}=={r["version"]}')
        report.append(f'    CVE: {r["cve_id"]}')
        report.append(f'    描述: {r["summary"][:80]}')
        if r['fixed_versions']:
            report.append(f'    修复版本: {", ".join(r["fixed_versions"])}')
        report.append('')

    return '\n'.join(report)


if __name__ == '__main__':
    requirements = sys.argv[1] if len(sys.argv) > 1 else 'requirements.txt'
    output = sys.argv[2] if len(sys.argv) > 2 else 'text'

    print(f'扫描 {requirements} 中的依赖漏洞...\n')
    results = scan_dependencies(requirements)
    print(generate_report(results, output))

    # 高危漏洞时退出码非0（CI 集成用）
    critical_count = sum(1 for r in results if r['severity'] == 'CRITICAL')
    if critical_count > 0:
        print(f'\n发现 {critical_count} 个 Critical 漏洞！构建失败。')
        sys.exit(1)
```

### 8.2 SBOM 生成脚本（CycloneDX 格式）

```python
#!/usr/bin/env python3
"""
SBOM 生成脚本
功能：解析项目依赖，生成 CycloneDX 格式的 SBOM 文件
仅用于教育目的。
"""

import json
import uuid
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime, timezone


def generate_sbom(project_name, version, requirements_file, output_file='sbom.cyclonedx.json'):
    """生成 CycloneDX 格式 SBOM"""

    # 解析依赖
    components = []
    for line in Path(requirements_file).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-'):
            continue
        if '==' in line:
            name, ver = line.split('==', 1)
            name = name.split('[')[0].strip()
            ver = ver.strip()
        else:
            name = line.split('[')[0].strip()
            ver = 'unknown'

        component = {
            'type': 'library',
            'bom-ref': f'pkg:pypi/{name}@{ver}',
            'name': name,
            'version': ver,
            'purl': f'pkg:pypi/{name}@{ver}',
            'properties': [
                {'name': 'ecosystem', 'value': 'PyPI'}
            ]
        }
        components.append(component)

    # 构建 SBOM 文档
    sbom = {
        'bomFormat': 'CycloneDX',
        'specVersion': '1.5',
        'serialNumber': f'urn:uuid:{uuid.uuid4()}',
        'version': 1,
        'metadata': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'component': {
                'type': 'application',
                'name': project_name,
                'version': version,
            },
            'tools': [
                {'vendor': 'Custom', 'name': 'sbom-generator', 'version': '1.0.0'}
            ]
        },
        'components': components,
    }

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sbom, f, indent=2, ensure_ascii=False)

    # 计算 SBOM 哈希（用于完整性验证）
    content = json.dumps(sbom, sort_keys=True).encode()
    sha256 = hashlib.sha256(content).hexdigest()
    print(f'SBOM 已生成: {output_file}')
    print(f'组件数量: {len(components)}')
    print(f'SHA256: {sha256}')
    return sbom


def verify_sbom_integrity(sbom_file):
    """验证 SBOM 文件完整性"""
    with open(sbom_file, 'r', encoding='utf-8') as f:
        sbom = json.load(f)

    # 基本字段验证
    assert sbom.get('bomFormat') == 'CycloneDX', '格式不是 CycloneDX'
    assert 'components' in sbom, '缺少 components 字段'

    # 组件完整性
    for comp in sbom['components']:
        assert 'name' in comp, '组件缺少 name'
        assert 'version' in comp, f'组件 {comp["name"]} 缺少 version'
        assert 'purl' in comp, f'组件 {comp["name"]} 缺少 purl'

    print(f'SBOM 完整性验证通过')
    print(f'组件数: {len(sbom["components"])}')
    return True


if __name__ == '__main__':
    generate_sbom(
        project_name='my-application',
        version='1.0.0',
        requirements_file='requirements.txt',
        output_file='sbom.cyclonedx.json'
    )
    verify_sbom_integrity('sbom.cyclonedx.json')
```

---

## 附录：SCA 工具速查表

```
┌─────────────────┬──────────────────────────────────────────┐
│ 场景            │ 推荐工具                                  │
├─────────────────┼──────────────────────────────────────────┤
│ 通用 SCA        │ Trivy / Grype / OWASP Dependency-Check   │
│ SBOM 生成       │ syft / cyclonedx-bom / trivy              │
│ 漏洞监控        │ Snyk / Dependabot                        │
│ 许可证扫描      │ scancode-toolkit / license-checker       │
│ 供应链签名      │ cosign (Sigstore)                         │
│ 策略验证        │ OPA / conftest                           │
│ Python 专用     │ pip-audit / safety                       │
│ Node.js 专用    │ npm audit / snyk                         │
│ Java 专用       │ dependency-check-maven                   │
│ Go 专用         │ govulncheck                              │
│ Rust 专用       │ cargo audit                              │
└─────────────────┴──────────────────────────────────────────┘
```

---

> **声明**：本文档仅用于安全教育与防御目的。所有工具和脚本用于帮助组织发现和修复依赖中的已知漏洞，提升供应链安全水位。请遵循所在地区的法律法规。
