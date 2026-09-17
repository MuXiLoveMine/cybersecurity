# 内网渗透实战

> 本文档整理自：`内网渗透实战.md`

---

## 目录

### [01. 内网渗透概述](./01_内网渗透概述/内网渗透概述.md)
  - 内网渗透定义
  - 内网渗透场景

### [02. Windows 域环境基础](./02_Windows 域环境基础/Windows 域环境基础.md)
  - Active Directory 架构
  - Kerberos 认证机制
  - NTLM 认证机制

### [03. 内网信息收集](./03_内网信息收集/内网信息收集.md)
  - 域环境信息收集
  - 主机信息收集
  - Linux 内网信息收集

### [04. 横向移动技术](./04_横向移动技术/横向移动技术.md)
  - Windows 横向移动
  - 非域环境横向移动

### [05. 权限提升](./05_权限提升/权限提升.md)
  - Windows 提权
  - Linux 提权

### [06. 代理与隧道技术](./06_代理与隧道技术/代理与隧道技术.md)
  - 正向代理
  - 反向代理
  - 多级代理
  - DNS 隧道

### [07. 持久化技术](./07_持久化技术/持久化技术.md)
  - Windows 持久化
  - Linux 持久化

### [08. 防御绕过技术](./08_防御绕过技术/防御绕过技术.md)
  - AMSI 绕过
  - EDR 绕过
  - 日志清理

### [09. 内网渗透实战案例](./09_内网渗透实战案例/内网渗透实战案例.md)
  - 场景：从 Web Shell 到域管
  - 场景：限制出网环境下的内网渗透

### [10. 内网信息收集自动化](./10_内网信息收集自动化/内网信息收集自动化.md)
  - PowerShell 自动化信息收集
  - WMIC 信息收集
  - BloodHound 深度分析

### [11. 横向移动技巧](./11_横向移动技巧/横向移动技巧.md)
  - WMI 横向移动
  - PsExec 横向移动
  - Pass the Hash 横向移动
  - RDP 横向移动

### [12. 域控攻击](./12_域控攻击/域控攻击.md)
  - ZeroLogon (CVE-2020-1472)
  - PrintNightmare (CVE-2021-1675/34527)
  - Golden Ticket 详解
  - Silver Ticket 详解
  - AD ACL 滥用

### [13. Kerberos 协议攻击总结](./13_Kerberos 协议攻击总结/Kerberos 协议攻击总结.md)

### [14. 流量代理与隧道](./14_流量代理与隧道/流量代理与隧道.md)
  - IcmpTunnel
  - HTTP 隧道
  - 多级代理链

### [15. C2 框架对比](./15_C2 框架对比/C2 框架对比.md)
  - 主流 C2 框架详细对比
  - Cobalt Strike 关键特性
  - Sliver 使用

---

## 📊 内容审核总览

- 总章节数：15
- 待完善章节：15

### 各章节审核状态
- **内网渗透概述**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **Windows 域环境基础**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **内网信息收集**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **横向移动技术**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **权限提升**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
- **代理与隧道技术**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **持久化技术**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **防御绕过技术**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **内网渗透实战案例**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **内网信息收集自动化**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **横向移动技巧**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **域控攻击**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Kerberos 协议攻击总结**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **流量代理与隧道**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **C2 框架对比**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
