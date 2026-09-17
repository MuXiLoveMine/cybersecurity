# Splunk ES实战

### 8.1 Splunk架构与部署

Splunk采用分布式架构，核心组件包括：

- **Forwarder（转发器）**：部署在各数据源主机上，负责数据采集和转发。Universal Forwarder是最常用的轻量级Agent
- **Indexer（索引器）**：接收数据并建立索引，是数据处理和存储的核心节点。生产环境通常部署多个Indexer组成集群
- **Search Head（搜索头）**：提供Web界面和搜索能力，将搜索请求分发给Indexer并汇总结果
- **Cluster Master**：管理Indexer集群，负责数据复制和故障恢复

Splunk Enterprise Security（ES）是建立在Splunk平台之上的安全应用套件，提供预置的CIM模型、关联搜索、安全态势仪表板和事件管理工作流。

**部署架构示例（中型企业）**：
```
数据源(1000+台主机) 
  → 2台Heavy Forwarder(负载均衡+预处理)
  → 3台Indexer集群(数据复制因子2)
  → 1台Search Head + 1台ES App
  → 1台Deployer(管理配置分发)
```

### 8.2 数据采集配置

**配置Universal Forwarder采集Windows安全日志**：

在inputs.conf中配置：
```ini
[WinEventLog://Security]
disabled = 0
index = wineventlog
renderXml = true
```

**配置Syslog接收**：
```ini
[udp://514]
connection_host = ip
index = network
sourcetype = syslog
source = udp:514
```

**通过Splunk Add-on采集云日志**：
- Splunk Add-on for AWS：通过SQS或直接API拉取CloudTrail、VPC Flow Log
- Splunk Add-on for Microsoft 365：拉取Azure AD Sign-in Log、Exchange Audit

### 8.3 关联规则编写

Splunk ES的关联检测使用Correlation Search（关联搜索），以Saved Search形式实现，支持计划定时执行。

**示例：检测异常RDP登录（横向移动场景）**

```splunk
index=auth sourcetype=WinEventLog:Security EventID=4624 LogonType=10
| stats count, dc(dest_host) as host_count, values(dest_host) as targets 
  by user, src_ip
| where host_count > 5
| lookup previously_seen_hosts user OUTPUT seen_hosts
| eval new_hosts = mvdiff(targets, seen_hosts)
| where mvcount(new_hosts) > 3
```

此搜索的逻辑：同一用户通过RDP登录超过5台不同主机，且其中超过3台是此前从未登录过的主机——典型的横向移动行为模式。

### 8.4 仪表板设计

Splunk ES预置多类仪表板，也可自定义：

**安全态势仪表板（Security Posture）**：
- 实时告警按级别分布的环形图
- Top 10威胁类型柱状图
- 资产风险热力图（按IP/子网）
- 24小时告警趋势时间线

**访问异常监控仪表板**：
- 地理位置异常登录地图可视化
- 非工作时间登录统计
- 特权账户使用趋势
- 新IP/新设备首次登录列表

**自定义仪表板设计原则**：
- 层次递进：总览→分类明细→单事件详情
- 颜色语义一致：红色=高危、黄色=中危、绿色=正常
- 可交互：点击图表元素可下钻到对应日志明细
- 时间范围可调：支持全局时间选择器联动

### 8.5 告警与工作流

Splunk ES的Notable Events（重要事件）机制：
- Correlation Search命中后生成Notable Event
- Notable Event进入ES的Incident Review工作台
- 分析师可在工作台中执行：状态变更→分派→添加注释→关联到已有Case→触发响应动作

**告警通知配置**：
```ini
[alert:critical_rdp_anomaly]
alert_type = scheduled
cron_schedule = */5 * * * *
alert.severity = 3
alert.track = 1
action.email = 1
action.email.to = soc-team@company.com
action.webhook = https://soar.company.com/api/trigger
```

**工作流集成**：
- 与Splunk SOAR集成：Notable Event自动触发Phantom Playbook
- 与工单系统集成：通过REST API创建ServiceNow工单
- 与飞书/钉钉集成：通过Webhook发送告警卡片到群聊

---

---

## 📋 内容审核与补充建议

> 针对「Splunk ES实战」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
