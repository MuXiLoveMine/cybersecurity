# SIEM与SOC安全运营实战

> 本文档对应审计报告覆盖率最低的模块15（覆盖率61%），聚焦SIEM平台架构、日志关联分析、UEBA行为分析、SOC运营体系及自动化编排等核心缺口领域，旨在帮助读者建立完整的"平台+流程+人员"三位一体安全运营能力。

---

## 一、SIEM概述

### 1.1 SIEM定义与核心功能

SIEM（Security Information and Event Management，安全信息与事件管理）是一种综合性安全平台，通过聚合来自异构数据源的日志与事件数据，进行实时关联分析，以实现威胁检测、告警响应和合规审计。SIEM一词由Gartner于2005年首次提出，本质上是SIM（Security Information Management，安全信息管理）与SEM（Security Event Management，安全事件管理）的融合体——SIM侧重日志的长期存储与合规报表，SEM侧重实时事件关联与告警。

SIEM的核心功能可归纳为六大支柱：

1. **日志聚合**：从防火墙、IDS/IPS、终端EDR、Web服务器、数据库、云平台等数十乃至数百种异构数据源收集日志，统一汇聚到集中式存储。一个典型企业日均日志量在50GB到5TB不等，SIEM需要支持高吞吐写入与长期留存。

2. **解析与标准化**：不同设备厂商的日志格式各异（如Cisco的Syslog、Windows的XML格式Event Log、JSON格式的云审计日志），SIEM通过解析器将其映射为统一字段模型，便于后续关联查询。

3. **关联分析**：这是SIEM最核心的价值所在。通过跨数据源、跨时间窗口的关联规则，将看似无关的孤立事件串联为完整的攻击链。例如，5分钟内同一源IP对SSH端口的20次失败登录 + 随后1次成功登录，可关联判定为暴力破解成功事件。

4. **告警管理**：当关联规则命中时生成告警，按严重等级分级，触发通知（邮件、短信、工单系统），并跟踪告警的完整生命周期（新建→调查中→处置中→关闭）。

5. **报表与合规**：预置PCI DSS、SOX、HIPAA、GDPR、等保2.0等合规框架的报表模板，一键生成审计所需的证据链报表，大幅降低合规审计的工作量。

6. **取证与调查**：提供强大的搜索查询语言（如Splunk SPL、Elastic KQL/Lucene），支持安全分析师在海量历史日志中快速溯源、还原攻击时间线。

### 1.2 SIEM演进历程

SIEM的发展经历了四个主要阶段：

**第一阶段：SIM/SEM分立时代（2000-2005）**

SIM产品以日志收集和合规存储为核心，代表产品如ArcSight的Logger、LogLogic。SEM产品以实时事件关联为核心，代表产品如eSecurity、NetForensics。两者功能互补但各自为政，分析师需要在两个系统间来回切换。

**第二阶段：SIEM融合时代（2005-2012）**

Gartner正式定义SIEM品类后，主流厂商开始整合SIM与SEM能力。ArcSight ESM、IBM QRadar、NitroSecurity（后McAfee收购）成为市场领导者。此阶段SIEM的核心能力在于规则引擎和日志标准化，但主要依赖人工编写规则，对未知威胁检测能力有限。

**第三阶段：下一代SIEM（2012-2019）**

随着大数据技术和机器学习的成熟，SIEM进入下一代阶段。Splunk以搜索引擎架构颠覆了传统SIEM的关系型数据库存储模式，Elastic Stack（ELK）以开源之姿进入安全领域。此阶段三大标志特征：引入UEBA（用户实体行为分析）实现异常检测、集成威胁情报实现 IOC比对、支持大数据平台实现PB级日志存储。

**第四阶段：智能融合时代（2019至今）**

当前SIEM正与SOAR（安全编排自动化与响应）、XDR（扩展检测与响应）深度融合。Microsoft Sentinel以云原生SIEM形态重新定义市场，Gartner提出"SIEM正在演变为统一安全运营平台"的趋势判断。AI大模型（LLM）开始被引入SIEM领域，用于自然语言查询、告警自动摘要、Playbook智能推荐等场景。

### 1.3 SIEM在安全运营中的定位

SIEM是SOC（安全运营中心）的核心技术底座，在整个安全运营体系中起到"中枢大脑"的作用。可从三个维度理解其定位：

**检测维度**：SIEM是唯一能够进行跨域关联分析的平台。EDR检测端点异常、防火墙检测网络异常、IAM检测身份异常——但这些单点工具无法看到完整攻击链。SIEM通过汇聚全量日志，实现"碎片化事件→完整攻击叙事"的拼图能力。

**响应维度**：SIEM不仅是检测引擎，更是响应的指挥中心。通过集成SOAR平台，SIEM告警可自动触发响应剧本（Playbook），实现自动封禁恶意IP、隔离失陷主机、禁用被盗账号等闭环操作。

**合规维度**：对于等保2.0三级及以上系统、PCI DSS、SOX等合规要求，SIEM的集中日志审计和报表功能是硬性刚需。等保2.0明确要求"对网络链路、安全设备、服务器和网络应用系统的运行状况、网络流量、用户行为等进行日志记录与审计"，SIEM正是满足此要求的标准设施。

### 1.4 市场主流SIEM产品对比

| 特性 | Splunk ES | IBM QRadar | Microsoft Sentinel | Elastic SIEM | Wazuh |
|------|-----------|------------|-------------------|--------------|-------|
| 架构 | 搜索引擎+索引 | 流式处理引擎 | 云原生SaaS | Elasticsearch | Server+Agent+Indexer |
| 部署模式 | 本地/云 | 本地/云 | 仅云（Azure） | 本地/云 | 本地 |
| 数据接入 | Universal Forwarder | Wincollect/Qradar Flow | Analytics/Agent | Beats/Logstash | Wazuh Agent |
| 关联引擎 | SPL查询+Correlation Search | Rule Building Engine | KQL+Analytics Rule | KQL/ESQL | Rule Engine |
| UEBA | Splunk UBA | QRadar UBA | Sentinel UEBA | ML作业 | 基线规则 |
| SOAR | Splunk SOAR | QRadar SOAR (Resilient) | Sentinel Playbooks | Elastic SIEM Actions | Active Response |
| 许可成本 | 按摄入量（高） | 按EPS/节点 | 按摄入量（中） | 按资源（中低） | 开源免费 |
| 适用场景 | 大型企业/复杂环境 | 金融/政府 | 云优先企业 | 技术能力强团队 | 中小企业/预算有限 |

**选型建议**：
- 大型集团、复杂异构环境、预算充足：Splunk ES或IBM QRadar
- 已全面使用Microsoft生态、云优先策略：Microsoft Sentinel
- 拥有强大技术运维团队、追求灵活可控：Elastic SIEM
- 中小企业、预算有限、希望快速起步：Wazuh

---

## 二、SIEM架构与核心组件

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

## 三、日志收集与解析

### 3.1 常见日志源

**Windows Event Log**：
- 安全日志：登录成功/失败(4624/4625)、权限提升(4672)、账户创建(4720)、策略修改(4739)、进程创建(4688)等
- 系统日志：服务启停、驱动加载、系统错误
- 应用日志：IIS、SQL Server、Exchange等应用日志
- PowerShell日志：脚本块日志(4104)、模块日志(4103)、脚本执行(400)
- Sysmon日志：进程创建(1)、网络连接(3)、文件创建(11)、注册表修改(12/13)等增强事件

**Linux Syslog**：
- /var/log/auth.log或/var/log/secure：SSH登录、sudo操作、用户管理
- /var/log/syslog或/var/log/messages：系统事件
- /var/log/audit/audit.log：auditd审计日志，支持细粒度系统调用审计
- /var/log/nginx/access.log、/var/log/apache2/access.log：Web服务器访问日志

**网络设备**：
- 防火墙：Cisco ASA/Palo Alto/Fortinet的允许/拒绝日志、NAT日志
- IDS/IPS：Suricata/Snort/Zeek的告警和会话日志
- 交换机/路由器：Cisco IOS日志、流量统计(NetFlow/sFlow)
- VPN网关：用户接入/断开日志、认证成功/失败

**云平台**：
- AWS：CloudTrail（API调用）、VPC Flow Logs（网络流量）、GuardDuty（威胁检测）
- Azure：Activity Log（订阅级操作）、Sign-in Logs（登录）、Azure AD Audit
- 阿里云：ActionTrail（API调用）、SLB日志、WAF日志

**应用与数据库**：
- 数据库审计日志：Oracle Audit、MySQL General Log、SQL Server Audit
- 中间件日志：WebLogic、Tomcat、Nginx access/error log
- 自研应用：业务安全日志（如风控系统的异常行为日志）

### 3.2 日志标准化方法

日志标准化是将异构原始日志转换为统一格式的过程，使得分析引擎能用统一查询语句检索来自不同数据源的日志。

**CEF格式示例**：
```
CEF:0|Cisco|ASA|9.0|302013|Built outbound TCP connection|6|src=10.0.0.1 spt=54321 dst=192.168.1.100 dpt=443 proto=TCP act=Built
```
CEF以管道符分隔字段，前缀固定为版本号|厂商|产品|产品版本|事件ID|事件名|严重级别|扩展字段。

**Sigma规则**：Sigma是开源的通用SIEM规则格式，类似于"日志分析的Yara"。一条Sigma规则可以自动转换为Splunk SPL、Elastic KQL、QRadar AQL等多平台查询语句。

Sigma规则示例（检测可疑PowerShell执行）：
```yaml
title: Suspicious PowerShell Execution
status: experimental
description: Detects PowerShell execution with encoded commands
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4688
        NewProcessName|endswith: powershell.exe
        CommandLine|contains: '-enc'
    condition: selection
level: high
```

### 3.3 日志解析规则编写

以Elastic的Logstash Grok过滤器为例，编写Apache访问日志解析规则：

原始日志：
```
192.168.1.50 - - [13/Sep/2026:10:25:36 +0800] "GET /admin/login.php HTTP/1.1" 200 4523 "https://example.com/" "Mozilla/5.0..."
```

Grok解析模式：
```
%{IP:client_ip} %{Ident:ident} %{User:user} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{URIPATHPARAM:request} HTTP/%{NUMBER:http_version}" %{NUMBER:status_code} %{NUMBER:bytes} "(?:%{URI:referrer}|-)" "%{DATA:user_agent}"
```

解析后输出结构化字段：
```json
{
  "client_ip": "192.168.1.50",
  "method": "GET",
  "request": "/admin/login.php",
  "status_code": 200,
  "bytes": 4523,
  "user_agent": "Mozilla/5.0..."
}
```

### 3.4 日志富化

日志富化在解析后执行，为原始日志补充上下文维度：

**威胁情报富化**：集成OTX、VirusTotal、MISP等威胁情报源，对日志中出现的IP/域名/文件哈希进行自动比对。若源IP命中恶意IP列表，在日志中添加`threat_intel.malicious=true`标记。

**资产信息富化**：对接CMDB数据库，根据IP查询关联的资产信息并附加到日志中：
```json
{
  "src_ip": "10.0.5.23",
  "asset": {
    "hostname": "DB-PROD-01",
    "os": "CentOS 7.9",
    "business_system": "核心交易系统",
    "data_classification": "机密",
    "owner": "数据库团队-张三"
  }
}
```

**地理位置富化**：通过MaxMind GeoIP2数据库，将公网IP解析为地理位置：
```json
{
  "src_ip": "203.0.113.50",
  "geo": {
    "country": "俄罗斯",
    "city": "莫斯科",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "asn": "AS12345",
    "isp": "某ISP"
  }
}
```

---

## 四、关联分析与告警

### 4.1 关联规则设计方法

**基于规则的关联**：安全专家根据已知的攻击技术（如MITRE ATT&CK框架中的技术项）编写显式规则。核心思路是"如果观察到A且B且C，则触发告警"。例如，ATT&CK T1110 Brute Force技术可转化为"5分钟内同一源IP对同一目标账户的认证失败超过10次"。

**基于行为的关联**：基于历史基线的偏差检测。先建立正常行为基线（如某用户日常登录时间9:00-18:00、日常访问IP范围10.0.x.x），再对偏离基线的行为生成告警。这种方法能够发现规则无法覆盖的未知攻击，但误报率较高，需要持续调优。

**基于场景的关联**：按照完整攻击链模型（如Cyber Kill Chain或MITRE ATT&CK）设计多阶段关联规则。将侦察→武器化→投递→利用→安装→命令控制→行动各阶段的信号串联，当多个阶段信号同时出现时提升置信度。例如"外部IP对Web服务器的漏洞扫描（侦察） + 随后该IP成功利用Web漏洞（投递+利用） + 该Web服务器开始向外发送DNS查询到已知C2域名（命令控制）"可关联为高置信度APT攻击链。

### 4.2 常见关联规则示例

**暴力破解检测**：
```
规则名称：SSH暴力破解检测
触发条件：
  同一源IP在5分钟内
  对同一目标主机的SSH端口(22)
  认证失败事件超过20次
严重级别：HIGH
Splunk SPL实现：
  index=auth sourcetype=linux_secure action=failure
  | stats count as fail_count by src_ip, dest_host
  | where fail_count > 20
```

**横向移动检测**：
```
规则名称：Pass-the-Hash横向移动检测
触发条件：
  同一源账户在30分钟内
  成功登录超过5台不同主机
  且登录类型为Network(LogonType=3)
  且源账户此前从未访问过这些主机
严重级别：HIGH
```

**数据外泄检测**：
```
规则名称：异常大流量外传检测
触发条件：
  源主机为内部IP
  目标为外部IP
  单次会话传输数据量超过500MB
  或 单日累计外传数据超过5GB
  且 目标IP不在白名单中（如已知CDN、备份服务器）
严重级别：CRITICAL
```

### 4.3 告警分级与降噪策略

告警分级通常采用四级模型：

| 级别 | 含义 | 响应时效 | 典型场景 |
|------|------|---------|---------|
| Critical | 确认攻击进行中或已成功 | 立即响应(<15分钟) | 勒索软件加密、C2通信已建立 |
| High | 高可信度攻击尝试 | 30分钟内 | 暴力破解成功、已知漏洞利用 |
| Medium | 可疑活动需调查 | 4小时内 | 异常登录时间、异常文件访问 |
| Low | 信息记录 | 24小时内 | 策略变更、正常运维操作 |

降噪策略：
1. **告警聚合**：将同一攻击相关的多条原始告警合并为一个Incident，避免"告警风暴"
2. **告警抑制**：同一规则在同一实体上短时间内重复触发时，只保留首条告警，抑制后续重复
3. **白名单机制**：对已知的合法行为（如漏洞扫描器的定期扫描、运维批量操作）加入白名单
4. **上下文富化降级**：命中威胁情报的告警升为High，来自已知安全资产的告警降为Medium
5. **UEBA置信度叠加**：规则触发的告警叠加UEBA评分，低于阈值的不展示

### 4.4 告警生命周期管理

完整的告警生命周期包含七个状态：

1. **New（新建）**：规则匹配触发，告警进入队列
2. **Triaged（分诊）**：Tier 1分析师确认告警有效性，过滤误报
3. **Assigned（分派）**：确认有效后分派给Tier 2/3深入调查
4. **In Progress（调查中）**：分析师正在调查根因和影响范围
5. **Contained（已遏制）**：威胁已被控制（如隔离主机、封禁IP）
6. **Resolved（已解决）**：威胁已根除，系统恢复正常
7. **Closed（关闭）**：完成复盘报告，归档

每个状态转换需记录操作人、时间戳、操作理由，形成完整的审计链。

---

## 五、UEBA用户实体行为分析

### 5.1 UEBA原理与架构

UEBA（User and Entity Behavior Analytics）通过建立用户和实体（服务器、设备、应用）的正常行为基线，对偏离基线的行为进行异常检测，弥补传统规则引擎"只能检测已知攻击"的局限。

UEBA架构包含四个核心组件：
1. **数据集成层**：汇聚身份日志（AD登录、VPN接入）、行为日志（文件访问、数据库查询）、网络日志（连接、流量）
2. **基线建模层**：对正常行为进行统计建模，建立时间序列基线
3. **异常检测层**：实时计算当前行为与基线的偏差度，生成异常评分
4. **风险评分层**：将多个异常信号聚合为单一风险评分，输出到SIEM告警

### 5.2 异常检测算法

**统计学方法**：
- 均值标准差法：超过均值±3σ的行为标记为异常
- 箱线图法：超出IQR(四分位距)1.5倍的为异常
- 时间序列分解：将行为分解为趋势+周期+残差，残差过大为异常
- 适用于：登录时间异常、流量突增等场景

**机器学习方法**：
- Isolation Forest：基于随机森林的异常点隔离算法，无需标注数据
- One-Class SVM：单类支持向量机，学习正常行为的边界
- 局部异常因子(LOF)：基于密度的异常检测，适合局部异常
- 适用于：多维行为特征异常检测

**深度学习方法**：
- LSTM/GRU：处理时序行为序列，捕捉时间依赖关系中的异常
- Autoencoder：用正常数据训练自编码器，重建误差大的为异常
- 适用于：复杂行为模式异常、高级持续威胁检测

### 5.3 UEBA使用场景

**内部威胁检测**：
- 场景：员工即将离职前批量下载客户数据
- UEBA信号：该用户文件下载量从日均50个突增至2000个，且下载时间异常（凌晨3点）
- 风险评分：文件下载异常(0.8) + 时间异常(0.7) + 首次访问敏感目录(0.6) → 综合评分0.9

**账号失陷检测**：
- 场景：攻击者盗用合法账户进行横向移动
- UEBA信号：该账户从从未登录过的IP地址登录 + 登录后立即访问非日常业务系统 + 登录后创建了新服务账户
- 风险评分：新IP登录(0.6) + 异常资源访问(0.7) + 特权操作(0.8) → 综合评分0.8

**数据外泄检测**：
- 场景：内部服务器被攻陷后向外传输大量数据
- UEBA信号：服务器出站流量从日均2GB突增至50GB + 目标IP从未出现过的ASN + 传输时间在工作时间之外

### 5.4 UEBA调优与误报管理

UEBA初期部署通常面临高误报率（可达80-90%），需要系统化调优：

1. **基线学习期**：首次部署后至少运行4-8周建立稳定基线，此阶段告警仅用于观察不用于响应
2. **分阶段启用**：先在高价值用户（特权账户、高管）上启用，验证效果后推广到全员
3. **反馈闭环**：分析师对每条UEBA告警标记"真实异常/误报"，模型根据反馈持续优化
4. **动态阈值调整**：根据业务周期（如月底财务批量操作）动态调整阈值
5. **组合评分**：单一异常信号置信度低，多信号叠加后才触发告警

---

## 六、SOC安全运营中心

### 6.1 SOC架构设计

现代SOC采用三层分层运营架构，确保不同复杂度的事件由适当技能等级的分析师处理：

**Tier 1 - 初级监控层**：
- 职责：7×24实时监控告警、初步分诊、误报过滤、基础事件响应
- 技能要求：熟悉SIEM操作、了解常见攻击类型、能执行标准化响应流程
- 处理时效：告警产生后15分钟内开始处理
- 处理比例：处理约70-80%的告警，将复杂事件升级到Tier 2

**Tier 2 - 深度分析层**：
- 职责：深入事件调查、恶意代码分析、威胁范围确定、制定响应方案
- 技能要求：掌握取证分析技术、能解读PCAP和日志关联、理解MITRE ATT&CK
- 处理时效：升级后2小时内响应
- 处理比例：处理约15-20%的事件

**Tier 3 - 专家狩猎层**：
- 职责：高级威胁狩猎、APT调查、新攻击模式研究、规则优化建议
- 技能要求：逆向工程能力、威胁情报分析、高级取证技能
- 处理比例：处理约5-10%的高难度事件 + 主动威胁狩猎

### 6.2 SOC人员角色与职责

**SOC分析师（Tier 1/2/3）**：
- 实时监控告警并进行分诊、调查和响应
- 编写和优化检测规则
- 编写事件调查报告
- 参与威胁狩猎任务

**SOC工程师**：
- 维护SIEM/SOAR平台稳定运行
- 开发新的日志解析器和数据源集成
- 设计和实现自动化Playbook
- 优化数据管道性能

**SOC管理员**：
- 用户权限和访问控制管理
- 数据保留策略和存储管理
- 系统监控和性能调优
- 灾备和应急通信

**SOC管理者**：
- 制定SOC运营策略和KPI
- 团队管理和能力建设
- 与管理层和业务部门沟通
- 预算和资源规划

### 6.3 SOC运营流程

SOC标准运营流程遵循"监控→检测→分析→响应→恢复→复盘"六步闭环：

1. **监控**：7×24持续监控SIEM告警看板、安全设备状态、威胁情报订阅
2. **检测**：通过规则触发、UEBA异常、威胁情报匹配、主动狩猎发现潜在威胁
3. **分析**：关联多源日志确定攻击时间线、影响范围、涉及资产和账户
4. **响应**：执行遏制措施（封禁IP、隔离主机、禁用账户）、根除威胁（清除恶意文件、修复漏洞）
5. **恢复**：验证系统干净后恢复业务运行、确认无后门残留
6. **复盘**：撰写事件报告、总结经验教训、优化检测规则和响应流程

### 6.4 SOC度量指标

| 指标 | 定义 | 目标值 | 说明 |
|------|------|--------|------|
| MTTD | 平均检测时间 | <30分钟 | 从攻击发生到SOC检测到的时间 |
| MTTR | 平均响应时间 | <4小时 | 从检测到完成处置的时间 |
| 告警准确率 | 真实告警/总告警 | >70% | 衡量规则质量 |
| 覆盖率 | 已覆盖资产/总资产 | >90% | 衡量日志接入完整性 |
| 误报率 | 误报数/总告警 | <15% | 衡量检测精度 |
| 事件闭环率 | 已关闭事件/总事件 | >95% | 衡量处置完成度 |
| Mean Time to Contain | 平均遏制时间 | <1小时 | 从检测到威胁被遏制的时间 |

### 6.5 SOC成熟度模型

| 级别 | 名称 | 特征 | 典型状态 |
|------|------|------|---------|
| Level 1 | 初级 | 人工监控、被动响应、无标准化流程 | 有SIEM但规则少，靠人工巡检 |
| Level 2 | 定义级 | 有标准流程和SOP、基础SIEM规则覆盖 | 规则覆盖主要攻击场景，有Tier 1 |
| Level 3 | 管理级 | 度量指标驱动、UEBA增强、初步自动化 | KPI体系建立，部分SOAR自动化 |
| Level 4 | 优化级 | SOAR深度自动化、主动威胁狩猎、威胁情报驱动 | 50%+自动化响应，有狩猎团队 |
| Level 5 | 卓越级 | AI驱动、XDR融合、零信任集成、持续自适应 | 大模型辅助分析，与DevSecOps融合 |

---

## 七、安全运营自动化

### 7.1 Playbook设计

Playbook（响应剧本）是SOAR平台的核心，定义了从告警触发到响应完成的标准自动化流程。设计Playbook遵循以下方法论：

**Playbook设计步骤**：
1. 分析触发场景：明确Playbook应对的安全事件类型
2. 定义触发条件：什么告警自动触发此Playbook
3. 编排动作序列：设计自动化执行的操作步骤
4. 设置决策分支：在关键步骤设置人工审批或条件判断
5. 定义超时和异常处理：每步设置超时和失败回退
6. 测试与验证：在测试环境验证后灰度上线

**示例：恶意IP告警自动响应Playbook**

```
触发条件：威胁情报匹配到恶意IP通信告警
步骤1：自动富化—查询该IP的威胁情报详情（病毒评分、攻击历史）
步骤2：自动关联—查询内网哪些主机曾与该IP通信
步骤3：自动判断—是否在白名单？（是→关闭告警，否→继续）
步骤4：自动封禁—在防火墙自动添加deny规则
步骤5：自动隔离—对已通信的内网主机触发EDR隔离
步骤6：人工审批—Tier 2确认是否需要对隔离主机做深度取证
步骤7：自动创建工单—将事件信息自动填入工单系统
步骤8：自动通知—通过飞书/钉钉通知相关负责人
```

### 7.2 SOAR集成与自动化编排

SOAR（Security Orchestration, Automation and Response）是连接SIEM与各类安全工具的"粘合剂"，通过预置的集成连接器（Integration/Connector）调用各类安全产品的API，实现跨工具自动化编排。

常见SOAR平台：
- Splunk SOAR（原Phantom）：300+集成连接器，支持Python自定义
- IBM Resilient：与QRadar深度集成，强项在事件管理和工单流程
- Palo Alto Cortex XSOAR：社区驱动的Playbook Marketplace
- Microsoft Sentinel Playbooks：基于Azure Logic Apps，云原生

SOAR核心能力：
1. **案例管理**：将多个告警聚合为一个Case，统一管理
2. **动作库**：预置数百个安全工具的API封装（封IP、隔离主机、查沙箱、发工单）
3. **剧本引擎**：可视化编排工作流，支持循环、条件、并行
4. **协同作战**：多分析师在同一Case上协同记录、共享调查信息

### 7.3 常见自动化场景

**自动封禁IP**：
- 触发：暴力破解/已知恶意IP通信告警
- 动作：API调用防火墙添加deny规则 + API调用WAF添加黑名单 + EDR标记
- 超时设置：封禁有效期24小时，到期自动评估是否续封
- 审批要求：对外网IP自动封禁无需审批；对内网IP需Tier 2审批

**自动隔离主机**：
- 触发：EDR检测到勒索软件行为/确认失陷
- 动作：EDR网络隔离 + VPN断开 + 防火墙隔离VLAN + 资产库标记"已隔离"
- 审批要求：生产环境主机隔离必须Tier 3审批，防止误隔离导致业务中断
- 恢复流程：取证完成后人工恢复网络连接

**自动创建工单**：
- 触发：所有Critical/High告警
- 动作：自动提取告警信息（时间、IP、主机、攻击类型、规则名）填入工单模板
- 分派规则：按攻击类型自动路由（勒索→应急响应组、数据泄露→数据安全组）
- 通知联动：同时通过飞书/钉钉机器人推送到对应团队群

### 7.4 人在环路（Human-in-the-loop）设计

并非所有响应都适合全自动，关键决策需要人工判断。人在环路设计原则：

1. **低风险+高确定性=全自动**：自动封禁已知恶意IP、自动关闭低危告警
2. **低风险+低确定性=半自动**：自动执行信息收集，人工确认后再执行动作
3. **高风险+高确定性=审批后自动**：隔离生产环境主机，人工一键审批后自动执行全流程
4. **高风险+低确定性=人工处理**：APT调查、法律取证等需要人工全程参与

关键设计要素：
- 审批超时机制：审批超时后自动降级处理（如只告警不动作）或自动升级
- 可逆操作优先：优先执行可逆操作（如IP封禁可撤销），不可逆操作需更高级别审批
- 操作审计：所有自动化操作完整记录日志，便于事后审计和复盘

---

## 八、Splunk ES实战

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

## 九、Wazuh开源SIEM实战

### 9.1 Wazuh架构

Wazuh是一套开源安全平台，融合了HIDS（主机入侵检测）、SIEM日志分析、漏洞检测和合规审计能力。

核心组件：

1. **Wazuh Server**：分析引擎，处理Agent上报的数据、执行规则匹配、生成告警
2. **Wazuh Agent**：部署在被监控主机上的轻量客户端（约5MB），采集日志、文件变更、运行进程等信息并上报Server
3. **Wazuh Indexer**：基于OpenSearch的存储和搜索引擎，存储告警和事件数据
4. **Wazuh Dashboard**：基于OpenSearch Dashboards的可视化界面，提供预置安全仪表板和告警管理

数据流：
```
Agent → Server(解码+规则匹配) → Indexer(索引存储) → Dashboard(可视化展示)
```

### 9.2 安装与部署

**快速安装（CentOS/RHEL）**：

```bash
# 安装Wazuh Server
curl -s https://packages.wazuh.com/4.x/yum/ | sudo tee /etc/yum.repos.d/wazuh.repo
sudo yum install wazuh-manager -y
sudo systemctl enable --now wazuh-manager

# 安装Indexer
sudo yum install wazuh-indexer -y
sudo systemctl enable --now wazuh-indexer

# 安装Dashboard
sudo yum install wazuh-dashboard -y
sudo systemctl enable --now wazuh-dashboard

# 安装Agent（在被监控主机上）
sudo WAZUH_MANAGER="10.0.0.1" \
  WAZUH_REGISTRATION_PASSWORD="password" \
  yum install wazuh-agent -y
sudo systemctl enable --now wazuh-agent
```

**部署规划建议**：
- Agent到Server通信默认使用1514/UDP端口，注意防火墙放行
- 单台Server可管理约5000个Agent（视硬件配置）
- 超过5000 Agent建议部署Server集群
- Indexer独立部署，建议16GB+内存、SSD存储

### 9.3 规则配置与自定义

Wazuh使用XML格式定义解码器（Decoder）和规则（Rule）。

**解码器示例（解析自定义应用日志）**：

```xml
<decoder name="custom-app">
  <prematch>^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \w+ </prematch>
  <regex>^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}) (\w+) (\S+) (\S+) (\d+)</regex>
  <order>timestamp,level,user,action,result_code</order>
</decoder>
```

**规则示例（检测异常用户创建）**：

```xml
<group name="linux, usermanagement,">
  <rule id="100200" level="10">
    <if_sid>530</if_sid>
    <match>adduser</match>
    <description>New user account created: $(user)</description>
    <group>usermanagement,account_change,</group>
  </rule>

  <rule id="100201" level="12">
    <if_sid>100200</if_sid>
    <user>^root$</user>
    <description>Root user created a new account - potential privilege escalation</description>
  </rule>
</group>
```

- level字段定义严重级别（0-15），10+为高危
- if_sid引用父规则，实现规则链
- match/regex支持字符串匹配和正则匹配

### 9.4 集成漏洞检测与文件完整性监控

**漏洞检测（Vulnerability Detection）**：

Wazuh Agent定期收集主机已安装软件包清单，与CVE数据库比对，自动发现已知漏洞。

配置（在ossec.conf中启用）：
```xml
<vulnerability-detector>
  <enabled>yes</enabled>
  <interval>1h</interval>
  <ignore_time>6h</ignore_time>
  <run_on_start>yes</run_on_start>
  <providers>
    <provider name="canonical">yes</provider>
    <provider name="nvd">yes</provider>
    <provider name="redhat">yes</provider>
    <provider name="msu">yes</provider>
  </providers>
</vulnerability-detector>
```

Dashboard会自动展示漏洞统计：按严重级别分布、受影响主机列表、Top CVE列表。

**文件完整性监控（FIM）**：

```xml
<syscheck>
  <disabled>no</disabled>
  <frequency>3600</frequency>
  <directories>/etc,/usr/bin,/usr/sbin,/bin,/sbin</directories>
  <directories>/var/www,/opt/app/config</directories>
  <ignore>/etc/mtab</ignore>
  <ignore>/etc/hostname</ignore>
  <nodiff>/etc/ssl/private</nodiff>
</syscheck>
```

FIM会记录被监控目录下文件的添加、修改、删除事件，并计算文件MD5/SHA256哈希。当关键系统文件被篡改时，立即触发告警——这是检测Webshell植入和后门持久化的有效手段。

### 9.5 告警配置与响应

**Active Response（主动响应）**：

Wazuh支持在规则触发后自动执行响应脚本：

```xml
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop.sh</executable>
  <expect>srcip</expect>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>100201</rules_id>
  <timeout>3600</timeout>
</active-response>
```

此配置在规则100201触发时，自动在本地防火墙添加对源IP的drop规则，持续1小时后自动解除。

**告警分级配置**：

Wazuh的rule level共16级（0-15）：
- Level 0：无告警
- Level 1-3：低危信息通知
- Level 4-7：中危需要关注
- Level 8-11：高危安全事件
- Level 12-15：严重安全事件

可在ossec.conf中配置按级别路由告警：
```xml
<alerts>
  <log_alert_level>5</log_alert_level>
  <email_alert_level>10</email_alert_level>
  <use_geoip>yes</use_geoip>
</alerts>
```

---

## 十、SOC建设实战案例

### 10.1 案例一：企业SOC从0到1建设

**背景**：某中型互联网企业（500人规模，服务器300台，日活用户50万），此前仅有兼职安全人员，无专业SOC。因合规要求和近期安全事件，决定从0到1建设SOC。

**建设阶段一：需求评估与规划（第1-2周）**

分析安全现状：
- 现有安全设备：边界防火墙、WAF、终端杀毒（无EDR）
- 日志现状：防火墙有日志但无人看，服务器几乎无日志收集
- 人员现状：2名兼职安全人员，无7×24监控能力
- 合规要求：等保2.0三级、数据安全法

确定建设目标：
- 建设SIEM平台实现全量日志集中
- 建立Tier 1/2两级运营体系（暂不做Tier 3）
- 覆盖核心系统（生产环境+办公环境）
- 7×12监控（工作时间+值班）→目标一年后7×24

**建设阶段二：平台搭建（第3-6周）**

选择Wazuh开源SIEM（预算有限）+ Elastic Stack（日志存储和可视化）。

部署方案：
- 1台Wazuh Server（16核/32GB/500GB SSD）
- 3台Elasticsearch集群节点（8核/16GB/2TB HDD/500GB SSD）
- 1台Kibana/Web界面
- 在所有300台服务器部署Wazuh Agent

日志接入范围：
- 服务器：Linux syslog + audit + Wazuh FIM
- 办公终端：Windows Event Log（特别是4624/4625/4688）+ Sysmon
- 网络：防火墙Syslog + WAF日志
- 云平台：阿里云ActionTrail + WAF日志

**建设阶段三：规则与流程建设（第7-10周）**

规则开发优先级：
1. 第一周（P0）：暴力破解检测、恶意IP通信检测、Web攻击检测、勒索软件行为检测
2. 第二周（P1）：横向移动检测、异常登录检测、权限提升检测
3. 第三周（P2）：数据外泄检测、内部威胁基线建立、UEBA初步配置
4. 第四周（P3）：规则调优、误报分析、白名单完善

流程文档编写：
- 事件响应SOP（标准操作流程）文档
- 告警分诊标准（什么是误报、什么升级到Tier 2）
- 值班交接流程
- 事件升级和通报流程

**建设阶段四：团队建设与运营（第11-14周）**

团队配置：
- 2名Tier 1分析师（白班+夜班轮岗）
- 1名Tier 2分析师（工作时间在岗）
- 1名SOC工程师（平台维护和规则开发）
- 与外部MSSP合作覆盖非工作时间（过渡方案）

运营首月重点：
- 每日告警量趋势观察（预期初期大量误报）
- 每周规则调优迭代
- 误报率从首周85%降至第四周30%
- 建立周报制度：告警数、真实事件数、MTTD/MTTR、覆盖资产数

**建设成果（3个月后）**：
- 日志覆盖率：核心系统90%+，全部系统75%+
- 告警准确率：65%+（持续提升中）
- MTTD：45分钟（目标30分钟）
- MTTR：6小时（目标4小时）
- 检测真实安全事件：月均8-15起
- 通过等保2.0三级测评中"集中审计"要求

### 10.2 案例二：利用SIEM检测APT攻击链

**背景**：某大型金融机构使用IBM QRadar SIEM，日处理日志量2TB。在一次威胁狩猎中，分析师通过SIEM关联分析发现并阻断了一起APT攻击。

**第一阶段发现：异常DNS查询**

QRadar UEBA生成异常评分：某内部服务器(DB-PROD-03)开始向一个此前从未出现过的外部域名发送DNS查询，频率为每5分钟一次。

分析师Tier 3初步调查：
- 在QRadar中搜索该服务器的DNS日志，确认异常查询始于3天前
- 将该域名提交威胁情报平台查询，命中一个已知APT组织的C2域名
- 判定：该服务器可能已被攻陷并建立了C2通信

**第二阶段关联：回溯入侵路径**

分析师利用QRadar的AQL（Admin Query Language）进行跨时间窗口关联搜索，回溯该服务器在过去30天内的事件时间线：

```
SELECT sourceip, destinationip, eventtime, devicetype, eventname
FROM events
WHERE sourceip='10.0.3.15' OR destinationip='10.0.3.15'
ORDER BY eventtime ASC
```

关联发现：
- 第25天前：该服务器收到来自某外部IP的端口扫描（被边界防火墙记录但未告警）
- 第24天前：该外部IP成功利用Web应用漏洞（WAF日志记录了异常POST请求）
- 第23天前：该服务器出现异常进程创建（Sysmon日志记录了powershell.exe执行编码命令）
- 第22天前：该服务器出现新增计划任务（Wazuh FIM检测到schtasks配置文件变更）
- 第20天前：开始出现C2 DNS查询

完整攻击链还原：侦察→漏洞利用→PowerShell执行→持久化(计划任务)→C2通信建立→（尚未进入数据外泄阶段）

**第三阶段响应：遏制与根除**

1. 立即隔离：通过EDR远程隔离DB-PROD-03的网络连接
2. 封禁C2：在边界防火墙和DNS服务器封禁C2域名和IP
3. 取证：通过EDR远程提取内存镜像、磁盘镜像
4. 根除：分析发现攻击者通过计划任务执行后门脚本，清除计划任务和后门文件
5. 加固：修复Web应用漏洞、加强WAF规则、启用PowerShell日志和约束语言模式

**第四阶段复盘与改进**

事件总结要点：
- **检测滞后分析**：C2通信在开始3天后才被发现，原因是UEBA基线学习期不足，C2域名首次出现时异常评分未达阈值
- **规则改进**：新增"C2域名首次出现即告警"规则，不依赖UEBA基线，依赖威胁情报实时比对
- **日志覆盖改进**：发现WAF日志虽记录了攻击请求但未触发告警，优化WAF检测规则
- **流程改进**：建立定期威胁狩猎机制（每周一次），不单纯依赖自动告警

### 10.3 案例三：内部威胁检测实战

**背景**：某高科技研发企业，核心资产为产品设计图纸和源代码。使用Splunk ES SIEM平台。安全部门接到HR部门通报：一名即将离职的资深工程师可能批量下载了设计文档。

**调查步骤一：数据收集与基线分析**

Splunk ES分析师调取该用户过去90天的文件访问日志（来自文件服务器审计日志和DLP系统）：

```splunk
index=fileaccess user=zhangsan
| timechart span=1d count by file_type
| where file_type="drawing" OR file_type="source_code"
```

基线分析结果：
- 该用户日均下载设计图纸：5-15份（正常研发工作范围）
- 过去90天日均下载量稳定，无异常波动

**调查步骤二：近期异常检测**

将分析窗口缩短到最近7天：

```splunk
index=fileaccess user=zhangsan earliest=-7d latest=now
| timechart span=1h count
| where count > 20
```

发现：
- 3天前该用户在非工作时间（凌晨2:00-4:00）一次性下载了287份设计图纸文件
- 下载行为涉及多个不属于其负责项目的产品线目录
- 下载后通过个人网盘外传了约2.3GB数据（DLP日志记录了外传行为，但因系统配置宽松未触发拦截）

**调查步骤三：UEBA风险评分叠加**

在Splunk UBA中查看该用户的风险评分变化：
- 30天前：风险评分0.2（正常）
- 7天前：风险评分0.4（轻度异常，非工作时间访问）
- 3天前：风险评分0.85（高危，多信号叠加）

风险信号分解：
- 非工作时间文件访问：+0.3
- 批量下载超出历史基线10倍：+0.4
- 访问非负责项目目录：+0.3
- 数据外传行为：+0.4
- 即将离职标记（HR系统集成）：+0.2

**调查步骤四：证据固定与处置**

1. 将Splunk调查结果导出为PDF报告作为证据
2. 冻结该用户所有系统访问权限
3. 对其工作电脑进行取证镜像
4. HR部门介入法律流程
5. 事后追溯该用户操作的历史，确认是否还有其他未发现的数据外泄

**事后改进**：
- 优化DLP策略：设计图纸类文件批量下载超过50份即触发拦截
- SIEM规则增强：新增"即将离职员工+异常数据访问"联合关联规则
- UEBA调优：将HR状态（离职流程中）作为UEBA的风险加权因子
- 访问控制加固：按项目维度实施更细粒度的文件目录访问控制

---

## 结语

SIEM与SOC安全运营是一个"平台+流程+人员"三位一体的系统工程。SIEM提供技术底座，SOC流程定义运营规范，安全分析师赋予组织实际的检测与响应能力。在构建安全运营体系时需要注意以下要点：

1. **平台是基础但非全部**：没有好的SIEM平台，分析师无法高效工作；但仅有平台而没有好的流程和人员，平台很快会沦为"日志坟场"。

2. **从覆盖到精准的渐进路径**：先确保日志覆盖率（广度），再提升检测规则质量（精度），最后引入UEBA和自动化（深度），逐步从Level 1成熟度迈向Level 5。

3. **威胁情报和自动化是加速器**：威胁情报让SIEM从"盲检测"转为"有针对性的检测"，SOAR自动化让分析师从"告警消防员"变为"威胁狩猎者"。

4. **持续调优是永恒主题**：安全运营没有"一劳永逸"，攻击手法在演进、业务在变化、人员在流动，SIEM规则和SOC流程必须持续迭代。

5. **度量驱动改进**：用MTTD、MTTR、告警准确率等KPI持续衡量SOC效能，用数据而非直觉驱动改进决策。

通过系统化地掌握SIEM架构设计、日志解析标准化、关联规则开发、UEBA行为分析、SOC运营流程和SOAR自动化编排，安全团队能够构建起从"看见威胁"到"快速响应"到"主动狩猎"的完整安全运营能力链。
