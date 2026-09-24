# AI 安全监测与告警

### 9.1 监测维度

```text
+--------------------------------------------+
|           LLM 安全监测维度                   |
+--------------------------------------------+
| 1. 有害内容生成率                           |
| 2. 提示注入检测率                           |
| 3. 越狱攻击成功率                           |
| 4. 拒绝率异常（过高可能被攻击，过低可能失守）|
| 5. 隐私泄露事件                             |
| 6. 工具调用异常                             |
| 7. 幻觉率                                   |
| 8. 用户投诉率                               |
+--------------------------------------------+
```

### 9.2 告警机制

```python
class LLMSecurityMonitor:
    """LLM 安全监测与告警"""

    THRESHOLDS = {
        "harmful_rate": 0.01,        # 有害内容率阈值
        "injection_rate": 0.05,     # 注入检测率阈值
        "jailbreak_rate": 0.02,      # 越狱成功率阈值
        "refusal_rate_low": 0.10,    # 拒绝率下限
        "refusal_rate_high": 0.80,  # 拒绝率上限（过高也异常）
    }

    def check_and_alert(self, metrics):
        """检查指标并触发告警"""
        alerts = []

        if metrics["harmful_rate"] > self.THRESHOLDS["harmful_rate"]:
            alerts.append({
                "level": "CRITICAL",
                "message": f"有害内容率过高: {metrics['harmful_rate']}"
            })

        if metrics["jailbreak_rate"] > self.THRESHOLDS["jailbreak_rate"]:
            alerts.append({
                "level": "HIGH",
                "message": f"越狱成功率异常: {metrics['jailbreak_rate']}"
            })

        if metrics["refusal_rate"] > self.THRESHOLDS["refusal_rate_high"]:
            alerts.append({
                "level": "MEDIUM",
                "message": "拒绝率过高，可能遭受攻击或配置异常"
            })

        for alert in alerts:
            self._send_alert(alert)

        return alerts

    def _send_alert(self, alert):
        """发送告警"""
        print(f"[{alert['level']}] {alert['message']}")
        # 实际场景可接入飞书/钉钉/邮件等
```

---

---

