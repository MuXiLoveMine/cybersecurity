# 各语言安全编码 Checklist

### 8.1 Java 安全编码清单

```
□ 使用 PreparedStatement 参数化查询，禁止字符串拼接 SQL
□ 使用 Encode.forHtml / Encode.forJavaScript 进行输出编码
□ XML 解析禁用外部实体（XXE 防护）
□ 使用 SecureRandom 而非 Math.random()
□ AES 使用 GCM 模式，禁止 ECB
□ Session Cookie 设置 HttpOnly + Secure + SameSite
□ 使用 @PreAuthorize 进行方法级权限控制
□ 全局异常处理不泄露堆栈信息
□ 依赖使用 OWASP Dependency-Check 扫描
□ 反序列化使用白名单（ObjectInputFilter）
□ 使用 ProcessBuilder 而非 Runtime.exec() 拼接命令
□ 日志中不记录密码/密钥等敏感信息
```

### 8.2 Python 安全编码清单

```
□ 使用参数化查询（cursor.execute 占位符）
□ Flask Jinja2 自动转义（不使用 |safe 渲染用户输入）
□ 使用 subprocess 参数列表，禁止 shell=True
□ 使用 defusedxml 替代标准 xml.etree
□ 使用 secrets / os.urandom 生成随机数
□ 使用 bcrypt/argon2 存储密码
□ 使用 AES-GCM 加密，禁止 ECB
□ 文件上传验证类型+大小+随机文件名
□ 路径遍历使用 os.path.abspath + startswith 校验
□ 生产环境关闭 DEBUG 模式
□ 使用 pip-audit 扫描依赖漏洞
□ 日志脱敏敏感字段
```

### 8.3 PHP 安全编码清单

```
□ 使用 PDO 参数化查询，弃用 mysql_* 函数
□ 使用 htmlspecialchars 输出编码（ENT_QUOTES）
□ 使用 escapeshellarg/escapeshellcmd 防命令注入
□ 使用 password_hash/password_verify 管理密码
□ 文件上传使用 is_uploaded_file + move_uploaded_file
□ 关闭 allow_url_include 和 allow_url_fopen
□ 关闭 display_errors，使用 error_log 记录
□ Session Cookie 设置 httponly + secure + samesite
□ 使用 random_int/random_bytes 替代 rand/mt_rand
□ 使用 OpenSSL 扩展替代 mcrypt
□ 配置 open_basedir 限制文件访问范围
□ 定期运行 composer audit 扫描漏洞
```

### 8.4 Go 安全编码清单

```
□ 使用 database/sql 占位符参数化查询
□ 使用 html/template（自动转义）而非 text/template
□ 使用 exec.Command 参数列表，禁止拼接 shell 命令
□ 使用 crypto/rand 生成随机数，不用 math/rand
□ 使用 AES-GCM 或 ChaCha20-Poly1305 加密
□ 使用 crypto/bcrypt 哈希密码
□ 文件路径使用 filepath.Clean + 前缀校验
□ 使用 net/http 超时配置防 Slowloris
□ 中间件设置安全响应头
□ 使用 govulncheck 扫描依赖漏洞
□ TLS 配置使用 MinVersion: tls.VersionTLS12
□ 敏感配置从环境变量或密钥管理服务读取
```

### 8.5 JavaScript (Node.js) 安全编码清单

```
□ 使用参数化查询（pg/ mysql2 占位符）
□ 使用 helmet 设置安全响应头
□ 使用 DOMPurify 清洗富文本，避免 innerHTML
□ 使用 execFile 而非 exec（避免 shell 注入）
□ 使用 crypto.randomBytes 生成随机数
□ 使用 bcrypt/argon2 存储密码
□ 使用 express-rate-limit 防暴力破解
□ Cookie 设置 secure + httpOnly + sameSite
□ CORS 白名单配置，禁止 origin: '*'
□ 生产环境禁用 x-powered-by 头
□ 定期运行 npm audit 扫描漏洞
□ 使用 dotenv 管理环境变量，不硬编码密钥
□ 输入验证使用 joi/zod 等验证库
□ 避免 eval() / new Function() / require(userInput)
```

---

---

