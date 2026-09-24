# SAST 工具使用

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

---

