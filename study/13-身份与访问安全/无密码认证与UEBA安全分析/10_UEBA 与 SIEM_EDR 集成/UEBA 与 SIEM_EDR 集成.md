# UEBA 与 SIEM/EDR 集成

### 10.1 集成架构

```
UEBA + SIEM + EDR 集成架构：

┌──────────┐     ┌──────────┐     ┌──────────┐
│   EDR    │     │  NDR     │     │ AD/VPN   │
│ (终端)   │     │ (网络)   │     │ (身份)   │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     └───────┬────────┘                │
             ▼                         │
     ┌───────────────┐                 │
     │  SIEM 日志聚合 │←───────────────┘
     │  (Splunk/QRadar)│
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │   UEBA 引擎   │
     │  行为分析     │
     │  风险评分     │
     └───────┬───────┘
             │
             ▼
     ┌───────────────┐
     │   SOAR 编排    │
     │  自动响应      │
     └───────┬───────┘
             │
     ┌───────┴───────┐
     ▼               ▼
┌─────────┐    ┌──────────┐
│ 阻断/隔离 │    │ 工单/通知 │
│ 自动执行  │    │ 安全团队  │
└─────────┘    └──────────┘
```

### 10.2 集成实现示例

```python
# UEBA与SIEM集成（以Splunk为例）
class SplunkIntegration:
    def __init__(self, splunk_api_url, token):
        self.api_url = splunk_api_url
        self.headers = {'Authorization': f'Bearer {token}'}
        
    def send_ueba_alert(self, risk_assessment):
        """将UEBA告警发送到SIEM"""
        # 构建Splunk事件
        splunk_event = {
            'index': 'ueba_alerts',
            'sourcetype': 'ueba:risk_assessment',
            'event': {
                'user_id': risk_assessment['user_id'],
                'risk_score': risk_assessment['risk_score'],
                'risk_level': risk_assessment['risk_level'],
                'anomalies': [a['type'] for a in risk_assessment['anomalies']],
                'recommended_action': risk_assessment['recommended_action'],
                'timestamp': time.time()
            }
        }
        
        # 发送到Splunk HEC
        requests.post(
            f'{self.api_url}/services/collector',
            json=splunk_event,
            headers=self.headers,
            verify=True
        )
        
    def trigger_soar_playbook(self, risk_assessment):
        """根据风险等级触发SOAR剧本"""
        level = risk_assessment['risk_level']
        
        if level == 'critical':
            # 自动隔离终端
            playbook = 'isolate_endpoint_and_freeze_account'
            self._execute_playbook(playbook, risk_assessment)
        elif level == 'high':
            # 强制MFA + 通知
            playbook = 'force_mfa_and_notify'
            self._execute_playbook(playbook, risk_assessment)
```

---

---

