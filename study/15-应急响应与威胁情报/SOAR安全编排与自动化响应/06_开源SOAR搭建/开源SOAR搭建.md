# 开源SOAR搭建

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

---

