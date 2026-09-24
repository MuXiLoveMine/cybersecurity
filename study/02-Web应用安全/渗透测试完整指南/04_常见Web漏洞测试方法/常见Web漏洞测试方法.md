# 常见Web漏洞测试方法

### 4.1 OWASP Top 10 测试方法

OWASP Top 10是Web应用安全风险的权威排名，2021版包含：

1. 访问控制失效
2. 加密失败
3. 注入
4. 不安全设计
5. 安全配置错误
6. 易受攻击和过时的组件
7. 身份认证失败
8. 软件和数据完整性失败
9. 安全日志和监控不足
10. 服务端请求伪造（SSRF）

### 4.2 SQL注入测试

**检测方法**：
- 基于报错：在参数后添加单引号`'`、双引号`"`、括号`)`等，观察是否出现SQL错误信息。
- 基于布尔：添加`AND 1=1`和`AND 1=2`，观察返回内容是否不同。
- 基于时间：添加`AND SLEEP(5)`或`WAITFOR DELAY '0:0:5'`，观察响应时间变化。
- 基于UNION：尝试`UNION SELECT`语句，观察是否返回额外数据。

**利用技术**：
- **UNION注入**：通过UNION SELECT联合查询获取其他表数据。
- **布尔盲注**：逐字符猜解数据，基于页面差异判断。
- **时间盲注**：无页面差异时，通过响应时间判断。
- **报错注入**：利用数据库报错函数回显数据（如MySQL的updatexml、extractvalue）。
- **堆叠注入**：在支持的数据库中执行多条SQL语句。

**绕过技巧**：
- 大小写混淆：`UnIoN sElEcT`
- 注释绕过：`UN/**/ION SEL/**/ECT`
- 编码绕过：URL编码、Hex编码、Unicode编码。
- 内联注释：`/*!50000UNION*/`
- 空格替代：`%0a`、`%09`、`%0b`替代空格。

**工具**：sqlmap自动化注入检测和利用，详见第5节。

### 4.3 XSS测试

**反射型XSS**：
- 在URL参数中注入payload，观察是否在响应中未编码地输出。
- 测试payload：`<script>alert(1)</script>`、`"><img src=x onerror=alert(1)>`、`javascript:alert(1)`。
- 测试所有输入参数（查询参数、路径参数、HTTP头）。

**存储型XSS**：
- 在输入框（评论、用户名、个人资料）中注入payload。
- 提交后重新访问页面，检查payload是否存储并在页面中执行。
- 检查所有用户输入是否在输出时正确编码。

**DOM型XSS**：
- 分析JavaScript代码中的`document.location`、`document.URL`、`document.referrer`等可被用户控制的输入。
- 检查这些输入是否被直接写入DOM（`innerHTML`、`document.write`、`eval`）。
- 构造URL触发DOM操作执行注入的JS代码。

**绕过技巧**：
- 大小写混淆、编码绕过、事件属性替代`<script>`标签。
- 利用SVG、Math等较少过滤的上下文。
- 模板注入配合XSS。

### 4.4 SSRF测试

**基础利用**：
- 将请求URL参数改为内部地址：`http://127.0.0.1`、`http://localhost`、`http://192.168.1.1`。
- 观察响应内容是否包含内部系统信息。
- 尝试访问云元数据端点：`http://169.254.169.254/latest/meta-data/`（AWS）。

**内网探测**：
- 通过SSRF扫描内网端口和服务。
- 使用dict://、gopher://、file://等协议尝试。
- 请求`file:///etc/passwd`测试文件读取。

**协议利用**：
- gopher协议：构造各种协议的原始数据包，攻击内网Redis、MySQL等。
- dict协议：探测内网服务端口。
- ldap协议：查询LDAP目录服务。

**绕过技巧**：
- IP地址变形：十进制IP、八进制、十六进制、IPv6。
- DNS重绑定：利用DNS解析时间差绕过IP白名单。
- 短链接服务重定向。
- URL解析差异（`http://safe.com@evil.com`）。

### 4.5 文件上传测试

**类型绕过**：
- 修改Content-Type为允许的类型（image/jpeg）。
- 修改文件扩展名（.php5、.phtml、.php3、.pht）。
- 大小写绕过（.PHP、.Php）。
- 双扩展名（file.php.jpg）。
- 空字节截断（file.php%00.jpg）。

**内容绕过**：
- 在图片文件中嵌入PHP代码（图片马）。
- 利用GIF文件头`GIF89a`+PHP代码。
- 利用文件头+内容组合。

**解析漏洞**：
- Apache解析漏洞：从右向左解析扩展名。
- Nginx解析漏洞：`/test.jpg/x.php`触发PHP解析。
- IIS解析漏洞：`test.asp;.jpg`、目录解析`test.asp/1.jpg`。

**利用方法**：
- 上传Web Shell获取命令执行权限。
- 上传HTML文件进行XSS或钓鱼。
- 上传恶意配置文件覆盖应用配置。

### 4.6 反序列化测试

**Java反序列化**：
- 检测：在HTTP请求中查找序列化数据特征（`rO0AB`Base64编码的Java序列化数据、`aced0005`Hex编码）。
- 利用：使用ysoserial工具生成利用链payload（CommonsCollections、Spring等）。
- 目标：JBoss、WebLogic、Jenkins等Java应用常见反序列化漏洞。

**PHP反序列化**：
- 检测：查找`unserialize()`函数调用，分析输入来源。
- 利用：构造POP链（利用__destruct、__wakeup等魔术方法）。
- 工具：PHPGGC（PHP Generic Gadget Chain）生成各种框架的利用链。

**.NET反序列化**：
- 检测：查找`BinaryFormatter`、`LosFormatter`、`ObjectStateFormatter`等反序列化方法。
- 利用：ysoserial.net生成.NET反序列化payload。
- 目标：ViewState反序列化、JSON.NET反序列化。

### 4.7 权限绕过测试

**水平越权**：
- 使用用户A的会话尝试访问用户B的资源（如修改URL中的userId参数）。
- 测试所有涉及资源标识符的接口（GET /api/users/{id}、GET /api/orders/{id}）。
- 使用Burp Suite Autorize插件自动化越权检测。

**垂直越权**：
- 使用普通用户会话尝试访问管理员接口。
- 修改请求方法绕过权限检查（GET替代POST）。
- 路径绕过：`/admin/../admin`、`/admin/./`、`/admin%2f`。
- HTTP方法覆盖：`X-HTTP-Method-Override: PUT`。
- 参数污染：`role=user&role=admin`。

---

---

