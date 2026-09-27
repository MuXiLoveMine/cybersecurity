# M6 蓝队与 SOC · 详细补充

> **模块编号**：M6
> **所属阶段**：阶段二 ~ 阶段三
> **建议学习时机**：第 9-16 个月（有一定攻防基础后）
> **前置知识**：M1（Python/Bash/PowerShell）+ M2（Linux/Windows/AD）+ M3（网络 / Wireshark）+ M4（Web 安全基础）
> **每日投入**：2 小时（其中实验环境实操 ≥ 1.5 小时）
> **信息时效**：2026 年 9 月版

---

## 1. 模块定位与前置知识

### 模块定位
蓝队（Blue Team）是企业安全防御的核心力量，SOC（Security Operations Center，安全运营中心）是蓝队的组织形态。红队攻得再漂亮，最终价值也要通过蓝队的检测和响应来体现。

本模块覆盖 **SOC 运营、入侵检测、威胁狩猎、应急响应、数字取证、威胁情报** 六大核心能力，带你从蓝队视角重新理解安全。

### 前置知识
- **必选前置**：M1~M4 全部内容（必须懂攻击才能做防御）
- **推荐先学**：M5（渗透测试与红队）的基础知识——不懂攻击怎么防？
- **环境要求**：需要搭建 SOC 实验环境（ELK + Wazuh + Sysmon 等）
- **思维转变**：从"怎么打进去"转变为"怎么发现、怎么响应、怎么防住"

### 蓝队能力分级

| 级别 | 能力描述 | 对应岗位 |
|------|---------|---------|
| **L1 入门** | 会用 SIEM 看告警、做基础告警研判、懂常见攻击特征 | SOC L1 分析师 |
| **L2 实用** | 能做事件调查、威胁狩猎、基础应急响应 | SOC L2 分析师 / 安全运营工程师 |
| **L3 熟练** | 能独立处理重大安全事件、高级威胁狩猎、规则优化 | 资深分析师 / 狩猎工程师 |
| **L4 精通** | SOC 架构设计、威胁情报体系、红蓝对抗防御、团队管理 | SOC 负责人 / 安全架构师 |

---

## 2. 知识图谱

```
蓝队与 SOC 知识体系
├── SOC 基础
│   ├── SOC 概念与组织架构
│   │   ├── 什么是 SOC（安全运营中心）
│   │   ├── SOC 人员配置（L1/L2/L3 分析师 / 狩猎 / 情报 / 响应）
│   │   ├── SOC 运营流程（告警 → 研判 → 响应 → 复盘）
│   │   └── SOC 成熟度模型
│   ├── 安全运营指标（KPI / SLA）
│   │   ├── MTTD（平均检测时间）
│   │   ├── MTTR（平均响应时间）
│   │   ├── MTTC（平均遏制时间）
│   │   ├── 告警误报率 / 告警处理量
│   │   └── 事件闭环率
│   └── 相关框架与标准
│       ├── NIST Cybersecurity Framework（识别 / 保护 / 检测 / 响应 / 恢复）
│       ├── NIST SP 800-61（计算机安全事件处理指南）
│       ├── MITRE ATT&CK（攻击者战术技术，蓝队也要懂）
│       ├── MITRE ENGAGE（防御方对抗框架）
│       └── FIRS 网络安全事件分类分级
│
├── 日志与监控
│   ├── 日志来源
│   │   ├── 网络设备日志（防火墙 / 交换机 / 路由器 / WAF / IDS）
│   │   ├── 操作系统日志（Windows Event / Linux Syslog）
│   │   ├── 应用日志（Web / 数据库 / 中间件）
│   │   ├── 安全产品日志（EDR / NDR / 邮件网关）
│   │   ├── 云平台日志（CloudTrail / Azure Activity / 操作审计）
│   │   └── DNS / DHCP / VPN / 认证日志
│   ├── 日志采集架构
│   │   ├── Agent 采集 vs Agentless 采集
│   │   ├── Syslog / SNMP / WMI / WinRM / API
│   │   ├── 日志转发（Logstash / Fluentd / Filebeat / NXLog）
│   │   └── 日志标准化（CEF / JSON / ECS）
│   ├── Windows 日志深度
│   │   ├── 事件 ID 体系（安全 / 系统 / 应用 / 安全审计）
│   │   ├── 登录事件（4624 成功 / 4625 失败 / 登录类型）
│   │   ├── 账户管理（4720 创建用户 / 4728 加组等）
│   │   ├── 进程创建（4688）/ 网络连接（5156）
│   │   ├── 对象访问 / 策略变更 / 系统事件
│   │   └── 常见攻击事件 ID 速查
│   ├── Sysmon 系统监控
│   │   ├── Sysmon 介绍与安装
│   │   ├── Sysmon 事件 ID（进程创建 / 网络连接 / 文件创建 / 注册表等）
│   │   ├── Sysmon 配置文件（SwiftOnSecurity / Olaf Hartong）
│   │   ├── Sysmon 检测规则编写
│   │   └── Sysmon + Windows Event Log 组合检测
│   ├── Linux 日志深度
│   │   ├── Syslog / rsyslog / journald
│   │   ├── auth.log / secure（认证日志）
│   │   ├── /var/log 下各日志文件详解
│   │   ├── auditd / auditctl（审计框架）
│   │   ├── 进程审计 / 文件审计 / 网络审计
│   │   └── 常见攻击日志特征
│   └── SIEM 平台
│       ├── Splunk（企业级标准）
│       │   ├── SPL 搜索处理语言（核心！）
│       │   ├── 数据输入与解析
│       │   ├── 字段提取与正则
│       │   ├── 统计与可视化
│       │   ├── 告警与报告
│       │   ├── Dashboard 仪表盘
│       │   └── Splunk ES（企业安全套件）
│       ├── ELK Stack（Elastic + Logstash + Kibana）
│       │   ├── Elasticsearch 基础（索引 / 查询 / 聚合）
│       │   ├── Logstash 数据处理（input / filter / output）
│       │   ├── Kibana 可视化（Discover / Visualize / Dashboard）
│       │   ├── Beats 轻量采集器（Filebeat / Metricbeat / Winlogbeat）
│       │   └── Elastic Security（安全检测引擎）
│       └── 其他 SIEM
│           ├── Wazuh（开源 XDR / HIDS）
│           ├── QRadar（IBM 企业级）
│           ├── 安恒 / 奇安信 / 深信服 / 绿盟（国内厂商）
│           └── Sentinel（微软云 SIEM）
│
├── 入侵检测与威胁狩猎
│   ├── IDS / IPS 基础
│   │   ├── NIDS（网络入侵检测）vs HIDS（主机入侵检测）
│   │   ├── 基于特征 vs 基于异常 vs 基于行为
│   │   ├── Suricata / Snort（开源 NIDS）
│   │   ├── Suricata 规则编写
│   │   └── EDR / NDR / XDR 概念
│   ├── 检测规则编写
│   │   ├── Sigma 规则（通用检测规则标准）⭐⭐⭐ 重点
│   │   ├── Splunk 检测规则（SPL）
│   │   ├── Elastic Security 检测规则
│   │   ├── Suricata / Snort 规则
│   │   ├── YARA 规则（恶意代码特征）
│   │   └── 规则优化与误报治理
│   ├── 威胁狩猎（Threat Hunting）
│   │   ├── 威胁狩猎方法论
│   │   │   ├── 假设驱动狩猎（Hypothesis-Driven）
│   │   │   ├── 数据驱动狩猎（Data-Driven）
│   │   │   └── 情报驱动狩猎（Intelligence-Driven）
│   │   ├── 狩猎循环（假说 → 调查 → 发现 → 加固 → 新假说）
│   │   ├── 狩猎成熟度模型
│   │   └── ATT&CK 映射与覆盖度评估
│   ├── 常见攻击检测
│   │   ├── 侦察与扫描检测（端口扫描 / 目录爆破 / 子域名枚举）
│   │   ├── Web 攻击检测（SQL 注入 / XSS / 上传 / 命令执行）
│   │   ├── 暴力破解检测（SSH / RDP / Web 登录）
│   │   ├── 横向移动检测（PsExec / WMI / WinRM / SMB / PtH）
│   │   ├── 权限提升检测
│   │   ├── 凭据窃取检测（Mimikatz / LSASS 访问）
│   │   ├── 权限维持检测（注册表 / 服务 / 计划任务 / 票据）
│   │   ├── 勒索软件检测
│   │   ├── C2 通信检测（异常流量 / DNS 隧道 / 加密流量特征）
│   │   └── 数据外泄检测（DLP / 异常外发流量）
│   └── 威胁狩猎工具
│       ├── Splunk / ELK（日志分析）
│       ├── Velociraptor（端点调查与取证）
│       ├── Kibana / Grafana（可视化与监控）
│       ├── Jupyter Notebook（数据分析与狩猎笔记本）
│       ├── Zeek（网络流量分析）
│       ├── BloodHound（蓝队视角：发现高危攻击路径）
│       └── Atomic Red Team（攻击模拟，验证检测能力）
│
├── 应急响应（Incident Response）
│   ├── 应急响应方法论
│   │   ├── NIST SP 800-61 四阶段：
│   │   │   1. 准备阶段（Preparation）
│   │   │   2. 检测与分析（Detection & Analysis）
│   │   │   3. 遏制、根除与恢复（Containment, Eradication & Recovery）
│   │   │   4. 事后活动（Post-Incident Activity）
│   │   ├── 事件分级（一般 / 较大 / 重大 / 特别重大）
│   │   ├── 应急响应团队（IRT）角色与职责
│   │   └── 应急预案与演练
│   ├── 事件调查
│   │   ├── 告警研判流程（Triage）
│   │   ├── 调查方法论（5W1H / 时间线重建）
│   │   ├── 证据收集与保全（链存证）
│   │   ├── 攻击链重建（Cyber Kill Chain / ATT&CK）
│   │   └── Root Cause Analysis（根因分析）
│   ├── 常见安全事件响应
│   │   ├── Web 入侵事件响应
│   │   ├── 勒索软件事件响应
│   │   ├── 钓鱼邮件事件响应
│   │   ├── 数据泄露事件响应
│   │   ├── 内网横向移动事件响应
│   │   ├── DDoS 攻击事件响应
│   │   └── 账户被盗 / 凭据泄露事件响应
│   ├── 遏制与恢复
│   │   ├── 网络遏制（断网 / 隔离 / 封 IP）
│   │   ├── 主机遏制（关机 / 断网 / 禁用账户）
│   │   ├── 根除恶意代码 / 后门 / 持久化
│   │   ├── 密码重置 / 凭据轮换
│   │   ├── 系统加固与补丁
│   │   └── 业务恢复与验证
│   └── 应急响应工具
│       ├── 终端响应：Velociraptor / Kape / CrowdResponse
│       ├── 取证工具：FTK / EnCase / Autopsy / X-Ways
│       ├── 内存取证：Volatility 3 / Redline
│       ├── 恶意代码分析：Cuckoo Sandbox / ANY.RUN
│       └── 事件管理：TheHive / Cortex / MISP
│
├── 数字取证（Digital Forensics）
│   ├── 取证基础
│   │   ├── 数字取证原则（合法性 / 完整性 / 可重复性）
│   │   ├── 证据链（Chain of Custody）
│   │   ├── 取证镜像（dd / E01 / AFF4）
│   │   └── 写保护与只读挂载
│   ├── Windows 取证
│   │   ├── 文件系统取证（NTFS / MFT / $USN 日志）
│   │   ├── 注册表取证（用户操作 / 安装程序 / 最近访问）
│   │   ├── Prefetch / Amcache / Shimcache
│   │   ├── Jump List / LNK 文件 / 回收站
│   │   ├── 事件日志取证
│   │   ├── 浏览器取证（历史 / Cookie / 缓存 / 下载）
│   │   ├── 邮件取证（Outlook / 网页邮件）
│   │   └── USB 设备使用痕迹
│   ├── Linux 取证
│   │   ├── 文件系统取证（Ext4 / XFS）
│   │   ├── 日志取证
│   │   ├── 进程与内存取证
│   │   ├── Bash 历史 / 命令审计
│   │   └── SSH 日志 / 登录记录
│   ├── 内存取证
│   │   ├── 内存镜像获取
│   │   ├── Volatility 3 框架
│   │   ├── 进程分析 / 网络连接 / 加载模块
│   │   ├── 恶意代码检测
│   │   └── 凭据提取
│   ├── 网络取证
│   │   ├── 流量捕获与分析（Wireshark / Tshark）
│   │   ├── PCAP 取证
│   │   ├── 网络会话重建
│   │   ├── 文件提取（HTTP / FTP / SMTP）
│   │   └── 隧道 / 隐蔽通道检测
│   └── 取证工具
│       ├── Autopsy / Sleuth Kit（开源取证平台）
│       ├── Volatility 3（内存取证）
│       ├── FTK Imager（镜像与查看）
│       ├── Wireshark / Tshark（流量分析）
│       ├── Eric Zimmerman 工具集（Windows 取证）
│       ├── KAPE（快速取证收集）
│       └── Velociraptor（大规模端点取证）
│
├── 威胁情报（Threat Intelligence）
│   ├── 威胁情报基础
│   │   ├── 什么是威胁情报
│   │   ├── 情报类型：战略 / 运营 / 战术 / 技术
│   │   ├── IOC（指标）/ TTP（战术技术过程）
│   │   ├── 情报生命周期（规划 → 收集 → 处理 → 分析 → 分发 → 反馈）
│   │   └── ATT&CK 与威胁情报
│   ├── 威胁情报来源
│   │   ├── 开源情报（OSINT）
│   │   ├── 商业情报（厂商威胁情报 feed）
│   │   ├── 行业共享（ISAC / 行业协会）
│   │   ├── 政府 / CERT
│   │   └── 内部情报（自己的事件数据）
│   ├── IOC 与 TTP
│   │   ├── IOC 类型：IP / 域名 / URL / Hash / 证书 / 文件
│   │   ├── STIX / TAXII 标准
│   │   ├── OpenIOC
│   │   └── TTP 描述（ATT&CK 映射）
│   ├── 威胁情报平台（TIP）
│   │   ├── MISP（开源威胁情报平台）⭐⭐⭐ 重点
│   │   ├── OpenCTI
│   │   ├── ThreatConnect
│   │   └── 商业 TIP
│   └── 威胁情报应用
│       ├── SIEM 关联检测
│       ├── 威胁狩猎
│       ├── 防火墙 / WAF 拦截
│       ├── 漏洞管理优先级
│       └── 风险评估与决策支持
│
├── 端点检测与响应（EDR / XDR）
│   ├── EDR 工作原理
│   │   ├── 行为检测 vs 特征检测
│   │   ├── 机器学习与异常检测
│   │   ├── 遥测数据采集
│   │   └── 检测与响应能力
│   ├── 常见 EDR 产品
│   │   ├── CrowdStrike Falcon
│   │   ├── SentinelOne
│   │   ├── Microsoft Defender for Endpoint
│   │   ├── 火绒 / 360 / 奇安信 / 安恒（国内）
│   │   └── Wazuh（开源 HIDS / XDR）
│   ├── EDR 检测与响应操作
│   │   ├── 告警调查
│   │   ├── 进程树分析
│   │   ├── 网络连接分析
│   │   ├── 文件 / 注册表 / 计划任务分析
│   │   ├── 隔离主机 / 查杀恶意文件
│   │   └── 远程响应
│   └── EDR 绕过与对抗（蓝队也要懂）
│       ├── EDR 检测原理
│       ├── 用户态钩子绕过
│       ├── 直接系统调用（Syscall）
│       ├── 未映射代码执行
│       └── 行为混淆
│
└── 蓝队工具链汇总
    ├── SIEM：Splunk / ELK / Wazuh / QRadar
    ├── 日志采集：Filebeat / Winlogbeat / NXLog / Fluentd
    ├── 端点监控：Sysmon / Wazuh agent / auditd
    ├── 网络监控：Suricata / Zeek / Wireshark
    ├── 端点响应：Velociraptor / KAPE
    ├── 取证：Autopsy / Volatility 3 / FTK Imager
    ├── 威胁情报：MISP / OpenCTI / STIX
    ├── 事件管理：TheHive / Cortex / RTIR
    ├── 攻击模拟：Atomic Red Team / Caldera
    ├── 检测规则：Sigma / YARA / Suricata
    └── 可视化：Grafana / Kibana / Splunk Dashboard
```

---

## 3. 学习顺序与时间表

### 总时长：约 7 个月（420 小时）

| 阶段 | 周次 | 学习内容 | 重点任务 | 实验目标 |
|------|------|---------|---------|---------|
| **SOC 基础** | 第 1-3 周 | SOC 概念 + 日志基础 | SOC 运营流程、Windows/Linux 日志体系 | 看懂常见 Event ID |
| | 第 4-6 周 | Sysmon + Windows 日志深度 | Sysmon 安装配置、事件 ID、攻击日志特征 | 部署 Sysmon + 配置规则 |
| | 第 7-9 周 | ELK Stack 入门 | Elasticsearch + Logstash + Kibana + Beats | 搭建 ELK 环境，接入日志 |
| **入侵检测** | 第 10-13 周 | Splunk / SPL 深入 | SPL 语法、搜索、统计、告警、仪表盘 | Splunk 本地实验环境 |
| | 第 14-17 周 | 检测规则 + 威胁狩猎 | Sigma 规则、ATT&CK 映射、狩猎方法论 | 写 20+ 条检测规则 |
| | 第 18-20 周 | 网络监控 + Suricata | Suricata 安装、规则编写、流量检测 | 部署 Suricata + 写规则 |
| **应急响应** | 第 21-24 周 | 应急响应方法论 + 实战 | NIST IR、常见事件响应流程、调查方法 | 完成 5+ 个应急案例 |
| | 第 25-27 周 | 数字取证 | Windows/Linux 取证、内存取证、网络取证 | Autopsy + Volatility 实战 |
| **威胁情报** | 第 28-30 周 | 威胁情报 + MISP | 情报体系、MISP 部署与使用、IOC 应用 | 搭建 MISP + 情报运营 |
| **综合实战** | 第 31-32 周 | SOC 综合演练 + 红蓝对抗 | 完整 SOC 运营模拟、检测 + 响应 + 报告 | 一次完整红蓝对抗演练 |

---

## 4. 工具链与版本建议

### 4.1 SIEM 平台

| 工具 | 版本建议 | 用途 | 优先级 | 费用 |
|------|---------|------|--------|------|
| **ELK Stack** | 8.x 最新版 | 开源 SIEM，学习首选 | ⭐⭐⭐ 必学 | 免费 |
| **Splunk Enterprise** | 9.x | 企业级 SIEM 行业标准 | ⭐⭐⭐ 必学 | 免费版 500MB/天（学习够用） |
| **Wazuh** | 4.x 最新版 | 开源 XDR / HIDS | ⭐⭐⭐ 必学 | 免费 |
| **Splunk Enterprise Security (ES)** | 最新版 | Splunk 安全套件 | ⭐⭐ 推荐 | 付费（贵） |
| **Elastic Security** | 随 ELK | Elastic 安全检测引擎 | ⭐⭐ 推荐 | 免费 + 付费 |

### 4.2 日志采集与监控

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **Sysmon** | Windows 系统监控增强 | ⭐⭐⭐ 必用 |
| **auditd / auditctl** | Linux 审计框架 | ⭐⭐⭐ 必用 |
| **Filebeat** | 轻量日志采集（ELK 生态） | ⭐⭐⭐ 必用 |
| **Winlogbeat** | Windows 事件日志采集 | ⭐⭐⭐ 必用 |
| **NXLog** | 跨平台日志转发 | ⭐⭐ 重要 |
| **Fluentd / Fluent Bit** | 云原生日志采集 | ⭐⭐ 重要 |
| **rsyslog / syslog-ng** | Linux Syslog 服务 | ⭐⭐⭐ 必用 |
| **Zeek (Bro)** | 网络流量分析 | ⭐⭐ 重要 |
| **Suricata** | 开源 IDS/IPS | ⭐⭐⭐ 必学 |

### 4.3 应急响应与取证

| 工具 | 用途 | 优先级 | 平台 |
|------|------|--------|------|
| **Velociraptor** | 端点取证与响应（神器） | ⭐⭐⭐ 必学 | 跨平台 |
| **Autopsy / Sleuth Kit** | 数字取证平台 | ⭐⭐⭐ 必学 | 跨平台 |
| **Volatility 3** | 内存取证框架 | ⭐⭐⭐ 必学 | 跨平台 |
| **FTK Imager** | 取证镜像创建与查看 | ⭐⭐ 重要 | Windows |
| **KAPE** | 快速取证收集器 | ⭐⭐ 重要 | Windows |
| **Wireshark / Tshark** | 网络取证与流量分析 | ⭐⭐⭐ 必用 | 跨平台 |
| **TheHive** | 安全事件响应平台 | ⭐⭐ 推荐 | 跨平台 |
| **Cortex** | TheHive 分析引擎 | ⭐⭐ 推荐 | 跨平台 |
| **MISP** | 威胁情报平台 | ⭐⭐⭐ 必学 | Linux |
| **Cuckoo Sandbox** | 恶意代码沙箱 | ⭐⭐ 重要 | Linux |
| **Eric Zimmerman Tools** | Windows 取证工具集 | ⭐⭐ 重要 | Windows |
| **Redline** | FireEye 内存取证工具 | ⭐⭐ 重要 | Windows |

### 4.4 检测与狩猎

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **Sigma** | 通用检测规则标准 | ⭐⭐⭐ 必学 |
| **YARA** | 恶意代码特征匹配 | ⭐⭐⭐ 必学 |
| **Atomic Red Team** | ATT&CK 攻击模拟框架 | ⭐⭐⭐ 必学 |
| **MITRE CALDERA** | 自动化红蓝对抗平台 | ⭐⭐ 推荐 |
| **BloodHound**（蓝队视角） | AD 攻击路径分析与加固 | ⭐⭐⭐ 必用 |
| **Jupyter Notebook** | 威胁狩猎数据分析 | ⭐⭐ 重要 |
| **HELK** | 狩猎 ELK 套件（含检测规则） | ⭐⭐ 推荐 |
| **DetectionLab** | 蓝队实验环境一键搭建 | ⭐⭐⭐ 强烈推荐 |
| **Threat Hunter Playbook** | 威胁狩猎 Playbook | ⭐⭐ 推荐 |

### 4.5 实验环境推荐

**DetectionLab**（强烈推荐！）
- 一键搭建完整的蓝队实验环境
- 包含：Windows 域控 + Windows 10 + Splunk + Wazuh + Velociraptor + Atomic Red Team
- 支持 VMware / VirtualBox / AWS / Azure
- GitHub 搜索 "DetectionLab"

---

## 5. 编程 / 脚本练习

### 5.1 Python 蓝队工具

```python
# 练习 1：日志分析脚本
# - 分析 Nginx / Apache 日志，统计攻击特征
# - 检测 SQL 注入 / XSS / 扫描行为
# - 输出攻击 IP 黑名单

# 练习 2：Windows 事件日志分析脚本（python-evtx）
# - 解析 .evtx 日志文件
# - 统计登录失败次数，找出爆破 IP
# - 检测异常进程创建事件

# 练习 3：Sigma 规则管理工具
# - 从 GitHub 拉取 Sigma 规则库
# - 规则分类 / 搜索
# - 转换为 Splunk / ELK 查询语句（sigmac）

# 练习 4：IOC 扫描器
# - 读取 IOC 列表（IP / 域名 / Hash）
# - 在日志中批量匹配
# - 输出匹配结果

# 练习 5：简单的 SIEM 告警引擎
# - 定时查询日志
# - 匹配检测规则
# - 触发告警（邮件 / 钉钉 / 企业微信）

# 练习 6：Volatility 自动化脚本
# - 批量分析内存镜像
# - 自动提取进程 / 网络 / 模块信息
# - 生成内存分析报告

# 练习 7：MISP API 自动化
# - 自动导入 IOC
# - 事件创建与关联
# - 情报导出到防火墙 / SIEM
```

### 5.2 Splunk SPL 练习

```spl
# 练习 1：统计登录失败次数 Top 10 的 IP
index=security EventCode=4625
| stats count by src_ip
| sort - count
| head 10

# 练习 2：检测短时间内多次登录失败（暴力破解）
index=security EventCode=4625
| bin _time span=5m
| stats count by src_ip, _time
| where count > 10
| sort - count

# 练习 3：检测 Mimikatz 典型行为（lsass.exe 访问）
index=sysmon EventCode=10
| where TargetImage="C:\\Windows\\System32\\lsass.exe"
  AND NOT (SourceImage IN ("C:\\Windows\\System32\\svchost.exe", ...))
| stats count by SourceImage, TargetImage, Computer

# 练习 4：检测新创建的服务（权限维持）
index=security EventCode=7045
| table _time, ComputerName, ServiceName, ServiceFileName, StartType
| sort - _time

# 练习 5：网络连接异常检测（罕见外联 IP）
index=sysmon EventCode=3
| stats count by DestinationIp
| sort count
| head 20

# 练习 6：注册表 Run 键修改检测
# 练习 7：PowerShell 可疑执行检测（EncodedCommand / Base64）
# 练习 8：横向移动检测（PsExec / WMI / WinRM 事件）
# 练习 9：仪表盘设计（安全态势总览）
# 练习 10：告警配置与降噪
```

### 5.3 PowerShell 蓝队脚本

```powershell
# 练习 1：系统信息收集脚本（应急响应快速收集）
# - 系统信息 / 网络连接 / 进程列表 / 服务 / 驱动
# - 计划任务 / 启动项 / 注册表自启动
# - 用户 / 组 / 登录会话
# - 最近修改的文件
# - 输出到 HTML 报告

# 练习 2：日志快速分析脚本
# - 获取最近 24 小时的安全事件
# - 统计登录成功 / 失败
# - 检测异常事件

# 练习 3：恶意代码初筛脚本
# - 扫描启动项 / 服务 / 计划任务
# - 检查数字签名
# - 提交 Hash 到 VirusTotal 查询

# 练习 4：Velociraptor 自定义 VQL 收集器
# （Velociraptor 使用 VQL 查询语言）
```

---

## 6. 靶场与实验环境

### 6.1 蓝队在线靶场

| 平台 | 特点 | 费用 | 适合阶段 |
|------|------|------|---------|
| **LetsDefend** | 蓝队 / SOC 实战平台，模拟真实 SOC 工作 | 免费 + 付费 | 入门到进阶 |
| **CyberDefenders** | 蓝队 CTF 与取证挑战，分类详细 | 免费 + 付费 | 入门到进阶 |
| **Blue Team Labs Online** | 蓝队专项实验室，含 SOC / 取证 / 威胁狩猎 | 付费 | 进阶 |
| **TryHackMe** | 蓝队 / SOC 路径房间 | 免费 + 付费 | 入门 |
| **HackTheBox** | 有蓝队相关赛道和挑战 | 免费 + 付费 | 进阶 |
| **Security Blue Team** | 蓝队认证与训练平台 | 付费 | 进阶 |
| **RangeForce** | 安全技能训练平台（含蓝队） | 付费 | 进阶 |
| **eLearnSecurity / INE** | eJPT / eCIR / eCDSA 等蓝队认证课程 | 付费 | 进阶 |

### 6.2 本地实验环境

#### 环境一：ELK + Sysmon 基础监控环境
```
  Linux 服务器（监控中心）
    ├── Elasticsearch
    ├── Logstash
    ├── Kibana
    └── Filebeat（自身日志）

  Windows 客户端（被监控）
    ├── Windows 10 / 11
    ├── Sysmon（SwiftOnSecurity 配置）
    └── Winlogbeat（转发到 Logstash）

  练习内容：
    - 日志接入与解析
    - 仪表盘制作
    - 检测规则编写
    - 攻击模拟 + 检测验证
```

#### 环境二：完整 SOC 实验环境（推荐 DetectionLab）
```
  1. DC (Windows Server 2022) - 域控制器
  2. WEF (Windows Server) - Windows Event Forwarding
  3. WIN10 (Windows 10) - 工作站
  4. Logger (Ubuntu) - Splunk + Wazuh + Velociraptor

  预装：
    - Sysmon + 优化配置
    - Atomic Red Team（攻击模拟）
    - Splunk 企业版（试用）
    - Wazuh 管理端 + Agent
    - Velociraptor 服务端 + 客户端
    - Caldera（红蓝对抗自动化）

  练习内容：
    - 全场景蓝队实战
    - 检测规则开发与验证
    - 威胁狩猎
    - 应急响应
```

#### 环境三：Suricata 网络监控环境
```
  攻击机 (Kali) ──┐
                   ├─── 交换机（端口镜像）─── Suricata 监控机
  靶机 (Web/Win) ──┘

  练习内容：
    - Suricata 安装与配置
    - Emerging Threats 规则集
    - 自定义规则编写
    - 攻击流量检测
    - 规则调优与误报治理
```

### 6.3 取证练习资源

| 资源 | 类型 | 用途 |
|------|------|------|
| **Digital Forensics Case Files** | 取证案例 | 真实案例练习 |
| **CFReDS** | 取证数据集 | 印度 CERT 提供 |
| **Forensics Wiki** | Wiki | 取证知识百科 |
| **CyberDefenders Forensics** | 在线挑战 | 取证类 CTF |
| **Root-Me Forensics** | 在线挑战 | 取证挑战 |
| **Volatility 样本库** | 内存镜像 | 内存取证练习 |

---

## 7. 推荐资料

### 📚 书籍

| 书名 | 难度 | 备注 |
|------|------|------|
| **《蓝队实战指南》** | ⭐⭐ 入门 | 蓝队基础入门 |
| **《安全运营与智能分析》** | ⭐⭐⭐ 进阶 | SOC 与安全分析 |
| **《应急响应：数字取证与事件响应》** | ⭐⭐⭐ 进阶 | 应急响应经典 |
| **《Windows 取证分析》**第 3 版 | ⭐⭐⭐ 进阶 | Windows 取证权威 |
| **《数字取证与调查指南》** | ⭐⭐ 入门 | 取证基础 |
| **《威胁情报：数据驱动的信息安全运营》** | ⭐⭐ 入门 | 威胁情报入门 |
| **《入侵检测与响应》** | ⭐⭐⭐ 进阶 | IDS/IPS 深入 |
| **《The Practice of Network Security Monitoring》** | ⭐⭐⭐ 进阶 | 网络监控实战，英文 |
| **《The Hacker Playbook 3》** | ⭐⭐⭐ 攻防 | 红蓝对抗视角，英文 |
| **《Blue Team Handbook》** | ⭐⭐⭐ 手册 | 蓝队速查手册 |

### 🌐 在线资源

| 资源 | 关键词 | 特点 |
|------|--------|------|
| **MITRE ATT&CK** | attack.mitre.org | ATT&CK 矩阵，必学 |
| **Sigma Rules** | github.com/SigmaHQ/sigma | 通用检测规则库 |
| **Atomic Red Team** | github.com/redcanaryco/atomic-red-team | ATT&CK 攻击模拟 |
| **MITRE Cyber Analytics Repository** | car.mitre.edu | 检测分析知识库 |
| **DetectionLab** | github.com/clong/DetectionLab | 蓝队实验环境一键搭建 |
| **HackTricks - Blue Team** | book.hacktricks.xyz/generic-methodologies-and-resources | 蓝队技巧 |
| **Elastic Security Docs** | elastic.co/security | ELK 安全文档 |
| **Splunk Security Content** | github.com/splunk/security_content | Splunk 检测内容库 |
| **MISP Project** | misp-project.org | 威胁情报平台官方 |
| **TheHive Project** | thehive-project.org | 事件响应平台 |
| **Velociraptor Docs** | docs.velocidex.com | Velociraptor 官方文档 |

### 🎥 视频与创作者

| 创作者 / 课程 | 平台 | 特点 |
|-------------|------|------|
| **John Hammond** | YouTube | 蓝队 / 取证 / CTF 教学 |
| **13Cubed** | YouTube | 数字取证与事件响应 |
| **DFIR Diva** | YouTube | 取证与威胁狩猎 |
| **Eric Conrad** | YouTube / Pluralsight | CISSP / 安全概念 |
| **TryHackMe SOC Level 1** | TryHackMe | SOC 入门路径 |
| **LetsDefend 教程** | YouTube / B 站 | 蓝队平台使用教程 |
| **国内：安全运营 / SOC 系列** | B 站 | 中文 SOC 入门课程 |
| **奇安信 / 安恒 公开课** | B 站 | 厂商安全运营分享 |

### 📝 社区与博客

| 平台 | 用途 |
|------|------|
| **FreeBuf / 先知社区** | 国内蓝队 / 安全运营文章 |
| **安全客** | 360 安全团队，有蓝队专栏 |
| **Reddit r/blueteamsec / r/netsec** | 国际蓝队社区 |
| **Medium - Blue Team / DFIR** | 英文蓝队文章 |
| **SANS DFIR Blog** | SANS 取证博客 |
| **FireEye / Mandiant Blog** | 顶级安全厂商博客，威胁情报 |
| **CrowdStrike Blog** | EDR 厂商博客，攻击分析 |

---

## 8. 实战项目

### 项目一：搭建企业级 SOC 监控环境

**目标**：从零搭建一个完整的蓝队实验环境，包含 SIEM、端点监控、网络监控。

**任务清单**：
1. **环境规划**
   - 设计网络拓扑（攻击区 / 服务区 / 办公区 / 监控区）
   - 确定需要监控的日志源
2. **SIEM 部署（ELK + Splunk 各搭一个）**
   - Elasticsearch 集群（单节点先）
   - Logstash 数据处理管道
   - Kibana 仪表盘
   - Splunk 企业版（免费授权）
3. **端点监控部署**
   - Windows 端：Sysmon + Winlogbeat + Wazuh agent
   - Linux 端：auditd + Filebeat + Wazuh agent
   - 日志标准化与字段映射（ECS 标准）
4. **网络监控部署**
   - Suricata IDS 部署
   - Emerging Threats 规则集导入
   - 流量镜像配置
5. **威胁情报集成**
   - MISP 部署
   - 开源情报 feed 接入
   - IOC 同步到 SIEM
6. **验证测试**
   - 用 Atomic Red Team 模拟攻击
   - 验证检测覆盖率
   - 调优规则，降低误报
7. **输出部署文档与运维手册**

**预计耗时**：40 小时
**产出物**：运行中的 SOC 环境 + 部署手册 + 运维手册

---

### 项目二：检测规则开发与威胁狩猎

**目标**：基于 ATT&CK 框架，开发一套检测规则，并进行威胁狩猎实战。

**任务清单**：
1. **ATT&CK 覆盖度评估**
   - 选取 20 个常见 ATT&CK 技术
   - 评估当前检测能力覆盖度
   - 找出检测盲区
2. **Sigma 规则开发**
   - 为每个盲区编写 Sigma 规则（至少 20 条）
   - 覆盖：初始访问 / 执行 / 持久化 / 提权 / 凭据访问 / 横向移动
   - 每条规则包含：描述 / 检测逻辑 / 误报处理 / 参考
3. **规则转换与部署**
   - 用 sigmac 转换为 Splunk / ELK 查询
   - 部署到 SIEM
   - 调优误报
4. **威胁狩猎实战**
   - 基于假说的狩猎（5 个狩猎假说）
   - 基于数据的狩猎（异常分析）
   - 基于情报的狩猎（IOC 匹配）
5. **用 Atomic Red Team 验证检测效果**
   - 执行攻击模拟
   - 检查是否触发告警
   - 记录检测延迟、误报、漏报
6. **输出检测规则库 + 狩猎报告**

**预计耗时**：35 小时
**产出物**：Sigma 规则集（20+ 条）+ 威胁狩猎报告 + ATT&CK 覆盖度矩阵

---

### 项目三：应急响应实战演练

**目标**：模拟一次真实的安全事件，完成从检测到响应到恢复的全流程。

**场景一：Web 服务器被入侵**
- 现象：Web 页面被篡改，发现 WebShell
- 任务：
  1. 遏制：隔离服务器，阻断攻击 IP
  2. 调查：WebShell 分析、日志溯源、入侵路径重建
  3. 根除：清除 WebShell、修复漏洞、清理后门
  4. 恢复：恢复业务、加固系统
  5. 报告：输出完整应急响应报告

**场景二：勒索软件事件**
- 现象：多台服务器文件被加密，留下勒索信
- 任务：
  1. 遏制：断网隔离，防止扩散
  2. 调查：感染源分析、传播路径、时间线重建
  3. 根除：清除恶意程序、封堵 C2
  4. 恢复：从备份恢复、加固、全面扫描
  5. 报告：勒索软件事件分析报告

**场景三：钓鱼邮件 + 凭据泄露**
- 现象：员工点击钓鱼链接，账户被盗，出现异常登录
- 任务：
  1. 遏制：禁用被盗账户、重置密码
  2. 调查：钓鱼邮件分析、攻击者行为分析
  3. 根除：清理恶意宏 / 后门
  4. 恢复：账户恢复、数据核查
  5. 报告：钓鱼事件响应报告

**要求**：
- 每个场景都输出标准格式的应急响应报告
- 包含时间线、攻击链、影响范围、处置过程、改进建议
- 用 ATT&CK 映射攻击行为

**预计耗时**：30 小时（每个场景 10 小时）
**产出物**：3 份应急响应报告 + 事件复盘总结

---

### 项目四：数字取证综合实战

**目标**：对一个"被入侵的系统"进行全面取证分析，还原攻击过程。

**任务清单**：
1. **镜像获取与验证**
   - 获取磁盘镜像 + 内存镜像
   - 计算 Hash，验证完整性
   - 建立证据链
2. **磁盘取证（Windows 系统）**
   - 文件系统分析（已删除文件恢复）
   - 注册表分析（用户行为 / 自启动 / 最近访问）
   - Prefetch / Amcache / Shimcache 分析
   - Jump List / LNK / 回收站分析
   - 浏览器历史 / Cookie / 下载记录
   - 事件日志分析
   - USB 设备使用痕迹
3. **内存取证**
   - 用 Volatility 3 分析内存镜像
   - 进程分析（找出恶意进程）
   - 网络连接分析
   - 加载的 DLL / 驱动
   - 凭据提取
   - 恶意代码检测
4. **网络取证**
   - 分析流量 PCAP
   - 重建攻击会话
   - 提取传输的文件
   - C2 通信分析
5. **攻击时间线重建**
   - 整合所有证据
   - 构建完整攻击时间线
   - 绘制攻击链图
6. **输出取证报告**

**预计耗时**：25 小时
**产出物**：数字取证报告 + 时间线 + 证据链清单

---

## 9. 常见误区

### ❌ 误区 1：蓝队就是"看告警的"，技术含量低
**现象**：觉得蓝队就是盯着屏幕等告警，没有红队有技术含量。
**纠正**：蓝队的技术深度一点不比红队浅。优秀的蓝队分析师要懂攻击、懂系统、懂网络、懂取证、懂情报，还要有极强的分析推理能力。高级威胁狩猎和逆向分析的技术门槛非常高。

### ❌ 误区 2：只会用工具，不懂原理
**现象**：会点 SIEM 的查询按钮，但写不出复杂的 SPL / DSL 查询，也不懂检测原理。
**纠正**：蓝队的核心能力是分析和推理。工具只是辅助，你得知道"查什么、为什么查、查出来说明了什么"。深入理解日志格式、攻击特征、检测逻辑。

### ❌ 误区 3：只学防御，不懂攻击
**现象**：只学 SIEM 操作、应急响应流程，完全不懂攻击技术。
**纠正**："知道攻击怎么发生的，才能知道怎么检测和防御"。蓝队必须懂红队的技术，甚至比红队懂得还多（要知道各种攻击变体和绕过手法）。建议先学红队基础再转蓝队，或者红蓝同步学。

### ❌ 误区 4：告警越多越好，不做误报治理
**现象**：疯狂加检测规则，告警量爆炸，分析师疲于奔命，真正的告警被淹没。
**纠正**：检测规则的质量比数量重要。好的规则应该是"高保真"的——精准、低误报。定期做规则审计和误报治理，持续优化。

### ❌ 误区 5：忽视业务理解
**现象**：只盯着技术告警，不了解业务，导致判断失误。
**纠正**：同一个行为在 A 业务是正常的，在 B 业务可能就是异常。优秀的蓝队分析师必须了解所保护的业务，结合业务上下文做判断。

### ❌ 误区 6：应急响应就是"重装系统"
**现象**：遇到入侵直接重装，不做调查，不知道怎么进来的、丢了什么数据、还留不留后门。
**纠正**：应急响应的核心是"调查 + 遏制 + 根除 + 恢复 + 复盘"。重装是最后一步，之前必须完成调查和取证，否则下次还会被黑，而且不知道为什么。

### ❌ 误区 7：只看技术书，不练实操
**现象**：看了很多书和视频，但从来没搭过环境、没做过取证、没处理过真实事件。
**纠正**：蓝队是实战性极强的工作。一定要自己搭环境、做实验、处理模拟事件。DetectionLab + LetsDefend + CyberDefenders 是非常好的实操资源。

---

## 10. 自测题与产出物

### 10.1 基础理论题

1. 什么是 SOC？SOC 的典型组织架构和人员分工是什么？
2. 解释 MTTD / MTTR / MTTC 的含义和计算方法。
3. NIST 网络安全框架（CSF）的五大核心功能是什么？
4. NIST SP 800-61 应急响应的四个阶段是什么？简述每个阶段的工作。
5. Windows 安全事件日志中，Event ID 4624 / 4625 / 4688 / 4698 / 4720 / 7045 分别代表什么？
6. Sysmon 是什么？它能监控哪些类型的事件？（至少列举 5 个 Event ID）
7. 什么是 Sigma 规则？它的优势是什么？
8. 什么是威胁狩猎？威胁狩猎和入侵检测有什么区别？
9. 威胁狩猎的方法论有哪些？简述假说驱动狩猎的流程。
10. 什么是 IOC 和 TTP？区别是什么？
11. 什么是 MITRE ATT&CK？它对蓝队有什么价值？
12. 数字取证的原则有哪些？什么是证据链（Chain of Custody）？
13. 内存取证能获取哪些磁盘取证得不到的信息？
14. 什么是 STIX 和 TAXII？在威胁情报中的作用是什么？
15. 勒索软件事件响应的关键步骤有哪些？

### 10.2 实操题

1. 搭建一个 ELK 环境，接入 Windows Sysmon 日志和 Linux 系统日志，制作一个安全态势仪表盘。
2. 用 Splunk / ELK 编写 10 条检测规则，覆盖 ATT&CK 的 5 个不同战术。
3. 部署 Suricata，导入 Emerging Threats 规则，并用 Nmap / sqlmap 等工具攻击靶机，验证检测效果。
4. 用 Atomic Red Team 模拟 10 种不同的攻击技术，检查你的 SIEM 是否能检测到，记录检测率和误报率。
5. 完成 LetsDefend 上的 10 个 SOC 分析案例，写出调查过程和结论。
6. 完成 CyberDefenders 上的 5 个取证挑战（内存 / 磁盘 / 流量各至少 1 个）。
7. 用 Volatility 3 分析一个内存镜像，找出恶意进程、网络连接、注入的 DLL，并写出分析报告。
8. 搭建 MISP，接入 3 个开源情报源，并配置 IOC 自动同步到 SIEM。
9. 模拟一次勒索软件入侵事件，完成完整的应急响应流程，输出标准格式的应急响应报告。
10. 进行一次威胁狩猎，基于某个假说（如"存在未被检测的 PowerShell 恶意脚本执行"），用数据验证假说，并写出狩猎报告。

### 10.3 阶段产出物清单

完成本模块后，你应该拥有以下产出物：

- [ ] **实验环境**
  - [ ] ELK Stack 监控环境（接了至少 3 种日志源）
  - [ ] Splunk 实验环境
  - [ ] Wazuh 端点监控环境
  - [ ] Suricata 网络监控环境
  - [ ] MISP 威胁情报平台
  - [ ] Velociraptor 端点响应平台
- [ ] **检测能力**
  - [ ] Sigma 检测规则库（30+ 条，覆盖 10+ ATT&CK 技术）
  - [ ] Suricata 自定义规则（10+ 条）
  - [ ] YARA 规则（10+ 条）
  - [ ] SIEM 仪表盘（5+ 个，涵盖安全态势 / 攻击趋势 / 告警统计等）
  - [ ] ATT&CK 检测覆盖度矩阵
- [ ] **应急响应**
  - [ ] 应急响应报告（5 份以上，覆盖不同类型事件）
  - [ ] 应急响应 Playbook（10+ 个常见事件）
  - [ ] 快速信息收集脚本（Windows + Linux）
- [ ] **取证能力**
  - [ ] 数字取证报告（3 份以上）
  - [ ] Volatility 内存分析脚本
  - [ ] 取证工具 Cheat Sheet
- [ ] **威胁情报**
  - [ ] 自建 MISP 实例 + 情报源配置
  - [ ] IOC 自动化处理脚本
  - [ ] 威胁情报运营手册
- [ ] **靶场战绩**
  - [ ] LetsDefend 完成 20+ 案例
  - [ ] CyberDefenders 完成 15+ 挑战
  - [ ] TryHackMe SOC 路径 100%
  - [ ] BTLO 完成 10+ 实验室（如有）
- [ ] **知识笔记**
  - [ ] Windows Event ID 速查表
  - [ ] Sysmon 事件与检测手册
  - [ ] SPL / ELK 查询 Cheat Sheet
  - [ ] ATT&CK 技术与检测映射笔记
  - [ ] 应急响应流程手册
  - [ ] 取证分析方法论笔记

---

> **下一步建议**：完成 M6 后，你已经具备了完整的蓝队核心能力。接下来：
> - 想继续深化蓝队 → 研究高级威胁狩猎、恶意代码分析、逆向工程
> - 想做安全管理 → 进入 **M10 认证与就业**，准备 CISSP / CISP 等管理类认证
> - 想扩展技术广度 → 学习 **M8 云原生安全**（云安全是蓝队的新战场）
> - 想全面发展 → 进入 **M9 安全开发与 DevSecOps**，从开发源头提升安全
