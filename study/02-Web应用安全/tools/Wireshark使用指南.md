# Wireshark 使用指南

> Wireshark 是最流行的网络协议分析工具，可以捕获和分析网络数据包，广泛用于网络故障排查、安全分析和协议学习。

---

## 目录

- [一、Wireshark 简介](#一wireshark-简介)
- [二、安装与界面](#二安装与界面)
- [三、抓包基础](#三抓包基础)
- [四、过滤器](#四过滤器)
- [五、常用协议分析](#五常用协议分析)
- [六、HTTP/HTTPS 分析](#六httphttps-分析)
- [七、TCP 流分析](#七tcp-流分析)
- [八、统计与图表](#八统计与图表)
- [九、抓包过滤技巧](#九抓包过滤技巧)
- [十、安全分析应用](#十安全分析应用)
- [十一、常用快捷键](#十一常用快捷键)

---

## 一、Wireshark 简介

Wireshark（前称 Ethereal）是一款免费开源的网络协议分析软件。

**特点**：
- 支持上千种协议解析
- 实时捕获和离线分析
- 强大的过滤功能
- 丰富的统计和图表
- 跨平台（Windows/Linux/Mac）
- 支持多种文件格式（pcap、pcapng 等）

**应用场景**：
- 网络故障排查
- 安全分析（入侵检测、流量分析）
- 协议学习和研究
- 应用调试
- 性能分析

---

## 二、安装与界面

### 2.1 安装

**Windows/Mac**：
- 官网下载：https://www.wireshark.org/download.html
- 安装时勾选 Npcap（Windows 抓包必需）

**Linux**：
```bash
# Ubuntu/Debian
sudo apt-get install wireshark

# CentOS/RHEL
sudo yum install wireshark-gnome

# 普通用户抓包权限（Linux）
sudo usermod -a -G wireshark $USER
```

### 2.2 主界面

```
┌─────────────────────────────────────────────────────────────┐
│ 菜单栏 / 工具栏 / 过滤栏                                     │
├─────────────┬───────────────────────────────────────────────┤
│             │ 1. 数据包列表（Packet List Pane）              │
│  左侧导航   │    显示每个数据包的基本信息                    │
│             ├───────────────────────────────────────────────┤
│             │ 2. 协议树（Packet Details Pane）              │
│             │    分层显示数据包的协议结构                    │
│             ├───────────────────────────────────────────────┤
│             │ 3. 字节流（Packet Bytes Pane）                │
│             │    原始十六进制和 ASCII 数据                  │
└─────────────┴───────────────────────────────────────────────┘
```

**数据包列表列**：
- `No.` — 编号
- `Time` — 时间
- `Source` — 源地址
- `Destination` — 目标地址
- `Protocol` — 协议
- `Length` — 长度
- `Info` — 信息摘要

---

## 三、抓包基础

### 3.1 开始抓包

1. 打开 Wireshark
2. 选择网络接口（网卡）
   - 有线：以太网 / Ethernet
   - 无线：Wi-Fi / WLAN
   - 本地回环：Loopback
3. 双击接口或点击鲨鱼鳍按钮开始抓包

### 3.2 停止抓包

- 点击红色停止按钮
- 快捷键：`Ctrl+E`

### 3.3 保存抓包文件

```
File → Save As
格式：.pcap 或 .pcapng
```

### 3.4 打开抓包文件

```
File → Open
支持格式：pcap、pcapng、cap、etc.
```

### 3.5 抓包选项

```
Capture → Options
```

- **混杂模式（Promiscuous Mode）**：捕获所有经过网卡的包
- **抓包过滤器**：只捕获符合条件的包
- **缓冲区大小**：设置抓包缓冲区
- **自动保存**：多文件滚动保存

---

## 四、过滤器

Wireshark 有两种过滤器：**抓包过滤器**（捕获时过滤）和**显示过滤器**（捕获后显示过滤）。

### 4.1 显示过滤器

在主界面过滤栏输入，语法为协议字段比较。

**基本语法**：
```
协议.字段 比较运算符 值
```

**比较运算符**：

| 运算符 | 说明 |
|--------|------|
| `==` / `eq` | 等于 |
| `!=` / `ne` | 不等于 |
| `>` / `gt` | 大于 |
| `<` / `lt` | 小于 |
| `>=` / `ge` | 大于等于 |
| `<=` / `le` | 小于等于 |
| `contains` | 包含 |
| `matches` | 正则匹配 |

**逻辑运算符**：

| 运算符 | 说明 |
|--------|------|
| `and` / `&&` | 与 |
| `or` / `\|\|` | 或 |
| `not` / `!` | 非 |

### 4.2 常用显示过滤

**IP 地址过滤**：
```
ip.addr == 192.168.1.1        # 源或目标 IP
ip.src == 192.168.1.1         # 源 IP
ip.dst == 192.168.1.1         # 目标 IP
ip.addr == 192.168.1.0/24     # 网段
```

**端口过滤**：
```
tcp.port == 80                # TCP 源或目标端口
tcp.srcport == 80             # TCP 源端口
tcp.dstport == 80             # TCP 目标端口
udp.port == 53                # UDP 端口
```

**协议过滤**：
```
http                          # HTTP
dns                           # DNS
ftp                           # FTP
ssh                           # SSH
tls                           # TLS/SSL
icmp                          # ICMP
arp                           # ARP
tcp                           # TCP
udp                           # UDP
```

**组合过滤**：
```
ip.addr == 192.168.1.1 and tcp.port == 80
http and ip.dst == 10.0.0.1
tcp.flags.syn == 1            # SYN 包
tcp.flags.reset == 1          # RST 包
http.request.method == "GET"  # HTTP GET 请求
http.response.code == 200     # HTTP 200 响应
```

**内容过滤**：
```
http contains "password"      # HTTP 中包含 password
tcp contains "admin"          # TCP 数据中包含 admin
http.host contains "example"  # Host 头包含 example
```

### 4.3 抓包过滤器（BPF 语法）

在 Capture Options 中设置，使用 BPF（Berkeley Packet Filter）语法。

**常用过滤**：
```
host 192.168.1.1              # 主机
src host 192.168.1.1          # 源主机
dst host 192.168.1.1          # 目标主机
port 80                       # 端口
tcp port 80                   # TCP 端口
udp port 53                   # UDP 端口
net 192.168.1.0/24            # 网段
portrange 1-1024              # 端口范围
icmp                          # ICMP
arp                           # ARP
tcp                           # TCP
udp                           # UDP
```

**组合**：
```
host 192.168.1.1 and port 80
src host 192.168.1.1 and tcp port 443
not port 22                   # 排除 SSH
```

### 4.4 过滤器快速操作

- 点击过滤栏右侧的表达式按钮 → 可视化构建过滤
- 在数据包列表中右键 → Apply as Filter → 快速应用过滤
- `Ctrl+/` 在过滤表达式前后切换
- 绿色 = 语法正确，红色 = 语法错误，黄色 = 警告

---

## 五、常用协议分析

### 5.1 HTTP 协议

**HTTP 请求结构**：
```
- Hypertext Transfer Protocol
  - GET /index.html HTTP/1.1\r\n   # 请求行
  - Host: example.com\r\n          # 头部
  - User-Agent: Mozilla/5.0\r\n
  - Accept: */*\r\n
  - \r\n                           # 空行
  - [no response]                  # 请求体（GET 没有）
```

**HTTP 响应结构**：
```
- Hypertext Transfer Protocol
  - HTTP/1.1 200 OK\r\n           # 状态行
  - Server: Apache\r\n            # 响应头
  - Content-Type: text/html\r\n
  - Content-Length: 1234\r\n
  - \r\n
  - File Data: ...                # 响应体
```

**HTTP 过滤**：
```
http.request                    # 所有 HTTP 请求
http.response                   # 所有 HTTP 响应
http.request.method == "POST"   # POST 请求
http.response.code == 404       # 404 响应
http.host == "example.com"      # 指定域名
http.request.uri contains "login"  # 包含 login 的 URI
```

### 5.2 DNS 协议

```
dns                             # 所有 DNS 数据包
dns.flags.response == 0         # DNS 查询
dns.flags.response == 1         # DNS 响应
dns.qry.name == "example.com"   # 查询域名
dns.resp.name == "example.com"  # 响应域名
```

### 5.3 TCP 协议

```
tcp.flags.syn == 1              # SYN 包（连接请求）
tcp.flags.syn == 1 and tcp.flags.ack == 1  # SYN+ACK
tcp.flags.fin == 1              # FIN 包（关闭连接）
tcp.flags.reset == 1            # RST 包（重置连接）
tcp.port == 443                 # 端口
tcp.len > 0                     # 有数据的 TCP 包
```

**TCP 三次握手**：
1. `SYN` — 客户端 → 服务器
2. `SYN, ACK` — 服务器 → 客户端
3. `ACK` — 客户端 → 服务器

**TCP 四次挥手**：
1. `FIN, ACK` — 主动关闭方
2. `ACK` — 被动关闭方
3. `FIN, ACK` — 被动关闭方
4. `ACK` — 主动关闭方

### 5.4 TLS/SSL 协议

```
tls                             # TLS 数据包
tls.handshake                   # TLS 握手
tls.handshake.type == 1         # Client Hello
tls.handshake.type == 2         # Server Hello
tls.handshake.ciphersuite       # 密码套件
tls.certificate                 # 证书
```

---

## 六、HTTP/HTTPS 分析

### 6.1 HTTP 对象导出

Wireshark 可以提取 HTTP 传输的文件。

```
File → Export Objects → HTTP
```

可以导出：HTML、图片、JS、CSS 等所有 HTTP 传输的文件。

### 6.2 HTTPS 解密

HTTPS 流量默认是加密的，需要密钥才能解密。

**方法一：SSLKEYLOGFILE（推荐）**

1. 设置环境变量：
   ```bash
   # Linux/Mac
   export SSLKEYLOGFILE=~/sslkey.log
   
   # Windows
   set SSLKEYLOGFILE=C:\sslkey.log
   ```

2. 启动浏览器（Chrome/Firefox 支持）
3. 在 Wireshark 中设置：
   ```
   Edit → Preferences → Protocols → TLS
   → (Pre)-Master-Secret log filename → 选择 sslkey.log 文件
   ```

4. 重新抓包，HTTPS 流量将自动解密

**方法二：服务器私钥**
- 需要服务器的 RSA 私钥
- 只能解密 RSA 密钥交换的连接（不支持 ECDHE/DHE 前向安全）

### 6.3 HTTP 流追踪

```
右键数据包 → Follow → HTTP Stream
```

可以看到完整的 HTTP 请求和响应内容。

---

## 七、TCP 流分析

### 7.1 追踪 TCP 流

```
右键数据包 → Follow → TCP Stream
```

显示整个 TCP 连接的数据流（类似 telnet 看到的内容），非常有用。

**颜色含义**：
- 红色：客户端 → 服务器
- 蓝色：服务器 → 客户端

### 7.2 流列表

```
Analyze → Follow → TCP Stream
Statistics → Conversations
```

可以查看所有 TCP 会话，按字节数/包数排序。

### 7.3 对话统计

```
Statistics → Conversations
```

按协议（IPv4、TCP、UDP 等）查看所有对话，快速定位异常流量。

---

## 八、统计与图表

### 8.1 常用统计功能

| 菜单 | 功能 |
|------|------|
| `Statistics → Summary` | 抓包摘要 |
| `Statistics → Protocol Hierarchy` | 协议层级统计 |
| `Statistics → Conversations` | 对话列表 |
| `Statistics → Endpoints` | 端点统计 |
| `Statistics → HTTP → Packet Counter` | HTTP 包计数 |
| `Statistics → HTTP → Requests` | HTTP 请求统计 |
| `Statistics → IO Graph` | IO 图表（流量趋势） |
| `Statistics → Flow Graph` | 流图 |
| `Statistics → TCP Stream Graphs` | TCP 流图 |

### 8.2 IO 图表

查看流量随时间的变化：
```
Statistics → IO Graph
```

可以创建多条线，对比不同流量的变化趋势。

### 8.3 协议层级

```
Statistics → Protocol Hierarchy
```

展示各种协议的占比，快速了解流量构成。

---

## 九、抓包过滤技巧

### 9.1 只抓 HTTP

```
# 抓包过滤器
tcp port 80
```

### 9.2 抓特定主机的流量

```
host 192.168.1.100
```

### 9.3 排除某些流量

```
# 排除 SSH，避免干扰
not port 22

# 排除广播
not broadcast

# 排除组播
not multicast
```

### 9.4 抓 DNS

```
udp port 53 or tcp port 53
```

### 9.5 抓取 TCP 握手包

```
# SYN 包
'tcp[tcpflags] & tcp-syn != 0'
```

### 9.6 大文件分卷保存

```
Capture → Options → Output
→ Create a new file automatically after...
设置文件大小或时间间隔
```

---

## 十、安全分析应用

### 10.1 发现端口扫描

**特征**：
- 大量 SYN 包来自同一源 IP
- 目标端口范围广
- 时间间隔短

**检测过滤**：
```
tcp.flags.syn == 1 and tcp.flags.ack == 0
```

然后看源 IP 统计：
```
Statistics → Conversations → IPv4
按 Packets 排序，找异常多的源 IP
```

### 10.2 发现暴力破解

**特征**：
- 大量登录请求（SSH、FTP、HTTP 认证等）
- 短时间内多次失败

**SSH 爆破检测**：
```
# SSH 协议，看对话数量
ssh
Statistics → Conversations → TCP
```

### 10.3 分析恶意软件通信

**特征**：
- 连接可疑 IP/域名
- 异常端口
- 定时通信（C&C 心跳）
- 大量上传数据（数据泄露）

**分析方法**：
1. 查看所有对话，找异常连接
2. 检查 DNS 查询，找可疑域名
3. 分析 HTTP User-Agent 是否异常
4. 查看 TLS 证书信息

### 10.4 SQL 注入检测

**特征**：
- HTTP 请求中包含 SQL 关键字
- URL 参数中有 `'`、`OR 1=1`、`UNION SELECT` 等

**检测过滤**：
```
http.request.uri contains "SELECT" or http.request.uri contains "UNION"
http.request.uri contains "'" or http.request.uri contains "1=1"
```

### 10.5 XSS 攻击检测

```
http.request.uri contains "<script>"
http.request.uri contains "javascript:"
http.request.uri contains "onerror="
```

---

## 十一、常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+E` | 开始/停止抓包 |
| `Ctrl+K` | 重新开始抓包（清空） |
| `Ctrl+O` | 打开抓包文件 |
| `Ctrl+S` | 保存抓包文件 |
| `Ctrl+F` | 查找数据包 |
| `Ctrl+G` | 跳转到指定包号 |
| `Ctrl++` | 放大字体 |
| `Ctrl+-` | 缩小字体 |
| `Ctrl+R` | 重新加载 |
| `Alt+Left` | 上一个数据包 |
| `Alt+Right` | 下一个数据包 |
| `Ctrl+M` | 标记/取消标记数据包 |
| `/` | 聚焦到显示过滤器 |
| `Enter` | 应用过滤器 |

---

## 十二、常用分析流程

### 12.1 分析 HTTP 流量

```
1. 设置过滤：http
2. 查看请求：Statistics → HTTP → Requests
3. 找 POST 请求：http.request.method == "POST"
4. 追踪流：右键 → Follow → HTTP Stream
5. 导出文件：File → Export Objects → HTTP
```

### 12.2 排查连接问题

```
1. 过滤目标 IP：ip.addr == 192.168.1.1
2. 看 TCP 握手：找 SYN、SYN-ACK、ACK
3. 看是否有 RST（连接被重置）
4. 看是否有重传（TCP Retransmission）
5. 看延迟（Time 列）
```

### 12.3 分析登录流量

```
1. 过滤 HTTP POST
   http.request.method == "POST"
2. 找到登录请求
3. Follow HTTP Stream 查看提交的表单数据
4. 看响应是否有 Set-Cookie
```

---

> **延伸学习**：Wireshark 是网络安全的基础工具。建议学习 TCP/IP 协议，结合 Wireshark 抓包分析，深入理解各种网络协议的工作原理。对于安全分析，掌握 Wireshark 可以帮助理解攻击流量的特征，提高入侵检测和应急响应能力。

---

## 十三、高级过滤技术

### 13.1 复合过滤表达式

```bash
# 组合条件（AND / OR / NOT）
http and ip.addr == 192.168.1.100
http or https
not arp and not icmp

# 括号分组
(http or dns) and ip.src == 192.168.1.50

# 子字符串匹配
http.request.uri contains "admin"
http.request.uri matches "(?i)select|union|drop"   # 正则匹配，忽略大小写

# 多值匹配
http.request.method == "POST" or http.request.method == "PUT"
tcp.port in {80 443 8080 8443}
ip.addr in {192.168.1.0/24 10.0.0.0/8}

# 按字段范围
tcp.port >= 1024 and tcp.port <= 65535
frame.len > 1500

# 按时间范围
frame.time >= "2024-01-01 10:00:00" and frame.time <= "2024-01-01 12:00:00"
```

### 13.2 协议层过滤

```bash
# 链路层
eth.src == 00:11:22:33:44:55          # 源 MAC
eth.dst == ff:ff:ff:ff:ff:ff          # 目标 MAC（广播）
eth.type == 0x0800                     # IPv4
eth.type == 0x86dd                     # IPv6
eth.type == 0x0806                     # ARP

# 网络层
ip.src == 192.168.1.100               # 源 IP
ip.dst == 10.0.0.1                    # 目标 IP
ip.ttl < 64                           # TTL 值
ip.flags.df == 1                      # 不分片标志
ip.proto == 6                         # 协议号（6=TCP, 17=UDP, 1=ICMP）

# IPv6 过滤
ipv6.src == fe80::1
ipv6.hop_limit == 64
icmpv6.type == 135                    # 邻居请求

# 传输层
tcp.srcport == 12345                 # 源端口
tcp.dstport == 80                    # 目标端口
tcp.seq == 1                         # 序列号
tcp.ack == 1                         # 确认号
tcp.window_size_value < 100          # 窗口大小

# 应用层
http.host == "example.com"           # HTTP Host
http.response.code == 200            # HTTP 状态码
http.response.code >= 400            # HTTP 错误码
http.request.uri matches "^/admin"   # URL 正则匹配
```

### 13.3 高级过滤技巧

```bash
# 查找特定字节序列（hex）
tcp.payload contains "41:42:43:44"   # 查找 ABCD 的 hex
frame contains "password"            # 任意层包含字符串

# 查找重复数据包
tcp.analysis.duplicate_ack           # 重复 ACK
tcp.analysis.retransmission          # TCP 重传
tcp.analysis.fast_retransmission     # 快速重传
tcp.analysis.out_of_order           # 乱序

# 连接状态
tcp.flags.syn == 1 and tcp.flags.ack == 0 and not ip.src == 192.168.1.1
# SYN 扫描（非本机发起）

# 查找 HTTP 头
http.request.line contains "X-Forwarded-For"
http.request.line contains "User-Agent: curl"
http.set_cookie contains "sessionid"

# DNS 过滤
dns.qry.name contains "malware"      # DNS 查询包含恶意域名
dns.flags.response == 1             # DNS 响应
dns.qry.type == 1                   # A 记录查询
dns.qry.type == 28                  # AAAA 记录查询
dns.count.answers > 5               # 多个应答记录

# TLS 过滤
tls.handshake.extensions_server_name contains "evil.com"
tls.record.content_type == 22       # TLS Handshake
tls.handshake.type == 1             # Client Hello
tls.handshake.type == 2             # Server Hello
```

### 13.4 过滤器组合应用

```
场景1：查找 SQL 注入尝试
  http.request.method == "POST" and
  (http.request.uri contains "union" or
   http.request.uri contains "select" or
   http.file_data contains "0x" or
   http.file_data contains "exec(")

场景2：查找目录遍历攻击
  http.request.uri contains "../" or
  http.request.uri contains "..\\" or
  http.request.uri contains "%2e%2e" or
  http.request.uri contains "..%2f"

场景3：查找 Web Shell 通信
  http.request.uri matches "(?i)(cmd|shell|exec|eval|system)\.(php|jsp|asp)" and
  http.request.method == "POST"

场景4：查找数据外泄
  tcp.dstport != 80 and tcp.dstport != 443 and
  tcp.len > 1000 and
  ip.dst != 192.168.0.0/16

场景5：查找 C&C 通信
  (dns.qry.name matches "^[a-z0-9]{15,}\." and dns.flags.response == 0) or
  (tls.handshake.extensions_server_name matches "^[a-z0-9]{15,}\." and
   tls.handshake.type == 1)
```

---

## 十四、TLS/SSL 深度解密

### 14.1 TLS 解密方法详解

**方法1：SSLKEYLOGFILE（浏览器流量）**

```bash
# 设置环境变量（关键步骤）
# Linux/MacOS
echo 'export SSLKEYLOGFILE=~/sslkey.log' >> ~/.bashrc
source ~/.bashrc

# Windows（PowerShell 永久设置）
[System.Environment]::SetEnvironmentVariable('SSLKEYLOGFILE', 'C:\sslkey.log', 'User')

# Windows（CMD 永久设置）
setx SSLKEYLOGFILE "C:\sslkey.log"

# 验证
echo $SSLKEYLOGFILE           # Linux/Mac
echo %SSLKEYLOGFILE%          # Windows CMD
```

在 Wireshark 中配置：
```
Edit → Preferences → Protocols → TLS
→ (Pre)-Master-Secret log filename
→ 浏览选择 sslkey.log 文件路径
→ 确定
```

**方法2：服务器私钥解密**

```
Edit → Preferences → Protocols → TLS
→ RSA keys list → Edit
→ 新增条目：
   IP address: 192.168.1.50
   Port: 443
   Protocol: http
   Key File: /path/to/server.key
```

注意：此方法仅适用于使用 RSA 密钥交换的 TLS 会话，不支持 ECDHE/DHE 前向安全。

**方法3：中间人代理（MITM Proxy）**

```bash
# 使用 mitmproxy 捕获 HTTPS 流量
mitmproxy --mode transparent --listen-port 8080

# 或使用 mitmdump 导出密钥
mitmdump --sslkeylogfile /path/to/sslkey.log

# 配置设备代理指向 mitmproxy
# 安装 mitmproxy CA 证书到设备
# Wireshark 中配置 SSLKEYLOGFILE 解密
```

### 14.2 TLS 证书分析

```bash
# 过滤所有证书
tls.handshake.certificate

# 查看证书中的通用名
tls.handshake.certificate.extensions.subject_alt_name contains "example.com"

# 查找自签名证书
# 需要手动检查 Issuer 和 Subject 是否相同

# 查找过期证书
# 检查 tls.handshake.certificate.validity_not_after 字段

# 查找弱密钥套件
tls.handshake.ciphersuite in {
  0x002f,   # TLS_RSA_WITH_AES_128_CBC_SHA
  0x0035,   # TLS_RSA_WITH_AES_256_CBC_SHA
  0x000a,   # TLS_RSA_WITH_3DES_EDE_CBC_SHA
  0x002c,   # TLS_ECDHE_ECDSA_WITH_3DES_EDE_CBC_SHA
}
```

### 14.3 TLS 版本和密码套件审计

```bash
# TLS 1.0/1.1 过滤（不安全版本）
tls.record.version == 0x0301    # TLS 1.0
tls.record.version == 0x0302    # TLS 1.1
tls.record.version == 0x0303    # TLS 1.2
tls.record.version == 0x0304    # TLS 1.3

# 客户端支持的密码套件
tls.handshake.ciphersuite

# 服务端选择的密码套件
tls.handshake.ciphersuite && tls.handshake.type == 2

# 检查是否使用 RC4
tls.handshake.ciphersuite in {0x0024 0x0028 0x0068 0x0069 0x008a 0x008b 0x008c}

# 检查是否使用 CBC 模式（可能受 BEAST/Lucky13 攻击）
tls.handshake.ciphersuite matches ".*CBC.*"
```

---

## 十五、tshark 命令行工具

### 15.1 基本抓包

```bash
# 列出可用网卡
tshark -D

# 在指定网卡抓包
tshark -i eth0

# 抓包并保存到文件
tshark -i eth0 -w capture.pcap

# 抓取指定数量后停止
tshark -i eth0 -c 100

# 抓包过滤器（BPF 语法）
tshark -i eth0 -f "port 80" -w http.pcap
tshark -i eth0 -f "host 192.168.1.100 and port 443" -w https.pcap
tshark -i eth0 -f "not port 22" -w no_ssh.pcap

# 多网卡同时抓包
tshark -i eth0 -i eth1 -w multi.pcap
```

### 15.2 显示过滤器

```bash
# 读取 pcap 并应用显示过滤器
tshark -r capture.pcap -Y "http"

# HTTP 请求
tshark -r capture.pcap -Y "http.request.method == POST"

# 特定 IP
tshark -r capture.pcap -Y "ip.addr == 192.168.1.100"

# 组合过滤
tshark -r capture.pcap -Y "http and ip.src == 192.168.1.50"
```

### 15.3 字段提取

```bash
# 提取特定字段
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.dstport

# 提取 HTTP URL
tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri

# 提取 HTTP POST 数据
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e http.file_data

# 提取 DNS 查询
tshark -r capture.pcap -Y "dns.qry.name" -T fields -e dns.qry.name

# 提取 User-Agent
tshark -r capture.pcap -Y "http.user_agent" -T fields -e http.user_agent

# 提取 TLS SNI
tshark -r capture.pcap -Y "tls.handshake.extensions_server_name" \
      -T fields -e ip.dst -e tls.handshake.extensions_server_name

# 指定分隔符
tshark -r capture.pcap -T fields -e frame.number -e ip.src -e ip.dst -E separator=,

# 带表头
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.dstport -E header=y
```

### 15.4 统计分析

```bash
# 协议层级统计
tshark -r capture.pcap -q -z io,phs

# 端点统计
tshark -r capture.pcap -q -z endpoints,ip

# 对话统计
tshark -r capture.pcap -q -z conv,tcp

# HTTP 请求统计
tshark -r capture.pcap -q -z http,tree

# DNS 统计
tshark -r capture.pcap -q -z dns,tree

# 包长度分布
tshark -r capture.pcap -q -z plen,io

# IO 图表数据
tshark -r capture.pcap -q -z io,stat,1
```

### 15.5 高级 tshark 用法

```bash
# 实时监控 HTTP 请求
tshark -i eth0 -Y "http.request" -T fields -e ip.src -e http.host -e http.request.uri

# 实时监控 DNS 查询
tshark -i eth0 -Y "dns.qry.name" -T fields -e ip.src -e dns.qry.name

# 导出 HTTP 对象
tshark -r capture.pcap --export-objects http,/tmp/http_objects/

# 导出 SMB 对象
tshark -r capture.pcap --export-objects smb,/tmp/smb_objects/

# 解码 TLS 流量（使用 SSLKEYLOGFILE）
tshark -r capture.pcap -o tls.keylog_file:sslkey.log -Y "http"

# 输出为 JSON
tshark -r capture.pcap -T json -Y "http.request" > http_requests.json

# 输出为 PDML（XML 格式）
tshark -r capture.pcap -T pdml > capture.xml

# 输出为 C 格式数组
tshark -r capture.pcap -T C -c 10
```

---

## 十六、其他命令行工具

### 16.1 dumpcap

```bash
# dumpcap 是 Wireshark 底层抓包引擎，资源占用更低
dumpcap -i eth0 -w capture.pcap

# 多文件轮转（每 100MB 或 60 秒一个文件）
dumpcap -i eth0 -w capture.pcap -b filesize:100000 -b duration:60

# 无限抓包（环形缓冲）
dumpcap -i eth0 -w capture.pcap -b files:5 -b filesize:100000

# 指定快照长度（截断每个包）
dumpcap -i eth0 -w capture.pcap -s 128
```

### 16.2 editcap

```bash
# 分割大文件
editcap -c 10000 large.pcap small      # 每 10000 包一个文件

# 按时间分割
editcap -A "2024-01-01 10:00:00" -B "2024-01-01 11:00:00" capture.pcap filtered.pcap

# 去除重复包
editcap -d capture.pcap dedup.pcap

# 修改时间戳
editcap -t 3600 capture.pcap adjusted.pcap   # 时间戳前移 1 小时

# 转换文件格式
editcap -F pcapng capture.pcap capture.pcapng

# 仅保留特定包
editcap -r -A "2024-01-01 10:00:00" -B "2024-01-01 12:00:00" capture.pcap 1hour.pcap
```

### 16.3 mergecap

```bash
# 合并多个 pcap 文件
mergecap -w merged.pcap file1.pcap file2.pcap file3.pcap

# 按时间戳排序合并
mergecap -a -w merged.pcap file1.pcap file2.pcap

# 指定输出格式
mergecap -F pcapng -w merged.pcapng file1.pcap file2.pcap
```

### 16.4 capinfos

```bash
# 获取 pcap 文件信息
capinfos capture.pcap

# 仅输出特定信息
capinfos -c capture.pcap      # 包数
capinfos -d capture.pcap       # 持续时间
capinfos -u capture.pcap       # 数据量
capinfos -e capture.pcap       # 结束时间
capinfos -a capture.pcap        # 开始时间

# 输出为表格
capinfos -T -c -u -e -a *.pcap

# 输出为 CSV
capinfos -m *.pcap > pcap_summary.csv
```

### 16.5 reordercap

```bash
# 按时间戳重新排序数据包
reordercap capture.pcap reordered.pcap
```

---

## 十七、网络取证案例分析

### 17.1 案例1：分析 C&C 通信

```bash
# 步骤1：统计协议分布，找异常协议
tshark -r capture.pcap -q -z io,phs
# 观察：大量 TLS 流量到未知 IP，少量 DNS 查询

# 步骤2：提取所有 DNS 查询，找可疑域名
tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name | sort -u | uniq -c | sort -rn

# 步骤3：提取所有 TLS SNI，找可疑目标
tshark -r capture.pcap -Y "tls.handshake.type == 1" -T fields -e ip.dst -e tls.handshake.extensions_server_name

# 步骤4：检查固定间隔通信（心跳包）
tshark -r capture.pcap -Y "ip.dst == 185.10.10.5" -T fields -e frame.time_relative -e tcp.len | awk '{print $1}' | uniq -c

# 步骤5：检查数据上传量
tshark -r capture.pcap -q -z conv,ip | sort -k3 -rn | head -20
```

**C&C 通信特征**：
- 固定间隔的 HTTP/TLS 请求
- 访问动态生成的域名（DGA）
- 异常的 User-Agent 字符串
- 数据上传量远大于下载量
- 使用非标端口通信

### 17.2 案例2：分析数据泄露

```bash
# 步骤1：识别大流量连接
tshark -r capture.pcap -q -z conv,tcp | sort -k1 -rn | head -10

# 步骤2：检查 DNS 隧道
# DNS 查询异常长（超过 50 字符）
tshark -r capture.pcap -Y "dns.qry.name and length(dns.qry.name) > 50" -T fields -e ip.src -e dns.qry.name

# 步骤3：检查 ICMP 隧道
tshark -r capture.pcap -Y "icmp and data.icmp" -T fields -e ip.src -e ip.dst -e data.data

# 步骤4：检查 HTTP POST 数据上传
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e http.host -e http.request.uri -e http.content_length

# 步骤5：检查 TLS 上传量
tshark -r capture.pcap -Y "tls and ip.src == 192.168.1.100" -T fields -e frame.time -e tls.record.length | awk '{sum+=$2; print $1, sum}'

# 步骤6：提取上传文件
tshark -r capture.pcap --export-objects http,/tmp/exfil_files/
tshark -r capture.pcap --export-objects smb,/tmp/smb_files/
```

### 17.3 案例3：分析中间人攻击

```bash
# 步骤1：检查 ARP 表是否有异常
tshark -r capture.pcap -Y "arp.opcode == 2" -T fields -e arp.src.proto_ipv4 -e arp.src.hw_mac -e arp.dst.proto_ipv4
# 网关 IP 对应多个 MAC → ARP 欺骗

# 步骤2：检查 TLS 证书变化
tshark -r capture.pcap -Y "tls.handshake.certificate" -T fields -e ip.src -e x509sat.printableString | sort -u

# 步骤3：检查 DHCP 欺骗
tshark -r capture.pcap -Y "dhcp.option.type == 3" -T fields -e dhcp.option.router -e ip.src

# 步骤4：检查 DNS 劫持
tshark -r capture.pcap -Y "dns.flags.response == 1" -T fields -e dns.qry.name -e dns.a -e ip.src | sort -u
# 同一域名返回不同 IP → 可能 DNS 劫持

# 步骤5：验证证书链完整性
tshark -r capture.pcap -Y "tls.handshake.type == 11" -T fields -e ip.src -e tls.handshake.certificate
```

### 17.4 案例4：Web 应用攻击取证

```bash
# SQL 注入取证
tshark -r capture.pcap -Y 'http.request.uri contains "union" or http.request.uri contains "select" or http.request.uri contains "'\''" ' -T fields -e frame.time -e ip.src -e http.request.uri

# XSS 攻击取证
tshark -r capture.pcap -Y 'http.request.uri contains "<script>" or http.request.uri contains "javascript:" or http.request.uri contains "onerror="' -T fields -e frame.time -e ip.src -e http.request.full_uri

# 目录遍历取证
tshark -r capture.pcap -Y 'http.request.uri contains "../" or http.request.uri contains "%2e%2e"' -T fields -e ip.src -e http.request.uri

# 文件上传攻击取证
tshark -r capture.pcap -Y 'http.request.method == "POST" and http.content_type contains "multipart"' -T fields -e ip.src -e http.request.uri

# Web Shell 通信取证
tshark -r capture.pcap -Y 'http.request.uri matches "(?i)(shell|cmd|eval|exec)" and http.request.method == "POST"' -T fields -e frame.time -e ip.src -e ip.dst -e http.request.uri
```

---

## 十八、TCP 性能分析

### 18.1 TCP 性能指标

```bash
# 查看重传
tshark -r capture.pcap -Y "tcp.analysis.retransmission" -T fields -e ip.src -e ip.dst -e tcp.seq

# 查看 duplicate ACK
tshark -r capture.pcap -Y "tcp.analysis.duplicate_ack" | wc -l

# 查看零窗口
tshark -r capture.pcap -Y "tcp.window_size_value == 0" -T fields -e ip.src -e ip.dst

# 查看 RTT（往返时延）
tshark -r capture.pcap -Y "tcp.analysis.ack_rtt" -T fields -e ip.src -e ip.dst -e tcp.analysis.ack_rtt

# 查看乱序包
tshark -r capture.pcap -Y "tcp.analysis.out_of_order" | wc -l
```

### 18.2 TCP 流图

```
Statistics → TCP Stream Graphs

1. Round Trip Time Graph（RTT 图）：
   显示 RTT 随时间变化，帮助发现网络延迟问题

2. Throughput Graph（吞吐量图）：
   显示每秒传输的数据量

3. Time Sequence Graph（时间序列图）：
   显示序列号随时间的变化

4. Window Scaling Graph（窗口缩放图）：
   显示接收窗口大小变化

5. Segments Graph（段图）：
   显示每个数据段的发送时间和大小
```

### 18.3 网络性能诊断

```
常见问题诊断：

问题1：高延迟
  特征：RTT > 200ms，ACK 延迟
  过滤：tcp.analysis.ack_rtt > 0.2
  分析：检查 RTT 图表，确认延迟是持续还是间歇性

问题2：高重传率
  特征：重传率 > 5%
  过滤：tcp.analysis.retransmission
  分析：检查是否有特定段反复重传，可能是 MTU 问题

问题3：零窗口
  特征：接收方窗口为 0
  过滤：tcp.window_size_value == 0
  分析：接收方处理能力不足，需优化应用层

问题4：连接重置
  特征：大量 RST 包
  过滤：tcp.flags.reset == 1
  分析：可能是防火墙拦截或服务异常关闭
```

---

## 十九、Lua 脚本扩展

### 19.1 自定义协议解析器

```lua
-- custom_protocol.lua — 自定义协议解析器
-- 将此文件放到 Wireshark 的 plugins 目录或通过 Lua 脚本加载

local custom_proto = Proto("custom", "Custom Protocol")

-- 定义字段
local f_command = ProtoField.uint8("custom.command", "Command", base.DEC)
local f_data = ProtoField.string("custom.data", "Data", base.STRING)
local f_length = ProtoField.uint16("custom.length", "Length", base.DEC)

custom_proto.fields = { f_command, f_data, f_length }

-- 解析函数
function custom_proto.dissector(buffer, pinfo, tree)
    local length = buffer:len()
    if length < 3 then return end

    pinfo.cols.protocol = "CUSTOM"
    
    local subtree = tree:add(custom_proto, buffer(), "Custom Protocol Data")
    
    -- 命令字段（1 字节）
    local command = buffer(0, 1):uint()
    subtree:add(f_command, buffer(0, 1))
    
    -- 长度字段（2 字节）
    local data_length = buffer(1, 2):uint()
    subtree:add(f_length, buffer(1, 2))
    
    -- 数据字段
    if length >= 3 + data_length then
        subtree:add(f_data, buffer(3, data_length))
    end
    
    -- 设置 Info 列
    local cmd_name = {
        [0x01] = "LOGIN",
        [0x02] = "LOGOUT",
        [0x03] = "DATA",
        [0x04] = "HEARTBEAT",
        [0x05] = "FILE_TRANSFER",
    }
    pinfo.cols.info = cmd_name[command] or "UNKNOWN"
end

-- 注册到 TCP 端口 9999
local tcp_port = DissectorTable.get("tcp.port")
tcp_port:add(9999, custom_proto)
```

### 19.2 自定义过滤器

```lua
-- custom_filter.lua — 自定义过滤逻辑
-- 检测可疑的 HTTP 请求模式

local suspicious_http = Proto("suspicious_http", "Suspicious HTTP")

-- 注册 tap
local function init_listener()
    local tap = Listener.new("http")

    function tap.packet(pinfo, tvb, tapinfo)
        local uri = tapinfo and tapinfo.request_uri or ""
        
        -- 检测 SQL 注入特征
        if uri:match("'") or uri:match("union") or uri:match("select") then
            print(string.format("[ALERT] SQL Injection: %s from %s",
                  uri, pinfo.src_ip))
        end
        
        -- 检测路径遍历
        if uri:match("%.%.") then
            print(string.format("[ALERT] Path Traversal: %s from %s",
                  uri, pinfo.src_ip))
        end
    end
    
    function tap.draw()
        print("[Suspicious HTTP Detection Complete]")
    end
end

-- 初始化
register_lua_script("suspicious_http")
init_listener()
```

---

## 二十、VoIP 分析

### 20.1 SIP 协议分析

```bash
# SIP 过滤
sip
sip.Method == "INVITE"
sip.Method == "REGISTER"
sip.Status-Code == 200

# 查看 SIP 呼叫流程
Statistics → VoIP Calls

# 导出 SIP 对话
Telephony → SIP → Flows
```

### 20.2 RTP 流分析

```bash
# RTP 流过滤
rtp
rtp.p_type == 0          # G.711 μ-law
rtp.p_type == 8          # G.711 A-law
rtp.ssrc                  # 同步源标识

# 查看 RTP 流统计
Telephony → RTP → Stream Analysis

# 提取 RTP 流信息
tshark -r capture.pcap -Y "rtp" -T fields -e ip.src -e ip.dst -e rtp.ssrc -e rtp.p_type

# 导出 RTP 音频
Telephony → RTP → Stream Analysis → Save Payload
```

### 20.3 VoIP 通话重建

```
Telephony → VoIP Calls → Start Player

功能：
  1. 自动识别 SIP/RTP 流
  2. 重建呼叫流程
  3. 播放音频内容
  4. 导出波形图

通话流程可视化：
  1. REGISTER → 注册
  2. INVITE → 呼叫
  3. 180 Ringing → 振铃
  4. 200 OK → 接听
  5. ACK → 确认
  6. RTP 通话
  7. BYE → 挂断
```

---

## 二十一、无线网络分析

### 21.1 802.11 过滤

```bash
# 管理帧
wlan.fc.type == 0                    # 管理帧
wlan.fc.subtype == 8                 # Beacon 帧
wlan.fc.subtype == 0                 # 关联请求
wlan.fc.subtype == 4                 # 探测请求

# 控制帧
wlan.fc.type == 1                    # 控制帧
wlan.fc.subtype == 11                # RTS
wlan.fc.subtype == 12                # CTS
wlan.fc.subtype == 14                # ACK

# 数据帧
wlan.fc.type == 2                    # 数据帧

# 指定 SSID
wlan.ssid == "TargetNetwork"

# 指定 BSSID
wlan.bssid == 00:11:22:33:44:55

# 指定信道
wlan_radio.channel == 6

# WPA 握手
eapol                               # EAPOL（WPA 认证）帧
```

### 21.2 无线安全分析

```bash
# 查找隐藏 SSID
wlan.fc.subtype == 8 and wlan.ssid == ""

# 查找弱加密
wlan.fc.subtype == 8 and wlan.fixed.capabilities.privacy == 0
# Beacon 中 Privacy=0 → 开放网络

# WPA 握手分析
eapol and wlan.addr == 00:11:22:33:44:55

# 查找邪恶双子 AP
wlan.fc.subtype == 8 and wlan.ssid == "TargetSSID"
# 检查是否有多个 BSSID 使用同一 SSID

# 查找去认证攻击
wlan.fc.subtype == 12               # 去认证帧
wlan.fixed.reason_code == 7         # Class 3 frame
```

---

## 二十二、Wireshark 最佳实践

### 22.1 抓包优化

```
1. 选择正确的网卡
   - 物理网卡优于虚拟网卡
   - 监听口（SPAN/Mirror）优于普通口

2. 设置抓包过滤器
   - 排除自身流量：not host <本机IP>
   - 排除 SSH：not port 22
   - 排除广播/组播：not broadcast and not multicast
   - 减少不必要的背景流量

3. 使用快照长度
   - 仅分析头部：-s 128（节省空间）
   - 完整分析：-s 0（默认，全包捕获）

4. 文件轮转
   - 设置文件大小上限（如 100MB）
   - 设置时间上限（如 1 小时）
   - 保留最近 N 个文件

5. 性能考虑
   - 大文件使用 editcap 分割
   - 使用 tshark 代替 Wireshark GUI 处理大文件
   - 合理设置显示过滤器减少渲染负担
```

### 22.2 分析方法论

```
网络流量分析方法论（自顶向下）：

1. 全局概览
   - Protocol Hierarchy → 了解流量构成
   - Endpoints → 找异常主机
   - Conversations → 找异常连接

2. 协议分析
   - DNS → 检查域名解析
   - HTTP → 检查 Web 请求
   - TLS → 检查加密通信目标
   - ICMP → 检查异常 ICMP 流量

3. 行为分析
   - 时间模式 → 固定间隔通信
   - 数据流向 → 上传 vs 下载
   - 连接频率 → 异常高频连接

4. 深入分析
   - TCP 流追踪 → 完整对话内容
   - 对象导出 → 提取传输文件
   - 流图可视化 → 时序关系

5. 取证报告
   - 记录关键包号
   - 截图关键证据
   - 导出过滤后的 pcap
   - 编写分析报告
```

### 22.3 Wireshark Profile 管理

```
Profile 管理（Edit → Configuration Profiles）：

  | Profile 名称 | 用途 | 自定义内容 |
  |-------------|------|-----------|
  | Default | 日常使用 | 默认设置 |
  | Security | 安全分析 | 安全相关过滤器、着色规则 |
  | Performance | 性能分析 | TCP 性能相关过滤器 |
  | VoIP | 语音分析 | SIP/RTP 相关设置 |
  | Wireless | 无线分析 | 802.11 相关设置 |

着色规则（Coloring Rules）：
  自定义着色帮助快速识别异常：
  - 红色：TCP RST
  - 橙色：HTTP 4xx/5xx
  - 黄色：DNS 查询到可疑域名
  - 紫色：TLS 证书异常
  - 青色：可疑 POST 请求
```

---

> ⚠️ **安全提示**：Wireshark 是网络分析的核心工具。在使用抓包功能时，请确保已获得网络管理者的授权。未经授权抓取网络流量可能违反相关法律法规。在使用 TLS 解密功能时，务必注意保护用户隐私和敏感数据。
