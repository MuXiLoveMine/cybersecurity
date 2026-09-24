# IDS-IPS基础

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

---

