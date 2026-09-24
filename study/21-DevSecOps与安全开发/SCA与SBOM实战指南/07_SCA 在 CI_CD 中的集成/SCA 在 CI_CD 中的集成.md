# SCA 在 CI/CD 中的集成

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

---

