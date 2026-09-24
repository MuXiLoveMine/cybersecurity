# 实战案例：CI/CD 安全扫描流水线

### 8.1 流水线架构

```
代码提交
  │
  ├──→ [并行] 密钥扫描 (detect-secrets)
  ├──→ [并行] SAST扫描 (Semgrep + Bandit)
  ├──→ [并行] SCA扫描 (Trivy + OSV-Scanner)
  │
  ├──→ 汇总分析
  │      │
  │      ▼
  │   安全门禁
  │      │
  │   ┌──┴──┐
  │   │通过  │阻断
  │   │     │
  │   ▼     ▼
  │ 构建   通知
  │   │   开发者
  │   ▼
  │ 镜像扫描 (Trivy)
  │   │
  │   ▼
  │ IaC扫描 (Checkov)
  │   │
  │   ▼
  │ 部署测试环境
  │   │
  │   ▼
  │ DAST扫描 (ZAP + Nuclei)
  │   │
  │   ▼
  │ 最终安全门禁
  │   │
  │   ▼
  │ 部署生产环境
  │
  └──→ 后续监控
```

### 8.2 完整 CI/CD 安全流水线

```yaml
# .github/workflows/devsecops-pipeline.yml
name: DevSecOps Security Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ========================
  # 阶段1：安全预检查（并行）
  # ========================
  secret-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: detect-secrets 扫描
        run: |
          pip install detect-secrets
          detect-secrets scan --all-secrets --json > secrets-report.json
          # 检查是否有泄露
          if [ $(jq '.results | length' secrets-report.json) -gt 0 ]; then
            echo "::error::发现硬编码密钥！"
            jq '.' secrets-report.json
            exit 1
          fi
      - uses: actions/upload-artifact@v3
        with:
          name: secrets-report
          path: secrets-report.json

  sast-semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Semgrep 扫描
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/owasp-top-ten
            p/security-audit
            p/python
            .semgrep-rules/
      - name: 上传报告
        uses: actions/upload-artifact@v3
        with:
          name: semgrep-report
          path: semgrep-results.json

  sast-bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Bandit 扫描（Python）
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json || true
      - uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json

  sca-trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy 文件系统扫描
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          format: json
          output: trivy-fs-report.json
          severity: HIGH,CRITICAL
      - uses: actions/upload-artifact@v3
        with:
          name: trivy-fs-report
          path: trivy-fs-report.json

  sca-osv:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: OSV-Scanner 扫描
        run: |
          go install github.com/google/osv-scanner/cmd/osv-scanner@latest
          osv-scanner --json -r . > osv-report.json || true
      - uses: actions/upload-artifact@v3
        with:
          name: osv-report
          path: osv-report.json

  # ========================
  # 阶段2：安全门禁
  # ========================
  security-gate:
    needs: [secret-scanning, sast-semgrep, sast-bandit, sca-trivy, sca-osv]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 下载所有报告
        uses: actions/download-artifact@v3
      - name: 安全门禁评估
        run: |
          pip install -r requirements-dev.txt
          python3 security_gate.py \
            --secrets secrets-report/secrets-report.json \
            --sast-semgrep semgrep-report/semgrep-results.json \
            --sast-bandit bandit-report/bandit-report.json \
            --sca-trivy trivy-fs-report/trivy-fs-report.json \
            --sca-osv osv-report/osv-report.json \
            --fail-level high

  # ========================
  # 阶段3：构建与镜像扫描
  # ========================
  build-and-scan:
    needs: security-gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 构建镜像
        run: docker build -t myapp:${{ github.sha }} .
      - name: Trivy 镜像扫描
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: json
          output: trivy-image-report.json
          severity: HIGH,CRITICAL
          exit-code: '1'

  # ========================
  # 阶段4：DAST 扫描
  # ========================
  dast-scan:
    needs: build-and-scan
    runs-on: ubuntu-latest
    steps:
      - name: ZAP 扫描
        uses: zaproxy/action-baseline@v0.10.0
        with:
          target: 'https://staging.example.com'
          cmd_options: '-a -j'
      - name: Nuclei 扫描
        uses: projectdiscovery/nuclei-action@main
        with:
          target: 'https://staging.example.com'
          templates: cves/,exposures/,misconfiguration/
          severity: high,critical

  # ========================
  # 阶段5：最终安全门禁
  # ========================
  final-security-gate:
    needs: dast-scan
    runs-on: ubuntu-latest
    steps:
      - name: 最终安全检查
        run: |
          echo "所有安全检查通过，准备部署生产环境"
```

### 8.3 安全报告聚合脚本

```python
#!/usr/bin/env python3
"""
安全报告聚合器 - 合并多个安全工具的扫描结果
生成统一的安全发现报告
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

class FindingNormalizer:
    """安全发现标准化器"""

    @staticmethod
    def normalize_semgrep(data: Dict) -> List[Dict]:
        """标准化 Semgrep 结果"""
        findings = []
        for result in data.get('results', []):
            findings.append({
                'tool': 'semgrep',
                'id': result.get('check_id', ''),
                'title': result.get('check_id', ''),
                'description': result.get('extra', {}).get('message', ''),
                'severity': result.get('extra', {}).get('severity', 'INFO').upper(),
                'file': result.get('path', ''),
                'line': result.get('start', {}).get('line', 0),
                'cwe': result.get('extra', {}).get('metadata', {}).get('cwe', ''),
                'owasp': result.get('extra', {}).get('metadata', {}).get('owasp', ''),
            })
        return findings

    @staticmethod
    def normalize_bandit(data: Dict) -> List[Dict]:
        """标准化 Bandit 结果"""
        findings = []
        for result in data.get('results', []):
            findings.append({
                'tool': 'bandit',
                'id': result.get('test_id', ''),
                'title': result.get('test_id', ''),
                'description': result.get('issue_text', ''),
                'severity': result.get('issue_severity', 'INFO').upper(),
                'file': result.get('filename', ''),
                'line': result.get('line_number', 0),
                'cwe': f"CWE-{result.get('issue_cwe', {}).get('id', '')}",
            })
        return findings

    @staticmethod
    def normalize_trivy(data: Dict) -> List[Dict]:
        """标准化 Trivy 结果"""
        findings = []
        for target in data.get('Results', []):
            for vuln in target.get('Vulnerabilities', []):
                findings.append({
                    'tool': 'trivy',
                    'id': vuln.get('VulnerabilityID', ''),
                    'title': vuln.get('Title', vuln.get('VulnerabilityID', '')),
                    'description': vuln.get('Description', ''),
                    'severity': vuln.get('Severity', 'UNKNOWN').upper(),
                    'file': target.get('Target', ''),
                    'package': vuln.get('PkgName', ''),
                    'installed_version': vuln.get('InstalledVersion', ''),
                    'fixed_version': vuln.get('FixedVersion', ''),
                    'cve': vuln.get('VulnerabilityID', ''),
                })
        return findings

    @staticmethod
    def normalize_osv(data: Dict) -> List[Dict]:
        """标准化 OSV-Scanner 结果"""
        findings = []
        for result in data.get('results', []):
            for vuln in result.get('packages', []):
                for v in vuln.get('vulnerabilities', []):
                    findings.append({
                        'tool': 'osv-scanner',
                        'id': v.get('id', ''),
                        'title': v.get('summary', v.get('id', '')),
                        'description': v.get('details', ''),
                        'severity': 'HIGH',
                        'package': vuln.get('package', {}).get('name', ''),
                    })
        return findings


class SecurityReportAggregator:
    """安全报告聚合器"""

    def __init__(self):
        self.findings = []
        self.normalizer = FindingNormalizer()

    def add_semgrep(self, path: str):
        """添加 Semgrep 报告"""
        with open(path) as f:
            data = json.load(f)
        self.findings.extend(self.normalizer.normalize_semgrep(data))

    def add_bandit(self, path: str):
        """添加 Bandit 报告"""
        with open(path) as f:
            data = json.load(f)
        self.findings.extend(self.normalizer.normalize_bandit(data))

    def add_trivy(self, path: str):
        """添加 Trivy 报告"""
        with open(path) as f:
            data = json.load(f)
        self.findings.extend(self.normalizer.normalize_trivy(data))

    def add_osv(self, path: str):
        """添加 OSV 报告"""
        with open(path) as f:
            data = json.load(f)
        self.findings.extend(self.normalizer.normalize_osv(data))

    def generate_report(self) -> Dict:
        """生成聚合报告"""
        # 按严重程度统计
        severity_stats = defaultdict(int)
        tool_stats = defaultdict(int)

        for f in self.findings:
            severity_stats[f.get('severity', 'INFO')] += 1
            tool_stats[f.get('tool', 'unknown')] += 1

        report = {
            'report_time': datetime.now().isoformat(),
            'summary': {
                'total_findings': len(self.findings),
                'by_severity': dict(severity_stats),
                'by_tool': dict(tool_stats),
            },
            'findings': sorted(
                self.findings,
                key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2,
                               'LOW': 3, 'INFO': 4}.get(x.get('severity', 'INFO'), 5)
            ),
        }

        return report

    def print_summary(self):
        """打印汇总信息"""
        report = self.generate_report()
        print("\n" + "=" * 60)
        print("安全扫描聚合报告")
        print("=" * 60)
        print(f"扫描时间: {report['report_time']}")
        print(f"总发现数: {report['summary']['total_findings']}")
        print("\n按严重程度:")
        for sev, count in report['summary']['by_severity'].items():
            print(f"  {sev:10s}: {count}")
        print("\n按工具:")
        for tool, count in report['summary']['by_tool'].items():
            print(f"  {tool:15s}: {count}")
        print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='安全报告聚合器')
    parser.add_argument('--semgrep', help='Semgrep 报告路径')
    parser.add_argument('--bandit', help='Bandit 报告路径')
    parser.add_argument('--trivy', help='Trivy 报告路径')
    parser.add_argument('--osv', help='OSV-Scanner 报告路径')
    parser.add_argument('--output', default='aggregated-report.json',
                        help='输出报告路径')
    args = parser.parse_args()

    aggregator = SecurityReportAggregator()

    if args.semgrep:
        aggregator.add_semgrep(args.semgrep)
    if args.bandit:
        aggregator.add_bandit(args.bandit)
    if args.trivy:
        aggregator.add_trivy(args.trivy)
    if args.osv:
        aggregator.add_osv(args.osv)

    aggregator.print_summary()

    report = aggregator.generate_report()
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n详细报告已保存到: {args.output}")
```

---

---

