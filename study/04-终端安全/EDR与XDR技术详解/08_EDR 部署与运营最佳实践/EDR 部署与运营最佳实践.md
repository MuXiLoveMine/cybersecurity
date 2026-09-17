# EDR 部署与运营最佳实践

### 8.1 部署策略

```
EDR 部署成熟度模型

Level 1 - 基础部署
├── 全终端覆盖安装
├── 默认规则启用
├── 告警人工处理
└── 适合: 初次部署 EDR 的组织

Level 2 - 优化运营
├── 自定义规则（适配业务场景）
├── 白名单管理（减少误报）
├── 自动响应策略配置
├── 定期威胁狩猎
└── 适合: 有专职安全团队的机构

Level 3 - 高级运营
├── XDR 跨域联动
├── SOAR 自动化编排
├── 主动威胁狩猎（Threat Hunting）
├── 自研检测规则
├── ATT&CK 覆盖度评估
└── 适合: 大型安全运营中心
```

### 8.2 规则调优

```yaml
# EDR 规则调优检查清单

误报处理:
  - 分析误报根因，调整规则条件
  - 对业务正常行为建立白名单
  - 使用更精确的匹配条件
  - 设置告警阈值和聚合窗口

漏报补查:
  - 结合威胁情报补充 IOC
  - 基于红蓝对抗结果补充检测规则
  - 定期 ATT&CK 技术覆盖率评估
  - 引入新威胁的检测规则

规则生命周期:
  - 新规则: 先观察模式（仅告警不响应）
  - 验证: 收集7天误报率数据
  - 上线: 误报率 < 5% 后启用自动响应
  - 退役: 规则失效后归档
```

### 8.3 威胁狩猎（Threat Hunting）

```
威胁狩猎方法论

假设驱动型狩猎:
1. 提出假设: "攻击者可能利用 WMI 实现持久化"
2. 编写查询: 查找 WMI 订阅创建行为
3. 分析结果: 过滤正常运维操作
4. 深入调查: 追踪可疑 WMI 消费者脚本
5. 更新规则: 将发现转化为新检测规则

KQL 威胁狩猎示例 (Defender):

// 查找异常 PowerShell 编码执行
DeviceProcessEvents
| where ProcessCommandLine has_any("-enc", "-EncodedCommand")
| where InitiatingProcessFileName in~ (
    "winword.exe", "excel.exe", "outlook.exe", "powerpnt.exe"
)
| project Timestamp, DeviceName, 
    InitiatingProcessFileName, ProcessCommandLine

// 查找可疑计划任务创建
DeviceProcessEvents
| where ProcessCommandLine has "schtasks" and has_any(
    "/create", "/Change")
| where ProcessCommandLine has_any(
    "powershell", "cmd", "wscript", "mshta", "rundll32"
)
```

### 8.4 EDR vs EDR 攻防对抗

```
攻防对抗中的 EDR 角色红队视角（攻击方）:
  - 信息收集: 目标终端安装的 EDR 类型和版本
  - 绕过测试: AMSI/ETW/系统调用绕过
  - 免杀: 修改 Payload 特征规避检测
  - 环境感知: 检测 EDR Agent 进程和服务
  - 利用合法工具: LOLBins 减少行为异常

蓝队视角（防守方）:
  - 规则优化: 持续降低误报/漏报
  - 威胁狩猎: 主动发现隐蔽威胁
  - 攻击链还原: 利用 EDR 数据追踪攻击者
  - 快速响应: 自动化隔离和清除
  - 经验积累: 每次攻防对抗转化为规则
```

---

> **学习建议**：EDR/XDR 是现代企业终端安全的核心技术。建议学习者结合实际部署体验（如试用 Defender for Endpoint），深入理解数据采集、检测引擎、响应机制的工作原理。同时关注红队绕过技术的发展动态，理解攻防对抗的平衡关系。

---

## 📋 内容审核与补充建议

> 针对「EDR 部署与运营最佳实践」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
