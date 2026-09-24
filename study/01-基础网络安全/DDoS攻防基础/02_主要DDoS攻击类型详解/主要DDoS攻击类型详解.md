# 主要DDoS攻击类型详解

### 2.1 SYN Flood原理与防御

**攻击原理：**

SYN Flood利用TCP三次握手的缺陷。攻击者发送大量伪造源IP的SYN包，服务器为每个SYN分配资源并回复SYN-ACK，但永远收不到ACK完成握手，导致半连接队列（SYN Queue）耗尽。

```
正常TCP三次握手:
  客户端 ──SYN──→ 服务器
  客户端 ←─SYN-ACK─ 服务器
  客户端 ──ACK──→ 服务器  ← 连接建立

SYN Flood攻击:
  攻击者(伪造源IP) ──SYN──→ 服务器
                          ←─SYN-ACK─ 伪造IP(收不到)
  攻击者(伪造源IP) ──SYN──→ 服务器
                          ←─SYN-ACK─ 伪造IP(收不到)
  ... 重复数万次

  服务器半连接队列被占满 → 合法用户无法建立连接
```

**防御措施：**

1. **SYN Cookies**：服务器不分配资源，而是将状态编码在序列号中
2. **SYN Proxy**：防火墙代理握手，验证成功才转发给后端
3. **连接速率限制**：限制每秒新连接数

```bash
# Linux启用SYN Cookies
echo 1 > /proc/sys/net/ipv4/tcp_syncookies

# 减小SYN-ACK重试次数（减少资源占用时间）
echo 2 > /proc/sys/net/ipv4/tcp_synack_retries

# 增大SYN队列长度
echo 8192 > /proc/sys/net/ipv4/tcp_max_syn_backlog

# 持久化配置（/etc/sysctl.conf）
# net.ipv4.tcp_syncookies = 1
# net.ipv4.tcp_synack_retries = 2
# net.ipv4.tcp_max_syn_backlog = 8192
```

```bash
# iptables限制每IP SYN速率
iptables -A INPUT -p tcp --syn -m limit --limit 50/s --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP
```

### 2.2 UDP Flood原理与防御

**攻击原理：** 攻击者向目标发送大量UDP包，目标处理每个包并回复ICMP端口不可达，消耗带宽和CPU。

```
UDP Flood:
  攻击者 ──UDP包(随机端口)──→ 目标
  目标检查端口 → 无服务监听 → 回复ICMP端口不可达
  大量UDP包 → 带宽耗尽 + ICMP回复消耗CPU
```

**防御措施：**

```bash
# iptables限制UDP速率
iptables -A INPUT -p udp -m limit --limit 100/s --limit-burst 200 -j ACCEPT
iptables -A INPUT -p udp -j DROP

# 限制ICMP端口不可达回复速率
iptables -A OUTPUT -p icmp --icmp-type port-unreachable -m limit --limit 10/s -j ACCEPT
iptables -A OUTPUT -p icmp --icmp-type port-unreachable -j DROP
```

### 2.3 HTTP Flood/CC攻击原理与防御

**攻击原理：** CC攻击（Challenge Collapsar）模拟大量合法HTTP请求，耗尽Web服务器应用层资源（CPU、内存、数据库连接）。

```
CC攻击 vs 流量型攻击:

流量型攻击: 大带宽消耗 → 目标带宽不足
  ┌──────────────────┐
  │ 10Gbps UDP Flood  │ → 带宽耗尽
  └──────────────────┘

CC攻击: 低带宽消耗 → 应用资源耗尽
  ┌──────────────────────────────┐
  │ 1000个请求/秒 "GET /search?q=..." │
  │ 每个请求触发数据库查询(耗时2秒)    │
  │ → 数据库连接池耗尽 → 服务无响应   │
  └──────────────────────────────┘
  带宽可能只有10Mbps，但应用已崩溃
```

**防御措施：**

```nginx
# Nginx限流配置
http {
    # 定义请求速率限制
    limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;
    # 定义连接数限制
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    server {
        # 每IP每秒最多10个请求，突发20个
        limit_req zone=req_limit burst=20 nodelay;
        # 每IP最多5个并发连接
        limit_conn conn_limit 5;

        # 慢速攻击防护：超时设置
        client_body_timeout 10s;
        client_header_timeout 10s;
        keepalive_timeout 15s;
        send_timeout 10s;

        # 限制请求体大小
        client_max_body_size 1m;
    }
}
```

```bash
# WAF规则示例（ModSecurity）
# 防止慢速POST攻击
SecRequestBodyLimit 1048576
SecRequestBodyNoFilesLimit 1048576
SecRequestBodyInMemoryLimit 131072
# 请求处理超时
SecRule REQBODY_PROCESSING_DURATION "@gt 30" "id:1001,deny,status:408"
```

### 2.4 DNS Amplification原理与防御

```
DNS放大攻击:

  攻击者(伪造源IP=目标)    开放DNS解析器           目标
     │                        │                    │
     │ 60字节DNS查询(ANY)     │                    │
     ├───────────────────────→│                    │
     │                        │ 3000字节DNS响应    │
     │                        ├───────────────────→│ 大量流量
     │                        │                    │
     │ (向数万个开放解析器     │                    │
     │  同时发送伪造查询)     │                    │
     │                        │                    │
     │ 总放大效果:            │                    │
     │ 100Mbps请求 →          │                    │
     │ 5-7Gbps响应流量        │                    │
```

**防御措施：**

```bash
# 1. 关闭DNS递归（仅允许本地客户端）
# /etc/bind/named.conf.options
options {
    recursion no;          # 关闭递归
    allow-query { any; };  # 允许查询权威域
    allow-recursion { localnets; };  # 仅本地递归
};

# 2. 限制DNS响应速率
iptables -A OUTPUT -p udp --sport 53 -m limit --limit 1000/s -j ACCEPT
iptables -A OUTPUT -p udp --sport 53 -j DROP

# 3. BCP38: 源地址验证（防止伪造源IP）
# 在边界路由器配置uRPF
# Cisco: interface Gi0/0 → ip verify unicast source reachable-via rx
```

### 2.5 NTP Amplification原理与防御

NTP放大攻击利用NTP monlist命令，请求小、响应大（放大倍数可达556倍）。

```
NTP放大攻击:
  攻击者 → 开放NTP服务器(monlist命令)
  请求: ~234字节
  响应: ~556 * 234 ≈ 100KB+ (巨大放大倍数)

  单台NTP服务器可产生556倍放大
  数千台 → 数Tbps级流量
```

**防御措施：**

```bash
# 1. 升级NTP服务版本（4.2.7p270+已移除monlist）
# 2. 限制monlist访问（旧版本）
# /etc/ntp.conf
restrict default nomodify notrap nopeer noquery
restrict -6 default nomodify notrap nopeer noquery

# 允许本地网络查询
restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

# 3. 禁用monlist
disable monlist

# 4. iptables限制NTP端口
iptables -A INPUT -p udp --dport 123 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p udp --dport 123 -j DROP
```

---

---

