# SCA 工具实战

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

---

## 📋 内容审核与补充建议

> 针对「SCA 工具实战」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
