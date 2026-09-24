# SIEM架构与核心组件

一个完整的SIEM系统采用分层架构设计，从数据采集到最终展示共有五层。

### 2.1 数据采集层

数据采集是SIEM的入口层，决定了后续分析的数据质量。

**Agent采集模式**：在终端/服务器上部署轻量级Agent程序（如Splunk Universal Forwarder、Wazuh Agent、Winlogbeat），主动读取本地日志文件、Windows Event Log、应用日志并转发到SIEM。优势是可控性强、支持本地预处理过滤、支持断点续传。劣势是需在每台主机安装维护Agent，增加管理开销。

**无Agent采集模式**：通过标准协议被动接收日志，最常用的是Syslog（UDP/TCP 514端口）。网络设备（防火墙、交换机、路由器）普遍支持Syslog输出，无需安装Agent。对于Windows环境，可通过WinRM/Event Subscription或WEC（Windows Event Forwarding）实现无Agent集中收集Event Log。API集成则是云时代的主流方式——AWS CloudTrail、Azure Activity Log、Office 365 Audit Log均通过REST API拉取。

**Beats/Winlogbeat**：Elastic Stack生态中的轻量数据采集器。Winlogbeat专门收集Windows Event Log，Filebeat读取文件日志，Packetbeat抓取网络流量，Auditbeat采集审计数据。各Beat模块开箱即用地预置了常见数据源的解析配置。

**采集层关键设计考量**：
- 带宽控制：对跨广域网传输的日志进行压缩和限流
- 缓冲与容灾：本地队列缓存+断点续传，防止SIEM宕机期间丢日志
- 过滤预处理：在采集端丢弃无用日志（如debug级别日志），降低后端存储和计算压力
- 时钟同步：要求所有日志源NTP同步，否则时间窗口关联分析将失效

### 2.2 数据处理层

日志进入SIEM后，需要经过四个处理步骤才能被有效分析：

**解析**：将原始日志文本拆解为结构化字段。例如Cisco ASA防火墙的Syslog消息：
```
%ASA-6-302013: Built outbound TCP connection 12345 for outside:192.168.1.100/443 (192.168.1.100/443)
```
解析器需要提取出：设备类型(ASA)、严重级别(6)、事件ID(302013)、动作(Built)、方向(outbound)、协议(TCP)、连接ID(12345)、接口(outside)、IP(192.168.1.100)、端口(443)等字段。

**标准化**：将不同厂商不同格式的字段映射为统一模型。例如：
- Cisco的"src_ip"字段、Palo Alto的"source-address"字段、Windows的"SourceAddress"字段，统一映射为标准字段名"src_ip"
- 时间戳格式统一为ISO 8601（2026-09-13T10:30:00Z）
- 严重级别统一为CRITICAL/HIGH/MEDIUM/LOW/INFO

主流标准化模型：
- **CIM（Common Information Model）**：Splunk的通用信息模型，定义了20+数据域的统一字段
- **CEF（Common Event Format）**：Micro Focus提出的标准化事件格式，被广泛支持
- **LEEF（Log Event Extended Format）**：IBM QRadar使用的格式
- **OCSF（Open Cybersecurity Schema Framework）**：2023年由多家厂商联合推出的开源标准

**富化**：在原始日志基础上补充上下文信息，大幅提升分析价值：
- 威胁情报富化：将IP/域名/文件哈希与威胁情报库比对，标记恶意属性
- 资产信息富化：通过CMDB关联，给IP添加资产属性（操作系统版本、所属业务系统、责任人、数据分级）
- 地理位置富化：通过GeoIP数据库将公网IP解析为国家/城市/ASN
- 身份富化：通过AD/LDAP关联，将机器名/IP映射为用户身份

**索引**：将处理后的结构化日志建立倒排索引，支持毫秒级全文检索。索引策略通常采用时间分片——每天或每小时创建一个索引，便于基于时间范围的高效查询和过期数据自动滚动删除。

### 2.3 存储层

SIEM存储采用分层策略，平衡查询性能与存储成本：

| 层级 | 存储介质 | 查询延迟 | 保留时间 | 典型用途 |
|------|---------|---------|---------|---------|
| 热数据 | SSD/NVMe | <1秒 | 7-30天 | 实时告警、日常调查 |
| 温数据 | HDD/对象存储 | 秒级 | 90-180天 | 取证溯源、趋势分析 |
| 冷数据 | 对象存储/磁带 | 分钟级 | 1-7年 | 合规审计、长期留存 |

在Elasticsearch中，此分层通过ILM（Index Lifecycle Management）策略实现：索引先在热节点（SSD）上活跃写入，7天后迁移到温节点（HDD），90天后转为只读快照存储到S3/MinIO对象存储。Splunk通过"索引卷"和"frozen"桶实现类似分层。

### 2.4 分析引擎

分析引擎是SIEM的大脑，包含三类分析能力：

**规则引擎**：基于确定条件的规则匹配。如"同一源IP在5分钟内对5个以上不同端口发起连接"触发端口扫描告警。规则引擎执行效率高、结果可解释性强，但对未知攻击无效。典型实现如Sigma规则（开源通用规则格式，可跨SIEM平台使用）。

**关联引擎**：跨事件、跨数据源、跨时间窗口的复杂关联。支持时序关联（A事件在B事件后N分钟内发生）、聚合关联（N个同类事件在T时间窗口内累计超过阈值）、因果关联（A事件是B事件的前置条件）。QRadar的Rule Building Engine和Splunk的Correlation Search是典型实现。

**UEBA/机器学习引擎**：基于统计学和ML的异常检测。与规则引擎互补——规则引擎回答"是否匹配已知攻击模式"，UEBA回答"是否存在偏离正常基线的行为"。详见第五章。

### 2.5 展示与告警层

**Dashboard（仪表板）**：可视化展示安全运营全景。典型Dashboard包括：
- 安全态势总览：实时告警数、高危事件数、资产风险分布
- 威胁趋势：告警趋势图、Top10攻击源IP、攻击类型分布
- 合规视图：日志覆盖率、审计报表状态
- 运营效率：MTTD/MTTR趋势、分析师工作量分布

**告警管理**：统一管理所有触发的告警，支持分级、分派、去重、抑制。高级SIEM支持告警聚合——将同一攻击活动的多条告警合并为一个Incident，避免告警风暴。

**工单集成**：与ITSM系统（ServiceNow、Jira Service Desk、Remedy）集成，将告警自动转为工单，跟踪处置全过程，实现"检测→响应→关闭"的闭环管理。

---

---

