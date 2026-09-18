# SOAR安全编排与自动化响应

> 本文档系统讲解SOAR（Security Orchestration, Automation and Response）的核心概念、平台选型、Playbook设计方法论、开源平台搭建，以及与SIEM/EDR/威胁情报的集成实践，涵盖自动化响应场景和实战案例。

---

## 目录

1. [SOAR概述](#1-soar概述)
2. [SOAR核心功能](#2-soar核心功能)
3. [Playbook设计方法论](#3-playbook设计方法论)
4. [常见自动化响应场景](#4-常见自动化响应场景)
5. [主流SOAR平台](#5-主流soar平台)
6. [开源SOAR搭建](#6-开源soar搭建)
7. [SOAR与SIEM/EDR/威胁情报集成](#7-soar与siemedr威胁情报集成)
8. [实战案例](#8-实战案例)

---

## 1. SOAR概述

### 1.1 什么是SOAR

SOAR（Security Orchestration, Automation and Response，安全编排、自动化与响应）是Gartner提出的安全运营概念，指能够将不同安全工具、流程和人员进行编排整合，实现安全运营自动化和智能化的平台。

SOAR的核心价值在于解决安全运营中的三大痛点：

```
安全运营痛点与SOAR解决方案：

┌────────────────────────┬──────────────────────────────────────┐
│ 痛点                    │ SOAR解决方案                          │
├────────────────────────┼──────────────────────────────────────┤
│ 告警疲劳                │ 自动化过滤和富化，减少误报            │
│ (Alert Fatigue)        │ 自动关联和优先级排序                  │
├────────────────────────┼──────────────────────────────────────┤
│ 工具孤岛                │ 统一编排，跨工具联动                  │
│ (Tool Silos)           │ 标准化API集成                         │
├────────────────────────┼──────────────────────────────────────┤
│ 人才短缺                │ 自动化重复性工作                      │
│ (Skills Shortage)      │ 让分析师专注于复杂调查                │
├────────────────────────┼──────────────────────────────────────┤
│ 响应滞后                │ 自动化响应，秒级处置                  │
│ (Slow Response)       │ 预定义剧本执行                        │
├────────────────────────┼──────────────────────────────────────┤
│ 流程不一致              │ 标准化Playbook                        │
│ (Inconsistent Process) │ 可审计的操作流程                      │
└────────────────────────┴──────────────────────────────────────┘
```

### 1.2 SOAR与SIEM的关系

```
SOAR与SIEM的定位差异：

SIEM（安全信息和事件管理）：
├── 数据收集与聚合（日志、事件）
├── 关联规则引擎（检测异常）
├── 实时告警生成
└── 报表与合规

SOAR（安全编排、自动化与响应）：
├── 告警富化与调查（接SIEM告警）
├── 自动化编排（跨工具联动）
├── 响应执行（隔离、封禁、修复）
└── 案例管理（全流程追踪）

协同关系：
SIEM ──── 告警 ───→ SOAR ──── 响应动作 ───→ 安全工具
  ↑                                                │
  └────────────── 关闭/反馈 ────────────────────────┘

发展趋势：SIEM与SOAR融合
  ├── Splunk: SIEM + Phantom(SOAR) 一体化
  ├── IBM: QRadar(SIEM) + Resilient(SOAR)
  ├── Palo Alto: Cortex XSIAM（一体化）
  └── Microsoft: Sentinel（SIEM + SOAR）
```

**SIEM与SOAR功能对比：**

| 维度 | SIEM | SOAR |
|------|------|------|
| 核心功能 | 日志收集与关联分析 | 安全流程编排与自动化 |
| 数据来源 | 日志、事件流 | SIEM告警、EDR告警、人工上报 |
| 输出 | 告警、报表 | 响应动作、案例记录 |
| 自动化程度 | 规则触发告警 | 多步骤自动化执行 |
| 响应能力 | 仅生成告警 | 执行隔离、封禁等动作 |
| 工具集成 | 日志源 | 安全工具API |
| 人工参与 | 告警后人工分析 | 人在环路（可选） |

### 1.3 市场产品对比

```
2025年主流SOAR产品市场格局：

商业产品：
├── Splunk SOAR（原Phantom）
│   ├── 优势：与Splunk生态深度集成，丰富的App库
│   ├── 劣势：成本较高，学习曲线陡峭
│   └── 适用：大型企业、已使用Splunk的组织
│
├── IBM Security Resilient
│   ├── 优势：强大的案例管理，合规性强
│   ├── 劣势：部署复杂，界面较传统
│   └── 适用：金融、医疗等强合规行业
│
├── Palo Alto Cortex XSOAR
│   ├── 优势：Threat Intelligence Market集成，XDR协同
│   ├── 劣势：绑定Palo Alto生态
│   └── 适用：已使用Palo Alto产品的组织
│
├── Microsoft Sentinel
│   ├── 优势：云原生，Azure深度集成，AI辅助
│   ├── 劣势：需要Azure环境
│   └── 适用：Microsoft生态用户
│
└── Tines
    ├── 优势：简洁易用，可视化编排
    ├── 劣势：功能相对简单
    └── 适用：中小团队，快速上手

开源产品：
├── Shuffle
│   ├── 优势：开源免费，可视化编排，活跃社区
│   ├── 劣势：功能不如商业产品丰富
│   └── 适用：预算有限的团队、学习研究
│
├── TheHive
│   ├── 优势：强大的案例管理，与Cortex/MISP集成
│   ├── 劣势：自动化能力相对有限
│   └── 适用：CSIRT/CERT团队
│
└── Caldera (MITRE)
    ├── 优势：ATT&CK框架原生支持，自动化对手模拟
    ├── 劣势：偏重攻击模拟而非响应
    └── 适用：红蓝对抗、ATT&CK评估
```

---

## 2. SOAR核心功能

### 2.1 剧本管理（Playbook Management）

Playbook是SOAR的核心概念，定义了针对特定安全事件的自动化响应流程。

```
Playbook组成要素：

┌─────────────────────────────────────────────────────┐
│                    Playbook                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ 触发条件（Trigger）                          │   │
│  │ ├── 事件类型：钓鱼邮件、恶意软件、数据泄露    │   │
│  │ ├── 严重级别：低、中、高、紧急               │   │
│  │ └── 来源：SIEM告警、人工上报、EDR检测        │   │
│  └─────────────────────┬───────────────────────┘   │
│                         v                           │
│  ┌─────────────────────────────────────────────┐   │
│  │ 决策节点（Decision Nodes）                   │   │
│  │ ├── 条件判断：if-then-else                  │   │
│  │ ├── 并行执行：并行处理多个动作              │   │
│  │ └── 人在环路：人工审核和确认                │   │
│  └─────────────────────┬───────────────────────┘   │
│                         v                           │
│  ┌─────────────────────────────────────────────┐   │
│  │ 动作编排（Action Orchestration）             │   │
│  │ ├── 查询威胁情报                            │   │
│  │ ├── 隔离主机                                │   │
│  │ ├── 封禁IP                                  │   │
│  │ ├── 创建工单                                │   │
│  │ └── 发送通知                                 │   │
│  └─────────────────────┬───────────────────────┘   │
│                         v                           │
│  ┌─────────────────────────────────────────────┐   │
│  │ 结果处理（Post-processing）                  │   │
│  │ ├── 记录案例                                 │   │
│  │ ├── 通知相关人员                            │   │
│  │ └── 关闭事件                                │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 2.2 案例管理（Case Management）

案例管理是SOAR对安全事件的完整生命周期管理，从事件创建到关闭的全流程追踪。

```
案例生命周期：

创建 → 分类 → 调查 → 处置 → 验证 → 关闭 → 复盘

案例状态流转：
├── New（新建）：事件刚被创建
├── Triage（分诊）：初步评估和分类
├── Investigating（调查中）：深入分析
├── Containing（遏制中）：采取遏制措施
├── Eradicating（根除中）：彻底清除威胁
├── Recovering（恢复中）：恢复系统服务
├── Resolved（已解决）：事件已处理完成
└── Closed（已关闭）：案例归档关闭

案例包含的信息：
├── 事件描述和时间线
├── 影响范围评估
├── 关联告警和日志
├── 执行的动作记录
├── 分析师笔记
├── 证据附件
├── 任务分配
├── 严重级别变更记录
└── 审计跟踪
```

### 2.3 自动化执行（Automation Execution）

```python
# SOAR自动化执行引擎示例（伪代码）

class SOAREngine:
    def __init__(self):
        self.playbooks = {}
        self.connectors = {}
        self.case_db = CaseDatabase()

    def register_playbook(self, name, playbook):
        """注册Playbook"""
        self.playbooks[name] = playbook

    def register_connector(self, name, connector):
        """注册连接器（集成工具）"""
        self.connectors[name] = connector

    def trigger(self, event):
        """事件触发器"""
        # 1. 匹配Playbook
        for name, playbook in self.playbooks.items():
            if playbook.match(event):
                print(f"[*] Triggering playbook: {name}")
                self.execute_playbook(playbook, event)

    def execute_playbook(self, playbook, event):
        """执行Playbook"""
        # 创建案例
        case = self.case_db.create_case(
            title=playbook.get_title(event),
            description=event.get('description', ''),
            severity=event.get('severity', 'medium'),
            source=event.get('source', 'SIEM')
        )

        # 执行动作
        context = {
            'event': event,
            'case': case,
            'results': {}
        }

        for action in playbook.get_actions():
            try:
                result = self.execute_action(action, context)
                context['results'][action.name] = result

                # 检查是否需要人工审核
                if action.requires_approval:
                    approval = self.request_approval(action, context)
                    if not approval:
                        case.add_note(
                            f"Action {action.name} was not approved"
                        )
                        continue

                # 记录动作
                case.add_action(
                    name=action.name,
                    input=action.input,
                    output=result,
                    status='success'
                )

            except Exception as e:
                case.add_action(
                    name=action.name,
                    status='failed',
                    error=str(e)
                )
                if action.on_failure == 'stop':
                    case.update_status('failed')
                    break

        case.update_status('resolved')

    def execute_action(self, action, context):
        """执行单个动作"""
        connector = self.connectors.get(action.connector)
        if not connector:
            raise Exception(f"Connector {action.connector} not found")

        # 渲染参数（变量替换）
        params = self.render_params(action.params, context)

        # 执行
        result = connector.execute(action.method, params)
        return result

    def request_approval(self, action, context):
        """人在环路审批"""
        # 发送审批请求
        case = context['case']
        case.add_note(
            f"Waiting for approval on action: {action.name}"
        )
        # 等待审批（实际实现可能通过邮件/Slack/工单系统）
        return self.wait_for_approval(case.id, action.name)

    def render_params(self, params, context):
        """参数渲染（模板替换）"""
        rendered = {}
        for key, value in params.items():
            if isinstance(value, str):
                # 替换变量，如 ${event.src_ip}
                rendered[key] = self.substitute_variables(value, context)
            else:
                rendered[key] = value
        return rendered

    def substitute_variables(self, template, context):
        """变量替换"""
        import re
        def replace(match):
            var_path = match.group(1).split('.')
            value = context
            for part in var_path:
                if isinstance(value, dict):
                    value = value.get(part, '')
                elif isinstance(value, object):
                    value = getattr(value, part, '')
            return str(value)

        return re.sub(r'\$\{([^}]+)\}', replace, template)
```

### 2.4 集成管理（Integration Management）

SOAR通过连接器（Connector/App/Integration）与各种安全工具集成：

```
SOAR集成类型与典型工具：

SIEM集成：
├── Splunk ES
├── IBM QRadar
├── Microsoft Sentinel
├── Elastic Security
└── LogRhythm

EDR集成：
├── CrowdStrike Falcon
├── Microsoft Defender for Endpoint
├── Carbon Black
├── SentinelOne
└── Sophos Intercept X

防火墙/网络设备：
├── Palo Alto NGFW
├── Cisco ASA/Firepower
├── Check Point
├── Fortinet FortiGate
├── Juniper SRX
└── F5 BIG-IP

威胁情报：
├── VirusTotal
├── AlienVault OTX
├── MISP
├── ThreatConnect
├── Recorded Future
├── IBM X-Force
└── Anomali ThreatStream

身份与访问：
├── Active Directory
├── Azure AD
├── Okta
└── Ping Identity

工单系统：
├── Jira
├── ServiceNow
├── Remedy
└── Zendesk

通信工具：
├── Slack
├── Microsoft Teams
├── Email (SMTP)
├── PagerDuty
└── Webhook

云平台：
├── AWS CloudTrail/GuardDuty
├── Azure Security Center
├── GCP Security Command Center
└── Kubernetes

其他：
├── CyberArk（特权访问）
├── Nessus（漏洞扫描）
├── Proofpoint（邮件安全）
├── Cisco Umbrella（DNS安全）
└── Carbon Black（终端安全）
```

---

## 3. Playbook设计方法论

### 3.1 触发条件设计

```
触发条件类型：

1. 事件驱动触发
   ├── SIEM告警 → SOAR自动接收
   ├── EDR检测 → SOAR自动接收
   ├── 邮件安全网关 → 转发告警
   └── 人工上报 → Web表单/API

2. 定时触发
   ├── 每日安全检查
   ├── 定期威胁狩猎
   └── 合规审计任务

3. 外部触发
   ├── Webhook（来自其他系统）
   ├── API调用
   └── 威胁情报Feed更新

触发条件示例：
┌─────────────────────────────────────────────────────┐
│ Playbook: 钓鱼邮件响应                                │
│ 触发条件:                                            │
│   source == "email_gateway"                          │
│   AND event_type == "phishing"                       │
│   AND severity IN ("high", "critical")              │
│   OR (sender_domain IN threat_intel_bad_domains)     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Playbook: 恶意软件检测响应                            │
│ 触发条件:                                            │
│   source == "EDR"                                     │
│   AND detection_type IN ("malware", "ransomware")   │
│   AND action == "detect" (not auto-contained)       │
└─────────────────────────────────────────────────────┘
```

### 3.2 决策节点设计

```python
# Playbook决策节点设计示例

phishing_playbook = {
    "name": "Phishing Email Response",
    "trigger": {
        "source": "email_gateway",
        "event_type": "phishing",
        "severity": ["high", "critical"]
    },

    "actions": [
        # 步骤1: 告警富化 - 查询威胁情报
        {
            "name": "enrich_sender_domain",
            "connector": "virustotal",
            "method": "domain_report",
            "params": {
                "domain": "${event.sender_domain}"
            },
            "next": "check_domain_reputation"
        },

        # 步骤2: 决策 - 根据情报结果判断
        {
            "name": "check_domain_reputation",
            "type": "decision",
            "conditions": [
                {
                    "if": "${results.enrich_sender_domain.positive_detections} > 5",
                    "then": "block_sender_domain"
                },
                {
                    "if": "${results.enrich_sender_domain.positive_detections} > 0",
                    "then": "quarantine_emails"
                },
                {
                    "else": "mark_as_low_risk"
                }
            ]
        },

        # 步骤3a: 高风险 - 封禁发件域名
        {
            "name": "block_sender_domain",
            "connector": "email_gateway",
            "method": "block_domain",
            "params": {
                "domain": "${event.sender_domain}"
            },
            "requires_approval": True,  # 需要人工确认
            "next": "search_all_mailboxes"
        },

        # 步骤3b: 中风险 - 隔离邮件
        {
            "name": "quarantine_emails",
            "connector": "email_gateway",
            "method": "quarantine",
            "params": {
                "message_id": "${event.message_id}",
                "sender": "${event.sender_email}"
            },
            "next": "notify_recipients"
        },

        # 步骤4: 搜索所有收件箱中的相同邮件
        {
            "name": "search_all_mailboxes",
            "connector": "email_gateway",
            "method": "search_messages",
            "params": {
                "sender": "${event.sender_email}",
                "subject": "${event.subject}"
            },
            "next": "delete_all_copies"
        },

        # 步骤5: 批量删除所有副本
        {
            "name": "delete_all_copies",
            "connector": "email_gateway",
            "method": "delete_messages",
            "params": {
                "message_ids": "${results.search_all_mailboxes.message_ids}"
            },
            "next": "extract_attachments"
        },

        # 步骤6: 提取附件进行沙箱分析
        {
            "name": "extract_attachments",
            "connector": "email_gateway",
            "method": "get_attachments",
            "params": {
                "message_id": "${event.message_id}"
            },
            "next": "sandbox_analysis"
        },

        # 步骤7: 沙箱分析
        {
            "name": "sandbox_analysis",
            "connector": "cuckoo_sandbox",
            "method": "analyze_file",
            "params": {
                "file": "${results.extract_attachments.attachments}"
            },
            "next": "check_sandbox_result"
        },

        # 步骤8: 决策 - 沙箱分析结果
        {
            "name": "check_sandbox_result",
            "type": "decision",
            "conditions": [
                {
                    "if": "${results.sandbox_analysis.score} > 7",
                    "then": "isolate_affected_hosts"
                },
                {
                    "if": "${results.sandbox_analysis.score} > 3",
                    "then": "create_high_priority_ticket"
                },
                {
                    "else": "notify_recipients"
                }
            ]
        },

        # 步骤9: 隔离受影响主机
        {
            "name": "isolate_affected_hosts",
            "connector": "edr",
            "method": "isolate_host",
            "params": {
                "host_ids": "${results.sandbox_analysis.affected_hosts}"
            },
            "requires_approval": True,
            "next": "create_incident_ticket"
        },

        # 步骤10: 创建事件工单
        {
            "name": "create_incident_ticket",
            "connector": "jira",
            "method": "create_issue",
            "params": {
                "project": "SEC",
                "issue_type": "Incident",
                "priority": "P1",
                "summary": "Phishing attack - ${event.sender_domain}",
                "description": "Automated phishing response triggered"
            },
            "next": "notify_soc_team"
        },

        # 步骤11: 通知SOC团队
        {
            "name": "notify_soc_team",
            "connector": "slack",
            "method": "send_message",
            "params": {
                "channel": "#security-alerts",
                "message": "Phishing incident: ${event.sender_domain} - Case: ${case.id}"
            },
            "next": "mark_as_low_risk"
        },

        # 终止节点
        {
            "name": "mark_as_low_risk",
            "type": "terminal",
            "action": "close_case",
            "params": {
                "status": "resolved",
                "resolution": "Low risk phishing - no action needed"
            }
        },

        # 通知收件人节点
        {
            "name": "notify_recipients",
            "connector": "email",
            "method": "send",
            "params": {
                "to": "${event.recipients}",
                "subject": "Security Alert - Phishing Email",
                "body": "A phishing email was detected and quarantined."
            },
            "next": "create_incident_ticket"
        }
    ]
}
```

### 3.3 人在环路（Human-in-the-Loop）

```
人在环路设计原则：

1. 高风险动作必须人工确认
   ├── 封禁IP（可能影响业务）
   ├── 隔离主机（影响用户工作）
   ├── 删除文件（可能误删）
   └── 修改配置（影响系统运行）

2. 低风险动作自动执行
   ├── 查询威胁情报（只读操作）
   ├── 创建工单（无影响）
   ├── 发送通知（无影响）
   └── 记录日志（无影响）

3. 审批机制
   ├── 自动审批：低风险动作自动通过
   ├── 通知审批：通知管理员，超时自动通过
   ├── 强制审批：必须等待人工确认
   └── 升级审批：需要上级确认

审批流程示例：
┌───────────┐     ┌───────────┐     ┌───────────┐
│ 触发审批   │───→│ 通知审批人 │───→│ 等待响应   │
│ (Slack/邮件)│    │ (30分钟)  │     │ (超时处理) │
└───────────┘     └───────────┘     └─────┬─────┘
                                          │
                              ┌───────────┼───────────┐
                              v           v           v
                          批准执行     拒绝执行    超时自动
                          (执行动作)  (跳过动作)  (按策略)
```

---

## 4. 常见自动化响应场景

### 4.1 自动封禁IP

```python
# 自动封禁恶意IP的Playbook

ip_block_playbook = {
    "name": "Auto Block Malicious IP",
    "trigger": {
        "source": ["SIEM", "WAF", "IDS"],
        "event_type": ["brute_force", "port_scan", "ddos", "c2_communication"]
    },
    "conditions": {
        "min_alerts": 5,          # 至少5次告警
        "time_window": 300,       # 5分钟内
        "auto_block_threshold": "high"  # 高风险自动封禁
    },
    "actions": [
        # 1. 查询IP威胁情报
        {
            "name": "query_threat_intel",
            "connector": "virustotal",
            "method": "ip_report",
            "params": {"ip": "${event.src_ip}"}
        },
        # 2. 检查IP是否在内网白名单
        {
            "name": "check_whitelist",
            "connector": "internal_db",
            "method": "query",
            "params": {
                "table": "ip_whitelist",
                "condition": f"ip = '{event.src_ip}'"
            }
        },
        # 3. 决策
        {
            "name": "decide_block",
            "type": "decision",
            "conditions": [
                # 白名单IP不封禁
                {
                    "if": "${results.check_whitelist.count} > 0",
                    "then": "skip_block"
                },
                # 威胁情报确认恶意，自动封禁
                {
                    "if": "${results.query_threat_intel.positive_detections} > 10",
                    "then": "auto_block_firewall"
                },
                # 需要人工确认
                {
                    "else": "request_approval"
                }
            ]
        },
        # 4. 防火墙封禁
        {
            "name": "auto_block_firewall",
            "connector": "palo_alto_fw",
            "method": "block_ip",
            "params": {
                "ip": "${event.src_ip}",
                "duration": 3600,  # 封禁1小时
                "reason": "Auto-block: ${event.event_type}"
            }
        },
        # 5. WAF封禁
        {
            "name": "block_waf",
            "connector": "waf",
            "method": "block_ip",
            "params": {
                "ip": "${event.src_ip}",
                "duration": 3600
            }
        },
        # 6. 记录和通知
        {
            "name": "notify_team",
            "connector": "slack",
            "method": "send_message",
            "params": {
                "channel": "#security-ops",
                "message": f"IP {event.src_ip} auto-blocked. "
                           f"Threat score: {results.query_threat_intel.positive_detections}"
            }
        }
    ]
}
```

### 4.2 自动隔离主机

```python
# 自动隔离受感染主机的Playbook

host_isolation_playbook = {
    "name": "Auto Isolate Compromised Host",
    "trigger": {
        "source": "EDR",
        "event_type": ["malware_detected", "ransomware", "lateral_movement"],
        "severity": ["high", "critical"]
    },
    "actions": [
        # 1. 收集主机信息
        {
            "name": "get_host_info",
            "connector": "edr",
            "method": "get_host_details",
            "params": {"host_id": "${event.host_id}"}
        },
        # 2. 检查是否为关键服务器
        {
            "name": "check_critical_asset",
            "connector": "cmdb",
            "method": "query",
            "params": {
                "table": "assets",
                "condition": f"hostname = '{event.hostname}' AND critical = true"
            }
        },
        # 3. 决策 - 关键服务器需要人工确认
        {
            "name": "decide_isolation",
            "type": "decision",
            "conditions": [
                # 勒索软件 - 立即隔离（即使关键服务器）
                {
                    "if": "${event.event_type} == 'ransomware'",
                    "then": "isolate_immediately"
                },
                # 关键服务器需要人工确认
                {
                    "if": "${results.check_critical_asset.count} > 0",
                    "then": "request_approval"
                },
                # 普通主机自动隔离
                {
                    "else": "isolate_immediately"
                }
            ]
        },
        # 4. 通过EDR隔离主机
        {
            "name": "isolate_immediately",
            "connector": "edr",
            "method": "isolate_host",
            "params": {
                "host_id": "${event.host_id}",
                "comment": "Auto-isolated due to ${event.event_type}"
            }
        },
        # 5. 网络层隔离（防火墙规则）
        {
            "name": "network_isolate",
            "connector": "firewall",
            "method": "add_rule",
            "params": {
                "source_ip": "${results.get_host_info.ip_address}",
                "action": "deny",
                "destination": "any",
                "duration": 86400  # 24小时
            }
        },
        # 6. 802.1X重新认证（将主机移到隔离VLAN）
        {
            "name": "quarantine_vlan",
            "connector": "nac",
            "method": "reassign_vlan",
            "params": {
                "mac_address": "${results.get_host_info.mac_address}",
                "vlan_id": 999  # 隔离VLAN
            }
        },
        # 7. 收集取证数据
        {
            "name": "collect_forensics",
            "connector": "edr",
            "method": "get_forensic_data",
            "params": {
                "host_id": "${event.host_id}",
                "data_types": ["processes", "network", "files", "registry"]
            }
        },
        # 8. 创建事件工单
        {
            "name": "create_ticket",
            "connector": "jira",
            "method": "create_issue",
            "params": {
                "project": "SEC",
                "issue_type": "Incident",
                "priority": "P1",
                "summary": f"Host ${event.hostname} isolated - ${event.event_type}",
                "assignee": "soc-team"
            }
        },
        # 9. 通知
        {
            "name": "notify",
            "connector": "pagerduty",
            "method": "create_incident",
            "params": {
                "title": f"Host isolation: ${event.hostname}",
                "severity": "critical",
                "service": "security-ops"
            }
        }
    ]
}
```

### 4.3 自动创建工单

```python
# 自动创建和分派工单的Playbook

ticket_creation_playbook = {
    "name": "Auto Create and Assign Ticket",
    "trigger": "any_alert",  # 任何告警都触发
    "actions": [
        # 1. 根据事件类型确定优先级
        {
            "name": "determine_priority",
            "type": "logic",
            "logic": """
                if event.severity == 'critical':
                    priority = 'P1'
                    sla = 15  # 分钟
                elif event.severity == 'high':
                    priority = 'P2'
                    sla = 60
                elif event.severity == 'medium':
                    priority = 'P3'
                    sla = 240
                else:
                    priority = 'P4'
                    sla = 1440
                return priority, sla
            """
        },
        # 2. 根据事件类型确定分派团队
        {
            "name": "determine_team",
            "type": "logic",
            "logic": """
                if event.type == 'malware':
                    team = 'malware-analysis'
                elif event.type == 'network_intrusion':
                    team = 'network-security'
                elif event.type == 'phishing':
                    team = 'email-security'
                elif event.type == 'insider_threat':
                    team = 'insider-threat'
                else:
                    team = 'soc-tier1'
                return team
            """
        },
        # 3. 创建Jira工单
        {
            "name": "create_jira_ticket",
            "connector": "jira",
            "method": "create_issue",
            "params": {
                "project": "SEC",
                "issue_type": "Incident",
                "priority": "${results.determine_priority.priority}",
                "summary": "${event.title}",
                "description": """
                    Event Details:
                    - Type: ${event.type}
                    - Source: ${event.source}
                    - Severity: ${event.severity}
                    - Affected Hosts: ${event.affected_hosts}
                    - Timestamp: ${event.timestamp}

                    Initial Analysis:
                    ${results.enrichment.summary}
                """,
                "labels": ["auto-created", event.type],
                "assignee": "${results.determine_team.team}"
            }
        },
        # 4. 设置SLA计时器
        {
            "name": "set_sla",
            "connector": "jira",
            "method": "set_sla",
            "params": {
                "issue_key": "${results.create_jira_ticket.key}",
                "sla_minutes": "${results.determine_priority.sla}"
            }
        }
    ]
}
```

### 4.4 自动查询威胁情报

```python
# 自动威胁情报富化的Playbook

threat_intel_enrichment_playbook = {
    "name": "Auto Threat Intelligence Enrichment",
    "trigger": "any_alert",
    "actions": [
        # 1. 提取IoC指标
        {
            "name": "extract_iocs",
            "type": "logic",
            "logic": """
                iocs = {
                    'ips': [],
                    'domains': [],
                    'hashes': [],
                    'urls': []
                }
                if event.src_ip:
                    iocs['ips'].append(event.src_ip)
                if event.dst_ip:
                    iocs['ips'].append(event.dst_ip)
                if event.domain:
                    iocs['domains'].append(event.domain)
                if event.file_hash:
                    iocs['hashes'].append(event.file_hash)
                if event.url:
                    iocs['urls'].append(event.url)
                return iocs
            """
        },
        # 2. 并行查询多个威胁情报源
        {
            "name": "query_all_sources",
            "type": "parallel",
            "actions": [
                {
                    "name": "query_virustotal",
                    "connector": "virustotal",
                    "method": "batch_query",
                    "params": {
                        "ips": "${results.extract_iocs.ips}",
                        "domains": "${results.extract_iocs.domains}",
                        "hashes": "${results.extract_iocs.hashes}",
                        "urls": "${results.extract_iocs.urls}"
                    }
                },
                {
                    "name": "query_alienvault_otx",
                    "connector": "otx",
                    "method": "batch_query",
                    "params": {
                        "indicators": "${results.extract_iocs}"
                    }
                },
                {
                    "name": "query_misp",
                    "connector": "misp",
                    "method": "search_indicators",
                    "params": {
                        "indicators": "${results.extract_iocs}"
                    }
                },
                {
                    "name": "query_internal_db",
                    "connector": "internal_ti",
                    "method": "search",
                    "params": {
                        "indicators": "${results.extract_iocs}"
                    }
                }
            ]
        },
        # 3. 关联分析
        {
            "name": "correlate_results",
            "type": "logic",
            "logic": """
                # 汇总所有情报源的检测结果
                total_positive = 0
                details = []

                for source in ['virustotal', 'otx', 'misp', 'internal_ti']:
                    result = results.get(source, {})
                    if result.get('positive'):
                        total_positive += 1
                        details.append({
                            'source': source,
                            'score': result.get('score', 0),
                            'tags': result.get('tags', []),
                            'description': result.get('description', '')
                        })

                # 计算综合风险评分
                risk_score = total_positive * 25  # 0-100

                # 确定风险等级
                if risk_score >= 75:
                    risk_level = 'critical'
                elif risk_score >= 50:
                    risk_level = 'high'
                elif risk_score >= 25:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'

                return {
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'details': details,
                    'positive_sources': total_positive
                }
            """
        },
        # 4. 根据风险评分触发相应Playbook
        {
            "name": "route_by_risk",
            "type": "decision",
            "conditions": [
                {
                    "if": "${results.correlate_results.risk_level} == 'critical'",
                    "then": "trigger_critical_response"
                },
                {
                    "if": "${results.correlate_results.risk_level} == 'high'",
                    "then": "trigger_high_response"
                },
                {
                    "else": "close_as_low_risk"
                }
            ]
        }
    ]
}
```

---

## 5. 主流SOAR平台

### 5.1 Splunk SOAR（原Phantom）

```
Splunk SOAR关键特性：

1. 架构
   ├── 基于Python的App/Connector生态
   ├── RESTful API驱动
   └── Docker容器化执行

2. Playbook编写
   ├── 可视化编辑器（拖拽式）
   ├── 代码编辑器（Python脚本）
   └── 版本控制支持

3. 集成生态
   ├── 600+ App连接器
   ├── 支持自定义App开发
   └── REST API自定义集成

4. Splunk SOAR关键API：
```

```python
# Splunk SOAR Playbook示例（Python）
# 文件: phishing_response.py

import phantom.rules as phantom
import json

def on_start(container):
    """Playbook启动"""
    # 获取事件参数
    parameters = []

    # 提取邮件信息
    artifacts = phantom.collect(
        container,
        'artifact',
        filter_keys=['cef.senderEmail']
    )

    for artifact in artifacts:
        sender_email = artifact.get('cef', {}).get('senderEmail')
        if sender_email:
            parameters.append({
                'email': sender_email,
                'context': {'artifact_id': artifact['id']}
            })

    # 并行执行威胁情报查询
    phantom.act("email reputation", parameters,
                assets=["virustotal", "otx"])

def on_email_reputation(action_results):
    """威胁情报查询回调"""
    for result in action_results:
        if result.get('summary', {}).get('positive', False):
            # 恶意邮箱 - 封禁
            phantom.act("block email",
                        parameters=[{
                            'email': result['parameter']['email']
                        }],
                        assets=["exchange"])
        else:
            # 未知 - 人工审核
            phantom.act("add tag",
                        parameters=[{
                            'tag': 'review_needed'
                        }])

def on_block_email(action_results):
    """封禁回调"""
    # 创建工单
    phantom.act("create ticket", parameters=[{
        'subject': 'Phishing email blocked',
        'description': json.dumps(action_results, indent=2)
    }], assets=["jira"])

    # 通知SOC
    phantom.act("send message", parameters=[{
        'message': f"Phishing email blocked: "
                   f"{action_results[0]['parameter']['email']}"
    }], assets=["slack"])

def on_finish(container, summary):
    """Playbook结束"""
    phantom.debug(f"Playbook finished. Summary: {summary}")
```

### 5.2 IBM Resilient

```
IBM Security Resilient特性：

1. 强大的案例管理
   ├── 完整的事件生命周期管理
   ├── 可自定义的工作流
   ├── SLA跟踪和报告
   └── 合规审计支持

2. 集成方式
   ├── REST API
   ├── Function Integration（Python插件）
   └── App Host（容器化集成）

3. Playbook构建
   ├── 可视化工作流设计器
   ├── 条件逻辑和并行处理
   └── 人工审核节点
```

```python
# IBM Resilient Function示例
# 文件: block_ip.py

from resilient_circuits import ResilientComponent, handler
from resilient_lib import IntegrationError, validate_fields

class BlockIPComponent(ResilientComponent):
    """IP封禁组件"""

    def __init__(self, opts):
        super().__init__(opts)
        self.options = opts.get("block_ip", {})
        validate_fields(["api_key", "firewall_ip"], self.options)
        self.api_key = self.options["api_key"]
        self.firewall_ip = self.options["firewall_ip"]

    @handler("block_ip_address")
    def handle_block_ip(self, event, *args, **kwargs):
        """处理IP封禁请求"""
        incident = event.message["incident"]
        ip_address = kwargs.get("ip_address")

        if not ip_address:
            raise IntegrationError("IP address is required")

        # 调用防火墙API
        result = self.block_on_firewall(ip_address)

        # 更新事件
        yield self._create_action_result(
            incident_id=incident["id"],
            action_name="Block IP",
            result=result
        )

    def block_on_firewall(self, ip_address):
        """在防火墙上封禁IP"""
        import requests
        url = f"https://{self.firewall_ip}/api/v1/block"
        headers = {"X-API-Key": self.api_key}
        data = {"ip": ip_address, "duration": 3600}

        response = requests.post(url, json=data, headers=headers,
                                verify=True, timeout=30)

        if response.status_code == 200:
            return {"success": True, "message": f"IP {ip_address} blocked"}
        else:
            return {"success": False, "error": response.text}
```

### 5.3 Cortex XSOAR

```python
# Cortex XSOAR Playbook示例（YAML格式）
# 文件: phishing_response.yml

"""
Cortex XSOAR使用YAML格式定义Playbook
关键概念：Tasks, Conditions, Loops, Scripts
"""

playbook_example = """
name: Phishing Email Response
id: phishing_response
version: 2
tasks:
  # 任务1: 获取邮件信息
  - id: 1
    type: regular
    scriptname: GetEmailDetails
    arguments:
      message_id: ${inputs.message_id}

  # 任务2: 提取IoC
  - id: 2
    type: regular
    scriptname: ExtractIOCs
    arguments:
      email_body: ${tasks.1.results.body}
      attachments: ${tasks.1.results.attachments}

  # 任务3: 查询威胁情报（并行）
  - id: 3
    type: parallel
    tasks:
      - id: 3a
        scriptname: VirusTotal-IP
        arguments:
          ip: ${tasks.2.results.ips}
      - id: 3b
        scriptname: VirusTotal-Domain
        arguments:
          domain: ${tasks.2.results.domains}
      - id: 3c
        scriptname: VirusTotal-File
        arguments:
          hash: ${tasks.2.results.hashes}

  # 任务4: 条件判断
  - id: 4
    type: condition
    conditions:
      - label: Malicious
        condition: ${tasks.3.results.total_positive} > 5
      - label: Suspicious
        condition: ${tasks.3.results.total_positive} > 0
      - label: Clean
        condition: ${tasks.3.results.total_positive} == 0

  # 任务5: 处理恶意邮件
  - id: 5
    type: regular
    scriptname: BlockEmail
    arguments:
      sender: ${tasks.1.results.sender}
      reason: "Phishing email detected"
    nexttasks:
      - id: 6
        label: Malicious

  # 任务6: 搜索并删除所有副本
  - id: 6
    type: regular
    scriptname: SearchAndDeleteEmail
    arguments:
      sender: ${tasks.1.results.sender}
      subject: ${tasks.1.results.subject}

  # 任务7: 创建工单
  - id: 7
    type: regular
    scriptname: JiraCreateIssue
    arguments:
      summary: "Phishing incident: ${tasks.1.results.sender}"
      priority: High
"""
```

### 5.4 Tines

```python
# Tines SOAR示例（JSON格式Story）
# Tines使用可视化Story构建器，底层为JSON

tines_story = {
    "story": {
        "name": "Automated Phishing Response",
        "events": [
            # 触发器 - Webhook接收告警
            {
                "id": 1,
                "type": "webhook",
                "name": "Receive Alert",
                "description": "Receives phishing alert from email gateway"
            },
            # 动作1 - 查询威胁情报
            {
                "id": 2,
                "type": "http_request",
                "name": "Query Threat Intel",
                "connector": "virustotal",
                "url": "https://www.virustotal.com/api/v3/domains/{{.receive_alert.body.sender_domain}}",
                "method": "GET",
                "headers": {"x-apikey": "{{.credentials.virustotal}}"},
                "run_at": "{{.receive_alert.body.severity}}"
            },
            # 动作2 - 条件判断
            {
                "id": 3,
                "type": "condition",
                "name": "Check Risk Level",
                "rules": [
                    {
                        "type": "formula",
                        "label": "High Risk",
                        "value": "{{.query_threat_intel.body.data.attributes.last_analysis_stats.malicious}} > 5"
                    },
                    {
                        "type": "formula",
                        "label": "Medium Risk",
                        "value": "{{.query_threat_intel.body.data.attributes.last_analysis_stats.malicious}} > 0"
                    }
                ]
            },
            # 动作3 - 封禁发件域名（高风险）
            {
                "id": 4,
                "type": "http_request",
                "name": "Block Domain",
                "url": "https://email-gateway/api/block_domain",
                "method": "POST",
                "body": {"domain": "{{.receive_alert.body.sender_domain}}"},
                "run_at": "high_risk"
            },
            # 动作4 - 隔离邮件（中风险）
            {
                "id": 5,
                "type": "http_request",
                "name": "Quarantine Email",
                "url": "https://email-gateway/api/quarantine",
                "method": "POST",
                "body": {"message_id": "{{.receive_alert.body.message_id}}"},
                "run_at": "medium_risk"
            },
            # 动作5 - 发送Slack通知
            {
                "id": 6,
                "type": "http_request",
                "name": "Notify Slack",
                "url": "https://hooks.slack.com/services/...",
                "method": "POST",
                "body": {
                    "text": f"Phishing alert: {receive_alert.body.sender_domain} - "
                           f"Risk: {query_threat_intel.body.data.attributes.last_analysis_stats.malicious}"
                }
            }
        ]
    }
}
```

### 5.5 Shuffle

Shuffle是开源SOAR平台，详见第6节。

---

## 6. 开源SOAR搭建

### 6.1 Shuffle平台安装

```bash
# Shuffle安装（Docker方式）

# 1. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 下载Shuffle
git clone https://github.com/Shuffle/Shuffle.git
cd Shuffle

# 4. 启动Shuffle
docker-compose up -d

# 5. 验证安装
curl http://localhost:3001
# 访问 http://localhost:3001 进行初始化配置

# 6. 配置Shuffle
# 首次访问会提示创建管理员账号
# 设置组织名称和管理员密码
```

**Shuffle架构：**

```
Shuffle组件架构：

┌─────────────────────────────────────────┐
│           Shuffle Frontend (3001)        │
│         Web UI + API Gateway              │
├─────────────────────────────────────────┤
│           Shuffle Backend (5001)        │
│    Workflow Engine + App Engine         │
├─────────────────────────────────────────┤
│           Shuffle Orborus               │
│     Workflow Executor (Docker容器)      │
├─────────────────────────────────────────┤
│           Shuffle Database               │
│    OpenSearch (日志/数据存储)           │
└─────────────────────────────────────────┘

Docker Compose服务：
├── shuffle-frontend    — Web界面 (端口3001)
├── shuffle-backend     — 后端API (端口5001)
├── shuffle-orborus     — 工作流执行器
├── shuffle-opensearch  — 数据存储
├── shuffle-app-sdk     — App开发SDK
└── shuffle-docker      — 容器执行环境
```

### 6.2 Shuffle配置与使用

```yaml
# Shuffle Workflow示例（YAML格式）
# 钓鱼邮件自动响应

workflow:
  name: "Phishing Auto Response"
  description: "Automated phishing email response workflow"
  trigger:
    type: webhook
    name: "Email Alert Webhook"

  steps:
    # 步骤1: 解析告警数据
    - name: "Parse Alert"
      action:
        type: code
        language: python
        code: |
          import json
          alert = webhook_data
          return {
            "sender_email": alert.get("sender", ""),
            "sender_domain": alert.get("sender", "").split("@")[-1],
            "subject": alert.get("subject", ""),
            "recipients": alert.get("recipients", []),
            "attachments": alert.get("attachments", [])
          }

    # 步骤2: 查询威胁情报
    - name: "Query VirusTotal"
      action:
        type: app
        app: virustotal
        action: query_domain
        parameters:
          domain: "$steps.Parse Alert.sender_domain"

    # 步骤3: 条件判断
    - name: "Check Risk"
      action:
        type: condition
        conditions:
          - condition: "$steps.Query VirusTotal.positive > 5"
            action: "High Risk"
          - condition: "$steps.Query VirusTotal.positive > 0"
            action: "Medium Risk"
          - condition: "else"
            action: "Low Risk"

    # 步骤4a: 高风险处理
    - name: "High Risk - Block"
      action:
        type: app
        app: email_gateway
        action: block_domain
        parameters:
          domain: "$steps.Parse Alert.sender_domain"
          duration: 86400

    # 步骤4b: 高风险 - 搜索删除所有副本
    - name: "High Risk - Delete Copies"
      action:
        type: app
        app: email_gateway
        action: search_delete
        parameters:
          sender: "$steps.Parse Alert.sender_email"
          subject: "$steps.Parse Alert.subject"

    # 步骤5: 创建Jira工单
    - name: "Create Ticket"
      action:
        type: app
        app: jira
        action: create_issue
        parameters:
          project: "SEC"
          type: "Incident"
          priority: "High"
          summary: "Phishing: $steps.Parse Alert.sender_domain"
          description: "Automated response triggered"

    # 步骤6: Slack通知
    - name: "Notify Slack"
      action:
        type: app
        app: slack
        action: send_message
        parameters:
          channel: "#security-alerts"
          message: "Phishing alert: $steps.Parse Alert.sender_email"
```

### 6.3 自定义App开发

```python
#!/usr/bin/env python3
"""
Shuffle自定义App示例 - 自定义威胁情报查询App
文件: app.py
"""

from shuffle import App  # Shuffle SDK
import requests
import json

# App配置信息
APP_CONFIG = {
    "name": "Custom Threat Intel",
    "description": "Custom threat intelligence lookup",
    "version": "1.0.0",
    "author": "Security Team",
    "authentication": {
        "type": "apikey",
        "fields": [
            {"name": "api_key", "label": "API Key", "type": "text"},
            {"name": "api_url", "label": "API URL", "type": "text"}
        ]
    }
}

# App入口
app = App(
    name=APP_CONFIG["name"],
    description=APP_CONFIG["description"],
    version=APP_CONFIG["version"]
)

@app.action(
    name="Query IP",
    description="Query threat intelligence for an IP address",
    parameters=[
        {"name": "ip", "label": "IP Address", "type": "text", "required": True}
    ],
    returns={
        "risk_score": "integer",
        "risk_level": "string",
        "details": "array"
    }
)
def query_ip(ip, authentication):
    """查询IP威胁情报"""
    api_key = authentication["api_key"]
    api_url = authentication["api_url"]

    response = requests.get(
        f"{api_url}/api/v1/ip/{ip}",
        headers={"X-API-Key": api_key},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "risk_score": data.get("risk_score", 0),
            "risk_level": data.get("risk_level", "unknown"),
            "details": data.get("details", []),
            "source": "Custom TI"
        }
    else:
        return {
            "success": False,
            "error": f"API returned {response.status_code}"
        }

@app.action(
    name="Query Domain",
    description="Query threat intelligence for a domain",
    parameters=[
        {"name": "domain", "label": "Domain", "type": "text", "required": True}
    ],
    returns={
        "risk_score": "integer",
        "categories": "array",
        "details": "array"
    }
)
def query_domain(domain, authentication):
    """查询域名威胁情报"""
    api_key = authentication["api_key"]
    api_url = authentication["api_url"]

    response = requests.get(
        f"{api_url}/api/v1/domain/{domain}",
        headers={"X-API-Key": api_key},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "risk_score": data.get("risk_score", 0),
            "categories": data.get("categories", []),
            "details": data.get("details", [])
        }
    else:
        return {
            "success": False,
            "error": f"API returned {response.status_code}"
        }

@app.action(
    name="Query Hash",
    description="Query threat intelligence for a file hash",
    parameters=[
        {"name": "hash", "label": "File Hash", "type": "text", "required": True},
        {"name": "hash_type", "label": "Hash Type",
         "type": "select", "options": ["md5", "sha1", "sha256"]}
    ],
    returns={
        "malicious": "boolean",
        "detections": "integer",
        "malware_family": "string"
    }
)
def query_hash(hash_value, hash_type, authentication):
    """查询文件哈希威胁情报"""
    api_key = authentication["api_key"]
    api_url = authentication["api_url"]

    response = requests.get(
        f"{api_url}/api/v1/file/{hash_value}",
        headers={"X-API-Key": api_key},
        params={"type": hash_type},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "malicious": data.get("malicious", False),
            "detections": data.get("detections", 0),
            "malware_family": data.get("malware_family", "unknown")
        }
    else:
        return {
            "success": False,
            "error": f"API returned {response.status_code}"
        }

if __name__ == "__main__":
    app.run()
```

**Dockerfile构建自定义App：**

```dockerfile
# Dockerfile for custom Shuffle App
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制App代码
COPY app.py .
COPY README.md .

# 运行App
CMD ["python3", "app.py", "--run-server", "--port", "3333"]
```

**requirements.txt：**
```
shuffle>=1.2.0
requests>=2.28.0
```

---

## 7. SOAR与SIEM/EDR/威胁情报集成

### 7.1 与SIEM集成

```
SOAR与SIEM集成模式：

模式1: SIEM → SOAR（单向推送）
┌─────────┐     告警      ┌─────────┐
│  SIEM   │ ──────────→ │  SOAR   │ ──→ 自动响应
└─────────┘              └─────────┘

模式2: SOAR ↔ SIEM（双向交互）
┌─────────┐     告警      ┌─────────┐
│  SIEM   │ ←─────────→ │  SOAR   │
│         │   查询/更新  │         │
└─────────┘              └─────────┘

模式3: SOAR → SIEM（事件注入）
┌─────────┐   事件/日志   ┌─────────┐
│  SIEM   │ ←─────────  │  SOAR   │
│  (存储) │              │ (响应)  │
└─────────┘              └─────────┘
```

**Splunk与Splunk SOAR集成配置：**

```python
# Splunk SOAR集成Splunk SIEM

# 1. 配置Splunk连接器
# 在SOAR中添加Splunk App
# 设置: Splunk Server URL, 用户名/密码, API Token

# 2. 创建告警动作（Splunk端）
# 在Splunk中配置告警动作为"Forward to Phantom"
# Splunk告警 → SOAR触发

# 3. SOAR Playbook接收Splunk告警
def on_splunk_alert(container):
    """接收Splunk告警"""
    # 从容器中提取告警信息
    artifacts = phantom.collect(container, 'artifact')

    for artifact in artifacts:
        cef = artifact.get('cef', {})
        # 提取关键字段
        src_ip = cef.get('sourceAddress')
        dst_ip = cef.get('destinationAddress')
        user = cef.get('userName')
        alert_type = cef.get('alertType')

        # 根据告警类型路由到不同Playbook
        if alert_type == 'brute_force':
            trigger_brute_force_response(src_ip)
        elif alert_type == 'malware':
            trigger_malware_response(dst_ip, user)
        elif alert_type == 'data_exfiltration':
            trigger_data_leak_response(src_ip, dst_ip)

# 4. SOAR回写Splunk
def update_splunk(container, action_result):
    """将SOAR执行结果回写Splunk"""
    phantom.act("add event to index", parameters=[{
        'index': 'soar_actions',
        'event': json.dumps({
            'container_id': container['id'],
            'action': action_result['action'],
            'result': action_result['summary'],
            'timestamp': datetime.now().isoformat()
        })
    }], assets=["splunk"])
```

### 7.2 与EDR集成

```python
# SOAR与EDR集成示例

class EDRIntegration:
    """EDR集成统一接口"""

    def __init__(self, edr_type="crowdstrike"):
        self.edr_type = edr_type
        self.connector = self._get_connector()

    def _get_connector(self):
        if self.edr_type == "crowdstrike":
            return CrowdStrikeConnector()
        elif self.edr_type == "defender":
            return DefenderConnector()
        elif self.edr_type == "sentinelone":
            return SentinelOneConnector()
        else:
            raise ValueError(f"Unsupported EDR: {self.edr_type}")

    # 统一API
    def isolate_host(self, host_identifier):
        """隔离主机"""
        return self.connector.isolate_host(host_identifier)

    def get_host_details(self, host_identifier):
        """获取主机详情"""
        return self.connector.get_host_details(host_identifier)

    def get_processes(self, host_identifier):
        """获取进程列表"""
        return self.connector.get_processes(host_identifier)

    def kill_process(self, host_identifier, process_id):
        """终止进程"""
        return self.connector.kill_process(host_identifier, process_id)

    def get_network_connections(self, host_identifier):
        """获取网络连接"""
        return self.connector.get_network_connections(host_identifier)

    def scan_host(self, host_identifier):
        """扫描主机"""
        return self.connector.scan_host(host_identifier)

    def get_forensic_data(self, host_identifier, data_types):
        """获取取证数据"""
        return self.connector.get_forensic_data(host_identifier, data_types)


class CrowdStrikeConnector:
    """CrowdStrike Falcon连接器"""

    def __init__(self):
        self.client_id = os.environ.get("CROWDSTRIKE_CLIENT_ID")
        self.client_secret = os.environ.get("CROWDSTRIKE_CLIENT_SECRET")
        self.base_url = "https://api.crowdstrike.com"
        self.token = self._authenticate()

    def _authenticate(self):
        import requests
        response = requests.post(
            f"{self.base_url}/oauth2/token",
            data={"client_id": self.client_id,
                  "client_secret": self.client_secret},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()["access_token"]

    def isolate_host(self, device_id):
        """隔离主机"""
        import requests
        # 先获取主机详情确认
        response = requests.post(
            f"{self.base_url}/devices/hosts/devices.contain",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json"},
            json={"ids": [device_id]}
        )
        return {
            "success": response.status_code == 200,
            "device_id": device_id,
            "action": "isolated"
        }

    def get_host_details(self, device_id):
        """获取主机详情"""
        import requests
        response = requests.get(
            f"{self.base_url}/devices/entities/devices/v1",
            params={"ids": device_id},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()["resources"][0] if response.json()["resources"] else None
```

### 7.3 与威胁情报集成

```python
# SOAR与威胁情报平台集成

class ThreatIntelIntegration:
    """威胁情报统一接口"""

    def __init__(self):
        self.sources = {
            "virustotal": VirusTotalConnector(),
            "misp": MISPConnector(),
            "otx": OTXConnector(),
            "internal": InternalTIConnector()
        }

    def enrich_indicator(self, indicator_type, indicator_value):
        """富化威胁指标"""
        results = {}
        total_positive = 0

        for source_name, source in self.sources.items():
            try:
                result = source.query(indicator_type, indicator_value)
                results[source_name] = result
                if result.get("malicious"):
                    total_positive += 1
            except Exception as e:
                results[source_name] = {"error": str(e)}

        # 计算综合评分
        risk_score = (total_positive / len(self.sources)) * 100

        return {
            "indicator": indicator_value,
            "type": indicator_type,
            "risk_score": risk_score,
            "positive_sources": total_positive,
            "details": results
        }

    def batch_enrich(self, indicators):
        """批量富化"""
        enriched = []
        for ind in indicators:
            result = self.enrich_indicator(
                ind.get("type"),
                ind.get("value")
            )
            enriched.append(result)
        return enriched


class MISPConnector:
    """MISP威胁情报平台连接器"""

    def __init__(self):
        self.url = os.environ.get("MISP_URL")
        self.api_key = os.environ.get("MISP_API_KEY")

    def query(self, indicator_type, indicator_value):
        """查询MISP"""
        import requests
        type_mapping = {
            "ip": "ip-src",
            "domain": "domain",
            "hash": "md5",
            "url": "url"
        }

        misp_type = type_mapping.get(indicator_type, indicator_type)

        response = requests.post(
            f"{self.url}/attributes/restSearch",
            headers={"Authorization": self.api_key,
                     "Content-Type": "application/json",
                     "Accept": "application/json"},
            json={
                "returnFormat": "json",
                "value": indicator_value,
                "type": misp_type
            }
        )

        data = response.json()
        if data.get("response"):
            return {
                "malicious": True,
                "source": "MISP",
                "events": data["response"],
                "tags": self._extract_tags(data["response"])
            }
        else:
            return {
                "malicious": False,
                "source": "MISP"
            }

    def _extract_tags(self, events):
        """提取标签"""
        tags = set()
        for event in events:
            for attribute in event.get("Attribute", []):
                for tag in attribute.get("Tag", []):
                    tags.add(tag.get("name"))
        return list(tags)
```

---

## 8. 实战案例

### 8.1 自动化钓鱼响应

**场景：** 企业邮件安全网关检测到钓鱼邮件，通过Webhook发送到SOAR，自动执行响应流程。

**完整Playbook设计：**

```
钓鱼邮件自动化响应流程：

触发: 邮件网关Webhook → SOAR
  │
  v
Step 1: 解析邮件数据
  ├── 提取发件人、收件人、主题、正文
  ├── 提取附件
  └── 提取邮件中的URL和域名
  │
  v
Step 2: 威胁情报查询（并行）
  ├── VirusTotal查询发件域名
  ├── MISP查询邮件URL
  ├── 内部TI查询发件IP
  └── OpenPhish查询URL
  │
  v
Step 3: 附件沙箱分析
  ├── Cuckoo沙箱分析附件
  └── Any.Run沙箱分析
  │
  v
Step 4: 风险评估
  ├── 综合威胁情报评分
  ├── 沙箱分析评分
  └── 确定风险等级（低/中/高/紧急）
  │
  ├── 紧急(风险>80):
  │   ├── 封禁发件域名
  │   ├── 搜索并删除所有邮件副本
  │   ├── 隔离已打开附件的主机
  │   ├── 重置受影响用户密码
  │   ├── 创建P1工单
  │   └── 通知CISO
  │
  ├── 高(风险60-80):
  │   ├── 隔离原始邮件
  │   ├── 搜索并隔离其他副本
  │   ├── 创建P2工单
  │   └── 通知SOC
  │
  ├── 中(风险30-60):
  │   ├── 标记邮件为可疑
  │   ├── 通知收件人注意
  │   └── 创建P3工单
  │
  └── 低(风险<30):
      ├── 记录日志
      └── 关闭事件
```

### 8.2 勒索软件应急自动化

**场景：** EDR检测到勒索软件行为，自动触发应急响应。

```python
# 勒索软件自动化响应Playbook（Shuffle格式）

ransomware_response_workflow = {
    "name": "Ransomware Auto Response",
    "trigger": {
        "source": "EDR",
        "event_type": "ransomware_detected",
        "severity": "critical"
    },
    "steps": [
        # 1. 立即隔离受感染主机（0延迟）
        {
            "name": "immediate_isolation",
            "action": {
                "type": "app",
                "app": "edr",
                "action": "isolate_host",
                "params": {"host_id": "${event.host_id}"},
                "priority": 1,  # 最高优先级
                "timeout": 30   # 30秒超时
            }
        },

        # 2. 同时隔离所有被感染的关联主机
        {
            "name": "isolate_related_hosts",
            "action": {
                "type": "app",
                "app": "edr",
                "action": "isolate_hosts",
                "params": {
                    "host_ids": "${event.lateral_movement_hosts}"
                }
            }
        },

        # 3. 网络层隔离
        {
            "name": "network_quarantine",
            "action": {
                "type": "app",
                "app": "firewall",
                "action": "quarantine_subnet",
                "params": {
                    "subnet": "${event.affected_subnet}",
                    "duration": 86400
                }
            }
        },

        # 4. 收集取证数据
        {
            "name": "collect_forensics",
            "action": {
                "type": "app",
                "app": "edr",
                "action": "snapshot",
                "params": {
                    "host_ids": "${event.all_affected_hosts}",
                    "include": ["processes", "files", "network",
                               "registry", "memory"]
                }
            }
        },

        # 5. 搜索勒索软件特征
        {
            "name": "search_ransomware_signatures",
            "action": {
                "type": "app",
                "app": "edr",
                "action": "search",
                "params": {
                    "query": "file_hash:${event.malware_hash}",
                    "scope": "all_hosts"
                }
            }
        },

        # 6. 封禁C2通信
        {
            "name": "block_c2",
            "action": {
                "type": "app",
                "app": "firewall",
                "action": "block_ip",
                "params": {
                    "ip": "${event.c2_ip}",
                    "duration": "permanent"
                }
            }
        },

        # 7. 创建紧急事件工单
        {
            "name": "create_critical_ticket",
            "action": {
                "type": "app",
                "app": "jira",
                "action": "create_issue",
                "params": {
                    "project": "SEC",
                    "type": "Incident",
                    "priority": "P1",
                    "summary": f"RANSOMWARE: ${event.malware_name} "
                               f"on ${event.hostname}",
                    "description": """
                        RANSOMWARE INCIDENT - AUTO RESPONSE
                        ────────────────────────────────
                        Detection: ${event.detection_name}
                        Host: ${event.hostname}
                        Malware: ${event.malware_name}
                        Affected hosts: ${event.all_affected_hosts}
                        C2 IP: ${event.c2_ip}

                        Actions taken:
                        - Host isolated
                        - Network quarantined
                        - C2 blocked
                        - Forensics collected

                        Next steps required:
                        1. Verify isolation is effective
                        2. Identify patient zero
                        3. Check backup integrity
                        4. Initiate recovery procedure
                    """
                }
            }
        },

        # 8. 紧急通知
        {
            "name": "emergency_notifications",
            "parallel": True,
            "actions": [
                {
                    "name": "page_oncall",
                    "action": {
                        "type": "app",
                        "app": "pagerduty",
                        "action": "trigger_incident",
                        "params": {
                            "service": "security-critical",
                            "severity": "critical",
                            "title": "RANSOMWARE DETECTED"
                        }
                    }
                },
                {
                    "name": "notify_slack",
                    "action": {
                        "type": "app",
                        "app": "slack",
                        "action": "send_message",
                        "params": {
                            "channel": "#security-incidents",
                            "message": f"RANSOMWARE ALERT: ${event.malware_name} "
                                       f"detected on ${event.hostname}. "
                                       f"Host isolated. Case: ${case.id}"
                        }
                    }
                },
                {
                    "name": "call_tree",
                    "action": {
                        "type": "app",
                        "app": "twilio",
                        "action": "make_calls",
                        "params": {
                            "numbers": "${oncall.call_tree}",
                            "message": "Ransomware incident detected. Immediate response required."
                        }
                    }
                }
            ]
        },

        # 9. 自动创建取证时间线
        {
            "name": "create_timeline",
            "action": {
                "type": "code",
                "language": "python",
                "code": """
                    timeline = []
                    for action in executed_actions:
                        timeline.append({
                            'timestamp': action.timestamp,
                            'action': action.name,
                            'result': action.summary
                        })
                    return {'timeline': timeline}
                """
            }
        }
    ]
}
```

### 8.3 内部威胁检测响应

**场景：** 用户异常数据访问行为，触发内部威胁响应。

```python
# 内部威胁自动化响应Playbook

insider_threat_workflow = {
    "name": "Insider Threat Response",
    "trigger": {
        "source": ["DLP", "UEBA", "SIEM"],
        "event_type": [
            "mass_data_download",
            "unusual_access_pattern",
            "data_exfiltration_attempt",
            "off_hours_access"
        ]
    },
    "steps": [
        # 1. 收集用户上下文
        {
            "name": "gather_user_context",
            "action": {
                "type": "app",
                "app": "active_directory",
                "action": "get_user",
                "params": {"username": "${event.username}"}
            }
        },

        # 2. 检查用户风险历史
        {
            "name": "check_risk_history",
            "action": {
                "type": "app",
                "app": "internal_db",
                "action": "query",
                "params": {
                    "table": "user_risk_events",
                    "condition": f"username = '{event.username}' AND "
                                 f"timestamp > NOW() - INTERVAL 30 DAY"
                }
            }
        },

        # 3. 分析访问模式异常
        {
            "name": "analyze_access_patterns",
            "action": {
                "type": "code",
                "language": "python",
                "code": """
                    # 分析用户访问行为
                    user_id = event['username']

                    # 获取用户历史访问记录
                    history = results['check_risk_history']

                    # 计算异常评分
                    anomaly_score = 0
                    risk_factors = []

                    # 因素1: 非工作时间访问
                    if event.get('off_hours'):
                        anomaly_score += 20
                        risk_factors.append('off_hours_access')

                    # 因素2: 大量数据下载
                    if event.get('data_volume', 0) > 1000000000:  # 1GB
                        anomaly_score += 30
                        risk_factors.append('large_data_download')

                    # 因素3: 访问不相关业务数据
                    if event.get('unrelated_data'):
                        anomaly_score += 25
                        risk_factors.append('unrelated_data_access')

                    # 因素4: 历史风险事件
                    if history and history.get('count', 0) > 3:
                        anomaly_score += 25
                        risk_factors.append('repeated_risk_events')

                    return {
                        'anomaly_score': anomaly_score,
                        'risk_factors': risk_factors,
                        'risk_level': 'critical' if anomaly_score >= 70
                                     else 'high' if anomaly_score >= 50
                                     else 'medium' if anomaly_score >= 30
                                     else 'low'
                    }
                """
            }
        },

        # 4. 根据风险等级响应
        {
            "name": "route_response",
            "action": {
                "type": "condition",
                "conditions": [
                    # 紧急 - 立即限制访问
                    {
                        "condition": "${results.analyze_access_patterns.risk_level} == 'critical'",
                        "action": "critical_response"
                    },
                    # 高风险 - 临时限制 + 通知
                    {
                        "condition": "${results.analyze_access_patterns.risk_level} == 'high'",
                        "action": "high_response"
                    },
                    # 中风险 - 监控 + 通知
                    {
                        "condition": "${results.analyze_access_patterns.risk_level} == 'medium'",
                        "action": "medium_response"
                    }
                ]
            }
        },

        # 5a. 紧急响应 - 限制访问
        {
            "name": "critical_response",
            "parallel": True,
            "actions": [
                # 禁用VPN访问
                {
                    "name": "disable_vpn",
                    "action": {
                        "type": "app",
                        "app": "vpn_gateway",
                        "action": "disable_user",
                        "params": {"username": "${event.username}"}
                    }
                },
                # 限制文件访问权限
                {
                    "name": "restrict_file_access",
                    "action": {
                        "type": "app",
                        "app": "file_server",
                        "action": "set_readonly",
                        "params": {"username": "${event.username}"}
                    }
                },
                # 启用会话录制
                {
                    "name": "enable_session_recording",
                    "action": {
                        "type": "app",
                        "app": "pam",
                        "action": "enable_recording",
                        "params": {"username": "${event.username}"}
                    }
                },
                # 强制重新认证
                {
                    "name": "force_reauth",
                    "action": {
                        "type": "app",
                        "app": "identity_provider",
                        "action": "revoke_sessions",
                        "params": {"username": "${event.username}"}
                    }
                },
                # HR和法务通知
                {
                    "name": "notify_hr_legal",
                    "action": {
                        "type": "app",
                        "app": "email",
                        "action": "send",
                        "params": {
                            "to": ["hr@company.com", "legal@company.com"],
                            "subject": f"INSIDER THREAT: ${event.username}",
                            "body": "Critical insider threat detected. User access restricted."
                        }
                    }
                }
            ]
        },

        # 5b. 高风险响应
        {
            "name": "high_response",
            "actions": [
                # 增加监控级别
                {
                    "name": "increase_monitoring",
                    "action": {
                        "type": "app",
                        "app": "ueba",
                        "action": "set_risk_level",
                        "params": {
                            "username": "${event.username}",
                            "risk_level": "high"
                        }
                    }
                },
                # 通知管理者
                {
                    "name": "notify_manager",
                    "action": {
                        "type": "app",
                        "app": "email",
                        "action": "send",
                        "params": {
                            "to": "${results.gather_user_context.manager_email}",
                            "subject": "Security Alert - Unusual Activity",
                            "body": f"Unusual activity detected for ${event.username}"
                        }
                    }
                }
            ]
        },

        # 6. 创建调查工单
        {
            "name": "create_investigation",
            "action": {
                "type": "app",
                "app": "jira",
                "action": "create_issue",
                "params": {
                    "project": "SEC",
                    "type": "Insider Threat Investigation",
                    "priority": "${results.analyze_access_patterns.risk_level}",
                    "summary": f"Insider threat: ${event.username}",
                    "assignee": "insider-threat-team"
                }
            }
        }
    ]
}
```

---

## 附录：SOAR实施清单

```
SOAR项目实施清单：

Phase 1: 需求评估
□ 识别当前安全运营痛点
□ 评估告警量和响应时间
□ 确定优先自动化的场景
□ 评估团队技能水平

Phase 2: 平台选型
□ 评估商业vs开源
□ 测试集成兼容性
□ 评估成本和ROI
□ 确定部署模式（云/本地）

Phase 3: 架构设计
□ 设计集成架构
□ 规划Playbook分类
□ 定义审批流程
□ 设计监控和告警

Phase 4: 集成开发
□ 实现SIEM集成
□ 实现EDR集成
□ 实现威胁情报集成
□ 开发自定义App

Phase 5: Playbook开发
□ 从简单场景开始
□ 充分测试每个步骤
□ 设置审批机制
□ 文档化每个Playbook

Phase 6: 试运行
□ 小范围试运行
□ 收集反馈和优化
□ 调整自动化阈值
□ 扩大自动化范围

Phase 7: 持续优化
□ 定期回顾Playbook效果
□ 根据新威胁更新Playbook
□ 持续监控自动化率
□ 定期演练和测试
```

---

## 参考文献

1. Gartner SOAR Market Guide: https://www.gartner.com
2. Splunk SOAR Documentation: https://docs.splunk.com/Documentation/SOAR
3. Shuffle Documentation: https://shuffler.io/docs
4. TheHive Project: https://thehive-project.org
5. MITRE CALDERA: https://github.com/mitre/caldera
6. SANS SOC Survey: https://www.sans.org
7. 《安全运营中心（SOC）建设指南》
8. NIST SP 800-61: Computer Security Incident Handling Guide
9. Cortex XSOAR Documentation: https://docs.paloaltonetworks.com/cortex
10. IBM Resilient Documentation: https://www.ibm.com/docs/resilient
