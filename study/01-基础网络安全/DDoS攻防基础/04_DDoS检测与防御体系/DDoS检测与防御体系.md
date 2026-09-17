# DDoS检测与防御体系

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

---

## 📋 内容审核与补充建议

> 针对「DDoS检测与防御体系」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
