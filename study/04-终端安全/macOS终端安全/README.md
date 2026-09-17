# macOS终端安全

> 本文档整理自：`macOS终端安全.md`

---

## 目录

### [01. macOS 安全架构概述](./01_macOS 安全架构概述/macOS 安全架构概述.md)
  - 操作系统架构（Darwin/XNU 内核）
  - 安全设计理念
  - macOS vs Linux/Windows 安全模型对比
  - 安全功能演进历史

### [02. Gatekeeper 与代码签名](./02_Gatekeeper 与代码签名/Gatekeeper 与代码签名.md)
  - Gatekeeper 工作机制
  - 代码签名原理
  - 公证（Notarization）流程
  - Gatekeeper 绕过技术与防御
  - ad-hoc 签名与内部应用管理

### [03. XProtect 与 MRT](./03_XProtect 与 MRT/XProtect 与 MRT.md)
  - XProtect（恶意软件检测引擎）
  - MRT（Malware Removal Tool）
  - 检测能力与局限性
  - 与商业 AV 产品的对比

### [04. SIP（系统完整性保护）](./04_SIP（系统完整性保护）/SIP（系统完整性保护）.md)
  - SIP 原理与保护范围
  - SIP 对安全的影响
  - SIP 绕过技术
  - SIP 配置与定制化

### [05. 沙箱机制](./05_沙箱机制/沙箱机制.md)
  - macOS 沙箱架构
  - 沙箱配置文件
  - 容器化应用（App Sandbox、App Group）
  - 沙箱逃逸技术与案例分析
  - TCC（Transparency, Consent, and Control）

### [06. FileVault 磁盘加密](./06_FileVault 磁盘加密/FileVault 磁盘加密.md)
  - FileVault 2 原理
  - 恢复密钥管理
  - FileVault 与硬件安全
  - 磁盘加密攻击与防御

### [07. macOS 权限与访问控制](./07_macOS 权限与访问控制/macOS 权限与访问控制.md)
  - 用户权限模型
  - sudo 与授权管理
  - POSIX 权限与 ACL
  - TCC 数据库与隐私权限管理

### [08. macOS 网络安全](./08_macOS 网络安全/macOS 网络安全.md)
  - 防火墙（Application Firewall, ALF）
  - pfctl 包过滤防火墙配置
  - VPN 配置与安全
  - 网络流量分析工具

### [09. macOS 安全加固](./09_macOS 安全加固/macOS 安全加固.md)
  - 安全配置基线（CIS Benchmark for macOS）
  - 企业级安全策略（MDM/Profile Manager/JAMF）
  - 补丁管理与自动更新
  - 审计日志与监控

### [10. macOS 取证与应急响应](./10_macOS 取证与应急响应/macOS 取证与应急响应.md)
  - 统一日志系统（OSLog）使用
  - 内存取证
  - 磁盘取证与分析
  - 常见 macOS 恶意软件分析案例
  - 应急响应工具清单

### [11. macOS vs Windows 安全对比](./11_macOS vs Windows 安全对比/macOS vs Windows 安全对比.md)
  - 安全模型对比
  - 威胁场景对比
  - 企业管理对比
  - 综合安全建议

### [12. 附录：macOS 安全速查命令](./12_附录：macOS 安全速查命令/附录：macOS 安全速查命令.md)

---

## 📊 内容审核总览

- 总章节数：12
- 待完善章节：12

### 各章节审核状态
- **macOS 安全架构概述**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Gatekeeper 与代码签名**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **XProtect 与 MRT**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **SIP（系统完整性保护）**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **沙箱机制**：⚠️ 需补充 1 项
  - 缺少：references
- **FileVault 磁盘加密**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **macOS 权限与访问控制**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **macOS 网络安全**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **macOS 安全加固**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **macOS 取证与应急响应**：⚠️ 需补充 2 项
  - 缺少：knowledge
  - 缺少：references
- **macOS vs Windows 安全对比**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **附录：macOS 安全速查命令**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
