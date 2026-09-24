# NIST AI RMF

### 4.1 框架概述

**NIST AI风险管理框架（AI RMF 1.0）** 由美国国家标准与技术研究院于2023年1月发布。

```text
NIST AI RMF特征

性质: 自愿性框架（非强制性）
目标: 为AI系统设计、开发、使用、评估提供风险管理指导
适用: 所有类型和规模的机构

核心理念:
  可信AI的七个特征:
  1. 有效性及可靠性 (Valid & Reliable)
  2. 安全性 (Safe)
  3. 安全和弹性 (Secure & Resilient)
  4. 可解释性和可解读性 (Explainable & Interpretable)
  5. 隐私增强 (Privacy-Enhanced)
  6. 公平性 - 管理有害偏见 (Fair - Manage Harmful Bias)
  7. 透明度和问责制 (Transparency & Accountability)

AI生命周期:
├── 设想和设计
├── 数据处理和模型训练
├── 部署和运行
├── 维护和监控
└── 退役和处置
```

### 4.2 四大核心功能

```text
NIST AI RMF核心功能

┌──────────────────────────────────────────────────────────┐
│              GOVERN (治理)                                 │
│  建立AI风险管理的组织框架和文化                            │
├──────────────────────────────────────────────────────────┤
│ │ AI风险管理政策                                          │
│ │ 角色、职责和权限                                        │
│ │ 风险承受度定义                                          │
│ │ 培训和文化建设                                          │
│ │ 第三方风险管理                                          │
└──────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│              MAP (映射)                                   │
│  识别AI系统的背景和风险                                    │
├──────────────────────────────────────────────────────────┤
│ │ AI系统背景分析                                          │
│ │ 利益相关方识别                                          │
│ │ 预期用途和限制                                          │
│ │ 风险识别和分类                                          │
│ │ 信任worthiness评估                                      │
└──────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│              MEASURE (度量)                               │
│  分析和评估AI风险                                          │
├──────────────────────────────────────────────────────────┤
│ │ 性能测试（精度/鲁棒性）                                  │
│ │ 公平性度量                                              │
│ │ 隐私评估                                                │
│ │ 安全测试                                                │
│ │ 可解释性评估                                            │
│ │ 透明度度量                                              │
└──────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│              MANAGE (管理)                                │
│  分配资源处理已识别的风险                                  │
├──────────────────────────────────────────────────────────┤
│ │ 风险缓解措施                                            │
│ │ 风险监测                                                │
│ │ 应急响应                                                │
│ │ 事件报告                                                │
│ │ 持续改进                                                │
└──────────────────────────────────────────────────────────┘
```

### 4.3 实施指南

```python
"""
NIST AI RMF实施示例 - AI系统风险评估框架
"""

class AIRiskAssessment:
    """基于NIST AI RMF的AI风险评估"""

    def __init__(self):
        self.assessment_results = {}

    def assess_system(self, system_info, context):
        """
        全面评估AI系统
        :param system_info: AI系统信息
        :param context: 使用背景
        """
        results = {
            'system_id': system_info['id'],
            'assessment_date': '2026-09-13',
            'governance': self._assess_governance(system_info),
            'mapping': self._assess_mapping(system_info, context),
            'measuring': self._assess_measuring(system_info),
            'managing': self._assess_managing(system_info)
        }

        # 计算综合风险等级
        results['overall_risk'] = self._calculate_overall_risk(results)
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _assess_governance(self, system_info):
        """GOVERN: 治理评估"""
        checks = {
            'has_ai_policy': system_info.get('has_ai_policy', False),
            'roles_defined': system_info.get('roles_defined', False),
            'risk_tolerance': system_info.get('risk_tolerance') is not None,
            'training_program': system_info.get('has_training', False),
            'third_party_assessment': system_info.get('third_party_assessed', False)
        }
        score = sum(checks.values()) / len(checks)
        return {'checks': checks, 'score': score, 'status': 'PASS' if score >= 0.8 else 'NEEDS_IMPROVEMENT'}

    def _assess_mapping(self, system_info, context):
        """MAP: 风险映射"""
        risks = []
        # 识别潜在风险
        if system_info.get('uses_personal_data'):
            risks.append({'type': 'privacy', 'severity': 'high',
                         'description': '使用个人数据，存在隐私风险'})
        if system_info.get('affects_decisions'):
            risks.append({'type': 'fairness', 'severity': 'high',
                         'description': '影响决策，存在公平性风险'})
        if system_info.get('safety_critical'):
            risks.append({'type': 'safety', 'severity': 'critical',
                         'description': '安全关键系统'})
        if not system_info.get('explainable'):
            risks.append({'type': 'transparency', 'severity': 'medium',
                         'description': '模型不可解释'})

        return {'identified_risks': risks, 'risk_count': len(risks)}

    def _assess_measuring(self, system_info):
        """MEASURE: 度量评估"""
        metrics = {
            'accuracy': system_info.get('accuracy'),
            'robustness': system_info.get('robustness_score'),
            'fairness': system_info.get('fairness_score'),
            'privacy_score': system_info.get('privacy_score'),
            'safety_score': system_info.get('safety_score')
        }
        return {'metrics': metrics}

    def _assess_managing(self, system_info):
        """MANAGE: 风险管理"""
        measures = {
            'has_monitoring': system_info.get('has_monitoring', False),
            'has_incident_response': system_info.get('has_ir', False),
            'has_rollback': system_info.get('has_rollback', False),
            'has_human_oversight': system_info.get('human_oversight', False)
        }
        return {'measures': measures}

    def _calculate_overall_risk(self, results):
        """计算综合风险等级"""
        risk_score = 0
        mapping = results.get('mapping', {})
        for risk in mapping.get('identified_risks', []):
            if risk['severity'] == 'critical':
                risk_score += 10
            elif risk['severity'] == 'high':
                risk_score += 5
            elif risk['severity'] == 'medium':
                risk_score += 2
            else:
                risk_score += 1

        if risk_score >= 20:
            return 'CRITICAL'
        elif risk_score >= 10:
            return 'HIGH'
        elif risk_score >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_recommendations(self, results):
        """生成建议"""
        recs = []
        if results['overall_risk'] in ('CRITICAL', 'HIGH'):
            recs.append('建议暂停部署，进行全面安全评估')
        if not results['governance']['checks']['has_ai_policy']:
            recs.append('建立AI风险管理政策')
        if not results['managing']['measures']['has_monitoring']:
            recs.append('部署持续监控系统')
        if not results['managing']['measures']['has_human_oversight']:
            recs.append('增加人类监督机制')
        return recs


# 使用示例
def demo_risk_assessment():
    """AI风险评估演示"""
    assessor = AIRiskAssessment()

    # AI系统信息
    system_info = {
        'id': 'AI-RECRUIT-001',
        'name': '智能招聘筛选系统',
        'has_ai_policy': True,
        'roles_defined': True,
        'risk_tolerance': 'medium',
        'has_training': True,
        'third_party_assessed': False,
        'uses_personal_data': True,
        'affects_decisions': True,
        'safety_critical': False,
        'explainable': False,
        'accuracy': 0.85,
        'robustness_score': 0.70,
        'fairness_score': 0.75,
        'privacy_score': 0.60,
        'safety_score': 0.90,
        'has_monitoring': True,
        'has_ir': False,
        'has_rollback': True,
        'human_oversight': True
    }

    context = {
        'deployment': 'enterprise',
        'users': 'HR部门',
        'stakeholders': ['HR', '求职者', '管理层']
    }

    results = assessor.assess_system(system_info, context)

    print("=" * 50)
    print("AI系统风险评估报告")
    print("=" * 50)
    print(f"系统ID: {results['system_id']}")
    print(f"评估日期: {results['assessment_date']}")
    print(f"\n综合风险等级: {results['overall_risk']}")
    print(f"\n治理评估: {results['governance']['status']} "
          f"(得分: {results['governance']['score']:.0%})")
    print(f"\n风险映射:")
    for risk in results['mapping']['identified_risks']:
        print(f"  [{risk['severity'].upper()}] {risk['type']}: {risk['description']}")
    print(f"\n安全度量:")
    for k, v in results['measuring']['metrics'].items():
        if v is not None:
            print(f"  {k}: {v}")
    print(f"\n建议:")
    for rec in results['recommendations']:
        print(f"  - {rec}")


if __name__ == "__main__":
    demo_risk_assessment()
```

---

---

