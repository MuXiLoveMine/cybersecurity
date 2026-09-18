# SOAR核心功能

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

---

## 📋 内容审核与补充建议

> 针对「SOAR核心功能」部分的内容审核结果：

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
