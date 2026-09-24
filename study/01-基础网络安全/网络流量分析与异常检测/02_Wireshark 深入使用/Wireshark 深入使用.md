# Wireshark 深入使用

### 2.1 高级过滤技巧

Wireshark 有两套过滤器：捕获过滤器（BPF 语法，抓包时生效）和显示过滤器（Wireshark 专有语法，抓包后过滤）。

**捕获过滤器（BPF 语法）：**

```
# 只抓某主机的80端口流量
host 192.168.1.100 and port 80

# 抓某网段的所有流量
net 192.168.1.0/24

# 排除 ARP 和广播，减少噪音
not arp and not (broadcast or multicast)

# 只抓 TCP SYN 包（扫描检测）
tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0

# 只抓 DNS 查询
udp port 53 or tcp port 53
```

**显示过滤器（实战常用）：**

```
# 基础字段过滤
ip.addr == 192.168.1.100          # 源或目的为该IP
ip.src == 10.0.0.1 && ip.dst == 8.8.8.8
tcp.port == 443
http.request.method == "POST"

# 协议组合与逻辑
http or dns or tls                 # 只看应用层握手
tcp.flags.syn == 1 && tcp.flags.ack == 0   # SYN扫描
!(ip.src == 192.168.1.0/24)       # 外联流量

# 字符串与内容匹配
http contains "password"           # HTTP中包含password
http.request.uri contains "admin"   # URL含admin
frame contains "SELECT"            # 任意层含SELECT（SQL注入痕迹）

# TLS 证书与 SNI
tls.handshake.type == 1            # ClientHello
tls.handshake.extensions_server_name contains "evil"
ssl.handshake.type == 11 && ssl.handshake.certificate contains "CN="

# 时间间隔（检测Beaconing）
# 用 Statistics -> I/O Graphs 配合更直观

# TCP 异常
tcp.analysis.retransmission        # 重传
tcp.analysis.fast_retransmission   # 快速重传
tcp.analysis.zero_window          # 零窗口
tcp.flags.reset == 1              # RST包

# 过滤特定HTTP状态码
http.response.code == 404
http.response.code >= 500
```

**复杂表达式实战：**

```
# 检测可疑的TLS外联（非标准端口、非常见SNI）
tls.handshake.type == 1 && not tls.handshake.extensions_server_name matches "google|facebook|microsoft|apple"

# 检测HTTP上传大文件（POST且Content-Length大）
http.request.method == "POST" && http.content_length > 1000000

# 检测DNS隧道（超长子域）
dns.qry.name.len > 50
dns.qry.type == 16  # TXT记录查询（常用于DNS隧道数据外泄）

# 检测ICMP隧道（大载荷）
icmp and data.len > 64
```

### 2.2 协议分析与解密

Wireshark 能解码上千种协议，但加密协议（TLS/IPSec/WLAN）默认看不到明文。掌握解密技术是深度分析的关键。

**TLS 解密：**

原理是用会话密钥（Session Key）把加密的 ApplicationData 解密成明文。获取密钥有三种途径：

```
方法1: 浏览器导出预主密钥（最常用）
# 设置环境变量，让浏览器把密钥写到文件
# Windows (PowerShell):
$env:SSLKEYLOGFILE = "C:\temp\sslkeys.log"
# 然后启动 Chrome/Firefox，所有TLS会话密钥写入该文件

# Wireshark 配置:
# Edit -> Preferences -> Protocols -> TLS
# (Pre)-Master-Secret log filename = C:\temp\sslkeys.log
```

配置后，Wireshark 会自动用密钥解密 TLS 流量，在包详情中新增 "Decrypted TLS" 层，可见明文 HTTP 请求/响应。

```
方法2: 服务端私钥解密（适用于RSA密钥交换，不适用DHE/ECDHE）
# Edit -> Preferences -> Protocols -> TLS -> RSA keys list
# 添加服务端私钥文件、密码、IP、端口
# 注意: 现代TLS 1.3与前向保密机制下此方法无效

方法3: 中间人代理（mitmproxy）
mitmproxy --mode transparent --listen-port 8080
# 抓包设备指向mitmproxy，Wireshark抓代理与目标间的流量
```

**WLAN 解密：**

抓 802.11 无线帧时，数据帧是加密的（WPA2/WPA3）。解密需要 EAPOL 4 次握手包。

```
# Wireshark配置:
# Edit -> Preferences -> Protocols -> IEEE 802.11
# Enable decryption: 勾选
# Decryption keys: 添加 wpa-pwd:你的WiFi密码
# 抓包时必须包含关联和4次握手，否则无法派生PTK
```

### 2.3 统计分析工具

Wireshark 的 Statistics 菜单是流量分析的"瑞士军刀"。

**1. 捕获文件属性（Capture File Properties）**

显示包数、流量大小、捕获时长、平均速率、是否有丢包等概览。

**2. 协议分层统计（Protocol Hierarchy）**

```
# 典型输出:
Frame 100000 100%
  Ethernet 100000 100%
    IPv4 98000 98%
      TCP 85000 85%
        HTTP 5000 5%
        TLS 30000 30%
      UDP 12000 12%
        DNS 3000 3%
    ARP 1500 1.5%
```

价值：一眼看出协议占比异常。正常内网 ARP 应很少，如果 ARP 占比 >10% 可能是 ARP 扫描或中毒；如果大量未知 UDP，可能是 P2P 或隧道。

**3. 会话统计**

按五元组聚合，显示每条会话的包数、字节数、持续时间。可按字节数排序，快速发现"大户"——可能是数据外泄或大文件下载。

**4. I/O 图表（I/O Graphs）**

```
# 实战配置示例:
# Filter: ip.addr==192.168.1.100
# Graph Type: Bytes/tick
# 看某主机的流量时序曲线，发现规律性脉冲=Beaconing
```

I/O 图表对检测周期性通信（C2 心跳）极为有效。把 Y 轴设为"packets/tick"，X 轴 1 秒一格，如果出现每隔 60 秒的固定峰值，就是典型 Beaconing。

### 2.4 专家信息系统与异常提示

Wireshark 内置专家系统，自动给包打标签提示异常：

| 标签 | 含义 | 可能原因 |
|------|------|----------|
| Retransmission | TCP重传 | 网络丢包、拥塞 |
| Fast Retransmission | 快速重传 | 收到3个重复ACK |
| Zero Window | 零窗口 | 接收方处理不过来 |
| Window Update | 窗口更新 | 接收方恢复 |
| Out-of-Order | 乱序 | 路径多径、丢包重排 |
| Keep-Alive | 保活 | TCP保活机制 |
| Connection RST | 连接重置 | 服务拒绝、防火墙、扫描 |
| Previous segment lost | 前序段丢失 | 丢包 |

实战：在专家信息中看到大量"Connection RST (TCP)"且来自同一源 IP，配合 SYN 多、ACK 少，基本可判定为 SYN 扫描。

### 2.5 Wireshark 自定义配置与插件

**1. 自定义协议解析器表：** Wireshark 允许把某个端口强制按某协议解析。

```
# Analyze -> Decode As
# 例: 把 8443 端口强制按 TLS 解析（默认可能是HTTP）
```

**2. Profile 管理：** 不同场景用不同配置（字体、列布局、过滤器）。Edit → Configuration Profiles，建议建三个 Profile：通用、安全分析、网络排障。

**3. 自定义列：** 在包列表右键列标题可添加自定义列，如 `http.request.uri`、`tls.handshake.extensions_server_name`，便于在列表里直接看到 URL 和 SNI。

**4. Lua 插件：** Wireshark 支持 Lua 编写自定义 dissector。

```lua
-- 示例: 简单自定义协议解析器
local my_proto = Proto("myproto", "My Custom Protocol")
local f_cmd = ProtoField.uint8("myproto.cmd", "Command", base.DEC)
my_proto.fields = { f_cmd }

function my_proto.dissector(buffer, pinfo, tree)
    if buffer:len() < 1 then return end
    pinfo.cols.protocol = "MYPROTO"
    local subtree = tree:add(my_proto, buffer())
    subtree:add(f_cmd, buffer(0,1))
end
-- 注册到UDP 9999端口
DissectorTable.get("udp.port"):add(9999, my_proto)
```

---

---

