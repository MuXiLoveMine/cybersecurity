# SIEM与安全运营

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

---

## 📋 内容审核与补充建议

> 针对「SIEM与安全运营」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
