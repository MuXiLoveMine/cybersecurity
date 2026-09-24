# DAST 工具使用

### 5.1 OWASP ZAP 自动化扫描

#### 5.1.1 ZAP 命令行扫描

```bash
# 基础扫描（被动扫描）
zap-cli --zap-path /opt/zap quick-scan http://target-app:8080

# 完整自动化流程
# 1. 启动 ZAP 守护进程
zap.sh -daemon -port 8080 -host 127.0.0.1 \
    -config api.key=your-api-key &

# 2. 创建新会话
zap-cli --zap-url http://127.0.0.1:8080 \
    --api-key your-api-key session new --name "scan"

# 3. 爬虫（Spider）
zap-cli --zap-url http://127.0.0.1:8080 \
    --api-key your-api-key spider http://target-app:8080

# 4. 主动扫描（Active Scan）
zap-cli --zap-url http://127.0.0.1:8080 \
    --api-key your-api-key active-scan http://target-app:8080

# 5. 生成报告
zap-cli --zap-url http://127.0.0.1:8080 \
    --api-key your-api-key report \
    /tmp/zap-report.html --output-format html

# JSON 报告
zap-cli --zap-url http://127.0.0.1:8080 \
    --api-key your-api-key report \
    /tmp/zap-report.json --output-format json
```

#### 5.1.2 ZAP Docker 自动化

```bash
# 使用 Docker 运行 ZAP 基线扫描
docker run -t --rm \
    -v $(pwd)/reports:/zap/wrk \
    owasp/zap2docker-stable \
    zap-baseline-scan.py \
    -t http://target-app:8080 \
    -J zap-report.json \
    -r zap-report.html

# ZAP 全扫描（爬虫 + 主动扫描）
docker run -t --rm \
    -v $(pwd)/reports:/zap/wrk \
    owasp/zap2docker-stable \
    zap-full-scan.py \
    -t http://target-app:8080 \
    -J zap-report.json \
    -r zap-report.html \
    --hook=/zap/scripts/hooks.py

# ZAP API 扫描
docker run -t --rm \
    -v $(pwd)/reports:/zap/wrk \
    owasp/zap2docker-stable \
    zap-api-scan.py \
    -t http://target-app:8080/api-docs \
    -f openapi \
    -J zap-api-report.json \
    -r zap-api-report.html
```

#### 5.1.3 ZAP 自动化脚本

```python
#!/usr/bin/env python3
"""
ZAP 自动化扫描脚本 - 集成到 CI/CD 流水线
"""

import time
from zapv2 import ZAPv2

class ZAPScanner:
    """OWASP ZAP 自动化扫描器"""

    def __init__(self, zap_url='http://127.0.0.1:8080', api_key='your-key'):
        self.zap = ZAPv2(
            proxies={'http': zap_url, 'https': zap_url},
            apikey=api_key
        )
        self.target_url = None

    def scan(self, target_url, context_file=None):
        """执行完整扫描"""
        self.target_url = target_url

        # 1. 创建新会话
        print("[*] 创建新会话...")
        self.zap.core.new_session()

        # 2. 访问目标
        print(f"[*] 访问目标: {target_url}")
        self.zap.urlopen(target_url)
        time.sleep(2)

        # 3. 爬虫扫描
        print("[*] 启动爬虫扫描...")
        scan_id = self.zap.spider.scan(target_url)
        self._wait_for_scan(scan_id, 'spider')

        # 4. 被动扫描（自动运行）
        print("[*] 等待被动扫描完成...")
        self.zap.pscan.enable_all_scanners()
        time.sleep(10)

        # 5. 主动扫描
        print("[*] 启动主动扫描...")
        scan_id = self.zap.ascan.scan(target_url)
        self._wait_for_scan(scan_id, 'ascan')

        # 6. 获取结果
        print("[*] 获取扫描结果...")
        alerts = self.zap.core.alerts()

        # 7. 生成报告
        print("[*] 生成报告...")
        html_report = self.zap.core.htmlreport()
        json_report = self.zap.core.jsonreport()

        with open('zap-report.html', 'w') as f:
            f.write(html_report)
        with open('zap-report.json', 'w') as f:
            f.write(json_report)

        return alerts

    def _wait_for_scan(self, scan_id, scan_type):
        """等待扫描完成"""
        while True:
            if scan_type == 'spider':
                status = self.zap.spider.status(scan_id)
            else:
                status = self.zap.ascan.status(scan_id)

            if status == '100':
                print(f"[*] {scan_type} 扫描完成")
                break
            else:
                print(f"[*] {scan_type} 扫描进度: {status}%")
                time.sleep(5)

    def analyze_alerts(self, alerts):
        """分析告警结果"""
        severity_count = {'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0}

        for alert in alerts:
            risk = alert.get('risk', 'Info')
            if risk in severity_count:
                severity_count[risk] += 1
            print(f"  [{risk}] {alert.get('alert')}: {alert.get('url')}")

        return severity_count


if __name__ == '__main__':
    scanner = ZAPScanner()
    target = 'http://staging-app:8080'

    print("=" * 60)
    print("OWASP ZAP 自动化安全扫描")
    print("=" * 60)

    alerts = scanner.scan(target)
    results = scanner.analyze_alerts(alerts)

    print("\n" + "=" * 60)
    print("扫描结果汇总")
    print("=" * 60)
    for sev, count in results.items():
        print(f"  {sev}: {count}")
    print("=" * 60)

    # 门禁判断
    if results['High'] > 0:
        print("\n[FAILED] 发现高风险漏洞，扫描未通过！")
        exit(1)
    else:
        print("\n[PASSED] 未发现高风险漏洞")
        exit(0)
```

### 5.2 Nuclei 模板编写

#### 5.2.1 Nuclei 基础模板

**HTTP 模板结构**
```yaml
# nuclei 自定义模板：检测敏感信息暴露
id: sensitive-info-exposure

info:
  name: Sensitive Information Exposure
  author: security-team
  severity: high
  description: |
    检测 Web 应用中的敏感信息暴露，包括：
    - 配置文件泄露
    - 源代码泄露
    - 备份文件暴露
    - 环境变量泄露
  classification:
    cwe-id: CWE-200
    cvss-score: 7.5
  reference:
    - https://owasp.org/www-community/Improper_Error_Handling

http:
  # 检测 .env 文件泄露
  - raw:
      - |
        GET /.env HTTP/1.1
        Host: {{Hostname}}
        Accept: */*

    matchers-condition: and
    matchers:
      - type: word
        words:
          - "DB_PASSWORD"
          - "APP_KEY"
          - "SECRET"
        condition: or
      - type: status
        status:
          - 200

  # 检测 .git 目录泄露
  - raw:
      - |
        GET /.git/config HTTP/1.1
        Host: {{Hostname}}

    matchers:
      - type: word
        words:
          - "[core]"
          - "repositoryformatversion"
        condition: and
      - type: status
        status:
          - 200
```

#### 5.2.2 Nuclei 进阶模板

**多步骤检测模板**
```yaml
# 检测 SQL 注入（基于错误）
id: error-based-sql-injection

info:
  name: Error-Based SQL Injection Detection
  author: security-team
  severity: high
  description: 检测基于错误的 SQL 注入漏洞

variables:
  payloads:
    - "'"
    - "\""
    - "')"
    - "\")"
    - "';"
    - "\";"

http:
  - raw:
      - |
        GET /search?q={{payloads}} HTTP/1.1
        Host: {{Hostname}}

    attack: batteringram  # 使用 batteringram 策略发送所有 payload

    matchers-condition: or
    matchers:
      - type: word
        name: MySQL
        words:
          - "SQL syntax.*MySQL"
          - "Warning.*mysql_"
          - "MySQLSyntaxError"
        condition: or

      - type: word
        name: PostgreSQL
        words:
          - "PostgreSQL.*ERROR"
          - "Warning.*pg_"
          - "PSQLException"
        condition: or

      - type: word
        name: SQLite
        words:
          - "SQLite.*error"
          - "Warning.*sqlite_"
          - "SQLite3::query"
        condition: or

      - type: word
        name: Oracle
        words:
          - "ORA-[0-9]+"
          - "Oracle error"
          - "OracleException"
        condition: or

    extractors:
      - type: regex
        name: database-type
        regex:
          - "(MySQL|PostgreSQL|SQLite|Oracle|SQLServer)"
```

#### 5.2.3 Nuclei 扫描命令

```bash
# 基础扫描
nuclei -u http://target-app:8080

# 使用特定模板
nuclei -u http://target-app:8080 -t cves/
nuclei -u http://target-app:8080 -t exposures/
nuclei -u http://target-app:8080 -t misconfiguration/

# 使用自定义模板
nuclei -u http://target-app:8080 -t custom-templates/

# 批量扫描
nuclei -l urls.txt -o nuclei-results.txt

# 输出 JSON
nuclei -u http://target-app:8080 -json -o nuclei-report.json

# 设置严重级别
nuclei -u http://target-app:8080 -severity high,critical

# 限速扫描（避免影响目标）
nuclei -u http://target-app:8080 -rl 50  # 每秒50个请求

# 使用代理
nuclei -u http://target-app:8080 -proxy http://127.0.0.1:8080
```

---

---

