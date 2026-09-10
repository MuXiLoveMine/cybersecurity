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
