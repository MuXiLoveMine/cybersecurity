# Playbook设计方法论

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

---

## 📋 内容审核与补充建议

> 针对「Playbook设计方法论」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
