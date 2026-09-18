# DDoS攻防基础

> 本文档用于网络安全教学与防御技术研究。所有脚本使用模拟数据，不含攻击工具代码。

---

## 目录

- [一、DDoS攻击概述](#一ddos攻击概述)
- [二、主要DDoS攻击类型详解](#二主要ddos攻击类型详解)
- [三、DDoS检测与防御体系](#三ddos检测与防御体系)
- [四、DDoS应急响应流程](#四ddos应急响应流程)
- [五、Python DDoS检测脚本示例](#五python-ddos检测脚本示例)

---

## 一、DDoS攻击概述

### 1.1 DoS与DDoS区别

**DoS（Denial of Service）** 是拒绝服务攻击，单一攻击源向目标发送恶意流量或请求，耗尽其资源使其无法提供正常服务。

**DDoS（Distributed Denial of Service）** 是分布式拒绝服务攻击，攻击者利用大量被控制的设备（僵尸网络/Botnet）同时向目标发起攻击，流量规模远超单一源。

```
DoS vs DDoS 对比:

DoS（单一源）:
  攻击者 ──→ 目标服务器
  特点: 源IP单一，易于封禁

DDoS（分布式）:
  僵尸节点1 ──┐
  僵尸节点2 ──┤
  僵尸节点3 ──┼──→ 目标服务器
  僵尸节点N ──┘
  特点: 源IP分散，难以逐个封禁，流量巨大
```

**关键差异：**

| 特征 | DoS | DDoS |
|------|-----|------|
| 攻击源数量 | 单一 | 数百至数百万 |
| 流量规模 | 较小 | TB级 |
| 防御难度 | 容易（封禁单IP） | 困难（需分布式清洗） |
| 僵尸网络 | 不需要 | 通常需要 |

### 1.2 DDoS攻击分类

根据攻击目标和OSI层次，DDoS可分为三大类：

```
┌─────────────────────────────────────────────────────────┐
│               DDoS攻击分类                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 流量型攻击 (Volumetric Attacks) - 体积压制          │
│     ├── UDP Flood                                      │
│     ├── ICMP Flood                                    │
│     ├── DNS Amplification                             │
│     └── NTP Amplification                             │
│     目标: 耗尽带宽                                    │
│     层次: L3/L4                                       │
│                                                         │
│  2. 协议型攻击 (Protocol Attacks) - 资源耗尽           │
│     ├── SYN Flood                                     │
│     ├── ACK Flood                                    │
│     ├── Fragmentation Attack                          │
│     └── Ping of Death                                │
│     目标: 耗尽连接表/内存                             │
│     层次: L3/L4                                       │
│                                                         │
│  3. 应用层攻击 (Application Attacks) - 精准消耗         │
│     ├── HTTP Flood (GET/POST Flood)                  │
│     ├── CC攻击 (Challenge Collapsar)                 │
│     ├── Slowloris (慢速连接)                          │
│     └── DNS Query Flood                              │
│     目标: 耗尽应用资源(CPU/内存/连接池)              │
│     层次: L7                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.3 常见DDoS攻击工具介绍（理论）

以下工具仅做理论介绍，了解其原理有助于防御研究：

| 工具名称 | 攻击类型 | 说明 |
|---------|---------|------|
| Hping3 | 多种 | 网络数据包构造工具，可用于TCP/UDP/ICMP Flood测试 |
| LOIC | 流量型 | Low Orbit Ion Cannon，简单HTTP/TCP/UDP Flood工具 |
| HOIC | 应用层 | High Orbit Ion Cannon，支持HTTP Flood |
| Slowloris | 应用层 | 慢速HTTP攻击，占用Web服务器连接池 |
| GoldenEye | 应用层 | HTTP Keep-Alive+慢速POST攻击 |

> 注意：上述工具仅可在授权测试环境中使用。在未授权目标上使用属于违法行为。

---

## 二、主要DDoS攻击类型详解

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

## 三、DDoS检测与防御体系

### 3.1 流量基线与异常检测

```
流量基线与异常检测流程:

  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
  │ 1. 流量采集 │───→│ 2. 基线建模  │───→│ 3. 异常检测  │
  │ (NetFlow/   │    │ 统计正常流量 │    │ 偏差超过阈值 │
  │  sFlow)     │    │ 的特征模式   │    │ → 触发告警   │
  └─────────────┘    └──────────────┘    └──────────────┘
                                                    │
                                                    ↓
                                           ┌──────────────┐
                                           │ 4. 自动响应  │
                                           │ 触发清洗/    │
                                           │ 黑洞路由     │
                                           └──────────────┘

基线特征:
  - 正常带宽: 500Mbps ± 50Mbps
  - 正常QPS: 1000/s ± 200/s
  - SYN包占比: < 5%
  - UDP/TCP比例: < 1:3

异常判定:
  - 带宽突增 > 3σ (3倍标准差)
  - SYN占比突增 > 30%
  - 某源IP QPS > 正常10倍
```

### 3.2 DDoS防护设备

**清洗中心（Scrubbing Center）：**

```
DDoS清洗中心架构:

  正常流量 + 攻击流量
         │
         ↓
  ┌──────────────┐
  │ BGP路由牵引  │  ← 将流量重定向到清洗中心
  └──────────────┘
         │
         ↓
  ┌──────────────┐
  │ 流量清洗设备 │  ← 过滤恶意流量
  │ - 限速       │
  │ - 特征匹配   │
  │ - 行为分析   │
  └──────────────┘
         │
         ↓ (干净流量)
  ┌──────────────┐
  │ 回注到目标   │  ← 清洗后正常流量回送到原服务器
  └──────────────┘
```

**黑洞路由（Blackholing）：**

```cisco
# 将攻击目标的流量导向null0（丢弃）
# 在BGP路由器上配置:
router bgp 65000
 address-family ipv4
  network 203.0.113.0 mask 255.255.255.0 route-map BLACKHOLE
 exit-address-family
!
route-map BLACKHOLE permit 10
 set ip next-hop 192.0.2.1  ! RTBH社区属性触发
!
# 使用BGP社区属性触发远端黑洞
# 社区 65000:666 → 黑洞路由
```

### 3.3 Cloudflare/AWS Shield等云防护

**Cloudflare DDoS防护配置（管理面板）：**

```
Cloudflare防护层级:

  用户请求 → Cloudflare边缘节点(Anycast)
              │
              ├── L3/L4防护: 自动检测网络层DDoS
              ├── L7防护:    HTTP Flood/CC攻击防护
              ├── Rate Limiting: 自定义速率规则
              └── Bot管理:    机器人特征识别

配置示例（Cloudflare Rules）:
  Rate Limiting Rule:
    - 匹配: URI Path starts with "/api/"
    - 条件: >100 requests per 10 seconds per IP
    - 动作: Block for 60 seconds

  WAF Rule:
    - 匹配: (http.request.method eq "POST" and
             http.request.uri.path eq "/login")
    - 条件: >5 requests per 60 seconds per IP
    - 动作: Challenge (CAPTCHA)
```

**AWS Shield配置：**

```json
// AWS Shield Advanced - 保护配置
{
  "ProtectionName": "web-app-protection",
  "ResourceArn": "arn:aws:elasticloadbalancing:us-east-1:123456:loadbalancer/app/my-alb/1234567890",
  "Tags": [
    {"Key": "Environment", "Value": "Production"}
  ]
}

// AWS WAF Rate-based Rule
{
  "Name": "RateLimitRule",
  "Priority": 1,
  "Action": {"Block": {}},
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "RateLimitRule"
  },
  "RateLimit": {
    "Limit": 2000,
    "EvaluationWindowSec": 300,
    "AggregateKeyType": "IP"
  }
}
```

### 3.4 Linux服务器层面防护

```bash
# === iptables综合防护规则 ===

# 1. SYN Flood防护
iptables -A INPUT -p tcp --syn -m limit --limit 100/s --limit-burst 200 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# 2. UDP Flood防护
iptables -A INPUT -p udp -m limit --limit 500/s --limit-burst 1000 -j ACCEPT
iptables -A INPUT -p udp -j DROP

# 3. ICMP Flood防护
iptables -A INPUT -p icmp -m limit --limit 10/s --limit-burst 20 -j ACCEPT
iptables -A INPUT -p icmp -j DROP

# 4. 连接数限制（防CC攻击）
iptables -A INPUT -p tcp --dport 80 -m connlimit --connlimit-above 50 -j DROP
iptables -A INPUT -p tcp --dport 443 -m connlimit --connlimit-above 50 -j DROP

# 5. 每IP连接速率限制
iptables -A INPUT -p tcp --dport 80 -m recent --name HTTP --set
iptables -A INPUT -p tcp --dport 80 -m recent --name HTTP --rcheck --seconds 1 --hitcount 20 -j DROP

# === 内核参数优化 ===
sysctl -w net.ipv4.tcp_syncookies=1
sysctl -w net.ipv4.tcp_max_syn_backlog=65535
sysctl -w net.ipv4.tcp_tw_reuse=1
sysctl -w net.core.somaxconn=65535
sysctl -w net.core.netdev_max_backlog=65535
```

---

## 四、DDoS应急响应流程

### 4.1 攻击识别与分类

```
DDoS应急响应 - 攻击识别决策树:

  发现服务异常（响应慢/不可达）
         │
         ↓
  ┌──────────────┐
  │ 1. 确认攻击  │  ← 检查流量监控/带宽图表
  │ 流量是否异常 │    是否有突增？
  └──────────────┘
     │           │
   是 ↓         否 ↓
  ┌──────────────┐    ┌──────────────┐
  │ 2. 攻击分类  │    │ 检查应用/    │
  │              │    │ 服务器故障   │
  └──────────────┘    └──────────────┘
     │
     ├── 带宽突增 → 流量型(UDP/ICMP/Amplification)
     ├── SYN激增 → 协议型(SYN Flood)
     ├── HTTP QPS激增 → 应用层(HTTP Flood/CC)
     └── 混合型 → 多种攻击同时进行
```

**快速诊断命令：**

```bash
# 查看当前连接数统计
ss -s

# 按状态统计TCP连接
ss -ant | awk '{print $1}' | sort | uniq -c | sort -rn

# 检查SYN_RECV数量（判断SYN Flood）
ss -ant | grep SYN-RECV | wc -l

# 查看连接数最多的IP
ss -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -20

# 实时流量监控
iftop -nNP -i eth0
# 或
nload -u M
```

### 4.2 应急处置步骤

```
DDoS应急处置标准流程（PDCERF模型）:

  ┌──────────────────────────────────────────────────────────┐
  │ 1. 准备(Preparation)    - 日常建立监控、预案、联系通道   │
  │ 2. 发现(Identification) - 检测到异常，确认DDoS攻击      │
  │ 3. 抑制(Containment)    - 紧急措施阻止攻击扩散         │
  │ 4. 根除(Eradication)    - 清除攻击源/引入清洗          │
  │ 5. 恢复(Recovery)       - 确认攻击停止，恢复服务       │
  │ 6. 总结(Follow-up)      - 事后分析，改进防护           │
  └──────────────────────────────────────────────────────────┘

抑制阶段紧急措施:
  1. 上联黑洞路由（丢弃所有流量到目标IP）
  2. 启动云清洗服务（Cloudflare/AWS Shield）
  3. 启用本地iptables限速规则
  4. 切换DNS到备用高防IP
  5. 增加服务器资源（弹性扩容）
```

### 4.3 事后分析与改进

```
事后分析检查清单:

  [ ] 攻击时间线重建（开始/峰值/结束时间）
  [ ] 攻击类型与流量规模记录
  [ ] 攻击源IP地域分布分析
  [ ] 受影响服务及持续时间
  [ ] 现有防护措施有效性评估
  [ ] 告警是否及时触发
  [ ] 应急响应流程是否顺畅
  [ ] 需要改进的环节

改进措施:
  - 调整检测阈值（减少漏报）
  - 优化清洗规则（提高精准度）
  - 预签约云防护服务（缩短响应时间）
  - 定期演练（验证预案有效性）
```

---

## 五、Python DDoS检测脚本示例

### 5.1 流量异常检测脚本

```python
"""
DDoS流量异常检测脚本 - 模拟教育版
功能：基于流量基线模型，检测带宽和包速率异常突增。
注意：使用模拟流量数据，不执行真实网络抓包。
"""

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple


@dataclass
class TrafficSample:
    """流量采样数据点"""
    timestamp: str
    bandwidth_mbps: float    # 带宽 Mbps
    packets_per_sec: int     # 每秒包数
    syn_packets: int         # SYN包数
    udp_packets: int         # UDP包数


class TrafficBaseline:
    """流量基线模型"""

    def __init__(self, history_data: List[TrafficSample]):
        self.bw_mean = statistics.mean([s.bandwidth_mbps for s in history_data])
        self.bw_stdev = statistics.stdev([s.bandwidth_mbps for s in history_data])
        self.pps_mean = statistics.mean([s.packets_per_sec for s in history_data])
        self.pps_stdev = statistics.stdev([s.packets_per_sec for s in history_data])

    def is_anomalous(self, sample: TrafficSample,
                     threshold_sigma: float = 3.0) -> Tuple[bool, str]:
        """判断单个采样点是否异常"""
        reasons = []

        # 带宽异常检测（超过 mean + 3*stdev）
        if self.bw_stdev > 0:
            bw_zscore = (sample.bandwidth_mbps - self.bw_mean) / self.bw_stdev
            if bw_zscore > threshold_sigma:
                reasons.append(
                    f"带宽异常: {sample.bandwidth_mbps:.1f}Mbps "
                    f"(基线均值={self.bw_mean:.1f}Mbps, "
                    f"偏离={bw_zscore:.1f}σ)"
                )

        # 包速率异常检测
        if self.pps_stdev > 0:
            pps_zscore = (sample.packets_per_sec - self.pps_mean) / self.pps_stdev
            if pps_zscore > threshold_sigma:
                reasons.append(
                    f"包速率异常: {sample.packets_per_sec}pps "
                    f"(基线均值={self.pps_mean:.0f}pps, "
                    f"偏离={pps_zscore:.1f}σ)"
                )

        # SYN包占比异常检测
        if sample.packets_per_sec > 0:
            syn_ratio = sample.syn_packets / sample.packets_per_sec
            if syn_ratio > 0.3:  # SYN占比超过30%
                reasons.append(
                    f"SYN占比异常: {syn_ratio*100:.1f}% "
                    f"(SYN={sample.syn_packets}/{sample.packets_per_sec})"
                )

        # UDP包占比异常
        if sample.packets_per_sec > 0:
            udp_ratio = sample.udp_packets / sample.packets_per_sec
            if udp_ratio > 0.5:  # UDP占比超过50%
                reasons.append(
                    f"UDP占比异常: {udp_ratio*100:.1f}% "
                    f"(UDP={sample.udp_packets}/{sample.packets_per_sec})"
                )

        if reasons:
            return True, "; ".join(reasons)
        return False, "正常"


def main():
    """主函数 - 模拟DDoS检测"""
    # === 构建历史正常流量数据（7天基线）===
    import random
    random.seed(42)
    history = []
    for i in range(168):  # 7天 * 24小时
        bw = random.gauss(500, 50)   # 正常带宽 500±50 Mbps
        pps = random.gauss(5000, 800)  # 正常包速率 5000±800 pps
        syn = random.gauss(100, 30)  # 正常SYN约100/s
        udp = random.gauss(500, 100)  # 正常UDP约500/s
        history.append(TrafficSample(
            timestamp=f"2026-09-{5+i//24:02d} {i%24:02d}:00",
            bandwidth_mbps=max(0, bw),
            packets_per_sec=max(0, int(pps)),
            syn_packets=max(0, int(syn)),
            udp_packets=max(0, int(udp)),
        ))

    baseline = TrafficBaseline(history)
    print("=" * 70)
    print("流量基线模型:")
    print(f"  带宽:   {baseline.bw_mean:.1f} ± {baseline.bw_stdev:.1f} Mbps")
    print(f"  包速率: {baseline.pps_mean:.0f} ± {baseline.pps_stdev:.0f} pps")
    print("=" * 70)

    # === 场景1: 正常流量 ===
    print("\n--- 场景1: 正常流量 ---")
    normal_sample = TrafficSample(
        timestamp="2026-09-12 10:00",
        bandwidth_mbps=520, packets_per_sec=5100,
        syn_packets=105, udp_packets=480
    )
    is_anomaly, reason = baseline.is_anomalous(normal_sample)
    print(f"  时间: {normal_sample.timestamp}")
    print(f"  带宽: {normal_sample.bandwidth_mbps}Mbps, PPS: {normal_sample.packets_per_sec}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'} - {reason}")

    # === 场景2: SYN Flood攻击 ===
    print("\n--- 场景2: SYN Flood攻击 ---")
    syn_flood_sample = TrafficSample(
        timestamp="2026-09-12 14:00",
        bandwidth_mbps=3000,   # 带宽突增6倍
        packets_per_sec=50000, # 包速率突增10倍
        syn_packets=35000,     # SYN占比70%
        udp_packets=200
    )
    is_anomaly, reason = baseline.is_anomalous(syn_flood_sample)
    print(f"  时间: {syn_flood_sample.timestamp}")
    print(f"  带宽: {syn_flood_sample.bandwidth_mbps}Mbps, PPS: {syn_flood_sample.packets_per_sec}")
    print(f"  SYN: {syn_flood_sample.syn_packets}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'}")
    if is_anomaly:
        print(f"  告警: {reason}")

    # === 场景3: UDP Flood/放大攻击 ===
    print("\n--- 场景3: UDP Flood/Amplification攻击 ---")
    udp_flood_sample = TrafficSample(
        timestamp="2026-09-12 16:00",
        bandwidth_mbps=8000,   # 带宽突增16倍
        packets_per_sec=30000,
        syn_packets=50,
        udp_packets=25000     # UDP占比83%
    )
    is_anomaly, reason = baseline.is_anomalous(udp_flood_sample)
    print(f"  时间: {udp_flood_sample.timestamp}")
    print(f"  带宽: {udp_flood_sample.bandwidth_mbps}Mbps, PPS: {udp_flood_sample.packets_per_sec}")
    print(f"  UDP: {udp_flood_sample.udp_packets}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'}")
    if is_anomaly:
        print(f"  告警: {reason}")

    # === 场景4: HTTP Flood/CC攻击 ===
    print("\n--- 场景4: HTTP Flood/CC攻击 ---")
    cc_sample = TrafficSample(
        timestamp="2026-09-12 18:00",
        bandwidth_mbps=600,    # 带宽仅略增
        packets_per_sec=15000, # 但包速率突增3倍
        syn_packets=200,      # SYN不多
        udp_packets=300
    )
    is_anomaly, reason = baseline.is_anomalous(cc_sample)
    print(f"  时间: {cc_sample.timestamp}")
    print(f"  带宽: {cc_sample.bandwidth_mbps}Mbps, PPS: {cc_sample.packets_per_sec}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'}")
    if is_anomaly:
        print(f"  告警: {reason}")
    else:
        print("  提示: CC攻击可能带宽增幅小，需结合应用层指标(L7 QPS)检测")


if __name__ == "__main__":
    main()
```

### 5.2 SYN Flood检测脚本

```python
"""
SYN Flood检测脚本 - 模拟教育版
功能：监控TCP半连接(SYN_RECV)数量与比例，检测SYN Flood攻击。
注意：使用模拟连接数据，不执行真实系统命令。
"""

from dataclasses import dataclass
from collections import Counter
from typing import List, Dict


@dataclass
class TCPConnection:
    """TCP连接状态"""
    local_ip: str
    local_port: int
    remote_ip: str
    remote_port: int
    state: str  # ESTABLISHED, SYN-RECV, TIME-WAIT, etc.


class SYNFloodDetector:
    """SYN Flood检测器"""

    def __init__(self, syn_threshold: int = 1000,
                 syn_ratio_threshold: float = 0.3,
                 per_ip_threshold: int = 100):
        self.syn_threshold = syn_threshold
        self.syn_ratio_threshold = syn_ratio_threshold
        self.per_ip_threshold = per_ip_threshold

    def analyze(self, connections: List[TCPConnection]) -> Dict:
        """分析连接列表，检测SYN Flood"""
        result = {
            "total_connections": len(connections),
            "syn_recv_count": 0,
            "established_count": 0,
            "syn_ratio": 0.0,
            "top_syn_sources": [],
            "is_syn_flood": False,
            "alerts": []
        }

        # 统计各状态连接数
        state_counts = Counter()
        syn_sources = Counter()

        for conn in connections:
            state_counts[conn.state] += 1
            if conn.state == "SYN-RECV":
                result["syn_recv_count"] += 1
                syn_sources[conn.remote_ip] += 1
            elif conn.state == "ESTABLISHED":
                result["established_count"] += 1

        total = len(connections)
        result["syn_ratio"] = (
            result["syn_recv_count"] / total if total > 0 else 0
        )
        result["top_syn_sources"] = syn_sources.most_common(10)

        # 检测条件1: SYN-RECV总数超过阈值
        if result["syn_recv_count"] > self.syn_threshold:
            result["is_syn_flood"] = True
            result["alerts"].append(
                f"SYN-RECV总数异常: {result['syn_recv_count']} "
                f"(阈值={self.syn_threshold})"
            )

        # 检测条件2: SYN占比超过阈值
        if result["syn_ratio"] > self.syn_ratio_threshold:
            result["is_syn_flood"] = True
            result["alerts"].append(
                f"SYN占比异常: {result['syn_ratio']*100:.1f}% "
                f"(阈值={self.syn_ratio_threshold*100:.0f}%)"
            )

        # 检测条件3: 单IP SYN-RECV连接数过多
        for ip, count in result["top_syn_sources"]:
            if count > self.per_ip_threshold:
                result["is_syn_flood"] = True
                result["alerts"].append(
                    f"单IP异常: {ip} 有 {count} 个SYN-RECV连接 "
                    f"(阈值={self.per_ip_threshold})"
                )

        return result


def generate_normal_connections(n: int = 500) -> List[TCPConnection]:
    """生成模拟正常连接"""
    import random
    random.seed(100)
    conns = []
    states_weighted = (
        ["ESTABLISHED"] * 60 +
        ["TIME-WAIT"] * 25 +
        ["SYN-RECV"] * 5 +
        ["CLOSE-WAIT"] * 5 +
        ["FIN-WAIT"] * 5
    )
    for _ in range(n):
        ip = f"192.168.1.{random.randint(1, 254)}"
        conns.append(TCPConnection(
            local_ip="10.0.0.1", local_port=443,
            remote_ip=ip, remote_port=random.randint(1024, 65535),
            state=random.choice(states_weighted)
        ))
    return conns


def generate_syn_flood_connections(n: int = 2000) -> List[TCPConnection]:
    """生成模拟SYN Flood连接"""
    import random
    random.seed(200)
    conns = []
    # 80%为SYN-RECV（伪造IP），20%为正常连接
    for i in range(n):
        if i < n * 0.8:
            # 伪造源IP（随机生成）
            ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}."
            ip += f"{random.randint(0, 255)}.{random.randint(1, 254)}"
            conns.append(TCPConnection(
                local_ip="10.0.0.1", local_port=443,
                remote_ip=ip, remote_port=random.randint(1024, 65535),
                state="SYN-RECV"
            ))
        else:
            ip = f"192.168.1.{random.randint(1, 254)}"
            conns.append(TCPConnection(
                local_ip="10.0.0.1", local_port=443,
                remote_ip=ip, remote_port=random.randint(1024, 65535),
                state="ESTABLISHED"
            ))
    return conns


def main():
    """主函数 - 模拟SYN Flood检测"""
    detector = SYNFloodDetector(
        syn_threshold=1000,
        syn_ratio_threshold=0.3,
        per_ip_threshold=100
    )

    # === 场景1: 正常连接 ===
    print("=" * 70)
    print("场景1: 正常TCP连接状态")
    print("=" * 70)
    normal_conns = generate_normal_connections(500)
    result = detector.analyze(normal_conns)
    print(f"  总连接数: {result['total_connections']}")
    print(f"  SYN-RECV: {result['syn_recv_count']}")
    print(f"  ESTABLISHED: {result['established_count']}")
    print(f"  SYN占比: {result['syn_ratio']*100:.1f}%")
    print(f"  结果: {'检测到SYN Flood!' if result['is_syn_flood'] else '正常，未检测到SYN Flood。'}")

    # === 场景2: SYN Flood攻击 ===
    print("\n" + "=" * 70)
    print("场景2: SYN Flood攻击")
    print("=" * 70)
    flood_conns = generate_syn_flood_connections(2000)
    result = detector.analyze(flood_conns)
    print(f"  总连接数: {result['total_connections']}")
    print(f"  SYN-RECV: {result['syn_recv_count']}")
    print(f"  ESTABLISHED: {result['established_count']}")
    print(f"  SYN占比: {result['syn_ratio']*100:.1f}%")
    print(f"  结果: {'检测到SYN Flood!' if result['is_syn_flood'] else '正常'}")
    if result["is_syn_flood"]:
        print(f"\n  告警列表:")
        for alert in result["alerts"]:
            print(f"    [ALERT] {alert}")
        print(f"\n  SYN-RECV最多的源IP (前5):")
        for ip, count in result["top_syn_sources"][:5]:
            print(f"    {ip}: {count} 个半连接")


if __name__ == "__main__":
    main()
```

---

## 总结

| 攻击类型 | OSI层次 | 核心特征 | 关键防御 |
|---------|---------|---------|---------|
| SYN Flood | L4 | 半连接队列耗尽 | SYN Cookies、SYN Proxy |
| UDP Flood | L3/L4 | 带宽耗尽 | 速率限制、ICMP限速 |
| HTTP Flood/CC | L7 | 应用资源耗尽 | WAF、速率限制、CAPTCHA |
| DNS Amplification | L3/L4 | 反射放大 | 关闭递归、BCP38 |
| NTP Amplification | L3/L4 | 超大放大倍数 | 升级NTP、禁用monlist |
| 慢速攻击 | L7 | 连接池占用 | 超时设置、连接数限制 |

**DDoS防护层次体系：**

```
  ┌─────────────────────────────────────────────────────┐
  │  第1层: 云防护 (Cloudflare/AWS Shield)              │
  │  → 大规模流量清洗、Anycast分散                       │
  ├─────────────────────────────────────────────────────┤
  │  第2层: 网络层防护 (清洗中心/黑洞路由)              │
  │  → BGP牵引、流量清洗、RTBH                          │
  ├─────────────────────────────────────────────────────┤
  │  第3层: 主机层防护 (iptables/内核参数)              │
  │  → 速率限制、连接数限制、SYN Cookies               │
  ├─────────────────────────────────────────────────────┤
  │  第4层: 应用层防护 (WAF/Nginx限流)                  │
  │  → HTTP速率限制、CAPTCHA、行为分析                  │
  └─────────────────────────────────────────────────────┘
```
