# 主流SOAR平台

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

---

