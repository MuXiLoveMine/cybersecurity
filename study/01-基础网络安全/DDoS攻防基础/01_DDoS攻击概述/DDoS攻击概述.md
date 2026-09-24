# DDoS攻击概述

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

---

