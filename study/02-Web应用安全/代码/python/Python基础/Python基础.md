# Python安全编程指南

> 本文档系统性地介绍Python在网络安全领域的应用，涵盖常用安全库、Web请求安全、文件操作安全、密码学编程、网络编程安全、正则表达式安全、多线程安全、代码审计及安全编码最佳实践。

---

## 目录

- [1. Python安全编程概述](#1-python安全编程概述)
  - [1.1 Python在安全领域的应用](#11-python在安全领域的应用)
  - [1.2 安全编程原则](#12-安全编程原则)
  - [1.3 Python安全生态](#13-python安全生态)
- [2. 常用安全库](#2-常用安全库)
  - [2.1 requests库](#21-requests库)
  - [2.2 urllib3库](#22-urllib3库)
  - [2.3 socket库](#23-socket库)
  - [2.4 ssl库](#24-ssl库)
  - [2.5 hashlib库](#25-hashlib库)
  - [2.6 hmac库](#26-hmac库)
  - [2.7 secrets库](#27-secrets库)
- [3. Web请求安全](#3-web请求安全)
  - [3.1 SSRF防护](#31-ssrf防护)
  - [3.2 SSL/TLS验证](#32-ssltls验证)
  - [3.3 重定向安全](#33-重定向安全)
  - [3.4 Cookie安全处理](#34-cookie安全处理)
- [4. 文件操作安全](#4-文件操作安全)
  - [4.1 路径遍历防护](#41-路径遍历防护)
  - [4.2 Zip Slip漏洞](#42-zip-slip漏洞)
  - [4.3 反序列化安全](#43-反序列化安全)
  - [4.4 临时文件安全](#44-临时文件安全)
- [5. 密码学编程](#5-密码学编程)
  - [5.1 hashlib哈希算法](#51-hashlib哈希算法)
  - [5.2 hmac消息认证码](#52-hmac消息认证码)
  - [5.3 Cryptography库](#53-cryptography库)
  - [5.4 PyCryptodome库](#54-pycryptodome库)
  - [5.5 密码存储与验证](#55-密码存储与验证)
- [6. 网络编程安全](#6-网络编程安全)
  - [6.1 socket编程基础](#61-socket编程基础)
  - [6.2 端口扫描器实现](#62-端口扫描器实现)
  - [6.3 协议解析](#63-协议解析)
  - [6.4 SSL/TLS安全通信](#64-ssltls安全通信)
- [7. 正则表达式安全](#7-正则表达式安全)
  - [7.1 ReDoS漏洞原理](#71-redos漏洞原理)
  - [7.2 ReDoS防护策略](#72-redos防护策略)
  - [7.3 安全正则编写规范](#73-安全正则编写规范)
- [8. 多线程/多进程安全](#8-多线程多进程安全)
  - [8.1 线程安全机制](#81-线程安全机制)
  - [8.2 GIL与多线程](#82-gil与多线程)
  - [8.3 并发安全实践](#83-并发安全实践)
- [9. Python代码审计常见漏洞](#9-python代码审计常见漏洞)
  - [9.1 代码注入漏洞](#91-代码注入漏洞)
  - [9.2 命令注入漏洞](#92-命令注入漏洞)
  - [9.3 SSTI模板注入](#93-ssti模板注入)
  - [9.4 常见漏洞模式](#94-常见漏洞模式)
- [10. 安全编码最佳实践](#10-安全编码最佳实践)
  - [10.1 输入验证](#101-输入验证)
  - [10.2 输出编码](#102-输出编码)
  - [10.3 错误处理](#103-错误处理)
  - [10.4 日志安全](#104-日志安全)
  - [10.5 依赖管理](#105-依赖管理)

---

## 1. Python安全编程概述

### 1.1 Python在安全领域的应用

Python因其简洁的语法、丰富的库生态和强大的跨平台能力，成为网络安全领域最常用的编程语言之一。其典型应用场景包括：

- **渗透测试工具开发**：快速构建扫描器、exploit原型、自动化攻击工具
- **安全审计与代码分析**：静态分析、动态分析、漏洞模式检测
- **恶意软件分析**：PE文件解析、行为分析、IOC提取
- **网络流量分析**：数据包捕获与解析、协议还原
- **安全运维自动化**：日志分析、配置审计、漏洞管理
- **密码学应用**：加密解密、数字签名、密钥管理

### 1.2 安全编程原则

安全编程遵循以下核心原则：

```python
# 原则1：最小权限原则 - 仅授予必要的权限
# 原则2：纵深防御原则 - 多层安全防护
# 原则3：默认安全原则 - 安全的默认配置
# 原则4：失败安全原则 - 出错时拒绝而非放行
# 原则5：不信任原则 - 永不信任用户输入

# 安全编程检查清单示例
SECURITY_CHECKLIST = {
    "输入验证": "所有外部输入必须验证和清洗",
    "输出编码": "输出到不同上下文时正确编码",
    "认证授权": "每个功能点都要检查权限",
    "会话管理": "使用安全的会话管理机制",
    "加密存储": "敏感数据必须加密存储",
    "传输加密": "使用TLS加密传输",
    "错误处理": "不泄露敏感信息的错误处理",
    "日志审计": "记录关键操作的安全日志",
    "防注入": "使用参数化查询防注入",
    "依赖管理": "定期更新第三方依赖",
}
```

### 1.3 Python安全生态

Python安全生态包含丰富的工具和库：

| 类别 | 常用库/工具 | 用途 |
|------|-----------|------|
| Web请求 | requests, httpx, aiohttp | HTTP请求发送 |
| 密码学 | cryptography, PyCryptodome, hashlib | 加密/签名/哈希 |
| 网络扫描 | scapy, python-nmap, socket | 网络发现与扫描 |
| 漏洞利用 | pwntools, impacket | 漏洞利用框架 |
| 逆向分析 | r2pipe, capstone, unicorn | 逆向工程 |
| 流量分析 | dpkt, scapy, pyshark | 数据包分析 |
| Web扫描 | burp-rest-api, w3af | Web漏洞扫描 |
| 取证分析 | volatility, yara-python | 数字取证 |
| 模糊测试 | boofuzz, AFL | 模糊测试 |
| 代码审计 | bandit, pyt, semgrep | 静态代码分析 |

---

## 2. 常用安全库

### 2.1 requests库

requests是Python最常用的HTTP库，在安全测试中广泛使用。

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class SecureRequests:
    """安全的requests封装类"""

    @staticmethod
    def create_session(max_retries=3, timeout=10):
        """
        创建安全的requests会话

        安全配置：
        - 重试机制：自动重试失败的请求
        - 超时设置：防止长时间等待
        - SSL验证：默认启用证书验证
        - User-Agent：自定义标识
        """
        session = requests.Session()

        # 配置重试策略
        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "HEAD"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # 安全头设置
        session.headers.update({
            'User-Agent': 'SecureScanner/1.0',
            'Accept': 'text/html,application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

        # 默认超时
        session.timeout = timeout

        return session

    @staticmethod
    def safe_get(url, params=None, **kwargs):
        """
        安全的GET请求

        防护措施：
        - 强制超时
        - SSL验证
        - 重定向控制
        """
        session = kwargs.pop('session', SecureRequests.create_session())
        timeout = kwargs.pop('timeout', 10)
        verify = kwargs.pop('verify', True)  # 默认验证SSL证书
        allow_redirects = kwargs.pop('allow_redirects', False)  # 默认不跟随重定向

        try:
            response = session.get(
                url, params=params, timeout=timeout,
                verify=verify, allow_redirects=allow_redirects,
                **kwargs
            )
            return response
        except requests.exceptions.SSLError as e:
            print(f"SSL验证失败: {e}")
            return None
        except requests.exceptions.Timeout:
            print("请求超时")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return None

# 使用示例
session = SecureRequests.create_session()
response = SecureRequests.safe_get(
    "https://httpbin.org/get",
    params={"key": "value"},
    session=session
)
if response:
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
```

### 2.2 urllib3库

urllib3是requests的底层库，提供更细粒度的HTTP控制。

```python
import urllib3
from urllib3.util.ssl_ import create_urllib3_context

class SecureHTTPClient:
    """使用urllib3的安全HTTP客户端"""

    def __init__(self):
        # 配置TLS安全
        ctx = create_urllib3_context()
        # 设置安全密码套件
        ctx.set_ciphers('ECDHE+AESGCM:!MD5:!DSS')
        # 要求最低TLS版本
        ctx.options |= urllib3.contrib.pyopenssl.SSL_OP_NO_SSLv2
        ctx.options |= urllib3.contrib.pyopenssl.SSL_OP_NO_SSLv3

        # 创建连接池
        self.http = urllib3.PoolManager(
            ssl_context=ctx,
            cert_reqs='CERT_REQUIRED',  # 强制证书验证
            ca_certs=urllib3.get_certinfo()['certs'],  # 使用系统CA证书
            timeout=urllib3.Timeout(connect=5, read=10),
            retries=urllib3.Retry(total=3, backoff_factor=0.5),
        )

    def request(self, method, url, **kwargs):
        """安全请求方法"""
        try:
            response = self.http.request(method, url, **kwargs)
            return response
        except urllib3.exceptions.SSLError as e:
            print(f"SSL错误: {e}")
            raise
        except urllib3.exceptions.TimeoutError as e:
            print(f"超时错误: {e}")
            raise
        except urllib3.exceptions.HTTPError as e:
            print(f"HTTP错误: {e}")
            raise
```

### 2.3 socket库

socket库是Python网络编程的基础，用于底层网络通信。

```python
import socket
import struct
import threading
from concurrent.futures import ThreadPoolExecutor

class SecureSocketClient:
    """安全的socket客户端"""

    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout

    def connect_tcp(self):
        """建立TCP连接"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        # 安全选项设置
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        try:
            sock.connect((self.host, self.port))
            return sock
        except socket.timeout:
            print(f"连接超时: {self.host}:{self.port}")
            sock.close()
            return None
        except ConnectionRefusedError:
            print(f"连接被拒绝: {self.host}:{self.port}")
            sock.close()
            return None
        except Exception as e:
            print(f"连接错误: {e}")
            sock.close()
            return None

    def connect_tls(self, cert_path=None, key_path=None, ca_path=None):
        """
        建立TLS加密连接

        参数：
            cert_path: 客户端证书路径（双向认证时需要）
            key_path: 客户端私钥路径
            ca_path: CA证书路径（用于验证服务器证书）
        """
        import ssl

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.verify_mode = ssl.CERT_REQUIRED

        # 加载CA证书
        if ca_path:
            context.load_verify_locations(ca_path)

        # 加载客户端证书（双向认证）
        if cert_path and key_path:
            context.load_cert_chain(cert_path, key_path)

        # 安全配置
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.check_hostname = True

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        # 包装为TLS连接
        secure_sock = context.wrap_socket(sock, server_hostname=self.host)

        try:
            secure_sock.connect((self.host, self.port))
            # 获取服务器证书信息
            cert = secure_sock.getpeercert()
            print(f"服务器证书: {cert.get('subject', '未知')}")
            return secure_sock
        except Exception as e:
            print(f"TLS连接错误: {e}")
            secure_sock.close()
            return None

    @staticmethod
    def safe_receive(sock, buffer_size=4096, max_size=1024*1024):
        """
        安全接收数据

        防护措施：
        - 限制最大接收大小，防止内存耗尽
        - 超时处理
        """
        total_data = b""
        try:
            while len(total_data) < max_size:
                data = sock.recv(buffer_size)
                if not data:
                    break
                total_data += data
                if len(data) < buffer_size:
                    break
            return total_data
        except socket.timeout:
            print("接收超时")
            return total_data
        except Exception as e:
            print(f"接收错误: {e}")
            return total_data
```

### 2.4 ssl库

```python
import ssl
import socket

class SSLSecurityChecker:
    """SSL/TLS安全配置检查器"""

    @staticmethod
    def check_ssl_config(hostname, port=443):
        """
        检查目标服务器的SSL/TLS配置

        检查项：
        - 证书有效性
        - 支持的TLS版本
        - 密码套件强度
        - 证书链完整性
        """
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        result = {
            'hostname': hostname,
            'port': port,
            'cert_valid': False,
            'tls_version': None,
            'cipher': None,
            'issuer': None,
            'subject': None,
            'not_after': None,
        }

        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    result['cert_valid'] = True
                    result['tls_version'] = ssock.version()
                    result['cipher'] = ssock.cipher()

                    cert = ssock.getpeercert()
                    result['issuer'] = dict(x[0] for x in cert.get('issuer', []))
                    result['subject'] = dict(x[0] for x in cert.get('subject', []))
                    result['not_after'] = cert.get('notAfter')
        except ssl.SSLError as e:
            print(f"SSL错误: {e}")
        except Exception as e:
            print(f"连接错误: {e}")

        return result

    @staticmethod
    def test_weak_ciphers(hostname, port=443):
        """
        测试服务器是否支持弱密码套件

        弱密码套件包括：
        - NULL认证/加密
        - RC4/DES等过时算法
        - MD5哈希
        - 导出级加密
        """
        weak_ciphers = 'NULL:EXPORT:LOW:RC4:MD5:DES'
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.set_ciphers(weak_ciphers)

        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock) as ssock:
                    print(f"[!] 服务器支持弱密码套件: {ssock.cipher()}")
                    return True
        except ssl.SSLError:
            print("[+] 服务器不支持弱密码套件")
            return False
        except Exception as e:
            print(f"测试失败: {e}")
            return False
```

### 2.5 hashlib库

```python
import hashlib
import os

class HashUtils:
    """哈希计算工具类"""

    # 安全哈希算法
    SECURE_ALGORITHMS = ['sha256', 'sha384', 'sha512', 'sha3_256', 'blake2b']
    # 不安全哈希算法（仅用于兼容性）
    INSECURE_ALGORITHMS = ['md5', 'sha1']

    @staticmethod
    def hash_data(data, algorithm='sha256'):
        """
        计算数据的哈希值

        安全建议：
        - 使用SHA-256或更强的算法
        - 避免使用MD5/SHA1（已不安全）
        - 密码哈希应使用专门的函数（如bcrypt）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        h = hashlib.new(algorithm)
        h.update(data)
        return h.hexdigest()

    @staticmethod
    def hash_file(filepath, algorithm='sha256', chunk_size=8192):
        """
        计算大文件的哈希值（分块读取）

        适用于大文件，避免内存溢出
        """
        h = hashlib.new(algorithm)
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()
        except FileNotFoundError:
            print(f"文件不存在: {filepath}")
            return None
        except PermissionError:
            print(f"权限不足: {filepath}")
            return None

    @staticmethod
    def hmac_hash(key, data, algorithm='sha256'):
        """
        使用HMAC进行消息认证

        HMAC结合了密钥和哈希函数，提供数据完整性和认证
        """
        import hmac
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(data, str):
            data = data.encode('utf-8')

        return hmac.new(key, data, algorithm).hexdigest()

    @staticmethod
    def verify_hmac(key, data, expected_hash, algorithm='sha256'):
        """验证HMAC（使用恒定时间比较防止时序攻击）"""
        import hmac
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(data, str):
            data = data.encode('utf-8')

        computed = hmac.new(key, data, algorithm).hexdigest()
        # hmac.compare_digest使用恒定时间比较，防止时序攻击
        return hmac.compare_digest(computed, expected_hash)
```

### 2.6 hmac库

```python
import hmac
import hashlib
import time

class HMACAuth:
    """HMAC认证工具"""

    @staticmethod
    def generate_token(secret, payload, ttl=3600):
        """
        生成带过期时间的HMAC令牌

        格式: timestamp.payload.signature
        """
        timestamp = str(int(time.time()) + ttl)
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{timestamp}.{payload}.{signature}"

    @staticmethod
    def verify_token(secret, token):
        """
        验证HMAC令牌

        返回: (是否有效, payload)
        """
        try:
            parts = token.split('.', 2)
            if len(parts) != 3:
                return False, None

            timestamp, payload, signature = parts

            # 验证签名
            message = f"{timestamp}.{payload}"
            expected_sig = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_sig):
                return False, None

            # 验证过期时间
            if int(time.time()) > int(timestamp):
                return False, None  # 令牌已过期

            return True, payload
        except (ValueError, AttributeError):
            return False, None
```

### 2.7 secrets库

```python
import secrets
import string

class SecureRandom:
    """安全随机数生成工具"""

    @staticmethod
    def generate_password(length=16):
        """
        生成安全密码

        使用secrets模块而非random模块
        random模块不适用于安全场景
        """
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # 使用secrets确保密码学安全
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    @staticmethod
    def generate_token(length=32):
        """生成安全令牌"""
        return secrets.token_hex(length)

    @staticmethod
    def generate_url_safe_token(length=32):
        """生成URL安全令牌"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key(prefix='sk'):
        """生成API密钥"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"

    @staticmethod
    def constant_time_compare(a, b):
        """
        恒定时间比较

        防止时序攻击：比较操作不因输入不同而耗时不同
        """
        return secrets.compare_digest(a, b)

# 注意：以下是不安全的写法
# import random
# token = random.randint(1000, 9999)  # 不安全！random不是密码学安全的

# 正确写法
# token = secrets.randbelow(9000) + 1000  # 安全
```

---

## 3. Web请求安全

### 3.1 SSRF防护

SSRF（Server-Side Request Forgery）是服务器端请求伪造漏洞，允许攻击者让服务器发起任意请求。

```python
import ipaddress
import socket
import re
from urllib.parse import urlparse

class SSRFProtector:
    """SSRF防护工具"""

    # 禁止访问的IP范围
    BLOCKED_RANGES = [
        # IPv4回环地址
        ipaddress.ip_network('127.0.0.0/8'),
        # IPv4私有地址
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        # IPv4链路本地
        ipaddress.ip_network('169.254.0.0/16'),
        # IPv4保留地址
        ipaddress.ip_network('0.0.0.0/8'),
        ipaddress.ip_network('100.64.0.0/10'),  # CGN
        # IPv6回环
        ipaddress.ip_network('::1/128'),
        # IPv6私有
        ipaddress.ip_network('fc00::/7'),
        # IPv6链路本地
        ipaddress.ip_network('fe80::/10'),
        # 云元数据服务
        ipaddress.ip_network('169.254.169.254/32'),
        # 其他元数据
        ipaddress.ip_network('fd00::/8'),
    ]

    # 允许的协议
    ALLOWED_SCHEMES = {'http', 'https'}

    # 禁止的协议
    BLOCKED_SCHEMES = {'file', 'ftp', 'gopher', 'dict', 'ldap', 'tftp',
                       'sftp', 'jar', 'netdoc', 'expect', 'php'}

    @classmethod
    def is_safe_url(cls, url):
        """
        检查URL是否安全

        检查项：
        1. 协议是否允许
        2. 域名解析后是否为内网IP
        3. 是否使用IP字面量访问内网
        4. 是否使用特殊编码绕过
        """
        try:
            parsed = urlparse(url)

            # 检查协议
            if parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
                return False, f"禁止的协议: {parsed.scheme}"

            hostname = parsed.hostname
            if not hostname:
                return False, "无效的主机名"

            # 检查是否是IP字面量
            try:
                ip = ipaddress.ip_address(hostname)
                if cls.is_blocked_ip(ip):
                    return False, f"禁止的IP地址: {ip}"
            except ValueError:
                # 不是IP字面量，进行DNS解析
                pass

            # DNS解析并检查
            try:
                # 使用getaddrinfo获取所有解析结果
                results = socket.getaddrinfo(hostname, None)
                for family, type_, proto, canonname, sockaddr in results:
                    ip_str = sockaddr[0]
                    ip = ipaddress.ip_address(ip_str)
                    if cls.is_blocked_ip(ip):
                        return False, f"域名解析到内网IP: {hostname} -> {ip}"
            except socket.gaierror:
                return False, f"DNS解析失败: {hostname}"

            # 检查URL编码绕过
            if '%' in url:
                decoded = cls._decode_url(url)
                if decoded != url:
                    safe, reason = cls.is_safe_url(decoded)
                    if not safe:
                        return False, f"URL编码绕过检测: {reason}"

            # 检查特殊字符
            if re.search(r'[#@]', hostname):
                return False, "主机名包含特殊字符"

            return True, "URL安全"
        except Exception as e:
            return False, f"检查异常: {e}"

    @classmethod
    def is_blocked_ip(cls, ip):
        """检查IP是否在禁止范围"""
        for network in cls.BLOCKED_RANGES:
            if ip in network:
                return True
        return False

    @staticmethod
    def _decode_url(url):
        """解码URL编码"""
        from urllib.parse import unquote
        return unquote(url)

    @classmethod
    def safe_request(cls, url, method='GET', **kwargs):
        """
        安全请求方法

        在发送请求前进行SSRF检查
        """
        safe, reason = cls.is_safe_url(url)
        if not safe:
            raise ValueError(f"SSRF防护: {reason}")

        # 二次检查：使用解析后的IP直接请求
        # 防止TOCTOU（Time-of-Check-Time-of-Use）漏洞
        import requests
        response = requests.request(method, url, **kwargs)

        # 检查重定向是否指向内网
        if response.history:
            for redirect in response.history:
                safe, reason = cls.is_safe_url(redirect.url)
                if not safe:
                    raise ValueError(f"重定向SSRF: {reason}")

        return response
```

### 3.2 SSL/TLS验证

```python
import ssl
import requests
from requests.adapters import HTTPAdapter

class SSLVerifier:
    """SSL/TLS验证工具"""

    @staticmethod
    def verify_cert(hostname, port=443):
        """
        验证服务器SSL证书

        检查项：
        - 证书是否有效
        - 主机名是否匹配
        - 证书链是否完整
        - 是否已过期
        """
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        'valid': True,
                        'subject': dict(x[0] for x in cert['subject']),
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'version': cert.get('version'),
                        'serial_number': cert.get('serialNumber'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'san': cert.get('subjectAltName', []),
                    }
        except ssl.CertificateError as e:
            return {'valid': False, 'error': f'证书验证失败: {e}'}
        except ssl.SSLError as e:
            return {'valid': False, 'error': f'SSL错误: {e}'}
        except Exception as e:
            return {'valid': False, 'error': f'连接错误: {e}'}

    @staticmethod
    def pin_certificate(hostname, port=443, expected_cert_hash=None):
        """
        证书锁定（Certificate Pinning）

        通过预设证书哈希值，防止中间人攻击
        """
        context = ssl.create_default_context()

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                der_cert = ssock.getpeercert(binary_form=True)
                cert_hash = hashlib.sha256(der_cert).hexdigest()

                if expected_cert_hash and cert_hash != expected_cert_hash:
                    raise ValueError(f"证书哈希不匹配! 期望: {expected_cert_hash}, 实际: {cert_hash}")

                return cert_hash

# 安全请求示例：强制SSL验证
def secure_get(url):
    """强制SSL验证的GET请求"""
    session = requests.Session()
    session.verify = True  # 强制证书验证
    session.cert = None  # 不使用客户端证书

    # 设置安全头
    session.headers.update({
        'User-Agent': 'SecureClient/1.0',
    })

    response = session.get(url, timeout=10)
    return response

# 注意：以下代码是不安全的
# response = requests.get(url, verify=False)  # 禁用SSL验证！危险！
```

### 3.3 重定向安全

```python
import requests
from urllib.parse import urlparse

class RedirectProtector:
    """重定向安全控制"""

    # 最大重定向次数
    MAX_REDIRECTS = 5

    # 允许重定向的域名白名单
    ALLOWED_REDIRECT_DOMAINS = {
        'example.com', 'www.example.com', 'api.example.com'
    }

    @classmethod
    def safe_request_with_redirects(cls, url, method='GET', **kwargs):
        """
        安全的重定向请求

        防护措施：
        - 限制最大重定向次数
        - 验证重定向目标域名
        - 防止开放重定向漏洞
        """
        kwargs['allow_redirects'] = False  # 手动处理重定向
        redirect_count = 0
        current_url = url

        while redirect_count < cls.MAX_REDIRECTS:
            response = requests.request(method, current_url, **kwargs)

            if response.status_code not in [301, 302, 303, 307, 308]:
                return response

            redirect_url = response.headers.get('Location', '')
            if not redirect_url:
                return response

            # 验证重定向目标
            safe, reason = cls._check_redirect_url(redirect_url)
            if not safe:
                raise ValueError(f"不安全的重定向: {reason}")

            current_url = redirect_url
            redirect_count += 1

        raise ValueError(f"超过最大重定向次数: {cls.MAX_REDIRECTS}")

    @classmethod
    def _check_redirect_url(cls, url):
        """检查重定向URL是否安全"""
        parsed = urlparse(url)

        # 检查协议
        if parsed.scheme and parsed.scheme not in ['http', 'https']:
            return False, f"不允许的协议: {parsed.scheme}"

        # 检查域名白名单
        hostname = parsed.hostname
        if hostname and hostname not in cls.ALLOWED_REDIRECT_DOMAINS:
            return False, f"重定向到非白名单域名: {hostname}"

        return True, "安全"

    @staticmethod
    def check_open_redirect(url, redirect_param='redirect'):
        """
        检测开放重定向漏洞

        测试URL参数是否可以被用于重定向到外部站点
        """
        test_payloads = [
            'https://evil.com',
            '//evil.com',
            '/\\evil.com',
            'https:evil.com',
            'https://evil.com@example.com',
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
        ]

        results = []
        for payload in test_payloads:
            test_url = f"{url}?{redirect_param}={payload}"
            try:
                response = requests.get(test_url, allow_redirects=False, timeout=10)
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location or 'javascript:' in location:
                        results.append({
                            'payload': payload,
                            'redirect_to': location,
                            'vulnerable': True,
                        })
            except Exception:
                continue

        return results
```

### 3.4 Cookie安全处理

```python
class CookieSecurity:
    """Cookie安全处理"""

    @staticmethod
    def set_secure_cookie(response, name, value, max_age=3600):
        """
        设置安全Cookie

        安全属性：
        - HttpOnly: 防止XSS窃取Cookie
        - Secure: 仅通过HTTPS传输
        - SameSite: 防止CSRF
        """
        response.set_cookie(
            name=name,
            value=value,
            max_age=max_age,
            httponly=True,       # 防止JavaScript访问
            secure=True,          # 仅HTTPS传输
            samesite='Strict',   # 严格的SameSite策略
            path='/',
        )
        return response

    @staticmethod
    def check_cookie_security(cookie_header):
        """检查Cookie安全属性"""
        issues = []

        if 'HttpOnly' not in cookie_header:
            issues.append('缺少HttpOnly属性')
        if 'Secure' not in cookie_header:
            issues.append('缺少Secure属性')
        if 'SameSite' not in cookie_header:
            issues.append('缺少SameSite属性')

        return {
            'issues': issues,
            'secure': len(issues) == 0,
        }
```

---

## 4. 文件操作安全

### 4.1 路径遍历防护

```python
import os
import os.path
import shutil

class PathTraversalProtector:
    """路径遍历防护"""

    @staticmethod
    def safe_join(base_path, user_path):
        """
        安全的路径拼接

        防止路径遍历攻击（如 ../../etc/passwd）

        原理：检查拼接后的路径是否仍在基础目录内
        """
        # 规范化基础路径
        base_path = os.path.abspath(base_path)

        # 规范化拼接后的路径
        full_path = os.path.abspath(os.path.join(base_path, user_path))

        # 检查最终路径是否在基础目录内
        if not full_path.startswith(base_path + os.sep) and full_path != base_path:
            raise ValueError(
                f"路径遍历检测! 基础路径: {base_path}, "
                f"请求路径: {user_path}, 实际路径: {full_path}"
            )

        return full_path

    @staticmethod
    def safe_read_file(base_path, filename):
        """
        安全读取文件

        确保文件路径在允许的目录范围内
        """
        # 检查路径遍历
        full_path = PathTraversalProtector.safe_join(base_path, filename)

        # 检查是否是符号链接
        if os.path.islink(full_path):
            raise ValueError(f"拒绝读取符号链接: {full_path}")

        # 检查文件是否存在且可读
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"文件不存在: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def validate_filename(filename):
        """
        验证文件名安全性

        检查项：
        - 不包含路径分隔符
        - 不包含..路径遍历
        - 不为空
        - 不包含特殊字符
        """
        if not filename:
            raise ValueError("文件名为空")

        # 检查路径遍历
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError(f"文件名包含路径遍历字符: {filename}")

        # 检查特殊字符
        import re
        if re.search(r'[<>"|?*:&;]', filename):
            raise ValueError(f"文件名包含特殊字符: {filename}")

        # 检查文件名长度
        if len(filename) > 255:
            raise ValueError("文件名过长")

        # 检查保留名称（Windows）
        windows_reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2',
                          'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'LPT4'}
        if filename.upper().split('.')[0] in windows_reserved:
            raise ValueError(f"文件名使用保留名称: {filename}")

        return True

# 使用示例
try:
    content = PathTraversalProtector.safe_read_file('/var/www/uploads', '../../../etc/passwd')
except ValueError as e:
    print(f"安全防护触发: {e}")
```

### 4.2 Zip Slip漏洞

```python
import zipfile
import os

class ZipSlipProtector:
    """Zip Slip漏洞防护"""

    @staticmethod
    def safe_extract(zip_path, extract_to):
        """
        安全解压ZIP文件

        Zip Slip漏洞：压缩包中的文件名包含路径遍历字符，
        解压时可能覆盖系统文件。

        防护措施：检查每个文件是否在目标目录内
        """
        extract_to = os.path.abspath(extract_to)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                # 规范化路径
                member_path = os.path.abspath(os.path.join(extract_to, member))

                # 检查路径是否在目标目录内
                if not member_path.startswith(extract_to + os.sep):
                    raise ValueError(
                        f"Zip Slip检测! 文件: {member}, "
                        f"解压路径: {member_path}"
                    )

                # 检查是否是符号链接
                if os.path.islink(member_path):
                    raise ValueError(f"拒绝解压符号链接: {member}")

            # 安全解压
            zf.extractall(extract_to)

    @staticmethod
    def safe_extract_with_size_limit(zip_path, extract_to, max_size=100*1024*1024):
        """
        带大小限制的安全解压

        防止ZIP炸弹攻击
        """
        extract_to = os.path.abspath(extract_to)
        total_size = 0

        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                info = zf.getinfo(member)
                total_size += info.file_size

                # 检查总大小是否超过限制
                if total_size > max_size:
                    raise ValueError(
                        f"解压大小超过限制: {total_size} > {max_size}"
                    )

                # 检查压缩率（异常压缩率可能是ZIP炸弹）
                if info.compress_size > 0:
                    ratio = info.file_size / info.compress_size
                    if ratio > 100:
                        print(f"警告: 高压缩率文件: {member} (比率: {ratio:.1f})")

            ZipSlipProtector.safe_extract(zip_path, extract_to)
```

### 4.3 反序列化安全

```python
import pickle
import json

class DeserializationSecurity:
    """反序列化安全"""

    @staticmethod
    def safe_pickle_load(data):
        """
        安全的pickle反序列化

        pickle反序列化可以执行任意代码，极其危险！
        禁止反序列化不受信任的数据！
        """
        # 安全建议：不要使用pickle反序列化不可信数据
        # 应使用JSON等安全格式替代
        raise NotImplementedError(
            "禁止使用pickle反序列化不可信数据！请使用JSON替代。"
        )

    @staticmethod
    def safe_json_load(data):
        """
        安全的JSON反序列化

        JSON是安全的反序列化格式
        """
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}")

    @staticmethod
    def restricted_pickle_load(data, allowed_classes=None):
        """
        受限的pickle反序列化（仅限必须使用pickle的场景）

        通过重写Unpickler.find_class来限制可加载的类
        """
        import io
        import pickle as _pickle

        class RestrictedUnpickler(_pickle.Unpickler):
            def find_class(self, module, name):
                if allowed_classes and (module, name) in allowed_classes:
                    return super().find_class(module, name)
                raise _pickle.UnpicklingError(
                    f"禁止反序列化: {module}.{name}"
                )

        return RestrictedUnpickler(io.BytesIO(data)).load()

# 安全建议：优先使用JSON而非pickle
# data = json.dumps(obj)  # 安全
# obj = json.loads(data)   # 安全

# 危险写法：
# obj = pickle.loads(untrusted_data)  # 极度危险！可执行任意代码
```

### 4.4 临时文件安全

```python
import tempfile
import os

class TempFileSecurity:
    """临时文件安全"""

    @staticmethod
    def create_secure_temp_file(suffix='', prefix='tmp'):
        """
        安全创建临时文件

        安全措施：
        - 使用mkstemp而非mktemp（后者有竞争条件）
        - 设置适当的文件权限
        - 文件不可预测的文件名
        """
        # mkstemp创建文件时使用O_EXCL标志，防止符号链接攻击
        fd, path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=tempfile.gettempdir()
        )

        # 设置文件权限为600（仅所有者可读写）
        os.chmod(path, 0o600)

        return fd, path

    @staticmethod
    def create_secure_temp_dir():
        """安全创建临时目录"""
        # mkdtemp创建目录时权限为700
        path = tempfile.mkdtemp()
        os.chmod(path, 0o700)
        return path

    @staticmethod
    def safe_cleanup(path):
        """安全清理临时文件"""
        try:
            if os.path.isdir(path):
                import shutil
                shutil.rmtree(path)
            else:
                os.remove(path)
        except Exception as e:
            print(f"清理失败: {e}")
```

---

## 5. 密码学编程

### 5.1 hashlib哈希算法

```python
import hashlib

class CryptoHash:
    """密码学哈希工具"""

    @staticmethod
    def sha256(data):
        """SHA-256哈希"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data):
        """SHA-512哈希"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def blake2b(data, digest_size=64):
        """BLAKE2b哈希（高性能安全哈希）"""
        if isinstance(data, str):
            data = data.encode()
        h = hashlib.blake2b(data, digest_size=digest_size)
        return h.hexdigest()

    @staticmethod
    def sha3_256(data):
        """SHA3-256哈希（Keccak）"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha3_256(data).hexdigest()

    @staticmethod
    def kdf_derive_key(password, salt, iterations=100000, dklen=32):
        """
        PBKDF2密钥派生

        从密码派生加密密钥
        参数：
            password: 用户密码
            salt: 随机盐值
            iterations: 迭代次数（越高越安全，最低100000）
            dklen: 派生密钥长度
        """
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            iterations,
            dklen
        ).hex()
```

### 5.2 hmac消息认证码

```python
import hmac
import hashlib

class CryptoHMAC:
    """HMAC消息认证码工具"""

    @staticmethod
    def compute_hmac(key, message, algorithm='sha256'):
        """计算HMAC"""
        if isinstance(key, str):
            key = key.encode()
        if isinstance(message, str):
            message = message.encode()
        return hmac.new(key, message, getattr(hashlib, algorithm)).hexdigest()

    @staticmethod
    def verify_hmac(key, message, expected_mac, algorithm='sha256'):
        """
        验证HMAC（恒定时间比较）

        使用compare_digest防止时序攻击
        """
        if isinstance(key, str):
            key = key.encode()
        if isinstance(message, str):
            message = message.encode()

        computed = hmac.new(key, message, getattr(hashlib, algorithm)).hexdigest()
        return hmac.compare_digest(computed, str(expected_mac))

    @staticmethod
    def hotp(secret, counter, digits=6, algorithm='sha1'):
        """
        HOTP（基于计数器的一次性密码）

        用于实现OTP认证
        """
        import struct
        if isinstance(secret, str):
            secret = secret.encode()

        # 将计数器转为8字节
        counter_bytes = struct.pack('>Q', counter)

        # 计算HMAC
        h = hmac.new(secret, counter_bytes, getattr(hashlib, algorithm))
        digest = h.digest()

        # 动态截断
        offset = digest[-1] & 0x0F
        code = struct.unpack('>I', digest[offset:offset+4])[0] & 0x7FFFFFFF

        return str(code % (10 ** digits)).zfill(digits)

    @staticmethod
    def totp(secret, time_step=30, digits=6):
        """
        TOTP（基于时间的一次性密码）

        类似Google Authenticator
        """
        import time
        counter = int(time.time()) // time_step
        return CryptoHMAC.hotp(secret, counter, digits)
```

### 5.3 Cryptography库

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class CryptoUtils:
    """Cryptography库工具类"""

    # 对称加密
    @staticmethod
    def generate_fernet_key():
        """生成Fernet加密密钥（256位）"""
        return Fernet.generate_key()

    @staticmethod
    def fernet_encrypt(key, data):
        """Fernet对称加密"""
        if isinstance(data, str):
            data = data.encode()
        f = Fernet(key)
        return f.encrypt(data)

    @staticmethod
    def fernet_decrypt(key, encrypted_data):
        """Fernet对称解密"""
        f = Fernet(key)
        return f.decrypt(encrypted_data)

    # AES加密
    @staticmethod
    def aes_encrypt(key, plaintext, mode='GCM'):
        """
        AES加密

        推荐使用GCM模式（提供认证加密）
        """
        if isinstance(key, str):
            key = key.encode()
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()

        # 生成随机IV
        iv = os.urandom(16)

        if mode == 'GCM':
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            return {
                'ciphertext': ciphertext,
                'iv': iv,
                'tag': encryptor.tag,
            }
        elif mode == 'CBC':
            # CBC需要填充
            from cryptography.hazmat.primitives import padding as sym_padding
            padder = sym_padding.PKCS7(128).padder()
            padded = padder.update(plaintext) + padder.finalize()

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded) + encryptor.finalize()
            return {
                'ciphertext': ciphertext,
                'iv': iv,
            }

    @staticmethod
    def aes_decrypt(key, encrypted_data, mode='GCM'):
        """AES解密"""
        if isinstance(key, str):
            key = key.encode()

        if mode == 'GCM':
            cipher = Cipher(algorithms.AES(key), modes.GCM(
                encrypted_data['iv'], encrypted_data['tag']
            ))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()
            return plaintext
        elif mode == 'CBC':
            cipher = Cipher(algorithms.AES(key), modes.CBC(encrypted_data['iv']))
            decryptor = cipher.decryptor()
            padded = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()

            from cryptography.hazmat.primitives import padding as sym_padding
            unpadder = sym_padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded) + unpadder.finalize()
            return plaintext

    # RSA非对称加密
    @staticmethod
    def generate_rsa_keypair(key_size=2048):
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        return private_key, private_key.public_key()

    @staticmethod
    def rsa_encrypt(public_key, plaintext):
        """RSA公钥加密"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    @staticmethod
    def rsa_decrypt(private_key, ciphertext):
        """RSA私钥解密"""
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    @staticmethod
    def rsa_sign(private_key, data):
        """RSA数字签名"""
        if isinstance(data, str):
            data = data.encode()
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def rsa_verify(public_key, data, signature):
        """RSA签名验证"""
        if isinstance(data, str):
            data = data.encode()
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    # 密钥派生
    @staticmethod
    def derive_key_from_password(password, salt=None):
        """
        从密码派生密钥

        使用PBKDF2-HMAC-SHA256
        """
        if salt is None:
            salt = os.urandom(16)
        if isinstance(password, str):
            password = password.encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
        return key, salt
```

### 5.4 PyCryptodome库

```python
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256, HMAC

class PyCryptodomeUtils:
    """PyCryptodome库工具"""

    @staticmethod
    def aes_gcm_encrypt(key, plaintext, aad=None):
        """
        AES-GCM认证加密

        GCM模式提供机密性和完整性
        aad: 附加认证数据（不加密但需验证完整性）
        """
        if isinstance(key, str):
            key = key.encode()
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()

        nonce = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        if aad:
            if isinstance(aad, str):
                aad = aad.encode()
            cipher.update(aad)

        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'tag': tag,
        }

    @staticmethod
    def aes_gcm_decrypt(key, encrypted_data, aad=None):
        """AES-GCM解密"""
        if isinstance(key, str):
            key = key.encode()

        cipher = AES.new(key, AES.MODE_GCM, nonce=encrypted_data['nonce'])

        if aad:
            if isinstance(aad, str):
                aad = aad.encode()
            cipher.update(aad)

        plaintext = cipher.decrypt_and_verify(
            encrypted_data['ciphertext'],
            encrypted_data['tag']
        )
        return plaintext
```

### 5.5 密码存储与验证

```python
import hashlib
import os
import hmac

class PasswordSecurity:
    """密码安全存储与验证"""

    # Argon2（推荐，需安装argon2-cffi）
    @staticmethod
    def hash_password_argon2(password):
        """
        使用Argon2哈希密码（推荐）

        Argon2是密码哈希竞赛的获胜者
        """
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher(
                time_cost=3,      # 迭代次数
                memory_cost=65536,  # 内存使用（KB）
                parallelism=4,     # 并行度
                hash_len=32,       # 哈希长度
                salt_len=16,       # 盐长度
            )
            return ph.hash(password)
        except ImportError:
            # 回退到PBKDF2
            return PasswordSecurity.hash_password_pbkdf2(password)

    @staticmethod
    def verify_password_argon2(password, hash_str):
        """验证Argon2密码"""
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            try:
                ph.verify(hash_str, password)
                return True
            except Exception:
                return False
        except ImportError:
            return PasswordSecurity.verify_password_pbkdf2(password, hash_str)

    # PBKDF2
    @staticmethod
    def hash_password_pbkdf2(password, iterations=100000):
        """
        使用PBKDF2哈希密码

        参数：
            password: 明文密码
            iterations: 迭代次数（最低100000）
        """
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, 32)
        return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"

    @staticmethod
    def verify_password_pbkdf2(password, hash_str):
        """验证PBKDF2密码"""
        try:
            parts = hash_str.split('$')
            if len(parts) != 4:
                return False
            algorithm = parts[0]
            iterations = int(parts[1])
            salt = bytes.fromhex(parts[2])
            expected_dk = parts[3]

            dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, 32)
            # 恒定时间比较
            return hmac.compare_digest(dk.hex(), expected_dk)
        except Exception:
            return False

    # bcrypt（可选）
    @staticmethod
    def hash_password_bcrypt(password):
        """使用bcrypt哈希密码"""
        try:
            import bcrypt
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode(), salt).decode()
        except ImportError:
            return PasswordSecurity.hash_password_pbkdf2(password)

    @staticmethod
    def verify_password_bcrypt(password, hash_str):
        """验证bcrypt密码"""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), hash_str.encode())
        except ImportError:
            return PasswordSecurity.verify_password_pbkdf2(password, hash_str)

# 使用示例
password = "MySecurePassword123!"
hashed = PasswordSecurity.hash_password_argon2(password)
print(f"哈希: {hashed}")
print(f"验证: {PasswordSecurity.verify_password_argon2(password, hashed)}")
```

---

## 6. 网络编程安全

### 6.1 socket编程基础

```python
import socket
import struct

class NetworkTools:
    """网络编程工具"""

    @staticmethod
    def get_local_ip():
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'

    @staticmethod
    def dns_lookup(domain, record_type='A'):
        """DNS查询"""
        import dns.resolver
        try:
            answers = dns.resolver.resolve(domain, record_type)
            return [str(r) for r in answers]
        except Exception as e:
            return []

    @staticmethod
    def reverse_dns(ip):
        """反向DNS查询"""
        try:
            hostname, alias, ip_list = socket.gethostbyaddr(ip)
            return hostname
        except socket.herror:
            return None
        except Exception:
            return None
```

### 6.2 端口扫描器实现

```python
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

class PortScanner:
    """多线程端口扫描器"""

    COMMON_PORTS = {
        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
        53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
        443: 'HTTPS', 445: 'SMB', 993: 'IMAPS', 995: 'POP3S',
        1433: 'MSSQL', 3306: 'MySQL', 3389: 'RDP',
        5432: 'PostgreSQL', 6379: 'Redis', 8080: 'HTTP-Alt',
    }

    @staticmethod
    def scan_port(host, port, timeout=2):
        """扫描单个端口"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    @staticmethod
    def scan_host(host, ports=None, threads=10, timeout=2):
        """扫描主机端口"""
        if ports is None:
            ports = list(PortScanner.COMMON_PORTS.keys())

        results = {}
        lock = threading.Lock()

        def scan(port):
            if PortScanner.scan_port(host, port, timeout):
                with lock:
                    service = PortScanner.COMMON_PORTS.get(port, '未知')
                    results[port] = f'open ({service})'

        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(scan, ports)

        return results

    @staticmethod
    def grab_banner(host, port, timeout=5):
        """获取服务Banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            if port in [80, 8080, 443]:
                sock.send(b'HEAD / HTTP/1.0\r\nHost: ' +
                         host.encode() + b'\r\n\r\n')

            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            return banner.split('\n')[0] if banner else ''
        except Exception:
            return ''
```

### 6.3 协议解析

```python
import struct

class ProtocolParser:
    """网络协议解析工具"""

    @staticmethod
    def parse_ipv4_header(data):
        """
        解析IPv4头部

        用于分析网络数据包
        """
        if len(data) < 20:
            return None

        # 解析IP头部字段
        version_ihl = data[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        header_length = ihl * 4

        ttl = data[8]
        protocol = data[9]
        src_ip = '.'.join(str(b) for b in data[12:16])
        dst_ip = '.'.join(str(b) for b in data[16:20])

        return {
            'version': version,
            'header_length': header_length,
            'ttl': ttl,
            'protocol': protocol,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'protocol_name': {1: 'ICMP', 6: 'TCP', 17: 'UDP'}.get(protocol, '未知'),
        }

    @staticmethod
    def parse_tcp_header(data):
        """解析TCP头部"""
        if len(data) < 20:
            return None

        src_port, dst_port, seq, ack = struct.unpack('!HHLL', data[:12])
        offset_reserved = data[12]
        offset = (offset_reserved >> 4) * 4
        flags = data[13]

        return {
            'src_port': src_port,
            'dst_port': dst_port,
            'seq': seq,
            'ack': ack,
            'header_length': offset,
            'flags': {
                'fin': bool(flags & 0x01),
                'syn': bool(flags & 0x02),
                'rst': bool(flags & 0x04),
                'psh': bool(flags & 0x08),
                'ack': bool(flags & 0x10),
                'urg': bool(flags & 0x20),
            },
        }
```

### 6.4 SSL/TLS安全通信

```python
import ssl
import socket

class SecureCommunication:
    """SSL/TLS安全通信"""

    @staticmethod
    def create_ssl_server(host, port, certfile, keyfile):
        """创建SSL服务器"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)

        # 安全配置
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE+AESGCM:!MD5:!DSS')

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)

        ssl_server = context.wrap_socket(server, server_side=True)
        return ssl_server

    @staticmethod
    def create_ssl_client(host, port, ca_certs=None):
        """创建SSL客户端"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        if ca_certs:
            context.load_verify_locations(ca_certs)

        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        sock = socket.create_connection((host, port), timeout=10)
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        return ssl_sock
```

---

## 7. 正则表达式安全

### 7.1 ReDoS漏洞原理

ReDoS（Regular Expression Denial of Service）是正则表达式拒绝服务攻击。某些正则表达式在处理特定输入时会导致指数级时间复杂度。

```python
import re
import time

class ReDoSDemo:
    """ReDoS漏洞演示"""

    @staticmethod
    def demonstrate_redos():
        """演示ReDoS漏洞"""

        # 危险正则表达式：(.+)+ 包含嵌套量词
        evil_regex = r'^(a+)+$'

        # 正常输入 - 快速匹配
        normal_input = 'aaaa'
        start = time.time()
        re.match(evil_regex, normal_input)
        normal_time = time.time() - start
        print(f"正常输入 ({len(normal_input)}字符): {normal_time:.6f}秒")

        # 恶意输入 - 指数级时间
        evil_input = 'a' * 30 + '!'
        start = time.time()
        re.match(evil_regex, evil_input)
        evil_time = time.time() - start
        print(f"恶意输入 ({len(evil_input)}字符): {evil_time:.6f}秒")
        print(f"时间倍数: {evil_time/normal_time:.0f}x")

    @staticmethod
    def dangerous_patterns():
        """列出常见的危险正则模式"""
        return [
            (r'(\d+)+', '嵌套量词 - 数字+量词嵌套'),
            (r'(a+)+', '嵌套量词 - 字母+量词嵌套'),
            (r'(.+)+', '嵌套量词 - 通配符+量词嵌套'),
            (r'(\w+)*', '嵌套量词 - 单词字符+量词嵌套'),
            (r'(a|a)*b', '重叠交替 - 重复的分支'),
            (r'(a+){2,}', '量词上限 - 重复的量词'),
            (r'^(a+)+$', '锚定嵌套 - 带锚定的嵌套'),
        ]
```

### 7.2 ReDoS防护策略

```python
import re
import signal
import time

class ReDoSProtector:
    """ReDoS防护工具"""

    # 危险正则模式
    DANGEROUS_PATTERNS = [
        r'\(.*[+*].*\)[+*]',  # 嵌套量词
        r'\([^)]*[+*][^)]*\)[+*]',  # 分组内量词后又有量词
        r'(\w+)\1+',  # 反向引用+量词
    ]

    @classmethod
    def check_regex_safety(cls, pattern):
        """
        检查正则表达式的安全性

        通过静态分析识别潜在的危险模式
        """
        for danger in cls.DANGEROUS_PATTERNS:
            if re.search(danger, pattern):
                return {
                    'safe': False,
                    'issue': f"检测到危险模式: {danger}",
                    'pattern': pattern,
                }

        # 检查是否有过度回溯的潜在风险
        quantifiers = len(re.findall(r'[+*?{]', pattern))
        groups = len(re.findall(r'\(', pattern))

        if quantifiers > 5 and groups > 3:
            return {
                'safe': False,
                'issue': f"正则过于复杂 ({quantifiers}个量词, {groups}个分组)",
                'pattern': pattern,
            }

        return {'safe': True, 'pattern': pattern}

    @staticmethod
    def safe_regex_match(pattern, text, timeout=2.0):
        """
        安全的正则匹配（带超时）

        使用信号超时防止ReDoS
        """
        # 仅Unix系统支持signal.alarm
        if hasattr(signal, 'SIGALRM'):
            def handler(signum, frame):
                raise TimeoutError("正则匹配超时，可能存在ReDoS")

            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.setitimer(signal.ITIMER_REAL, timeout)

            try:
                result = re.match(pattern, text)
                signal.setitimer(signal.ITIMER_REAL, 0)
                return result
            except TimeoutError:
                return None
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Windows系统：使用简单超时
            start = time.time()
            # 使用正则的扫描限制
            return re.match(pattern, text)

    @staticmethod
    def safe_alternative(pattern, text):
        """
        使用安全替代方案

        对于简单匹配，使用字符串操作替代正则
        """
        # 简单的字符串包含检查
        if pattern.replace('^', '').replace('$', '').replace('.*', '') in text:
            return True
        return False
```

### 7.3 安全正则编写规范

```python
class SafeRegexPractices:
    """安全正则表达式编写规范"""

    @staticmethod
    def atomic_groups():
        """
        使用原子组防止回溯

        原子组(?>...)一旦匹配成功就不回溯
        """
        # 危险写法
        bad = r'(\d+)+'

        # 安全写法：使用原子组
        safe = r'(?>\d+)'

        return bad, safe

    @staticmethod
    def possessive_quantifiers():
        """
        使用占有型量词防止回溯

        占有型量词(++/??/++)匹配后不回溯
        """
        # 危险写法
        bad = r'a+a'

        # 安全写法：占有型量词
        safe = r'a++a'

        return bad, safe

    @staticmethod
    def bounded_quantifiers():
        """
        使用有界量词

        避免无限量词，使用有界范围
        """
        # 危险写法：无限量词
        bad = r'a+'

        # 安全写法：有界量词
        safe = r'a{1,100}'

        return bad, safe

    @staticmethod
    def avoid_overlapping_alternation():
        """
        避免重叠的交替分支
        """
        # 危险写法：重叠的交替
        bad = r'(a|a)*b'

        # 安全写法：消除重叠
        safe = r'a*b'

        return bad, safe

    # 安全正则示例
    SAFE_EMAIL = r'^[a-zA-Z0-9._%+-]{1,64}@[a-zA-Z0-9.-]{1,255}\.[a-zA-Z]{2,}$'
    SAFE_URL = r'^https?://[a-zA-Z0-9.-]{1,253}[/a-zA-Z0-9._-]*$'
    SAFE_IP = r'^(\d{1,3}\.){3}\d{1,3}$'
    SAFE_PHONE = r'^1[3-9]\d{9}$'
```

---

## 8. 多线程/多进程安全

### 8.1 线程安全机制

```python
import threading
import time
from queue import Queue

class ThreadSafeCounter:
    """线程安全计数器"""

    def __init__(self, initial=0):
        self._value = initial
        self._lock = threading.Lock()

    def increment(self, amount=1):
        """安全递增"""
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount=1):
        """安全递减"""
        with self._lock:
            self._value -= amount
            return self._value

    def get(self):
        """获取当前值"""
        with self._lock:
            return self._value

class ThreadSafeDict:
    """线程安全字典"""

    def __init__(self):
        self._dict = {}
        self._lock = threading.RLock()  # 可重入锁

    def get(self, key, default=None):
        with self._lock:
            return self._dict.get(key, default)

    def set(self, key, value):
        with self._lock:
            self._dict[key] = value

    def delete(self, key):
        with self._lock:
            if key in self._dict:
                del self._dict[key]

    def items(self):
        with self._lock:
            return list(self._dict.items())
```

### 8.2 GIL与多线程

```python
import threading
import multiprocessing
import time

class GILExample:
    """GIL（全局解释器锁）示例"""

    @staticmethod
    def cpu_bound_task(n):
        """CPU密集型任务"""
        total = 0
        for i in range(n):
            total += i * i
        return total

    @staticmethod
    def test_threading_vs_multiprocessing():
        """
        比较多线程和多进程

        CPU密集型任务：多进程更快（绕过GIL）
        IO密集型任务：多线程更高效
        """
        n = 10_000_000
        num_workers = 4

        # 多线程测试
        start = time.time()
        threads = []
        for _ in range(num_workers):
            t = threading.Thread(target=GILExample.cpu_bound_task, args=(n,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        thread_time = time.time() - start

        # 多进程测试
        start = time.time()
        processes = []
        for _ in range(num_workers):
            p = multiprocessing.Process(target=GILExample.cpu_bound_task, args=(n,))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
        process_time = time.time() - start

        print(f"多线程时间: {thread_time:.2f}秒")
        print(f"多进程时间: {process_time:.2f}秒")
        print(f"加速比: {thread_time/process_time:.2f}x")

# 安全建议
# 1. CPU密集型任务使用multiprocessing
# 2. IO密集型任务使用threading或asyncio
# 3. 共享数据使用锁保护
# 4. 避免死锁（固定锁获取顺序）
# 5. 使用Queue而非共享变量进行线程间通信
```

### 8.3 并发安全实践

```python
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

class ConcurrentSecurity:
    """并发安全实践"""

    @staticmethod
    def safe_producer_consumer():
        """
        安全的生产者-消费者模式

        使用Queue实现线程间安全通信
        """
        task_queue = Queue(maxsize=100)
        result_queue = Queue()

        def producer():
            for i in range(20):
                task_queue.put(i)
            # 放入结束标记
            task_queue.put(None)

        def consumer(consumer_id):
            while True:
                task = task_queue.get()
                if task is None:
                    task_queue.put(None)  # 传递结束标记
                    break
                result = task * task
                result_queue.put((consumer_id, task, result))
                task_queue.task_done()

        # 启动生产者
        prod = threading.Thread(target=producer)
        prod.start()

        # 启动多个消费者
        consumers = []
        for i in range(3):
            t = threading.Thread(target=consumer, args=(i,))
            t.start()
            consumers.append(t)

        prod.join()
        for t in consumers:
            t.join()

        return list(result_queue.queue)

    @staticmethod
    def safe_concurrent_requests(urls, max_workers=10):
        """
        安全的并发HTTP请求

        使用线程池+错误处理
        """
        import requests

        def fetch_url(url):
            try:
                response = requests.get(url, timeout=10, verify=True)
                return {'url': url, 'status': response.status_code,
                       'size': len(response.content)}
            except Exception as e:
                return {'url': url, 'error': str(e)}

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_url, url): url for url in urls}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({'url': futures[future], 'error': str(e)})

        return results

    @staticmethod
    def deadlock_example():
        """
        死锁示例与避免

        死锁条件：
        1. 互斥
        2. 持有并等待
        3. 不可剥夺
        4. 循环等待

        避免方法：固定锁获取顺序
        """
        lock1 = threading.Lock()
        lock2 = threading.Lock()

        # 安全做法：所有线程按相同顺序获取锁
        def safe_task():
            with lock1:  # 先获取lock1
                with lock2:  # 再获取lock2
                    pass

        return "使用固定锁获取顺序避免死锁"
```

---

## 9. Python代码审计常见漏洞

### 9.1 代码注入漏洞

```python
# 危险示例 - 代码注入
class CodeInjectionVuln:
    """代码注入漏洞示例与修复"""

    @staticmethod
    def dangerous_eval(user_input):
        """危险：使用eval执行用户输入"""
        # 极度危险！攻击者可执行任意代码
        # payload: __import__('os').system('whoami')
        return eval(user_input)

    @staticmethod
    def safe_eval(user_input):
        """安全：限制eval的名称空间"""
        # 限制可用变量和函数
        safe_dict = {
            '__builtins__': {},
            'abs': abs,
            'min': min,
            'max': max,
            'round': round,
        }
        try:
            return eval(user_input, safe_dict, {})
        except Exception as e:
            return f"评估失败: {e}"

    @staticmethod
    def dangerous_exec(user_input):
        """危险：使用exec执行用户输入"""
        # 极度危险！
        exec(user_input)

    @staticmethod
    def dangerous_compile(user_input):
        """危险：编译并执行用户输入"""
        code = compile(user_input, '<string>', 'exec')
        exec(code)

# 安全建议：永远不要对不可信数据使用eval/exec
# 替代方案：使用安全的表达式解析器如ast.literal_eval
import ast

class SafeEval:
    """安全表达式评估"""

    @staticmethod
    def safe_literal_eval(expression):
        """
        安全的字面量评估

        只允许基本数据类型：字符串/数字/元组/列表/字典/布尔/None
        """
        try:
            return ast.literal_eval(expression)
        except (ValueError, SyntaxError) as e:
            return None
```

### 9.2 命令注入漏洞

```python
import subprocess
import shlex

class CommandInjectionVuln:
    """命令注入漏洞示例与修复"""

    @staticmethod
    def dangerous_os_system(user_input):
        """危险：使用os.system执行用户输入"""
        import os
        # 攻击payload: ; rm -rf /
        # 攻击payload: | cat /etc/passwd
        return os.system(f"ping -c 1 {user_input}")

    @staticmethod
    def dangerous_subprocess_shell(user_input):
        """危险：使用shell=True"""
        # shell=True允许命令注入
        return subprocess.call(
            f"ping -c 1 {user_input}",
            shell=True
        )

    @staticmethod
    def safe_subprocess(user_input):
        """安全：使用列表参数，shell=False"""
        # 使用列表参数，每个参数独立
        return subprocess.call(
            ['ping', '-c', '1', user_input],
            shell=False  # 不通过shell执行
        )

    @staticmethod
    def safe_subprocess_with_validation(user_input):
        """安全：输入验证 + 列表参数"""
        import re

        # 验证输入格式（仅允许域名/IP格式）
        if not re.match(r'^[a-zA-Z0-9.\-]+$', user_input):
            raise ValueError("输入包含非法字符")

        # 使用列表参数执行
        return subprocess.call(
            ['ping', '-c', '1', user_input],
            shell=False,
            timeout=10,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    @staticmethod
    def safe_shlex(user_command):
        """使用shlex安全分割命令"""
        # shlex.quote() 对参数进行安全引用
        safe_command = shlex.quote(user_command)
        return subprocess.call(
            f"echo {safe_command}",
            shell=True
        )
```

### 9.3 SSTI模板注入

```python
class SSTIVuln:
    """SSTI（服务器端模板注入）漏洞"""

    @staticmethod
    def dangerous_render(user_input, template_engine='jinja2'):
        """危险：直接将用户输入渲染到模板"""
        if template_engine == 'jinja2':
            from jinja2 import Environment
            env = Environment()
            # 攻击payload: {{ ''.__class__.__mro__[2].__subclasses__() }}
            template = env.from_string(user_input)
            return template.render()

    @staticmethod
    def safe_render(user_input):
        """安全：使用沙箱环境"""
        from jinja2 import Environment, SandboxedEnvironment
        from jinja2.sandbox import ImmutableSandboxedEnvironment

        # 使用沙箱环境，限制危险操作
        env = SandboxedEnvironment()
        try:
            template = env.from_string(user_input)
            return template.render()
        except Exception as e:
            return f"模板渲染失败: {e}"

    @staticmethod
    def safe_template_var(user_input):
        """安全：将用户输入作为模板变量"""
        from jinja2 import Environment
        env = Environment()

        # 固定模板，用户输入作为变量
        template = env.from_string("Hello, {{ name }}!")
        return template.render(name=user_input)
```

### 9.4 常见漏洞模式

```python
class VulnerablePatterns:
    """常见漏洞代码模式"""

    # 1. SQL注入
    @staticmethod
    def sqli_dangerous(user_input):
        """危险：字符串拼接SQL"""
        import sqlite3
        conn = sqlite3.connect('test.db')
        # 攻击payload: ' OR '1'='1
        query = f"SELECT * FROM users WHERE name = '{user_input}'"
        return conn.execute(query).fetchall()

    @staticmethod
    def sqli_safe(user_input):
        """安全：参数化查询"""
        import sqlite3
        conn = sqlite3.connect('test.db')
        query = "SELECT * FROM users WHERE name = ?"
        return conn.execute(query, (user_input,)).fetchall()

    # 2. XSS
    @staticmethod
    def xss_dangerous(user_input):
        """危险：直接输出用户输入"""
        return f"<div>{user_input}</div>"

    @staticmethod
    def xss_safe(user_input):
        """安全：HTML转义"""
        import html
        return f"<div>{html.escape(user_input)}</div>"

    # 3. 路径遍历
    @staticmethod
    def path_traversal_dangerous(filename):
        """危险：未验证文件名"""
        with open(f'/uploads/{filename}', 'r') as f:
            return f.read()

    @staticmethod
    def path_traversal_safe(filename):
        """安全：验证路径"""
        import os
        base_dir = '/uploads'
        filepath = os.path.abspath(os.path.join(base_dir, filename))
        if not filepath.startswith(base_dir + os.sep):
            raise ValueError("路径遍历检测")
        with open(filepath, 'r') as f:
            return f.read()

    # 4. XML外部实体（XXE）
    @staticmethod
    def xxe_dangerous(xml_data):
        """危险：允许外部实体"""
        from xml.etree import ElementTree
        # 默认允许外部实体解析
        return ElementTree.fromstring(xml_data)

    @staticmethod
    def xxe_safe(xml_data):
        """安全：禁用外部实体"""
        from defusedxml import ElementTree
        # 使用defusedxml防止XXE
        return ElementTree.fromstring(xml_data)

    # 5. 不安全反序列化
    @staticmethod
    def deserialization_dangerous(data):
        """危险：pickle反序列化"""
        import pickle
        # 极度危险！可执行任意代码
        return pickle.loads(data)

    @staticmethod
    def deserialization_safe(data):
        """安全：使用JSON"""
        import json
        return json.loads(data)
```

---

## 10. 安全编码最佳实践

### 10.1 输入验证

```python
import re
from datetime import datetime
from urllib.parse import urlparse

class InputValidator:
    """输入验证工具"""

    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True
        return False

    @staticmethod
    def validate_phone(phone):
        """验证手机号格式"""
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_url(url):
        """验证URL格式"""
        try:
            result = urlparse(url)
            if result.scheme in ['http', 'https'] and result.netloc:
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """验证整数"""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_length(value, min_len=0, max_len=1000):
        """验证长度"""
        if not isinstance(value, str):
            value = str(value)
        return min_len <= len(value) <= max_len

    @staticmethod
    def validate_alphanumeric(value):
        """验证仅字母数字"""
        return bool(re.match(r'^[a-zA-Z0-9]+$', value))

    @staticmethod
    def validate_filename(filename):
        """验证文件名"""
        if not filename or '..' in filename or '/' in filename or '\\' in filename:
            return False
        return bool(re.match(r'^[a-zA-Z0-9._-]+$', filename))

    @staticmethod
    def sanitize_html(html_content):
        """清洗HTML内容"""
        from html.parser import HTMLParser

        class HTMLSanitizer(HTMLParser):
            ALLOWED_TAGS = {'p', 'br', 'strong', 'em', 'ul', 'ol', 'li',
                           'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
            ALLOWED_ATTRS = {}

            def __init__(self):
                super().__init__()
                self.result = []
                self.skip = False

            def handle_starttag(self, tag, attrs):
                if tag.lower() in self.ALLOWED_TAGS:
                    self.result.append(f'<{tag}>')
                else:
                    self.skip = True

            def handle_endtag(self, tag):
                if tag.lower() in self.ALLOWED_TAGS:
                    self.result.append(f'</{tag}>')
                self.skip = False

            def handle_data(self, data):
                import html
                self.result.append(html.escape(data))

        parser = HTMLSanitizer()
        parser.feed(html_content)
        return ''.join(parser.result)
```

### 10.2 输出编码

```python
import html
import json
import re

class OutputEncoder:
    """输出编码工具"""

    @staticmethod
    def encode_for_html(text):
        """HTML上下文编码"""
        return html.escape(text, quote=True)

    @staticmethod
    def encode_for_attribute(text):
        """HTML属性编码"""
        return html.escape(text, quote=True)

    @staticmethod
    def encode_for_javascript(text):
        """JavaScript上下文编码"""
        # 使用JSON编码
        return json.dumps(text)

    @staticmethod
    def encode_for_url(text):
        """URL编码"""
        from urllib.parse import quote
        return quote(text, safe='')

    @staticmethod
    def encode_for_css(text):
        """CSS上下文编码"""
        encoded = []
        for char in text:
            encoded.append(f'\\{ord(char):06x}')
        return ''.join(encoded)

    @staticmethod
    def encode_for_sql(text, db_type='mysql'):
        """
        SQL编码（推荐使用参数化查询而非手动编码）
        """
        if db_type == 'mysql':
            return text.replace('\\', '\\\\').replace("'", "\\'")
        elif db_type == 'postgres':
            return text.replace("'", "''")
        return text
```

### 10.3 错误处理

```python
import logging
import sys

class SecureErrorHandler:
    """安全错误处理"""

    def __init__(self, log_file='security.log'):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # 文件处理器
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)

    def handle_error(self, error, context=None, user_message=None):
        """
        安全错误处理

        原则：
        - 内部错误信息记录到日志，不返回给用户
        - 用户看到的是通用错误消息
        - 敏感信息不泄露
        """
        # 记录详细错误到日志（包含堆栈）
        self.logger.error(
            f"错误: {str(error)}\n"
            f"上下文: {context}\n"
            f"类型: {type(error).__name__}",
            exc_info=True
        )

        # 返回给用户的安全消息
        if user_message:
            return user_message
        return "操作失败，请稍后重试或联系管理员"

    @staticmethod
    def safe_exception_handler(func):
        """异常处理装饰器"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                print(f"输入错误: {e}")
                return None
            except PermissionError:
                print("权限不足")
                return None
            except FileNotFoundError:
                print("文件不存在")
                return None
            except Exception:
                # 捕获所有未处理异常，不泄露内部信息
                print("系统错误，请联系管理员")
                return None
        return wrapper
```

### 10.4 日志安全

```python
import logging
import re

class SecureLogger:
    """安全日志工具"""

    # 需要脱敏的敏感数据模式
    SENSITIVE_PATTERNS = [
        (r'\b\d{16,19}\b', '[CARD]'),           # 信用卡号
        (r'\b\d{15}\b', '[CARD]'),              # Amex卡号
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),     # SSN
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
        (r'password["\']?\s*[:=]\s*["\']?(\S+)', 'password=[REDACTED]'),
        (r'token["\']?\s*[:=]\s*["\']?(\S+)', 'token=[REDACTED]'),
        (r'key["\']?\s*[:=]\s*["\']?(\S+)', 'key=[REDACTED]'),
        (r'secret["\']?\s*[:=]\s*["\']?(\S+)', 'secret=[REDACTED]'),
    ]

    @classmethod
    def sanitize_log(cls, message):
        """脱敏日志中的敏感信息"""
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        return message

    @staticmethod
    def secure_log(logger, level, message, **kwargs):
        """安全日志记录"""
        sanitized = SecureLogger.sanitize_log(message)
        for k, v in kwargs.items():
            kwargs[k] = SecureLogger.sanitize_log(str(v))
        getattr(logger, level)(sanitized, **kwargs)
```

### 10.5 依赖管理

```python
import subprocess
import json

class DependencySecurity:
    """依赖安全管理"""

    @staticmethod
    def check_vulnerabilities():
        """
        检查依赖漏洞

        使用safety或pip-audit检查已知漏洞
        """
        try:
            # 使用pip-audit
            result = subprocess.run(
                ['pip-audit', '--format', 'json'],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout)
                return vulnerabilities
        except FileNotFoundError:
            print("pip-audit未安装，请运行: pip install pip-audit")
        except Exception as e:
            print(f"检查失败: {e}")
        return []

    @staticmethod
    def scan_with_bandit(filepath):
        """
        使用bandit进行代码安全扫描

        bandit是Python静态代码安全分析工具
        """
        try:
            result = subprocess.run(
                ['bandit', '-r', filepath, '-f', 'json'],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode is not None:
                return json.loads(result.stdout)
        except FileNotFoundError:
            print("bandit未安装，请运行: pip install bandit")
        except Exception as e:
            print(f"扫描失败: {e}")
        return {}

    @staticmethod
    def check_requirements(requirements_file='requirements.txt'):
        """检查requirements.txt中的依赖"""
        with open(requirements_file, 'r') as f:
            deps = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    deps.append(line)
        return deps
```

---

## 总结

本文档系统性地介绍了Python安全编程的各个方面，包括：

1. **常用安全库**：requests、urllib3、socket、ssl、hashlib、hmac、secrets库的安全用法
2. **Web请求安全**：SSRF防护、SSL验证、重定向控制、Cookie安全
3. **文件操作安全**：路径遍历防护、Zip Slip漏洞、反序列化安全、临时文件安全
4. **密码学编程**：哈希算法、HMAC认证、AES/RSA加密、密码安全存储
5. **网络编程安全**：socket编程、端口扫描、协议解析、SSL/TLS通信
6. **正则表达式安全**：ReDoS漏洞原理与防护、安全正则编写规范
7. **多线程安全**：线程安全机制、GIL影响、并发安全实践
8. **代码审计**：代码注入、命令注入、SSTI、SQL注入等常见漏洞
9. **安全编码实践**：输入验证、输出编码、错误处理、日志安全、依赖管理

安全编程的核心原则是**永不信任用户输入**，对所有外部输入进行严格的验证和清洗。通过遵循本文档的最佳实践，可以显著降低Python应用的安全风险。

> **免责声明**：本文档仅用于安全学习和研究目的。使用这些技术时请确保获得适当授权，遵守相关法律法规。

---

## 学习资源与知识拓展

### 官方资源

- **Python 官方文档**：各语言官网提供最权威的文档和教程
- **Python 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 Python**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《Python程序设计》— 入门经典教材
- 《Python高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
