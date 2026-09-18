# SAST 与 DAST 实战指南

> SAST（静态应用安全测试）和 DAST（动态应用安全测试）是应用安全测试的两大核心支柱，分别从源代码层面和运行时层面发现安全漏洞。本文档详细讲解其原理、工具使用及实战集成方案。

---

## 一、SAST 原理详解

### 1.1 SAST 分析层次

SAST 通过多层次分析源代码来检测安全漏洞，每个层次逐步深入：

```
源代码
  │
  ├─ 1. 词法分析（Lexical Analysis）
  │     将源代码分解为 Token 流
  │     例：x = 1 + 2 → [ID:x, EQ, NUM:1, PLUS, NUM:2]
  │
  ├─ 2. 语法分析（Syntax Analysis）
  │     构建 AST（抽象语法树）
  │     例：Assign(x, Add(1, 2))
  │
  ├─ 3. 语义分析（Semantic Analysis）
  │     理解代码含义，类型检查
  │     例：x 是整数赋值
  │
  ├─ 4. 数据流分析（Data Flow Analysis）
  │     追踪数据在程序中的流动
  │     例：request.getParameter("id") → 变量 id → SQL 查询
  │
  ├─ 5. 控制流分析（Control Flow Analysis）
  │     理解程序执行路径
  │     例：if/else 分支可达性分析
  │
  └─ 6. 污点分析（Taint Analysis）
        追踪不可信数据的传播路径
        Source → 传播 → Sink
```

### 1.2 污点分析详解

污点分析是 SAST 检测注入类漏洞的核心技术。

**基本概念**
- **Source（污点源）**：不可信数据入口（如用户输入）
- **Sink（汇点）**：敏感操作执行点（如 SQL 执行、命令执行）
- **传播路径**：数据从 Source 到 Sink 的流动路径
- **Sanitizer（净化器）**：对污点数据进行清洗的函数

**污点分析流程示例**
```python
# Python 污点分析示例

# Source: 用户输入（污点源）
user_input = request.getParameter("id")  # [TAINT] 污点源：用户输入

# 传播：污点数据赋值给新变量
data = user_input                        # [TAINT] 传播：data 被污染

# 传播：污点数据进入函数
processed = process_data(data)           # [TAINT] 传播：processed 被污染

# Sink: SQL 查询执行（危险！污点到达 Sink）
query = "SELECT * FROM users WHERE id=" + processed
cursor.execute(query)                    # [ALERT] SQL 注入风险！

# 安全示例：使用参数化查询
cursor.execute("SELECT * FROM users WHERE id=%s", (user_input,))
# [SAFE] 参数化查询，污点被隔离
```

**污点分析规则定义示例（Semgrep）**
```yaml
# Semgrep 污点分析规则：检测 Python SQL 注入
rules:
  - id: python-sql-injection
    mode: taint
    pattern-sources:
      # 定义污点源：所有用户输入
      - patterns:
          - pattern: flask.request.form.get(...)
      - patterns:
          - pattern: flask.request.args.get(...)
      - patterns:
          - pattern: flask.request.cookies.get(...)
      - patterns:
          - pattern-either:
              - pattern: input(...)
              - pattern: sys.stdin.readline()

    pattern-sinks:
      # 定义汇点：所有 SQL 执行
      - patterns:
          - pattern: $CUR.execute(...)
          - pattern-not: $CUR.execute("...", ...)
      - patterns:
          - pattern: $CUR.executemany(...)
          - pattern-not: $CUR.executemany("...", ...)

    pattern-sanitizers:
      # 定义净化器：安全转换函数
      - pattern: int(...)
      - pattern: float(...)

    message: 检测到SQL注入风险，请使用参数化查询
    languages: [python]
    severity: ERROR
    metadata:
      cwe: "CWE-89: SQL Injection"
      owasp: "A03:2021-Injection"
```

### 1.3 控制流分析

控制流分析用于理解程序执行路径，检测可达性和逻辑漏洞。

**控制流图（CFG）示例**
```
        [Entry]
           │
           ▼
      [Input Validation]
       /         \
    Pass         Fail
     │             │
     ▼             ▼
[Process Data]  [Error Response]
     │             │
     ▼             ▼
[Output]      [Return Error]
     │             │
     └──────┬──────┘
            ▼
        [Exit]
```

**控制流分析应用场景**
- 检测不可达代码
- 验证错误处理路径
- 检查权限验证分支
- 分析资源释放路径
- 检测逻辑死锁

---

## 二、SAST 工具使用

### 2.1 SonarQube 配置与规则自定义

#### 2.1.1 SonarQube 安装与配置

**Docker 安装 SonarQube**
```bash
# 启动 SonarQube（使用 PostgreSQL 数据库）
docker run -d --name sonarqube \
  -p 9000:9000 \
  -e SONAR_JDBC_URL=jdbc:postgresql://sonar-db:5432/sonar \
  -e SONAR_JDBC_USERNAME=sonar \
  -e SONAR_JDBC_PASSWORD=sonar \
  sonarqube:latest-community

# 访问 http://localhost:9000
# 默认账号: admin / admin
```

**sonar-project.properties 配置文件**
```properties
# 项目唯一标识
sonar.projectKey=my-secure-app
sonar.projectName=My Secure Application
sonar.projectVersion=1.0

# 源代码目录
sonar.sources=src
sonar.tests=tests

# 语言设置
sonar.language=py

# 代码覆盖率
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.coveragePlugin=cobertura

# 排除不需要扫描的文件
sonar.exclusions=**/node_modules/**,**/vendor/**,**/*.min.js

# 安全相关配置
# 启用安全热点查看
sonar.security.hotspotReview=true
# 设置质量门禁
sonar.qualitygate.wait=true

# 编码规范规则集
sonar.python.bandit.reportPaths=bandit-report.json
```

#### 2.1.2 SonarQube 质量门禁配置

**自定义质量门禁**
```
# 质量门禁条件
1. 安全评级 = A（安全漏洞率 < 5%）
2. 可靠性评级 = A（Bug 数 < 10）
3. 可维护性评级 = A（技术债务比例 < 5%）
4. 代码覆盖率 >= 80%
5. 重复代码比例 < 3%
6. 安全热点审查率 = 100%
```

#### 2.1.3 SonarQube 自定义规则

**Java 自定义规则（示例）**
```java
// 检测不安全的密码哈希
@Rule(
    key = "CustomInsecurePasswordHash",
    name = "检测不安全的密码哈希算法",
    description = "密码不应使用 MD5/SHA1 等弱哈希算法",
    priority = Priority.CRITICAL,
    tags = {"cwe", "owasp", "security"}
)
@ActivatedByDefault
public class InsecurePasswordHashCheck extends AbstractJavaRule {

    private static final Set<String> INSECURE_HASHES = Set.of(
        "MD5", "SHA1", "SHA-1"
    );

    @Override
    public void visitNode(Tree tree) {
        if (tree instanceof MethodInvocationTree) {
            MethodInvocationTree method = (MethodInvocationTree) tree;
            String methodName = method.symbol().name();
            if (methodName.equals("getInstance")) {
                ExpressionTree algorithmArg = method.arguments().get(0);
                if (algorithmArg instanceof LiteralTree) {
                    String algo = ((LiteralTree) algorithmArg).value()
                        .replace("\"", "").toUpperCase();
                    if (INSECURE_HASHES.contains(algo)) {
                        reportIssue(tree,
                            "检测到不安全的哈希算法: " + algo +
                            "，请使用 BCrypt/Argon2/PBKDF2 替代");
                    }
                }
            }
        }
    }
}
```

### 2.2 Fortify 使用

#### 2.2.1 Fortify 扫描流程

```bash
# 第一步：翻译（将代码转换为中间表示）
sourceanalyzer -b myapp -source src/ -encoding UTF-8

# 第二步：扫描（对中间表示进行安全分析）
sourceanalyzer -b myapp -scan -f fortify-report.fpr

# 第三步：生成报告
ReportGenerator -format HTML -f fortify-report.html \
    -source fortify-report.fpr -template "Developer"

# 第四步：上传到 SSC（Software Security Center）
fortifyclient uploadFPR -file fortify-report.fpr \
    -url https://ssc.example.com/ssc \
    -authtoken your-token \
    -applicationVersion "MyApp:1.0"
```

#### 2.2.2 Fortify 自定义规则

**Fortify 自定义规则文件（XML）**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<LanguageScope>
  <Language language="python">
    <Rule>
      <RuleID>Custom-SQL-Injection-Django</RuleID>
      <Metadata>
        <Group>SQL Injection</Group>
        <Description>
          检测 Django Raw SQL 中的字符串拼接
        </Description>
        <Risk>SQL注入</Risk>
        <Impact>High</Impact>
        <Confidence>High</Confidence>
      </Metadata>
      <FunctionDefinitions>
        <Function name="raw">
          <Source>django.db.models.QuerySet</Source>
          <InsecureParam position="0"/>
        </Function>
      </FunctionDefinitions>
    </Rule>
  </Language>
</LanguageScope>
```

### 2.3 Semgrep 规则编写

#### 2.3.1 Semgrep 基础规则

**Semgrep 规则语法结构**
```yaml
rules:
  - id: 规则唯一ID
    pattern: 匹配模式  # 基础模式匹配
    pattern-regex: 正则表达式  # 正则匹配
    pattern-either:  # 多模式任一匹配
      - pattern: 模式1
      - pattern: 模式2
    pattern-inside:  # 在指定上下文内匹配
      pattern: 外部模式
    pattern-not-inside:  # 不在指定上下文内匹配
      pattern: 排除模式
    message: 报告消息
    languages: [python]
    severity: ERROR  # ERROR / WARNING / INFO
    metadata:
      cwe: "CWE-89"
      owasp: "A03:2021"
```

#### 2.3.2 常用安全规则示例

**规则集1：检测 Python 安全问题**
```yaml
# custom-python-security.yml
rules:
  # 1. 检测 eval() 使用
  - id: python-eval-usage
    pattern: eval(...)
    message: "检测到 eval() 使用，存在代码注入风险"
    languages: [python]
    severity: ERROR
    metadata:
      cwe: "CWE-95: Code Injection"

  # 2. 检测不安全 pickle 反序列化
  - id: python-pickle-deserialize
    pattern: pickle.loads($DATA)
    pattern-not: pickle.loads($DATA)
    message: "pickle.loads 存在不安全反序列化风险"
    languages: [python]
    severity: ERROR
    metadata:
      cwe: "CWE-502: Deserialization"

  # 3. 检测 subprocess 命令注入
  - id: python-subprocess-shell-injection
    pattern: subprocess.call($CMD, shell=True)
    message: "subprocess with shell=True 存在命令注入风险"
    languages: [python]
    severity: ERROR
    metadata:
      cwe: "CWE-78: OS Command Injection"

  # 4. 检测弱加密算法
  - id: python-weak-hash-md5
    pattern-either:
      - pattern: hashlib.md5(...)
      - pattern: hashlib.sha1(...)
    message: "使用了弱哈希算法，请使用 SHA-256+"
    languages: [python]
    severity: WARNING
    metadata:
      cwe: "CWE-327: Weak Cryptography"

  # 5. 检测硬编码密码
  - id: python-hardcoded-password
    pattern: $VAR = "..."
    metavariable-regex:
      metavariable: $VAR
      regex: '(?i)(password|passwd|pwd|secret|key|token)'
    message: "检测到硬编码密码/密钥"
    languages: [python]
    severity: WARNING
    metadata:
      cwe: "CWE-798: Hardcoded Credentials"
```

**规则集2：检测 JavaScript 安全问题**
```yaml
# custom-js-security.yml
rules:
  # 1. 检测 XSS（innerHTML 赋值）
  - id: js-xss-innerhtml
    pattern: $EL.innerHTML = $INPUT
    pattern-not: $EL.innerHTML = ""
    message: "innerHTML 赋值可能导致 XSS"
    languages: [javascript, typescript]
    severity: WARNING
    metadata:
      cwe: "CWE-79: XSS"

  # 2. 检测不安全的 eval
  - id: js-eval-usage
    pattern: eval($INPUT)
    message: "eval() 存在代码注入风险"
    languages: [javascript, typescript]
    severity: ERROR
    metadata:
      cwe: "CWE-95: Code Injection"

  # 3. 检测 SQL 注入
  - id: js-sql-injection
    pattern: $DB.query(`SELECT ... ${$INPUT} ...`)
    message: "模板字符串 SQL 查询可能导致注入"
    languages: [javascript, typescript]
    severity: ERROR
    metadata:
      cwe: "CWE-89: SQL Injection"

  # 4. 检测不安全的正则（ReDoS）
  - id: js-redos-regex
    pattern: new RegExp($INPUT)
    message: "动态正则表达式可能导致 ReDoS"
    languages: [javascript, typescript]
    severity: WARNING
    metadata:
      cwe: "CWE-1333: ReDoS"
```

#### 2.3.3 Semgrep 在 CI/CD 中的使用

```bash
# 使用预定义规则集
semgrep ci --config p/owasp-top-ten
semgrep ci --config p/security-audit
semgrep ci --config p/python
semgrep ci --config p/javascript

# 使用自定义规则
semgrep ci --config custom-rules.yml

# 多规则集组合
semgrep ci --config p/owasp-top-ten --config custom-rules.yml

# 输出 JSON 格式
semgrep ci --json -o semgrep-report.json

# 输出 SARIF 格式（用于 GitHub Code Scanning）
semgrep ci --sarif -o semgrep-results.sarif

# 只报告错误级别
semgrep ci --config p/owasp-top-ten --error
```

---

## 三、误报管理

### 3.1 误报产生原因

| 原因 | 说明 | 示例 |
|------|------|------|
| 缺乏上下文 | 工具不理解运行时上下文 | 已验证输入仍报 SQL 注入 |
| 安全函数未识别 | 工具不认识自定义净化函数 | ORM 安全封装被忽略 |
| 代码不可达 | 逻辑分支不可达但被扫描 | 条件永不成立的分支 |
| 配置问题 | 规则过于宽泛 | 敏感词匹配过于笼统 |
| 语言特性 | 动态类型/元编程 | Python 动态属性访问 |

### 3.2 误报标记与抑制

**Semgrep 抑制标记**
```python
# 安全：此处 eval 仅用于受信任的数学表达式计算
# 输入已通过 validate_expression() 严格验证
# nosemgrep: python-eval-usage
result = eval(safe_expression)

# 多行抑制
safe_result = compile(safe_expression, '<string>', 'eval')  # nosemgrep
result = eval(safe_result)
```

**SonarQube 抑制标记**
```java
// Java 中抑制 SonarQube 规则
@SuppressWarnings("squid:S2068") // 密码不是硬编码，来自配置文件
private String password = config.getPassword();
```

**Bandit 抑制标记**
```python
# 安全：此处的 subprocess 调用使用了固定参数列表
# 输入来自内部配置文件，非用户输入
subprocess.run(["ping", "-c", "1", host], check=True)  # nosec B603
```

### 3.3 基线管理

**基线管理策略**
```yaml
# .semgrep_baseline.yml
# 基线文件记录已知的、已审查的发现
# CI 只报告新增的安全问题

baseline_findings:
  - id: python-eval-usage
    file: src/calculator.py
    line: 42
    status: accepted_risk
    reviewer: security-team
    review_date: 2024-01-15
    reason: "eval 用于受控数学表达式，输入经过严格验证"

  - id: python-hardcoded-password
    file: tests/test_config.py
    line: 10
    status: false_positive
    reviewer: developer
    review_date: 2024-01-10
    reason: "测试文件中的示例密码，不会部署到生产"
```

**基线管理脚本**
```python
#!/usr/bin/env python3
"""
Semgrep 基线管理工具
只报告基线文件中不存在的新增安全问题
"""

import json
import sys
from typing import List, Dict

class BaselineManager:
    """基线管理器"""

    def __init__(self, baseline_path: str):
        self.baseline = self._load_baseline(baseline_path)

    def _load_baseline(self, path: str) -> List[Dict]:
        """加载基线文件"""
        try:
            with open(path) as f:
                data = json.load(f)
            return data.get('baseline_findings', [])
        except FileNotFoundError:
            return []

    def filter_new_findings(self, report_path: str) -> List[Dict]:
        """过滤出基线中不存在的新发现"""
        with open(report_path) as f:
            report = json.load(f)

        new_findings = []
        for result in report.get('results', []):
            finding_key = self._make_key(result)
            if finding_key not in self.baseline_keys:
                new_findings.append(result)

        return new_findings

    @property
    def baseline_keys(self) -> set:
        """获取基线发现键集合"""
        return {
            self._make_key_from_baseline(b) for b in self.baseline
        }

    @staticmethod
    def _make_key(finding: Dict) -> str:
        """从扫描结果生成唯一键"""
        return f"{finding.get('check_id')}:{finding.get('path')}:{finding.get('start', {}).get('line')}"

    @staticmethod
    def _make_key_from_baseline(baseline: Dict) -> str:
        """从基线记录生成唯一键"""
        return f"{baseline.get('id')}:{baseline.get('file')}:{baseline.get('line')}"


if __name__ == '__main__':
    manager = BaselineManager('.semgrep_baseline.yml')
    new_findings = manager.filter_new_findings('semgrep-report.json')

    print(f"基线中已有: {len(manager.baseline)} 条")
    print(f"本次扫描新增: {len(new_findings)} 条")

    if new_findings:
        print("\n新增安全问题:")
        for f in new_findings:
            print(f"  - [{f.get('extra', {}).get('severity', 'INFO')}] "
                  f"{f.get('check_id')}: {f.get('path')}:{f.get('start', {}).get('line')}")
        sys.exit(1)
    else:
        print("无新增安全问题")
        sys.exit(0)
```

---

## 四、DAST 原理详解

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

## 五、DAST 工具使用

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

## 六、IAST 原理与工具

### 6.1 IAST 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                     IAST 工作原理                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  测试请求                                               │
│     │                                                    │
│     ▼                                                    │
│  ┌─────────┐    ┌─────────────────────┐                  │
│  │ 测试工具 │───→│   应用服务器         │                  │
│  │(功能测试)│    │  ┌───────────────┐ │                  │
│  └─────────┘    │  │  IAST Agent   │ │                  │
│                  │  │  (运行时插桩)  │ │                  │
│                  │  │               │ │                  │
│                  │  │ • 监控数据流   │ │                  │
│                  │  │ • 追踪污点     │ │                  │
│                  │  │ • 检测Sink     │ │                  │
│                  │  │ • 代码级定位   │ │                  │
│                  │  └───────┬───────┘ │                  │
│                  └──────────┼──────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌────────────────┐                    │
│                    │  IAST 服务器     │                    │
│                    │  (结果聚合)     │                    │
│                    │  • 实时告警     │                    │
│                    │  • 漏洞报告     │                    │
│                    │  • 代码定位     │                    │
│                    └────────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2 OpenRASP-IAST 配置

```json
{
  "iast": {
    "enabled": true,
    "server_url": "http://iast-server:8080",
    "agent_token": "your-agent-token",
    "project_name": "ecommerce-app",
    "language": "java",

    "hooks": {
      "sql": {
        "enabled": true,
        "hook_points": [
          "java.sql.Statement.execute",
          "java.sql.Statement.executeQuery",
          "java.sql.PreparedStatement.execute"
        ]
      },
      "ssrf": {
        "enabled": true,
        "hook_points": [
          "java.net.URL.openConnection",
          "org.apache.http.client.methods.HttpGet"
        ]
      },
      "command_exec": {
        "enabled": true,
        "hook_points": [
          "java.lang.Runtime.exec",
          "java.lang.ProcessBuilder.start"
        ]
      },
      "file_include": {
        "enabled": true,
        "hook_points": [
          "java.io.FileInputStream",
          "java.io.FileReader"
        ]
      },
      "xss": {
        "enabled": true,
        "hook_points": [
          "javax.servlet.ServletOutputStream.print",
          "javax.servlet.jsp.JspWriter.print"
        ]
      },
      "deserialization": {
        "enabled": true,
        "hook_points": [
          "java.io.ObjectInputStream.readObject"
        ]
      }
    },

    "report": {
      "realtime": true,
      "interval": 5,
      "max_queue_size": 1000
    },

    "performance": {
      "max_hook_depth": 10,
      "max_data_length": 4096,
      "exclude_packages": [
        "java.lang",
        "sun.",
        "com.sun."
      ]
    }
  }
}
```

---

## 七、SCA 工具使用

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

## 八、实战案例：CI/CD 安全扫描流水线

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

## 九、最佳实践总结

### 9.1 SAST 最佳实践
1. **分层扫描策略**：预提交快速扫描 + CI/CD 全量扫描 + 定期深度扫描
2. **多工具组合**：不同工具覆盖不同漏洞类型，交叉验证减少遗漏
3. **误报管理**：建立基线机制，标记和抑制已知误报，定期审查
4. **自定义规则**：根据项目特点编写针对性的安全规则
5. **覆盖率追踪**：监控安全扫描覆盖率，确保代码被充分覆盖

### 9.2 DAST 最佳实践
1. **分层扫描**：测试环境主动扫描 + 生产环境被动监控
2. **认证支持**：配置认证信息扫描需要登录的功能
3. **限速控制**：避免扫描影响目标系统稳定性
4. **持续扫描**：每次部署后自动执行 DAST 扫描
5. **结果关联**：将 DAST 发现与代码关联，定位问题代码位置

### 9.3 SCA 最佳实践
1. **持续监控**：每次代码提交和每日定期扫描
2. **SBOM 生成**：为每个制品生成软件物料清单
3. **修复优先级**：根据可利用性和影响范围评估修复优先级
4. **自动修复**：使用工具自动升级安全版本
5. **供应链验证**：验证第三方组件来源和完整性

---

> **总结**：SAST 和 DAST 是互补的安全测试方法，SAST 在早期发现源代码层面的漏洞，DAST 在运行时验证实际可利用的漏洞。最佳实践是将两者与 IAST、SCA 结合使用，通过 CI/CD 流水线自动化集成，配合安全门禁策略，实现持续的安全质量保障。关键是根据项目实际情况选择合适的工具组合，建立可持续的安全扫描流程。
