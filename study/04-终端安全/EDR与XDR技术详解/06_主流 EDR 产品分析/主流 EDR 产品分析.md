# 主流 EDR 产品分析

### 6.1 产品对比

| 产品 | 厂商 | 检测优势 | 响应能力 | 国内可用性 |
|------|------|----------|----------|------------|
| CrowdStrike Falcon | CrowdStrike | 云原生+行为分析 | 强 | 受限 |
| SentinelOne | SentinelOne | AI+自动响应 | 强 | 受限 |
| Defender for Endpoint | Microsoft | 深度集成Windows | 强 | 可用 |
| Carbon Black | VMware | 行为分析+威胁狩猎 | 强 | 受限 |
| 奇安信天擎 | 奇安信 | 本土适配+合规 | 中强 | 强 |
| 深信服EDR | 深信服 | 病毒+勒索防护 | 中强 | 强 |
| 微步终端安全 | 微步在线 | 威胁情报驱动 | 中 | 强 |
| 360终端安全 | 360 | 安全大脑+大数据 | 中强 | 强 |

### 6.2 CrowdStrike Falcon

```
CrowdStrike Falcon 架构

终端 Sensor (轻量Agent ~30MB)
├── 采集: 进程/文件/网络/注册表/内存
├── 本地检测: 机器学习模型
├── 云端查询: 指纹上传云端分析
└── 响应执行: 隔离/终止/网络阻断

云端平台 (Falcon)
├── Falcon Insight - EDR 功能
├── Falcon Overwatch - 托管威胁狩猎
├── Falcon Intelligence - 威胁情报
├── Falcon Discover - 资产发现
└── Falcon Firewall - 主机防火墙
```

### 6.3 Microsoft Defender for Endpoint

```powershell
# Defender for Endpoint 关键命令

# 查看保护状态
Get-MpComputerStatus

# 查看当前威胁
Get-MpThreatDetection

# 触发快速扫描
Start-MpScan -ScanType QuickScan

# 隔离特定文件
Add-MpPreference -ThreatName "Trojan.Win32.Generic" -Action Quarantine

# 添加排除项（需谨慎）
Add-MpPreference -ExclusionPath "C:\MyApp"

# 启用网络保护
Set-MpPreference -EnableNetworkProtection Enabled

# 查看攻击面减少规则
Get-MpPreference | Select-Object -ExpandProperty AttackSurfaceReductionRules_Ids

# 高级 hunting 查询 (KQL)
# DeviceProcessEvents
# | where ProcessCommandLine has "powershell" and has "-enc"
# | project Timestamp, DeviceName, ProcessCommandLine
```

---

---

## 📋 内容审核与补充建议

> 针对「主流 EDR 产品分析」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
