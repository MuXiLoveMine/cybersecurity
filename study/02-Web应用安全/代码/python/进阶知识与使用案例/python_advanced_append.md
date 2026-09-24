
---

## 四、高级实战案例

### 4.1 异步端口扫描器（asyncio）

使用 asyncio 实现高性能异步端口扫描，比传统多线程快 10 倍以上。

```python
import asyncio
from typing import List, Tuple

async def port_scan(host: str, port: int, timeout: float = 1.0) -> Tuple[int, bool]:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return (port, True)
    except:
        return (port, False)

async def scan_ports(host: str, ports: List[int], concurrency: int = 100) -> List[int]:
    semaphore = asyncio.Semaphore(concurrency)
    open_ports = []
    
    async def scan_with_sem(port):
        async with semaphore:
            return await port_scan(host, port)
    
    tasks = [scan_with_sem(p) for p in ports]
    results = await asyncio.gather(*tasks)
    
    for port, is_open in results:
        if is_open:
            open_ports.append(port)
    
    return sorted(open_ports)

# 使用示例
async def main():
    host = "127.0.0.1"
    ports = list(range(1, 10000))
    open_ports = await scan_ports(host, ports, concurrency=500)
    print(f"开放端口: {open_ports}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 Web 漏洞扫描器框架

模块化的 Web 漏洞扫描器，支持插件扩展。

```python
import requests
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class Vulnerability:
    name: str
    severity: str
    url: str
    description: str
    evidence: str = ""

class WebScanner:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; WebScanner/1.0)"
        })
        self.vulns: List[Vulnerability] = []
        self.plugins: List[Callable] = []
    
    def register_plugin(self, plugin_func):
        self.plugins.append(plugin_func)
    
    def scan(self):
        for plugin in self.plugins:
            try:
                results = plugin(self.base_url, self.session)
                if results:
                    self.vulns.extend(results)
            except Exception as e:
                print(f"插件 {plugin.__name__} 执行失败: {e}")
        return self.vulns

# 插件示例：SQL 注入检测
def sqli_plugin(base_url: str, session: requests.Session) -> List[Vulnerability]:
    vulns = []
    test_urls = [
        f"{base_url}/page?id=1'",
    ]
    errors = ["MySQL syntax", "SQL syntax", "ORA-", "PostgreSQL", "Warning: mysql_"]
    
    for url in test_urls:
        try:
            resp = session.get(url, timeout=5)
            for err in errors:
                if err.lower() in resp.text.lower():
                    vulns.append(Vulnerability(
                        name="SQL Injection",
                        severity="critical",
                        url=url,
                        description=f"检测到 SQL 错误: {err}",
                        evidence=err
                    ))
                    break
        except:
            pass
    return vulns

# 使用示例
scanner = WebScanner("http://target.com")
scanner.register_plugin(sqli_plugin)
results = scanner.scan()
for v in results:
    print(f"[{v.severity.upper()}] {v.name} - {v.url}")
```

### 4.3 加密与解密工具箱

常用加密算法实现和密码学工具。

```python
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet

class CryptoToolkit:
    @staticmethod
    def md5(data: str) -> str:
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def sha1(data: str) -> str:
        return hashlib.sha1(data.encode()).hexdigest()
    
    @staticmethod
    def sha256(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def hmac_sha256(key: str, data: str) -> str:
        return hmac.new(key.encode(), data.encode(), hashlib.sha256).hexdigest()
    
    @staticmethod
    def b64_encode(data: str) -> str:
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def b64_decode(data: str) -> str:
        return base64.b64decode(data.encode()).decode()
    
    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode()
    
    @staticmethod
    def fernet_encrypt(key: str, plaintext: str) -> str:
        f = Fernet(key.encode())
        return f.encrypt(plaintext.encode()).decode()
    
    @staticmethod
    def fernet_decrypt(key: str, ciphertext: str) -> str:
        f = Fernet(key.encode())
        return f.decrypt(ciphertext.encode()).decode()
    
    @staticmethod
    def crack_hash(target_hash: str, wordlist_path: str, algo: str = "md5") -> str:
        hash_func = getattr(hashlib, algo)
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    word = line.strip()
                    if hash_func(word.encode()).hexdigest() == target_hash:
                        return word
        except FileNotFoundError:
            print(f"字典文件不存在: {wordlist_path}")
        return None
```

### 4.4 代理与隧道工具

HTTP 代理和端口转发实现。

```python
import socket
import threading
import select
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request

# 端口转发
class PortForwarder:
    def __init__(self, local_port: int, remote_host: str, remote_port: int):
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
    
    def forward(self, client_sock):
        try:
            remote_sock = socket.create_connection(
                (self.remote_host, self.remote_port), timeout=10
            )
            sockets = [client_sock, remote_sock]
            while True:
                readable, _, _ = select.select(sockets, [], [], 60)
                for sock in readable:
                    data = sock.recv(4096)
                    if not data:
                        return
                    if sock is client_sock:
                        remote_sock.sendall(data)
                    else:
                        client_sock.sendall(data)
        except Exception as e:
            print(f"转发错误: {e}")
        finally:
            client_sock.close()
    
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.local_port))
        server.listen(100)
        print(f"端口转发: 0.0.0.0:{self.local_port} -> {self.remote_host}:{self.remote_port}")
        while True:
            client, addr = server.accept()
            t = threading.Thread(target=self.forward, args=(client,), daemon=True)
            t.start()
```

---

## 五、进阶学习资源

### 5.1 高级安全开发

- **OWASP Top 10 深入解析**：https://owasp.org/www-project-top-ten/
- **OWASP Cheat Sheet Series**：https://cheatsheetseries.owasp.org/
- **CWE Top 25**：https://cwe.mitre.org/top25/

### 5.2 Python 安全工具库

- **Scapy**：https://scapy.net/ — 网络数据包操作库
- **pwntools**：https://docs.pwntools.com/ — CTF PWN 工具库
- **impacket**：https://github.com/fortra/impacket — 网络协议库，SMB/MSRPC
- **PyCryptodome**：https://pycryptodome.readthedocs.io/ — 密码学库
- **cryptography**：https://cryptography.io/ — 现代密码学库
- **paramiko**：SSH 客户端库
- **shodan**：Shodan 搜索引擎 API

### 5.3 红队与渗透测试资源

- **HackTricks**：https://book.hacktricks.xyz/ — 渗透测试百科
- **PayloadsAllTheThings**：https://github.com/swisskyrepo/PayloadsAllTheThings
- **GTFOBins**：https://gtfobins.github.io/ — Unix 二进制提权
- **LOLBAS**：https://lolbas-project.github.io/ — Windows 内置工具利用
- **Red Team Notes**：https://www.ired.team/ — 红队技术笔记
- **ATT&CK**：https://attack.mitre.org/ — MITRE ATT&CK 矩阵

### 5.4 CTF 平台与练习

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **picoCTF**：https://picoctf.org/
- **OverTheWire**：https://overthewire.org/wargames/
- **CTFtime**：https://ctftime.org/
- **Bugku**：https://ctf.bugku.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/

### 5.5 推荐进阶书籍

- **Python 相关**：
  - 《Python 黑帽子》— 黑客与渗透测试编程之道
  - 《Python 绝技》— 运用 Python 成为顶级黑客
  - 《Python 密码学编程》

- **Web 安全**：
  - 《Web 安全深度剖析》
  - 《白帽子讲 Web 安全》
  - 《SQL 注入攻击与防御》

- **红队**：
  - 《红队攻防实战》
  - 《高级渗透测试》

### 5.6 安全博客与资讯

- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/
- **看雪学院**：https://www.kanxue.com/
- **Hacker News**：https://news.ycombinator.com/

### 5.7 GitHub 开源项目

- **Awesome 系列**：
  - awesome-python-security
  - awesome-web-security
  - awesome-hacking
  - awesome-pentesting
  - awesome-ctf

- **知名工具**：
  - sqlmap: SQL 注入自动化工具
  - nmap: 网络扫描器
  - metasploit-framework: 渗透测试框架
  - hashcat: 密码恢复工具

### 5.8 进阶学习路线

**第 1 阶段：基础夯实（1-2月）**
- 熟练掌握 Python 进阶语法（装饰器、生成器、上下文管理器、元类）
- 掌握常用标准库和第三方库
- 学习 HTTP 协议、TCP/IP 协议栈

**第 2 阶段：工具开发（2-3月）**
- 开发端口扫描器、目录爆破、SQL 注入检测等基础工具
- 学习多线程、多进程、异步编程
- 掌握爬虫开发、数据包分析

**第 3 阶段：漏洞利用（3-4月）**
- 深入理解 Web 漏洞原理
- 编写漏洞 PoC 和 EXP
- 学习密码学和加密绕过技巧

**第 4 阶段：红队技术（持续）**
- 学习内网渗透、横向移动
- 研究免杀技术、权限提升
- 了解 C2 框架开发

**第 5 阶段：CTF 实战（持续）**
- 参加 CTF 比赛积累经验
- 研究各类 CTF 题型
- 学习逆向工程、PWN、密码学
