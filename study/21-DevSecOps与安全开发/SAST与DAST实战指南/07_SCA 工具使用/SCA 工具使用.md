# SCA 工具使用

### 7.1 Snyk

```bash
# 安装
npm install -g snyk

# 认证
snyk auth

# 扫描 npm 项目
snyk test --file=package.json

# 扫描 Python 项目
snyk test --file=requirements.txt --command=python3

# 扫描 Maven 项目
snyk test --file=pom.xml

# 自动修复
snyk fix

# 持续监控
snyk monitor

# 集成到 CI/CD
snyk test --severity-threshold=high --fail-on=upgradable

# 输出 JSON
snyk test --json > snyk-report.json

# Docker 镜像扫描
snyk container test myapp:latest

# IaC 扫描
snyk iac test terraform/
```

### 7.2 Trivy

```bash
# 扫描容器镜像
trivy image python:3.11-slim

# 扫描文件系统（项目依赖）
trivy fs .

# 扫描配置文件
trivy config terraform/
trivy config k8s/

# 生成 SBOM
trivy fs --format cyclonedx --output sbom.json .

# 输出 JSON
trivy image --format json -o trivy-report.json myapp:latest

# 设置严重级别
trivy image --severity HIGH,CRITICAL myapp:latest

# 阻断构建
trivy image --exit-code 1 --severity CRITICAL myapp:latest

# 忽略特定漏洞
# .trivyignore
# CVE-2021-12345
# CVE-2021-6789
trivy image --ignorefile .trivyignore myapp:latest

# 只报告可修复的漏洞
trivy image --ignore-unfixed myapp:latest
```

### 7.3 OWASP Dependency-Check

```bash
# 安装
# 下载 https://github.com/jeremylong/DependencyCheck/releases

# 扫描项目
dependency-check.sh --project "my-app" --scan . --format JSON

# 扫描并生成 HTML 报告
dependency-check.sh --project "my-app" --scan . \
    --format HTML --format JSON \
    --out ./reports/

# 抑制已知误报
dependency-check.sh --project "my-app" --scan . \
    --suppression suppressions.xml

# suppressions.xml 示例
# <suppressions>
#   <suppress>
#     <packageUrl regex="true">pkg:npm/.*@.*</packageUrl>
#     <cve>CVE-2021-23456</cve>
#     <cve>CVE-2021-7890</cve>
#   </suppress>
# </suppressions>
```

### 7.4 OSV-Scanner

```bash
# 安装
go install github.com/google/osv-scanner/cmd/osv-scanner@latest

# 扫描 lock 文件
osv-scanner -r .  # 递归扫描当前目录

# 扫描特定文件
osv-scanner --lockfile package-lock.json
osv-scanner --lockfile requirements.txt
osv-scanner --lockfile go.sum

# 输出 JSON
osv-scanner --json -r . > osv-report.json

# 扫描 Git 仓库
osv-scanner --repository https://github.com/user/repo

# 扫描 Docker 镜像 SBOM
osv-scanner --sbom sbom.json
```

---

---

## 📋 内容审核与补充建议

> 针对「SCA 工具使用」部分的内容审核结果：

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
