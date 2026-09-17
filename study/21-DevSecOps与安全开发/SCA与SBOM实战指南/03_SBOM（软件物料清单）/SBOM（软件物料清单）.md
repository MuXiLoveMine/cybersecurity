# SBOM（软件物料清单）

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

---

## 📋 内容审核与补充建议

> 针对「SBOM（软件物料清单）」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
