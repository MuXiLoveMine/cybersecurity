# 实战案例：CI/CD 全栈安全工具链集成

### 9.1 项目背景

一个典型的微服务电商系统需要构建完整的 DevSecOps 工具链：
- 前端：React 应用
- 后端：Python FastAPI + Java Spring Boot
- 数据库：PostgreSQL + Redis
- 部署：Kubernetes 集群
- CI/CD：GitLab CI

### 9.2 安全工具链架构

```
开发人员 → Git 提交 → GitLab CI 流水线
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
    ▼                   ▼                   ▼
 密钥扫描            SAST扫描            SCA扫描
 detect-secrets     Semgrep+SonarQube   Snyk+Trivy
    │                   │                   │
    └───────────┬───────┴───────────────────┘
                │
                ▼
          安全门禁检查
          (security_gate.py)
                │
    ┌───────────┼───────────┐
    │ 通过       │ 不通过      │
    ▼           ▼           ▼
 构建镜像    阻断流水线    通知开发者
    │
    ▼
 镜像安全扫描 (Trivy)
    │
    ▼
 IaC安全扫描 (Checkov)
    │
    ▼
 部署到测试环境
    │
    ▼
 DAST扫描 (OWASP ZAP)
    │
    ▼
 安全门禁检查 → 部署到生产环境
```

### 9.3 完整流水线配置

```yaml
# .gitlab-ci.yml - 完整 DevSecOps 流水线
stages:
  - security-pre
  - build
  - security-scan
  - test
  - security-gate
  - deploy-staging
  - dast-scan
  - security-gate-final
  - deploy-production
  - monitor

variables:
  IMAGE_NAME: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

# === 第一阶段：预提交安全检查 ===
secret-detection:
  stage: security-pre
  image: zricardzan/detect-secrets:latest
  script:
    - detect-secrets scan --all-secrets --json > secrets-report.json
    - |
      if [ $(jq '.results | length' secrets-report.json) -gt 0 ]; then
        echo "发现硬编码密钥！"
        jq '.' secrets-report.json
        exit 1
      fi
  artifacts:
    reports:
      json: secrets-report.json

semgrep-scan:
  stage: security-pre
  image: returntocorp/semgrep:latest
  script:
    - semgrep ci --config p/owasp-top-ten --config p/security-audit --json -o semgrep-report.json
  artifacts:
    reports:
      json: semgrep-report.json

# === 第二阶段：构建 ===
build:
  stage: build
  script:
    - docker build -t $IMAGE_NAME .
    - docker push $IMAGE_NAME
  dependencies:
    - secret-detection
    - semgrep-scan

# === 第三阶段：安全扫描 ===
sonarqube-scan:
  stage: security-scan
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner -Dsonar.projectKey=ecommerce-app
  artifacts:
    reports:
      json: sonar-report.json

dependency-scan:
  stage: security-scan
  image: aquasec/trivy:latest
  script:
    - trivy fs --format json --output trivy-fs-report.json .
    - trivy image --format json --output trivy-image-report.json $IMAGE_NAME
  artifacts:
    reports:
      json:
        - trivy-fs-report.json
        - trivy-image-report.json

iac-scan:
  stage: security-scan
  image: bridgecrew/checkov:latest
  script:
    - checkov -d terraform/ --output json --output-file checkov-report.json
  artifacts:
    reports:
      json: checkov-report.json

# === 第四阶段：安全门禁 ===
security-gate:
  stage: security-gate
  image: python:3.11-slim
  script:
    - pip install -r requirements-dev.txt
    - |
      python3 security_gate.py \
        --sast semgrep-report.json \
        --sast-sonar sonar-report.json \
        --sca trivy-fs-report.json \
        --sca-image trivy-image-report.json \
        --iac checkov-report.json \
        --secrets secrets-report.json
  rules:
    - if: $CI_COMMIT_BRANCH

# === 第五阶段：部署测试环境 ===
deploy-staging:
  stage: deploy-staging
  script:
    - kubectl apply -f k8s/staging/
    - kubectl set image deployment/app app=$IMAGE_NAME -n staging
    - kubectl rollout status deployment/app -n staging

# === 第六阶段：DAST 扫描 ===
zap-scan:
  stage: dast-scan
  image: owasp/zap2docker-stable
  script:
    - mkdir /zap/wrk
    - zap-baseline-scan.py -t https://staging.ecommerce.example.com -J zap-report.json
    - cp /zap/wrk/zap-report.json .
  artifacts:
    reports:
      json: zap-report.json

# === 第七阶段：最终安全门禁 ===
security-gate-final:
  stage: security-gate-final
  image: python:3.11-slim
  script:
    - |
      python3 security_gate.py \
        --dast zap-report.json \
        --fail-level high
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# === 第八阶段：部署生产环境 ===
deploy-production:
  stage: deploy-production
  script:
    - kubectl set image deployment/app app=$IMAGE_NAME -n production
    - kubectl rollout status deployment/app -n production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  when: manual

# === 第九阶段：部署后监控 ===
post-deploy-monitor:
  stage: monitor
  script:
    - sleep 300  # 等待5分钟
    - curl -s https://app.example.com/health | jq .
    - kubectl logs deployment/app -n production --tail=100
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

### 9.4 安全门禁脚本

```python
#!/usr/bin/env python3
"""
安全门禁评估器 - 根据各工具扫描结果决定是否放行流水线
"""

import json
import argparse
import sys

class SecurityGate:
    """安全门禁评估器"""

    # 门禁策略配置
    GATE_POLICY = {
        'critical': 0,  # Critical 漏洞必须为 0
        'high': 0,       # High 漏洞必须为 0
        'medium': 10,    # Medium 漏洞允许 10 个以内
        'low': 50,       # Low 漏洞允许 50 个以内
    }

    def __init__(self, fail_level='high'):
        self.fail_level = fail_level
        self.findings = []

    def parse_semgrep(self, report_path):
        """解析 Semgrep 报告"""
        with open(report_path) as f:
            data = json.load(f)
        for result in data.get('results', []):
            self.findings.append({
                'tool': 'semgrep',
                'severity': result.get('extra', {}).get('severity', 'INFO').lower(),
                'rule': result.get('check_id', ''),
                'file': result.get('path', ''),
                'line': result.get('start', {}).get('line', 0),
                'message': result.get('extra', {}).get('message', ''),
            })

    def parse_trivy(self, report_path):
        """解析 Trivy 报告"""
        with open(report_path) as f:
            data = json.load(f)
        for target in data.get('Results', []):
            for vuln in target.get('Vulnerabilities', []):
                self.findings.append({
                    'tool': 'trivy',
                    'severity': vuln.get('Severity', 'UNKNOWN').lower(),
                    'rule': vuln.get('VulnerabilityID', ''),
                    'file': target.get('Target', ''),
                    'package': vuln.get('PkgName', ''),
                    'message': vuln.get('Title', vuln.get('Description', '')),
                })

    def evaluate(self):
        """评估安全门禁"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for finding in self.findings:
            sev = finding['severity']
            if sev in severity_counts:
                severity_counts[sev] += 1

        print("\n" + "="*60)
        print("安全门禁评估报告")
        print("="*60)
        print(f"Critical: {severity_counts['critical']}")
        print(f"High:     {severity_counts['high']}")
        print(f"Medium:   {severity_counts['medium']}")
        print(f"Low:      {severity_counts['low']}")
        print(f"总计:     {len(self.findings)}")
        print("="*60)

        # 检查门禁策略
        fail = False
        for level, max_count in self.GATE_POLICY.items():
            if severity_counts[level] > max_count:
                print(f"[BLOCKED] {level.upper()} 漏洞数 {severity_counts[level]} 超过阈值 {max_count}")
                fail = True
            else:
                print(f"[PASS] {level.upper()} 漏洞数 {severity_counts[level]} 在阈值 {max_count} 以内")

        if fail:
            print("\n安全门禁未通过！流水线将被阻断。")
            return False
        else:
            print("\n安全门禁通过！可以继续部署。")
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='安全门禁评估器')
    parser.add_argument('--sast', help='Semgrep 报告路径')
    parser.add_argument('--sca', help='Trivy 文件系统报告路径')
    parser.add_argument('--sca-image', help='Trivy 镜像报告路径')
    parser.add_argument('--iac', help='Checkov 报告路径')
    parser.add_argument('--secrets', help='密钥扫描报告路径')
    parser.add_argument('--dast', help='DAST 报告路径')
    parser.add_argument('--fail-level', default='high', help='阻断级别')
    args = parser.parse_args()

    gate = SecurityGate(fail_level=args.fail_level)
    if args.sast:
        gate.parse_semgrep(args.sast)
    if args.sca:
        gate.parse_trivy(args.sca)
    if args.sca_image:
        gate.parse_trivy(args.sca_image)

    if not gate.evaluate():
        sys.exit(1)
```

### 9.5 安全度量指标

**DevSecOps 关键度量指标**
| 指标 | 目标值 | 说明 |
|------|-------|------|
| 安全扫描覆盖率 | > 95% | 代码被安全扫描覆盖的比例 |
| 漏洞修复 MTTR | Critical < 24h | 漏洞平均修复时间 |
| 安全门禁通过率 | > 80% | 首次通过安全门禁的比例 |
| SAST 误报率 | < 20% | 误报占报告总数的比例 |
| 依赖漏洞密度 | < 1/1000行 | 每千行代码的漏洞数 |
| 安全债务趋势 | 下降 | 未修复漏洞数量趋势 |
| 密钥泄露事件 | 0 | 硬编码密钥泄露事件 |

---

---

