# 防火墙与IDS-IPS入门

> 本文档用于网络安全教学与防御技术研究。所有配置示例和脚本基于模拟环境，确保安全合规。

---

## 目录

- [一、防火墙技术演进](#一防火墙技术演进)
- [二、防火墙策略设计](#二防火墙策略设计)
- [三、IDS-IPS基础](#三ids-ips基础)
- [四、SIEM与安全运营](#四siem与安全运营)
- [五、Python安全监控脚本示例](#五python安全监控脚本示例)

---

## 一、防火墙技术演进

### 1.1 包过滤防火墙（第一代）

包过滤防火墙工作在OSI模型第3-4层（网络层/传输层），根据预定义规则对每个数据包独立进行允许或拒绝决策。

**过滤依据：**
- 源IP地址 / 目标IP地址
- 协议类型（TCP / UDP / ICMP）
- 源端口 / 目标端口
- TCP标志位（SYN / ACK等）

```
数据包到达防火墙:

  ┌──────────────────────────────────┐
  │ 入站数据包                        │
  │ src=10.1.1.5 dst=192.168.1.100   │
  │ proto=TCP dport=443             │
  └──────────────────────────────────┘
                 │
                 ↓
  ┌──────────────────────────────────┐
  │ 规则匹配（按顺序逐条匹配）         │
  │                                  │
  │ 规则1: 允许 TCP→443  → MATCH   │
  │ 规则2: 拒绝 TCP→22   → (跳过)   │
  │ 规则3: 默认拒绝     → (兜底)   │
  └──────────────────────────────────┘
                 │
                 ↓
  ┌──────────────────────────────────┐
  │ 决策: ALLOW (匹配规则1)          │
  └──────────────────────────────────┘
```

**优点：** 速度快、开销小
**缺点：** 无法检查应用层数据、无法跟踪连接状态、易被IP伪造欺骗

### 1.2 状态检测防火墙（第二代）

状态检测防火墙（Stateful Inspection Firewall）在包过滤基础上维护连接状态表（Session Table），能够跟踪TCP连接状态，基于连接上下文做决策。

```
状态检测工作原理:

  ┌─────────────────────────────────────────┐
  │           连接状态表                     │
  │  src_ip | dst_ip | proto | sport:dport │ state │
  │ 10.1.1.5 | 192.168.1.100 | TCP | 54321:443 │ ESTABLISHED │
  │ 10.1.1.6 | 192.168.1.100 | TCP | 12345:80  │ SYN_SENT    │
  └─────────────────────────────────────────┘

  入站包处理逻辑:
  1. 查看连接状态表
  2. 若属于已建立的连接 → 允许（无需逐条匹配规则）
  3. 若是新连接 → 匹配规则表
  4. 若不属于任何已知连接且非新连接请求 → 拒绝
```

**状态转换示意（TCP）：**
```
  NEW → SYN_SENT → SYN_RECV → ESTABLISHED → FIN_WAIT → CLOSED
   │                                          │
   └── 未授权的新连接直接拒绝                │
                                              ↓
                        已建立连接的后续包直接放行（查表即可）
```

**优点：** 比包过滤更安全、效率更高（已建立连接无需逐条匹配）
**缺点：** 仍无法深度检测应用层内容

### 1.3 下一代防火墙（NGFW）

下一代防火墙（Next-Generation Firewall）集成了多种安全能力，具备应用层识别和深度包检测能力。

```
NGFW架构:

  ┌───────────────────────────────────────────┐
  │              下一代防火墙 (NGFW)            │
  ├───────────────────────────────────────────┤
  │                                           │
  │  ┌─────────┐ ┌──────────┐ ┌───────────┐  │
  │  │ 状态检测 │ │ 应用识别  │ │ 入侵防御   │  │
  │  │ (L3/L4) │ │ (L7 DPI) │ │ (IPS)     │  │
  │  └─────────┘ └──────────┘ └───────────┘  │
  │                                           │
  │  ┌─────────┐ ┌──────────┐ ┌───────────┐  │
  │  │ URL过滤 │ │ 反病毒   │ │ 威胁情报   │  │
  │  └─────────┘ └──────────┘ └───────────┘  │
  │                                           │
  │  ┌─────────────────────────────────────┐  │
  │  │       统一管理面板 + 日志审计        │  │
  │  └─────────────────────────────────────┘  │
  └───────────────────────────────────────────┘
```

**NGFW核心能力：**
- **应用识别**：识别具体应用（如区分微信流量和一般HTTP流量）
- **用户身份感知**：基于用户而非IP制定策略
- **深度包检测（DPI）**：检查应用层载荷内容
- **集成IPS**：实时入侵防御
- **威胁情报联动**：与云端威胁情报库同步

### 1.4 Web应用防火墙（WAF）

WAF专用于保护Web应用，工作在OSI第7层（应用层），针对HTTP/HTTPS流量进行深度检测和过滤。

```
WAF部署位置:

  用户请求 → [CDN] → [WAF] → [负载均衡] → [Web服务器集群]
                        │
                        ├── SQL注入检测
                        ├── XSS跨站脚本检测
                        ├── CC攻击防护
                        ├── 虚拟补丁（已知漏洞临时防护）
                        ├── 敏感数据脱敏
                        └── API安全网关

WAF vs 网络防火墙:

  网络防火墙: 关注IP/端口/协议 → "谁能访问"
  WAF:        关注HTTP内容/行为 → "访问了什么、是否有恶意"
```

---

## 二、防火墙策略设计

### 2.1 默认拒绝原则

**默认拒绝（Default Deny）** 是防火墙策略设计的黄金准则：除非明确允许，否则拒绝所有流量。

```
默认拒绝 vs 默认允许:

  默认允许（危险）:
    规则1: 拒绝 已知恶意IP
    规则2: 拒绝 已知攻击端口
    默认:   允许其余所有  ← 未知威胁可绕过

  默认拒绝（安全）:
    规则1: 允许 业务必需的80/443
    规则2: 允许 管理网段→22
    默认:   拒绝其余所有  ← 仅白名单流量通过
```

### 2.2 区域划分与访问控制

```
企业网络区域划分示例:

  ┌─────────────────────────────────────────────────┐
  │                    互联网                        │
  │                        │                        │
  │              ┌───────┴───────┐                  │
  │              │   外部防火墙   │                  │
  │              └───────┬───────┘                  │
  │                      │                          │
  │  ┌───────────────────┼───────────────────┐      │
  │  │              DMZ区域                  │      │
  │  │  ┌──────┐ ┌──────┐ ┌──────┐          │      │
  │  │  │Web服务器│ │DNS服务器│ │邮件服务器│    │      │
  │  │  └──────┘ └──────┘ └──────┘          │      │
  │  └───────────────────┬───────────────────┘      │
  │              ┌───────┴───────┐                  │
  │              │   内部防火墙   │                  │
  │              └───────┬───────┘                  │
  │                      │                          │
  │  ┌───────────────────┼───────────────────┐      │
  │  │             内网区域                   │      │
  │  │  ┌──────────┐  ┌──────────┐           │      │
  │  │  │办公网段   │  │核心数据库 │           │      │
  │  │  │10.1.0.0/16│  │10.2.0.0/24│          │      │
  │  │  └──────────┘  └──────────┘           │      │
  │  └─────────────────────────────────────────┘      │
  └─────────────────────────────────────────────────┘

访问控制矩阵（区域间策略）:
  源\目标    互联网    DMZ       内网办公    核心数据库
  互联网     -        仅80/443   拒绝        拒绝
  DMZ       允许出站   -        拒绝        仅特定端口
  内网办公   允许出站  允许管理   -          仅应用端口
  核心数据库  拒绝     拒绝       拒绝        -
```

### 2.3 规则优化与审计

**防火墙规则优化原则：**

1. **最小权限**：每条规则只开放必需端口
2. **最具体匹配优先**：避免使用`any`，尽量指定具体IP/端口
3. **规则排序**：高频匹配规则靠前，减少性能开销
4. **定期审计**：清理过期/冗余规则
5. **规则命名与注释**：每条规则标注用途和责任人

```
规则审计检查清单:
  [ ] 是否存在 "any any allow" 规则？
  [ ] 是否存在重复/冲突规则？
  [ ] 是否存在过期临时规则（如测试遗留）？
  [ ] 是否有规则无注释说明？
  [ ] 是否存在未使用的IP对象/地址组？
  [ ] 是否有规则允许直接访问核心数据库？
```

### 2.4 iptables/nftables实战配置

**iptables综合防护配置示例：**

```bash
#!/bin/bash
# === iptables防火墙基础配置 ===

# 清空现有规则
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X  # 删除自定义链

# 设置默认策略（默认拒绝）
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# === 基本安全规则 ===

# 1. 允许回环接口
iptables -A INPUT  -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 2. 允许已建立连接的流量（状态检测）
iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. 防止IP伪造（拒绝内部源IP从外网进入）
iptables -A INPUT -i eth0 -s 10.0.0.0/8 -j DROP
iptables -A INPUT -i eth0 -s 172.16.0.0/12 -j DROP
iptables -A INPUT -i eth0 -s 192.168.0.0/16 -j DROP

# 4. SYN Flood防护
iptables -A INPUT -p tcp --syn -m limit --limit 50/s --limit-burst 100 -j ACCEPT

# 5. 允许SSH（仅管理网段）
iptables -A INPUT -p tcp -s 10.1.0.0/16 --dport 22 -j ACCEPT

# 6. 允许HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 7. 允许ICMP（限制速率，防止Ping Flood）
iptables -A INPUT -p icmp -m limit --limit 10/s -j ACCEPT

# 8. 记录被拒绝的流量（便于审计）
iptables -A INPUT -j LOG --log-prefix "FW-DROP-INPUT: " --log-level 6
iptables -A INPUT -j DROP

# 9. 限制出站（防止反弹Shell）
iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT  # DNS
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT  # SSH
# 最后：记录并拒绝其余出站流量
iptables -A OUTPUT -j LOG --log-prefix "FW-DROP-OUTPUT: " --log-level 6
iptables -A OUTPUT -j DROP

# 保存规则（重启后生效）
# iptables-save > /etc/iptables/rules.v4
```

**nftables配置示例（现代替代方案）：**

```bash
# /etc/nftables.conf

#!/usr/sbin/nft -f

flush ruleset

table inet firewall {
    set blocked_ips {
        type ipv4_addr
        flags interval
        elements = { 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 }
    }

    chain input {
        type filter hook input priority 0; policy drop;

        # 允许回环
        iif "lo" accept

        # 允许已建立连接
        ct state established,related accept

        # 拒绝IP伪造
        iif "eth0" ip saddr @blocked_ips drop

        # SYN Flood防护
        tcp flags syn limit rate 50/second burst 100 packets accept

        # 允许SSH（管理网段）
        ip saddr 10.1.0.0/16 tcp dport 22 accept

        # 允许HTTP/HTTPS
        tcp dport { 80, 443 } accept

        # 允许ICMP（限速）
        icmp type echo-request limit rate 10/second accept

        # 记录并拒绝其余流量
        log prefix "FW-DROP: " counter drop
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy drop;

        oif "lo" accept
        ct state established,related accept
        tcp dport { 80, 443, 22 } accept
        udp dport 53 accept
        log prefix "FW-OUT-DROP: " counter drop
    }
}
```

---

## 三、IDS-IPS基础

### 3.1 IDS与IPS区别

```
IDS (入侵检测系统) - 被动检测:

  流量 ──→ [IDS传感器] ──→ 目标
              │
              └──→ 检测到威胁 → 告警（不阻断）
              └──→ 事后分析

  优点: 不影响网络性能、误报不会中断业务
  缺点: 只能告警，无法实时阻断攻击


IPS (入侵防御系统) - 主动阻断:

  流量 ──→ [IPS传感器] ──┬──→ 目标（正常流量）
              │           │
              │    └──→ 丢弃（恶意流量）
              │
              └──→ 检测到威胁 → 实时阻断 + 告警

  优点: 实时阻断攻击、自动化防护
  缺点: 误报会中断业务、增加延迟

对比:

  特征        IDS          IPS
  部署方式    旁路部署     串联部署
  响应方式    仅告警       告警+阻断
  对性能影响  无           有（增加延迟）
  误报后果    可忽略       业务中断
  适用场景    审计/监控     实时防护
```

### 3.2 Snort/Suricata规则编写

**Snort/Suricata规则语法结构：**

```
规则格式:
  [动作] [协议] [源IP] [源端口] [方向] [目标IP] [目标端口] ([规则选项])

  动作: alert(告警) | drop(丢弃) | reject(拒绝) | pass(放行)
  方向: → (单向) | <> (双向)
  规则选项: msg(消息), content(内容匹配), pcre(正则),
            sid(规则ID), rev(版本), classtype(分类), priority(优先级)
```

**常见攻击检测规则示例：**

```
# 1. 检测SQL注入攻击
alert tcp any any -> $HOME_NET 80 ( \
    msg:"SQL注入攻击检测 - UNION SELECT"; \
    content:"UNION"; nocase; \
    content:"SELECT"; distance:0; within:50; nocase; \
    sid:1000001; rev:1; \
    classtype:web-application-attack; \
    priority:high; \
)

# 2. 检测跨站脚本(XSS)攻击
alert tcp any any -> $HOME_NET 80 ( \
    msg:"XSS攻击检测 - script标签"; \
    content:"<script"; nocase; \
    content:"</script>"; distance:0; within:200; nocase; \
    sid:1000002; rev:1; \
    classtype:web-application-attack; \
    priority:high; \
)

# 3. 检测SSH暴力破解
alert tcp $EXTERNAL_NET any -> $HOME_NET 22 ( \
    msg:"SSH暴力破解 - 频率检测"; \
    flow:to_server,established; \
    detection_filter:track by_src, count 5, seconds 60; \
    sid:1000003; rev:1; \
    classtype:attempt-admin; \
    priority:high; \
)

# 4. 检测已知恶意文件哈希
alert tcp any any -> $HOME_NET any ( \
    msg:"已知恶意文件传输"; \
    filesha:256:5d41402abc4b2a76b9719d911017c592; \
    sid:1000004; rev:1; \
    classtyle:trojan-activity; \
    priority:high; \
)

# 5. 检测反弹Shell连接（iptables+Suricata联动）
alert tcp $HOME_NET any -> $EXTERNAL_NET 4444 ( \
    msg:"可疑反弹Shell - Meterpreter默认端口"; \
    flow:to_server,established; \
    sid:1000005; rev:1; \
    classtype:trojan-activity; \
    priority:high; \
)
```

**Suricata配置文件结构：**

```yaml
# /etc/suricata/suricata.yaml (关键配置段)

# 网络配置
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
    EXTERNAL_NET: "!$HOME_NET"
  port-groups:
    HTTP_PORTS: "80"
    SSH_PORTS: "22"

# 规则路径
default-rule-path: /etc/suricata/rules
rule-files:
  - local.rules          # 自定义规则
  - emerging-all.rules   # Emerging Threats规则集

# 输出配置
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: eve.json
      types:
        - alert:           # 告警输出
            payload: yes   # 包含载荷
            packet: yes
        - http:             # HTTP日志
        - dns:             # DNS日志
        - tls:             # TLS日志
```

### 3.3 告警分析与误报处理

```
告警分析流程:

  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │ 1. 告警分类  │───→│ 2. 上下文关联│───→│ 3. 处置决策  │
  │ 确定攻击类型 │    │ 源/目标/时间 │    │ 告警/阻断/   │
  │ 优先级/置信度│    │ 历史行为关联  │    │ 白名单/忽略  │
  └──────────────┘    └──────────────┘    └──────────────┘

误报处理方法:
  1. 确认告警是否为误报（分析完整载荷）
  2. 如为误报 → 添加排除规则或调整阈值
  3. 记录误报原因，优化规则
  4. 定期回顾白名单，防止过度放宽

误报常见原因:
  - 规则过于宽泛（如仅匹配content无上下文限制）
  - 正常业务行为被误判（如安全扫描器流量）
  - 签名库过时（合法应用更新后特征变化）
  - 网络架构变化（新部署服务未纳入基线）
```

### 3.4 入侵检测系统部署模式

```
IDS/IPS部署模式对比:

  旁路部署(IDS):
  ┌──────┐         ┌───────┐
  │ 交换机 │──SPAN──→│  IDS  │  (仅镜像流量，被动检测)
  └──────┘         └───────┘
  优点: 零延迟、不影响业务
  缺点: 只能告警，无法阻断

  串联部署(IPS):
  ┌──────┐    ┌───────┐    ┌──────┐
  │ 路由器 │───→│  IPS  │───→│ 交换机 │  (流量必经IPS)
  └──────┘    └───────┘    └──────┘
  优点: 实时阻断、主动防护
  缺点: 增加延迟、误报影响业务

  混合部署:
  ┌──────┐    ┌───────┐    ┌──────┐
  │ 路由器 │───→│  IPS  │───→│ 交换机 │  (核心链路IPS)
  └──────┘    └───────┘    └──┬───┘
                               │ SPAN
                          ┌────┴───┐
                          │  IDS   │  (全量旁路检测)
                          └────────┘
```

---

## 四、SIEM与安全运营

### 4.1 日志收集与关联分析

**SIEM（Security Information and Event Management）** 是安全信息和事件管理平台，核心能力是集中收集多源日志并进行关联分析。

```
SIEM架构:

  ┌─────────────────────────────────────────────────┐
  │                   SIEM平台                      │
  │                                                  │
  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
  │  │ 日志采集   │  │ 关联分析   │  │ 告警响应   │  │
  │  │ (Collector)│  │ (Correlation│ │ (Alerting) │  │
  │  │           │  │  Engine)   │  │           │  │
  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  │
  │        │              │              │          │
  │  ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐  │
  │  │ 归一化     │  │ 规则引擎   │  │ 工单/通知  │  │
  │  │ (Parse)   │  │ (Rules)   │  │           │  │
  │  └───────────┘  └───────────┘  └───────────┘  │
  └─────────────────────────────────────────────────┘
          ↑               ↑               ↑
  ┌───────┴───┐   ┌───────┴───┐   ┌───────┴───┐
  │防火墙日志  │   │IDS/IPS日志 │   │Web服务器日志│
  │(syslog)  │   │(eve.json) │   │(access.log)│
  └───────────┘   └───────────┘   └───────────┘
  ┌───────┴───┐   ┌───────┴───┐
  │系统日志    │   │应用日志    │
  │(/var/log) │   │(业务系统)  │
  └───────────┘   └───────────┘
```

**关联分析规则示例：**

```
规则1: 暴力破解 + 登录成功 = 可疑入侵
  条件:
    (5分钟内同一源IP SSH认证失败 ≥ 10次)
    AND (同一源IP SSH认证成功 ≥ 1次)
  动作: 高优先级告警 → 自动封禁IP → 通知安全团队

规则2: IDS告警 + 防火墙拒绝 = 可能被阻断的攻击
  条件:
    (IDS检测到攻击告警)
    AND (防火墙日志显示同一源IP被DROP)
  动作: 中优先级告警 → 记录但不重复通知

规则3: 异常DNS查询 + 恶意域名命中 = C2通信
  条件:
    (某主机DNS查询量异常增加)
    AND (查询域名命中威胁情报黑名单)
  动作: 高优先级告警 → 隔离主机 → 安全排查
```

### 4.2 ELK Stack安全运营实践

```
ELK Stack (Elasticsearch + Logstash + Kibana):

  多源日志
    │
    ↓
  ┌──────────────────┐
  │ Logstash/Fluentd  │  ← 日志收集与解析
  │ 解析/过滤/转换    │
  └────────┬─────────┘
           │
  ┌────────┴─────────┐
  │ Elasticsearch     │  ← 日志存储与检索
  │ 索引/存储/搜索    │
  └────────┬─────────┘
           │
  ┌────────┴─────────┐
  │ Kibana            │  ← 可视化与告警
  │ 仪表盘/图表/告警  │
  └──────────────────┘
```

**Logstash安全日志解析配置：**

```
# /etc/logstash/conf.d/security.conf

input {
  # 防火墙syslog输入
  udp {
    port => 514
    type => "firewall"
  }
  # Suricata eve.json
  file {
    path => "/var/log/suricata/eve.json"
    type => "ids"
    codec => json
  }
  # Web访问日志
  file {
    path => "/var/log/nginx/access.log"
    type => "web"
  }
}

filter {
  # 防火墙日志解析
  if [type] == "firewall" {
    grok {
      match => { "message" => "%{FW_LOG_PATTERN}" }
    }
  }
  # IDS告警提取
  if [type] == "ids" and [event_type] == "alert" {
    mutate {
      add_field => { "alert_severity" => "%{alert_severity}" }
    }
  }
  # Web日志解析
  if [type] == "web" {
    grok {
      match => { "message" => "%{IPORHOST:client_ip} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:status} %{NUMBER:bytes}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "security-%{+YYYY.MM.dd}"
  }
}
```

**Kibana安全仪表盘示例配置：**
- 面板1: 防火墙TOP 10被拒绝源IP（柱状图）
- 面板2: IDS告警趋势（时间线）
- 面板3: HTTP 4xx/5xx错误统计（饼图）
- 面板4: 地理IP攻击来源地图
- 告警规则: IDS high severity > 0 → 触发邮件告警

### 4.3 威胁狩猎基础

```
威胁狩猎（Threat Hunting）流程:

  假设驱动型狩猎 (Hypothesis-Driven):
  ┌─────────────────────────────────────────────┐
  │ 1. 提出假设                                  │
  │    "内部可能存在通过DNS隧道外传数据的主机"    │
  │                                              │
  │ 2. 确定检测指标 (IOC)                        │
  │    - DNS查询异常频繁的主机                   │
  │    - 查询TXT记录为主                         │
  │    - 子域名长度异常                          │
  │                                              │
  │ 3. 数据检索                                  │
  │    在SIEM中搜索DNS日志，筛选匹配条件          │
  │                                              │
  │ 4. 验证与扩展                                │
  │    发现可疑主机 → 关联其他日志验证            │
  │    → 扩展搜索相关IOC                         │
  │                                              │
  │ 5. 处置与改进                                │
  │    确认威胁 → 应急响应                       │
  │    → 将检测逻辑固化为SIEM规则                │
  └─────────────────────────────────────────────┘
```

---

## 五、Python安全监控脚本示例

### 5.1 日志分析脚本

```python
"""
安全日志分析脚本 - 模拟教育版
功能：分析模拟的Web访问日志，检测以下安全威胁：
  - 暴力破解（同一IP大量401响应）
  - 目录扫描（大量404响应）
  - SQL注入特征检测
  - 路径遍历攻击检测
注意：使用模拟日志数据，不读取真实系统日志。
"""

import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    client_ip: str
    method: str
    path: str
    status: int
    bytes_sent: int


class LogAnalyzer:
    """安全日志分析器"""

    def __init__(self):
        self.entries: List[LogEntry] = []
        self.alerts: List[str] = []

    def add_entry(self, timestamp: str, client_ip: str, method: str,
                  path: str, status: int, bytes_sent: int = 0):
        """添加日志条目"""
        self.entries.append(LogEntry(
            timestamp, client_ip, method, path, status, bytes_sent
        ))

    def check_brute_force(self, threshold: int = 10,
                          window: int = 300) -> List[str]:
        """检测暴力破解（大量401/403响应）"""
        alerts = []
        # 按IP统计401/403响应
        ip_failures: Dict[str, int] = defaultdict(int)
        for entry in self.entries:
            if entry.status in (401, 403):
                ip_failures[entry.client_ip] += 1

        for ip, count in sorted(ip_failures.items(),
                                key=lambda x: x[1], reverse=True):
            if count >= threshold:
                alert = (
                    f"[BRUTE FORCE] 暴力破解检测! "
                    f"IP={ip}, "
                    f"失败请求={count}次(401/403), "
                    f"阈值={threshold}"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def check_dir_scan(self, threshold: int = 20) -> List[str]:
        """检测目录扫描（大量404响应）"""
        alerts = []
        ip_404: Dict[str, int] = defaultdict(int)
        for entry in self.entries:
            if entry.status == 404:
                ip_404[entry.client_ip] += 1

        for ip, count in sorted(ip_404.items(),
                                key=lambda x: x[1], reverse=True):
            if count >= threshold:
                alert = (
                    f"[DIR SCAN] 目录扫描检测! "
                    f"IP={ip}, "
                    f"404响应={count}次, "
                    f"阈值={threshold}"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def check_sqli(self) -> List[str]:
        """检测SQL注入特征"""
        alerts = []
        sqli_patterns = [
            r"(?i)union\s+select",
            r"(?i)'\s*or\s*'?\d+'?\s*=\s*'?\d+",
            r"(?i)select\s+.*\s+from\s+",
            r"(?i)insert\s+into\s+",
            r"(?i)drop\s+table\s+",
            r"(?i)exec(\s|\()+",
            r"(?i)xp_cmdshell",
            r"(?i)(%27|')\s*(or|and)\s*",
        ]

        for entry in self.entries:
            for pattern in sqli_patterns:
                if re.search(pattern, entry.path):
                    alert = (
                        f"[SQL INJECTION] SQL注入特征! "
                        f"IP={entry.client_ip}, "
                        f"路径={entry.path}, "
                        f"匹配模式={pattern}, "
                        f"时间={entry.timestamp}"
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
                    break  # 每条日志只告警一次
        return alerts

    def check_path_traversal(self) -> List[str]:
        """检测路径遍历攻击"""
        alerts = []
        traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
            r"/etc/passwd",
            r"/etc/shadow",
            r"c:\\windows\\system32",
        ]

        for entry in self.entries:
            for pattern in traversal_patterns:
                if re.search(pattern, entry.path, re.IGNORECASE):
                    alert = (
                        f"[PATH TRAVERSAL] 路径遍历攻击! "
                        f"IP={entry.client_ip}, "
                        f"路径={entry.path}, "
                        f"时间={entry.timestamp}"
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
                    break
        return alerts

    def print_summary(self):
        """打印分析摘要"""
        print(f"\n=== 日志分析摘要 ===")
        print(f"  总请求数: {len(self.entries)}")
        status_counts = Counter(e.status for e in self.entries)
        print(f"  状态码分布: {dict(sorted(status_counts.items()))}")
        ip_counts = Counter(e.client_ip for e in self.entries)
        print(f"  TOP 5 IP:")
        for ip, count in ip_counts.most_common(5):
            print(f"    {ip}: {count}次请求")

    def print_alerts(self):
        """打印所有安全告警"""
        print(f"\n=== 安全告警 ({len(self.alerts)}条) ===")
        if not self.alerts:
            print("  无告警，日志未发现安全威胁。")
            return
        for i, alert in enumerate(self.alerts, 1):
            print(f"  [{i}] {alert}")


def main():
    """主函数 - 模拟日志分析"""
    analyzer = LogAnalyzer()

    # === 场景1: 正常流量 ===
    print("=" * 60)
    print("场景1: 正常Web访问流量")
    print("=" * 60)
    normal_ips = [f"10.0.0.{i}" for i in range(1, 21)]
    import random
    random.seed(42)
    for i in range(100):
        ip = random.choice(normal_ips)
        paths = ["/", "/index.html", "/about", "/products",
                 "/api/v1/users", "/static/style.css"]
        analyzer.add_entry(
            timestamp=f"2026-09-12 10:{i:02d}:00",
            client_ip=ip,
            method="GET",
            path=random.choice(paths),
            status=200,
        )
    analyzer.print_summary()
    analyzer.check_brute_force()
    analyzer.check_dir_scan()
    analyzer.check_sqli()
    analyzer.check_path_traversal()
    analyzer.print_alerts()

    # === 场景2: 暴力破解 + 目录扫描 ===
    print("\n" + "=" * 60)
    print("场景2: 暴力破解 + 目录扫描")
    print("=" * 60)
    attacker_ip = "203.0.113.66"
    # 模拟暴力破解（401响应）
    for i in range(15):
        analyzer.add_entry(
            timestamp=f"2026-09-12 14:{i:02d}:00",
            client_ip=attacker_ip,
            method="POST",
            path="/login",
            status=401,
        )
    # 模拟目录扫描（404响应）
    scan_paths = ["/admin", "/phpmyadmin", "/.env", "/wp-admin",
                  "/config.php", "/backup.zip", "/.git/config"]
    for i, path in enumerate(scan_paths * 4):  # 28次404
        analyzer.add_entry(
            timestamp=f"2026-09-12 15:{i:02d}:00",
            client_ip=attacker_ip,
            method="GET",
            path=path,
            status=404,
        )
    analyzer.check_brute_force()
    analyzer.check_dir_scan()

    # === 场景3: SQL注入 + 路径遍历 ===
    print("\n" + "=" * 60)
    print("场景3: SQL注入 + 路径遍历攻击")
    print("=" * 60)
    sqli_ip = "198.51.100.77"
    analyzer.add_entry(
        "2026-09-12 16:00:00", sqli_ip, "GET",
        "/products?id=1 UNION SELECT username,password FROM users", 200
    )
    analyzer.add_entry(
        "2026-09-12 16:01:00", sqli_ip, "GET",
        "/login?user=admin' OR '1'='1", 200
    )
    analyzer.add_entry(
        "2026-09-12 16:02:00", sqli_ip, "GET",
        "/download?file=../../../etc/passwd", 200
    )
    analyzer.add_entry(
        "2026-09-12 16:03:00", sqli_ip, "GET",
        "/page?tpl=../../etc/shadow", 200
    )
    analyzer.check_sqli()
    analyzer.check_path_traversal()

    # === 最终汇总 ===
    analyzer.print_summary()
    analyzer.print_alerts()


if __name__ == "__main__":
    main()
```

### 5.2 端口监控脚本

```python
"""
端口监控脚本 - 模拟教育版
功能：监控主机开放端口变化，检测以下风险：
  - 新增异常端口（可能后门）
  - 监听端口变化
  - 非标准端口上的服务
注意：使用模拟端口数据，不执行真实系统命令。
"""

from dataclasses import dataclass
from typing import Dict, List, Set
from datetime import datetime


@dataclass
class PortInfo:
    """端口信息"""
    port: int
    protocol: str  # tcp / udp
    state: str     # LISTEN / ESTABLISHED
    process: str   # 进程名
    pid: int       # 进程ID


# 常见合法服务端口白名单
LEGITIMATE_PORTS = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
    9090: "Prometheus",
}

# 已知恶意/可疑端口
SUSPICIOUS_PORTS = {
    4444: "Metasploit Meterpreter",
    31337: "Back Orifice / Elite",
    12345: "NetBus",
    6667: "IRC Botnet (常见)",
    6660: "IRC Botnet",
    9001: "Tor / 代理",
    5900: "VNC (需确认是否授权)",
}


class PortMonitor:
    """端口监控器"""

    def __init__(self):
        self.baseline_ports: Set[int] = set()
        self.current_ports: Set[int] = set()
        self.port_details: Dict[int, PortInfo] = {}

    def set_baseline(self, ports: List[PortInfo]):
        """设置基线端口"""
        for p in ports:
            self.baseline_ports.add(p.port)
        print(f"基线端口已设置: {sorted(self.baseline_ports)}")

    def scan_current(self, ports: List[PortInfo]):
        """扫描当前端口"""
        self.current_ports = set()
        self.port_details = {}
        for p in ports:
            self.current_ports.add(p.port)
            self.port_details[p.port] = p

    def check_new_ports(self) -> List[str]:
        """检测新增端口"""
        alerts = []
        new_ports = self.current_ports - self.baseline_ports
        for port in sorted(new_ports):
            detail = self.port_details.get(port)
            proc = detail.process if detail else "unknown"
            if port in SUSPICIOUS_PORTS:
                alert = (
                    f"[HIGH] 新增可疑端口! "
                    f"端口={port}/{detail.protocol if detail else '?'}, "
                    f"进程={proc}, "
                    f"已知关联={SUSPICIOUS_PORTS[port]}"
                )
            elif port in LEGITIMATE_PORTS:
                alert = (
                    f"[INFO] 新增标准端口: "
                    f"端口={port}, "
                    f"服务={LEGITIMATE_PORTS[port]}, "
                    f"进程={proc}"
                )
            else:
                alert = (
                    f"[MEDIUM] 新增未知端口: "
                    f"端口={port}/{detail.protocol if detail else '?'}, "
                    f"进程={proc}, "
                    f"需人工确认"
                )
            alerts.append(alert)
        return alerts

    def check_closed_ports(self) -> List[str]:
        """检测关闭的端口"""
        alerts = []
        closed = self.baseline_ports - self.current_ports
        for port in sorted(closed):
            service = LEGITIMATE_PORTS.get(port, "unknown")
            alerts.append(
                f"[INFO] 端口已关闭: "
                f"端口={port}, 原服务={service}"
            )
        return alerts

    def check_suspicious(self) -> List[str]:
        """检测已知可疑端口"""
        alerts = []
        for port in self.current_ports:
            if port in SUSPICIOUS_PORTS:
                detail = self.port_details.get(port)
                alert = (
                    f"[CRITICAL] 检测到可疑端口! "
                    f"端口={port}, "
                    f"进程={detail.process if detail else '?'}, "
                    f"PID={detail.pid if detail else '?'}, "
                    f"已知关联={SUSPICIOUS_PORTS[port]}"
                )
                alerts.append(alert)
        return alerts

    def print_current(self):
        """打印当前端口状态"""
        print(f"\n=== 当前监听端口 ({len(self.current_ports)}个) ===")
        print(f"{'端口':<10} {'协议':<6} {'状态':<12} {'进程':<15} {'PID':<8} {'备注'}")
        print("-" * 75)
        for port in sorted(self.current_ports):
            d = self.port_details.get(port)
            if d:
                note = LEGITIMATE_PORTS.get(port, "")
                if port in SUSPICIOUS_PORTS:
                    note = f"⚠ {SUSPICIOUS_PORTS[port]}"
                print(f"{d.port:<10} {d.protocol:<6} {d.state:<12} "
                      f"{d.process:<15} {d.pid:<8} {note}")


def main():
    """主函数 - 模拟端口监控"""
    monitor = PortMonitor()

    # === 设置基线端口 ===
    print("=" * 60)
    print("步骤1: 建立端口基线（正常运行状态）")
    print("=" * 60)
    baseline = [
        PortInfo(22, "tcp", "LISTEN", "sshd", 1234),
        PortInfo(80, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(443, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(3306, "tcp", "LISTEN", "mysqld", 9012),
    ]
    monitor.set_baseline(baseline)

    # === 场景1: 正常（无变化） ===
    print("\n" + "=" * 60)
    print("场景1: 端口无变化（正常）")
    print("=" * 60)
    monitor.scan_current(baseline)
    monitor.print_current()
    alerts = monitor.check_new_ports() + monitor.check_suspicious()
    print(f"\n检测结果: {'发现异常!' if alerts else '正常，端口无变化。'}")

    # === 场景2: 新增可疑端口（后门） ===
    print("\n" + "=" * 60)
    print("场景2: 检测到新增可疑端口（可能后门）")
    print("=" * 60)
    current = [
        PortInfo(22, "tcp", "LISTEN", "sshd", 1234),
        PortInfo(80, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(443, "tcp", "LISTEN", "nginx", 5678),
        PortInfo(3306, "tcp", "LISTEN", "mysqld", 9012),
        # 新增可疑端口
        PortInfo(4444, "tcp", "LISTEN", "unknown", 6666),
        PortInfo(31337, "tcp", "LISTEN", "unknown", 7777),
        # 新增非标准端口
        PortInfo(9999, "tcp", "LISTEN", "python3", 8888),
    ]
    monitor.scan_current(current)
    monitor.print_current()

    all_alerts = []
    all_alerts.extend(monitor.check_new_ports())
    all_alerts.extend(monitor.check_closed_ports())
    all_alerts.extend(monitor.check_suspicious())

    print(f"\n=== 端口监控告警 ({len(all_alerts)}条) ===")
    for i, alert in enumerate(all_alerts, 1):
        print(f"  [{i}] {alert}")


if __name__ == "__main__":
    main()
```

---

## 总结

**安全设备能力对比：**

| 设备类型 | 工作层次 | 核心能力 | 部署方式 |
|---------|---------|---------|---------|
| 包过滤防火墙 | L3/L4 | IP/端口过滤 | 串联 |
| 状态检测防火墙 | L3/L4 | 连接状态跟踪 | 串联 |
| NGFW | L3-L7 | 应用识别+IPS+AV | 串联 |
| WAF | L7 | Web攻击防护 | 串联/反向代理 |
| IDS | L3-L7 | 被动检测告警 | 旁路 |
| IPS | L3-L7 | 主动检测阻断 | 串联 |
| SIEM | 全层 | 日志关联分析 | 独立平台 |

**纵深防御体系（Defense in Depth）：**

```
  ┌───────────────────────────────────────────────────┐
  │ 第1层: 边界防护 (NGFW + IPS)                       │
  │ → 网络层攻击拦截、已知威胁阻断                      │
  ├───────────────────────────────────────────────────┤
  │ 第2层: 应用防护 (WAF)                              │
  │ → OWASP Top 10攻击防护、CC攻击防御                  │
  ├───────────────────────────────────────────────────┤
  │ 第3层: 终端防护 (EDR + 主机IPS)                    │
  │ → 恶意软件检测、异常进程监控                        │
  ├───────────────────────────────────────────────────┤
  │ 第4层: 检测响应 (SIEM + 威胁狩猎)                  │
  │ → 多源日志关联分析、主动威胁发现                    │
  ├───────────────────────────────────────────────────┤
  │ 第5层: 应急响应 (IR Plan + SOAR)                   │
  │ → 自动化响应、快速隔离与恢复                        │
  └───────────────────────────────────────────────────┘
```

**安全运营成熟度模型：**
- **Level 1 - 被动防御**：依赖防火墙规则，事件驱动响应
- **Level 2 - 主动监控**：部署IDS/SIEM，建立告警流程
- **Level 3 - 威胁狩猎**：主动搜索未知威胁，假设驱动分析
- **Level 4 - 自动化响应**：SOAR编排，自动化阻断与恢复
- **Level 5 - 智能运营**：AI辅助检测，威胁情报驱动，自适应防御
