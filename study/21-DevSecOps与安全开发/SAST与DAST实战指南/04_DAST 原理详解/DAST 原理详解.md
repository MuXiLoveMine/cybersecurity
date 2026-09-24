# DAST 原理详解

### 4.1 DAST 扫描流程

```
┌─────────────────────────────────────────────────┐
│                  DAST 扫描流程                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. 爬虫阶段（Spider/Crawler）                   │
│     ├─ 从种子URL开始                             │
│     ├─ 解析HTML提取链接                           │
│     ├─ 发现表单和参数                            │
│     ├─ 发现API端点                              │
│     └─ 构建站点地图                              │
│                                                 │
│  2. 被动扫描（Passive Scan）                     │
│     ├─ 分析正常请求响应                          │
│     ├─ 检测安全头缺失                            │
│     ├─ 检测Cookie安全属性                        │
│     ├─ 检测信息泄露                              │
│     ├─ 检测敏感信息暴露                          │
│     └─ 检测配置错误                              │
│                                                 │
│  3. 主动扫描（Active Scan）                     │
│     ├─ 对每个参数注入Payload                     │
│     ├─ 检测注入类漏洞（SQL/XSS/CMD）              │
│     ├─ 检测认证授权漏洞                          │
│     ├─ 检测路径遍历                              │
│     ├─ 检测SSRF                                  │
│     └─ 检测文件上传                              │
│                                                 │
│  4. 结果分析                                     │
│     ├─ 漏洞确认验证                              │
│     ├─ 去重处理                                  │
│     ├─ 风险评级                                  │
│     └─ 生成报告                                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 4.2 爬虫原理

**爬虫发现逻辑**
```python
# 简化的 DAST 爬虫核心逻辑
import re
from urllib.parse import urljoin, urlparse
from collections import deque
import requests
from bs4 import BeautifulSoup

class DASTSpider:
    """DAST 爬虫 - 发现应用页面和参数"""

    def __init__(self, base_url: str, max_depth: int = 3):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited = set()
        self.urls_to_scan = deque()
        self.forms = []
        self.params = {}
        self.cookies = {}

    def crawl(self):
        """开始爬取"""
        self.urls_to_scan.append((self.base_url, 0))

        while self.urls_to_scan:
            url, depth = self.urls_to_scan.popleft()

            if url in self.visited or depth > self.max_depth:
                continue

            self.visited.add(url)

            try:
                response = requests.get(url, cookies=self.cookies, timeout=10)
                self._extract_links(response, url, depth)
                self._extract_forms(response, url)
                self._extract_params(response, url)
            except Exception as e:
                continue

        return {
            'urls': list(self.visited),
            'forms': self.forms,
            'params': self.params,
        }

    def _extract_links(self, response, url, depth):
        """提取页面中的链接"""
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if self._is_same_origin(full_url) and full_url not in self.visited:
                self.urls_to_scan.append((full_url, depth + 1))

    def _extract_forms(self, response, url):
        """提取表单和输入参数"""
        soup = BeautifulSoup(response.text, 'html.parser')
        for form in soup.find_all('form'):
            form_info = {
                'url': url,
                'method': form.get('method', 'GET').upper(),
                'action': urljoin(url, form.get('action', '')),
                'inputs': [],
            }
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                form_info['inputs'].append({
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', ''),
                })
            self.forms.append(form_info)

    def _is_same_origin(self, url):
        """检查是否同源"""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
```

### 4.3 主动扫描与 Payload 注入

**Payload 注入策略**
```python
# DAST Payload 注入核心逻辑
import requests
from typing import List, Dict

class DASTScanner:
    """DAST 主动扫描器"""

    # SQL 注入测试 Payload
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "' UNION SELECT NULL,NULL,NULL --",
        "1; DROP TABLE users --",
        "' AND SLEEP(5) --",
        "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
    ]

    # XSS 测试 Payload
    XSS_PAYLOADS = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "\"><script>alert(1)</script>",
        "<body onload=alert(1)>",
    ]

    # 命令注入 Payload
    CMD_INJECTION_PAYLOADS = [
        "; id",
        "| id",
        "`id`",
        "$(id)",
        "& id",
        "; whoami",
    ]

    # 路径遍历 Payload
    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]

    def scan_sql_injection(self, url: str, params: dict) -> List[Dict]:
        """SQL 注入扫描"""
        findings = []
        for param_name, param_value in params.items():
            for payload in self.SQL_INJECTION_PAYLOADS:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    # 发送测试请求
                    response = requests.get(url, params=test_params, timeout=10)
                    # 检测 SQL 错误信息
                    if self._detect_sql_error(response.text):
                        findings.append({
                            'type': 'SQL Injection',
                            'url': url,
                            'param': param_name,
                            'payload': payload,
                            'evidence': 'SQL错误信息泄露',
                            'severity': 'HIGH',
                        })
                        break  # 该参数已确认漏洞，不再测试

                    # 检测时间延迟（盲注）
                    if self._detect_time_based(url, test_params, param_name):
                        findings.append({
                            'type': 'SQL Injection (Time-based)',
                            'url': url,
                            'param': param_name,
                            'payload': payload,
                            'evidence': '时间延迟检测',
                            'severity': 'HIGH',
                        })
                        break

                except requests.RequestException:
                    continue

        return findings

    def scan_xss(self, url: str, params: dict) -> List[Dict]:
        """XSS 扫描"""
        findings = []
        for param_name in params:
            for payload in self.XSS_PAYLOADS:
                test_params = params.copy()
                test_params[param_name] = payload

                try:
                    response = requests.get(url, params=test_params, timeout=10)
                    # 检测 Payload 是否反射在响应中
                    if payload in response.text:
                        findings.append({
                            'type': 'Reflected XSS',
                            'url': url,
                            'param': param_name,
                            'payload': payload,
                            'evidence': 'Payload 反射在响应中',
                            'severity': 'MEDIUM',
                        })
                        break
                except requests.RequestException:
                    continue

        return findings

    def _detect_sql_error(self, response_text: str) -> bool:
        """检测 SQL 错误信息"""
        sql_errors = [
            'SQL syntax', 'mysql_fetch', 'ORA-', 'SQLSTATE',
            'PostgreSQL ERROR', 'SQLite3::query', 'Microsoft OLE DB',
            'Unclosed quotation mark', 'SQL command not properly ended',
        ]
        text_lower = response_text.lower()
        return any(err.lower() in text_lower for err in sql_errors)

    def _detect_time_based(self, url, params, param_name, delay=5):
        """检测基于时间的盲注"""
        import time
        # 正常请求计时
        start = time.time()
        requests.get(url, params={param_name: '1'}, timeout=10)
        normal_time = time.time() - start

        # 注入延迟请求计时
        start = time.time()
        delay_params = params.copy()
        delay_params[param_name] = f"1' AND SLEEP({delay}) --"
        requests.get(url, params=delay_params, timeout=delay + 10)
        delay_time = time.time() - start

        return delay_time - normal_time >= delay - 1
```

### 4.4 被动扫描

**被动扫描检查项**
```python
# 被动扫描核心逻辑
from typing import Dict, List

class PassiveScanner:
    """被动扫描器 - 分析正常请求响应"""

    def scan(self, response: Dict) -> List[Dict]:
        """被动扫描"""
        findings = []

        # 1. 安全头检查
        findings.extend(self._check_security_headers(response))
        # 2. Cookie 安全属性检查
        findings.extend(self._check_cookie_security(response))
        # 3. 敏感信息泄露检查
        findings.extend(self._check_info_disclosure(response))
        # 4. SSL/TLS 配置检查
        findings.extend(self._check_tls_config(response))
        # 5. 缓存策略检查
        findings.extend(self._check_cache_policy(response))

        return findings

    def _check_security_headers(self, response: Dict) -> List[Dict]:
        """检查安全响应头"""
        findings = []
        headers = response.get('headers', {})

        required_headers = {
            'Strict-Transport-Security': 'HSTS 头缺失，可能遭受中间人攻击',
            'X-Content-Type-Options': 'X-Content-Type-Options 缺失，可能遭受 MIME 嗅探',
            'X-Frame-Options': 'X-Frame-Options 缺失，可能遭受点击劫持',
            'Content-Security-Policy': 'CSP 缺失，XSS 防护不足',
            'X-XSS-Protection': 'X-XSS-Protection 缺失',
        }

        for header, message in required_headers.items():
            if header not in headers:
                findings.append({
                    'type': 'Missing Security Header',
                    'header': header,
                    'severity': 'MEDIUM',
                    'message': message,
                })

        return findings

    def _check_cookie_security(self, response: Dict) -> List[Dict]:
        """检查 Cookie 安全属性"""
        findings = []
        cookies = response.get('cookies', [])

        for cookie in cookies:
            issues = []
            if not cookie.get('secure', False):
                issues.append('缺少 Secure 属性')
            if not cookie.get('httponly', False):
                issues.append('缺少 HttpOnly 属性')
            if not cookie.get('samesite'):
                issues.append('缺少 SameSite 属性')

            if issues:
                findings.append({
                    'type': 'Insecure Cookie',
                    'cookie': cookie.get('name'),
                    'severity': 'MEDIUM',
                    'message': '; '.join(issues),
                })

        return findings

    def _check_info_disclosure(self, response: Dict) -> List[Dict]:
        """检查敏感信息泄露"""
        findings = []
        headers = response.get('headers', {})
        body = response.get('body', '')

        # 检查服务器版本信息暴露
        if 'Server' in headers:
            server = headers['Server']
            if any(ver in server for ver in ['/', 'version']):
                findings.append({
                    'type': 'Server Version Disclosure',
                    'severity': 'LOW',
                    'message': f'服务器版本暴露: {server}',
                })

        # 检查调试信息暴露
        debug_patterns = [
            'Traceback (most recent call last)',
            'Debug mode is on',
            'Stack trace',
            'PHP Notice',
            'Warning: include(',
        ]
        for pattern in debug_patterns:
            if pattern in body:
                findings.append({
                    'type': 'Debug Information Disclosure',
                    'severity': 'MEDIUM',
                    'message': f'调试信息暴露: {pattern}',
                })
                break

        return findings
```

---

---

