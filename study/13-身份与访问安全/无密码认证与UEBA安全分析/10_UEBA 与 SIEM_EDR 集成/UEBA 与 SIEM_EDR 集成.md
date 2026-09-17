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

## 📋 内容审核与补充建议

> 针对「UEBA 与 SIEM/EDR 集成」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
