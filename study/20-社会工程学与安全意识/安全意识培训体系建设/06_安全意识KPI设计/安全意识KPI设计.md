# 安全意识KPI设计

### 6.1 KPI体系

```
安全意识KPI体系：

┌──────────────────────────────────────────────────────┐
│                  安全意识KPI体系                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  战略层KPI（向董事会汇报）                             │
│  ├── 安全事件年同比下降率                             │
│  │   目标: 同比下降 > 20%                             │
│  ├── 安全投资ROI                                      │
│  │   目标: > 3.0                                      │
│  ├── 合规审计通过率                                   │
│  │   目标: 100%                                       │
│  └── 企业安全风险评分                                 │
│      目标: 从C级提升至B级                              │
│                                                      │
│  运营层KPI（向CISO汇报）                              │
│  ├── 钓鱼模拟点击率                                   │
│  │   目标: < 10%（年度）                              │
│  ├── 钓鱼模拟报告率                                   │
│  │   目标: > 60%（年度）                              │
│  ├── 培训完成率                                       │
│  │   目标: > 95%                                      │
│  ├── 培训通过率                                       │
│  │   目标: > 90%                                      │
│  ├── 安全事件响应时间                                 │
│  │   目标: < 30分钟                                   │
│  └── 安全冠军覆盖率                                   │
│      目标: 100%部门有安全冠军                          │
│                                                      │
│  执行层KPI（向安全意识经理汇报）                       │
│  ├── 月度钓鱼模拟执行率                                │
│  │   目标: 100%按计划执行                              │
│  ├── 培训课程更新频率                                  │
│  │   目标: 每季度更新1次                               │
│  ├── 安全提醒发送频率                                  │
│  │   目标: 每月至少1次                                 │
│  ├── 安全事件分享频率                                  │
│  │   目标: 每月1次安全简报                             │
│  └── 员工安全满意度                                    │
│      目标: > 4.0/5.0                                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 6.2 KPI仪表板设计

```python
# 安全意识KPI仪表板数据结构

kpi_dashboard = {
    "meta": {
        "report_period": "2026 Q3",
        "generated_at": "2026-09-30",
        "generated_by": "Security Awareness Team"
    },
    "summary": {
        "overall_security_awareness_grade": "B+",
        "trend": "improving",
        "key_achievement": "钓鱼点击率从Q2的18%降至Q3的12%",
        "key_concern": "销售部门培训完成率和报告率偏低"
    },
    "kpi_groups": {
        "phishing_simulation": {
            "click_rate": {
                "current": 12.0,
                "previous": 18.0,
                "target": 10.0,
                "status": "improving",
                "trend": "-6.0%"
            },
            "report_rate": {
                "current": 55.0,
                "previous": 42.0,
                "target": 60.0,
                "status": "improving",
                "trend": "+13.0%"
            },
            "submission_rate": {
                "current": 4.0,
                "previous": 7.0,
                "target": 5.0,
                "status": "on_target",
                "trend": "-3.0%"
            }
        },
        "training": {
            "completion_rate": {
                "current": 94.0,
                "previous": 89.0,
                "target": 95.0,
                "status": "near_target",
                "trend": "+5.0%"
            },
            "pass_rate": {
                "current": 91.0,
                "previous": 85.0,
                "target": 90.0,
                "status": "on_target",
                "trend": "+6.0%"
            }
        },
        "incident": {
            "phishing_incidents": {
                "current": 8,
                "previous": 14,
                "target": 10,
                "status": "on_target",
                "trend": "-43.0%"
            },
            "avg_response_time_min": {
                "current": 22,
                "previous": 35,
                "target": 30,
                "status": "on_target",
                "trend": "-37.0%"
            }
        },
        "culture": {
            "champion_coverage": {
                "current": 90.0,
                "previous": 70.0,
                "target": 100.0,
                "status": "improving",
                "trend": "+20.0%"
            },
            "employee_satisfaction": {
                "current": 4.2,
                "previous": 3.8,
                "target": 4.0,
                "status": "on_target",
                "trend": "+0.4"
            }
        }
    },
    "action_items": [
        {
            "priority": "high",
            "action": "销售部门专项安全培训",
            "owner": "安全意识经理",
            "deadline": "2026-10-15"
        },
        {
            "priority": "medium",
            "action": "优化钓鱼邮件一键报告功能",
            "owner": "IT运维",
            "deadline": "2026-10-30"
        },
        {
            "priority": "low",
            "action": "未覆盖部门安全冠军选拔",
            "owner": "安全意识经理",
            "deadline": "2026-11-15"
        }
    ]
}
```

---

---

