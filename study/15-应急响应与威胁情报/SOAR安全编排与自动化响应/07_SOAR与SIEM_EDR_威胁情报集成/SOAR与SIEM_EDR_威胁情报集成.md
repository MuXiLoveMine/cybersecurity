# SOAR与SIEM/EDR/威胁情报集成

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

---

## 📋 内容审核与补充建议

> 针对「SOAR与SIEM/EDR/威胁情报集成」部分的内容审核结果：

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
