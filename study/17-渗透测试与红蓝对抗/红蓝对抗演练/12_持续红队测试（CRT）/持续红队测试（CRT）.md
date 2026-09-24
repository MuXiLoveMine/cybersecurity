# 持续红队测试（CRT）

### 12.1 CRT概念

持续红队测试（Continuous Red Teaming, CRT）是对传统红蓝对抗的演进，将周期性的大规模演练转变为持续性的小规模攻击模拟。

**传统红蓝对抗 vs CRT对比**

| 维度 | 传统红蓝对抗 | 持续红队(CRT) |
|------|------------|-------------|
| 频率 | 每年1-2次 | 持续/每周 |
| 范围 | 全面攻击链 | 单项技术测试 |
| 持续时间 | 数周 | 持续运行 |
| 目标 | 全面评估 | 持续改进 |
| 工具 | 全套攻击工具 | 自动化框架 |
| 报告 | 详细报告 | 实时仪表盘 |

### 12.2 CRT平台与工具

**CyRANGE/MTR平台**

```
CyRANGE/MTR平台架构:

├── 攻击自动化引擎
│   ├── ATT&CK技术库（映射Atomic Red Team）
│   ├── 攻击计划编排器
│   ├── 攻击执行Agent
│   └── 结果收集器
│
├── 检测评估引擎
│   ├── SIEM集成接口
│   ├── EDR集成接口
│   ├── NDR集成接口
│   └── 检测结果关联器
│
├── 持续评估引擎
│   ├── 覆盖率趋势分析
│   ├── 检测时效统计
│   ├── 退化检测（检测规则失效）
│   └── 改进跟踪
│
└── 可视化层
    ├── ATT&CK覆盖热力图
    ├── 趋势仪表盘
    ├── 告警通知
    └── 报告生成
```

### 12.3 CRT自动化示例

```python
# 持续红队测试编排示例
class ContinuousRedTeam:
    def __init__(self):
        self.attack_techniques = self.load_attack_library()
        self.detection_results = {}
    
    def load_attack_library(self):
        """加载ATT&CK技术测试库"""
        return {
            "T1566.001": {"name": "鱼叉钓鱼附件", "automation": "manual"},
            "T1059.001": {"name": "PowerShell执行", "automation": "atomic"},
            "T1003.001": {"name": "LSASS内存转储", "automation": "atomic"},
            "T1550.002": {"name": "Pass the Hash", "automation": "script"},
            "T1071.001": {"name": "Web C2通信", "automation": "script"},
            "T1053.005": {"name": "计划任务", "automation": "atomic"},
            "T1547.001": {"name": "注册表Run键", "automation": "atomic"},
            "T1110.001": {"name": "密码爆破", "automation": "script"},
        }
    
    def execute_test(self, technique_id):
        """执行单项ATT&CK技术测试"""
        tech = self.attack_techniques[technique_id]
        print(f"[CRT] 执行测试: {technique_id} - {tech['name']}")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 执行攻击模拟
        attack_result = self.run_attack(technique_id)
        
        # 等待检测窗口（如5分钟）
        time.sleep(300)
        
        # 检查SIEM/EDR是否产生告警
        detection_result = self.check_detection(technique_id, start_time)
        
        # 记录结果
        self.detection_results[technique_id] = {
            "attack_time": start_time,
            "attack_success": attack_result,
            "detected": detection_result["detected"],
            "detection_delay": detection_result.get("delay_seconds", 0),
            "alert_source": detection_result.get("source", ""),
            "response_action": detection_result.get("response", ""),
        }
        
        return self.detection_results[technique_id]
    
    def generate_report(self):
        """生成持续评估报告"""
        total = len(self.detection_results)
        detected = sum(1 for r in self.detection_results.values() if r["detected"])
        avg_delay = np.mean([r["detection_delay"] for r in self.detection_results.values() if r["detected"]])
        
        report = {
            "total_tests": total,
            "detected_count": detected,
            "coverage_rate": f"{detected}/{total} ({detected/total*100:.1f}%)",
            "avg_detection_delay": f"{avg_delay:.1f}秒",
            "gaps": [tid for tid, r in self.detection_results.items() if not r["detected"]],
        }
        return report

# 运行CRT
crt = ContinuousRedTeam()
for tid in ["T1059.001", "T1003.001", "T1547.001"]:
    crt.execute_test(tid)
print(json.dumps(crt.generate_report(), indent=2, ensure_ascii=False))
```

---

---

