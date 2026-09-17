# Sigma规则

Sigma是一种通用的签名格式，用于跨SIEM平台的检测规则共享。

```yaml
# Sigma规则示例 - 检测Mimikatz
title: Mimikatz Process Detection
id: f1234567-89ab-cdef-0123-456789abcdef
status: experimental
description: |
  检测Mimikatz凭证提取工具的执行。
  Mimikatz常用于从LSASS内存中提取凭据。
references:
  - https://github.com/gentilkiwi/mimikatz
author: Security Team
date: 2026/09/13
logsource:
  product: windows
  service: security
detection:
  selection_process:
    EventID: 4688
    NewProcessName|endswith: 'mimikatz.exe'
  selection_commandline:
    EventID: 4688
    CommandLine|contains:
      - 'sekurlsa'
      - 'lsadump'
      - 'kerberos'
      - 'privilege::debug'
  condition: selection_process or selection_commandline
falsepositives:
  - 安全研究人员使用
  - 红队演练
level: high
tags:
  - attack.credential_access
  - attack.t1003
  - attack.t1003.001
```

```yaml
# Sigma规则 - 检测可疑PowerShell编码命令
title: PowerShell Encoded Command Execution
id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
status: stable
description: 检测使用编码参数执行PowerShell的恶意行为
references:
  - https://attack.mitre.org/techniques/T1059/001/
author: Security Team
date: 2026/09/13
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4688
    NewProcessName|endswith: '\powershell.exe'
    CommandLine|contains:
      - '-enc '
      - '-encodedcommand '
      - '-e '
      - '/encodedcommand '
  condition: selection
falsepositives:
  - 合法的管理脚本
  - 自动化运维工具
level: high
tags:
  - attack.execution
  - attack.t1059.001
```

```yaml
# Sigma规则 - 检测横向移动(RDP)
title: RDP from Untrusted Source
id: b2c3d4e5-f678-90ab-cdef-123456789abc
status: stable
description: 检测来自非信任网络的RDP连接
author: Security Team
date: 2026/09/13
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4624
    LogonType: 10
  filter_trusted:
    IpAddress|cidr:
      - '10.0.0.0/8'
      - '172.16.0.0/12'
      - '192.168.0.0/16'
  condition: selection and not filter_trusted
falsepositives:
  - VPN连接后RDP
  - 外部管理员访问
level: medium
tags:
  - attack.lateral_movement
  - attack.t1021.001
```

---

> **参考资源**
>
> - MITRE ATT&CK - attack.mitre.org
> - Sigma Project - github.com/SigmaHQ/sigma
> - Splunk SPL Reference - docs.splunk.com/Splex
> - ELK Documentation - elastic.co/guide
> - Windows Security Event IDs - docs.microsoft.com
> - SwiftOnSecurity Sysmon Config - github.com/SwiftOnSecurity

---

## 📋 内容审核与补充建议

> 针对「Sigma规则」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
