# Windows系统安全配置指南

> 本文档系统梳理Windows操作系统安全相关知识，从系统基础到安全加固，涵盖网络配置、防火墙、端口管理、远程访问、日志审计、PowerShell安全、安全基线、组策略等核心内容，适用于安全运维、系统管理员及网络安全学习者。

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. Windows系统基础](./02_Windows系统基础/Windows系统基础.md)
  - Windows系统架构
  - Windows版本介绍
  - 用户账户与权限体系
  - 文件系统基础
  - 注册表基础
  - 进程与服务管理

### [03. Windows网络配置](./03_Windows网络配置/Windows网络配置.md)
  - 网卡配置
  - netsh命令与PowerShell网络命令
  - 网络适配器管理
  - Hosts文件配置
  - 路由表管理
  - 网络故障排查

### [04. Windows防火墙与高级安全](./04_Windows防火墙与高级安全/Windows防火墙与高级安全.md)
  - Windows防火墙基础
  - 高级安全防火墙（wf.msc）
  - 防火墙规则配置
  - 连接安全规则（IPsec）
  - 防火墙日志配置与分析
  - 常见服务端口放行配置

### [05. 端口管理与服务安全](./05_端口管理与服务安全/端口管理与服务安全.md)
  - 常见端口与服务对照
  - 端口查看与监听
  - 服务管理
  - 危险服务与禁用建议
  - 服务权限配置与加固
  - 启动项管理

### [06. RDP与远程访问安全加固](./06_RDP与远程访问安全加固/RDP与远程访问安全加固.md)
  - RDP协议基础与安全风险
  - RDP安全配置
  - 端口修改与防火墙规则
  - 账户锁定策略
  - 多因素认证配置
  - 跳板机与堡垒机概念
  - WinRM与PowerShell远程管理安全

### [07. Windows日志系统与安全审计](./07_Windows日志系统与安全审计/Windows日志系统与安全审计.md)
  - Windows日志体系
  - 事件查看器使用
  - 安全审计策略配置
  - 常见安全事件ID说明
  - wevtutil命令与PowerShell日志查询
  - 日志收集与转发

### [08. PowerShell安全与脚本执行](./08_PowerShell安全与脚本执行/PowerShell安全与脚本执行.md)
  - PowerShell执行策略
  - PowerShell 2.0降级攻击与防御
  - 约束语言模式
  - AMSI与PowerShell保护
  - 脚本签名与证书
  - PowerShell日志记录
  - 常用安全命令与安全实践

### [09. Windows安全基线与加固](./09_Windows安全基线与加固/Windows安全基线与加固.md)
  - 账户策略
  - 本地策略
  - 用户账户控制（UAC）
  - Windows Defender配置
  - 自动更新与补丁管理
  - BitLocker磁盘加密
  - 应用程序控制策略
  - 浏览器安全配置

### [10. 组策略与域安全基础](./10_组策略与域安全基础/组策略与域安全基础.md)
  - 活动目录基础概念
  - 组策略对象（GPO）基础
  - 常用安全组策略配置
  - 组策略结果与建模
  - 域环境安全最佳实践
  - 本地组策略编辑器

### [11. 实战加固检查清单](./11_实战加固检查清单/实战加固检查清单.md)
  - 系统信息收集清单
  - 账户安全检查
  - 网络与防火墙检查
  - 服务与端口检查
  - 补丁与更新检查
  - 日志与审计检查
  - 应用程序安全检查
  - 加固操作步骤汇总

### [12. 总结](./12_总结/总结.md)
  - 学习要点总结
  - 进阶学习方向
  - 推荐工具
  - 参考资料

---

## 📊 内容审核总览

- 总章节数：12
- 待完善章节：12

### 各章节审核状态
- **目录**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：attack
  - 缺少：references
- **Windows系统基础**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Windows网络配置**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Windows防火墙与高级安全**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **端口管理与服务安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **RDP与远程访问安全加固**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Windows日志系统与安全审计**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **PowerShell安全与脚本执行**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **Windows安全基线与加固**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **组策略与域安全基础**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **实战加固检查清单**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **总结**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：attack
  - 缺少：short
  - 缺少：references
