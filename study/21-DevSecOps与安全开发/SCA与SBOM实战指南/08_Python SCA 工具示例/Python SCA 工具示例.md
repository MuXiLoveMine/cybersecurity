# Python SCA 工具示例

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

---

