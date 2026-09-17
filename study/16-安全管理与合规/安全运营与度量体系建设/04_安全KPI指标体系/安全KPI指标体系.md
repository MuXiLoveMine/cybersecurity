# 安全KPI指标体系

### 3.1 防御度量

防御度量衡量组织预防安全事件的能力，是安全运营的基础。

**漏洞修复率（Vulnerability Remediation Rate）**

```
指标定义：
  漏洞修复率 = （已修复漏洞数 / 发现漏洞总数）× 100%

细分指标：
  ├── 高危漏洞修复率 = （已修复高危漏洞 / 发现高危漏洞总数）× 100%
  ├── 严重漏洞修复率 = （已修复严重漏洞 / 发现严重漏洞总数）× 100%
  ├── 平均修复时间（MTTR-Vuln）= 所有漏洞修复总时间 / 修复数量
  └── SLA达标率 = 在SLA时间内修复的漏洞数 / 应在SLA内修复的漏洞总数 × 100%

SLA目标示例：
  ├── 严重（Critical）：7天内修复，达标率>95%
  ├── 高危（High）：14天内修复，达标率>90%
  ├── 中危（Medium）：30天内修复，达标率>85%
  └── 低危（Low）：90天内修复，达标率>80%

计算示例：
  本月扫描发现漏洞：
    严重：10个（已修复9个）
    高危：50个（已修复45个）
    中危：200个（已修复160个）
    低危：500个（已修复350个）

  高危修复率 = 45/50 = 90%
  总体修复率 = (9+45+160+350)/(10+50+200+500) = 564/760 = 74.2%
```

```python
# 漏洞度量自动化脚本
import json
from datetime import datetime, timedelta
from collections import defaultdict

class VulnerabilityMetrics:
    def __init__(self):
        self.vulnerabilities = []

    def add_vuln(self, vuln_id, severity, discovered_date,
                 remediated_date=None, asset_id=None):
        self.vulnerabilities.append({
            'id': vuln_id,
            'severity': severity,
            'discovered': discovered_date,
            'remediated': remediated_date,
            'asset_id': asset_id
        })

    def calculate_remediation_rate(self, severity=None, period=None):
        """计算修复率"""
        vulns = self.vulnerabilities
        if severity:
            vulns = [v for v in vulns if v['severity'] == severity]
        if period:
            start, end = period
            vulns = [v for v in vulns
                     if start <= v['discovered'] <= end]

        total = len(vulns)
        remediated = sum(1 for v in vulns if v['remediated'])
        rate = (remediated / total * 100) if total > 0 else 0

        return {
            'total': total,
            'remediated': remediated,
            'rate': round(rate, 2)
        }

    def calculate_mttr(self, severity=None):
        """计算平均修复时间（天）"""
        vulns = [v for v in self.vulnerabilities
                 if v['remediated'] and
                 (severity is None or v['severity'] == severity)]

        if not vulns:
            return 0

        total_days = sum(
            (v['remediated'] - v['discovered']).days
            for v in vulns
        )
        return round(total_days / len(vulns), 1)

    def calculate_sla_compliance(self, sla_days):
        """计算SLA达标率"""
        sla_map = {'Critical': 7, 'High': 14,
                   'Medium': 30, 'Low': 90}

        results = {}
        for severity, sla in sla_map.items():
            vulns = [v for v in self.vulnerabilities
                     if v['severity'] == severity]

            total = len(vulns)
            if total == 0:
                results[severity] = {'rate': 100, 'total': 0}
                continue

            compliant = sum(
                1 for v in vulns
                if v['remediated'] and
                (v['remediated'] - v['discovered']).days <= sla
            )
            results[severity] = {
                'rate': round(compliant / total * 100, 2),
                'total': total,
                'compliant': compliant,
                'sla_days': sla
            }

        return results

    def generate_report(self, period=None):
        """生成度量报告"""
        print("=" * 60)
        print("Vulnerability Metrics Report")
        if period:
            print(f"Period: {period[0].date()} to {period[1].date()}")
        print("=" * 60)

        # 按严重级别统计
        for sev in ['Critical', 'High', 'Medium', 'Low']:
            rate = self.calculate_remediation_rate(severity=sev)
            mttr = self.calculate_mttr(severity=sev)
            print(f"\n{sev}:")
            print(f"  Total: {rate['total']}")
            print(f"  Remediated: {rate['remediated']}")
            print(f"  Remediation Rate: {rate['rate']}%")
            print(f"  MTTR: {mttr} days")

        # SLA达标率
        print("\nSLA Compliance:")
        sla_results = self.calculate_sla_compliance(None)
        for sev, data in sla_results.items():
            print(f"  {sev}: {data['rate']}% ({data.get('compliant', 0)}/"
                  f"{data['total']}, SLA: {data.get('sla_days', 'N/A')} days)")

        return {
            'remediation_rates': {
                sev: self.calculate_remediation_rate(severity=sev)
                for sev in ['Critical', 'High', 'Medium', 'Low']
            },
            'sla_compliance': sla_results
        }
```

**补丁覆盖率（Patch Coverage Rate）**

```
指标定义：
  补丁覆盖率 = （已打补丁的资产数 / 应打补丁的资产总数）× 100%

细分指标：
  ├── 关键补丁覆盖率：关键安全补丁的部署率
  ├── 30天补丁覆盖率：发布30天内的补丁部署率
  ├── 操作系统补丁覆盖率
  ├── 应用程序补丁覆盖率
  └── 第三方软件补丁覆盖率

目标值：
  ├── 关键补丁：>95%（30天内）
  ├── 操作系统补丁：>90%（60天内）
  └── 应用程序补丁：>85%（90天内）
```

**配置合规率（Configuration Compliance Rate）**

```
指标定义：
  配置合规率 = （合规配置项数 / 检查配置项总数）× 100%

基线标准：
  ├── CIS Benchmark
  ├── 企业安全基线
  ├── 行业标准（PCI DSS、等保2.0）
  └── 自定义安全策略

示例检查项：
  ├── 密码策略（长度、复杂度、过期）
  ├── 账户锁定策略
  ├── 审计日志启用
  ├── 不必要服务关闭
  ├── 文件权限设置
  ├── 防火墙规则
  └── 加密配置
```

### 3.2 检测度量

**平均检测时间（MTTD - Mean Time to Detect）**

```
指标定义：
  MTTD = 从威胁发生到被检测到的平均时间

计算公式：
  MTTD = Σ(检测时间 - 威胁发生时间) / 检测事件数

时间线：
  威胁发生 → ──── MTTD ──── → 检测到 → ──── MTTR ──── → 解决

目标值：
  ├── 自动化检测（EDR/NDR）：< 5分钟
  ├── SIEM关联检测：< 30分钟
  ├── 人工分析检测：< 4小时
  └── 综合MTTD：< 1小时（高危事件）

改进方向：
  ├── 扩大检测覆盖面
  ├── 优化检测规则（减少盲区）
  ├── 引入威胁狩猎（主动检测）
  ├── 部署EDR/XDR（实时检测）
  └── 引入UEBA（行为异常检测）
```

**告警准确率（Alert Accuracy / Precision）**

```
指标定义：
  告警准确率 = 真实安全事件告警数 / 总告警数 × 100%

相关指标：
  ├── 误报率（False Positive Rate）
  │   误报率 = 误报数 / 总告警数 × 100%
  │   目标：< 10%
  │
  ├── 漏报率（False Negative Rate）
  │   漏报率 = 未检测到的真实事件 / 真实事件总数 × 100%
  │   目标：< 5%
  │
  └── 告警信噪比（Signal-to-Noise Ratio）
      SNR = 真实告警 / 虚假告警

告警分级准确率：
  ┌──────────────┬──────────┬──────────┐
  │ 告警级别      │ 准确率目标│ 实际值   │
  ├──────────────┼──────────┼──────────┤
  │ 紧急(Critical)│ >95%     │ 待采集   │
  │ 高危(High)   │ >85%     │ 待采集   │
  │ 中危(Medium)  │ >70%     │ 待采集   │
  │ 低危(Low)    │ >50%     │ 待采集   │
  └──────────────┴──────────┴──────────┘
```

**覆盖率（Detection Coverage）**

```
指标定义：
  检测覆盖率 = 覆盖的资产/威胁数 / 应覆盖的总数 × 100%

覆盖率维度：
  ├── 资产覆盖率：被监控的资产占总资产的比例
  │   ├── 服务器覆盖率：>95%
  │   ├── 终端覆盖率：>90%
  │   ├── 网络覆盖率：>80%
  │   └── 云资产覆盖率：>90%
  │
  ├── ATT&CK覆盖率：检测规则覆盖MITRE ATT&CK技术的比例
  │   ├── 战术覆盖率：覆盖的战术数 / 14 × 100%
  │   ├── 技术覆盖率：覆盖的技术数 / 全部技术 × 100%
  │   └── 目标：>70%的技术覆盖率
  │
  └── 日志覆盖率：采集日志的资产/系统比例
      ├── Windows安全日志：>95%
      ├── Linux系统日志：>95%
      ├── 网络设备日志：>90%
      ├── 应用日志：>80%
      └── 云平台日志：>90%
```

### 3.3 响应度量

**平均响应时间（MTTR - Mean Time to Respond/Recover）**

```
指标定义：
  MTTR = 从检测到威胁到完全解决的平均时间

MTTR细分：
  ├── MTTR-Contain：检测到遏制的时间
  │   目标：紧急<30分钟，高危<2小时
  │
  ├── MTTR-Eradicate：遏制到根除的时间
  │   目标：紧急<4小时，高危<8小时
  │
  ├── MTTR-Recover：根除到恢复的时间
  │   目标：紧急<24小时，高危<48小时
  │
  └── MTTR-Total：检测到完全解决的时间
      目标：紧急<24小时，高危<72小时

MTTR计算示例：
  事件1: 检测14:00 → 遏制14:20 → 根除15:00 → 恢复16:00
         MTTR-Contain=20min, MTTR-Total=120min

  事件2: 检测09:00 → 遏制09:15 → 根除10:30 → 恢复12:00
         MTTR-Contain=15min, MTTR-Total=180min

  平均MTTR-Contain = (20+15)/2 = 17.5min
  平均MTTR-Total = (120+180)/2 = 150min
```

```python
class IncidentMetrics:
    """安全事件度量"""

    def __init__(self):
        self.incidents = []

    def add_incident(self, incident_id, detected_time, contained_time,
                     eradicated_time=None, recovered_time=None,
                     severity='medium', auto_detected=False):
        self.incidents.append({
            'id': incident_id,
            'detected': detected_time,
            'contained': contained_time,
            'eradicated': eradicated_time,
            'recovered': recovered_time,
            'severity': severity,
            'auto_detected': auto_detected
        })

    def calculate_mttd(self, occurred_time_key='occurred'):
        """计算MTTD"""
        # 需要知道威胁实际发生时间
        # 通常来自事后分析
        detection_times = []
        for inc in self.incidents:
            if inc.get(occurred_time_key):
                mttd = (inc['detected'] - inc[occurred_time_key]).total_seconds() / 60
                detection_times.append(mttd)
        return sum(detection_times) / len(detection_times) if detection_times else 0

    def calculate_mttr(self, phase='total', severity=None):
        """计算MTTR"""
        incidents = self.incidents
        if severity:
            incidents = [i for i in incidents if i['severity'] == severity]

        times = []
        for inc in incidents:
            if phase == 'contain':
                t = (inc['contained'] - inc['detected']).total_seconds() / 60
            elif phase == 'eradicate' and inc.get('eradicated'):
                t = (inc['eradicated'] - inc['contained']).total_seconds() / 60
            elif phase == 'recover' and inc.get('recovered'):
                t = (inc['recovered'] - inc.get('eradicated', inc['contained'])).total_seconds() / 60
            elif phase == 'total' and inc.get('recovered'):
                t = (inc['recovered'] - inc['detected']).total_seconds() / 60
            else:
                continue
            times.append(t)

        return round(sum(times) / len(times), 1) if times else 0

    def calculate_closure_rate(self, period=None):
        """计算事件闭环率"""
        incidents = self.incidents
        if period:
            start, end = period
            incidents = [i for i in incidents
                        if start <= i['detected'] <= end]

        total = len(incidents)
        closed = sum(1 for i in incidents if i.get('recovered'))

        return {
            'total': total,
            'closed': closed,
            'rate': round(closed / total * 100, 2) if total > 0 else 0
        }

    def calculate_false_positive_rate(self):
        """计算误报率"""
        total = len(self.incidents)
        false_pos = sum(1 for i in self.incidents if i.get('false_positive'))

        return round(false_pos / total * 100, 2) if total > 0 else 0

    def generate_dashboard(self):
        """生成度量仪表板数据"""
        return {
            'mttr_contain': self.calculate_mttr('contain'),
            'mttr_eradicate': self.calculate_mttr('eradicate'),
            'mttr_recover': self.calculate_mttr('recover'),
            'mttr_total': self.calculate_mttr('total'),
            'closure_rate': self.calculate_closure_rate(),
            'false_positive_rate': self.calculate_false_positive_rate(),
            'auto_detection_rate': self.calculate_auto_detection_rate(),
            'incidents_by_severity': self.count_by_severity()
        }

    def calculate_auto_detection_rate(self):
        """计算自动化检测率"""
        total = len(self.incidents)
        auto = sum(1 for i in self.incidents if i.get('auto_detected'))
        return round(auto / total * 100, 2) if total > 0 else 0

    def count_by_severity(self):
        """按严重级别统计"""
        counts = defaultdict(int)
        for inc in self.incidents:
            counts[inc['severity']] += 1
        return dict(counts)
```

**事件闭环率（Incident Closure Rate）**

```
指标定义：
  事件闭环率 = 已关闭事件数 / 总事件数 × 100%

目标：> 95%（30天内）

关联指标：
  ├── 超期未关闭事件数：超过SLA未关闭的事件
  ├── 平均关闭时间：从创建到关闭的平均天数
  ├── 重开率：关闭后重新打开的事件比例
  │   目标：< 5%
  └── 事后分析完成率：完成事后分析的事件比例
      目标：> 80%（重大事件）
```

### 3.4 运营度量

**安全事件趋势（Security Incident Trends）**

```
指标定义：
  按时间维度统计安全事件数量和类型的变化趋势

分析维度：
  ├── 月度/季度/年度事件数量趋势
  ├── 事件类型分布（钓鱼、恶意软件、数据泄露等）
  ├── 严重级别分布
  ├── 攻击来源分布
  ├── 受影响资产分布
  └── 与威胁情报的关联率

目标趋势：
  ├── 总事件数：平稳或下降
  ├── 重大事件数：持续下降
  ├── 钓鱼事件：下降（意识培训效果）
  ├── 恶意软件事件：下降（EDR效果）
  └── 检测率：持续上升
```

**重复事件率（Recurring Incident Rate）**

```
指标定义：
  重复事件率 = 重复发生的事件数 / 总事件数 × 100%

目标：< 10%

分析意义：
  ├── 高重复率 → 根因分析不足
  ├── 高重复率 → 防御措施失效
  └── 高重复率 → 需要改进根本解决方案

改进措施：
  ├── 加强根因分析
  ├── 实施预防性控制
  ├── 更新Playbook覆盖
  └── 加强配置加固
```

**自动化率（Automation Rate）**

```
指标定义：
  自动化率 = 自动化处置的事件数 / 总事件数 × 100%

细分：
  ├── 告警自动分诊率：自动分类的告警比例
  ├── 自动响应率：自动执行响应动作的事件比例
  ├── 自动封禁率：自动封禁的IP/主机比例
  └── 自动关闭率：无需人工干预自动关闭的事件比例

目标：
  ├── 告警自动分诊率：> 60%
  ├── 自动响应率：> 40%
  └── 自动关闭率：> 30%
```

---

---

## 📋 内容审核与补充建议

> 针对「安全KPI指标体系」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
