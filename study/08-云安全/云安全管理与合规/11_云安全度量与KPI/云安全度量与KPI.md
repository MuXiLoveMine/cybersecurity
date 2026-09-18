# 云安全度量与KPI

### 11.1 云安全度量指标

```text
云安全度量框架:

身份与访问:
  ├── MFA覆盖率 = MFA用户数 / 总用户数
  ├── 特权账号比例 = 特权账号数 / 总账号数
  ├── 未使用账号数 = 90天未登录账号数
  └── 访问密钥年龄 = 平均密钥使用天数

网络安全:
  ├── 暴露面 = 公网开放端口数
  ├── 安全组规则数 = 平均每实例规则数
  ├── 0.0.0.0/0规则数 = 公开入站规则数
  └── 流量日志覆盖率 = 日志覆盖实例比例

数据安全:
  ├── 加密覆盖率 = 加密存储桶/实例数 / 总数
  ├── CMK使用率 = 客户管理密钥使用比例
  ├── 敏感数据发现率 = 发现的敏感数据项数
  └── 备份覆盖率 = 有备份的资源 / 总资源

配置合规:
  ├── CIS合规率 = 合规检查项 / 总检查项
  ├── CSPM告警数 = 未修复配置告警数
  ├── 配置漂移次数 = 偏离基线的次数
  └── 修复时间(MTTR) = 平均修复时间

威胁检测:
  ├── GuardDuty发现数 = 新增安全发现数
  ├── 检测时间(MTTD) = 平均检测时间
  ├── 误报率 = 误报数 / 总告警数
  └── 威胁覆盖率 = ATT&CK覆盖技术数

事件响应:
  ├── 事件数 = 安全事件总数
  ├── 响应时间 = 平均响应时间
  ├── 恢复时间 = 平均恢复时间
  └── 自动化率 = 自动响应事件比例

DevSecOps:
  ├── IaC扫描覆盖率 = 扫描模板数 / 总模板数
  ├── 镜像扫描覆盖率 = 扫描镜像数 / 总镜像数
  ├── 漏洞修复SLA达标率 = 按时修复漏洞比例
  └── 部署拦截率 = 被拦截部署次数
```

### 11.2 安全仪表盘设计

```python
#!/usr/bin/env python3
"""云安全度量仪表盘数据生成"""

import json
from datetime import datetime, timedelta

class SecurityMetrics:
    """云安全度量指标收集"""

    def __init__(self):
        self.metrics = {}

    def collect_identity_metrics(self):
        """收集身份安全指标"""
        return {
            "mfa_coverage": 0.95,  # 95%
            "privileged_accounts": 12,
            "inactive_accounts_90d": 5,
            "access_key_avg_age_days": 45,
            "target": {"mfa_coverage": 1.0, "access_key_age": 90}
        }

    def collect_network_metrics(self):
        """收集网络安全指标"""
        return {
            "exposed_ports": 3,
            "sg_rules_per_instance": 8,
            "public_ingress_rules": 2,
            "flow_log_coverage": 0.85,
            "target": {"exposed_ports": 0, "flow_log_coverage": 1.0}
        }

    def collect_data_metrics(self):
        """收集数据安全指标"""
        return {
            "encryption_coverage": 0.92,
            "cmk_usage": 0.80,
            "sensitive_data_items": 1543,
            "backup_coverage": 0.98,
            "target": {"encryption_coverage": 1.0, "backup_coverage": 1.0}
        }

    def collect_compliance_metrics(self):
        """收集合规指标"""
        return {
            "cis_compliance_rate": 0.88,
            "cspm_open_alerts": 23,
            "config_drifts": 7,
            "mttr_hours": 4.5,
            "target": {"cis_compliance_rate": 0.95, "mttr_hours": 2.0}
        }

    def collect_threat_metrics(self):
        """收集威胁检测指标"""
        return {
            "guardduty_findings": 15,
            "mttd_minutes": 12,
            "false_positive_rate": 0.08,
            "attack_coverage": 0.72,
            "target": {"false_positive_rate": 0.05, "attack_coverage": 0.85}
        }

    def generate_dashboard(self):
        """生成仪表盘数据"""
        return {
            "timestamp": datetime.now().isoformat(),
            "identity": self.collect_identity_metrics(),
            "network": self.collect_network_metrics(),
            "data": self.collect_data_metrics(),
            "compliance": self.collect_compliance_metrics(),
            "threat": self.collect_threat_metrics(),
            "overall_health": self._calculate_health_score()
        }

    def _calculate_health_score(self):
        """计算总体安全健康分"""
        identity = self.collect_identity_metrics()
        network = self.collect_network_metrics()
        data = self.collect_data_metrics()
        compliance = self.collect_compliance_metrics()
        # 综合评分
        score = (
            identity["mfa_coverage"] * 20 +
            (1 - min(identity["access_key_avg_age_days"] / 90, 1)) * 10 +
            (1 - min(network["exposed_ports"] / 10, 1)) * 15 +
            data["encryption_coverage"] * 15 +
            data["backup_coverage"] * 10 +
            compliance["cis_compliance_rate"] * 15 +
            (1 - min(compliance["cspm_open_alerts"] / 50, 1)) * 10 +
            (1 - min(compliance["mttr_hours"] / 8, 1)) * 5
        )
        return round(score, 1)


if __name__ == '__main__':
    metrics = SecurityMetrics()
    dashboard = metrics.generate_dashboard()
    print(json.dumps(dashboard, indent=2, ensure_ascii=False, default=str))
```

---

---

## 📋 内容审核与补充建议

> 针对「云安全度量与KPI」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
