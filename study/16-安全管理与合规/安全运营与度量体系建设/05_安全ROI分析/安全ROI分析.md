# 安全ROI分析

### 4.1 投资回报率计算方法

```
安全ROI计算模型：

基本公式：
  ROI = （收益 - 投资） / 投资 × 100%

安全投资的收益维度：
├── 避免损失（Loss Avoidance）
│   ├── 避免的潜在数据泄露损失
│   ├── 避免的业务中断损失
│   ├── 避免的合规罚款
│   └── 避免的声誉损失
│
├── 运营效率（Operational Efficiency）
│   ├── 减少的人工分析时间
│   ├── 自动化节省的人力成本
│   ├── 减少的误报处理时间
│   └── 加速的响应时间
│
└── 风险降低（Risk Reduction）
    ├── 风险评分降低
    ├── 攻击面缩小
    └── 保险费降低
```

**ROI计算示例：**

```python
class SecurityROI:
    """安全投资回报率计算"""

    def __init__(self):
        self.investments = {}
        self.benefits = {}
        self.baseline_metrics = {}

    def add_investment(self, category, amount, description=""):
        """添加投资项"""
        self.investments[category] = {
            'amount': amount,
            'description': description
        }

    def add_benefit(self, category, amount, description=""):
        """添加收益项"""
        self.benefits[category] = {
            'amount': amount,
            'description': description
        }

    def calculate_loss_avoidance(self, annual_loss_expectancy_before,
                                 annual_loss_expectancy_after):
        """
        计算避免的损失
        ALE = SLE × ARO
        SLE = Single Loss Expectancy（单次损失期望）
        ARO = Annualized Rate of Occurrence（年发生率）
        """
        return annual_loss_expectancy_before - annual_loss_expectancy_after

    def calculate_operational_savings(self, hours_saved, hourly_rate,
                                       automation_investment):
        """计算运营节省"""
        annual_savings = hours_saved * hourly_rate * 52  # 52周
        return annual_savings

    def calculate_roi(self):
        """计算总ROI"""
        total_investment = sum(
            v['amount'] for v in self.investments.values()
        )
        total_benefit = sum(
            v['amount'] for v in self.benefits.values()
        )

        roi = ((total_benefit - total_investment) /
               total_investment * 100) if total_investment > 0 else 0

        # 计算投资回收期
        payback_months = (total_investment /
                          (total_benefit / 12)) if total_benefit > 0 else 0

        return {
            'total_investment': total_investment,
            'total_benefit': total_benefit,
            'net_benefit': total_benefit - total_investment,
            'roi_percentage': round(roi, 2),
            'payback_months': round(payback_months, 1),
            'investments': self.investments,
            'benefits': self.benefits
        }

    def generate_roi_report(self):
        """生成ROI报告"""
        result = self.calculate_roi()

        print("=" * 60)
        print("Security Investment ROI Report")
        print("=" * 60)

        print("\nInvestments:")
        for cat, data in result['investments'].items():
            print(f"  {cat}: ${data['amount']:,.0f}")
            if data['description']:
                print(f"    ({data['description']})")

        print(f"\nTotal Investment: ${result['total_investment']:,.0f}")

        print("\nBenefits:")
        for cat, data in result['benefits'].items():
            print(f"  {cat}: ${data['amount']:,.0f}")
            if data['description']:
                print(f"    ({data['description']})")

        print(f"\nTotal Benefit: ${result['total_benefit']:,.0f}")
        print(f"Net Benefit: ${result['net_benefit']:,.0f}")
        print(f"ROI: {result['roi_percentage']}%")
        print(f"Payback Period: {result['payback_months']} months")

        return result


# 使用示例
if __name__ == "__main__":
    roi = SecurityROI()

    # 投资项
    roi.add_investment("SOAR平台采购", 500000, "3年许可+实施")
    roi.add_investment("EDR部署", 300000, "10000终端")
    roi.add_investment("SIEM升级", 200000, "扩容+新功能")
    roi.add_investment("人员培训", 100000, "SOC团队技能提升")

    # 收益项 - 避免的损失
    roi.add_benefit("避免数据泄露损失", 2000000,
                    "基于ALE计算，降低数据泄露风险")
    roi.add_benefit("避免业务中断", 500000,
                    "减少 ransomware导致的停机")
    roi.add_benefit("避免合规罚款", 300000,
                    "GDPR/等保合规风险降低")

    # 收益项 - 运营效率
    roi.add_benefit("人力成本节省", 400000,
                    "自动化减少5个FTE")
    roi.add_benefit("响应效率提升", 200000,
                    "MTTR降低50%的经济价值")

    roi.generate_roi_report()
```

### 4.2 ROI分析案例

```
案例：某企业SOAR部署ROI分析

背景：
  企业年安全事件数：5000+
  SOC团队：8人
  年度安全预算：500万

投资（3年）：
  ┌─────────────────────┬──────────┬───────────────────────┐
  │ 投资项目             │ 金额(万) │ 说明                   │
  ├─────────────────────┼──────────┼───────────────────────┤
  │ SOAR平台许可          │ 60       │ 3年企业版许可           │
  │ 实施和定制            │ 40       │ Playbook开发+集成       │
  │ 培训                 │ 10       │ 团队培训               │
  │ 运维                 │ 30       │ 3年运维成本             │
  │ 总投资               │ 140      │                        │
  └─────────────────────┴──────────┴───────────────────────┘

收益（3年）：
  ┌─────────────────────┬──────────┬───────────────────────┐
  │ 收益项               │ 金额(万) │ 计算依据               │
  ├─────────────────────┼──────────┼───────────────────────┤
  │ 人力成本节省         │ 150      │ 减少3名分析师×15万×3年│
  │ 响应效率提升         │ 90       │ MTTR从4h→1h×5000事件  │
  │ 避免数据泄露         │ 300      │ ALE降低×概率           │
  │ 避免业务中断         │ 100      │ 减少停机时间           │
  │ 合规罚款降低         │ 50       │ 降低违规风险           │
  │ 总收益               │ 690      │                        │
  └─────────────────────┴──────────┴───────────────────────┘

ROI = (690 - 140) / 140 × 100% = 392.8%
投资回收期 = 140 / (690/36) = 7.3个月

结论：SOAR投资具有高回报率，7.3个月可收回投资。
```

---

---

## 📋 内容审核与补充建议

> 针对「安全ROI分析」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
